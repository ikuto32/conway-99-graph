"""Stage only hash-bound new wave34 evidence and its finite continuation records.

Large already-packaged models and the noncertificate native resume checkpoint
remain separate; no scientific statement or availability is promoted here.
"""
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
import validate_claims as registry
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
BASE = 'acceleration/results/20261002_wave34_registration01/CLAIMS.before.yaml'
PACKAGES = [
    ('acceleration/results/20261002_wave33_model_package01/manifest.json', 'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145'),
    ('acceleration/results/20261002_wave33_reconstruction_package01/manifest.json', 'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989'),
]
CHECKPOINT = 'acceleration/results/20261002_rooted8_normalized_gf2_solve01/solve/checkpoint.bin'
CHECKPOINT_SHA = '3ecd66eb252cdd8cd92b1293fae8edfdd1a03d218fc9ab15684a81738370c227'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ledger-sha256', required=True)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--extra', action='append', default=[])
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    deadline = CommandDeadline(args.seconds, allocation_reason='Hash/stage only frozen new-wave evidence and completed contained run records')
    def sha(name):
        need(not deadline.status()['stop_required'], 'staging deadline')
        path = (ROOT / name).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'bounded existing file ' + name)
        with path.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
    need(sha('CLAIMS.yaml') == args.ledger_sha256, 'frozen current ledger')
    data, before = registry.read_ledger(ROOT / 'CLAIMS.yaml'), registry.read_ledger(ROOT / BASE)
    prior = {a['id'] for a in before['artifacts']}
    pins = {a['path']: a['sha256'] for a in data['artifacts'] if a['id'] not in prior and a['path']}
    raw = {}
    for name, identity in PACKAGES:
        need(sha(name) == identity, 'frozen previously published model package')
        for row in json.loads((ROOT / name).read_bytes())['records']:
            raw[row['raw_path']] = dict(sha256=row['raw_sha256'], bytes=row['raw_bytes'], retrieval_manifest=name, retrieval_manifest_sha256=identity)
    paths = set(pins) | {'CLAIMS.yaml', Path(__file__).resolve().relative_to(ROOT).as_posix()}
    patterns = ['confirm_20261002_wave33_publication_v1*', 'freeze_20261002_hypergraph_weighted_pilot_plan_v1*', 'plan_20261002_hypergraph_weighted_pilot_v1*', 'record_20261002_hypergraph_weighted_pilot_binding_v1*', 'theory_20261002_prism_global_parameter_means*', 'theory_20261002_per_vertex_rooted6_means*', 'theory_20261002_almost_prism_global_mean*', 'audit_20261002_normalized_gf2_full_artifact_v1*', '*20261002*wave33*publication*', '*20261002*wave33*availability*', '*20261002*wave34*']
    for pattern in patterns:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'acceleration').glob(pattern) if p.is_file())
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'docs').glob('*20261002*') if p.is_file() and any(s in p.name for s in ['WAVE34', 'WEIGHTED_PILOT_SETUP', 'WAVE33_PUBLICATION_SETUP', 'NORMALIZED_GF2_FULL']))
    folders = ['20261002_wave33_public_confirmation*', '20261002_prism_global_parameter_means*', '20261002_per_vertex_rooted6_means*', '20261002_almost_prism_global_mean*', '20261002_wave34_registration*', '20261002_wave34_milestone*', '20261002_hypergraph_weighted_pilot*', '20261002_rooted8_normalized_launch*', '20261002_rooted8_normalized_process_diagnosis*', '20261002_rooted8_normalized_live_observation*', '20261002_rooted8_normalized_gf2_solve*']
    for pattern in folders:
        for folder in (ROOT / 'acceleration/results').glob(pattern):
            if folder.is_dir():
                paths.update(p.relative_to(ROOT).as_posix() for p in folder.rglob('*') if p.is_file())
    for pattern in ['hypergraph_weighted_pilot*', 'normalized_full_checker_calibration*', 'normalized_gf2_full_artifact*', 'wave33_public*', 'wave33_availability*', 'wave34_transition*', 'rooted6_means*']:
        for folder in (ROOT / 'acceleration/results/20261002_independent_review').glob(pattern):
            if folder.is_dir():
                paths.update(p.relative_to(ROOT).as_posix() for p in folder.rglob('*') if p.is_file())
    for name in args.extra:
        path = (ROOT / name).resolve()
        need(path.is_relative_to(ROOT), 'bounded explicit extra')
        if path.is_dir():
            paths.update(p.relative_to(ROOT).as_posix() for p in path.rglob('*') if p.is_file())
        else:
            paths.add(path.relative_to(ROOT).as_posix())
    records, omitted = [], []
    for name in sorted(paths):
        need(name.startswith(('acceleration/', 'docs/')) or name in {'CLAIMS.yaml', 'uv.lock', 'pyproject.toml', 'README.md', 'ACTIVE_RESEARCH.md'}, 'research namespace ' + name)
        identity = sha(name)
        need(name not in pins or pins[name] == identity, 'exact registered evidence ' + name)
        size = (ROOT / name).stat().st_size
        if name in raw:
            need(identity == raw[name]['sha256'] and size == raw[name]['bytes'], 'exact public compressed model input')
            omitted.append(dict(path=name, **raw[name], reason='Previously published lossless package; do not duplicate raw Git blob.'))
            continue
        if name == CHECKPOINT:
            need(identity == CHECKPOINT_SHA and size == 343414964, 'exact noncertificate resume checkpoint')
            omitted.append(dict(path=name, sha256=identity, bytes=size, availability='LOCAL_ONLY', reason='Native producer resume state, hashed only; three full primal vectors and literal input constitute the modular certificate. No replay of the native trajectory or rank claim.'))
            continue
        need(size < 50 * 1024 ** 2, 'bounded direct artifact ' + name)
        records.append(dict(path=name, sha256=identity, bytes=size))
    names = [r['path'] for r in records]
    for start in range(0, len(names), 75):
        subprocess.run(['git', 'add', '-f', '--', *names[start:start + 75]], cwd=ROOT, check=True, capture_output=True)
    report = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=[sys.executable, *sys.argv], cwd=str(ROOT), source_sha256=sha(Path(__file__).resolve().relative_to(ROOT).as_posix()), ledger_sha256=args.ledger_sha256, records=records, omitted=omitted, mathematical_promotion=False, availability_changed=False)
    (out / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    subprocess.run(['git', 'add', '-f', '--', (out / 'manifest.json').relative_to(ROOT).as_posix()], cwd=ROOT, check=True, capture_output=True)
    print(json.dumps(dict(status='FROZEN_WAVE34_EVIDENCE_STAGED', distinct_paths=len(records), direct_bytes=sum(r['bytes'] for r in records), omitted=len(omitted))))


if __name__ == '__main__':
    main()
