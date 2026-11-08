"""Detection module registry.

All detector classes are registered here for discovery by the engine.
"""

from pdf_vanguard.detector.modules.extraction import ExtractionDetector
from pdf_vanguard.detector.modules.invisible_text import InvisibleTextDetector
from pdf_vanguard.detector.modules.metadata import MetadataDetector
from pdf_vanguard.detector.modules.ocg_layers import OCGLayerDetector
from pdf_vanguard.detector.modules.offpage import OffPageDetector
from pdf_vanguard.detector.modules.unicode_chars import UnicodeDetector

# Ordered list of detection modules to run
DETECTOR_REGISTRY = [
    InvisibleTextDetector(),
    MetadataDetector(),
    OffPageDetector(),
    UnicodeDetector(),
    OCGLayerDetector(),
    ExtractionDetector(),
]
