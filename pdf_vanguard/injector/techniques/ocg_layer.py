"""Hidden OCG (Optional Content Group) layer injection technique."""

import logging

import pikepdf

from pdf_vanguard.core.models import InjectionResult
from pdf_vanguard.injector.techniques.base import BaseTechnique
from pdf_vanguard.injector.pdf_utils import (
    escape_pdf_string,
    append_content_stream,
    ensure_font_resource,
)

logger = logging.getLogger(__name__)


class OCGLayerTechnique(BaseTechnique):
    """Create an Optional Content Group layer with visibility=OFF.

    The payload is placed inside a marked content block belonging to
    a hidden OCG named "PrinterMarks". Invisible in viewers but
    extractable by text parsers.
    """

    name = "Hidden OCG Layer"
    flag = "ocg"
    stealth_level = 4

    def inject(self, pdf: pikepdf.Pdf, payload: str) -> InjectionResult:
        try:
            # Create OCG dictionary
            ocg = pikepdf.Dictionary({
                "/Type": pikepdf.Name("/OCG"),
                "/Name": pikepdf.String("PrinterMarks"),  # Innocuous name
            })
            ocg_ref = pdf.make_indirect(ocg)

            # Set up OCProperties with layer OFF by default
            oc_properties = pikepdf.Dictionary({
                "/OCGs": pikepdf.Array([ocg_ref]),
                "/D": pikepdf.Dictionary({
                    "/OFF": pikepdf.Array([ocg_ref]),
                    "/BaseState": pikepdf.Name("/ON"),
                }),
            })
            pdf.Root["/OCProperties"] = oc_properties

            # Inject payload in hidden layer on each page
            for page in pdf.pages:
                injection = (
                    "\nq "
                    "/OC /InjectedOCG BDC "
                    "BT "
                    "/F1 1 Tf "
                    "0 0 0 rg "
                    "72 5 Td "
                    f"({escape_pdf_string(payload)}) Tj "
                    "ET "
                    "EMC "
                    "Q\n"
                )
                append_content_stream(pdf, page, injection)

                # Register OCG in page resources
                resources = page.get("/Resources", pikepdf.Dictionary())
                if "/Resources" not in page:
                    page["/Resources"] = resources
                props = resources.get("/Properties", pikepdf.Dictionary())
                if "/Properties" not in resources:
                    resources["/Properties"] = props
                props["/InjectedOCG"] = ocg_ref

                ensure_font_resource(page)

            return self._ok("Hidden OCG layer ('PrinterMarks', visibility=OFF)")
        except Exception as e:
            logger.error("OCG layer injection failed: %s", e)
            return self._fail(str(e))
