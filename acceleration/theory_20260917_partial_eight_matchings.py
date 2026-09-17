"""Bounded complete-domain pilot for eight freed same-sign coordinates; no LP."""
import argparse
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm
from theory_20260917_partial_matching import add,valid,direct_subset_ok,members,Cap,CANDIDATE
from theory_20260917_six_coordinate_enumerator import enumerate_star_retained

OLD=Path('acceleration/results/20260917_partial_six_matchings')
AUDIT=Path('acceleration/results/20260917_independent_review/six_matchings/summary.json')
AUDIT_HASH='051a57b2fc1b5353a6100b949f86674483cff686c4f797f4f1ad8b037d7f3768'
PROTOCOL=Path('docs/NEXT_20260917_EIGHT_COORDINATE_DOMAIN_PILOT.md')
DOMAIN='PARTIAL_K_EIGHT_SAME_SIGN_COORDINATES_ROOT0123_V1'
ORDER=[0,4,24,8,44,60]+[u for u in range(84) if u not in(0,4,24,8,44,60)]


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2);f.write('\n')
def stamp():return datetime.now(timezone.utc).isoformat()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True);assert not any(args.out.iterdir())
    assert digest(AUDIT)==AUDIT_HASH;audit=read(AUDIT)
    assert audit['status']=='INDEPENDENT_SIX_COORDINATE_DOMAINS_PASS' and audit['domain_choices']==879449
    paths=[AUDIT,OLD/'manifest.json',OLD/'summary.json',Path(CANDIDATE),Path(__file__),
           Path('acceleration/theory_20260917_six_coordinate_enumerator.py'),Path('acceleration/theory_20260917_partial_matching.py'),PROTOCOL,Path('uv.lock')]
    paths+=[OLD/f'domain_{u:02d}.json' for u in range(84)]
    for p in paths:
        if p.parent==OLD:assert digest(p) in audit['inputs_sha256'].values()
    bindings={p.as_posix():digest(p) for p in paths}
    old_manifest=read(OLD/'manifest.json');candidate=read(CANDIDATE)
    labels=[(2*a+s,2*b+t) for a,b in combinations(range(7),2) for s in(0,1) for t in(0,1)]
    supports=[{s//2 for s in pair} for pair in labels]
    all_K=set(map(tuple,candidate['overlap_edges_outer_zero_based']));allowed_Y=set()
    for symbol in range(8):
        coordinate=[u for u,pair in enumerate(labels) if symbol in pair]
        legal={(u,v) for u,v in combinations(coordinate,2) if len(supports[u]&supports[v])==1}
        assert len(legal)==60;allowed_Y|=legal
    removed=all_K&allowed_Y;fixed=all_K-removed
    unknown=sorted({(u,v) for u,v in combinations(range(84),2) if not supports[u]&supports[v]}|allowed_Y)
    old_fixed=set(map(tuple,old_manifest['remaining_fixed_K_edges_outer']))
    def graph(edges):
        r=[0]*99
        for u in range(1,15):add(r,0,u)
        for u in range(1,15,2):add(r,u,u+1)
        for u,pair in enumerate(labels,15):
            for s in pair:add(r,u,s+1)
        for u,v in edges:add(r,u+15,v+15)
        return r
    rows=graph(fixed);old_rows=graph(old_fixed)
    assert len(fixed)==120 and len(removed)==48 and len(allowed_Y)==480 and len(unknown)==2160
    assert Counter(14-rows[u+15].bit_count() for u in range(84))=={10:24,9:48,8:12}
    assert fixed<=old_fixed and valid(rows)
    scope='Retain 120 baseline K edges including all 7 cross and 6 other same-sign matchings; all same-fibre and unlisted other-coordinate absences fixed. Unknown 480 same-sign edges at root groups 0,1,2,3 plus 1680 disjoint-support edges.'
    manifest=dict(timestamp=stamp(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
        domain=DOMAIN,scope=scope,enumeration_order=ORDER,selection='Frozen pilot centers 0,4,24,8,44,60, then all remaining outer labels ascending; fixed before results.',
        limits=dict(enumeration_seconds=300,nodes=50000000,per_center_domains=250000,total_domains=5000000),
        remaining_fixed_K_edges_outer=sorted(fixed),removed_edges_outer=sorted(removed),freed_legal_matching_edges_outer=sorted(allowed_Y),
        unknown_edges_outer=unknown,missing_neighbors='10 at 24 centers, 9 at 48 centers, 8 at 12 centers',
        old_population=879449,old_embedding='Add removed old fixedneighbors to eachmask; fullcenter neighborhood identical; otheredges onlydeleted, preserving localcaps/rootquotas.',
        shared_code='Disclosed retained-partial adaptation of frozen exact enumerator; old add/valid/direct_subset_ok/members helpers. Independent completeness review still required.',
        stopping='One capped invocation only; no retry; retain discoveredpartialmasks and captrigger. NoLP.',
        controls='Six preselected restricteduniverses brutechecked, corruptedmissingedge rejected; cap0 retains trigger and no completeflag.',
        LP_ran=False,target_resolution=False)
    save(args.out/'manifest.json',manifest)
    allowed=[set() for _ in range(84)]
    for a,b in unknown:allowed[a].add(b);allowed[b].add(a)
    converted=[];embedding_counts=[]
    for u in tqdm(range(84),desc='Embed all prior six-coordinate stars',unit='center'):
        old_masks=[int(x,16) for x in read(OLD/f'domain_{u:02d}.json')['domain_masks_hex']]
        extra=(old_rows[u+15]&~rows[u+15])>>15;new_masks=[mask|extra for mask in old_masks]
        assert len(set(new_masks))==len(new_masks)
        for old_mask,new_mask in zip(old_masks,new_masks):
            assert (old_rows[u+15]>>15)|old_mask==(rows[u+15]>>15)|new_mask
            assert new_mask.bit_count()+rows[u+15].bit_count()==14
            assert set(members(new_mask))<=allowed[u]
        converted.append(new_masks)
        p=args.out/f'embedding_{u:02d}.json'
        save(p,dict(outer_vertex=u,old_original_ids=list(range(len(old_masks))),new_masks_hex=[hex(x) for x in new_masks],
                    full_center_neighborhood_preserved=True,complete_new_domain_membership='Pending enumeration; admissibility follows by monotone fixededge deletion'))
        embedding_counts.append(dict(outer_vertex=u,old_choices=len(old_masks),path=str(p),sha256=digest(p)))
    assert sum(x['old_choices'] for x in embedding_counts)==879449
    save(args.out/'embedding_summary.json',dict(status='CANDIDATE_ALL_OLD_NEIGHBORHOODS_EMBED',old_choices=879449,records=embedding_counts,
        derivation='Each new partialgraph+convertedstar is a subgraph of oldpartialgraph+oldstar with the centerrow unchanged. Deletingotheredges cannotincrease commonneighbors or tighten caps; rootrows fixed, so all rootquotas preserved.',independent_review=False))
    # Calibration is separate from the capped full-enumeration node/time counters.
    cb=dict(deadline=time.monotonic()+30,nodes=0,node_cap=1000000,domain_cap=100000,total_cap=1000000,complete_choices=0)
    controls=[]
    for u in ORDER[:6]:
        selected=set(members(converted[u][0]));pool=selected|set(sorted(allowed[u]-selected)[:2])
        state=dict(masks=[],nodes=0);actual,_,_=enumerate_star_retained(rows,labels,unknown,u,cb,state,restricted=pool)
        expected=sorted(sum(1<<v for v in subset) for subset in combinations(sorted(pool),14-rows[u+15].bit_count()) if direct_subset_ok(rows,labels,u,subset))
        assert actual==expected and actual
        corrupt=actual[0]^(actual[0]&-actual[0]);assert not direct_subset_ok(rows,labels,u,list(members(corrupt)))
        controls.append(dict(outer_vertex=u,pool=sorted(pool),accepted_masks_hex=[hex(x) for x in actual],brute_agreement=True,missing_edge_rejected=True))
    trigger=dict(masks=[],nodes=0);zero=cb.copy();zero['domain_cap']=0
    try:enumerate_star_retained(rows,labels,unknown,ORDER[0],zero,trigger,restricted=set(members(converted[ORDER[0]][0])))
    except Cap as exc:assert str(exc)=='PER_VERTEX_DOMAIN_CAP' and not trigger['masks'] and 'cap_trigger_mask' in trigger
    else:raise AssertionError('zero-domain cap not honored')
    save(args.out/'controls.json',dict(positive_corrupt_controls=controls,zero_cap_retains_trigger=True,independent_verification=False))
    started=time.monotonic();budget=dict(deadline=started+300,nodes=0,node_cap=50000000,domain_cap=250000,total_cap=5000000,complete_choices=0)
    records=[];incomplete=None
    for u in tqdm(ORDER,desc='Eight freed matching coordinates',unit='center'):
        if time.monotonic()>=budget['deadline']:
            incomplete=dict(outer_vertex=u,reason='TIME_CAP_BEFORE_CENTER');break
        state=dict(masks=[],nodes=0)
        try:masks,nodes,candidates=enumerate_star_retained(rows,labels,unknown,u,budget,state)
        except Cap as exc:
            masks=sorted(state['masks']);assert len(masks)==len(set(masks))
            trigger_mask=state.get('cap_trigger_mask')
            p=args.out/f'partial_domain_{u:02d}.json'
            save(p,dict(outer_vertex=u,status='INCOMPLETE_ENUMERATION',domain_masks_hex=[hex(x) for x in masks],
                retained_partial_choices=len(masks),search_nodes=state['nodes'],allowed_single_neighbors=state.get('candidates'),
                cap_trigger_mask_hex=hex(trigger_mask) if trigger_mask is not None else None,
                cap_trigger_null_reason=None if trigger_mask is not None else 'Node/timecap interrupted recursion, no additional acceptedleaf.',
                complete=False,reason=str(exc)))
            incomplete=dict(outer_vertex=u,reason=str(exc),partial_choices=len(masks),partial_path=str(p),partial_sha256=digest(p));break
        lookup={mask:i for i,mask in enumerate(masks)};mapping=[lookup[mask] for mask in converted[u]]
        assert len(mapping)==len(set(mapping))
        p=args.out/f'domain_{u:02d}.json'
        record=dict(outer_vertex=u,domain=DOMAIN,status='CANDIDATE_COMPLETE_EIGHT_COORDINATE_DOMAIN',domain_size=len(masks),
                    domain_masks_hex=[hex(x) for x in masks],missing_neighbor_count=14-rows[u+15].bit_count(),
                    allowed_single_neighbors=candidates,search_nodes=nodes,old_to_new_domain_ids=mapping,old_embedded_choices=len(mapping))
        save(p,record);budget['complete_choices']+=len(masks)
        records.append(dict(outer_vertex=u,domain_size=len(masks),search_nodes=nodes,old_embedded_choices=len(mapping),path=str(p),sha256=digest(p)))
        save(args.out/f'checkpoint_{len(records):02d}.json',dict(timestamp=stamp(),completed_centers=records,
            complete_domain_choices=budget['complete_choices'],search_nodes=budget['nodes'],elapsed_seconds=time.monotonic()-started))
    assert all(digest(p)==h for p,h in bindings.items())
    summary=dict(timestamp=stamp(),status='CANDIDATE_EIGHT_COORDINATE_DOMAIN_PILOT',domain=DOMAIN,scope=scope,
        completed_centers=len(records),complete_domain_choices=budget['complete_choices'],complete_all_centers=len(records)==84 and incomplete is None,
        all_old_neighborhood_embeddings=879449,old_choices_located_in_complete_domains=sum(r['old_embedded_choices'] for r in records),
        largest_completed_domain=max((r['domain_size'] for r in records),default=0),incomplete=incomplete,domains=records,
        search_nodes=budget['nodes'],enumeration_seconds=time.monotonic()-started,
        output_sha256={p.name:digest(p) for p in args.out.iterdir() if p.is_file()},
        independent_domain_review=False,LP_ran=False,exclusion_claimed=False,target_resolution=False,
        restart_policy='No retries authorized for this finitepilot; partial masks are retained, not an exact recursive resume stack.')
    save(args.out/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in('domains','output_sha256')}))


if __name__=='__main__':main()
