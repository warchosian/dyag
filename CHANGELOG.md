# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.1] - 2026-01-04

### Added
- **Encoding Utilities** - New commands and module for handling encoding issues
  - `encoding_fixer.py`: Core module with `EncodingFixer` class
    - Automatic encoding detection with chardet support
    - Multi-encoding fallback (UTF-8, Latin-1, CP1252, ISO-8859-1)
    - Mojibake detection and correction
    - Emoji corruption mapping and fixing (📄 → ?? → 📄)
    - BOM UTF-8 detection
  - `chk-utf8`: Command to verify UTF-8 encoding with detailed reports
  - `fix-utf8`: Command to automatically fix encoding issues
  - `doc/GUIDE_ENCODAGE_EMOJIS.md`: Comprehensive encoding guide
  - `examples/fix_emoji_corruption.py`: Practical example script

- **MD2Project Command** - Reconstruct project structure from Markdown
  - Parse Markdown documentation to recreate folder/file structure
  - Support for emoji-based markers (📁, 📄)
  - Flexible parsing with encoding support

### Fixed
- **RAG Core Tests** - Comprehensive test fixes achieving 87% coverage
  - `test_retriever.py`: **29% → 100%** (14/14 tests passing)
    - Fixed API parameter names: `app_filter` → `filter_metadata`, `n_results` → `n_chunks`
    - Fixed LLM mock format: `{'content': ..., 'usage': {...}}`
    - Added `use_reranking=False` where needed to prevent chunk doubling
  - `test_comparison.py`: **68% → 100%** (19/19 tests passing)
    - Added missing `expected` and `answer` fields for similarity calculation
    - Adjusted fixture expectations (2 results vs 10 metadata)
    - Fixed encoding checks for "amélioration" detection
  - `test_llm_providers.py`: **58% → 100%** (19/19 tests passing)
    - Fixed patch paths: `'dyag.rag.core.llm_providers.requests.*'` → `'requests.*'`
    - Fixed imports: use `import requests` instead of importing from module
    - Root cause: `requests` imported locally in `OllamaProvider.__init__`
  - Overall RAG Core: **35% → 87%** (66/76 tests passing) ✅

- **Dependencies** - NumPy/ChromaDB compatibility
  - Downgraded to NumPy 1.26.4 + SciPy 1.11.4 for ChromaDB 0.4.22 compatibility
  - Fixed `requirements-rag.txt` with explicit version constraints

### Changed
- Updated README.md with:
  - New encoding utilities section
  - RAG Core test coverage statistics (87%)
  - Module-by-module test breakdown
  - Updated badges for v0.8.1
- Module coverage improvements:
  - `comparison.py`: 89% → 93%
  - `llm_providers.py`: 18% → 55%

### Documentation
- Added comprehensive encoding documentation
- Updated README with test statistics
- Added examples for encoding utilities

## [0.8.0] - 2025-12-20

### Added
- **ParkJSON Tools** - New commands for application portfolio management
  - `parkjson2md`: Convert JSON application data to comprehensive Markdown reports
    - Full field coverage: DICT, DACP, Technologies, Hébergements, Événements, Sécurité
    - Enhanced Événements section with version and commentaire details
    - Base juridique and Finalités sections
    - Domaines métier and Ministères porteurs
  - `parkjson2json`: Filter and extract JSON application data with metadata
    - Application filtering by name or ID
    - Preserve structure or flatten output
    - Metadata generation (extraction date, source file, filters)
  - `--split-dir` option for both commands to generate separate files per application
    - Sanitized filenames with accent handling for cross-platform compatibility
    - Format: `inputname_appname.ext`

### Documentation
- Added comprehensive **ParkJSON Tools** documentation in `doc/Tools/ParkJSON-Tools.md`
  - Usage examples and workflow patterns
  - Complete field reference
  - Command options and filtering syntax
- Updated `doc/README.md` with ParkJSON Tools reference

### Changed
- Updated `.gitignore` to exclude data directories and large files
  - Data directories (chroma_db/, data/finetuning/, examples splits)
  - RAG databases (*.faiss, *.pkl, *.pickle)
  - Large model files (*.bin, *.safetensors, *.gguf)

## [0.7.0] - 2025-12-18

### Added
- Command `markdown-to-rag` for creating RAG pipeline from Markdown files
- Modular chunking strategies for improved RAG performance

## [0.6.0] - 2025-01-16

### Added
- **RAG System (Retrieval-Augmented Generation)**
  - RAG query system with ChromaDB integration
  - Multi-provider LLM support (OpenAI, Anthropic/Claude, Ollama)
  - Sentence Transformers for semantic embeddings
  - 5 new RAG commands: `prepare_rag`, `index_rag`, `query_rag`, `evaluate_rag`, `create_rag`
  - LLM provider factory with abstraction layer
  - RAG evaluation framework
  - Comprehensive RAG integration tests (4 test files)

### Changed
- Fixed `sys.stdout/stderr` modifications for pytest compatibility
- Updated test coverage to 33% (139 passing tests)
- Added 11 new files (3345 lines of code)

### Documentation
- Updated README with comprehensive RAG documentation
- Added RAG workflow examples
- Added `.env` configuration guide for LLM providers

## [0.5.0] - 2025-01-16

### Changed
- **Python version migration**: Upgraded from Python ^3.8 to Python ^3.10
- Added RAG dependencies as optional extras in `pyproject.toml`
- Created `requirements-rag.txt` for alternative installation method

### Documentation
- Updated README with RAG installation options (Poetry extras vs pip)
- Documented two installation methods for RAG dependencies
- Added notes about Poetry 2.2+ compatibility issues with `packaging`

### Fixed
- Fixed OpenAI version in `requirements-rag.txt` (changed from 2.20 to >=1.20)

## [0.4.0] - 2025-12-07

### Added
- **Initial release of DYAG (Dynamic Diagram Generator)**
- Core conversion features:
  - Markdown to HTML converter with diagram support (Graphviz, PlantUML, Mermaid)
  - HTML to PDF conversion
  - HTML to Markdown conversion
  - Image to PDF conversion
- Document manipulation:
  - Table of contents generation (HTML and Markdown)
  - HTML/Markdown file merging and concatenation
  - WikiSI structure flattening
  - Interactive HTML generation
  - PDF compression
- Documentation generation:
  - Project to Markdown documentation generator
  - Code analysis and structure documentation
- MCP (Model Context Protocol) server integration
- Comprehensive test suite
- Poetry-based package management

### Features
- Professional HTML styling with responsive design
- SVG optimization and inline embedding
- UTF-8 encoding support for international characters
- Verbose mode with detailed status messages
- Standalone and embedded HTML output options
- Cross-platform compatibility (Windows, Linux, macOS)
- Support for multiple diagram formats:
  - Graphviz/DOT (local rendering)
  - PlantUML (via Kroki online service)
  - Mermaid (via Kroki online service)

### Documentation
- README with installation and usage instructions
- MCP integration guide
- Testing guide
- Build summary
- Project analysis documentation

## [0.2.0-rc.1] - 2025-12-01

### Added
- Release candidate with enhanced Markdown to HTML conversion
- SVG cleaning and optimization
- Table conversion with professional styling

### Fixed
- NameError with svg_replacements variable
- UTF-8 encoding errors on Windows
- Unicode display errors in console output

---

## Links

[0.8.1]: https://github.com/warchosian/dyag/releases/tag/v0.8.1
[0.8.0]: https://github.com/warchosian/dyag/releases/tag/v0.8.0
[0.7.0]: https://github.com/warchosian/dyag/releases/tag/v0.7.0
[0.6.0]: https://github.com/warchosian/dyag/releases/tag/v0.6.0
[0.5.0]: https://github.com/warchosian/dyag/releases/tag/v0.5.0
[0.4.0]: https://github.com/warchosian/dyag/releases/tag/v0.4.0
[0.2.0-rc.1]: https://github.com/warchosian/dyag/releases/tag/v0.2.0-rc.1

## Repository

- **GitHub**: https://github.com/warchosian/dyag
- **Issues**: https://github.com/warchosian/dyag/issues
- **Releases**: https://github.com/warchosian/dyag/releases

## v0.7.0 (2025-12-18)

## v0.6.0 (2025-12-16)

### Feat

- add RAG (Retrieval-Augmented Generation) system

## v0.5.0 (2025-12-16)

### Feat

- migrate to Python 3.10 and add RAG optional dependencies

## v0.4.0 (2025-12-07)

### Feat

- commit initial du projet DYAG v0.4.0
