"""Exact one-outside-vertex domains for frozen two-star local witnesses."""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'acceleration/results/20260930_joint_two_star_matching/run02'
OUT=ROOT/'acceleration/results/20260930_two_star_outside_domains/run01'
def h(p):return sha256(p.read_bytes()).hexdigest()
def save(name,obj):
    with(OUT/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def bits(a):return[sum(x<<i for i,x in enumerate(row))for row in a]
def members(x):
    while x:
        t=x&-x;yield t.bit_length()-1;x^=t
def add(r,x,y):r[x]|=1<<y;r[y]|=1<<x
def violation(r,x,y):
    pairs={(min(x,y),max(x,y))}
    pairs.update((min(x,z),max(x,z))for z in members(r[y])if z!=x)
    pairs.update((min(y,z),max(y,z))for z in members(r[x])if z!=y)
    for a,b in sorted(pairs):
        common=r[a]&r[b];adj=r[a]>>b&1
        if common.bit_count()+adj>2:return {'pair':[a,b],'common':list(members(common)),'adjacent':adj,'sum':common.bit_count()+adj}
    return None
def patterns(left,right,p,q):
    for e in (0,1):
        if p<e or q<e:continue
        for a in combinations(left,p-e):
            for b in combinations(right,q-e):yield e,a,b
def check_pattern(base,z,w,pattern):
    e,a,b=pattern;r=base[:];neighbors=([w]if e else[])+list(a)+list(b)
    for y in neighbors:
        add(r,z,y);bad=violation(r,z,y)
        if bad:return bad
    return None
def controls():
    assert len(list(patterns([0,1],[2,3],1,1)))==5
    # Actual rook3 is a positive SRG(9,4,1,2) control for the same local identities.
    a=[[int(i!=j and(i//3==j//3 or i%3==j%3))for j in range(9)]for i in range(9)]
    base=[row[:]for row in a]
    for z in [5,8]:
        for y in range(9):base[z][y]=base[y][z]=0
    r=bits(base);accepted=[]
    for z in [5,8]:
        pat=(1,(3 if z==5 else 6,),(4 if z==5 else 7,))
        assert pat in list(patterns([3,6],[4,7],2,2))
        assert check_pattern(r,z,2,pat)is None;accepted.append({'z':z,'pattern':pat})
    k=[0]*5
    for x,y in combinations(range(4),2):add(k,x,y)
    bad=violation(k,0,1);assert bad and bad['sum']==3
    corrupt=dict(bad,common=[])
    assert len(corrupt['common'])+corrupt['adjacent']!=corrupt['sum']
    return{'five_tiny_patterns':True,'rook3_raw_positive_patterns':accepted,'K4_negative_cap':bad,'corrupt_common_count_rejected':True}
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    cases=[0,8,16,24];inputs=[INPUT/f'case_{i:02d}.json'for i in cases]
    inputs +=[INPUT/'population.json',INPUT/'summary.json',Path(__file__).resolve(),ROOT/'uv.lock',ROOT/'pyproject.toml']
    save('manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'python':platform.python_version(),'question':'Does any outside vertex have no exact pair-cap-compatible assignment into the two frozen center neighborhoods?','selection':{'case_ids':cases,'outside_vertices':'All outer vertices not in either center neighborhood or the centers, ascending label index. Stop at first empty domain.'},'success':'Complete finite assignment coverage and cap witness for every rejected pattern; empty domain excludes this fixed partial local configuration only.','limits':{'seconds':60,'stop_first_empty':True},'numerical_thresholds':None,'numerical_thresholds_null_reason':'Exact integer and Boolean computation only.','inputs_sha256':{p.relative_to(ROOT).as_posix():h(p)for p in inputs}})
    save('controls.json',controls());start=time.monotonic();records=[];stop=False
    for case in cases:
        raw=json.loads((INPUT/f'case_{case:02d}.json').read_bytes());a=raw['partial_known_edge_adjacency'];r=bits(a);meta=raw['metadata'];u,v,w=(meta[k]for k in ['u','v','w'])
        left=[x for x in meta['A']if x>=15];right=[x for x in meta['B']if x>=15]
        assert len(left)==len(right)==10 and not set(left)&set(right)
        outside=[z for z in range(15,99)if z not in[u,v]and not(r[u]>>z&1)and not(r[v]>>z&1)]
        assert len(outside)==61
        for z in outside:
            if time.monotonic()-start>60:
                records.append({'case':case,'z':z,'status':'NOT_STARTED_RESOURCE_CAP'});stop=True;break
            p=2-(r[u]&r[z]).bit_count();q=2-(r[v]&r[z]).bit_count()
            rejected=[];survivors=[];total=0
            for pattern in patterns(left,right,p,q):
                total+=1;bad=check_pattern(r,z,w,pattern)
                if bad:rejected.append({'pattern':pattern,'cap':bad})
                else:survivors.append(pattern)
            record={'case':case,'z':z,'deficits':[p,q],'universe':{'shared_vertex':w,'left':left,'right':right,'rule':'e in{0,1}, |L|=p-e, |R|=q-e; all subsets enumerated exactly'},'patterns':total,'survivor_count':len(survivors),'rejection_count':len(rejected),'surviving_patterns':survivors,'status':'CANDIDATE_EMPTY_DOMAIN_EXCLUSION'if not survivors else'NONEMPTY_LOCAL_DOMAIN'}
            name=f'case_{case:02d}_z{z:02d}.json';save(name,record)
            records.append({k:record[k]for k in ['case','z','patterns','survivor_count','rejection_count','status']})
            if not survivors:
                cert={'scope':'Every target containing the fixed raw partial known-edge graph would require one of these patterns at this outside vertex; every pattern violates a known-edge common-plus-adjacency cap.','base_path':(INPUT/f'case_{case:02d}.json').relative_to(ROOT).as_posix(),'base_sha256':h(INPUT/f'case_{case:02d}.json'),'domain':record,'all_rejections':rejected,'target_resolution':'NONE','status':'CANDIDATE_PENDING_INDEPENDENT_COMPLETE_COVERAGE_CHECK'}
                data=(json.dumps(cert,indent=2)+'\n').encode();(OUT/'empty_domain_certificate.json').write_bytes(data)
                with(OUT/'empty_domain_certificate.json.gz').open('xb')as f:f.write(gzip.compress(data,mtime=0))
                stop=True;break
            save(f'checkpoint_{case:02d}_{z:02d}.json',{'completed':records,'next_after':[case,z]})
        if stop:break
    save('summary.json',{'status':'CANDIDATE_TWO_STAR_OUTSIDE_DOMAIN_SCREEN','timestamp':datetime.now(timezone.utc).isoformat(),'selected_local_witnesses':cases,'completed_domains':sum(r['status']!='NOT_STARTED_RESOURCE_CAP'for r in records),'empty_domains':sum(r['status']=='CANDIDATE_EMPTY_DOMAIN_EXCLUSION'for r in records),'patterns_enumerated':sum(r.get('patterns',0)for r in records),'surviving_patterns':sum(r.get('survivor_count',0)for r in records),'records':records,'wall_seconds':time.monotonic()-start,'independent_verification':None,'independent_verification_null_reason':'Producer experiment; raw certificate needs separate checker.','limitations':['A nonempty domain is not simultaneous consistency of outside vertices.','An empty domain excludes only a frozen matching-augmented pair of stars, not every matching for those stars.','No target automorphism assumed.','No whole-family exclusion or target resolution.'],'solver_calls':0,'artifact_hashes':{p.name:h(p)for p in sorted(OUT.iterdir())}})
    s=json.loads((OUT/'summary.json').read_bytes());print(json.dumps({k:s[k]for k in ['completed_domains','empty_domains','patterns_enumerated','surviving_patterns','wall_seconds']}))
if __name__=='__main__':main()
