# DARK IBRAHIM · Base64 Toolkit

A fast, dependency-free command-line tool to **encode and decode Base64** from text, files or standard input — with a clean terminal UI that adapts to wide screens and phones.

> **Note:** Base64 is an *encoding*, not encryption. It makes binary data text-safe, but it does **not** protect secrets. Never rely on it to hide sensitive information.

## Features

- Encode and decode text, files, or piped (stdin) data
- Standard and **URL-safe** Base64 alphabets (`-u`)
- Strict input validation with clear error messages
- Automatically repairs missing `=` padding when decoding
- Safe file output: refuses to overwrite unless you pass `--force`
- Script-friendly `--raw` mode (prints only the result)
- Optional line wrapping (`-w N`)
- Adaptive banner for narrow screens (works on phones)
- Respects the `NO_COLOR` environment variable
- Pure Python standard library, nothing to install
- Unit tests included

## Requirements

- Python 3.8 or newer

## Quick start

```bash
python3 dark_ibrahim_b64.py -e "Hello World"
python3 dark_ibrahim_b64.py -d "SGVsbG8gV29ybGQ="
```

**Android (Termux):**

```bash
pkg install python
python dark_ibrahim_b64.py -e "Hello World"
```

## Usage

| Option | Description |
| --- | --- |
| `-e [TEXT]` | Encode TEXT (or stdin / `-f` file) |
| `-d [TEXT]` | Decode Base64 TEXT (or stdin / `-f` file) |
| `-f PATH` | Read input from a file |
| `-o PATH` | Write the result to a file |
| `--force` | Overwrite the output file if it exists |
| `-u`, `--url-safe` | Use the URL-safe alphabet (`-` and `_`) |
| `-w N` | Wrap encoded output every N characters |
| `--raw` | Print only the result (no banner, no colors) |
| `--no-anim` | Disable animations |
| `--no-banner` | Hide the banner |
| `--no-color` | Disable colors |
| `-V`, `--version` | Show the version |
| `-h`, `--help` | Show help |

## Examples

```bash
# Encode / decode a file
python3 dark_ibrahim_b64.py -e -f notes.txt -o notes.b64
python3 dark_ibrahim_b64.py -d -f notes.b64 -o notes_restored.txt

# Use in a pipeline
echo "pipe me" | python3 dark_ibrahim_b64.py -e --raw

# URL-safe alphabet
python3 dark_ibrahim_b64.py -e "subjects?_d" -u --raw
```

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Error (bad input, missing file, existing output, ...) |
| `130` | Interrupted by the user (Ctrl+C) |

## Running the tests

```bash
python3 -m unittest -v
```

## Author

**DARK IBRAHIM** — Cyber Security Expert

## License

Released under the [MIT License](LICENSE).
