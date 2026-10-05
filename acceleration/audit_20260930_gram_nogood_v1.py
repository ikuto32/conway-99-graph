"""Independent integer Gram obstruction and complete support-nogood audit.

Reusable for59vertex graphs in the frozen780edge rook-window encoding. No
producer or numerical eigensolver is imported. All scalar arithmetic is Python
integer arithmetic. The cut is target-extension-valid, not base-CNF-entailed.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys

import audit_20260930_rook_free_internal_cnf_v1 as window

ROOT = Path(__file__).resolve().parents[1]
STAR = ROOT/'acceleration/results/20260930_rook_cell_factors/local_witness.json'


def need(condition,message):
    if not condition:
        raise ValueError(message)


def digest(path):
    value = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            value.update(block)
    return value.hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def product_basis(left,right,n=99,k=14,constant=12,adjacency=-1,jcoefficient=2):
    # Basis I,A,J. Derived target relations: A²=12I-A+2J,
    # AJ=JA=14J, and J²=99J.
    multiplication = {(0,0):(1,0,0),(0,1):(0,1,0),(1,0):(0,1,0),
                      (0,2):(0,0,1),(2,0):(0,0,1),
                      (1,1):(constant,adjacency,jcoefficient),
                      (1,2):(0,0,k),(2,1):(0,0,k),(2,2):(0,0,n)}
    result = [0,0,0]
    for i,x in enumerate(left):
        for j,y in enumerate(right):
            for t,value in enumerate(multiplication[i,j]):
                result[t] += x*y*value
    return tuple(result)


def direct_quadratic(graph,vector):
    n = len(graph)
    return sum(vector[u]*(27*int(u==v)-9*graph[u][v]+1)*vector[v]
               for u in range(n) for v in range(n))


def reconstruct_mapping(model):
    known = model['known_adjacency']
    need(len(known) == 50 and all(len(row) == 50 and all(type(x) is int and x in (-1,0,1) for x in row) for row in known),'known adjacency shape')
    need(all(known[u][u] == 0 for u in range(50)) and all(known[u][v] == known[v][u] for u,v in combinations(range(50),2)),'known symmetry')
    pairs = {(u,v) for u,v in combinations(range(50),2) if known[u][v] == -1}
    need(pairs == set(combinations(range(10,50),2)),'exact780edge unknown universe')
    mapping = {}
    used_edges = set()
    for record in model['edge_variables']:
        u,v,variable = record['u'],record['v'],record['id']
        need(type(variable) is int and variable > 0 and variable not in mapping and (u,v) in pairs and (u,v) not in used_edges,'edge-variable bijection')
        mapping[variable] = (u+9,v+9)
        used_edges.add((u,v))
    need(used_edges == pairs and set(mapping) == set(range(1,781)),'complete780edge mapping')
    return mapping


def audit_certificate(certificate,graph,mapping):
    need(certificate['matrix'] == '27I-9A+J','matrix definition')
    vector = certificate['integer_negative_vector']
    need(len(vector) == 59 and all(type(x) is int for x in vector),'exact59integer vector')
    support = [i for i,x in enumerate(vector) if x]
    need(certificate['support'] == support,'support identity')
    direct = direct_quadratic(graph,vector)
    need(type(certificate['quadratic_value']) is int and direct == certificate['quadratic_value'] < 0,'strictly negative exact quadratic')
    base = [row.copy() for row in graph]
    for u,v in mapping.values():
        base[u][v] = base[v][u] = 0
    # The constant is evaluated as a full ordered matrix sum on the graph with
    # all variable edges zero, independently of the producer's edge expansion.
    constant = direct_quadratic(base,vector)
    coefficients = {variable:-9*(vector[u]*vector[v]+vector[v]*vector[u]) for variable,(u,v) in mapping.items()}
    expected = [dict(variable=variable,edge_full59=list(mapping[variable]),coefficient=coefficient,
                     value_in_rejected_graph=graph[mapping[variable][0]][mapping[variable][1]])
                for variable,coefficient in sorted(coefficients.items()) if coefficient]
    need(certificate['linear_quadratic_constant'] == constant,'full fixed-part constant')
    actual = certificate['nonzero_variable_coefficients']
    need(all(type(row['variable']) is int and type(row['coefficient']) is int and type(row['value_in_rejected_graph']) is int for row in actual),'integer coefficient metadata')
    need(sorted(actual,key=lambda row:row['variable']) == expected,'complete nonzero coefficient/edge/value table')
    total = constant+sum(row['coefficient']*row['value_in_rejected_graph'] for row in expected)
    need(total == direct,'independent polynomial evaluation equality')
    expected_clause = [-row['variable'] if row['value_in_rejected_graph'] else row['variable'] for row in expected]
    clause = certificate['nogood_clause']
    need(all(type(literal) is int and literal != 0 for literal in clause)
         and len(clause) == len(set(map(abs,clause))) == certificate['nogood_clause_length'] == len(expected_clause)
         and sorted(clause) == sorted(expected_clause),'exact signed support nogood')
    need(all(graph[mapping[abs(literal)][0]][mapping[abs(literal)][1]] != int(literal>0) for literal in clause),'current graph must falsify every cut literal')
    covered = {row['variable'] for row in expected}
    omitted = set(mapping)-covered
    need(all(coefficients[variable] == 0 for variable in omitted),'omitted variable coefficient not zero')
    return dict(support=support,support_size=len(support),quadratic_value=direct,linear_quadratic_constant=constant,
                checked_edge_variables=len(mapping),nonzero_variable_coefficients=expected,
                zero_coefficient_variables=len(omitted),verified_clause=clause,clause_length=len(clause),
                all_omitted_coefficients_zero=True,falsifies_current_graph=True,
                preservation_argument='The exact affine polynomial is constant plus the listed nonzero edge coefficients. Fixing all listed values to the rejected graph fixes its value to the same negative integer, regardless of every omitted variable and every outside vertex.')


def controls(certificate,graph,mapping):
    target = (27,-9,1)
    need(product_basis(target,target) == tuple(63*x for x in target) == (1701,-567,63),'exact target projector identity')
    need(product_basis(target,target,adjacency=1) != tuple(63*x for x in target),'wrong target identity control')
    # Known-valid rook9 has A²=2I-A+2J. Its P=3I-3A+J satisfies
    # P²=9P. Check this by literal matrix multiplication, not a spectral claim.
    rook = [[int(u != v and (u//3 == v//3 or u%3 == v%3)) for v in range(9)] for u in range(9)]
    def rook_projector_ok(adjacency):
        projector = [[3*int(u==v)-3*adjacency[u][v]+1 for v in range(9)] for u in range(9)]
        return all(sum(projector[u][w]*projector[w][v] for w in range(9)) == 9*projector[u][v] for u in range(9) for v in range(9))
    need(rook_projector_ok(rook),'known-valid rook projector fixture')
    bad_rook = [row.copy() for row in rook]
    bad_rook[0][1] ^= 1
    bad_rook[1][0] ^= 1
    need(not rook_projector_ok(bad_rook),'corrupted rook projector accepted')
    valid = audit_certificate(certificate,graph,mapping)
    rejected = []
    for kind in ('nonnegative_vector','wrong_quadratic','wrong_constant','wrong_edge_mapping',
                 'wrong_coefficient','wrong_current_value','omitted_nonzero_coefficient','omitted_clause_literal','flipped_clause_literal'):
        bad = deepcopy(certificate)
        if kind == 'nonnegative_vector':
            bad['integer_negative_vector'] = [1]+[0]*58
            bad['support'] = [0]
            bad['quadratic_value'] = 28
        elif kind == 'wrong_quadratic':
            bad['quadratic_value'] += 1
        elif kind == 'wrong_constant':
            bad['linear_quadratic_constant'] += 1
        elif kind == 'wrong_edge_mapping':
            bad['nonzero_variable_coefficients'][0]['edge_full59'][0] += 1
        elif kind == 'wrong_coefficient':
            bad['nonzero_variable_coefficients'][0]['coefficient'] += 1
        elif kind == 'wrong_current_value':
            bad['nonzero_variable_coefficients'][0]['value_in_rejected_graph'] ^= 1
        elif kind == 'omitted_nonzero_coefficient':
            bad['nonzero_variable_coefficients'].pop()
        elif kind == 'omitted_clause_literal':
            bad['nogood_clause'].pop()
            bad['nogood_clause_length'] -= 1
        else:
            bad['nogood_clause'][0] *= -1
        try:
            audit_certificate(bad,graph,mapping)
        except ValueError:
            rejected.append(kind)
        else:
            raise ValueError('bad cut fixture accepted: '+kind)
    return dict(known_rook_projector_passed=True,corrupted_rook_rejected=True,
                exact_target_basis_identity=[1701,-567,63],wrong_target_identity_rejected=True,
                positive_certificate_accepted=True,corruptions_rejected=rejected),valid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graph',type=Path,required=True)
    parser.add_argument('--certificate',type=Path,required=True)
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--cnf',type=Path,required=True)
    parser.add_argument('--encoding-audit',type=Path,required=True)
    parser.add_argument('--encoding-audit-sha256',required=True)
    parser.add_argument('--expected-certificate-sha256')
    parser.add_argument('--clause',type=Path)
    parser.add_argument('--claim-id')
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    need(not args.out.exists(),'refuse overwrite')
    bindings = {}
    def read(path):
        bindings[key(path)] = digest(path)
        return json.loads(Path(path).read_bytes())
    need(digest(args.encoding_audit) == args.encoding_audit_sha256,'encoding audit pin')
    gate = read(args.encoding_audit)
    need(gate['status'] == 'INDEPENDENT_ROOK_FREE_INTERNAL_WINDOW_CNF_ENCODING_PASS','exact780edge encoding gate')
    authenticated = {str((Path(path) if Path(path).is_absolute() else ROOT/path).resolve()):value for path,value in gate['inputs_sha256'].items()}
    for path in (args.model,args.cnf):
        need(authenticated.get(str(path.resolve())) == digest(path),'raw model/CNF identity under independent encoding gate')
        bindings[key(path)] = digest(path)
    if args.expected_certificate_sha256:
        need(digest(args.certificate) == args.expected_certificate_sha256,'requested certificate hash')
    certificate = read(args.certificate)
    raw = read(args.graph)
    model = read(args.model)
    star = read(STAR)
    graph = raw['adjacency_full59']
    local_check = window.validate_candidate(graph,star,True)
    need(certificate['graph_sha256'] == digest(args.graph) and certificate['encoding_model_sha256'] == digest(args.model)
         and certificate['base_cnf_sha256'] == digest(args.cnf),'certificate raw input bindings')
    with args.cnf.open('r',encoding='ascii') as stream:
        need(stream.readline().split() == ['p','cnf',str(model['variables']),str(model['clauses'])],'raw base CNF header')
    mapping = reconstruct_mapping(model)
    for variable,(u,v) in mapping.items():
        need(model['known_adjacency'][u-9][v-9] == -1,'variable targets known absence/edge')
    # Ensure all entries treated as constants really are fixed by the exact
    # model/scaffold. The independent local graph validator checks the same
    # raw-star family, and this second comparison explicitly binds model bytes.
    for u,v in combinations(range(50),2):
        value = model['known_adjacency'][u][v]
        if value != -1:
            need(graph[u+9][v+9] == value,'graph-model fixed adjacency mismatch')
    calibration,checked = controls(certificate,graph,mapping)
    if args.clause:
        values = list(map(int,args.clause.read_text(encoding='ascii').split()))
        need(values and values[-1] == 0 and values[:-1] == checked['verified_clause'],'raw clause identity')
        bindings[key(args.clause)] = digest(args.clause)
    for path in (__file__,window.__file__,window.symbolic.__file__,window.graphcheck.__file__,ROOT/'uv.lock'):
        bindings[key(path)] = digest(path)
    need(all(digest(ROOT/path) == value for path,value in bindings.items()),'input stability')
    report = dict(status='INDEPENDENT_TARGET_GRAM_NOGOOD_PASS',
                  claim_id=args.claim_id,claim_id_null_reason=None if args.claim_id else 'Caller must bind this reusable checker result to an explicit stable ledger claim',
                  claim_revision=1 if args.claim_id else None,recommendation='VERIFIED',
                  statement='Every99vertex target extension of the exact780edge rook-window family satisfies the recorded support nogood: preserving all listed edge values would retain a strictly negative principal quadratic of27I-9A+J. The recorded clause is not asserted to follow from the weaker original local CNF.',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  checker_path=key(__file__),checker_sha256=digest(__file__),
                  verifier='Independent checker authored by /root/eight_domain_audit; invocation provenance is the recorded command',
                  verification_type='Exact integer raw-graph quadratic, complete edge-coefficient coverage, clause mapping, and independent universal PSD derivation',
                  inputs_sha256=bindings,encoding_audit_sha256=digest(args.encoding_audit),base_cnf_sha256=digest(args.cnf),
                  encoding_model_sha256=digest(args.model),graph_sha256=digest(args.graph),certificate_sha256=digest(args.certificate),
                  **checked,controls=calibration,raw_local_graph_check=local_check,
                  universal_psd_derivation=['The diagonal of A²=12I-A+2J and binary symmetry/zero diagonal gives every row degree14; hence AJ=JA=14J and J²=99J.',
                    'For symmetric G=27I-9A+J, direct expansion gives G²=729I+81A²+J²-486A+54J-9(AJ+JA)=1701I-567A+63J=63G.',
                    'For every real x, x^TGx=(Gx)^T(Gx)/63>=0; thus G is PSD. A principal59matrix is PSD by extending vectors with40zeros.',
                    'Every unknown-edge coefficient of the exact principal quadratic is checked. Variables absent from the clause have coefficientzero. Fixing the clause variables to their current values fixes a negative quadratic, regardless of all other choices; therefore every target extension must satisfy the clause.'],
                  cut_scope='Target extensions of the frozen central factor family; this adds a necessary target condition to the weaker local SAT relaxation.',
                  local_cnf_consequence_claimed=False,current_locally_valid_graph_falsifies_cut=True,
                  dependencies=[dict(id='C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING',revision=1,relation='encoding_equivalence')],
                  producer_imported=False,shared_components=['Python standard library exact integers','prior independent780edge raw59 validator and its independent helpers'],
                  limitations=['No exhaustive proof that the 780edge family is empty; only the stated edge-value pattern is excluded for target extensions.',
                               'No claim of globally minimum vector support or minimum clause length.',
                               'A later augmented-CNF UNSAT proof needs exact ordered cut artifacts and independently verified validity of every added clause.',
                               'No target graph, universal rook containment, unrestricted nonexistence, or external review.'],
                  target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=report['status'],clause_length=checked['clause_length'],quadratic_value=checked['quadratic_value'],sha256=digest(args.out))))


if __name__ == '__main__':
    main()
