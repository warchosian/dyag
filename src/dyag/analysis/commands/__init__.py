"""Commandes d'analyse et génération - DYAG"""

from .analyze_training import analyze_training_coverage
from .generate_evaluation_report import run_generate_evaluation_report
from .generate_questions import run_generate_questions
from .merge_evaluation import run_merge_evaluation
from .analyze_evaluation import run_analyze_evaluation
from .project2md import register_project2md_command
from .md2project import register_md2project_command
from .fix_encoding import fix_encoding

__all__ = [
    "analyze_training_coverage",
    "run_generate_evaluation_report",
    "run_generate_questions",
    "run_merge_evaluation",
    "run_analyze_evaluation",
    "register_project2md_command",
    "register_md2project_command",
    "fix_encoding",
]
