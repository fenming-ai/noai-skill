"""核验中长文汇总的等权口径、缺失记录与篡改检测。"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPORT = Path(__file__).resolve().parents[1] / 'docs/evaluations/mixed-length'
spec = importlib.util.spec_from_file_location('mixed_recompute', REPORT / 'recompute.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MixedReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((REPORT / 'results.json').read_text())

    def test_equal_case_weighting(self):
        result = module.recompute(self.data)
        self.assertEqual(len(result), 7)
        for row in result:
            self.assertAlmostEqual(row['mean'], (row['long_mean'] * 6 + row['medium_score']) / 7)
        self.assertEqual(len(self.data['ratings']), 91)

    def test_missing_duplicate_or_invalid_rating(self):
        for failure in ['missing', 'duplicate', 'panel', 'score', 'nan']:
            d = copy.deepcopy(self.data)
            if failure == 'missing': d['ratings'].pop()
            elif failure == 'duplicate': d['ratings'][-1] = d['ratings'][0]
            elif failure == 'panel': d['ratings'][-1]['panel'] = 'A'
            elif failure == 'score': d['ratings'][0]['scores']['facts'] = True
            else: d['ratings'][0]['total'] = float('nan')
            with self.subTest(failure=failure), self.assertRaises(ValueError): module.recompute(d)

    def test_score_endpoints(self):
        for endpoint in [0, 4]:
            d = copy.deepcopy(self.data)
            for row in d['ratings']:
                row['scores'] = dict.fromkeys(row['scores'], endpoint)
                row['total'] = endpoint * 25
            for row in d['summary']:
                row.update(mean=endpoint*25, long_mean=endpoint*25, medium_score=endpoint*25, rank=1)
            d['summary'].sort(key=lambda r:r['arm'])
            self.assertTrue(all(r['mean']==endpoint*25 for r in module.recompute(d)))

    def test_summary_tampering_rejected(self):
        for field in ['mean', 'long_mean', 'medium_score', 'rank']:
            d = copy.deepcopy(self.data);d['summary'][0][field] = -1
            with self.subTest(field=field), self.assertRaises(ValueError):module.recompute(d)

    def test_source_or_output_tampering_rejected(self):
        for kind in ['source', 'output']:
            d=copy.deepcopy(self.data)
            if kind=='source':d['cases'][0]['text']+='改动'
            else:d['outputs'][d['arms'][0]][d['cases'][0]['id']]=''
            with self.subTest(kind=kind), self.assertRaises(ValueError):module.recompute(d)

    def test_medium_full_text_is_not_redistributed(self):
        c=next(c for c in self.data['cases'] if c['group']=='medium')
        self.assertNotIn('text',c)
        for arm in self.data['arms']:
            self.assertNotIn(c['id'],self.data['outputs'][arm])
        for row in self.data['ratings']:
            if row['case_id']==c['id']:self.assertNotIn('evidence',row)

    def test_cli_failure(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'broken.json';path.write_text('{')
            for target in [path,Path(d)/'missing.json']:
                run=subprocess.run([sys.executable,str(REPORT/'recompute.py'),str(target)],capture_output=True,text=True,timeout=10)
                self.assertEqual(run.returncode,1)
                self.assertIn('核验失败',run.stderr)


if __name__=='__main__':unittest.main()
