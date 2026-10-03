"""Independent exact target graph and eight-family SAT-object checker.

Uses only the Python standard library; imports no producer or earlier checker.
Commands: calibrate --out DIR; graph --graph JSON --out DIR; sat --help.
The graph command always requires SRG(99,14,1,2), never fixture parameters.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import io
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT/'acceleration/results/20260917_partial_eight_matchings/manifest.json'
SCOPE_SHA = 'a389f457280212fbafcaa556dfe2064c9b1659045475fe4f93a0becb400cb7a2'
MODEL = ROOT/'acceleration/results/20260930_eight_full99_cnf/model.json'
MODEL_SHA = 'f2b7a649e74aa476380e14066239a188a2d2122d2ba1cc6e330e9a094d2cc0ee'
CNF_SHA = 'f247be8432d69f4feec037833a6923ef623e20c0aa0dbdea77fd13ec218d095b'


def need(test, message):
    if not test:
        raise ValueError(message)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def key(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def unique_keys(pairs):
    result = {}
    for k,v in pairs:
        need(k not in result,'duplicate JSON key: '+k)
        result[k] = v
    return result


def read(path):
    return json.loads(Path(path).read_bytes(),object_pairs_hook=unique_keys)


def save(path,data):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(data,stream,indent=2)
        stream.write('\n')


def validate_srg(a,n,k,lam,mu):
    """All entries of literal integer A*A=(k-mu)I+(lam-mu)A+mu J."""
    need(type(a) is list and len(a) == n,'matrix row count')
    need(all(type(row) is list and len(row) == n for row in a),'matrix square dimensions')
    need(all(type(x) is int and x in (0,1) for row in a for x in row),'strict integer binary entries')
    need(all(a[i][i] == 0 for i in range(n)),'zero diagonal')
    need(all(a[i][j] == a[j][i] for i in range(n) for j in range(n)),'symmetry')
    degrees = [sum(row) for row in a]
    need(degrees == [k]*n,'degree requirement')
    checked = 0
    for i in range(n):
        for j in range(n):
            observed = sum(a[i][h]*a[h][j] for h in range(n))
            expected = (k-mu)*int(i == j)+(lam-mu)*a[i][j]+mu
            need(observed == expected,'integer matrix identity fails at (%d,%d): %d != %d'%(i,j,observed,expected))
            checked += 1
    return dict(parameters=[n,k,lam,mu],strict_binary_entries=n*n,degree_rows_checked=n,
                exact_integer_matrix_entries_checked=checked,unordered_edges=sum(degrees)//2,
                identity_coefficients=dict(I=k-mu,A=lam-mu,J=mu),valid=True)


def family_specification(scope):
    labels = [(2*i+s,2*j+t) for i,j in itertools.combinations(range(7),2) for s in (0,1) for t in (0,1)]
    need(len(labels) == 84 and len(set(labels)) == 84,'outer labels')
    def pairs(field,count):
        raw = scope[field]
        need(type(raw) is list and len(raw) == count,'scope pair count '+field)
        need(all(type(e) is list and len(e) == 2 and all(type(x) is int for x in e) and 0 <= e[0] < e[1] < 84 for e in raw),'canonical scope pairs '+field)
        result = {tuple(e) for e in raw}
        need(len(result) == count,'distinct scope pairs '+field)
        return result
    fixed = pairs('remaining_fixed_K_edges_outer',120)
    unknown = pairs('unknown_edges_outer',2160)
    need(not (fixed & unknown),'fixed/free disjoint')
    a = [[0]*99 for _ in range(99)]
    def put(i,j,value):
        a[i][j] = a[j][i] = value
    for i in range(1,15):
        put(0,i,1)
    for i in range(7):
        put(1+2*i,2+2*i,1)
    for outer,label in enumerate(labels,15):
        for inner in label:
            put(outer,inner+1,1)
    scaffold = sum(a[i][j] for i,j in itertools.combinations(range(99),2))
    need(scaffold == 189,'root scaffold edge count')
    for i,j in fixed:
        put(i+15,j+15,1)
    for i,j in unknown:
        put(i+15,j+15,-1)
    edges = [(i+15,j+15) for i,j in sorted(unknown)]
    return a,labels,fixed,unknown,edges


def check_model_scope(model,scope):
    a,labels,fixed,unknown,edges = family_specification(scope)
    need(model['scope_sha256'] == SCOPE_SHA and model['scope_path'] == key(SCOPE),'declared scope identity')
    need(model['known_adjacency_full99'] == a,'all9801 fixed/free adjacency entries')
    need(model['outer_labels'] == list(map(list,labels)),'outer label order')
    need(model['fixed_scaffold_edges'] == 189 and model['fixed_K_edges'] == list(map(list,sorted(fixed))) and model['unknown_edges_outer'] == list(map(list,sorted(unknown))),'scope edge inventories')
    expected = [dict(u=u,v=v,id=i+1) for i,(u,v) in enumerate(edges)]
    need(model['edge_variables'] == expected,'all2160 edge variable labels and endpoints')
    need(model['variables'] == 485165 and model['clauses'] == 1684724,'exact encoding size')
    return a,edges,dict(fixed_scaffold_edges=189,fixed_outer_K_edges=120,variable_outer_edges=2160,
                        fixed_unordered_pair_entries=2691,fixed_absent_unordered_pairs=2382,full_matrix_entries_checked=9801)


def assignment_values(signed,variables):
    need(type(signed) is list and len(signed) == variables,'complete assignment length')
    values = bytearray([2])*(variables+1)
    for lit in signed:
        need(type(lit) is int and 1 <= abs(lit) <= variables,'signed integer variable range')
        variable = abs(lit)
        need(values[variable] == 2,'duplicate assigned variable')
        values[variable] = int(lit > 0)
    need(all(x != 2 for x in values[1:]),'all variables assigned')
    return values


def check_cnf_stream(stream,values,variables,clauses):
    need(stream.readline().split() == [b'p',b'cnf',str(variables).encode(),str(clauses).encode()],'exact DIMACS header')
    count,literals = 0,0
    for line in stream:
        row = list(map(int,line.split()))
        need(len(row) >= 1 and row[-1] == 0 and all(1 <= abs(x) <= variables for x in row[:-1]),'one complete canonical-range clause per row')
        need(any(values[abs(x)] == (1 if x > 0 else 0) for x in row[:-1]),'unsatisfied raw clause %d'%(count+1))
        count += 1
        literals += len(row)-1
    need(count == clauses,'exact raw clause count')
    return dict(clauses_checked=count,literals_evaluated=literals)


def decode_model(a,edges,values):
    graph = [row.copy() for row in a]
    for variable,(i,j) in enumerate(edges,1):
        graph[i][j] = graph[j][i] = int(values[variable])
    need(all(x in (0,1) for row in graph for x in row),'no unresolved graph entries')
    need(all(a[i][j] == -1 or graph[i][j] == a[i][j] for i in range(99) for j in range(99)),'all fixed entries preserved')
    return graph


def fixtures():
    cycle = [[int((i-j)%5 in (1,4)) for j in range(5)] for i in range(5)]
    residues = {x*x%13 for x in range(1,13)}
    paley = [[int((i-j)%13 in residues) for j in range(13)] for i in range(13)]
    pairs5 = list(map(set,itertools.combinations(range(5),2)))
    petersen = [[int(not (u & v)) for v in pairs5] for u in pairs5]
    complement = [[int(i != j and not petersen[i][j]) for j in range(10)] for i in range(10)]
    rook = [[int(i != j and (i//4 == j//4 or i%4 == j%4)) for j in range(16)] for i in range(16)]
    pairs8 = list(map(set,itertools.combinations(range(8),2)))
    triangular = [[int(len(u & v) == 1) for v in pairs8] for u in pairs8]
    return [('cycle5',cycle,(5,2,0,1)),('paley13',paley,(13,6,2,3)),('petersen10',petersen,(10,3,0,1)),
            ('petersen_complement10',complement,(10,6,3,4)),('rook4',rook,(16,6,2,2)),('triangular8',triangular,(28,12,6,4))]


def controls(out):
    records,rejected = [],[]
    def reject(name,operation):
        try:
            operation()
        except (ValueError,IndexError,TypeError) as error:
            rejected.append(dict(case=name,error=str(error)))
        else:
            raise ValueError('corruption accepted: '+name)
    for name,a,params in fixtures():
        check = validate_srg(a,*params)
        fixture_path = out/(name+'.json')
        save(fixture_path,dict(adjacency=a,parameters=params,checking_result=check))
        records.append(dict(name=name,path=key(fixture_path),sha256=digest(fixture_path),result=check))
        modifications = ['loop','asymmetry','symmetric_flip','nonbinary','float_entry','wrong_shape']
        for corruption in modifications:
            b = copy.deepcopy(a)
            if corruption == 'loop': b[0][0] = 1
            if corruption == 'asymmetry': b[0][1] = 1-b[0][1]
            if corruption == 'symmetric_flip': b[0][1] = b[1][0] = 1-b[0][1]
            if corruption == 'nonbinary': b[0][0] = 2
            if corruption == 'float_entry': b[0][0] = 0.0
            if corruption == 'wrong_shape': b[0].pop()
            reject(name+'/'+corruption,lambda:validate_srg(b,*params))
        reject(name+'/wrong_lambda',lambda:validate_srg(a,params[0],params[1],params[2]+1,params[3]))
    # Preserve degree3 on all10 vertices while destroying common-neighbor counts.
    p = fixtures()[2][1]
    switch = None
    for a,b,c,d in itertools.permutations(range(10),4):
        if p[a][b] and p[c][d] and not p[a][c] and not p[b][d]:
            trial = copy.deepcopy(p)
            for u,v,x in ((a,b,0),(c,d,0),(a,c,1),(b,d,1)):
                trial[u][v] = trial[v][u] = x
            try:
                validate_srg(trial,10,3,0,1)
            except ValueError as error:
                need('integer matrix identity' in str(error),'degree-preserving rejection reaches exact matrix test')
                switch = dict(vertices=[a,b,c,d],graph=trial,error=str(error))
                break
    need(switch is not None,'known degree-preserving non-SRG control')
    save(out/'degree_preserving_corruption.json',switch)
    # Complete99 degree14 is insufficient: this circulant has the wrong common counts.
    circulant = [[int(0 < min((i-j)%99,(j-i)%99) <= 7) for j in range(99)] for i in range(99)]
    need(all(sum(row) == 14 for row in circulant),'99vertex degree-positive control')
    reject('99vertex_degree14_wrong_common_counts',lambda:validate_srg(circulant,99,14,1,2))
    save(out/'invalid99_degree14.json',dict(adjacency_full99=circulant,deliberately_invalid_target=True))
    cnf = b'p cnf 3 3\n1 -2 0\n2 3 0\n-1 3 0\n'
    values = assignment_values([1,2,3],3)
    sat_control = check_cnf_stream(io.BytesIO(cnf),values,3,3)
    reject('cnf_wrong_assignment',lambda:check_cnf_stream(io.BytesIO(cnf),assignment_values([-1,2,3],3),3,3))
    reject('cnf_changed_header',lambda:check_cnf_stream(io.BytesIO(cnf.replace(b'3 3',b'3 4',1)),values,3,3))
    reject('cnf_truncated_clause_set',lambda:check_cnf_stream(io.BytesIO(cnf[:-7]),values,3,3))
    reject('cnf_extra_clause',lambda:check_cnf_stream(io.BytesIO(cnf+b'3 0\n'),values,3,3))
    reject('cnf_variable_out_of_range',lambda:check_cnf_stream(io.BytesIO(cnf.replace(b'2 3 0',b'2 4 0')),values,3,3))
    reject('assignment_missing',lambda:assignment_values([1,2],3))
    reject('assignment_duplicate',lambda:assignment_values([1,2,2],3))
    reject('assignment_noninteger',lambda:assignment_values([1,2,3.0],3))
    reject('json_duplicate_key',lambda:json.loads('{"x":1,"x":2}',object_pairs_hook=unique_keys))
    return dict(valid_srg_fixtures=records,valid_srg_fixture_count=len(records),corruptions_rejected=rejected,
                degree_preserving_corruption_rejected=True,degree_preserving_corruption_sha256=digest(out/'degree_preserving_corruption.json'),
                complete99_degree14_invalid_target_rejected=True,known_tiny_sat=sat_control,
                valid99_target_fixture=None,valid99_target_fixture_null_reason='No known target graph is available; none is fabricated.')


def provenance():
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                verifier='/root/state_literature_audit independent checking agent',producer_imported=False,
                shared_components=['Python standard library; exact arbitrary-precision integer arithmetic'],
                external_review=False,artifact_availability='LOCAL_ONLY')


def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False)
    record = controls(args.out)
    need(digest(SCOPE) == SCOPE_SHA and digest(MODEL) == MODEL_SHA,'frozen scope/model pins')
    scope,model = read(SCOPE),read(MODEL)
    a,edges,scope_record = check_model_scope(model,scope)
    arbitrary_values = bytearray(model['variables']+1)
    graph = decode_model(a,edges,arbitrary_values)
    save(args.out/'scope_valid_target_invalid_all_free_zero.json',dict(adjacency_full99=graph,scope_valid=True,target_valid=False))
    scope_corruptions = []
    for name,mutate in [('wrong_fixed_entry',lambda m:m['known_adjacency_full99'][0].__setitem__(1,0)),
                        ('wrong_edge_id',lambda m:m['edge_variables'][0].__setitem__('id',2)),
                        ('wrong_outer_label',lambda m:m['outer_labels'][0].__setitem__(0,1))]:
        bad = copy.deepcopy(model); mutate(bad)
        try: check_model_scope(bad,scope)
        except ValueError as error: scope_corruptions.append(dict(case=name,error=str(error)))
        else: raise ValueError('scope corruption accepted: '+name)
    try: validate_srg(graph,99,14,1,2)
    except ValueError as error: false_graph_reason = str(error)
    else: raise ValueError('all-free-zero falsely accepted as target')
    report = provenance()
    report.update(status='INDEPENDENT_FULL99_SAT_OBJECT_CHECKER_CALIBRATION_PASS',controls=record,scope_check=scope_record,
                  scope_corruptions_rejected=scope_corruptions,all_free_zero_target_rejection=false_graph_reason,
                  inputs_sha256={key(p):digest(p) for p in (SCOPE,MODEL,Path(__file__),ROOT/'uv.lock')},
                  solver_launched=False,target_resolution=False,
                  scope='Independent checker calibration and exact raw eight-family decode mapping; no satisfiable research CNF or target graph is asserted.',
                  limitations=['Small known-valid graphs calibrate the generic checker; no valid99 target positive control is available.','Calibration does not prove CNF equivalence or solve any research instance.'])
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))


def check(args):
    started = time.monotonic()
    args.out.mkdir(parents=True,exist_ok=False)
    bindings = {}
    def load(path,expected=None):
        path = Path(path)
        if not path.is_absolute(): path = ROOT/path
        actual = digest(path)
        need(expected is None or actual == expected,'artifact hash mismatch: '+key(path))
        bindings[key(path)] = actual
        return read(path)
    scope_check = cnf_check = None
    if args.command == 'sat':
        gate = load(args.encoding_audit,args.encoding_audit_sha256)
        need(gate['status'] == 'INDEPENDENT_EIGHT_FULL99_CNF_ENCODING_PASS','independent full99 encoding gate')
        model = load(args.model,MODEL_SHA)
        need(digest(args.cnf) == CNF_SHA,'frozen CNF pin')
        for path in (args.model,args.cnf):
            need(gate['inputs_sha256'][key(path)] == digest(path),'encoding gate binds exact artifact')
            bindings[key(path)] = digest(path)
        scope = load(SCOPE,SCOPE_SHA)
        a,edges,scope_check = check_model_scope(model,scope)
        signed = load(args.assignment)['assignment']
        values = assignment_values(signed,model['variables'])
        with args.cnf.open('rb') as stream:
            cnf_check = check_cnf_stream(stream,values,model['variables'],model['clauses'])
        graph = decode_model(a,edges,values)
        if args.decoded is not None:
            supplied = load(args.decoded)
            need(supplied['adjacency_full99'] == graph,'independent decoded graph equals supplied object')
    else:
        supplied = load(args.graph)
        graph = supplied if type(supplied) is list else supplied['adjacency_full99']
    exact = validate_srg(graph,99,14,1,2)
    output_path = args.out/'independent_adjacency_full99.json'
    save(output_path,dict(adjacency_full99=graph,exact_identity='A^2 = 12I - A + 2J',independent_check=exact,external_review=False))
    for path in (Path(__file__),ROOT/'uv.lock'):
        bindings[key(path)] = digest(path)
    need(all(digest(ROOT/name) == expected for name,expected in bindings.items()),'stable raw inputs')
    report = provenance()
    report.update(status='INDEPENDENT_TARGET_GRAPH_PASS_PENDING_EXTERNAL_REVIEW',inputs_sha256=bindings,
                  verification_type='All strict binary/symmetric/zero-diagonal entries, all99degrees and all9801 literal Python-integer matrix-square entries; SAT command additionally checks every raw CNF clause and all scope entries',
                  graph_result=exact,scope_check=scope_check,cnf_check=cnf_check,
                  scope_check_null_reason='Standalone raw target graph command has no conditional family claim.' if scope_check is None else None,
                  cnf_check_null_reason='Standalone raw graph command has no SAT encoding claim.' if cnf_check is None else None,
                  graph_path=key(output_path),graph_sha256=digest(output_path),target_resolution=True,
                  statement='The saved explicit99by99 matrix is symmetric, binary, zero-diagonal and satisfies A^2=12I-A+2J exactly over the integers.',
                  limitations=['Internal independent artifact validation; external mathematical review is pending.'],elapsed_seconds=time.monotonic()-started)
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],graph_sha256=digest(output_path),summary_sha256=digest(args.out/'summary.json'))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    calibration = sub.add_parser('calibrate'); calibration.add_argument('--out',type=Path,required=True)
    graph = sub.add_parser('graph'); graph.add_argument('--graph',type=Path,required=True); graph.add_argument('--out',type=Path,required=True)
    sat = sub.add_parser('sat')
    for name in ('cnf','model','assignment','encoding-audit','out'):
        sat.add_argument('--'+name,type=Path,required=True)
    sat.add_argument('--decoded',type=Path)
    sat.add_argument('--encoding-audit-sha256',required=True)
    args = parser.parse_args()
    (calibrate if args.command == 'calibrate' else check)(args)


if __name__ == '__main__':
    main()
