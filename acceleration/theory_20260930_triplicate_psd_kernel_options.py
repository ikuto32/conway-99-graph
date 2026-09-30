"""Candidate exact PSD-kernel local-option screen; no solver calls."""
import argparse,copy,gzip,hashlib,itertools,json,math,platform,subprocess,sys,time
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';I=B/'20260930_independent_review';D=I/'triplicate_count_psd'
PINS={D/'summary.json':'1217ea22d037c24be3039c29687e8e0b126f3fe122186687ecaee8065351a4f4',B/'20260930_hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',B/'20260930_hadamard_triplicate_counts/local_triples.json':'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',B/'20260930_srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439'}
CASES=[('first','count_master_sat_outcome','0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152'),('second','count_master_eight_orbit_cut_sat_outcome','7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'),('third','count_master_partial_cut_sat_outcome','03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e')]
def need(ok,m):
    if not ok:raise ValueError(m)
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def gzsave(p,x):
    with p.open('xb')as f:
        with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0)as g:g.write((json.dumps(x,separators=(',',':'))+'\n').encode())
def tr(a):return list(map(list,zip(*a)))
def mm(a,b):return [[sum(x*y for x,y in zip(r,c))for c in zip(*b)]for r in a]
def gram(a):return mm(a,tr(a))
def primitive(v):
    l=math.lcm(*(Q(x).denominator for x in v));w=[int(Q(x)*l)for x in v];g=math.gcd(*w);need(g>0,'nonzero basis vector');w=[x//g for x in w]
    return [-x for x in w]if next(x for x in w if x)<0 else w
def rref(a):
    w=[[Q(x)for x in row]for row in a];n=len(w[0]);k=0;ps=[]
    for j in range(n):
        z=next((i for i in range(k,len(w))if w[i][j]),None)
        if z is None:continue
        w[k],w[z]=w[z],w[k];d=w[k][j];w[k]=[x/d for x in w[k]]
        for i in range(len(w)):
            if i!=k and w[i][j]:
                d=w[i][j];w[i]=[x-d*y for x,y in zip(w[i],w[k])]
        ps.append(j);k+=1
        if k==len(w):break
    return w[:k],ps
def kernel(a):
    r,ps=rref(a);basis=[]
    for j in range(len(a[0])):
        if j in ps:continue
        v=[Q(i==j)for i in range(len(a[0]))]
        for i,p in enumerate(ps):v[p]=-r[i][j]
        v=primitive(v);need(all(sum(x*y for x,y in zip(row,v))==0 for row in a),'literal full nullvector');basis.append(v)
    return len(ps),basis
def spansame(a,b):return len(rref(a)[1])==len(rref(b)[1])==len(rref(a+b)[1])
def matrix(g,n):return [[3*g[i][j]-sum(x*y for x,y in zip(n[i],n[j]))for j in range(len(g))]for i in range(len(g))]
def projections(basis,rows):return [[sum(v[i]for i in col)for col in rows]for v in basis]
def residues(proj):return [[x[0]-x[1],x[0]-x[2],x[1]-x[2]]for x in proj]
def factor_control(f,order):
    a=[[r[j]for j in order]for r in f];n=[[sum(row[j:j+3])for j in range(0,len(order),3)]for row in a];m=matrix(gram(a),n);dif=[[row[j+p]-row[j+q]for j in range(0,len(order),3)for p,q in[(0,1),(0,2),(1,2)]]for row in a];need(gram(dif)==m,'literal generic SOS');rank,k=kernel(m);dots=mm(k,dif)if k else[];need(all(v==0 for row in dots for v in row),'generic kernel projections')
    return dict(rows=len(f),columns=len(order),order=order,rank=rank,nullity=len(k),integer_nullspace=k,all_pair_difference_projections=dots,own_Gram=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        v=sha(p);need(h is None or h==v,'pin '+key(p));pins[key(p)]=v
    def timecheck():need(time.perf_counter()-start<120,'120-second cooperative bound')
    try:
        for p,h in PINS.items():pin(p,h)
        for p in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        gate=read(D/'summary.json');need(gate['status']=='INDEPENDENT_TRIPLICATE_COUNT_PSD_PASS','independent PSD gate')
        for name,h in gate['outputs_sha256'].items():pin(ROOT/name,h)
        save(out/'manifest.json',dict(inputs_sha256=pins,created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],configured_seconds=120,selection='Exactly first, second, third literal count profiles; complete initial domains.',native_calls=0))
        prior=[ROOT/'acceleration/audit_20260930_hadamard_gram_affine_gf2.py',ROOT/'acceleration/theory_20260930_triplicate_count_psd.py',ROOT/'docs/AUDIT_20260930_TRIPLICATE_COUNT_PSD.md']
        for p in prior:pin(p)
        save(out/'prior_work.json',dict(examined=[dict(path=key(p),sha256=sha(p))for p in prior],comparison='The GF2 screen concerns affine combinations of whole local Gram contributions modulo2. This candidate uses real SOS nullvectors on individual column differences. The earlier three-profile PSD pass supplied exact nullspaces but did not test every local option. No novelty assertion.'))
        raw=read(B/'20260930_hadamard20_support/six_prism.json');C=raw['core_adjacency'];G=[[12*int(i==j)+2-C[i][j]-sum(C[i][k]*C[k][j]for k in range(36))-int(i//12==j//12)for j in range(36)]for i in range(36)];need(G==raw['prescribed_Gram36'],'raw Gram');groups=[]
        for j in range(60):
            s=[a for a in range(12)if raw['L'][a][j]]
            if s not in groups:groups.append(s)
        need(len(groups)==20,'twenty groups');cat=read(B/'20260930_hadamard_triplicate_counts/local_triples.json');words=cat['words'];triples=cat['survivors'];need(words==[list(w)for w in itertools.product(range(3),repeat=6)if all(w.count(f)==2 for f in range(3))],'all90 local words');classes={}
        for i,t in enumerate(triples):classes.setdefault(tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3)),[]).append(i)
        N0=[[int(a in s)for s in groups]for f in range(3)for a in range(12)];M0=matrix(G,N0);rank0,K0=kernel(M0);baseline=dict(N=N0,M=M0,rank=rank0,nullity=len(K0),integer_nullspace=K0,N_rank=len(rref(N0)[1]),G_rank=len(rref(G)[1]));save(out/'balanced_baseline.json',baseline)
        word_records=[]
        for gi,s in enumerate(groups):
            dots=[[sum(v[12*f+a]for a,f in zip(s,w))for v in K0]for w in words];word_records.append(dict(group=gi,support=s,projections_by_word=dots,constant_across_all90=all(x==dots[0]for x in dots)))
        gzsave(out/'baseline_all_word_projections.json.gz',word_records);all_word_constant=all(r['constant_across_all90']for r in word_records);timecheck()
        controls=[];fixture=read(B/'20260930_srg243_residual_fixture/triangle_blocks.json')['factor60x180']
        for name,order in [('consecutive',list(range(180))),('reversed',list(reversed(range(180)))),('permuted',[(7*j+11)%180 for j in range(180)])]:controls.append(dict(name='genuine243_'+name,record=factor_control(fixture,order)));timecheck()
        for i in range(16):
            f=[[((i+3*r+5*c+r*c)%7)-2 for c in range(9)]for r in range(5)];controls.append(dict(name='integer_partition_'+str(i),record=factor_control(f,list(range(9)))))
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,IndexError,KeyError):rejected.append(name)
            else:raise ValueError('corruption accepted '+name)
        bad=K0[0][:];bad[0]+=1;reject('nullvector_mutation',lambda:need(all(sum(x*y for x,y in zip(row,bad))==0 for row in M0),'changed nullvector'))
        bm=copy.deepcopy(M0);nz=next(i for i,x in enumerate(K0[0])if x);bm[nz][nz]+=1;reject('matrix_mutation',lambda:need(all(sum(x*y for x,y in zip(row,K0[0]))==0 for row in bm),'changed M'))
        results=[]
        for name,folder,h in CASES:
            p=I/folder/'independent_count_profile.json';pin(p,h);profile=read(p);counts=profile['coordinate_group_fibre_counts'];N=[[counts[a][g][f]for g in range(20)]for f in range(3)for a in range(12)];M=matrix(G,N);checked=read(D/(name+'_exact_check.json'));need(checked['source_profile_sha256']==h and checked['matrix']['M']==M and checked['matrix']['N']==N,'approved exact profile matrices');basis=[primitive([Q(*x)for x in row])for row in checked['certificate_check']['nullspace']];rank,own=kernel(M);need(rank==22 and len(basis)==14 and all(all(sum(x*y for x,y in zip(row,v))==0 for row in M)for v in basis)and spansame(basis,own),'complete independently approved integer kernel');samebase=spansame(basis,K0)
            records=[];sizes=[];retained=[]
            for gi,s in enumerate(groups):
                signature=tuple(counts[a][gi][f]for a in s for f in range(3));ids=classes[signature];need(ids==profile['local_survivor_indices_by_group'][gi],'complete original count class');live=[]
                for local_index in ids:
                    t=triples[local_index];cols=[[12*f+a for a,f in zip(s,words[w])]for w in t];proj=projections(basis,cols);res=residues(proj);ok=all(x==0 for row in res for x in row)
                    if ok:live.append(local_index)
                    records.append(dict(group=gi,local_survivor_index=local_index,word_indices=t,column_rows=cols,integer_kernel_projections=proj,pair_difference_residuals=res,passes=ok))
                sizes.append(len(ids));retained.append(live)
            need(sum(sizes)==len(records),'all per-option records');caseout=out/name;caseout.mkdir();gzsave(caseout/'all_option_residuals.json.gz',records);save(caseout/'kernel_and_domains.json',dict(integer_nullspace=basis,independently_computed_integer_nullspace=own,rank=rank,same_kernel_as_balanced_baseline=samebase,initial_domain_sizes=sizes,retained_local_survivor_indices=retained,empty_groups=[g for g,r in enumerate(retained)if not r]))
            damaged=copy.deepcopy(records[0]);damaged['pair_difference_residuals'][0][0]+=1;reject(name+'_saved_residual_mutation',lambda damaged=damaged:need(damaged['pair_difference_residuals']==residues(projections(basis,damaged['column_rows'])),'raw residual replay'))
            badids=profile['local_survivor_indices_by_group'][0][:-1];reject(name+'_missing_initial_option',lambda badids=badids:need(badids==classes[tuple(counts[a][0][f]for a in groups[0]for f in range(3))],'exact class'))
            result=dict(profile=name,rank=rank,nullity=len(basis),same_kernel_as_balanced_baseline=samebase,initial_options=len(records),retained_options=sum(map(len,retained)),removed_options=len(records)-sum(map(len,retained)),empty_groups=[g for g,r in enumerate(retained)if not r]);results.append(result);print(json.dumps(result),flush=True);timecheck()
        save(out/'controls.json',dict(positive_controls=controls,corruptions_rejected=rejected,research_factor_positive=False));summary=dict(status='CANDIDATE_TRIPLICATE_PSD_KERNEL_OPTION_SCREEN_COMPLETE',created_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},baseline_rank=rank0,baseline_nullity=len(K0),baseline_N_rank=baseline['N_rank'],G_rank=baseline['G_rank'],all20_by90_baseline_word_projections_constant=all_word_constant,results=results,total_options=sum(r['initial_options']for r in results),total_removed=sum(r['removed_options']for r in results),configured_seconds=120,elapsed_seconds=time.perf_counter()-start,python=platform.python_version(),command=[sys.executable,*sys.argv],source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),native_calls=0,independent_approval=False,scope='Three literal profiles, complete initial domains and balanced-baseline kernel word test. Necessary local SOS screen only; no factor or unrestricted-profile inference.');save(out/'summary.json',summary);print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),elapsed_seconds=summary['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start));raise
if __name__=='__main__':main()
