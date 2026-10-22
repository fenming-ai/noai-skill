"""私有声音库扩展：公开仓库只提供机制，不含私有内容。"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
REF = ROOT / 'references' / 'private-voice.md'

# 公开仓库里不应出现的私有线索：个人目录、私有仓库名
PRIVATE_MARKERS = re.compile(r'/home/[a-z]|/Users/[A-Za-z]|pcommon|relunctance|gaoqilin')
PUBLIC_DIRS = ['SKILL.md', 'references', 'samples']


class PrivateVoiceContract(unittest.TestCase):
    def test_reference_exists_and_is_linked(self):
        self.assertTrue(REF.is_file())
        self.assertIn('references/private-voice.md', SKILL)

    def test_discovery_and_fallback_are_documented(self):
        ref = REF.read_text(encoding='utf-8')
        for key in ['NOAI_VOICE_DIR', 'voiceDir', 'VOICE.md', 'pairs/', 'candidates/']:
            self.assertIn(key, ref)
        self.assertIn('行为与以前完全一致', ref)

    def test_feedback_goes_to_private_candidates_not_public_samples(self):
        step6 = SKILL.split('### 步骤 6')[1].split('## 加载策略')[0]
        self.assertIn('candidates/', step6)
        self.assertIn('不写入本仓库', step6)

    def test_public_files_have_no_private_markers(self):
        hits = []
        for name in PUBLIC_DIRS:
            path = ROOT / name
            files = [path] if path.is_file() else sorted(path.rglob('*.md'))
            for f in files:
                for no, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
                    if PRIVATE_MARKERS.search(line):
                        hits.append(f'{f.relative_to(ROOT)}:{no}')
        self.assertEqual(hits, [])


if __name__ == '__main__':
    unittest.main()
