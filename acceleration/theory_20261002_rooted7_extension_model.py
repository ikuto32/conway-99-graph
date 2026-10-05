"""Fresh exact rooted7 universe and necessary model for all210 local profiles.

Universe completeness uses every one-vertex extension of the independently
checked complete rooted6 nonedge catalogue, not an archived order7 catalogue.
Only permutations of induced free vertices are used, never target automorphisms.
Ordinary extension rows and rerooted conditional rooted6 identities are exact.
"""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
B = ROOT/'acceleration/results'
RAW = B/'20261002_rooted6_prismfree_rigidity'
PARAM = B/'20261002_rooted6_exact_parameter_domain'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


@lru_cache(None)
def edges(n):
    return list(combinations(range(n), 2))


def graph(n, mask):
    adj = [0]*n
    for bit, (u, v) in enumerate(edges(n)):
        if mask >> bit & 1:
            adj[u] |= 1 << v; adj[v] |= 1 << u
    return adj


def encode(adj, order):
    return sum(1 << bit for bit, (u, v) in enumerate(combinations(order, 2)) if adj[u] >> v & 1)


@lru_cache(None)
def transformations(n):
    index = {edge:bit for bit, edge in enumerate(edges(n))}
    result = []
    for free in permutations(range(2, n)):
        order = (0, 1, *free)
        inverse = {vertex:position for position, vertex in enumerate(order)}
        mapping = [index[tuple(sorted([inverse[u], inverse[v]]))] for u, v in edges(n)]
        result.append((order, mapping))
    return result


@lru_cache(None)
def canonical(n, mask):
    active = [bit for bit in range(math.comb(n, 2)) if mask >> bit & 1]
    best, best_order = None, None
    for order, mapping in transformations(n):
        current = sum(1 << mapping[bit] for bit in active)
        if best is None or current < best:
            best, best_order = current, order
    return best, best_order


def admissible(adj):
    return all((adj[u]&adj[v]).bit_count() <= (1 if adj[u] >> v & 1 else 2)
               for u, v in combinations(range(len(adj)), 2))


def prism_on(adj, selected):
    mask = sum(1 << vertex for vertex in selected)
    if any((adj[vertex]&mask).bit_count() != 3 for vertex in selected):
        return False
    first = selected[0]
    for rest in combinations(selected[1:], 2):
        triangle = (first, *rest)
        other = [vertex for vertex in selected if vertex not in triangle]
        if all(adj[u] >> v & 1 for u, v in combinations(triangle, 2)) and all(adj[u] >> v & 1 for u, v in combinations(other, 2)):
            return True
    return False


def prismfree(adj):
    return not any(prism_on(adj, list(selected)) for selected in combinations(range(len(adj)), 6))


def catalogue(six, deadline):
    complete, provenance = set(), []
    labelled_attempts, locally_admissible = 0, 0
    for mask in tqdm(six, desc='all456x64 rooted extensions', mininterval=5):
        need(canonical(6, mask)[0] == mask and not mask & 1, 'canonical nonedge six-class')
        original = graph(6, mask)
        for neighborhood in range(64):
            labelled_attempts += 1
            adj = [*original, neighborhood]
            for vertex in range(6):
                if neighborhood >> vertex & 1:
                    adj[vertex] |= 1 << 6
            if not admissible(adj):
                continue
            locally_admissible += 1
            normalized = canonical(7, encode(adj, range(7)))[0]
            if normalized not in complete:
                complete.add(normalized)
                provenance.append([normalized, mask, neighborhood])
        need(not deadline.status()['stop_required'], 'not completed within the allocated budget')
    complete = sorted(complete)
    conditional = [mask for mask in complete if prismfree(graph(7, mask))]
    return dict(format='COMPLETE_ROOTED7_ONE_VERTEX_AUGMENTATION_V1',
        complete_locally_admissible_masks=complete, prismfree_masks=conditional,
        first_generating_extensions=sorted(provenance), base_six_masks=six,
        labelled_attempts=labelled_attempts, labelled_locally_admissible_extensions=locally_admissible,
        coverage='Every rooted7 flag loses a free vertex to a rooted6 flag; canonicalize only the remaining free vertices, then one of all64 neighborhoods reconstructs it. Each representative is independently locally tested; prismfree subset tests every six-subset.')


def marks(mask):
    adj = graph(6, mask)
    automorphisms = [order for order, _ in transformations(6) if encode(adj, order) == mask]
    pending = {(u,) for u in range(6)} | set(combinations(range(6), 2))
    result = []
    while pending:
        first = min(pending, key=lambda item:(len(item), item))
        orbit = {tuple(sorted(order[u] for u in first)) for order in automorphisms}
        pending -= orbit
        if len(first) == 1:
            result.append(('degree', sorted(orbit)))
        else:
            result.append(('pair_common', sorted(orbit)))
    return result


def extension_rows(six, seven, n, k, lam, mu):
    descriptors, positions, rows = {}, {}, []
    rows.append(dict(kind='order7_total', terms=[[j, 1] for j in range(len(seven))],
        known_terms=[], rhs=math.comb(n-2, 5), rhs_reason='All unordered five-free-vertex subsets per actual ordered primary nonedge.'))
    for mask in six:
        adj = graph(6, mask)
        specifications = [('delete', [], n-6)]
        for kind, orbit in marks(mask):
            left = (sum(k-adj[u].bit_count() for u, in orbit) if kind == 'degree' else
                    sum((lam if adj[u] >> v & 1 else mu)-(adj[u]&adj[v]).bit_count() for u, v in orbit))
            specifications.append((kind, orbit, left))
        descriptors[mask] = specifications
        for kind, orbit, left in specifications:
            positions[mask, kind, tuple(map(tuple, orbit))] = len(rows)
            rows.append(dict(kind=kind, parent6mask=mask, orbit=orbit,
                terms=[], known_terms=[[mask, -left]] if left else [], rhs=0))
    coefficients = [Counter() for _ in rows]
    for j, mask in enumerate(tqdm(seven, desc='all exact extension coefficients', mininterval=5)):
        adj = graph(7, mask)
        for deleted in range(2, 7):
            remaining = [u for u in range(7) if u != deleted]
            raw = encode(adj, remaining)
            parent, order = canonical(6, raw)
            mapping = [remaining[u] for u in order]
            for kind, orbit, _ in descriptors[parent]:
                if kind == 'delete':
                    contribution = 1
                elif kind == 'degree':
                    contribution = sum(adj[deleted] >> mapping[u] & 1 for u, in orbit)
                else:
                    contribution = sum((adj[deleted] >> mapping[u] & 1) and (adj[deleted] >> mapping[v] & 1) for u, v in orbit)
                if contribution:
                    coefficients[positions[parent, kind, tuple(map(tuple, orbit))]][j] += contribution
    for i in range(1, len(rows)):
        rows[i]['terms'] = [[j, value] for j, value in sorted(coefficients[i].items())]
    return rows


def reroot_rows(six, seven, cardinalities, edge_counts, nonedge_origin, nonedge_basis, aggregates):
    rows, positions = [], {}
    for anchor in [0, 1]:
        for partition in range(4):
            adjacent = bool(partition & 1 << anchor)
            counts = edge_counts if adjacent else nonedge_origin
            for flag, constant in sorted(counts.items()):
                terms = []
                if not adjacent and aggregates:
                    for coordinate in range(2):
                        coefficient = nonedge_basis[coordinate][flag]
                        if coefficient:
                            terms.append([aggregates[anchor, partition, coordinate], -coefficient])
                positions[anchor, partition, flag] = len(rows)
                rows.append(dict(kind='reroot6', anchor=anchor, partition=partition,
                    relation='edge' if adjacent else 'nonedge', new_root6mask=flag,
                    terms=terms, known_terms=[], rhs=cardinalities[partition]*constant))
    coefficients = [Counter(dict(row['terms'])) for row in rows]
    known = [Counter() for _ in rows]
    for h, masks in [(6, six), (7, seven)]:
        for j, mask in enumerate(masks):
            adj = graph(h, mask)
            for anchor in [0, 1]:
                for marked in range(2, h):
                    partition = int(adj[0] >> marked & 1)+2*int(adj[1] >> marked & 1)
                    rest = [u for u in range(h) if u not in [anchor, marked] and (h == 6 or u != 1-anchor)]
                    order = [anchor, marked, *rest]
                    need(len(order) == 6, 'reroot6 union/collision size')
                    flag = canonical(6, encode(adj, order))[0]
                    row = positions[anchor, partition, flag]
                    if h == 6:
                        known[row][mask] += 1
                    else:
                        coefficients[row][j] += 1
    for row, terms, collision in zip(rows, coefficients, known):
        row['terms'] = [[j, coefficient] for j, coefficient in sorted(terms.items()) if coefficient]
        row['known_terms'] = [[mask, coefficient] for mask, coefficient in sorted(collision.items())]
    return rows


def actual_counts(adj, root, h, catalogue_masks):
    counts = Counter()
    free = [u for u in range(len(adj)) if u not in root]
    for subset in combinations(free, h-2):
        counts[canonical(h, encode(adj, [*root, *subset]))[0]] += 1
    need(set(counts) <= set(catalogue_masks), 'every actual induced flag in fresh catalogue')
    return {mask:counts[mask] for mask in catalogue_masks}


def residual(row, unknown, known):
    return sum(value*unknown[j] for j, value in row['terms']) + sum(value*known[mask] for mask, value in row['known_terms'])-row['rhs']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Complete456x64augmentation and exact rooted7 sparse rows with Petersencontrols; expectedseconds to minutes, reserve60.')
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    try:
        inputs = [RAW/'ordered_nonedge_model.json', RAW/'ordered_edge_model.json', RAW/'ordered_edge_prismfree_primal.json',
                  PARAM/'prismfree_nonedge_domain.json', PARAM/'prismfree_nonedge_nullspace.json',
                  B/'20261002_independent_review/rooted6_nonedge_domain01/summary.json',
                  B/'20261002_independent_review/rooted6_prismfree02/summary.json',
                  Path(__file__), ROOT/'pyproject.toml', ROOT/'uv.lock', ROOT/'acceleration/command_deadline.py']
        pins = {path.relative_to(ROOT).as_posix():sha(path) for path in inputs}
        manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), inputs_sha256=pins,
            question='Can all210 necessary prismfree rooted6 nonedge count profiles extend to rooted7 counts satisfying exact extension and rerooted6 identities?',
            selection='All210 rectangle profiles a0..20,b0..9. Build complete rooted7 universe from all456 independently checked rooted6 classes and all64 neighborhoods.',
            success_criterion='Complete fresh catalogue with generating-extension evidence, exact sparse necessary rows, exact affine parameter RHS, direct knownvalid fixture controls before subsequent feasibility tests.',
            falsification_criterion='Any missing actual fixture flag, failed exact control row, altered source/input, or unaccounted augmentation vetoes model use.',
            verification_requirement='Independent catalogue/coverage and coefficient/derivation replay before promoting any exclusion.',
            scope='Conditional prismfree necessary count relaxation only. No target automorphism, archived order7 universe, numerical feasibility or target coverage conclusion.',
            dependencies=[dict(id='C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY', revision=1, relation='uses_result', reason='Foundation for separately checked rooted6 profiles; no direct root5 novelty claimed.')])
        save(out/'manifest.json', manifest)
        data = read(RAW/'ordered_nonedge_model.json')
        six = [mask for h, mask in data['variables'] if h == 6]
        need(len(six) == 456, 'frozen complete456rooted6nonedgepopulation')
        catalog = catalogue(six, deadline)
        save(out/'catalogue.json', catalog)
        seven = catalog['prismfree_masks']
        rows = extension_rows(six, seven, 99, 14, 1, 2)
        # Prismfree Petersen(10,3,0,1) fixture, with every pair relation and
        # root counted directly. This controls counting logic, not the target.
        petersen = [0]*10
        for u in range(5):
            for v in [(u+1)%5, u+5]:
                petersen[u] |= 1 << v; petersen[v] |= 1 << u
            v = (u+2)%5+5
            petersen[u+5] |= 1 << v; petersen[v] |= 1 << (u+5)
        need(all(adj.bit_count() == 3 for adj in petersen) and all((petersen[u]&petersen[v]).bit_count() == (0 if petersen[u] >> v & 1 else 1) for u, v in combinations(range(10), 2)) and prismfree(petersen), 'knownvalid prismfree Petersen fixture')
        fixture_rows = extension_rows(six, seven, 10, 3, 0, 1)
        fixture_vectors, known_vectors = [], []
        for u in range(10):
            for v in range(10):
                if u != v and not petersen[u] >> v & 1:
                    known = actual_counts(petersen, [u, v], 6, six)
                    unknown = actual_counts(petersen, [u, v], 7, seven)
                    vector = [unknown[mask] for mask in seven]
                    need(all(residual(row, vector, known) == 0 for row in fixture_rows), 'every directPetersen extension row')
                    fixture_vectors.append(vector); known_vectors.append(known)
        edge_data = read(RAW/'ordered_edge_model.json')
        edge_values = read(RAW/'ordered_edge_prismfree_primal.json')['exact_primal']
        edge_counts = {mask:edge_values[j] for j, (h, mask) in enumerate(edge_data['variables']) if h == 6}
        domain, null = read(PARAM/'prismfree_nonedge_domain.json'), read(PARAM/'prismfree_nonedge_nullspace.json')
        origin_all = [Fraction(*value) for value in domain['origin']]
        basis_all = [[Fraction(*value) for value in vector] for vector in null['rational_vectors']]
        origin = {mask:origin_all[j] for j, (h, mask) in enumerate(data['variables']) if h == 6}
        basis = [{mask:vector[j] for j, (h, mask) in enumerate(data['variables']) if h == 6} for vector in basis_all]
        need(all(value.denominator == 1 for values in [origin, *basis] for value in values.values()), 'integer affine profile basis')
        origin = {mask:int(value) for mask, value in origin.items()}
        basis = [{mask:int(value) for mask, value in values.items()} for values in basis]
        cardinalities = {0:71, 1:12, 2:12, 3:2}
        aggregates, variables = {}, [[7, mask] for mask in seven]
        for anchor in [0, 1]:
            for partition in range(4):
                if not partition & 1 << anchor:
                    for coordinate in range(2):
                        aggregates[anchor, partition, coordinate] = len(variables)
                        variables.append(['aggregate', anchor, partition, coordinate])
        rows += reroot_rows(six, seven, cardinalities, edge_counts, origin, basis, aggregates)
        for (anchor, partition, coordinate), j in aggregates.items():
            slack = len(variables); variables.append(['aggregate_slack', anchor, partition, coordinate])
            rows.append(dict(kind='aggregate_rectangle_bound', anchor=anchor, partition=partition, coordinate=coordinate,
                terms=[[j, 1], [slack, 1]], known_terms=[], rhs=cardinalities[partition]*(20 if coordinate == 0 else 9)))
        edge_six = [mask for h, mask in edge_data['variables'] if h == 6]
        fixture_edge = actual_counts(petersen, [0, 1], 6, edge_six)
        fixture_nonedge = known_vectors[0]
        for u in range(10):
            for v in range(10):
                if u != v:
                    actual = actual_counts(petersen, [u, v], 6, edge_six if petersen[u] >> v & 1 else six)
                    need(actual == (fixture_edge if petersen[u] >> v & 1 else fixture_nonedge), 'all90Petersenroot6directuniformity control')
        fixture_reroot = reroot_rows(six, seven, {0:3, 1:2, 2:2, 3:1}, fixture_edge, fixture_nonedge,
                                    [{mask:0 for mask in six}, {mask:0 for mask in six}], {})
        for vector, known in zip(fixture_vectors, known_vectors):
            need(all(residual(row, vector, known) == 0 for row in fixture_reroot), 'all60Petersen reroot6 rootcontrols')
        bad = list(fixture_vectors[0]); bad[0] += 1
        need(any(residual(row, bad, known_vectors[0]) for row in fixture_rows), 'corruptedPetersen7count rejected')
        # Fixed lower counts x6=origin+a*basis0+b*basis1 move to RHS.
        equations = []
        for row in rows:
            rhs = [row['rhs']-sum(value*origin[mask] for mask, value in row['known_terms']),
                   -sum(value*basis[0][mask] for mask, value in row['known_terms']),
                   -sum(value*basis[1][mask] for mask, value in row['known_terms'])]
            equations.append(dict(terms=row['terms'], rhs_affine=rhs))
        model = dict(format='ROOTED7_CONDITIONAL_EXTENSION_AFFINE_MODEL_V1', variables=variables,
            equations=equations, row_derivation_descriptors=rows,
            feasible_domain='All variables nonnegative integers for actual graph counts; continuous relaxation used only when explicitly stated.',
            parameter_domain=[[0,20],[0,9]], parameters='Actual rooted6 masks8024and15540 counts a,b per primary ordered nonedge.',
            premise='Hypothetical target with no induced triangular prism; no automorphism is assumed.',
            root6_profile_basis=dict(origin=origin, basis=basis),
            scope='Necessary rooted7 count extension and rerooted conditionalroot6 constraints, not graph realization or target-level resolution.')
        save(out/'model.json', model)
        summary = dict(status='CANDIDATE_ROOTED7_EXTENSION_MODEL', timestamp=datetime.now(timezone.utc).isoformat(),
            complete_locally_admissible_root7_classes=len(catalog['complete_locally_admissible_masks']),
            conditional_prismfree_root7_classes=len(seven), augmentation_attempts=catalog['labelled_attempts'],
            variables=len(variables), rows=len(rows), nonzero_coefficients=sum(len(row['terms']) for row in equations),
            petersen_primary_nonedge_roots_checked=len(fixture_vectors), petersen_root6_uniformity_roots_checked=90,
            corrupted_controls_rejected=True, profile_population=210, profile_evaluations=0,
            target_resolution='UNKNOWN', independent_review=None, independent_review_reason='Pending separate coverage/coefficient audit.',
            elapsed_seconds=time.monotonic()-start,
            outputs_sha256={path.relative_to(ROOT).as_posix():sha(path) for path in out.iterdir() if path.is_file()})
        save(out/'summary.json', summary); print(json.dumps(summary), flush=True)
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), elapsed_seconds=time.monotonic()-start, target_resolution='UNKNOWN'))
        raise


if __name__ == '__main__':
    main()
