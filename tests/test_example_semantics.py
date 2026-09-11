import ast
import re
import unittest
from pathlib import Path


class CodeExampleSemantics(unittest.TestCase):
    def test_rewrite_keeps_executable_behavior(self):
        text = (Path(__file__).parents[1] / 'samples/code-pairs.md').read_text()
        blocks = re.findall(r'```python\n(.*?)```', text, re.S)
        self.assertGreaterEqual(len(blocks), 2)
        self.assertEqual(ast.dump(ast.parse(blocks[0])), ast.dump(ast.parse(blocks[1])))
