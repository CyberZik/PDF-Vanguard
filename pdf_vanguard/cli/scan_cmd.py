"""CLI entry point for the PDF injection scanner (Blue Team)."""

import argparse
import logging
import os
import sys

from pdf_vanguard.detector.engine import scan_pdf
from pdf_vanguard.detector.reporter import print_report, print_summary_table, export_json


def main():
    parser = argparse.ArgumentParser(
        description="PDF-Vanguard Scanner — Detect prompt injection attacks in PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pdf-scan suspicious.pdf
  pdf-scan file1.pdf file2.pdf file3.pdf
  pdf-scan --output-dir results/
        """
    )
    parser.add_argument("files", nargs="*", help="PDF files to scan")
    parser.add_argument("--output-dir", default="scan_reports",
                        help="Directory for JSON reports (default: scan_reports/)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="  %(message)s",
    )

    # Determine files to scan
    if args.files:
        targets = args.files
    else:
        sample_dir = "test_samples"
        if os.path.isdir(sample_dir):
            targets = sorted([
                os.path.join(sample_dir, f)
                for f in os.listdir(sample_dir) if f.lower().endswith(".pdf")
            ])
        else:
            print(f"\n[!] No files specified and '{sample_dir}/' not found.")
            print(f"    Usage: pdf-scan <file1.pdf> [file2.pdf ...]")
            sys.exit(1)

    if not targets:
        print("[!] No PDF files found to scan.")
        sys.exit(1)

    # Header
    print("=" * 70)
    print("  PDF-Vanguard Scanner (Blue Team)")
    print("=" * 70)
    print(f"\n[*] Scanning {len(targets)} file(s)...\n")

    all_reports = []
    for filepath in targets:
        if not os.path.isfile(filepath):
            print(f"[!] File not found: {filepath}")
            continue
        print(f"[*] Scanning: {filepath}")
        report = scan_pdf(filepath)
        all_reports.append(report)
        print_report(report)

    # Summary table
    if len(all_reports) > 1:
        print_summary_table(all_reports)

    # Export JSON reports
    os.makedirs(args.output_dir, exist_ok=True)
    for r in all_reports:
        json_name = os.path.splitext(os.path.basename(r.filepath))[0] + "_report.json"
        export_json(r, os.path.join(args.output_dir, json_name))

    print(f"\n[OK] All scans complete. JSON reports saved in {args.output_dir}/")


if __name__ == "__main__":
    main()
