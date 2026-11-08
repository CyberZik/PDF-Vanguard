"""Off-page text injection technique."""

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


class OffPageTechnique(BaseTechnique):
    """Place payload text at coordinates far outside the visible page area.

    Text exists in the content stream but renders off-screen at (-5000, -5000).
    """

    name = "Off-Page Text Injection"
    flag = "offpage"
    stealth_level = 3

    def inject(self, pdf: pikepdf.Pdf, payload: str) -> InjectionResult:
        try:
            for page in pdf.pages:
                injection = (
                    "\nq "
                    "0 0 0 rg "
                    "BT "
                    "/F1 10 Tf "
                    "-5000 -5000 Td "          # Far off-page (negative coords)
                    f"({escape_pdf_string(payload)}) Tj "
                    "ET "
                    "Q\n"
                )
                append_content_stream(pdf, page, injection)
                ensure_font_resource(page)
            return self._ok("Off-page text at coordinates (-5000, -5000)")
        except Exception as e:
            logger.error("Off-page text injection failed: %s", e)
            return self._fail(str(e))
