"""公开长文报告的原始数据、复算和失败边界验证。"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPORT = Path(__file__).resolve().parents[1] / 'docs/evaluations/long-form'
spec = importlib.util.spec_from_file_location('long_report_recompute', REPORT / 'recompute.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LongReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((REPORT / 'results.json').read_text())

    def test_complete_report_recomputes(self):
        result = module.recompute(self.data)
        self.assertEqual(len(result), 7)
        self.assertEqual(len(self.data['ratings']), 84)
        self.assertEqual(len(self.data['cases']), 6)

    def test_valid_score_endpoints(self):
        for endpoint in [0, 4]:
            data = copy.deepcopy(self.data)
            for row in data['ratings']:
                row['scores'] = dict.fromkeys(row['scores'], endpoint)
                row['total'] = endpoint * 25
            for row in data['summary']:
                row.update(mean=endpoint * 25, panel_A=endpoint * 25, panel_B=endpoint * 25, rank=1)
            data['summary'].sort(key=lambda row: row['arm'])
            with self.subTest(endpoint=endpoint):
                self.assertTrue(all(row['mean'] == endpoint * 25 for row in module.recompute(data)))

    def test_missing_or_duplicate_rating_rejected(self):
        for duplicate in [False, True]:
            data = copy.deepcopy(self.data)
            if duplicate:
                data['ratings'][-1] = copy.deepcopy(data['ratings'][0])
            else:
                data['ratings'].pop()
            with self.subTest(duplicate=duplicate), self.assertRaises(ValueError):
                module.recompute(data)

    def test_invalid_scores_rejected(self):
        for value in [None, True, -1, 5, 2.5]:
            data = copy.deepcopy(self.data)
            dim = next(iter(data['ratings'][0]['scores']))
            data['ratings'][0]['scores'][dim] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.recompute(data)

    def test_source_and_output_tampering_rejected(self):
        for target in ['source', 'output']:
            data = copy.deepcopy(self.data)
            if target == 'source':
                data['cases'][0]['text'] += '改动'
            else:
                arm = next(iter(data['outputs']))
                case = next(iter(data['outputs'][arm]))
                data['outputs'][arm][case] += '改动'
            with self.subTest(target=target), self.assertRaises(ValueError):
                module.recompute(data)

    def test_cached_score_and_order_tampering_rejected(self):
        for target in ['total', 'mean', 'panel', 'rank', 'order']:
            data = copy.deepcopy(self.data)
            if target == 'total':
                data['ratings'][0]['total'] = float('nan')
            elif target == 'mean':
                data['summary'][0]['mean'] = float('nan')
            elif target == 'panel':
                data['summary'][0]['panel_A'] = -1
            elif target == 'rank':
                data['summary'][0]['rank'] = 99
            else:
                data['summary'].reverse()
            with self.subTest(target=target), self.assertRaises(ValueError):
                module.recompute(data)

    def test_empty_evidence_and_output_rejected(self):
        for target in ['evidence', 'output']:
            data = copy.deepcopy(self.data)
            if target == 'evidence':
                dim = next(iter(data['ratings'][0]['evidence']))
                data['ratings'][0]['evidence'][dim] = ' '
            else:
                arm = next(iter(data['outputs']))
                data['outputs'][arm][next(iter(data['outputs'][arm]))] = ''
            with self.subTest(target=target), self.assertRaises(ValueError):
                module.recompute(data)

    def test_cli_errors_are_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            malformed = Path(directory) / 'broken.json'
            malformed.write_text('{')
            for path in [malformed, Path(directory) / 'missing.json']:
                run = subprocess.run([sys.executable, str(REPORT / 'recompute.py'), str(path)], capture_output=True, text=True, timeout=10)
                self.assertEqual(run.returncode, 1)
                self.assertIn('核验失败', run.stderr)


if __name__ == '__main__':
    unittest.main()
