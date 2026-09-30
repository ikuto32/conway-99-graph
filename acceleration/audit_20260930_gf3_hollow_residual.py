"""Separate stdlib field checker: actual D coefficient systems and raw certificates."""
import argparse,copy,hashlib,itertools,json,platform,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';D=B/'20260930_gf3_hollow_residual'
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def tr(a):return list(map(list,zip(*a)))
def mm(a,b,mod=None):
    cols=tr(b);r=[[sum(x*y for x,y in zip(row,col)) for col in cols] for row in a]
    return [[v%mod for v in row] for row in r] if mod else r
def mod(a):return [[x%3 for x in row] for row in a]
def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def echelon(rows,width):
    basis={}
    for row in rows:
        v=[x%3 for x in row];need(len(v)==width,'row width')
        for p in sorted(basis,reverse=True):
            if v[p]:
                c=v[p];b=basis[p];v=[(x-c*y)%3 for x,y in zip(v,b)]
        p=next((i for i in range(width-1,-1,-1) if v[i]),None)
        if p is not None:
            c=v[p];basis[p]=[(c*x)%3 for x in v]
    return basis
def rank(a,width=None):return len(echelon(a,width if width is not None else len(a[0])))
def nullspace(a,width):
    e=echelon(a,width);free=[j for j in range(width) if j not in e];basis=[]
    for j in free:
        v=[0]*width;v[j]=1
        for p in sorted(e):v[p]=-sum(e[p][c]*v[c] for c in range(p))%3
        need(all(sum(x*y for x,y in zip(row,v))%3==0 for row in a),'own literal kernel');basis.append(v)
    return basis
def member(rows,v):return rank(rows+[v],len(v))==rank(rows,len(v))
def solve(a,b,width):
    e={}
    for row,rhs in zip(a,b):
        v=[x%3 for x in row]+[rhs%3];need(len(v)==width+1,'augmented width')
        for p in sorted(e,reverse=True):
            if v[p]:c=v[p];v=[(x-c*y)%3 for x,y in zip(v,e[p])]
        p=next((i for i in range(width-1,-1,-1) if v[i]),None)
        if p is None:
            if v[-1]:return None
        else:c=v[p];e[p]=[c*x%3 for x in v]
    x=[0]*width
    for p in sorted(e):x[p]=(e[p][-1]-sum(e[p][j]*x[j] for j in range(p)))%3
    need(all(sum(c*v for c,v in zip(row,x))%3==rhs%3 for row,rhs in zip(a,b)),'direct system solution');return x
def d_system(f,h,hollow=False):
    a=len(f);m=len(f[0]);pairs=[(i,j) for i in range(m) for j in range(i+int(hollow),m)];matrix=[];rhs=[]
    for r in range(a):
        for col in range(m):
            matrix.append([(f[r][i] if j==col else 0)+(f[r][j] if i==col and i!=j else 0) for i,j in pairs]);rhs.append(h[r][col])
    x=solve(matrix,rhs,len(pairs))
    if x is None:return None
    d=[[0]*m for _ in range(m)]
    for (i,j),v in zip(pairs,x):d[i][j]=d[j][i]=v
    need(mm(f,d,3)==mod(h) and d==tr(d) and (not hollow or not any(d[i][i] for i in range(m))),'actual D');return d
def criterion(f,h,d0=None):
    a=len(f);m=len(f[0]);left=nullspace(tr(f),a);compat=all(sum(v[i]*h[i][j] for i in range(a))%3==0 for v in left for j in range(m));fh=mm(f,tr(h),3);sym=fh==tr(fh)
    k=nullspace(f,m);products=[[u[t]*v[t]%3 for t in range(m)] for i,u in enumerate(k) for v in k[i:]]
    if not compat or not sym:return compat,sym,False
    if d0 is None:d0=d_system(f,h)
    need(d0 is not None,'symmetric criterion has direct solution');return compat,sym,member(products,[d0[i][i] for i in range(m)])
def small_checks(raw):
    outcomes=[];lookup={(tuple(r['shape']),tuple(r['F']),tuple(r['H'])):r for r in raw['records']};need(len(lookup)==len(raw['records'])==7290,'complete unique producer small records')
    for a,m in [(1,3),(2,2)]:
        for fv in itertools.product(range(3),repeat=a*m):
            f=[list(fv[i*m:(i+1)*m]) for i in range(a)]
            for hv in itertools.product(range(3),repeat=a*m):
                h=[list(hv[i*m:(i+1)*m]) for i in range(a)];symd=d_system(f,h);hollow=d_system(f,h,True);c,s,z=criterion(f,h,symd);need((c and s)==(symd is not None) and z==(hollow is not None),'theorem vs direct D coefficient systems')
                r=lookup[( (a,m),fv,hv)];need((c,s,z)==(r['kernel_compatible'],r['symmetry_compatible'],r['hollow_possible']),'saved entire finite decision');outcomes.append([a,m,list(fv),list(hv),c,s,z])
    nr=0
    for values in itertools.product(range(3),repeat=6):
        rows=[list(values[:3]),list(values[3:])];span={tuple((s*rows[0][i]+t*rows[1][i])%3 for i in range(3)) for s in range(3) for t in range(3)};need(3**rank(rows)==len(span),'independent finite-span rank');nr+=1
    for r in raw['omitted_premise_counterexamples']:
        c,s,z=criterion(r['F'],r['H']);need((c,s)==(r['kernel_compatible'],r['symmetry_compatible']) and not z and d_system(r['F'],r['H'],True) is None,'omitted premise actual failure')
    return dict(decisions=outcomes,direct_system_pairs=len(outcomes),finite_span_rank_controls=nr)
def check_kernel(f,k,expected_rank):
    need(rank(f)==expected_rank and len(k)==len(f[0])-expected_rank and rank(k)==len(k),'complete independent kernel dimensions');need(not any(v for row in mm(f,tr(k),3) for v in row),'all literal kernel equations')
def check_products(k,cert):
    pairs=list(itertools.combinations_with_replacement(range(len(k)),2));inds=[tuple(x) for x in cert['selected_product_indices']];need(len(inds)==len(set(inds))==180 and inds==sorted(inds),'distinct ordered products');rows=[[k[i][t]*k[j][t]%3 for t in range(180)] for i,j in inds];need(rows==cert['selected_product_rows'],'literal products');need(rank(rows)==180 and rank(cert['forward_basis'])==180 and cert['rank']==cert['width']==180 and cert['full_span'],'independent full product span');need(cert['products_examined']==pairs.index(inds[-1])+1==8911,'saved finite generation prefix');return rows
def genuine(raw,adj,cert):
    a=adj['adjacency'];n=243;aa=mm(a,a);need(all(aa[i][j]==20*int(i==j)-a[i][j]+2 for i in range(n) for j in range(n)),'genuine243 adjacency identity')
    c=raw['cubic_core60'];f=raw['factor60x180'];d=raw['residual180x180'];cc=mm(c,c);g=[[20*int(i==j)-c[i][j]-cc[i][j]+2-int(i//20==j//20) for j in range(60)] for i in range(60)];h=[[2-f[i][j]-sum(c[i][t]*f[t][j] for t in range(60)) for j in range(180)] for i in range(60)]
    need(mm(f,tr(f))==g and mm(f,d)==h,'integer Gram and mixed');dd=mm(d,d);ff=mm(tr(f),f);need(all(dd[i][j]+ff[i][j]==20*int(i==j)-d[i][j]+2 for i in range(180) for j in range(180)),'integer residual quadratic')
    need(all(sum(r)==18 for r in f) and all(sum(f[i][j] for i in range(20*s,20*s+20))==2 for s in range(3) for j in range(180)),'literal triangle margins');need(mm(c,g)==mm(g,c),'Gram commutes');k=cert['kernel_certificate']['nullspace_basis'];check_kernel(f,k,47);products=check_products(k,cert['square_span_certificate'])
    sc=cert['symmetric_completion'];p=sc['basis'];inv=sc['basis_inverse'];z=sc['congruence_matrix'];d0=sc['symmetric_solution'];need(mm(p,inv,3)==eye(180) and mm(inv,p,3)==eye(180),'two-sided basis inverse');need(z==tr(z) and mm(mm(tr(inv),z,3),inv,3)==d0,'saved congruence');need(d0==tr(d0) and mm(f,d0,3)==mod(h),'literal symmetric D0');need(all(sum(r)%3==1 for r in d0),'D0 automatic degree')
    # A fresh hollow completion, constructed from the independently checked diagonal-product system.
    coeff=solve(tr(products),[-d0[i][i] for i in range(180)],180);need(coeff is not None,'full diagonal correction exists');s=[[0]*133 for _ in range(133)]
    for (i,j),v in zip(cert['square_span_certificate']['selected_product_indices'],coeff):
        if i==j:s[i][i]=(s[i][i]+v)%3
        else:s[i][j]=s[j][i]=(s[i][j]+2*v)%3
    correction=mm(mm(tr(k),s,3),k,3);new=[[(d0[i][j]+correction[i][j])%3 for j in range(180)] for i in range(180)]
    need(new==tr(new) and not any(new[i][i] for i in range(180)) and mm(f,new,3)==mod(h) and all(sum(row)%3==1 for row in new),'fresh hollow mixed completion with automatic degree')
    minus=[[(a[i][j]-int(i==j))%3 for j in range(243)] for i in range(243)];square=mm(minus,minus,3);need(all(x==2 for row in square for x in row) and not any(x for row in mm(square,minus,3) for x in row),'distinct243 nilpotent identity')
    ranks=dict(rank_F=rank(f),kernel_dimension=rank(k),square_span_rank=rank(products),rank_A=rank(a),rank_A_minus_I=rank(minus),rank_square=rank(square))
    need(all(cert[key]==value for key,value in ranks.items()),'all reported243 ranks');return ranks,dict(diagonal_product_coefficients=coeff,hollow_solution=new,scope='GF3 only; no binary/quadratic claim about this newly constructed solution.'),dict(F=f,H=h,K=k,D0=d0,products=products)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        v=sha(p);need(h is None or h==v,'identity '+key(p));pins[key(p)]=v
    try:
        pin(D/'summary.json','021a0fa0e3f2ff3e4e688a1f389bd7d5139fe8822e2a0f171c92d481dd33970a');summary=read(D/'summary.json')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_GF3_HOLLOW_RESIDUAL.md']:pin(p)
        small=small_checks(read(D/'controls.json'));save(out/'independent_small_systems.json',small)
        raw=read(B/'20260930_srg243_residual_fixture/triangle_blocks.json');adj=read(B/'20260930_srg243_residual_fixture/adjacency243.json');cert=read(D/'genuine243.json');ranks,hollow,objects=genuine(raw,adj,cert);save(out/'independent_hollow_completion243.json',hollow)
        rook=read(D/'rook9.json');a=[[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)];need(a==rook['adjacency'],'raw rook9');aa=mm(a,a);need(all(aa[i][j]==2*int(i==j)-a[i][j]+2 for i in range(9) for j in range(9)),'rook identity');minus=[[(a[i][j]-int(i==j))%3 for j in range(9)] for i in range(9)];sq=mm(minus,minus,3);need([rank(a),rank(minus),rank(sq)]==[rook['rank_A'],rook['rank_A_minus_I'],rook['rank_square']],'rook finite ranks');need(all(x==2 for row in sq for x in row) and not any(v for row in mm(sq,minus,3) for v in row),'rook nilpotence')
        cores=[]
        for rec in read(D/'core_diagnostics.json')['records']:
            rawc=read(ROOT/rec['path']);c=rawc.get('core_adjacency36',rawc.get('core_adjacency'));b=[[int(i!=j) if i<3 and j<3 else int((j-3)//12==i) if i<3 else int((i-3)//12==j) if j<3 else c[i-3][j-3] for j in range(39)] for i in range(39)];v=[rank(c),rank(b),rank([[b[i][j]+int(i==j) for j in range(39)] for i in range(39)])];need(v==[rec['rank_C_mod3'],rec['rank_triangle39_mod3'],rec['rank_triangle39_plus_I_mod3']],'all five core ranks');cores.append(dict(path=rec['path'],ranks=v))
        rejected=[]
        def reject(name,check):
            try:check()
            except ValueError:rejected.append(name)
            else:raise ValueError('accepted corruption '+name)
        bad=copy.deepcopy(objects['K']);bad[0][0]=(bad[0][0]+1)%3;reject('kernel_coordinate',lambda:check_kernel(objects['F'],bad,47))
        bad=copy.deepcopy(cert['square_span_certificate']);bad['selected_product_rows'][0][0]=(bad['selected_product_rows'][0][0]+1)%3;reject('product_entry',lambda:check_products(objects['K'],bad))
        bad=copy.deepcopy(cert['square_span_certificate']);bad['selected_product_indices'][1]=bad['selected_product_indices'][0];reject('duplicate_generator',lambda:check_products(objects['K'],bad))
        bad=copy.deepcopy(cert['square_span_certificate']);bad['products_examined']-=1;reject('wrong_prefix_count',lambda:check_products(objects['K'],bad))
        d0=copy.deepcopy(objects['D0']);d0[0][1]=(d0[0][1]+1)%3;reject('nonsymmetric_D0',lambda:need(d0==tr(d0),'symmetry'))
        altered=copy.deepcopy(hollow['hollow_solution']);altered[0][0]=1;reject('hollow_diagonal',lambda:need(not any(altered[i][i] for i in range(180)),'diagonal'))
        hh=copy.deepcopy(objects['H']);hh[0][0]+=1;reject('wrong_mixed_rhs',lambda:need(mm(objects['F'],objects['D0'],3)==mod(hh),'mixed'))
        save(out/'corruptions.json',dict(rejected=rejected,omitted_premise_counterexamples=read(D/'controls.json')['omitted_premise_counterexamples']))
        need(summary['complete_small_F_H_pairs']==7290 and summary['rank_controls']==729 and summary['genuine243_rank_F']==47 and summary['genuine243_kernel_dimension']==133 and summary['genuine243_square_span_rank']==180 and summary['genuine243_square_span_full'],'summary exact population')
        statement='Over GF(3), symmetric FD=H is solvable exactly when ker(F^T) is contained in ker(H^T) and FH^T is symmetric. Given a symmetric solution D0 and a complete kernel basis K, a symmetric zero-diagonal solution exists exactly when diag(D0) belongs to span{Ki entrywise Kj:i<=j}. Under the stated triangle Gram and margins, symmetry of FH^T and the row-degree congruence n-4 are automatic. The genuine243 fixture has rankF47, kernel dimension133 and full180-dimensional product span; all7290 small F/H systems and729 finite rank controls were independently checked.'
        limitations=['Field completion only: no binary D, integer degree, quadratic residual identity or target existence follows.','No universal full product-span or new adjacency-rank theorem;243 ranks are finite fixture observations.','Rook9 has empty residual and does not replace the nonempty243 control.','Existing nilpotent/rank overlap is disclosed, without novelty claim.'];ts=datetime.now(timezone.utc).isoformat()
        binding=dict(id='C-GF3-SYMMETRIC-HOLLOW-MIXED-COMPLETION',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,scope='Arbitrary finite GF3 matrices with the stated consistency hypotheses; conditional triangle consequences and explicitly finite controls.',assumptions=['All completion matrices are over GF(3).','K is a complete linearly independent basis of ker(F).','Triangle degree consequence additionally assumes the exact stated core Gram and row/cell-column margins.'],dependencies=[dict(id='C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION',revision=1,relation='uses_result'),dict(id='C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL',revision=1,relation='verification_dependency')],verifier='/root/structural_attack',producer='/root/state_literature_audit',method='Independent written linear-algebra proof, reverse-pivot field elimination and direct actual D coefficient systems, complete raw certificate products, genuine fixture identities and corrupt controls.',shared_components=['Frozen raw243/core fixtures and prior claim premises; Python standard-library integer arithmetic.','No producer or repository checker imports.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},limitations=limitations,artifact_availability='LOCAL_ONLY',availability_reason='Awaiting parent publication.',external_review=None,external_review_reason='No external review asserted.',created_at=ts,updated_at=ts)
        save(out/'claim_binding.json',binding);report=dict(status='INDEPENDENT_GF3_HOLLOW_RESIDUAL_CRITERION_PASS',created_at=ts,inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},small_direct_system_pairs=7290,rank_controls=729,genuine243=ranks,core_diagnostics=cores,corruptions_rejected=rejected,claim_id=binding['id'],claim_revision=1,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python=platform.python_version(),command=[sys.executable,*sys.argv],elapsed_seconds=time.perf_counter()-start,new_solver_calls=0,scope=binding['scope'],limitations=limitations);save(out/'summary.json',report);print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'),elapsed_seconds=report['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),inputs_sha256=pins));raise
if __name__=='__main__':main()
