# arabic-finder

A Python script that scans files and directories for Arabic Unicode characters, with optional include/ignore paths.

## Features

- Recursively scans files or a single file.
- Detects Arabic characters in the following Unicode ranges:
  - U+0600–U+06FF
  - U+0750–U+077F
  - U+08A0–U+08FF
  - U+FB50–U+FDFF
  - U+FE70–U+FEFF
- Prints each matching line once with all Arabic characters highlighted.
- Skips common binary, media, archive, and document extensions by default.
- Skips common directories such as `.git`, `node_modules`, `venv`, and `__pycache__`.
- Supports explicit ignore and include paths.
- Supports disabling colored output.
- No third-party dependencies.

## Requirements

- Python 3.8 or newer
- No external packages

## Installation

Clone the repository:

```bash
git clone https://github.com/ziadshalaby00/arabic-finder.git
cd arabic-finder
```

No installation is required. You can run the script directly.

## Usage

### Windows

```cmd
arabic-finder.cmd <path> [options]
```

### Linux / macOS

```bash
python3 arabic-finder.py <path> [options]
```

### Options

- `path` – File or directory to scan.
- `--ignore PATH [PATH ...]` – Files or directories to force ignore.
- `--include PATH [PATH ...]` – Files or directories to force include, even if they would be ignored by default.
- `--no-color` – Disable colored output.

## Examples

Scan the current directory:

```bash
python3 arabic-finder.py .
```

On Windows:

```cmd
arabic-finder.cmd .
```

Scan a specific file:

```bash
python3 arabic-finder.py document.txt
```

Ignore specific paths:

```bash
python3 arabic-finder.py . --ignore build/ dist/ secret.log
```

Include a path that is ignored by default:

```bash
python3 arabic-finder.py . --include node_modules/
```

Disable colored output:

```bash
python3 arabic-finder.py . --no-color
```

## Default Ignored Extensions

The following extensions are ignored by default:

- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.ico`, `.bmp`, `.svg`
- Videos: `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`
- Audio: `.mp3`, `.wav`, `.ogg`, `.flac`
- Archives: `.zip`, `.xpi`, `.rar`, `.7z`, `.tar`, `.gz`
- Binary / compiled: `.exe`, `.dll`, `.so`, `.bin`, `.pyc`, `.class`
- Databases: `.db`, `.sqlite`, `.sqlite3`
- Fonts: `.ttf`, `.otf`, `.woff`, `.woff2`
- Documents: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`

## Default Ignored Directories

The following directory names are ignored by default:

- `.git`, `.hg`, `.svn`
- `node_modules`, `venv`, `.venv`, `env`, `.env`
- `__pycache__`
- `.angular`, `.next`, `.nuxt`
- `dist`, `build`, `coverage`
- `.idea`, `.vscode`

## How It Works

The script walks through the given path and reads each file as UTF-8 with
`errors="replace"`. It uses a regular expression to find Arabic Unicode
characters. Matching lines are printed with the relative file path, line number,
and the Arabic characters highlighted in red.

Explicit `--ignore` paths take precedence over `--include` paths. Explicit
`--include` paths override the default extension and directory ignores.

## License

This project is licensed under the MIT License.
