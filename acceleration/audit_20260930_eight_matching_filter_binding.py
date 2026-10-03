"""Bind the completed independent eight-coordinate filter audit to its claim."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    base = Path('acceleration/results/20260930_independent_review')
    summary_path = base / 'eight_coordinate_matching_filter/summary.json'
    expected = '4fcd5fd7f02cd5362bda1f8f0a1c8e4669ce036bde56a04dcd1b6a3391b262f4'
    assert digest(summary_path) == expected
    summary = json.loads(summary_path.read_text())
    assert summary['status'] == 'INDEPENDENT_EIGHT_COORDINATE_NEIGHBORHOOD_MATCHING_FILTER_PASS'
    assert [r['outer_vertex'] for r in summary['records']] == list(range(84))
    assert summary['counts']['original_count'] == 2290122
    assert summary['counts']['rejected_count'] == 414908
    assert summary['counts']['surviving_count'] == 1875214
    assert summary['empty_domains'] == 0 and summary['producer_imported'] is False
    for field in ('original_count', 'rejected_count', 'surviving_count'):
        assert sum(r[field] for r in summary['records']) == summary['counts'][field]
    files = [summary_path, base / 'eight_domains_claim_binding.json',
             base / 'eight_filter_protocol.md',
             base / 'eight_coordinate_matching_filter/DERIVATION.md',
             Path('acceleration/audit_20260930_eight_coordinate_matching_filter.py'),
             Path('acceleration/results/20260930_eight_matching_filter/run01/manifest.json'),
             Path('acceleration/results/20260930_eight_matching_filter/run01/summary.json'),
             Path('uv.lock'), Path(__file__)]
    for name in ('acceleration/audit_20260930_eight_coordinate_matching_filter.py',
                 'acceleration/audit_20260917_partial_matching.py',
                 'acceleration/audit_20260917_triangle_matching.py',
                 'acceleration/audit_compressed_artifacts.py'):
        assert digest(name) == summary['inputs_sha256'][name]
    record = {
        'status': 'INDEPENDENT_EIGHT_COORDINATE_MATCHING_FILTER_CLAIM_BINDING_PASS',
        'claim_id': summary['claim_id'], 'claim_revision': 1, 'recommendation': 'VERIFIED',
        'verifier': 'Codex subagent /root/state_literature_audit',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'statement': 'For every one of the 2290122 independently audited eight-coordinate local center stars, the saved surviving IDs are exactly those whose individually cap-permitted residual neighborhood graph has a perfect matching. Exactly 414908 stars fail this necessary condition and 1875214 survive, with no empty center domain; every target extension of the declared fixed family must use surviving stars.',
        'scope': summary['scope'],
        'dependencies': [{'id': 'C-PARTIAL-K-EIGHT-COORDINATE-DOMAINS', 'revision': 1, 'relation': 'coverage'}],
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(Path.cwd()),
        'python': platform.python_version(),
        'inputs_sha256': {p.as_posix(): digest(p) for p in files},
        'checking_method': summary['method'],
        'counts': summary['counts'], 'centers': 84, 'empty_domains': 0,
        'controls': summary['controls'],
        'verification_type': 'independent_artifact_check plus independently reviewed written necessity derivation',
        'shared_components': summary['shared_components'],
        'limitations': summary['limitations'],
        'numeric_acceptance_threshold': None,
        'numeric_acceptance_threshold_reason': 'All checks are exact integer or finite combinatorial checks.',
        'random_seed': None, 'random_seed_reason': 'Deterministic checking with no randomized step.',
        'target_resolution': False,
        'external_review': None, 'external_review_reason': 'Internal independent audit; no external review claimed.'
    }
    out = Path(args.out)
    with out.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(record, handle, indent=2)
        handle.write('\n')
    print(json.dumps({'status': record['status'], 'out': str(out), 'sha256': digest(out)}))


if __name__ == '__main__':
    main()
