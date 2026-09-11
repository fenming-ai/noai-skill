"""公开包在独立目录中的脚本边界与异常验证。"""
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from tests.check_text import load_ai_words, check_quotes

ROOT = Path(__file__).resolve().parents[1]


class StandaloneCLI(unittest.TestCase):
    def run_scan(self, content, strict=False):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'input.md'
            p.write_bytes(content)
            return subprocess.run(
                [sys.executable, '-I', str(ROOT/'tests/check_text.py'), str(p)]
                + (['--strict'] if strict else []), cwd=tmp,
                capture_output=True, text=True, timeout=15)

    def test_report_and_strict_have_different_exit_codes(self):
        text = '此外，这一步保留原始记录。'.encode()
        self.assertEqual(self.run_scan(text).returncode, 0)
        self.assertEqual(self.run_scan(text, True).returncode, 1)

    def test_empty_and_large_plain_text(self):
        for text in [b'', ('记录已保存。\n'*10000).encode()]:
            with self.subTest(size=len(text)):
                self.assertEqual(self.run_scan(text, True).returncode, 0)

    def test_invalid_encoding_is_handled(self):
        result = self.run_scan(b'\xff\xfe', True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('Traceback', result.stderr)

    def test_missing_input_and_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            for p in [Path(tmp)/'missing.md', Path(tmp)]:
                result = subprocess.run([sys.executable, '-I', str(ROOT/'tests/check_text.py'), str(p)],
                                        cwd=tmp, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn('Traceback', result.stderr)

    def test_rules_missing_empty_malformed_and_invalid_encoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'rules.md'
            for content in [None, b'', b'## unrelated\n', b'\xff', '## text 媒介\n无词条\n'.encode()]:
                if content is not None:
                    p.write_bytes(content)
                with self.subTest(content=content), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as exc:
                        load_ai_words(p)
                    self.assertEqual(exc.exception.code, 1)

    def test_quote_thresholds(self):
        for count in [6, 7, 10, 11]:
            self.assertEqual(check_quotes('“'*count), count)
            result = self.run_scan(('“'*count).encode(), True)
            self.assertEqual(result.returncode, 1 if count > 10 else 0)


if __name__ == '__main__':
    unittest.main()
