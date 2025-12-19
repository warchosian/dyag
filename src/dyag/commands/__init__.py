"""
Commands module for dyag.
Contains all command implementations.
"""

from dyag.commands.img2pdf import register_img2pdf_command
from dyag.commands.compresspdf import register_compresspdf_command
from dyag.commands.md2html import register_md2html_command
from dyag.commands.html2md import register_html2md_command
from dyag.commands.concat_html import register_concat_html_command
from dyag.commands.add_toc4md import register_add_toc4md_command
from dyag.commands.add_toc4html import register_add_toc4html_command
from dyag.commands.html2pdf import register_html2pdf_command
from dyag.commands.project2md import register_project2md_command
from dyag.commands.make_interactive import register_make_interactive_command
from dyag.commands.flatten_wikisi import register_flatten_wikisi_command
from dyag.commands.flatten_md import register_flatten_md_command
from dyag.commands.flatten_html import register_flatten_html_command
from dyag.commands.merge_md import register_merge_md_command
from dyag.commands.merge_html import register_merge_html_command
from dyag.commands.analyze_training import register_analyze_training_command
from dyag.commands.prepare_rag import register_prepare_rag_command
from dyag.commands.evaluate_rag import register_evaluate_rag_command
from dyag.commands.index_rag import register_index_rag_command
from dyag.commands.query_rag import register_query_rag_command
from dyag.commands.markdown_to_rag import register_markdown_to_rag_command
from dyag.commands.json2md import register_json2md_command
from dyag.commands.parkjson2md import register_parkjson2md_command

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
    "register_index_rag_command",
    "register_query_rag_command",
    "register_markdown_to_rag_command",
    "register_json2md_command",
    "register_parkjson2md_command"
]
