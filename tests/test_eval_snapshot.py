import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('eval_snapshot', Path(__file__).parents[1] / 'scripts/eval_snapshot.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SnapshotTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'skill'
        self.root.mkdir()
        def git(*args):
            return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)
        self.git = git
        git('init', '-b', 'main')
        for name in mod.CORE + ['samples/extra.md']:
            p = self.root / name
            p.parent.mkdir(exist_ok=True, parents=True)
            p.write_text('固定规则：' + name)
        git('add', '.')
        git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', '-c', 'commit.gpgsign=false', 'commit', '-m', 'fixture')

    def test_frozen_content_and_explicit_references(self):
        out = self.base / 'snapshot'
        m = mod.snapshot(self.root, out, ['samples/extra.md'])
        self.assertEqual(len(m['files']), 5)
        self.assertEqual(m['not_included'], [])
        self.assertEqual(json.loads((out / 'manifest.json').read_text()), m)
        for name in mod.CORE:
            self.assertEqual((out / 'files' / name).read_bytes(), (self.root / name).read_bytes())
        with self.assertRaises(ValueError):
            mod.snapshot(self.root, out)

    def test_default_does_not_claim_full_loading(self):
        m = mod.snapshot(self.root, self.base / 'snapshot')
        self.assertEqual(m['not_included'], ['samples/extra.md'])

    def test_dirty_tree_rejected(self):
        (self.root / 'SKILL.md').write_text('未提交修改')
        with self.assertRaises(ValueError):
            mod.snapshot(self.root, self.base / 'snapshot')

    def test_escape_and_in_repo_output_rejected(self):
        for name in ['../secret.md', '/tmp/secret.md', '.env']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                mod.snapshot(self.root, self.base / 'snapshot', [name])
        with self.assertRaises(ValueError):
            mod.snapshot(self.root, self.root / 'snapshot')
