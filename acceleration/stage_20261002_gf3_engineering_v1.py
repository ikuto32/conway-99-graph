"""Stage exact independently gated original-GF3 engineering inputs only."""
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
ALLOW = 'acceleration/results/20261002_rooted8_gf3_allowlist01/manifest.json'
ALLOW_SHA = '1c29f461f8671732c947b3751e930d32b443344145e671ec662cd989d04763dd'
GATE = 'acceleration/results/20261002_independent_review/gf3_native_controls01/summary.json'
GATE_SHA = 'e4622abb19498f53591b6fe26d57a9e40b673d4c91231775274c1f2393af4ce8'
ENDPOINT = 'acceleration/results/20261002_independent_review/gf3_endpoint_calibration01/summary.json'
ENDPOINT_SHA = 'da9ee10677ef26cd0dd5c6a1272c98f12d05b6d52a7f2f676d85d85f58ea215b'
RAW = 'acceleration/results/20261002_rooted8_universal5_product_model02/model.json'
RAW_SHA = 'a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    deadline = CommandDeadline(args.seconds, allocation_reason='Authenticate fixed386-member engineering allowlist and separate scalar/native/endpoint gates before committing source')
    def sha(name):
        need(not deadline.status()['stop_required'], 'staging deadline')
        path = (ROOT / name).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'bounded existing artifact ' + name)
        with path.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
    pins = {}
    for name, wanted, status in [(ALLOW, ALLOW_SHA, None), (GATE, GATE_SHA, 'INDEPENDENT_ORIGINAL_GF3_PRIMAL_RELATION_CONTROLS_V1_PASS'), (ENDPOINT, ENDPOINT_SHA, 'INDEPENDENT_GF3_LITERAL_ENDPOINT_CHECKER_CALIBRATION_V1_PASS')]:
        need(sha(name) == wanted, 'exact allowlist/checking report')
        report = json.loads((ROOT / name).read_bytes())
        need(status is None or report['status'] == status, 'separate gate scope')
        closure = {r['path']:r['sha256'] for r in report['records']} if status is None else report['inputs_sha256']
        for path, identity in {name:wanted, **closure}.items():
            need(path not in pins or pins[path] == identity, 'consistent complete gate closure')
            pins[path] = identity
    allow = json.loads((ROOT / ALLOW).read_bytes())
    need(allow['hashed_records'] == len(allow['records']) == 386 and allow['stage_paths_count'] == 388, 'frozen native engineering population')
    paths = set(pins) | set(allow['self_metadata_paths']) | {Path(__file__).resolve().relative_to(ROOT).as_posix(), 'acceleration/plan_20261002_rooted8_gf3_timestamp_correction_v1.json'}
    roots = ['acceleration/results/20261002_rooted8_gf3_allowlist_supervision01']
    for pattern in ['gf3_scalar_calibration*', 'gf3_native_controls*', 'gf3_endpoint_calibration*']:
        roots.extend(p.relative_to(ROOT).as_posix() for p in (ROOT / 'acceleration/results/20261002_independent_review').glob(pattern) if p.is_dir())
    for name in roots:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / name).rglob('*') if p.is_file())
    records, omitted = [], []
    for name in sorted(paths):
        need(name.startswith(('acceleration/', 'docs/')) or name in {'uv.lock','pyproject.toml'}, 'exact research namespace')
        identity = sha(name)
        need(name not in pins or pins[name] == identity, 'exact source/gate input ' + name)
        size = (ROOT / name).stat().st_size
        if name == RAW:
            need(identity == RAW_SHA and size == 57414699, 'sole previously packaged raw model')
            omitted.append(dict(path=name, sha256=identity, bytes=size, retrieval_manifest='acceleration/results/20261002_wave33_model_package01/manifest.json', retrieval_manifest_sha256='c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145'))
            continue
        need(size < 50 * 1024 ** 2, 'bounded direct engineering artifact')
        records.append(dict(path=name, sha256=identity, bytes=size))
    names = [r['path'] for r in records]
    for start in range(0, len(names), 75):
        subprocess.run(['git','add','-f','--',*names[start:start+75]], cwd=ROOT, check=True, capture_output=True)
    report = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(), command=[sys.executable,*sys.argv], cwd=str(ROOT), source_sha256=sha(Path(__file__).resolve().relative_to(ROOT).as_posix()), records=records, omitted=omitted, scientific_launched=False, ledger_changed=False, mathematical_promotion=False, endpoint_and_finite_gates_separate=True)
    (out / 'manifest.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf8', newline='\n')
    subprocess.run(['git','add','-f','--',(out / 'manifest.json').relative_to(ROOT).as_posix()], cwd=ROOT, check=True, capture_output=True)
    print(json.dumps(dict(status='EXACT_GATED_GF3_ENGINEERING_STAGED', direct_paths=len(records), direct_bytes=sum(r['bytes'] for r in records), omitted_models=len(omitted))))


if __name__ == '__main__':
    main()
