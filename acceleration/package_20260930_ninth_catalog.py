"""Inventory an explicit ninth-wave allowlist, retaining incomplete traces locally."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import yaml
import package_20260930_eighth_catalog as common

ROOT = common.ROOT
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
DIRS = [
    B+'triangle_q1_binary_scout', I+'triangle_q1_binary_scout',
    B+'triangle_joint_factor_cnf', I+'triangle_joint_factor_cnf',
    I+'triangle_joint_factor_object_calibration', I+'triangle_joint_factor_object_calibration_v2',
    B+'triangle_factor_components', I+'triangle_factor_components',
    I+'triangle_component_factor_object_calibration',
    I+'triangle_joint_factor_unknown',
    B+'triangle_joint_factor_native_preflight', B+'triangle_joint_factor_native_pilot',
    B+'triangle_component_factor_native_preflight', B+'triangle_component_factor_native_pilot',
    B+'ninth_registration',
]
FILES = ['acceleration/'+p for p in [
    'theory_20260930_triangle_q1_binary_scout.py', 'theory_20260930_triangle_q1_binary_scout_spec.md',
    'theory_20260930_triangle_q1_row_controls.py', 'audit_20260930_triangle_q1_binary_scout.py',
    'theory_20260930_triangle_joint_factor_cnf.py', 'theory_20260930_triangle_joint_factor_cnf_spec.md',
    'audit_20260930_triangle_joint_factor_cnf.py', 'audit_20260930_triangle_joint_factor_object.py',
    'audit_20260930_triangle_joint_factor_object_v2.py',
    'audit_20260930_triangle_joint_factor_unknown.py',
    'native_20260930_triangle_joint_factor.py', 'native_20260930_triangle_joint_factor_spec.md',
    'theory_20260930_triangle_factor_components.py', 'theory_20260930_triangle_factor_components_spec.md',
    'audit_20260930_triangle_factor_components.py', 'audit_20260930_triangle_component_factor_object.py',
    'native_20260930_triangle_component_factor.py', 'native_20260930_triangle_component_factor_spec.md',
    'register_20260930_ninth_milestone.py', 'package_20260930_ninth_catalog.py',
]] + ['docs/'+p for p in [
    'AUDIT_20260930_TRIANGLE_Q1_BINARY_SCOUT.md',
    'AUDIT_20260930_TRIANGLE_JOINT_FACTOR_ENCODING.md',
    'AUDIT_20260930_TRIANGLE_FACTOR_COMPONENTS.md',
    'REPRODUCING_20260930_NINTH_WAVE.md',
]]
LOCAL = {B+p+'/main/proof.drat' for p in [
    'triangle_joint_factor_native_pilot', 'triangle_component_factor_native_pilot']}
LOCAL_BINARIES = {
    'build/research-cadical195/source/build/cadical',
    'build/rook-drat-checker/drat-trim.exe',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--additional-audit-directory', required=True)
    ap.add_argument('--additional-audit-source', required=True)
    args = ap.parse_args()
    out = ROOT / args.out
    assert not out.exists()
    directories = DIRS + [args.additional_audit_directory]
    files = FILES + [args.additional_audit_source]
    selected = set(files)
    for directory in directories:
        assert (ROOT/directory).is_dir(), directory
        selected.update(common.relative(p) for p in (ROOT/directory).rglob('*') if p.is_file())
    assert LOCAL <= selected
    ledger_bytes = (ROOT/'CLAIMS.yaml').read_bytes()
    data = yaml.safe_load(ledger_bytes)
    registration = json.loads((ROOT/(B+'ninth_registration/summary.json')).read_bytes())
    assert hashlib.sha256(ledger_bytes).hexdigest() == registration['ledger_sha256']
    ids = registration['new_claim_ids']
    claims = [c for c in data['claims'] if c['id'] in ids]
    assert len(claims) == 7 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in claims)
    tracked = set(common.git('ls-files', '-z').decode().split('\0'))
    index_before = common.git('ls-files', '--stage', '-z')
    cache = {}

    def info(path):
        if path not in cache:
            p = ROOT/path
            assert p.is_file() and p.resolve().is_relative_to(ROOT), path
            cache[path] = dict(path=path, sha256=common.digest(p), bytes=p.stat().st_size)
        return cache[path]

    refs = []
    def check(name, expected, origin, archive=False):
        path = common.resolve_ref(name, ROOT/origin, archive)
        assert path, (origin, name)
        item = info(path)
        assert item['sha256'] == expected, (origin, path)
        assert path in selected or path in tracked or path.startswith('external_conway99_research/') or path in LOCAL_BINARIES, ('missing explicit dependency', path)
        refs.append(dict(origin=origin, **item))

    def walk(obj, origin):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in common.MAP_KEYS | {'outputs_sha256'} and isinstance(value, dict):
                    for name, expected in value.items():
                        if isinstance(expected, str) and common.HEX.fullmatch(expected):
                            check(name, expected, origin)
                walk(value, origin)
            if isinstance(obj.get('path'), str) and isinstance(obj.get('sha256'), str) and common.HEX.fullmatch(obj['sha256']):
                check(obj['path'], obj['sha256'], origin, 'conway-99-research' in obj.get('repository', ''))
        elif isinstance(obj, list):
            for value in obj:
                walk(value, origin)

    for path in sorted(selected):
        info(path)
        if path.endswith('.json'):
            walk(json.loads((ROOT/path).read_bytes()), path)
    artifacts = {a['id']:a for a in data['artifacts']}
    for claim in claims:
        for aid in claim['evidence']:
            a = artifacts[aid]
            assert a['path'] in selected
            check(a['path'], a['sha256'], 'CLAIMS.yaml')
    public = sorted(selected - LOCAL)
    assert all(info(p)['bytes'] <= 10*1024**2 for p in public), 'unexpected large artifact'
    out.mkdir(parents=True, exist_ok=False)
    common.save(out/'catalog.json', dict(
        entries=[dict(info(p), availability='LOCAL_ONLY' if p in LOCAL else 'READY_FOR_PUBLICATION',
                      limitation='Incomplete DRAT after UNKNOWN; not a refutation certificate.' if p in LOCAL else None)
                 for p in sorted(selected)],
        directories=directories, files=files, local_tool_binaries=sorted(LOCAL_BINARIES),
        selection_rule='Exact directory and source allowlists; only the two explicitly named incomplete traces excluded from publication.',
        omitted_next_wave='Q1 projection, residual-D derivation and earlier candidate proof-core extraction are outside this snapshot.',
        local_trace_retrieval='Exact workspace paths in entries; their Linux source locations and copy/hash receipts are in each native run summary. Public native replay may regenerate a different incomplete trace on another environment.',
        mathematical_reverification_performed=False))
    common.save(out/'reference_checks.json', dict(status='EXACT_REFERENCED_HASHES_PASS', records=refs,
        binding_count=len(refs), unique_paths=len({r['path'] for r in refs})))
    common.save(out/'scope.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=common.git('rev-parse','HEAD').decode().strip(), command=[sys.executable,*sys.argv],
        cwd=str(ROOT), python=platform.python_version(), ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),
        claim_ids=ids, claim_population=len(data['claims']),
        verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in data['claims']),
        target_resolution='UNKNOWN', local_only_traces=[info(p) for p in sorted(LOCAL)]))
    payload = public + [common.relative(p) for p in out.iterdir() if p.is_file()]
    common.save(out/'stage_inventory.json', dict(paths=sorted(payload), entries=[info(p) for p in sorted(payload)],
        wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'), common.relative(out/'summary.json')]))
    for p, item in cache.items():
        assert common.digest(ROOT/p) == item['sha256'], ('concurrent edit', p)
    assert (ROOT/'CLAIMS.yaml').read_bytes() == ledger_bytes
    assert common.git('ls-files','--stage','-z') == index_before
    common.save(out/'summary.json', dict(status='NINTH_EXPLICIT_PUBLICATION_INVENTORY_PASS',
        timestamp=datetime.now(timezone.utc).isoformat(), claim_ids=ids, selected_files=len(selected),
        public_payload_files=len(payload), local_only_incomplete_traces=len(LOCAL),
        reference_bindings=len(refs), unique_referenced_files=len({r['path'] for r in refs}),
        output_hashes={common.relative(p):common.digest(p) for p in sorted(out.iterdir()) if p.is_file()}))
    print(json.dumps(dict(status='NINTH_EXPLICIT_PUBLICATION_INVENTORY_PASS', payload_files=len(payload), local_incomplete_traces=len(LOCAL))))


if __name__ == '__main__':
    main()
