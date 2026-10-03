"""Independent literal matrices/congruences/inverses; no repository imports."""
import argparse
import copy
import hashlib
import itertools
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'
PROD = B + 'triplicate_count_psd/'
PINS = {
    PROD+'summary.json': '0f13893425d9185b9bfed342c5ba4b86fbcee6523c762972f126a7eb823771cf',
    B+'hadamard20_support/six_prism.json': 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    I+'hadamard20_support_v2/summary.json': 'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f',
    B+'srg243_residual_fixture/triangle_blocks.json': '3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
    I+'srg243_residual_fixture/summary.json': '28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',
    I+'count_master_sat_outcome/summary.json': '61e7eb9643902c866617a270d856a521f71f5b2723c0e731edae3896baba484d',
    I+'count_master_eight_orbit_cut_sat_outcome/summary.json': '7c80d3e4daef0f259bd354e6e6b28188b660edaaf17c7a20f9c54cfb3abc4c3c',
    I+'count_master_partial_cut_sat_outcome/summary.json': '736ccbcda81ee34c21ede2a80253d5b224fabb96a2e83d0a2c1c76dba435d071',
}
CASES = [('first', 'eight_count_profile_lift', 'count_master_sat_outcome'),
         ('second', 'eight_count_profile_lift_second', 'count_master_eight_orbit_cut_sat_outcome'),
         ('third', 'eight_count_profile_lift_third', 'count_master_partial_cut_sat_outcome')]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def key(path):
    return path.resolve().relative_to(ROOT).as_posix()

def read(path):
    return json.loads(path.read_bytes())

def save(path, data):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def pack(matrix):
    return [[[Q(x).numerator, Q(x).denominator] for x in row] for row in matrix]

def unpack(matrix):
    need(isinstance(matrix, list), 'rational matrix list')
    ans = []
    for row in matrix:
        out = []
        for x in row:
            need(isinstance(x, list) and len(x)==2 and all(type(v) is int for v in x) and x[1]>0, 'rational pair')
            out.append(Q(x[0], x[1]))
        ans.append(out)
    return ans

def tr(a):
    return [list(col) for col in zip(*a)]

def mm(a,b):
    cols = tr(b)
    need(a and b and all(len(row)==len(b) for row in a), 'product shape')
    return [[sum(u*v for u,v in zip(row,col)) for col in cols] for row in a]

def ident(n):
    return [[int(i==j) for j in range(n)] for i in range(n)]

def gram(a):
    return mm(a,tr(a))

def inverse(a):
    """Bottom available row pivot; no reliance on candidate transform history."""
    n=len(a)
    need(n and all(len(row)==n for row in a), 'inverse square')
    w=[[Q(x) for x in a[i]]+[Q(i==j) for j in range(n)] for i in range(n)]
    det=Q(1)
    for col in range(n):
        pivot=next((r for r in range(n-1,col-1,-1) if w[r][col]),None)
        need(pivot is not None, 'singular transform')
        if pivot!=col:
            w[pivot],w[col]=w[col],w[pivot]
            det=-det
        d=w[col][col]
        det*=d
        w[col]=[v/d for v in w[col]]
        for r in range(n):
            if r!=col and w[r][col]:
                t=w[r][col]
                w[r]=[x-t*y for x,y in zip(w[r],w[col])]
    inv=[row[n:] for row in w]
    need(mm(a,inv)==ident(n) and mm(inv,a)==ident(n), 'literal two-sided inverse')
    return inv,det

def rank_kernel(a):
    """Reverse column elimination, independently checking every returned null vector."""
    m=len(a); n=len(a[0]); w=[[Q(v) for v in row] for row in a]
    pivots=[]; k=0
    for col in range(n-1,-1,-1):
        pivot=next((r for r in range(m-1,k-1,-1) if w[r][col]),None)
        if pivot is None:
            continue
        w[k],w[pivot]=w[pivot],w[k]
        d=w[k][col]; w[k]=[v/d for v in w[k]]
        for r in range(m):
            if r!=k and w[r][col]:
                d=w[r][col]; w[r]=[x-d*y for x,y in zip(w[r],w[k])]
        pivots.append(col); k+=1
        if k==m: break
    free=[j for j in range(n) if j not in pivots]
    basis=[]
    for col in free:
        v=[Q(0)]*n; v[col]=Q(1)
        for r,p in enumerate(pivots): v[p]=-w[r][col]
        need(all(sum(x*y for x,y in zip(row,v))==0 for row in a),'literal nullspace')
        basis.append(v)
    return k,basis,pivots,w

def certificate_check(matrix, cert):
    n=len(matrix)
    need(all(len(row)==n for row in matrix) and matrix==tr(matrix), 'symmetric input')
    need(cert['status']=='EXACT_RATIONAL_PSD', 'PSD certificate status')
    t=unpack(cert['transform'])
    d=unpack([cert['diagonal']])[0]
    need(len(t)==n and all(len(row)==n for row in t) and len(d)==n,'certificate dimension')
    need(all(v>=0 for v in d),'nonnegative diagonal')
    need(cert['rank']==sum(v>0 for v in d),'saved diagonal rank')
    need(mm(tr(t),mm(matrix,t))==[[d[i] if i==j else 0 for j in range(n)] for i in range(n)],'literal congruence')
    inv,det=inverse(t)
    rank,kernel,pivots,rref=rank_kernel(matrix)
    need(rank==cert['rank'] and len(kernel)==n-rank,'independent rank agreement')
    return dict(rank=rank, nullity=n-rank, determinant=[det.numerator,det.denominator],
                inverse=pack(inv), nullspace=pack(kernel), reverse_pivots=pivots,
                reduced_matrix=pack(rref), full_congruence_entries=n*n,
                two_sided_inverse_entries=2*n*n, operations_list_used=False)

def fixed_core():
    return [[int((i//12==j//12 and (i%12)^1==j%12) or (i//12!=j//12 and i%12==j%12)) for j in range(36)] for i in range(36)]

def prescribed(c,n):
    size=3*n
    need(len(c)==size and all(len(row)==size for row in c),'core dimension')
    return [[n*int(i==j)+2-c[i][j]-sum(c[i][k]*c[j][k] for k in range(size))-int(i//n==j//n) for j in range(size)] for i in range(size)]

def group_order(raw):
    cols=raw['support_columns']; groups=[]
    need(len(cols)==60,'sixty columns')
    for support in cols:
        need(len(support)==6 and support==sorted(set(support)), 'support coordinates')
        if support not in groups: groups.append(support)
    need(len(groups)==20 and all(cols.count(s)==3 for s in groups),'twenty triplicate groups')
    need(raw['L']==[[int(a in s) for s in cols] for a in range(12)],'literal L support')
    return groups

def matrix_from_profile(raw,scope,profile):
    c=fixed_core(); g=prescribed(c,12); groups=group_order(raw)
    need(raw['core_adjacency']==c and scope['core_adjacency36']==c,'independent fixed core')
    need(raw['prescribed_Gram36']==g and scope['prescribed_Gram36']==g,'literal Gram')
    need(scope['groups']==groups,'first-occurrence group order')
    counts=profile['coordinate_group_fibre_counts']
    need(len(counts)==12 and all(len(row)==20 for row in counts),'count dimensions')
    for a in range(12):
        for j in range(20):
            vals=counts[a][j]
            need(len(vals)==3 and all(type(v)is int and 0<=v<=3 for v in vals),'literal integer counts')
            need(sum(vals)==3*int(a in groups[j]),'support coordinate quota')
    need(scope['coordinate_group_fibre_counts']==counts and scope['selected_profile_sha256']==profile['profile_sha256'],'scope raw counts')
    n=[[counts[a][j][f] for j in range(20)] for f in range(3) for a in range(12)]
    need(all(sum(row)==10 for row in n),'row margins')
    need(all(sum(n[12*f+a][j] for a in range(12))==6 for f in range(3) for j in range(20)),'group fibre quotas')
    m=[[3*g[i][j]-sum(n[i][k]*n[j][k] for k in range(20)) for j in range(36)] for i in range(36)]
    return dict(N=n,G=g,M=m,row_order='12*fibre+coordinate',profile_digest=profile['profile_sha256'])

def factor_identity(f):
    rows=len(f); width=len(f[0]); need(width%3==0,'triple factor width')
    n=[[sum(row[g:g+3]) for g in range(0,width,3)] for row in f]
    g=gram(f); m=[[3*g[i][j]-sum(n[i][k]*n[j][k] for k in range(width//3)) for j in range(rows)] for i in range(rows)]
    d=[[row[g+a]-row[g+b] for g in range(0,width,3) for a,b in ((0,1),(0,2),(1,2))] for row in f]
    need(gram(d)==m,'pair difference SOS identity')
    return n,m,d

def expect_reject(name,fn,records):
    try: fn()
    except (ValueError,ZeroDivisionError,KeyError,IndexError,TypeError) as ex:
        records.append(dict(name=name,rejected=True,reason=str(ex)));return
    raise ValueError('corruption accepted: '+name)

def controls(fixture):
    records=[]
    # Independent two-by-two determinant formula calibrates the rank path completely.
    for a,b,c,d in itertools.product(range(-2,3),repeat=4):
        m=[[a,b],[c,d]]; expected=2 if a*d-b*c else int(any((a,b,c,d)))
        need(rank_kernel(m)[0]==expected,'625 determinant rank controls')
    positives=[([[2,1],[1,2]],[[1,Q(-1,2)],[0,1]],[2,Q(3,2)]),
               ([[1,1],[1,1]],[[1,-1],[0,1]],[1,0]),
               ([[0,0],[0,0]],ident(2),[0,0])]
    for m,t,d in positives:
        cert=dict(status='EXACT_RATIONAL_PSD',rank=sum(x>0 for x in d),transform=pack(t),diagonal=pack([d])[0])
        records.append(dict(matrix=m,certificate=cert,check=certificate_check(m,cert)))
    rejections=[]
    for name,m,t,d in [('negative_diagonal',[[-1,0],[0,2]],ident(2),[-1,2]),
                         ('zero_diagonal_indefinite',[[0,1],[1,0]],[[1,1],[1,-1]],[2,-2]),
                         ('hidden_negative',[[1,2],[2,1]],[[1,-2],[0,1]],[1,-3]),
                         ('singular_transform_hides_negative',[[1,0],[0,-1]],[[1,0],[0,0]],[1,0])]:
        cert=dict(status='EXACT_RATIONAL_PSD',rank=sum(x>0 for x in d),transform=pack(t),diagonal=pack([d])[0])
        expect_reject(name,lambda m=m,cert=cert: certificate_check(m,cert),rejections)
    for bits in itertools.product((0,1),repeat=12):
        factor_identity([list(bits[:6]),list(bits[6:])])
    rational_records=[]
    for seed in range(64):
        f=[[Q(((seed+3*i+5*j)*(j+2)+i)%11-5,1+(seed+i+j)%3) for j in range(9)] for i in range(4)]
        n,m,d=factor_identity(f)
        rational_records.append(dict(factor=pack(f),N=pack(n),M=pack(m)))
    f=fixture['factor60x180']; c=fixture['cubic_core60']
    need(len(f)==60 and all(len(row)==180 and all(v in (0,1) for v in row) for row in f),'243 fixture shape')
    need(gram(f)==prescribed(c,20),'genuine243 own literal Gram')
    n,m,d=factor_identity(f)
    return dict(rank_controls=625,binary_partition_controls=4096,rational_partition_controls=rational_records,
                small_positive_certificates=records,indefinite_controls=rejections,
                genuine243=dict(N=n,M=m,pair_difference_factor=d,scope='Own Gram, generic consecutive triples; not research36 factor.'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();inputs={}
    def pin(path,expected=None):
        p=ROOT/path if isinstance(path,str) else path
        h=sha(p);need(expected is None or h==expected,'input hash '+key(p));inputs[key(p)]=h;return p
    try:
        for path,h in PINS.items():pin(path,h)
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'docs/AUDIT_20260930_TRIPLICATE_COUNT_PSD.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        producer=read(ROOT/(PROD+'summary.json'))
        for mapping in ('inputs_sha256','outputs_sha256'):
            for p,h in producer[mapping].items():pin(p,h)
        save(out/'manifest.json',dict(inputs_sha256=inputs,command=[sys.executable,*sys.argv],cwd=str(ROOT),created_at=datetime.now(timezone.utc).isoformat(),allocation_seconds=120,no_producer_imports=True))
        raw=read(ROOT/(B+'hadamard20_support/six_prism.json'))
        support_gate=read(ROOT/(I+'hadamard20_support_v2/summary.json'))
        need(support_gate['inputs_sha256'][B+'hadamard20_support/six_prism.json']==inputs[B+'hadamard20_support/six_prism.json'],'support gate raw binding')
        control=controls(read(ROOT/(B+'srg243_residual_fixture/triangle_blocks.json')))
        results=[]; corruptions=[]
        for name,directory,auditdir in CASES:
            scope=read(ROOT/(B+directory+'/scope.json'));profile=read(ROOT/(B+directory+'/selected_profile.json'))
            independent=pin(scope['source_count_profile_path'],scope['source_count_profile_sha256'])
            need(read(independent)==profile,'independently decoded profile equality')
            gate=read(ROOT/(I+auditdir+'/summary.json'))
            gates={**gate.get('inputs_sha256',{}),**gate.get('outputs_sha256',{})}
            need(gates.get(key(independent))==sha(independent),'independent outcome profile binding')
            expected=matrix_from_profile(raw,scope,profile)
            saved=read(ROOT/(PROD+name+'/matrix.json'));need(saved==expected,'all raw matrix fields '+name)
            cert=read(ROOT/(PROD+name+'/certificate.json'))
            checked=certificate_check(expected['M'],cert)
            need(checked['rank']==22 and checked['nullity']==14,'literal three rank22 results')
            record=dict(profile=name,source_profile_sha256=sha(independent),matrix=expected,certificate_check=checked)
            save(out/(name+'_exact_check.json'),record)
            results.append(dict(profile=name,profile_digest=profile['profile_sha256'],rank=22,nullity=14,determinant=checked['determinant'],status='NECESSARY_PSD_TEST_PASS'))
            # In-memory mutations only; raw artifacts never altered.
            bad=copy.deepcopy(cert);bad['transform'][0][0][0]+=1
            expect_reject(name+'_transform_entry',lambda bad=bad:certificate_check(expected['M'],bad),corruptions)
            bad=copy.deepcopy(cert);bad['diagonal'][0][0]+=1
            expect_reject(name+'_diagonal_entry',lambda bad=bad:certificate_check(expected['M'],bad),corruptions)
            bad=copy.deepcopy(cert);bad['rank']-=1
            expect_reject(name+'_rank',lambda bad=bad:certificate_check(expected['M'],bad),corruptions)
            bad=copy.deepcopy(cert);bad['transform'][0][0][1]=0
            expect_reject(name+'_zero_denominator',lambda bad=bad:certificate_check(expected['M'],bad),corruptions)
            bad=copy.deepcopy(expected['M']);bad[0][0]+=1
            expect_reject(name+'_matrix',lambda bad=bad:certificate_check(bad,cert),corruptions)
            bad=copy.deepcopy(profile);bad['coordinate_group_fibre_counts'][0][0][0]+=1
            expect_reject(name+'_count',lambda bad=bad:matrix_from_profile(raw,scope,bad),corruptions)
            need(time.perf_counter()-start<120,'cooperative time bound')
        bad=copy.deepcopy(raw);bad['core_adjacency'][0][1]=0
        expect_reject('core_mutation',lambda:matrix_from_profile(bad,scope,profile),corruptions)
        bad=copy.deepcopy(raw);bad['prescribed_Gram36'][0][0]+=1
        expect_reject('Gram_mutation',lambda:matrix_from_profile(bad,scope,profile),corruptions)
        bad=copy.deepcopy(raw);bad['support_columns'][0][0]=1
        expect_reject('support_mutation',lambda:matrix_from_profile(bad,scope,profile),corruptions)
        expect_reject('summary_identity',lambda:pin(PROD+'summary.json','0'*64),corruptions)
        control['research_corruptions']=corruptions;save(out/'controls.json',control)
        status='INDEPENDENT_TRIPLICATE_COUNT_PSD_PASS'
        summary=dict(status=status,created_at=datetime.now(timezone.utc).isoformat(),verifier='/root/state_literature_audit',
                     source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                     command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,
                     outputs_sha256={key(p):sha(p) for p in sorted(out.iterdir()) if p.is_file()},results=results,
                     literal_research_matrices=3,matrix_entries_rebuilt=3*(36*20+2*36*36),
                     congruence_entries_checked=3*36*36,inverse_product_entries_checked=6*36*36,
                     controls=dict(rank=625,binary_partition=4096,rational_partition=64,genuine243=True,
                                   indefinite_rejections=len(control['indefinite_controls']),research_corruptions=len(corruptions)),
                     producer_imports=False,shared_components=['Python standard library exact integers and fractions; authenticated raw support, count profiles and saved certificate candidates.'],
                     artifact_availability='LOCAL_ONLY',elapsed_seconds=time.perf_counter()-start,
                     scope='Three exact count profiles pass the necessary real triplicate Gram PSD test at rank22. No factor feasibility, target exclusion, novelty or universal sufficiency claim.')
        save(out/'summary.json',summary)
        deps=[dict(id=x,revision=1,relation='uses_result') for x in ['C-FIXED-HADAMARD-AT-LEAST-SEVEN-COUNT-CSP-WITNESS','C-FIXED-HADAMARD-SIX-CUT-COUNT-CSP-WITNESS','C-FIXED-HADAMARD-PARTIAL-CUT-COUNT-CSP-WITNESS','C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS']]
        binding=dict(id='C-FIXED-HADAMARD-THREE-COUNT-PROFILES-PSD-NECESSITY-PASS',revision=1,kind='mathematical',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
                     statement='For the first, second and third pinned count-CSP profiles on the literal six-prism Hadamard support, each independently reconstructed matrix 3G-NN^T is positive semidefinite of exact rational rank22 (nullity14). This is a necessary real Gram-factor test because 3FF^T-NN^T is the sum of the within-triplicate pair-difference outer products.',
                     scope=summary['scope'],dependencies=deps,profile_digests=[r['profile_digest'] for r in results],
                     independent_verification=dict(report=key(out/'summary.json'),sha256=sha(out/'summary.json'),status=status,verifier='/root/state_literature_audit',method='Independent literal matrix reconstruction, rational congruence plus two-sided inverse and determinant, separate reverse-column rank/nullspace, exact positive and adversarial controls.'),
                     shared_components=summary['shared_components'],inputs_sha256=inputs,artifact_availability='LOCAL_ONLY',
                     limitations=['The three PSD passes do not give real or binary Gram factors with these counts.','No cross-column or residual-D completion, target existence/exclusion, or claim of novelty.','Producer shear lists are not a premise for invertibility. Generic factor positives use their own Grams, including SRG243.'],
                     controls=summary['controls'])
        save(out/'claim_binding.json',binding)
        print(json.dumps(dict(status=status,summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'),elapsed_seconds=time.perf_counter()-start)),flush=True)
    except BaseException as ex:
        save(out/'failure.json',dict(error=repr(ex),inputs_sha256=inputs,elapsed_seconds=time.perf_counter()-start))
        raise

if __name__=='__main__':main()
