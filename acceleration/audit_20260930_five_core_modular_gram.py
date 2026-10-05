"""Independent literal core/finite-field rank certificates and kernel-action audit."""
from copy import deepcopy
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_five_core_modular_gram'
SUMMARY_SHA='04fa52ef09cac8d6911050424c3ba8dc5ca220280256637cf575b5d96154a3e1'
DOC=ROOT/'docs/DERIVATION_20260930_FIVE_CORE_MODULAR_GRAM.md'
DOC_SHA='a7e4e904a5504e64e75421498c5119ff46bd866a7351dd2f65a3d93ecc4364bb'
def need(x,s):
    if not x:raise ValueError(s)
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def read(p):return json.loads(Path(p).read_bytes())
def mv(a,v,p):return [sum(x*y for x,y in zip(row,v,strict=True))%p for row in a]
def multiply(a,b,p):
    width=len(b[0]);out=[]
    for row in a:
        z=[0]*width
        for t,x in enumerate(row):
            x%=p
            if x:
                for j,y in enumerate(b[t]):z[j]=(z[j]+x*y)%p
        out.append(z)
    return out
def span_rank(rows,p):
    """Incremental row-span basis using the RIGHTMOST coordinate; no full RREF."""
    basis={}
    for original in rows:
        v=[x%p for x in original]
        while any(v):
            k=max(i for i,x in enumerate(v) if x)
            if k in basis:
                v=[(a-v[k]*b)%p for a,b in zip(v,basis[k])]
            else:
                inverse=1 if v[k]==1 else 2
                basis[k]=[(x*inverse)%p for x in v];break
    return len(basis)
def matrix_shape(a,rows,columns,p):
    need(len(a)==rows and all(len(r)==columns and all(type(x)is int and 0<=x<p for x in r) for r in a),'canonical field matrix shape/types')

def certificate(a,cert,p):
    rows=len(a);width=len(a[0]);r=[[x%p for x in row] for row in a]
    t=[[int(i==j) for j in range(rows)] for i in range(rows)]
    need((cert['field'],cert['input_rows'],cert['input_columns'])==(p,rows,width),'certificate dimensions/field')
    for op in cert['operations']:
        need(type(op)is list and len(op) in (3,4) and all(type(x)is int for x in op[1:]),'operation types')
        typ=op[0];i=op[1];need(0<=i<rows,'operation destination')
        if typ=='swap':
            need(len(op)==3 and 0<=op[2]<rows,'swap input');j=op[2]
            r[i],r[j]=r[j],r[i];t[i],t[j]=t[j],t[i]
        elif typ=='scale':
            need(len(op)==3 and 0<op[2]<p,'invertible canonical scaling')
            r[i]=[x*op[2]%p for x in r[i]];t[i]=[x*op[2]%p for x in t[i]]
        elif typ=='add':
            need(len(op)==4 and 0<=op[2]<rows and op[2]!=i and 0<op[3]<p,'invertible distinct row addition')
            j,s=op[2:];r[i]=[(x+s*y)%p for x,y in zip(r[i],r[j])];t[i]=[(x+s*y)%p for x,y in zip(t[i],t[j])]
        else:raise ValueError('unknown operation')
    matrix_shape(cert['rref'],rows,width,p);matrix_shape(cert['row_transform'],rows,rows,p)
    need(r==cert['rref'] and t==cert['row_transform'],'every replayed row operation and transform')
    need(multiply(t,a,p)==r and span_rank(t,p)==rows,'invertible transformation times raw input')
    pivots=[];zero_seen=False
    for i,row in enumerate(r):
        nz=[j for j,x in enumerate(row) if x]
        if not nz:zero_seen=True;continue
        j=nz[0];need(not zero_seen and (not pivots or j>pivots[-1]) and row[j]==1 and
                     all(rr[j]==int(k==i) for k,rr in enumerate(r)),'literal RREF pivot conditions');pivots.append(j)
    need(cert['pivot_columns']==pivots and cert['rank']==len(pivots)==span_rank(a,p),'separate right-pivot rank agrees')
    null=cert['nullspace_basis'];matrix_shape(null,width-len(pivots),width,p)
    need(span_rank(null,p)==len(null) and all(not any(mv(a,v,p)) for v in null),'complete independent kernel basis')
    return dict(rank=len(pivots),rows=rows,columns=width,nullity=len(null),replayed_operations=len(cert['operations']))

def action(c,g,cert,act,p,n):
    size=3*n;cells=[[int(i//n==j) for i in range(size)] for j in range(3)]
    forced=cells if p==2 else [[(cells[j][i]-cells[2][i])%p for i in range(size)] for j in range(2)]
    need(act['forced_cell_basis']==forced,'exact forced cell relations')
    basis=act['complete_Gram_kernel_basis'];k=len(forced);dim=size-cert['rank']
    matrix_shape(basis,dim,size,p)
    need(basis[:k]==forced and span_rank(basis,p)==dim and all(not any(mv(g,v,p)) for v in basis),'complete adapted Gram kernel')
    a=act['core_action_matrix'];matrix_shape(a,dim,dim,p)
    for j,v in enumerate(basis):
        image=mv(c,v,p);represented=[sum(a[i][j]*basis[i][t] for i in range(dim))%p for t in range(size)]
        need(image==represented,'every action column in raw coordinates')
    need(all(a[i][j]==0 for i in range(k,dim) for j in range(k)),'forced relation span invariant')
    q=[row[k:] for row in a[k:]];d=dim-k
    scalars=[s for s in range(p) if all(q[i][j]==(s if i==j else 0) for i in range(d) for j in range(d))]
    need(act['quotient_action_matrix']==q and act['quotient_dimension']==d and act['quotient_scalar_values']==scalars,'complete quotient coordinates/scalars')
    need(act['quotient_action_idempotent']==(multiply(q,q,p)==q),'quotient idempotence telemetry')
    return dict(quotient_dimension=d,scalar_values=scalars,forced_relation_dimension=k,
                zero_quotient_verified=(0 in scalars),all_action_entries=dim*dim)

def geometry(c):
    size=len(c);need(size%3==0,'three equal cells');n=size//3
    matrix_shape(c,size,size,2)
    need(all(c[i][i]==0 and all(c[i][j]==c[j][i] for j in range(size)) for i in range(size)),'simple symmetric raw core')
    nb=[{j for j,x in enumerate(row) if x} for row in c]
    need(all(len(neighbors & set(range(g*n,(g+1)*n)))==1 for neighbors in nb for g in range(3)),'one neighbor in each cell')
    gram=[[n*int(i==j)+2-c[i][j]-len(nb[i]&nb[j])-int(i//n==j//n) for j in range(size)] for i in range(size)]
    # Integer commutation using neighbor sums rather than producer matrix products.
    need(all(sum(gram[k][j] for k in nb[i])==sum(gram[i][k] for k in nb[j]) for i in range(size) for j in range(size)), 'integer CG=GC')
    return n,gram

def controls(rawcase):
    counts={}
    for p in (2,3):
        count=0
        for flat in product(range(p),repeat=6):
            rows=[flat[:3],flat[3:]]
            rawspan={tuple((s*rows[0][j]+t*rows[1][j])%p for j in range(3)) for s,t in product(range(p),repeat=2)}
            need(len(rawspan)==p**span_rank(rows,p),'explicit tiny span rank');count+=1
        counts[str(p)]=count
    rejected=[];g=rawcase['prescribed_gram'];c=rawcase['core_adjacency'];field=rawcase['fields'][0];p=field['field']
    for name in ['rank','rref','transform','singular_operation','null_vector','duplicate_null_basis','action','quotient','forced_basis']:
        cert=deepcopy(field['Gram_rank_certificate']);act=deepcopy(field['Gram_kernel_action'])
        if name=='rank':cert['rank']+=1
        elif name=='rref':cert['rref'][0][0]^=1
        elif name=='transform':cert['row_transform'][0][0]^=1
        elif name=='singular_operation':cert['operations'].append(['scale',0,0])
        elif name=='null_vector':cert['nullspace_basis'][0][0]^=1
        elif name=='duplicate_null_basis':cert['nullspace_basis'][1]=cert['nullspace_basis'][0][:]
        elif name=='action':act['core_action_matrix'][0][0]^=1
        elif name=='quotient':act['quotient_action_matrix'][0][0]^=1
        else:act['forced_cell_basis'][0][0]^=1
        try:certificate(g,cert,p);action(c,g,cert,act,p,12)
        except ValueError:rejected.append(name)
        else:raise AssertionError('accepted corruption '+name)
    bad=deepcopy(c);bad[0][0]=1
    try:geometry(bad)
    except ValueError:rejected.append('raw_core_self_loop')
    else:raise AssertionError('raw core accepted')
    return dict(exhaustive_tiny_span_controls=counts,corruptions_rejected=rejected)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False);bindings={}
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'artifact hash '+key(p));bindings[key(p)]=value
    def load(p,h=None):pin(p,h);return read(p)
    try:
        summary=load(D/'summary.json',SUMMARY_SHA);manifest=load(D/'manifest.json',summary['manifest_sha256']);pin(DOC,DOC_SHA)
        for path,h in manifest['inputs_sha256'].items():pin(ROOT/path,h)
        for path,h in summary['outputs_sha256'].items():pin(ROOT/path,h)
        rows=[];all_certificates=[];lastcase=None
        expected_labels=[f'connected_{i:02d}' for i in range(4)]+['known243']
        need([x['label'] for x in summary['cases']]==expected_labels and summary['field_cases']==10,'frozen finite population')
        for label in expected_labels:
            rawcase=load(D/(label+'.json'));raw=load(ROOT/rawcase['raw_path']);lastcase=rawcase if label=='connected_00' else lastcase
            c=raw['cubic_core60'] if label=='known243' else raw['core_adjacency'];n,g=geometry(c)
            need(rawcase['core_adjacency']==c and rawcase['n']==n and rawcase['prescribed_gram']==g,'raw case geometry')
            if label!='known243':need(g==raw['target_gram'],'authenticated prescribed Gram')
            need([f['field'] for f in rawcase['fields']]==[2,3],'both declared prime fields')
            for f in rawcase['fields']:
                p=f['field'];cert=certificate(g,f['Gram_rank_certificate'],p)
                act=action(c,g,f['Gram_rank_certificate'],f['Gram_kernel_action'],p,n)
                lower=cert['rank'];upper=3*n-(3 if p==2 else 2)
                need(f['Gram_rank']==f['forced_factor_rank_lower']==lower and f['forced_factor_rank_upper']==upper and
                     f['Gram_rank_alone_forces_maximal_factor_rank']==(lower==upper),'finite rank conclusions')
                record=dict(label=label,n=n,field=p,Gram_rank=lower,forced_factor_rank_upper=upper,**act)
                all_certificates.append(dict(label=label,kind='Gram',field=p,**cert))
                if p==2:
                    need(f['all_Gram_factor_mixed_compatibility_sufficient_conditions']==dict(rank_gap_at_most_one=upper-lower<=1,scalar_quotient_action=bool(act['scalar_values'])),'GF2 sufficient-test telemetry')
                if label=='known243':
                    factor=raw['factor60x180'];width=180
                    need(all(sum(row)==18 for row in factor) and all(sum(factor[i][d] for i in range(g0*20,(g0+1)*20))==2 for g0 in range(3) for d in range(width)),'known exact margins')
                    need(all(sum(factor[i][d]*factor[j][d] for d in range(width))==g[i][j] for i in range(60) for j in range(60)),'known integer Gram')
                    h=[[2-factor[i][d]-sum(factor[j][d] for j,x in enumerate(c[i]) if x) for d in range(width)] for i in range(60)]
                    fc=certificate(factor,f['known_factor_certificate'],p)
                    ac=certificate([row+rhs for row,rhs in zip(factor,h)],f['augmented_certificate'],p)
                    need(fc['rank']==f['known_factor_rank']==ac['rank']==f['augmented_F_H_rank'],'known exact mixed rank consistency')
                    need(multiply(factor,raw['residual180x180'],p)==[[x%p for x in row] for row in h],'known actual nonempty D mixed equation')
                    all_certificates.extend([dict(label=label,kind='F',field=p,**fc),dict(label=label,kind='F_H',field=p,**ac)])
                    record['known_factor_rank']=fc['rank'];record['known_mixed_equations_checked']=10800
                else:need(f['known_factor_rank'] is None,'no invented research factor rank')
                rows.append(record)
        control=controls(lastcase);save(args.out/'controls.json',control);save(args.out/'exact_checks.json',dict(cases=rows,certificates=all_certificates))
        need([r['Gram_rank'] for r in rows if r['field']==2]==[22,24,24,26,30] and
             [r['Gram_rank'] for r in rows if r['field']==3]==[27,29,29,29,27],'expected exact ranks')
        need([r['label'] for r in rows if r['field']==3 and r['zero_quotient_verified']]==['connected_01','connected_02','connected_03'],'exact finite zero-action premise')
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_FIVE_CORE_MODULAR_GRAM.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat()
        report=dict(status='INDEPENDENT_FIVE_CORE_MODULAR_GRAM_AND_KERNEL_LEMMAS_PASS',timestamp=now,
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
            outputs_sha256={key(p):digest(p) for p in args.out.iterdir() if p.is_file()},cases=rows,
            complete_rank_certificates=14,complete_kernel_action_cases=10,positive_small_controls=793,
            corrupt_controls=len(control['corruptions_rejected']),verifier='/root/state_literature_audit',
            method='independent_artifact_check_and_independent_derivation',
            shared_components=['Python standard library only; no producer imports, RREF routines or coordinate solvers reused.',
                               'Frozen raw cores and independently checked SRG243 fixture.'],
            written_universal_audit='docs/AUDIT_20260930_FIVE_CORE_MODULAR_GRAM.md',
            recommendation='VERIFIED',review_state='CLEAR',artifact_availability='LOCAL_ONLY',
            target_resolution=False,external_review=False,
            limitations=['Only five raw cores and two fields were examined; no matching census or target coverage claim.',
                         'The GF2 sufficient conditions fail in all five cases; this establishes no incompatible factor.',
                         'The GF3 conclusions concern arbitrary field D only, not symmetric, zero-diagonal, binary, degree-constrained or quadratic residual feasibility.',
                         'No rank of an unavailable research factor is asserted.'])
        save(args.out/'summary.json',report)
        claims=[dict(id='C-TRIANGLE-GF2-SCALAR-KERNEL-MIXED-CONSISTENCY',revision=1,kind='mathematical result',basis=['DERIVED'],
            statement='For any symmetric three-cell core C with one neighbor per cell and Gram G=nI-C-C²+2J-B, every GF2 factor F with FF^T=G and even cell-column sums has some field solution D to FD=2J-(I+C)F whenever C acts as a scalar on ker(G) modulo the three cell indicators; rank(G)>=3n-4 is sufficient.',
            scope='Conditional universal GF2 linear compatibility; no residual graph constraints.',dependencies=[]),
            dict(id='C-FIVE-CORE-MODULAR-GRAM-RANKS-ACTIONS',revision=1,kind='empirical/engineering result',basis=['COMPUTED'],
            statement='The four frozen connected cores and known243 have GF2 Gram ranks22,24,24,26,30 and GF3 ranks27,29,29,29,27; all five GF2 kernel quotient actions are nonscalar, while the GF3 quotient action is zero precisely for connected01,02,03 in this population.',
            scope='Exact finite ten matrix/action cases, with known243 factor ranks57 and47 checked independently.',
            dependencies=[dict(id='C-FOUR-CONNECTED-IDENTITY-CORE-PORTFOLIO',revision=1,relation='uses_result'),dict(id='C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL',revision=1,relation='verification_dependency')]),
            dict(id='C-THREE-CONNECTED-CORE-GF3-MIXED-CONSISTENCY',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],
            statement='For each frozen core connected01,02,03, every binary36x60 incidence factor with prescribed integer Gram, row sums10 and cell-column sums2 has some GF3 matrix D solving FD=2J-(I+C)F.',
            scope='Three fixed cores only; a conditional modular linear solution, without symmetry or graph completion.',
            dependencies=[dict(id='C-FIVE-CORE-MODULAR-GRAM-RANKS-ACTIONS',revision=1,relation='premise')])]
        for claim in claims:claim.update(recommendation='VERIFIED',review_state='CLEAR',assumptions=['No nontrivial target automorphism is assumed.'],
            verifier=report['verifier'],method=report['method'],evidence=[dict(path=key(args.out/'summary.json'),sha256=digest(args.out/'summary.json'),availability='LOCAL_ONLY')],
            limitations=report['limitations'],created_at=now,updated_at=now)
        save(args.out/'claim_bindings.json',dict(claims=claims,ledger_changed=False))
        print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'),bindings_sha256=digest(args.out/'claim_bindings.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
