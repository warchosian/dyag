"""
Command to generate detailed evaluation reports from RAG evaluation results.
"""

import sys
from pathlib import Path
from dyag.rag.report_generator import generate_report_from_file


def run_generate_evaluation_report(args):
    """Run generate-evaluation-report command with parsed args"""

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Results file not found: {args.input}", file=sys.stderr)
        return 1

    # Set default output path
    if not args.output:
        args.output = str(input_path.stem) + "_report.md"

    if args.verbose:
        print("=" * 80)
        print("GENERATE EVALUATION REPORT")
        print("=" * 80)
        print(f"Input: {args.input}")
        print(f"Output: {args.output}")
        print("=" * 80)
        print()

    try:
        # Generate report
        generate_report_from_file(
            results_file=str(input_path),
            output_path=args.output,
            verbose=args.verbose
        )

        if args.verbose:
            print()
            print("=" * 80)
            print(f"[OK] Rapport genere avec succes: {args.output}")
            print("=" * 80)

        return 0

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
