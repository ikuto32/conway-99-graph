"""Candidate falsification screen; no producer or prior graph-checker imports."""
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse,json,platform,subprocess,sys,time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
REVIEW=ROOT/'acceleration/results/20260930_independent_review/eight_coordinate_matching_filter'
TABLES=ROOT/'acceleration/results/20260930_eight_domains/run01'
OUT=ROOT/'acceleration/results/20260930_matching_cap_composition'
PREVIOUS_SOURCE_SHA='c288622ec72d58cde20181f420b0eb17601aa6de595563788365562b62faef30'
def digest(p):
    h=sha256()
    with Path(p).open('rb')as f:
        while b:=f.read(1<<20):h.update(b)
    return h.hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,d):
    with p.open('x')as f:json.dump(d,f,indent=2)
def add(rows,a,b):rows[a]|=1<<b;rows[b]|=1<<a
def violations(rows):
    return [dict(pair=[a,b],common=(rows[a]&rows[b]).bit_count(),cap=2-((rows[a]>>b)&1))for a,b in combinations(range(len(rows)),2)if(rows[a]&rows[b]).bit_count()>2-((rows[a]>>b)&1)]
def extended(rows,edges):
    result=rows[:]
    for a,b in edges:add(result,a,b)
    return result
def matchings(vertices):
    if not vertices:yield [];return
    first=vertices[0]
    for j in range(1,len(vertices)):
        for rest in matchings(vertices[1:j]+vertices[j+1:]):yield[(first,vertices[j])]+rest
def controls():
    windmill=[0]*99
    for v in range(1,15):add(windmill,0,v)
    matching=[(v,v+1)for v in range(1,15,2)]
    assert not violations(windmill)and all(not violations(extended(windmill,[e]))for e in matching)and not violations(extended(windmill,matching))
    overlap=[(1,2),(1,3)];assert all(not violations(extended(windmill,[e]))for e in overlap)and violations(extended(windmill,overlap))
    base=[0]*5
    for e in[(0,3),(0,4),(1,2),(2,4)]:add(base,*e)
    bad=[(0,1),(2,3)]
    assert not violations(base)and all(not violations(extended(base,[e]))for e in bad)and violations(extended(base,bad))==[dict(pair=[0,2],common=3,cap=2)]
    graphs=0;instances=0;admissible=0;pairs=list(combinations(range(5),2))
    for mask in range(1<<len(pairs)):
        rows=[0]*5
        for j,e in enumerate(pairs):
            if mask>>j&1:add(rows,*e)
        if violations(rows):continue
        graphs+=1
        for count in(0,2,4):
            for vertices in combinations(range(5),count):
                if any(rows[a]>>b&1 for a,b in combinations(vertices,2)):continue
                for matching in matchings(list(vertices)):
                    instances+=1
                    if all(not violations(extended(rows,[e]))for e in matching):
                        admissible+=1;assert not violations(extended(rows,matching))
    return dict(known_valid_windmill='PASS',overlapping_edges_corruption='REJECTED',nonindependent_endpoint_corruption=dict(base_rows=base,matching=bad,violation=violations(extended(base,bad))),five_vertex_graph_population=1024,cap_admissible_five_vertex_graphs=graphs,independent_set_matching_instances=instances,single_edge_admissible_instances=admissible,general_proof_claimed=False)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=float,default=100);parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=args.resume);assert not(OUT/'summary.json').exists();tick=time.monotonic();stamp=datetime.now(timezone.utc).isoformat();bindings={}
    def read(p):bindings[key(p)]=digest(p);return json.loads(p.read_bytes())
    for p in[Path(__file__),ROOT/'uv.lock',ROOT/'acceleration/theory_20260930_matching_cap_composition.md']:bindings[key(p)]=digest(p)
    gatepath=REVIEW/'summary.json';assert digest(gatepath)=='4fcd5fd7f02cd5362bda1f8f0a1c8e4669ce036bde56a04dcd1b6a3391b262f4';gate=read(gatepath)
    assert gate['status']=='INDEPENDENT_EIGHT_COORDINATE_NEIGHBORHOOD_MATCHING_FILTER_PASS'
    primary=read(TABLES/'manifest.json');assert bindings[key(TABLES/'manifest.json')]==gate['inputs_sha256'][key(TABLES/'manifest.json')]
    prereg=dict(retrieval_correction='V2 only adds fallback to original uncompressed raw files; all audited raw SHA256 checks and cap calculations unchanged. Resumed V1 center receipts retain their exact source binding.',previous_source_sha256=PREVIOUS_SOURCE_SHA,timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),question='Can a saved individually permitted residual perfect matching violate a full pair cap when added jointly?',candidate_general_lemma='Independent endpoint matching additions preserve caps jointly whenever every individual edge preserves caps.',selection='First256 surviving original IDs in ascending order for each center0..83; one frozen saved matching witness per selected star; no selection by outcome.',selected_stars=sum(min(256,r['surviving_count'])for r in gate['records']),population='1875214 retained eight-coordinate stars; sample only21504',success_or_falsification='Any violation after all saved witness edges falsifies cap composition only if base/independence/matching/single-edge premises hold; one failed witness alone never excludes its star.',resource_cap_seconds=args.seconds,cap_boundary='Checked between whole centers; completed center receipts support resume.',first_counterexample_stops=True,numerical_threshold=None,numerical_threshold_reason='Integer adjacency and popcount only.',inputs_sha256=dict(bindings),mathematical_status='CANDIDATE pending independent proof review')
    attempt=1+len(list(OUT.glob('invocation_*.json')));save(OUT/f'invocation_{attempt:02d}.json',prereg)
    if not(OUT/'controls.json').exists():save(OUT/'controls.json',controls())
    ctrl=read(OUT/'controls.json')
    labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)]
    base=[0]*99
    for a in range(1,15):add(base,0,a)
    for a in range(1,15,2):add(base,a,a+1)
    for u,label in enumerate(labels,15):
        for a in label:add(base,u,a+1)
    for a,b in primary['remaining_fixed_K_edges_outer']:add(base,a+15,b+15)
    assert not violations(base);records=[];first=None
    for u in tqdm(range(84),desc='Joint matching cap falsification',unit='center'):
        done=OUT/f'center_{u:02d}.json'
        if done.exists():
            r=read(done);assert r['source_sha256']in{bindings[key(Path(__file__))],PREVIOUS_SOURCE_SHA} and r['raw_sha256']==gate['records'][u]['raw_sha256'] and r['joint_cap_failures']==0;records.append(r);continue
        if time.monotonic()-tick>=args.seconds:break
        rawpath=REVIEW/'recovered'/f'vertex_{u:02d}.json'
        if not rawpath.exists():rawpath=ROOT/'acceleration/results/20260930_eight_matching_filter/run01'/f'vertex_{u:02d}.json'
        raw=read(rawpath);assert bindings[key(rawpath)]==gate['records'][u]['raw_sha256']
        reject=set(gate['records'][u]['rejected_ids']);selected=[i for i in range(raw['original_count'])if i not in reject][:256]
        domain=read(TABLES/f'domain_{u:02d}.json');assert bindings[key(TABLES/f'domain_{u:02d}.json')]==gate['inputs_sha256'][key(TABLES/f'domain_{u:02d}.json')]
        checked=[];edge_count=0
        for i in selected:
            r=raw['records'][i];assert r['original_id']==i and r['mask']==domain['domain_masks_hex'][i]and r['matching_count']>0
            rows=base[:];center=u+15;mask=int(r['mask'],16)
            for v in range(84):
                if mask>>v&1:add(rows,center,v+15)
            neighbors=[v for v in range(99)if rows[center]>>v&1];assert len(neighbors)==14
            forced=[(a,b)for a,b in combinations(neighbors,2)if rows[a]>>b&1];used=[v for edge in forced for v in edge];assert len(used)==len(set(used))
            free=sorted(set(neighbors)-set(used));witness=r['matching_witness_full99'];assert sorted(v for edge in witness for v in edge)==free
            assert not any(rows[a]>>b&1 for a,b in combinations(free,2))and all(edge in r['allowed_edges_full99']for edge in witness)
            joint=extended(rows,witness);bad=violations(joint);checked.append(i);edge_count+=len(witness)
            if bad:
                first=dict(outer_vertex=u,original_id=i,mask=r['mask'],base_star_rows=rows,matching=witness,joint_rows=joint,violations=bad,base_violations=violations(rows),individual_violations=[violations(extended(rows,[edge]))for edge in witness]);save(OUT/'first_counterexample.json',first);break
        record=dict(outer_vertex=u,selected_ids=selected,checked_ids=checked,completed=len(checked)==len(selected),witnesses_checked=len(checked),pair_caps_checked=len(checked)*4851,matching_edges_added=edge_count,joint_cap_failures=int(first is not None),raw_sha256=bindings[key(rawpath)],domain_sha256=bindings[key(TABLES/f'domain_{u:02d}.json')],source_sha256=bindings[key(Path(__file__))])
        save(done,record);records.append(record)
        if first:break
    complete=len(records)==84 and all(r['completed']for r in records)
    assert all(digest(ROOT/k)==v for k,v in bindings.items()),'input changed during screen'
    report=dict(status='CANDIDATE_MATCHING_CAP_SAMPLE_COMPLETE'if complete else'CANDIDATE_MATCHING_CAP_COUNTEREXAMPLE'if first else'INCOMPLETE_MATCHING_CAP_SCREEN_TIME_CAP',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=prereg['source_commit'],command=prereg['command'],cwd=str(ROOT),inputs_sha256=bindings,records=records,selected_stars=prereg['selected_stars'],checked_stars=sum(r['witnesses_checked']for r in records),checked_pair_caps=sum(r['pair_caps_checked']for r in records),centers_completed=sum(r['completed']for r in records),joint_cap_failures=sum(r['joint_cap_failures']for r in records),unattempted_stars=prereg['selected_stars']-sum(r['witnesses_checked']for r in records),controls=ctrl,elapsed_seconds=time.monotonic()-tick,independent_verification=False,producer_filter_imported=False,target_resolution=False,limitations=['Sampled one witness per selected star; no claim about untested stars or all matching choices from sampling.','General redundancy depends on the separate independently reviewed lemma, not on absence of sampled failures.','All original artifacts and earlier reports remain unchanged.'])
    save(OUT/('summary.json'if complete or first else f'checkpoint_{attempt:02d}.json'),report)
    print(json.dumps({k:report[k]for k in('status','checked_stars','checked_pair_caps','centers_completed','joint_cap_failures','unattempted_stars','elapsed_seconds')}))
if __name__=='__main__':main()
