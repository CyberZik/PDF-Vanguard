"""Metadata injection detection module."""

import logging
from typing import List

import pikepdf
from pypdf import PdfReader

from pdf_vanguard.core.models import Finding
from pdf_vanguard.detector.modules.base import BaseDetector
from pdf_vanguard.detector.modules.patterns import detect_injection_patterns

logger = logging.getLogger(__name__)


class MetadataDetector(BaseDetector):
    """Scan PDF metadata fields for prompt injection payloads.

    Checks DocumentInfo fields (Title, Author, Subject, Creator, Producer),
    XMP metadata, and flags unusually long metadata values.
    """

    name = "Metadata Analyzer"
    description = "Scans PDF metadata fields for injection payloads"

    def scan(self, filepath: str) -> List[Finding]:
        findings = []
        try:
            # Check standard metadata via pypdf
            reader = PdfReader(filepath)
            meta = reader.metadata
            if meta:
                meta_fields = {
                    "Title": meta.title,
                    "Author": meta.author,
                    "Subject": meta.subject,
                    "Creator": meta.creator,
                    "Producer": meta.producer,
                }
                for field_name, value in meta_fields.items():
                    if value and len(str(value)) > 0:
                        pattern_findings = detect_injection_patterns(
                            str(value), source=f"Metadata/{field_name}"
                        )
                        findings.extend(pattern_findings)

                        # Flag unusually long metadata
                        if len(str(value)) > 200:
                            findings.append(Finding(
                                technique="Suspicious Metadata",
                                severity="MEDIUM",
                                description=f"Metadata field '{field_name}' is unusually long ({len(str(value))} chars)",
                                evidence=str(value)[:100] + "...",
                                location=f"Metadata/{field_name}",
                            ))

            # Check XMP and DocumentInfo via pikepdf
            with pikepdf.open(filepath) as pdf:
                try:
                    with pdf.open_metadata() as xmp:
                        xmp_str = str(xmp)
                        if xmp_str:
                            xmp_findings = detect_injection_patterns(
                                xmp_str, source="XMP Metadata"
                            )
                            findings.extend(xmp_findings)
                except Exception as xmp_err:
                    logger.debug("XMP metadata read failed: %s", xmp_err)

                # Check DocumentInfo dictionary
                if pdf.docinfo:
                    for key, value in pdf.docinfo.items():
                        val_str = str(value)
                        if val_str:
                            di_findings = detect_injection_patterns(
                                val_str, source=f"DocumentInfo{key}"
                            )
                            findings.extend(di_findings)

        except Exception as e:
            logger.warning("Metadata scan error: %s", e)
            findings.append(Finding(
                technique="Scan Error",
                severity="INFO",
                description=f"Metadata scan error: {e}",
            ))
        return findings
