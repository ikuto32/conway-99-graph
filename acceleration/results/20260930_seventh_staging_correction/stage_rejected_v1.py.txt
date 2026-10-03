"""Stage only the reviewed seventh inventory and bind exact index bytes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
CAT = ROOT/(B+'seventh_artifact_packaging')

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def read(path):
    return json.loads(path.read_bytes())

def main():
    existing = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, text=True).strip()
    if existing:
        raise ValueError('index already contains changes')
    if digest(CAT/'catalog.json') != '150050d18fda0318e370566b253b8cf506c847fdd3c8b8fbb7d3be835f0ba756':
        raise ValueError('catalog changed')
    proposal = read(CAT/'stage_inventory.json')
    paths = set(proposal['paths'])
    frozen = read(CAT/'untracked_inventory.json')['entries'] + read(CAT/'raw_logs_publication.json')['entries']
    for row in frozen:
        path = ROOT/row['path']
        if digest(path) != row['sha256'] or path.stat().st_size != row['bytes']:
            raise ValueError('frozen publication input changed '+row['path'])
    paths.update(path.relative_to(ROOT).as_posix() for path in CAT.iterdir() if path.is_file())
    paths.update(['README.md', 'ACTIVE_RESEARCH.md', 'CLAIMS.yaml', '.gitignore', 'docs/RESEARCH_MAP.md',
        'docs/REPRODUCING.md', 'docs/RESEARCH_20260930_SEVENTH_WAVE.md', 'docs/REPRODUCING_20260930_SEVENTH_WAVE.md',
        'acceleration/stage_20260930_seventh_evidence.py', B+'resume/seventh_milestone_checkpoint.json',
        B+'resume/claims_at_seventh_milestone.yaml', B+'resume/seventh_native_process_snapshot.stdout.log',
        B+'resume/seventh_native_process_snapshot.stderr.log', B+'resume/seventh_precommit_validation.json'])
    forbidden = ('matching_pair_census', 'proof_core', 'row_obstruction', 'p_core')
    for name in paths:
        path = ROOT/name
        if any(term in name.lower() for term in forbidden) or name == 'PROMPT.md' or name.startswith('tools/'):
            raise ValueError('out-of-wave publication path '+name)
        if not path.resolve().is_relative_to(ROOT) or not path.is_file() or path.stat().st_size > 10*1024**2:
            raise ValueError('invalid/missing/oversized stage path '+name)
    if paths.intersection(proposal['oversized_raw_paths_not_to_stage']):
        raise ValueError('raw oversize included')
    ignore = ROOT/'.gitignore'
    original = ignore.read_bytes()
    lines = (CAT/'proposed_gitignore.txt').read_text().splitlines()
    new = [line for line in lines if line and line not in original.decode().splitlines()]
    ignore.write_bytes(original + (b'' if original.endswith(b'\n') else b'\n') + ('\n'.join(new)+'\n').encode())
    ordered = sorted(paths)
    for start in range(0, len(ordered), 40):
        subprocess.run(['git', 'add', '-f', '--', *ordered[start:start+40]], cwd=ROOT, check=True, capture_output=True)
    names = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).decode().split('\0')
    names = sorted(name for name in names if name)
    if set(names) != paths:
        raise ValueError('unexpected staged path set')
    blob = subprocess.run(['git', 'cat-file', '--batch'], input=''.join(':'+name+'\n' for name in names).encode(), cwd=ROOT, capture_output=True, check=True).stdout
    offset, checked = 0, []
    secret = re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for name in names:
        end = blob.index(b'\n', offset)
        fields = blob[offset:end].split()
        if len(fields) != 3 or fields[1] != b'blob':
            raise ValueError('missing index blob '+name)
        size = int(fields[2]); content = blob[end+1:end+1+size]; offset = end+size+2
        hashed = hashlib.sha256(content).hexdigest()
        if hashed != digest(ROOT/name):
            raise ValueError('index/worktree byte mismatch '+name)
        if secret.search(content):
            raise ValueError('credential-shaped material needs review '+name)
        checked.append(dict(path=name, sha256=hashed, bytes=size, git_blob=fields[0].decode()))
    assert offset == len(blob)
    report_path = ROOT/(B+'resume/seventh_staging_check.json')
    with report_path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(dict(timestamp=datetime.now(timezone.utc).isoformat(), command=[sys.executable, *sys.argv], cwd=str(ROOT),
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            scope='Exact seventh-wave publication path inventory and raw Git index identities; no mathematical verification.',
            staged_paths=checked, checked_index_blobs=len(checked), frozen_inventory_entries_checked=len(frozen),
            ignore_before_sha256=hashlib.sha256(original).hexdigest(), ignore_after_sha256=digest(ignore),
            credential_shape_scan='No matches for the documented token/private-key patterns; not a universal secret-detection claim.',
            preserved_user_changes=['PROMPT.md', 'tools/drat-trim'], deferred_patterns=list(forbidden),
            mathematical_verification=False), handle, indent=2)
        handle.write('\n')
    subprocess.run(['git', 'add', '--', report_path.relative_to(ROOT).as_posix()], cwd=ROOT, check=True)
    print(json.dumps({'staged_and_byte_checked': len(checked), 'receipt_added_separately': True, 'target_resolution': 'UNKNOWN'}))

if __name__ == '__main__':
    main()
