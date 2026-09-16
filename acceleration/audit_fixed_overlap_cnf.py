"""Independent stdlib audit of the fixed-K label map and appended CNF units.

Does not import the adapter, SAT model producer, solver, or graph helpers.
Base CNF semantics remain conditional on the frozen unrestricted model; this
audits the complete reduction from current K to that model, not a SAT answer.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = '91d22e62625e1221dd46b819e89494db8141dd4ddc9a06f13b9abdb530b83242'
MODEL_SHA = '8c21ac331af1569ee526ae4ddbf2553f6252d544a08b14bebb7fe3fd485489cc'


def require(ok,message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    path = Path(str(name).replace('\\','/'))
    return path if path.is_absolute() else ROOT/path


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def audit(manifest_path):
    manifest = json.loads(manifest_path.read_bytes())
    require(manifest['status'] == 'FIXED_OVERLAP_CNF_ADAPTER_COMPLETE', 'Wrong adapter status')
    bindings = dict(manifest['inputs_sha256'])
    for name,expected in bindings.items():
        require(digest(resolve(name)) == expected, 'Changed adapter input/source')
    for field in ('candidate','base_cnf','cnf','adapter_source','base_model_source'):
        path = resolve(manifest[field+'_path'])
        require(digest(path) == manifest[field+'_sha256'], 'Changed bound '+field)
        bindings[manifest[field+'_path']] = manifest[field+'_sha256']
    require(manifest['base_cnf_sha256'] == BASE_SHA and manifest['base_model_source_sha256'] == MODEL_SHA, 'Unrecognized base model')
    candidate = json.loads(resolve(manifest['candidate_path']).read_bytes())
    # Independently order exact inner-symbol pairs, then group by support.
    legacy = [list(p) for p in combinations(range(14),2) if p[0]//2 != p[1]//2]
    current = sorted(legacy,key=lambda p:(p[0]//2,p[1]//2,p[0],p[1]))
    require(manifest['current_labels'] == current and manifest['legacy_labels'] == legacy, 'Wrong declared labels')
    forward = [legacy.index(label) for label in current]
    reverse = [current.index(label) for label in legacy]
    require(manifest['current_to_legacy_vertices'] == forward and manifest['legacy_to_current_vertices'] == reverse,
            'Incorrect label bijection')
    require(sorted(forward) == list(range(84)) and sum(i != forward[i] for i in range(84)) == manifest['moved_coordinate_indices'] == 60,
            'Incorrect permutation/moved count')
    edges = candidate['overlap_edges_outer_zero_based']
    require(type(edges) is list and len(edges) == 168, 'Wrong K size')
    known = set()
    adj = [set() for _ in range(99)]
    fixed_scaffold = [(0,s) for s in range(1,15)] + [(s,s+1) for s in range(1,15,2)]
    fixed_scaffold += [(s+1,u+15) for u,label in enumerate(current) for s in label]
    for u,v in fixed_scaffold:
        adj[u].add(v); adj[v].add(u)
    for edge in edges:
        require(type(edge) is list and len(edge) == 2 and all(type(v) is int for v in edge), 'Malformed K edge')
        u,v = edge
        require(0 <= u < v < 84 and (u,v) not in known, 'Invalid/repeated K edge')
        require(len({s//2 for s in current[u]} & {s//2 for s in current[v]}) == 1, 'Nonoverlap K edge')
        known.add((u,v)); adj[u+15].add(v+15); adj[v+15].add(u+15)
    require([len(row) for row in adj] == [14]*15+[6]*84, 'Partial degree mismatch')
    for u,v in combinations(range(99),2):
        require(len(adj[u]&adj[v]) <= (1 if v in adj[u] else 2), 'Full99 partial cap violation')
    own_checks = 0
    for u,label in enumerate(current):
        for symbol in range(14):
            if symbol//2 in {s//2 for s in label}:
                require(len(adj[u+15]&adj[symbol+1]) == (1 if symbol in label else 2), 'Own-root quota mismatch')
                own_checks += 1
    # Enumerate in the opposite coordinate order to the adapter. Derive the
    # current edge and its fixed/free semantics independently for every ID.
    expected_units, free = [], []
    pair_records = list(combinations(range(84),2))
    for variable,(a,b) in enumerate(pair_records,1):
        u,v = sorted((reverse[a],reverse[b]))
        intersect = {s//2 for s in legacy[a]} & {s//2 for s in legacy[b]}
        if intersect:
            value = int((u,v) in known)
            expected_units.append(dict(current_edge=[u,v],legacy_edge=[a,b],variable=variable,
                                       value=value,literal=(2*value-1)*variable))
        else:
            free.append(variable)
    require(manifest['fixed_units'] == expected_units and manifest['free_edge_variables'] == free, 'Incorrect semantic unit/free inventory')
    # Check the reverse traversal too: no hidden reorder, omission or duplicate.
    by_current = {tuple(r['current_edge']):r for r in expected_units}
    free_set = set(free)
    for u,v in combinations(range(84),2):
        mapped = tuple(sorted((forward[u],forward[v])))
        identifier = pair_records.index(mapped)+1
        require((u,v) in by_current or identifier in free_set, 'Unrepresented current pair')
        if (u,v) in by_current:
            require(by_current[u,v]['variable'] == identifier, 'Current/legacy variable disagreement')
    require(len(expected_units) == 1806 and sum(r['value'] for r in expected_units) == 168 and len(free) == 1680, 'Wrong fixed/free counts')
    for name,value in dict(edge_variables=3486,base_variables=817278,base_clauses=1622502,
                           output_variables=817278,output_clauses=1624308,appended_unit_count=1806,
                           true_unit_count=168,false_unit_count=1638,free_edge_count=1680).items():
        require(type(manifest[name]) is int and manifest[name] == value, 'Wrong metadata '+name)
    base = resolve(manifest['base_cnf_path']).read_bytes()
    base_header,body = base.split(b'\n',1)
    require(base_header == b'p cnf 817278 1622502', 'Wrong base header')
    suffix = ''.join(str(row['literal'])+' 0\n' for row in expected_units).encode('ascii')
    actual = resolve(manifest['cnf_path']).read_bytes()
    require(actual == b'p cnf 817278 1624308\n'+body+suffix, 'Output CNF is not exactly base body plus expected units')
    require(body.count(b'\n') == 1622502 and all(line.endswith(b' 0') for line in body.splitlines()), 'Unexpected frozen clause layout')
    require(manifest['no_symmetry_branch_added'] is True and manifest['disjoint_block_totals_assumed'] is False,
            'Additional restriction claimed')
    require(manifest['solver_run'] is False and manifest['graph_witness_created'] is False and manifest['general_nonexistence_proved'] is False,
            'Adapter improperly claims a solve/proof')
    bindings[manifest_path.resolve().relative_to(ROOT).as_posix() if manifest_path.resolve().is_relative_to(ROOT) else manifest_path.resolve().as_posix()] = digest(manifest_path)
    bindings[Path(__file__).resolve().relative_to(ROOT).as_posix()] = digest(Path(__file__))
    return dict(status='INDEPENDENT_FIXED_OVERLAP_CNF_MAPPING_AUDIT_PASS',inputs_sha256=bindings,
        candidate_path=manifest['candidate_path'],candidate_sha256=manifest['candidate_sha256'],
        cnf_path=manifest['cnf_path'],cnf_sha256=manifest['cnf_sha256'],
        current_pairs_checked=3486,legacy_pairs_checked=3486,moved_coordinate_indices=60,
        full99_partial_pairs_checked=4851,own_root_quotas_checked=own_checks,
        appended_units=1806,true_units=168,false_units=1638,free_edges=1680,
        base_body_byte_identical=True,no_symmetry_branch_added=True,
        producer_or_solver_imported=False,solver_run=False,graph_witness_created=False,
        known_lp_excluded_control=manifest['known_lp_excluded_control'],
        scope='Exact fixed-K restriction and vertex-coordinate mapping only, relative to the frozen unrestricted CNF. No SAT solve, new exclusion, witness, or general nonexistence claim.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve prior audit')
    result = audit(args.manifest)
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'inputs_sha256'}))


if __name__ == '__main__':
    main()
