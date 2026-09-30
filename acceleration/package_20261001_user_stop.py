"""Prepare an explicit small stop-package allowlist; no solver or research calls."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import re
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'acceleration/results/20261001_user_stop'


def main():
    selected = {'README.md', 'ACTIVE_RESEARCH.md', 'STOPPED_BY_USER.md', 'CLAIMS.yaml',
                'docs/RESEARCH_MAP.md', 'docs/REPRODUCING.md', 'docs/STOP_20261001_EIGHT_COORDINATE.md'}
    # Direct children only. This deliberately excludes all bulk results and user files.
    for parent in ['acceleration', 'docs']:
        for path in (ROOT / parent).iterdir():
            if path.is_file() and '20261001' in path.name and path.suffix in {'.py', '.md'}:
                rel = path.relative_to(ROOT).as_posix()
                if subprocess.run(['git', 'ls-files', '--error-unmatch', '--', rel], cwd=ROOT, capture_output=True).returncode:
                    selected.add(rel)
    ledger = yaml.safe_load((ROOT / 'CLAIMS.yaml').read_bytes())
    checkpoint = json.loads((OUT / 'checkpoint.json').read_bytes())
    artifacts = {a['id']: a for a in ledger['artifacts']}
    for claim in ledger['claims']:
        if claim['id'] in checkpoint['new_verified_ids']:
            for aid in claim['evidence']:
                selected.add(artifacts[aid]['path'])
    folders = ['20261001_thirtieth_initial_registration', '20261001_stop_registration']
    for folder in folders:
        for name in ['summary.json', 'CLAIMS.before.yaml', 'CLAIMS.after.yaml', 'validation.json', 'controls.json', 'transaction.json']:
            path = 'acceleration/results/' + folder + '/' + name
            if (ROOT / path).is_file():
                selected.add(path)
    for name in ['checkpoint.json', 'resume_plan.json', 'CLAIMS.snapshot.yaml']:
        selected.add((OUT / name).relative_to(ROOT).as_posix())
    prefix = 'acceleration/results/20261001_exact_eight_prefix64_batch05_execution/'
    for name in ['user_stop_checkpoint.json', 'user_stop_directive.json', 'final_stop_process_observation.json',
                 'final_stop_process_observation.wsl.stdout.log', 'final_stop_process_observation.wsl.stderr.log',
                 'build_invocation_refusal.json', 'builds.receipt.json', 'consolidation.receipt.json',
                 'request_freeze.receipt.json', 'selection.receipt.json']:
        selected.add(prefix + name)
    selected.add('acceleration/results/20261001_independent_review/exact_eight_prefix64_batch05_object_calibration/summary.json')
    selected.add('acceleration/results/20261001_wave205_third_star_execution_provenance/receipt.json')
    patterns = [rb'gh[pousr]_[A-Za-z0-9]{30,}', rb'github_pat_[A-Za-z0-9_]{35,}',
                rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', rb'AKIA[0-9A-Z]{16}',
                rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{35,}']
    records, syntax = [], []
    for name in sorted(selected):
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT) and name != 'PROMPT.md' and not name.startswith('tools/')
        assert 'hadamard_oriented_unknown' not in name
        raw = path.read_bytes()
        assert len(raw) < 25 * 1024 * 1024, ('oversize stop metadata', name)
        assert not any(re.search(pattern, raw) for pattern in patterns), ('credential-shaped content', name)
        if path.suffix == '.py':
            ast.parse(raw, filename=name)
            syntax.append(name)
        records.append(dict(path=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    record = dict(timestamp=datetime.now(timezone.utc).isoformat(), status='STOP_PACKAGE_ALLOWLIST_PREPARED',
                  source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  selected_files=records, selected_count=len(records), selected_bytes=sum(r['bytes'] for r in records),
                  parsed_python_sources=syntax, credential_shape_scan='No matches in selected files; bounded pattern scan only.',
                  raw_evidence_public_replay=False, publication_state='NOT_YET_COMMITTED_OR_PUSHED',
                  independent_source_only_reviews=[
                      dict(verifier='/root/state_literature_audit', subject='acceleration/register_20261001_stop_claims.py', sha256='5325fb1eee85b13825a8806e3d92b6911740e498c4eb32ff85bf307879a0dc04', outcome='No source-only blocker found; no execution or mathematical approval.', timestamp=None, reason='Exact completion timestamp not supplied by reviewer; message received before package generation.'),
                      dict(verifier='/root/state_literature_audit', subject='acceleration/record_20261001_user_stop.py', outcome='No source-only blocker found; counts/scopes and native CLI reviewed, no execution.', timestamp=None, reason='Exact completion timestamp not supplied by reviewer; message received before package generation.')],
                  limitations=['This allowlist preserves metadata and sources, not the complete new evidence closure.', 'AST syntax checking and registration schema checking are not mathematical verification.', 'Bulk raw artifacts and rejected-run logs are preserved locally and not deleted.'])
    with (OUT / 'package_manifest.json').open('x', encoding='utf8', newline='\n') as f:
        json.dump(record, f, indent=2)
        f.write('\n')
    selected.add((OUT / 'package_manifest.json').relative_to(ROOT).as_posix())
    with (OUT / 'git_paths.txt').open('x', encoding='utf8', newline='\n') as f:
        f.write('\n'.join(sorted(selected)) + '\n')
    print(json.dumps({k: record[k] for k in ['selected_count', 'selected_bytes', 'credential_shape_scan']}))


if __name__ == '__main__':
    main()
