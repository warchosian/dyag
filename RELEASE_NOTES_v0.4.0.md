# dyag v0.4.0 Release Notes

**Release Date**: 2025-12-07
**Type**: Stable Release
**Status**: Production Ready

---

## 📦 Package Information

- **Package Name**: dyag
- **Version**: 0.4.0
- **Python Compatibility**: Python 3.8+
- **Distribution Files**:
  - `dyag-0.4.0-py3-none-any.whl` (45 KB) - Wheel package
  - `dyag-0.4.0.tar.gz` (37 KB) - Source distribution

---

## 🎯 What's New in v0.4.0

### ✨ Major Features

This is the **first stable release** of DYAG (Dynamic Diagram Generator), a comprehensive toolkit for converting Markdown to HTML with advanced diagram support and various document processing utilities.

#### 1. **Complete Command-Line Interface**
   - ✅ `dyag md2html` - Convert Markdown to HTML with diagram support
   - ✅ `dyag html2pdf` - Convert HTML to PDF
   - ✅ `dyag html2md` - Convert HTML back to Markdown
   - ✅ `dyag project2md` - Generate documentation from project structure
   - ✅ `dyag add-toc` - Add table of contents to HTML files
   - ✅ `dyag make-interactive` - Add interactive features to HTML
   - ✅ `dyag flatten-wikisi` - Flatten WikiSI structure
   - ✅ `dyag compress-pdf` - Compress PDF files
   - ✅ `dyag concat-html` - Concatenate multiple HTML files
   - ✅ `dyag img2pdf` - Convert images to PDF

#### 2. **Enhanced Markdown to HTML Converter**
   - ✅ Full support for Graphviz/DOT diagrams → SVG conversion
   - ✅ PlantUML diagrams support via Kroki online service
   - ✅ Mermaid diagrams support via Kroki online service
   - ✅ Markdown tables conversion to styled HTML tables
   - ✅ UTF-8 encoding support for international characters
   - ✅ Standalone and embedded HTML output options

#### 3. **SVG Optimization**
   - ✅ Automatic SVG cleaning (removes XML declarations, DOCTYPE, comments)
   - ✅ Inline SVG embedding in HTML for portable documents
   - ✅ Responsive SVG sizing with CSS

#### 4. **MCP (Model Context Protocol) Integration**
   - ✅ MCP server implementation for AI assistant integration
   - ✅ Easy setup with configuration templates
   - ✅ Integration guide and examples

#### 5. **Professional Development Setup**
   - ✅ Poetry-based package management
   - ✅ Comprehensive test suite with pytest
   - ✅ Testing guide and documentation
   - ✅ Git repository initialization with proper .gitignore
   - ✅ CHANGELOG.md following Keep a Changelog format

---

## 📊 Supported Diagram Types

| Diagram Type | Syntax | Conversion Method | Status |
|--------------|--------|-------------------|--------|
| **Graphviz/DOT** | ```dot | Local (`dot -Tsvg`) | ✅ Fully supported |
| **Graphviz** | ```graphviz | Local (`dot -Tsvg`) | ✅ Fully supported |
| **PlantUML** | ```plantuml | Kroki online service | ✅ Fully supported |
| **Mermaid** | ```mermaid | Kroki online service | ✅ Fully supported |

---

## 🚀 Installation

### From Wheel (Recommended)
```bash
pip install dist/dyag-0.4.0-py3-none-any.whl
```

### From Source Distribution
```bash
pip install dist/dyag-0.4.0.tar.gz
```

### For Development
```bash
git clone <repository-url>
cd dyag
poetry install
```

---

## 💻 Usage Examples

### Markdown to HTML Conversion
```bash
# Basic conversion
dyag md2html input.md -o output.html

# With verbose output
dyag md2html input.md --verbose

# Embedded HTML (no standalone)
dyag md2html input.md --no-standalone
```

### HTML to PDF Conversion
```bash
dyag html2pdf input.html -o output.pdf
```

### Project Documentation
```bash
dyag project2md /path/to/project -o project-doc.md
```

### Add Table of Contents
```bash
dyag add-toc document.html
```

---

## 🔧 Dependencies

### Runtime Dependencies
- **Python** ^3.8
- **Pillow** ^10.0.0 - Image processing
- **PyMuPDF** ^1.23.0 - PDF manipulation
- **playwright** ^1.40.0 - HTML to PDF conversion
- **markdown** ^3.5 - Markdown parsing

### Development Dependencies
- **pytest** ^7.0 - Testing framework
- **pytest-cov** ^4.0 - Coverage reporting
- **pytest-mock** ^3.10 - Mocking support
- **black** ^23.0 - Code formatting
- **flake8** ^6.0 - Linting
- **commitizen** ^4.10.0 - Commit message formatting

### Optional (for diagram conversion)
- **Graphviz** (for local DOT conversion)
- Internet connection (for PlantUML/Mermaid via Kroki)

---

## 🎨 Key Improvements from Previous Versions

### From v0.2.0-rc.1 to v0.4.0

#### Added
- Complete command-line interface with 10 commands
- HTML to Markdown conversion
- HTML to PDF conversion with Playwright
- Project to Markdown documentation generator
- PDF compression and concatenation tools
- Image to PDF conversion
- Interactive HTML features
- WikiSI flattening functionality
- MCP server implementation
- Comprehensive test suite
- Poetry-based package management
- Git repository with proper versioning
- CHANGELOG.md

#### Improved
- Better error handling and logging
- Enhanced CSS styling for HTML output
- More robust UTF-8 encoding support
- Improved documentation
- Better project structure

#### Fixed
- All issues from RC versions
- Improved Windows compatibility
- Better handling of large files
- More stable diagram conversion

---

## 📂 Package Structure

```
dyag/
├── src/dyag/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py
│   ├── mcp_server.py
│   └── commands/
│       ├── md2html.py
│       ├── html2pdf.py
│       ├── html2md.py
│       ├── project2md.py
│       ├── add_toc.py
│       ├── make_interactive.py
│       ├── flatten_wikisi.py
│       ├── compresspdf.py
│       ├── concat_html.py
│       └── img2pdf.py
├── tests/
│   └── unit/commands/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── LICENSE (if applicable)
└── docs/
    ├── MCP_INTEGRATION.md
    ├── MCP_SETUP.md
    └── TESTING_GUIDE.md
```

---

## 🧪 Testing

### Run All Tests
```bash
poetry run pytest
```

### Run with Coverage
```bash
poetry run pytest --cov=src/dyag --cov-report=html
```

### Run Specific Test Suite
```bash
poetry run pytest tests/unit/commands/test_md2html.py
```

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for more details.

---

## 📋 Git Repository Information

This release includes:
- ✅ Initialized Git repository
- ✅ Tag: `v0.4.0`
- ✅ Commit history with conventional commits
- ✅ Proper .gitignore for Python projects
- ✅ CHANGELOG.md following Keep a Changelog format

### Git Tag Information
```bash
# View this release tag
git tag -l v0.4.0

# View tag details
git show v0.4.0

# Checkout this release
git checkout v0.4.0
```

---

## 🔜 Roadmap for Future Versions

### Planned for v0.5.0
- [ ] Support for additional diagram types (D2, Nomnoml)
- [ ] Local Mermaid conversion option (without Kroki)
- [ ] Configuration file support (.dyagrc)
- [ ] Improved error handling for network issues
- [ ] Progress bar for batch conversions
- [ ] Template system for HTML output
- [ ] Plugin architecture for custom converters

### Under Consideration
- [ ] GUI interface
- [ ] Watch mode for automatic conversion
- [ ] Integration with popular editors (VS Code, Sublime)
- [ ] Docker image for easy deployment
- [ ] CI/CD pipeline templates

---

## 🐛 Known Issues

- PlantUML local conversion requires `plantuml` command (falls back to Kroki)
- Mermaid conversion requires internet connection (uses Kroki online service)
- Large PDF files may take significant time to compress
- Some complex HTML structures may not convert perfectly to Markdown

---

## 📞 Support & Contributions

### Reporting Issues
If you encounter any bugs or have feature requests:
1. Check existing issues in the issue tracker
2. Provide detailed information about your environment
3. Include steps to reproduce the issue
4. Attach sample files if relevant

### Contributing
Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow the existing code style (use black for formatting)
4. Add tests for new features
5. Update documentation as needed
6. Submit a pull request

---

## 📜 License

[Specify your license here]

---

## 👥 Credits

**Author**: MARCHAL Hervé (herve.marchal@developpement-durable.gouv.fr)

**Powered by**:
- Python community
- Graphviz project
- PlantUML and Kroki
- Mermaid diagram library
- All open-source dependencies

---

## 🎉 Release Summary

DYAG v0.4.0 represents the first stable, production-ready release of the Dynamic Diagram Generator toolkit. With a comprehensive command-line interface, extensive diagram support, and professional development practices, DYAG is ready to streamline your documentation workflow.

**Key Highlights**:
- ✅ 10 powerful CLI commands
- ✅ Full diagram support (Graphviz, PlantUML, Mermaid)
- ✅ MCP integration for AI assistants
- ✅ Production-ready code with tests
- ✅ Professional packaging with Poetry
- ✅ Git repository with proper versioning

Thank you for using DYAG! We hope this tool makes your documentation work more efficient and enjoyable.

---

**Generated**: 2025-12-07
**Package**: dyag v0.4.0
**Status**: Stable Release 🚀
