"""Exact sampled three-matching CSP, with full failed search trees; producer only."""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_joint_two_star_matching/run01'
MODEL=ROOT/'acceleration/results/20260930_unrestricted_full99_cnf/model.json'
SINGLE=ROOT/'acceleration/results/20260930_unrestricted_star_matching_redundancy/run01/records.json'
SEED=2026093002
def need(ok,msg):
    if not ok: raise ValueError(msg)
def h(p):
    q=sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):q.update(b)
    return q.hexdigest()
def save(name,obj):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,indent=2);f.write('\n')
def quotas(center,star):
    need(len(star)==len(set(star))==12 and center not in star,'twelve distinct nonself labels')
    need(all(a<b and a//2!=b//2 for a,b in star),'label validity')
    need([sum(s in e for e in star)for s in range(14)]==[2-int(s in center)-int((s^1)in center)for s in range(14)],'fourteen exact symbol quotas')
def sample_v(rng):
    center=(4,6);fixed=(0,2)
    deg=[2-int(s in center)-int((s^1)in center)-int(s in fixed)for s in range(14)]
    stubs=[s for s,d in enumerate(deg)for _ in range(d)]
    for attempt in range(1,100001):
        rng.shuffle(stubs);star=[fixed]+[tuple(sorted(stubs[i:i+2]))for i in range(0,len(stubs),2)]
        if len(set(star))!=12 or center in star or any(a//2==b//2 for a,b in star):continue
        quotas(center,star);return sorted(star),attempt
    raise RuntimeError('v star generation cap')
def scaffold(labels):
    rows=[0]*99
    def add(x,y):rows[x]|=1<<y;rows[y]|=1<<x
    for s in range(14):add(0,s+1)
    for s in range(0,14,2):add(s+1,s+2)
    for i,label in enumerate(labels):
        for s in label:add(15+i,1+s)
    return rows
def members(bits):
    while bits:
        low=bits&-bits;yield low.bit_length()-1;bits^=low
def violation(rows,edge=None):
    pairs=set(combinations(range(99),2)) if edge is None else set()
    if edge:
        x,y=edge;pairs.add(tuple(sorted(edge)))
        pairs.update(tuple(sorted((x,z)))for z in members(rows[y])if z!=x)
        pairs.update(tuple(sorted((y,z)))for z in members(rows[x])if z!=y)
    for x,y in sorted(pairs):
        common=rows[x]&rows[y];adj=rows[x]>>y&1
        if common.bit_count()+adj>2:return {'pair':[x,y],'common':list(members(common)),'adjacent':adj,'sum':common.bit_count()+adj}
    return None
def add(rows,x,y):rows[x]|=1<<y;rows[y]|=1<<x
def remove(rows,x,y):rows[x]^=1<<y;rows[y]^=1<<x
def allowed(rows,x,y):
    if rows[x]>>y&1:return None
    add(rows,x,y);bad=violation(rows,(x,y));remove(rows,x,y);return bad
def prepare(labels,stars):
    index={lab:15+i for i,lab in enumerate(labels)};u=index[(0,2)];v=index[(4,6)]
    su,sv=stars;quotas((0,2),su);quotas((4,6),sv)
    need((4,6)in su and(0,2)in sv,'reciprocal anchor')
    common=set(su)&set(sv);need(len(common)==1,'central edge exact common count')
    wlab=next(iter(common));need(not set(wlab)&{0,2,4,6},'triangle label disjointness')
    rows=scaffold(labels)
    for label in su:add(rows,u,index[label])
    for label in sv:add(rows,v,index[label])
    w=index[wlab];a=set(members(rows[u]))-{v,w};b=set(members(rows[v]))-{u,w}
    need(len(a)==len(b)==12 and not a&b,'two disjoint twelve-fibres')
    groups=[];fixed=[]
    for name,kind,left,right in [('A','internal',a,a),('B','internal',b,b),('AB','cross',a,b)]:
        present=[(x,y)for x in sorted(left)for y in sorted(right)if(kind=='cross'or x<y)and rows[x]>>y&1]
        ld={x:sum(rows[x]>>y&1 for y in right)for x in left};rd={y:sum(rows[y]>>x&1 for x in left)for y in right}
        need(max(ld.values())<=1 and max(rd.values())<=1,'fixed block degree cap')
        l=tuple(x for x in sorted(left)if ld[x]==0);r=tuple(y for y in sorted(right)if rd[y]==0)
        need(len(l)==len(r)==8,'eight unmatched vertices per side')
        groups.append({'name':name,'kind':kind,'left':l,'right':r});fixed.append({'name':name,'edges':present})
    need(violation(rows)is None,'initial known-edge pair caps')
    return rows,groups,{'u':u,'v':v,'w':w,'A':sorted(a),'B':sorted(b),'fixed_matching_edges':fixed}
def final_checks(rows,meta):
    need(violation(rows)is None,'all partial pair caps')
    need(all(row.bit_count()<=14 for row in rows),'partial degrees')
    closed={meta['u'],meta['v'],meta['w'],*meta['A'],*meta['B']}
    for u in [meta['u'],meta['v']]:
        need(rows[u].bit_count()==14,'degree14 center')
        for y in sorted((closed|set(range(15)))-{u}):need((rows[u]&rows[y]).bit_count()+(rows[u]>>y&1)==2,'center equality in frozen domain')
    return {'all_pair_caps':4851,'degree_caps':99,'closed_edge_neighborhood_vertices':len(closed),'center_equalities_per_center':len((closed|set(range(15)))-{meta['u']})}
class Limit(Exception):pass
def search(rows,groups,deadline,budget,stats,chosen=()):
    if time.monotonic()>deadline or stats['nodes']>=budget:raise Limit()
    stats['nodes']+=1
    candidates=[]
    for i,g in enumerate(groups):
        for x in g['left']:
            partners=[y for y in(g['left']if g['kind']=='internal'else g['right'])if y!=x]
            options=[(y,allowed(rows,x,y))for y in partners]
            candidates.append((sum(bad is None for _,bad in options),len(options),i,x,options))
    if not candidates:return {'kind':'SUCCESS','chosen_edges':list(chosen),'rows':rows[:]},None
    _,_,i,x,options=min(candidates,key=lambda t:t[:4]);g=groups[i]
    tree={'kind':'BRANCH','group':g['name'],'vertex':x,'partners':[y for y,_ in options],'branches':[]}
    for y,bad in options:
        if bad is not None:tree['branches'].append({'edge':[x,y],'reject':bad});stats['cap_prunes']+=1;continue
        add(rows,x,y)
        new=[dict(t)for t in groups];new[i]['left']=tuple(v for v in g['left']if v!=x and(g['kind']!='internal'or v!=y))
        new[i]['right']=new[i]['left']if g['kind']=='internal'else tuple(v for v in g['right']if v!=y)
        success,child=search(rows,new,deadline,budget,stats,chosen+((g['name'],x,y),))
        remove(rows,x,y)
        if success is not None:return success,None
        tree['branches'].append({'edge':[x,y],'child':child})
    return None,tree
def controls(labels):
    r=scaffold(labels);need(violation(r)is None,'positive root scaffold')
    r2=r[:];add(r2,15,16);bad=violation(r2);need(bad is not None,'deliberate shared-inner adjacency corruption')
    toy=[0]*99;stats={'nodes':0,'cap_prunes':0}
    yes,_=search(toy,[{'name':'K4','kind':'internal','left':(15,16,17,18),'right':(15,16,17,18)}],time.monotonic()+2,100,stats)
    need(yes is not None and len(yes['chosen_edges'])==2,'K4 positive')
    no,tree=search(toy,[{'name':'singleton','kind':'internal','left':(15,),'right':(15,)}],time.monotonic()+2,100,stats)
    need(no is None and tree['partners']==[],'impossible singleton')
    rejected=False
    try:quotas((0,2),[(4,6)]*12)
    except ValueError:rejected=True
    need(rejected,'corrupt quotas')
    return {'scaffold_positive':True,'K4_matching_positive':True,'singleton_matching_negative':True,'corrupt_partial_cap_witness':bad,'duplicate_quota_rejected':True}
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    need(h(MODEL)=='77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e','model hash')
    model=json.loads(MODEL.read_bytes());labels=list(map(tuple,model['outer_labels']))
    files=[MODEL,SINGLE,Path(__file__).resolve(),ROOT/'docs/NEXT_20260930_JOINT_TWO_STAR_MATCHING.md',ROOT/'docs/THEORY_20260917_MATCHING_PAIR.md',ROOT/'external_conway99_research/attempts/wave151-triangle-root-factor/derivation.md',ROOT/'uv.lock',ROOT/'pyproject.toml']
    save('manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'python':platform.python_version(),'seed':SEED,'scope':'Sampled exact three-matching relaxation for two full adjacent stars; not global target feasibility.','limits':{'seconds':60,'nodes':1000000,'cases':32},'inputs_sha256':{p.relative_to(ROOT).as_posix():h(p)for p in files}})
    calibrated=controls(labels);save('controls.json',calibrated)
    rng=random.Random(SEED);population=[]
    source=json.loads(SINGLE.read_bytes())
    for old in source:
        if old['number']>=8:continue
        su=list(map(tuple,old['star_labels']));attempts=0
        for pair_attempt in range(1,100001):
            sv,n=sample_v(rng);attempts+=n;common=set(su)&set(sv)
            if len(common)!=1 or set(next(iter(common)))&{0,2,4,6}:continue
            _,_,meta=prepare(labels,(su,sv));break
        else:raise RuntimeError('pair sampling cap')
        population.append({'id':len(population),'branch':old['branch'],'source_number':old['number'],'u_star':su,'v_star':sv,'v_stub_attempts':attempts,'pair_attempts':pair_attempt,'metadata':meta})
    save('population.json',population)
    start=time.monotonic();deadline=start+60;records=[];stats={'nodes':0,'cap_prunes':0}
    for case in population:
        rows,groups,meta=prepare(labels,(list(map(tuple,case['u_star'])),list(map(tuple,case['v_star']))));before=dict(stats)
        try:success,tree=search(rows,groups,deadline,1000000,stats)
        except Limit:
            records.append({'id':case['id'],'status':'INCOMPLETE_RESOURCE_CAP'});break
        if success:
            checked=final_checks(success['rows'],meta)
            artifact={'status':'CANDIDATE_LOCAL_MATCHING_WITNESS','case_id':case['id'],'metadata':meta,'initial_groups':groups,'chosen_edges':success['chosen_edges'],'partial_known_edge_adjacency':[[row>>j&1 for j in range(99)]for row in success['rows']],'checks':checked}
        else:artifact={'status':'CANDIDATE_EXACT_TWO_STAR_EXCLUSION','case_id':case['id'],'metadata':meta,'initial_groups':groups,'complete_enumeration_tree':tree}
        name=f'case_{case["id"]:02d}.json';save(name,artifact)
        records.append({'id':case['id'],'status':artifact['status'],'artifact':name,'sha256':h(OUT/name),'nodes':stats['nodes']-before['nodes'],'cap_prunes':stats['cap_prunes']-before['cap_prunes']})
        save(f'checkpoint_{case["id"]:02d}.json',{'completed':records,'stats':stats,'next_case':case['id']+1})
    save('summary.json',{'status':'CANDIDATE_JOINT_TWO_STAR_MATCHING_PILOT','timestamp':datetime.now(timezone.utc).isoformat(),'frozen_population':len(population),'attempted':len(records),'completed':sum(r['status']!='INCOMPLETE_RESOURCE_CAP'for r in records),'local_witnesses':sum(r['status']=='CANDIDATE_LOCAL_MATCHING_WITNESS'for r in records),'conditional_exclusions':sum(r['status']=='CANDIDATE_EXACT_TWO_STAR_EXCLUSION'for r in records),'incomplete':sum(r['status']=='INCOMPLETE_RESOURCE_CAP'for r in records),'records':records,'stats':stats,'wall_seconds':time.monotonic()-start,'independent_verification':None,'independent_verification_null_reason':'Producer discovery and controls only; independent complete raw certificate review pending.','solver_calls':0,'limitations':['Every exclusion is only one fixed pair of stars, never the anchor family or target.','Positive local witnesses do not satisfy all outer-to-center equalities, only the declared closed-neighborhood and inner subset.','No target automorphism assumed; no quotient used.','Overall search coverage: UNKNOWN; no validated denominator.'],'artifact_hashes':{p.name:h(p)for p in sorted(OUT.iterdir())}})
    print(json.dumps({k:v for k,v in json.loads((OUT/'summary.json').read_bytes()).items()if k in ['status','completed','local_witnesses','conditional_exclusions','incomplete','stats','wall_seconds']}))
if __name__=='__main__':main()
