"""Exact raw-neighborhood transfer to all four-coordinate local stars."""
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
from tqdm import tqdm
from theory_20260917_partial_matching_moments import digest,save

ROOT=Path(__file__).resolve().parents[1]
DOMAIN="acceleration/results/20260917_partial_four_matchings"
OLDMODEL="acceleration/results/20260917_two_matching_moments/model.json"
OLDCERT="acceleration/results/20260917_two_matching_moments/exact_support_bound.json"
OUT=ROOT/"acceleration/results/20260917_four_matching_transferred_certificate"


def main():
    OUT.mkdir(exist_ok=True);assert not any(OUT.iterdir())
    bindings={}
    def read(name):
        bindings[name]=digest(ROOT/name)
        return json.loads((ROOT/name).read_bytes())
    domain=read(DOMAIN+"/manifest.json");summary=read(DOMAIN+"/summary.json")
    old=read(OLDMODEL);cert=read(OLDCERT)["bound"]
    tables=[]
    for u in range(84):
        name=f"domain_{u:02d}.json";r=read(DOMAIN+"/"+name)
        assert bindings[DOMAIN+"/"+name]==summary["output_sha256"][name]
        tables.append([int(s,16) for s in r["domain_masks_hex"]])
    for name in (Path(__file__).relative_to(ROOT).as_posix(),"acceleration/theory_20260917_partial_matching_moments.py","uv.lock"):
        bindings[name]=digest(ROOT/name)
    assert summary["complete_all_centers"] and sum(map(len,tables))==290460
    save(OUT/"manifest.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),inputs_sha256=bindings,
        selection="One exact transfer from verifiedtwo-coordinate weights: unchanged3486y;1800q mapped byunorderededge;120newq=0; no sign/weight optimization",
        arithmetic="Python integer raw-neighborhood sums for every290460star; fullneighbor66pair weights +smallerendpointprojection +signedreciprocity; new RHS from supportintersection/fixed144edges",
        scope=domain["scope"],criterion="Strictlypositive exact bound candidate exclusion only after independent completeness/necessity/arithmetic checking",
        old_certificate_not_inherited=True,LP_model_required=False,solver_run=False,target_resolution=False))
    pairs=list(combinations(range(84),2));assert pairs==list(map(tuple,old["pair_order"]))
    y={e:int(v) for e,v in zip(pairs,cert["moment_weight_numerators"])}
    oldq={tuple(e):int(q) for e,q in zip(old["unknown_edges"],cert["reciprocity_weight_numerators"])}
    unknown=list(map(tuple,domain["unknown_edges_outer"]))
    assert set(oldq)<=set(unknown) and len(unknown)-len(oldq)==120
    q={e:oldq.get(e,0) for e in unknown}
    fixed=set(map(tuple,domain["remaining_fixed_K_edges_outer"]))
    assert len(fixed)==144 and len(q)==1920
    neighbors=[set() for _ in range(84)]
    for a,b in fixed:neighbors[a].add(b);neighbors[b].add(a)
    supports=[{2*a+s,2*b+t} for a,b in combinations(range(7),2) for s in (0,1) for t in (0,1)]
    denominator=cert["denominator"];assert all(abs(v)<=denominator for v in y.values())
    rhs=[2-len(supports[a]&supports[b])-int((a,b) in fixed) for a,b in pairs]
    rhsdot=sum(y[e]*b for e,b in zip(pairs,rhs))
    maxima=[];argmax=[]
    for u in tqdm(range(84),desc="Exact four-coordinate raw transfer",unit="center"):
        best=None;best_id=None
        for j,mask in enumerate(tables[u]):
            selected=[v for v in range(84) if mask>>v&1]
            full=sorted(neighbors[u]|set(selected));assert len(full)==12
            value=sum(y[e] for e in combinations(full,2))
            for v in selected:
                e=(min(u,v),max(u,v))
                value+=(q[e]+y[e]) if u<v else -q[e]
            if best is None or value>best:best,best_id=value,j
        maxima.append(best);argmax.append(best_id)
    numerator=rhsdot-sum(maxima)
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),status="CANDIDATE_RAW_NEIGHBORHOOD_TRANSFER_BOUND",
        numerator=numerator,denominator=denominator,approximate=numerator/denominator,strictly_positive=numerator>0,
        moment_weight_numerators=[y[e] for e in pairs],reciprocity_weight_numerators=[q[e] for e in unknown],
        unknown_edge_order=unknown,pair_order=pairs,rhs=rhs,rhs_dot_numerator=rhsdot,
        center_maxima_numerators=maxima,maximizing_new_domain_ids=argmax,checked_columns=290460,checked_centers=84,
        added_zero_reciprocity_edges=[e for e in unknown if e not in oldq],independent_review_pending=True,target_resolution=False)
    assert all(digest(ROOT/name)==h for name,h in bindings.items())
    save(OUT/"certificate.json",result)
    save(OUT/"summary.json",dict(timestamp=result["timestamp"],status="CANDIDATE",numerator=numerator,denominator=denominator,
        approximate=numerator/denominator,strictly_positive=numerator>0,certificate_sha256=digest(OUT/"certificate.json"),
        manifest_sha256=digest(OUT/"manifest.json"),solver_run=False,independent_review_pending=True,target_resolution=False))
    print(json.dumps({k:result[k] for k in ("numerator","denominator","approximate","strictly_positive")}))


if __name__=="__main__":main()
