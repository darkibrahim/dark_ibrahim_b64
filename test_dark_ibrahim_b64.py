"""Unit tests. Run with:  python3 -m unittest -v"""
import contextlib
import io
import os
import tempfile
import unittest

import dark_ibrahim_b64 as b64


def cli(*argv):
    """Run the CLI, return (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = b64.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class Base64ToolTests(unittest.TestCase):
    def test_encode_known_value(self):
        self.assertEqual(b64.Base64Tool().encode(b"Hello World"), "SGVsbG8gV29ybGQ=")

    def test_decode_known_value(self):
        self.assertEqual(b64.Base64Tool().decode("SGVsbG8gV29ybGQ="), b"Hello World")

    def test_round_trip_unicode(self):
        tool = b64.Base64Tool()
        text = "আমার প্রথম টুল ✔"
        self.assertEqual(tool.decode(tool.encode(text.encode())).decode(), text)

    def test_missing_padding_is_repaired(self):
        self.assertEqual(b64.Base64Tool().decode("SGVsbG8"), b"Hello")

    def test_whitespace_is_ignored(self):
        self.assertEqual(b64.Base64Tool().decode("SGVs\nbG8="), b"Hello")

    def test_empty_input(self):
        tool = b64.Base64Tool()
        self.assertEqual(tool.encode(b""), "")
        self.assertEqual(tool.decode(""), b"")

    def test_invalid_characters_rejected(self):
        with self.assertRaises(ValueError):
            b64.Base64Tool().decode("not base64!!")

    def test_impossible_length_rejected(self):
        with self.assertRaises(ValueError):
            b64.Base64Tool().decode("A")

    def test_url_safe_alphabet(self):
        data = b"\xfb\xff"
        self.assertEqual(b64.Base64Tool().encode(data), "+/8=")
        self.assertEqual(b64.Base64Tool(urlsafe=True).encode(data), "-_8=")
        self.assertEqual(b64.Base64Tool(urlsafe=True).decode("-_8="), data)

    def test_wrap_text(self):
        self.assertEqual(b64.wrap_text("abcdef", 4), "abcd\nef")
        self.assertEqual(b64.wrap_text("abcdef", 0), "abcdef")


class CliTests(unittest.TestCase):
    def test_encode_raw(self):
        self.assertEqual(cli("-e", "Hello", "--raw")[:2], (0, "SGVsbG8=\n"))

    def test_decode_raw(self):
        self.assertEqual(cli("-d", "SGVsbG8=", "--raw")[:2], (0, "Hello\n"))

    def test_decode_error_returns_1(self):
        code, _, err = cli("-d", "@@@", "--no-banner", "--no-anim")
        self.assertEqual(code, 1)
        self.assertIn("Invalid Base64", err)

    def test_text_and_file_conflict(self):
        code, _, err = cli("-e", "hi", "-f", "x.txt", "--raw")
        self.assertEqual(code, 1)
        self.assertIn("not both", err)

    def test_missing_file(self):
        code, _, err = cli("-e", "-f", "does_not_exist.txt", "--raw")
        self.assertEqual(code, 1)
        self.assertIn("File not found", err)

    def test_file_round_trip_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "in.txt")
            enc = os.path.join(tmp, "out.b64")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write("secret notes")
            self.assertEqual(cli("-e", "-f", src, "-o", enc, "--raw")[0], 0)
            with open(enc, encoding="utf-8") as fh:
                self.assertEqual(fh.read(), "c2VjcmV0IG5vdGVz")
            code, _, err = cli("-e", "-f", src, "-o", enc, "--raw")
            self.assertEqual(code, 1)
            self.assertIn("--force", err)
            self.assertEqual(cli("-e", "-f", src, "-o", enc, "--force", "--raw")[0], 0)

    def test_version_flag(self):
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(io.StringIO()):
                b64.main(["--version"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
