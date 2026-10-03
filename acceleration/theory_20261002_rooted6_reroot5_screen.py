"""Discovery: exact rerooted universal five-flag identities on all210 profiles.

For a fixed primary pair(u,v), sum universal rooted(u,w) five-flag counts
over w in each adjacency partition to(u,v). Separate whether v occurs among
the three free vertices. The union terms have primary rooted orders6 and5.
No target automorphism, floating arithmetic, or order7 catalogue is used.
"""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
B = ROOT/'acceleration/results'
MODEL = B/'20261002_rooted6_prismfree_rigidity/ordered_nonedge_model.json'
DOMAIN = B/'20261002_rooted6_exact_parameter_domain/prismfree_nonedge_domain.json'
NULL = B/'20261002_rooted6_exact_parameter_domain/prismfree_nonedge_nullspace.json'
FLAGS = {True:B/'20261002_rooted5_flag_rigidity/ordered_edge_forced5flags.json',
         False:B/'20261002_rooted5_flag_rigidity/ordered_nonedge_forced5flags.json'}


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def need(value, reason):
    if not value:
        raise ValueError(reason)


def graph(n, mask):
    result = [set() for _ in range(n)]
    for bit, (u, v) in enumerate(combinations(range(n), 2)):
        if mask >> bit & 1:
            result[u].add(v); result[v].add(u)
    return result


def encode(adjacency, order):
    return sum(1 << bit for bit, (u, v) in enumerate(combinations(order, 2)) if v in adjacency[u])


@lru_cache(None)
def canonical(n, mask):
    adjacency = graph(n, mask)
    return min(encode(adjacency, (0, 1, *free)) for free in permutations(range(2, n)))


def reroot_rows(variables, primary_edge, n, k, forced):
    partitions = {3: 1 if primary_edge else 2}
    partitions[1] = partitions[2] = k - (2 if primary_edge else 2)
    partitions[0] = n-2-sum(partitions.values())
    rows, position = [], {}
    for anchor in [0, 1]:
        for partition in range(4):
            adjacent = bool(partition & (1 << anchor))
            for flag, count in sorted(forced[adjacent].items()):
                position[anchor, partition, flag] = len(rows)
                rows.append(dict(kind='reroot_universal5', anchor=anchor, partition=partition,
                    new_root_relation='edge' if adjacent else 'nonedge', rooted5mask=flag,
                    rhs=partitions[partition]*count, terms=[]))
    accumulated = [Counter() for _ in rows]
    for index, (h, mask) in enumerate(variables):
        if h not in [5, 6]:
            continue
        adjacency = graph(h, mask)
        for anchor in [0, 1]:
            for marked in range(2, h):
                partition = int(marked in adjacency[0]) + 2*int(marked in adjacency[1])
                # At order6 the other primary root is excluded. At order5 it
                # is included; these are disjoint and exhaustive free triples.
                rest = [v for v in range(h) if v not in [anchor, marked] and
                        (h == 5 or v != 1-anchor)]
                order = [anchor, marked, *rest]
                need(len(order) == 5, 'exact union size')
                flag = canonical(5, encode(adjacency, order))
                accumulated[position[anchor, partition, flag]][index] += 1
    for row, terms in zip(rows, accumulated):
        row['terms'] = [[j, value] for j, value in sorted(terms.items()) if value]
    return rows


def actual_counts(adjacency, pair, variables):
    counts = Counter()
    free = [vertex for vertex in range(len(adjacency)) if vertex not in pair]
    for h in [5, 6]:
        for selected in combinations(free, h-2):
            counts[h, canonical(h, encode(adjacency, [*pair, *selected]))] += 1
    return [counts[tuple(variable)] for variable in variables]


def exact_residual(row, vector):
    return sum(value*vector[j] for j, value in row['terms'])-row['rhs']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exact612reroot equations and210 frozen local profiles; direct36rook nonedge rootscontrols; likelyseconds, reserve30.')
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    try:
        paths = [MODEL, DOMAIN, NULL, *FLAGS.values(), Path(__file__), ROOT/'pyproject.toml', ROOT/'uv.lock']
        inputs = {path.relative_to(ROOT).as_posix():sha(path) for path in paths}
        need(inputs[MODEL.relative_to(ROOT).as_posix()] == 'ecf558faa95576b8e76fbc5a62743729a875307eeb99df803c7cb5cdac7b7645', 'frozen model')
        need(inputs[DOMAIN.relative_to(ROOT).as_posix()] == '54f08f8dc87bebf61bada59067cbc721497f3d3a9683936e850b695f0ec41b12', 'frozen all210 domain')
        need(inputs[NULL.relative_to(ROOT).as_posix()] == 'b8abff4be27e90c5d1274cf94ee8aff262cf02117a2086cfdffec5dc97a13e77', 'frozen exact basis')
        manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), inputs_sha256=inputs,
            selection='All210 frozen integer necessary profiles a0..20,b0..9, no omissions or favorable selection.',
            question='Do independently established universal rooted5 counts exclude any prism-free rooted6 nonedge profile by exact rerooted sum identities?',
            success_criterion='Complete612 raw sum identities, calibrated directrook roots, exactaffine residuals and one explicit violated necessary row for each rejected profile.',
            falsification_criterion='Any rook positive control fails, corruption undetected, missing domain point, or nonexact residual vetoes results.',
            scope='Conditional prism-free local necessary count profiles; rejected profiles do not establish target-level nonexistence.',
            verification='Separate implementation checks reroot identity derivation, every coefficient and row certificate; producer does not selfapprove.')
        save(out/'manifest.json', manifest)
        model = read(MODEL); variables = model['variables']
        forced = {relation:{mask:Fraction(*value) for mask, value in read(path)['flag_counts']} for relation, path in FLAGS.items()}
        need(all(value.denominator == 1 for values in forced.values() for value in values.values()), 'universal integral flags')
        forced = {relation:{mask:int(value) for mask, value in values.items()} for relation, values in forced.items()}
        # Direct rook9 controls give different parameters, and universality is
        # checked on every actual root rather than presumed from automorphisms.
        rook = [{v for v in range(9) if v != u and (u//3 == v//3 or u%3 == v%3)} for u in range(9)]
        need(all(len(rook[u]) == 4 and len(rook[u]&rook[v]) == (1 if v in rook[u] else 2) for u, v in combinations(range(9), 2)), 'knownvalid rook exact fixture')
        fixture_forced = {True:{mask:0 for mask in forced[True]}, False:{mask:0 for mask in forced[False]}}
        for relation, pair in [(True, [0, 1]), (False, [0, 4])]:
            for selected in combinations([v for v in range(9) if v not in pair], 3):
                flag = canonical(5, encode(rook, [*pair, *selected]))
                fixture_forced[relation][flag] += 1
        root_controls = 0
        for u in range(9):
            for v in range(9):
                if u == v:
                    continue
                relation = v in rook[u]
                counts = Counter(canonical(5, encode(rook, [u, v, *selected]))
                                 for selected in combinations([w for w in range(9) if w not in [u, v]], 3))
                need(all(counts[mask] == count for mask, count in fixture_forced[relation].items()), 'all72rook5root universality controls')
                root_controls += 1
        control_rows = reroot_rows(variables, False, 9, 4, fixture_forced)
        fixture_vectors = []
        for u in range(9):
            for v in range(9):
                if u != v and v not in rook[u]:
                    vector = actual_counts(rook, [u, v], variables)
                    need(all(exact_residual(row, vector) == 0 for row in control_rows), 'directrook rooted6 reroot rows')
                    fixture_vectors.append(vector)
        corrupted = list(fixture_vectors[0])
        changed = next(j for j, value in enumerate(corrupted) if value)
        corrupted[changed] += 1
        need(any(exact_residual(row, corrupted) for row in control_rows), 'corrupted fixture count rejected')
        rows = reroot_rows(variables, False, 99, 14, forced)
        save(out/'reroot5_rows.json', rows)
        domain, null = read(DOMAIN), read(NULL)
        origin = [Fraction(*value) for value in domain['origin']]
        basis = [[Fraction(*value) for value in vector] for vector in null['rational_vectors']]
        reduced = []
        for i, row in enumerate(rows):
            constant = exact_residual(row, origin)
            a = sum(value*basis[0][j] for j, value in row['terms'])
            b = sum(value*basis[1][j] for j, value in row['terms'])
            denominator = math_lcm = 1
            import math
            denominator = math.lcm(a.denominator, b.denominator, constant.denominator)
            reduced.append(dict(row_index=i, coefficients=[int(a*denominator), int(b*denominator), int(constant*denominator)], denominator=denominator))
        save(out/'parameter_residuals.json', reduced)
        need(domain['exact_integer_feasible_points'] == [[a, b] for a in range(21) for b in range(10)], 'exactfrozen210 complete selection')
        cases = []
        for a, b in tqdm(domain['exact_integer_feasible_points'], desc='all210 exact profiles', mininterval=5):
            need(not deadline.status()['stop_required'], 'not completed within the allocated budget')
            violations = [row for row in reduced if row['coefficients'][0]*a + row['coefficients'][1]*b + row['coefficients'][2]]
            cases.append(dict(parameters=[a, b], outcome='REFUTED_NECESSARY_PROFILE' if violations else 'SURVIVES',
                first_violated_row=None if not violations else violations[0]['row_index'],
                first_exact_scaled_residual=None if not violations else sum(x*y for x, y in zip(violations[0]['coefficients'], [a, b, 1])),
                violated_row_count=len(violations)))
        save(out/'all210_outcomes.json', cases)
        summary = dict(status='CANDIDATE_EXACT_REROOT5_SCREEN', timestamp=datetime.now(timezone.utc).isoformat(),
            population='All210 frozen prism-free rooted6 nonedge necessary integer count profiles',
            selected=210, attempted=210, completed=210, survivors=sum(case['outcome'] == 'SURVIVES' for case in cases),
            rejected=sum(case['outcome'] != 'SURVIVES' for case in cases), raw_necessary_rows=len(rows),
            nontrivial_parameter_rows=sum(any(row['coefficients']) for row in reduced),
            rook5_roots_checked=root_controls, rook6_nonedge_roots_checked=len(fixture_vectors), corrupted_controls_rejected=True,
            target_resolution='UNKNOWN', independent_verification=None, independent_verification_reason='Pending separate coefficient/derivation/certificate review.',
            limitations=['Conditional local count-profile screen only.', 'Relies on independently established universal5flag theorem and raw counts; no target automorphism.', 'No actual99graph or target-wide denominator.'],
            elapsed_seconds=time.monotonic()-start,
            outputs_sha256={path.relative_to(ROOT).as_posix():sha(path) for path in out.iterdir() if path.is_file()})
        save(out/'summary.json', summary)
        print(json.dumps(summary), flush=True)
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), elapsed_seconds=time.monotonic()-start, target_resolution='UNKNOWN'))
        raise


if __name__ == '__main__':
    main()
