"""Abstract base class for injection techniques."""

from abc import ABC, abstractmethod

import pikepdf

from pdf_vanguard.core.models import InjectionResult


class BaseTechnique(ABC):
    """Base class that all injection techniques must inherit from."""

    name: str = ""           # Human-readable name
    flag: str = ""           # CLI flag (e.g., "white")
    stealth_level: int = 0   # 1-5 rating

    @abstractmethod
    def inject(self, pdf: pikepdf.Pdf, payload: str) -> InjectionResult:
        """Apply this injection technique to the PDF.

        Args:
            pdf: An open pikepdf.Pdf object to modify in-place.
            payload: The prompt injection payload text.

        Returns:
            InjectionResult with status and detail.
        """

    def _ok(self, detail: str) -> InjectionResult:
        """Helper to create a successful result."""
        return InjectionResult(
            technique_flag=self.flag,
            technique_name=self.name,
            detail=detail,
            status="OK",
        )

    def _fail(self, error: str) -> InjectionResult:
        """Helper to create a failed result."""
        return InjectionResult(
            technique_flag=self.flag,
            technique_name=self.name,
            detail=error,
            status="FAIL",
        )
