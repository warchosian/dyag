"""
Generate question/answer pairs for RAG evaluation and fine-tuning
"""

import sys
from pathlib import Path

from ..question_generators import (
    MarkdownParser,
    TemplateQuestionGenerator,
    format_questions,
)


def run_generate_questions(args):
    """Run generate-questions command with parsed args"""

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Set default output path
    if not args.output:
        args.output = str(input_path.stem) + "_questions"

    # Parse categories and difficulty
    categories = [c.strip() for c in args.categories.split(",")]
    difficulty_levels = [d.strip() for d in args.difficulty.split(",")]

    if args.verbose:
        print("=" * 80)
        print("GENERATE QUESTIONS")
        print("=" * 80)
        print(f"Input: {args.input}")
        print(f"Output format: {args.format}")
        print(f"Mode: {args.mode}")
        print(f"Categories: {categories}")
        print(f"Difficulty: {difficulty_levels}")
        print(f"Questions per section: {args.questions_per_section}")
        print("=" * 80)
        print()

    try:
        # Parse Markdown
        if args.verbose:
            print("[1/3] Parsing Markdown...")
            print("-" * 80)

        parser = MarkdownParser(verbose=args.verbose)
        applications = parser.parse_file(str(input_path))

        if not applications:
            print("[ERROR] No applications found in document", file=sys.stderr)
            return 1

        if args.verbose:
            print(f"[OK] Extracted {len(applications)} applications")
            print()

        # Generate questions
        if args.verbose:
            print("[2/3] Generating questions...")
            print("-" * 80)

        if args.mode == "template":
            generator = TemplateQuestionGenerator(
                categories=categories,
                questions_per_section=args.questions_per_section,
                difficulty=difficulty_levels,
                verbose=args.verbose,
            )
            questions = generator.generate(applications)
            questions = generator.validate(questions)

        elif args.mode == "llm":
            print("[ERROR] LLM mode not yet implemented", file=sys.stderr)
            print("[INFO] Use --mode template for now", file=sys.stderr)
            return 1

        elif args.mode == "hybrid":
            print("[ERROR] Hybrid mode not yet implemented", file=sys.stderr)
            print("[INFO] Use --mode template for now", file=sys.stderr)
            return 1

        if not questions:
            print("[ERROR] No questions generated", file=sys.stderr)
            return 1

        if args.verbose:
            print(f"[OK] Generated {len(questions)} valid questions")
            print()

        # Format and save
        if args.verbose:
            print("[3/3] Formatting and saving...")
            print("-" * 80)

        output_files = format_questions(
            questions=questions,
            output_format=args.format,
            output_path=args.output,
            system_prompt=args.system_prompt,
            verbose=args.verbose,
        )

        if args.verbose:
            print()
            print("=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Applications processed: {len(applications)}")
            print(f"Questions generated: {len(questions)}")
            print(f"Output files:")
            for fmt, path in output_files.items():
                print(f"  - {fmt}: {path}")
            print("=" * 80)

        return 0

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
