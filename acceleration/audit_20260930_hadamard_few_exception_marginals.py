"""Independent full-Gram marginal implication and exact small-column minors."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
RAW=B+'hadamard20_support/six_prism.json';PROD=B+'hadamard_exception_groups/'
UNSAT=I+'hadamard_balanced_gram_unsat_v2/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    PROD+'summary.json':'59bb3232eabf096c29234dda732bab0230a01806c72116d71fd0adc232515a01',
    PROD+'few_exception_marginal_certificates.json':'39acf3674e30c1502e160fa4b0c0e4f23c30de60abbab649490ecaff8a2661b4',
    'acceleration/theory_20260930_hadamard_exception_groups.py':'1d74f819ec3a6039984cb58f170e5438a0f23385b71c9f1098c2f76648015a87',
    'acceleration/theory_20260930_hadamard_exception_groups_spec.md':'28d5484d3b5732740c29516b3ccff16d73defc35e1b6ac2bcf380d842e96e0a2',
    UNSAT:'edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5',
    I+'hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',
    I+'hadamard_two_group_margin_cancellation/summary.json':'9c16ea1e303fb9ef5832dd03512e487f8d6c7a285f2ef51f85cedabe1d81749f'}

def need(ok,message):
    if not ok:raise ValueError(message)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,value):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
def determinant(M):
    n=len(M);need(n in[1,2,3] and all(len(r)==n for r in M),'small exact square')
    # Leibniz formula: independent of producer fraction-free elimination.
    total=0
    for order in permutations(range(n)):
        sign=(-1)**sum(order[i]>order[j] for i in range(n) for j in range(i+1,n))
        term=sign
        for i,j in enumerate(order):term*=M[i][j]
        total+=term
    return total
def rank(M):
    rows=[list(map(Fraction,r)) for r in M];r=0
    for c in reversed(range(len(rows[0]))):
        p=next((j for j in reversed(range(r,len(rows))) if rows[j][c]),None)
        if p is None:continue
        rows[r],rows[p]=rows[p],rows[r];s=rows[r][c];rows[r]=[x/s for x in rows[r]]
        for j in range(len(rows)):
            if j!=r:
                s=rows[j][c];rows[j]=[x-s*y for x,y in zip(rows[j],rows[r])]
        r+=1
    return r
def matrix_from_supports(a,supports):
    groups=[g for g,s in enumerate(supports) if a in s]
    others=[b for b in range(12) if b not in[a,a^1]]
    M=[[1]*len(groups)]+[[int(b in supports[g]) for g in groups] for b in others]
    need(len(groups)==10 and len(others)==10,'literal marginal dimensions')
    return groups,others,M
def all_small_minors(M):
    records=[]
    for k in[1,2,3]:
        for cols in combinations(range(len(M[0])),k):
            chosen=None
            for rows in combinations(range(len(M)),k):
                minor=[[M[r][c] for c in cols] for r in rows];value=determinant(minor)
                if value:chosen=dict(columns=list(cols),rows=list(rows),minor=minor,determinant=value);break
            need(chosen is not None,'every subset of at most3columns independent')
            records.append(chosen)
    return records
def check_saved(M,records):
    expected=[list(c) for k in[1,2,3] for c in combinations(range(10),k)]
    need([r['columns'] for r in records]==expected,'complete175column-subset coverage')
    for rec in records:
        cols,rows=rec['columns'],rec['rows'];k=len(cols)
        need(len(rows)==k and sorted(set(rows))==rows and all(0<=r<11 for r in rows),'valid minor row selection')
        minor=[[M[r][c] for c in cols] for r in rows]
        need(rec['minor']==minor and rec['determinant']==determinant(minor)!=0,'literal independent determinant replay')
def gram(F):return [[sum(x*y for x,y in zip(a,b)) for b in F] for a in F]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};corrupt=[]
    def pin(p,expected=None):
        value=sha(ROOT/p);need(expected is None or value==expected,'exact input '+p);pins[p]=value
    def load(p,expected=None):pin(p,expected);return json.loads((ROOT/p).read_bytes())
    def reject(label,action):
        try:action()
        except(ValueError,KeyError,TypeError,IndexError):corrupt.append(label)
        else:raise ValueError('corruption accepted '+label)
    try:
        for p,h in PINS.items():pin(p,h)
        raw=load(RAW);L=raw['L'];C=raw['core_adjacency'];K=raw['prescribed_Gram36'];supports=[];group_columns=[]
        for d in range(60):
            s=[a for a in range(12) if L[a][d]]
            if s not in supports:supports.append(s);group_columns.append([])
            group_columns[supports.index(s)].append(d)
        need(len(supports)==20 and all(len(s)==6 for s in supports) and all(len(ds)==3 for ds in group_columns),'fixed raw triplicate supports')
        need(all(sum(a in s for a in [2*p,2*p+1])==1 for s in supports for p in range(6)),'support matching transversals')
        expectedK=[[12*int(i==j)+2-int(i//12==j//12)-C[i][j]-sum(C[i][q]*C[q][j] for q in range(36)) for j in range(36)] for i in range(36)]
        need(K==expectedK and all(K[i][i]==10 for i in range(36)),'raw literal prescribed Gram and diagonal')
        # The column quotas required by the balanced encoding follow from Gram.
        fibre_quadratics=[sum(K[12*f+a][12*f+b] for a in range(12) for b in range(12)) for f in range(3)]
        need(fibre_quadratics==[240]*3,'sum of squared fibre-column counts is240')
        saved=load(PROD+'few_exception_marginal_certificates.json');need(len(saved['matrices'])==12 and saved['nonzero_minors']==2100,'producer scope counts')
        matrices=[];total=0
        for a,item in enumerate(saved['matrices']):
            groups,others,M=matrix_from_supports(a,supports)
            need(item['coordinate']==a and item['groups']==groups and item['other_coordinates']==others and item['matrix']==M,'all raw marginal entries')
            need(all(row.count(1)==5 for row in M[1:]) and len({tuple(M[r][c] for r in range(11)) for c in range(10)})==10,'constant RHS and distinct binary columns')
            for f in range(3):
                need([sum(K[12*f+a][12*h+b] for h in range(3)) for b in others]==[5]*10,'fullGram summed-coordinate RHS')
            check_saved(M,item['certificates'])
            independent_minors=all_small_minors(M)
            exactrank=rank(M);need(exactrank==6,'separate exact marginal rank')
            matrices.append(dict(coordinate=a,groups=groups,other_coordinates=others,matrix=M,rank=exactrank,independent_minors=independent_minors))
            total+=len(independent_minors)
        need(total==2100,'all120single+540pair+1440triple subsets')
        # A genuine binary margin control verifies the full double-counting identity,
        # while its nonzero residual records why margins alone do not imply Gram.
        control=load(I+'hadamard_two_group_margin_cancellation/two_exception_positive.json')
        F=control['factor'];actualG=gram(F);nonzero=[]
        need(all(sum(F[12*f+a][d] for f in range(3))==L[a][d] for a in range(12) for d in range(60)), 'raw control exact coordinate support')
        need(all(sum(sum(F[12*f+a][d] for d in group_columns[g])-1 for f in range(3))==0 for g,s in enumerate(supports) for a in s), 'coordinate fibre deviations sum zero')
        need(all(sum(sum(F[12*f+a][d] for d in group_columns[g])-1 for a in s)==0 for g,s in enumerate(supports) for f in range(3)), 'group fibre deviations sum zero on quota control')
        for a,record in enumerate(matrices):
            for f in range(3):
                delta=[sum(F[12*f+a][d] for d in group_columns[g])-1 for g in record['groups']]
                residual=[sum(v*x for v,x in zip(row,delta)) for row in record['matrix']]
                literal=[sum(F[12*f+a])-10]+[sum(actualG[12*f+a][12*h+b] for h in range(3))-5 for b in record['other_coordinates']]
                need(residual==literal,'all396 literal Gram-to-marginal identities on raw control')
                if any(residual):nonzero.append(dict(coordinate=a,fibre=f,delta=delta,residual=residual))
        need(nonzero,'weaker two-group margin control violates fullGram marginals')
        # Exhaustive small cube controls prove implementation accepts distinct
        # columns and rejects assumptions violated by deliberate duplicates.
        cube=[[1,*p] for p in product([0,1],repeat=3)];cubeM=list(map(list,zip(*cube)))
        need(len(all_small_minors(cubeM))==92,'all8+28+56 small cube controls')
        duplicate=deepcopy(cubeM)
        for row in duplicate:row[1]=row[0]
        reject('duplicate_binary_columns',lambda:all_small_minors(duplicate))
        missing_lead=[r[:] for r in cubeM[1:]]
        reject('remove_affine_leading_row',lambda:all_small_minors(missing_lead))
        square=[[1,1,1,1],[0,1,0,1],[0,0,1,1]];v=[1,-1,-1,1]
        need(all(sum(a*b for a,b in zip(row,v))==0 for row in square) and len(all_small_minors(square))==14,'four-corner exact sharpness control, not a full factor')
        bad=deepcopy(saved['matrices'][0]['certificates']);bad[-1]['determinant']*=2
        reject('wrong_nonzero_determinant',lambda:check_saved(matrices[0]['matrix'],bad))
        bad=deepcopy(saved['matrices'][0]['certificates']);bad.pop()
        reject('missing_column_subset',lambda:check_saved(matrices[0]['matrix'],bad))
        bad=deepcopy(saved['matrices'][0]['certificates']);bad[-1]['minor'][0][0]^=1
        reject('changed_minor_entry',lambda:check_saved(matrices[0]['matrix'],bad))
        bad=deepcopy(matrices[0]['matrix']);bad[0][0]=0
        reject('changed_raw_marginal',lambda:need(bad==matrix_from_supports(0,supports)[2],'raw coefficient identity'))
        reject('universal_rank119',lambda:need(all(x['rank']==119 for x in matrices),'no rank inflation'))
        gate=load(UNSAT);need(gate['status'].endswith('_PASS'),'independently replayed balanced exclusion gate')
        binding_balanced=load(I+'hadamard_balanced_gram_unsat_v2/claim_binding.json')
        need(binding_balanced['id']=='C-FIXED-HADAMARD-BALANCED-GRAM-EXCLUSION' and binding_balanced['revision']==1
             and binding_balanced['status']=='VERIFIED','exact separate balanced-family premise')
        need(gate['inputs_sha256'][RAW]==PINS[RAW] and binding_balanced['inputs_sha256'][RAW]==PINS[RAW], 'balanced exclusion exact raw support binding')
        need(gate['inputs_sha256'][B+'hadamard_balanced_gram_cnf/instance.cnf']==binding_balanced['inputs_sha256'][B+'hadamard_balanced_gram_cnf/instance.cnf']=='c2d780f94dac4dda955743df03f8db2e8ec0f51217c671eb19fc5e42ed69ba37','balanced exclusion exact CNF binding')
        # Pin its encoding scope to the same raw L; no second DRAT replay asserted.
        basegate=load(I+'hadamard_balanced_gram_cnf_v2/summary.json','b63a4de43c1bcf4de56c52e4b4cc3ae8c697a3198654eb3f44d97bce7549ea7c')
        need(basegate['inputs_sha256'][RAW]==PINS[RAW],'same raw support in exact balanced encoding')
        for p,h in gate['outputs_sha256'].items():pin(p,h)
        save(out/'independent_marginal_certificates.json',dict(matrices=matrices,nonzero_minors=total,
            fibre_block_quadratics=fibre_quadratics,sparse_kernel_bound='Every nonzero rational kernel vector has support at least4.'))
        save(out/'weaker_margin_countercontrol.json',dict(nonzero_marginal_residuals=nonzero,scope='Literal row-margin positive fails necessary full-Gram marginals; no factor claimed.'))
        save(out/'controls.json',dict(small_cube_subsets=92,raw_minor_subsets=2100,double_counting_control_entries=396,
            four_corner_kernel=dict(matrix=square,vector=v),corruptions_rejected=corrupt))
        now=datetime.now(timezone.utc).isoformat()
        for p in ['acceleration/audit_20260930_hadamard_few_exception_marginals.py','docs/AUDIT_20260930_HADAMARD_FEW_EXCEPTION_MARGINALS.md','uv.lock','pyproject.toml']:pin(p)
        common=dict(revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
            verifier='/root/eight_domain_audit',created_at=now,updated_at=now,artifact_availability='LOCAL_ONLY',external_review=False,
            inputs_sha256=pins,method='Independent raw-support and Gram reconstruction; literal double-counting derivation; complete175 minors per coordinate by separate Leibniz determinants; independently authenticated balanced exclusion premise.',
            trusted_components=['Python integer/Fraction arithmetic and standard library; prior separately checked balanced encoding and DRAT replay only for the corollary.'])
        claims=[dict(common,id='C-FIXED-HADAMARD-AT-MOST-THREE-EXCEPTIONS-IMPLIES-BALANCED',
            statement='Every binary36x60 factor with the exact frozen six-prism Hadamard coordinate support and prescribed full integer Gram, if it has at most three unbalanced triplicate-support groups, has no unbalanced group. More precisely, any nonzero coordinate/fibre count-deviation vector in its necessary11x10 marginal system has at least four nonzero entries.',
            scope='Universal conditional implication for factors on this literal fixed support; it does not assume balance or a target automorphism.',
            assumptions=['BinaryF with exact coordinate support and prescribed Gram.','Unbalanced means some coordinate does not occupy all three fibres once across the group\'s three raw columns.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-TRIPLICATE-MARGINAL-RELAXATION',revision=1,relation='uses_result')],
            limitations=['The implication alone does not exclude balanced factors.','The four-corner control limits the abstract sparse-kernel argument, not the existence of four-exception factors.','No unrestricted target or full-support nonexistence follows.']),
            dict(common,id='C-FIXED-HADAMARD-AT-MOST-THREE-UNBALANCED-GROUPS-EXCLUSION',
            statement='No binary36x60 factor with the exact frozen six-prism Hadamard coordinate support and prescribed full integer Gram has at most three unbalanced support groups; hence any such factor, if one exists, has at least four unbalanced groups.',
            scope='Exclusion of the at-most-three-unbalanced-group subfamily on this one fixed support, using the separately verified balanced-family exclusion.',
            assumptions=['Same fixed support and prescribed Gram.','The exact independently replayed balanced-Gram exclusion is a separate premise.'],
            dependencies=[dict(id='C-FIXED-HADAMARD-AT-MOST-THREE-EXCEPTIONS-IMPLIES-BALANCED',revision=1,relation='premise'),
                          dict(id='C-FIXED-HADAMARD-BALANCED-GRAM-EXCLUSION',revision=1,relation='uses_result')],
            limitations=['No conclusion for factors with four or more exceptional groups.','No full-support, core-wide or unrestricted target exclusion.','Prior complete DRAT replay is authenticated, not repeated by this audit.'])]
        save(out/'claim_bindings.json',claims)
        for p in ['acceleration/audit_20260930_hadamard_few_exception_marginals.py','docs/AUDIT_20260930_HADAMARD_FEW_EXCEPTION_MARGINALS.md','uv.lock','pyproject.toml']:pin(p)
        save(out/'summary.json',dict(status='INDEPENDENT_HADAMARD_FEW_EXCEPTION_MARGINALS_PASS',timestamp=now,
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},
            marginal_matrices=12,matrix_shape=[11,10],ranks=[6]*12,nonzero_minors=2100,subset_population=dict(single=120,pair=540,triple=1440),
            corruptions=len(corrupt),verifier='/root/eight_domain_audit',shared_components=['Pinned raw artifacts and prior independent balanced proof gate only; no producer imports or elimination reuse.'],
            exclusions_scope='At most3 exceptional groups on one literal support; no broader factor or target resolution.',
            unaudited_producer_outputs=['required_balance_domains.json','two_group_row_margin_census.json'],
            limitations=['The separate64-domain/190pair row-only census is not approved by this report.','No new solver execution or DRAT replay.'],target_resolution=False,solver_calls=0,artifact_availability='LOCAL_ONLY'))
        print(json.dumps(dict(status='INDEPENDENT_HADAMARD_FEW_EXCEPTION_MARGINALS_PASS',sha256=sha(out/'summary.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(__file__)));raise

if __name__=='__main__':main()
