"""Injection engine — orchestrates the injection pipeline."""

import logging
import os
from typing import List, Optional

import pikepdf

from pdf_vanguard.core.constants import DEFAULT_PAYLOAD
from pdf_vanguard.core.models import InjectionSummary
from pdf_vanguard.injector.techniques import ALL_TECHNIQUE_FLAGS, TECHNIQUE_REGISTRY

logger = logging.getLogger(__name__)


def inject_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    techniques: Optional[List[str]] = None,
    payload: str = DEFAULT_PAYLOAD,
) -> InjectionSummary:
    """Inject hidden prompt injection payloads into a PDF.

    Args:
        input_path: Path to the source PDF file.
        output_path: Path for the output PDF. Defaults to {input}_injected.pdf.
        techniques: List of technique flags to apply. Defaults to all.
        payload: The injection payload text.

    Returns:
        InjectionSummary with results for each technique.

    Raises:
        FileNotFoundError: If input_path does not exist.
        pikepdf.PdfError: If the input file is not a valid PDF.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    # Resolve defaults
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_injected{ext}"

    if techniques is None:
        techniques = ALL_TECHNIQUE_FLAGS

    # Open and process
    pdf = pikepdf.open(input_path)
    original_pages = len(pdf.pages)
    original_size = os.path.getsize(input_path)

    summary = InjectionSummary(
        input_path=input_path,
        output_path=output_path,
        payload=payload,
        original_pages=original_pages,
        original_size=original_size,
    )

    for tech_flag in techniques:
        if tech_flag not in TECHNIQUE_REGISTRY:
            logger.warning("Unknown technique flag: %s, skipping", tech_flag)
            continue

        technique = TECHNIQUE_REGISTRY[tech_flag]
        logger.info("Applying: %s", technique.name)

        result = technique.inject(pdf, payload)
        summary.results.append(result)

        if result.status == "OK":
            logger.info("  \u2713 %s", result.detail)
        else:
            logger.warning("  \u2717 Failed: %s", result.detail)

    # Save output
    pdf.save(output_path)
    pdf.close()

    summary.output_size = os.path.getsize(output_path)
    logger.info("Output saved: %s", output_path)

    return summary
