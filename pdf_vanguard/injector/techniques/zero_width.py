"""Zero-width character encoding injection technique."""

import logging

import pikepdf

from pdf_vanguard.core.models import InjectionResult
from pdf_vanguard.injector.pdf_utils import (
    ZWC_CODE_MAP,
    append_content_stream_raw,
    ensure_zwc_font_resource,
)
from pdf_vanguard.injector.techniques.base import BaseTechnique

logger = logging.getLogger(__name__)


class ZeroWidthTechnique(BaseTechnique):
    """Encode payload using zero-width Unicode characters.

    Each byte is binary-encoded with:
      - U+200B (Zero-Width Space) = bit 0
      - U+200D (Zero-Width Joiner) = bit 1
      - U+200C (Zero-Width Non-Joiner) = character separator

    Drawn on the first page with a font whose ToUnicode CMap maps the
    byte codes back to the real code points, so text extractors recover them.
    """

    name = "Zero-Width Char Encoding"
    flag = "zwc"
    stealth_level = 5

    def inject(self, pdf: pikepdf.Pdf, payload: str) -> InjectionResult:
        try:
            encoded = encode_zwc(payload)

            # Each zero-width char is drawn as a single-byte code; the font's
            # ToUnicode CMap maps it back to the real code point on extraction.
            raw = bytes(ZWC_CODE_MAP[ch] for ch in encoded)

            page = pdf.pages[0]  # First page only
            font = ensure_zwc_font_resource(pdf, page)
            injection = (
                b"\nq BT " + font.encode("ascii") + b" 1 Tf 0 0 Td <"
                + raw.hex().upper().encode("ascii") + b"> Tj ET Q\n"
            )
            append_content_stream_raw(pdf, page, injection)

            return self._ok(
                f"Zero-width character encoding ({len(encoded)} invisible chars, ToUnicode-mapped)"
            )
        except Exception as e:
            logger.error("Zero-width char injection failed: %s", e)
            return self._fail(str(e))


def encode_zwc(payload: str) -> str:
    """Binary-encode the UTF-8 bytes of ``payload`` as zero-width characters.

    U+200B = bit 0, U+200D = bit 1, U+200C terminates each byte.
    """
    out = []
    for byte in payload.encode("utf-8"):
        out.append("".join("\u200B" if b == "0" else "\u200D" for b in format(byte, "08b")))
        out.append("\u200C")
    return "".join(out)
