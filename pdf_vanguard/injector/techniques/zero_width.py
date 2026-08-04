"""Zero-width character encoding injection technique."""

import logging

import pikepdf

from pdf_vanguard.core.models import InjectionResult
from pdf_vanguard.injector.techniques.base import BaseTechnique
from pdf_vanguard.injector.pdf_utils import (
    append_content_stream_raw,
    ensure_font_resource,
)

logger = logging.getLogger(__name__)


class ZeroWidthTechnique(BaseTechnique):
    """Encode payload using zero-width Unicode characters.

    Each byte is binary-encoded with:
      - U+200B (Zero-Width Space) = bit 0
      - U+200D (Zero-Width Joiner) = bit 1
      - U+200C (Zero-Width Non-Joiner) = character separator

    Injected as a UTF-16BE hex string into the first page.
    """

    name = "Zero-Width Char Encoding"
    flag = "zwc"
    stealth_level = 5

    def inject(self, pdf: pikepdf.Pdf, payload: str) -> InjectionResult:
        try:
            zwsp = "\u200B"
            zwj = "\u200D"
            zwnj = "\u200C"

            # Binary-encode each character of the payload
            encoded = ""
            for ch in payload:
                bits = format(ord(ch), '08b')
                encoded += "".join(zwsp if b == '0' else zwj for b in bits)
                encoded += zwnj

            # Encode as UTF-16BE hex string for PDF
            utf16_bytes = encoded.encode("utf-16-be")
            hex_str = "FEFF" + utf16_bytes.hex().upper()

            # Inject as hex string in content stream (first page only)
            for page in pdf.pages:
                injection = (
                    "\nq "
                    "BT "
                    "/F1 1 Tf "
                    "0 0 Td "
                    f"<{hex_str}> Tj "
                    "ET "
                    "Q\n"
                )
                append_content_stream_raw(pdf, page, injection.encode("ascii"))
                ensure_font_resource(page)
                break  # Only first page

            return self._ok(
                f"Zero-width character encoding ({len(encoded)} invisible chars, UTF-16BE hex)"
            )
        except Exception as e:
            logger.error("Zero-width char injection failed: %s", e)
            return self._fail(str(e))
