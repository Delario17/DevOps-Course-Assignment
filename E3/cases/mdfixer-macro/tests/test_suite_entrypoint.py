"""Exercise suite failure handling with test doubles, not experiment evidence."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ENTRY = Path(__file__).resolve().parents[1] / 'scripts/run_mdfixer_all.py'


@unittest.skipUnless(sys.platform == 'linux', 'The entrypoint intentionally requires Linux')
class SuiteEntrypointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='e3-suite-tests-')
        self.addCleanup(self.temporary.cleanup)
        self.e3 = Path(self.temporary.name) / 'E3'
        self.case = self.e3 / 'cases/mdfixer-macro'
        (self.case / 'scripts').mkdir(parents=True)
        shutil.copy2(ENTRY, self.case / 'scripts/run_mdfixer_all.py')

    def add_case(self, case, fail=False, record=None):
        directory = self.e3 / f'cases/mdfixer-{case}'
        for relative in ['fixture/Makefile', 'oracle/expected.json', 'patches/reference.patch', 'patches/invalid.patch']:
            path = directory / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('TEST DOUBLE ONLY\n')
        code = '''import argparse, json
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--operator')
p.add_argument('--output', type=Path)
a = p.parse_args()
a.output.mkdir()
(a.output / 'observations.json').write_text(json.dumps(RECORD))
raise SystemExit(EXIT)
'''.replace('RECORD', repr(record if record is not None else {'status': 'FAIL' if fail else 'PASS', 'assertions': [{'passed': not fail}]})).replace('EXIT', '1' if fail else '0')
        (directory / 'scripts').mkdir(parents=True, exist_ok=True)
        (directory / 'scripts/run.py').write_text(code)

    def run_suite(self, *options):
        output = self.case / '.runs/test'
        result = subprocess.run([sys.executable, str(self.case / 'scripts/run_mdfixer_all.py'),
                                 '--operator', 'automated test double', '--output', str(output), *options],
                                capture_output=True, text=True, timeout=20)
        summary_path = output / 'summary.json'
        return result, json.loads(summary_path.read_text()) if summary_path.exists() else None

    def test_default_reports_missing_cases_and_still_runs_present_case(self):
        self.add_case('macro')
        result, summary = self.run_suite()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(summary['status'], 'FAIL')
        self.assertEqual([r['status'] for r in summary['cases']], ['MISSING', 'PASS', 'MISSING', 'MISSING'])

    def test_available_is_explicit_partial_success(self):
        self.add_case('macro')
        result, summary = self.run_suite('--cases', 'available')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(summary['status'], 'PASS_SELECTED')
        self.assertEqual(summary['selected'], ['macro'])

    def test_failed_case_does_not_prevent_later_evidence(self):
        for case in ('target', 'macro', 'hybrid', 'implicit'):
            self.add_case(case, fail=case == 'macro')
        result, summary = self.run_suite()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(summary['status'], 'FAIL')
        self.assertEqual([r['status'] for r in summary['cases']], ['PASS', 'FAIL', 'PASS', 'PASS'])
        self.assertTrue((self.case / '.runs/test/implicit/observations.json').exists())

    def test_all_four_required_for_full_success(self):
        for case in ('target', 'macro', 'hybrid', 'implicit'):
            self.add_case(case)
        result, summary = self.run_suite()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(summary['status'], 'PASS')

    def test_empty_available_is_failure(self):
        result, summary = self.run_suite('--cases', 'available')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(summary['status'], 'FAIL')

    def test_malformed_evidence_fails_and_later_case_runs(self):
        self.add_case('macro', record=['invalid observation shape'])
        self.add_case('hybrid')
        result, summary = self.run_suite('--cases', 'macro', 'hybrid')
        self.assertEqual(result.returncode, 1)
        self.assertEqual([r['status'] for r in summary['cases']], ['FAIL', 'PASS'])

    def test_success_label_without_assertions_is_not_accepted(self):
        self.add_case('macro', record={'status': 'PASS', 'assertions': []})
        result, summary = self.run_suite('--cases', 'macro')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(summary['cases'][0]['status'], 'FAIL')

    def test_existing_evidence_is_not_overwritten(self):
        output = self.case / '.runs/test'
        output.mkdir(parents=True)
        (output / 'sentinel').write_text('keep')
        result, _ = self.run_suite()
        self.assertEqual(result.returncode, 2)
        self.assertEqual((output / 'sentinel').read_text(), 'keep')

    def test_invalid_selection_and_source_output_are_rejected(self):
        result, _ = self.run_suite('--cases', 'available', 'macro')
        self.assertEqual(result.returncode, 2)
        result, _ = self.run_suite('--output', str(self.case / 'fixture/new'))
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.case / 'fixture/new').exists())

    def test_target_uses_independent_case_directory(self):
        self.add_case('target')
        result, summary = self.run_suite('--cases', 'target')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(summary['cases'][0]['status'], 'PASS')

    def test_output_cannot_write_a_sibling_case(self):
        sibling = self.e3 / 'cases/mdfixer-hybrid/evidence/not-owned'
        result, _ = self.run_suite('--output', str(sibling))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(sibling.exists())

    def test_default_output_stays_in_owned_case(self):
        for case in ('target', 'macro', 'hybrid', 'implicit'):
            self.add_case(case)
        result = subprocess.run([sys.executable, str(self.case / 'scripts/run_mdfixer_all.py'),
                                 '--operator', 'automated test double'], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0)
        summaries = list((self.case / 'evidence/suite').glob('*/summary.json'))
        self.assertEqual(len(summaries), 1)
        self.assertEqual(json.loads(summaries[0].read_text())['status'], 'PASS')
        for peer in ['mdfixer-hybrid', 'mdfixer-implicit']:
            self.assertFalse((self.e3 / 'cases' / peer / 'evidence').exists())


if __name__ == '__main__':
    unittest.main()
