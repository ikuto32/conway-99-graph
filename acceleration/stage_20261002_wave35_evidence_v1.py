"""Authenticate and stage only frozen wave35 evidence and completed receipts."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from command_deadline import CommandDeadline
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
BASE = 'acceleration/results/20261002_wave35_registration01/CLAIMS.before.yaml'
PACKAGES = [
    ('acceleration/results/20261002_wave33_model_package01/manifest.json', 'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145'),
    ('acceleration/results/20261002_wave33_reconstruction_package01/manifest.json', 'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989'),
]
CHECKPOINTS = {
    'acceleration/results/20261002_rooted8_gf3_solve01/solve/checkpoint.bin': ('c2c13e6e83079264344f9610ba31ebe254544b501d9b95e9cafea9ff2d66b0b8', 494930751),
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger-sha256', required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--extra', action='append', default=[])
    args = parser.parse_args()
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'bounded stage metadata')
    out.mkdir(parents=True, exist_ok=False)
    deadline = CommandDeadline(args.seconds, allocation_reason='Frozen334 ledger evidence identity/staging only; large public models and hash-only resume checkpoints omitted')

    def sha(name):
        need(not deadline.status()['stop_required'], 'staging deadline')
        path = (ROOT / name).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'bounded existing input ' + name)
        with path.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()

    need(sha('CLAIMS.yaml') == args.ledger_sha256, 'frozen ledger')
    data, before = registry.read_ledger(ROOT / 'CLAIMS.yaml'), registry.read_ledger(ROOT / BASE)
    need(len(data['claims']) == 334 and len(before['claims']) == 329, 'exact wave populations')
    prior_ids = {a['id'] for a in before['artifacts']}
    pins = {}
    for artifact in data['artifacts']:
        if artifact['id'] not in prior_ids and artifact['path']:
            name = artifact['path']
            need(name not in pins or pins[name] == artifact['sha256'], 'consistent repeated artifact identity')
            pins[name] = artifact['sha256']
    raw = {}
    for name, wanted in PACKAGES:
        need(sha(name) == wanted, 'pinned public model package')
        for row in json.loads((ROOT / name).read_bytes())['records']:
            raw[row['raw_path']] = dict(sha256=row['raw_sha256'], bytes=row['raw_bytes'], retrieval_manifest=name, retrieval_manifest_sha256=wanted)
    paths = set(pins) | {'CLAIMS.yaml', Path(__file__).resolve().relative_to(ROOT).as_posix()}
    for pattern in ['*20261002*wave35*', '*20261002*wave34*publication*', 'audit_20261002_wave34_availability*', 'design_20261002_hypergraph_weight60_v2.md']:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'acceleration').glob(pattern) if p.is_file())
    for pattern in ['*20261002*THIRTYFIFTH*', '*20261002*WAVE34_PUBLICATION*']:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'docs').glob(pattern) if p.is_file())
    result_patterns = ['20261002_wave35_registration*', '20261002_wave35_milestone*', '20261002_wave34_public_confirmation*', '20261002_rooted8_gf3_launch*', '20261002_rooted8_gf3_live_observation*', '20261002_rooted8_gf3_solve*', '20261002_rooted6_unrestricted_domain*', '20261002_rooted6_unrestricted_edge_domain*']
    for pattern in result_patterns:
        for folder in (ROOT / 'acceleration/results').glob(pattern):
            if folder.is_dir():
                paths.update(p.relative_to(ROOT).as_posix() for p in folder.rglob('*') if p.is_file())
    for pattern in ['gf3_full_artifact*', 'rooted6_unrestricted_domain*', 'rooted6_unrestricted_edge_domain*', 'lambda_phase_structure*', 'wave34_availability*']:
        for folder in (ROOT / 'acceleration/results/20261002_independent_review').glob(pattern):
            if folder.is_dir():
                paths.update(p.relative_to(ROOT).as_posix() for p in folder.rglob('*') if p.is_file())
    for name in args.extra:
        path = (ROOT / name).resolve()
        need(path.is_relative_to(ROOT), 'bounded explicit extra')
        paths.update(p.relative_to(ROOT).as_posix() for p in path.rglob('*') if p.is_file()) if path.is_dir() else paths.add(path.relative_to(ROOT).as_posix())
    records, omitted = [], []
    for name in sorted(paths):
        need(name.startswith(('acceleration/', 'docs/')) or name in {'CLAIMS.yaml', 'README.md', 'ACTIVE_RESEARCH.md', 'pyproject.toml', 'uv.lock'}, 'research namespace ' + name)
        identity = sha(name)
        need(name not in pins or identity == pins[name], 'exact registered evidence ' + name)
        size = (ROOT / name).stat().st_size
        if name in raw:
            need(identity == raw[name]['sha256'] and size == raw[name]['bytes'], 'exact lossless model identity')
            omitted.append(dict(path=name, **raw[name], reason='Previously published model package; do not duplicate raw Git blob.'))
        elif name in CHECKPOINTS:
            need((identity, size) == CHECKPOINTS[name], 'exact hash-only native resume state')
            omitted.append(dict(path=name, sha256=identity, bytes=size, availability='LOCAL_ONLY', reason='Native resume state hash only; three public primal vectors and raw operator form the mathematical certificate.'))
        else:
            need(size < 50 * 1024 ** 2, 'bounded direct artifact ' + name)
            records.append(dict(path=name, sha256=identity, bytes=size))
    names = [r['path'] for r in records]
    for start in range(0, len(names), 75):
        subprocess.run(['git', 'add', '-f', '--', *names[start:start+75]], cwd=ROOT, check=True, capture_output=True)
    report = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), source_sha256=sha(Path(__file__).resolve().relative_to(ROOT).as_posix()), command=[sys.executable, *sys.argv], cwd=str(ROOT), ledger_sha256=args.ledger_sha256, records=records, omitted=omitted, mathematical_promotion=False, availability_changed=False, scientific_launched=False)
    (out / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    subprocess.run(['git', 'add', '-f', '--', (out / 'manifest.json').relative_to(ROOT).as_posix()], cwd=ROOT, check=True, capture_output=True)
    print(json.dumps(dict(status='FROZEN_WAVE35_EVIDENCE_STAGED', distinct_paths=len(records), direct_bytes=sum(r['bytes'] for r in records), omitted=len(omitted))))


if __name__ == '__main__':
    main()
