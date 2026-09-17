"""Complete-domain pilot freeing both root-group0 same-sign coordinates."""
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
OLD="acceleration/results/20260917_partial_matching"
DOMAIN="PARTIAL_K_TWO_SAME_SIGN_COORDINATES_ROOT0_V1"


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
    assert old_summary["completed_centers"]==84 and sum(map(len,old_tables))==54478
    labels,rows,old_unknown,affected0,removed0,old_fixed,Y0=build(candidate)
    old_rows=rows[:]
    affected1=[u for u,pair in enumerate(labels) if 1 in pair]
    supports=[{a//2 for a in pair} for pair in labels]
    Y1={edge(u,v) for u,v in combinations(affected1,2) if len(supports[u]&supports[v])==1}
    removed1=set(map(tuple,old_fixed))&Y1
    assert len(Y1)==60 and len(removed1)==6
    for u,v in removed1:
        rows[u+15]&=~(1<<(v+15));rows[v+15]&=~(1<<(u+15))
    fixed=set(map(tuple,old_fixed))-removed1
    unknown=sorted(set(old_unknown)|Y1)
    affected=sorted(affected0+affected1)
    assert len(fixed)==156 and len(unknown)==1800 and len(set(affected))==24 and valid(rows)
    assert all(rows[u+15].bit_count()==(5 if u in affected else 6) for u in range(84))
    for path in ("acceleration/theory_20260917_partial_matching.py",Path(__file__).relative_to(ROOT).as_posix(),"uv.lock"):
        bindings[path]=digest(ROOT/path)
    order=[0,2,24]+[u for u in range(84) if u not in (0,2,24)]
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        inputs_sha256=bindings,domain=DOMAIN,selection="Deterministically free same_0 and same_1 at root_group0; pilot centers0,2,24 then remaining labels ascending",
        enumeration_order=order,limits=dict(enumeration_seconds=180,nodes=10000000,per_center_domains=1000000,total_domains=200000),
        scope="Retain156baselineK edges including all7cross matchings and12other same-sign matchings; all same-fibre and unlisted other-coordinate absences remain fixed. Unknown120same-sign edges in2root0coordinates plus1680disjoint-support edges.",
        remaining_fixed_K_edges_outer=sorted(fixed),removed_edges_outer=sorted(set(map(tuple,removed0))|removed1),
        freed_legal_matching_edges_outer=sorted(set(map(tuple,Y0))|Y1),unknown_edges_outer=unknown,
        affected_outer_vertices=affected,missing_neighbors="9at24affected centers,8at60others",
        shared_code="Reuses frozen enumerate_star/direct_subset_ok/build helpers; new scope requires independent full domain audit, not merely old embedding",
        controls="Three preselected center restricted-universe brute checks and corrupted missing-edge controls; all54478 old choices embed by adding exactly removed old fixed neighbors and preserving full neighborhoods",
        checkpoint="Each completed center plus immutable checkpoint record is saved; cap interrupts only current center, previously saved domains reusable after hash validation",
        acceptance="Complete only if all84center searches exhaust without a cap. New domain IDs sorted by integer mask, unrelated to old IDs except explicit embedding map.",
        LP_gate="No LP in this run; independently audited full new domains and rechecked moment model required first",target_resolution=False)
    save(args.out/"manifest.json",manifest)
    started=time.monotonic();budget=dict(deadline=started+180,nodes=0,node_cap=10000000,domain_cap=1000000)
    def old_embedding(u,mask):
        removed_neighbors=(old_rows[u+15]&~rows[u+15])>>15
        converted=mask|removed_neighbors
        assert ((old_rows[u+15]>>15)|mask)==((rows[u+15]>>15)|converted)
        return converted
    controls=[]
    for u in (0,2,24):
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
    for u in tqdm(order,desc="Two freed matching coordinates",unit="center"):
        if time.monotonic()>=budget["deadline"]:
            incomplete=dict(outer_vertex=u,reason="TIME_CAP_BEFORE_CENTER");break
        try:
            masks,nodes,candidates=enumerate_star(rows,labels,unknown,u,budget)
        except Cap as exc:
            incomplete=dict(outer_vertex=u,reason=str(exc));break
        lookup={mask:i for i,mask in enumerate(masks)}
        mapping=[lookup[old_embedding(u,mask)] for mask in old_tables[u]]
        assert len(mapping)==len(set(mapping))
        record=dict(outer_vertex=u,domain=DOMAIN,status="CANDIDATE_COMPLETE_TWO_COORDINATE_DOMAIN",
            domain_size=len(masks),domain_masks_hex=[hex(m) for m in masks],missing_neighbor_count=14-rows[u+15].bit_count(),
            allowed_single_neighbors=candidates,search_nodes=nodes,old_to_new_domain_ids=mapping,
            old_embedded_choices=len(mapping),full_outer_neighborhood_preserved=True)
        save(args.out/f"domain_{u:02d}.json",record)
        records.append({k:v for k,v in record.items() if k not in ("domain_masks_hex","old_to_new_domain_ids","allowed_single_neighbors")})
        total+=len(masks);embedded+=len(mapping)
        save(args.out/f"checkpoint_{len(records):02d}.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),completed_centers=[r["outer_vertex"] for r in records],
            complete_domain_choices=total,old_embedded_choices=embedded,search_nodes=budget["nodes"],elapsed_seconds=time.monotonic()-started,
            completed_domain_sha256={f"domain_{r['outer_vertex']:02d}.json":digest(args.out/f"domain_{r['outer_vertex']:02d}.json") for r in records}))
        if total>=200000:
            incomplete=dict(outer_vertex=u,reason="TOTAL_DOMAIN_CAP_AFTER_COMPLETE_CENTER",limit=200000,actual=total);break
    assert all(digest(ROOT/name)==h for name,h in bindings.items()),"Inputs changed"
    summary=dict(timestamp=datetime.now(timezone.utc).isoformat(),status="CANDIDATE_TWO_COORDINATE_DOMAIN_PILOT",domain=DOMAIN,
        completed_centers=len(records),complete_domain_choices=total,old_embedded_choices=embedded,old_population=54478,
        incomplete=incomplete,complete_all_centers=len(records)==84 and incomplete is None,
        largest_completed_domain=max((r["domain_size"] for r in records),default=0),domains=records,
        search_nodes=budget["nodes"],elapsed_seconds=time.monotonic()-started,
        output_sha256={p.name:digest(p) for p in args.out.iterdir() if p.is_file()},independent_domain_review=False,
        LP_ran=False,LP_skipped_reason="Independent new-domain and model review required",family_exclusion_claimed=False,target_resolution=False)
    save(args.out/"summary.json",summary)
    print(json.dumps({k:summary[k] for k in ("completed_centers","complete_domain_choices","old_embedded_choices","largest_completed_domain","incomplete","search_nodes","elapsed_seconds")}))


if __name__=="__main__":
    main()
