"""Adversarial controls for the narrow historical parse-failure CI exception."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from check_python_syntax import check_sources, digest


class SyntaxSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'acceleration').mkdir()
        self.name = 'acceleration/preserved.py'
        self.source = self.root / self.name
        self.source.write_bytes(b'x = 1 if True else2\n')
        self.evidence = self.root / 'failure.json'
        self.evidence.write_text(json.dumps(dict(source_sha256=digest(self.source.read_bytes()),
                                                research_executed=False)), encoding='utf8')
        self.record = dict(sha256=digest(self.source.read_bytes()), failure_path='failure.json',
                           failure_sha256=digest(self.evidence.read_bytes()), line=1,
                           message="expected 'else' after 'if' expression")
        self.preserved = {self.name: self.record}

    def test_expected_failure_and_live_sources_are_both_checked_without_execution(self):
        (self.root / 'active.py').write_text("raise RuntimeError('must not execute')\n", encoding='utf8')
        result = check_sources(self.root, self.preserved)
        self.assertEqual(result['compiled_sources'], 1)
        self.assertEqual(result['authenticated_preserved_failures'], [self.name])
        self.assertFalse(result['source_execution'])

    def test_unregistered_error_is_fatal(self):
        (self.root / 'active.py').write_text('x = (\n', encoding='utf8')
        with self.assertRaises(SyntaxError):
            check_sources(self.root, self.preserved)

    def test_no_broad_failure_exemption(self):
        with self.assertRaises(SyntaxError):
            check_sources(self.root, {})

    def test_changed_historical_source_is_fatal(self):
        self.source.write_bytes(self.source.read_bytes() + b'# changed\n')
        with self.assertRaisesRegex(ValueError, 'source bytes changed'):
            check_sources(self.root, self.preserved)

    def test_changed_receipt_is_fatal(self):
        self.evidence.write_bytes(self.evidence.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'receipt changed'):
            check_sources(self.root, self.preserved)

    def test_missing_historical_source_is_fatal(self):
        self.source.unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            check_sources(self.root, self.preserved)

    def test_missing_receipt_is_fatal(self):
        self.evidence.unlink()
        with self.assertRaises(FileNotFoundError):
            check_sources(self.root, self.preserved)

    def test_wrong_line_or_diagnostic_is_fatal(self):
        for field, value in [('line', 2), ('message', 'a different error')]:
            with self.subTest(field=field):
                records = {self.name: dict(self.record, **{field: value})}
                with self.assertRaisesRegex(ValueError, 'syntax failure changed'):
                    check_sources(self.root, records)

    def test_hash_matching_but_wrong_provenance_is_fatal(self):
        self.evidence.write_text(json.dumps(dict(source_sha256='0' * 64, research_executed=False)), encoding='utf8')
        self.record['failure_sha256'] = digest(self.evidence.read_bytes())
        with self.assertRaisesRegex(ValueError, 'provenance'):
            check_sources(self.root, self.preserved)

    def test_valid_source_cannot_be_silently_exempted(self):
        self.source.write_bytes(b'x = 1\n')
        self.record['sha256'] = digest(self.source.read_bytes())
        self.evidence.write_text(json.dumps(dict(source_sha256=self.record['sha256'], research_executed=False)), encoding='utf8')
        self.record['failure_sha256'] = digest(self.evidence.read_bytes())
        with self.assertRaisesRegex(ValueError, 'unexpectedly compiles'):
            check_sources(self.root, self.preserved)


if __name__ == '__main__':
    unittest.main()
