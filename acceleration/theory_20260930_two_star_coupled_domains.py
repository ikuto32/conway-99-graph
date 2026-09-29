"""Bounded witness search coupling all outside domains; no exclusion without proof."""
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_two_star_coupled_domains/run01'
BASE=ROOT/'acceleration/results/20260930_joint_two_star_matching/run02/case_00.json'
DOM=ROOT/'acceleration/results/20260930_two_star_outside_domains/run01'
HELPER=ROOT/'acceleration/theory_20260930_two_star_outside_domains.py'
SEED=2026093003
def h(p):return sha256(p.read_bytes()).hexdigest()
def save(name,obj):
    with(OUT/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def load_helper():
    spec=importlib.util.spec_from_file_location('frozen_domain_producer',HELPER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
class Limit(Exception):pass
def main():
    OUT.mkdir(parents=True,exist_ok=False);helper=load_helper()
    controls=helper.controls();raw=json.loads(BASE.read_bytes());meta=raw['metadata'];r=helper.bits(raw['partial_known_edge_adjacency']);w=meta['w']
    files=sorted(DOM.glob('case_00_z*.json'));domains=[json.loads(p.read_bytes())for p in files]
    assert len(domains)==61 and all(x['survivor_count']>0 for x in domains)
    domains.sort(key=lambda x:(x['survivor_count'],x['z']))
    rng=random.Random(SEED)
    for d in domains:rng.shuffle(d['surviving_patterns'])
    save('manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'python':platform.python_version(),'seed':SEED,'question':'Can one frozen three-matching witness extend by61 coupled outside patterns satisfying all centered common-neighbor equations and all known pair/degree caps?','selection':'Only case00; variables sorted by original domain size then vertex; each domain deterministically shuffled. Depth-first exhaustive branches until a witness or resource cap.','limits':{'seconds':45,'nodes':20000},'shared_components':['Frozen own outside-domain producer reused for bitset operations, cap predicate and controls; this is discovery, not independent verification.'],'inputs_sha256':{p.relative_to(ROOT).as_posix():h(p)for p in [BASE,HELPER,Path(__file__).resolve(),ROOT/'uv.lock',*files]}})
    save('controls.json',controls);save('ordered_domains.json',domains)
    start=time.monotonic();deadline=start+45;stats={'nodes':0,'patterns_attempted':0,'cap_rejections':0,'degree_rejections':0,'max_depth':0};best=[];choice=[];result=None
    def apply(z,pat):
        e,a,b=pat;added=[]
        for y in ([w]if e else[])+a+b:
            assert not(r[z]>>y&1)
            helper.add(r,z,y);added.append((z,y))
            if r[z].bit_count()>14 or r[y].bit_count()>14:
                stats['degree_rejections']+=1;bad=True
            else:
                bad=helper.violation(r,z,y)
                if bad:stats['cap_rejections']+=1
            if bad:
                for x,t in reversed(added):r[x]^=1<<t;r[t]^=1<<x
                return None
        return added
    def visit(depth):
        nonlocal best,result
        if time.monotonic()>deadline or stats['nodes']>=20000:raise Limit()
        stats['nodes']+=1
        if depth>stats['max_depth']:stats['max_depth']=depth;best=[dict(x)for x in choice]
        if depth==len(domains):result=r[:];return True
        d=domains[depth];z=d['z']
        for pat in d['surviving_patterns']:
            stats['patterns_attempted']+=1
            changed=apply(z,pat)
            if changed is None:continue
            choice.append({'z':z,'pattern':pat})
            found=visit(depth+1)
            choice.pop()
            for x,y in reversed(changed):r[x]^=1<<y;r[y]^=1<<x
            if found:return True
        return False
    try:found=visit(0);status='CANDIDATE_COMPLETE_CENTERED_PARTIAL_WITNESS'if found else'UNSUCCESSFUL_COMPLETE_ENUMERATION_UNCERTIFIED'
    except Limit:status='UNKNOWN_RESOURCE_CAP';found=False
    checks=None
    if found:
        assert all(row.bit_count()<=14 for row in result)
        for u in[meta['u'],meta['v']]:
            assert result[u].bit_count()==14
            for y in range(99):
                if y!=u:assert(result[u]&result[y]).bit_count()+(result[u]>>y&1)==2
        for x in range(99):
            for y in range(x+1,99):assert(result[x]&result[y]).bit_count()+(result[x]>>y&1)<=2
        checks={'all_centered_offdiagonal_equations':196,'center_degrees':2,'all_partial_pair_caps':4851,'all_partial_degree_caps':99}
        save('partial99.json',{'known_edge_adjacency':[[row>>j&1 for j in range(99)]for row in result],'all_outside_patterns':best,'checks':checks})
    else:save('deepest_partial_assignment.json',{'assigned_outside_vertices':len(best),'patterns':best,'status':'NOT_A_COMPLETE_CENTERED_WITNESS'})
    save('summary.json',{'status':status,'timestamp':datetime.now(timezone.utc).isoformat(),'stats':stats,'wall_seconds':time.monotonic()-start,'checks':checks,'checks_null_reason':None if found else'No complete witness; no full failed-tree certificate exported.','independent_verification':None,'independent_verification_null_reason':'Producer search; any complete witness needs independent raw99 checking.','solver_calls':0,'conditional_exclusion_claimed':False,'limitations':['Only one fixed matching-augmented star pair was searched.','Resource exhaustion or uncertified enumeration is not an exclusion.','A complete centered partial witness would still not satisfy all noncenter SRG equations.','No target automorphism or whole-family coverage.'],'artifact_hashes':{p.name:h(p)for p in sorted(OUT.iterdir())}})
    print(json.dumps({'status':status,'stats':stats,'seconds':time.monotonic()-start,'summary_sha256':h(OUT/'summary.json')}))
if __name__=='__main__':main()
