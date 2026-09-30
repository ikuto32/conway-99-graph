"""Independent exact rank/nullspace certificate and septet classification audit."""
import argparse, copy, gzip, hashlib, json, math, platform, subprocess, sys, time
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations, permutations, product
from pathlib import Path
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_seven_exception_census'
M=B/'20260930_independent_review/hadamard_few_exception_marginals'
RAW=B/'20260930_hadamard20_support/six_prism.json'
PINS={D/'summary.json':'d1eaefc7ddab2199964b909e222107aaefa3e6914d1c8a23c919419ca8fcf1bb',M/'summary.json':'6b9512567a77ef3bad2fbb1b581fadb30c486c9ac4151543001705776e0c5df9',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'}
CID='C-FIXED-HADAMARD-SEVEN-EXCEPTION-KERNEL-CENSUS'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,obj):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(obj,f,indent=2);f.write('\n')

def determinant_mod(matrix,p):
    a=[[x%p for x in row] for row in matrix];d=1
    for j in range(len(a)):
        pivot=next((i for i in range(j,len(a)) if a[i][j]),None)
        if pivot is None:return 0
        if pivot!=j:a[j],a[pivot]=a[pivot],a[j];d=-d
        x=a[j][j];d=d*x%p;inv=pow(x,-1,p)
        for i in range(j+1,len(a)):
            scale=a[i][j]*inv%p
            if scale:
                for k in range(j,len(a)):a[i][k]=(a[i][k]-scale*a[j][k])%p
    return d%p

def validate_certificate(matrix,cert):
    m=len(matrix);n=len(matrix[0]);rank=cert['rank']
    need(type(rank) is int and 0<=rank<=min(m,n),'rank range')
    rows=cert['minor_rows'];cols=cert['minor_columns'];free=cert['free_columns']
    need(len(rows)==len(cols)==rank and len(set(rows))==len(set(cols))==rank,'minor independent index sets')
    need(all(type(i) is int and 0<=i<m for i in rows) and all(type(i) is int and 0<=i<n for i in cols),'minor indices valid')
    need(free==[i for i in range(n) if i not in cols],'complete free column partition')
    a=[[matrix[i][j] for j in cols] for i in rows]
    need(a==cert['minor'] and all(x in [0,1] for row in a for x in row),'literal binary minor')
    bound=math.factorial(rank);p=1000003 if 2*bound<1000003 else 2305843009213693951
    need(2*bound<p,'Leibniz uniqueness bound below modulus')
    d=cert['determinant'];need(type(d) is int and 0<abs(d)<=bound,'bounded nonzero determinant')
    need(d%p==determinant_mod(a,p),'exact determinant established by residue and bound')
    basis=cert['integer_null_basis'];need(len(basis)==n-rank,'complete null dimension')
    for v in basis:
        need(len(v)==n and all(type(x) is int for x in v) and math.gcd(*v)==1,'primitive integer null vector')
        need(all(sum(x*y for x,y in zip(row,v))==0 for row in matrix),'literal null equations')
    if free:need(determinant_mod([[v[i] for i in free] for v in basis],1000003)!=0,'whole null basis independent over rationals')
    return rank,basis

def classify(rank,basis):
    if rank==7:return 'EXCLUDED_FULL_COLUMN_RANK',list(range(7))
    forced=[i for i in range(7) if all(v[i]==0 for v in basis)]
    if forced:return 'EXCLUDED_FORCED_BALANCED_GROUP',forced
    if rank==6:
        c=basis[0];need(sum(c)==0 and all(c) and max(map(abs,c))>=2,'odd full-support primitive line premise')
        return 'EXCLUDED_ONE_DIMENSIONAL_ODD_KERNEL',[]
    return 'RETAINED_HIGHER_DIMENSION_KERNEL',[]

def validate_record(rec,index,ids,H):
    need(rec['index']==index and rec['groups']==list(ids),'complete exact lexicographic population')
    matrix=[[row[g] for g in ids] for row in H];rank,basis=validate_certificate(matrix,rec['certificate'])
    category,forced=classify(rank,basis)
    need(rec['classification']==category and rec['forced_balanced_local_positions']==forced,'whole-nullspace conditional classification')
    if rank==6:
        b=rec['primitive_Bezout'];need(len(b)==7 and all(type(x) is int for x in b) and sum(x*y for x,y in zip(b,basis[0]))==1,'integer multiplier Bezout identity')
    return rank,category,forced

def determinant_expansion(a):
    value=0
    for q in permutations(range(len(a))):
        sign=(-1)**sum(q[i]>q[j] for i in range(len(q)) for j in range(i+1,len(q)))
        value+=sign*math.prod(a[i][q[i]] for i in range(len(a)))
    return value

def calibrate(saved):
    checked=0
    for bits in product(range(2),repeat=9):
        a=[list(bits[3*i:3*i+3]) for i in range(3)];rank=0
        for size in [1,2,3]:
            for rows in combinations(range(3),size):
                for cols in combinations(range(3),size):
                    minor=[[a[i][j] for j in cols] for i in rows];d=determinant_expansion(minor)
                    need(d%1000003==determinant_mod(minor,1000003),'independent tiny determinant calibration')
                    if d:rank=max(rank,size)
        # Nonzero modular minors and direct permutation minors give the same rank.
        modular=max([0]+[size for size in [1,2,3] if any(determinant_mod([[a[i][j] for j in cs] for i in rs],1000003) for rs in combinations(range(3),size) for cs in combinations(range(3),size))])
        need(rank==modular,'all512 exact tiny ranks');checked+=1
    oddcols=[(0,)*5,*[tuple(int(i==j) for i in range(5)) for j in range(5)],(1,)*5]
    odd=[[1]*7]+[[v[j] for v in oddcols] for j in range(5)]
    rank,basis=validate_certificate(odd,saved['odd_kernel']);need(classify(rank,basis)[0]=='EXCLUDED_ONE_DIMENSIONAL_ODD_KERNEL','synthetic odd primitive line')
    need(sum(x*y for x,y in zip(basis[0],saved['odd_Bezout']))==1,'synthetic primitive lattice certificate')
    cube=list(product(range(2),repeat=3))[:7];a=[[1]*7]+[[v[j] for v in cube] for j in range(3)]
    rank,basis=validate_certificate(a,saved['retained']);need(rank==4 and classify(rank,basis)==('RETAINED_HIGHER_DIMENSION_KERNEL',[]),'higher-dimensional positive retention')
    need(any(v[i]==0 for v in basis for i in range(7)),'one basis-vector zero is not a forced-zero coordinate')
    forced=[[1]*7]+[[int(j in (i,(i+1)%6)) if j<6 else 0 for j in range(7)] for i in range(6)]
    rank,basis=validate_certificate(forced,saved['forced_balanced']);need(classify(rank,basis)==('EXCLUDED_FORCED_BALANCED_GROUP',[6]),'complete forced-zero control')
    identity=[[int(i==j) for j in range(7)] for i in range(7)]
    cert=dict(rank=7,minor_rows=list(range(7)),minor_columns=list(range(7)),free_columns=[],minor=identity,determinant=1,integer_null_basis=[])
    rank,basis=validate_certificate(identity,cert);need(classify(rank,basis)==('EXCLUDED_FULL_COLUMN_RANK',list(range(7))),'handwritten full-rank positive')
    for c in [-4,-3,-2,2,3,4]:
        good=[v for v in product(range(-8,9),repeat=3) if sum(v)==0 and all(c*x>=-1 for x in v)]
        need(good==[(0,0,0)],'integer one-sided fibre-sum calibration')
    need(all(sum(v)!=0 for v in product([-1,1],repeat=7)),'odd seven signs cannot sum zero')
    need(all(-1<=c*t<=2 for c in [-1,1] for t in [-1,0,1]),'even sign-line nonzero positive prevents overextension')
    return dict(binary_3x3_matrices=checked,odd_sign_vectors=128,integer_coefficient_controls=6,scalar_triples_per_coefficient=4913,synthetic_full_rank=True,synthetic_odd_line=True,synthetic_forced_zero=True,synthetic_higher_dimension_retained=True,even_sign_line_not_excluded=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,expected=None):
        h=sha(p);need(expected is None or h==expected,'hash '+key(p));pins[key(p)]=h;return h
    try:
        for p,h in PINS.items():pin(p,h)
        summary=read(D/'summary.json');marginal=read(M/'summary.json')
        need(summary['status']=='CANDIDATE_COMPLETE_SEVEN_EXCEPTION_CENSUS' and summary['completed']==summary['population']==77520,'full final population, not partial prefix')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        need(marginal['status']=='INDEPENDENT_HADAMARD_FEW_EXCEPTION_MARGINALS_PASS','independent universal marginal premise')
        mp=M/'independent_marginal_certificates.json';pin(mp,marginal['outputs_sha256'][key(mp)]);matrices=read(mp)['matrices']
        raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][j]) for j in range(60)))
        need(len(groups)==20 and math.comb(20,7)==77520,'complete septet denominator')
        H=[[1]*20]+[[int(a in g) for g in groups] for a in range(12)]
        global_saved=read(D/'global_marginal_matrix.json');need(global_saved['groups']==[list(g) for g in groups] and global_saved['matrix']==H,'raw global incidence matrix')
        validate_certificate(H,global_saved['global_certificate']);bridge=[]
        for a in range(12):
            gs=[g for g,s in enumerate(groups) if a in s];other=[b for b in range(12) if b not in [a,a^1]]
            expected=[[1]*10]+[[int(b in groups[g]) for g in gs] for b in other]
            need(matrices[a]['groups']==gs and matrices[a]['matrix']==expected,'previous full-Gram marginal matrix literal identity')
            need([H[a+1][g] for g in gs]==[1]*10 and [H[(a^1)+1][g] for g in gs]==[0]*10,'global H bridge self/mate rows')
            bridge.append(dict(coordinate=a,incident_groups=gs,rows=[0]+[b+1 for b in other],duplicate_row=a+1,zero_row=(a^1)+1))
        controls=calibrate(read(D/'controls.json'))
        final=read(D/'checkpoint_77520.json');need(final['completed']==final['population']==77520 and final['inputs_sha256']==summary['inputs_sha256'],'final exact checkpoint')
        chunks=final['chunks'];need(len(chunks)==39,'all39 immutable chunks')
        expected_ids=iter(combinations(range(20),7));rankcounts=Counter();classcounts=Counter();crosscounts=Counter();remaining=[];completed=0;templates={};chunk_checks=[]
        for ci,chunk in enumerate(tqdm(chunks,desc='Independent septet certificates',mininterval=1)):
            need(chunk['first_index']==completed and chunk['count']==min(2000,77520-completed),'exact nonoverlapping chunk interval')
            path=ROOT/chunk['path'];pin(path,chunk['sha256']);n=0;chunkrank=Counter();chunkclass=Counter()
            with gzip.open(path,'rt',encoding='utf8') as stream:
                for line in stream:
                    rec=json.loads(line);ids=next(expected_ids);rank,category,forced=validate_record(rec,completed,ids,H)
                    rankcounts[rank]+=1;classcounts[category]+=1;crosscounts[rank,category]+=1;chunkrank[rank]+=1;chunkclass[category]+=1;templates.setdefault(category,(rec,ids))
                    if category.startswith('RETAINED'):remaining.append(rec)
                    completed+=1;n+=1
            need(n==chunk['count'],'exact chunk record population')
            checkpoint=read(D/f'checkpoint_{completed:05d}.json')
            need(checkpoint['status']=='SEVEN_GROUP_EXACT_CENSUS_PREFIX' and checkpoint['completed']==completed and checkpoint['population']==77520 and checkpoint['chunks']==chunks[:ci+1] and checkpoint['inputs_sha256']==summary['inputs_sha256'],'immutable contiguous checkpoint history')
            chunk_checks.append(dict(first=chunk['first_index'],count=n,rank_counts=dict(chunkrank),class_counts=dict(chunkclass)))
        need(next(expected_ids,None) is None and completed==77520,'every septet checked exactly once')
        need(rankcounts=={5:326,6:20930,7:56264},'complete exact rank populations')
        need(classcounts=={'EXCLUDED_FULL_COLUMN_RANK':56264,'EXCLUDED_FORCED_BALANCED_GROUP':18412,'EXCLUDED_ONE_DIMENSIONAL_ODD_KERNEL':2644,'RETAINED_HIGHER_DIMENSION_KERNEL':200},'proof-supported categories')
        need(summary['rank_counts']=={str(k):v for k,v in rankcounts.items()} and summary['class_counts']==dict(classcounts),'producer aggregate equality')
        rem=read(D/'remaining_candidates.json');need(rem['records']==remaining and rem['count']==summary['remaining_necessary_subsets']==200 and all(r['certificate']['rank']==5 for r in remaining),'all200 kernel-two cases retained, none declared feasible')
        need(summary['native_solver_calls']==0 and summary['independent_approval'] is False,'preserved candidate producer status')
        rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,IndexError,TypeError):rejected.append(label)
            else:raise ValueError('corruption accepted '+label)
        rec,ids=templates['EXCLUDED_FULL_COLUMN_RANK'];matrix=[[row[g] for g in ids] for row in H]
        bad=copy.deepcopy(rec['certificate']);bad['determinant']+=1;reject('wrong_determinant',lambda:validate_certificate(matrix,bad))
        bad=copy.deepcopy(rec['certificate']);bad['minor'][0][0]^=1;reject('wrong_raw_minor',lambda:validate_certificate(matrix,bad))
        bad=copy.deepcopy(rec);bad['groups'][0]=99;reject('wrong_subset',lambda:validate_record(bad,rec['index'],ids,H))
        bad=copy.deepcopy(rec);bad['classification']='RETAINED_HIGHER_DIMENSION_KERNEL';reject('full_rank_retained',lambda:validate_record(bad,rec['index'],ids,H))
        rec,ids=templates['EXCLUDED_ONE_DIMENSIONAL_ODD_KERNEL'];matrix=[[row[g] for g in ids] for row in H]
        bad=copy.deepcopy(rec['certificate']);bad['integer_null_basis'][0][0]+=1;reject('wrong_null_vector',lambda:validate_certificate(matrix,bad))
        bad=copy.deepcopy(rec['certificate']);bad['integer_null_basis'][0]=[2*x for x in bad['integer_null_basis'][0]];reject('nonprimitive_generator',lambda:validate_certificate(matrix,bad))
        bad=copy.deepcopy(rec);j=next(i for i,x in enumerate(rec['certificate']['integer_null_basis'][0]) if x);bad['primitive_Bezout'][j]+=1;reject('wrong_lattice_certificate',lambda:validate_record(bad,rec['index'],ids,H))
        rec,ids=templates['RETAINED_HIGHER_DIMENSION_KERNEL'];matrix=[[row[g] for g in ids] for row in H]
        bad=copy.deepcopy(rec['certificate']);bad['integer_null_basis'][1]=bad['integer_null_basis'][0][:];reject('dependent_null_basis',lambda:validate_certificate(matrix,bad))
        bad=copy.deepcopy(rec['certificate']);bad['integer_null_basis'].pop();reject('incomplete_null_basis',lambda:validate_certificate(matrix,bad))
        bad=copy.deepcopy(rec);bad['classification']='EXCLUDED_ONE_DIMENSIONAL_ODD_KERNEL';reject('discard_kernel_dimension_two',lambda:validate_record(bad,rec['index'],ids,H))
        rec,ids=templates['EXCLUDED_FORCED_BALANCED_GROUP'];bad=copy.deepcopy(rec);bad['forced_balanced_local_positions']=[];reject('missing_forced_zero',lambda:validate_record(bad,rec['index'],ids,H))
        reject('missing_final_chunk',lambda:need(sum(c['count'] for c in chunks[:-1])==77520,'complete coverage'))
        save(out/'controls.json',dict(**controls,corruptions_rejected=rejected))
        save(out/'marginal_bridge.json',dict(global_matrix=H,coordinate_records=bridge))
        save(out/'checked_chunks.json',dict(records=chunk_checks,population=77520,rank_by_class=[dict(rank=r,classification=c,count=n) for (r,c),n in sorted(crosscounts.items())]))
        save(out/'independent_remaining.json',dict(records=[dict(groups=r['groups'],rank=5,integer_null_basis=r['certificate']['integer_null_basis']) for r in remaining],count=200,scope='Necessary subsets only; no actual marginal profile or factor asserted.'))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_SEVEN_GROUP_KERNELS.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat()
        binding=dict(id=CID,revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For all77520 seven-element subsets of the20literal fixed six-prism Hadamard support groups, the augmented support-incidence matrix has rank7 for56264, rank6 for20930, and rank5 for326. Any prescribed-Gram factor with exactly seven unbalanced groups must use one of the200 saved rank5 subsets with no coordinate forced zero throughout the nullspace. All other subsets are excluded by full rank, a forced-balanced nominated group, or the primitive odd one-dimensional integer-kernel obstruction.',scope='Complete septet census and necessary exactly-seven-exception reduction on this one fixed support. The200 retained subsets are not asserted marginally feasible or realizable.',assumptions=['The literal fixed support and full prescribed integer Gram.','Exactly seven triplicate-support groups have a nonzero coordinate/fibre count deviation.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-TRIPLICATE-MARGINAL-RELAXATION',revision=1,relation='uses_result')],verifier='/root/structural_attack',producer='/root',method='Every raw minor checked by modular arithmetic with exact determinant bounds; every complete integer null basis and Bezout identity checked literally; full lexicographic chunk/checkpoint coverage and independent universal marginal argument.',shared_components=['Same raw support and separately checked full-Gram marginal equations.','Python integer arithmetic and standard modules plus tqdm; no producer rank/certificate/classification helper imports.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},artifact_availability='LOCAL_ONLY',availability_reason='Review artifacts awaiting parent publication.',external_review=None,external_review_reason='No external review asserted.',limitations=['Outside-column caps are not premises.','Higher-dimensional subsets without a forced zero are retained.','No factor, whole-support/core exclusion or unrestricted target resolution.','No assumed automorphism of a hypothetical graph.'],created_at=now,updated_at=now)
        save(out/'claim_binding.json',binding)
        save(out/'summary.json',dict(status='INDEPENDENT_HADAMARD_SEVEN_EXCEPTION_KERNEL_CENSUS_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},claim_id=CID,claim_revision=1,subset_population=77520,completed_chunks=39,rank_counts=dict(rankcounts),class_counts=dict(classcounts),remaining_necessary_subsets=200,remaining_kernel_dimension=2,corruptions_rejected=len(rejected),solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start))
        print(json.dumps(dict(status='INDEPENDENT_HADAMARD_SEVEN_EXCEPTION_KERNEL_CENSUS_PASS',sha256=sha(out/'summary.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(Path(__file__))));raise

if __name__=='__main__':main()
