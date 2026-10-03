"""Finite discovery controls for the stronger weight5 collision/C4 count; no LP."""
import argparse
from collections import defaultdict
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/theory_20261003_triangle_image_weight5_c4_v2.py'
SPEC = 'acceleration/theory_20261003_triangle_image_weight5_c4_v2_spec.md'
INPUT = 'acceleration/results/20261003_triangle_image_weight5_controls01/actual_graph_fixtures.json'
INPUT_SHA = 'c2c1fe1c6c861b7e85ee8b56a5f999651b243af4600efd69149410f0943aa2fd'
NOTE = 'docs/CANDIDATE_20261003_TRIANGLE_IMAGE_WEIGHT5_COLLISION_C4_V1.md'
NOTE_SHA = '88f0372d495e43b62971544f743c1e9e5a517c62fa6780ebc2b9b0ef2874dca8'
PROOF = 'acceleration/audit_20261003_triangle_image_weight5_c4_v1.md'
PROOF_SHA = 'bdc99b2f6a2bf92f9e322616227c4be26db7d57b08ccbcfd9353fbf76260ce12'
CAL = 'acceleration/results/20261003_independent_review/weight5_c4_calibration01/summary.json'
CAL_SHA = 'de1cde6369b81961c7c658a4ce1ffa41413fdc7d66d3fcccea6c4c57b24881c9'
OLD = 'acceleration/results/20261003_independent_review/weight5_full02/summary.json'
OLD_SHA = 'dedb5c3affcfd0edb98a1d97ebdc973290b53b67ecbb76f3d78135b2bea688f2'
INVERSE_PROOF = 'acceleration/audit_20261003_triangle_image_weight5_v1_proof.md'
INVERSE_PROOF_SHA = '8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee'


class InvalidControl(ValueError):
    pass


def need(ok, stage):
    if not ok:
        raise InvalidControl(stage)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def adjacency(n, edges):
    need(type(n) is int and n > 0 and type(edges) is list, 'GRAPH_LITERAL_DOMAIN')
    need(all(type(e) is list and len(e) == 2 and all(type(v) is int for v in e)
             and 0 <= e[0] < e[1] < n for e in edges), 'GRAPH_LITERAL_DOMAIN')
    need(len({tuple(e) for e in edges}) == len(edges), 'GRAPH_DUPLICATE_EDGE')
    rows = [set() for _ in range(n)]
    for u, v in edges:
        rows[u].add(v)
        rows[v].add(u)
    need(all(len(rows[u] & rows[v]) == 1 for u, v in edges), 'EDGE_CN1_PREMISE')
    return rows


def support(triangles):
    mask = 0
    for t in triangles:
        for v in t:
            mask ^= 1 << v
    return [v for v in range(mask.bit_length()) if mask >> v & 1]


def cycle_matchings(rows, q):
    a, b, c, d = q
    choices = [((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))]
    return sorted(m for m in choices if all(v in rows[u] for u, v in m))


def map_double(rows, word, preimages):
    need(len(preimages) == 2 and len(word) == 5, 'DOUBLE_FIBER_DOMAIN')
    isolated = [v for v in word if not (rows[v] & set(word))]
    need(len(isolated) == 1, 'DOUBLE_UNIQUE_ISOLATED')
    r = isolated[0]
    q = sorted(v for v in word if v != r)
    need(all(len(rows[v] & set(q)) == 2 for v in q), 'DOUBLE_INDUCED_C4')
    matchings = cycle_matchings(rows, q)
    need(len(matchings) == 2, 'DOUBLE_TWO_MATCHINGS')
    matching = matchings[0]
    completed = [rows[u] & rows[v] for u, v in matching]
    need(all(len(s) == 1 for s in completed), 'CANONICAL_EDGE_COMPLETIONS')
    p, t = [next(iter(s)) for s in completed]
    need(p != t and p not in q and t not in q and t in rows[p], 'CANONICAL_CENTRAL_EDGE')
    need(rows[p] & rows[t] == {r}, 'CANONICAL_CENTRAL_COMPLETION')
    recovered = sorted([sorted([*matching[0], p]), sorted([*matching[1], t]), sorted([p, t, r])])
    need(recovered in preimages, 'CANONICAL_PATH_RECOVERY')
    return dict(support=word, isolated_vertex=r, cycle_vertices=q,
                canonical_matching=[list(e) for e in matching], canonical_edge_completions=[p, t],
                central_edge=sorted([p, t]), central_completion=r,
                canonical_path_triangles=recovered, two_path_triangle_sets=preimages)


def produce(label, n, edges):
    rows = adjacency(n, edges)
    triangles = [tuple(t) for t in combinations(range(n), 3)
                 if all(v in rows[u] for u, v in combinations(t, 2))]
    incidence = [sum(v in t for t in triangles) for v in range(n)]
    raw, paths = [], []
    fibers = defaultdict(list)
    for indices in combinations(range(len(triangles)), 3):
        ts = [set(triangles[i]) for i in indices]
        intersections = [len(ts[i] & ts[j]) for i, j in [(0, 1), (0, 2), (1, 2)]]
        degrees = [intersections[0] + intersections[1], intersections[0] + intersections[2], intersections[1] + intersections[2]]
        is_path = sorted(degrees) == [1, 1, 2] and sorted(intersections) == [0, 1, 1]
        word = support(ts)
        record = dict(triangle_indices=list(indices), intersection_sizes=intersections, support=word, is_path=is_path)
        raw.append(record)
        if is_path:
            need(len(word) == 5, 'PATH_WEIGHT5')
            chosen = sorted([list(triangles[i]) for i in indices])
            paths.append(record)
            fibers[tuple(word)].append(chosen)
    formula = sum((incidence[p] - 1) * (incidence[q] - 1) for t in triangles for p, q in combinations(t, 2))
    need(formula == len(paths), 'COMPLETE_PATH_FORMULA')
    raw_fibers = [dict(support=list(word), path_triangle_sets=sorted(records), multiplicity=len(records))
                  for word, records in sorted(fibers.items())]
    need(all(row['multiplicity'] in [1, 2] for row in raw_fibers), 'AT_MOST_TWO_PATH_PREIMAGES')
    cycles = [list(q) for q in combinations(range(n), 4) if all(len(rows[v] & set(q)) == 2 for v in q)]
    cycle_records = [dict(vertices=q, induced_edges=[list(e) for e in combinations(q, 2) if e[1] in rows[e[0]]],
                          perfect_matchings=[[list(e) for e in m] for m in cycle_matchings(rows, q)]) for q in cycles]
    doubles = [map_double(rows, f['support'], f['path_triangle_sets']) for f in raw_fibers if f['multiplicity'] == 2]
    need(len({tuple(f['cycle_vertices']) for f in doubles}) == len(doubles), 'C4_COLLISION_MAP_INJECTION')
    need(all(f['cycle_vertices'] in cycles for f in doubles), 'C4_MAP_IMAGE_CONTAINED')
    need(len(fibers) == len(paths) - len(doubles), 'PATH_MINUS_DOUBLE_WORD_IDENTITY')
    image_records = [dict(coefficient_mask=mask, support=support([t for i, t in enumerate(triangles) if mask >> i & 1]))
                     for mask in range(1 << len(triangles))]
    image = sorted({tuple(row['support']) for row in image_records})
    words5 = [list(word) for word in image if len(word) == 5]
    lower = max((len(paths) + 1) // 2, len(paths) - len(cycles))
    need(len(words5) >= len(fibers) >= lower, 'STRONG_PATH_WORD_LOWER_BOUND')
    return dict(schema='TRIANGLE_IMAGE_WEIGHT5_C4_COLLISION_FIXTURE_V1', label=label, vertices=n, edges=edges,
                actual_triangles=[list(t) for t in triangles], vertex_triangle_counts=incidence,
                all_triangle_triples=raw, path_records=paths, support_fibers=raw_fibers,
                induced_c4_records=cycle_records, double_fiber_cycle_map=doubles,
                path_count=len(paths), irregular_path_formula=formula, cycle_count=len(cycles),
                double_fiber_count=len(doubles), distinct_path_words=len(fibers),
                old_half_path_lower=(len(paths) + 1) // 2, subtracted_cycle_lower=len(paths) - len(cycles),
                strengthened_lower=lower, complete_small_image_records=image_records,
                complete_small_image_weight5_words=words5)


def verify_fixture(row):
    correct = produce(row['label'], row['vertices'], row['edges'])
    need(row['actual_triangles'] == correct['actual_triangles'], 'RAW_ACTUAL_TRIANGLES')
    need(row['all_triangle_triples'] == correct['all_triangle_triples'], 'RAW_COMPLETE_TRIPLES')
    need(row['path_records'] == correct['path_records'], 'RAW_COMPLETE_PATHS')
    need(row['support_fibers'] == correct['support_fibers'], 'RAW_COMPLETE_FIBERS')
    need(row['induced_c4_records'] == correct['induced_c4_records'], 'RAW_COMPLETE_C4S')
    maps = row['double_fiber_cycle_map']
    need(all(all(type(v) is int for v in m['support']) for m in maps), 'RAW_MAP_INTEGER_SUPPORT')
    need(len({tuple(m['cycle_vertices']) for m in maps}) == len(maps), 'RAW_MAP_INJECTION')
    need(maps == correct['double_fiber_cycle_map'], 'RAW_EXACT_COLLISION_MAP')
    for key in ['path_count', 'cycle_count', 'double_fiber_count', 'distinct_path_words', 'strengthened_lower']:
        need(type(row[key]) is int and row[key] == correct[key], 'RAW_EXACT_COUNTS')
    need(row['complete_small_image_records'] == correct['complete_small_image_records']
         and row['complete_small_image_weight5_words'] == correct['complete_small_image_weight5_words'], 'RAW_COMPLETE_IMAGE')


def target_row():
    n, k, r = 99, 14, 7
    triangles = n * k // 6
    paths, nonedges = triangles * 3 * (r - 1) ** 2, n * (n - 1 - k) // 2
    cycles = nonedges // 2
    lower = paths - cycles
    rhs = math.comb(n, 5) - lower
    coefficients = [sum((-1) ** s * math.comb(w, s) * math.comb(n - w, 5 - s)
                        for s in range(max(0, 5 - (n - w)), min(5, w) + 1)) for w in range(n + 1)]
    pairs = [[Fraction(lower - coefficients[w], rhs).numerator, Fraction(lower - coefficients[w], rhs).denominator]
             for w in range(1, n + 1)]
    return dict(schema='TRIANGLE_IMAGE_WEIGHT5_C4_TARGET_CHARACTER_V1', length=n, triangle_incidence_degree=r,
                actual_triangle_count_conditional=triangles, unordered_paths=paths, unordered_nonedges=nonedges,
                induced_c4_count=cycles, image_weight5_lower=lower, degree=5,
                krawtchouk_by_weight0to99=coefficients, shifted_rhs=rhs,
                normalized_coefficient_pairs_by_weight1to99=pairs, target_resolution='NONE')


def verify_target(row):
    correct = target_row()
    need(row['induced_c4_count'] == correct['induced_c4_count'], 'TARGET_C4_DOUBLECOUNT')
    need(row['image_weight5_lower'] == correct['image_weight5_lower'], 'TARGET_COLLISION_SUBTRACTION')
    need(row['shifted_rhs'] == correct['shifted_rhs'], 'TARGET_CHARACTER_ZERO_WORD')
    need(all(type(v) is int for v in row['krawtchouk_by_weight0to99'])
         and row['krawtchouk_by_weight0to99'] == correct['krawtchouk_by_weight0to99']
         and row['normalized_coefficient_pairs_by_weight1to99'] == correct['normalized_coefficient_pairs_by_weight1to99'], 'TARGET_ALL_EXACT_COEFFICIENTS')


def reject(call, expected):
    try:
        call()
    except InvalidControl as error:
        need(str(error) == expected, 'PRECISE_NEGATIVE_STAGE')
        return expected
    raise InvalidControl('NEGATIVE_CONTROL_ACCEPTED')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seconds', type=float, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--source-sha256', required=True)
    p.add_argument('--protocol-sha256', required=True)
    a = p.parse_args()
    deadline = CommandDeadline(a.seconds, allocation_reason='Seven exact finite fixtures and changed C4 collision maps plus one relabelled positive control; no LP;10seconds save reserve')
    out = a.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_WORKSPACE_OUTPUT')
    out.mkdir(parents=True)
    pins = {SOURCE: a.source_sha256, SPEC: a.protocol_sha256, INPUT: INPUT_SHA, NOTE: NOTE_SHA,
            PROOF: PROOF_SHA, CAL: CAL_SHA, OLD: OLD_SHA, INVERSE_PROOF: INVERSE_PROOF_SHA}
    pins.update({
        'acceleration/theory_20261003_triangle_image_weight5_c4_v1.py': 'f9203c6c1aeab51849a7511c918cfbd97e2c9348883ddaf3450e058562fde2d0',
        'acceleration/theory_20261003_triangle_image_weight5_c4_v1_spec.md': '4832b3c40f8e5f9d9cb34fa4f9da808064df86d5b5a0b5d5a803217b415dd7ee',
        'acceleration/results/20261003_triangle_image_weight5_c4_controls01/failure.json': 'c6ce45e1872d3058feaae794fe210bded6e13ce231d4d639110200b5d9d33074',
        'acceleration/results/20261003_triangle_image_weight5_c4_controls_supervision01/summary.json': '0f904489f8feb6b8d6d91356af25b40f0edd144aeb9648763311180ab55e7253',
        'acceleration/results/20261003_triangle_image_weight5_c4_controls_supervision02/summary.json': '02518942aac63ab6f242cc7a342216923b24131f3bae1a14b3f0e50100d3e08d'
    })
    records, negatives = [], []
    protected = {path: sha(ROOT / path) for path in ['CLAIMS.yaml', '.git/index']}
    try:
        for path in ['pyproject.toml', 'uv.lock', 'acceleration/command_deadline.py', 'acceleration/run_compute_command.py', 'docs/COMPUTE_POLICY.md', 'acceleration/compute_policy.json']:
            pins[path] = sha(ROOT / path)
        need(all(sha(ROOT / path) == expected for path, expected in pins.items()), 'EXACT_SOURCE_PROTOCOL_AND_PRIOR_IDENTITIES')
        cal = json.loads((ROOT / CAL).read_bytes())
        need(cal['status'] == 'INDEPENDENT_WEIGHT5_C4_COLLISION_CHECKER_V3_CALIBRATION_PASS' and cal['producer_outputs_checked'] is False,
             'PREOUTPUT_CHANGED_CHECKER_CALIBRATION')
        inputs = json.loads((ROOT / INPUT).read_bytes())
        need([r['label'] for r in inputs] == ['single_triangle', 'friendship7', 'one_intersection_plus_disjoint', 'loose_chain3', 'three_disjoint', 'loose_cycle4', 'rook9'], 'FROZEN_SEVEN_FIXTURE_SELECTION')
        for index, old in enumerate(inputs):
            need(deadline.status()['remaining_seconds'] > 10, 'SERIALIZATION_RESERVE')
            row = produce(old['label'], old['vertices'], old['edges'])
            verify_fixture(row)
            records.append(row)
            save(out / f'fixture_{index:02d}.json', row)
        rook = records[-1]
        need([rook[k] for k in ['path_count', 'cycle_count', 'double_fiber_count', 'distinct_path_words']] == [18, 9, 9, 9], 'ROOK_SATURATION')
        need(records[3]['path_count'] == 1 and records[3]['cycle_count'] == 0, 'CHAIN_SATURATION')
        need(records[5]['cycle_count'] > records[5]['double_fiber_count'], 'COLLISION_MAP_NOT_SURJECTIVE')
        permutation = [1, 0, 2, 3, 4, 5, 6, 7, 8]
        perm_edges = sorted([sorted([permutation[u], permutation[v]]) for u, v in rook['edges']])
        relabelled = produce('rook9_transposition01', 9, perm_edges)
        verify_fixture(relabelled)
        transform = lambda values: sorted(permutation[v] for v in values)
        need(sorted(transform(m['support']) for m in rook['double_fiber_cycle_map']) == sorted(m['support'] for m in relabelled['double_fiber_cycle_map'])
             and sorted(transform(m['cycle_vertices']) for m in rook['double_fiber_cycle_map']) == sorted(m['cycle_vertices'] for m in relabelled['double_fiber_cycle_map']), 'COUNT_PRESERVING_RELABEL_EQUIVARIANCE')
        save(out / 'permutation_control.json', dict(schema='WEIGHT5_C4_RELABEL_CONTROL_V1', vertex_permutation=permutation, relabelled_fixture=relabelled,
                                                  support_cycle_map_equivariance_checked=True, original_label='rook9'))
        cases = []
        def mutation(label, stage, change):
            raw = copy.deepcopy(rook)
            # Detach this controlled branch: deepcopy otherwise preserves fiber/map aliases.
            raw['double_fiber_cycle_map'] = copy.deepcopy(raw['double_fiber_cycle_map'])
            change(raw)
            cases.append((label, stage, raw, verify_fixture))
        mutation('missing_cycle', 'RAW_COMPLETE_C4S', lambda x: x['induced_c4_records'].pop())
        mutation('missing_collision_map', 'RAW_EXACT_COLLISION_MAP', lambda x: x['double_fiber_cycle_map'].pop())
        mutation('wrong_isolated', 'RAW_EXACT_COLLISION_MAP', lambda x: x['double_fiber_cycle_map'][0].update(isolated_vertex=x['double_fiber_cycle_map'][0]['cycle_vertices'][0]))
        mutation('wrong_completion', 'RAW_EXACT_COLLISION_MAP', lambda x: x['double_fiber_cycle_map'][0]['canonical_edge_completions'].__setitem__(0, 99))
        mutation('boolean_support', 'RAW_MAP_INTEGER_SUPPORT', lambda x: x['double_fiber_cycle_map'][0]['support'].__setitem__(0, True))
        mutation('count_preserving_duplicate_cycle_map', 'RAW_MAP_INJECTION', lambda x: x['double_fiber_cycle_map'].__setitem__(1, copy.deepcopy(x['double_fiber_cycle_map'][0])))
        mutation('count_preserving_matching_permutation', 'RAW_EXACT_COLLISION_MAP', lambda x: x['double_fiber_cycle_map'][0].update(canonical_matching=copy.deepcopy(x['double_fiber_cycle_map'][1]['canonical_matching'])))
        mutation('wrong_double_count', 'RAW_EXACT_COUNTS', lambda x: x.update(double_fiber_count=8))
        mutation('false_path_injection', 'RAW_EXACT_COUNTS', lambda x: x.update(distinct_path_words=18))
        mutation('overstated_word_lower', 'RAW_EXACT_COUNTS', lambda x: x.update(strengthened_lower=10))
        mutation('missing_path', 'RAW_COMPLETE_PATHS', lambda x: x['path_records'].pop())
        mutation('changed_image', 'RAW_COMPLETE_IMAGE', lambda x: x['complete_small_image_weight5_words'].pop())
        target = target_row()
        need([target[k] for k in ['unordered_paths', 'induced_c4_count', 'image_weight5_lower', 'shifted_rhs']] == [24948, 2079, 22869, 71500275], 'EXACT_TARGET_CONSTANTS')
        verify_target(target)
        for label, stage, key, value in [('wrong_target_c4','TARGET_C4_DOUBLECOUNT','induced_c4_count',2078), ('wrong_target_lower','TARGET_COLLISION_SUBTRACTION','image_weight5_lower',22870), ('omitted_zero_word_constant','TARGET_CHARACTER_ZERO_WORD','shifted_rhs',71500274)]:
            raw = copy.deepcopy(target)
            raw[key] = value
            cases.append((label, stage, raw, verify_target))
        raw = copy.deepcopy(target)
        raw['krawtchouk_by_weight0to99'][36] += 1
        cases.append(('changed_exact_coefficient', 'TARGET_ALL_EXACT_COEFFICIENTS', raw, verify_target))
        for label, stage, raw, checker in cases:
            need(deadline.status()['remaining_seconds'] > 10, 'SERIALIZATION_RESERVE')
            save(out / (label + '.json'), raw)
            observed = reject(lambda raw=raw, checker=checker: checker(raw), stage)
            negatives.append(dict(case=label, raw_path=label+'.json', expected_stage=stage, observed_stage=observed))
        k7_edges = [list(e) for e in combinations(range(7), 2)]
        stage = reject(lambda: adjacency(7, k7_edges), 'EDGE_CN1_PREMISE')
        negatives.append(dict(case='k7_missing_lambda', expected_stage=stage, observed_stage=stage))
        twice_rook_edges = rook['edges'] + [[u+9, v+9] for u, v in rook['edges']]
        twice_rows = adjacency(18, twice_rook_edges)
        stage = reject(lambda: need(all(len(twice_rows[u] & twice_rows[v]) == 2 for u, v in combinations(range(18), 2) if v not in twice_rows[u]), 'NONEDGE_CN2_PREMISE'), 'NONEDGE_CN2_PREMISE')
        negatives.append(dict(case='two_rooks_missing_mu2', expected_stage=stage, observed_stage=stage))
        save(out / 'missing_premises.json', dict(k7=dict(vertices=7, edges=k7_edges), two_rooks=dict(vertices=18, edges=twice_rook_edges)))
        save(out / 'actual_graph_fixtures.json', records)
        save(out / 'strict_controls.json', negatives)
        save(out / 'target_character_row.json', target)
        need(protected == {path: sha(ROOT / path) for path in protected}, 'PROTECTED_STATE_CHANGED')
        for path in out.iterdir():
            if path.is_file():
                pins[path.relative_to(ROOT).as_posix()] = sha(path)
        save(out / 'summary.json', dict(status='AUTHOR_WEIGHT5_C4_COLLISION_CONTROLS_PASS_PENDING_INDEPENDENT_RAW_AUDIT',
             timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/structural', implementation_version=2, source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
             source_commit_limitation='New separately pinned working source/spec; not asserted committed in context source commit.',
             command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_outputs_sha256=dict(sorted(pins.items())),
             complete_original_fixtures=7, original_triangle_triples=sum(len(r['all_triangle_triples']) for r in records), original_paths=sum(r['path_count'] for r in records),
             original_distinct_support_words=sum(r['distinct_path_words'] for r in records), original_induced_cycles=sum(r['cycle_count'] for r in records), original_double_fibers=sum(r['double_fiber_count'] for r in records),
             original_small_image_coefficient_masks=sum(len(r['complete_small_image_records']) for r in records), positive_relabelled_fixtures=1,
             strict_negative_controls=len(negatives), complete_target_degree5_character_coefficients=100,
             target_unordered_paths=24948, target_induced_c4_count=2079, target_weight5_lower_count=22869, target_character_rhs=71500275,
             mathematical_status='CANDIDATE_PENDING_INDEPENDENT_NEW_RAW_CHECK', target_resolution='NONE', numerical_solver_invocations=0,
             graph_exclusions=0, rank_bound_claimed=False, independent_approval=False,
             shared_components=['Raw seven adjacency fixture identities reused from independently checked prior N5 artifacts; all triangles/trios/path fibers/C4 maps rebuilt without producer/checker imports.', 'Python exact integers/Fraction/sets, JSON/SHA and common deadline/runtime.'],
             historical_protected_execution_state=protected, deadline=deadline.status()))
        print(json.dumps(dict(status='AUTHOR_WEIGHT5_C4_COLLISION_CONTROLS_PASS_PENDING_INDEPENDENT_RAW_AUDIT', negative_controls=len(negatives), target_resolution='NONE')))
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), inputs_sha256=pins, completed_fixtures=len(records), completed_negative_controls=len(negatives),
                                      outputs_preserved=True, restart='No automatic retry; preserve exact source/artifacts/receipt and seek separate new invocation approval.', deadline=deadline.status()))
        raise


if __name__ == '__main__':
    main()
