"""Authenticate exact late root metadata and staged Python syntax before publication."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
ALLOW = 'acceleration/results/20261003_wave36_allowlist02/manifest.json'
ALLOW_SHA = '83e995d249766549450f46e92b0a2bc9c27038eafb96af82352eb7fc2802c5b4'
EXTRAS = ['.gitattributes', 'docs/REPLAY_20261003_WAVE36_COUPLING_CONTROL.md', 'docs/DEVIATION_20261003_WAVE36_INDEX_POLICY_BYTES.md', 'acceleration/stage_20261003_wave36_index_v1.py']
ROOTS = ['acceleration/results/20261003_wave36_allowlist_supervision02', 'acceleration/results/20261003_wave36_index01', 'acceleration/results/20261003_wave36_index02', 'acceleration/results/20261003_wave36_index_supervision01', 'acceleration/results/20261003_wave36_index_supervision02']


def require(ok, why):
    if not ok:
        raise ValueError(why)


def hashes(path):
    raw = path.read_bytes()
    return len(raw), hashlib.sha256(raw).hexdigest(), hashlib.sha1(('blob ' + str(len(raw)) + '\0').encode('ascii') + raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exact late root metadata/index/PythonAST checks after existing1839rawobjects passed;120outer90worker15reserve, no mathematical replay')
    require(hashes(ROOT / ALLOW)[1] == ALLOW_SHA, 'frozen allowlist')
    manifest = json.loads((ROOT / ALLOW).read_bytes())
    require(hashes(ROOT / 'CLAIMS.yaml')[1] == manifest['ledger_sha256'], '337ledger unchanged')
    paths = set(EXTRAS + [Path(__file__).relative_to(ROOT).as_posix()])
    for name in ROOTS:
        directory = ROOT / name
        require(directory.is_dir(), 'exact completed late root')
        paths.update(path.relative_to(ROOT).as_posix() for path in directory.rglob('*') if path.is_file())
    records = []
    for name in sorted(paths):
        size, identity, blob = hashes(ROOT / name)
        records.append(dict(path=name, bytes=size, sha256=identity, raw_git_blob=blob))
    for start in range(0, len(records), 50):
        subprocess.run(['git', 'add', '-f', '--', *[row['path'] for row in records[start:start+50]]], cwd=ROOT, check=True, capture_output=True)
    index = {}
    for entry in subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=ROOT).split(b'\0'):
        if entry:
            header, name = entry.split(b'\t', 1)
            mode, blob, stage = header.decode('ascii').split()
            if stage == '0':
                index[name.decode('utf8')] = blob
    require(all(index.get(row['path']) == row['raw_git_blob'] for row in records), 'late extras exact raw Git objects')
    source_names = sorted({row['path'] for row in manifest['records'] if row['path'].endswith('.py')} | {name for name in paths if name.endswith('.py')})
    source_records = []
    for name in source_names:
        require(not deadline.status()['stop_required'], 'not completed within the allocated budget')
        raw = subprocess.check_output(['git', 'cat-file', 'blob', index[name]], cwd=ROOT)
        ast.parse(raw, filename=name)
        source_records.append(dict(path=name, sha256=hashlib.sha256(raw).hexdigest(), index_blob=index[name]))
    out = args.out.resolve(); require(out.is_relative_to(ROOT), 'bounded report'); out.mkdir(parents=True, exist_ok=False)
    report = dict(status='WAVE36_LATE_METADATA_AND_INDEXED_PYTHON_AST_PASS', timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), source_sha256=hashes(Path(__file__))[1], command=[sys.executable, *sys.argv], cwd=str(ROOT), allowlist_manifest_sha256=ALLOW_SHA, ledger_sha256=manifest['ledger_sha256'], records=records, late_metadata_records=len(records), indexed_python_sources=len(source_records), syntax_records=source_records, mathematical_verification=False, availability_changed=False, deadline=deadline.status())
    (out / 'summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(status=report['status'], late_metadata_records=len(records), indexed_python_sources=len(source_records))))


if __name__ == '__main__':
    main()
