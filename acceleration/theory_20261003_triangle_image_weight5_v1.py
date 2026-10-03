"""Exact finite author controls for trianglepath weight5 counts; no LP."""
from __future__ import annotations
import argparse
import copy
import hashlib
import itertools
import json
import math
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parent.parent
SOURCE = 'acceleration/theory_20261003_triangle_image_weight5_v1.py'
SPEC = 'acceleration/theory_20261003_triangle_image_weight5_v1_spec.md'
NOTE = 'docs/CANDIDATE_20261003_TRIANGLE_IMAGE_WEIGHT5_V1.md'
NOTE_SHA = 'f175e6803924056cbaee112f2430b010f21277cb5792d1ce104ed9cb6c9f60c4'


class InvalidControl(ValueError):
    pass


def need(condition, stage):
    if not condition:
        raise InvalidControl(stage)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n', encoding='utf8', newline='\n')


def graph(n, edges, scoped=True):
    neighbors = [set() for _ in range(n)]
    need(len({tuple(e) for e in edges}) == len(edges), 'EDGE_DUPLICATE')
    for edge in edges:
        need(len(edge) == 2 and all(type(v) is int for v in edge)
             and 0 <= edge[0] < edge[1] < n, 'EDGE_LITERAL')
        a, b = edge
        neighbors[a].add(b)
        neighbors[b].add(a)
    if scoped:
        need(all(len(neighbors[a] & neighbors[b]) == 1 for a, b in edges), 'SCOPE_EDGE_CN1')
    triangles = [tuple(t) for t in itertools.combinations(range(n), 3)
                 if t[1] in neighbors[t[0]] and t[2] in neighbors[t[0]] and t[2] in neighbors[t[1]]]
    return neighbors, triangles


def edge_union(triangles):
    return [list(edge) for edge in sorted({tuple(sorted(edge)) for t in triangles
                                          for edge in itertools.combinations(t, 2)})]


def xor_support(triangles):
    result = set()
    for triangle in triangles:
        result.symmetric_difference_update(triangle)
    return sorted(result)


def path_inverse(neighbors, triangles, indices):
    ts = [set(triangles[i]) for i in indices]
    intersections = {(a, b): ts[a] & ts[b] for a, b in itertools.combinations(range(3), 2)}
    need(all(len(v) <= 1 for v in intersections.values()), 'PATH_LINEARITY')
    degree = [sum(bool(intersections[tuple(sorted((a, b)))]) for b in range(3) if b != a) for a in range(3)]
    need(sorted(degree) == [1, 1, 2], 'PATH_INTERSECTION_SHAPE')
    middle = degree.index(2)
    ends = [i for i in range(3) if i != middle]
    points = sorted(next(iter(ts[middle] & ts[end])) for end in ends)
    private = sorted(ts[middle] - set(points))
    need(len(private) == 1, 'PATH_CENTRAL_PRIVATE_VERTEX')
    support = xor_support(ts)
    need(len(support) == 5, 'PATH_XOR_WEIGHT')
    induced = [list(edge) for edge in itertools.combinations(support, 2) if edge[1] in neighbors[edge[0]]]
    induced_degree = Counter(v for edge in induced for v in edge)
    isolated = [v for v in support if induced_degree.get(v, 0) == 0]
    need(isolated == private, 'PATH_UNIQUE_ISOLATED_VERTEX')
    degs = sorted(induced_degree.get(v, 0) for v in support)
    shapes = {(0, 1, 1, 1, 1): '2K2_PLUS_K1', (0, 1, 1, 2, 2): 'P4_PLUS_K1',
              (0, 2, 2, 2, 2): 'C4_PLUS_K1'}
    need(tuple(degs) in shapes, 'PATH_INDUCED_SHAPE')
    r = isolated[0]
    q = [v for v in support if v != r]
    candidates = [((q[0], q[1]), (q[2], q[3])), ((q[0], q[2]), (q[1], q[3])),
                  ((q[0], q[3]), (q[1], q[2]))]
    matchings = [matching for matching in candidates if all(b in neighbors[a] for a, b in matching)]
    need(1 <= len(matchings) <= 2, 'PATH_MATCHING_MULTIPLICITY')
    index_by_triangle = {triangle: i for i, triangle in enumerate(triangles)}
    preimages = []
    for matching in matchings:
        completions = []
        for a, b in matching:
            completed = neighbors[a] & neighbors[b]
            need(len(completed) == 1, 'PATH_UNIQUE_EDGE_COMPLETION')
            completions.append(next(iter(completed)))
        p, v = completions
        proposed = [tuple(sorted((*matching[0], p))), tuple(sorted((*matching[1], v))),
                    tuple(sorted((p, v, r)))]
        if p != v and len(set(proposed)) == 3 and all(t in index_by_triangle for t in proposed):
            recovered = sorted(index_by_triangle[t] for t in proposed)
            if xor_support(proposed) == support:
                preimages.append(dict(matching_edges=[list(e) for e in matching],
                                      edge_completions=completions, triangle_indices=recovered))
    need(sorted(indices) in [p['triangle_indices'] for p in preimages], 'PATH_INVERSE_RECOVERS_ORIGINAL')
    need(len(preimages) <= 2, 'PATH_PREIMAGE_BOUND')
    return dict(triangle_indices=list(indices), central_triangle_index=indices[middle],
                intersection_points=points, support=support, isolated_vertex=r,
                induced_edges=induced, induced_shape=shapes[tuple(degs)],
                perfect_matchings=[[list(e) for e in m] for m in matchings], candidate_preimages=preimages)


def produce(label, n, edges):
    neighbors, triangles = graph(n, edges)
    incidence = Counter(v for t in triangles for v in t)
    irregular_paths = sum((incidence[p]-1)*(incidence[q]-1) for t in triangles
                          for p, q in itertools.combinations(t, 2))
    raw_triples, paths = [], []
    for indices in itertools.combinations(range(len(triangles)), 3):
        ts = [set(triangles[i]) for i in indices]
        meetings = sum(bool(ts[a] & ts[b]) for a, b in itertools.combinations(range(3), 2))
        support = xor_support(ts)
        raw_triples.append(dict(triangle_indices=list(indices), support=support, weight=len(support),
                                intersection_pairs=meetings))
        if meetings == 2:
            paths.append(path_inverse(neighbors, triangles, indices))
        else:
            need(len(support) != 5, 'WEIGHT5_EXHAUSTIVE_INTERSECTION_TYPE')
    need(len(paths) == irregular_paths, 'IRREGULAR_PATH_COUNT')
    fibers = defaultdict(list)
    for path in paths:
        fibers[tuple(path['support'])].append(path['triangle_indices'])
    raw_fibers = []
    for support, preimages in sorted(fibers.items()):
        need(len(preimages) <= 2, 'SUPPORT_FIBER_BOUND')
        exemplar = next(path for path in paths if path['support'] == list(support))
        inverses = [p['triangle_indices'] for p in exemplar['candidate_preimages']]
        need(sorted(preimages) == sorted(inverses), 'SUPPORT_COMPLETE_FIBER_INVERSE')
        raw_fibers.append(dict(support=list(support), preimages=preimages, multiplicity=len(preimages)))
    image_records = []
    for coefficient_mask in range(1 << len(triangles)):
        support = xor_support([t for i, t in enumerate(triangles) if coefficient_mask >> i & 1])
        image_records.append(dict(coefficient_mask=coefficient_mask, support=support))
    image = {tuple(row['support']) for row in image_records}
    image_weight5 = sorted([list(word) for word in image if len(word) == 5])
    need(all(support in image for support in fibers), 'PATH_IMAGE_MEMBERSHIP')
    need(len(fibers) >= (irregular_paths+1)//2, 'DISTINCT_WORD_LOWER_BOUND')
    regular_r = incidence.get(0, 0)
    if any(incidence.get(v, 0) != regular_r for v in range(n)):
        regular_r = None
    regular_formula = None if regular_r is None else len(triangles)*3*(regular_r-1)**2
    if regular_formula is not None:
        need(regular_formula == irregular_paths, 'REGULAR_PATH_FORMULA')
    return dict(schema='TRIANGLE_IMAGE_WEIGHT5_PATH_FIXTURE_V1', label=label, vertices=n, edges=edges,
                actual_triangles=[list(t) for t in triangles], vertex_triangle_counts=[incidence.get(v, 0) for v in range(n)],
                all_triangle_triples=raw_triples, path_records=paths, support_fibers=raw_fibers,
                path_count=len(paths), distinct_path_words=len(fibers), path_word_lower_bound=(irregular_paths+1)//2,
                irregular_path_formula=irregular_paths, regular_r=regular_r, regular_path_formula=regular_formula,
                complete_small_image_records=image_records, complete_small_image_size=len(image),
                complete_small_image_weight5_words=image_weight5)


def verify(row):
    correct = produce(row['label'], row['vertices'], row['edges'])
    need(row.get('actual_triangles') == correct['actual_triangles'], 'RAW_ACTUAL_TRIANGLES')
    need(len(row.get('path_records', [])) == len(correct['path_records']), 'RAW_PATH_POPULATION')
    for raw, exact in zip(row['path_records'], correct['path_records']):
        for key in ('triangle_indices', 'central_triangle_index', 'intersection_points', 'support', 'isolated_vertex',
                    'induced_edges', 'induced_shape', 'perfect_matchings', 'candidate_preimages'):
            need(raw.get(key) == exact[key], 'RAW_PATH:' + key)
    for key in ('support_fibers', 'all_triangle_triples', 'vertex_triangle_counts', 'path_count', 'distinct_path_words',
                'path_word_lower_bound', 'irregular_path_formula', 'regular_r', 'regular_path_formula',
                'complete_small_image_records', 'complete_small_image_size', 'complete_small_image_weight5_words'):
        need(row.get(key) == correct[key], 'RAW_METADATA:' + key)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['controls'], required=True)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--source-sha256', required=True)
    ap.add_argument('--protocol-sha256', required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Seven small actual graphs/62 triples/234 image coefficient masks; no target search/LP')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'OUTPUT_WORKSPACE')
    out.mkdir(parents=True, exist_ok=False)
    pins = {}
    try:
        for path, expected in ((SOURCE, args.source_sha256), (SPEC, args.protocol_sha256), (NOTE, NOTE_SHA)):
            pins[path] = sha(ROOT/path)
            need(pins[path] == expected, 'EXACT_SOURCE_PIN:' + path)
        for path in ('acceleration/command_deadline.py', 'acceleration/run_compute_command.py', 'uv.lock', 'pyproject.toml'):
            pins[path] = sha(ROOT/path)
        definitions = [
            ('single_triangle', 3, [(0, 1, 2)]),
            ('friendship7', 15, [(0, 2*i+1, 2*i+2) for i in range(7)]),
            ('one_intersection_plus_disjoint', 8, [(0, 1, 2), (2, 3, 4), (5, 6, 7)]),
            ('loose_chain3', 7, [(0, 1, 2), (2, 3, 4), (4, 5, 6)]),
            ('three_disjoint', 9, [(0, 1, 2), (3, 4, 5), (6, 7, 8)]),
            ('loose_cycle4', 8, [(0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 0)]),
            ('rook9', 9, [(3*r, 3*r+1, 3*r+2) for r in range(3)] + [(c, c+3, c+6) for c in range(3)]),
        ]
        fixtures = []
        for label, n, ts in definitions:
            need(deadline.status()['remaining_seconds'] > 10, 'DEADLINE_SERIALIZATION_RESERVE')
            row = produce(label, n, edge_union(ts))
            verify(row)
            fixtures.append(row)
        labels = {row['label']: row for row in fixtures}
        need(labels['rook9']['path_count'] == 18 and labels['rook9']['distinct_path_words'] == 9
             and all(f['multiplicity'] == 2 for f in labels['rook9']['support_fibers']), 'ROOK9_TWO_FOLD_CONTROL')
        need(labels['loose_chain3']['path_count'] == labels['loose_chain3']['distinct_path_words'] == 1, 'LOOSE_CHAIN_ONE_FOLD_CONTROL')
        need(labels['single_triangle']['path_count'] == labels['friendship7']['path_count'] == 0, 'ZERO_PATH_CONTROLS')
        need(set(p['induced_shape'] for row in fixtures for p in row['path_records'])
             == {'2K2_PLUS_K1', 'P4_PLUS_K1', 'C4_PLUS_K1'}, 'ALL_THREE_INDUCED_SHAPES')
        save(out/'actual_graph_fixtures.json', fixtures)
        controls = []
        def reject(label, call, stage):
            try:
                call()
            except InvalidControl as error:
                need(str(error) == stage, 'EXACT_NEGATIVE_STAGE:' + label)
                controls.append(dict(label=label, expected=stage, actual=str(error), rejected=True))
                return
            raise InvalidControl('CORRUPTION_ACCEPTED:' + label)
        original = labels['rook9']
        cases = [
            ('drop_path', lambda r: r['path_records'].pop(), 'RAW_PATH_POPULATION'),
            ('changed_support', lambda r: r['path_records'][0]['support'].pop(), 'RAW_PATH:support'),
            ('changed_isolated', lambda r: r['path_records'][0].update(isolated_vertex=99), 'RAW_PATH:isolated_vertex'),
            ('changed_induced_edges', lambda r: r['path_records'][0]['induced_edges'].pop(), 'RAW_PATH:induced_edges'),
            ('changed_shape', lambda r: r['path_records'][0].update(induced_shape='2K2_PLUS_K1'), 'RAW_PATH:induced_shape'),
            ('changed_matching', lambda r: r['path_records'][0]['perfect_matchings'].pop(), 'RAW_PATH:perfect_matchings'),
            ('changed_completion', lambda r: r['path_records'][0]['candidate_preimages'][0]['edge_completions'].append(99), 'RAW_PATH:candidate_preimages'),
            ('changed_middle', lambda r: r['path_records'][0].update(central_triangle_index=99), 'RAW_PATH:central_triangle_index'),
            ('changed_fiber', lambda r: r['support_fibers'][0]['preimages'].pop(), 'RAW_METADATA:support_fibers'),
            ('changed_path_count', lambda r: r.update(path_count=17), 'RAW_METADATA:path_count'),
            ('changed_distinct_count', lambda r: r.update(distinct_path_words=18), 'RAW_METADATA:distinct_path_words'),
            ('changed_irregular_formula', lambda r: r.update(irregular_path_formula=17), 'RAW_METADATA:irregular_path_formula'),
            ('changed_regular_formula', lambda r: r.update(regular_path_formula=17), 'RAW_METADATA:regular_path_formula'),
            ('changed_complete_image', lambda r: r['complete_small_image_records'].pop(), 'RAW_METADATA:complete_small_image_records'),
            ('changed_actual_triangles', lambda r: r['actual_triangles'].pop(), 'RAW_ACTUAL_TRIANGLES'),
        ]
        for label, mutate, stage in cases:
            bad = copy.deepcopy(original)
            mutate(bad)
            save(out/(label+'.json'), bad)
            reject(label, lambda bad=bad: verify(bad), stage)
        bad_scope = [
            ('pasch', 6, [(0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 5)]),
            ('complete_k7', 7, list(itertools.combinations(range(7), 3))),
        ]
        missing = []
        for label, n, ts in bad_scope:
            edges = edge_union(ts)
            neighbors, actual = graph(n, edges, scoped=False)
            missing.append(dict(label=label, vertices=n, edges=edges, actual_triangles=[list(t) for t in actual],
                                edge_common_neighbors=[dict(edge=e, common_neighbors=sorted(neighbors[e[0]] & neighbors[e[1]])) for e in edges]))
            reject(label, lambda label=label, n=n, edges=edges: produce(label, n, edges), 'SCOPE_EDGE_CN1')
        collisions = [
            [(0, 5, 6), (1, 2, 5), (3, 4, 6)],
            [(1, 5, 6), (0, 2, 5), (3, 4, 6)],
            [(2, 5, 6), (0, 1, 5), (3, 4, 6)],
        ]
        need(all(xor_support(ts) == list(range(5)) for ts in collisions), 'K7_THREE_FOLD_SCOPE_FALSIFICATION')
        save(out/'missing_premise_controls.json', dict(fixtures=missing, k7_three_distinct_weight5_paths=collisions,
                                                     shared_support=list(range(5))))
        save(out/'strict_controls.json', controls)
        target = dict(n=99, m=231, r=7, unordered_path_count=231*3*6*6, maximum_support_fiber=2,
                      distinct_image_weight5_lower_bound=(231*3*6*6+1)//2, status='CANDIDATE',
                      independent_verification=None, reason='Universal written proof and finite raw checking pending separate review')
        need(target['unordered_path_count'] == 24948 and target['distinct_image_weight5_lower_bound'] == 12474, 'TARGET_ARITHMETIC')
        save(out/'candidate_constants.json', target)
        need(deadline.status()['remaining_seconds'] > 0, 'DEADLINE_COMPLETE')
        outputs = {path.relative_to(ROOT).as_posix(): sha(path) for path in sorted(out.iterdir()) if path.is_file()}
        save(out/'summary.json', dict(status='AUTHOR_TRIANGLE_IMAGE_WEIGHT5_CONTROLS_V1_PASS', timestamp=datetime.now(timezone.utc).isoformat(),
             source_commit_context='2d578fa8171597d7a009f02f0d92ee987de24555',
             actual_source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
             command=[sys.executable, *sys.argv], working_directory=str(ROOT), python_version=platform.python_version(),
             inputs_sha256=pins, outputs_sha256=outputs, positive_graph_fixtures=len(fixtures),
             complete_fixture_triangle_triples=sum(len(r['all_triangle_triples']) for r in fixtures),
             unordered_fixture_paths=sum(r['path_count'] for r in fixtures), distinct_fixture_path_words=sum(r['distinct_path_words'] for r in fixtures),
             complete_small_image_coefficient_masks=sum(len(r['complete_small_image_records']) for r in fixtures),
             strict_negative_controls=len(controls), target_path_count=24948, target_image_weight5_lower_count=12474,
             independent_approval=False, mathematical_status='CANDIDATE', numerical_solver=False, target_graph_search=False,
             target_resolution='NONE', ledger_mutated=False, random_seed=None, random_seed_reason='No random generator; frozen complete finite fixtures',
             shared_components=['command_deadline.py only; rechecking shares this producer and does not independently establish the universal theorem'],
             limitations=['Not a generic code bound or target existence/nonexistence result', 'No novelty or incidence rank upper bound',
                          'Tiny complete image enumeration is not target code enumeration'], deadline=deadline.status()))
        print('AUTHOR_TRIANGLE_IMAGE_WEIGHT5_CONTROLS_V1_PASS')
    except BaseException as error:
        save(out/'failure.json', dict(exception=type(error).__name__, diagnostic=str(error), inputs_sha256=pins,
                                      deadline=deadline.status(), mathematical_status='UNKNOWN', ledger_mutated=False))
        raise


if __name__ == '__main__':
    main()
