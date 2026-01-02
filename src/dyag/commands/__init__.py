"""
Commands module for dyag - LEGACY

Ce module est conservé pour compatibilité ascendante.
Les nouvelles commandes sont organisées dans les modules spécialisés:
- dyag.conversion.commands
- dyag.processing.commands
- dyag.analysis.commands
- dyag.rag.commands
- dyag.park.commands
- dyag.mcp.commands
"""

# Import depuis les nouveaux emplacements
from dyag.conversion.commands.img2pdf import register_img2pdf_command
from dyag.processing.commands.compress_pdf import register_compresspdf_command
from dyag.conversion.commands.md2html import register_md2html_command
from dyag.conversion.commands.html2md import register_html2md_command
from dyag.processing.commands.concat_html import register_concat_html_command
from dyag.processing.commands.add_toc4md import register_add_toc4md_command
from dyag.processing.commands.add_toc4html import register_add_toc4html_command
from dyag.conversion.commands.html2pdf import register_html2pdf_command
from dyag.analysis.commands.project2md import register_project2md_command
from dyag.analysis.commands.md2project import register_md2project_command
from dyag.processing.commands.make_interactive import register_make_interactive_command
from dyag.processing.commands.flatten_wikisi import register_flatten_wikisi_command
from dyag.processing.commands.flatten_md import register_flatten_md_command
from dyag.processing.commands.flatten_html import register_flatten_html_command
from dyag.processing.commands.merge_md import register_merge_md_command
from dyag.processing.commands.merge_html import register_merge_html_command
from dyag.analysis.commands.analyze_training import register_analyze_training_command
from dyag.rag.commands import (
    register_prepare_rag_command,
    register_evaluate_rag_command,
    register_compare_rag_command,
    register_index_rag_command,
    register_query_rag_command,
    register_markdown_to_rag_command,
    register_test_rag_command,
    register_rag_stats_command,
    register_show_evaluation_command,
    register_compare_evaluations_command,
)
from dyag.conversion.commands.json2md import register_json2md_command
from dyag.park.commands.json2md_park import register_parkjson2md_command
from dyag.park.commands.json2json_park import register_parkjson2json_command
from dyag.conversion.commands.json2jsonl import register_json2jsonl_command
from dyag.web.commands.web_server import register_web_server_command
from dyag.encoding.commands import register_chk_utf8_command, register_fix_utf8_command

def register_generate_evaluation_report_command(subparsers):
    """Register generate-evaluation-report command"""
    from dyag.analysis.commands.generate_evaluation_report import run_generate_evaluation_report

    parser = subparsers.add_parser(
        "generate-evaluation-report",
        help="Générer un rapport d'analyse détaillé des résultats d'évaluation RAG"
    )

    parser.add_argument("input", help="Fichier JSON des résultats d'évaluation")
    parser.add_argument("--output", help="Fichier de sortie (défaut: {input}_report.md)", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")

    parser.set_defaults(func=run_generate_evaluation_report)

def register_generate_questions_command(subparsers):
    """Register generate-questions command"""
    from dyag.analysis.commands.generate_questions import run_generate_questions

    parser = subparsers.add_parser(
        "generate-questions",
        help="Générer des questions/réponses pour RAG et fine-tuning"
    )

    parser.add_argument("input", help="Fichier Markdown source")
    parser.add_argument("--output", help="Fichier de sortie (défaut: {input}_questions.jsonl)", default=None)
    parser.add_argument("--format", choices=["rag", "finetuning", "simple", "all"], default="rag", help="Format de sortie (défaut: rag)")
    parser.add_argument("--system-prompt", help="Prompt système pour format finetuning", default=None)
    parser.add_argument("--mode", choices=["template", "llm", "hybrid"], default="template", help="Mode de génération (défaut: template)")
    parser.add_argument("--questions-per-section", type=int, default=3, help="Nombre de questions par section (défaut: 3)")
    parser.add_argument("--categories", help="Catégories de questions (séparées par des virgules, défaut: all)", default="all")
    parser.add_argument("--difficulty", help="Niveaux de difficulté (séparés par des virgules, défaut: easy,medium,hard)", default="easy,medium,hard")
    parser.add_argument("--language", default="fr", help="Langue des questions (défaut: fr)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")

    parser.set_defaults(func=run_generate_questions)

def register_merge_evaluation_command(subparsers):
    """Register merge-evaluation command"""
    from dyag.analysis.commands.merge_evaluation import run_merge_evaluation

    parser = subparsers.add_parser(
        "merge-evaluation",
        help="Fusionner plusieurs fichiers de résultats d'évaluation RAG"
    )

    parser.add_argument("files", nargs='*', help="Fichiers batch à fusionner (supporte wildcards)")
    parser.add_argument("--output", "-o", default="evaluation/results_merged.json", help="Fichier de sortie (défaut: evaluation/results_merged.json)")
    parser.add_argument("--pattern", "-p", help='Pattern glob pour auto-découverte (ex: "evaluation/results_*_batch*.json")')
    parser.add_argument("-v", "--verbose", action="store_true", help="Afficher progression détaillée")

    parser.set_defaults(func=run_merge_evaluation)

def register_analyze_evaluation_command(subparsers):
    """Register analyze-evaluation command"""
    from dyag.analysis.commands.analyze_evaluation import run_analyze_evaluation

    parser = subparsers.add_parser(
        "analyze-evaluation",
        help="Analyser les résultats d'évaluation RAG"
    )

    parser.add_argument("results_file", help="Fichier JSON de résultats à analyser")
    parser.add_argument("--detailed", "-d", action="store_true", help="Afficher analyses détaillées (apps, top échecs, distributions)")

    parser.set_defaults(func=run_analyze_evaluation)

__all__ = [
    "register_img2pdf_command",
    "register_compresspdf_command",
    "register_md2html_command",
    "register_html2md_command",
    "register_concat_html_command",
    "register_add_toc4md_command",
    "register_add_toc4html_command",
    "register_html2pdf_command",
    "register_project2md_command",
    "register_make_interactive_command",
    "register_flatten_wikisi_command",
    "register_flatten_html_command",
    "register_merge_html_command",
    "register_flatten_md_command",
    "register_merge_md_command",
    "register_analyze_training_command",
    "register_prepare_rag_command",
    "register_evaluate_rag_command",
    "register_compare_rag_command",
    "register_index_rag_command",
    "register_query_rag_command",
    "register_markdown_to_rag_command",
    "register_test_rag_command",
    "register_rag_stats_command",
    "register_show_evaluation_command",
    "register_compare_evaluations_command",
    "register_json2md_command",
    "register_parkjson2md_command",
    "register_parkjson2json_command",
    "register_json2jsonl_command",
    "register_generate_questions_command",
    "register_generate_evaluation_report_command",
    "register_merge_evaluation_command",
    "register_analyze_evaluation_command",
    "register_web_server_command",
    "register_chk_utf8_command",
    "register_fix_utf8_command"
]
