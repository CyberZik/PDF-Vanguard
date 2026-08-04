"""Off-page text detection module."""

import logging
from typing import List

import pdfplumber

from pdf_vanguard.core.models import Finding
from pdf_vanguard.detector.modules.base import BaseDetector

logger = logging.getLogger(__name__)


class OffPageDetector(BaseDetector):
    """Detect text placed at coordinates outside the visible page area."""

    name = "Off-Page Detector"
    description = "Detects text placed outside visible page boundaries"

    def scan(self, filepath: str) -> List[Finding]:
        findings = []
        try:
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_width = page.width
                    page_height = page.height
                    chars = page.chars

                    offpage_chars = []
                    for char in chars:
                        x = char.get("x0", 0)
                        y = char.get("top", 0)
                        # Check if character is outside visible page boundaries
                        if x < -10 or x > page_width + 10 or y < -10 or y > page_height + 10:
                            offpage_chars.append(char)

                    if offpage_chars:
                        sample_text = "".join(c.get("text", "") for c in offpage_chars[:50])
                        findings.append(Finding(
                            technique="Off-Page Text",
                            severity="HIGH",
                            description=f"Found {len(offpage_chars)} characters placed outside visible page area",
                            evidence=f"Sample: '{sample_text[:80]}...'",
                            location=f"Page {page_num}",
                        ))

        except Exception as e:
            logger.warning("Off-page detection error: %s", e)
            findings.append(Finding(
                technique="Scan Error",
                severity="INFO",
                description=f"Off-page detection error: {e}",
            ))
        return findings
