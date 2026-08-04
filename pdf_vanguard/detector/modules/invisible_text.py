"""Invisible text detection module (white text + micro font)."""

import logging
from typing import List

import pdfplumber

from pdf_vanguard.core.models import Finding
from pdf_vanguard.core.constants import MICRO_FONT_THRESHOLD, WHITE_COLOR_THRESHOLD
from pdf_vanguard.detector.modules.base import BaseDetector

logger = logging.getLogger(__name__)


class InvisibleTextDetector(BaseDetector):
    """Detect text with suspicious visual properties.

    Catches:
      - White or near-white font color on white background
      - Extremely small font sizes (< threshold)
    """

    name = "Invisible Text Scanner"
    description = "Detects white/near-white text and micro font sizes"

    def scan(self, filepath: str) -> List[Finding]:
        findings = []
        try:
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    chars = page.chars
                    found_micro = False
                    found_white = False

                    for char in chars:
                        text_char = char.get("text", "")
                        if not text_char.strip():
                            continue

                        # Check font size
                        if not found_micro:
                            font_size = char.get("size", 12)
                            if font_size is not None and font_size < MICRO_FONT_THRESHOLD:
                                findings.append(Finding(
                                    technique="Micro Font Injection",
                                    severity="HIGH",
                                    description=f"Text with extremely small font size ({font_size:.1f}pt) detected",
                                    evidence=f"Char: '{text_char}' at size {font_size:.1f}pt",
                                    location=f"Page {page_num}, pos ({char.get('x0', '?'):.0f}, {char.get('top', '?'):.0f})",
                                ))
                                found_micro = True

                        # Check color (near-white detection)
                        if not found_white:
                            color = char.get("non_stroking_color")
                            if color and _is_near_white(color):
                                findings.append(Finding(
                                    technique="White Text Injection",
                                    severity="HIGH",
                                    description="Text with near-white color detected (likely hidden)",
                                    evidence=f"Char: '{text_char}', color: {color}",
                                    location=f"Page {page_num}, pos ({char.get('x0', '?'):.0f}, {char.get('top', '?'):.0f})",
                                ))
                                found_white = True

                        # Stop scanning this page if both found
                        if found_micro and found_white:
                            break

        except Exception as e:
            logger.warning("Could not analyze character properties: %s", e)
            findings.append(Finding(
                technique="Scan Error",
                severity="INFO",
                description=f"Could not analyze character properties: {e}",
            ))
        return findings


def _is_near_white(color) -> bool:
    """Check if a color value is near-white (invisible on white background)."""
    if color is None:
        return False
    try:
        if isinstance(color, (list, tuple)):
            if len(color) == 3:  # RGB
                return all(c >= WHITE_COLOR_THRESHOLD for c in color)
            elif len(color) == 4:  # CMYK
                return all(c <= (1 - WHITE_COLOR_THRESHOLD) for c in color)
            elif len(color) == 1:  # Grayscale
                return color[0] >= WHITE_COLOR_THRESHOLD
        elif isinstance(color, (int, float)):
            return color >= WHITE_COLOR_THRESHOLD
    except (TypeError, IndexError):
        pass
    return False
