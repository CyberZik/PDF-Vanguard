"""Hidden OCG (Optional Content Group) layer detection module."""

import logging
from typing import List

import pikepdf

from pdf_vanguard.core.models import Finding
from pdf_vanguard.detector.modules.base import BaseDetector

logger = logging.getLogger(__name__)


class OCGLayerDetector(BaseDetector):
    """Detect Optional Content Groups with visibility set to OFF."""

    name = "OCG Layer Scanner"
    description = "Detects hidden Optional Content Groups"

    def scan(self, filepath: str) -> List[Finding]:
        findings = []
        try:
            with pikepdf.open(filepath) as pdf:
                root = pdf.Root
                if "/OCProperties" not in root:
                    return findings

                oc_props = root["/OCProperties"]
                findings.append(Finding(
                    technique="Optional Content Groups Present",
                    severity="MEDIUM",
                    description="PDF contains Optional Content Groups (layer system)",
                    location="Document Root /OCProperties",
                ))

                # Check for layers set to OFF
                if "/D" in oc_props:
                    default_config = oc_props["/D"]
                    if "/OFF" in default_config:
                        off_layers = default_config["/OFF"]
                        if len(off_layers) > 0:
                            layer_names = []
                            for layer_ref in off_layers:
                                try:
                                    layer = layer_ref
                                    if "/Name" in layer:
                                        layer_names.append(str(layer["/Name"]))
                                except Exception:
                                    layer_names.append("[unnamed]")

                            findings.append(Finding(
                                technique="Hidden OCG Layer",
                                severity="CRITICAL",
                                description=f"Found {len(off_layers)} layer(s) with visibility OFF (hidden content)",
                                evidence=f"Hidden layers: {', '.join(layer_names)}",
                                location="Document Root /OCProperties/D/OFF",
                            ))

                # Check total layer count
                if "/OCGs" in oc_props:
                    total_layers = len(oc_props["/OCGs"])
                    if total_layers > 3:
                        findings.append(Finding(
                            technique="Suspicious Layer Count",
                            severity="LOW",
                            description=f"PDF contains {total_layers} content layers (unusual for a resume/document)",
                            location="Document Root /OCProperties/OCGs",
                        ))

        except Exception as e:
            logger.warning("OCG detection error: %s", e)
            findings.append(Finding(
                technique="Scan Error",
                severity="INFO",
                description=f"OCG detection error: {e}",
            ))
        return findings
