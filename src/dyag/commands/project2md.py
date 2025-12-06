"""
Command to convert a project directory to a single Markdown file for AI analysis.

This module scans a directory and generates a Markdown file containing:
- Clickable file tree (table of contents)
- All non-binary files as code blocks
- Relative file paths
- Proper syntax highlighting
"""

import os
import sys
from pathlib import Path
from typing import List, Set, Optional, Tuple
import mimetypes
import fnmatch


# Common binary extensions to skip
BINARY_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin', '.dat',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
    '.zip', '.tar', '.gz', '.7z', '.rar',
    '.pyc', '.pyo', '.class', '.o', '.obj',
    '.db', '.sqlite', '.sqlite3'
}

# Default directories to exclude
DEFAULT_EXCLUDE_DIRS = {
    '__pycache__', '.git', '.svn', '.hg', '.idea', '.vscode',
    'node_modules', 'venv', 'env', '.env', 'virtualenv',
    'dist', 'build', '.egg-info', '.tox', '.pytest_cache',
    'target', 'out', 'bin', 'obj'
}

# Language mapping for syntax highlighting
LANGUAGE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.jsx': 'jsx',
    '.tsx': 'tsx',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.cs': 'csharp',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'zsh',
    '.fish': 'fish',
    '.ps1': 'powershell',
    '.bat': 'batch',
    '.cmd': 'batch',
    '.html': 'html',
    '.htm': 'html',
    '.xml': 'xml',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'less',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.ini': 'ini',
    '.cfg': 'ini',
    '.conf': 'conf',
    '.sql': 'sql',
    '.md': 'markdown',
    '.rst': 'rst',
    '.txt': 'text',
    '.log': 'text',
    '.csv': 'csv',
    '.tsv': 'tsv',
    '.makefile': 'makefile',
    '.dockerfile': 'dockerfile',
    '.gitignore': 'text',
    '.env': 'text',
}


def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary.

    Args:
        file_path: Path to file

    Returns:
        True if file is binary, False otherwise
    """
    # Check extension
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
        return True

    # Check mime type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and not mime_type.startswith('text'):
        return True

    # Try to read first few bytes
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True
    except:
        return True

    return False


def should_exclude_dir(dir_name: str, exclude_dirs: Set[str]) -> bool:
    """Check if directory should be excluded."""
    return dir_name in exclude_dirs or dir_name.startswith('.')


class ProjectIgnore:
    """
    Parser and matcher for .projectignore files.
    Supports gitignore-style patterns with exclusion and inclusion rules.
    """

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.patterns = []  # List of (pattern, is_negation, is_dir_only)
        self._load_patterns()

    def _load_patterns(self):
        """Load patterns from .projectignore file."""
        projectignore_file = self.root_dir / '.projectignore'

        if not projectignore_file.exists():
            return

        try:
            with open(projectignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Check for negation (inclusion)
                    is_negation = line.startswith('!')
                    if is_negation:
                        line = line[1:].strip()

                    # Check if pattern is for directories only
                    is_dir_only = line.endswith('/')
                    if is_dir_only:
                        line = line.rstrip('/')

                    self.patterns.append((line, is_negation, is_dir_only))
        except Exception as e:
            # Silently ignore errors reading .projectignore
            pass

    def _match_pattern(self, path_str: str, pattern: str, is_dir: bool, is_dir_only: bool) -> bool:
        """
        Check if a path matches a pattern.

        Args:
            path_str: Relative path string (normalized with /)
            pattern: Pattern to match against
            is_dir: Whether the path is a directory
            is_dir_only: Whether the pattern should only match directories

        Returns:
            True if path matches pattern
        """
        # Directory-only patterns should only match directories
        if is_dir_only and not is_dir:
            return False

        # Pattern without / matches anywhere in the path
        if '/' not in pattern:
            # Match against filename
            filename = path_str.split('/')[-1]
            if fnmatch.fnmatch(filename, pattern):
                return True
            # Also check if any part of the path matches
            for part in path_str.split('/'):
                if fnmatch.fnmatch(part, pattern):
                    return True
        else:
            # Pattern with / is matched from root
            if fnmatch.fnmatch(path_str, pattern):
                return True
            if fnmatch.fnmatch(path_str, pattern + '/*'):
                return True

        return False

    def should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored based on .projectignore patterns.

        Args:
            path: Path to check (relative to root_dir)

        Returns:
            True if path should be ignored
        """
        if not self.patterns:
            return False

        try:
            rel_path = path.relative_to(self.root_dir)
        except ValueError:
            # Path is not relative to root_dir
            return False

        # Normalize path (use forward slashes)
        path_str = str(rel_path).replace('\\', '/')
        is_dir = path.is_dir()

        # Process patterns in order, last match wins
        ignored = False

        for pattern, is_negation, is_dir_only in self.patterns:
            if self._match_pattern(path_str, pattern, is_dir, is_dir_only):
                ignored = not is_negation

        return ignored


def load_gitignore_patterns(root_dir: Path) -> Set[str]:
    """Load patterns from .gitignore file."""
    gitignore_file = root_dir / '.gitignore'
    patterns = set()

    if gitignore_file.exists():
        try:
            with open(gitignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line)
        except:
            pass

    return patterns


def scan_directory(
    root_dir: Path,
    exclude_dirs: Set[str],
    max_file_size: int,
    verbose: bool = False,
    use_projectignore: bool = True
) -> List[Path]:
    """
    Scan directory for non-binary files.

    Args:
        root_dir: Root directory to scan
        exclude_dirs: Set of directory names to exclude
        max_file_size: Maximum file size in bytes
        verbose: Print progress
        use_projectignore: Use .projectignore file if present

    Returns:
        List of file paths
    """
    files = []

    # Load .projectignore patterns if requested
    projectignore = ProjectIgnore(root_dir) if use_projectignore else None

    if verbose:
        print(f"[INFO] Scanning directory: {root_dir}")
        if projectignore and projectignore.patterns:
            print(f"[INFO] Using .projectignore with {len(projectignore.patterns)} patterns")

    for root, dirs, filenames in os.walk(root_dir):
        root_path = Path(root)

        # Filter out excluded directories
        dirs_to_remove = []
        for d in dirs:
            dir_path = root_path / d

            # Check default exclusions
            if should_exclude_dir(d, exclude_dirs):
                dirs_to_remove.append(d)
                continue

            # Check .projectignore
            if projectignore and projectignore.should_ignore(dir_path):
                dirs_to_remove.append(d)
                if verbose:
                    print(f"[SKIP] .projectignore: {dir_path.relative_to(root_dir)}/")
                continue

        # Remove excluded directories from walk
        for d in dirs_to_remove:
            dirs.remove(d)

        for filename in filenames:
            file_path = Path(root) / filename

            # Check .projectignore for files
            if projectignore and projectignore.should_ignore(file_path):
                if verbose:
                    print(f"[SKIP] .projectignore: {file_path.relative_to(root_dir)}")
                continue

            # Skip if too large
            try:
                if file_path.stat().st_size > max_file_size:
                    if verbose:
                        print(f"[SKIP] Too large: {file_path.relative_to(root_dir)}")
                    continue
            except:
                continue

            # Skip binary files
            if is_binary_file(file_path):
                continue

            files.append(file_path)

    if verbose:
        print(f"[INFO] Found {len(files)} non-binary files")

    return sorted(files)


def format_size(size: int) -> str:
    """
    Format file size with thousands separator (dot for French format).

    Args:
        size: File size in bytes

    Returns:
        Formatted size string with dot separator
    """
    size_str = str(size)
    # Add dot separator for thousands (French format)
    result = []
    for i, digit in enumerate(reversed(size_str)):
        if i > 0 and i % 3 == 0:
            result.append('.')
        result.append(digit)
    return ''.join(reversed(result))


def generate_file_tree(files: List[Path], root_dir: Path) -> str:
    """
    Generate a clickable file tree in Markdown with file sizes.

    Args:
        files: List of file paths
        root_dir: Root directory

    Returns:
        Markdown string for file tree
    """
    tree_lines = ["## 📁 Arborescence des fichiers\n"]

    # Build tree structure with file sizes
    tree = {}
    file_sizes = {}

    for file_path in files:
        rel_path = file_path.relative_to(root_dir)
        parts = rel_path.parts

        current = tree
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Add file with size
        current[parts[-1]] = None
        # Store file size with normalized path (forward slashes)
        normalized_path = str(rel_path).replace('\\', '/')
        try:
            file_sizes[normalized_path] = file_path.stat().st_size
        except:
            file_sizes[normalized_path] = 0

    # Render tree
    def render_tree(node: dict, prefix: str = "", is_last: bool = True, path: str = ""):
        items = sorted(node.items(), key=lambda x: (x[1] is None, x[0]))
        for i, (name, children) in enumerate(items):
            is_last_item = i == len(items) - 1
            current_path = f"{path}/{name}" if path else name

            # Create anchor link
            anchor = current_path.replace('/', '-').replace('.', '-')

            if children is None:
                # File - add size and tree ID for back-navigation
                connector = "└── " if is_last_item else "├── "
                file_size = file_sizes.get(current_path, 0)
                size_str = format_size(file_size)
                tree_id = f'tree-{anchor}'
                # Use <a> tag for anchor, then link
                tree_lines.append(f'{prefix}{connector}<a id="{tree_id}"></a>[{name}](#{anchor}) *({size_str} octets)*')
            else:
                # Directory
                connector = "└── " if is_last_item else "├── "
                tree_lines.append(f"{prefix}{connector}**{name}/**")

                # Recursive call
                new_prefix = prefix + ("    " if is_last_item else "│   ")
                render_tree(children, new_prefix, is_last_item, current_path)

    render_tree(tree)

    return "\n".join(tree_lines)


def get_language_for_file(file_path: Path) -> str:
    """Get syntax highlighting language for file."""
    ext = file_path.suffix.lower()
    name = file_path.name.lower()

    # Check filename first
    if name in ['makefile', 'dockerfile']:
        return LANGUAGE_MAP.get(f'.{name}', 'text')

    # Check extension
    return LANGUAGE_MAP.get(ext, 'text')


def generate_file_content(files: List[Path], root_dir: Path, verbose: bool = False) -> str:
    """
    Generate Markdown content for all files with bidirectional navigation.
    Files with more than 100 lines are collapsible.

    Args:
        files: List of file paths
        root_dir: Root directory
        verbose: Print progress

    Returns:
        Markdown string with all file contents
    """
    content_lines = ["\n---\n", "## 📄 Contenu des fichiers\n"]
    COLLAPSE_THRESHOLD = 100  # Lines threshold for collapsible content

    for file_path in files:
        rel_path = file_path.relative_to(root_dir)
        # Normalize path to use forward slashes for consistent anchors
        normalized_path = str(rel_path).replace('\\', '/')
        anchor = normalized_path.replace('/', '-').replace('.', '-')
        tree_id = f'tree-{anchor}'
        language = get_language_for_file(file_path)

        if verbose:
            print(f"[PROCESS] {rel_path}")

        # Get file size
        try:
            file_size = file_path.stat().st_size
            size_str = format_size(file_size)
        except:
            file_size = 0
            size_str = "0"

        # Add file header with enhanced styling and back-to-tree link
        content_lines.append(f"\n---\n")
        content_lines.append(f"### 📄 `{normalized_path}` [{size_str} octets]")
        content_lines.append(f'<a id="{anchor}"></a> [↩ Retour à l\'arborescence](#{tree_id})\n')

        # Read file content with encoding detection
        try:
            # Try multiple encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            file_content = None
            last_error = None

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        file_content = f.read()
                    break  # Success, exit loop
                except (UnicodeDecodeError, LookupError) as e:
                    last_error = e
                    continue

            if file_content is None:
                raise last_error or Exception("Could not read file with any encoding")

            # Count lines
            line_count = file_content.count('\n') + 1 if file_content else 0

            # Add metadata box
            content_lines.append(f"> **Chemin relatif** : `{normalized_path}`  ")
            content_lines.append(f"> **Taille** : {size_str} octets  ")
            content_lines.append(f"> **Lignes** : {line_count}  ")
            content_lines.append(f"> **Type** : {language}\n")

            # Determine the number of backticks needed to wrap the content
            # If content has ``` blocks, we need more backticks for the outer fence
            max_backticks = 3
            import re
            backtick_matches = re.findall(r'`+', file_content)
            if backtick_matches:
                max_backticks = max(len(m) for m in backtick_matches) + 1
                max_backticks = max(max_backticks, 4)  # Use at least 4 backticks if content has any

            fence = '`' * max_backticks

            # Add code block with collapse for long files
            if line_count > COLLAPSE_THRESHOLD:
                content_lines.append(f'<details class="file-content-collapsible">')
                content_lines.append(f'<summary>📖 Afficher le contenu ({line_count} lignes) - Cliquer pour déplier</summary>\n')
                content_lines.append(f"{fence}{language}")
                content_lines.append(file_content)
                content_lines.append(f"{fence}\n")
                content_lines.append("</details>\n")
            else:
                # Add code block with language
                content_lines.append(f"{fence}{language}")
                content_lines.append(file_content)
                content_lines.append(f"{fence}\n")

        except Exception as e:
            content_lines.append(f"```\nError reading file: {e}\n```\n")

    return "\n".join(content_lines)


def get_collapsible_styles_and_scripts() -> str:
    """
    Generate CSS and JavaScript for collapsible file contents.

    Returns:
        HTML string with styles and scripts
    """
    return """
<style>
/* Collapsible file content styles */
.file-content-collapsible {
    margin: 15px 0;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    background: #f6f8fa;
}

.file-content-collapsible summary {
    padding: 12px 15px;
    cursor: pointer;
    font-weight: 600;
    color: #0366d6;
    user-select: none;
    list-style: none;
    background: #f6f8fa;
    border-radius: 6px;
    transition: background-color 0.2s, color 0.2s;
}

.file-content-collapsible summary::-webkit-details-marker {
    display: none;
}

.file-content-collapsible summary::before {
    content: '▶ ';
    display: inline-block;
    transition: transform 0.2s;
    margin-right: 5px;
}

.file-content-collapsible[open] summary::before {
    transform: rotate(90deg);
}

.file-content-collapsible summary:hover {
    background-color: #e1e4e8;
    color: #0256a0;
}

.file-content-collapsible[open] summary {
    border-bottom: 1px solid #e1e4e8;
    margin-bottom: 0;
    border-radius: 6px 6px 0 0;
}

.file-content-collapsible pre {
    margin: 0 !important;
    border-radius: 0 0 6px 6px !important;
    border: none !important;
}

/* Button to expand/collapse all */
.collapse-controls {
    position: sticky;
    top: 10px;
    z-index: 100;
    text-align: right;
    margin: 20px 0;
}

.collapse-btn {
    display: inline-block;
    padding: 8px 16px;
    margin: 0 5px;
    background: #0366d6;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: background 0.2s;
    text-decoration: none;
}

.collapse-btn:hover {
    background: #0256a0;
}

.collapse-btn:active {
    transform: translateY(1px);
}
</style>

<script>
// Add expand/collapse all buttons
document.addEventListener('DOMContentLoaded', function() {
    // Find the file contents section
    const fileContentsSection = document.querySelector('h2');
    if (!fileContentsSection) return;

    // Create control buttons
    const controlsDiv = document.createElement('div');
    controlsDiv.className = 'collapse-controls';
    controlsDiv.innerHTML = `
        <button class="collapse-btn" onclick="expandAllFiles()">📖 Tout déplier</button>
        <button class="collapse-btn" onclick="collapseAllFiles()">📕 Tout replier</button>
    `;

    // Insert after the "Contenu des fichiers" heading
    const contenuHeading = Array.from(document.querySelectorAll('h2')).find(h => h.textContent.includes('Contenu des fichiers'));
    if (contenuHeading) {
        contenuHeading.parentNode.insertBefore(controlsDiv, contenuHeading.nextSibling);
    }
});

function expandAllFiles() {
    document.querySelectorAll('.file-content-collapsible').forEach(details => {
        details.open = true;
    });
}

function collapseAllFiles() {
    document.querySelectorAll('.file-content-collapsible').forEach(details => {
        details.open = false;
    });
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+E: Expand all
    if (e.ctrlKey && e.key === 'e') {
        e.preventDefault();
        expandAllFiles();
    }
    // Ctrl+R: Collapse all
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        collapseAllFiles();
    }
});
</script>
"""


def project_to_markdown(
    directory: str,
    output_path: Optional[str] = None,
    exclude_dirs: Optional[Set[str]] = None,
    max_file_size: int = 1024 * 1024,  # 1 MB default
    use_gitignore: bool = True,
    verbose: bool = False
) -> int:
    """
    Convert project directory to Markdown file for AI analysis.

    Args:
        directory: Directory to scan
        output_path: Output Markdown file path
        exclude_dirs: Additional directories to exclude
        max_file_size: Maximum file size in bytes
        use_gitignore: Respect .gitignore patterns
        verbose: Print detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    root_dir = Path(directory).resolve()

    if not root_dir.exists():
        print(f"Error: Directory '{directory}' does not exist.", file=sys.stderr)
        return 1

    if not root_dir.is_dir():
        print(f"Error: '{directory}' is not a directory.", file=sys.stderr)
        return 1

    # Determine output path
    if output_path is None:
        output_file = Path(f"{root_dir.name}_project.md")
    else:
        output_file = Path(output_path)

    # Build exclude set
    exclude_set = DEFAULT_EXCLUDE_DIRS.copy()
    if exclude_dirs:
        exclude_set.update(exclude_dirs)

    # Load gitignore if requested
    if use_gitignore:
        gitignore_patterns = load_gitignore_patterns(root_dir)
        exclude_set.update(gitignore_patterns)

    if verbose:
        print(f"Project: {root_dir}")
        print(f"Output: {output_file}")
        print(f"Excluded dirs: {', '.join(sorted(exclude_set))}")

    try:
        # Scan directory (always use .projectignore)
        files = scan_directory(root_dir, exclude_set, max_file_size, verbose, True)

        if not files:
            print("[WARNING] No non-binary files found!", file=sys.stderr)
            return 1

        # Generate Markdown
        if verbose:
            print("\n[INFO] Generating Markdown...")

        md_content = []

        # Header
        md_content.append(f"# Projet : {root_dir.name}\n")
        md_content.append(f"**Chemin** : `{root_dir}`\n")
        md_content.append(f"**Fichiers** : {len(files)} fichiers non-binaires\n")

        # File tree
        md_content.append(generate_file_tree(files, root_dir))

        # File contents
        md_content.append(generate_file_content(files, root_dir, verbose))

        # Footer with CSS and JavaScript for collapsible sections
        md_content.append("\n---\n")
        md_content.append("*Généré par dyag project2md*\n")
        md_content.append(get_collapsible_styles_and_scripts())

        # Write output with UTF-8 BOM for better Windows compatibility
        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write("\n".join(md_content))

        output_size = output_file.stat().st_size
        output_size_formatted = format_size(output_size)

        print(f"\n[SUCCESS] Markdown créé: {output_file}")
        print(f"[INFO] {len(files)} fichiers traités")
        print(f"[INFO] Taille: {output_size_formatted} octets ({output_size / 1024:.1f} KB)")
        print(f"\n[TIP] Utilisez ce fichier pour l'analyse par IA (ChatGPT, DeepSeek, Qwen)")

        return 0

    except Exception as e:
        print(f"Error: Failed to generate Markdown: {e}", file=sys.stderr)
        import traceback
        if verbose:
            traceback.print_exc()
        return 1


def register_project2md_command(subparsers):
    """Register the project2md command."""
    parser = subparsers.add_parser(
        'project2md',
        help='Convert project directory to Markdown for AI analysis',
        description='Scan a directory and generate a Markdown file with clickable file tree '
                    'and all non-binary files as code blocks. Perfect for AI code analysis.'
    )

    parser.add_argument(
        'directory',
        type=str,
        help='Directory to scan'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output Markdown file (default: <directory_name>_project.md)'
    )

    parser.add_argument(
        '--exclude',
        type=str,
        nargs='*',
        default=[],
        help='Additional directories to exclude'
    )

    parser.add_argument(
        '--max-size',
        type=int,
        default=1024 * 1024,
        help='Maximum file size in bytes (default: 1MB)'
    )

    parser.add_argument(
        '--no-gitignore',
        action='store_true',
        help='Ignore .gitignore patterns'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.set_defaults(func=lambda args: project_to_markdown(
        args.directory,
        args.output,
        set(args.exclude) if args.exclude else None,
        args.max_size,
        not args.no_gitignore,
        args.verbose
    ))
