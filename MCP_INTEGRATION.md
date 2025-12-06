# MCP Integration - md2html Tool

**Date**: 2025-12-01
**Status**: ✅ Integrated and Tested

---

## 📋 Overview

The `md2html` command has been successfully integrated into the dyag MCP (Model Context Protocol) server, allowing AI assistants to convert Markdown files with diagrams to HTML via the MCP interface.

---

## 🔧 Integration Details

### 1. MCP Tool Definition

**Tool Name**: `dyag_md2html`

**Description**: Convert Markdown files with diagrams (Graphviz, PlantUML, Mermaid) to HTML with embedded SVG graphics. Supports tables, code blocks, and standard markdown formatting.

### 2. Input Schema

```json
{
  "type": "object",
  "properties": {
    "markdown": {
      "type": "string",
      "description": "Path to input Markdown file to convert",
      "required": true
    },
    "output": {
      "type": "string",
      "description": "Optional output HTML path. If not specified, uses same name with .html extension"
    },
    "verbose": {
      "type": "boolean",
      "description": "Show detailed conversion progress including diagram conversion status",
      "default": false
    },
    "standalone": {
      "type": "boolean",
      "description": "Generate standalone HTML with CSS and full page structure",
      "default": true
    }
  },
  "required": ["markdown"]
}
```

### 3. Response Format

**Success Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Successfully converted Markdown to HTML: <output_path>\nDiagrams (Graphviz, PlantUML, Mermaid) have been converted to embedded SVG graphics."
    }
  ]
}
```

**Error Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Failed to convert Markdown to HTML"
    }
  ],
  "isError": true
}
```

---

## 🧪 Test Results

### Test 1: Tool Listing ✅

```
Found 3 tools:
  - dyag_img2pdf
  - dyag_compresspdf
  - dyag_md2html ✅
```

**Result**: dyag_md2html tool successfully registered in MCP server

### Test 2: Markdown Conversion ✅

**Test File**: `examples/test-graphviz/graphviz_tools.md`
**Output**: `examples/test-graphviz/graphviz_tools.mcp.html`

**Conversion Results**:
- ✅ 8 Graphviz/DOT diagrams converted to SVG
- ✅ HTML file generated (40,438 bytes)
- ✅ All diagrams embedded successfully

**Conversion Log**:
```
Processing: examples/test-graphviz/graphviz_tools.md
Output: examples/test-graphviz/graphviz_tools.mcp.html

Found 8 diagram blocks
  Converting dot diagram... [OK] Converted successfully
  Converting dot diagram... [OK] Converted successfully
  Converting dot diagram... [OK] Converted successfully
  Converting dot diagram... [OK] Converted successfully
  Converting dot diagram... [OK] Converted successfully
  Converting dot diagram... [OK] Converted successfully
  Converting dot diagram... [OK] Converted successfully
  Converting dot diagram... [OK] Converted successfully

[SUCCESS] HTML created
[OK] All 8 diagrams converted to SVG successfully
```

---

## 🔄 MCP Request/Response Examples

### Example 1: Basic Conversion

**Request**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "dyag_md2html",
    "arguments": {
      "markdown": "document.md"
    }
  }
}
```

**Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Successfully converted Markdown to HTML: document.html\nDiagrams (Graphviz, PlantUML, Mermaid) have been converted to embedded SVG graphics."
    }
  ]
}
```

### Example 2: Conversion with Custom Output

**Request**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "dyag_md2html",
    "arguments": {
      "markdown": "input.md",
      "output": "output/result.html",
      "verbose": true,
      "standalone": true
    }
  }
}
```

---

## 📂 Files Modified

### 1. `src/dyag/mcp_server.py`

**Changes**:
- Added import: `from dyag.commands.md2html import process_markdown_to_html`
- Added tool definition in `self.tools` dictionary
- Added handler in `call_tool()` method

**Lines Modified**: ~50 lines added

### 2. Test Files Created

- `test_mcp_md2html.py` - Automated test suite
- `run_mcp_test.bat` - Test execution script
- `mcp_test_output.txt` - Test results log

---

## 🎯 Supported Features via MCP

### Diagram Types
- ✅ **Graphviz/DOT**: Local conversion with `dot -Tsvg`
- ✅ **PlantUML**: Online conversion via Kroki service
- ✅ **Mermaid**: Online conversion via Kroki service

### Markdown Elements
- ✅ **Tables**: Converted to styled HTML tables
- ✅ **Code blocks**: Syntax highlighting preserved
- ✅ **Headings**: H1-H6 support
- ✅ **Lists**: Ordered and unordered
- ✅ **Formatting**: Bold, italic, inline code
- ✅ **Links and images**: Preserved in HTML

### Output Options
- ✅ **Standalone HTML**: Full document with CSS
- ✅ **HTML Fragment**: Content only (no-standalone)
- ✅ **Custom output path**: Specify target file
- ✅ **Verbose mode**: Detailed conversion logs

---

## 🚀 Usage via MCP

### From AI Assistant

AI assistants connected to the MCP server can use:

```
Use the dyag_md2html tool to convert my_document.md to HTML
```

The MCP server will:
1. Parse the Markdown file
2. Convert all diagrams to SVG
3. Generate styled HTML
4. Return success message with output path

### Manual Testing

```bash
# Start MCP server
python -m dyag.mcp_server

# Send request (via stdin)
{"method":"tools/list","params":{}}

# Call md2html tool
{"method":"tools/call","params":{"name":"dyag_md2html","arguments":{"markdown":"test.md"}}}
```

---

## 📊 Integration Summary

| Component | Status | Details |
|-----------|--------|---------|
| **Tool Registration** | ✅ | dyag_md2html added to MCP tools |
| **Input Schema** | ✅ | 4 parameters (1 required, 3 optional) |
| **Handler Implementation** | ✅ | Calls process_markdown_to_html() |
| **Error Handling** | ✅ | Returns error responses properly |
| **Testing** | ✅ | 2/2 tests passed |
| **Documentation** | ✅ | This file + inline docs |

---

## 🔜 Future Enhancements

Potential improvements for MCP integration:

- [ ] Add progress streaming for long conversions
- [ ] Support batch conversion of multiple files
- [ ] Add diagram validation before conversion
- [ ] Return diagram statistics in response
- [ ] Support custom CSS themes via MCP
- [ ] Add option to return HTML as base64

---

## 📞 Testing

### Run Automated Tests

```bash
# Windows
./run_mcp_test.bat

# Linux/Mac
python test_mcp_md2html.py
```

### Expected Output

```
============================================================
MCP Server - md2html Integration Tests
============================================================

TEST 1: List Tools
  [OK] SUCCESS: dyag_md2html tool found!

TEST 2: Convert Markdown to HTML via MCP
  [OK] SUCCESS!
  Generated file: output.html

============================================================
TEST SUMMARY
============================================================
[OK] PASSED: List Tools
[OK] PASSED: Convert Markdown

[SUCCESS] ALL TESTS PASSED!
```

---

## ✅ Conclusion

The `md2html` command has been successfully integrated into the dyag MCP server. All tests pass, and the tool is ready for use by AI assistants via the Model Context Protocol.

**Integration Version**: v0.2.0-rc.1
**Date Completed**: 2025-12-01
**Test Status**: ✅ All tests passed
