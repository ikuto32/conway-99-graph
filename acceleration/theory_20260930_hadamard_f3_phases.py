"""Candidate exact phase linear screen; no independent approval or solver."""
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json'
PROJECTION=B/'20260930_independent_review/hadamard_parity_support_cuts_sat/independent_projection.json'
GATE=PROJECTION.parent/'summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',PROJECTION:'f43ad5f79d6fc8c8f6825f52d0140a07852a873207642b4edb7c035cb5ed4a8c',GATE:'02ae20d479a0d2589c02f435e2a8fdd781ec0459b60095d130b68b5f2721a04a'}
def need(ok,why):
    if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def dot(a,b):return sum(x*y for x,y in zip(a,b,strict=True))%3
def rref(matrix,n):
    a=[r[:]for r in matrix];m=len(a);transform=[[int(i==j)for j in range(m)]for i in range(m)];ops=[];pivots=[];r=0
    for c in range(n):
        pivot=next((i for i in range(r,m)if a[i][c]),None)
        if pivot is None:continue
        if pivot!=r:a[r],a[pivot]=a[pivot],a[r];transform[r],transform[pivot]=transform[pivot],transform[r];ops.append(['swap',r,pivot])
        if a[r][c]==2:a[r]=[(2*v)%3 for v in a[r]];transform[r]=[(2*v)%3 for v in transform[r]];ops.append(['scale',r,2])
        for i in range(m):
            if i==r or not a[i][c]:continue
            v=a[i][c];a[i]=[(x-v*y)%3 for x,y in zip(a[i],a[r],strict=True)];transform[i]=[(x-v*y)%3 for x,y in zip(transform[i],transform[r],strict=True)];ops.append(['subtract',i,r,v])
        pivots.append(c);r+=1
        if r==m:break
    free=[c for c in range(n)if c not in pivots];basis=[]
    for c in free:
        v=[0]*n;v[c]=1
        for i,p in enumerate(pivots):v[p]=(-a[i][c])%3
        basis.append(v)
    return dict(rref=a,row_transform=transform,operations=ops,pivots=pivots,free_columns=free,nullspace_basis=basis,rank=len(pivots),nullity=len(free))
def verify_linear(a,cert):
    n=len(a[0]);m=len(a);need(len(cert['rref'])==m and all(len(r)==n for r in cert['rref']),'RREF dimensions')
    need(all(sum(cert['row_transform'][i][j]*a[j][k]for j in range(m))%3==cert['rref'][i][k]for i in range(m)for k in range(n)),'complete transform times matrix identity')
    need(all(dot(row,v)==0 for row in a for v in cert['nullspace_basis']),'all nullspace products zero')
    need(cert['rank']+cert['nullity']==n and len(cert['nullspace_basis'])==cert['nullity'],'rank-nullity')
    need(all(cert['nullspace_basis'][i][j]==int(i==k)for i in range(cert['nullity'])for k,j in enumerate(cert['free_columns'])),'basis free-coordinate identity')

def controls():
    compositions=[]
    for sa,ta,sb,tb,x in product((1,2),range(3),(1,2),range(3),range(3)):
        g=(sa*x+ta)%3;e=sb*sa%3;u=(tb-e*ta)%3
        need((e*g+u)%3==(sb*x+tb)%3,'relative map orientation')
        compositions.append([sa,ta,sb,tb,x,e,u])
    need(len(compositions)==108,'all affine permutation pairs and letters')
    target=[[2-int(i==j)for j in range(3)]for i in range(3)];pairs=[]
    for ts in product(range(3),repeat=5):
        signs=[2,2,2,1,1]
        matrix=[[sum((s*i+t)%3==j for s,t in zip(signs,ts,strict=True))for j in range(3)]for i in range(3)]
        linear=sum(ts[:3])%3==sum(ts[3:])%3==0
        full=linear and len(set(ts[:3]))==3 and all(ts[i]!=0 for i in (3,4))
        need((matrix==target)==full,'all243 pair-phase exact Gram characterization')
        pairs.append(dict(phases=list(ts),linear=linear,exact_Gram=matrix==target))
    need(sum(x['exact_Gram']for x in pairs)==12,'twelve exact pair-phase configurations')
    patterns=[p for p in product(range(2),repeat=6)if p[0]==0 and sum(p)==3];localcases=[]
    for p in patterns:
        signs=[1 if v==0 else 2 for v in p];valid=[]
        for rest in product(range(3),repeat=5):
            ts=(0,*rest);good=all(len({ts[i]for i in range(6)if signs[i]==s})==3 for s in(1,2))
            words=[[(signs[i]*x+ts[i])%3 for i in range(6)]for x in range(3)]
            balanced=all(w.count(g)==2 for w in words for g in range(3))and len({(signs[i],ts[i])for i in range(6)})==6
            need(good==balanced,'literal local mixed maps and word balance')
            if good:valid.append(list(ts))
        need(len(valid)==12,'twelve gauged local mixed choices');localcases.append(dict(pattern=list(p),phases=valid))
    tiny=0
    for flat in product(range(3),repeat=6):
        a=[list(flat[:3]),list(flat[3:])];cert=rref(a,3);verify_linear(a,cert)
        expected=2 if any((a[0][i]*a[1][j]-a[0][j]*a[1][i])%3 for i,j in combinations(range(3),2))else int(any(flat))
        need(cert['rank']==expected,'729 tiny exact minor ranks');tiny+=1
    corrupt=[]
    bad=rref([[1,1,0],[0,1,1]],3);bad['nullspace_basis'][0][0]=(bad['nullspace_basis'][0][0]+1)%3
    try:verify_linear([[1,1,0],[0,1,1]],bad)
    except ValueError:corrupt.append('changed_nullspace_vector')
    else:raise ValueError('corrupted basis accepted')
    need(any(((sb*x+tb)-(sb*sa*(sa*x+ta)+tb+sb*sa*ta))%3 for sa,ta,sb,tb,x in product((1,2),range(3),(1,2),range(3),range(3))),'wrong relative intercept plus sign falsified');corrupt.append('wrong_relative_intercept_sign')
    return dict(affine_orientation_cases=compositions,pair_phase_cases=pairs,local_gauged_phase_domains=localcases,tiny_minor_rank_cases=tiny,corruptions_rejected=corrupt,scope='Exact finite controls; no full research factor.')

def build(raw,projection):
    L=raw['L'];supports=[[a for a in range(12)if L[a][d]]for d in range(60)];groups=[]
    for s in supports:
        if s not in groups:groups.append(s)
    need(len(groups)==20 and all(supports.count(s)==3 for s in groups),'twenty groups of three raw columns')
    patterns=projection['selected_group_parity_patterns'];need(len(patterns)==20 and all(p[0]==0 and sum(p)==3 for p in patterns),'chosen all-mixed normalized parity branch')
    signs=[[1 if p==0 else 2 for p in row]for row in patterns]
    variables=[dict(index=6*g+i,group=g,position=i,coordinate=a,sign=signs[g][i])for g,s in enumerate(groups)for i,a in enumerate(s)]
    rows=[];inequalities=[]
    def form(terms):
        v=[0]*120
        for i,c in terms:v[i]=(v[i]+c)%3
        return v
    def equation(kind,terms,**meta):rows.append(dict(index=len(rows),kind=kind,coefficients=form(terms),rhs=0,**meta))
    def nonzero(kind,vector,**meta):inequalities.append(dict(index=len(inequalities),kind=kind,coefficients=vector,required='nonzero in GF(3)',**meta))
    for g in range(20):equation('column_gauge',[(6*g,1)],group=g)
    for g in range(20):
        for s in(1,2):
            pos=[i for i in range(6)if signs[g][i]==s];need(len(pos)==3,'three coordinates per sign')
            equation('local_same_sign_sum',[(6*g+i,1)for i in pos],group=g,sign=s,positions=pos)
            for i,j in combinations(pos,2):nonzero('local_same_sign_distinct',form([(6*g+j,1),(6*g+i,-1)]),group=g,positions=[i,j])
    pairrecords=[]
    for a,b in combinations(range(12),2):
        if a^1==b:continue
        inc=[g for g,s in enumerate(groups)if a in s and b in s];need(len(inc)==5,'five shared groups')
        relative=[]
        for g in inc:
            i,j=groups[g].index(a),groups[g].index(b);e=signs[g][i]*signs[g][j]%3;v=form([(6*g+j,1),(6*g+i,-e)])
            relative.append(dict(group=g,positions=[i,j],relative_sign=e,relative_phase_coefficients=v))
        odd=[r for r in relative if r['relative_sign']==2];even=[r for r in relative if r['relative_sign']==1]
        need(len(odd)==3 and len(even)==2,'three odd and two even relative maps')
        for name,part in [('odd',odd),('even',even)]:
            terms=[(i,c)for r in part for i,c in enumerate(r['relative_phase_coefficients'])if c]
            equation('pair_'+name+'_phase_sum',terms,coordinates=[a,b],groups=[r['group']for r in part])
        for x,y in combinations(odd,2):nonzero('odd_relative_phases_distinct',[(a-b)%3 for a,b in zip(x['relative_phase_coefficients'],y['relative_phase_coefficients'],strict=True)],coordinates=[a,b],groups=[x['group'],y['group']])
        for r in even:nonzero('even_relative_phase_nonzero',r['relative_phase_coefficients'],coordinates=[a,b],group=r['group'])
        pairrecords.append(dict(coordinates=[a,b],relative_maps=relative))
    need(len(rows)==180 and len(pairrecords)==60 and len(inequalities)==420,'complete frozen linear/inequality populations')
    return dict(field=3,variables=variables,groups=groups,patterns=patterns,signs=signs,rows=rows,pair_records=pairrecords,necessary_nonzero_functionals=inequalities,all_balanced_parity_branches_covered=False,one_fixed_parity_branch=True,Ycaps_encoded=False,residual_D_encoded=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    try:
        for p,d in PINS.items():need(h(p)==d,'input identity '+key(p));pins[key(p)]=d
        need(read(GATE)['status']=='INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_SAT_OBJECT_PASS'and read(GATE)['outputs_sha256'][key(PROJECTION)]==PINS[PROJECTION],'raw parity object independently bound')
        for p in[Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_f3_phases_spec.md'),ROOT/'docs/DERIVATION_20260930_HADAMARD_F3_PHASES.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=h(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,limits=dict(seconds=60,solver_calls=0,nonlinear_enumeration=0),question='Does exact necessary phase linear algebra force a required nonzero form to zero?',status='PREREGISTERED_CANDIDATE_PRODUCER'))
        save(out/'controls.json',controls())
        system=build(read(RAW),read(PROJECTION));save(out/'phase_system.json',system);matrix=[r['coefficients']for r in system['rows']];cert=rref(matrix,120);verify_linear(matrix,cert);save(out/'linear_certificate.json',cert)
        screens=[];obstructions=[]
        for condition in system['necessary_nonzero_functionals']:
            vector=condition['coefficients'];restricted=[dot(vector,v)for v in cert['nullspace_basis']];record=dict(inequality_index=condition['index'],restricted_coefficients=restricted,identically_zero=not any(restricted));screens.append(record)
            if not any(restricted):
                work=vector[:];weights=[0]*180
                for i,p in enumerate(cert['pivots']):
                    c=work[p]
                    if not c:continue
                    work=[(x-c*y)%3 for x,y in zip(work,cert['rref'][i],strict=True)];weights=[(x+c*y)%3 for x,y in zip(weights,cert['row_transform'][i],strict=True)]
                need(not any(work)and all(sum(weights[j]*matrix[j][i]for j in range(180))%3==vector[i]for i in range(120)),'exact zero-functional row-space certificate')
                obstructions.append(dict(condition=condition,row_combination=weights,identity='row_combination times equation matrix equals required-nonzero functional, over GF(3)'))
        save(out/'inequality_screen.json',dict(screens=screens,obstructions=obstructions))
        need(time.monotonic()-start<60,'exact linear experiment time limit')
        summary=dict(status='CANDIDATE_GF3_PHASE_LINEAR_SCREEN_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()},variables=120,equations=180,rank=cert['rank'],nullity=cert['nullity'],necessary_inequalities=420,identically_zero_required_functionals=len(obstructions),candidate_branch_exclusion=bool(obstructions),factor_constructed=False,solver_calls=0,nonlinear_enumeration=0,independent_approval=False,elapsed_seconds=time.monotonic()-start,scope='Only the one saved all-mixed balanced parity branch on the fixed support; no all-branch or target conclusion.',claim_id='C-FIXED-HADAMARD-SECOND-PARITY-GF3-PHASE-SCREEN',claim_revision=1,claim_status='CANDIDATE')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in['inputs_sha256','outputs_sha256']}))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=h(__file__)));raise

if __name__=='__main__':main()
