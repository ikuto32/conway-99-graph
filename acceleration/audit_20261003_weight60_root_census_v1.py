"""Different-author dense integer root census check, with no producer imports."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'acceleration/results/20261003_weight60_warm_root_census01'
PINS = {'final_best': ('best.adj', '818314b75fccfa0f3fe702602afb02b6415f3138a770ef15ed0621d189d88836'), 'first_lambda0': ('first_lambda0.adj', 'c95eff815f69c6d7c4122c5c0cde96d8c5124ffec892f3d8a4913ad0b1486f21')}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dense_square(rows):
    n = len(rows)
    need(all(len(row) == n and all(type(value) is int and value in (0, 1) for value in row) for row in rows), 'literal binary square')
    need(all(rows[i][i] == 0 for i in range(n)) and all(rows[i][j] == rows[j][i] for i in range(n) for j in range(n)), 'zero diagonal and symmetry')
    return [[sum(rows[i][k] * rows[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def literal_root(rows, square, r):
    n = len(rows)
    inside = [j for j in range(n) if rows[r][j] == 1]
    outside = [j for j in range(n) if j != r and rows[r][j] == 0]
    edges = [[i, j] for i in inside for j in inside if i < j and rows[i][j]]
    degrees = {str(j): sum(rows[j][i] for i in inside) for j in inside}
    outsiders = []
    for j in outside:
        witnesses = [k for k in range(n) if rows[r][k] == 1 and rows[k][j] == 1]
        need(len(witnesses) == square[r][j], 'literal common-neighbor witness agrees with matrix multiplication')
        outsiders.append(dict(vertex=j, common_neighbor_count=square[r][j], common_neighbors=witnesses, cn2_eligible=square[r][j] == 2))
    return dict(root=r, neighbors=inside, neighbor_count=len(inside), neighborhood_matching_edges=edges, neighborhood_internal_degrees=degrees, neighborhood_is_perfect_matching=len(inside) % 2 == 0 and len(edges) * 2 == len(inside) and all(value == 1 for value in degrees.values()), outside_count=len(outside), outsiders=outsiders, cn2_eligible_outside_vertices=[j for j in outside if square[r][j] == 2], cn2_eligible_count=sum(square[r][j] == 2 for j in outside), mu_row_residual=sum((square[r][j] - 2) ** 2 for j in outside), outside_common_neighbor_histogram={str(value): sum(square[r][j] == value for j in outside) for value in range(len(inside) + 1)})


def controls():
    rows = [[int(i != j and (i // 3 == j // 3 or i % 3 == j % 3)) for j in range(9)] for i in range(9)]
    square = dense_square(rows)
    need(all(square[i][j] == (4 if i == j else 1 if rows[i][j] else 2) for i in range(9) for j in range(9)), 'rook9 exact SRG identity')
    for r in range(9):
        rec = literal_root(rows, square, r)
        need(rec['neighborhood_is_perfect_matching'] and rec['mu_row_residual'] == 0 and rec['cn2_eligible_count'] == 4, 'all nine positive roots')
    negatives = 0
    for i, j, value in ((0, 0, 1), (0, 1, 0), (0, 0, True), (0, 0, 2)):
        corrupt = copy.deepcopy(rows); corrupt[i][j] = value
        try:
            dense_square(corrupt)
        except ValueError:
            negatives += 1
        else:
            raise ValueError('corrupt graph accepted')
    bad = copy.deepcopy(square); bad[0][4] += 1
    try:
        literal_root(rows, bad, 0)
    except ValueError:
        negatives += 1
    else:
        raise ValueError('corrupt common-neighbor matrix accepted')
    return dict(positive_roots=9, strict_negative_controls=negatives, control_timing='Controls completed before full target-artifact inspection; this is a cheap census check after separately calibrated scientific saved-object validation, not a new search gate.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True); parser.add_argument('--seconds', type=float, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exactly2raw99graphs complete198roots, dense integer A squared and313698triangles;120outer100worker20reserve no solver')
    out = args.out.resolve(); need(out.is_relative_to(ROOT), 'bounded output'); out.mkdir(parents=True, exist_ok=False)
    calibration = controls()
    (out / 'calibration.json').write_text(json.dumps(calibration, indent=2) + '\n', encoding='utf8', newline='\n')
    summary_path = RUN / 'summary.json'
    need(digest(summary_path) == 'd3cb54a62bee9145134d472b7c567ff32a5e796dca708c76dfcc057c2e94aa06', 'frozen census discovery')
    summary = json.loads(summary_path.read_bytes()); inputs = {summary_path.relative_to(ROOT).as_posix(): digest(summary_path), Path(__file__).relative_to(ROOT).as_posix(): digest(Path(__file__))}
    checked = []
    for label, (file_name, identity) in PINS.items():
        path = ROOT / 'acceleration/results/20261002_hypergraph_weight60_pilot01/native' / file_name
        need(digest(path) == identity, 'frozen raw matrix')
        lines = path.read_text(encoding='ascii').splitlines(); need(lines[0] == '99' and len(lines) == 100, 'complete raw99matrix')
        rows = [[int(value) for value in line] for line in lines[1:]]; square = dense_square(rows)
        need(all(sum(row) == 14 for row in rows), 'all99degree14')
        expected = [literal_root(rows, square, r) for r in range(99)]
        census_path = RUN / (label + '_census.json'); census = json.loads(census_path.read_bytes())
        need(census['roots'] == expected, 'every dense row record and witness exactly reconstructed')
        jsonl = RUN / (label + '_roots.jsonl'); need([json.loads(line) for line in jsonl.read_text(encoding='utf8').splitlines()] == expected, 'complete duplicated root stream')
        triangle_path = RUN / (label + '_triangles.json'); triangle = json.loads(triangle_path.read_bytes())
        triangles = [[i, j, k] for i, j, k in itertools.combinations(range(99), 3) if rows[i][j] and rows[j][k] and rows[k][i]]
        need(triangle == dict(triple_universe=156849, triangles=triangles), 'all156849literal triples')
        energies = [rec['mu_row_residual'] for rec in expected]; minimum = min(energies); ties = [r for r in range(99) if energies[r] == minimum]
        need(census['minimum_mu_row_residual'] == minimum and census['minimum_root_ties'] == ties and census['selected_root'] == ties[0], 'exact minimum and all ties')
        need(census['global_unordered_mu_energy'] * 2 == sum(energies), 'global and all-root energy consistency')
        need(census['matching_roots'] == [r for r, rec in enumerate(expected) if rec['neighborhood_is_perfect_matching']] and census['all84_cn2_eligible_roots'] == [r for r, rec in enumerate(expected) if rec['cn2_eligible_count'] == 84], 'complete eligibility population')
        need(all(sum(square[r][j] for j in range(99) if j != r and not rows[r][j]) == 168 for r in range(99)), 'all-root exact nonedge mean2')
        checked.append(dict(label=label, matching_roots=len(census['matching_roots']), fully_cn2_roots=len(census['all84_cn2_eligible_roots']), minimum_mu_row_residual=minimum, minimum_root_ties=ties, selected_root=ties[0], triangle_count=len(triangles), global_mu_energy=sum(energies) // 2))
        for artifact in (path, census_path, jsonl, triangle_path): inputs[artifact.relative_to(ROOT).as_posix()] = digest(artifact)
        need(not deadline.status()['stop_required'], 'not completed within the allocated budget')
    report = dict(status='INDEPENDENT_WEIGHT60_TWO_GRAPH_DENSE_ROOT_CENSUS_V1_PASS', timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver', verifier='/root', method='independent_artifact_check', command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=inputs, raw_graphs=2, complete_roots=198, literal_triangle_population=313698, complete_scalar_matrix_entries=19602, graph_records=checked, controls=calibration, target_resolution='NONE', limitations=['Exactly two raw partial graphs; no unrestricted exclusion, graph normalization or SAT equivalence certificate.', 'Discovery bitsets not imported; dense Python integer products and literal neighbor/triple witnesses.', 'No source-commit or transitive historical mathematical replay inferred from current data.'], deadline=deadline.status())
    (out / 'summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(status=report['status'], graph_records=checked)))


if __name__ == '__main__':
    main()
