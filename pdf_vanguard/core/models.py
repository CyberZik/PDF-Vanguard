"""Shared data models for PDF-Vanguard."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Finding:
    """A single detection finding from a scan module."""
    technique: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    description: str
    evidence: str = ""
    location: str = ""


@dataclass
class ScanReport:
    """Aggregated scan results for a single PDF file."""
    filepath: str
    scan_time: str = ""
    file_size: int = 0
    page_count: int = 0
    findings: List[Finding] = field(default_factory=list)
    risk_score: int = 0
    risk_level: str = "CLEAN"

    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the report."""
        self.findings.append(finding)

    def calculate_risk(self) -> None:
        """Calculate risk score from findings. Capped at 100."""
        from pdf_vanguard.core.constants import SEVERITY_SCORES
        total = sum(SEVERITY_SCORES.get(f.severity, 0) for f in self.findings)
        self.risk_score = min(total, 100)
        if self.risk_score >= 60:
            self.risk_level = "CRITICAL"
        elif self.risk_score >= 40:
            self.risk_level = "HIGH"
        elif self.risk_score >= 20:
            self.risk_level = "MEDIUM"
        elif self.risk_score > 0:
            self.risk_level = "LOW"
        else:
            self.risk_level = "CLEAN"


@dataclass
class InjectionResult:
    """Result of a single injection technique application."""
    technique_flag: str
    technique_name: str
    detail: str
    status: str  # "OK" or "FAIL"


@dataclass
class InjectionSummary:
    """Overall summary of an injection job."""
    input_path: str
    output_path: str
    payload: str
    original_pages: int = 0
    original_size: int = 0
    output_size: int = 0
    results: List[InjectionResult] = field(default_factory=list)
