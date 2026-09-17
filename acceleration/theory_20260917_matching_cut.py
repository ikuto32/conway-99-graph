"""Candidate reusable positive-adjacency nogoods from local matching failures.

No fixed-K zero edge is treated as permanently absent. This producer does not
approve its mathematical output; independent review is required.
"""
import argparse
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
BASE = "acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json"
DOMAINS = "acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/local/stars.json"
OLD = "acceleration/results/20260917_theory/matching_baseline18481/summary.json"


def stamp():
    return datetime.now(timezone.utc).isoformat()


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2)
        f.write("\n")


def put(rows, a, b):
    rows[a] |= 1 << b
    rows[b] |= 1 << a


def members(mask):
    return [i for i in range(mask.bit_length()) if mask >> i & 1]


def scaffold():
    rows = [0] * 99
    for r in range(1, 15):
        put(rows, 0, r)
    for r in range(1, 15, 2):
        put(rows, r, r+1)
    labels = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2) for s in range(2) for t in range(2)]
    for u, label in enumerate(labels, 15):
        for s in label:
            put(rows, u, s+1)
    return rows


def rows_from(core, center, selected):
    rows = scaffold()
    for a, b in core:
        put(rows, a, b)
    for v in selected:
        put(rows, center, v)
    return rows


def cap_violation(rows):
    for a, b in combinations(range(len(rows)), 2):
        common = (rows[a] & rows[b]).bit_count()
        bound = 2 - int(bool(rows[a] >> b & 1))
        if common > bound:
            return dict(pair=[a, b], common=common, bound=bound)
    return None


def insertion_blocker(rows, a, b):
    # Every missing edge between free neighbors is considered, even an edge
    # omitted from the original complete overlap assignment.
    for v in (a, b):
        if rows[v].bit_count() >= 14:
            return dict(kind="degree", vertex=v, present_neighbors=members(rows[v]))
    old_a, old_b = rows[a], rows[b]
    put(rows, a, b)
    blocker = None
    for u in (a, b):
        for v in range(len(rows)):
            if u == v:
                continue
            common_vertices = rows[u] & rows[v]
            bound = 2 - int(bool(rows[u] >> v & 1))
            if common_vertices.bit_count() > bound:
                blocker = dict(kind="pair_cap", pair=sorted([u, v]), bound=bound,
                               common_vertices=members(common_vertices))
                break
        if blocker:
            break
    rows[a], rows[b] = old_a, old_b
    return blocker


def matching_exists(nodes, edges):
    where = {v: i for i, v in enumerate(nodes)}
    neighbors = [0] * len(nodes)
    for a, b in edges:
        i, j = where[a], where[b]
        neighbors[i] |= 1 << j
        neighbors[j] |= 1 << i
    @lru_cache(None)
    def possible(mask):
        if not mask:
            return True
        i = (mask & -mask).bit_length()-1
        rest = mask ^ (1 << i)
        return any(possible(rest ^ (1 << j)) for j in members(rest & neighbors[i]))
    return possible((1 << len(nodes))-1)


def condition(rows, center, with_blockers=False):
    neighborhood = members(rows[center])
    assert len(neighborhood) == 14
    forced = [(a, b) for a, b in combinations(neighborhood, 2) if rows[a] >> b & 1]
    used = [v for e in forced for v in e]
    assert len(set(used)) == len(used), "Input neighborhood violates adjacent caps"
    free = [v for v in neighborhood if v not in used]
    edges, blocked = [], []
    for a, b in combinations(free, 2):
        assert not rows[a] >> b & 1
        reason = insertion_blocker(rows, a, b)
        if reason is None:
            edges.append([a, b])
        elif with_blockers:
            blocked.append(dict(edge=[a, b], reason=reason))
    return dict(neighborhood=neighborhood, forced_edges=forced, free_vertices=free,
                possible_edges=edges, blocked_edges=blocked,
                matching_exists=matching_exists(free, edges))


def odd_component_witness(nodes, edges):
    adjacent = {v: set() for v in nodes}
    for a, b in edges:
        adjacent[a].add(b)
        adjacent[b].add(a)
    for size in range(len(nodes)+1):
        for removed in combinations(nodes, size):
            rest = set(nodes) - set(removed)
            components = []
            while rest:
                start = min(rest)
                rest.remove(start)
                todo, component = [start], [start]
                while todo:
                    v = todo.pop()
                    additions = adjacent[v] & rest
                    rest -= additions
                    todo.extend(additions)
                    component.extend(additions)
                components.append(sorted(component))
            odd = [c for c in components if len(c) % 2]
            if len(odd) > size:
                return dict(separator=list(removed), components=components,
                            odd_component_count=len(odd), separator_size=size,
                            deficiency=len(odd)-size)
    return None


def controls():
    checks = []
    for name, nodes, edges, expected in (
        ("K4", list(range(4)), list(combinations(range(4), 2)), True),
        ("two_odd_components", list(range(6)), [[0, 1], [1, 2], [0, 2], [3, 4], [4, 5], [3, 5]], False),
        ("bridge_repairs_odd_components", list(range(6)), [[0, 1], [1, 2], [0, 2], [3, 4], [4, 5], [3, 5], [2, 3]], True),
        ("empty_graph", [], [], True),
    ):
        assert matching_exists(nodes, edges) is expected
        witness = odd_component_witness(nodes, edges)
        assert (witness is None) is expected
        checks.append(dict(name=name, expected=expected, outcome="PASS"))
    rows = [0]*99
    for v in range(1, 15):
        put(rows, 0, v)
    assert condition(rows, 0)["matching_exists"]
    put(rows, 1, 2)
    assert insertion_blocker(rows, 1, 3) is not None
    assert condition(rows, 0)["matching_exists"]
    put(rows, 1, 3)
    assert cap_violation(rows) is not None
    checks.append(dict(name="windmill_missing_edges_allowed_and_corrupt_second_pair_rejected", outcome="PASS"))
    return checks


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seconds", type=float, default=240)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    bindings = {}
    def read(name):
        bindings[name] = digest(ROOT / name)
        return json.loads((ROOT / name).read_bytes())
    candidate, domains, old = read(BASE), read(DOMAINS), read(OLD)
    assert len(candidate["overlap_edges_outer_zero_based"]) == 168
    core_full = [tuple(sorted((a+15, b+15))) for a, b in candidate["overlap_edges_outer_zero_based"]]
    population = []
    for directory in ("acceleration/results/20260917_fresh_star_shortlist", "acceleration/results/20260917_same_star_round/star_shortlist"):
        summary = read(directory + "/summary.json")
        for row in summary["records"]:
            if row["audited"]:
                phase = read(directory + f"/index_{row['proposal_index']}/phase1.json")
                name = phase["candidate_path"].replace("\\", "/")
                doc = read(name)
                population.append(dict(path=name, edges={tuple(sorted((a+15, b+15))) for a, b in doc["overlap_edges_outer_zero_based"]}))
    selections = [dict(outer_vertex=u, domain_id=old["vertices"][u]["removed_domain_ids"][0]) for u in range(16)]
    survivors = [dict(outer_vertex=u, domain_id=old["vertices"][u]["survivor_domain_ids"][0]) for u in range(8)]
    source = "acceleration/theory_20260917_matching_cut.py"
    bindings[source], bindings["uv.lock"] = digest(ROOT / source), digest(ROOT / "uv.lock")
    manifest = dict(timestamp=stamp(), source_commit=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(),
                    command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()), python=platform.python_version(),
                    question="Do positive-edge-only matching obstructions remain after lifting all fixed-K absent-edge restrictions, and can their K support be reduced?",
                    scope="16 deterministic baseline rejected stars; 8 surviving controls; containment only in the saved fresh16/same13 population",
                    selection_rule="First rejected original domain ID at each outer vertex0..15; first survivor at each vertex0..7",
                    selected=selections, survivor_controls=survivors, inputs_sha256=bindings,
                    falsification="If permissive graph admits a matching, old fixed-K rejection does not produce this positive-edge cut; preserve that failure",
                    success="No perfect matching after allowing every missing free-neighbor edge passing exact degree/cap checks; save odd-component separator and all blockers",
                    acceptance_threshold="Exact Boolean/integer statements only", numerical_thresholds=None,
                    numerical_thresholds_reason="No floating-point optimization used", time_limit_seconds=args.seconds,
                    pruning="Greedy sorted K-edge deletions; center-incident K edges never removed; no known-absent K literal is retained",
                    status="PREREGISTERED_CANDIDATE_PRODUCER", independent_verification=False)
    save(args.out / "manifest.json", manifest)
    started = time.monotonic()
    checks = controls()
    survivor_results = []
    for selection in survivors:
        u, d = selection["outer_vertex"], selection["domain_id"]
        selected = [v+15 for v in members(int(domains["domains"][u]["domain_masks_hex"][d], 16))]
        result = condition(rows_from(core_full, u+15, selected), u+15)
        assert result["matching_exists"], "Relaxed graph rejected old positive control"
        survivor_results.append(dict(**selection, result="MATCHING_EXISTS"))
    records = []
    for selection in tqdm(selections, desc="Reusable matching cut pilot", unit="star"):
        if time.monotonic()-started >= args.seconds:
            break
        u, d = selection["outer_vertex"], selection["domain_id"]
        center = u+15
        selected = [v+15 for v in members(int(domains["domains"][u]["domain_masks_hex"][d], 16))]
        rows = rows_from(core_full, center, selected)
        assert len(selected) == 8 and cap_violation(rows) is None
        original = condition(rows, center)
        if original["matching_exists"]:
            records.append(dict(**selection, status="LIFT_FAILED_MATCHING_REAPPEARS", original_relaxed_graph=original))
            continue
        retained, deletions, trials = list(sorted(core_full)), [], 0
        for edge in list(retained):
            if center in edge:
                continue
            if time.monotonic()-started >= args.seconds:
                break
            trial = [e for e in retained if e != edge]
            trials += 1
            if not condition(rows_from(trial, center, selected), center)["matching_exists"]:
                retained = trial
                deletions.append(edge)
        reduced = condition(rows_from(retained, center, selected), center, with_blockers=True)
        assert not reduced["matching_exists"]
        witness = odd_component_witness(reduced["free_vertices"], reduced["possible_edges"])
        assert witness is not None
        matched_population = [item["path"] for item in population if set(retained) <= item["edges"]]
        literals = sorted(set(retained) | {tuple(sorted((center, v))) for v in selected})
        record = dict(**selection, status="CANDIDATE_REUSABLE_POSITIVE_EDGE_CUT", center_full99=center,
                      retained_K_edges_full99=retained, protected_center_K_edges_full99=[e for e in retained if center in e],
                      removed_K_edges_full99=deletions, center_star_edges_full99=[[center, v] for v in selected],
                      all14_center_neighbors_full99=reduced["neighborhood"], scaffold="Fixed189 root/matching/label-incidence positive edges; source hash in manifest",
                      negative_K_literals=[], all_other_non_scaffold_adjacencies="UNFIXED; every absent free-neighbor edge tested, regardless of original support class",
                      reduced_graph=reduced, odd_component_certificate=witness,
                      cut=dict(positive_full99_edge_literals=literals, coefficients="all1", sense="<=", rhs=len(literals)-1),
                      deletion_trials=trials, greedy_complete=trials == 164,
                      empirical_containment=dict(population="Saved fresh16 plus same13 candidate assignments", population_size=len(population), matching_candidate_paths=matched_population,
                                                 meaning="Core prerequisites only; no whole-K exclusion and no star-domain membership asserted"),
                      independent_verification=False)
        save(args.out / f"vertex_{u:02d}_domain_{d}.json", record)
        records.append(record)
        print(json.dumps(dict(vertex=u, retained_K=len(retained), literal_count=len(literals), separator_size=witness["separator_size"], odd_components=witness["odd_component_count"], contained_K=len(matched_population))), flush=True)
    assert all(digest(ROOT / name) == expected for name, expected in bindings.items()), "Input changed"
    successful = [r for r in records if r["status"] == "CANDIDATE_REUSABLE_POSITIVE_EDGE_CUT"]
    summary = dict(timestamp=stamp(), status="CANDIDATE_PILOT_COMPLETE" if len(records) == 16 else "CANDIDATE_PILOT_CAPPED",
                   manifest_sha256=digest(args.out / "manifest.json"), controls=checks, survivor_controls=survivor_results,
                   attempted_stars=len(records), successful_lifts=len(successful), failed_lifts=len(records)-len(successful),
                   retained_K_counts=[len(r["retained_K_edges_full99"]) for r in successful],
                   records=records, elapsed_seconds=time.monotonic()-started,
                   result_artifacts_sha256={p.name: digest(p) for p in args.out.glob("vertex_*.json")},
                   mathematical_claim_promotion=False, independent_verification=False, target_resolution=False,
                   limitations=["Producer discovery only; independent proof and raw certificate review pending.",
                                "Cuts condition on the fixed labeled root scaffold and selected star edges; they do not exclude every star or a changed K.",
                                "Greedy reduction is not a minimum-cardinality core search.",
                                "Containment counts concern a named finite population, not unrestricted coverage."])
    save(args.out / "summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("status", "attempted_stars", "successful_lifts", "failed_lifts", "retained_K_counts", "elapsed_seconds")}))


if __name__ == "__main__":
    main()
