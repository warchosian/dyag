"""
Commands module for dyag.
Contains all command implementations.
"""

from dyag.commands.img2pdf import register_img2pdf_command
from dyag.commands.compresspdf import register_compresspdf_command
from dyag.commands.md2html import register_md2html_command
from dyag.commands.html2md import register_html2md_command
from dyag.commands.concat_html import register_concat_html_command
from dyag.commands.add_toc import register_add_toc_command
from dyag.commands.html2pdf import register_html2pdf_command
from dyag.commands.project2md import register_project2md_command
from dyag.commands.make_interactive import register_make_interactive_command
from dyag.commands.flatten_wikisi import register_flatten_wikisi_command

__all__ = [
    "register_img2pdf_command",
    "register_compresspdf_command",
    "register_md2html_command",
    "register_html2md_command",
    "register_concat_html_command",
    "register_add_toc_command",
    "register_html2pdf_command",
    "register_project2md_command",
    "register_make_interactive_command",
    "register_flatten_wikisi_command"
]
