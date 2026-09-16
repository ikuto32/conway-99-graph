"""Atomic-cycle global-defect search with final complete-star pair arc consistency.

Rust enumerates legal atomic three/four-edge alternating matching cycles. CUDA evaluates the defect at the current
fractional disjoint-edge vector. HiGHS then optimizes that vector for selected
proposals. Accepted proposals must also pass complete-star exact pair arc
consistency in the native checker. Only the simultaneous final partial graph
is required to satisfy the caps; no intermediate swap path is assumed. These are necessary conditions only.
Every merit is numerical; neither a positive nor zero merit is an
exact infeasibility/feasibility certificate or a Conway graph.
"""
import argparse
import json
from math import isfinite
from pathlib import Path
import random
import subprocess
import time

from audit_certificate import full_graph, require
from guided_overlap import digest, write_input, invoke
from prepare import path_key
from phase1_probe_ipm import solve_edges_with_basis

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, data):
    """Compact new records; previous hash-bound global pilot is unchanged."""
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, separators=(',', ':'), allow_nan=False)+'\n', encoding='utf-8')
    temporary.replace(path)


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
    parser.add_argument('--cycle-size', choices=('3','4','both'), default='3')
    parser.add_argument('--lp-best', type=int, default=2)
    parser.add_argument('--lp-diverse', type=int, default=4)
    parser.add_argument('--cached-best', type=int, default=2)
    parser.add_argument('--lp-random', type=int, default=2)
    parser.add_argument('--seconds-per-lp', type=float, default=30)
    parser.add_argument('--seed', type=int, default=20260918)
    args = parser.parse_args()
    require(0 < args.iterations <= 1000, 'Invalid finite search budget')
    require(0 < args.lp_best <= 100 and 0 <= args.lp_random <= 100
            and 0 <= args.lp_diverse <= 100 and 0 <= args.cached_best <= 100,
            'Invalid LP selection budget')
    require(isfinite(args.seconds_per_lp) and args.seconds_per_lp > 0, 'Invalid LP time budget')
    require(not args.out.exists(), 'Preserve previous search output')
    args.out.mkdir(parents=True)
    scratch = args.out/'work'
    scratch.mkdir()
    for name in ('proposals', 'probes', 'local'):
        (args.out/name).mkdir()
    native = ROOT/'acceleration/build/overlap_cycle_neighbors.exe'
    gpu = ROOT/'acceleration/build/overlap_phase_gpu.exe'
    stars = ROOT/'acceleration/build/star_domains.exe'
    pairs = ROOT/'acceleration/build/pair_domains.exe'
    sources = [args.initial, Path(__file__), native, gpu, stars, pairs,
               ROOT/'acceleration/guided_global_overlap.py',
               ROOT/'acceleration/guided_coupled_overlap.py',
               ROOT/'acceleration/guided_two_trade_overlap.py',
               ROOT/'acceleration/star_domains.rs', ROOT/'acceleration/pair_domains.rs',
               ROOT/'acceleration/guided_overlap.py', ROOT/'acceleration/prepare.py',
               ROOT/'acceleration/audit_certificate.py', ROOT/'acceleration/linear_probe.py',
               ROOT/'acceleration/phase1_probe_ipm.py', ROOT/'acceleration/overlap_cycle_neighbors.rs',
               ROOT/'acceleration/overlap_phase_gpu.cu']
    bindings = {path_key(path): digest(path) for path in sources}
    manifest = dict(inputs_sha256=bindings, seed=args.seed, iterations=args.iterations,
                    cycle_size=args.cycle_size, lp_best=args.lp_best, lp_diverse=args.lp_diverse,
                    lp_random=args.lp_random, cached_best=args.cached_best,
                    seconds_per_lp=args.seconds_per_lp,
                    scope='Bounded global-defect search over completely enumerated atomic-cycle subfamilies, with native pair AC at accepted endpoints. No intermediate graph is asserted. LP shortlist is nonexhaustive; cached native failures only guide selection. Caps are unavailable checks, never exclusions. No full graph or exhaustive coverage.')
    write_json(args.out/'manifest.json', manifest)
    initial = [list(e) for e in signature(json.loads(args.initial.read_bytes())['overlap_edges_outer_zero_based'])]
    full_graph({'overlap_edges_outer_zero_based': initial})
    generator = random.Random(args.seed)
    evaluated, numeric_unknown, cache_hits = 0, 0, 0
    cache = {}
    local_cache = {}

    def local_check(edges, name):
        key = signature(edges)
        if key in local_cache:
            return local_cache[key]
        prefix = args.out/'local'/name
        candidate_input = prefix.with_name(prefix.name+'_candidate.txt')
        star_output = prefix.with_name(prefix.name+'_stars.json')
        write_input(candidate_input, [edges])
        domains = invoke(stars, candidate_input, star_output, 30, 2000000, 20000)
        report = {'passed': False, 'star_status': domains['status'],
                  'candidate_input': path_key(candidate_input), 'candidate_input_sha256': digest(candidate_input),
                  'stars_path': path_key(star_output), 'stars_sha256': digest(star_output)}
        if domains['status'] == 'COMPLETE_DOMAINS_RECIPROCITY_ARC_CONSISTENT_NONEMPTY':
            domain_input = prefix.with_name(prefix.name+'_domains.txt')
            pair_output = prefix.with_name(prefix.name+'_pairs.json')
            domain_input.write_text('C99DOMAINS1 84\n'+''.join(str(len(row['domain_masks_hex']))+' '+
                ' '.join(row['domain_masks_hex'])+'\n' for row in domains['domains']), encoding='ascii')
            process = subprocess.run([str(pairs), str(candidate_input), str(domain_input), str(pair_output),
                                      '30', '500000000'], text=True, capture_output=True, timeout=40)
            require(process.returncode == 0, f'Native pair check failed: {process.stderr}')
            pair = json.loads(pair_output.read_bytes())
            report.update(pair_status=pair['status'], pair_path=path_key(pair_output), pair_sha256=digest(pair_output),
                          domain_input=path_key(domain_input), domain_input_sha256=digest(domain_input),
                          passed=pair['status'] == 'EXACT_PAIR_DOMAIN_ARC_CONSISTENT_NONEMPTY')
        local_cache[key] = report
        return report

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
    initial_local = local_check(initial, 'initial')
    require(initial_local['passed'], 'Initial candidate lacks a completed nonempty native pair-AC check')
    best = current
    visited = {signature(initial)}
    records, snapshots = [], [initial]
    proposal_evaluations = 0
    proposal_occurrences = 0
    reused_proposal_batches = 0
    proposal_cache = {}
    stop = 'ITERATION_LIMIT'
    for iteration in range(args.iterations):
        if best['objective'] <= 1e-8:
            stop = 'NUMERICAL_ZERO_DEFECT_REQUIRES_EXACT_VALIDATION'
            break
        current_key = signature(current['candidate'])
        reused = current_key in proposal_cache
        if reused:
            proposed, proposal_path, score_path, scored, option_keys = proposal_cache[current_key]
            reused_proposal_batches += 1
        else:
            neighbor_input, neighbor_output = scratch/'neighbor_input.txt', scratch/'neighbor_output.json'
            write_input(neighbor_input, [current['candidate']])
            proposed = invoke(native, neighbor_input, neighbor_output, args.cycle_size)
            proposal_path = args.out/'proposals'/f'iteration_{iteration:04d}.json'
            write_json(proposal_path, proposed)
            options = proposed['overlap_candidates']
            option_keys = [signature(edges) for edges in options]
            require(proposed['status'] == 'COMPLETE_ATOMIC_CYCLE_SUBFAMILY_ENUMERATION'
                    and len(proposed['moves']) == len(options)
                    and all(len(move['removed']) == len(move['added']) == move['cycle_size']
                            and move['cycle_size'] in (3,4) for move in proposed['moves']),
                    'Invalid atomic-cycle proposal batch')
            proposal_evaluations += len(options)
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
            # Accepted states are never revisited: only the current batch needs memory.
            proposal_cache = {current_key: (proposed, proposal_path, score_path, scored, option_keys)}
        options = proposed['overlap_candidates']
        proposal_occurrences += len(options)
        if not options:
            stop = 'NO_LEGAL_ATOMIC_CYCLES_IN_SELECTED_SUBFAMILY'
            break
        eligible = [i for i, key in enumerate(option_keys) if key not in visited]
        ordered = sorted((scored[i+1]['total_violation'], i) for i in eligible
                         if option_keys[i] not in cache)
        selected_fresh = [i for _,i in ordered[:args.lp_best]]
        def bucket(i):
            move = proposed['moves'][i]
            return move['root_group'], move['matching_class'], move['cycle_size']
        represented = {bucket(i) for i in selected_fresh}
        buckets = {}
        for _, i in ordered:
            key = bucket(i)
            if key not in represented and key not in buckets:
                buckets[key] = i
        keys = sorted(buckets)
        generator.shuffle(keys)
        selected_fresh += [buckets[key] for key in keys[:args.lp_diverse]]
        unused = [i for _,i in ordered if i not in selected_fresh]
        selected_fresh += generator.sample(unused, min(args.lp_random, len(unused)))
        cached_options = []
        for i in eligible:
            key = option_keys[i]
            saved = cache.get(key)
            local = local_cache.get(key)
            if saved and saved['objective'] <= current['objective'] + 0.5 and (local is None or local['passed']):
                cached_options.append((saved['objective'], i))
        selected_cached = [i for _,i in sorted(cached_options)[:args.cached_best]]
        selected = selected_fresh + selected_cached
        if not selected:
            stop = 'NO_UNPROBED_OR_ELIGIBLE_CACHED_CYCLE_CANDIDATES'
            break
        trials = [probe(options[i], f'iteration_{iteration:04d}_choice_{i:04d}', current['basis']) for i in selected]
        usable = [(trial['objective'], generator.random(), j) for j, trial in enumerate(trials) if trial['usable']]
        if not usable:
            stop = 'ALL_SELECTED_PHASE1_PROBES_INCOMPLETE'
            break
        local_checks = []
        trial_index = min(usable)[2]
        compatible = False
        for value, _, j in sorted(usable):
            if value > current['objective'] + 0.5:
                break
            checked = local_check(trials[j]['candidate'], f'iteration_{iteration:04d}_choice_{selected[j]:04d}')
            local_checks.append({'proposal_index': selected[j], **checked})
            if checked['passed']:
                trial_index = j
                compatible = True
                break
        choice = selected[trial_index]
        chosen = trials[trial_index]
        delta = chosen['objective']-current['objective']
        accepted = compatible and (delta <= 1e-7 or (delta <= 0.5 and generator.random() < 0.1))
        record = dict(iteration=iteration, proposal_batch_reused=reused,
                      proposal_path=path_key(proposal_path), proposal_sha256=digest(proposal_path),
                      gpu_scores_path=path_key(score_path), gpu_scores_sha256=digest(score_path),
                      previous_probe=lightweight(current), selected_proposal_indices=selected,
                      fresh_selected_proposal_indices=selected_fresh,
                      cached_selected_proposal_indices=selected_cached,
                      phase1_trials=[lightweight(trial) for trial in trials], chosen_index=choice,
                      native_local_checks=local_checks, chosen_passes_native_pair_ac=compatible,
                      chosen_probe=lightweight(chosen), accepted=accepted,
                      move=proposed['moves'][choice])
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
                       accepted_moves=len(snapshots)-1,
                       accepted_edge_replacements=sum(row['move']['cycle_size'] for row in records if row['accepted']),
                       proposal_occurrences=proposal_occurrences, cached_proposal_batches=reused_proposal_batches,
                       records=records, overlap_candidates=snapshots,
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
    summary = dict(status='BOUNDED_ATOMIC_CYCLE_COUPLED_SEARCH_FINISHED', stop_reason=stop,
                   best_numeric_objective=best['objective'], phase1_evaluations=evaluated,
                   cached_phase1_lookups=cache_hits,
                   numeric_unknown_probes=numeric_unknown, proposal_evaluations=proposal_evaluations,
                   accepted_moves=len(snapshots)-1,
                   accepted_edge_replacements=sum(row['move']['cycle_size'] for row in records if row['accepted']),
                   proposal_occurrences=proposal_occurrences, cached_proposal_batches=reused_proposal_batches,
                   records=records, overlap_candidates=snapshots,
                   manifest=manifest, initial_native_pair_ac=initial_local,
                   local_candidates_checked=len(local_cache), elapsed_seconds=time.perf_counter()-started,
                   scope='Numerical global merit and native pair arc consistency are necessary-condition controls only. No full graph or exhaustive coverage; independent audits still required.')
    write_json(args.out/'summary.json', summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('records','overlap_candidates','manifest')}))


if __name__ == '__main__':
    main()
