"""Metadata injection technique."""

import logging

import pikepdf

from pdf_vanguard.core.models import InjectionResult
from pdf_vanguard.injector.techniques.base import BaseTechnique

logger = logging.getLogger(__name__)


class MetadataTechnique(BaseTechnique):
    """Inject payload into PDF metadata fields.

    Targets DocumentInfo (/Subject, /Keywords) and XMP metadata
    (dc:description, dc:subject, pdf:Keywords).
    """

    name = "Metadata Injection"
    flag = "meta"
    stealth_level = 4

    def inject(self, pdf: pikepdf.Pdf, payload: str) -> InjectionResult:
        try:
            # DocumentInfo dictionary
            pdf.docinfo["/Subject"] = payload
            pdf.docinfo["/Keywords"] = payload

            # XMP metadata
            try:
                with pdf.open_metadata() as meta:
                    meta["dc:description"] = payload
                    meta["dc:subject"] = [payload]
                    meta["pdf:Keywords"] = payload
            except Exception as xmp_err:
                logger.warning("XMP metadata write failed (PDF may have locked XMP): %s", xmp_err)

            return self._ok("Metadata injection (DocumentInfo + XMP: Subject, Keywords, Description)")
        except Exception as e:
            logger.error("Metadata injection failed: %s", e)
            return self._fail(str(e))
