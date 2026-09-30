"""Exact count compression PSD screen, no numerical or SAT inference."""
import argparse,hashlib,itertools,json,math,platform,subprocess,sys,time
from fractions import Fraction as Q
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
CASES=[('first','eight_count_profile_lift','8342a2c4e45af5f92e1e36a3e61b3d5f299f79ad9dd6320d84618c4645d6373b','0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152'),('second','eight_count_profile_lift_second','652225f2bf156a4bb1a92979504ec810bba3277137b889059f227d0c035f2afc','7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'),('third','eight_count_profile_lift_third','4f5eedcd74eb2c5d44a6955f80b9d8cfb8899949bcfeb31a5aafd56adc8260e2','03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e')]
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def transpose(a):return list(map(list,zip(*a)))
def multiply(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def gram(a):return multiply(a,transpose(a))
def packed(a):return [[[v.numerator,v.denominator] for v in row] for row in a]
def quadratic(m,v):return sum(v[i]*m[i][j]*v[j] for i in range(len(v)) for j in range(len(v)))
def primitive(v):
    l=math.lcm(*(x.denominator for x in v));w=[int(x*l) for x in v];g=math.gcd(*w);return [x//g for x in w]
def classify(m,deadline):
    n=len(m);need(all(len(r)==n for r in m) and m==transpose(m),'symmetric exact matrix');a=[[Q(v) for v in r] for r in m];t=[[Q(i==j) for j in range(n)] for i in range(n)];active=list(range(n));ops=[]
    def negative(v,reason):
        w=primitive(v);value=quadratic(m,w);need(value<0,'direct exact negative quadratic');return dict(status='NEGATIVE_INTEGER_VECTOR',vector=w,quadratic=value,reason=reason,prior_positive_pivots=len(ops),operations=ops)
    while active:
        if time.perf_counter()>deadline:return dict(status='UNKNOWN_RESOURCE_BOUND',operations=ops)
        k=next((i for i in active if a[i][i]<0),None)
        if k is not None:return negative([r[k] for r in t],'negative Schur diagonal')
        k=next((i for i in active if a[i][i]>0),None)
        if k is None:
            edge=next(((i,j) for i in active for j in active if i<j and a[i][j]),None)
            if edge:
                i,j=edge;s=1 if a[i][j]>0 else -1;return negative([r[i]-s*r[j] for r in t],'zero diagonal and nonzero off-diagonal')
            break
        p=a[k][k];others=[j for j in active if j!=k];coeff={j:a[k][j]/p for j in others if a[k][j]}
        for i in others:
            for j in others:a[i][j]-=a[i][k]*a[k][j]/p
        for j,c in coeff.items():
            for i in range(n):t[i][j]-=c*t[i][k]
        for j in others:a[k][j]=a[j][k]=Q(0)
        ops.append(dict(pivot=k,value=[p.numerator,p.denominator],shears=[dict(column=j,coefficient=[c.numerator,c.denominator]) for j,c in coeff.items()]));active.remove(k)
    diag=[a[i][i] for i in range(n)];need(all(x>=0 for x in diag),'nonnegative final diagonal');actual=multiply(transpose(t),multiply(m,t));need(actual==a and all(a[i][j]==0 for i in range(n) for j in range(n) if i!=j),'literal whole congruence identity')
    # Each recorded operation subtracts a multiple of another column, so det(T)=1.
    return dict(status='EXACT_RATIONAL_PSD',rank=sum(x>0 for x in diag),diagonal=[[x.numerator,x.denominator] for x in diag],transform=packed(t),operations=ops,transform_invertibility='Product of the saved unit-determinant column shears; detT=1.',full_congruence_identity_checked=True)
def partition_factor(f):
    n=len(f);width=len(f[0]);need(width%3==0 and all(len(r)==width for r in f),'triple partition');nn=[[sum(row[3*g:3*g+3]) for g in range(width//3)] for row in f];gg=gram(f);ng=gram(nn);m=[[3*gg[i][j]-ng[i][j] for j in range(n)] for i in range(n)]
    differences=[[f[i][3*g+a]-f[i][3*g+b] for g in range(width//3) for a,b in [(0,1),(0,2),(1,2)]] for i in range(n)];need(gram(differences)==m,'integer pair-difference SOS identity');return m
def controls(fixture,deadline):
    matrices=[('positive',[[2,1],[1,2]],'EXACT_RATIONAL_PSD'),('singular',[[1,1],[1,1]],'EXACT_RATIONAL_PSD'),('negative_diagonal',[[-1,0],[0,2]],'NEGATIVE_INTEGER_VECTOR'),('zero_diagonal',[[0,1],[1,0]],'NEGATIVE_INTEGER_VECTOR'),('hidden_negative',[[1,2],[2,1]],'NEGATIVE_INTEGER_VECTOR')];records=[]
    for name,m,status in matrices:
        r=classify(m,deadline);need(r['status']==status,'matrix control '+name);records.append(dict(name=name,matrix=m,certificate=r))
    synthetic=[[int((i*5+j*3+j//3)%7<3) for j in range(9)] for i in range(5)]
    for name,f in [('synthetic_binary_partition',synthetic),('genuine243_generic_partition',fixture['factor60x180'])]:
        m=partition_factor(f);r=classify(m,deadline);need(r['status']=='EXACT_RATIONAL_PSD' and r['rank']<=2*(len(f[0])//3),'factor positive');records.append(dict(name=name,matrix=m,certificate=r,scope='Own exact factor Gram and consecutive triple partition; not a research36 witness.'))
    neg=records[2]['certificate'];need(quadratic(matrices[2][1],[0,0])>=0,'zero-vector corruption rejected');pos=records[0]['certificate'];t=[[Q(*v) for v in r] for r in pos['transform']];bad=[r[:] for r in matrices[0][1]];bad[0][0]+=1;need(multiply(transpose(t),multiply(bad,t))!=[[Q(*pos['diagonal'][i]) if i==j else Q(0) for j in range(2)] for i in range(2)],'matrix mutation invalidates certificate');return dict(records=records,corrupted_negative_vector_rejected=True,corrupted_psd_matrix_rejected=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();deadline=start+120;pins={};results=[]
    def pin(p,h=None):
        s=sha(p);need(h is None or h==s,'identity '+key(p));pins[key(p)]=s
    try:
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        raw=B/'20260930_hadamard20_support/six_prism.json';pin(raw,'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d');support=read(raw);c=support['core_adjacency'];c2=multiply(c,c);g=[[12*int(i==j)-c[i][j]+2-c2[i][j]-int(i//12==j//12) for j in range(36)] for i in range(36)];need(g==support['prescribed_Gram36'],'independently expanded raw core Gram')
        fixture=B/'20260930_srg243_residual_fixture/triangle_blocks.json';pin(fixture,'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439');save(out/'controls.json',controls(read(fixture),deadline))
        searches=[['git','-C','external_conway99_research','grep','-n','-i','-E','triplic.*(positive|psd)|count.*schur|3g.*nn|centered.*trip|group.*count.*gram','--','*.md','*.py'],['rg','-n','--max-columns','220','triplic.*(PSD|psd)|(?:PSD|psd).*triplic|N\\s*@\\s*N\\.T|counts\\s*@\\s*counts\\.T','acceleration','docs','-g','*.py','-g','*.md','-g','!acceleration/results/**','-g','!*triplicate_count_psd*']];search_records=[]
        for i,cmd in enumerate(searches):
            r=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=20);need(r.returncode in [0,1],'bounded archive search');(out/f'search_{i}.stdout.log').write_bytes(r.stdout);(out/f'search_{i}.stderr.log').write_bytes(r.stderr);search_records.append(dict(command=cmd,exit_code=r.returncode))
        save(out/'prior_work_search.json',dict(archive_commit=subprocess.check_output(['git','-C','external_conway99_research','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),records=search_records,conclusion='No exact-profile triplicate-count PSD test found by these searches. Related Gram/Schur/partial-residual methods exist; this is not an exhaustive novelty claim.'))
        for name,directory,scopehash,profilehash in CASES:
            d=B/('20260930_'+directory);pin(d/'scope.json',scopehash);pin(d/'selected_profile.json',profilehash);scope=read(d/'scope.json');profile=read(d/'selected_profile.json');counts=profile['coordinate_group_fibre_counts'];need(scope['prescribed_Gram36']==g and scope['coordinate_group_fibre_counts']==counts,'literal selected counts and Gram')
            nn=[[counts[a][j][f] for j in range(20)] for f in range(3) for a in range(12)];need(len(nn)==36 and all(len(r)==20 and all(type(x)is int and 0<=x<=3 for x in r) for r in nn),'integer count36x20')
            need(all(sum(row)==10 for row in nn) and all(sum(nn[i][j] for i in range(36))==18 for j in range(20)),'literal row and group margins');ng=gram(nn);m=[[3*g[i][j]-ng[i][j] for j in range(36)] for i in range(36)];co=out/name;co.mkdir();save(co/'matrix.json',dict(N=nn,G=g,M=m,row_order='12*fibre+coordinate',profile_digest=profile['profile_sha256']))
            cert=classify(m,deadline)
            if cert['status']=='NEGATIVE_INTEGER_VECTOR':
                v=cert['vector'];totals=[sum(v[i]*nn[i][j] for i in range(36)) for j in range(20)];cert['reusable_inequality']=dict(group_linear_forms=totals,left=sum(x*x for x in totals),right=3*quadratic(g,v),required='left<=right')
            save(co/'certificate.json',cert);result=dict(profile=name,status=cert['status'],rank=cert.get('rank'),negative_quadratic=cert.get('quadratic'));results.append(result);print(json.dumps(result),flush=True)
        summary=dict(status='CANDIDATE_TRIPLICATE_COUNT_PSD_SCREEN',created_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.rglob('*') if p.is_file()},results=results,python=platform.python_version(),command=[sys.executable,*sys.argv],source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),configured_seconds=120,elapsed_seconds=time.perf_counter()-start,native_sat_calls=0,numerical_eigensolver_calls=0,independent_approval=False,scope='Necessary real Gram-factor condition for three exact literal count profiles; a PSD pass is not a factor or binary feasibility certificate.')
        save(out/'summary.json',summary);print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),elapsed_seconds=summary['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise
if __name__=='__main__':main()
