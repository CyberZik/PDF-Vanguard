"""Tests for risk scoring and deduplication."""

from pdf_vanguard.core.models import Finding, ScanReport


def _report(*findings):
    r = ScanReport(filepath="x.pdf")
    for f in findings:
        r.add_finding(f)
    r.calculate_risk()
    return r


def test_duplicate_findings_do_not_saturate_score():
    many = _report(*[
        Finding(technique="Prompt Injection Pattern", severity="CRITICAL",
                description="dup", location=f"stream{i}")
        for i in range(25)
    ])
    single = _report(
        Finding(technique="Prompt Injection Pattern", severity="CRITICAL", description="one")
    )
    # 25 copies of one technique score the same as one copy of it.
    assert many.risk_score == single.risk_score


def test_more_distinct_techniques_scores_higher():
    one = _report(
        Finding(technique="Off-Page Text", severity="HIGH", description="a"),
    )
    three = _report(
        Finding(technique="Off-Page Text", severity="HIGH", description="a"),
        Finding(technique="White Text Injection", severity="HIGH", description="b"),
        Finding(technique="Micro Font Injection", severity="HIGH", description="c"),
    )
    assert three.risk_score > one.risk_score


def test_clean_report_is_zero():
    assert _report().risk_score == 0
    assert _report().risk_level == "CLEAN"


def test_score_capped_at_100():
    r = _report(*[
        Finding(technique=f"T{i}", severity="CRITICAL", description="x")
        for i in range(50)
    ])
    assert r.risk_score <= 100
