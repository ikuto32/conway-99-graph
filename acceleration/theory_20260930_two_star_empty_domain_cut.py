"""Extract a complete finite-domain obstruction from a capped search prefix."""
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_two_star_empty_domain_cut/run01'
BASE=ROOT/'acceleration/results/20260930_joint_two_star_matching/run02/case_00.json'
COUPLED=ROOT/'acceleration/results/20260930_two_star_coupled_domains/run01'
MODEL=ROOT/'acceleration/results/20260930_unrestricted_full99_cnf/model.json'
HELPER=ROOT/'acceleration/theory_20260930_two_star_outside_domains.py'
def h(p):return sha256(p.read_bytes()).hexdigest()
def save(name,obj):
    with(OUT/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('outside_domain_producer',HELPER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    frozen=json.loads(BASE.read_bytes());meta=frozen['metadata'];u,v,w=[meta[x]for x in['u','v','w']]
    prefix=json.loads((COUPLED/'deepest_partial_assignment.json').read_bytes())
    domains=json.loads((COUPLED/'ordered_domains.json').read_bytes());depth=prefix['assigned_outside_vertices'];next_domain=domains[depth];z=next_domain['z']
    assert[p['z']for p in prefix['patterns']]==[d['z']for d in domains[:depth]]
    inputs=[BASE,COUPLED/'deepest_partial_assignment.json',COUPLED/'ordered_domains.json',COUPLED/'summary.json',MODEL,HELPER,Path(__file__).resolve(),ROOT/'uv.lock']
    save('manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'python':platform.python_version(),'question':'Does the first unassigned vertex at the saved deepest search prefix have an empty exact domain, and can optional positive edges be removed while retaining a complete obstruction?','selection':'One saved prefix, its next ordered variable; greedily test each noncenter outer positive edge once in lexicographic order. Stop reduction after20seconds; retain all checked evidence.','limits':{'greedy_seconds':20,'independent_verification':False},'success':'Every full pattern selecting the necessary remaining center-neighbor counts has an explicit integer pair-cap violation in the final fixed-positive graph.','inputs_sha256':{p.relative_to(ROOT).as_posix():h(p)for p in inputs}})
    module.controls()
    initial=module.bits(frozen['partial_known_edge_adjacency']);r=initial[:]
    for rec in prefix['patterns']:
        e,a,b=rec['pattern']
        for y in([w]if e else[])+a+b:module.add(r,rec['z'],y)
    left=[x for x in meta['A']if x>=15];right=[x for x in meta['B']if x>=15]
    p=2-(r[u]&r[z]).bit_count();q=2-(r[v]&r[z]).bit_count();patterns=list(module.patterns(left,right,p,q))
    def check(rows,full=False):
        rejects=[]
        for pat in patterns:
            bad=module.check_pattern(rows,z,w,pat)
            if bad is None:return None
            if full:rejects.append({'pattern':pat,'cap':bad})
        return rejects if full else True
    assert any(module.check_pattern(initial,z,w,pat)is None for pat in patterns),'base positive control'
    original=check(r,True);assert original is not None,'deepest prefix actually empty'
    save('original_empty_domain.json',{'known_edge_adjacency':[[row>>j&1 for j in range(99)]for row in r],'z':z,'deficits':[p,q],'all_rejections':original})
    optional=[(x,y)for x in range(15,99)for y in range(x+1,99)if x not in[u,v]and y not in[u,v]and r[x]>>y&1]
    attempts=[];start=time.monotonic()
    for x,y in optional:
        if time.monotonic()-start>20:break
        r[x]^=1<<y;r[y]^=1<<x;empty=check(r)
        if empty is None:module.add(r,x,y)
        attempts.append({'edge':[x,y],'removed_preserving_empty_domain':empty is not None})
    final=check(r,True);assert final is not None
    need_edges=[(x,y)for x in range(15,99)for y in range(x+1,99)if r[x]>>y&1]
    model=json.loads(MODEL.read_bytes());ids={(e['u'],e['v']):e['id']for e in model['edge_variables']}
    assert len(ids)==3486
    clause=[-ids[e]for e in need_edges]
    cert={'status':'CANDIDATE_TWO_STAR_EMPTY_DOMAIN_NOGOOD_PENDING_INDEPENDENT_REVIEW','timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'scope':'One exact positive-edge configuration in the unrestricted root scaffold. Every target retaining all these edges must choose a listed outside pattern, but every pattern violates a pair cap. No original-two-star, anchor-family or global nonexistence claim.','model_path':MODEL.relative_to(ROOT).as_posix(),'model_sha256':h(MODEL),'center_vertices':[u,v],'center_neighbors':[list(module.members(r[u])),list(module.members(r[v]))],'shared_neighbor':w,'outside_vertex':z,'residual_left':left,'residual_right':right,'deficits':[p,q],'enumeration_rule':'All e=0,1, L subset residual_left with |L|=p-e, R subset residual_right with |R|=q-e; candidate outside adjacency e to w plus L plus R.','pattern_count':len(patterns),'all_rejections':final,'known_positive_outer_edges':need_edges,'clause':clause,'known_edge_adjacency':[[row>>j&1 for j in range(99)]for row in r],'logical_derivation':['In a target these two complete14-neighbor stars saturate the centers, so every other center edge is absent.','The one common neighbor w and disjoint twelve-fibres partition the two center neighborhoods.','For outside z, the exact target common-neighbor counts2 with each center require exactly p,q new neighbors in these outer parts.','Every restriction of a target to those neighborhoods occurs in the enumerated pattern universe, regardless of z edges outside that union.','Each listed cap witness uses only fixed-positive and chosen-pattern edges; additional edges cannot decrease the violating common-plus-adjacency count.','Therefore at least one conditioned outer edge must be absent, which is the negative-literal clause.'],'independent_verification':None,'independent_verification_null_reason':'Certificate produced by discovery code; separate raw coverage, literal mapping and cap-witness replay needed.','minimality_claimed':False,'target_resolution':'NONE'}
    save('certificate.json',cert);(OUT/'nogood.clause').write_text(' '.join(map(str,clause))+' 0\n',encoding='ascii')
    save('reduction_attempts.json',attempts)
    save('controls.json',{'frozen_rook3_and_K4_controls_rerun':True,'unextended_case00_domain_has_survivor':True,'original_prefix_empty_domain_complete':True,'full_center_degrees':[r[u].bit_count(),r[v].bit_count()]})
    save('summary.json',{'status':cert['status'],'timestamp':datetime.now(timezone.utc).isoformat(),'prefix_outside_vertices':depth,'blocked_vertex':z,'complete_patterns':len(patterns),'original_positive_outer_edges':23+len(optional),'final_positive_outer_edges':len(need_edges),'optional_edges_tested':len(attempts),'optional_edges_removed':sum(a['removed_preserving_empty_domain']for a in attempts),'greedy_wall_seconds':time.monotonic()-start,'certificate_sha256':h(OUT/'certificate.json'),'target_resolution':'NONE','independent_verification':None,'independent_verification_null_reason':'Pending separate complete finite-domain certificate replay.','artifact_hashes':{p.name:h(p)for p in sorted(OUT.iterdir())}})
    print(json.dumps({'patterns':len(patterns),'cut_literals':len(clause),'z':z,'certificate_sha256':h(OUT/'certificate.json'),'summary_sha256':h(OUT/'summary.json')}))
if __name__=='__main__':main()
