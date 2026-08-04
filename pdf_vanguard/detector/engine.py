"""Detection engine — orchestrates the scanning pipeline."""

import logging
import os
from datetime import datetime

from pypdf import PdfReader

from pdf_vanguard.core.models import ScanReport
from pdf_vanguard.detector.modules import DETECTOR_REGISTRY

logger = logging.getLogger(__name__)


def scan_pdf(filepath: str) -> ScanReport:
    """Run all detection modules on a PDF file.

    Args:
        filepath: Path to the PDF file to scan.

    Returns:
        ScanReport with all findings and risk score.

    Raises:
        FileNotFoundError: If filepath does not exist.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"PDF file not found: {filepath}")

    report = ScanReport(
        filepath=filepath,
        scan_time=datetime.now().isoformat(),
        file_size=os.path.getsize(filepath),
    )

    # Get page count
    try:
        reader = PdfReader(filepath)
        report.page_count = len(reader.pages)
    except Exception:
        report.page_count = -1

    # Run all detection modules
    total = len(DETECTOR_REGISTRY)
    for i, detector in enumerate(DETECTOR_REGISTRY, 1):
        logger.info("[%d/%d] %s", i, total, detector.name)
        findings = detector.scan(filepath)
        report.findings.extend(findings)

    # Calculate risk
    report.calculate_risk()
    return report
