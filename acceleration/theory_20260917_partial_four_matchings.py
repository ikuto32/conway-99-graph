"""Complete-domain pilot freeing both same-sign coordinates at root groups0 and1."""
import argparse
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm

from theory_20260917_partial_matching import build,enumerate_star,direct_subset_ok,valid,Cap,members,edge,digest,save,CANDIDATE

ROOT=Path(__file__).resolve().parents[1]
OLD="acceleration/results/20260917_partial_two_matchings"
DOMAIN="PARTIAL_K_FOUR_SAME_SIGN_COORDINATES_ROOT01_V1"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    assert not any(args.out.iterdir())
    bindings={}
    def read(name):
        bindings[name]=digest(ROOT/name)
        return json.loads((ROOT/name).read_bytes())
    candidate=read(CANDIDATE);old_manifest=read(OLD+"/manifest.json");old_summary=read(OLD+"/summary.json")
    old_tables=[]
    for u in range(84):
        name=f"domain_{u:02d}.json";record=read(OLD+"/"+name)
        assert bindings[OLD+"/"+name]==old_summary["output_sha256"][name]
        old_tables.append([int(s,16) for s in record["domain_masks_hex"]])
    assert old_summary["completed_centers"]==84 and sum(map(len,old_tables))==89308
    labels=[(2*a+s,2*b+t) for a,b in combinations(range(7),2) for s in (0,1) for t in (0,1)]
    supports=[{a//2 for a in pair} for pair in labels]
    all_K={tuple(e) for e in candidate["overlap_edges_outer_zero_based"]}
    allowed_Y=set()
    for symbol in (0,1,2,3):
        coordinate=[u for u,pair in enumerate(labels) if symbol in pair]
        legal={edge(u,v) for u,v in combinations(coordinate,2) if len(supports[u]&supports[v])==1}
        assert len(legal)==60
        allowed_Y|=legal
    removed=all_K&allowed_Y
    fixed=all_K-removed
    disjoint={edge(u,v) for u,v in combinations(range(84),2) if not supports[u]&supports[v]}
    unknown=sorted(disjoint|allowed_Y)
    old_fixed=set(map(tuple,old_manifest["remaining_fixed_K_edges_outer"]))
    def graph(fixed_edges):
        rows=[0]*99
        def put(a,b):
            rows[a]|=1<<b;rows[b]|=1<<a
        for u in range(1,15):put(0,u)
        for u in range(1,15,2):put(u,u+1)
        for u,pair in enumerate(labels,15):
            for symbol in pair:put(u,symbol+1)
        for u,v in fixed_edges:put(u+15,v+15)
        return rows
    rows=graph(fixed);old_rows=graph(old_fixed)
    affected=[u for u,pair in enumerate(labels) if any(s in (0,1,2,3) for s in pair)]
    needs=[14-rows[u+15].bit_count() for u in range(84)]
    assert len(fixed)==144 and len(unknown)==1920 and len(allowed_Y)==240 and len(removed)==24 and valid(rows)
    assert needs.count(10)==4 and needs.count(9)==40 and needs.count(8)==40
    assert fixed<=old_fixed and all_K-old_fixed<=removed
    for path in ("acceleration/theory_20260917_partial_matching.py",Path(__file__).relative_to(ROOT).as_posix(),"uv.lock"):
        bindings[path]=digest(ROOT/path)
    order=[0,4,24,44]+[u for u in range(84) if u not in (0,4,24,44)]
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        inputs_sha256=bindings,domain=DOMAIN,selection="Deterministically free same_0 and same_1 at root_groups0 and1; pilot centers0,4,24,44 then remaining labels ascending",
        enumeration_order=order,limits=dict(enumeration_seconds=180,nodes=20000000,per_center_domains=100000,total_domains=600000),
        scope="Retain144baselineK edges including all7cross matchings and10other same-sign matchings; all same-fibre and unlisted other-coordinate absences remain fixed. Unknown240same-sign edges in4root0/1coordinates plus1680disjoint-support edges.",
        remaining_fixed_K_edges_outer=sorted(fixed),removed_edges_outer=sorted(removed),
        freed_legal_matching_edges_outer=sorted(allowed_Y),unknown_edges_outer=unknown,
        affected_outer_vertices=affected,missing_neighbors="10at4centers,9at40centers,8at40centers",
        shared_code="Reuses frozen enumerate_star/direct_subset_ok/build helpers; new scope requires independent full domain audit, not merely old embedding",
        controls="Four preselected center restricted-universe brute checks and corrupted missing-edge controls; all89308 old choices embed by adding exactly removed old fixed neighbors and preserving full neighborhoods",
        checkpoint="Each completed center plus immutable checkpoint record is saved; cap interrupts only current center, previously saved domains reusable after hash validation",
        acceptance="Complete only if all84center searches exhaust without a cap. New domain IDs sorted by integer mask, unrelated to old IDs except explicit embedding map.",
        LP_gate="No LP in this run; independently audited full new domains and rechecked moment model required first",target_resolution=False)
    save(args.out/"manifest.json",manifest)
    started=time.monotonic();budget=dict(deadline=started+180,nodes=0,node_cap=20000000,domain_cap=100000)
    def old_embedding(u,mask):
        removed_neighbors=(old_rows[u+15]&~rows[u+15])>>15
        converted=mask|removed_neighbors
        assert ((old_rows[u+15]>>15)|mask)==((rows[u+15]>>15)|converted)
        return converted
    controls=[]
    for u in (0,4,24,44):
        selected=set(members(old_embedding(u,old_tables[u][0])))
        candidates={b if a==u else a for a,b in unknown if u in (a,b)}
        pool=selected|set(sorted(candidates-selected)[:2])
        actual,nodes,_=enumerate_star(rows,labels,unknown,u,budget,restricted=pool)
        expected=sorted(sum(1<<v for v in subset) for subset in combinations(sorted(pool),14-rows[u+15].bit_count()) if direct_subset_ok(rows,labels,u,subset))
        assert actual==expected and actual
        corrupt=actual[0]^(actual[0]&-actual[0])
        assert not direct_subset_ok(rows,labels,u,list(members(corrupt)))
        controls.append(dict(outer_vertex=u,pool=sorted(pool),accepted_masks_hex=[hex(m) for m in actual],exact_brute_agreement=True,corrupted_missing_edge="REJECTED"))
    save(args.out/"controls.json",controls)
    records=[];total=0;embedded=0;incomplete=None
    for u in tqdm(order,desc="Four freed matching coordinates",unit="center"):
        if time.monotonic()>=budget["deadline"]:
            incomplete=dict(outer_vertex=u,reason="TIME_CAP_BEFORE_CENTER");break
        try:
            masks,nodes,candidates=enumerate_star(rows,labels,unknown,u,budget)
        except Cap as exc:
            incomplete=dict(outer_vertex=u,reason=str(exc));break
        lookup={mask:i for i,mask in enumerate(masks)}
        mapping=[lookup[old_embedding(u,mask)] for mask in old_tables[u]]
        assert len(mapping)==len(set(mapping))
        record=dict(outer_vertex=u,domain=DOMAIN,status="CANDIDATE_COMPLETE_FOUR_COORDINATE_DOMAIN",
            domain_size=len(masks),domain_masks_hex=[hex(m) for m in masks],missing_neighbor_count=14-rows[u+15].bit_count(),
            allowed_single_neighbors=candidates,search_nodes=nodes,old_to_new_domain_ids=mapping,
            old_embedded_choices=len(mapping),full_outer_neighborhood_preserved=True)
        save(args.out/f"domain_{u:02d}.json",record)
        records.append({k:v for k,v in record.items() if k not in ("domain_masks_hex","old_to_new_domain_ids","allowed_single_neighbors")})
        total+=len(masks);embedded+=len(mapping)
        save(args.out/f"checkpoint_{len(records):02d}.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),completed_centers=[r["outer_vertex"] for r in records],
            complete_domain_choices=total,old_embedded_choices=embedded,search_nodes=budget["nodes"],elapsed_seconds=time.monotonic()-started,
            completed_domain_sha256={f"domain_{r['outer_vertex']:02d}.json":digest(args.out/f"domain_{r['outer_vertex']:02d}.json") for r in records}))
        if total>=600000:
            incomplete=dict(outer_vertex=u,reason="TOTAL_DOMAIN_CAP_AFTER_COMPLETE_CENTER",limit=600000,actual=total);break
    assert all(digest(ROOT/name)==h for name,h in bindings.items()),"Inputs changed"
    summary=dict(timestamp=datetime.now(timezone.utc).isoformat(),status="CANDIDATE_FOUR_COORDINATE_DOMAIN_PILOT",domain=DOMAIN,
        completed_centers=len(records),complete_domain_choices=total,old_embedded_choices=embedded,old_population=89308,
        incomplete=incomplete,complete_all_centers=len(records)==84 and incomplete is None,
        largest_completed_domain=max((r["domain_size"] for r in records),default=0),domains=records,
        search_nodes=budget["nodes"],elapsed_seconds=time.monotonic()-started,
        output_sha256={p.name:digest(p) for p in args.out.iterdir() if p.is_file()},independent_domain_review=False,
        LP_ran=False,LP_skipped_reason="Independent new-domain and model review required",family_exclusion_claimed=False,target_resolution=False)
    save(args.out/"summary.json",summary)
    print(json.dumps({k:summary[k] for k in ("completed_centers","complete_domain_choices","old_embedded_choices","largest_completed_domain","incomplete","search_nodes","elapsed_seconds")}))


if __name__=="__main__":
    main()
