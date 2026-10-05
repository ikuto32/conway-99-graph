"""Bind independent Gram-minor census to all raw producer rank/kernel certificates."""
import argparse, copy, gzip, hashlib, json, math, platform, subprocess, sys
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_six_exception_census'
I=B/'20260930_independent_review/six_group_rank_preparation'
M=B/'20260930_independent_review/hadamard_few_exception_marginals'
PINS={D/'summary.json':'42add93a6d929e244aa0f32d16083beabc47cc0f02fedccff33280131383b74f',I/'summary.json':'4dcc7a97c52f92e7da1eae860dcb9e8a3484cb4eff8690e16cebdd591ac1da33',M/'summary.json':'6b9512567a77ef3bad2fbb1b581fadb30c486c9ac4151543001705776e0c5df9'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def write(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def det_mod(matrix,p=1000003):
    A=[[v%p for v in row] for row in matrix];value=1
    for i in range(len(A)):
        k=next((k for k in range(i,len(A)) if A[k][i]),None)
        if k is None:return 0
        if k!=i:A[k],A[i]=A[i],A[k];value=-value
        pivot=A[i][i];value=value*pivot%p;inverse=pow(pivot,-1,p)
        for r in range(i+1,len(A)):
            factor=A[r][i]*inverse%p
            for c in range(i,len(A)):A[r][c]=(A[r][c]-factor*A[i][c])%p
    return value%p
def validate_certificate(H,cert,rank):
    need(cert['rank']==rank,'independent rank agrees')
    rows,cols=cert['minor_rows'],cert['minor_columns'];free=cert['free_columns']
    need(len(rows)==len(cols)==rank and len(set(rows))==rank and len(set(cols))==rank,'independent minor index shape')
    need(all(type(i) is int and 0<=i<13 for i in rows) and all(type(j) is int and 0<=j<6 for j in cols),'raw minor ranges')
    need(free==[j for j in range(6) if j not in cols],'free column partition')
    minor=[[H[i][j] for j in cols] for i in rows];need(minor==cert['minor'],'literal producer minor entries')
    d=cert['determinant'];need(type(d) is int and 0<abs(d)<=math.factorial(rank),'nonzero determinant exact bound')
    need(d%1000003==det_mod(minor),'exact determinant via residue and n-factorial bound')
    kernel=cert['integer_null_basis'];need(len(kernel)==6-rank,'kernel dimension')
    for v in kernel:
        need(len(v)==6 and all(type(x) is int for x in v) and math.gcd(*v)==1,'primitive integral null vector')
        need(all(sum(a*b for a,b in zip(row,v))==0 for row in H),'all literal null equations')
    if free:need(det_mod([[v[j] for j in free] for v in kernel])!=0,'saved null vectors independent')
def category(rank,kernel,common):
    if rank==6:return 'EXCLUDED_FULL_COLUMN_RANK'
    if rank==4:return 'RETAINED_KERNEL_DIMENSION_AT_LEAST_TWO'
    need(rank==5,'explicit finite rank treatment')
    v=kernel[0]
    if not all(v):return 'EXCLUDED_ZERO_KERNEL_COORDINATE'
    if max(map(abs,v))>1:return 'EXCLUDED_INTEGER_COEFFICIENT_MAGNITUDE'
    need(sorted(v)==[-1,-1,-1,1,1,1] and len(common)<2,'full sign line requires but lacks two common coordinates')
    return 'EXCLUDED_COMMON_SUPPORT_AT_MOST_ONE'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        v=sha(p);need(h is None or v==h,'pin '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        producer=read(D/'summary.json');independent=read(I/'summary.json');marginal=read(M/'summary.json')
        for report in [producer,independent,marginal]:
            for p,h in {**report['inputs_sha256'],**report['outputs_sha256']}.items():pin(ROOT/p,h)
        need(marginal['status']=='INDEPENDENT_HADAMARD_FEW_EXCEPTION_MARGINALS_PASS','full-Gram marginal premise')
        raw=read(B/'20260930_hadamard20_support/six_prism.json');groups=list(dict.fromkeys(tuple(i for i in range(12) if raw['L'][i][d]) for d in range(60)))
        H=[[1]*20]+[[int(a in g) for g in groups] for a in range(12)];global_saved=read(D/'global_marginal_matrix.json')
        need(global_saved==dict(groups=[list(s) for s in groups],matrix=H,rows=['leading_one',*range(12)]),'exact global matrix')
        marg=read(M/'independent_marginal_certificates.json');bridge=[]
        for a in range(12):
            gs=[g for g,s in enumerate(groups) if a in s];other=[b for b in range(12) if b not in [a,a^1]]
            expected=[[1]*10]+[[int(b in groups[g]) for g in gs] for b in other]
            need(marg['matrices'][a]['matrix']==expected and marg['matrices'][a]['groups']==gs,'exact marginal matrices')
            need([H[a+1][g] for g in gs]==[1]*10 and [H[(a^1)+1][g] for g in gs]==[0]*10,'self/absent-mate bridge')
            bridge.append(dict(coordinate=a,incident_groups=gs,rows=[0]+[b+1 for b in other],duplicate_leading_row=a+1,zero_row=(a^1)+1))
        paircounts=read(I/'pair_multiplicities.json');need(len(paircounts)==66,'all raw coordinate pairs')
        for pair,rec in zip(combinations(range(12),2),paircounts,strict=True):need(rec['pair']==list(pair) and rec['groups']==[g for g,s in enumerate(groups) if all(a in s for a in pair)],'literal pair multiplicity')
        need(Counter(len(r['groups']) for r in paircounts)=={0:6,5:60},'six groups cannot share two coordinates')
        prepared=read(I/'records.json');need(prepared['complete_population']==len(prepared['records'])==38760,'independent complete census')
        rankcounts=Counter();classes=Counter();remaining=[];templates={}
        with gzip.open(D/'all_subsets.jsonl.gz','rt',encoding='utf-8') as f:
            for index,(ids,ref) in enumerate(zip(combinations(range(20),6),prepared['records'],strict=True)):
                line=f.readline();need(bool(line),'producer complete population');r=json.loads(line)
                need(r['index']==index and r['groups']==list(ids)==ref['groups'],'exact lexicographic coverage')
                matrix=[[row[g] for g in ids] for row in H];validate_certificate(matrix,r['certificate'],ref['rank'])
                common=sorted(set.intersection(*(set(groups[g]) for g in ids)));need(common==r['common_support']==ref['common_support'],'six-way raw intersection')
                v=r['certificate']['integer_null_basis'];cl=category(ref['rank'],v,common);need(r['classification']==cl,'proof-supported classification')
                if ref['rank']==5:
                    need(v[0]==ref['kernel'][0],'same canonical primitive rank5 kernel')
                    b=r['primitive_Bezout'];need(len(b)==6 and all(type(x) is int for x in b) and sum(a*z for a,z in zip(b,v[0]))==1,'literal primitive lattice certificate')
                rankcounts[ref['rank']]+=1;classes[cl]+=1;templates.setdefault(cl,(r,matrix))
                if cl.startswith('RETAINED'):remaining.append(r)
            need(not f.read().strip(),'no duplicate or extra producer records')
        need(rankcounts=={6:35587,5:3164,4:9} and sum(rankcounts.values())==38760,'complete rank counts')
        need(producer['rank_counts']=={str(k):v for k,v in sorted(rankcounts.items())} and producer['class_counts']==dict(classes),'producer aggregate classifications')
        rem=read(D/'remaining_candidates.json');need(rem['records']==remaining and rem['count']==producer['remaining_necessary_subsets']==9,'every rank4 retained exactly')
        need(all(r['certificate']['rank']==4 for r in remaining),'no one-dimensional survivors')
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,KeyError,IndexError,TypeError):rejected.append(name)
            else:raise ValueError('accepted corruption '+name)
        rec,matrix=templates['EXCLUDED_FULL_COLUMN_RANK'];bad=copy.deepcopy(rec['certificate']);bad['determinant']+=1;reject('wrong_minor_determinant',lambda:validate_certificate(matrix,bad,6))
        bad=copy.deepcopy(rec['certificate']);bad['minor'][0][0]^=1;reject('wrong_minor_entry',lambda:validate_certificate(matrix,bad,6))
        rec,matrix=templates['EXCLUDED_INTEGER_COEFFICIENT_MAGNITUDE'];bad=copy.deepcopy(rec['certificate']);bad['integer_null_basis'][0][0]+=1;reject('wrong_null_vector',lambda:validate_certificate(matrix,bad,5))
        bad=copy.deepcopy(rec['certificate']);bad['integer_null_basis'][0]=[2*x for x in bad['integer_null_basis'][0]];reject('nonprimitive_vector',lambda:validate_certificate(matrix,bad,5))
        rec,matrix=templates['RETAINED_KERNEL_DIMENSION_AT_LEAST_TWO'];bad=copy.deepcopy(rec['certificate']);bad['integer_null_basis'][1]=bad['integer_null_basis'][0][:];reject('dependent_null_basis',lambda:validate_certificate(matrix,bad,4))
        reject('discard_rank4_by_basis_vector',lambda:need(category(4,rec['certificate']['integer_null_basis'],[])!='RETAINED_KERNEL_DIMENSION_AT_LEAST_TWO','rank4 must remain'))
        reject('missing_subset',lambda:need(len(prepared['records'][:-1])==38760,'complete population'))
        reject('false_pair_multiplicity',lambda:need(max(len(r['groups']) for r in paircounts)>=6,'raw support bound'))
        write(out/'controls.json',dict(corruptions_rejected=rejected,reused_independent_preparation_controls_sha256=sha(I/'controls.json')))
        write(out/'marginal_bridge.json',dict(global_matrix=H,records=bridge))
        write(out/'independent_remaining.json',dict(groups=[r['groups'] for r in remaining],integer_null_bases=[r['certificate']['integer_null_basis'] for r in remaining],scope='Nine necessary subsets only; no factor realizability claim.'))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_SIX_GROUP_KERNELS.md']:pin(p)
        ts=datetime.now(timezone.utc).isoformat();write(out/'manifest.json',dict(timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,solver_calls=0))
        binding=dict(id='C-FIXED-HADAMARD-SIX-EXCEPTION-KERNEL-CENSUS',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='Among all38760 six-element subsets of the20fixed Hadamard support groups, the augmented incidence matrix has rank6 for35587, rank5 for3164, and rank4 for9. Any binary prescribed-Gram factor with exactly six unbalanced groups must use one of the nine saved rank4 subsets: every rank6 and rank5 subset is excluded by the checked integer marginal-kernel argument.',scope='Complete finite sextet census and necessary exact-six-exception reduction for one fixed support; the nine retained subsets remain unresolved.',assumptions=['Literal fixed six-prism Hadamard support and full prescribed integer Gram.','Exactly six triplicate-support groups have a nonzero coordinate/fibre deviation.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-TRIPLICATE-MARGINAL-RELAXATION',revision=1,relation='uses_result')],verifier='/root/structural_attack',producer='/root/state_literature_audit',method='Independent Gram determinants and Cramer kernel construction for every subset, then literal validation of all producer rank minors and primitive null/Bézout certificates; separate global-marginal and integer-count proof.',shared_components=['Same raw support and separately checked full-Gram marginal theorem; no producer code imports.','Python exact integers. The independent preparation uses fraction-free determinants while the producer chooses a Fraction row basis; saved minors additionally checked by bounded modular arithmetic.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},artifact_availability='LOCAL_ONLY',availability_reason='Review artifacts pending parent publication.',external_review=None,external_review_reason='No external peer review asserted.',limitations=['Nine kernel-dimension-two cases are retained, not excluded or constructed.','No outside-column-cap, balanced-UNSAT or exactly-five-exclusion premise is needed.','No whole-support/core/unrestricted-target exclusion or graph automorphism assumption.'],created_at=ts,updated_at=ts)
        write(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_HADAMARD_SIX_EXCEPTION_KERNEL_CENSUS_PASS',timestamp=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},subset_population=38760,rank_counts=dict(rankcounts),classification_counts=dict(classes),remaining_necessary_subsets=9,raw_pair_multiplicities={'0':6,'5':60},corruptions_rejected=len(rejected),solver_calls=0,target_resolution=False)
        write(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as e:write(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
