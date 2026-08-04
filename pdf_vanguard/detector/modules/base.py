"""Abstract base class for detection modules."""

from abc import ABC, abstractmethod
from typing import List

from pdf_vanguard.core.models import Finding


class BaseDetector(ABC):
    """Base class that all detection modules must inherit from."""

    name: str = ""           # Module name
    description: str = ""    # What this module detects

    @abstractmethod
    def scan(self, filepath: str) -> List[Finding]:
        """Run this detection module against a PDF file.

        Args:
            filepath: Path to the PDF file to scan.

        Returns:
            List of Finding objects for any detections.
        """
