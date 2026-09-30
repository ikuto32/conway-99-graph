"""Independent universal-coverage derivation and literal artifact checks."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,permutations
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_unrestricted_triangle_factor'
SUMMARY_SHA='fecb50f01e6548c79e486068eeea3ca41dd6922ed4cf74686d9757ae0061b2eb'
def need(ok,message):
    if not ok:raise ValueError(message)
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def read(p):return json.loads(Path(p).read_bytes())

def validate_types(matchings,p):
    n=len(p);need(n>0 and n%2==0 and len(matchings)==3,'even dimensions')
    need(all(type(x) is int for x in p) and sorted(p)==list(range(n)),'cross permutation')
    for q in matchings:need(len(q)==n and all(type(x) is int and 0<=x<n for x in q) and all(q[i]!=i and q[q[i]]==i for i in range(n)),'fixed-point-free matching involution')

def raw_graph(matchings,p):
    validate_types(matchings,p);n=len(p);h=[[0]*(3+3*n) for _ in range(3+3*n)]
    def edge(i,j):h[i][j]=h[j][i]=1
    for i,j in combinations(range(3),2):edge(i,j)
    for f in range(3):
        for a in range(n):edge(f,3+f*n+a);edge(3+f*n+a,3+f*n+matchings[f][a])
    for a in range(n):edge(3+a,3+n+a);edge(3+a,3+2*n+a);edge(3+n+a,3+2*n+p[a])
    return h

def literal_gram(h,n):
    neighbours=[{j for j,x in enumerate(row) if x} for row in h]
    return [[n*int(a==b)+2-h[3+a][3+b]-len(neighbours[3+a]&neighbours[3+b]) for b in range(3*n)] for a in range(3*n)]

def formula_gram(matchings,p):
    validate_types(matchings,p);n=len(p);g=[[0]*(3*n) for _ in range(3*n)]
    for i in range(3*n):
        f,a=divmod(i,n)
        for j in range(i,3*n):
            k,b=divmod(j,n)
            if f==k:v=(n-3)*int(a==b)+1-int(matchings[f][a]==b)
            elif (f,k)==(0,1):v=2-int(a==b)-int(matchings[0][a]==b)-int(matchings[1][a]==b)-int(p[b]==a)
            elif (f,k)==(0,2):v=2-int(a==b)-int(matchings[0][a]==b)-int(matchings[2][a]==b)-int(p[a]==b)
            else:v=2-int(a==b)-int(p[a]==b)-int(p[matchings[1][a]]==b)-int(matchings[2][p[a]]==b)
            g[i][j]=g[j][i]=v
    return g

def fixture_check(record):
    q,p=record['matchings'],record['P_row_to_column'];h=raw_graph(q,p);n=len(p)
    need(record['core36']==[r[3:] for r in h[3:]],'every saved core entry')
    g=literal_gram(h,n);need(g==formula_gram(q,p)==record['prescribed_Gram'],'all literal and symbolic Gram entries')
    need(record['P_is_involution']==all(p[p[i]]==i for i in range(n)),'permutation type metadata')
    need(record['local_feasibility_asserted'] is False,'arbitrary algebra fixtures only')
    return h,g

def srg_check(a,k):
    n=len(a);need(all(len(row)==n and all(type(x) is int and x in (0,1) for x in row) for row in a),'raw binary square')
    need(all(a[i][i]==0 and sum(a[i])==k for i in range(n)),'diagonal and degrees')
    need(all(a[i][j]==a[j][i] for i,j in combinations(range(n),2)),'symmetry')
    nb=[{j for j,x in enumerate(row) if x} for row in a]
    need(all(len(nb[i]&nb[j])==((k-2)*int(i==j)-a[i][j]+2) for i in range(n) for j in range(n)),'exact integer identity')

def rook_case_check(record,index):
    a=record['normalized_adjacency'];srg_check(a,4);labels=record['new_to_old_labels']
    need(sorted(labels)==list(range(9)) and labels[:3]==record['root'],'normalization permutation and root')
    q,p=record['matchings'],record['P_row_to_column'];need(q[0]==[1,0],'standard M0')
    need(a==raw_graph(q,p),'all normalized rook scaffold entries')
    need(record['Y_size']==0 and record['C0_degenerate'] is True and record['incidence']==[[] for _ in range(6)],'explicit empty-Y control')
    if index<6:
        rook=[[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)]
        need(a==[[rook[i][j] for j in labels] for i in labels],'literal original rook relabelling')

def canonical_check(raw,matching):
    n=len(matching);expected=[(i,j) for i,j in combinations(range(n),2) if matching[i]!=j]
    need(len(raw)==n and all(len(row)==len(expected) and all(type(x) is int and x in (0,1) for x in row) for row in raw),'canonical incidence shape')
    labels=[tuple(i for i in range(n) if raw[i][d]) for d in range(len(expected))]
    need(sorted(labels)==expected,'complete nonmatching-pair bijection')
    return [labels.index(pair) for pair in expected]

def mixed_checks(h,seed):
    rng=random.Random(seed);f=[[rng.randrange(2) for _ in range(60)] for _ in range(36)]
    nb=[set() for _ in range(99)]
    for i in range(39):
        for j in range(39):
            if h[i][j]:nb[i].add(j)
    for r in range(36):
        for d in range(60):
            if f[r][d]:nb[3+r].add(39+d);nb[39+d].add(3+r)
    for r in range(36):
        for d in range(60):
            direct=len(nb[3+r]&nb[39+d]);formula=sum(h[3+r][3+s]*f[s][d] for s in range(36))
            need(direct==formula,'every literal mixed known-common count')
            need((direct+f[r][d]<=2)==(formula<=2-f[r][d]),'mixed pair cap orientation')
    for d,e in combinations(range(60),2):need(len(nb[39+d]&nb[39+e])==sum(f[r][d]*f[r][e] for r in range(36)),'every literal outside known-common count')
    return dict(seed=seed,mixed_pairs=2160,outside_pairs=1770,feasible_factor_claimed=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(p,expected=None):
        p=Path(p);value=digest(p);need(expected is None or value==expected,'hash '+str(p));bindings[key(p)]=value;return p
    try:
        summary=read(bind(D/'summary.json',SUMMARY_SHA))
        for p,value in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():bind(ROOT/p,value)
        fixtures=read(D/'arbitrary12_core_coefficients.json');need(len(fixtures)==12,'saved core population')
        checks=[]
        for i,fixture in enumerate(fixtures):h,g=fixture_check(fixture);checks.append(mixed_checks(h,20261000+i))
        matchings=[[1,0,3,2],[2,3,0,1],[3,2,1,0]];small=0
        for q1 in matchings:
            for q2 in matchings:
                for p in permutations(range(4)):
                    qs=[matchings[0],q1,q2];need(literal_gram(raw_graph(qs,p),4)==formula_gram(qs,p),'complete four-coordinate coefficient population');small+=1
        need(small==216,'small population count')
        rook=read(D/'rook9_normalization_controls.json');need(rook['SRG_parameters']==[9,4,1,2] and len(rook['cases'])==12,'rook population')
        for i,record in enumerate(rook['cases']):rook_case_check(record,i)
        codec=read(D/'nonempty_C0_codec_controls.json');canonical=[[int(i in pair) for pair in combinations(range(12),2) if pair[1]!=(pair[0]^1)] for i in range(12)]
        need(codec['raw_canonical_C0']==canonical and len(codec['cases'])==6,'nonempty canonical codec population')
        for record in codec['cases']:
            order=record['input_column_order'];need(sorted(order)==list(range(60)),'input column permutation')
            raw=[[row[d] for d in order] for row in canonical];got=canonical_check(raw,[i^1 for i in range(12)])
            need(got==record['recovered_column_order'] and [order[d] for d in got]==list(range(60)),'complete recovered column mapping')
        rejected=[]
        def reject(name,fn):
            try:fn()
            except (ValueError,IndexError,KeyError):rejected.append(name)
            else:raise ValueError('corruption accepted '+name)
        for label in ['Gram_entry','core_edge','wrong_P_metadata','matching_fixed_point','permutation_duplicate']:
            bad=deepcopy(fixtures[2])
            if label=='Gram_entry':bad['prescribed_Gram'][0][12]+=1
            elif label=='core_edge':bad['core36'][0][12]^=1
            elif label=='wrong_P_metadata':bad['P_is_involution']=not bad['P_is_involution']
            elif label=='matching_fixed_point':bad['matchings'][1][0]=0
            else:bad['P_row_to_column'][1]=bad['P_row_to_column'][0]
            reject(label,lambda:fixture_check(bad))
        bad=deepcopy(next(f for f in fixtures if not f['P_is_involution']));p=bad['P_row_to_column']
        for a in range(12):
            for b in range(12):bad['prescribed_Gram'][a][12+b]+=int(p[b]==a)-int(p[a]==b)
        reject('P_not_transpose_in_G01',lambda:fixture_check(bad))
        bad=deepcopy(rook['cases'][0]);bad['normalized_adjacency'][0][1]^=1;reject('corrupt_rook_edge',lambda:rook_case_check(bad,0))
        bad=deepcopy(rook['cases'][0]);bad['new_to_old_labels'][1]=bad['new_to_old_labels'][0];reject('duplicate_vertex_label',lambda:rook_case_check(bad,0))
        bad=[row[:] for row in canonical]
        for row in bad:row[1]=row[0]
        reject('duplicate_C0_column',lambda:canonical_check(bad,[i^1 for i in range(12)]))
        bad=[row[:] for row in canonical]
        for a,row in enumerate(bad):row[0]=int(a in (0,1))
        reject('matched_C0_column',lambda:canonical_check(bad,[i^1 for i in range(12)]))
        archive=read(D/'archive_overlap.json');archive_checks=[]
        for ref in archive['references']:
            raw=subprocess.check_output(['git','-C',str(ROOT/'external_conway99_research'),'show',ref['commit']+':'+ref['path']])
            need(sha256(raw).hexdigest()==ref['sha256'],'immutable archive identity')
            bind(ROOT/'external_conway99_research'/ref['path'],ref['sha256']);archive_checks.append({k:ref[k] for k in ['repository','commit','path','sha256','section']})
        controls=dict(saved12coordinate_cores=12,integer_Gram_entries_per_saved_core=1296,exhaustive_fourcoordinate_cores=small,rook9_positive_normalizations=12,rook_Y_empty=True,nonempty_C0_codec_cases=6,mixed_formula_controls=checks,corruptions_rejected=rejected)
        save(args.out/'controls.json',controls)
        bind(Path(__file__));bind(ROOT/'docs/AUDIT_20260930_UNRESTRICTED_TRIANGLE_FACTOR.md')
        need(all(digest(ROOT/p)==value for p,value in bindings.items()),'stable frozen inputs')
        report=dict(status='INDEPENDENT_UNRESTRICTED_TRIANGLE_FACTOR_NORMALIZATION_PASS',claim_id='C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION',claim_revision=1,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/eight_domain_audit independent derivation and literal graph checker',recommendation='VERIFIED',review_state='CLEAR',kind='mathematical result',basis=['DERIVED','COMPUTED'],
          statement=summary['statement'],scope='Every unrestricted target admits the stated normalized arbitrary-core factor form. Conversely the factor conditions establish only the stated partial99 specification, with residual D absent.',
          assumptions=['Symmetric binary zero-diagonal99x99 A and exact integer identity A^2=12I-A+2J.'],dependencies=[],dependencies_reason='Independent direct derivation from the target identity, with no historical result or fixed-core exclusion needed as a premise.',
          written_review='docs/AUDIT_20260930_UNRESTRICTED_TRIANGLE_FACTOR.md',coverage_method='Universal constructive relabelling argument; no finite sample is used to establish target coverage.',controls=controls,archive_checks=archive_checks,producer_imports=False,shared_components=['Python standard library and immutable raw producer artifacts only; independent graph/common-neighbour implementation.'],
          limitations=['A factor is not a complete graph and no existence, nonexistence or search-coverage percentage follows.','No automorphism, prism-free restriction, symmetric P or commuting matchings are assumed.','Rook9 controls have empty Y; arbitrary core and incidence controls are not feasible research factors.','No novelty or inherited historical verification labels are claimed.'],solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e),inputs_sha256=bindings));raise

if __name__=='__main__':main()
