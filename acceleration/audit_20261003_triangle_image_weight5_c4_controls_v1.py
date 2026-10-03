"""Independent finite collision-map controls; no discovery producer imports."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import platform
import subprocess
import sys
from command_deadline import CommandDeadline
import audit_20261003_triangle_image_weight5_core_v1 as prior

ROOT = Path(__file__).resolve().parents[1]
PROOF = 'acceleration/audit_20261003_triangle_image_weight5_c4_v1.md'
PROOF_SHA = 'bdc99b2f6a2bf92f9e322616227c4be26db7d57b08ccbcfd9353fbf76260ce12'
CORE = 'acceleration/audit_20261003_triangle_image_weight5_core_v1.py'
CORE_SHA = '7e9813b687afd83551d1beecce01a00b525f51b6ba25c769c76fc5efb7385848'


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, data):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def cycles(rows):
    return [list(q) for q in combinations(range(len(rows)), 4)
            if all(len(rows[v] & set(q)) == 2 for v in q)]


def map_one(rows, record):
    support = record['support']
    need(type(support) is list and len(support) == 5
         and all(type(v) is int and 0 <= v < len(rows) for v in support)
         and support == sorted(set(support)), 'SUPPORT')
    isolated = [v for v in support if not (rows[v] & set(support))]
    need(isolated == [record['isolated']], 'ISOLATED')
    q = [v for v in support if v != isolated[0]]
    need(q == record['cycle'] and q in cycles(rows), 'CYCLE')
    a, *rest = q
    matches = []
    for b in rest:
        c, d = [v for v in rest if v != b]
        if b in rows[a] and d in rows[c]:
            matches.append([[a, b], [c, d]])
    need(len(matches) == 2, 'MATCHINGS')
    matching = sorted(matches)[0]
    p, r = [sorted(rows[u] & rows[v]) for u, v in matching]
    need(len(p) == len(r) == 1 and p[0] != r[0]
         and p[0] not in q and r[0] not in q, 'EDGE_COMPLETIONS')
    need(r[0] in rows[p[0]] and sorted(rows[p[0]] & rows[r[0]]) == isolated,
         'CENTRAL_COMPLETION')
    need(record['canonical_matching'] == matching
         and record['canonical_hidden_points'] == [p[0], r[0]], 'CANONICAL_MAP')
    return tuple(q)


def inject(rows, records):
    keys = [map_one(rows, record) for record in records]
    need(len(keys) == len(set(keys)), 'CYCLE_INJECTION')
    return keys


def complete(rows):
    raw = prior.full_small_graph(rows)
    double = []
    for inverse in raw['inverses']:
        if len(inverse['paths']) != 2:
            continue
        support = inverse['support']
        r = inverse['isolated']
        q = [v for v in support if v != r]
        canonical = sorted(inverse['matchings'])[0]
        hidden = [sorted(rows[u] & rows[v])[0] for u, v in canonical]
        double.append(dict(support=support, isolated=r, cycle=q,
                           canonical_matching=canonical, canonical_hidden_points=hidden,
                           path_preimages=inverse['paths']))
    keys = inject(rows, double)
    c4 = cycles(rows)
    need(raw['distinct_path_words'] == raw['path_count'] - len(double), 'FIBER_SUBTRACTION')
    need(len(keys) <= len(c4), 'CYCLE_BOUND')
    need(raw['complete_weight5_words'] >= raw['path_count'] - len(c4), 'IMAGE_BOUND')
    return dict(path_count=raw['path_count'], distinct_path_words=raw['distinct_path_words'],
                complete_weight5_words=raw['complete_weight5_words'],
                actual_triangles=raw['actual_triangles'], paths=raw['paths'],
                double_fibers=double, induced_cycles=c4,
                double_fiber_count=len(double), cycle_count=len(c4))


def srg_cycles(rows, k):
    n = len(rows)
    prior.validate_graph(rows)
    need(all(len(row) == k for row in rows), 'SRG_DEGREE')
    nonedges = [(u, v) for u, v in combinations(range(n), 2) if v not in rows[u]]
    mapped = []
    for u, v in nonedges:
        common = sorted(rows[u] & rows[v])
        need(len(common) == 2, 'SRG_NONEDGE_CN2')
        x, y = common
        need(y not in rows[x], 'SRG_INDUCED_CYCLE')
        mapped.append(tuple(sorted((u, v, x, y))))
    c4 = cycles(rows)
    need(set(mapped) == set(map(tuple, c4))
         and all(mapped.count(tuple(q)) == 2 for q in c4), 'SRG_TWO_OPPOSITE_PAIRS')
    need(4 * len(c4) == n * (n-k-1), 'SRG_CYCLE_FORMULA')
    return len(c4)


def poly5(n, w):
    values = [1, 0, 0, 0, 0, 0]
    for i in range(n):
        sign = -1 if i < w else 1
        for j in range(5, 0, -1):
            values[j] += sign * values[j-1]
    return values[5]


def reject(label, stage, call, records):
    try:
        call()
    except ValueError as error:
        need(type(error) is ValueError and str(error) == stage, 'WRONG_NEGATIVE_STAGE')
        records.append(dict(case=label, stage=stage, outcome='REJECTED'))
        return
    raise ValueError('CORRUPTION_ACCEPTED:' + label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent seven tiny complete collision-map fixtures, cycle inverse controls and exact100 coefficients; no new producer output or optimization')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'WORKSPACE_OUTPUT')
    out.mkdir(parents=True, exist_ok=False)
    protected = {name: sha(ROOT/name) for name in ['CLAIMS.yaml', '.git/index']}
    pins = {PROOF: PROOF_SHA, CORE: CORE_SHA}
    try:
        for path in [Path(__file__), Path(__file__).with_name(Path(__file__).stem+'_spec.md'),
                     ROOT/'acceleration/command_deadline.py', ROOT/'acceleration/run_compute_command.py',
                     ROOT/'pyproject.toml', ROOT/'uv.lock',
                     ROOT/'acceleration/audit_20261003_triangle_image_weight5_v1_proof.md']:
            pins[path.relative_to(ROOT).as_posix()] = sha(path)
        need(all(sha(ROOT/name) == h for name, h in pins.items()), 'EXACT_INPUT_HASH')
        fixtures = {}
        graphs = {}
        for name, (n, triangles) in prior.fixtures().items():
            need(deadline.status()['remaining_seconds'] > 10, 'SAVE_RESERVE')
            rows = prior.adjacency(n, triangles)
            graphs[name] = rows
            fixtures[name] = complete(rows)
        rook = fixtures['rook9']
        need([rook[k] for k in ['path_count','distinct_path_words','double_fiber_count','cycle_count','complete_weight5_words']]
             == [18,9,9,9,9], 'KNOWN_ROOK_SATURATION')
        need(fixtures['loosechain7']['cycle_count'] == 0
             and fixtures['loosechain7']['path_count'] == 1, 'KNOWN_CHAIN_SATURATION')
        need(fixtures['loosecycle8']['cycle_count'] > fixtures['loosecycle8']['double_fiber_count'],
             'KNOWN_INJECTION_NOT_SURJECTION')
        need(srg_cycles(graphs['rook9'], 4) == 9, 'KNOWN_SRG_CYCLE_FORMULA')
        coefficients = [poly5(99, w) for w in range(100)]
        need(coefficients == [prior.krawtchouk(99, 5, w) for w in range(100)], 'ALL_CHARACTER_COEFFICIENTS')
        paths, c4 = 231*3*6*6, 99*84//4
        lower, denominator = paths-c4, comb(99,5)-(paths-c4)
        need((paths,c4,lower,denominator) == (24948,2079,22869,71500275), 'EXACT_TARGET_CONSTANTS')
        controls = []
        row = copy.deepcopy(rook['double_fibers'][0])
        row['isolated'] = next(v for v in row['cycle'])
        reject('changed isolated', 'ISOLATED', lambda: map_one(graphs['rook9'],row), controls)
        row = copy.deepcopy(rook['double_fibers'][0]); row['cycle'] = row['cycle'][::-1]
        reject('changed cycle', 'CYCLE', lambda: map_one(graphs['rook9'],row), controls)
        row = copy.deepcopy(rook['double_fibers'][0]); row['support'][0] = True
        reject('boolean support', 'SUPPORT', lambda: map_one(graphs['rook9'],row), controls)
        row = copy.deepcopy(rook['double_fibers'][0]); row['canonical_hidden_points'][0] = 99
        reject('changed hidden point', 'CANONICAL_MAP', lambda: map_one(graphs['rook9'],row), controls)
        duplicate = [copy.deepcopy(rook['double_fibers'][0])]*2
        reject('duplicate cycle assignment', 'CYCLE_INJECTION', lambda: inject(graphs['rook9'],duplicate), controls)
        reject('false injective paths', 'FALSE_PATH_INJECTION', lambda: need(rook['path_count'] == rook['distinct_path_words'], 'FALSE_PATH_INJECTION'), controls)
        reject('false surjective collision map', 'FALSE_CYCLE_SURJECTION', lambda: need(fixtures['loosecycle8']['cycle_count'] == fixtures['loosecycle8']['double_fiber_count'], 'FALSE_CYCLE_SURJECTION'), controls)
        reject('cycle formula lacks mu premise', 'SRG_NONEDGE_CN2', lambda: srg_cycles(graphs['loosechain7'], 4), controls)
        reject('overstated rook image', 'FALSE_IMAGE_LOWER', lambda: need(rook['complete_weight5_words'] >= 10, 'FALSE_IMAGE_LOWER'), controls)
        for name, value in protected.items():
            need(sha(ROOT/name) == value, 'PROTECTED_STATE_CHANGED')
        need(not deadline.status()['stop_required'], 'ALLOCATION_EXHAUSTED')
        save(out/'fixture_records.json', fixtures)
        save(out/'strict_controls.json', controls)
        save(out/'target_character_row.json', dict(degree=5, lower=lower, coefficients=coefficients, rhs=denominator))
        save(out/'summary.json', dict(status='INDEPENDENT_WEIGHT5_C4_COLLISION_CHECKER_V1_CALIBRATION_PASS',
             timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/structural', verifier='/root',
             method='independent_derivation', command=[sys.executable,*sys.argv], cwd=str(ROOT),
             python=platform.python_version(), source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             inputs_sha256=pins, complete_fixtures=7, strict_corruption_controls=len(controls),
             complete_character_coefficients=100, target_lower_word_count=lower, target_character_rhs=denominator,
             producer_outputs_checked=False, universal_written_derivation=PROOF,
             target_resolution='NONE', graph_exclusions=0, rank_asserted=False,
             fixture_records_sha256=sha(out/'fixture_records.json'), strict_controls_sha256=sha(out/'strict_controls.json'),
             target_character_row_sha256=sha(out/'target_character_row.json'),
             historical_protected_execution_state=protected,
             shared_components=['Prior independent weight5 core7e981 adjacency, brute unordered paths, inverse and complete small image; no producer imports.',
                                'New independent unordered induced-cycle census and canonical matching reconstruction; truncated polynomial character coefficients differ from binomial checking path.',
                                'Python integers/sets, JSON, SHA256, Git, pinned runtime and command_deadline.'],
             limitations=['New checker calibration and written conditional proof; new producer raw output is not yet checked.',
                          'No optimizer optimum, forced nonzero kernel, graph exclusion, target resolution or external review.'], deadline=deadline.status()))
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), inputs_sha256=pins, saved_outputs_preserved=True))
        raise


if __name__ == '__main__':
    main()
