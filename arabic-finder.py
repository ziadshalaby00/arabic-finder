#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

DEFAULT_IGNORED_EXTENSIONS = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".svg",
    # Videos
    ".mp4", ".mkv", ".avi", ".mov", ".webm",
    # Audio
    ".mp3", ".wav", ".ogg", ".flac",
    # Archives
    ".zip", "xpi", ".rar", ".7z", ".tar", ".gz",
    # Binary / compiled
    ".exe", ".dll", ".so", ".bin", ".pyc", ".class",
    # Databases
    ".db", ".sqlite", ".sqlite3",
    # Fonts
    ".ttf", ".otf", ".woff", ".woff2",
    # Documents
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
}

DEFAULT_IGNORED_DIRECTORIES = {
    ".git", ".hg", ".svn",
    "node_modules", "venv", ".venv", "env", ".env",
    "__pycache__",
    ".angular", ".next", ".nuxt",
    "dist", "build", "coverage",
    ".idea", ".vscode",
}

# Arabic Unicode ranges.
ARABIC_PATTERN = re.compile(
    r"[\u0600-\u06FF"
    r"\u0750-\u077F"
    r"\u08A0-\u08FF"
    r"\uFB50-\uFDFF"
    r"\uFE70-\uFEFF]"
)


# ============================================================
# Colors
# ============================================================

class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"


def color(text: str, colour: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{colour}{text}{Colors.RESET}"


# ============================================================
# Path ignore/include helpers
# ============================================================

def is_path_ignored(path: Path, ignored_paths: set[Path]) -> bool:
    """Return True if path is exactly an ignored path or inside an ignored directory."""
    for ignored in ignored_paths:
        if ignored.is_dir():
            try:
                path.relative_to(ignored)
                return True
            except ValueError:
                pass
        elif path == ignored:
            return True
    return False


def is_path_included(path: Path, included_paths: set[Path]) -> bool:
    """Return True if path is exactly an included path or inside an included directory."""
    for included in included_paths:
        if included.is_dir():
            try:
                path.relative_to(included)
                return True
            except ValueError:
                pass
        elif path == included:
            return True
    return False


# ============================================================
# File handling
# ============================================================

def is_ignored_extension(path: Path, ignored_extensions: set[str]) -> bool:
    return path.suffix.lower() in ignored_extensions


def is_ignored_directory(path: Path, ignored_directories: set[str]) -> bool:
    return any(part in ignored_directories for part in path.parts)


def iter_files(
    path: Path,
    ignored_extensions: set[str],
    ignored_directories: set[str],
    included_paths: set[Path],
    ignored_paths: set[Path],
):
    """
    Yield files that should be searched, respecting explicit includes/ignores.
    """
    # If the root itself is explicitly ignored, stop.
    if is_path_ignored(path, ignored_paths):
        return

    if path.is_file():
        if is_path_included(path, included_paths):
            yield path
            return
        if not is_ignored_extension(path, ignored_extensions):
            yield path
        return

    if not path.is_dir():
        return

    for file_path in path.rglob("*"):
        if not file_path.is_file():
            continue

        # 1. Explicit ignore takes precedence
        if is_path_ignored(file_path, ignored_paths):
            continue

        # 2. Explicit include overrides default ignores
        if is_path_included(file_path, included_paths):
            yield file_path
            continue

        # 3. Default directory ignore
        if is_ignored_directory(file_path, ignored_directories):
            continue

        # 4. Default extension ignore
        if is_ignored_extension(file_path, ignored_extensions):
            continue

        yield file_path


def read_lines(path: Path):
    """Read a file as UTF-8 with replacement for malformed characters."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as file:
            yield from file
    except (OSError, UnicodeError) as exc:
        print(
            f"{Colors.YELLOW}[WARNING] Could not read {path}: {exc}{Colors.RESET}",
            file=sys.stderr,
        )


# ============================================================
# Search
# ============================================================

def search_file(path: Path, root: Path, use_color: bool) -> int:
    """
    Search a single file for Arabic characters.
    Prints each matching line once with all Arabic highlighted.
    Returns number of matching lines.
    """
    matched_lines = 0

    for line_number, line in enumerate(read_lines(path), start=1):
        found = list(ARABIC_PATTERN.finditer(line))
        if not found:
            continue

        matched_lines += 1

        relative_path = path.relative_to(root) if root.is_dir() else path
        highlighted_line = line.rstrip("\n\r")

        if use_color:
            highlighted_line = ARABIC_PATTERN.sub(
                lambda m: color(m.group(), Colors.RED + Colors.BOLD, True),
                highlighted_line,
            )

        location = f"{relative_path}:{line_number}"
        print(
            f"{color(location, Colors.CYAN, use_color)} "
            f"{color('→', Colors.YELLOW, use_color)} "
            f"{highlighted_line}"
        )

    return matched_lines


# ============================================================
# CLI
# ============================================================

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Search files or directories for Arabic Unicode characters.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "path",
        type=Path,
        help="File or directory to scan.",
    )

    parser.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        type=Path,
        metavar="PATH",
        help=(
            "Files or directories to force ignore.\n"
            "Example: --ignore temp/ build/ secret.log"
        ),
    )

    parser.add_argument(
        "--include",
        nargs="*",
        default=[],
        type=Path,
        metavar="PATH",
        help=(
            "Files or directories to force include, even if they would be ignored by default.\n"
            "Example: --include node_modules/ config.json"
        ),
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output.",
    )

    return parser.parse_args()


# ============================================================
# Main
# ============================================================

def main():
    args = parse_arguments()

    path = args.path.expanduser().resolve()

    if not path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 1

    use_color = not args.no_color

    # Normalize default ignored extensions.
    ignored_extensions = {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        for ext in DEFAULT_IGNORED_EXTENSIONS
    }

    # Resolve explicit ignored paths.
    ignored_paths = set()
    for p in args.ignore:
        resolved = p.expanduser().resolve()
        if not resolved.exists():
            print(f"Warning: ignored path does not exist: {resolved}", file=sys.stderr)
        ignored_paths.add(resolved)

    # Resolve explicit included paths.
    included_paths = set()
    for p in args.include:
        resolved = p.expanduser().resolve()
        if not resolved.exists():
            print(f"Warning: included path does not exist: {resolved}", file=sys.stderr)
        included_paths.add(resolved)

    print(color("Arabic Character Scanner", Colors.BOLD + Colors.BLUE, use_color))
    print(color(f"Scanning: {path}", Colors.CYAN, use_color))
    print()

    files_scanned = 0
    total_matches = 0

    for file_path in iter_files(
        path,
        ignored_extensions,
        DEFAULT_IGNORED_DIRECTORIES,
        included_paths,
        ignored_paths,
    ):
        files_scanned += 1
        total_matches += search_file(
            file_path,
            path if path.is_dir() else file_path.parent,
            use_color,
        )

    print()
    print(color("─" * 60, Colors.BLUE, use_color))
    print(f"{color('Files scanned:', Colors.CYAN, use_color)} {files_scanned}")
    print(f"{color('Lines with Arabic text:', Colors.CYAN, use_color)} {total_matches}")

    if total_matches == 0:
        print(color("No Arabic characters found.", Colors.GREEN, use_color))
    else:
        print(color("Arabic characters were found.", Colors.YELLOW, use_color))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())