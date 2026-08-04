"""Core data models and constants."""

from pdf_vanguard.core.models import Finding, ScanReport, InjectionResult, InjectionSummary
from pdf_vanguard.core.constants import (
    INJECTION_PATTERNS,
    INVISIBLE_CHARS,
    TAG_RANGE,
    MICRO_FONT_THRESHOLD,
    WHITE_COLOR_THRESHOLD,
    SEVERITY_SCORES,
    DEFAULT_PAYLOAD,
)
