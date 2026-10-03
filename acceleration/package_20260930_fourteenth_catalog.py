"""Explicit fourteenth publication closure and recovery; no ledger/index mutation."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import platform
import subprocess
import sys
import yaml
import package_20260930_eighth_catalog as common
import recover_20260930_fourteenth_inputs as recovery

ROOT = common.ROOT
B = 'acceleration/results/20260930_'
I = B+'independent_review/'
DIRS = [B+p for p in [
    'factor_permutation_annealer_calibration', 'factor_permutation_annealer_calibration_v2',
    'factor_annealer_pilot', 'factor_annealer_cooling', 'factor_annealer_resume_diagnosis',
    'factor_permutation_resume_calibration_v3', 'factor_annealer_cooling_v3', 'factor_gpu_binding_failures',
    'variable_core_pair_orbits', 'variable_core_pair_orbits_object_calibration',
    'variable_core_pair_orbits_native_preflight', 'variable_core_pair_orbits_native_pilot',
    'triangle_modular_kernel', 'triangle_modular_kernel_controls',
    'prism_column_caps', 'prism_column_caps_v2', 'prism_column_caps_v3', 'prism_column_caps_native_preflight',
    'fourteenth_gpu_registration', 'fourteenth_pair_modular_registration', 'fourteenth_factor_results_registration',
    'fourteenth_gpu_trace_packages', 'fourteenth_packaging_preparation/attempt01',
]]+[I+p for p in [
    'factor_annealing_objective_calibration', 'factor_permutation_annealer', 'factor_permutation_annealer_bound',
    'factor_annealer_pilot', 'factor_annealer_pilot_availability_correction', 'factor_resume_v3',
    'factor_annealer_cooling_v3', 'factor_gpu_claim_bindings', 'variable_core_pair_orbits',
    'variable_core_pair_orbits_v2', 'variable_core_pair_object_wrapper', 'variable_core_pair_orbits_unknown',
    'triangle_modular_kernel_finite', 'pair_and_modular_claim_bindings', 'prism_column_caps',
    'prism_column_caps_object_calibration',
]]
FILES = ['acceleration/'+p for p in [
    'theory_20260930_factor_permutation_annealer.py', 'theory_20260930_factor_permutation_annealer_spec.md',
    'factor_permutation_anneal_20260930.cu', 'build_factor_permutation_anneal_20260930.ps1',
    'theory_20260930_factor_permutation_annealer_v2.py', 'theory_20260930_factor_permutation_annealer_v2_spec.md',
    'factor_permutation_anneal_20260930_v2.cu', 'build_factor_permutation_anneal_20260930_v2.ps1',
    'theory_20260930_factor_permutation_annealer_v3.py', 'theory_20260930_factor_permutation_annealer_v3_spec.md',
    'theory_20260930_factor_annealer_pilot.py', 'theory_20260930_factor_annealer_pilot_spec.md',
    'theory_20260930_factor_annealer_cooling.py', 'theory_20260930_factor_annealer_cooling_spec.md',
    'theory_20260930_factor_annealer_cooling_v3.py', 'theory_20260930_factor_annealer_cooling_v3_spec.md',
    'theory_20260930_factor_annealer_resume_diagnosis.py', 'audit_20260930_factor_annealing_objective.py',
    'audit_20260930_factor_permutation_annealer.py', 'audit_20260930_factor_permutation_trace.py',
    'audit_20260930_factor_annealer_pilot.py', 'audit_20260930_factor_resume_v3.py', 'audit_20260930_factor_cooling_v3.py',
    'bind_20260930_factor_permutation_annealer.py', 'bind_20260930_factor_gpu_claims.py', 'record_20260930_factor_pilot_availability.py',
    'theory_20260930_variable_core_pair_orbits.py', 'theory_20260930_variable_core_pair_orbits_spec.md',
    'audit_20260930_variable_core_pair_orbits.py', 'audit_20260930_variable_core_pair_orbits_v2.py',
    'audit_20260930_variable_core_pair_orbits_object.py', 'audit_20260930_variable_core_pair_object_wrapper.py',
    'native_20260930_variable_core_pair_orbits.py', 'native_20260930_variable_core_pair_orbits_spec.md',
    'audit_20260930_variable_core_pair_orbits_unknown.py', 'theory_20260930_triangle_modular_kernel.py',
    'theory_20260930_triangle_modular_kernel_spec.md', 'control_20260930_triangle_modular_kernel.py',
    'audit_20260930_triangle_modular_kernel_finite.py', 'audit_20260930_pair_and_modular_claim_bindings.py',
    'theory_20260930_prism_column_caps.py', 'theory_20260930_prism_column_caps_spec.md',
    'theory_20260930_prism_column_caps_v2.py', 'theory_20260930_prism_column_caps_v3.py',
    'theory_20260930_prism_column_caps_v3_spec.md', 'audit_20260930_prism_column_caps.py',
    'audit_20260930_prism_column_caps_object.py', 'native_20260930_prism_column_caps.py', 'native_20260930_prism_column_caps_spec.md',
    'register_20260930_fourteenth_gpu.py', 'register_20260930_fourteenth_pair_modular.py',
    'register_20260930_fourteenth_factor_results.py', 'package_20260930_fourteenth_gpu_traces.py',
    'recover_20260930_fourteenth_inputs.py', 'package_20260930_fourteenth_catalog.py',
]]+['docs/'+p for p in [
    'AUDIT_20260930_FACTOR_PERMUTATION_ANNEALER.md', 'AUDIT_20260930_FACTOR_RESUME_V3.md',
    'AUDIT_20260930_VARIABLE_CORE_PAIR_ORBITS.md', 'AUDIT_20260930_VARIABLE_CORE_PAIR_ORBITS_V2_ADDENDUM.md',
    'AUDIT_20260930_VARIABLE_CORE_PAIR_OBJECT_WRAPPER.md', 'EXPLORATION_20260930_TRIANGLE_MODULAR_KERNEL.md',
    'AUDIT_20260930_TRIANGLE_MODULAR_KERNEL_FINITE.md', 'AUDIT_20260930_PRISM_COLUMN_CAPS.md',
    'AUDIT_20260930_PRISM_COLUMN_CAP_UNKNOWN.md',
    'REPRODUCING_20260930_FOURTEENTH_WAVE.md',
]]
LOCAL_FIXED = {
    B+'prism_column_caps_v3/instance.cnf':'Oversized exact raw CNF; verified public gzip recovery.',
    B+'variable_core_pair_orbits_native_pilot/main/proof.drat':'Retained incomplete UNKNOWN-run trace; not a proof certificate; no public recovery.',
}
LOCAL_TOOLS = {'build/research-cadical195/source/build/cadical', 'build/rook-drat-checker/drat-trim.exe',
    'acceleration/build/factor_permutation_anneal_20260930_v2.exe'}
PRIOR_RECOVERABLE = {B+'variable_core_factor_cnf/model.json', B+'prism_all_columns/instance.cnf',
    B+'prism_all_columns/model.json', B+'prism_all_columns/clauses.body', B+'prism_first_choice_normalization/instance.cnf'}
REGISTRATIONS = [B+p for p in ['fourteenth_gpu_registration', 'fourteenth_pair_modular_registration', 'fourteenth_factor_results_registration']]
# Exact intentionally false evidence bindings are added only after inspecting their
# frozen control files; no generic all-zero or path-substring exceptions are allowed.
FALSE_BINDINGS = {
    (I+'variable_core_pair_object_wrapper/wrong_bound_model.json', B+'variable_core_factor_cnf/model.json'):
        dict(expected='0'*64, actual='42071b881973450db0f1813356133688b7532dd7d0495d37962acc5fa8c071f2',
            origin_sha256='cd0392a1c80e1067a1856e09d5c31fb263cf913cc1362b81f53ab717c67443f8',
            audit=I+'variable_core_pair_object_wrapper/summary.json',
            audit_sha256='a888c847c8ee5942e11eed179d79796f826354cbabc515a3cc8554f7af672355',
            reason='Frozen deliberately false model-hash gate rejected by the independent pair-object-wrapper audit; not an authentic evidence binding.'),
}


def main(args):
    out = (ROOT/args.out).resolve(); assert out.is_relative_to(ROOT) and not out.exists()
    out.mkdir(parents=True)
    # A failed catalog is itself preserved, including the exact executing source.
    snapshot = Path(__file__).read_bytes()
    try: execute(args, out)
    except BaseException as error:
        (out/'failed_source.py').write_bytes(snapshot)
        common.save(out/'failure.json', dict(error=repr(error), source_sha256=hashlib.sha256(snapshot).hexdigest(),
            command=[sys.executable, *sys.argv], timestamp=datetime.now(timezone.utc).isoformat(), mathematical_verification=False))
        raise


def execute(args, out):
    ledger_bytes = (ROOT/'CLAIMS.yaml').read_bytes(); ledger = yaml.safe_load(ledger_bytes)
    tracked = set(common.git('ls-files', '-z').decode().split('\0')); index = common.git('ls-files', '--stage', '-z')
    ids = []; previous = None
    for directory, count in zip(REGISTRATIONS, [4, 2, 2], strict=True):
        p = ROOT/directory; receipt = json.loads((p/'summary.json').read_bytes())
        before, after = (p/'CLAIMS.before.yaml').read_bytes(), (p/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest() == receipt['previous_ledger_sha256']
        assert hashlib.sha256(after).hexdigest() == receipt['ledger_sha256']
        assert previous is None or previous == before, 'registration chain continuity'
        assert len(receipt['new_claim_ids']) == count
        ids.extend(receipt['new_claim_ids']); previous = after
    assert previous == ledger_bytes and len(ledger['claims']) == 138, 'frozen fourteen registration ledger'
    assert len(set(ids)) == 8
    claims = [c for c in ledger['claims'] if c['id'] in ids]
    assert len(claims) == 8 and all(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in claims)
    dirs = list(DIRS); files = list(FILES); local = dict(LOCAL_FIXED)
    for name, pin in recovery.MANIFESTS.items(): assert common.digest(ROOT/name) == pin
    package_manifest = json.loads((ROOT/(B+'fourteenth_gpu_trace_packages/artifact_packages.json')).read_bytes())
    assert len(package_manifest['packages']) == 224
    for item in package_manifest['packages']:
        local[item['raw_path']] = 'Losslessly packaged GPU raw JSON; exact public gzip recovery, original retained.'
    if not args.prepare:
        assert args.caps_audit and args.caps_audit_sha256 and args.caps_audit_source, 'completed cap outcome audit/source required'
        audit_path = (ROOT/args.caps_audit).resolve(); assert common.digest(audit_path) == args.caps_audit_sha256
        audit = json.loads(audit_path.read_bytes())
        assert audit['status'] == args.caps_audit_status and 'UNKNOWN' in audit['status'] and 'PASS' in audit['status'], 'explicit separately checked cap UNKNOWN outcome'
        for required in [B+'prism_column_caps_v3/instance.cnf', B+'prism_column_caps_native_pilot/summary.json',
                B+'prism_column_caps_native_pilot/main/solver.stdout.log', B+'prism_column_caps_native_pilot/main/proof.drat', args.caps_audit_source]:
            assert audit['inputs_sha256'][required] == common.digest(ROOT/required), 'specific completed cap input/outcome identity'
        dirs += [B+'prism_column_caps_native_pilot', common.relative(audit_path.parent)]
        files += [args.caps_audit_source]
        local[B+'prism_column_caps_native_pilot/main/proof.drat'] = 'Retained incomplete UNKNOWN-run trace; no proof certificate or public recovery.'
    selected = set(files)
    for directory in dirs:
        assert (ROOT/directory).is_dir(), directory
        selected.update(common.relative(p) for p in (ROOT/directory).rglob('*') if p.is_file())
    assert set(local) <= selected
    cache = {}; refs = []; corrupt = []; recovered = []; errors = []
    def info(path):
        if path not in cache:
            p = ROOT/path; assert p.is_file() and p.resolve().is_relative_to(ROOT), path
            cache[path] = dict(path=path, sha256=common.digest(p), bytes=p.stat().st_size)
        return cache[path]
    def check(name, expected, origin, archive=False):
        path = common.resolve_ref(name, ROOT/origin, archive)
        if path is None:
            errors.append(dict(kind='unresolved', origin=origin, name=name, expected=expected)); return
        item = info(path)
        if item['sha256'] != expected:
            binding = FALSE_BINDINGS.get((origin, path))
            if binding is not None:
                assert binding['expected'] == expected and binding['actual'] == item['sha256']
                assert common.digest(ROOT/origin) == binding['origin_sha256']
                assert common.digest(ROOT/binding['audit']) == binding['audit_sha256']
                assert 'wrong_bound_model' in json.loads((ROOT/binding['audit']).read_bytes())['black_box_wrapper_controls']['fresh_corruptions_rejected']
                corrupt.append(dict(origin=origin, **item, deliberately_false_sha256=expected, reason=binding['reason'])); return
            errors.append(dict(kind='hash_mismatch', origin=origin, **item, expected=expected)); return
        if not (path in selected or path in tracked or path.startswith('external_conway99_research/') or path in LOCAL_TOOLS or path in PRIOR_RECOVERABLE):
            errors.append(dict(kind='missing_explicit_dependency', origin=origin, **item))
        refs.append(dict(origin=origin, **item))
    def package(obj, origin):
        if not all(k in obj for k in ('raw_path', 'raw_sha256', 'raw_bytes')): return
        if 'ordered_parts' in obj:
            parts = []
            for p in obj['ordered_parts']:
                check(p['path'], p['sha256'], origin); raw = (ROOT/p['path']).read_bytes(); assert len(raw) == p['bytes']; parts.append(raw)
            compressed = b''.join(parts); assert hashlib.sha256(compressed).hexdigest() == obj['compressed_stream_sha256']
        elif 'gzip_path' in obj:
            check(obj['gzip_path'], obj['gzip_sha256'], origin); compressed = (ROOT/obj['gzip_path']).read_bytes()
            assert len(compressed) == obj['gzip_bytes']
        else: return
        raw = gzip.decompress(compressed); assert len(raw) == obj['raw_bytes'] and hashlib.sha256(raw).hexdigest() == obj['raw_sha256']
        check(obj['raw_path'], obj['raw_sha256'], origin)
        recovered.append(dict(origin=origin, path=obj['raw_path'], bytes=len(raw), sha256=obj['raw_sha256']))
    def walk(obj, origin):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in common.MAP_KEYS|{'outputs_sha256'} and isinstance(v, dict):
                    for name, h in v.items():
                        if isinstance(h, str) and common.HEX.fullmatch(h): check(name, h, origin)
                walk(v, origin)
            if isinstance(obj.get('path'), str) and isinstance(obj.get('sha256'), str) and common.HEX.fullmatch(obj['sha256']):
                check(obj['path'], obj['sha256'], origin, 'conway-99-research' in obj.get('repository', ''))
            package(obj, origin)
        elif isinstance(obj, list):
            for v in obj: walk(v, origin)
    for p in sorted(selected):
        info(p)
        if p.endswith('.json'): walk(json.loads((ROOT/p).read_bytes()), p)
    artifacts = {a['id']:a for a in ledger['artifacts']}
    for claim in claims:
        for aid in claim['evidence']:
            a = artifacts[aid]; assert a['path'] in selected; check(a['path'], a['sha256'], 'CLAIMS.yaml')
    common.save(out/'reference_diagnostics.json', dict(errors=errors, count=len(errors)))
    assert not errors, f'{len(errors)} explicit closure errors; see reference_diagnostics.json'
    public = sorted(selected-set(local)); assert all(info(p)['bytes'] <= 10*1024**2 for p in public), 'oversize public artifact'
    ignored = subprocess.run(['git', 'check-ignore', '--stdin'], cwd=ROOT, input='\n'.join(public)+'\n', text=True, capture_output=True)
    assert ignored.returncode in (0, 1); ignored_paths = ignored.stdout.splitlines(); assert set(ignored_paths) <= set(public)
    common.save(out/'catalog.json', dict(entries=[dict(info(p), availability='LOCAL_ONLY' if p in local else 'READY_FOR_PUBLICATION', limitation=local.get(p)) for p in sorted(selected)],
        directories=dirs, files=files, local_tools=[dict(info(p), availability='LOCAL_ONLY', limitation='Authenticated saved executable; source/build provenance does not guarantee byte-identical rebuild on another toolchain.') for p in sorted(LOCAL_TOOLS)], prior_public_gzip_recoverable_dependencies=sorted(PRIOR_RECOVERABLE),
        selection_rule='Exact directory/file allowlists; exact224raw JSON exclusions from authenticated manifest plus named raw CNF and incomplete proof traces.',
        excluded_cohorts=['GF2 maximum-rank lemma', 'connected-core portfolio and v4 annealer', 'unregistered older identity-scope/proof-core/preflight work'],
        cap_outcome_pending=args.prepare, mathematical_reverification_performed=False,
        local_retrieval='Raw JSON and formula recover from exact public gzip; incomplete traces and native executables require local saved paths/rebuild and are not mathematical certificates.'))
    common.save(out/'reference_checks.json', dict(status='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS', records=refs, binding_count=len(refs),
        unique_paths=len({r['path'] for r in refs}), gzip_recoveries=recovered, deliberately_corrupted_control_bindings=corrupt))
    common.save(out/'scope.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=common.git('rev-parse', 'HEAD').decode().strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),
        claim_ids=ids, claim_population=len(ledger['claims']), verified_clear=sum(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in ledger['claims']),
        registration_chain_checked=True, target_resolution='UNKNOWN', preparation_only=args.prepare, cap_outcome_included=not args.prepare,
        local_only=[info(p) for p in sorted(local)]))
    common.save(out/'ignored_payload_paths.json', dict(paths=ignored_paths, raw_log_paths=[p for p in ignored_paths if p.endswith('.log')], meaning='Only these explicitly selected payload paths may be force-staged.'))
    common.save(out/'proposed_raw_ignore_paths.json', dict(paths=sorted(local), reason='Proposal only; no .gitignore edit performed.'))
    payload = sorted(set(public)|{common.relative(p) for p in out.iterdir() if p.is_file()})
    if not args.prepare:
        common.save(out/'stage_inventory.json', dict(paths=payload, entries=[info(p) for p in payload], wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'), common.relative(out/'summary.json')]))
    for p, item in cache.items(): assert common.digest(ROOT/p) == item['sha256'], ('concurrent edit', p)
    assert (ROOT/'CLAIMS.yaml').read_bytes() == ledger_bytes and common.git('ls-files', '--stage', '-z') == index
    status = 'FOURTEENTH_PROVISIONAL_CLOSURE_PASS_CAP_OUTCOME_PENDING' if args.prepare else 'FOURTEENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS'
    common.save(out/'summary.json', dict(status=status, timestamp=datetime.now(timezone.utc).isoformat(), claim_ids=ids,
        selected_files=len(selected), public_research_files=len(public), public_research_bytes=sum(info(p)['bytes'] for p in public),
        local_only_research_artifacts=len(local), public_recoverable_raw_GPU_JSON_files=224, incomplete_traces=1 if args.prepare else 2,
        reference_bindings=len(refs), unique_referenced_files=len({r['path'] for r in refs}), gzip_recoveries=len(recovered),
        cap_outcome_pending=args.prepare, output_hashes={common.relative(p):common.digest(p) for p in out.iterdir() if p.is_file()}))
    print(json.dumps(dict(status=status, public_files=len(public), local_only=len(local))))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--prepare', action='store_true')
    ap.add_argument('--caps-audit'); ap.add_argument('--caps-audit-sha256'); ap.add_argument('--caps-audit-status'); ap.add_argument('--caps-audit-source')
    main(ap.parse_args())
