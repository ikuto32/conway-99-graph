"""Independent partial-K filter check: graph mutation and edge-processing matching DP."""
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import gzip
import zlib
import audit_compressed_artifacts as recovery
import time
from tqdm import tqdm
import audit_20260917_partial_matching as scope
import audit_20260917_triangle_matching as graphcheck

ROOT=scope.ROOT
D=ROOT/'acceleration/results/20260917_six_coordinate_matching_filter/run01'
TABLES=ROOT/'acceleration/results/20260917_partial_six_matchings'
OUT=ROOT/'acceleration/results/20260917_independent_review/six_coordinate_matching_filter'

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
    original_root=ROOT;recovered={};recovery_records=[];relocations={}
    def resolve(p):
        p=Path(p)
        if not p.is_absolute():return (ROOT/p).resolve()
        p=p.resolve()
        if p.is_relative_to(ROOT):return p
        relative=p.relative_to(original_root);mapped=(ROOT/relative).resolve();mapped.relative_to(ROOT);relocations[str(p)]=str(mapped);return mapped
    def digest(p):
        p=resolve(p);return scope.digest(recovered.get(p,p))
    def read(p):
        p=resolve(p);bindings[scope.key(p)]=digest(p);return json.loads(recovered.get(p,p).read_bytes())
    manifest=read(D/'manifest.json');original_root=Path(manifest['cwd']).resolve();summary=read(D/'summary.json')
    scope.require(summary['manifest_sha256']==digest(D/'manifest.json'),'manifest pin')
    for f,v in manifest['inputs_sha256'].items():
        p=resolve(f);scope.require(digest(p)==v,'producer input changed');bindings[scope.key(p)]=v
    compressed=summary.get('compressed_manifest')
    if compressed:
        cp=resolve(compressed['path']);scope.require(digest(cp)==compressed['sha256'],'gzip manifest binding');cm=read(cp)
        for row in cm['files']:
            raw=resolve(row['path']);source=resolve(row['compressed_path']);scope.require(raw.parent==D.resolve()and source.parent==D.resolve(),'gzip artifact scope')
            scope.require(source.stat().st_size==row['compressed_size_bytes']and digest(source)==row['compressed_sha256'],'gzip source identity');bindings[scope.key(source)]=digest(source)
            target=OUT/'recovered'/raw.name;target.parent.mkdir(exist_ok=True)
            if target.exists():scope.require(scope.digest(target)==row['sha256']and target.stat().st_size==row['size_bytes'],'existing recovered identity')
            else:
                with source.open('rb')as inp,target.open('xb')as sink:recovery.decode(iter(lambda:inp.read(100003),b''),sink.write,row['size_bytes'],row['sha256'])
            recovered[raw]=target;bindings[scope.key(raw)]=row['sha256'];recovery_records.append(dict(raw_path=scope.key(raw),raw_sha256=row['sha256'],compressed_path=scope.key(source),compressed_sha256=row['compressed_sha256'],size_bytes=row['size_bytes'],recovered_path=scope.key(target),original_raw_consulted=False))
    proofpath=ROOT/'acceleration/results/20260917_independent_review/six_matchings/summary.json'
    scope.require(digest(proofpath)=='051a57b2fc1b5353a6100b949f86674483cff686c4f797f4f1ad8b037d7f3768','domain audit pin')
    proof=read(proofpath);scope.require(proof['status']=='INDEPENDENT_SIX_COORDINATE_DOMAINS_PASS','domain review')
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
    scope.require(len(unknown)==2040 and graphcheck.cap_ok(B),'partial graph')
    ctrl=controls();fixture=b'independent six matching gzip control';blob=gzip.compress(fixture,mtime=0);expected=__import__('hashlib').sha256(fixture).hexdigest();recovery.decode([blob],lambda _:None,len(fixture),expected);bad=bytearray(blob);bad[-8]^=1
    try:recovery.decode([bytes(bad)],lambda _:None,len(fixture),expected)
    except(ValueError,zlib.error):pass
    else:raise ValueError('corrupt gzip accepted')
    ctrl['gzip_positive_and_corrupt_crc']='PASS';results=[]
    scope.require([v['outer_vertex']for v in summary['vertices']]==list(range(84)),'vertex population')
    for u in tqdm(range(84),desc='Independent six-coordinate matching filter',unit='center'):
        out=OUT/f'vertex_{u:02d}.json';p=D/f'vertex_{u:02d}.json';raw=read(p)
        masks=read(TABLES/f'domain_{u:02d}.json')['domain_masks_hex']
        scope.require(digest(p)==summary['vertices'][u]['sha256'] and len(raw['records'])==len(masks)==raw['original_count'] and raw['outer_vertex']==u,'original universe')
        if out.exists():
            done=read(out);scope.require(done['raw_sha256']==digest(p)and done['auditor_sha256']==digest(__file__),'resume identity');results.append(done);continue
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
        rejected_set=set(rejected)
        scope.require(rejected==raw['rejected_ids']and raw['complete']is True and raw['surviving_ids']==[i for i in range(len(masks))if i not in rejected_set],'rejected/surviving ID partition')
        done=dict(outer_vertex=u,original_count=len(masks),rejected_ids=rejected,rejected_count=len(rejected),surviving_count=len(masks)-len(rejected),prospective_edges_checked=checks,negative_DP_states_visited=states,raw_sha256=digest(p),auditor_sha256=digest(__file__))
        with out.open('x')as f:json.dump(done,f,indent=2)
        results.append(done)
    counts={k:sum(r[k]for r in results)for k in ('original_count','rejected_count','surviving_count','prospective_edges_checked','negative_DP_states_visited')}
    scope.require(counts['original_count']==summary['original_choices']and counts['rejected_count']==summary['rejected_choices']and counts['surviving_count']==summary['surviving_choices'],'summary counts')
    for p in (__file__,scope.__file__,graphcheck.__file__,recovery.__file__,ROOT/'uv.lock'):bindings[scope.key(p)]=digest(p)
    result=dict(status='INDEPENDENT_SIX_COORDINATE_NEIGHBORHOOD_MATCHING_FILTER_PASS',claim_id='C-PARTIAL-K-SIX-COORDINATE-NEIGHBORHOOD-MATCHING-FILTER',claim_revision=1,started_at=started,completed_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-tick,source_commit_observed_after_checks=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,counts=counts,empty_domains=sum(r['surviving_count']==0 for r in results),records=results,controls=ctrl,lossless_gzip_recovery=recovery_records,explicit_original_root_relocations=relocations,original_large_raw_consulted=False,producer_imported=False,method='Full99 row mutation checks all affected common-neighbor cap pairs for each prospective edge; positive matching witnesses checked directly; every rejection checked by edge-processing reachable-subset DP, distinct from producer vertex recurrence. Base-star cap validity and domain completeness reused from pinned independent full-domain audit.',derivation='For any SRG target, lambda=1 means each vertex in N(center) has exactly one neighbor in N(center). Thus its 14-neighborhood is seven disjoint edges. Existing forced edges occupy distinct endpoints. Every remaining matching edge must lie in the partial-family unknown set and preserve common-neighbor upper caps under its individual insertion. Absence of a matching in this supergraph rules out this local star.',scope='Exact frozen 132-fixed-overlap-edge family with same-fibre and other-coordinate prescribed absences, 2040 unknown edges and 879449 original choices. Original center/domain IDs retained.',limitations=['No empty domain; no family or unrestricted exclusion follows from this filter alone.','Positive witnesses establish only a matching in individually permissible edges, not simultaneous cap feasibility or a graph completion.','Positive matching multiplicities are not independently recounted; only existence and the exact rejected/surviving partition are claimed.'],shared_components=['Python standard library','tqdm progress','prior independent artifact helpers and graph-mutation checker','pinned independently complete domain audit','independent streaming zlib recovery helper'])
    with(OUT/'summary.json').open('x')as f:json.dump(result,f,indent=2)
    print(json.dumps(counts))
if __name__=='__main__':main()
