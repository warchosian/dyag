# dyag v0.2.0-rc.1 Release Notes

**Release Date**: 2025-12-01
**Type**: Release Candidate (RC.1)
**Status**: Pre-release for testing

---

## 📦 Package Information

- **Package Name**: dyag
- **Version**: 0.2.0-rc.1
- **Python Compatibility**: Python 3.8+
- **Distribution Files**:
  - `dyag-0.2.0rc1-py3-none-any.whl` (15 KB) - Wheel package
  - `dyag-0.2.0rc1.tar.gz` (24 KB) - Source distribution

---

## 🎯 What's New in v0.2.0-rc.1

### ✨ Major Features

#### 1. **Enhanced Markdown to HTML Converter (`md2html`)**
   - ✅ Full support for Graphviz/DOT diagrams → SVG conversion
   - ✅ PlantUML diagrams support via Kroki online service
   - ✅ Mermaid diagrams support via Kroki online service
   - ✅ Markdown tables conversion to styled HTML tables
   - ✅ UTF-8 encoding support for international characters

#### 2. **SVG Optimization**
   - ✅ Automatic SVG cleaning (removes XML declarations, DOCTYPE, comments)
   - ✅ Inline SVG embedding in HTML for portable documents
   - ✅ Responsive SVG sizing with CSS

#### 3. **Improved Output Messages**
   - ✅ Clear status indicators: [OK], [FAILED], [WARNING], [SUCCESS], [INFO]
   - ✅ Detailed conversion statistics
   - ✅ Windows-compatible ASCII messages (no Unicode errors)

### 🐛 Bug Fixes

- **Fixed**: `NameError` with undefined `svg_replacements` variable
- **Fixed**: UTF-8 encoding issues with PlantUML temporary files on Windows
- **Fixed**: Unicode character display errors in verbose mode on Windows

### 🎨 Styling Improvements

#### Enhanced CSS for HTML Output
- Professional table styling with headers, borders, and hover effects
- Improved diagram containers with shadows and rounded corners
- Zebra-striped table rows for better readability
- Responsive design with max-width constraints

---

## 📊 Supported Diagram Types

| Diagram Type | Syntax | Conversion Method | Status |
|--------------|--------|-------------------|--------|
| **Graphviz/DOT** | ```dot | Local (`dot -Tsvg`) | ✅ Fully supported |
| **Graphviz** | ```graphviz | Local (`dot -Tsvg`) | ✅ Fully supported |
| **PlantUML** | ```plantuml | Kroki online service | ✅ Fully supported |
| **Mermaid** | ```mermaid | Kroki online service | ✅ Fully supported |

---

## 🚀 Usage Examples

### Basic Conversion
```bash
dyag md2html input.md -o output.html
```

### Verbose Mode
```bash
dyag md2html input.md --verbose
```

### Without Standalone HTML
```bash
dyag md2html input.md --no-standalone
```

---

## 📝 Example Files Generated

### Test Files Successfully Converted
- ✅ `examples/test-hraccess/pseudonymes.html` (3 diagrams: PlantUML, Mermaid, DOT)
- ✅ `examples/test-multidiagrams/multidiagrams.dos.html` (9 diagrams: 3 PlantUML, 3 Mermaid, 3 DOT)
- ✅ `examples/test-graphviz/graphviz_tools.dos.html` (8 Graphviz/DOT diagrams)

---

## ⚙️ Installation

### From Wheel (Recommended)
```bash
pip install dist/dyag-0.2.0rc1-py3-none-any.whl
```

### From Source
```bash
pip install dist/dyag-0.2.0rc1.tar.gz
```

### For Development
```bash
poetry install
```

---

## 🔧 Dependencies

### Runtime Dependencies
- Python ^3.8
- Pillow ^10.0.0
- PyMuPDF ^1.23.0

### Optional (for diagram conversion)
- **Graphviz** (for local DOT conversion)
- Internet connection (for PlantUML/Mermaid via Kroki)

---

## 🧪 Testing

This is a **Release Candidate** (RC.1). Please test thoroughly before using in production:

1. Test with your own Markdown files containing diagrams
2. Verify SVG rendering in different browsers
3. Check table formatting with various table sizes
4. Test with international characters (UTF-8)
5. Report any issues to the development team

---

## 🐛 Known Issues

- PlantUML local conversion requires `plantuml` command (falls back to Kroki)
- Mermaid conversion requires internet connection (uses Kroki online service)

---

## 📋 Changelog Summary

```
[0.2.0-rc.1] - 2025-12-01
### Added
- Markdown to HTML conversion with diagram support
- SVG cleaning and optimization
- Table conversion with professional styling
- UTF-8 encoding support
- Verbose mode with clear status messages

### Fixed
- NameError with svg_replacements variable
- UTF-8 encoding errors on Windows
- Unicode display errors in console output

### Changed
- Improved CSS styling for tables and diagrams
- Enhanced error messages and logging
- Updated package description
```

---

## 🔜 Next Steps (Planned for v0.2.0 Final)

- [ ] Add support for more diagram types (D2, Nomnoml)
- [ ] Implement local Mermaid conversion option
- [ ] Add configuration file support
- [ ] Improve error handling for network issues
- [ ] Add progress bar for multiple diagram conversion

---

## 📞 Support & Feedback

For issues, questions, or feedback on this release candidate:
- Report bugs via issue tracker
- Test with your use cases
- Provide feedback on new features

---

**Note**: This is a pre-release version intended for testing purposes. Please do not use in production without thorough testing.
