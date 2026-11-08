"""PDF-Vanguard Injector — Red Team PDF prompt injection tool."""

from pdf_vanguard.injector.engine import inject_pdf
from pdf_vanguard.injector.techniques import ALL_TECHNIQUE_FLAGS, TECHNIQUE_REGISTRY

__all__ = ["inject_pdf", "ALL_TECHNIQUE_FLAGS", "TECHNIQUE_REGISTRY"]
