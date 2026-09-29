"""Independent frozen-rook-window CNF semantics and complete clause audit.

Reconstruct symbolic common-neighbor polynomials from the raw star, identify
each required monomial, then compare the entire unordered clause multiset.
No producer/solver imports. This validates an encoding, not SAT or UNSAT.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import audit_20260930_rook_window_graph_v1 as graphcheck

ROOT = Path(__file__).resolve().parents[1]


def need(condition,message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def normalize(clause):
    need(all(type(lit) is int and lit != 0 for lit in clause),'literal type/zero')
    need(len(clause) == len(set(clause)) and not any(-lit in clause for lit in clause),'duplicate/tautological clause')
    return tuple(sorted(clause))


def at_most(variables,bound):
    need(len(variables) == len(set(variables)) and all(type(v) is int and v > 0 for v in variables),'distinct positive card vars')
    if bound < 0:
        return [()]
    if bound >= len(variables):
        return []
    return [normalize([-v for v in subset]) for subset in combinations(variables,bound+1)]


def exactly(variables,value):
    if not 0 <= value <= len(variables):
        return [()]
    return at_most(variables,value)+[normalize(list(subset)) for subset in combinations(variables,len(variables)-value+1)]


def truth(clauses,assignment):
    return all(any(assignment[abs(lit)] == (lit > 0) for lit in clause) for clause in clauses)


def cardinal_controls():
    checks = 0
    for n in range(7):
        variables = list(range(1,n+1))
        for values in product((False,True),repeat=n):
            assignment = dict(zip(variables,values))
            for bound in range(-1,n+2):
                need(truth(at_most(variables,bound),assignment) == (sum(values) <= bound),'at-most truth table')
                need(truth(exactly(variables,bound),assignment) == (sum(values) == bound),'exactly truth table')
                checks += 2
    for x,y,z in product((False,True),repeat=3):
        gates = [(-3,1),(-3,2),(3,-1,-2)]
        need(truth(gates,{1:x,2:y,3:z}) == (z == (x and y)),'AND equivalence truth table')
    return dict(cardinality_cases=checks,and_gate_cases=8)


def semantics(model,known,shared,expected_degrees):
    n = len(known)
    need(model['known_adjacency'] == known and model['shared_core_common_neighbors'] == shared,'raw known adjacency or shared-core constants')
    raw_edges = model['edge_variables']
    expected_edges = [(u,v) for u,v in combinations(range(n),2) if known[u][v] == -1]
    need([(row['u'],row['v']) for row in raw_edges] == expected_edges,'all independent edge variables')
    need([row['id'] for row in raw_edges] == list(range(1,len(raw_edges)+1)),'edge ID bijection')
    ids = {(row['u'],row['v']):row['id'] for row in raw_edges}
    degrees = expected_degrees(ids)
    need(len(model['degree_constraints']) == len(degrees),'degree row count')
    degree_signature = lambda row:(tuple(sorted(row['variables'])),row['value'],tuple(row['label']))
    need(Counter(degree_signature(row) for row in model['degree_constraints']) == Counter(degree_signature(row) for row in degrees),'complete degree rows')
    products = model['products']
    need([row['id'] for row in products] == list(range(len(ids)+1,len(ids)+len(products)+1)),'auxiliary ID bijection')
    product_map = {}
    for row in products:
        left,right = row['left'],row['right']
        need(type(left) is int and type(right) is int and 1 <= left < right <= len(ids),'product input edge scope')
        need((left,right) not in product_map,'duplicate product definition')
        product_map[(left,right)] = row['id']

    def edge_term(u,v):
        if known[u][v] != -1:
            return known[u][v],()
        return 1,(ids[tuple(sorted((u,v)))],)

    pair_records = model['pair_constraints']
    need([(row['u'],row['v']) for row in pair_records] == list(combinations(range(n),2)),'complete pair coverage')
    used_products = set()
    expected_rows = []
    for record in pair_records:
        u,v = record['u'],record['v']
        monomials = Counter({():shared[u][v]})
        coefficient,variables = edge_term(u,v)
        monomials[variables] += coefficient
        for w in range(n):
            first,left = edge_term(u,w)
            second,right = edge_term(v,w)
            if first*second:
                factors = tuple(sorted(left+right))
                need(len(factors) == len(set(factors)),'repeated factor within path')
                monomials[factors] += first*second
        constant = monomials.pop((),0)
        literals = []
        for factors,multiplicity in monomials.items():
            if not multiplicity:
                continue
            need(multiplicity == 1,'weighted cardinality silently flattened')
            if len(factors) == 1:
                literals.append(factors[0])
            else:
                need(len(factors) == 2 and factors in product_map,'missing exact path product')
                used_products.add(factors)
                literals.append(product_map[factors])
        need(len(literals) == len(set(literals)),'pair literals duplicated')
        need(record['constant'] == constant and record['bound'] == 2-constant
             and sorted(record['literals']) == sorted(literals),'exact pair polynomial')
        expected_rows.append((literals,2-constant))
    need(used_products == set(product_map),'missing or extraneous product universe')
    clauses = Counter()
    for row in degrees:
        clauses.update(exactly(row['variables'],row['value']))
    degree_clause_count = sum(clauses.values())
    for (left,right),z in product_map.items():
        clauses.update([normalize([-z,left]),normalize([-z,right]),normalize([z,-left,-right])])
    for literals,bound in expected_rows:
        clauses.update(at_most(sorted(literals),bound))
    need(model['variables'] == len(ids)+len(products) and model['clauses'] == sum(clauses.values())
         and model['degree_clause_count'] == degree_clause_count and model['product_clause_count'] == 3*len(products),'model clause counts')
    return clauses,ids,product_map


def check_dimacs(path,clauses,variables):
    remaining = clauses.copy()
    count = 0
    header = None
    with Path(path).open('r',encoding='ascii') as stream:
        for line in stream:
            parts = line.split()
            if not parts or parts[0] == 'c':
                continue
            if parts[0] == 'p':
                need(header is None and parts == ['p','cnf',str(variables),str(sum(clauses.values()))],'DIMACS header')
                header = parts
                continue
            need(header is not None,'clause before header')
            values = list(map(int,parts))
            need(values and values[-1] == 0 and all(0 < abs(v) <= variables for v in values[:-1]),'DIMACS clause bounds')
            clause = normalize(values[:-1])
            need(remaining[clause] > 0,'unexpected or excess clause')
            remaining[clause] -= 1
            count += 1
    need(header is not None and count == sum(clauses.values()) and not any(remaining.values()),'missing clauses')
    return count


def evaluate_graph(model,clauses,graph):
    assignment = {row['id']:bool(graph[row['u']][row['v']]) for row in model['edge_variables']}
    for row in model['products']:
        assignment[row['id']] = assignment[row['left']] and assignment[row['right']]
    failed = sum(multiplicity for clause,multiplicity in clauses.items() if not truth([clause],assignment))
    return assignment,failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--star',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    need(not args.out.exists(),'refuse overwrite')
    started = time.monotonic()
    bindings = {}
    def read(path):
        bindings[str(path)] = digest(path)
        return json.loads(Path(path).read_bytes())
    need(digest(args.star) == graphcheck.STAR_HASH,'frozen star hash')
    star = read(args.star)
    summary = read(args.run/'summary.json')
    manifest = read(args.run/'manifest.json')
    for path,expected in manifest['input_hashes'].items():
        need(digest(ROOT/path) == expected,'producer input hash')
        bindings[path] = expected
    for name,record in summary['outputs'].items():
        path = args.run/name
        need(digest(path) == record['sha256'] and path.stat().st_size == record['bytes'],'producer output hash/size')
        bindings[str(path)] = record['sha256']
    controls = cardinal_controls()
    controls['raw59'] = graphcheck.controls(star)
    rook_model = read(args.run/'rook_control_model.json')
    rook_payload = read(args.run/'rook_control_assignment.json')
    rook = [[int(u != v and (u//3 == v//3 or u%3 == v%3)) for v in range(9)] for u in range(9)]
    need(rook_payload['adjacency'] == rook,'known-valid rook adjacency identity')
    known9 = [[0 if u == v else -1 for v in range(9)] for u in range(9)]
    def rook_degrees(ids):
        return [dict(variables=[ids[tuple(sorted((u,v)))] for v in range(9) if v != u],value=4,label=[u]) for u in range(9)]
    rook_clauses,_,_ = semantics(rook_model,known9,[[0]*9 for _ in range(9)],rook_degrees)
    check_dimacs(args.run/'rook_control.cnf',rook_clauses,rook_model['variables'])
    positive,failed = evaluate_graph(rook_model,rook_clauses,rook)
    need(failed == 0 and positive == {int(k):v for k,v in rook_payload['assignment'].items()},'positive rook assignment')
    damaged = [row.copy() for row in rook]
    damaged[0][1] ^= 1
    damaged[1][0] ^= 1
    _,failed = evaluate_graph(rook_model,rook_clauses,damaged)
    need(failed > 0,'damaged rook assignment accepted')
    controls['rook_positive_false_clauses'] = 0
    controls['rook_corrupt_false_clauses'] = failed
    # A wrong exact-AND auxiliary assignment must also fail.
    corrupted_assignment = positive.copy()
    auxiliary = rook_model['products'][0]['id']
    corrupted_assignment[auxiliary] = not corrupted_assignment[auxiliary]
    need(not truth(rook_clauses,corrupted_assignment),'corrupt product accepted')
    controls['wrong_product_value_rejected'] = True
    model = read(args.run/'model.json')
    fixed = graphcheck.fixed_external(star)
    unknown = {(u,v) for u,v in combinations(range(10,50),2) if u//10 != v//10}
    known = [[0]*50 for _ in range(50)]
    for u,v in fixed:
        known[u][v] = known[v][u] = 1
    for u,v in unknown:
        known[u][v] = known[v][u] = -1
    shared = [[int(u != v and u//10 == v//10) for v in range(50)] for u in range(50)]
    need(model['cell_rook_coordinates'] == list(map(list,graphcheck.COORDINATES)),'cell-core assignment')
    def degrees(ids):
        rows = []
        for ca,cb in combinations(range(1,5),2):
            coordinates = graphcheck.COORDINATES
            target = 1 if any(a == b for a,b in zip(coordinates[ca],coordinates[cb])) else 2
            for u in range(ca*10,ca*10+10):
                rows.append(dict(variables=[ids[(u,v)] for v in range(cb*10,cb*10+10)],value=target,label=[ca,cb,'row',u]))
            for v in range(cb*10,cb*10+10):
                rows.append(dict(variables=[ids[(u,v)] for u in range(ca*10,ca*10+10)],value=target,label=[ca,cb,'column',v]))
        return rows
    expected,edge_ids,product_ids = semantics(model,known,shared,degrees)
    count = check_dimacs(args.run/'instance.cnf',expected,model['variables'])
    for name in ('instance.cnf','model.json'):
        packed = args.run/(name+'.gz')
        with gzip.open(packed,'rb') as stream:
            raw = stream.read()
        need(raw == (args.run/name).read_bytes(),'lossless public gzip companion')
    for path in (__file__,graphcheck.__file__,ROOT/'uv.lock'):
        bindings[str(path)] = digest(path)
    need(all(digest(Path(path) if Path(path).is_absolute() else ROOT/path) == value for path,value in bindings.items()),'input stability')
    report = dict(status='INDEPENDENT_FROZEN_ROOK_STAR_WINDOW_CNF_ENCODING_PASS',recommendation='VERIFIED',
                  claim_id='C-ROOK-FIXED-STAR-WINDOW-CNF-ENCODING',claim_revision=1,
                  statement='The exact saved CNF is satisfiable if and only if the600right-cell edges extend the frozen central star to the stated59vertex local window with all required block degrees and all common-neighbor upper caps. Every full target containing this exact labelled fixed star induces such a satisfying assignment. No universal coverage of rook-containing targets is claimed.',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  inputs_sha256=bindings,variables=model['variables'],edge_variables=len(edge_ids),product_variables=len(product_ids),
                  clauses=count,degree_constraints=120,external_pair_constraints=1225,embedded59_pair_count=1711,
                  controls=controls,producer_imported=False,solver_launched=False,
                  method='Independent symbolic common-neighbor polynomials; complete exact-AND variable bijection; independently rebuilt block degrees; full unordered DIMACS clause-multiset equality; raw59 validator controls.',
                  derivation='Every AND auxiliary is equivalent to its two edge inputs by all three clauses. Direct subset clauses are equivalent to the integer cardinalities. The600edge variables cover exactly all four arbitrary perfect-matching and two arbitrary degree2bipartite blocks. External pair constraints count known common external neighbors, the shared owner-core neighbor, and adjacency. Core-core caps are inherited from rook9. For a core-external pair in two included distinct cells, its common-neighbor count is their rook-adjacency indicator plus required block degree, equal2; in the same cell it is the fixed internal matching degree1. For a missing-cell core it is at most1. Known degrees are at most14. Thus the external constraints and exact block degrees imply every full59upper cap; no extra normalization/pruning is used.',
                  verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent encoding equivalence and raw-artifact check',
                  shared_components=['Python standard library','separate independent raw59 graph validator'],
                  scope='One exact raw central star SHA256 '+graphcheck.STAR_HASH+' and its five fixed internal matchings;600free labelled right-cell edges, no automorphism assumption.',
                  limitations=['Encoding verification supplies no SAT/UNSAT result.',
                               'A valid59window is only a necessary local condition for the99vertex target.',
                               'UNSAT can exclude only this frozen family after independent proof replay; no claim that every target contains this star or any rook9.',
                               'Full target regular-set necessity depends on the independently reviewed conditional rook9 encoding, not established by this CNF artifact alone.'],
                  elapsed_seconds=time.monotonic()-started,artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=report['status'],clauses=count,sha256=digest(args.out))))


if __name__ == '__main__':
    main()
