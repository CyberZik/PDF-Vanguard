"""Round-trip tests: each injection technique must be caught by a scan."""

import pytest

from pdf_vanguard.detector import scan_pdf

# technique flag -> substring expected in at least one finding's technique field
TECHNIQUE_EXPECTED = {
    "white": "White Text",
    "micro": "Micro Font",
    "meta": "Prompt Injection Pattern",
    "offpage": "Off-Page",
    "zwc": "Zero-Width",
    "ocg": "OCG",
}


@pytest.mark.parametrize("flag,expected", TECHNIQUE_EXPECTED.items())
def test_injection_is_detected(make_injected, flag, expected):
    report = scan_pdf(make_injected(flag))
    techniques = {f.technique for f in report.findings}
    assert any(expected in t for t in techniques), (
        f"{flag}: expected a '{expected}' finding, got {sorted(techniques)}"
    )
    assert report.risk_score > 0


def test_clean_pdf_has_no_findings(clean_pdf):
    report = scan_pdf(clean_pdf)
    real = [f for f in report.findings if f.severity != "INFO"]
    assert real == [], f"clean PDF flagged: {[f.technique for f in real]}"
    assert report.risk_score == 0
    assert report.risk_level == "CLEAN"


def test_scan_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        scan_pdf("does_not_exist_12345.pdf")
