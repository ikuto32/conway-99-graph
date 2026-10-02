"""Unrestricted induced-count relaxation through order eight (discovery only).

Build degree and pair-common-neighbor marked extension identities from raw
archived class streams. No discovery source is imported. Numerical HiGHS
outcomes are explicitly not certificates. The producer cannot approve itself.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

import highspy
import numpy as np
import scipy
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / 'external_conway99_research'
INPUT45 = LEGACY / 'attempts/wave45-flag-moment/checkpoint-v1-moment-coefficients.json'
INPUT147 = LEGACY / 'attempts/wave147-alternative-lane/exact-results.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(obj, stream, indent=2)
        stream.write('\n')


@lru_cache(None)
def pairs(n):
    return tuple(itertools.combinations(range(n), 2))


@lru_cache(None)
def rows(n, mask):
    result = [0] * n
    for bit, (u, v) in enumerate(pairs(n)):
        if (mask >> bit) & 1:
            result[u] |= 1 << v
            result[v] |= 1 << u
    return tuple(result)


def local(n, mask):
    adj = rows(n, mask)
    return all((adj[u] & adj[v]).bit_count() <= (1 if (adj[u] >> v) & 1 else 2)
               for u, v in pairs(n))


@lru_cache(None)
def positions(n):
    return {p: i for i, p in enumerate(pairs(n))}


def remap(n, mask, mapping):
    result = 0
    pos = positions(n)
    for bit, (u, v) in enumerate(pairs(n)):
        if (mask >> bit) & 1:
            a, b = mapping[u], mapping[v]
            result |= 1 << pos[tuple(sorted((a, b)))]
    return result


def degree_maps(n, mask):
    cells = defaultdict(list)
    for u, row in enumerate(rows(n, mask)):
        cells[row.bit_count()].append(u)
    cells = [cells[d] for d in sorted(cells)]
    targets, start = [], 0
    for cell in cells:
        targets.append(tuple(range(start, start + len(cell))))
        start += len(cell)
    for products in itertools.product(*(itertools.permutations(t) for t in targets)):
        mapping = [None] * n
        for old, new in zip(cells, products):
            for u, v in zip(old, new):
                mapping[u] = v
        yield tuple(mapping)


@lru_cache(None)
def canonical(n, mask):
    best, bestmap = None, None
    for mapping in degree_maps(n, mask):
        transformed = remap(n, mask, mapping)
        if best is None or transformed < best:
            best, bestmap = transformed, mapping
    return best, bestmap


@lru_cache(None)
def orbits(n, mask):
    """Automorphisms quotient only marks in this finite induced class."""
    assert canonical(n, mask)[0] == mask
    automorphisms = [m for m in degree_maps(n, mask) if remap(n, mask, m) == mask]
    universe = [tuple([u]) for u in range(n)] + list(pairs(n))
    remaining, result = set(universe), []
    while remaining:
        seed = min(remaining, key=lambda x: (len(x), x))
        orbit = sorted({tuple(sorted(m[u] for u in seed)) for m in automorphisms})
        remaining.difference_update(orbit)
        result.append(tuple(orbit))
    return tuple(result)


def induced(n, mask, vertices):
    adj = rows(n, mask)
    result = 0
    for bit, (i, j) in enumerate(pairs(len(vertices))):
        if (adj[vertices[i]] >> vertices[j]) & 1:
            result |= 1 << bit
    return result


def load_classes():
    data45 = json.loads(INPUT45.read_text())
    data147 = json.loads(INPUT147.read_text())
    classes = {}
    for n in range(1, 4):
        classes[n] = sorted({canonical(n, m)[0] for m in range(1 << math.comb(n, 2)) if local(n, m)})
    # Pair-root matrices stop at order six; the one-root family retains every
    # class through order seven. V1 incorrectly requested the former stream.
    records = data45['families']['vertex']['class_coefficients']
    for n in range(4, 8):
        # Wave45 uses global lexicographic masks while Wave147 order eight uses
        # degree-cell masks. Translate the former explicitly; no raw input edit.
        classes[n] = sorted({canonical(n, int(r['canonical_mask']))[0] for r in records if int(r['order']) == n})
        assert len(classes[n]) == data45['class_streams'][str(n)]['count']
    classes[8] = data147['class_streams']['8']['canonical_masks']
    assert len(classes[8]) == 916
    return classes


def build_model(classes, graph_n, degree, show=True):
    """Return exact integer count rows; each row has RHS zero or fixed counts."""
    variables = [(n, m) for n in range(1, 9) for m in classes[n]]
    index = {key: i for i, key in enumerate(variables)}
    equations = []
    for n in range(1, 9):
        equations.append(dict(kind='total', order=n, mask=None, mark=None,
                              rhs=math.comb(graph_n, n),
                              terms=[[index[n, m], 1] for m in classes[n]]))
    for n in tqdm(range(1, 8), desc='marked-extension layers', disable=not show):
        per_class = {}
        for mask in classes[n]:
            adj = rows(n, mask)
            descriptors = [('deletion', None, graph_n - n)]
            for orbit in orbits(n, mask):
                if len(orbit[0]) == 1:
                    coefficient = sum(degree - adj[u[0]].bit_count() for u in orbit)
                    descriptors.append(('degree', orbit, coefficient))
                else:
                    coefficient = sum((1 if (adj[u] >> v) & 1 else 2)
                                      - (adj[u] & adj[v]).bit_count() for u, v in orbit)
                    descriptors.append(('common_neighbor', orbit, coefficient))
            per_class[mask] = descriptors
        accum = {(mask, i): Counter() for mask in classes[n] for i in range(len(per_class[mask]))}
        for bigger in tqdm(classes[n+1], desc=f'order {n+1} deletions', leave=False, disable=not show):
            adj_big = rows(n + 1, bigger)
            for removed in range(n + 1):
                remaining = tuple(u for u in range(n + 1) if u != removed)
                sub = induced(n + 1, bigger, remaining)
                mask, mapping = canonical(n, sub)
                assert mask in per_class, (n, mask)
                neighbor_set = {mapping[i] for i, u in enumerate(remaining) if (adj_big[removed] >> u) & 1}
                for i, (kind, orbit, _) in enumerate(per_class[mask]):
                    coefficient = (1 if kind == 'deletion' else
                                   sum(all(u in neighbor_set for u in marked) for marked in orbit))
                    if coefficient:
                        accum[mask, i][index[n + 1, bigger]] += coefficient
        for mask in classes[n]:
            for i, (kind, orbit, left) in enumerate(per_class[mask]):
                terms = accum[mask, i]
                if left:
                    terms[index[n, mask]] -= left
                equations.append(dict(kind=kind, order=n, mask=mask,
                                      mark=None if orbit is None else [list(p) for p in orbit],
                                      rhs=0, terms=[[k, v] for k, v in sorted(terms.items()) if v]))
    return dict(format='ORDER8_MARKED_EXTENSION_COUNTS_V1', target=dict(n=graph_n, k=degree, lambda_=1, mu=2),
                variables=[list(x) for x in variables], equations=equations,
                scope='Necessary unrestricted induced-count relaxation; aggregate counts do not construct a graph.',
                graph_automorphism_assumption=False, coefficients='Exact integers in count convention')


def direct_counts(graph_rows, variables):
    n = len(graph_rows)
    counts = Counter()
    for h in range(1, 9):
        for subset in itertools.combinations(range(n), h):
            mask = 0
            for bit, (i, j) in enumerate(pairs(h)):
                if (graph_rows[subset[i]] >> subset[j]) & 1:
                    mask |= 1 << bit
            counts[h, canonical(h, mask)[0]] += 1
    return [counts[tuple(key)] for key in variables]


def residuals(model, counts):
    return [sum(counts[j] * a for j, a in row['terms']) - row['rhs'] for row in model['equations']]


def controls(classes):
    vertices = list(itertools.product(range(3), repeat=2))
    graph_rows = [sum(1 << j for j, v in enumerate(vertices) if u != v and (u[0] == v[0] or u[1] == v[1]))
                  for u in vertices]
    model = build_model(classes, 9, 4, show=False)
    count = direct_counts(graph_rows, model['variables'])
    assert not any(residuals(model, count))
    mutated = count[:]
    mutated[model['variables'].index([2, 1])] += 1
    assert any(residuals(model, mutated))
    damaged = json.loads(json.dumps(model))
    degree_row = next(row for row in damaged['equations'] if row['kind'] == 'degree' and row['order'] == 1)
    degree_row['terms'][0][1] += 1
    assert any(residuals(damaged, count))
    return dict(known_valid='srg(9,4,1,2) rook graph', exact_equation_controls='ALL_PASS',
                altered_edge_count_rejected=True, altered_degree_coefficient_rejected=True,
                independent=False, note='Producer calibration only; separate source review/checking is required.')


def solve(model, out, seconds):
    n = model['target']['n']
    keys = [tuple(x) for x in model['variables']]
    n3_mask = canonical(6, sum(1 << positions(6)[tuple(sorted(e))] for e in
                            [(0,1),(1,2),(0,2),(3,4),(4,5),(3,5),(0,3),(1,4)]))[0]
    n3_index = keys.index((6, n3_mask))
    scale = [math.comb(n, h) for h, _ in keys]
    rr, cc, vv, rhs = [], [], [], []
    for i, row in enumerate(model['equations']):
        normalizer = max([abs(a * scale[j]) for j, a in row['terms']] + [abs(row['rhs']), 1])
        for j, a in row['terms']:
            rr.append(i); cc.append(j); vv.append(a * scale[j] / normalizer)
        rhs.append(row['rhs'] / normalizer)
    matrix = coo_matrix((vv, (rr, cc)), shape=(len(rhs), len(keys))).tocsr()
    summary = []
    for name, sign, endpoint in [('minimum', 1, False), ('maximum', -1, False), ('endpoint4158', 0, True)]:
        objective = np.zeros(len(keys)); objective[n3_index] = sign * scale[n3_index]
        bounds = [(0, None)] * len(keys)
        if endpoint:
            bounds[n3_index] = (4158 / scale[n3_index], 4158 / scale[n3_index])
        start = time.monotonic()
        result = linprog(objective, A_eq=matrix, b_eq=rhs, bounds=bounds, method='highs',
                         options=dict(time_limit=seconds, primal_feasibility_tolerance=1e-9,
                                      dual_feasibility_tolerance=1e-9, presolve=True))
        row = dict(attempt=name, scipy_status=int(result.status), scipy_message=result.message,
                   solver_success=bool(result.success), elapsed_seconds=time.monotonic() - start,
                   certificate_status='CANDIDATE_NUMERICAL_ONLY', exact_certificate=None,
                   exact_certificate_reason='No rational primal or dual certificate is produced by this numerical run.')
        if result.x is not None:
            xcount = [float(value * scale[i]) for i, value in enumerate(result.x)]
            row.update(n3_approximate=xcount[n3_index], maximum_normalized_residual=float(np.max(np.abs(matrix @ result.x - rhs))),
                       minimum_density=float(np.min(result.x)), numerical_nonzero_count=sum(v > 1e-12 for v in result.x))
            save(out / f'{name}_numerical_primal.json', dict(counts=xcount, densities=result.x.tolist(),
                                                         eq_dual=None if result.eqlin.marginals is None else result.eqlin.marginals.tolist(),
                                                         result=row))
        summary.append(row)
        print(json.dumps(row), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--lp-seconds', type=float, default=90)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    source_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    pinned = subprocess.check_output(['git', 'rev-parse', 'HEAD:external_conway99_research'], cwd=ROOT, text=True).strip()
    manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=source_commit,
                    source_sha256=sha(Path(__file__)), command=[sys.executable, *sys.argv], cwd=str(ROOT),
                    legacy_repository='https://github.com/YesterdaysLemon/conway-99-research', legacy_commit=pinned,
                    inputs=[dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for p in [INPUT45, INPUT147, ROOT/'uv.lock', ROOT/'pyproject.toml']],
                    versions=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                                  highs=highspy.Highs().version()), scope='Unrestricted necessary count equations through order eight.',
                    numerical_acceptance='Residuals are diagnostics only; no floating threshold establishes a mathematical result.',
                    independent_verification='Different implementation must reconstruct all rows and check any exact bound/null witness.',
                    random_seed=None, random_seed_reason='Deterministic class/orbit enumeration; no randomized operation.',
                    hardware=platform.platform(), cpu=platform.processor(), no_psd_constraints=True,
                    limitations=['Aggregate counts need not be realizable.', 'Raw historical class completeness is an inherited premise.',
                                 'No SDP or exact proof certificate is produced.'])
    save(args.out / 'manifest.json', manifest)
    classes = load_classes()
    calibration = controls(classes)
    save(args.out / 'producer_controls.json', calibration)
    model = build_model(classes, 99, 14)
    packed = json.dumps(model, separators=(',', ':')).encode()
    with (args.out / 'model.json.gz').open('xb') as stream:
        stream.write(gzip.compress(packed, mtime=0))
    save(args.out / 'model_summary.json', dict(class_counts={str(h):len(m) for h,m in classes.items()},
                                              variables=len(model['variables']), equations=len(model['equations']),
                                              nonzeros=sum(len(r['terms']) for r in model['equations']),
                                              equation_kinds=dict(Counter(r['kind'] for r in model['equations'])),
                                              payload_sha256=hashlib.sha256(packed).hexdigest(),
                                              compressed_sha256=sha(args.out / 'model.json.gz'),
                                              generation_elapsed_seconds=time.monotonic()-start))
    outcomes = solve(model, args.out, args.lp_seconds)
    save(args.out / 'summary.json', dict(status='COMPLETED_INDEPENDENT_VERIFICATION_PENDING',
                                        exact_new_bound=None, target_resolution='UNKNOWN',
                                        outcomes=outcomes, elapsed_seconds=time.monotonic()-start,
                                        outputs=[dict(path=p.name,sha256=sha(p)) for p in sorted(args.out.iterdir()) if p.is_file()]))


if __name__ == '__main__':
    main()
