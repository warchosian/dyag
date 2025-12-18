# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.6.0]: https://github.com/warchosian/dyag/releases/tag/v0.6.0
[0.5.0]: https://github.com/warchosian/dyag/releases/tag/v0.5.0
[0.4.0]: https://github.com/warchosian/dyag/releases/tag/v0.4.0
[0.2.0-rc.1]: https://github.com/warchosian/dyag/releases/tag/v0.2.0-rc.1

## Repository

- **GitHub**: https://github.com/warchosian/dyag
- **Issues**: https://github.com/warchosian/dyag/issues
- **Releases**: https://github.com/warchosian/dyag/releases
