"""Cross1 CP search: audited cross single3/4 cycles with version2 input guards.

Floating CP values rank candidates only; they never exclude a candidate or prove
feasibility. Every stage restarts from the same semantic warm X/Y, and preserves
the initial upper bound. Final LP artifacts still need independent auditing.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
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


def resolve(path):
    result = Path(str(path).replace('\\', '/'))
    return result if result.is_absolute() else ROOT/result


def valid_signature(edges):
    require(type(edges) is list and len(edges) == 168 and all(
        type(e) is list and len(e) == 2 and all(type(v) is int for v in e)
        and 0 <= e[0] < e[1] < 84 for e in edges), 'Invalid prior candidate edges')
    result = signature(edges)
    require(len(set(result)) == 168, 'Duplicate prior candidate edge')
    return result


def validate_cross_moves(data, family, base_signature):
    """Guard adapter metadata/order; family completeness comes from its audit."""
    candidates, moves = data['overlap_candidates'], data['moves']
    indices = data.get('original_native_indices')
    require(type(indices) is list and len(indices) == len(moves) and
            all(type(i) is int and i >= 0 for i in indices) and indices == sorted(set(indices)),
            'Cross original indices are not strictly increasing')
    require(data.get('legal_count') == family['legal_count'] == len(moves), 'Cross legal count differs')
    labels = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2)
              for s in range(2) for t in range(2)]
    known, seen = set(base_signature), set()
    counts = Counter()
    for edges, move, original_index in zip(candidates, moves, indices):
        group, size = move['root_group'], move['cycle_size']
        require(type(group) is int and 0 <= group < 7 and type(size) is int and size in (3, 4)
                and move['matching_class'] == 'cross' and move['changed_edges'] == size,
                'Invalid cross move coordinate or size')
        require(move['original_native_index'] == original_index, 'Cross original index association differs')
        removed, added = move['removed'], move['added']
        for changed in (removed, added):
            require(type(changed) is list and len(changed) == size and all(
                type(e) is list and len(e) == 2 and all(type(v) is int for v in e)
                and 0 <= e[0] < e[1] < 84 for e in changed), 'Malformed cross changed edges')
            require(changed == sorted(changed) and len(set(map(tuple, changed))) == size,
                    'Cross changed edges are not canonical')
        old, new = set(map(tuple, removed)), set(map(tuple, added))
        require(old <= known and not new & known, 'Cross removed/added presence mismatch')
        cycle = move['alternating_cycle']
        require(type(cycle) is list and len(cycle) == 2*size and all(type(v) is int and 0 <= v < 84 for v in cycle)
                and len(set(cycle)) == 2*size and cycle[0] == min(cycle)
                and move['alternating_cycles'] == [cycle], 'Noncanonical single cross cycle')
        def colors(vertices):
            return ({tuple(sorted((vertices[i], vertices[i+1]))) for i in range(0, 2*size, 2)},
                    {tuple(sorted((vertices[i], vertices[(i+1) % (2*size)]))) for i in range(1, 2*size, 2)})
        require(colors(cycle) == (old, new), 'Cross cycle edge colors differ')
        source_cycle = move['source_alternating_cycle']
        require(type(source_cycle) is list and len(source_cycle) == 2*size and
                all(type(v) is int for v in source_cycle) and set(source_cycle) == set(cycle)
                and colors(source_cycle) == (old, new), 'Original cross cycle geometry differs')
        signs = {u: [symbol % 2 for symbol in labels[u] if symbol // 2 == group] for u in cycle}
        require(all(len(v) == 1 for v in signs.values()) and
                all(signs[u] != signs[v] for u, v in old | new), 'Cross root/sign membership differs')
        final = valid_signature(edges)
        require(set(final) == (known-old) | new and final not in seen, 'Cross final graph/order association differs')
        seen.add(final)
        counts[group, size] += 1
    require(data['by_class'] == family['by_class'] and len(data['by_class']) == 14,
            'Cross family class inventory differs')
    require({(r['root_group'], r['cycle_size']) for r in data['by_class']} ==
            {(g, k) for g in range(7) for k in (3, 4)}, 'Cross family coordinates differ')
    for row in data['by_class']:
        require(row['matching_class'] == 'cross' and row['legal_cycles'] == counts[row['root_group'], row['cycle_size']],
                'Cross per-coordinate legal count differs')
    require(family['per_cycle_size_legal'] == {str(k): sum(counts[g, k] for g in range(7)) for k in (3, 4)},
            'Cross per-size count differs')


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
    parser.add_argument('--native', type=Path, default=RESULTS/'20260916_cp_cross_family_qa/cross.json')
    parser.add_argument('--family-audit', type=Path, default=RESULTS/'20260916_cp_cross_family_qa/cross_independent_audit.json')
    parser.add_argument('--initial', type=Path, default=RESULTS/'20260916_cp_matching_search/adopted_index_59390/best_candidate.json')
    parser.add_argument('--initial-phase1', type=Path, default=RESULTS/'20260916_cp_matching_search/adopted_index_59390/best_phase1.json')
    parser.add_argument('--gpu-audit', type=Path, default=RESULTS/'20260916_cp_gpu_controls/audit.json')
    parser.add_argument('--gpu', type=Path, default=ROOT/'acceleration/build/overlap_cp_gpu.exe')
    parser.add_argument('--gpu-source', type=Path, default=ROOT/'acceleration/overlap_cp_gpu.cu')
    parser.add_argument('--coarse-steps', type=int, default=500)
    parser.add_argument('--refine-steps', type=int, default=2000)
    parser.add_argument('--refine-count', type=int, default=2048)
    parser.add_argument('--lp-count', type=int, default=64)
    parser.add_argument('--previous-summary', type=Path, action='append', default=[],
                        help='Repeatable completed CP/hint-shortlist summary; exclude its exact candidate edge sets')
    parser.add_argument('--validate-only', action='store_true',
                        help='Validate all inputs and print counts, without creating output or launching GPU/LP')
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve all previous outputs')
    require(1 <= args.coarse_steps < args.refine_steps <= 1000000 and
            32 <= args.lp_count <= 64 and 140 <= args.refine_count <= 99999,
            'Invalid stage sizes')
    started = time.perf_counter()
    inputs = {}

    def bind(path, expected=None):
        actual = digest(path)
        require(expected is None or expected == actual, 'Changed dependency: ' + str(path))
        inputs[key(path)] = actual
        return actual

    for path in [Path(__file__), args.native, args.family_audit, args.initial, args.initial_phase1,
                 args.gpu_audit, args.gpu, args.gpu_source] + [ROOT/'acceleration'/name for name in
                 ('phase1_probe_ipm.py', 'linear_probe.py', 'audit_phase1.py', 'audit_certificate.py')]:
        bind(path)
    gpu_audit = json.loads(args.gpu_audit.read_bytes())
    require(gpu_audit['status'] == 'INDEPENDENT_CP_GPU_SAVED_CPU_AND_DIRECT_SHORT_REPLAY_AUDIT_PASS', 'GPU controls have not passed')
    # Bind every saved control dependency, including the precise executable.
    gpu_bindings = {key(resolve(name)): expected for name, expected in gpu_audit['inputs_sha256'].items()}
    for name, expected in gpu_bindings.items():
        bind(resolve(name), expected)
    require(inputs[key(args.gpu)] == gpu_bindings.get(key(args.gpu)), 'Different GPU binary')
    require(inputs[key(args.gpu_source)] == gpu_bindings.get(key(args.gpu_source)), 'Different GPU source')
    family = json.loads(args.family_audit.read_bytes())
    require(family['status'] == 'INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS', 'Family audit missing')
    family_bindings = {key(resolve(name)): expected for name, expected in family['inputs_sha256'].items()}
    for name, expected in family_bindings.items():
        bind(resolve(name), expected)
    native_matches = sorted(name for name, expected in family_bindings.items()
                            if expected == inputs[key(args.native)] and Path(name).suffix == '.json')
    require(native_matches, 'Native payload is not byte-identical to a family-audited input')
    bound_native = key(args.native) if key(args.native) in native_matches else native_matches[0]
    initial, warm = [json.loads(path.read_bytes()) for path in (args.initial, args.initial_phase1)]
    base_signature = valid_signature(initial['overlap_edges_outer_zero_based'])
    bound_bases = []
    for name in family_bindings:
        if Path(name).suffix == '.json' and name not in native_matches:
            bound_data = json.loads(resolve(name).read_bytes())
            if 'overlap_edges_outer_zero_based' in bound_data:
                bound_bases.append((name, valid_signature(bound_data['overlap_edges_outer_zero_based'])))
    require(len(bound_bases) == 1, 'Family audit must bind one explicit base candidate')
    bound_base, audited_base_signature = bound_bases[0]
    require(base_signature == audited_base_signature, 'Initial graph differs from family-audited base')
    family_association = dict(native_path=key(args.native), native_sha256=inputs[key(args.native)],
        bound_native_path=bound_native, bound_native_sha256=family_bindings[bound_native],
        native_method='EXACT_BOUND_FILE' if key(args.native) == bound_native else 'IDENTICAL_BOUND_BYTES',
        initial_path=key(args.initial), initial_sha256=inputs[key(args.initial)],
        bound_base_path=bound_base, bound_base_sha256=family_bindings[bound_base],
        base_method='EXACT_BOUND_FILE' if key(args.initial) == bound_base else 'EXACT_LABELED_GRAPH_IDENTITY',
        overlap_edges_sha256=edge_hash(initial['overlap_edges_outer_zero_based']))
    warm_candidate = resolve(warm['candidate_path'])
    bind(warm_candidate, warm['candidate_sha256'])
    require(base_signature == valid_signature(json.loads(warm_candidate.read_bytes())['overlap_edges_outer_zero_based']), 'Warm candidate mismatch')
    groups, raw_y = warm['constraint_groups'], warm['phase1_multipliers']
    require(type(groups) is list and type(raw_y) is list and len(groups) == len(raw_y), 'Raw warm dual length mismatch')
    require(all(type(v) in (int, float) and isfinite(v) for v in raw_y), 'Raw warm dual is nonfinite or nonnumeric')
    semantic_keys = [(row['kind'], tuple(row['coordinate'])) for row in groups]
    require(len(set(semantic_keys)) == len(semantic_keys), 'Duplicate warm semantic row key')
    edges, rows, omitted = graph_rows(initial)
    require(len(rows) == 4326 and len(omitted) == 336 and list(map(list, edges)) == warm['edge_variables'], 'Warm semantic order mismatch')
    compare_rows(warm['constraint_groups'], rows)
    x = warm['numeric_edge_values']
    mapped = dict(zip(semantic_keys, raw_y))
    y = [min(1, max(-1 if r['equality'] else 0, mapped.get((r['kind'], tuple(r['coordinate'])), 0))) for r in rows]
    require(type(x) is list and len(x) == 1680 and all(type(v) in (int, float) and isfinite(v) and 0 <= v <= 1 for v in x), 'Invalid warm X')
    require(len(y) == 4326 and all(isfinite(v) for v in y), 'Invalid warm Y')
    require(type(warm['numeric_objective']) in (int, float) and isfinite(warm['numeric_objective']) and warm['numeric_objective'] >= 0,
            'Invalid baseline numerical objective')
    data = json.loads(args.native.read_bytes())
    candidates, moves = data['overlap_candidates'], data['moves']
    require(data['status'] == 'COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION' and
            len(candidates) == len(moves) == family['legal_count'] and data['selector'] == 'cross_3_4'
            and data['cycle_sizes'] == [3, 4], 'Family size/scope mismatch')
    validate_cross_moves(data, family, base_signature)
    for name, expected in data['inputs_sha256'].items():
        bind(resolve(name), expected)
    for path_field, hash_field in [('candidate_path', 'candidate_sha256'),
                                 ('source_native_path', 'source_native_sha256'),
                                 ('source_family_audit_path', 'source_family_audit_sha256')]:
        target = resolve(data[path_field])
        require(family['inputs_sha256'].get(key(target)) == data[hash_field],
                'Cross extraction provenance is not family-bound: ' + path_field)
        bind(target, data[hash_field])
    require(valid_signature(json.loads(resolve(data['candidate_path']).read_bytes())['overlap_edges_outer_zero_based']) == base_signature,
            'Cross extraction base graph differs')
    require(args.refine_count <= len(candidates) <= 99999, 'Native/refinement count exceeds available or GPU batch size')
    excluded, prior = set(), []
    prior_by_path = {}

    def add_prior(path, expected, origin):
        path = resolve(path)
        actual = bind(path, expected)
        old = json.loads(path.read_bytes())['overlap_edges_outer_zero_based']
        excluded.add(valid_signature(old))
        name = key(path)
        if name not in prior_by_path:
            record = dict(candidate_path=name, candidate_sha256=actual, overlap_edges_sha256=edge_hash(old), origins=[])
            prior_by_path[name] = record
            prior.append(record)
        prior_by_path[name]['origins'].append(origin)

    for directory in ['20260916_whole_matching_pilot', '20260916_matching_hint_shortlist']:
        for path in sorted((RESULTS/directory/'probes').glob('*_candidate.json')):
            add_prior(path, None, dict(kind='DEFAULT_PROBE_DIRECTORY', directory=key(RESULTS/directory)))
    require(len(prior) == 193, 'Default previous129+64 probe inventory changed')
    previous_summary_reports = []
    seen_summaries = set()
    for path in args.previous_summary:
        path = resolve(path)
        if key(path) in seen_summaries:
            continue
        seen_summaries.add(key(path))
        summary_sha = bind(path)
        previous = json.loads(path.read_bytes())
        require(previous['status'] in ('BOUNDED_CP_MATCHING_SEARCH_FINISHED', 'BOUNDED_MATCHING_HINT_SHORTLIST_FINISHED'),
                'Previous summary is not a completed CP/hint-shortlist run')
        records = previous['records']
        require(type(records) is list and len(records) == previous['probes'], 'Previous summary record count mismatch')
        summary_signatures = set()
        for record in records:
            candidate_path = resolve(record['candidate_path'])
            expected = record['candidate_sha256']
            declared = {key(resolve(name)): value for name, value in previous['outputs_sha256'].items()}
            require(declared.get(key(candidate_path)) == expected, 'Previous summary candidate/output binding differs')
            add_prior(candidate_path, expected, dict(kind='PREVIOUS_SUMMARY', summary_path=key(path), summary_sha256=summary_sha))
            summary_signatures.add(signature(json.loads(candidate_path.read_bytes())['overlap_edges_outer_zero_based']))
        previous_summary_reports.append(dict(path=key(path), sha256=summary_sha, status=previous['status'],
                                             records_count=len(records), unique_candidate_count=len(summary_signatures)))
    require(sum(signature(candidate) not in excluded for candidate in candidates) >= args.lp_count,
            'Insufficient new candidates after previous-summary exclusions')
    paths = {name:key(getattr(args, name)) for name in ('native','family_audit','initial','initial_phase1','gpu_audit','gpu','gpu_source')}
    if args.validate_only:
        print(json.dumps(dict(status='CP_CROSS_INPUT_VALIDATION_PASS', producer_version='cross1', paths=paths,
              family_association=family_association, previous_summary_reports=previous_summary_reports,
              previous_candidate_artifacts=len(prior), previous_unique_edge_signatures=len(excluded),
              candidate_count=len(candidates), gpu_launches=0, lp_solves=0, output_created=False)), flush=True)
        return
    args.out.mkdir(parents=True)
    outputs = {}

    def output(path, value):
        save(path, value)
        outputs[key(path)] = digest(path)

    output(args.out/'manifest.json', dict(status='CP_MATCHING_SEARCH_MANIFEST', producer_version='cross1', paths=paths,
           family_association=family_association, previous_summary_reports=previous_summary_reports,
           previous_summary_arguments=[key(resolve(path)) for path in args.previous_summary], inputs_sha256=inputs,
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
    summary = dict(status='BOUNDED_CP_MATCHING_SEARCH_FINISHED', producer_version='cross1', paths=paths,
                   family_association=family_association, previous_summary_reports=previous_summary_reports,
                   inputs_sha256=inputs, outputs_sha256=outputs,
                   coarse_candidate_count=len(candidates), refined_candidate_count=len(refined), probes=len(records),
                   baseline_numeric_objective=warm['numeric_objective'], best=usable[0] if usable else None,
                   numerically_optimal_count=sum(r['optimal'] for r in records), numerical_improvement_count=len(improved),
                   numerically_improving_candidates=improved, records=records, elapsed_seconds=time.perf_counter()-started,
                   cp_values_used_as_proof=False, pair_gates_run=0, full_graph_constructed=False, general_nonexistence_proved=False)
    save(args.out/'summary.json', summary)
    print(json.dumps({k:summary[k] for k in ('status','probes','numerical_improvement_count','elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
