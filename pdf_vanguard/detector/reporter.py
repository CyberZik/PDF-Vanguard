"""Report formatting and export for scan results."""

import json
import os
from dataclasses import asdict
from typing import List

from pdf_vanguard.core.models import ScanReport

# ── ANSI color codes ─────────────────────────────────────────────
SEVERITY_COLORS = {
    "CRITICAL": "\033[91m",  # Red
    "HIGH": "\033[93m",      # Yellow
    "MEDIUM": "\033[33m",    # Orange
    "LOW": "\033[36m",       # Cyan
    "INFO": "\033[37m",      # Gray
}

RISK_COLORS = {
    "CRITICAL": "\033[91m",
    "HIGH": "\033[93m",
    "MEDIUM": "\033[33m",
    "LOW": "\033[36m",
    "CLEAN": "\033[92m",
}

RESET = "\033[0m"
BOLD = "\033[1m"


def print_report(report: ScanReport) -> None:
    """Pretty-print a scan report to the terminal."""
    risk_color = RISK_COLORS.get(report.risk_level, RESET)

    print(f"\n{'-' * 70}")
    print(f"{BOLD}SCAN REPORT: {os.path.basename(report.filepath)}{RESET}")
    print(f"{'-' * 70}")
    print(f"  File:       {report.filepath}")
    print(f"  Size:       {report.file_size:,} bytes")
    print(f"  Pages:      {report.page_count}")
    print(f"  Scan Time:  {report.scan_time}")
    print(f"  Findings:   {len(report.findings)}")
    print(f"  Risk Score: {risk_color}{BOLD}{report.risk_score}/100 ({report.risk_level}){RESET}")
    print(f"{'-' * 70}")

    if not report.findings:
        print(f"  {RISK_COLORS['CLEAN']}[OK] No suspicious content detected.{RESET}")
    else:
        for i, f in enumerate(report.findings, 1):
            color = SEVERITY_COLORS.get(f.severity, RESET)
            print(f"\n  {color}[{f.severity}]{RESET} Finding #{i}: {BOLD}{f.technique}{RESET}")
            print(f"    Description: {f.description}")
            if f.evidence:
                print(f"    Evidence:    {f.evidence[:120]}")
            if f.location:
                print(f"    Location:    {f.location}")

    print(f"\n{'-' * 70}\n")


def print_summary_table(reports: List[ScanReport]) -> None:
    """Print a summary table of multiple scan results."""
    print(f"\n{'=' * 70}")
    print(f"  SUMMARY")
    print(f"{'=' * 70}")
    print(f"  {'File':<42s} {'Findings':>8s}  {'Score':>5s}  {'Risk':>10s}")
    print(f"  {'-' * 42} {'-' * 8}  {'-' * 5}  {'-' * 10}")
    for r in reports:
        risk_color = RISK_COLORS.get(r.risk_level, RESET)
        name = os.path.basename(r.filepath)
        print(f"  {name:<42s} {len(r.findings):>8d}  {r.risk_score:>5d}  {risk_color}{r.risk_level:>10s}{RESET}")
    print(f"{'=' * 70}\n")


def export_json(report: ScanReport, output_path: str) -> None:
    """Export scan report as JSON file."""
    data = {
        "filepath": report.filepath,
        "scan_time": report.scan_time,
        "file_size": report.file_size,
        "page_count": report.page_count,
        "risk_score": report.risk_score,
        "risk_level": report.risk_level,
        "findings_count": len(report.findings),
        "findings": [asdict(f) for f in report.findings],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[*] JSON report exported: {output_path}")
