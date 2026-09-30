"""Independent exact restricted encoding, DRAT replay and bit-parity proof."""
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, permutations, product
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_prism_factor_design_pilot/'
HELPER='acceleration/audit_20260930_triangle_wave154_unsat.py'
HELPER_SHA='b7b98d9da7986fac7c005fb9a6d4e5b9cd2811ea46a8ea75a6e7e34933e4b649'
CNF_SHA='4fcda92fda7b82b2225448f744293d0fedd3f0a4786025603d1aeecc6edeaeaf'
PROOF_SHA='5a1f7c0dd73e5f416ea01b93400db7b6e645b45d45cc3c78cea63d89497d38e6'
MODEL_SHA='a64b2b1bb1f3a0580ef0eb94354069fe617d37103cb55ae10965126cc6891c12'
DOC='docs/AUDIT_20260930_PRISM_COMPLEMENT_DESIGN.md'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def h(p):
    import hashlib
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
need(h(ROOT/HELPER)==HELPER_SHA,'frozen independent checker-helper identity')
import audit_20260930_triangle_wave154_unsat as drat
# Reuse only its source/build authentication and native replay functions.
# Remove unrelated Wave154 research inputs from this helper's configuration.
drat.PINS={p:v for p,v in drat.PINS.items()if p.startswith(drat.BUILD)}

def load(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def canon(c):return tuple(sorted(c,key=lambda v:(abs(v),v)))
def clause_ok(c,assignment):return any(bool(assignment[abs(x)-1])==(x>0)for x in c)

@lru_cache(None)
def prime_relation(n,name):
    truth=list(product((0,1),repeat=n))
    allowed=[v for v in truth if (v[2]==(v[0]^v[1]) if name=='xor' else sum(v)==n//2)]
    valid=[]
    for width in range(1,n+1):
        for support in combinations(range(1,n+1),width):
            for signs in product((-1,1),repeat=width):
                c=tuple(i*s for i,s in zip(support,signs))
                if all(clause_ok(c,v)for v in allowed)and not any(set(p)<=set(c)for p in valid):valid.append(c)
    need(all(all(clause_ok(c,v)for c in valid)==(v in allowed)for v in truth),'complete prime-clause truth relation')
    return tuple(valid)

def restriction(model):
    matchings=[]
    for t in range(5):matchings.append([[5,t],[(t+1)%5,(t-1)%5],[(t+2)%5,(t-2)%5]])
    need(sorted(tuple(sorted(e))for m in matchings for e in m)==list(combinations(range(6),2)),'five matchings exactly partition K6 edges')
    expected_patterns=[];var=0
    for mi,m in enumerate(matchings):
        for colors in permutations(range(3)):
            cells=[None]*6
            for (a,b),g in zip(m,colors):cells[a]=cells[b]=g
            bits=[0]+list(range(var+1,var+6));var+=5
            expected_patterns.append(dict(matching=mi,cells=cells,bit_variables=bits))
    need(model['matchings']==matchings and model['patterns']==expected_patterns,'all30 patterns exact restricted universe and orientation')
    need(all(sum(p['cells'][a]==g for p in expected_patterns)==10 for a in range(6)for g in range(3)),'automatic row10 margins')
    need(all(Counter(p['cells'])=={0:2,1:2,2:2}for p in expected_patterns),'each column fibre2')
    clauses=[];parity={}
    def relation(ids,name):
        clauses.extend([[(1 if x>0 else -1)*ids[abs(x)-1]for x in c]for c in prime_relation(len(ids),name)])
    for t,p in enumerate(expected_patterns):
        for a,b in combinations(range(6),2):
            if a==0:parity[t,a,b]=p['bit_variables'][b]
            else:
                var+=1;parity[t,a,b]=var;relation([p['bit_variables'][a],p['bit_variables'][b],var],'xor')
    constraints=[]
    for a,b in combinations(range(6),2):
        for g in range(3):
            for k in range(3):
                indices=[t for t,p in enumerate(expected_patterns)if (p['cells'][a],p['cells'][b])==(g,k)]
                need(len(indices)==(2 if g==k else 4),'restricted component/cell population')
                ids=[parity[t,a,b]for t in indices];relation(ids,'half')
                constraints.append(dict(components=[a,b],cells=[g,k],patterns=indices,parity_variables=ids,odd_count=len(ids)//2))
    need(model['constraints']==constraints,'all135 recorded constraints')
    need(var==450 and len(clauses)==2010,'450 variables2010clauses')
    expected=Counter(canon(c)for c in clauses)
    need(Counter(canon(c)for c in model['clauses'])==expected,'model clause multiset exact independent prime clauses')
    return expected,dict(patterns=30,primary_bits=150,extension_XORs=300,component_cell_constraints=135,variables=450,clauses=2010,proof='See independent written counting/necessity/sufficiency derivation.')

def parse_cnf(path):
    lines=Path(path).read_text('ascii').splitlines();need(lines[0]=='p cnf 450 2010','exact header')
    clauses=[]
    for line in lines[1:]:
        ns=list(map(int,line.split()));need(ns and ns[-1]==0 and all(1<=abs(v)<=450 for v in ns[:-1]),'clause IDs and terminator');clauses.append(ns[:-1])
    need(len(clauses)==2010,'actual clause count')
    return Counter(canon(c)for c in clauses)

def parity_check():
    c=[[0]*36 for _ in range(36)]
    for g in range(3):
        for a in range(6):
            for b in range(2):
                i=12*g+2*a+b;c[i][12*g+2*a+1-b]=1
                for other in range(3):
                    if other!=g:c[i][12*other+2*a+b]=1
    k=[[12*int(i==j)-c[i][j]-sum(c[i][t]*c[t][j]for t in range(36))+2-int(i//12==j//12)for j in range(36)]for i in range(36)]
    components=[[12*g+2*a+b for g in range(3)for b in range(2)]for a in range(6)]
    contrast=[]
    for a in range(1,6):
        v=[int(i in components[a])-int(i in components[0])for i in range(36)]
        need(all(sum(k[i][j]*v[j]for j in range(36))==0 for i in range(36)),'literal Gram kernel contrast');contrast.append(v)
    pair_totals=[]
    for a,d in combinations(range(6),2):
        for b,e in product(range(2),repeat=2):
            entries=[k[12*g+2*a+b][12*j+2*d+e]for g,j in product(range(3),repeat=2)]
            need(entries==[1 if g==j else 2 for g,j in product(range(3),repeat=2)],'all cross-component row intersections')
            need(sum(entries)==15,'component bit pair count15');pair_totals.append(dict(components=[a,d],bits=[b,e],nine_Gram_entries=entries,total=15))
    coordinate_controls=[]
    for bits in product((0,1),repeat=3):
        total=sum(bits[i]!=bits[j]for i,j in combinations(range(3),2));need(total in (0,2),'coordinate triple parity');coordinate_controls.append(dict(bits=bits,total=total))
    # Positive generic paired/balanced6-bit table on16columns, not a research F.
    representatives=[[((mask&word).bit_count()&1)for mask in range(1,7)]for word in range(8)]
    columns=[v for r in representatives for v in [r,[1-x for x in r]]]
    need(all(sum(r[a]for r in columns)==8 for a in range(6)),'positive balanced bit marginals')
    need(all(Counter((r[a],r[b])for r in columns)=={(0,0):4,(0,1):4,(1,0):4,(1,1):4}for a,b in combinations(range(6),2)),'positive pair balances4')
    need(all(sum(r[a]!=r[b]for r in representatives)==4 for a,b in combinations(range(6),2)),'positive representative even distances')
    # Exhaust all triples of length3 words, rather than only repeated equations.
    allwords=list(product((0,1),repeat=3));odd_triangles=0
    for x,y,z in product(allwords,repeat=3):
        ds=[sum(a!=b for a,b in zip(u,v))for u,v in [(x,y),(y,z),(z,x)]]
        need(sum(ds)%2==0,'all512 triple-word parity checks');odd_triangles+=int(all(d%2 for d in ds))
    need(odd_triangles==0 and (15*3)%2==1,'required odd-distance triangle impossible')
    bad=[r[:]for r in columns];bad[0][0]^=1
    need(any(Counter((r[a],r[b])for r in bad)!={(0,0):4,(0,1):4,(1,0):4,(1,1):4}for a,b in combinations(range(6),2)),'corrupted positive bit table fails pair count')
    return dict(core36=c,Gram36=k,components=components,kernel_contrasts=contrast,all60bit_pair_totals=pair_totals,
        coordinate_truth_controls=coordinate_controls,positive16column_table=columns,positive_fixture_is_research_factor=False,
        exhaustive_length3_word_triples=512,all_odd_distance_triangles=0,corrupted_table_rejected=True,
        mathematical_derivation=DOC,cell_choice_preservation_used_for_final_parity=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args();out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False);start=time.monotonic();inputs={}
    def bind(path,expected=None):
        got=h(ROOT/path);need(expected is None or got==expected,'input hash '+path);inputs[path]=got
    try:
        for path,expected in [(B+'instance.cnf',CNF_SHA),(B+'proof.drat',PROOF_SHA),(B+'model.json',MODEL_SHA),(HELPER,HELPER_SHA)]:bind(path,expected)
        producer=load(B+'summary.json');bind(B+'summary.json')
        for path,expected in producer['outputs_sha256'].items():bind(path,expected)
        manifest=load(B+'manifest.json')
        for path,expected in manifest['inputs_sha256'].items():bind(path,expected)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=inputs.copy(),question='Is the exact five-matching complement-paired formula UNSAT, and does a separate parity proof exclude every global complement-paired factor of this fixed six-prism core?',resource_limits=dict(each_proof_check_seconds=120),numerical_thresholds=None,numerical_thresholds_null_reason='Exact Boolean/integer arithmetic and complete DRAT checking.'))
        model=load(B+'model.json');expected,encoding=restriction(model);need(parse_cnf(ROOT/(B+'instance.cnf'))==expected,'all actual2010clauses independent equivalence')
        controls=[]
        for n,name in [(3,'xor'),(2,'half'),(4,'half')]:
            clauses=prime_relation(n,name);controls.append(dict(relation=name,variables=n,assignments=2**n,prime_clauses=[list(c)for c in clauses]))
            need(all(any(not clause_ok(c,v)and all(clause_ok(d,v)for j,d in enumerate(clauses)if j!=i)for v in product((0,1),repeat=n))for i,c in enumerate(clauses)),'removing every prime clause detected by truth oracle')
        broken=expected.copy();one=next(iter(broken));broken[one]-=1;need(broken!=expected,'missing actual clause corruption')
        broken=model.copy();broken['clauses']=[r[:]for r in model['clauses']];broken['clauses'][0][0]*=-1
        try:restriction(broken)
        except ValueError:pass
        else:raise ValueError('changed auxiliary clause accepted')
        save(out/'encoding_check.json',dict(**encoding,controls=controls,missing_clause_rejected=True,changed_auxiliary_sign_rejected=True))
        save(out/'parity_derivation_checks.json',parity_check())
        provenance=drat.authenticate(inputs)
        tiny={'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n',
              'tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','valid.drat':b'-2 0\n1 0\n0\n',
              'empty_only.drat':b'0\n','fresh_unit.drat':b'3 0\n0\n'}
        for name,data in tiny.items():(out/name).write_bytes(data)
        need(not any(all(clause_ok(c,v)for c in [(1,2),(1,-2),(-1,2),(-1,-2)])for v in product((0,1),repeat=2)),'tiny UNSAT independent truth table')
        need(all(clause_ok(c,(1,1))for c in [(1,2),(1,-2),(-1,2)]),'tiny SAT literal positive')
        specs=[('positive_tiny',out/'tiny_unsat.cnf',out/'valid.drat',True),('corrupt_empty_only',out/'tiny_unsat.cnf',out/'empty_only.drat',False),
               ('corrupt_fresh_unit',out/'tiny_unsat.cnf',out/'fresh_unit.drat',False),('corrupt_sat_formula',out/'tiny_sat.cnf',out/'valid.drat',False),
               ('corrupt_main_empty',ROOT/(B+'instance.cnf'),out/'empty_only.drat',False),('complete_main_proof',ROOT/(B+'instance.cnf'),ROOT/(B+'proof.drat'),True)]
        replays=[drat.replay(name,cnf,proof,out,want)for name,cnf,proof,want in specs]
        need(producer['receipt']['actual_exit_code']==20 and not producer['receipt']['outer_windows_guard_expired'],'actual recorded native20 and completed worker')
        for path,expected_hash in list(inputs.items()):bind(path,expected_hash)
        for path in [key(__file__),DOC,'uv.lock','pyproject.toml']:bind(path)
        common=dict(claim_revision=1,recommendation='VERIFIED',review_state='CLEAR',kind='exclusion',basis=['DERIVED','COMPUTED'],verifier='/root/state_literature_audit',method='independent_derivation_and_artifact_check',target_resolution=False,external_review=False)
        claims=[dict(**common,claim_id='C-SIX-PRISM-FIVE-MATCHING-COMPLEMENT-DESIGN-EXCLUSION',statement='No binary36x60 incidence factor with the fixed six-prism Gram and margins is represented by the specified five round-robin matchings, all six cell-label assignments per matching, and30globally complementary column pairs. Its exact450variable2010clause Boolean encoding is UNSAT.',scope='Only the explicit frozen restricted construction design.',dependencies=[],evidence=['encoding_check.json','complete_main_proof.receipt.json'],limitations=['No exclusion of arbitrary incidence factors, the whole six-prism core, or the unrestricted target.']),
                dict(**common,claim_id='C-SIX-PRISM-GLOBAL-COMPLEMENT-PAIRING-EXCLUSION',statement='For the fixed standard-matchings/identity-cross-matching six-prism core, no binary36x60 incidence factor satisfying FF^T=12I-C-C^2+2J-diag(J12,J12,J12), row sums10 and fibre-column sums2 admits a partition of its60columns into30pairs that preserve all six component cell labels while complementing all six component bits.',scope='All cell-pattern choices under this explicit global complement-pairing restriction; not limited to the five matching patterns.',dependencies=[],evidence=[DOC,'parity_derivation_checks.json'],limitations=['This restricts a proposed factor construction; no target automorphism is assumed.','No unrestricted factor/core/target exclusion or existence result.','The samples calibrate exact count checks; universal contradiction is the written Hamming-distance parity proof.'])]
        save(out/'summary.json',dict(status='INDEPENDENT_PRISM_RESTRICTED_DESIGN_AND_COMPLEMENT_PARITY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),claims=claims,inputs_sha256=inputs,producer_imports=False,
            shared_components=['Frozen independent build-authentication/native-proof-replay helper, configured only for its checker build pins.','Authenticated drat-trim proof checker and its historical compiler build; no diverse formal kernel claim.','Python standard library.'],
            checker_provenance=provenance,checker_controls_and_replay=replays,cnf_sha256=CNF_SHA,proof_sha256=PROOF_SHA,proof_bytes=(ROOT/(B+'proof.drat')).stat().st_size,
            native_solver_version='CaDiCaL1.9.5 commit146207318796f094dcded87349a64f0c6927309e',native_solver_command=producer['receipt']['command'],native_actual_exit_code=20,
            artifact_availability='LOCAL_ONLY',artifact_availability_reason='All exact inputs,trace,source/build provenance and raw audit logs are present; publication controlled by parent.',target_resolution=False,external_review=False,
            outputs_sha256={key(p):h(p)for p in sorted(out.iterdir())if p.is_file()},elapsed_seconds=time.monotonic()-start))
        print(json.dumps(dict(status='INDEPENDENT_PRISM_RESTRICTED_DESIGN_AND_COMPLEMENT_PARITY_PASS',report_sha256=h(out/'summary.json'))))
    except BaseException as e:
        save(out/'failure.json',dict(status='CHECK_FAILED',timestamp=datetime.now(timezone.utc).isoformat(),error=repr(e),inputs_sha256=inputs));raise

if __name__=='__main__':main()
