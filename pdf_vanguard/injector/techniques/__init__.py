"""Injection technique registry.

All technique classes are registered here for discovery by the engine.
"""

from pdf_vanguard.injector.techniques.white_text import WhiteTextTechnique
from pdf_vanguard.injector.techniques.micro_font import MicroFontTechnique
from pdf_vanguard.injector.techniques.metadata import MetadataTechnique
from pdf_vanguard.injector.techniques.offpage import OffPageTechnique
from pdf_vanguard.injector.techniques.zero_width import ZeroWidthTechnique
from pdf_vanguard.injector.techniques.ocg_layer import OCGLayerTechnique

# Registry: maps CLI flag -> technique instance
TECHNIQUE_REGISTRY = {
    "white": WhiteTextTechnique(),
    "micro": MicroFontTechnique(),
    "meta": MetadataTechnique(),
    "offpage": OffPageTechnique(),
    "zwc": ZeroWidthTechnique(),
    "ocg": OCGLayerTechnique(),
}

ALL_TECHNIQUE_FLAGS = list(TECHNIQUE_REGISTRY.keys())
