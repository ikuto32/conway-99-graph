"""Evaluate necessary capacity cuts under sampled or complete S7 root relabelings.

The native evaluator supplies all 128 sign swaps for every group permutation.
Raw score shards are temporary; only minima and independently checked witnesses
are retained. Neither native evaluator nor the existing exporter is modified.
"""
import argparse
from collections import Counter
from itertools import combinations, permutations
import json
from pathlib import Path
import random
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from audit_certificate import full_graph, graph_constraint
from prepare import (all_cuts, cut_text, digest, path_key, recorded_path,
                     require, verify_manifest)
from verify_scores import read_candidates, check_tensor


LABELS = [(a, b) for a, b in combinations(range(14), 2) if a//2 != b//2]
LABELS.sort(key=lambda pair: (pair[0]//2, pair[1]//2, pair))
VERTEX_OF = {pair: i for i, pair in enumerate(LABELS)}


def group_image(candidate, permutation):
    vertex_map = [VERTEX_OF[tuple(sorted(2*permutation[s//2]+s%2 for s in pair))]
                  for pair in LABELS]
    require(sorted(vertex_map) == list(range(84)), 'Group map is not a permutation')
    return [sorted((vertex_map[u], vertex_map[v])) for u, v in candidate]


def witness_image(candidate, permutation, mask):
    # Independently compose symbol relabeling and signs in the target groups.
    symbol_map = [2*permutation[s//2] + ((s%2) ^ ((mask >> permutation[s//2]) & 1))
                  for s in range(14)]
    require(sorted(symbol_map) == list(range(14)), 'Symbol map is not bijective')
    result = []
    for u, v in candidate:
        image = []
        for vertex in (u, v):
            pair = tuple(sorted(symbol_map[s] for s in LABELS[vertex]))
            image.append(VERTEX_OF[pair])
        result.append(sorted(image))
    return result


def semantic_score(candidate, cut):
    """Full99 graph constraints, independent of native/bank score expansion."""
    adjacency, unknown = full_graph({'overlap_edges_outer_zero_based': candidate})
    coefficients = dict.fromkeys(unknown, 0)
    rhs = 0
    for u in range(84):
        for symbol in range(14):
            weight = cut['alpha'][u][symbol]
            if weight:
                terms, target = graph_constraint(adjacency, unknown, 'label_quota', [u, symbol])
                rhs += weight*target
                for edge, count in terms.items():
                    coefficients[edge] += weight*count
    for u, v in combinations(range(84), 2):
        weight = cut['beta'][u][v]
        require(type(weight) is int and weight >= 0, 'Pair cap needs nonnegative multiplier')
        if weight:
            terms, target = graph_constraint(adjacency, unknown, 'linear_pair_cap', [u, v])
            rhs += weight*target
            for edge, count in terms.items():
                coefficients[edge] += weight*count
    lower = sum(min(0, value) for value in coefficients.values())
    return {'score': rhs-lower, 'combined_rhs': rhs, 'box_lower_bound': lower}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank', type=Path, required=True, help='Manifest-bound export directory')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--permutations', type=int, default=128, help='1..5040; includes identity')
    parser.add_argument('--seed', type=int, default=20260916)
    parser.add_argument('--batch', type=int, default=512, help='Maximum temporary native candidates per shard')
    parser.add_argument('--gpu', type=Path, default=ROOT/'acceleration/overlap_gpu.exe')
    parser.add_argument('--continue-excluded', action='store_true', help='Compute full orbit minima even after rejection')
    args = parser.parse_args()
    require(not args.out.exists(), 'Output must be new')
    require(1 <= args.permutations <= 5040 and 1 <= args.batch <= 1024, 'Invalid permutation/batch count')
    started = time.perf_counter()
    manifest_path = args.bank/'manifest.json'
    manifest = verify_manifest(manifest_path, args.bank/'candidates.txt')
    certificates = [recorded_path(row['certificate']) for row in manifest['extra_cut_certificates']]
    audits = [recorded_path(row['audit']) for row in manifest['extra_cut_certificates']]
    cuts = all_cuts(certificates, audits)
    require(len(cuts) == manifest['cuts'], 'Wrong cut count')
    require((args.bank/'cuts.txt').read_text(encoding='ascii').split() == cut_text(cuts).split(),
            'Manifest native cut input differs from audited cuts')
    candidates = read_candidates(args.bank/'candidates.txt')
    require(len(candidates) == manifest['candidates'], 'Wrong candidate count')
    all_permutations = list(permutations(range(7)))
    identity = all_permutations.pop(0)
    random.Random(args.seed).shuffle(all_permutations)
    selected = [identity] + all_permutations[:args.permutations-1]
    records = [{'candidate_index': i, 'group_permutations_tested': 0, 'minimum_score': None,
                'cut_minima': [None]*len(cuts), 'identity_minimum': None,
                'excluded': False, 'minimizer': None} for i in range(len(candidates))]
    total_evaluations = 0
    native_elapsed = 0.0
    kernel_elapsed = 0.0
    shards = 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='group-orbit-', dir=args.out.parent) as temporary:
        temporary = Path(temporary)
        pending = []
        native_candidates = temporary/'candidates.txt'
        native_output = temporary/'scores.json'

        def flush():
            nonlocal total_evaluations, native_elapsed, kernel_elapsed, shards
            if not pending:
                return
            with native_candidates.open('w', encoding='ascii', newline='\n') as stream:
                stream.write(f'C99OVERLAPS1 {len(pending)}\n')
                for candidate_index, permutation_index in pending:
                    image = group_image(candidates[candidate_index], selected[permutation_index])
                    stream.write(' '.join(str(v) for edge in image for v in edge)+'\n')
            process = subprocess.run([str(args.gpu.resolve()), str((args.bank/'cuts.txt').resolve()),
                                      str(native_candidates.resolve()), str(native_output.resolve())],
                                     text=True, capture_output=True, check=True)
            result = json.loads(native_output.read_bytes())
            check_tensor(result['scores'], len(pending), len(cuts))
            require(result['evaluations'] == len(pending)*len(cuts)*128 and result['repeats'] == 1,
                    'GPU evaluation count mismatch')
            total_evaluations += result['evaluations']
            native_elapsed += result['elapsed_seconds']
            kernel_elapsed += result['kernel_seconds']
            for (candidate_index, permutation_index), scores in zip(pending, result['scores']):
                record = records[candidate_index]
                record['group_permutations_tested'] += 1
                for cut_index, row in enumerate(scores):
                    value = min(row)
                    if record['cut_minima'][cut_index] is None or value < record['cut_minima'][cut_index]:
                        record['cut_minima'][cut_index] = value
                    if record['minimum_score'] is None or value < record['minimum_score']:
                        record['minimum_score'] = value
                        record['minimizer'] = {'permutation_index': permutation_index,
                                               'group_permutation': list(selected[permutation_index]),
                                               'cut_index': cut_index, 'cut_name': cuts[cut_index]['name'],
                                               'sign_mask': row.index(value)}
                    if permutation_index == 0:
                        if record['identity_minimum'] is None or value < record['identity_minimum']:
                            record['identity_minimum'] = value
                record['excluded'] = record['minimum_score'] < 0
            pending.clear()
            shards += 1

        for permutation_index in range(len(selected)):
            for candidate_index, record in enumerate(records):
                if record['excluded'] and not args.continue_excluded:
                    continue
                pending.append((candidate_index, permutation_index))
                if len(pending) == args.batch:
                    flush()
            # Flush identity immediately so the baseline exclusions are separate.
            if permutation_index == 0:
                flush()
            if (permutation_index+1) % 64 == 0:
                flush()
                print(json.dumps({'permutations_visited': permutation_index+1,
                                  'excluded': sum(r['excluded'] for r in records),
                                  'wall_seconds': time.perf_counter()-started}), flush=True)
        flush()
    checked = 0
    for record in records:
        witness = record['minimizer']
        image = witness_image(candidates[record['candidate_index']], witness['group_permutation'],
                              witness['sign_mask'])
        semantic = semantic_score(image, cuts[witness['cut_index']])
        require(semantic['score'] == record['minimum_score'], 'Independent full99 semantic score mismatch')
        record['semantic_check'] = semantic
        record['new_group_exclusion'] = record['excluded'] and record['identity_minimum'] >= 0
        record['complete_group_sign_orbit'] = record['group_permutations_tested'] == 5040
        checked += 1
    sources = [Path(__file__), args.gpu, ROOT/'acceleration/overlap_gpu.cu',
               ROOT/'acceleration/audit_certificate.py', ROOT/'acceleration/prepare.py',
               ROOT/'acceleration/verify_scores.py', args.bank/'candidates.txt', args.bank/'cuts.txt', manifest_path]
    result = {
        'status': 'S7_SIGN_NECESSARY_CUT_ORBIT_WITH_INDEPENDENT_MINIMUM_WITNESSES_PASS',
        'candidate_count': len(candidates), 'cut_count': len(cuts), 'sign_masks_per_permutation': 128,
        'planned_group_permutations': len(selected), 'full_group_permutations': 5040,
        'full_group_sign_relabelings': 645120, 'selection_seed': args.seed,
        'group_permutations': [list(p) for p in selected],
        'skipped_after_rejection': not args.continue_excluded,
        'identity_excluded': sum(r['identity_minimum'] < 0 for r in records),
        'new_group_exclusions': sum(r['new_group_exclusion'] for r in records),
        'excluded': sum(r['excluded'] for r in records),
        'unexcluded': sum(not r['excluded'] for r in records),
        'independent_full99_semantic_witnesses_checked': checked,
        'evaluations': total_evaluations, 'native_shards': shards,
        'native_transfer_and_kernel_seconds': native_elapsed, 'native_kernel_seconds': kernel_elapsed,
        'wall_seconds': time.perf_counter()-started, 'records': records,
        'inputs_sha256': {path_key(path): digest(path) for path in sources},
        'validity': 'Group permutations and target-group sign swaps preserve root matching, label incidence, and the disjoint unknown-edge domain. Quota equalities allow signed alpha, pair inequalities require beta>=0. Any completion must satisfy RHS-sum(min(0,coefficient))>=0. No fixed compression totals are used.',
        'scope': 'Negative witnesses exactly reject only the corresponding complete overlap assignments. Unexcluded records pass only the recorded sampled relabelings unless complete_group_sign_orbit is true. No completion or global Conway exclusion follows.',
    }
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: value for key, value in result.items() if key not in ('records', 'group_permutations', 'inputs_sha256')}))


if __name__ == '__main__':
    main()
