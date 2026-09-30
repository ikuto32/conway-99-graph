"""Candidate all-triple block descent: exact integer objective, no exclusion."""
import argparse,hashlib,json,platform,random,subprocess,sys,time
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import numpy as np
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
GATE=B/'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json'
FIX=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
SPEC=Path(__file__).with_name('theory_20260930_hadamard_all_triple_descent_spec.md')
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',FIX:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',GATE:'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88'}
VERSION='FIXED_L_FULL_GRAM_FROBENIUS_SQUARED_V1';SEEDS=[99023000,99023001,99023002,99023003]
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def tuple_tree(x):return tuple(tuple_tree(y) for y in x) if isinstance(x,list) else x
def literal_gram(f):
    rows=[{d for d,v in enumerate(row) if v} for row in f]
    return [[len(a&b) for b in rows] for a in rows]
def literal_score(f,target):return sum((v-target[a][b])**2 for a,row in enumerate(literal_gram(f)) for b,v in enumerate(row))
def exact_target(core):
    n=len(core)//3;nb=[{j for j,v in enumerate(row) if v} for row in core]
    return [[n*int(i==j)+2-core[i][j]-len(nb[i]&nb[j])-int(i//n==j//n) for j in range(3*n)] for i in range(3*n)]
class Engine:
    def __init__(self,raw,local):
        self.words=local['words'];self.triples=local['survivors'];self.target=np.array(raw['prescribed_Gram36'],dtype=np.int64)
        self.supports=sorted(set(tuple(c) for c in raw['support_columns']))
        self.columns=[[i for i,c in enumerate(raw['support_columns']) if tuple(c)==s] for s in self.supports]
        need(len(self.supports)==20 and all(len(v)==3 for v in self.columns),'twenty repeated supports')
        self.maps=[np.array([12*f+a for f in range(3) for a in s],dtype=np.int64) for s in self.supports]
        self.i,self.j=np.triu_indices(18);self.weights=np.where(self.i==self.j,1,2).astype(np.int64)
        w=np.zeros((90,18),dtype=np.int64)
        for k,word in enumerate(self.words):
            for a,f in enumerate(word):w[k,6*f+a]=1
        wg=w[:,self.i]*w[:,self.j]
        self.contrib=wg[np.array(self.triples,dtype=np.int64)].sum(axis=1,dtype=np.int64)
        self.norm=(self.contrib*self.contrib)@self.weights
        need(self.contrib.shape==(31110,171) and self.contrib.min()>=0 and self.contrib.max()<=3,'literal contribution shape/bounds')
    def matrix(self,k):
        m=np.zeros((18,18),dtype=np.int64);m[self.i,self.j]=self.contrib[k];m[self.j,self.i]=self.contrib[k];return m
    def factor(self,indices):
        need(len(indices)==20 and all(type(k)is int and 0<=k<31110 for k in indices),'all-triple state domain')
        f=[[0]*60 for _ in range(36)]
        for g,k in enumerate(indices):
            for d,w in zip(self.columns[g],self.triples[k]):
                for pos,a in enumerate(self.supports[g]):f[12*self.words[w][pos]+a][d]=1
        return f
    def residual(self,indices,target):
        a=np.zeros((36,36),dtype=np.int64)
        for g,k in enumerate(indices):ix=np.ix_(self.maps[g],self.maps[g]);a[ix]+=self.matrix(k)
        return a-target
    def scores(self,residual,g,old):
        r=residual[np.ix_(self.maps[g],self.maps[g])][self.i,self.j]
        without=r-self.contrib[old]
        outside=int(np.sum(residual*residual,dtype=np.int64))-int((r*r)@self.weights)
        return outside+int((without*without)@self.weights)+self.norm+2*(self.contrib@(self.weights*without))
    def start(self,seed,target):
        rng=random.Random(seed);indices=[rng.randrange(31110) for _ in range(20)];score=int(np.sum(self.residual(indices,target)**2))
        return dict(seed=seed,indices=indices,best_indices=indices[:],score=score,best_score=score,rng=rng.getstate(),order=[],cursor=0,sweeps=0,updates=0,options_evaluated=0,kicks=0,sweep_start_best=score)
    def step(self,s,target):
        rng=random.Random();rng.setstate(tuple_tree(s['rng']));r=self.residual(s['indices'],target)
        need(int(np.sum(r*r))==s['score'],'resume exact current score')
        if s['cursor']==len(s['order']):s['order']=list(range(20));rng.shuffle(s['order']);s['cursor']=0;s['sweep_start_best']=s['best_score']
        g=s['order'][s['cursor']];old=s['indices'][g];scores=self.scores(r,g,old);minimum=int(scores.min());choices=np.flatnonzero(scores==minimum);new=int(choices[rng.randrange(len(choices))])
        s['indices'][g]=new;s['score']=minimum;s['cursor']+=1;s['updates']+=1;s['options_evaluated']+=31110
        if minimum<s['best_score']:s['best_score']=minimum;s['best_indices']=s['indices'][:]
        event=dict(update=s['updates'],group=g,old=old,new=new,score_after_coordinate=minimum,best_score=s['best_score'],minimum_ties=len(choices),kicks=[])
        if s['cursor']==20:
            s['sweeps']+=1
            if s['best_score']!=0 and s['best_score']==s['sweep_start_best']:
                for h in rng.sample(range(20),2):
                    prev=s['indices'][h];replacement=rng.randrange(31110);s['indices'][h]=replacement;event['kicks'].append(dict(group=h,old=prev,new=replacement))
                rr=self.residual(s['indices'],target);s['score']=int(np.sum(rr*rr));s['kicks']+=1
        s['rng']=rng.getstate();event['score_after_kicks']=s['score'];return event
def controls(e,raw):
    fixture=read(FIX);target=exact_target(fixture['cubic_core60']);f=fixture['factor60x180']
    need(literal_score(f,target)==0,'genuine243 perfect-score control')
    bad=[r[:] for r in f];bad[0][0]^=1;need(literal_score(bad,target)>0,'flipped genuine fixture rejected')
    rng=random.Random(120099);local_ids=[0,31109]+rng.sample(range(31110),30);rows=[]
    for k in local_ids:
        lf=[[int(e.words[w][a]==f) for w in e.triples[k]] for f in range(3) for a in range(6)]
        expected=literal_gram(lf);need(e.matrix(k).tolist()==expected,'literal local contribution control');rows.append(dict(index=k,gram=expected))
    checks=[]
    for trial in range(4):
        indices=[rng.randrange(31110) for _ in range(20)];r=e.residual(indices,e.target);need(int(np.sum(r*r))==literal_score(e.factor(indices),e.target.tolist()),'literal initial research score')
        g=rng.randrange(20);scores=e.scores(r,g,indices[g])
        for new in [indices[g]]+rng.sample(range(31110),12):
            changed=indices[:];changed[g]=new;exact=literal_score(e.factor(changed),e.target.tolist());need(int(scores[new])==exact,'all-coordinate prediction control');checks.append(dict(indices=indices,group=g,new=new,score=exact))
    perfect=[rng.randrange(31110) for _ in range(20)];synthetic=np.array(literal_gram(e.factor(perfect)),dtype=np.int64)
    need(literal_score(e.factor(perfect),synthetic.tolist())==0,'synthetic perfect own-Gram positive')
    for g in [0,7,19]:need(int(e.scores(e.residual(perfect,synthetic),g,perfect[g]).min())==0,'no negative objective at perfect control')
    full=e.start(9181,synthetic);split=e.start(9181,synthetic)
    for _ in range(64):e.step(full,synthetic)
    for _ in range(23):e.step(split,synthetic)
    split=json.loads(json.dumps(split))
    for _ in range(41):e.step(split,synthetic)
    need(json.loads(json.dumps(full))==json.loads(json.dumps(split)),'actual serialized23+41 versus64 resume')
    corrupted=[]
    for label,state in [('wrong_score',{**full,'score':full['score']+1}),('bad_index',{**full,'indices':[31110]+full['indices'][1:]})]:
        try:
            e.factor(state['indices']);e.step(state,synthetic)
        except (ValueError,IndexError):corrupted.append(label)
        else:raise ValueError('accepted corrupted checkpoint')
    return dict(genuine_positive='Authenticated SRG243 factor, not research99.',generic_positive_error=0,flipped_fixture_rejected=True,local_contribution_checks=rows,replacement_checks=checks,synthetic_perfect_indices=perfect,synthetic_target=synthetic.tolist(),synthetic_is_research_Gram=False,resume=dict(whole=full,split=split,steps=[23,41,64],pass_equal=True),corrupted_checkpoints_rejected=corrupted,independent_approval=False)
def raw_object(e,indices,expected,target):
    f=e.factor(indices);gram=literal_gram(f);score=sum((gram[a][b]-int(target[a,b]))**2 for a in range(36) for b in range(36));need(score==expected,'saved raw exact objective')
    cols=[{a for a in range(36) if f[a][d]} for d in range(60)];violations=[dict(columns=[i,j],overlap=len(cols[i]&cols[j])) for i,j in combinations(range(60),2) if len(cols[i]&cols[j])>2]
    need(all(sum(f[a][d] for a in range(12*g,12*g+12))==2 for g in range(3) for d in range(60)),'all fibre column margins')
    return dict(factor36x60=f,local_catalogue_indices=indices,objective_version=VERSION,exact_score=score,full_Gram=gram,row_sums=[sum(row) for row in f],outside_cap_violations=violations,full_Gram_valid=score==0,all_outside_caps_valid=not violations,residual_D=None,residual_D_reason='Not encoded or constructed.',target_graph=False,independent_approval=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    try:
        for p,h in PINS.items():need(sha(p)==h,'input identity');pins[key(p)]=h
        gate=read(GATE);need(gate['status']=='INDEPENDENT_HADAMARD_TRIPLICATE_PROJECTIONS_PASS' and gate['inputs_sha256'][key(LOCAL)]==PINS[LOCAL],'complete local-domain independent gate')
        for p in [GATE,Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=sha(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,tqdm=__import__('tqdm').__version__,platform=platform.platform(),processor=platform.processor(),inputs_sha256=pins,objective_version=VERSION,seeds=SEEDS,limits=dict(total_wall_seconds=120,chain_wall_seconds=24,maximum_updates_per_chain=2000,automatic_retry=False),research_scope='One fixed L; all31110 options at every group, no exception-count restriction.',independent_approval=False))
        raw=read(RAW);need(exact_target(raw['core_adjacency'])==raw['prescribed_Gram36'],'raw core target derivation');e=Engine(raw,read(LOCAL));np.save(out/'contributions_u8.npy',e.contrib.astype(np.uint8),allow_pickle=False)
        save(out/'model.json',dict(groups=[dict(support=list(s),columns=c,global_rows=m.tolist()) for s,c,m in zip(e.supports,e.columns,e.maps)],local_upper_pairs=list(map(list,zip(e.i.tolist(),e.j.tolist()))),weights=e.weights.tolist(),target=e.target.tolist(),contributions_path=key(out/'contributions_u8.npy'),contributions_sha256=sha(out/'contributions_u8.npy'),domain_size=31110,group_count=20,objective_version=VERSION))
        save(out/'controls.json',controls(e,raw));need(time.monotonic()-start<120,'calibration consumed pilot budget')
        results=[];zero=False
        for ci,seed in enumerate(SEEDS):
            if time.monotonic()-start>=120:break
            folder=out/f'chain_{ci:02d}';folder.mkdir();s=e.start(seed,e.target);chain_start=time.monotonic();checkpoints=[]
            def checkpoint(label):
                cp=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_sha256=pins[key(Path(__file__))],model_sha256=sha(out/'model.json'),elapsed_total_seconds=time.monotonic()-start,state=s,current=raw_object(e,s['indices'],s['score'],e.target),best=raw_object(e,s['best_indices'],s['best_score'],e.target),independent_approval=False)
                p=folder/f'checkpoint_{label}.json';save(p,cp);checkpoints.append(dict(path=key(p),sha256=sha(p)))
            checkpoint('initial')
            with (folder/'updates.jsonl').open('x',encoding='utf-8',newline='\n') as log,tqdm(total=2000,desc=f'all-triple chain{ci}',unit='coordinate',mininterval=3,file=sys.stderr) as bar:
                while s['updates']<2000 and time.monotonic()-chain_start<24 and time.monotonic()-start<120:
                    event=e.step(s,e.target);log.write(json.dumps(event,separators=(',',':'))+'\n');bar.update(1)
                    if s['cursor']==20:checkpoint(f"sweep_{s['sweeps']:05d}")
                    if s['best_score']==0:zero=True;break
            checkpoint('final');best=raw_object(e,s['best_indices'],s['best_score'],e.target);save(folder/'best_factor.json',best)
            result=dict(chain=ci,seed=seed,updates=s['updates'],candidate_replacements_evaluated=s['options_evaluated'],sweeps=s['sweeps'],kicks=s['kicks'],current_score=s['score'],best_score=s['best_score'],best_factor_path=key(folder/'best_factor.json'),best_factor_sha256=sha(folder/'best_factor.json'),best_outside_cap_violations=len(best['outside_cap_violations']),checkpoints=checkpoints,elapsed_seconds=time.monotonic()-chain_start,stop_reason='GRAM_ZERO_PENDING_INDEPENDENT_REVIEW' if zero else 'UPDATE_LIMIT' if s['updates']==2000 else 'COOPERATIVE_TIME_LIMIT');save(folder/'summary.json',result);results.append(result)
            if zero:break
        elapsed=time.monotonic()-start
        save(out/'summary.json',dict(status='CANDIDATE_ALL_TRIPLE_DESCENT_COMPLETED',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.rglob('*') if p.is_file()},chains=results,selected_chains=4,completed_chains=len(results),unattempted_seeds=SEEDS[len(results):],objective_version=VERSION,best_score=min((r['best_score'] for r in results),default=None),candidate_replacements_evaluated=sum(r['candidate_replacements_evaluated'] for r in results),elapsed_seconds=elapsed,budget_overrun_seconds=max(0,elapsed-120),exact_Gram_zero=zero,independent_approval=False,target_resolution=False,solver_calls=0,scope='One fixed Hadamard support; heuristic search of all local triples; zero is only Gram equality until independent object checking; positive scores exclude nothing.'))
        print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),best_score=min((r['best_score'] for r in results),default=None),elapsed_seconds=elapsed)))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
