"""Independent exact audit of both raw orbit-local59 Gram obstructions.

No discovery/elimination implementation or numerical package is imported.
"""
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GRAPH = 'acceleration/results/20260930_independent_review/rook_orbit_sat_replay_v2/independent_full59.json'
SAT_GATE = 'acceleration/results/20260930_independent_review/rook_orbit_sat_replay_v2/summary.json'
CERT = 'acceleration/results/20260930_rook_orbit_gram01/result.json'
MANIFEST = 'acceleration/results/20260930_rook_orbit_gram01/manifest.json'
OUT = ROOT/'acceleration/results/20260930_independent_review/rook_orbit_gram'


def need(test,message):
    if not test:
        raise ValueError(message)


def digest(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def product(left,right):
    # Independent multiplication of I,A,J under the defining target relation.
    ii,aa,jj = left; kk,bb,ll = right
    return [ii*kk+12*aa*bb,
            ii*bb+aa*kk-aa*bb,
            ii*ll+jj*kk+2*aa*bb+14*(aa*ll+jj*bb)+99*jj*ll]


def check(graph,vector,kind,expected):
    n = len(graph)
    need(n and len(vector) == n and all(type(x) is int for x in vector),'exact vector shape/type')
    need(all(type(row) is list and len(row) == n for row in graph),'square graph')
    need(all(type(graph[i][j]) is int and graph[i][j] in (0,1) and graph[i][j] == graph[j][i] and (i != j or graph[i][j] == 0) for i in range(n) for j in range(n)),'simple binary symmetric graph')
    coefficients = {'27I-9A+J':(27,-9,1),'A+4I':(4,1,0)}
    need(kind in coefficients,'known exact matrix')
    i_coef,a_coef,j_coef = coefficients[kind]
    literal = sum(vector[i]*(i_coef*int(i == j)+a_coef*graph[i][j]+j_coef)*vector[j] for i in range(n) for j in range(n))
    edgewise = i_coef*sum(x*x for x in vector)+j_coef*sum(vector)**2+2*a_coef*sum(vector[i]*vector[j] for i,j in itertools.combinations(range(n),2) if graph[i][j])
    need(type(expected) is int and literal == edgewise == expected and literal < 0,'strictly negative exact matching quadratic')
    return dict(matrix=kind,quadratic_value=literal,vector_length=n,support_size=sum(x != 0 for x in vector),
                literal_ordered_entries_checked=n*n,undirected_pairs_checked=n*(n-1)//2,independent_integer_formulas_agree=True)


def controls(graph,records):
    known = []
    k5 = [[int(i != j) for j in range(5)] for i in range(5)]
    known.append(check(k5,[1]*5,'27I-9A+J',-20))
    star = [[int(i != j and (i == 0 or j == 0)) for j in range(26)] for i in range(26)]
    known.append(check(star,[5]+[-1]*25,'A+4I',-50))
    rook9 = [[int(i != j and (i//3 == j//3 or i%3 == j%3)) for j in range(9)] for i in range(9)]
    rejected = []
    for record in records:
        kind = record['matrix']; result = record['result']; vector = result['integer_negative_vector']; q = result['quadratic_value']
        bad_graph = copy.deepcopy(graph); bad_graph[0][1] ^= 1
        cases = [('wrong_value',graph,vector,q-1),('truncated_vector',graph,vector[:-1],q),
                 ('zero_direction',graph,[0]*59,q),('asymmetric_graph',bad_graph,vector,q),
                 ('nonnegative_is_not_certificate',graph,[0]*59,0),
                 ('PSD_rook9_constant_direction',rook9,[1]*9,-1),('PSD_rook9_difference_direction',rook9,[1,-1]+[0]*7,-1)]
        for name,a,v,expected in cases:
            try: check(a,v,kind,expected)
            except ValueError as error: rejected.append(dict(matrix=kind,case=name,error=str(error)))
            else: raise ValueError('corruption accepted: '+kind+'/'+name)
    return dict(known_negative_certificates=known,corruptions_rejected=rejected)


def main():
    need(digest(GRAPH) == '989cb3d10e7985cfa11958b579f0ede4ffa8e3d94fc8ed73c43ffbde26effbdc','raw graph pin')
    need(digest(SAT_GATE) == '511aa9b61eb913b84d3e6d8be1adc71d889897a28538669bcf41e8521b1cb8a8','independent local SAT gate pin')
    gate = json.loads((ROOT/SAT_GATE).read_bytes())
    need(gate['status'] == 'INDEPENDENT_ORBIT_AUGMENTED_ROOK_WINDOW_SAT_PASS' and gate['raw_graph_sha256'] == digest(GRAPH),'independent graph provenance')
    manifest = json.loads((ROOT/MANIFEST).read_bytes())
    need(manifest['input_hashes'][GRAPH] == digest(GRAPH),'producer raw graph binding')
    graph = json.loads((ROOT/GRAPH).read_bytes())['adjacency_full59']
    certificate = json.loads((ROOT/CERT).read_bytes())
    need(len(graph) == 59 and {r['matrix'] for r in certificate['tests']} == {'27I-9A+J','A+4I'} and len(certificate['tests']) == 2,'both exact matrix cases')
    results = []
    for row in certificate['tests']:
        result = row['result']
        need(result['psd'] is False and result['support'] == [i for i,x in enumerate(result['integer_negative_vector']) if x],'certificate support metadata')
        results.append(check(graph,result['integer_negative_vector'],row['matrix'],result['quadratic_value']))
    # These are target-level algebraic necessities, not an eigenvalue guess.
    g,p = (27,-9,1),(44,11,-2)
    need(product(g,g) == [63*x for x in g],'G square identity')
    need(product(p,p) == [77*x for x in p],'P square identity')
    need([p[0],p[1],p[2]+2] == [44,11,0],'11(A+4I)=P+2J')
    calibration = controls(graph,certificate['tests'])
    files = [GRAPH,SAT_GATE,CERT,MANIFEST,Path(__file__).relative_to(ROOT).as_posix(),'uv.lock']
    bound = {name:digest(name) for name in files}
    for name,expected in manifest['input_hashes'].items():
        actual = digest(name)
        need(actual == expected,'producer source/input identity')
        bound[name] = actual
    report = dict(status='INDEPENDENT_ORBIT_LOCAL59_DUAL_GRAM_EXCLUSION_PASS',claim_id='C-ROOK-ORBIT-LOCAL59-DUAL-GRAM-EXCLUSION',claim_revision=1,
        recommendation='VERIFIED',review_state='CLEAR',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='/root/state_literature_audit independent checking agent',verification_type='Raw literal integer double sums and separate edge sums; independent target polynomial sum-of-squares derivation',
        inputs_sha256=bound,graph_sha256=digest(GRAPH),certificate_sha256=digest(CERT),results=results,controls=calibration,
        statement='The single exact labelled59vertex graph with SHA256'+digest(GRAPH)+' cannot be an induced subgraph of any srg(99,14,1,2); both saved integer vectors separately contradict necessary principal positive semidefiniteness.',
        scope='One exact local59 witness surviving352 prior target cuts. No family-wide or unrestricted nonexistence claim; no graph automorphism assumption.',
        assumptions=['A hypothetical target is symmetric binary zero-diagonal and satisfies A^2=12I-A+2J.','The candidate is asserted to occur as the exact induced graph on these59 designated vertices.'],
        mathematical_derivation=[
            'The diagonal target identity gives degree14, so AJ=JA=14J; J^2=99J.',
            'For G=27I-9A+J, direct multiplication gives G^2=63G, hence x^TGx=||Gx||^2/63>=0.',
            'For P=11A+44I-2J, direct multiplication gives P^2=77P. Since11(A+4I)=P+2J, x^T(A+4I)x=||Px||^2/847+(2/11)(sum x)^2>=0.',
            'Every induced principal submatrix inherits positive semidefiniteness by zero-padding a vector outside its vertex set. Each recorded strict negative integer contradicts that requirement.'],
        polynomial_identities=dict(G_squared=product(g,g),sixtythree_G=[63*x for x in g],P_squared=product(p,p),seventyseven_P=[77*x for x in p]),
        basis=['DERIVED','COMPUTED'],kind='exclusion',dependencies=[],
        dependency_null_reason='The exact exclusion follows directly from the raw graph, integer directions and the defining target identity; prior local-SAT validity is independently pinned provenance but is not a logical premise of nonextendibility.',
        producer_imported=False,shared_components=['Python standard library and exact integers','Raw graph from independently authored SAT checking path'],
        limitations=['No target graph, full frozen-scaffold exclusion, unrestricted nonexistence or external review.','No rank or full inertia of either local matrix is asserted.','The earlier local SAT construction remains valid for its weaker encoded constraints.'],
        target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    OUT.mkdir(parents=True,exist_ok=False)
    with (OUT/'summary.json').open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2); stream.write('\n')
    print(json.dumps(dict(status=report['status'],quadratic_values=[r['quadratic_value'] for r in results],sha256=digest(OUT/'summary.json'))))


if __name__ == '__main__':
    main()
