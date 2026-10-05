"""Separate exact triangle-path artifact/character checker; no producer imports."""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import platform
import subprocess
import sys
from command_deadline import CommandDeadline
import audit_20261003_triangle_image_weight5_core_v1 as C

ROOT = Path(__file__).resolve().parents[1]
CODE = ['acceleration/audit_20261003_triangle_image_weight5_v1.py',
        'acceleration/audit_20261003_triangle_image_weight5_v1_spec.md',
        'acceleration/audit_20261003_triangle_image_weight5_core_v1.py',
        'acceleration/audit_20261003_triangle_image_weight5_v1_proof.md',
        'acceleration/command_deadline.py', 'acceleration/run_compute_command.py',
        'pyproject.toml', 'uv.lock']
PRODUCER = {
    'acceleration/theory_20261003_triangle_image_weight5_v1.py':
        'ac8287ac4ca1cfc82f5b9042ac578900b5a4dec2fe13938d8a5adaeb96b60bbc',
    'acceleration/theory_20261003_triangle_image_weight5_v1_spec.md':
        'aff76615bee6d7f2ae8a7c1aa0b52e9aa4701aaa00d21aadc845b758ca05ef78',
    'docs/CANDIDATE_20261003_TRIANGLE_IMAGE_WEIGHT5_V1.md':
        'f175e6803924056cbaee112f2430b010f21277cb5792d1ce104ed9cb6c9f60c4',
}
BASE = 'acceleration/results/20261003_triangle_image_weight5_controls01'
SUPERVISOR = 'acceleration/results/20261003_triangle_image_weight5_controls_supervision01'


def local(name):
    path = (ROOT / name).resolve()
    C.require(path.is_relative_to(ROOT), 'IDENTITY', 'workspace path')
    return path


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def unique(pairs):
    result = {}
    for key, value in pairs:
        C.require(key not in result, 'SYNTAX', 'duplicate JSON key')
        result[key] = value
    return result


def load(path):
    def constant(value):
        raise C.AuditError('SYNTAX', 'nonfinite literal ' + value)
    return json.loads(path.read_bytes(), object_pairs_hook=unique, parse_constant=constant)


def identical(left, right):
    return json.dumps(left, sort_keys=True, separators=(',', ':'), allow_nan=False) == \
        json.dumps(right, sort_keys=True, separators=(',', ':'), allow_nan=False)


def definitions():
    return [
        ('single_triangle', 3, [(0, 1, 2)]),
        ('friendship7', 15, [(0, 2 * i + 1, 2 * i + 2) for i in range(7)]),
        ('one_intersection_plus_disjoint', 8, [(0, 1, 2), (2, 3, 4), (5, 6, 7)]),
        ('loose_chain3', 7, [(0, 1, 2), (2, 3, 4), (4, 5, 6)]),
        ('three_disjoint', 9, [(0, 1, 2), (3, 4, 5), (6, 7, 8)]),
        ('loose_cycle4', 8, [(0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 0)]),
        ('rook9', 9, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(3)]
         + [(i, i + 3, i + 6) for i in range(3)]),
    ]


def reconstruct(label, rows):
    proof = C.full_small_graph(rows)
    triangles = [tuple(t) for t in proof['actual_triangles']]
    all_trios = []
    for ids in combinations(range(len(triangles)), 3):
        support = C.points(C.mask(triangles[ids[0]]) ^ C.mask(triangles[ids[1]])
                           ^ C.mask(triangles[ids[2]]))
        meetings = sum(bool(set(triangles[i]) & set(triangles[j]))
                       for i, j in combinations(ids, 2))
        all_trios.append(dict(triangle_indices=list(ids), support=support,
                              weight=len(support), intersection_pairs=meetings))
    paths = []
    inverse_by_support = {tuple(r['support']): r for r in proof['inverses']}
    fibers = {}
    for path in proof['paths']:
        ids = path['path']
        central = path['central']
        meet = sorted(next(iter(set(triangles[central]) & set(triangles[i])))
                      for i in ids if i != central)
        iv = inverse_by_support[tuple(path['support'])]
        ds = sorted(sum(u in edge for edge in iv['induced_edges']) for u in path['support'])
        shape = {(0, 1, 1, 1, 1): '2K2_PLUS_K1',
                 (0, 1, 1, 2, 2): 'P4_PLUS_K1',
                 (0, 2, 2, 2, 2): 'C4_PLUS_K1'}.get(tuple(ds))
        C.require(shape is not None, 'SHAPE', 'complete induced graph shape')
        preimages = [dict(matching_edges=v['matching'], edge_completions=v['completions'],
                         triangle_indices=v['recovered_path'])
                     for v in iv['completion_records'] if v['recovered_path'] is not None]
        paths.append(dict(triangle_indices=ids, central_triangle_index=central,
                          intersection_points=meet, support=path['support'],
                          isolated_vertex=iv['isolated'], induced_edges=iv['induced_edges'],
                          induced_shape=shape, perfect_matchings=iv['matchings'],
                          candidate_preimages=preimages))
        fibers.setdefault(tuple(path['support']), []).append(ids)
    image_records = []
    for coefficient in range(1 << len(triangles)):
        word = 0
        for i, triangle in enumerate(triangles):
            if coefficient >> i & 1:
                word ^= C.mask(triangle)
        image_records.append(dict(coefficient_mask=coefficient, support=C.points(word)))
    code = {C.mask(r['support']) for r in image_records}
    counts = [sum(v in t for t in triangles) for v in range(len(rows))]
    r = counts[0] if counts and all(v == counts[0] for v in counts) else None
    result = dict(schema='TRIANGLE_IMAGE_WEIGHT5_PATH_FIXTURE_V1', label=label,
                  vertices=len(rows), edges=[list(p) for p in combinations(range(len(rows)), 2)
                                            if p[1] in rows[p[0]]],
                  actual_triangles=[list(t) for t in triangles], vertex_triangle_counts=counts,
                  all_triangle_triples=all_trios, path_records=paths,
                  support_fibers=[dict(support=list(s), preimages=v, multiplicity=len(v))
                                  for s, v in sorted(fibers.items())],
                  path_count=len(paths), distinct_path_words=len(fibers),
                  path_word_lower_bound=(len(paths) + 1) // 2,
                  irregular_path_formula=C.formula(triangles, len(rows)), regular_r=r,
                  regular_path_formula=None if r is None else 3 * len(triangles) * (r - 1) ** 2,
                  complete_small_image_records=image_records, complete_small_image_size=len(code),
                  complete_small_image_weight5_words=sorted(C.points(w) for w in code if w.bit_count() == 5))
    return result, code


def raw_check(raw, exact):
    C.require(set(raw) == set(exact) and all(identical(raw.get(k), exact[k])
              for k in ['schema', 'label', 'vertices', 'edges']), 'RAW_HEADER', 'exact raw fixture identity')
    C.require(identical(raw['actual_triangles'], exact['actual_triangles']),
              'RAW_ACTUAL_TRIANGLES', 'complete lexicographic actual triangle family')
    C.require(len(raw['path_records']) == len(exact['path_records']),
              'RAW_PATH_POPULATION', 'complete path population')
    for row, wanted in zip(raw['path_records'], exact['path_records']):
        C.require(set(row) == set(wanted), 'RAW_PATH_KEYS', 'complete path record')
        for key in ['triangle_indices', 'central_triangle_index', 'intersection_points', 'support',
                    'isolated_vertex', 'induced_edges', 'induced_shape', 'perfect_matchings', 'candidate_preimages']:
            C.require(identical(row[key], wanted[key]), 'RAW_PATH:' + key, 'independent raw value')
    for key in ['support_fibers', 'all_triangle_triples', 'vertex_triangle_counts', 'path_count',
                'distinct_path_words', 'path_word_lower_bound', 'irregular_path_formula',
                'regular_r', 'regular_path_formula', 'complete_small_image_records',
                'complete_small_image_size', 'complete_small_image_weight5_words']:
        C.require(identical(raw[key], exact[key]), 'RAW_METADATA:' + key, 'independent exact metadata')


def character_check(rows, code):
    triangles = C.actual_triangles(rows)
    generators = [C.mask(t) for t in triangles]
    kernel = [w for w in range(1 << len(rows))
              if all((w & g).bit_count() % 2 == 0 for g in generators)]
    C.require(len(code) * len(kernel) == 1 << len(rows), 'CHARACTER', 'literal image/kernel dimensions')
    five = [C.mask(s) for s in combinations(range(len(rows)), 5)]
    direct = sum((-1) ** ((x & y).bit_count() % 2) for x in kernel for y in five)
    polynomial = sum(C.krawtchouk(len(rows), 5, x.bit_count()) for x in kernel) if len(rows) >= 5 else 0
    full_count = sum(y in code for y in five)
    C.require(direct == polynomial == len(kernel) * full_count,
              'CHARACTER', 'complete ambient weight-five binary character sums')
    lower = (C.formula(triangles, len(rows)) + 1) // 2
    shifted = sum(lower - C.krawtchouk(len(rows), 5, x.bit_count()) for x in kernel if x) if len(rows) >= 5 else 0
    rhs = comb(len(rows), 5) - lower if len(rows) >= 5 else -lower
    C.require(shifted <= rhs, 'CHARACTER', 'sharp shifted constant including zero word')
    return dict(kernel_words=len(kernel), image_words=len(code), weight5_ambient=len(five),
                literal_character_terms=len(kernel) * len(five), actual_weight5_words=full_count,
                lower_count=lower, shifted_lhs=shifted, shifted_rhs=rhs)


def reject(records, label, stage, fn):
    try:
        fn()
    except C.AuditError as error:
        C.require(error.stage == stage, 'WRONG_CONTROL_STAGE', 'precise diagnostic ' + label)
        records.append(dict(label=label, expected=stage, actual=error.stage, outcome='REJECTED'))
        return
    raise C.AuditError('CONTROL_ACCEPTED', label)


def corruptions():
    return [
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


def calibration(out):
    controls = []
    details = []
    raw = {}
    for label, n, triples in definitions():
        rows = C.adjacency(n, triples)
        exact, code = reconstruct(label, rows)
        raw_check(copy.deepcopy(exact), exact)
        detail = character_check(rows, code)
        details.append(dict(label=label, path_count=exact['path_count'],
                            distinct_path_words=exact['distinct_path_words'], character=detail))
        controls.append(dict(label=label, outcome='PASS'))
        raw[label] = exact
    rook = raw['rook9']
    C.require(rook['path_count'] == 18 and rook['distinct_path_words'] == 9
              and len(rook['complete_small_image_weight5_words']) == 9
              and all(v['multiplicity'] == 2 for v in rook['support_fibers']),
              'CALIBRATION', 'rook exact two-fold inverse and full-code N5')
    C.require({p['induced_shape'] for r in raw.values() for p in r['path_records']} ==
              {'2K2_PLUS_K1', 'P4_PLUS_K1', 'C4_PLUS_K1'}, 'CALIBRATION', 'all three inverse shapes')
    for label, mutation, stage in corruptions():
        bad = copy.deepcopy(rook)
        mutation(bad)
        reject(controls, label, stage, lambda bad=bad: raw_check(bad, rook))
    for label, rows in [('pasch', C.adjacency(6, [(0,1,2),(0,3,4),(1,3,5),(2,4,5)])),
                        ('complete_k7', [set(range(7)) - {v} for v in range(7)])]:
        reject(controls, label, 'PREMISE', lambda rows=rows: C.validate_graph(rows))
    bad = copy.deepcopy(rook)
    bad['path_count'] = True
    reject(controls, 'Boolean path count', 'RAW_METADATA:path_count', lambda: raw_check(bad, rook))
    bad = copy.deepcopy(rook)
    bad['regular_path_formula'] = 18.0
    reject(controls, 'Floating exact formula', 'RAW_METADATA:regular_path_formula', lambda: raw_check(bad, rook))
    rook_character = next(v['character'] for v in details if v['label'] == 'rook9')
    rook_full_sum = rook_character['kernel_words'] * rook_character['actual_weight5_words']
    rook_nonzero_sum = rook_full_sum - comb(9, 5)
    reject(controls, 'false zero-word-free constant', 'CHARACTER',
           lambda: C.require(rook_nonzero_sum >= rook_full_sum, 'CHARACTER', 'rook omitted zero-word K5(0) constant'))
    reject(controls, 'wrong-stage diagnostic harness', 'WRONG_CONTROL_STAGE',
           lambda: reject([], 'wrong stage', 'MATCHING', lambda: C.require(False, 'SUPPORT', 'synthetic wrong stage')))
    save(out / 'controls.json', controls)
    save(out / 'calibration_fixtures.json', details)
    return dict(status='INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_V1_CALIBRATION_PASS',
                positive_fixtures=7, strict_negative_controls=21,
                controls_sha256=sha(out / 'controls.json'),
                calibration_fixtures_sha256=sha(out / 'calibration_fixtures.json'),
                producer_outputs_checked=False)


def full(args, out, pin, pins):
    C.require(all([args.calibration, args.calibration_sha256, args.producer_summary_sha256]),
              'IDENTITY', 'exact pre-full calibration and raw producer identities')
    pin(args.calibration, args.calibration_sha256)
    cal = load(local(args.calibration))
    C.require(cal['status'] == 'INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_V1_CALIBRATION_PASS'
              and cal['positive_fixtures'] == 7 and cal['strict_negative_controls'] == 21,
              'CALIBRATION', 'pre-full calibrated separate checking path')
    for name in CODE:
        C.require(cal['inputs_sha256'].get(name) == pins[name], 'CALIBRATION', 'unchanged checker/code environment')
    for name, wanted in cal['inputs_sha256'].items():
        pin(name, wanted)
    summary_name = BASE + '/summary.json'
    pin(summary_name, args.producer_summary_sha256)
    producer = load(local(summary_name))
    C.require(producer['status'] == 'AUTHOR_TRIANGLE_IMAGE_WEIGHT5_CONTROLS_V1_PASS'
              and producer['independent_approval'] is False and producer['mathematical_status'] == 'CANDIDATE'
              and producer['numerical_solver'] is False and producer['target_graph_search'] is False,
              'PRODUCER_SCOPE', 'raw author controls only')
    for name, wanted in {**producer['inputs_sha256'], **producer['outputs_sha256']}.items():
        pin(name, wanted)
    for name in ['manifest.json', 'summary.json', 'stdout.log', 'stderr.log']:
        pin(SUPERVISOR + '/' + name)
    terminal = load(local(SUPERVISOR + '/summary.json'))
    C.require(terminal['command_exit_code'] == 0 and terminal['cleanup']['reaped'] is True
              and terminal['cleanup']['job_active_zero_observed'] is True
              and terminal['cleanup']['cleanup_errors'] == [], 'SUPERVISOR', 'actual complete contained producer')
    fixtures = load(local(BASE + '/actual_graph_fixtures.json'))
    C.require(len(fixtures) == 7 and [r['label'] for r in fixtures] == [r[0] for r in definitions()],
              'RAW_POPULATION', 'seven frozen fixtures')
    actual = {}
    details = []
    for raw, (label, n, triples) in zip(fixtures, definitions()):
        rows = C.adjacency(n, triples)
        exact, code = reconstruct(label, rows)
        raw_check(raw, exact)
        actual[label] = exact
        details.append(dict(label=label, vertices=n, actual_triangles=len(exact['actual_triangles']),
                            three_triangle_combinations=len(exact['all_triangle_triples']),
                            paths=exact['path_count'], distinct_path_words=exact['distinct_path_words'],
                            image_coefficient_masks=len(exact['complete_small_image_records']),
                            character=character_check(rows, code)))
    controls = []
    stages = {label: stage for label, _, stage in corruptions()}
    for label, _, stage in corruptions():
        bad = load(local(BASE + '/' + label + '.json'))
        reject(controls, 'actual_saved_' + label, stage, lambda bad=bad: raw_check(bad, actual['rook9']))
    missing = load(local(BASE + '/missing_premise_controls.json'))
    expected_missing = [('pasch', 6, [(0,1,2),(0,3,4),(1,3,5),(2,4,5)]),
                        ('complete_k7', 7, list(combinations(range(7), 3)))]
    C.require(len(missing['fixtures']) == 2, 'RAW_POPULATION', 'two premise counterfixtures')
    for raw, (label, n, triples) in zip(missing['fixtures'], expected_missing):
        rows = C.adjacency(n, triples)
        edges = [list(e) for e in combinations(range(n), 2) if e[1] in rows[e[0]]]
        exact = dict(label=label, vertices=n, edges=edges,
                     actual_triangles=[list(t) for t in C.actual_triangles(rows)],
                     edge_common_neighbors=[dict(edge=e, common_neighbors=sorted(rows[e[0]] & rows[e[1]])) for e in edges])
        C.require(identical(raw, exact), 'MISSING_PREMISE', 'literal full counterfixture')
        reject(controls, 'actual_saved_' + label, 'PREMISE', lambda rows=rows: C.validate_graph(rows))
    collisions = missing['k7_three_distinct_weight5_paths']
    C.require(len(collisions) == 3 and len({tuple(sorted(tuple(sorted(t)) for t in ts)) for ts in collisions}) == 3,
              'SCOPE_FALSIFICATION', 'three different actual K7 paths')
    for ts in collisions:
        triangles = sorted(tuple(sorted(t)) for t in ts)
        C.require(len(triangles) == 3 and all(len(set(t)) == 3 and set(t) <= set(range(7)) for t in triangles),
                  'SCOPE_FALSIFICATION', 'actual K7 triangles')
        paths = C.unordered_paths([set(range(7)) - {v} for v in range(7)], triangles)
        C.require(len(paths) == 1 and paths[0]['support'] == missing['shared_support'] == list(range(5)),
                  'SCOPE_FALSIFICATION', 'three preimages of identical support outside premise')
    counts = load(local(BASE + '/candidate_constants.json'))
    C.require(counts['n'] == 99 and counts['m'] == 231 and counts['r'] == 7
              and counts['unordered_path_count'] == 24948 and counts['maximum_support_fiber'] == 2
              and counts['distinct_image_weight5_lower_bound'] == 12474,
              'TARGET_CONSTANT', 'conditional target arithmetic')
    lower = 12474
    denom = comb(99, 5) - lower
    normalized = {'lower_count': lower, 'denominator': denom,
                  'coefficient_by_weight': {str(w): [q.numerator, q.denominator]
                    for w in range(1,100) for q in [Fraction(lower - C.krawtchouk(99,5,w), denom)]}}
    C.require(denom == 71510670, 'CHARACTER', 'exact target denominator')
    save(out / 'checked_fixtures.json', details)
    save(out / 'actual_corruption_checks.json', controls)
    save(out / 'normalized_target_row.json', normalized)
    return dict(status='INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_PATH_LOWER_COUNT_V1_PASS',
                statement='For every finite simple graph in which every adjacent pair has exactly one common neighbor, let T be its complete actual triangle family and r_v the number of its triangles through v. Its binary triangle-incidence image contains at least ceil(P/2) distinct weight5 words, where P=sum_{t in T} sum_{unordered {u,v} subset t}(r_u-1)(r_v-1). Consequently any graph satisfying the exact Conway99 target has P=24948 and at least12474 weight5 image words; its triangle-incidence kernel satisfies sum_{w>0} A_w(12474-K5(w))<=71510670. These are conditional necessary lower counts and an exact character inequality, not a target graph, rank bound or exclusion.',
                universal_derivation_checked=True,
                written_audit='acceleration/audit_20261003_triangle_image_weight5_v1_proof.md',
                positive_fixtures=7, actual_saved_strict_negative_controls=len(controls),
                complete_triangle_combinations=sum(v['three_triangle_combinations'] for v in details),
                unordered_fixture_paths=sum(v['paths'] for v in details),
                distinct_separate_fixture_path_words=sum(v['distinct_path_words'] for v in details),
                complete_small_image_coefficient_masks=sum(v['image_coefficient_masks'] for v in details),
                target_unordered_paths=24948, target_weight5_lower_count=12474,
                character_normalization=normalized, checked_fixtures_sha256=sha(out/'checked_fixtures.json'),
                actual_corruption_checks_sha256=sha(out/'actual_corruption_checks.json'),
                normalized_target_row_sha256=sha(out/'normalized_target_row.json'),
                new_exclusions=0, target_resolution='NONE', rank_bound_claimed=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['calibration', 'full'])
    p.add_argument('--seconds', type=float, required=True)
    p.add_argument('--out', required=True)
    for name in ['calibration', 'calibration-sha256', 'producer-summary-sha256']:
        p.add_argument('--' + name)
    args = p.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent complete small trianglepath/character calibration or raw check;20second save reserve, no optimizer')
    out = local(args.out)
    out.mkdir(parents=True, exist_ok=False)
    pins = {}
    def pin(name, wanted=None):
        C.require(deadline.status()['remaining_seconds'] > 20, 'DEADLINE', 'orderly serialization reserve')
        h = sha(local(name))
        C.require(wanted is None or h == wanted, 'IDENTITY', 'exact bytes ' + name)
        pins[name] = h
    try:
        for name in CODE:
            pin(name)
        for name, h in PRODUCER.items():
            pin(name, h)
        protected = {name: sha(local(name)) for name in ['CLAIMS.yaml', '.git/index']}
        result = calibration(out) if args.mode == 'calibration' else full(args, out, pin, pins)
        C.require(all(sha(local(name)) == h for name, h in protected.items()),
                  'PROTECTED_STATE', 'live ledger/index unchanged during checking')
        result.update(timestamp=datetime.now(timezone.utc).isoformat(),
                      producer='/root/structural', verifier='/root/checkpoint_audit', method='independent_derivation',
                      source_commit_context=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                      command=[sys.executable,*sys.argv], cwd=str(ROOT), python=platform.python_version(),
                      inputs_sha256=pins, historical_protected_execution_state=protected,
                      deadline=deadline.status(),
                      shared_components=['Declared raw schema and fixed fixture definitions; no producer implementation imported.',
                                         'Independent adjacency-set actual triangles, integer binary masks, exhaustive unordered triples and inverse matchings.',
                                         'Python exact integers/Fraction/binomial functions/JSON/SHA256 and supported deadline/supervision.'],
                      limitations=['Tiny complete image enumeration calibrates the checking path; universal implication relies on the separate written inverse.',
                                   'Image count is a lower bound; no claim that every target weight5 word is a trianglepath image.',
                                   'No rank upper bound, generic code optimum, novelty, external review, target-wide coverage or target resolution.'])
        save(out/'summary.json',result)
        print(json.dumps({k:result[k] for k in ['status','positive_fixtures','strict_negative_controls','target_weight5_lower_count'] if k in result}))
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),stage=getattr(error,'stage',None),
                                   inputs_sha256=pins,deadline=deadline.status(),outputs_preserved=True,no_approval=True))
        raise


if __name__ == '__main__':
    main()
