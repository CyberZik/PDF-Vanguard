"""Text extraction comparison detection module."""

import logging
from typing import List

import pdfplumber
from pypdf import PdfReader

from pdf_vanguard.core.models import Finding
from pdf_vanguard.detector.modules.base import BaseDetector
from pdf_vanguard.detector.modules.patterns import detect_injection_patterns

logger = logging.getLogger(__name__)


class ExtractionDetector(BaseDetector):
    """Compare text extracted by different methods.

    Large discrepancies may indicate hidden text that only some
    extractors capture.
    """

    name = "Extraction Comparator"
    description = "Detects discrepancies between text extraction methods"

    def scan(self, filepath: str) -> List[Finding]:
        findings = []
        try:
            # Method 1: pypdf extraction
            reader = PdfReader(filepath)
            pypdf_text = ""
            for page in reader.pages:
                pypdf_text += (page.extract_text() or "")

            # Method 2: pdfplumber extraction (respects layout)
            plumber_text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    plumber_text += (page.extract_text() or "")

            # Compare lengths — significant difference indicates hidden content
            len_diff = abs(len(pypdf_text) - len(plumber_text))
            max_len = max(len(pypdf_text), len(plumber_text), 1)
            discrepancy_pct = (len_diff / max_len) * 100

            if discrepancy_pct > 20:
                findings.append(Finding(
                    technique="Text Extraction Discrepancy",
                    severity="MEDIUM",
                    description=(
                        f"Different extractors return significantly different text "
                        f"({discrepancy_pct:.1f}% difference: pypdf={len(pypdf_text)} chars, "
                        f"pdfplumber={len(plumber_text)} chars)"
                    ),
                    evidence="This may indicate hidden text visible to some parsers but not others",
                    location="Full document",
                ))

            # Also check: does extracted text contain injection patterns?
            all_text = pypdf_text + " " + plumber_text
            text_findings = detect_injection_patterns(all_text, source="Extracted Text")
            findings.extend(text_findings)

        except Exception as e:
            logger.warning("Text comparison error: %s", e)
            findings.append(Finding(
                technique="Scan Error",
                severity="INFO",
                description=f"Text comparison error: {e}",
            ))
        return findings
