"""Append only a complete fixed-K assignment to the frozen unrestricted CNF.

No SAT solver is imported or invoked. Vertex labels, rather than numeric
indices, identify the current support-major and legacy symbol-lex orders.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'scratch_general_exact.cnf'
BASE_SHA = '91d22e62625e1221dd46b819e89494db8141dd4ddc9a06f13b9abdb530b83242'
MODEL_SOURCE = ROOT / 'scratch_general_exact_sat.py'
MODEL_SHA = '8c21ac331af1569ee526ae4ddbf2553f6252d544a08b14bebb7fe3fd485489cc'
BASE_VARIABLES, BASE_CLAUSES = 817278, 1622502


def require(ok, message):
    if not ok:
        raise ValueError(message)


def key(path):
    path = path.resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def prepare(candidate):
    supports = list(combinations(range(7), 2))
    current = [(2*a+s, 2*b+t) for a,b in supports for s in range(2) for t in range(2)]
    legacy = list(sorted(current))
    lookup = {label:i for i,label in enumerate(legacy)}
    forward = [lookup[label] for label in current]
    reverse = [forward.index(i) for i in range(84)]
    pairs = candidate['overlap_edges_outer_zero_based']
    require(type(pairs) is list and len(pairs) == 168, 'Expected exactly 168 K edges')
    known = set()
    adjacency = [set() for _ in range(99)]

    def add(u,v):
        adjacency[u].add(v)
        adjacency[v].add(u)

    for s in range(14):
        add(0, s+1)
    for g in range(7):
        add(2*g+1, 2*g+2)
    for u,label in enumerate(current):
        for s in label:
            add(u+15, s+1)
    for pair in pairs:
        require(type(pair) is list and len(pair) == 2 and all(type(v) is int for v in pair), 'Invalid K edge')
        u,v = pair
        require(0 <= u < v < 84 and (u,v) not in known, 'Repeated or out-of-range K edge')
        require(len(set(supports[u//4]) & set(supports[v//4])) == 1, 'K edge outside overlap domain')
        known.add((u,v))
        add(u+15,v+15)
    require([len(row) for row in adjacency] == [14]*15+[6]*84, 'Incorrect fixed partial degrees')
    for u,v in combinations(range(99),2):
        require(len(adjacency[u]&adjacency[v]) <= (1 if v in adjacency[u] else 2), 'Partial full99 cap violation')
    for u in range(84):
        for s in range(14):
            if s//2 in supports[u//4]:
                require(len(adjacency[u+15]&adjacency[s+1]) == (1 if s in current[u] else 2), 'Own-root quota violation')
    variables = {pair:i for i,pair in enumerate(combinations(range(84),2),1)}
    units, free = [], []
    for u,v in combinations(range(84),2):
        a,b = sorted((forward[u],forward[v]))
        variable = variables[a,b]
        if set(supports[u//4]) & set(supports[v//4]):
            value = int((u,v) in known)
            units.append(dict(current_edge=[u,v], legacy_edge=[a,b], variable=variable,
                              value=value, literal=variable if value else -variable))
        else:
            free.append(variable)
    units.sort(key=lambda row:row['variable'])
    free.sort()
    require(len(units) == 1806 and sum(r['value'] for r in units) == 168 and len(free) == 1680, 'Wrong fixed/free partition')
    require(sum(i != v for i,v in enumerate(forward)) == 60, 'Unexpected coordinate map')
    return current,legacy,forward,reverse,units,free


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--control-known-lp-excluded', action='store_true',
                        help='Label a previously excluded input as an adapter control; does not establish a new exclusion')
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve prior output; choose a fresh directory')
    candidate_bytes = args.candidate.read_bytes()
    current,legacy,forward,reverse,units,free = prepare(json.loads(candidate_bytes))
    base_bytes = BASE.read_bytes()
    require(sha256(base_bytes).hexdigest() == BASE_SHA and digest(MODEL_SOURCE) == MODEL_SHA, 'Frozen base CNF/source changed')
    header,body = base_bytes.split(b'\n',1)
    require(header == f'p cnf {BASE_VARIABLES} {BASE_CLAUSES}'.encode('ascii') and body.endswith(b'\n'), 'Unexpected base layout')
    suffix = ''.join(f"{row['literal']} 0\n" for row in units).encode('ascii')
    output = f'p cnf {BASE_VARIABLES} {BASE_CLAUSES+len(units)}\n'.encode('ascii') + body + suffix
    # All parsing, geometry, and fixed-source checks precede the first write.
    args.out.mkdir(parents=True, exist_ok=False)
    cnf = args.out/'fixed.cnf'
    with cnf.open('xb') as stream:
        stream.write(output)
    manifest = dict(status='FIXED_OVERLAP_CNF_ADAPTER_COMPLETE',
        candidate_path=key(args.candidate), candidate_sha256=sha256(candidate_bytes).hexdigest(),
        base_cnf_path=key(BASE), base_cnf_sha256=BASE_SHA,
        cnf_path=key(cnf), cnf_sha256=sha256(output).hexdigest(),
        adapter_source_path=key(Path(__file__)), adapter_source_sha256=digest(Path(__file__)),
        base_model_source_path=key(MODEL_SOURCE), base_model_source_sha256=MODEL_SHA,
        current_labels=current, legacy_labels=legacy,
        current_to_legacy_vertices=forward, legacy_to_current_vertices=reverse,
        moved_coordinate_indices=60, edge_variables=3486,
        base_variables=BASE_VARIABLES, base_clauses=BASE_CLAUSES,
        output_variables=BASE_VARIABLES, output_clauses=BASE_CLAUSES+1806,
        appended_unit_count=1806, true_unit_count=168, false_unit_count=1638,
        fixed_units=units, free_edge_variables=free, free_edge_count=1680,
        no_symmetry_branch_added=True, disjoint_block_totals_assumed=False,
        known_lp_excluded_control=args.control_known_lp_excluded,
        control_flag_is_prior_user_context_not_new_exclusion=True,
        solver_run=False, graph_witness_created=False, general_nonexistence_proved=False,
        inputs_sha256={key(args.candidate):sha256(candidate_bytes).hexdigest(), key(BASE):BASE_SHA,
                       key(MODEL_SOURCE):MODEL_SHA, key(Path(__file__)):digest(Path(__file__))},
        scope='All completions of this labeled fixed K within the rooted E0=0 representation. Only the 1806 non-disjoint-support edge values are added to the unrestricted base; no C totals or symmetry branch units. No solve, exclusion, or witness is claimed.')
    with (args.out/'manifest.json').open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=manifest['status'], cnf_path=key(cnf),cnf_sha256=manifest['cnf_sha256'],
                         appended_units=1806,free_edges=1680,solver_run=False)))


if __name__ == '__main__':
    main()
