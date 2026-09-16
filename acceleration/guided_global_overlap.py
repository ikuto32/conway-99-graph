"""Bounded K/X search guided by the global linear completion defect.

Rust proposes legal overlap trades. CUDA evaluates the defect at the current
fractional disjoint-edge vector. HiGHS then optimizes that vector for selected
proposals. Every merit is numerical; neither a positive nor zero merit is an
exact infeasibility/feasibility certificate or a Conway graph.
"""
import argparse
import json
from math import isfinite
from pathlib import Path
import random
import time

from audit_certificate import full_graph, require
from guided_overlap import digest, write_json, write_input, invoke
from prepare import path_key
from phase1_probe_ipm import solve_edges_with_basis

ROOT = Path(__file__).resolve().parents[1]


def signature(edges):
    return tuple(sorted(map(tuple, edges)))


def write_global_input(path, x, candidates):
    require(len(x) == 1680 and all(isfinite(v) and 0 <= v <= 1 for v in x), 'Invalid fractional X vector')
    with path.open('w', encoding='ascii', newline='\n') as stream:
        stream.write(f'C99GLOBAL1 {len(candidates)}\n')
        stream.write(' '.join(format(v, '.17g') for v in x)+'\n')
        for candidate in candidates:
            stream.write(' '.join(str(v) for edge in candidate for v in edge)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--initial', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--iterations', type=int, default=24)
    parser.add_argument('--neighbors', type=int, default=128)
    parser.add_argument('--lp-best', type=int, default=4)
    parser.add_argument('--lp-random', type=int, default=2)
    parser.add_argument('--seconds-per-lp', type=float, default=30)
    parser.add_argument('--seed', type=int, default=20260918)
    args = parser.parse_args()
    require(0 < args.iterations <= 1000 and 0 < args.neighbors <= 1000, 'Invalid finite search budget')
    require(0 < args.lp_best <= args.neighbors and 0 <= args.lp_random <= args.neighbors,
            'Invalid LP selection budget')
    require(isfinite(args.seconds_per_lp) and args.seconds_per_lp > 0, 'Invalid LP time budget')
    require(not args.out.exists(), 'Preserve previous search output')
    args.out.mkdir(parents=True)
    scratch = args.out/'work'
    scratch.mkdir()
    for name in ('proposals', 'probes'):
        (args.out/name).mkdir()
    native = ROOT/'acceleration/build/overlap_neighbors.exe'
    gpu = ROOT/'acceleration/build/overlap_phase_gpu.exe'
    sources = [args.initial, Path(__file__), native, gpu,
               ROOT/'acceleration/guided_overlap.py', ROOT/'acceleration/prepare.py',
               ROOT/'acceleration/audit_certificate.py', ROOT/'acceleration/linear_probe.py',
               ROOT/'acceleration/phase1_probe_ipm.py', ROOT/'acceleration/overlap_neighbors.rs',
               ROOT/'acceleration/overlap_phase_gpu.cu']
    bindings = {path_key(path): digest(path) for path in sources}
    manifest = dict(inputs_sha256=bindings, seed=args.seed, iterations=args.iterations,
                    neighbors=args.neighbors, lp_best=args.lp_best, lp_random=args.lp_random,
                    seconds_per_lp=args.seconds_per_lp,
                    scope='Finite numerical global-defect guided K/X search. No exact completion/exclusion from merit scores.')
    write_json(args.out/'manifest.json', manifest)
    initial = [list(e) for e in signature(json.loads(args.initial.read_bytes())['overlap_edges_outer_zero_based'])]
    full_graph({'overlap_edges_outer_zero_based': initial})
    generator = random.Random(args.seed)
    evaluated, numeric_unknown, cache_hits = 0, 0, 0
    cache = {}

    def probe(edges, name, basis=None):
        nonlocal evaluated, numeric_unknown, cache_hits
        key = signature(edges)
        if key in cache:
            cache_hits += 1
            return cache[key]
        candidate_path = args.out/'probes'/f'{name}_candidate.json'
        output_path = args.out/'probes'/f'{name}_phase1.json'
        write_json(candidate_path, {'overlap_edges_outer_zero_based': edges,
                                  'source_manifest': path_key(args.out/'manifest.json')})
        result, next_basis = solve_edges_with_basis(edges, args.seconds_per_lp, basis)
        result.update(candidate_path=path_key(candidate_path), candidate_sha256=digest(candidate_path))
        write_json(output_path, result)
        evaluated += 1
        value, x = result.get('numeric_objective'), result.get('numeric_edge_values')
        usable = result.get('optimal') is True and value is not None and isfinite(value) and value >= -1e-7
        usable = usable and x is not None and len(x) == 1680 and all(isfinite(v) and 0 <= v <= 1 for v in x)
        if not usable:
            numeric_unknown += 1
        saved = {'candidate': edges, 'candidate_path': path_key(candidate_path),
                'candidate_sha256': digest(candidate_path), 'result_path': path_key(output_path),
                'result_sha256': digest(output_path), 'objective': value, 'usable': usable,
                'data': result, 'basis': next_basis}
        if usable:
            cache[key] = saved
        return saved

    def lightweight(probed):
        return {k:v for k,v in probed.items() if k not in ('candidate','data','basis')}

    started = time.perf_counter()
    current = probe(initial, 'initial')
    require(current['usable'], 'Initial phase-I solve did not finish optimally')
    best = current
    visited = {signature(initial)}
    records, snapshots = [], [initial]
    proposal_evaluations = 0
    stop = 'ITERATION_LIMIT'
    for iteration in range(args.iterations):
        if best['objective'] <= 1e-8:
            stop = 'NUMERICAL_ZERO_DEFECT_REQUIRES_EXACT_VALIDATION'
            break
        neighbor_input, neighbor_output = scratch/'neighbor_input.txt', scratch/'neighbor_output.json'
        write_input(neighbor_input, [current['candidate']])
        trade_seed = generator.getrandbits(64)
        proposed = invoke(native, neighbor_input, neighbor_output, args.neighbors, trade_seed)
        proposal_path = args.out/'proposals'/f'iteration_{iteration:04d}.json'
        write_json(proposal_path, proposed)
        options = proposed['overlap_candidates']
        proposal_evaluations += len(options)
        if not options:
            stop = 'NO_LEGAL_TWO_EDGE_MOVE'
            break
        gpu_input, gpu_output = scratch/'global_input.txt', scratch/'global_scores.json'
        write_global_input(gpu_input, current['data']['numeric_edge_values'], [current['candidate']]+options)
        scores = invoke(gpu, gpu_input, gpu_output)
        require(scores['status'] == 'NUMERICAL_FIXED_X_PHASE1_HEURISTIC', 'Unexpected CUDA status')
        scored = scores['results']
        require(len(scored) == len(options)+1 and [r['candidate_index'] for r in scored] == list(range(len(scored))),
                'CUDA batch count/order mismatch')
        require(all(isfinite(r['total_violation']) and r['total_violation'] >= 0 for r in scored),
                'Invalid CUDA merit')
        require(abs(scored[0]['total_violation']-current['objective']) <= 1e-5*(1+abs(current['objective'])),
                'Current CUDA residual objective differs from optimal phase-I merit')
        score_path = args.out/'proposals'/f'iteration_{iteration:04d}_gpu.json'
        write_json(score_path, scores)
        ordered = sorted((scored[i+1]['total_violation'], i) for i, edges in enumerate(options)
                         if signature(edges) not in visited)
        selected = [i for _,i in ordered[:args.lp_best]]
        unused = [i for _,i in ordered if i not in selected]
        selected += generator.sample(unused, min(args.lp_random, len(unused)))
        if not selected:
            stop = 'SAMPLED_NEIGHBORS_ALREADY_VISITED'
            break
        trials = [probe(options[i], f'iteration_{iteration:04d}_choice_{i:04d}', current['basis']) for i in selected]
        usable = [(trial['objective'], generator.random(), j) for j, trial in enumerate(trials) if trial['usable']]
        if not usable:
            stop = 'ALL_SELECTED_PHASE1_PROBES_INCOMPLETE'
            break
        _, _, trial_index = min(usable)
        choice = selected[trial_index]
        chosen = trials[trial_index]
        delta = chosen['objective']-current['objective']
        accepted = delta <= 1e-7 or (delta <= 0.5 and generator.random() < 0.1)
        record = dict(iteration=iteration, native_sample_seed=trade_seed,
                      proposal_path=path_key(proposal_path), proposal_sha256=digest(proposal_path),
                      gpu_scores_path=path_key(score_path), gpu_scores_sha256=digest(score_path),
                      previous_probe=lightweight(current), selected_proposal_indices=selected,
                      phase1_trials=[lightweight(trial) for trial in trials], chosen_index=choice,
                      chosen_probe=lightweight(chosen), accepted=accepted,
                      removed=proposed['trades'][choice]['removed'], added=proposed['trades'][choice]['added'])
        if accepted:
            full_graph({'overlap_edges_outer_zero_based': chosen['candidate']})
            current = chosen
            visited.add(signature(current['candidate']))
            snapshots.append(current['candidate'])
            if current['objective'] < best['objective']:
                best = current
        records.append(record)
        write_json(args.out/'best_candidate.json', {'overlap_edges_outer_zero_based': best['candidate'],
                   'numeric_phase1_objective': best['objective'], 'phase1_probe': lightweight(best),
                   'source_manifest': path_key(args.out/'manifest.json')})
        write_json(args.out/'best_phase1.json', best['data'])
        summary = dict(status='SEARCH_IN_PROGRESS', best_numeric_objective=best['objective'],
                       current_numeric_objective=current['objective'], phase1_evaluations=evaluated,
                       cached_phase1_lookups=cache_hits,
                       numeric_unknown_probes=numeric_unknown, proposal_evaluations=proposal_evaluations,
                       accepted_moves=len(snapshots)-1, records=records, overlap_candidates=snapshots,
                       manifest=manifest, elapsed_seconds=time.perf_counter()-started)
        write_json(args.out/'summary.json', summary)
        print(json.dumps({k:v for k,v in summary.items() if k not in ('records','overlap_candidates','manifest')}), flush=True)
    if best['objective'] <= 1e-8:
        stop = 'NUMERICAL_ZERO_DEFECT_REQUIRES_EXACT_VALIDATION'
    for source in sources:
        require(bindings[path_key(source)] == digest(source), 'Input/source changed during search')
    write_json(args.out/'best_candidate.json', {'overlap_edges_outer_zero_based': best['candidate'],
               'numeric_phase1_objective': best['objective'], 'phase1_probe': lightweight(best),
               'source_manifest': path_key(args.out/'manifest.json')})
    write_json(args.out/'best_phase1.json', best['data'])
    summary = dict(status='BOUNDED_GLOBAL_DEFECT_SEARCH_FINISHED', stop_reason=stop,
                   best_numeric_objective=best['objective'], phase1_evaluations=evaluated,
                   cached_phase1_lookups=cache_hits,
                   numeric_unknown_probes=numeric_unknown, proposal_evaluations=proposal_evaluations,
                   accepted_moves=len(snapshots)-1, records=records, overlap_candidates=snapshots,
                   manifest=manifest, elapsed_seconds=time.perf_counter()-started,
                   scope='Numerical necessary-relaxation search only. Even a zero objective needs exact feasibility verification and full graph completion.')
    write_json(args.out/'summary.json', summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('records','overlap_candidates','manifest')}))


if __name__ == '__main__':
    main()
