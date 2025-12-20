# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
