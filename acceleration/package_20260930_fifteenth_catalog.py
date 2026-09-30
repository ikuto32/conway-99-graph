"""Explicit fifteenth publication closure and recovery; no ledger/index mutation."""
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
import recover_20260930_fifteenth_inputs as recovery

ROOT = common.ROOT
B = 'acceleration/results/20260930_'
I = B+'independent_review/'
DIRS = [B+p for p in [
    'connected_identity_cores', 'factor_permutation_portfolio_calibration_v4',
    'connected_core_portfolio_pilot', 'connected_fixed_core_cnf',
    'connected_fixed_core_native_preflight_00', 'connected_fixed_core_native_00',
    'connected_fixed_core_native_01', 'connected_fixed_core_native_02', 'connected_fixed_core_native_03',
    'five_core_modular_gram', 'prism_coarse_complement', 'prism_coarse60_bitlift', 'prism_coarse60_native_preflight',
    'fifteenth_preparation_registration', 'fifteenth_modular_registration', 'fifteenth_coarse_registration',
    'fifteenth_bitlift_registration', 'fifteenth_gpu_trace_packages', 'fifteenth_packaging_preparation/attempt01',
]]+[I+p for p in [
    'triangle_gf2_maxrank', 'connected_identity_cores', 'factor_portfolio_v4', 'connected_core_portfolio_states',
    'connected_fixed_core_cnf', 'connected_fixed_core_claim_binding', 'connected_fixed_core_object_calibration',
    'connected_fixed_core_outcome_calibration', 'connected_fixed_core_outcome_calibration_v2',
    'connected_fixed_core_native_00', 'connected_fixed_core_native_00_v2', 'connected_fixed_core_native_01_v2',
    'connected_fixed_core_native_02_v2', 'connected_fixed_core_native_03_v2', 'five_core_modular_gram',
    'prism_coarse_complement', 'prism_coarse60_bitlift_cnf', 'prism_coarse60_bitlift_object_calibration',
    'prism_coarse60_outcome_calibration',
]]
FILES = ['acceleration/'+p for p in [
    'audit_20260930_triangle_gf2_maxrank.py',
    'theory_20260930_connected_identity_cores.py', 'theory_20260930_connected_identity_cores_spec.md',
    'audit_20260930_connected_identity_cores.py',
    'theory_20260930_factor_permutation_annealer_v4.py', 'theory_20260930_factor_permutation_annealer_v4_spec.md',
    'audit_20260930_factor_portfolio_v4.py',
    'theory_20260930_connected_core_portfolio_pilot.py', 'theory_20260930_connected_core_portfolio_pilot_spec.md',
    'audit_20260930_connected_core_portfolio_states.py',
    'theory_20260930_connected_fixed_core_cnf.py', 'theory_20260930_connected_fixed_core_cnf_spec.md',
    'audit_20260930_connected_fixed_core_cnf.py', 'bind_20260930_connected_fixed_core_claim.py',
    'audit_20260930_connected_fixed_core_object.py', 'native_20260930_connected_fixed_core.py',
    'native_20260930_connected_fixed_core_spec.md', 'audit_20260930_connected_fixed_core_native_outcome.py',
    'audit_20260930_connected_fixed_core_native_outcome_v2.py',
    'theory_20260930_five_core_modular_gram.py', 'theory_20260930_five_core_modular_gram_spec.md',
    'audit_20260930_five_core_modular_gram.py',
    'theory_20260930_prism_coarse_complement.py', 'theory_20260930_prism_coarse_complement_spec.md',
    'audit_20260930_prism_coarse_complement.py',
    'theory_20260930_prism_coarse60_bitlift.py', 'theory_20260930_prism_coarse60_bitlift_spec.md',
    'audit_20260930_prism_coarse60_bitlift_cnf.py', 'audit_20260930_prism_coarse60_bitlift_object.py',
    'audit_20260930_noncanonical_triangle_factor.py', 'theory_20260930_prism_coarse60_decode.py',
    'native_20260930_prism_coarse60.py', 'native_20260930_prism_coarse60_spec.md',
    'audit_20260930_prism_coarse60_native_outcome.py',
    'register_20260930_fifteenth_preparation.py', 'register_20260930_fifteenth_modular.py',
    'register_20260930_fifteenth_coarse.py', 'register_20260930_fifteenth_bitlift.py',
    'package_20260930_fifteenth_gpu_traces.py', 'recover_20260930_fifteenth_inputs.py',
    'package_20260930_fifteenth_catalog.py',
]]+['docs/'+p for p in [
    'AUDIT_20260930_TRIANGLE_GF2_MAXRANK.md', 'AUDIT_20260930_CONNECTED_IDENTITY_CORES.md',
    'AUDIT_20260930_FACTOR_PORTFOLIO_V4.md', 'AUDIT_20260930_CONNECTED_FIXED_CORE_CNF.md',
    'AUDIT_20260930_CONNECTED_FIXED_CORE_OBJECT.md', 'DERIVATION_20260930_FIVE_CORE_MODULAR_GRAM.md',
    'AUDIT_20260930_FIVE_CORE_MODULAR_GRAM.md', 'AUDIT_20260930_PRISM_COARSE_COMPLEMENT.md',
    'AUDIT_20260930_PRISM_COARSE60_BITLIFT.md', 'AUDIT_20260930_PRISM_COARSE60_BITLIFT_OBJECT.md',
    'REPRODUCING_20260930_FIFTEENTH_WAVE.md',
]]
LOCAL_FIXED = {B+f'connected_fixed_core_native_{i:02d}/main/proof.drat':
    'Retained incomplete UNKNOWN-run trace; not a proof certificate; no public recovery.' for i in range(4)}
LOCAL_TOOLS = {'build/research-cadical195/source/build/cadical', 'build/rook-drat-checker/drat-trim.exe',
    'acceleration/build/factor_permutation_anneal_20260930_v2.exe'}
PRIOR_PACKAGES = {
    B+'variable_core_factor_cnf/artifact_packages.json': '46867dcccbb99bd72379b50a7415e6dd1d9d888af8832289d3d054573cad3a1d',
    B+'prism_all_columns/artifact_packages.json': '112a6b94b98ef1f29f0b0691d356018f51697fd39f819b66fa52d8c2e934e55c',
    B+'prism_first_choice_normalization/artifact_packages.json': 'ce2eb961406cbd780f7ff93d81a1916484fd42f29a0ac43f17065f4988c5a9f9',
    B+'fourteenth_gpu_trace_packages/artifact_packages.json': '7ce95bd15128833fff0f4fc1526fcf43f81625fbcba2c4a36276434a6e9e438f',
}
REGISTRATIONS = [B+p for p in ['fifteenth_preparation_registration', 'fifteenth_modular_registration',
    'fifteenth_coarse_registration', 'fifteenth_bitlift_registration']]
FALSE_BINDINGS = {(I+'factor_portfolio_v4/wrong_selected_hash_corrupt_gate.json', B+'connected_identity_cores/core_00.json'): dict(
    expected='0'*64, actual='3d4ad2d5b8ff92ca3d7761ac79e3651e306052897c3327b4eec87d7a85dabe81',
    origin_sha256='482aad4b090f48c7b7ce742f5a0647be5cd2b94915cd99b9fb650d64a1fae240',
    audit=I+'factor_portfolio_v4/summary.json', audit_sha256='df3d3a9ef20c622ce9b529a1aabbba2df18e95ac3e17b1210a866d46657e3ae2',
    control_name='wrong_selected_hash', reason='Exact deliberately false core hash in an independently rejected wrapper gate control; not an artifact identity assertion.')}


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
    for directory, count in zip(REGISTRATIONS, [5, 3, 1, 1], strict=True):
        p = ROOT/directory; receipt = json.loads((p/'summary.json').read_bytes())
        before, after = (p/'CLAIMS.before.yaml').read_bytes(), (p/'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest() == receipt['previous_ledger_sha256']
        assert hashlib.sha256(after).hexdigest() == receipt['ledger_sha256']
        assert previous is None or previous == before, 'registration chain continuity'
        assert len(receipt['new_claim_ids']) == count
        ids.extend(receipt['new_claim_ids']); previous = after
    assert previous == ledger_bytes and len(ledger['claims']) == 148, 'frozen fifteenth registration ledger'
    assert len(set(ids)) == 10
    claims = [c for c in ledger['claims'] if c['id'] in ids]
    assert len(claims) == 10 and all(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in claims)
    dirs = list(DIRS); files = list(FILES); local = dict(LOCAL_FIXED)
    for name, pin in recovery.MANIFESTS.items(): assert common.digest(ROOT/name) == pin
    package_manifest = json.loads((ROOT/(B+'fifteenth_gpu_trace_packages/artifact_packages.json')).read_bytes())
    assert len(package_manifest['packages']) == 192
    for item in package_manifest['packages']:
        local[item['raw_path']] = 'Losslessly packaged GPU raw JSON; exact public gzip recovery, original retained.'
    prior_packages = {}
    prior_recoverable = {B+'prism_all_columns/clauses.body'}
    for name, pin in PRIOR_PACKAGES.items():
        assert common.digest(ROOT/name) == pin and name in tracked, 'authenticated previously published package manifest'
        prior_packages[name] = json.loads((ROOT/name).read_bytes())
        prior_recoverable.update(item['raw_path'] for item in prior_packages[name]['packages'])
    if not args.prepare:
        assert args.coarse_audit and args.coarse_audit_sha256 and args.coarse_audit_source, 'completed coarse outcome audit/source required'
        audit_path = (ROOT/args.coarse_audit).resolve(); assert common.digest(audit_path) == args.coarse_audit_sha256
        audit = json.loads(audit_path.read_bytes())
        assert audit['status'] == args.coarse_audit_status and 'PASS' in audit['status'] and audit['outcome']['recorded_outcome'].startswith('UNKNOWN_'), 'explicit separately checked coarse UNKNOWN outcome'
        for required in [B+'prism_coarse60_bitlift/instance.cnf', B+'prism_coarse60_native_pilot/summary.json',
                B+'prism_coarse60_native_pilot/main/solver.stdout.log', B+'prism_coarse60_native_pilot/main/proof.drat', args.coarse_audit_source]:
            assert audit['inputs_sha256'][required] == common.digest(ROOT/required), 'specific completed coarse input/outcome identity'
        dirs += [B+'prism_coarse60_native_pilot', common.relative(audit_path.parent)]
        files += [args.coarse_audit_source]
        local[B+'prism_coarse60_native_pilot/main/proof.drat'] = 'Retained incomplete UNKNOWN-run trace; no proof certificate or public recovery.'
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
                assert binding['control_name'] in json.loads((ROOT/binding['audit']).read_bytes())['independent_gate_controls']
                corrupt.append(dict(origin=origin, **item, deliberately_false_sha256=expected, reason=binding['reason'])); return
            errors.append(dict(kind='hash_mismatch', origin=origin, **item, expected=expected)); return
        if not (path in selected or path in tracked or path.startswith('external_conway99_research/') or path in LOCAL_TOOLS or path in prior_recoverable):
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
        if obj['raw_path'] == B+'prism_all_columns/instance.cnf':
            header, body = raw.split(b'\n', 1); assert header == b'p cnf 245880 874800'
            assert (ROOT/(B+'prism_all_columns/clauses.body')).read_bytes() == body
            recovered.append(dict(origin=origin, path=B+'prism_all_columns/clauses.body', bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), reconstruction='Drop the exact authenticated DIMACS header line.'))
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
    for name, obj in prior_packages.items():
        check(name, PRIOR_PACKAGES[name], common.relative(Path(__file__)))
        for item in obj['packages']: package(item, name)
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
    # Ensure current Git attributes would preserve every publication payload byte.
    staged_blob_ids = common.git('hash-object', '--stdin-paths', input=('\n'.join(public)+'\n').encode()).decode().splitlines()
    assert len(staged_blob_ids) == len(public)
    git_bytes = []
    for path, git_sha1 in zip(public, staged_blob_ids, strict=True):
        raw = (ROOT/path).read_bytes()
        raw_sha1 = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        assert raw_sha1 == git_sha1, ('Git would transform publication bytes', path)
        git_bytes.append(dict(path=path, git_blob_sha1=git_sha1, sha256=info(path)['sha256']))
    ignored = subprocess.run(['git', 'check-ignore', '--stdin'], cwd=ROOT, input='\n'.join(public)+'\n', text=True, capture_output=True)
    assert ignored.returncode in (0, 1); ignored_paths = ignored.stdout.splitlines(); assert set(ignored_paths) <= set(public)
    common.save(out/'catalog.json', dict(entries=[dict(info(p), availability='LOCAL_ONLY' if p in local else 'READY_FOR_PUBLICATION', limitation=local.get(p)) for p in sorted(selected)],
        directories=dirs, files=files, local_tools=[dict(info(p), availability='LOCAL_ONLY', limitation='Authenticated saved executable; source/build provenance does not guarantee byte-identical rebuild on another toolchain.') for p in sorted(LOCAL_TOOLS)], prior_public_gzip_recoverable_dependencies=sorted(prior_recoverable), prior_public_package_manifests=PRIOR_PACKAGES,
        selection_rule='Exact directory/file allowlists; exact192raw JSON exclusions from authenticated manifest plus four named fixed-core incomplete traces and the completed coarse run partial trace when present.',
        excluded_cohorts=['Pending universal identity-P factor lemma and 64-bit-flip normalization', 'Unregistered older identity-scope/proof-core/preflight work', 'PROMPT.md and dirty historical submodule changes'],
        coarse_outcome_pending=args.prepare, mathematical_reverification_performed=False,
        local_retrieval='Raw JSON and formula recover from exact public gzip; incomplete traces and native executables require local saved paths/rebuild and are not mathematical certificates.'))
    common.save(out/'reference_checks.json', dict(status='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS', records=refs, binding_count=len(refs),
        unique_paths=len({r['path'] for r in refs}), gzip_recoveries=recovered, deliberately_corrupted_control_bindings=corrupt))
    common.save(out/'git_byte_checks.json', dict(status='CURRENT_GIT_FILTER_BYTES_PASS', records=git_bytes, count=len(git_bytes), limitation='Read-only hash-object without -w; no index mutation or publication performed.'))
    common.save(out/'scope.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=common.git('rev-parse', 'HEAD').decode().strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),
        claim_ids=ids, claim_population=len(ledger['claims']), verified_clear=sum(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in ledger['claims']),
        registration_chain_checked=True, target_resolution='UNKNOWN', preparation_only=args.prepare, coarse_outcome_included=not args.prepare,
        local_only=[info(p) for p in sorted(local)]))
    common.save(out/'ignored_payload_paths.json', dict(paths=ignored_paths, raw_log_paths=[p for p in ignored_paths if p.endswith('.log')], meaning='Only these explicitly selected payload paths may be force-staged.'))
    common.save(out/'proposed_raw_ignore_paths.json', dict(paths=sorted(local), reason='Proposal only; no .gitignore edit performed.'))
    payload = sorted(set(public)|{common.relative(p) for p in out.iterdir() if p.is_file()})
    if not args.prepare:
        common.save(out/'stage_inventory.json', dict(paths=payload, entries=[info(p) for p in payload], wrapper_paths_to_add_separately=[common.relative(out/'stage_inventory.json'), common.relative(out/'summary.json')]))
    for p, item in cache.items(): assert common.digest(ROOT/p) == item['sha256'], ('concurrent edit', p)
    assert (ROOT/'CLAIMS.yaml').read_bytes() == ledger_bytes and common.git('ls-files', '--stage', '-z') == index
    status = 'FIFTEENTH_PROVISIONAL_CLOSURE_PASS_COARSE_OUTCOME_PENDING' if args.prepare else 'FIFTEENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS'
    common.save(out/'summary.json', dict(status=status, timestamp=datetime.now(timezone.utc).isoformat(), claim_ids=ids,
        selected_files=len(selected), public_research_files=len(public), public_research_bytes=sum(info(p)['bytes'] for p in public),
        local_only_research_artifacts=len(local), public_recoverable_raw_GPU_JSON_files=192, incomplete_traces=4 if args.prepare else 5,
        reference_bindings=len(refs), unique_referenced_files=len({r['path'] for r in refs}), gzip_recoveries=len(recovered),
        coarse_outcome_pending=args.prepare, output_hashes={common.relative(p):common.digest(p) for p in out.iterdir() if p.is_file()}))
    print(json.dumps(dict(status=status, public_files=len(public), local_only=len(local))))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--prepare', action='store_true')
    ap.add_argument('--coarse-audit'); ap.add_argument('--coarse-audit-sha256'); ap.add_argument('--coarse-audit-status'); ap.add_argument('--coarse-audit-source')
    main(ap.parse_args())
