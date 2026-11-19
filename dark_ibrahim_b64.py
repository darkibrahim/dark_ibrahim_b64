#!/usr/bin/env python3
"""
DARK IBRAHIM - Base64 Toolkit

A small, dependency-free command-line tool that encodes and decodes Base64
from text, files or standard input.

Note: Base64 is an *encoding*, not encryption. It offers no secrecy.

Copyright (c) 2026 DARK IBRAHIM. Released under the MIT License (see LICENSE).
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import os
import pathlib
import random
import re
import shutil
import sys
import time

__author__ = "DARK IBRAHIM"
__version__ = "5.0.0"
__license__ = "MIT"

EXAMPLES = """\
examples:
  dark_ibrahim_b64.py -e "Hello World"
  dark_ibrahim_b64.py -d "SGVsbG8gV29ybGQ="
  dark_ibrahim_b64.py -e -f notes.txt -o notes.b64
  dark_ibrahim_b64.py -d -f notes.b64 -o notes_restored.txt --force
  echo "pipe me" | dark_ibrahim_b64.py -e --raw
"""

MAX_INPUT_BYTES = 64 * 1024 * 1024  # 64 MiB safety limit
EXIT_OK, EXIT_ERROR, EXIT_INTERRUPTED = 0, 1, 130

# ==========================================================
#  THEME
# ==========================================================
GREEN, MATRIX, CYAN, PINK = 46, 34, 51, 201
RED, WHITE, GRAY, YELLOW = 196, 255, 244, 226
GRADIENT = [51, 50, 49, 48, 47, 46]  # banner rows, top -> bottom
GLYPHS = "01!@#$%^&*<>?/\\|[]{}=+-"
WIDTH = 66  # inner width of the full banner box

ANSI_RE = re.compile(r"\033\[[0-9;]*m")
USE_COLOR = False


def init_color(force_off: bool = False) -> None:
    """Enable colors only on real terminals that support them."""
    global USE_COLOR
    USE_COLOR = (
        sys.stdout.isatty() and "NO_COLOR" not in os.environ and not force_off
    )
    if USE_COLOR and os.name == "nt":
        os.system("")  # switches on ANSI escape handling in Windows terminals


def paint(text: str, color: int | None = None, bold: bool = False) -> str:
    """Wrap text in ANSI codes (no-op when colors are disabled)."""
    if not USE_COLOR:
        return text
    codes = "\033[1m" if bold else ""
    if color is not None:
        codes += f"\033[38;5;{color}m"
    return f"{codes}{text}\033[0m"


def visible_len(text: str) -> int:
    return len(ANSI_RE.sub("", text))


def term_width() -> int:
    return shutil.get_terminal_size((80, 24)).columns


def is_compact() -> bool:
    """True on narrow screens (for example phones) where the big banner would wrap."""
    return term_width() < WIDTH + 2


# ==========================================================
#  BRANDING
# ==========================================================
class Brand:
    NAME = __author__
    TITLE = "Cyber Security Expert"
    TAGLINE = "Advanced Base64 Encoder / Decoder"
    VERSION = __version__
    LICENSE = __license__


FONT = {
    "D": ["██████╗ ", "██╔══██╗", "██║  ██║", "██║  ██║", "██████╔╝", "╚═════╝ "],
    "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
    "R": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██║  ██║", "╚═╝  ╚═╝"],
    "K": ["██╗  ██╗", "██║ ██╔╝", "█████╔╝ ", "██╔═██╗ ", "██║  ██╗", "╚═╝  ╚═╝"],
    "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
    "B": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██████╔╝", "╚═════╝ "],
    "H": ["██╗  ██╗", "██║  ██║", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
    "M": ["███╗   ███╗", "████╗ ████║", "██╔████╔██║", "██║╚██╔╝██║", "██║ ╚═╝ ██║", "╚═╝     ╚═╝"],
}


def render_word(word: str) -> list[str]:
    return ["".join(FONT[ch][i] for ch in word) for i in range(6)]


def box_row(content: str = "", center: bool = False) -> str:
    """One line inside the banner box, padded to an exact width."""
    pad = WIDTH - visible_len(content)
    left = pad // 2 if center else 1
    right = max(pad - left, 0)
    edge = paint("│", CYAN)
    return f"{edge}{' ' * left}{content}{' ' * right}{edge}"


def banner() -> None:
    if is_compact():
        rule = paint("─" * max(10, min(term_width() - 4, 38)), CYAN)
        print(f"  {paint('◆ ' + Brand.NAME + ' ◆', GREEN, bold=True)}")
        print(f"  {paint(Brand.TITLE, GREEN)}")
        print(f"  {paint(Brand.TAGLINE, CYAN)}")
        print(f"  {paint('v' + Brand.VERSION + ' · ' + Brand.LICENSE, GRAY)}")
        print(f"  {rule}\n")
        return

    print(paint("╭" + "─" * WIDTH + "╮", CYAN))
    print(box_row())
    for word in ("DARK", "IBRAHIM"):
        for i, line in enumerate(render_word(word)):
            print(box_row(paint(line, GRADIENT[i], bold=True), center=True))
        print(box_row())
    print(box_row(paint(Brand.TAGLINE.upper(), CYAN, bold=True), center=True))
    print(box_row(paint("─ ◆ ─", GRAY), center=True))
    print(paint("├" + "─" * WIDTH + "┤", CYAN))
    info = [
        ("AUTHOR", Brand.NAME, GREEN),
        ("ROLE", Brand.TITLE, GREEN),
        ("VERSION", "v" + Brand.VERSION, CYAN),
        ("LICENSE", Brand.LICENSE, CYAN),
        ("MODES", "text · file · stdin · url-safe", CYAN),
    ]
    for key, value, color in info:
        label = paint(f"{key:<8}", GRAY)
        line = f"{paint('◈', PINK)} {label} {paint(':', GRAY)} {paint(value, color, bold=True)}"
        print(box_row(line))
    print(paint("╰" + "─" * WIDTH + "╯", CYAN))
    print()


# ==========================================================
#  OUTPUT HELPERS
# ==========================================================
def progress_effect(label: str, duration: float = 0.9) -> None:
    """Animated progress bar with a text-reveal effect (terminal only)."""
    compact = is_compact()
    if compact:
        label = label.split()[1] if len(label.split()) > 1 else label
    bar_len = 10 if compact else 20
    if not (USE_COLOR and sys.stdout.isatty()):
        print(f"  {paint('✔', GREEN, bold=True)} {label}")
        return
    steps = 30
    for i in range(steps + 1):
        done = len(label) * i // steps
        scrambled = "".join(random.choice(GLYPHS) for _ in label[done:])
        pct = f"{i * 100 // steps:3d}%"
        fill = bar_len * i // steps
        bar = "[" + "█" * fill + "░" * (bar_len - fill) + "]"
        sys.stdout.write(
            f"\r  {paint(bar, CYAN)} {paint(pct, WHITE)}  "
            f"{paint(label[:done], GREEN, bold=True)}{paint(scrambled, MATRIX)}"
        )
        sys.stdout.flush()
        time.sleep(duration / steps)
    sys.stdout.write("\r\033[K")
    print(f"  {paint('✔', GREEN, bold=True)} {paint(label, WHITE, bold=True)}")


def result_panel(title: str, payload: str) -> None:
    inner = min(term_width() - 2, WIDTH)
    top_dashes = max(2, inner - len(title) - 8)
    print()
    print(paint(f"  ╭─── {title} " + "─" * top_dashes, CYAN))
    for line in payload.splitlines() or [""]:
        print(paint("  │ ", CYAN) + paint(line, GREEN, bold=True))
    print(paint("  ╰" + "─" * max(2, inner - 3), CYAN))


def stats_block(in_bytes: int, out_bytes: int, elapsed_ms: float, digest: str) -> None:
    items = [
        ("in", f"{in_bytes} B"),
        ("out", f"{out_bytes} B"),
        ("time", f"{elapsed_ms:.2f} ms"),
        ("sha256", digest[:12] + "…"),
    ]
    cells = [f"{paint(k, GRAY)} {paint(v, WHITE)}" for k, v in items]
    if is_compact():
        print("\n".join("  " + cell for cell in cells) + "\n")
    else:
        print("  " + paint(" · ", GRAY).join(cells) + "\n")


def success(message: str) -> None:
    print(f"  {paint('✔', GREEN, bold=True)} {paint(message, WHITE)}")


def error(message: str) -> None:
    print(f"\n  {paint('✖', RED, bold=True)} {paint(message, RED, bold=True)}\n", file=sys.stderr)


# ==========================================================
#  CORE LOGIC
# ==========================================================
class ToolError(Exception):
    """A user-facing error (bad input, missing file, ...)."""


class Base64Tool:
    """Encode and decode Base64 using the standard or the URL-safe alphabet."""

    _STD_RE = re.compile(r"^[A-Za-z0-9+/]*={0,2}$")
    _URL_RE = re.compile(r"^[A-Za-z0-9_\-]*={0,2}$")

    def __init__(self, urlsafe: bool = False) -> None:
        self.urlsafe = urlsafe

    def encode(self, data: bytes) -> str:
        func = base64.urlsafe_b64encode if self.urlsafe else base64.b64encode
        return func(data).decode("ascii")

    def decode(self, text: str) -> bytes:
        cleaned = "".join(text.split())  # ignore spaces and line breaks
        pattern = self._URL_RE if self.urlsafe else self._STD_RE
        if not pattern.match(cleaned):
            hint = "" if self.urlsafe else " (if it contains - or _, try --url-safe)"
            raise ValueError("Invalid Base64 characters" + hint)
        cleaned += "=" * (-len(cleaned) % 4)  # repair missing padding
        func = base64.urlsafe_b64decode if self.urlsafe else base64.b64decode
        try:
            return func(cleaned)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(f"Malformed Base64 data: {exc}") from exc


def wrap_text(text: str, width: int) -> str:
    if width <= 0:
        return text
    return "\n".join(text[i:i + width] for i in range(0, len(text), width))


# ==========================================================
#  INPUT / OUTPUT
# ==========================================================
_STDIN = object()  # marker: "read from standard input"


def read_input(text, file_path: str | None) -> tuple[bytes, pathlib.Path | None]:
    """Return (data, source_path). Raises ToolError on any problem."""
    if file_path:
        if isinstance(text, str):
            raise ToolError("Use either TEXT or -f FILE, not both.")
        path = pathlib.Path(file_path).expanduser()
        if not path.is_file():
            raise ToolError(f"File not found: {path}")
        try:
            if path.stat().st_size > MAX_INPUT_BYTES:
                raise ToolError("Input file is larger than 64 MiB.")
            return path.read_bytes(), path
        except OSError as exc:
            raise ToolError(f"Cannot read '{path}': {exc.strerror or exc}") from exc
    if text is _STDIN:
        if sys.stdin.isatty():
            raise ToolError("No input. Provide TEXT, use -f FILE, or pipe data in.")
        data = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        if len(data) > MAX_INPUT_BYTES:
            raise ToolError("Input is larger than 64 MiB.")
        return data, None
    return text.encode("utf-8"), None


def write_output(path_str: str, data: bytes, force: bool, source: pathlib.Path | None) -> pathlib.Path:
    path = pathlib.Path(path_str).expanduser()
    if source is not None and path.exists() and path.samefile(source):
        raise ToolError("Output file must be different from the input file.")
    if path.exists() and not force:
        raise ToolError(f"'{path}' already exists. Use --force to overwrite it.")
    try:
        path.write_bytes(data)
    except OSError as exc:
        raise ToolError(f"Cannot write '{path}': {exc.strerror or exc}") from exc
    return path


# ==========================================================
#  CLI
# ==========================================================
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dark_ibrahim_b64",
        description=Brand.TAGLINE,
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-e", "--encode", nargs="?", const=_STDIN, metavar="TEXT",
                      help="encode TEXT (or stdin / -f file) to Base64")
    mode.add_argument("-d", "--decode", nargs="?", const=_STDIN, metavar="TEXT",
                      help="decode Base64 TEXT (or stdin / -f file)")
    parser.add_argument("-f", "--file", metavar="PATH", help="read input from a file")
    parser.add_argument("-o", "--output", metavar="PATH", help="write the result to a file")
    parser.add_argument("--force", action="store_true", help="overwrite the output file if it exists")
    parser.add_argument("-u", "--url-safe", action="store_true", help="use the URL-safe alphabet (- and _)")
    parser.add_argument("-w", "--wrap", type=int, default=0, metavar="N",
                        help="wrap encoded output every N characters (0 = off)")
    parser.add_argument("--raw", action="store_true", help="print only the result (script friendly)")
    parser.add_argument("--no-anim", action="store_true", help="disable animations")
    parser.add_argument("--no-banner", action="store_true", help="hide the banner")
    parser.add_argument("--no-color", action="store_true", help="disable colors")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def run(args: argparse.Namespace) -> int:
    if args.wrap < 0:
        raise ToolError("--wrap must be 0 or a positive number.")

    quiet = args.raw
    encoding = args.encode is not None
    source_arg = args.encode if encoding else args.decode

    if not quiet:
        if sys.stdout.isatty() and USE_COLOR and not args.no_banner:
            sys.stdout.write("\033[2J\033[H")  # clear screen
        if not args.no_banner:
            banner()

    data, source_path = read_input(source_arg, args.file)
    tool = Base64Tool(urlsafe=args.url_safe)

    if not quiet:
        label = "Initiating Encoding Sequence" if encoding else "Initiating Decoding Sequence"
        if args.no_anim:
            success(label)
        else:
            progress_effect(label)

    started = time.perf_counter()
    try:
        if encoding:
            result = wrap_text(tool.encode(data), args.wrap)
            out_bytes = result.encode("ascii")
        else:
            try:
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise ToolError("Input is not valid text. Base64 input must be plain text.") from exc
            out_bytes = tool.decode(text)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    elapsed_ms = (time.perf_counter() - started) * 1000

    if args.output:
        saved = write_output(args.output, out_bytes, args.force, source_path)
        if not quiet:
            success(f"Saved to {paint(str(saved), CYAN, bold=True)}")
    else:
        try:
            text_out = out_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ToolError("Decoded data is binary. Use -o FILE to save it.") from exc
        if quiet:
            print(text_out)
        else:
            result_panel("ENCODED" if encoding else "DECODED", text_out)

    if not quiet:
        stats_block(len(data), len(out_bytes), elapsed_ms, hashlib.sha256(out_bytes).hexdigest())
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    argv = sys.argv[1:] if argv is None else argv

    if not argv:  # no arguments: welcome screen
        init_color()
        banner()
        parser.print_help()
        return EXIT_OK

    args = parser.parse_args(argv)
    init_color(force_off=args.no_color or args.raw)
    try:
        return run(args)
    except ToolError as exc:
        error(str(exc))
        return EXIT_ERROR


def _use_utf8_streams() -> None:
    """Make sure box-drawing characters print correctly (e.g. on Windows)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    _use_utf8_streams()
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n  Interrupted by user.", file=sys.stderr)
        sys.exit(EXIT_INTERRUPTED)
    except BrokenPipeError:
        sys.exit(EXIT_OK)
