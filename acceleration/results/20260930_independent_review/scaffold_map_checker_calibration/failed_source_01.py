"""Independent raw scaffold/variable/degree-map audit; no producer imports."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COORDINATES = ((0,0),(1,1),(1,2),(2,1),(2,2))


def need(condition,message):
    if not condition:raise ValueError(message)


def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()


def raw_specification(star):
    mask = [[0]*59 for _ in range(59)]
    for u,v in combinations(range(9),2):
        mask[u][v] = mask[v][u] = int(u//3 == v//3 or u%3 == v%3)
    for cell,(r,c) in enumerate(COORDINATES):
        owner = 3*r+c
        for external in range(10*cell,10*cell+10):mask[owner][external+9] = mask[external+9][owner] = 1
    for u,v in combinations(range(19,59),2):mask[u][v] = mask[v][u] = -1
    need(len(star['matching']) == 5 and sorted(v for pair in star['matching'] for v in pair) == list(range(10)),'raw central matching')
    for u,v in star['matching']:mask[u+9][v+9] = mask[v+9][u+9] = 1
    need(len(star['four_factors']) == 4,'four raw central incidence blocks')
    for cell,record in enumerate(star['four_factors'],1):
        matrix = record['incidence_block']
        need(len(matrix) == 10 and all(len(row) == 10 and all(type(x) is int and x in (0,1) for x in row) for row in matrix),'raw binary incidence shape')
        need(all(sum(row) == 2 for row in matrix) and all(sum(matrix[i][j] for i in range(10)) == 2 for j in range(10)),'raw incidence two-regularity')
        for i in range(10):
            for j in range(10):mask[i+9][10*cell+j+9] = mask[10*cell+j+9][i+9] = matrix[i][j]
    return mask


def model_structure(model,mask):
    need(model['known_adjacency'] == [row[9:] for row in mask[9:]],'model fixed/free bytes versus raw star')
    need(model['cell_rook_coordinates'] == [list(x) for x in COORDINATES],'exact attachment cells')
    by_pair,by_variable = {},{}
    for row in model['edge_variables']:
        variable,u,v = row['id'],row['u']+9,row['v']+9
        need(type(variable) is int and variable not in by_variable and (u,v) not in by_pair and 19 <= u < v < 59,'unique free variable map')
        by_pair[u,v],by_variable[variable] = variable,(u,v)
    need(set(by_pair) == set(combinations(range(19,59),2)) and set(by_variable) == set(range(1,781)),'complete780edge variable universe')
    expected = []
    for cell in range(1,5):
        vertices = list(range(10*cell+9,10*cell+19))
        for u in vertices:expected.append((1,tuple(sorted(by_pair[tuple(sorted((u,v)))] for v in vertices if u != v))))
    for a,b in combinations(range(1,5),2):
        left,right = list(range(10*a+9,10*a+19)),list(range(10*b+9,10*b+19))
        degree = 1 if (COORDINATES[a][0] == COORDINATES[b][0] or COORDINATES[a][1] == COORDINATES[b][1]) else 2
        for u in left:expected.append((degree,tuple(sorted(by_pair[u,v] for v in right))))
        for v in right:expected.append((degree,tuple(sorted(by_pair[u,v] for u in left))))
    degrees = Counter((row['value'],tuple(sorted(row['variables']))) for row in model['degree_constraints'])
    need(degrees == Counter(expected) and sum(degrees.values()) == 160,'all independently reconstructed160degree rows')
    shared = [[sum(mask[u+9][w]*mask[v+9][w] for w in range(9)) for v in range(50)] for u in range(50)]
    need(shared == model['shared_core_common_neighbors'],'raw core common-neighbor ownership matrix')
    return by_pair,by_variable,degrees,shared


def check_map(record,mask,by_pair,by_variable,degrees,shared):
    p = record['full59']
    need(len(p) == 59 and all(type(x) is int for x in p) and set(p) == set(range(59)),'full59 permutation')
    need(p[0] == 0 and set(p[:9]) == set(range(9)) and set(p[9:19]) == set(range(9,19)),'root/core/designated central cell preserved')
    need(record['core'] == p[:9] and record['central'] == [v-9 for v in p[9:19]],'core/central metadata matches raw permutation')
    cells = []
    for cell in range(5):
        images = p[9+10*cell:19+10*cell]
        target_cells = {(x-9)//10 for x in images}
        need(len(target_cells) == 1,'ownership cell maps to a complete cell')
        cells.append(next(iter(target_cells)))
    need(record['cells'] == cells and sorted(cells) == list(range(5)),'cell permutation metadata')
    for u in range(59):
        for v in range(59):need(mask[u][v] == mask[p[u]][p[v]],'raw59fixed/free adjacency not preserved')
    edge_map = {variable:by_pair[tuple(sorted((p[u],p[v])))] for variable,(u,v) in by_variable.items()}
    need(set(edge_map.values()) == set(range(1,781)),'780edge image bijection')
    need(record['edge_variable_map'] == [edge_map[v] for v in range(1,781)],'saved edge images disagree with raw vertex permutation')
    transformed = Counter()
    for (degree,variables),multiplicity in degrees.items():transformed[degree,tuple(sorted(edge_map[v] for v in variables))] += multiplicity
    need(transformed == degrees,'degree rows and prescribed values not preserved')
    for u in range(50):
        for v in range(50):need(shared[u][v] == shared[p[u+9]-9][p[v+9]-9],'shared core contribution not preserved')
    return dict(full59=p,edge_variable_map=record['edge_variable_map'],full_fixed_free_entries_checked=59*59,
                free_variable_images_checked=780,degree_rows_checked=160,core_shared_entries_checked=50*50,
                root_core_central_matching_incidence_and_cells_preserved=True)


def controls(mask,by_pair,by_variable,degrees,shared,model):
    identity = dict(full59=list(range(59)),core=list(range(9)),central=list(range(10)),cells=list(range(5)),edge_variable_map=list(range(1,781)))
    check_map(identity,mask,by_pair,by_variable,degrees,shared)
    rejected = []
    for name in ('duplicate_vertex','move_root','wrong_central_swap','wrong_right_swap','wrong_edge_variable_map','wrong_core_metadata','move_free_to_fixed'):
        bad = deepcopy(identity)
        if name == 'duplicate_vertex':bad['full59'][-1] = 57
        elif name == 'move_root':bad['full59'][0],bad['full59'][1] = 1,0;bad['core'] = bad['full59'][:9]
        elif name == 'wrong_central_swap':
            bad['full59'][9],bad['full59'][10] = 10,9;bad['central'] = [v-9 for v in bad['full59'][9:19]]
        elif name == 'wrong_right_swap':bad['full59'][19],bad['full59'][20] = 20,19
        elif name == 'wrong_edge_variable_map':bad['edge_variable_map'][0],bad['edge_variable_map'][1] = 2,1
        elif name == 'wrong_core_metadata':bad['core'][1],bad['core'][2] = 2,1
        else:bad['full59'][9],bad['full59'][19] = 19,9
        try:check_map(bad,mask,by_pair,by_variable,degrees,shared)
        except (ValueError,KeyError):rejected.append(name)
        else:raise ValueError('corrupted scaffold map accepted: '+name)
    bad_model = deepcopy(model);bad_model['degree_constraints'][0]['value'] += 1
    try:model_structure(bad_model,mask)
    except ValueError:rejected.append('wrong_degree_value')
    else:raise ValueError('corrupted degree specification accepted')
    return dict(identity_permutation_accepted=True,corruptions_rejected=rejected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args();need(not args.out.exists(),'refuse overwrite')
    bindings = {}
    def read(path,expected=None):
        observed = digest(path);need(expected is None or expected == observed,'artifact hash mismatch: '+str(path))
        bindings[key(path)] = observed;return json.loads(Path(path).read_bytes())
    model_path = ROOT/'acceleration/results/20260930_rook_free_internal_sat/model.json'
    star_path = ROOT/'acceleration/results/20260930_rook_cell_factors/local_witness.json'
    gate_path = ROOT/'acceleration/results/20260930_rook_free_internal_sat/independent_cnf_encoding.json'
    read(gate_path,'a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0')
    model = read(model_path,'26908e992235e307cfc6145275deb3d2765a930c7c59a774c9a7bc42f2f0f95e')
    star = read(star_path,'da71c5381af0a68f8a7e7dea36535b92cbcfc67d95e3b57d6cc3591dd1dda33f')
    records = read(args.maps,'026d223aff6341bdefe8a9cb2c4401cfd644e5c6a59420a334d8c1e75363400b')['maps']
    mask = raw_specification(star)
    by_pair,by_variable,degrees,shared = model_structure(model,mask)
    calibration = controls(mask,by_pair,by_variable,degrees,shared,model)
    checked = [dict(index=index,**check_map(record,mask,by_pair,by_variable,degrees,shared)) for index,record in enumerate(records)]
    maps = {tuple(row['full59']) for row in checked}
    need(len(checked) == len(maps) == 32,'exact32distinct supplied maps')
    identity_present = tuple(range(59)) in maps
    closure = all(tuple(p[q[v]] for v in range(59)) in maps for p in maps for q in maps)
    need(identity_present and closure,'observed supplied-map composition closure')
    derivation = ROOT/'docs/DERIVATION_20260930_SCAFFOLD_CUT_TRANSPORT.md'
    for path in (Path(__file__),derivation,ROOT/'uv.lock'):bindings[key(path)] = digest(path)
    need(all(digest(ROOT/name) == value for name,value in bindings.items()),'stable artifacts')
    report = dict(status='INDEPENDENT_ROOK_SCAFFOLD_RELABELINGS32_PASS',claim_id='C-ROOK-FOUR-FACTOR-SCAFFOLD-RELABELINGS32',claim_revision=1,
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  verifier='/root/eight_domain_audit independent checking agent',verification_type='Direct reconstruction from raw star and exhaustive entry/variable/degree checks for every supplied map',
                  inputs_sha256=bindings,raw_maps_sha256=digest(args.maps),maps_checked=32,distinct_maps=32,checked_maps=checked,controls=calibration,
                  known_unordered_edges=sum(mask[u][v] == 1 for u,v in combinations(range(59),2)),free_unordered_pairs=780,
                  observed_set_has_identity=identity_present,observed_set_closed_under_composition=closure,
                  statement='Each of the32explicit saved permutations preserves the designated root/core/central cell and the complete raw59fixed/free scaffold, induces the recorded780edge-variable bijection, and preserves all160degree rows and core common-neighbor contributions. Each can therefore transport any independently established edge clause valid for every target extension of this scaffold.',
                  scope='The exact32supplied maps in this one frozen family; no census completeness or hypothetical-target automorphism assertion.',
                  dependencies=[dict(id='C-FIXED-SCAFFOLD-RELABELING-CUT-TRANSPORT',revision=1,relation='uses_result'),
                                dict(id='C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING',revision=1,relation='encoding_equivalence')],
                  general_transport_derivation=key(derivation),basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',
                  producer_imported=False,shared_components=['Python standard library; raw pinned model and star artifacts only'],
                  limitations=['Producer30,720pair census completeness is not independently checked here; no claim that these are every scaffold automorphism.',
                               'Only780edge variables are mapped; no auxiliary AND-variable or rawCNF clause permutation is asserted.',
                               'Source clauses require their own independent validity evidence before transport.',
                               'No nontrivial automorphism of any hypothetical target is assumed or deduced.'],
                  target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=report['status'],maps_checked=32,sha256=digest(args.out))))


if __name__ == '__main__':main()
