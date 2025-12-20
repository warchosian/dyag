"""
Formatters for different output formats (RAG, fine-tuning, simple)
"""

import json
from typing import List, Dict
from pathlib import Path

from .template_generator import Question
from .templates import DEFAULT_SYSTEM_PROMPT


def format_questions(
    questions: List[Question],
    output_format: str,
    output_path: str = None,
    system_prompt: str = None,
    verbose: bool = False,
) -> Dict[str, str]:
    """
    Format questions to specified format and save to file(s)

    Args:
        questions: List of Question objects
        output_format: One of 'rag', 'finetuning', 'simple', 'all'
        output_path: Base output path (without extension)
        system_prompt: System prompt for finetuning format
        verbose: Verbose output

    Returns:
        Dict mapping format to output file path
    """
    if output_format == "all":
        # Generate all formats
        return _format_all(questions, output_path, system_prompt, verbose)
    else:
        # Generate single format
        output_file = _get_output_filename(output_path, output_format)
        _format_single(questions, output_format, output_file, system_prompt, verbose)
        return {output_format: output_file}


def _format_all(
    questions: List[Question],
    base_path: str,
    system_prompt: str,
    verbose: bool,
) -> Dict[str, str]:
    """Format to all output formats"""
    results = {}

    for fmt in ["rag", "finetuning", "simple"]:
        output_file = _get_output_filename(base_path, fmt)
        _format_single(questions, fmt, output_file, system_prompt, verbose)
        results[fmt] = output_file

    return results


def _format_single(
    questions: List[Question],
    output_format: str,
    output_file: str,
    system_prompt: str,
    verbose: bool,
):
    """Format to a single output format"""
    if output_format == "rag":
        _format_rag(questions, output_file, verbose)
    elif output_format == "finetuning":
        _format_finetuning(questions, output_file, system_prompt, verbose)
    elif output_format == "simple":
        _format_simple(questions, output_file, verbose)
    else:
        raise ValueError(f"Unknown format: {output_format}")


def _get_output_filename(base_path: str, output_format: str) -> str:
    """Get output filename with appropriate suffix"""
    if not base_path:
        base_path = "questions"

    # Remove extension if present
    base = Path(base_path).stem
    parent = Path(base_path).parent

    # Add format suffix
    if output_format == "rag":
        filename = f"{base}_rag.jsonl"
    elif output_format == "finetuning":
        filename = f"{base}_finetuning.jsonl"
    elif output_format == "simple":
        filename = f"{base}_simple.jsonl"
    else:
        filename = f"{base}.jsonl"

    return str(parent / filename) if parent.name else filename


def _format_rag(questions: List[Question], output_file: str, verbose: bool):
    """Format for RAG evaluation"""
    if verbose:
        print(f"[FORMAT] RAG format -> {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        for q in questions:
            line = json.dumps(q.to_dict(), ensure_ascii=False)
            f.write(line + '\n')

    if verbose:
        print(f"  [OK] Wrote {len(questions)} questions")


def _format_finetuning(
    questions: List[Question],
    output_file: str,
    system_prompt: str,
    verbose: bool,
):
    """Format for fine-tuning (OpenAI/Anthropic style with messages)"""
    if verbose:
        print(f"[FORMAT] Fine-tuning format -> {output_file}")

    if not system_prompt:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    with open(output_file, 'w', encoding='utf-8') as f:
        for q in questions:
            # Create messages format
            entry = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": q.question},
                    {"role": "assistant", "content": _enhance_answer(q)},
                ]
            }

            line = json.dumps(entry, ensure_ascii=False)
            f.write(line + '\n')

    if verbose:
        print(f"  [OK] Wrote {len(questions)} question/answer pairs")


def _format_simple(questions: List[Question], output_file: str, verbose: bool):
    """Format for simple prompt/completion"""
    if verbose:
        print(f"[FORMAT] Simple format -> {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        for q in questions:
            entry = {
                "prompt": q.question,
                "completion": q.expected_answer,
            }

            line = json.dumps(entry, ensure_ascii=False)
            f.write(line + '\n')

    if verbose:
        print(f"  [OK] Wrote {len(questions)} prompt/completion pairs")


def _enhance_answer(question: Question) -> str:
    """
    Enhance answer for fine-tuning by adding context

    For fine-tuning, we want more complete answers that include
    the application name for context.
    """
    answer = question.expected_answer

    # For simple answers, add context
    if question.category in ["status", "domains", "websites"]:
        enhanced = f"L'application {question.app_name} {_get_verb(question.category)} {answer}."
        return enhanced

    # For more complex answers, return as-is
    return answer


def _get_verb(category: str) -> str:
    """Get appropriate verb for category"""
    verbs = {
        "status": "a le statut",
        "domains": "intervient dans le domaine",
        "websites": "est accessible à l'adresse",
        "contacts": "a pour contact",
        "description": "a pour description",
    }
    return verbs.get(category, "est")
