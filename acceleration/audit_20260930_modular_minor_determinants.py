"""Separate literal integer determinant review of modular minor certificates.

Imports neither the rank-screen producer nor the modular-pivot minor selector.
Fraction-free integer determinants are checked before reduction modulo primes.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import permutations,product
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
DERIVATION=ROOT/'docs/AUDIT_20260930_TARGET_MODULAR_RANKS.md'

def need(condition,message):
    if not condition:raise ValueError(message)
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def save(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2);stream.write('\n')

def integer_determinant(matrix):
    n=len(matrix);need(all(len(row)==n and all(type(x) is int for x in row) for row in matrix),'exact square integer determinant input')
    if n==0:return 1
    b=[row.copy() for row in matrix];sign=1;previous=1
    for k in range(n-1):
        pivot=next((i for i in range(k,n) if b[i][k]),None)
        if pivot is None:return 0
        if pivot!=k:b[k],b[pivot]=b[pivot],b[k];sign=-sign
        current=b[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                numerator=current*b[i][j]-b[i][k]*b[k][j]
                quotient,remainder=divmod(numerator,previous)
                need(remainder==0,'Bareiss exact division')
                b[i][j]=quotient
            b[i][k]=0
        previous=current
    return sign*b[-1][-1]

def leibniz(matrix):
    result=0;n=len(matrix)
    for p in permutations(range(n)):
        sign=-1 if sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))%2 else 1
        term=sign
        for i in range(n):term*=matrix[i][p[i]]
        result+=term
    return result

def check_certificate(certificate,graph):
    need(len(graph)==59 and all(len(row)==59 and all(type(x) is int and x in (0,1) for x in row) for row in graph),'raw59 integer adjacency')
    need(all(graph[u][u]==0 and all(graph[u][v]==graph[v][u] for v in range(59)) for u in range(59)),'raw graph symmetry/zero diagonal')
    label=certificate['matrix'];need(label in ('A_mod3','G_mod2'),'exact matrix definition')
    prime,bound=(3,45) if label=='A_mod3' else (2,44)
    need(type(certificate['prime']) is int and certificate['prime']==prime and certificate['target_rank_upper_bound']==bound,'exact applicable field/target bound')
    need(certificate['certified_rank_lower_bound_candidate']==46,'requested46minor')
    rows,cols=certificate['rows_zero_based'],certificate['columns_zero_based']
    for chosen in (rows,cols):
        need(len(chosen)==len(set(chosen))==46 and all(type(x) is int and 0<=x<59 for x in chosen),'46distinct raw indices')
    raw=[[graph[u][v] if label=='A_mod3' else 27*int(u==v)-9*graph[u][v]+1 for v in cols] for u in rows]
    need(certificate['raw_integer_minor']==raw and all(type(x) is int for row in certificate['raw_integer_minor'] for x in row),'literal raw minor extraction')
    det=integer_determinant(raw);residue=det%prime
    need(residue!=0,'strict nonzero determinant in exact field')
    return dict(matrix=label,prime=prime,minor_order=46,integer_determinant=det,determinant_mod_prime=residue,
                certified_local_rank_at_least=46,target_rank=bound,rank_bound_violated=True,
                raw_rows=rows,raw_columns=cols,raw_minor_entries_checked=46*46)

def controls(certificate,graph):
    small=0
    for entries in product((-1,0,1),repeat=4):
        matrix=[list(entries[:2]),list(entries[2:])]
        need(integer_determinant(matrix)==leibniz(matrix),'exhaustive2x2integer control');small+=1
    for entries in product((0,1),repeat=9):
        matrix=[list(entries[3*i:3*i+3]) for i in range(3)]
        need(integer_determinant(matrix)==leibniz(matrix),'exhaustive3x3binary control');small+=1
    identity=[[int(i==j) for j in range(46)] for i in range(46)]
    need(integer_determinant(identity)==1,'order46identity positive fixture')
    swapped=[row.copy() for row in identity];swapped[0],swapped[-1]=swapped[-1],swapped[0]
    need(integer_determinant(swapped)==-1,'large row-swap sign control')
    singular=[row.copy() for row in identity];singular[-1]=singular[0].copy()
    need(integer_determinant(singular)==0,'large duplicate-row singular control')
    for prime in (2,3):
        multiple=[row.copy() for row in identity];multiple[0][0]=prime
        need(integer_determinant(multiple)!=0 and integer_determinant(multiple)%prime==0,'nonzerointeger is not modularinvertibility')
    check_certificate(certificate,graph);rejected=[]
    for name in ('corrupt_minor_entry','duplicate_row','duplicate_column','wrong_prime','wrong_target_bound','wrong_minor_order','noninteger_entry'):
        bad=deepcopy(certificate)
        if name=='corrupt_minor_entry':bad['raw_integer_minor'][0][0]+=1
        elif name=='duplicate_row':bad['rows_zero_based'][0]=bad['rows_zero_based'][1]
        elif name=='duplicate_column':bad['columns_zero_based'][0]=bad['columns_zero_based'][1]
        elif name=='wrong_prime':bad['prime']=5
        elif name=='wrong_target_bound':bad['target_rank_upper_bound']+=1
        elif name=='wrong_minor_order':bad['certified_rank_lower_bound_candidate']=45
        else:bad['raw_integer_minor'][0][0]=float(bad['raw_integer_minor'][0][0])
        try:check_certificate(bad,graph)
        except ValueError:rejected.append(name)
        else:raise ValueError('corrupted certificate accepted: '+name)
    # Exact polynomial-basis identity checks supplement the independent proof.
    # A^3+2A^2+A =12I+12A+30J, divisible by3.
    cubic=(-12,13,26);square=(12,-1,2)
    annihilator=tuple(cubic[i]+2*square[i]+(1 if i==1 else 0) for i in range(3))
    need(annihilator==(12,12,30) and all(x%3==0 for x in annihilator),'mod3annihilator expansion')
    need(14+3*54-4*44==0 and 54+44==98,'exact rational spectral multiplicities')
    need(14+3*53-4*45!=0,'corrupted multiplicity rejected by trace')
    return dict(exhaustive_direct_Leibniz_comparisons=small,large_identity_and_row_swap_passed=True,large_singular_control_passed=True,
                integer_nonzero_but_modular_zero_controls=2,positive_raw_certificate_passed=True,corruptions_rejected=rejected,
                mod3_annihilator_integer_coefficients=list(annihilator),multiplicity_trace_control_passed=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--certificates',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False);bindings={}
    def bind(path,expected=None):
        value=digest(path);need(expected is None or value==expected,'raw input hash '+str(path));bindings[key(path)]=value;return Path(path)
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    index=read(args.certificates/'index.json','0206e2c16f431f7454b55d705dfa0e4c448c72a11783d486cb0ff160ded155ed')
    for name,value in index['inputs_sha256'].items():bind(ROOT/name,value)
    screen_path=ROOT/'acceleration/results/20260930_modular_rank_screen/results.json'
    producer=read(screen_path,index['inputs_sha256'][key(screen_path)])
    manifest=read(screen_path.with_name('manifest.json'))
    for name,value in manifest['inputs_sha256'].items():bind(ROOT/name,value)
    graph_records=producer['records'];need(len(graph_records)==11,'exact11rawgraph population')
    graphs={};matrix_hashes=set()
    for record in graph_records:
        path=ROOT/record['path'];raw=read(path,record['raw_sha256']);graph=raw['adjacency_full59']
        raw_matrix_hash=sha256(bytes(x for row in graph for x in row)).hexdigest()
        need(raw_matrix_hash==record['matrix_bytes_sha256'],'raw matrix identity independent ofJSONserialization')
        matrix_hashes.add(raw_matrix_hash);graphs[record['path']]=graph
    need(len(graphs)==len(matrix_hashes)==11,'eleven distinct labeled raw matrices')
    first=read(ROOT/index['certificates'][0]['path'],index['certificates'][0]['sha256'])
    calibration=controls(first,graphs[first['raw_graph']]);save(args.out/'controls.json',calibration)
    checked=[];covered=set()
    for entry in index['certificates']:
        certificate=read(ROOT/entry['path'],entry['sha256']);path=certificate['raw_graph']
        need(path in graphs and certificate['raw_graph_sha256']==digest(ROOT/path),'minor exact graph binding')
        result=check_certificate(certificate,graphs[path]);marker=(path,result['matrix'])
        need(marker not in covered,'no repeated minor case');covered.add(marker)
        checked.append(dict(certificate=entry['path'],certificate_sha256=entry['sha256'],raw_graph=path,
                            raw_graph_sha256=certificate['raw_graph_sha256'],**result))
    need(covered=={(path,label) for path in graphs for label in ('A_mod3','G_mod2')} and len(checked)==22,'complete22lowerbound certificates')
    for path in (__file__,DERIVATION,ROOT/'uv.lock'):bind(path)
    need(all(digest(ROOT/name)==value for name,value in bindings.items()),'input stability')
    common=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='/root/eight_domain_audit independent checking agent',inputs_sha256=bindings,recommendation='VERIFIED',
        producer_imported=False,minor_selector_imported=False,shared_components=['Python standard library exact integers and JSON only',
            'Minor selector and determinant checker share rawgraph artifacts; they share no arithmetic implementation.'],
        artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False)
    theorem=dict(**common,status='INDEPENDENT_TARGET_MODULAR_RANK_THEOREMS_PASS',claim_id='C-TARGET-MODULAR-RANKS',claim_revision=1,
        kind='mathematical result',basis=['DERIVED'],dependencies=[],
        statement='Every exact target adjacency has rank54 overF2 and rank45 overF3, and its matrix27I-9A+J has rank44 overF2. Every principal submatrix has rank at most the corresponding target rank.',
        scope='Universal necessary target conditions, with no fixed configuration or graph symmetry hypothesis.',
        assumptions=['A is a99x99symmetric binary zero-diagonal matrix with A^2=12I-A+2J.'],
        written_derivation=key(DERIVATION),characteristic_polynomials=dict(A='(t-14)(t-3)^54(t+4)^44',G='t^55(t-63)^44'),
        reduced_characteristic_polynomials=dict(A_mod2='t^45(t+1)^54',A_mod3='t^54(t+1)^45',G_mod2='t^55(t+1)^44'),
        annihilators=dict(A_mod2='t(t+1)',A_mod3='t(t+1)^2',G_mod2='t(t+1)'),
        verification_type='Independent exact characteristic multiplicity and primary-decomposition proof, not numerical eigenanalysis',
        controls=calibration,limitations=['No target existence/nonexistence conclusion or novelty claim.','Diagonalizability modulo3 at the nonzero eigenvalue is not assumed.'])
    save(args.out/'theorem.json',theorem)
    report=dict(**common,status='INDEPENDENT_ELEVEN_LOCAL59_MODULAR_MINORS_PASS',claim_id='C-ROOK-ELEVEN-LOCAL59-MODULAR-MINOR-EXCLUSIONS',claim_revision=1,
        kind='exclusion',basis=['DERIVED','COMPUTED'],dependencies=[dict(id='C-TARGET-MODULAR-RANKS',revision=1,relation='uses_result')],
        statement='Each of the11exact saved59vertex adjacency matrices has an explicit46x46minor with nonzero determinant modulo3, and its27I-9H+J has an explicit46x46minor with nonzero determinant modulo2. Each therefore cannot be an induced principal subgraph of any target.',
        scope='Exactly11distinct labeled raw adjacency matrices and22checked lower-bound minors; neither allisomorphism types nor a whole family.',
        assumptions=['The universal exact target-rank theorem and the fixed raw adjacency/certificate hashes.'],
        verification_type='Complete literal raw integer minor extraction and separate fraction-free integer determinant computation, then exact modular reduction',
        raw_graphs=11,distinct_labeled_raw_matrices=11,minor_certificates_checked=22,minor_order=46,checked_minors=checked,
        controls=calibration,theorem_report=key(args.out/'theorem.json'),theorem_sha256=digest(args.out/'theorem.json'),
        original_full_rank_values_independently_approved=False,
        original_A_mod2_local_tests=None,original_A_mod2_local_tests_null_reason='Not needed for these exclusions; reportedfullranks are not promoted by this lower-bound-only check.',
        producer_warning_note='The frozen Python3.12producer emitted spacing SyntaxWarnings for0for/1for and exited0. Its source and manifest are preserved; warnings are not a mathematical refutation.',
        limitations=['The producer full local rank values are not independently certified here; only the explicit rank>=46 lower bounds are approved.',
                     'The11objects were already excluded by earlier Gram/local checks; this is alternate necessary-condition evidence, not additional target-wide coverage.',
                     'No whole780edge family exclusion, arbitrary target containment, graph-isomorphism count, novelty, or general nonexistence claim.'])
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],minors=len(checked),theorem_sha256=digest(args.out/'theorem.json'),summary_sha256=digest(args.out/'summary.json'))))

if __name__=='__main__':main()
