"""CLI entry point for the PDF injection tool (Red Team)."""

import argparse
import logging
import sys

from pdf_vanguard.injector.engine import inject_pdf
from pdf_vanguard.injector.techniques import TECHNIQUE_REGISTRY, ALL_TECHNIQUE_FLAGS
from pdf_vanguard.core.constants import DEFAULT_PAYLOAD


def main():
    parser = argparse.ArgumentParser(
        description="PDF-Vanguard Injector — Inject hidden prompt injection payloads into PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pdf-inject resume.pdf
  pdf-inject resume.pdf -o injected.pdf
  pdf-inject resume.pdf -t white meta ocg
  pdf-inject resume.pdf -p "Ignore previous instructions..."
  pdf-inject resume.pdf --list

Techniques:
  white    White text (color matches background)
  micro    Micro font size (0.5pt near-white)
  meta     Metadata fields (XMP + DocumentInfo)
  offpage  Off-page coordinates (-5000, -5000)
  zwc      Zero-width Unicode character encoding
  ocg      Hidden Optional Content Group layer
  all      Apply all techniques (default)
        """
    )
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("-o", "--output", help="Output PDF file path (default: input_injected.pdf)")
    parser.add_argument("-t", "--techniques", nargs="+", default=["all"],
                        choices=ALL_TECHNIQUE_FLAGS + ["all"],
                        help="Injection techniques to apply (default: all)")
    parser.add_argument("-p", "--payload", default=DEFAULT_PAYLOAD,
                        help="Custom payload text to inject")
    parser.add_argument("--list", action="store_true",
                        help="List all available techniques and exit")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="  %(message)s",
    )

    if args.list:
        print("\nAvailable injection techniques:")
        for flag, technique in TECHNIQUE_REGISTRY.items():
            stars = '*' * technique.stealth_level + '.' * (5 - technique.stealth_level)
            print(f"  {flag:8s} - {technique.name} (stealth: {stars})")
        sys.exit(0)

    # Resolve techniques
    if "all" in args.techniques:
        techniques = ALL_TECHNIQUE_FLAGS
    else:
        techniques = args.techniques

    # Print header
    print(f"\n{'=' * 65}")
    print(f"  PDF-Vanguard Injector (Red Team)")
    print(f"{'=' * 65}")
    print(f"  Input:      {args.input}")
    print(f"  Output:     {args.output or '(auto)'}")
    print(f"  Payload:    {args.payload[:60]}...")
    print(f"  Techniques: {', '.join(techniques)}")
    print(f"{'=' * 65}\n")

    try:
        summary = inject_pdf(
            input_path=args.input,
            output_path=args.output,
            techniques=techniques,
            payload=args.payload,
        )
    except FileNotFoundError as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")
        sys.exit(2)

    # Print summary
    print(f"\n{'-' * 65}")
    print(f"  INJECTION SUMMARY")
    print(f"{'-' * 65}")
    print(f"  Pages:         {summary.original_pages}")
    print(f"  Original size: {summary.original_size:,} bytes")
    print(f"  Output size:   {summary.output_size:,} bytes (+{summary.output_size - summary.original_size:,})")
    print(f"  Techniques applied:")
    for r in summary.results:
        icon = "+" if r.status == "OK" else "x"
        print(f"    {icon} [{r.technique_flag:7s}] {r.technique_name}")
    print(f"\n  Output saved: {summary.output_path}")
    print(f"{'=' * 65}\n")


if __name__ == "__main__":
    main()
