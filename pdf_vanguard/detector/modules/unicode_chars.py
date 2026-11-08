"""Zero-width / invisible Unicode character detection module."""

import logging
from typing import Dict, List

from pypdf import PdfReader

from pdf_vanguard.core.constants import INVISIBLE_CHARS, TAG_RANGE
from pdf_vanguard.core.models import Finding
from pdf_vanguard.detector.modules.base import BaseDetector
from pdf_vanguard.detector.zwc_decoder import decode_zwc

logger = logging.getLogger(__name__)


class UnicodeDetector(BaseDetector):
    """Detect zero-width characters and Unicode tags in text content."""

    name = "Unicode Inspector"
    description = "Detects zero-width characters and Unicode tags"

    def scan(self, filepath: str) -> List[Finding]:
        findings = []
        try:
            reader = PdfReader(filepath)
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""

                # Check for known invisible characters
                found_invisible: Dict[str, int] = {}
                for char in text:
                    if char in INVISIBLE_CHARS:
                        name = INVISIBLE_CHARS[char]
                        found_invisible[name] = found_invisible.get(name, 0) + 1

                    # Check for Unicode Tags block
                    if ord(char) in TAG_RANGE:
                        tag_name = f"Unicode Tag U+{ord(char):05X}"
                        found_invisible[tag_name] = found_invisible.get(tag_name, 0) + 1

                if found_invisible:
                    total = sum(found_invisible.values())
                    detail = ", ".join(f"{name}: {count}" for name, count in found_invisible.items())

                    if total > 50:
                        severity = "CRITICAL"
                    elif total > 10:
                        severity = "HIGH"
                    else:
                        severity = "MEDIUM"

                    findings.append(Finding(
                        technique="Invisible Unicode Characters",
                        severity=severity,
                        description=f"Found {total} invisible/zero-width characters on page {page_num}",
                        evidence=detail,
                        location=f"Page {page_num}",
                    ))

                    # Attempt to decode zero-width steganography payload
                    decoded = decode_zwc(text)
                    if decoded:
                        snippet = decoded if len(decoded) <= 160 else decoded[:157] + "..."
                        findings.append(Finding(
                            technique="Decoded Zero-Width Payload",
                            severity="CRITICAL",
                            description=f"Decoded hidden zero-width payload on page {page_num}",
                            evidence=f"Hidden text: {snippet}",
                            location=f"Page {page_num}",
                        ))

        except Exception as e:
            logger.warning("Unicode detection error: %s", e)
            findings.append(Finding(
                technique="Scan Error",
                severity="INFO",
                description=f"Unicode detection error: {e}",
            ))
        return findings
