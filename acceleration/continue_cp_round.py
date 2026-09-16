"""Run exactly one hash-bound CP search round through frozen tools.

This orchestrates existing producers and independent auditors. It does not
solve graph constraints itself, loop over rounds, retry failures, or complete
the research goal. A pending completion candidate remains pending.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
A = ROOT/'acceleration'
PYTHON = ROOT/'.venv/Scripts/python.exe'
GPU = A/'build/overlap_cp_gpu_layout_v2.exe'
GPU_SOURCE = A/'overlap_cp_gpu_layout_v2.cu'
GPU_AUDIT = A/'results/20260916_cp_gpu_layout_v2_controls/audit.json'
CHECKPOINT_STATUSES = {
    'HASH_VERIFIED_CUDA_CP_SEARCH_AND_IMPROVEMENT_CHECKPOINT',
    'HASH_VERIFIED_CP_CONTINUATION_CHECKPOINT',
    'HASH_VERIFIED_CP_CROSS_CONTINUATION_CHECKPOINT',
}
# Filled once during authoring, before independent review and source freeze.
FROZEN_SHA256 = {
    "acceleration/overlap_matching_neighbors.rs": "021fce360a184bde2a7f141f381c0058d886e8e7241bf3204deeb77b5f233bde",
    "acceleration/build/overlap_matching_neighbors.exe": "5815bcbb7736c4375be26f71dbbae11b393b141d7ef020eea09944e0c9afd739",
    "acceleration/audit_whole_matching_family.py": "6cf07c9fbd402616480f06fd2c0ec6af9b005a9c6bb2b57a5473df4c058d8006",
    "acceleration/overlap_cycle_neighbors.rs": "d6c6563b974050246b14e996a737feb9936d18094257a3b47993d64339aaf41c",
    "acceleration/build/overlap_cycle_neighbors.exe": "812373d00ac43e069bd961ed9b173e9c6a83bdac1a7cb34fbd02f4cfee2e8e56",
    "acceleration/audit_atomic_cycle_family.py": "f6878a7c113025382d264e0911f49ca82f2f62cac3237ede1cfcdc5db0138223",
    "acceleration/extract_cross_atomic_family.py": "499dbe03dde2f173a2c27d4351fd709a1d9b9a6eae10fd5530f4cb5ca7bbe613",
    "acceleration/audit_cross_atomic_extraction.py": "9829d8321f008225e5617fa4c9e62b206e72695b284a1a47b064caf6dbf9f51d",
    "acceleration/audit_atomic_trace.py": "83965566c3181020588c94333e2ab7bd0246a49714d491e839a9334468e0d31e",
    "acceleration/search_cp_matching_v2.py": "c3295be46673f67dc8e7cf0d061fd52c079072c0153507eacebbc2ee39442b9c",
    "acceleration/search_cp_cross.py": "2ac011ccf2ea9e4ee5cc4b07982bd167e2f8eb883e5b361b6acaf469c02ef3f6",
    "acceleration/audit_cp_matching_search_v2.py": "13cf83c3047c382dc9fe86b05f605ab3e3b957c90f415073e9fffa76cec658bb",
    "acceleration/audit_cp_cross_search.py": "60eab84b4eecc07509eb470247e9e8728cdc13530b8f1c1a4f2d2de01c9a84e9",
    "acceleration/adopt_cp_search_best.py": "a57ec7b847779cb598f06a91f59179594e8a72abcf4618e4218c0e7e27ebb197",
    "acceleration/adopt_cp_cross_best.py": "d065ccbd11b5d0c264529f4c2d16eddd00d2d5a902c004c93ac986de5d0c3304",
    "acceleration/build_cp_continuation_checkpoint.py": "5a2a715caddb2dd66ef396254ffd8c8f23b36585926f285ddf16cc533d7666ec",
    "acceleration/build_cp_cross_checkpoint.py": "528f031cea3bb30c23f6a291505f164641cfffb9e40b7400003e417762f096c0",
    "acceleration/bind_cp_matching_improvement.py": "8c65cfe3bebc67164f5aeafdd0ed108d802aa07c28502102a739dfecb9e868fb",
    "acceleration/bind_cp_cross_improvement.py": "758592eddf34ef02d9e6e0759a2e8225699dea8fcd6fe8d866b07e52449d75ce",
    "acceleration/audit_certificate.py": "22d3e334930f734890216f18cfc8335c0a5c046f142a72e5a30beca6be9f1c9d",
    "acceleration/audit_phase1.py": "655898a7f9f565dea18236aaa706081c2adb169b84ad836c49dccbe459f7ff2d",
    "acceleration/audit_phase1_kkt.py": "c8efc709bcd10dc11d1f7ef3013a84cd834708880f09af5e026ee8cf3eda2d34",
    "acceleration/audit_matching_accepted.py": "c926dfd2747b20453b706570d5cd759a42d279d8317b0f9855b385cdc5b03452",
    "acceleration/audit_atomic_accepted.py": "ab08a97d7afbe797a27d325e6f6e01d4f70834925f97a364a3574346411ba2ba",
    "acceleration/phase1_probe_ipm.py": "d15215a6cd7c83e8b8b8aa54809d1f0517e4ce2b4b7db78504673bf84db178fa",
    "acceleration/linear_probe.py": "d90fed2c9a2d953dc9fc323f2149975514e107a473bfb860a9d0424d214d68e1",
    "acceleration/check_shortlist_native_pair.py": "5422d2d1cf5abb07ce7c6483f3fc5f5af41c0b2ddcdccf31c70c4c553cf0b398",
    "acceleration/audit_goal_theory_pairs.py": "9da60c600c45c16274efd05db0cf3c21cab8a61969dd2fe0d372ac9a2e7be75f",
    "acceleration/audit_goal_theory_domains.py": "150ea838ad370793b6508728a9ce4d88e5121f51e2774d24f9bb37d244b52388",
    "acceleration/guided_overlap.py": "03a839c004fc049e20ecbbeeb11eaff97baee49b6e8212fc15c2eb596d43fcbf",
    "acceleration/prepare.py": "f9eaf973bb5530b88f12ad455bffa4a82d17904be0786ee37070bb98ead16417",
    "acceleration/star_domains.rs": "b3637615352c0a5372fe7ed2237f34bc2d5c8773a892ee647c05acb772584d80",
    "acceleration/pair_domains.rs": "39fe24d3a87ee4780ad8daff1aeb95cb830fe0877d9ed2b56b0ccdb82e3621ff",
    "acceleration/build/star_domains.exe": "e34d5081e1ce73ef68c47cd9dff2baa41046b7defbea8abe12c2126c5eb95f36",
    "acceleration/build/pair_domains.exe": "7031a0a9d32075fb8f32777149ff5f54466c930726a2777709aa5278779eb976",
    "acceleration/overlap_cp_gpu_layout_v2.cu": "43b1452adee28f01f90e227875f7d08bab6dad8141041c2036945fcd122cc389",
    "acceleration/build/overlap_cp_gpu_layout_v2.exe": "42dbd7ea8f41d9b195d4bfb2c900e5edcd6feec8dd58b9d68f777bca889c065e",
    "acceleration/results/20260916_cp_gpu_layout_v2_controls/audit.json": "caa285833ab3ef523dda693607c37ed3d6c89c9355734bc65728c0cf2f2defed",
    "scratch_next_overlap_cut_bank.py": "6634ac5ac9caa9d2658bbf146774729d4a810d3d4c15a2a20c2b9485877b9a24",
    "scratch_next_overlap_cut.py": "f3069af836a03fc46cf08b647c7bcce2d5b1349e976b4bfd82d9a0a7f968a449",
    "scratch_next_overlap_cut_orbit.py": "b56acd616862b807d7c1ad1f442c35c98ab3db9ab1aa964cef3b29b397c7ec96",
    "acceleration/audit_goal_theory_stars.py": "e572175d69bef9a31ea4896dd74a181cd0d27d212a14f37e4c9871a0f213fb78"
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    path = Path(str(name).replace('\\', '/'))
    if not path.is_absolute():
        path = ROOT/path
        if not path.exists() and len(Path(name).parts) == 1:
            path = A/name
    return path.resolve()


def key(path):
    path = resolve(path)
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def digest(path):
    with resolve(path).open('rb') as stream:
        value = sha256()
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            value.update(chunk)
    return value.hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False)+'\n')


def graph_signature(candidate):
    edges = candidate['overlap_edges_outer_zero_based']
    require(type(edges) is list and len(edges) == 168 and all(type(e) is list and len(e) == 2 and
            all(type(v) is int for v in e) and 0 <= e[0] < e[1] < 84 for e in edges), 'Invalid seed edges')
    require(len(set(map(tuple, edges))) == 168, 'Repeated seed edge')
    return tuple(sorted(map(tuple, edges)))


def preflight(args):
    """Read/hash only. Nothing is created, even on valid input."""
    out = args.out.resolve()
    require(not out.exists(), 'Output root already exists; never resume or retry it')
    require(out.is_relative_to(ROOT) and out != ROOT, 'Output root must be within the workspace')
    require(re.fullmatch('[0-9a-f]{64}', args.previous_sha256) is not None, 'Expected lowercase SHA256')
    previous_path = resolve(args.previous_checkpoint)
    require(previous_path.is_file() and digest(previous_path) == args.previous_sha256, 'Previous checkpoint SHA256 mismatch')
    previous = json.loads(previous_path.read_bytes())
    require(previous.get('status') in CHECKPOINT_STATUSES, 'Unsupported previous checkpoint status')
    require(previous.get('graph_constructed') is False and previous.get('general_nonexistence_proved') is False
            and previous.get('submission_txt_exists') is False and previous['goal'].get('complete') is False,
            'Reassess completed or changed goal state before continuing')
    require(previous.get('pending_completion_work') is None, 'Previous checkpoint has pending completion work')
    require(not (ROOT/'submission.txt').exists(), 'Unexpected submission artifact')
    verified = {}

    def bind(name, expected):
        require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected), 'Malformed expected file hash')
        path, label = resolve(name), key(name)
        if label not in verified:
            require(path.is_file(), 'Missing referenced artifact: '+label)
            verified[label] = digest(path)
        require(verified[label] == expected, 'Changed referenced artifact: '+label)

    def bindings(data):
        if isinstance(data, dict):
            for field, value in data.items():
                if field.endswith('_sha256') and isinstance(value, dict):
                    for name, expected in value.items():
                        bind(name, expected)
                elif field.endswith('_path') and isinstance(value, str) and field[:-5]+'_sha256' in data:
                    bind(value, data[field[:-5]+'_sha256'])
                bindings(value)
        elif isinstance(data, list):
            for value in data:
                bindings(value)

    refs = previous.get('referenced_files_sha256')
    require(type(refs) is dict and refs and len(refs) == previous['verified_referenced_file_count'], 'Invalid checkpoint reference inventory')
    normalized_refs = {key(name): expected for name, expected in refs.items()}
    require(len(normalized_refs) == len(refs), 'Duplicate normalized checkpoint reference paths')
    bindings(previous)
    current = previous['current_best']
    require(current.get('best_pair_ac_independently_nonempty') is True and
            current.get('positive_merit_seed_still_exactly_excluded') is True and current.get('no_graph_completion') is True,
            'Previous seed does not have the required independently checked status')
    candidate, phase = resolve(current['best_candidate_path']), resolve(current['best_phase1_path'])
    for field, path in [('best_candidate_sha256', candidate), ('best_phase1_sha256', phase)]:
        bind(path, current[field])
        require(normalized_refs.get(key(path)) == verified[key(path)], 'Seed artifact is not in checkpoint references')
    seed, warm = json.loads(candidate.read_bytes()), json.loads(phase.read_bytes())
    original = resolve(current['best_original_candidate_path'])
    bind(original, current['best_original_candidate_sha256'])
    warm_candidate = resolve(warm['candidate_path'])
    bind(warm_candidate, warm['candidate_sha256'])
    require(graph_signature(seed) == graph_signature(json.loads(original.read_bytes())) ==
            graph_signature(json.loads(warm_candidate.read_bytes())), 'Seed wrapper/warm/original graph mismatch')
    require(warm['numeric_objective'] == current['best_numeric_merit'], 'Seed phase-I objective differs')
    inputs = {key(previous_path): args.previous_sha256, key(candidate): digest(candidate), key(phase): digest(phase)}
    priors, seen = [], set()
    for value in args.previous_summary:
        path = resolve(value)
        if key(path) in seen:
            continue
        seen.add(key(path))
        summary = json.loads(path.read_bytes())
        require(summary.get('status') in ('BOUNDED_CP_MATCHING_SEARCH_FINISHED', 'BOUNDED_MATCHING_HINT_SHORTLIST_FINISHED'),
                'Prior summary is unfinished or unsupported')
        bindings(summary)
        require(type(summary.get('records')) is list and len(summary['records']) == summary['probes'], 'Prior records malformed')
        for row in summary['records']:
            require(summary['outputs_sha256'].get(row['candidate_path']) == row['candidate_sha256'], 'Prior candidate is not output-bound')
            bind(row['candidate_path'], row['candidate_sha256'])
        inputs[key(path)] = digest(path)
        priors.append(path)
    require(FROZEN_SHA256, 'Frozen tool inventory is empty')
    for name, expected in FROZEN_SHA256.items():
        bind(name, expected)
        inputs[name] = expected
    inputs[key(Path(__file__))] = digest(Path(__file__))
    inputs[key(PYTHON)] = digest(PYTHON)
    gpu_audit = json.loads(GPU_AUDIT.read_bytes())
    require(gpu_audit['status'] == 'INDEPENDENT_CP_GPU_SAVED_CPU_AND_DIRECT_SHORT_REPLAY_AUDIT_PASS', 'GPU QA missing')
    bindings(gpu_audit)
    require(all(gpu_audit['inputs_sha256'].get(key(p)) == digest(p) for p in (GPU, GPU_SOURCE)), 'GPU QA implementation mismatch')
    family_dir, search_dir = out/'family', out/'search'
    inp, native = family_dir/'input.txt', family_dir/'all.json'
    family_audit = family_dir/'independent_audit.json'
    steps = []

    def command(name, program, arguments, result=None, status=None):
        executable = resolve(program)
        argv = ([str(PYTHON), '-B', key(executable)] if executable.suffix == '.py' else [str(executable)]) + list(arguments)
        steps.append(dict(name=name, command=argv, result_path=key(result) if result else None, expected_status=status))

    candidate_arg = key(candidate)
    if args.kind == 'same':
        command('native_family', A/'build/overlap_matching_neighbors.exe', [key(inp), key(native), 'all'], native,
                'COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION')
        command('family_audit', A/'audit_whole_matching_family.py', ['--candidate', candidate_arg, '--input', key(inp),
                '--native', key(native), '--out', key(family_audit)], family_audit, 'INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS')
        driver, auditor, adopter, builder = ('search_cp_matching_v2.py', 'audit_cp_matching_search_v2.py',
                                            'adopt_cp_search_best.py', 'build_cp_continuation_checkpoint.py')
        checkpoint_status = 'HASH_VERIFIED_CP_CONTINUATION_CHECKPOINT'
        search_audit_status = 'INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS'
    else:
        atomic, atomic_audit = family_dir/'all_atomic.json', family_dir/'atomic_audit.json'
        native, family_audit = family_dir/'cross.json', family_dir/'cross_audit.json'
        command('native_atomic_family', A/'build/overlap_cycle_neighbors.exe', [key(inp), key(atomic), 'both'], atomic,
                'COMPLETE_ATOMIC_CYCLE_SUBFAMILY_ENUMERATION')
        command('atomic_family_audit', A/'audit_atomic_cycle_family.py', ['--candidate', candidate_arg, '--input', key(inp),
                '--native', key(atomic), '--out', key(atomic_audit)], atomic_audit, 'INDEPENDENT_COMPLETE_ATOMIC_CYCLE_FAMILY_PASS')
        common = ['--candidate', candidate_arg, '--native', key(atomic), '--family-audit', key(atomic_audit)]
        command('extract_cross', A/'extract_cross_atomic_family.py', [*common, '--out', key(native)], native,
                'COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION')
        command('cross_family_audit', A/'audit_cross_atomic_extraction.py', [*common, '--adapted', key(native), '--out', key(family_audit)],
                family_audit, 'INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS')
        driver, auditor, adopter, builder = ('search_cp_cross.py', 'audit_cp_cross_search.py',
                                            'adopt_cp_cross_best.py', 'build_cp_cross_checkpoint.py')
        checkpoint_status = 'HASH_VERIFIED_CP_CROSS_CONTINUATION_CHECKPOINT'
        search_audit_status = 'INDEPENDENT_CP_CROSS_SEARCH_AUDIT_PASS'
    search_args = ['--native', key(native), '--family-audit', key(family_audit), '--initial', candidate_arg,
                   '--initial-phase1', key(phase), '--gpu', key(GPU), '--gpu-source', key(GPU_SOURCE),
                   '--gpu-audit', key(GPU_AUDIT), '--out', key(search_dir)]
    for prior in priors:
        search_args.extend(['--previous-summary', key(prior)])
    command('search', A/driver, search_args, search_dir/'summary.json', 'BOUNDED_CP_MATCHING_SEARCH_FINISHED')
    command('search_audit', A/auditor, ['--run', key(search_dir), '--out', key(search_dir/'audit.json')],
            search_dir/'audit.json', search_audit_status)
    command('adoption', A/adopter, ['--directory', key(search_dir)], search_dir/'adoption.json', 'CP_EXACT_IMPROVEMENT_LOCAL_ADOPTION_FINISHED')
    command('checkpoint', A/builder, ['--previous', key(previous_path), '--previous-sha256', args.previous_sha256,
            '--family-audit', key(family_audit), '--directory', key(search_dir), '--extra-report', key(out/'run_manifest.json'),
            '--out', key(out/'checkpoint.json')], out/'checkpoint.json', checkpoint_status)
    manifest = dict(status='HASH_VERIFIED_ONE_CP_ROUND_MANIFEST', kind=args.kind,
                    created_utc=datetime.now(timezone.utc).isoformat(), inputs_sha256=inputs,
                    previous_checkpoint_path=key(previous_path), previous_checkpoint_sha256=args.previous_sha256,
                    previous_checkpoint_references_verified=len(refs), all_preflight_files_verified=len(verified),
                    initial_candidate_path=key(candidate), initial_candidate_sha256=digest(candidate),
                    initial_phase1_path=key(phase), initial_phase1_sha256=digest(phase), initial_numeric_merit=warm['numeric_objective'],
                    previous_summaries=[key(p) for p in priors], output_root=key(out), steps=steps,
                    cp_parameters=dict(coarse_steps=500, refine_steps=2000, refine_count=2048, lp_count=64),
                    rounds=1, retry_existing_output=False, numerical_CP_values_are_proofs=False, marks_goal_complete=False,
                    pending_completion_policy='Leave the existing adopter pending record unchanged; do not start another round.',
                    scope='Invoke frozen producers and independent auditors for one bounded round; no new solver or mathematical proof implementation.')
    return manifest, seed, out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous-checkpoint', type=Path, required=True)
    parser.add_argument('--previous-sha256', required=True)
    parser.add_argument('--kind', choices=('same', 'cross'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--previous-summary', type=Path, action='append', default=[])
    parser.add_argument('--validate-only', action='store_true', help='Verify inputs and print the command plan without creating files or launching tools')
    args = parser.parse_args()
    manifest, seed, out = preflight(args)
    if args.validate_only:
        print(json.dumps(dict(status='ONE_CP_ROUND_READ_ONLY_PREFLIGHT_PASS', manifest=manifest,
                             processes_launched=0, output_created=False)), flush=True)
        return
    out.mkdir(parents=True, exist_ok=False)
    save(out/'run_manifest.json', manifest)
    (out/'family').mkdir()
    (out/'logs').mkdir()
    with (out/'family/input.txt').open('x', encoding='ascii', newline='\n') as stream:
        stream.write('C99OVERLAPS1 1\n'+' '.join(str(v) for edge in sorted(seed['overlap_edges_outer_zero_based']) for v in edge)+'\n')
    completed, active = [], None
    started = time.perf_counter()
    try:
        for order, step in enumerate(manifest['steps']):
            active = step['name']
            require(all(digest(name) == expected for name, expected in manifest['inputs_sha256'].items()), 'Bound orchestration input changed')
            require(step['result_path'] is None or not resolve(step['result_path']).exists(), 'Step output already exists; no retry')
            logfile = out/'logs'/f'{order:02d}_{active}.log'
            print(json.dumps(dict(stage=active, event='START')), flush=True)
            begin = time.perf_counter()
            with logfile.open('x', encoding='utf-8') as stream:
                process = subprocess.run(step['command'], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=False)
            require(process.returncode == 0, f'{active} failed with exit code {process.returncode}; see {key(logfile)}')
            result = json.loads(resolve(step['result_path']).read_bytes())
            require(result.get('status') == step['expected_status'], 'Unexpected step status: '+active)
            completed.append(dict(stage=active, result_path=step['result_path'], result_sha256=digest(step['result_path']),
                                  log_path=key(logfile), log_sha256=digest(logfile), elapsed_seconds=time.perf_counter()-begin))
            save(out/'logs'/f'{order:02d}_{active}_completed.json', completed[-1])
            print(json.dumps(dict(stage=active, event='FINISHED', elapsed_seconds=completed[-1]['elapsed_seconds'])), flush=True)
        checkpoint = json.loads((out/'checkpoint.json').read_bytes())
        require(checkpoint['graph_constructed'] is False and checkpoint['general_nonexistence_proved'] is False,
                'Unexpected goal-state change')
        report = dict(status='ONE_CP_ROUND_FINISHED_GOAL_REMAINS_OPEN', kind=args.kind,
                      manifest_path=key(out/'run_manifest.json'), manifest_sha256=digest(out/'run_manifest.json'),
                      checkpoint_path=key(out/'checkpoint.json'), checkpoint_sha256=digest(out/'checkpoint.json'),
                      completed_steps=completed, pending_completion_work=checkpoint['pending_completion_work'],
                      best_numeric_merit=checkpoint['current_best']['best_numeric_merit'], elapsed_seconds=time.perf_counter()-started,
                      graph_constructed=False, general_nonexistence_proved=False, goal_marked_complete=False)
        save(out/'run_result.json', report)
        print(json.dumps({k: report[k] for k in ('status', 'checkpoint_path', 'checkpoint_sha256', 'best_numeric_merit', 'pending_completion_work')}), flush=True)
    except BaseException as exc:
        save(out/'run_failure.json', dict(status='ONE_CP_ROUND_STOPPED_PRESERVING_ARTIFACTS', stage=active,
             error_type=type(exc).__name__, message=str(exc), completed_steps=completed, retries=0,
             manifest_path=key(out/'run_manifest.json'), manifest_sha256=digest(out/'run_manifest.json'),
             elapsed_seconds=time.perf_counter()-started, goal_marked_complete=False))
        raise


if __name__ == '__main__':
    main()
