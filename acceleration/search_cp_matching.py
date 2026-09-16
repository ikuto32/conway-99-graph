"""Bounded whole-matching search using CUDA CP reoptimization, then exact-auditable LPs.

Floating CP values rank candidates only; they never exclude a candidate or prove
feasibility. Every stage restarts from the same semantic warm X/Y, and preserves
the initial upper bound. Final LP artifacts still need independent auditing.
"""
import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import subprocess
import time

from audit_phase1 import graph_rows, compare_rows
from phase1_probe_ipm import solve_edges_with_basis

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'acceleration/results'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, separators=(',', ':'), allow_nan=False) + '\n')


def signature(edges):
    return tuple(sorted(map(tuple, edges)))


def edge_hash(edges):
    return sha256(json.dumps(signature(edges), separators=(',', ':')).encode('ascii')).hexdigest()


def choose(eligible, scores, moves, count, diversity_count):
    ordered = sorted(eligible, key=lambda i: (scores[i], i))
    coordinates = {i: (moves[i]['root_group'], moves[i]['matching_class']) for i in eligible}
    parts = {i: tuple(sorted(len(c)//2 for c in moves[i]['alternating_cycles'])) for i in eligible}
    selected, roles = [], {}

    def add(i, role):
        if i not in roles:
            selected.append(i)
            roles[i] = []
        roles[i].append(role)

    for coordinate in sorted(set(coordinates.values())):
        add(next(i for i in ordered if coordinates[i] == coordinate), 'coordinate_minimum')
    for part in sorted(set(parts.values())):
        add(next(i for i in ordered if parts[i] == part), 'cycle_partition_minimum')
    represented = {(coordinates[i], parts[i]) for i in selected}
    for i in ordered:
        if len(selected) >= diversity_count:
            break
        bucket = (coordinates[i], parts[i])
        if bucket not in represented:
            add(i, 'coordinate_partition_minimum')
            represented.add(bucket)
    for i in ordered:
        if len(selected) >= count:
            break
        if i not in roles:
            add(i, 'global_score_fill')
    require(len(selected) == count, 'Insufficient eligible candidates')
    return [dict(proposal_index=i, selection_roles=roles[i], score=scores[i], move=moves[i]) for i in selected]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--native', type=Path, default=RESULTS/'20260916_cp_new_seed_family/all.json')
    parser.add_argument('--family-audit', type=Path, default=RESULTS/'20260916_cp_new_seed_family/independent_audit.json')
    parser.add_argument('--initial', type=Path, default=RESULTS/'20260916_matching_hint_shortlist/adopted_index_17109/best_candidate.json')
    parser.add_argument('--initial-phase1', type=Path, default=RESULTS/'20260916_matching_hint_shortlist/adopted_index_17109/best_phase1.json')
    parser.add_argument('--gpu-audit', type=Path, default=RESULTS/'20260916_cp_gpu_controls/audit.json')
    parser.add_argument('--gpu', type=Path, default=ROOT/'acceleration/build/overlap_cp_gpu.exe')
    parser.add_argument('--coarse-steps', type=int, default=500)
    parser.add_argument('--refine-steps', type=int, default=2000)
    parser.add_argument('--refine-count', type=int, default=2048)
    parser.add_argument('--lp-count', type=int, default=64)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve all previous outputs')
    require(args.coarse_steps > 0 and args.refine_steps > args.coarse_steps and args.refine_count >= args.lp_count >= 32,
            'Invalid stage sizes')
    started = time.perf_counter()
    inputs = {}

    def bind(path, expected=None):
        actual = digest(path)
        require(expected is None or expected == actual, 'Changed dependency: ' + str(path))
        inputs[key(path)] = actual
        return actual

    for path in [Path(__file__), args.native, args.family_audit, args.initial, args.initial_phase1,
                 args.gpu_audit, args.gpu] + [ROOT/'acceleration'/name for name in
                 ('overlap_cp_gpu.cu', 'phase1_probe_ipm.py', 'linear_probe.py', 'audit_phase1.py', 'audit_certificate.py')]:
        bind(path)
    gpu_audit = json.loads(args.gpu_audit.read_bytes())
    require(gpu_audit['status'] == 'INDEPENDENT_CP_GPU_SAVED_CPU_AND_DIRECT_SHORT_REPLAY_AUDIT_PASS', 'GPU controls have not passed')
    # Bind every saved control dependency, including the precise executable.
    for name, expected in gpu_audit['inputs_sha256'].items():
        path = Path(name)
        bind(path if path.is_absolute() else ROOT/path, expected)
    require(inputs[key(args.gpu)] == gpu_audit['inputs_sha256'][key(args.gpu)], 'Different GPU binary')
    family = json.loads(args.family_audit.read_bytes())
    require(family['status'] == 'INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS', 'Family audit missing')
    for name, expected in family['inputs_sha256'].items():
        path = Path(name)
        bind(path if path.is_absolute() else ROOT/path, expected)
    data = json.loads(args.native.read_bytes())
    candidates, moves = data['overlap_candidates'], data['moves']
    require(len(candidates) == len(moves) == family['legal_count'] and data['selector'] == 'all', 'Family size/scope mismatch')
    initial, warm = [json.loads(path.read_bytes()) for path in (args.initial, args.initial_phase1)]
    warm_candidate = ROOT/Path(warm['candidate_path'])
    bind(warm_candidate, warm['candidate_sha256'])
    require(signature(initial['overlap_edges_outer_zero_based']) == signature(json.loads(warm_candidate.read_bytes())['overlap_edges_outer_zero_based']), 'Warm candidate mismatch')
    edges, rows, omitted = graph_rows(initial)
    require(len(rows) == 4326 and len(omitted) == 336 and list(map(list, edges)) == warm['edge_variables'], 'Warm semantic order mismatch')
    compare_rows(warm['constraint_groups'], rows)
    x = warm['numeric_edge_values']
    mapped = {(r['kind'], tuple(r['coordinate'])): y for r, y in zip(warm['constraint_groups'], warm['phase1_multipliers'])}
    y = [min(1, max(-1 if r['equality'] else 0, mapped.get((r['kind'], tuple(r['coordinate'])), 0))) for r in rows]
    require(len(x) == 1680 and all(isfinite(v) and 0 <= v <= 1 for v in x), 'Invalid warm X')
    require(len(y) == 4326 and all(isfinite(v) for v in y), 'Invalid warm Y')
    excluded, prior = set(), []
    for directory in ['20260916_whole_matching_pilot', '20260916_matching_hint_shortlist']:
        for path in sorted((RESULTS/directory/'probes').glob('*_candidate.json')):
            old = json.loads(path.read_bytes())['overlap_edges_outer_zero_based']
            excluded.add(signature(old))
            prior.append(dict(candidate_path=key(path), candidate_sha256=bind(path), overlap_edges_sha256=edge_hash(old)))
    args.out.mkdir(parents=True)
    outputs = {}

    def output(path, value):
        save(path, value)
        outputs[key(path)] = digest(path)

    output(args.out/'manifest.json', dict(status='CP_MATCHING_SEARCH_MANIFEST', inputs_sha256=inputs,
           baseline_numeric_objective=warm['numeric_objective'], coarse_steps=args.coarse_steps,
           refine_steps=args.refine_steps, refine_count=args.refine_count, lp_count=args.lp_count,
           coarse_candidates=len(candidates), initial_x=x, initial_y=y, previous_candidates=prior,
           selection_policy='Rank by checked best upper only. Coordinate minima, partition minima, coordinate/partition strata, then global score. Refine diversity prefix140; LP diversity prefix32. Restart every stage from common initial X/Y.',
           scope='Floating CP ranking only, no exclusions by numeric duals; bounded LP selection, not exhaustive LP coverage.'))

    def gpu_run(stem, indices, steps, vectors=False, baseline=False):
        path, result_path = args.out/(stem+'_input.txt'), args.out/(stem+'_gpu.json')
        ks = ([initial['overlap_edges_outer_zero_based']] if baseline else []) + [candidates[i] for i in indices]
        with path.open('x', encoding='ascii', newline='\n') as stream:
            stream.write(f'C99CP1 {len(ks)} 1\n{steps}\n')
            stream.write(' '.join(format(v, '.17g') for v in x) + '\n')
            stream.write(' '.join(format(v, '.17g') for v in y) + '\n')
            for k in ks:
                stream.write(' '.join(str(v) for edge in k for v in edge) + '\n')
        outputs[key(path)] = digest(path)
        command = [str(args.gpu.resolve()), str(path.resolve()), str(result_path.resolve())]
        if vectors:
            command.append('--vectors')
        t = time.perf_counter()
        subprocess.run(command, check=True, timeout=1800)
        outputs[key(result_path)] = digest(result_path)
        result = json.loads(result_path.read_bytes())
        require(result['status'] == 'NUMERICAL_CHAMBOLLE_POCK_PHASE1_HEURISTIC' and len(result['results']) == len(ks), 'Bad GPU status/size')
        scores = {}
        for j, record in enumerate(result['results']):
            require(record['candidate_index'] == j and len(record['checkpoints']) == 1, 'Bad GPU result order')
            checkpoint = record['checkpoints'][0]
            require(checkpoint['iterations'] == steps, 'Wrong GPU checkpoint')
            upper = min(record['initial']['primal_upper'], checkpoint['last']['primal_upper'], checkpoint['average']['primal_upper'])
            lower = max(record['initial']['dual_lower'], checkpoint['last']['dual_lower'], checkpoint['average']['dual_lower'])
            require(all(isfinite(v) for v in [upper, lower, checkpoint['best_upper'], checkpoint['best_lower']]) and
                    upper >= 0 and lower <= upper + 1e-7 and abs(checkpoint['best_upper']-upper) < 1e-10 and
                    abs(checkpoint['best_lower']-lower) < 1e-10, 'Invalid GPU numerical summary')
            if not baseline or j:
                scores[indices[j-int(baseline)]] = upper
        report = dict(stage=stem, candidate_count=len(ks), steps=steps, elapsed_seconds=time.perf_counter()-t,
                      gpu_input_path=key(path), gpu_input_sha256=digest(path), gpu_output_path=key(result_path),
                      gpu_output_sha256=digest(result_path), proposal_indices=([None] if baseline else [])+indices,
                      minimum_upper=min(scores.values()), baseline_included=baseline)
        output(args.out/(stem+'_stage.json'), report)
        print(json.dumps({k:v for k,v in report.items() if k not in ('proposal_indices',)}), flush=True)
        return scores

    coarse = gpu_run('coarse', list(range(len(candidates))), args.coarse_steps, baseline=True)
    refine_selection = choose(list(coarse), coarse, moves, args.refine_count, 140)
    output(args.out/'refine_selection.json', refine_selection)
    refined = gpu_run('refined', [r['proposal_index'] for r in refine_selection], args.refine_steps, baseline=True)
    eligible = [i for i in refined if signature(candidates[i]) not in excluded]
    selection = choose(eligible, refined, moves, args.lp_count, 32)
    for order, record in enumerate(selection):
        i = record['proposal_index']
        record.update(selection_order=order, coarse_score=coarse[i], overlap_edges_sha256=edge_hash(candidates[i]))
    output(args.out/'lp_selection.json', selection)
    # Retain selected vectors for independent full99/CPU audits; this rerun is
    # deliberately identical to the scalar refined stage, not an extra optimizer.
    replay = gpu_run('selected_vectors', [r['proposal_index'] for r in selection], args.refine_steps, vectors=True)
    require(all(abs(replay[i]-refined[i]) <= 1e-9 for i in replay), 'Selected-vector rerun differs')
    (args.out/'probes').mkdir()
    records = []
    for chosen in selection:
        i = chosen['proposal_index']
        stem = f"selection_{chosen['selection_order']:02d}_index_{i}"
        candidate_path = args.out/'probes'/(stem+'_candidate.json')
        result_path = args.out/'probes'/(stem+'_phase1.json')
        output(candidate_path, dict(overlap_edges_outer_zero_based=candidates[i], selection=chosen,
                                    native_source_path=key(args.native), native_source_sha256=inputs[key(args.native)]))
        result, _ = solve_edges_with_basis(candidates[i], seconds=30, basis=None)
        result.update(candidate_path=key(candidate_path), candidate_sha256=digest(candidate_path))
        require(result['overlap_edges_sha256'] == chosen['overlap_edges_sha256'], 'LP candidate association differs')
        for name, expected in result['source_sha256'].items():
            require(inputs[key(ROOT/'acceleration'/name)] == expected, 'LP source changed')
        output(result_path, result)
        records.append(dict(**chosen, candidate_path=key(candidate_path), candidate_sha256=digest(candidate_path),
                            result_path=key(result_path), result_sha256=digest(result_path),
                            numeric_objective=result['numeric_objective'], optimal=result['optimal'], status=result['status']))
        if len(records)%8 == 0:
            print(json.dumps(dict(lp_completed=len(records), best_numeric_objective=min(r['numeric_objective'] for r in records if r['numeric_objective'] is not None))), flush=True)
    require(all(digest(ROOT/name) == expected for name, expected in inputs.items()), 'Source/input changed during search')
    usable = sorted((r for r in records if r['numeric_objective'] is not None), key=lambda r:(r['numeric_objective'], r['proposal_index']))
    improved = [r for r in usable if r['numeric_objective'] < warm['numeric_objective']]
    summary = dict(status='BOUNDED_CP_MATCHING_SEARCH_FINISHED', inputs_sha256=inputs, outputs_sha256=outputs,
                   coarse_candidate_count=len(candidates), refined_candidate_count=len(refined), probes=len(records),
                   baseline_numeric_objective=warm['numeric_objective'], best=usable[0] if usable else None,
                   numerically_optimal_count=sum(r['optimal'] for r in records), numerical_improvement_count=len(improved),
                   numerically_improving_candidates=improved, records=records, elapsed_seconds=time.perf_counter()-started,
                   cp_values_used_as_proof=False, pair_gates_run=0, full_graph_constructed=False, general_nonexistence_proved=False)
    save(args.out/'summary.json', summary)
    print(json.dumps({k:summary[k] for k in ('status','probes','numerical_improvement_count','elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
