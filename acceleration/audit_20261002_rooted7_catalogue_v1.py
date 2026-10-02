"""Independent full labelled-mask rooted7 catalogue exhaustion.

No discovery module or archive catalogue is imported. This checks catalogue
coverage only, not the candidate marked/reroot model or any LP conclusion.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime,timezone
import hashlib
from itertools import combinations,permutations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
CAT="acceleration/results/20261002_rooted7_extension_model/catalogue.json"
CAT_SHA="a01649d78eccfcb93c85ff2a86c84463458c120fd22cebaf34b8e573363084d5"
EDGES=tuple(combinations(range(7),2))
PERMUTATIONS=tuple((0,1,*free) for free in permutations(range(2,7)))


def need(value,why):
    if not value:raise ValueError(why)


def rows(mask):
    neighbors=[0]*7
    for bit,(a,b) in enumerate(EDGES):
        if mask & (1<<bit):neighbors[a]|=1<<b;neighbors[b]|=1<<a
    return neighbors


def admissible(neighbors):
    for a,b in EDGES:
        if (neighbors[a]&neighbors[b]).bit_count()>2-((neighbors[a]>>b)&1):return False
    return True


def orbit(neighbors):
    result=set()
    for mapping in PERMUTATIONS:
        image=0
        for bit,(a,b) in enumerate(EDGES):
            if neighbors[mapping[a]]&(1<<mapping[b]):image|=1<<bit
        result.add(image)
    return result


def prism(neighbors,selected):
    domain=sum(1<<vertex for vertex in selected)
    if any((neighbors[vertex]&domain).bit_count()!=3 for vertex in selected):return False
    for tail in combinations(selected[1:],2):
        first=(selected[0],*tail);other=tuple(vertex for vertex in selected if vertex not in first)
        if all(neighbors[a]&(1<<b) for a,b in combinations(first,2)) and all(neighbors[a]&(1<<b) for a,b in combinations(other,2)):return True
    return False


def prismfree(neighbors):return not any(prism(neighbors,selected) for selected in combinations(range(7),6))


def check_catalogue(raw,classes,filtered):
    need(raw["format"]=="COMPLETE_ROOTED7_ONE_VERTEX_AUGMENTATION_V1","frozen catalogue format")
    need(raw["complete_locally_admissible_masks"]==classes,"every producer root7 representative equals full independent exhaustion")
    need(raw["prismfree_masks"]==filtered,"every conditional prismfree representative equals independent filter")


def save(path,value):
    with path.open("x",encoding="utf-8",newline="\n") as stream:json.dump(value,stream,indent=2);stream.write("\n")


def run(args):
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason="Full1,048,576labelled fixed-nonedge-root7 masks, free-permutation orbits and complete prism filter;30seconds shutdown reserve")
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    pins={}
    def pin(path,wanted=None):
        path=path.resolve();actual=hashlib.sha256(path.read_bytes()).hexdigest();need(wanted is None or actual==wanted,"frozen checking bytes")
        pins[path.relative_to(ROOT).as_posix()]=actual
    try:
        pin(ROOT/CAT,CAT_SHA);raw=json.loads((ROOT/CAT).read_bytes())
        for path in [Path(__file__),ROOT/"uv.lock",ROOT/"pyproject.toml",ROOT/"acceleration/command_deadline.py",ROOT/"acceleration/run_compute_command.py"]:pin(path)
        # Independent explicit triangular prism plus isolated vertex control.
        triangle_edges={(0,1),(0,2),(1,2),(3,4),(3,5),(4,5),(0,3),(1,4),(2,5)}
        control_mask=sum(1<<bit for bit,edge in enumerate(EDGES) if edge in triangle_edges)
        control=rows(control_mask)
        need(admissible(control) and prism(control,tuple(range(6))) and not prismfree(control),"known triangular prism recognized")
        damaged=rows(control_mask^(1<<EDGES.index((0,3))))
        need(not prism(damaged,tuple(range(6))),"missing prism matching edge rejected")
        clique=sum(1<<bit for bit,(a,b) in enumerate(EDGES) if a<4 and b<4)
        need(not admissible(rows(clique)),"common-neighbor cap violation rejected")
        valid=set()
        for mask in tqdm(range(0,1<<21,2),desc="All labelled fixed-nonedge seven-vertex graphs",mininterval=5):
            if admissible(rows(mask)):valid.add(mask)
            if not mask%65536:need(not deadline.status()["stop_required"],"not completed within the allocated budget")
        complete_labelled=len(valid);classes=[];filtered=[];orbit_records=[]
        for mask in tqdm(sorted(valid),desc="Exact free-label orbit partition",mininterval=5):
            if mask not in valid:continue
            neighbors=rows(mask);images=orbit(neighbors)
            need(mask==min(images) and images<=valid,"complete remaining permutation orbit with least representative")
            valid.difference_update(images);classes.append(mask)
            keep=prismfree(neighbors)
            if keep:filtered.append(mask)
            orbit_records.append(dict(mask=mask,labelled_orbit_size=len(images),conditional_prismfree=keep))
            need(not deadline.status()["stop_required"],"not completed within the allocated budget")
        need(not valid and sum(record["labelled_orbit_size"] for record in orbit_records)==complete_labelled,"exact labelled population partition")
        check_catalogue(raw,classes,filtered)
        need(len(classes)==2770 and len(filtered)==2750,"saved finite class populations")
        rejected=[]
        for key in ["complete_locally_admissible_masks","prismfree_masks"]:
            damaged_catalogue=copy.deepcopy(raw);damaged_catalogue[key].pop()
            try:check_catalogue(damaged_catalogue,classes,filtered)
            except ValueError:rejected.append(key)
            else:raise ValueError("omitted catalogue member accepted")
        detail=dict(all_labelled_masks_of_fixed_nonedge=1<<20,admissible_labelled_masks=complete_labelled,
            complete_classes=classes,conditional_prismfree_classes=filtered,orbits=orbit_records)
        save(args.out/"catalogue_audit.json",detail);pin(args.out/"catalogue_audit.json")
        result=dict(status="INDEPENDENT_COMPLETE_ROOTED7_CATALOGUE_COVERAGE_PASS",timestamp=datetime.now(timezone.utc).isoformat(),
            verifier="/root/checkpoint_audit",producer="/root/structural",method="independent_derivation",
            source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
            statement="Full exhaustion of all1,048,576labelled simple seven-vertex graphs with fixed ordered nonadjacent roots and local common-neighbor caps1/2 gives exactly the saved2770free-label rooted classes; absence of any induced triangular prism gives exactly the saved2750-class subcatalogue.",
            all_labelled_masks_of_fixed_nonedge=1<<20,admissible_labelled_masks=complete_labelled,complete_rooted_classes=2770,conditional_prismfree_classes=2750,
            controls=dict(known_prism_detected=True,missing_prism_edge_rejected=True,common_neighbor_cap_violation_rejected=True,omitted_catalogue_members_rejected=rejected),
            scope="Exact finite catalogue coverage only; small flagged-graph permutation classes do not assume automorphisms of a hypothetical target.",
            limitations=["The rooted7 marked/rerooted necessary model and any numerical/certified LP conclusions are not checked by this catalogue audit.","Prism-free applicability to a hypothetical target is conditional; the premise remains UNKNOWN.","No construction, exclusion, novelty or target-wide search coverage percentage is established."],
            shared_components=["Python bit integers, permutations, JSON/SHA-256, locked environment and contained deadline; no discovery or archived catalogue code imported."],
            new_exclusions=0,target_resolution=False,artifact_availability="LOCAL_ONLY",elapsed_seconds=time.monotonic()-start)
        save(args.out/"summary.json",result);print(json.dumps(dict(status=result["status"],sha256=hashlib.sha256((args.out/"summary.json").read_bytes()).hexdigest(),elapsed_seconds=result["elapsed_seconds"])),flush=True)
    except BaseException as error:
        save(args.out/"failure.json",dict(error=repr(error),elapsed_seconds=time.monotonic()-start,target_resolution=False));raise


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--seconds",type=float,required=True);parser.add_argument("--out",type=Path,required=True);run(parser.parse_args())
