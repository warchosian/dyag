#!/usr/bin/env python3
"""
MCP Server for dyag - Allows AI assistants to use dyag tools directly.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from dyag.commands.img2pdf import images_to_pdf
from dyag.commands.compresspdf import compress_pdf
from dyag.commands.md2html import process_markdown_to_html


class MCPServer:
    """MCP Server implementation for dyag."""

    def __init__(self):
        self.tools = {
            "dyag_img2pdf": {
                "description": "Convert images in a directory to a PDF file. Images are sorted alphabetically by filename.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Path to directory containing images"
                        },
                        "output": {
                            "type": "string",
                            "description": "Optional output PDF path. If not specified, creates PDF in source directory with directory name"
                        },
                        "compress": {
                            "type": "boolean",
                            "description": "Enable compression to reduce PDF size",
                            "default": False
                        },
                        "quality": {
                            "type": "integer",
                            "description": "JPEG quality for compression (1-100, default 85)",
                            "default": 85,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Show detailed progress",
                            "default": False
                        }
                    },
                    "required": ["directory"]
                }
            },
            "dyag_compresspdf": {
                "description": "Compress an existing PDF file by reprocessing its images with JPEG compression.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Path to input PDF file to compress"
                        },
                        "output": {
                            "type": "string",
                            "description": "Optional output PDF path. If not specified, adds '_compressed' suffix"
                        },
                        "quality": {
                            "type": "integer",
                            "description": "JPEG quality for compression (1-100, default 85). Lower values = smaller file size but lower quality",
                            "default": 85,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Show detailed progress",
                            "default": False
                        }
                    },
                    "required": ["input"]
                }
            },
            "dyag_md2html": {
                "description": "Convert Markdown files with diagrams (Graphviz, PlantUML, Mermaid) to HTML with embedded SVG graphics. Supports tables, code blocks, and standard markdown formatting.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "markdown": {
                            "type": "string",
                            "description": "Path to input Markdown file to convert"
                        },
                        "output": {
                            "type": "string",
                            "description": "Optional output HTML path. If not specified, uses same name with .html extension"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Show detailed conversion progress including diagram conversion status",
                            "default": False
                        },
                        "standalone": {
                            "type": "boolean",
                            "description": "Generate standalone HTML with CSS and full page structure (default true)",
                            "default": True
                        }
                    },
                    "required": ["markdown"]
                }
            }
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools."""
        return [
            {
                "name": name,
                "description": info["description"],
                "inputSchema": info["inputSchema"]
            }
            for name, info in self.tools.items()
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        try:
            if name == "dyag_img2pdf":
                result_code = images_to_pdf(
                    directory=arguments["directory"],
                    output_path=arguments.get("output"),
                    verbose=arguments.get("verbose", False),
                    compress=arguments.get("compress", False),
                    quality=arguments.get("quality", 85)
                )

                if result_code == 0:
                    output_path = arguments.get("output")
                    if output_path is None:
                        dir_path = Path(arguments["directory"]).resolve()
                        output_path = str(dir_path / (dir_path.name + ".pdf"))

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Successfully created PDF: {output_path}"
                            }
                        ]
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "Failed to create PDF"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_compresspdf":
                result_code = compress_pdf(
                    input_path=arguments["input"],
                    output_path=arguments.get("output"),
                    quality=arguments.get("quality", 85),
                    verbose=arguments.get("verbose", False)
                )

                if result_code == 0:
                    output_path = arguments.get("output")
                    if output_path is None:
                        pdf_path = Path(arguments["input"]).resolve()
                        output_path = str(pdf_path.parent / f"{pdf_path.stem}_compressed{pdf_path.suffix}")

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Successfully compressed PDF: {output_path}"
                            }
                        ]
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "Failed to compress PDF"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_md2html":
                result_code = process_markdown_to_html(
                    markdown_path=arguments["markdown"],
                    output_path=arguments.get("output"),
                    verbose=arguments.get("verbose", False),
                    standalone=arguments.get("standalone", True)
                )

                if result_code == 0:
                    output_path = arguments.get("output")
                    if output_path is None:
                        md_path = Path(arguments["markdown"]).resolve()
                        output_path = str(md_path.parent / (md_path.stem + ".html"))

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Successfully converted Markdown to HTML: {output_path}\nDiagrams (Graphviz, PlantUML, Mermaid) have been converted to embedded SVG graphics."
                            }
                        ]
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "Failed to convert Markdown to HTML"
                            }
                        ],
                        "isError": True
                    }

            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown tool: {name}"
                        }
                    ],
                    "isError": True
                }

        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing tool: {str(e)}"
                    }
                ],
                "isError": True
            }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request."""
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/list":
            return {
                "tools": self.list_tools()
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return self.call_tool(tool_name, arguments)
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    def run(self):
        """Run the MCP server in stdio mode."""
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)


def main():
    """Main entry point for MCP server."""
    server = MCPServer()
    server.run()


if __name__ == "__main__":
    main()
