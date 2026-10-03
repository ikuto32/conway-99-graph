"""Five frozen prescribed-Gram rank cases; exact producer certificates, candidates only."""
from datetime import datetime,timezone
from hashlib import file_digest
from itertools import product
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
SPEC=Path(__file__).with_name('theory_20260930_five_core_modular_gram_spec.md')
PORT=ROOT/'acceleration/results/20260930_connected_identity_cores'
RAW243=ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json'
GATES={ROOT/'acceleration/results/20260930_independent_review/connected_identity_cores/summary.json':
    ('efdcacb9130bf29a28ece4c07022bdab11ab953a862f117fc55f44bd5244d2b4','INDEPENDENT_CONNECTED_IDENTITY_CORE_PORTFOLIO_PASS'),
    ROOT/'acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json':
    ('28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e','INDEPENDENT_SRG243_NONEMPTY_RESIDUAL_FIXTURE_PASS'),
    ROOT/'acceleration/results/20260930_independent_review/triangle_gf2_maxrank/summary.json':
    ('229dfa1a24b3fa840965125c2efc7a017cd882fb77edd056cc714e4ca866d006','INDEPENDENT_TRIANGLE_GF2_MAXRANK_MIXED_CONSISTENCY_PASS')}

def need(ok,msg):
    if not ok: raise ValueError(msg)
def digest(path):
    with Path(path).open('rb') as f:return file_digest(f,'sha256').hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def read(path):return json.loads(Path(path).read_bytes())
def stamp():return datetime.now(timezone.utc).isoformat()
def save(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
def matmul(a,b,p=None):
    cols=list(zip(*b)); out=[[sum(x*y for x,y in zip(row,col,strict=True)) for col in cols] for row in a]
    return out if p is None else [[v%p for v in row] for row in out]
def transpose(a):return list(map(list,zip(*a)))
def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]

def eliminate(a,p):
    need(p in (2,3) and a and len({len(row) for row in a})==1,'literal supported rectangular field matrix')
    rows,cols=len(a),len(a[0]);r=[[x%p for x in row] for row in a];t=eye(rows);ops=[];piv=[]
    for j in range(cols):
        k=len(piv)
        if k==rows:break
        candidate=next((i for i in range(k,rows) if r[i][j]),None)
        if candidate is None:continue
        if candidate!=k:
            r[k],r[candidate]=r[candidate],r[k];t[k],t[candidate]=t[candidate],t[k];ops.append(['swap',k,candidate])
        inv=pow(r[k][j],-1,p)
        if inv!=1:
            r[k]=[inv*x%p for x in r[k]];t[k]=[inv*x%p for x in t[k]];ops.append(['scale',k,inv])
        for i in range(rows):
            if i!=k and r[i][j]:
                mult=(-r[i][j])%p;r[i]=[(x+mult*y)%p for x,y in zip(r[i],r[k])]
                t[i]=[(x+mult*y)%p for x,y in zip(t[i],t[k])];ops.append(['add',i,k,mult])
        piv.append(j)
    free=[j for j in range(cols) if j not in piv];null=[]
    for j in free:
        v=[0]*cols;v[j]=1
        for i,col in enumerate(piv):v[col]=-r[i][j]%p
        null.append(v)
    return dict(field=p,input_rows=rows,input_columns=cols,rank=len(piv),pivot_columns=piv,
        rref=r,row_transform=t,operations=ops,nullspace_basis=null)

def check_certificate(a,c):
    p=c['field'];r=[[x%p for x in row] for row in a];t=eye(len(a))
    for op in c['operations']:
        if op[0]=='swap':
            _,i,j=op;r[i],r[j]=r[j],r[i];t[i],t[j]=t[j],t[i]
        elif op[0]=='scale':
            _,i,s=op;need(s%p!=0,'invertible scale');r[i]=[s*x%p for x in r[i]];t[i]=[s*x%p for x in t[i]]
        elif op[0]=='add':
            _,i,j,s=op;need(i!=j,'distinct row addition');r[i]=[(x+s*y)%p for x,y in zip(r[i],r[j])];t[i]=[(x+s*y)%p for x,y in zip(t[i],t[j])]
        else:raise ValueError('invalid row operation')
    need(r==c['rref'] and t==c['row_transform'] and matmul(t,a,p)==r,'row-operation transcript/transform equality')
    piv=[]
    for row in r:
        j=next((j for j,x in enumerate(row) if x),None)
        if j is not None:
            need(not piv or j>piv[-1],'increasing pivots');piv.append(j)
            need(row[j]==1 and sum(int(rr[j]!=0) for rr in r)==1,'normalized unique pivot')
        else:need(all(not any(rr) for rr in r[len(piv):]),'zero rows form tail')
    need(piv==c['pivot_columns'] and len(piv)==c['rank'],'exact rank metadata')
    need(len(c['nullspace_basis'])==len(a[0])-len(piv),'nullity count')
    for v in c['nullspace_basis']:need(all(sum(x*y for x,y in zip(row,v))%p==0 for row in a),'nullspace vector')
    return True

def rank(a,p):return eliminate(a,p)['rank']
def coordinates(basis,v,p):
    # Unique coefficients in the independent row-vector basis, solved as columns.
    aug=[row+[value] for row,value in zip(transpose(basis),v)]
    rr=eliminate(aug,p);need(rr['rank']==len(basis) and rr['pivot_columns']==list(range(len(basis))),'vector lies in independent basis span')
    return [rr['rref'][i][-1] for i in range(len(basis))]

def kernel_action(c,g,cert,p,n):
    cells=[[int(i//n==a) for i in range(3*n)] for a in range(3)]
    forced=cells if p==2 else [[(x-y)%p for x,y in zip(cells[a],cells[2])] for a in range(2)]
    need(all(all(sum(x*y for x,y in zip(row,v))%p==0 for row in g) for v in forced),'forced cell relations annihilate Gram')
    basis=[v[:] for v in forced]
    for v in cert['nullspace_basis']:
        if rank(basis+[v],p)>len(basis):basis.append(v[:])
    need(len(basis)==3*n-cert['rank'],'basis covers complete Gram kernel')
    action_columns=[]
    for v in basis:
        image=[sum(x*y for x,y in zip(row,v))%p for row in c]
        action_columns.append(coordinates(basis,image,p))
    action=transpose(action_columns);k=len(forced);qdim=len(basis)-k
    need(all(action[i][j]==0 for i in range(k,len(basis)) for j in range(k)),'forced cell relation span is C-invariant')
    quotient=[row[k:] for row in action[k:]]
    scalars=[a for a in range(p) if quotient==[[a*int(i==j)%p for j in range(qdim)] for i in range(qdim)]]
    idempotent=(matmul(quotient,quotient,p)==quotient) if quotient else True
    return dict(forced_cell_basis=forced,complete_Gram_kernel_basis=basis,core_action_matrix=action,
        quotient_dimension=qdim,quotient_action_matrix=quotient,quotient_scalar_values=scalars,
        quotient_action_idempotent=idempotent,
        interpretation='Computed C-action on ker(G) modulo forced cell relations. Scalar action is sufficient for all intermediate kernel subspaces to be C-invariant; field consistency still needs the inhomogeneous term considered.')

def calibrate(out):
    counts={};rejected=[]
    for p in (2,3):
        done=0
        for values in product(range(p),repeat=6):
            a=[list(values[:3]),list(values[3:])];cert=eliminate(a,p);check_certificate(a,cert)
            span={tuple((s*a[0][j]+t*a[1][j])%p for j in range(3)) for s,t in product(range(p),repeat=2)}
            need(len(span)==p**cert['rank'],'exhaustive coefficient-span rank positive control');done+=1
        counts[str(p)]=done
    a=[[1,2,0],[0,1,1],[1,0,2]];valid=eliminate(a,3);check_certificate(a,valid)
    for label in ('rank','rref','transform','operation','nullvector'):
        bad=json.loads(json.dumps(valid))
        if label=='rank':bad['rank']+=1
        if label=='rref':bad['rref'][0][0]=(bad['rref'][0][0]+1)%3
        if label=='transform':bad['row_transform'][0][0]=(bad['row_transform'][0][0]+1)%3
        if label=='operation':bad['operations'].append(['scale',0,0])
        if label=='nullvector':
            # Use a rank-deficient positive control to ensure a saved kernel exists.
            aa=[[1,1,0],[0,0,0]];bad=eliminate(aa,3);bad['nullspace_basis'][0][0]=(bad['nullspace_basis'][0][0]+1)%3
        else:aa=a
        try:check_certificate(aa,bad)
        except ValueError:rejected.append(label)
        else:raise ValueError('corrupted elimination accepted '+label)
    save(out/'controls.json',dict(exhaustive_two_by_three_matrices=counts,method='Independent explicit row-span cardinality vs elimination rank for all small matrices.',corrupted_certificates_rejected=rejected,independent_approval=False))

def derive(c):
    size=len(c);n=size//3;need(size in (36,60) and all(len(row)==size for row in c),'exact planned dimensions')
    need(all(type(x)is int and x in (0,1) for row in c for x in row),'literal binary core')
    need(all(c[i][i]==0 and all(c[i][j]==c[j][i] for j in range(size)) for i in range(size)),'symmetric simple core')
    need(all(sum(c[i][h*n:(h+1)*n])==1 for i in range(size) for h in range(3)),'one neighbor per cell')
    cc=matmul(c,c)
    g=[[n*int(i==j)+2-c[i][j]-cc[i][j]-int(i//n==j//n) for j in range(size)] for i in range(size)]
    need(matmul(c,g)==matmul(g,c),'literal integer CG=GC')
    return n,g

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();bindings={}
    for path,(h,status) in GATES.items():
        need(digest(path)==h and read(path)['status']==status,'frozen independent prerequisite gate');bindings[key(path)]=h
    cases=[(f'connected_{i:02d}',PORT/f'core_{i:02d}.json') for i in range(4)]+[('known243',RAW243)]
    for label,path in cases:
        bindings[key(path)]=digest(path)
        gate=read(next(iter(GATES))) if label!='known243' else read(list(GATES)[1])
        need(gate['inputs_sha256'][key(path)]==bindings[key(path)],'independently checked raw input')
    for p in [Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml',PORT/'summary.json']:
        bindings[key(p)]=digest(p)
    save(args.out/'manifest.json',dict(timestamp=stamp(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),
        uv_version=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=bindings,
        question='Do five prescribed core Grams force maximal field factor rank or scalar core action on the remaining Gram kernel?',
        frozen_population=[dict(label=label,path=key(path),sha256=digest(path)) for label,path in cases],fields=[2,3],
        resource_limit_seconds=60,selection='Exactly four already frozen connected P=I cores and the independently checked SRG243 positive fixture; no matching-census enumeration.',
        acceptance='Exact row-operation certificate replay, no numerical tolerance.',all_new_claims='CANDIDATE pending a separate reviewer'))
    calibrate(args.out);records=[];outputs={}
    for label,path in cases:
        need(time.monotonic()-start<60,'bounded preparation limit')
        raw=read(path);c=raw['core_adjacency'] if label!='known243' else raw['cubic_core60'];n,g=derive(c)
        if label!='known243':need(g==raw['target_gram'],'literal core formula matches saved prescribed Gram')
        f=raw['factor60x180'] if label=='known243' else None
        if f is not None:
            need(matmul(f,transpose(f))==g,'known positive exact integer Gram')
            need(all(sum(row)==n-2 for row in f) and all(sum(f[r][d] for r in range(h*n,(h+1)*n))==2 for h in range(3) for d in range(len(f[0]))),'known factor exact margins')
        record=dict(label=label,raw_path=key(path),n=n,core_adjacency=c,prescribed_gram=g,fields=[])
        for p in (2,3):
            cert=eliminate(g,p);check_certificate(g,cert);action=kernel_action(c,g,cert,p,n)
            upper=3*n-(3 if p==2 else 2);lower=cert['rank']
            field=dict(field=p,Gram_rank=lower,Gram_rank_certificate=cert,forced_factor_rank_lower=lower,forced_factor_rank_upper=upper,
                Gram_rank_alone_forces_maximal_factor_rank=lower==upper,Gram_kernel_action=action)
            if p==2:
                need(all(g[i][i]%2==0 for i in range(3*n)) and lower%2==0,'alternating Gram even rank')
                field['all_Gram_factor_mixed_compatibility_sufficient_conditions']=dict(rank_gap_at_most_one=upper-lower<=1,scalar_quotient_action=bool(action['quotient_scalar_values']))
            if f is not None:
                fcert=eliminate(f,p);check_certificate(f,fcert)
                cf=matmul(c,f);h=[[2-f[i][d]-cf[i][d] for d in range(len(f[0]))] for i in range(3*n)]
                aug=[x+y for x,y in zip(f,h)];acert=eliminate(aug,p);check_certificate(aug,acert)
                d=raw['residual180x180'];need(matmul(f,d,p)==[[x%p for x in row] for row in h],'actual known residual field mixed equation')
                field.update(known_factor_rank=fcert['rank'],known_factor_certificate=fcert,augmented_F_H_rank=acert['rank'],augmented_certificate=acert,
                    maximal_factor_rank_premise_holds=fcert['rank']==upper,known_actual_residual_checks=3*n*len(f[0]))
            else:
                field.update(known_factor_rank=None,known_factor_rank_null_reason='No complete feasible factor for this core is known to this experiment; only necessary Gram data are supplied.')
            record['fields'].append(field)
        dest=args.out/(label+'.json');save(dest,record);outputs[key(dest)]=digest(dest)
        records.append(dict(label=label,n=n,fields=[{k:v for k,v in x.items() if k in ('field','Gram_rank','forced_factor_rank_lower','forced_factor_rank_upper','Gram_rank_alone_forces_maximal_factor_rank','known_factor_rank','maximal_factor_rank_premise_holds','all_Gram_factor_mixed_compatibility_sufficient_conditions')}|dict(quotient_dimension=x['Gram_kernel_action']['quotient_dimension'],quotient_scalar_values=x['Gram_kernel_action']['quotient_scalar_values']) for x in record['fields']]))
        print(json.dumps(records[-1]),flush=True)
    need(all(digest(ROOT/p)==h for p,h in bindings.items()),'all frozen inputs unchanged')
    outputs[key(args.out/'controls.json')]=digest(args.out/'controls.json')
    summary=dict(status='CANDIDATE_FIVE_CORE_MODULAR_GRAM_RANK_CHARACTERIZATION',timestamp=stamp(),manifest_sha256=digest(args.out/'manifest.json'),
        cases=records,distinct_raw_cores=5,field_cases=10,outputs_sha256=outputs,elapsed_seconds=time.monotonic()-start,
        new_candidate_derivation='Over GF2 CG=GC makes ker G invariant; cell parity bounds rank F by3n-3. If rank G>=3n-4 then ker(F^T) is either the cell span or all ker G, so FD=H is field-consistent. More generally scalar C-action on ker G modulo the cell span makes every intermediate kernel invariant and gives the same consistency.',
        interpretation='These sufficient conditions can close a finite field-consistency attack for the stated core, but do not construct symmetric/binary D or satisfy the residual quadratic equation.',
        target_resolution=False,independent_approval=False,artifact_availability='LOCAL_ONLY',limitations=['All new ranks and derived implications await independent review.',
            'Only five raw cores are counted; no all3580 census.', 'Known243 is a positive fixture, not Conway99.',
            'A field-solvable FD=H is not a graph completion.', 'Failure of a sufficient condition is not evidence of an obstruction.'])
    save(args.out/'summary.json',summary);print(json.dumps(dict(summary=key(args.out/'summary.json'),sha256=digest(args.out/'summary.json'))))

if __name__=='__main__':main()
