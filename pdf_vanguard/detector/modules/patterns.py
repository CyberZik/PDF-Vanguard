"""Prompt injection pattern matching module."""

import logging
import re
from typing import List

from pdf_vanguard.core.models import Finding
from pdf_vanguard.core.constants import INJECTION_PATTERNS
from pdf_vanguard.detector.modules.base import BaseDetector

logger = logging.getLogger(__name__)


def detect_injection_patterns(text: str, source: str = "body") -> List[Finding]:
    """Scan text for known prompt injection patterns.

    This is a standalone utility function used by multiple detection modules.

    Args:
        text: The text to scan.
        source: Label for where the text came from (e.g., "Metadata/Subject").

    Returns:
        List of Finding objects for each pattern match.
    """
    findings = []
    for pattern in INJECTION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            match = re.search(pattern, text, re.IGNORECASE)
            snippet = text[max(0, match.start() - 20): match.end() + 20].strip()
            findings.append(Finding(
                technique="Prompt Injection Pattern",
                severity="CRITICAL",
                description=f"Detected injection keyword pattern in {source}: /{pattern}/",
                evidence=f"...{snippet}...",
                location=source,
            ))
    return findings


class PatternDetector(BaseDetector):
    """Pattern matching detector — used as a utility by other modules.

    The scan() method returns an empty list because pattern matching
    is invoked by MetadataDetector and ExtractionDetector directly
    via the detect_injection_patterns() function.
    """

    name = "Pattern Matcher"
    description = "Detects common prompt injection phrases via regex"

    def scan(self, filepath: str) -> List[Finding]:
        # Pattern matching is invoked by other modules, not standalone
        return []
