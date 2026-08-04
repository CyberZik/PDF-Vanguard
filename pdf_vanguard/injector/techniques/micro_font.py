"""Micro font injection technique."""

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


class MicroFontTechnique(BaseTechnique):
    """Inject payload with 0.5pt font in near-white gray color.

    Practically invisible but extractable by text parsers.
    """

    name = "Micro Font Injection"
    flag = "micro"
    stealth_level = 3

    def inject(self, pdf: pikepdf.Pdf, payload: str) -> InjectionResult:
        try:
            for page in pdf.pages:
                injection = (
                    "\nq "
                    "0.96 0.96 0.96 rg "  # Near-white gray
                    "BT "
                    "/F1 0.5 Tf "          # 0.5pt font
                    "72 1 Td "
                    f"({escape_pdf_string(payload)}) Tj "
                    "ET "
                    "Q\n"
                )
                append_content_stream(pdf, page, injection)
                ensure_font_resource(page)
            return self._ok("Micro font (0.5pt, near-white) at page bottom")
        except Exception as e:
            logger.error("Micro font injection failed: %s", e)
            return self._fail(str(e))
