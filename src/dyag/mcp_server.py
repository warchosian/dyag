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
from dyag.commands.analyze_training import analyze_training_coverage
from dyag.rag_query import RAGQuerySystem
from dyag.commands.evaluate_rag import load_dataset, evaluate_rag
from dyag.commands.index_rag import ChunkIndexer


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
            },
            "dyag_analyze_training": {
                "description": "Analyze training data coverage for applications. Compares an applications file with training data to calculate which applications are covered and coverage statistics.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "applications": {
                            "type": "string",
                            "description": "Path to applications file (JSON or Markdown format)"
                        },
                        "training": {
                            "type": "string",
                            "description": "Path to training data file (JSONL format)"
                        }
                    },
                    "required": ["applications", "training"]
                }
            },
            "dyag_rag_query": {
                "description": "Query the RAG (Retrieval Augmented Generation) system with a question. Searches relevant chunks from the indexed knowledge base and generates an answer using an LLM.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Question to ask the RAG system"
                        },
                        "n_chunks": {
                            "type": "integer",
                            "description": "Number of context chunks to retrieve (default: 5)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        },
                        "collection": {
                            "type": "string",
                            "description": "ChromaDB collection name (default: applications)",
                            "default": "applications"
                        },
                        "chroma_path": {
                            "type": "string",
                            "description": "Path to ChromaDB database (default: ./chroma_db)",
                            "default": "./chroma_db"
                        }
                    },
                    "required": ["question"]
                }
            },
            "dyag_evaluate_rag": {
                "description": "Evaluate the RAG system using a dataset of question/answer pairs. Tests accuracy, performance, and generates detailed evaluation report.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset": {
                            "type": "string",
                            "description": "Path to JSONL dataset file with question/answer pairs"
                        },
                        "n_chunks": {
                            "type": "integer",
                            "description": "Number of context chunks per question (default: 5)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        },
                        "max_questions": {
                            "type": "integer",
                            "description": "Max number of questions to test (default: all)",
                            "minimum": 1
                        },
                        "output": {
                            "type": "string",
                            "description": "Output JSON file for detailed results"
                        },
                        "collection": {
                            "type": "string",
                            "description": "ChromaDB collection name (default: applications)",
                            "default": "applications"
                        },
                        "chroma_path": {
                            "type": "string",
                            "description": "Path to ChromaDB database (default: ./chroma_db)",
                            "default": "./chroma_db"
                        }
                    },
                    "required": ["dataset"]
                }
            },
            "dyag_index_rag": {
                "description": "Index chunks into ChromaDB for RAG (Retrieval Augmented Generation). Creates a vector database from JSON/JSONL chunk files for semantic search.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Path to JSONL or JSON file containing chunks to index"
                        },
                        "collection": {
                            "type": "string",
                            "description": "ChromaDB collection name (default: applications)",
                            "default": "applications"
                        },
                        "chroma_path": {
                            "type": "string",
                            "description": "Path to ChromaDB database (default: ./chroma_db)",
                            "default": "./chroma_db"
                        },
                        "embedding_model": {
                            "type": "string",
                            "description": "Sentence transformer model for embeddings (default: all-MiniLM-L6-v2)",
                            "default": "all-MiniLM-L6-v2"
                        },
                        "batch_size": {
                            "type": "integer",
                            "description": "Batch size for indexing (default: 100)",
                            "default": 100,
                            "minimum": 1
                        },
                        "reset": {
                            "type": "boolean",
                            "description": "Reset collection before indexing (deletes existing data)",
                            "default": False
                        }
                    },
                    "required": ["input"]
                }
            },
            "dyag_generate_questions": {
                "description": "Generate question/answer pairs from structured Markdown documents for RAG evaluation and model fine-tuning. Supports multiple output formats (rag, finetuning, simple) with automatic category detection and validation.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Path to structured Markdown file containing applications or documentation"
                        },
                        "output": {
                            "type": "string",
                            "description": "Output file path (default: {input_stem}_questions)"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["rag", "finetuning", "simple", "all"],
                            "description": "Output format: 'rag' for RAG evaluation, 'finetuning' for model training, 'simple' for basic prompt/completion, 'all' for all formats (default: rag)",
                            "default": "rag"
                        },
                        "questions_per_section": {
                            "type": "integer",
                            "description": "Number of questions to generate per section (default: 3)",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 10
                        },
                        "categories": {
                            "type": "string",
                            "description": "Comma-separated list of question categories (default: all). Available: status,domains,description,contacts,events,websites,actors,related_apps,metadata",
                            "default": "all"
                        },
                        "difficulty": {
                            "type": "string",
                            "description": "Comma-separated difficulty levels (default: easy,medium,hard)",
                            "default": "easy,medium,hard"
                        },
                        "system_prompt": {
                            "type": "string",
                            "description": "Custom system prompt for finetuning format (uses default expert assistant prompt if not specified)"
                        }
                    },
                    "required": ["input"]
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

            elif name == "dyag_analyze_training":
                # Capture stdout to return as MCP response
                import io
                from contextlib import redirect_stdout, redirect_stderr

                stdout_buffer = io.StringIO()
                stderr_buffer = io.StringIO()

                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    result_code = analyze_training_coverage(
                        app_file=arguments["applications"],
                        training_file=arguments["training"]
                    )

                output = stdout_buffer.getvalue()
                errors = stderr_buffer.getvalue()

                if result_code == 0:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Training coverage analysis completed successfully.\n\n{output}"
                            }
                        ]
                    }
                else:
                    error_text = errors if errors else "Failed to analyze training coverage"
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Analysis failed:\n{error_text}\n\nOutput:\n{output}"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_rag_query":
                try:
                    # Initialize RAG system
                    rag = RAGQuerySystem(
                        chroma_path=arguments.get("chroma_path", "./chroma_db"),
                        collection_name=arguments.get("collection", "applications")
                    )

                    # Query RAG
                    result = rag.ask(
                        question=arguments["question"],
                        n_chunks=arguments.get("n_chunks", 5)
                    )

                    # Format response
                    response_text = f"**Question:** {arguments['question']}\n\n"
                    response_text += f"**Réponse:**\n{result['answer']}\n\n"
                    response_text += f"**Sources:** {len(result['sources'])} chunks\n"
                    response_text += f"**Tokens:** {result.get('tokens_used', 0)}\n"
                    response_text += f"**Chunk IDs:** {', '.join(result['sources'][:5])}"
                    if len(result['sources']) > 5:
                        response_text += f"... (+{len(result['sources'])-5} more)"

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error querying RAG: {str(e)}"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_evaluate_rag":
                try:
                    # Load dataset
                    questions = load_dataset(arguments["dataset"])
                    if not questions:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "No questions found in dataset"
                                }
                            ],
                            "isError": True
                        }

                    # Initialize RAG
                    rag = RAGQuerySystem(
                        chroma_path=arguments.get("chroma_path", "./chroma_db"),
                        collection_name=arguments.get("collection", "applications")
                    )

                    # Evaluate
                    stats = evaluate_rag(
                        rag=rag,
                        questions=questions,
                        n_chunks=arguments.get("n_chunks", 5),
                        max_questions=arguments.get("max_questions"),
                        output_file=arguments.get("output")
                    )

                    # Format response
                    response_text = "**RAG Evaluation Results**\n\n"
                    response_text += f"Questions tested: {stats['total']}\n"
                    response_text += f"✓ Success: {stats['successful']} ({stats['successful']/stats['total']*100:.1f}%)\n"
                    response_text += f"✗ Failed: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)\n\n"

                    if stats['successful'] > 0:
                        avg_time = stats['total_time'] / stats['successful']
                        avg_tokens = stats['total_tokens'] / stats['successful']
                        response_text += f"**Performance:**\n"
                        response_text += f"Avg time: {avg_time:.1f}s\n"
                        response_text += f"Avg tokens: {avg_tokens:.0f}\n\n"

                    response_text += f"Total time: {stats['total_time']:.1f}s ({stats['total_time']/60:.1f} min)\n"
                    response_text += f"Total tokens: {stats['total_tokens']}\n"

                    if arguments.get("output"):
                        response_text += f"\n✓ Detailed results saved to: {arguments['output']}"

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error evaluating RAG: {str(e)}"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_index_rag":
                try:
                    # Verify input file exists
                    input_path = Path(arguments["input"])
                    if not input_path.exists():
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Input file not found: {arguments['input']}"
                                }
                            ],
                            "isError": True
                        }

                    # Create indexer
                    indexer = ChunkIndexer(
                        chroma_path=arguments.get("chroma_path", "./chroma_db"),
                        collection_name=arguments.get("collection", "applications"),
                        embedding_model=arguments.get("embedding_model", "all-MiniLM-L6-v2"),
                        reset_collection=arguments.get("reset", False)
                    )

                    # Load chunks
                    if input_path.suffix == '.jsonl':
                        chunks = indexer.load_chunks_from_jsonl(input_path)
                    elif input_path.suffix == '.json':
                        chunks = indexer.load_chunks_from_json(input_path)
                    else:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Unsupported file format: {input_path.suffix}. Use .jsonl or .json"
                                }
                            ],
                            "isError": True
                        }

                    if not chunks:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "No chunks found in file"
                                }
                            ],
                            "isError": True
                        }

                    # Index chunks
                    stats = indexer.index_chunks(
                        chunks,
                        batch_size=arguments.get("batch_size", 100),
                        show_progress=False  # Disable progress bar for MCP
                    )

                    # Get collection stats
                    collection_stats = indexer.get_stats()

                    # Format response
                    response_text = "**RAG Indexing Complete**\n\n"
                    response_text += f"File: {input_path.name}\n"
                    response_text += f"Collection: {arguments.get('collection', 'applications')}\n"
                    response_text += f"Embedding model: {arguments.get('embedding_model', 'all-MiniLM-L6-v2')}\n\n"
                    response_text += f"**Results:**\n"
                    response_text += f"✓ Indexed: {stats['indexed']} chunks\n"
                    response_text += f"✗ Errors: {stats['errors']}\n"
                    response_text += f"Success rate: {stats['success_rate']:.1f}%\n\n"
                    response_text += f"Total chunks in collection: {collection_stats['total_chunks']}"

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error indexing RAG: {str(e)}"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_generate_questions":
                try:
                    from dyag.commands.generate_questions import run_generate_questions
                    from argparse import Namespace

                    # Verify input file exists
                    input_path = Path(arguments["input"])
                    if not input_path.exists():
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Input file not found: {arguments['input']}"
                                }
                            ],
                            "isError": True
                        }

                    # Determine output path
                    output_base = arguments.get("output")
                    if not output_base:
                        output_base = f"{input_path.stem}_questions"

                    # Create args namespace compatible with run_generate_questions
                    args = Namespace(
                        input=str(input_path),
                        output=output_base,
                        format=arguments.get("format", "rag"),
                        system_prompt=arguments.get("system_prompt"),
                        mode="template",  # Currently only template mode is implemented
                        questions_per_section=arguments.get("questions_per_section", 3),
                        categories=arguments.get("categories", "all"),
                        difficulty=arguments.get("difficulty", "easy,medium,hard"),
                        language="fr",
                        verbose=False  # Disable verbose for MCP
                    )

                    # Run the command
                    result_code = run_generate_questions(args)

                    if result_code == 0:
                        # Determine which output files were created
                        format_type = arguments.get("format", "rag")

                        if format_type == "all":
                            files = [
                                f"{output_base}_rag.jsonl",
                                f"{output_base}_finetuning.jsonl",
                                f"{output_base}_simple.jsonl"
                            ]
                            files_text = "\n".join([f"  - {f}" for f in files])
                            response_text = f"**Questions Generated Successfully**\n\nOutput files:\n{files_text}\n\nAll formats have been generated: RAG evaluation, fine-tuning, and simple prompt/completion."
                        else:
                            output_file = f"{output_base}_{format_type}.jsonl"
                            format_names = {
                                "rag": "RAG evaluation",
                                "finetuning": "model fine-tuning",
                                "simple": "simple prompt/completion"
                            }
                            response_text = f"**Questions Generated Successfully**\n\nOutput file: {output_file}\nFormat: {format_names.get(format_type, format_type)}\n\nQuestions have been generated and validated."

                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": response_text
                                }
                            ]
                        }
                    else:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Failed to generate questions. Check that the input file has the expected Markdown structure."
                                }
                            ],
                            "isError": True
                        }

                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error generating questions: {str(e)}"
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
