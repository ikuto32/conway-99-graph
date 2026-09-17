"""Independent partial-K filter check: graph mutation and edge-processing matching DP."""
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm
import audit_20260917_partial_matching as scope
import audit_20260917_triangle_matching as graphcheck

ROOT=scope.ROOT
D=ROOT/'acceleration/results/20260917_four_coordinate_matching_filter/run01'
TABLES=ROOT/'acceleration/results/20260917_partial_four_matchings'
OUT=ROOT/'acceleration/results/20260917_independent_review/four_coordinate_matching_filter'

def possible(nodes,edges):
    """Enumerate reachable covered-vertex subsets by processing edges, not first vertex."""
    positions={v:i for i,v in enumerate(nodes)}
    if len(nodes)%2:return False,0
    target=(1<<len(nodes))-1
    masks=[(1<<positions[a])|(1<<positions[b])for a,b in edges]
    if target and (not masks or __import__('functools').reduce(int.__or__,masks,0)!=target):return False,1
    reachable={0};visits=0
    for edge in masks:
        added={state|edge for state in reachable if not state&edge};visits+=len(reachable)
        reachable.update(added)
        if target in reachable:return True,visits
    return target in reachable,visits

def controls():
    for n,edges,want in [(4,list(combinations(range(4),2)),True),(14,[(i,i+1)for i in range(0,14,2)],True),(14,[(i,i+1)for i in range(0,12,2)],False),(6,[(0,1),(1,2),(0,2),(3,4),(3,5),(4,5)],False),(0,[],True)]:
        scope.require(possible(list(range(n)),edges)[0]==want,'matching control')
    old=graphcheck.controls()
    return dict(edge_DP_fixtures=5,prior_independent_graph_mutation_and_exhaustive_controls=old)

def main():
    OUT.mkdir(parents=True,exist_ok=True);bindings={};started=datetime.now(timezone.utc).isoformat();tick=time.perf_counter()
    def read(p):
        bindings[scope.key(p)]=scope.digest(p);return json.loads(Path(p).read_bytes())
    manifest=read(D/'manifest.json');summary=read(D/'summary.json')
    scope.require(summary['manifest_sha256']==scope.digest(D/'manifest.json'),'manifest pin')
    for f,v in manifest['inputs_sha256'].items():
        p=ROOT/Path(f);scope.require(scope.digest(p)==v,'producer input changed');bindings[scope.key(p)]=v
    proofpath=ROOT/'acceleration/results/20260917_independent_review/four_matchings/summary.json'
    scope.require(scope.digest(proofpath)=='fb21f69b6e5785e0897bccb6965bfea75c171aad2e685b7d60966bc5c8019e73','domain audit pin')
    proof=read(proofpath);scope.require(proof['status']=='INDEPENDENT_FOUR_COORDINATE_DOMAINS_PASS','domain review')
    primary=read(TABLES/'manifest.json')
    labels=sorted([(a,b)for a in range(14)for b in range(a+1,14)if a//2!=b//2],key=lambda e:(e[0]//2,e[1]//2,e[0],e[1]))
    B=[0]*99
    def add(rows,a,b):rows[a]|=1<<b;rows[b]|=1<<a
    for v in range(1,15):add(B,0,v)
    for v in range(1,15,2):add(B,v,v+1)
    for u,pair in enumerate(labels,15):
        for s in pair:add(B,u,s+1)
    for a,b in primary['remaining_fixed_K_edges_outer']:add(B,a+15,b+15)
    unknown={(a+15,b+15)for a,b in primary['unknown_edges_outer']}
    scope.require(len(unknown)==1920 and graphcheck.cap_ok(B),'partial graph')
    ctrl=controls();results=[]
    scope.require([v['outer_vertex']for v in summary['vertices']]==list(range(84)),'vertex population')
    for u in tqdm(range(84),desc='Independent four-coordinate matching filter',unit='center'):
        out=OUT/f'vertex_{u:02d}.json';p=D/f'vertex_{u:02d}.json';raw=read(p)
        masks=read(TABLES/f'domain_{u:02d}.json')['domain_masks_hex']
        scope.require(scope.digest(p)==summary['vertices'][u]['sha256'] and len(raw['records'])==len(masks)==raw['original_count'] and raw['outer_vertex']==u,'original universe')
        if out.exists():
            done=read(out);scope.require(done['raw_sha256']==scope.digest(p)and done['auditor_sha256']==scope.digest(__file__),'resume identity');results.append(done);continue
        rejected=[];checks=0;states=0
        for i,(masktext,r)in enumerate(zip(masks,raw['records'])):
            scope.require(r['original_id']==i and r['mask']==masktext,'original ID')
            rows=B[:];center=u+15
            for v in scope.bits(int(masktext,16)):
                scope.require(tuple(sorted((center,v+15)))in unknown,'star edge scope');add(rows,center,v+15)
            scope.require(rows[center].bit_count()==14,'complete center')
            neighbors=[v for v in range(99)if rows[center]>>v&1]
            forced=[[a,b]for a,b in combinations(neighbors,2)if rows[a]>>b&1];used=[v for e in forced for v in e]
            scope.require(len(set(used))==len(used),'forced matching')
            free=[v for v in neighbors if v not in used]
            allowed=[]
            for a,b in combinations(free,2):
                if(a,b)in unknown:
                    checks+=1
                    if graphcheck.permitted(rows,a,b):allowed.append([a,b])
            scope.require(forced==r['forced_edges_full99']and free==r['unmatched_vertices_full99']and allowed==r['allowed_edges_full99'],'permissive graph')
            scope.require(type(r['matching_count'])is int and r['matching_count']>=0,'count sign')
            if r['matching_count']==0:
                exists,visits=possible(free,allowed);states+=visits
                scope.require(not exists and r['matching_witness_full99']==[],'false rejection');rejected.append(i)
            else:
                witness=r['matching_witness_full99']
                scope.require(len(witness)*2==len(free)and all(e in allowed for e in witness)and sorted(v for e in witness for v in e)==free,'invalid positive matching')
        scope.require(rejected==raw['rejected_ids']and raw['complete']is True and raw['surviving_ids']==[i for i in range(len(masks))if i not in set(rejected)],'rejected/surviving ID partition')
        done=dict(outer_vertex=u,original_count=len(masks),rejected_ids=rejected,rejected_count=len(rejected),surviving_count=len(masks)-len(rejected),prospective_edges_checked=checks,negative_DP_states_visited=states,raw_sha256=scope.digest(p),auditor_sha256=scope.digest(__file__))
        with out.open('x')as f:json.dump(done,f,indent=2)
        results.append(done)
    counts={k:sum(r[k]for r in results)for k in ('original_count','rejected_count','surviving_count','prospective_edges_checked','negative_DP_states_visited')}
    scope.require(counts['original_count']==summary['original_choices']and counts['rejected_count']==summary['rejected_choices']and counts['surviving_count']==summary['surviving_choices'],'summary counts')
    for p in (__file__,scope.__file__,graphcheck.__file__,ROOT/'uv.lock'):bindings[scope.key(p)]=scope.digest(p)
    result=dict(status='INDEPENDENT_FOUR_COORDINATE_NEIGHBORHOOD_MATCHING_FILTER_PASS',claim_id='C-PARTIAL-K-FOUR-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER',claim_revision=1,started_at=started,completed_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-tick,source_commit_observed_after_checks=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,counts=counts,empty_domains=sum(r['surviving_count']==0 for r in results),records=results,controls=ctrl,producer_imported=False,method='Full99 row mutation checks all affected common-neighbor cap pairs for each prospective edge; positive matching witnesses checked directly; every rejection checked by edge-processing reachable-subset DP, distinct from producer vertex recurrence. Base-star cap validity and domain completeness reused from pinned independent full-domain audit.',derivation='For any SRG target, lambda=1 means each vertex in N(center) has exactly one neighbor in N(center). Thus its 14-neighborhood is seven disjoint edges. Existing forced edges occupy distinct endpoints. Every remaining matching edge must lie in the partial-family unknown set and preserve common-neighbor upper caps under its individual insertion. Absence of a matching in this supergraph rules out this local star.',scope='Exact frozen 144-fixed-overlap-edge family with same-fibre and other-coordinate prescribed absences, 1920 unknown edges and 290460 original choices. Original center/domain IDs retained.',limitations=['No empty domain; no family or unrestricted exclusion follows from this filter alone.','Positive witnesses establish only a matching in individually permissible edges, not simultaneous cap feasibility or a graph completion.','Positive matching multiplicities are not independently recounted; only existence and the exact rejected/surviving partition are claimed.'],shared_components=['Python standard library','tqdm progress','prior independent artifact helpers and graph-mutation checker','pinned independently complete domain audit'])
    with(OUT/'summary.json').open('x')as f:json.dump(result,f,indent=2)
    print(json.dumps(counts))
if __name__=='__main__':main()
