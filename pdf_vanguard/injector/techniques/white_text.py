"""White text injection technique."""

import logging

import pikepdf

from pdf_vanguard.core.models import InjectionResult
from pdf_vanguard.injector.pdf_utils import (
    append_content_stream,
    ensure_font_resource,
    escape_pdf_string,
)
from pdf_vanguard.injector.techniques.base import BaseTechnique

logger = logging.getLogger(__name__)


class WhiteTextTechnique(BaseTechnique):
    """Inject payload as white text (RGB 1 1 1) with 1pt font at page bottom.

    Invisible on white background; fully extractable by text parsers.
    """

    name = "White Text Injection"
    flag = "white"
    stealth_level = 2

    def inject(self, pdf: pikepdf.Pdf, payload: str) -> InjectionResult:
        try:
            for page in pdf.pages:
                injection = (
                    "\nq "
                    "1 1 1 rg "           # Set fill color to white
                    "BT "
                    "/F1 1 Tf "           # Font size 1pt
                    "72 2 Td "            # Position near bottom-left
                    f"({escape_pdf_string(payload)}) Tj "
                    "ET "
                    "Q\n"
                )
                append_content_stream(pdf, page, injection)
                ensure_font_resource(page)
            return self._ok("White text (1pt, RGB white) at page bottom")
        except Exception as e:
            logger.error("White text injection failed: %s", e)
            return self._fail(str(e))
