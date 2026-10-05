"""Candidate exact GF3 residual-completion exploration, no producer imports."""
from pathlib import Path
from itertools import product, combinations_with_replacement
from datetime import datetime, timezone
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
ARCHIVE_COMMIT='85e705cc6c2a14d123120c93a847e30aaab1789e'
PINS={
B+'srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
B+'srg243_residual_fixture/adjacency243.json':'5c7c8268b7d62997b5c87a56b11fd673f3f80fcb029b83816179ee8127b8e0d3',
B+'independent_review/srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',
'docs/AUDIT_20260930_TARGET_MODULAR_RANKS.md':'c819ec41287a1a5394d84e2031b6cd2ba564ed8c9771082363dc46ad11a894ed',
'docs/AUDIT_20260930_FIVE_CORE_MODULAR_GRAM.md':'a22f72f34236c7b046aaf9f024bd124d9d808ae0e56ee23ab525472e87de270b',
'external_conway99_research/attempts/wave23-index-pranks/failed-routes.md':'1371323a35959482a888fd3eaf226995eaae99e05800cde889ad239dcccabc65',
'external_conway99_research/attempts/wave171-pq-centered-code/derivation.md':'0ff4280e782acccfb76e2ca093291be3e3a1c4ca08225ccb763b113c5ac286e3',
'external_conway99_research/attempts/wave171-pq-centered-code/failed-routes.md':'18f3afd2373111b9c1604a47e98f13184ecb1b74def86b93e5095def9c529196',
B+'connected_identity_cores/core_00.json':'3d4ad2d5b8ff92ca3d7761ac79e3651e306052897c3327b4eec87d7a85dabe81',
B+'connected_identity_cores/core_01.json':'23fb79efbc42fcaf7d54edb32311703be47fa96014a1c46ed00859a0753576e4',
B+'connected_identity_cores/core_02.json':'40c23054a9276039b0dc1320594f102ae65d06c8e2c819a31d6600c3ee279eeb',
B+'connected_identity_cores/core_03.json':'cdd61bb140888090f092af7bbc3dbc40399f8e06bb3b41781dcfba22f0f701f1',
B+'hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}

def need(x,msg):
    if not x:raise ValueError(msg)
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,separators=(',',':'),sort_keys=True);f.write('\n')
def mat(x):return np.array(x,dtype=np.int64)

def rref(x,width=None):
    a=mat(x).copy()%3
    if a.size==0:a=np.zeros((0,width or (a.shape[1] if a.ndim==2 else 0)),dtype=np.int64)
    m,n=a.shape;ps=[];r=0
    for j in range(n):
        inds=np.flatnonzero(a[r:,j])
        if not len(inds):continue
        q=r+int(inds[0]);a[[r,q]]=a[[q,r]];a[r]=(a[r]*int(a[r,j]))%3
        factors=a[:,j].copy();factors[r]=0;a=(a-factors[:,None]*a[r])%3;ps.append(j);r+=1
        if r==m:break
    return a,ps

def rank(x):return len(rref(x)[1])
def kernel(x):
    a,ps=rref(x);n=a.shape[1];free=[j for j in range(n) if j not in ps];rows=[]
    for j in free:
        v=np.zeros(n,dtype=np.int64);v[j]=1
        for i,p in enumerate(ps):v[p]=-a[i,j]%3
        rows.append(v)
    k=np.array(rows,dtype=np.int64).reshape((len(rows),n));need(np.all((mat(x)@k.T)%3==0),'literal nullspace multiplication');return k,dict(rank=len(ps),pivots=ps,rref=a[:len(ps)].tolist(),nullspace_basis=k.tolist())
def inspan(rows,v):return rank(np.vstack((rows,v)))==rank(rows)

def square_span(k):
    width=k.shape[1];basis=[];piv=[];indices=[];rawrows=[];attempts=0
    for i,j in combinations_with_replacement(range(len(k)),2):
        v=(k[i]*k[j])%3;original=v.copy();attempts+=1
        for b,p in zip(basis,piv):v=(v-v[p]*b)%3
        nz=np.flatnonzero(v)
        if len(nz):
            p=int(nz[0]);v=(v*int(v[p]))%3;basis.append(v);piv.append(p);indices.append([i,j]);rawrows.append(original.tolist())
            if len(basis)==width:break
    a=np.array(basis,dtype=np.int64).reshape((len(basis),width))
    need(rank(a)==len(basis),'square basis independence')
    return a,dict(rank=len(basis),width=width,products_examined=attempts,selected_product_indices=indices,selected_product_rows=rawrows,forward_basis=a.tolist(),full_span=len(basis)==width)

def consistency(F,H):
    left,_=kernel(F.T);compatible=bool(np.all((left@H)%3==0));s=(F@H.T)%3
    return compatible,bool(np.array_equal(s,s.T))

def symmetric_base(F,H):
    m=F.shape[1];k,sym=consistency(F,H);need(k and sym,'symmetric consistency')
    if not m:return np.zeros((0,0),dtype=np.int64),{}
    _,which=rref(F.T);W=F[which];T=H[which].T;r=len(which);_,piv=rref(W);free=[j for j in range(m) if j not in piv]
    P=np.column_stack([*list(W),*[np.eye(m,dtype=np.int64)[:,j] for j in free]])
    aug=np.column_stack((P,np.eye(m,dtype=np.int64)));rr,ps=rref(aug)
    need(ps[:m]==list(range(m)) and np.array_equal(rr[:,:m],np.eye(m,dtype=np.int64)),'basis invertible')
    inv=rr[:,m:];need(np.array_equal(P@inv%3,np.eye(m,dtype=np.int64)),'literal inverse')
    Z=np.zeros((m,m),dtype=np.int64);known=P.T@T%3;Z[:,:r]=known;Z[:r,:]=known.T
    need(np.array_equal(Z,Z.T),'congruence symmetry');D=inv.T@Z@inv%3
    need(np.array_equal(F@D%3,H%3) and np.array_equal(D,D.T),'constructed symmetric solution')
    return D,dict(selected_F_rows=which,basis=P.tolist(),basis_inverse=inv.tolist(),congruence_matrix=Z.tolist(),symmetric_solution=D.tolist())

def symmetric_matrices(m,hollow=False):
    pairs=[(i,j) for i in range(m) for j in range(i if not hollow else i+1,m)]
    for entries in product(range(3),repeat=len(pairs)):
        D=np.zeros((m,m),dtype=np.int64)
        for (i,j),v in zip(pairs,entries):D[i,j]=D[j,i]=v
        yield D

def controls():
    records=[];rankcases=0
    for vals in product(range(3),repeat=6):
        a=mat(vals).reshape(2,3);span={tuple((mat(c)@a%3).tolist()) for c in product(range(3),repeat=2)};need(len(span)==3**rank(a),'rank vs literal finite span');rankcases+=1
    for a,m in [(1,3),(2,2)]:
        syms=list(symmetric_matrices(m));hollows=list(symmetric_matrices(m,True))
        for entries in product(range(3),repeat=a*m):
            F=mat(entries).reshape(a,m);k,_=kernel(F);sq,_=square_span(k)
            image={tuple((F@D%3).flat):D for D in syms};zero={tuple((F@D%3).flat) for D in hollows}
            for hs in product(range(3),repeat=a*m):
                H=mat(hs).reshape(a,m);compat,sym=consistency(F,H);ordinary=compat and sym
                need(ordinary==(hs in image),'symmetric criterion vs actual D enumeration')
                pred=ordinary and inspan(sq,np.diag(image[hs]));actual=hs in zero;need(pred==actual,'hollow criterion vs actual D enumeration')
                if ordinary:
                    D,_=symmetric_base(F,H);need(inspan(sq,np.diag(D))==actual,'constructed D0 diagonal criterion')
                records.append(dict(shape=[a,m],F=list(entries),H=list(hs),kernel_compatible=compat,symmetry_compatible=sym,hollow_possible=actual))
    # Missing premises must each admit a generic false inference.
    generic=[]
    for name,F,H in [('missing_kernel',[[0,0]],[[1,0]]),('missing_symmetry',[[1,0],[0,1]],[[0,1],[0,0]]),('missing_diagonal',[[1,0]],[[1,0]])]:
        F=mat(F);H=mat(H);compat,sym=consistency(F,H);k,_=kernel(F);sq,_=square_span(k)
        diag=None
        if compat and sym:
            D,_=symmetric_base(F,H);diag=bool(inspan(sq,np.diag(D)))
        generic.append(dict(name=name,F=F.tolist(),H=H.tolist(),kernel_compatible=compat,symmetry_compatible=sym,diagonal_compatible=diag,not_a_graph_or_factor=True))
    need(not generic[0]['kernel_compatible'] and not generic[1]['symmetry_compatible'] and generic[2]['diagonal_compatible'] is False,'three distinct omitted-premise controls')
    return dict(complete_F_H_pairs=len(records),rank_controls=rankcases,records=records,omitted_premise_counterexamples=generic)

def run(out):
    start=time.monotonic();pins=dict(PINS)
    for p,h in pins.items():need(sha(ROOT/p)==h,'pinned input '+p)
    archive=subprocess.check_output(['git','-C','external_conway99_research','rev-parse','HEAD'],cwd=ROOT,text=True).strip();need(archive==ARCHIVE_COMMIT,'pinned archive commit')
    for p in [Path(__file__),Path(__file__).with_name('theory_20260930_gf3_hollow_residual_spec.md'),ROOT/'docs/DERIVATION_20260930_GF3_HOLLOW_RESIDUAL.md']:
        pins[key(p)]=sha(p)
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,inputs_sha256=pins,archive_commit=archive,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),limits=dict(cooperative_seconds=120,planning_memory_bytes=512*1024**2),native_calls=0,arithmetic='Integer int64 modulo3; no floating arithmetic.'))
    ctl=controls();save(out/'controls.json',ctl)
    blocks=read(ROOT/(B+'srg243_residual_fixture/triangle_blocks.json'));A=mat(read(ROOT/(B+'srg243_residual_fixture/adjacency243.json'))['adjacency']);C=mat(blocks['cubic_core60']);F=mat(blocks['factor60x180']);D=mat(blocks['residual180x180']);n=20;m=180
    need(np.array_equal(A@A,20*np.eye(243,dtype=np.int64)-A+2*np.ones((243,243),dtype=np.int64)),'genuine243 integer target identity')
    U=np.kron(np.eye(3,dtype=np.int64),np.ones((n,n),dtype=np.int64));G=n*np.eye(3*n,dtype=np.int64)-C-C@C+2*np.ones((3*n,3*n),dtype=np.int64)-U
    H=2*np.ones(F.shape,dtype=np.int64)-(np.eye(3*n,dtype=np.int64)+C)@F
    need(np.array_equal(F@F.T,G) and np.array_equal(F@D,H),'genuine exact Gram/mixed')
    need(np.array_equal(D@D+F.T@F,n*np.eye(m,dtype=np.int64)-D+2*np.ones((m,m),dtype=np.int64)),'genuine quadratic residual')
    need(np.all(F.sum(axis=1)==n-2) and all(np.all(F[i*n:(i+1)*n].sum(axis=0)==2) for i in range(3)),'literal genuine margins')
    need(np.array_equal(C@G,G@C),'core Gram commutation')
    ternF=F%3;ternH=H%3;K,kcert=kernel(ternF);sq,sqcert=square_span(K);D0,d0cert=symmetric_base(ternF,ternH)
    need(inspan(sq,np.diag(D0)),'genuine diagonal compatibility');need(np.all(D0.sum(axis=1)%3==(n-4)%3),'automatic field residual row degree')
    N=(A-np.eye(243,dtype=np.int64))%3;need(np.all(N@N%3==2) and np.all(N@N@N%3==0),'243 nilpotent identity, distinct target parameters')
    genuine=dict(parameters=[243,22,1,2],rank_F=rank(ternF),kernel_dimension=len(K),square_span_rank=len(sq),symmetric_completion=d0cert,kernel_certificate=kcert,square_span_certificate=sqcert,rank_A=rank(A),rank_A_minus_I=rank(N),rank_square=rank(N@N%3),integer_full_factor_and_residual_verified=True,automatic_degree_mod3=int((n-4)%3),Conway99=False)
    save(out/'genuine243.json',genuine)
    rook=mat([[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)])
    need(np.array_equal(rook@rook,2*np.eye(9,dtype=np.int64)-rook+2*np.ones((9,9),dtype=np.int64)),'rook9 identity');rookN=(rook-np.eye(9,dtype=np.int64))%3
    need(np.all(rookN@rookN%3==2) and np.all(rookN@rookN@rookN%3==0),'rook nilpotent identity')
    save(out/'rook9.json',dict(adjacency=rook.tolist(),parameters=[9,4,1,2],rank_A=rank(rook),rank_A_minus_I=rank(rookN),rank_square=rank(rookN@rookN%3),residual_dimension=0,nonempty_residual_control=False,Conway99=False))
    cores=[]
    for p in [B+'connected_identity_cores/core_'+f'{i:02d}'+'.json' for i in range(4)]+[B+'hadamard20_support/six_prism.json']:
        d=read(ROOT/p);core=mat(d.get('core_adjacency36',d.get('core_adjacency')));need(core.shape==(36,36),'rawcore36')
        R=np.kron(np.eye(3,dtype=np.int64),np.ones((1,12),dtype=np.int64));B39=np.block([[np.ones((3,3),dtype=np.int64)-np.eye(3,dtype=np.int64),R],[R.T,core]])
        cores.append(dict(path=p,rank_C_mod3=rank(core),rank_triangle39_mod3=rank(B39),rank_triangle39_plus_I_mod3=rank(B39+np.eye(39,dtype=np.int64)),factor_available=False,diagnostic_only=True))
    save(out/'core_diagnostics.json',dict(records=cores,scope='Finite raw core ranks only; no assumed full F or rank-completion obstruction.'))
    rejected=[]
    bad=K.copy();bad[0,0]=(bad[0,0]+1)%3;need(np.any(ternF@bad.T%3),'altered kernel control');rejected.append('changed_kernel_vector')
    bad=D0.copy();bad[0,1]=(bad[0,1]+1)%3;need(not np.array_equal(bad,bad.T),'nonsymmetric completion');rejected.append('nonsymmetric_completion')
    bad=D.copy();bad[0,0]=1;need(np.any(np.diag(bad)),'nonzero diagonal');rejected.append('changed_diagonal')
    bad=A.copy();bad[0,1]=1-bad[0,1];need(not np.array_equal(bad,bad.T) or not np.array_equal(bad@bad,20*np.eye(243,dtype=np.int64)-bad+2*np.ones((243,243),dtype=np.int64)),'graph corruption');rejected.append('changed_fixture_adjacency')
    save(out/'corruptions.json',dict(rejected=rejected))
    save(out/'overlap.json',dict(archive_commit=archive,existing=['Current target modular-rank derivation already establishes rank_F3(A)=45.', 'Pinned Wave23 explicitly gives rank_F3(A+I)=55.', 'Pinned Wave171 identifies its nilpotent triangle-block code with the earlier centered code; not a new endpoint contradiction.'],new_candidate_scope='General GF3 symmetric hollow mixed-completion criterion via ker(F) coordinatewise-product span; triangle symmetry/degree redundancy under stated margins.',novelty_claimed=False,whole_support_or_target_exclusion=False))
    need(time.monotonic()-start<120,'cooperative budget')
    summary=dict(status='CANDIDATE_GF3_HOLLOW_RESIDUAL_CRITERION_AND_FINITE_CONTROLS',inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},complete_small_F_H_pairs=ctl['complete_F_H_pairs'],rank_controls=ctl['rank_controls'],genuine243_rank_F=rank(ternF),genuine243_kernel_dimension=len(K),genuine243_square_span_rank=len(sq),genuine243_square_span_full=len(sq)==m,saved_core_diagnostics=len(cores),native_calls=0,solver_calls=0,independent_approval=False,target_resolution=False,artifact_availability='LOCAL_ONLY',shared_components=['NumPy int64 exact modular operations; raw fixtures and earlier reports as data, no producer or checker imports.'],scope='Conditional field-completion criterion plus finite controls/non-obstruction diagnostics. No binary/quadratic D, target construction, all-core rank or general nonexistence claim.',elapsed_seconds=time.monotonic()-start)
    save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256','shared_components','scope')}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    try:run(out)
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(__file__),independent_approval=False));raise
if __name__=='__main__':main()
