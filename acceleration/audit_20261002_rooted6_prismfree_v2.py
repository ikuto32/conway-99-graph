"""Independent complete conditional ordered-edge rooted6 rigidity audit v2.

Only prior independent small-graph geometry/rank helpers are shared. No
discovery modules, canonical transport code, numerical solver or model builder
are imported. A prism-free hypothesis remains explicit throughout.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261002_rooted5_rigidity_v2 as independent

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "acceleration/results/20261002_rooted6_prismfree_rigidity"
PINS = {
    "ordered_edge_model.json": "06051294a142dfcda956f4ee3748986982f7f8ba5f9785fe4d7680d967538584",
    "ordered_edge_prismfree_rows.json": "034cf6d54c71b91390dbc2ebb68fab6be6f648ca64118f33b2d9b8f9d2103449",
    "ordered_edge_prismfree_primal.json": "8c914f27e91f5c003644148738b9a634ac0dfe9683915dd42dc3ae067d2a2010",
}
HELPER_SHA = "b281675c501cbf49116b2c1f6cfd6beb55d0bdf00b0bacc34bf8e9b42660f0ed"


def need(value, reason):
    if not value:
        raise ValueError(reason)


def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def basis(deadline):
    classes, inventories = {}, []
    for order in tqdm(range(2, 7), desc="Independent rooted-edge bases"):
        admissible = set()
        for mask in range(1, 1 << len(independent.pairs(order)), 2):
            if independent.caps(independent.matrix(order, mask)):
                admissible.add(mask)
        count = len(admissible)
        representatives = []
        while admissible:
            mask = min(admissible)
            images = independent.orbit(order, mask)
            need(images <= admissible, "entire necessary rooted orbit exhausted")
            representatives.append(min(images))
            admissible.difference_update(images)
        classes[order] = representatives
        inventories.append(dict(order=order, all_simple_masks=1 << len(independent.pairs(order)),
            ordered_edge_admissible_labelled_masks=count, complete_rooted_classes=len(representatives)))
        need(not deadline.status()["stop_required"], "not completed within the allocated budget")
    return classes, inventories


def reconstruct(classes, n, k, deadline):
    """Accumulate from each larger graph; independently try every lower isomorphism."""
    variables = [(h, mask) for h in range(2, 7) for mask in classes[h]]
    index = {value: at for at, value in enumerate(variables)}
    rows = [dict(kind="total", order=h, mask=None, mark=None,
        terms=[[index[h, mask], 1] for mask in classes[h]], rhs=math.comb(n-2, h-2)) for h in range(2, 7)]
    transport_checks = 0
    for h in tqdm(range(2, 6), desc="Independent marked extension rows"):
        descriptors, coefficients = {}, {}
        for mask in classes[h]:
            graph = independent.matrix(h, mask)
            marks = independent.mark_orbits(h, mask)
            desc = [("deletion", None, n-h)]
            for orbit in marks:
                if len(orbit[0]) == 1:
                    desc.append(("degree", orbit, sum(k-sum(graph[u]) for (u,) in orbit)))
                else:
                    desc.append(("common_neighbor", orbit,
                        sum(2-graph[u][v]-sum(graph[u][w]*graph[v][w] for w in range(h)) for u,v in orbit)))
            descriptors[mask] = desc
            coefficients[mask] = [Counter({index[h,mask]: -constant}) if constant else Counter() for _,_,constant in desc]
        for bigmask in classes[h+1]:
            big = independent.matrix(h+1, bigmask)
            for removed in range(2, h+1):
                free = [v for v in range(2, h+1) if v != removed]
                lower = independent.bits(big, (0, 1, *free))
                canonical = min(independent.orbit(h, lower))
                # A map labels the fixed canonical lower class using actual
                # vertices of big; every such map is tested, not just one.
                maps = [(0,1,*tail) for tail in independent.permutations(free)
                    if independent.bits(big, (0,1,*tail)) == canonical]
                need(maps, "every deletion has an explicit root-fixing isomorphism")
                for at, (kind, mark, _) in enumerate(descriptors[canonical]):
                    values = [1 if kind == "deletion" else
                        sum(all(big[removed][mapping[u]] for u in marked) for marked in mark) for mapping in maps]
                    need(len(set(values)) == 1, "marked coefficient invariant under every root-fixing isomorphism")
                    transport_checks += len(values)
                    if values[0]:
                        coefficients[canonical][at][index[h+1,bigmask]] += values[0]
            need(not deadline.status()["stop_required"], "not completed within the allocated budget")
        for mask in classes[h]:
            for (kind, mark, _), counter in zip(descriptors[mask], coefficients[mask]):
                rows.append(dict(kind=kind, order=h, mask=mask,
                    mark=None if mark is None else [list(value) for value in mark],
                    terms=[[col, value] for col,value in sorted(counter.items()) if value], rhs=0))
    return variables, rows, transport_checks


def prism(mask):
    graph = independent.matrix(6, mask)
    if any(sum(row) != 3 for row in graph):
        return False
    for first in independent.combinations(range(6), 3):
        other = tuple(v for v in range(6) if v not in first)
        if all(graph[u][v] for u,v in independent.combinations(first,2)) and all(graph[u][v] for u,v in independent.combinations(other,2)):
            if all(sum(graph[u][v] for v in other)==1 for u in first) and all(sum(graph[u][v] for u in first)==1 for v in other):
                return True
    return False


def count_root(graph, root, variables):
    counts = Counter()
    free = [v for v in range(len(graph)) if v not in root]
    for order in range(2, 7):
        for tail in independent.combinations(free, order-2):
            raw = independent.bits(graph, (*root,*tail))
            counts[order, min(independent.orbit(order,raw))] += 1
    need(set(counts) <= set(variables), "actual valid fixture belongs to entire necessary flag basis")
    return [counts[value] for value in variables]


def rows_hold(values, rows):
    return all(sum(value*values[col] for col,value in row["terms"])==row["rhs"] for row in rows)


def run(args):
    start = time.monotonic()
    deadline = CommandDeadline(args.seconds, allocation_reason="Complete rooted6 ordered-edge basis, every marked row, independent modular rank and exact primal plus all36 known-valid rook roots; reserve30seconds shutdown")
    args.out.mkdir(parents=True, exist_ok=False)
    pins = {}
    def pin(path, wanted=None):
        path = path.resolve()
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        need(wanted is None or actual==wanted, "frozen raw input: "+path.name)
        pins[path.relative_to(ROOT).as_posix()] = actual
    try:
        pin(ROOT/"acceleration/audit_20261002_rooted5_rigidity_v2.py", HELPER_SHA)
        raw = {}
        for name, identity in PINS.items():
            pin(DATA/name, identity)
            raw[name] = json.loads((DATA/name).read_bytes())
        pin(DATA/"manifest.json")
        pin(DATA/"summary.json")
        pin(Path(__file__).resolve())
        pin(ROOT/"acceleration/command_deadline.py")
        pin(ROOT/"acceleration/run_compute_command.py")
        pin(ROOT/"uv.lock")
        pin(ROOT/"pyproject.toml")
        pin(ROOT/"acceleration/audit_20261002_rooted6_prismfree_v1_spec.md")
        # Calibrate shared exact rank routine against independently obvious
        # full/deficient integer matrices before new research derivation.
        full = [dict(terms=[[0,1],[1,2]]),dict(terms=[[0,3],[1,4]])]
        deficient = [dict(terms=[[0,1],[1,2]]),dict(terms=[[0,2],[1,4]])]
        need(independent.modular_rank(full,2,1009)["rank"]==2 and independent.modular_rank(deficient,2,1009)["rank"]==1, "positive and rank-deficient controls")
        classes, inventories = basis(deadline)
        variables, rows, transports = reconstruct(classes,99,14,deadline)
        model = raw["ordered_edge_model.json"]
        need(model["adjacent_roots"] is True, "ordered-edge root relation")
        independent.verify_model(model,variables,rows)
        prism_indices = [at for at,(order,mask) in enumerate(variables) if order==6 and prism(mask)]
        added = [dict(kind="prismfree",order=6,mask=variables[at][1],mark=None,terms=[[at,1]],rhs=0) for at in prism_indices]
        need(added==raw["ordered_edge_prismfree_rows.json"] and len(added)==2, "all and only prism-rooted basis coordinates zero")
        conditional = [*rows,*added]
        rank = independent.modular_rank(conditional,len(variables),1009)
        need(rank["rank"]==len(variables), "independent full rational rank from a prime maximal minor")
        solution = raw["ordered_edge_prismfree_primal.json"]["exact_primal"]
        need(len(solution)==len(variables) and all(type(value) is int and value>=0 for value in solution), "complete exact nonnegative integer vector")
        need(rows_hold(solution,conditional), "all1101 independently reconstructed equations exactly satisfied")
        corrupt_solution = list(solution)
        corrupt_solution[0] += 1
        need(not rows_hold(corrupt_solution,conditional), "corrupted endpoint count rejected")
        damaged_model = copy.deepcopy(model)
        damaged_model["equations"][0]["terms"][0][1] += 1
        try:
            independent.verify_model(damaged_model,variables,rows)
        except ValueError:
            pass
        else:
            raise ValueError("corrupted raw coefficient accepted")
        # Necessary rows are also calibrated on a genuine9-vertex rook graph;
        # it contains prisms, so deliberately must fail the prism-free rows.
        rook = [[int(a!=b and (a//3==b//3 or a%3==b%3)) for b in range(9)] for a in range(9)]
        need(independent.graph_is_srg(rook,4), "exact known-valid srg(9,4,1,2) control")
        fixture_variables, fixture_rows, _ = reconstruct(classes,9,4,deadline)
        need(fixture_variables==variables, "same necessary rooted basis in smaller SRG control")
        controls = []
        for a,b in independent.permutations(range(9),2):
            if not rook[a][b]:
                continue
            counts = count_root(rook,(a,b),variables)
            need(rows_hold(counts,fixture_rows), "every necessary row for every actual rook ordered-edge root")
            need(any(counts[at] for at in prism_indices), "known prism-bearing fixture fails conditional zero requirements")
            controls.append(dict(root=[a,b], necessary_rows="PASS", conditional_prismfree="REJECT"))
        need(len(controls)==36, "all actual ordered-edge roots in fixture covered")
        forced = [dict(mask=mask,count=solution[at]) for at,(order,mask) in enumerate(variables) if order==6]
        need(len(forced)==307 and sum(item["count"] for item in forced)==math.comb(97,4), "complete unordered four-free-vertex population")
        detail = dict(variables=[list(value) for value in variables], reconstructed_rows=rows,
            independent_prism_rows=added, exact_primal=solution, modular_rank=rank,
            basis_inventory=inventories, all_isomorphism_marked_value_checks=transports,
            forced_six_flag_vector=forced, known_valid_controls=controls)
        save(args.out/"ordered_edge_audit.json",detail)
        pin(args.out/"ordered_edge_audit.json")
        result = dict(status="INDEPENDENT_CONDITIONAL_PRISMFREE_ROOTED6_EDGE_RIGIDITY_PASS",
            timestamp=datetime.now(timezone.utc).isoformat(), verifier="/root/checkpoint_audit", producer="/root/structural",
            method="independent_derivation", source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
            statement="For every prism-free srg(99,14,1,2) and every actual ordered adjacent root, the complete saved 394-coordinate rooted-flag count vector through order6 is the unique exact solution of the independently reconstructed necessary equations and prism-zero constraints; hence its 307 six-flag counts equal the saved exact nonnegative integers.",
            scope="Conditional on absence of induced triangular prisms in the hypothetical unrestricted target. No target automorphism, fixed support or other configuration is assumed.",
            variables=len(variables),necessary_rows=len(rows),prism_zero_rows=len(added),conditional_rows=len(conditional),rank_over_Q=rank["rank"],
            exact_six_flag_population=len(forced),unordered_four_free_vertex_population=math.comb(97,4),
            controls=dict(rank_full_and_deficient=True,corrupted_count_rejected=True,corrupted_coefficient_rejected=True,
                known_valid_rook_ordered_edges=36,necessary_rows_per_root=len(rows),prism_bearing_fixture_conditional_rejections=36),
            new_exclusions=0,target_resolution=False,prismfree_premise_established=False,
            shared_components=["Prior independent rooted5 checker supplies adjacency/orbit/DSU marks and Python modular rank; same verifier's source pinned. No producer modules or numerical solver imported.","Python exact integer arithmetic, JSON/SHA-256, pinned uv environment and contained deadline."],
            limitations=["The absence of triangular prisms is an unestablished premise for a general target graph.","A nonnegative exact necessary count vector does not construct a graph or prove feasibility.","No exact rational nullity or rigidity is asserted for the nonedge model or unconditional edge model.","No novelty or literature priority is asserted.","Version1 completed finite checks but stopped while recording a relative output path against the absolute repository root. Its source/detail/failure receipt remain unchanged. Version2 resolves identity paths before bookkeeping; mathematical checks are unchanged."],
            artifact_availability="LOCAL_ONLY",elapsed_seconds=time.monotonic()-start)
        save(args.out/"summary.json",result)
        print(json.dumps(dict(status=result["status"],sha256=hashlib.sha256((args.out/"summary.json").read_bytes()).hexdigest(),elapsed_seconds=result["elapsed_seconds"])),flush=True)
    except BaseException as error:
        save(args.out/"failure.json",dict(error=repr(error),elapsed_seconds=time.monotonic()-start,target_resolution=False))
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--seconds",type=float,required=True)
    run(parser.parse_args())
