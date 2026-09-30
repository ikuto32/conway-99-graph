"""Independent human argument, exact marginal bridge and finite cube controls."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations,product
from math import gcd,lcm
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
RAW=B+'hadamard20_support/six_prism.json';CAND='docs/DERIVATION_20260930_FIVE_UNBALANCED_GROUPS_CANDIDATE.md'
PINS={CAND:'bb22bbfe9d500f69425f41bb03f264019b239460a6e8b0b2860d99e510ef5f61',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
I+'hadamard_few_exception_marginals/summary.json':'6b9512567a77ef3bad2fbb1b581fadb30c486c9ac4151543001705776e0c5df9',
I+'hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88'}
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def rref(M):
    A=[list(map(Fraction,row))for row in M];piv=[]
    for c in range(len(A[0])):
        r=next((r for r in range(len(piv),len(A))if A[r][c]),None)
        if r is None:continue
        i=len(piv);A[i],A[r]=A[r],A[i];q=A[i][c];A[i]=[x/q for x in A[i]]
        for r in range(len(A)):
            if r!=i:
                q=A[r][c];A[r]=[x-q*y for x,y in zip(A[r],A[i])]
        piv.append(c)
    return A,piv
def egcd(a,b):
    if b==0:return(abs(a),1 if a>=0 else -1,0)
    g,x,y=egcd(b,a%b);return g,y,x-(a//b)*y
def bezout(v):
    g=0;b=[0]*len(v)
    for i,x in enumerate(v):
        ng,u,w=egcd(g,x);b=[u*z for z in b];b[i]+=w;g=ng
    need(g==1 and sum(x*y for x,y in zip(b,v))==1,'primitive Bezout identity');return b
def primitive_kernel(M):
    A,piv=rref(M);n=len(M[0])
    if len(piv)==n:return len(piv),None,None
    need(len(piv)==n-1,'one-dimensional kernel control')
    free=next(c for c in range(n)if c not in piv);v=[Fraction(0)]*n;v[free]=1
    for r,p in enumerate(piv):v[p]=-A[r][free]
    den=lcm(*(x.denominator for x in v));ints=[int(x*den)for x in v];g=gcd(*ints);ints=[x//g for x in ints]
    if next(x for x in ints if x)<0:ints=[-x for x in ints]
    validate_kernel(M,ints);return len(piv),ints,bezout(ints)
def validate_kernel(M,v):
    need(gcd(*v)==1 and any(v),'primitive nonzero kernel vector')
    need(all(sum(a*b for a,b in zip(row,v))==0 for row in M),'literal kernel identity')
def augmented(points):return [[1]*len(points)]+[list(r)for r in zip(*points)]
def coefficient_triples(sigma):
    # Sum sigma=0 forces both signs. A nonzero integer coefficient is at most1
    # in magnitude under all delta>=-1 inequalities.
    return [list(t)for t in product([-1,0,1],repeat=3)if sum(t)==0 and all(x*s>=-1 for x in t for s in sigma)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};corrupt=[]
    def pin(p,h=None):v=sha(ROOT/p);need(h is None or h==v,'exact input '+p);pins[p]=v
    def load(p,h=None):pin(p,h);return json.loads((ROOT/p).read_bytes())
    def reject(label,fn):
        try:fn()
        except(ValueError,IndexError,TypeError):corrupt.append(label)
        else:raise ValueError('corruption accepted '+label)
    try:
        for p,h in PINS.items():pin(p,h)
        raw=load(RAW);L=raw['L'];K=raw['prescribed_Gram36'];C=raw['core_adjacency'];supports=[]
        for d in range(60):
            s=tuple(L[a][d]for a in range(12))
            if s not in supports:supports.append(s)
        need(len(supports)==20 and all(sum(s)==6 for s in supports),'twenty distinct binary supports')
        H=augmented(supports);need(all(sum(s[a]for s in supports)==10 for a in range(12)),'ten incident groups')
        need(K==[[12*int(i==j)+2-int(i//12==j//12)-C[i][j]-sum(C[i][q]*C[q][j]for q in range(36))for j in range(36)]for i in range(36)],'raw prescribed Gram identity')
        marg=load(I+'hadamard_few_exception_marginals/independent_marginal_certificates.json');bridge=[]
        for a in range(12):
            gs=[g for g,s in enumerate(supports)if s[a]];others=[b for b in range(12)if b not in[a,a^1]]
            M=[[1]*10]+[[supports[g][b]for g in gs]for b in others]
            need(M==marg['matrices'][a]['matrix'] and gs==marg['matrices'][a]['groups'],'exact per-coordinate premise')
            rows=[[H[r][g]for g in gs]for r in range(13)]
            need(rows[0]==rows[a+1]==[1]*10 and rows[(a^1)+1]==[0]*10,'self and absent mate rows')
            need([rows[b+1]for b in others]==M[1:] and all(sum(row)==5 for row in M[1:]),'all other global-H rows are existing marginals')
            need(all(K[12*f+a][12*f+a]==10 and all(sum(K[12*f+a][12*h+b]for h in range(3))==5 for b in others)for f in range(3)),'literal Gram-to-marginal RHS')
            bridge.append(dict(coordinate=a,incident_groups=gs,marginal_matrix=M,global_rows_by_marginal=[0]+[b+1 for b in others],self_row=a+1,zero_mate_row=(a^1)+1))
        # Positive/negative exact algebra controls precede the finite census.
        square=augmented([(0,0),(1,0),(0,1),(1,1)]);_,square_sigma,_=primitive_kernel(square)
        need(any(t!=[0,0,0]for t in coefficient_triples(square_sigma)),'four-group abstract control permits nonzero deviations')
        circuit=augmented([(0,0,0),(1,1,0),(1,0,1),(0,1,1),(1,1,1)])
        rr,sigma,bez=primitive_kernel(circuit);need(rr==4 and all(sigma)and max(map(abs,sigma))==2,'five-point affine circuit with magnitude2')
        need(coefficient_triples(sigma)==[[0,0,0]],'five nonzero circuit integer coefficient obstruction')
        fractional=[Fraction(1,2),Fraction(-1,2),Fraction(0)]
        need(sum(fractional)==0 and all(t*s>=-1 for t in fractional for s in sigma)and any((t*s).denominator>1 for t in fractional for s in sigma),'fractional control shows integrality is essential')
        nonprimitive=[2*x for x in square_sigma];need([Fraction(1,2)*x for x in nonprimitive]==square_sigma,'nonprimitive half-integral coefficient control')
        reject('nonprimitive_generator',lambda:validate_kernel(square,nonprimitive))
        wrong=sigma[:];wrong[0]+=1;reject('perturbed_kernel',lambda:validate_kernel(circuit,wrong))
        wrongb=bez[:];wrongb[0]+=1;reject('wrong_Bezout_certificate',lambda:need(sum(x*y for x,y in zip(wrongb,sigma))==1,'Bezout'))
        duplicates=augmented([(0,0),(1,0),(0,1),(1,1),(0,0)])
        need(len(rref(duplicates)[1])==3,'duplicate-point adversarial control')
        reject('duplicate_points_pass_rank_bound',lambda:need(len({tuple(p)for p in zip(*duplicates[1:])})==5,'distinctness premise'))
        need(len(rref(circuit[1:])[1])==3,'leading-row omission can lower rank')
        reject('omit_augmented_leading_row',lambda:need(circuit[1:][0]==[1]*5,'leading-one premise'))
        reject('absent_coordinate_nonzero_coefficient',lambda:need(sigma[0]*1==0,'absence forces t0'))
        reject('one_sided_sum_not_zero',lambda:need(sum([1,0,0])==0,'fibre conservation'))
        records=[];census={}
        for dim in[3,4]:
            cube=list(product([0,1],repeat=dim));counts=Counter();zero_kernel=full_kernel=0
            for ids in combinations(range(len(cube)),5):
                M=augmented([cube[i]for i in ids]);rank,v,b=primitive_kernel(M);need(rank>=4,'complete finite cube rank bound');counts[rank]+=1
                if v is not None:
                    need(sum(v)==0 and sum(x*y for x,y in zip(b,v))==1,'literal primitive lattice certificate')
                    if all(v):
                        full_kernel+=1;need(max(map(abs,v))>=2 and coefficient_triples(v)==[[0,0,0]],'all fullsupport five-circuit controls')
                    else:zero_kernel+=1
                records.append(dict(dimension=dim,points=list(ids),rank=rank,primitive_kernel=v,bezout=b))
            census[str(dim)]=dict(subsets=sum(counts.values()),rank_counts=dict(counts),full_support_kernel_lines=full_kernel,kernel_lines_with_zero=zero_kernel)
        need(census['3']['subsets']==56 and census['4']['subsets']==4368,'complete bounded control universes')
        save(out/'raw_marginal_bridge.json',dict(supports=supports,augmented_support_matrix=H,coordinates=bridge))
        save(out/'cube_five_point_controls.json',dict(census=census,records=records))
        save(out/'controls.json',dict(corruptions_rejected=corrupt,four_point=dict(matrix=square,sigma=square_sigma,allowed_coefficient_triples=coefficient_triples(square_sigma)),
            five_point=dict(matrix=circuit,sigma=sigma,bezout=bez,allowed_integer_triples=coefficient_triples(sigma),fractional_triple=[str(t)for t in fractional]),
            note='Cube controls are not research factor constructions or the universal rank proof.'))
        for p in ['acceleration/audit_20260930_five_unbalanced_groups.py','docs/AUDIT_20260930_FIVE_UNBALANCED_GROUPS.md','uv.lock','pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();claim=dict(id='C-FIXED-HADAMARD-EXACTLY-FIVE-UNBALANCED-GROUPS-EXCLUSION',revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            statement='No binary36x60factor on the exact frozen six-prism Hadamard coordinate support with the prescribed full integer Gram has exactly five unbalanced triplicate-support groups.',
            scope='Only the exactly-five-exception subfamily on one literal fixed support. The proof uses Gram marginals and integer counts, without outside-column caps or a balanced-family UNSAT premise.',
            assumptions=['BinaryF with the exact frozen coordinate support and prescribed integer Gram.','Unbalanced means at least one coordinate/fibre count in that group differs from one.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-TRIPLICATE-MARGINAL-RELAXATION',revision=1,relation='uses_result')],
            verifier='/root/eight_domain_audit',producer='/root',method='Independent human derivation of global marginal kernel, affine cube rank bound, primitive lattice and sign argument; exact raw bridge and4424finite cube controls.',
            inputs_sha256=pins,limitations=['No conclusion for exactly four or six or more exceptional groups.','No whole-support, core-wide or unrestricted target exclusion.','No unknown target automorphism or balance normalization.'],
            created_at=now,updated_at=now,artifact_availability='LOCAL_ONLY',external_review=False)
        save(out/'claim_binding.json',claim)
        result=dict(status='INDEPENDENT_EXACTLY_FIVE_UNBALANCED_GROUPS_EXCLUSION_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()if p.is_file()},raw_marginal_coordinates=12,global_matrix_shape=[13,20],cube_controls=census,corruptions=len(corrupt),
            shared_components=['Pinned raw artifacts and previously independently established Gram marginals; no producer/checker imports.','Python exact Fraction/integer arithmetic and standard library.'],target_resolution=False,solver_calls=0,proof_replays=0)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],sha256=sha(out/'summary.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(__file__)));raise
if __name__=='__main__':main()
