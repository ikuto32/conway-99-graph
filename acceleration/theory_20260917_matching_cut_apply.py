"""Apply independently approved identity cuts to frozen original star IDs.

No producer imports. Application results remain pending independent review;
no removed local choice is reported as a complete-K exclusion.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
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
PROTOCOL = "acceleration/results/20260917_matching_cut/next_application_protocol.json"
AUDIT = "acceleration/results/20260917_independent_review/matching_positive_cuts_recheck.json"
AUDIT_HASH = "3e807d158c7fea05e5a31ec631105fa1733e3ca86ad96549cc46a14dcf3e5fc9"


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(path, data):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")


def edge(a, b):
    assert a != b
    return (min(a, b), max(a, b))


def mask_neighbors(mask):
    value = int(mask, 16)
    return {15+i for i in range(84) if value >> i & 1}


def scaffold_edges():
    result = {edge(0, r) for r in range(1, 15)}
    result |= {edge(1+2*i, 2+2*i) for i in range(7)}
    labels = sorted(((a, b) for a in range(14) for b in range(a+1, 14) if a//2 != b//2),
                    key=lambda x: (x[0]//2, x[1]//2, x[0], x[1]))
    for u, pair in enumerate(labels, 15):
        result |= {edge(u, r+1) for r in pair}
    assert len(result) == 189
    return result


def direct_clause_hit(base, center, selected, literals):
    graph = base | {edge(center, v) for v in selected}
    return all(e in graph for e in literals)


def independent_matching_check(present, center):
    """Set-neighborhood mutation and unmemoized matching search, no cut oracle."""
    adjacency = [set() for _ in range(99)]
    for a, b in present:
        adjacency[a].add(b)
        adjacency[b].add(a)
    assert all(len(s) <= 14 for s in adjacency)
    assert all(len(adjacency[a] & adjacency[b]) <= 2-int(b in adjacency[a]) for a, b in combinations(range(99), 2))
    neighbors = sorted(adjacency[center])
    assert len(neighbors) == 14
    forced = [e for e in combinations(neighbors, 2) if e in present]
    occupied = [v for e in forced for v in e]
    assert len(set(occupied)) == len(occupied)
    free = set(neighbors) - set(occupied)
    allowed = set()
    for a, b in combinations(sorted(free), 2):
        if len(adjacency[a]) >= 14 or len(adjacency[b]) >= 14:
            continue
        adjacency[a].add(b)
        adjacency[b].add(a)
        valid = all(len(adjacency[u] & adjacency[v]) <= 2-int(v in adjacency[u])
                    for u in (a, b) for v in range(99) if u != v)
        adjacency[a].remove(b)
        adjacency[b].remove(a)
        if valid:
            allowed.add((a, b))
    partner = {v: {w for w in free if w != v and edge(v, w) in allowed} for v in free}
    search_nodes = 0
    def possible(remaining):
        nonlocal search_nodes
        search_nodes += 1
        if not remaining:
            return True
        u = min(remaining, key=lambda v: (len(partner[v] & remaining), v))
        return any(possible(remaining - {u, v}) for v in sorted(partner[u] & remaining))
    exists = possible(free)
    return dict(matching_exists=exists, forced_edges=forced, free_vertices=sorted(free),
                possible_edges=sorted(allowed), exhaustive_search_nodes=search_nodes,
                missing_edge_scope="Every absent free-neighbor pair, regardless of support/fibre")


def controls():
    controls = []
    base = {edge(0, v) for v in range(1, 15)}
    for name, literal, selected, expected in (
        ("positive_literal_hit", {(0, 1), (1, 2)}, {2}, True),
        ("missing_star_literal", {(0, 1), (1, 2)}, {3}, False),
        ("missing_K_literal", {(0, 1), (1, 2), (4, 5)}, {2}, False),
    ):
        assert direct_clause_hit(base, 1, selected, literal) is expected
        controls.append(dict(name=name, expected=expected, outcome="PASS"))
    assert independent_matching_check(base, 0)["matching_exists"]
    controls.append(dict(name="windmill_all_missing_edges_allowed", outcome="PASS"))
    bad = base | {(1, 2), (1, 3)}
    try:
        independent_matching_check(bad, 0)
    except AssertionError:
        controls.append(dict(name="corrupt_adjacent_cap", outcome="REJECT"))
    else:
        raise ValueError("Corrupt graph accepted")
    matches = {}
    for clause in ("cut0", "cut1", "cut0"):
        matches.setdefault((4, 8), set()).add(clause)
    assert len(matches) == 1 and len(matches[4, 8]) == 2
    controls.append(dict(name="duplicate_clause_hits_union_one_original_ID", outcome="PASS"))
    return controls


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--controls-only", action="store_true")
    p.add_argument("--seconds", type=float, default=180)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out / "manifest.json").exists() or (args.out / "summary.json").exists():
        raise ValueError("Preserve previous application evidence")
    tested_controls = controls()
    if args.controls_only:
        save(args.out / "controls.json", dict(timestamp=stamp(), controls=tested_controls,
             source_sha256=digest(__file__), command_argv=[sys.executable, *sys.argv],
             elimination_counts_executed=False))
        print(json.dumps(dict(status="APPLICATION_CONTROLS_PASS", controls=len(tested_controls), elimination_counts_executed=False)))
        return
    bindings = {}
    def read(name):
        bindings[name] = digest(ROOT / name)
        return json.loads((ROOT / name).read_bytes())
    assert digest(ROOT / AUDIT) == AUDIT_HASH, "Independent gate artifact differs"
    audit = read(AUDIT)
    assert audit["status"] == "INDEPENDENT_POSITIVE_MATCHING_CUTS_PASS"
    assert audit["claim_id"] == "C-MATCHING-POSITIVE-CUTS-16" and audit["claim_revision"] == 1
    # Freeze every audited dependency, including the exact derivation text.
    for name, expected in audit["inputs_sha256"].items():
        assert digest(ROOT / name) == expected, "Stale independent gate: " + name
        bindings[name] = expected
    protocol = read(PROTOCOL)
    for name, expected in protocol["inputs_sha256"].items():
        assert digest(ROOT / name) == expected, "Changed frozen corpus: " + name
        bindings[name] = expected
    cuts = []
    cut_summary = read("acceleration/results/20260917_matching_cut/summary.json")
    for record in cut_summary["records"]:
        name = f"acceleration/results/20260917_matching_cut/vertex_{record['outer_vertex']:02d}_domain_{record['domain_id']}.json"
        raw = read(name)
        assert audit["inputs_sha256"].get(name) == bindings[name]
        center = raw["center_full99"]
        star = {tuple(e) for e in raw["center_star_edges_full99"]}
        wanted = {b if a == center else a for a, b in star}
        core = {tuple(e) for e in raw["retained_K_edges_full99"]}
        assert len(wanted) == 8 and all(center in e for e in star)
        assert len([e for e in core if center in e]) == 4
        cuts.append(dict(id=name, center=center, wanted=wanted, core=core,
                         literals={tuple(e) for e in raw["cut"]["positive_full99_edge_literals"]}))
    assert len(cuts) == 16 and len(protocol["corpus"]) == 29
    bindings["acceleration/theory_20260917_matching_cut_apply.py"] = digest(__file__)
    manifest = dict(timestamp=stamp(), source_commit=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(),
                    command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()), python=platform.python_version(),
                    independent_gate=dict(path=AUDIT, sha256=AUDIT_HASH, claim_id=audit["claim_id"], claim_revision=1),
                    preregistration=PROTOCOL, inputs_sha256=bindings,
                    explicit_verification_selection="All actual matched original choices receive independent set-neighborhood permissive matching feasibility checks; no sample selection",
                    application_checks="Fast K-core/mask equality versus direct full-positive-edge-set literal containment for every original domain at all16 named cut centers, including nonhits",
                    other_centers="Every8-edge cut star is absent from K/scaffold; adding a star at another center can add at most1 of those8 edges, so cannot satisfy this clause",
                    time_limit_seconds=args.seconds, exact_acceptance="Every fast/direct result agrees and every unique removed star has no permissive perfect matching",
                    orbit_expansion=False, independent_application_review=False, target_resolution=False)
    save(args.out / "manifest.json", manifest)
    started = time.monotonic()
    scaffold = scaffold_edges()
    records = []
    for item in tqdm(protocol["corpus"], desc="Approved identity cuts on original domains", unit="candidate"):
        if time.monotonic()-started > args.seconds:
            break
        candidate = read(item["candidate_path"])
        domains = read(item["original_domains_path"])
        complete = read(item["original_domain_audit_path"])
        assert complete["complete_used_domains_verified"] is True
        assert domains["complete_domain_enumeration"] is True
        assert [r["outer_vertex"] for r in domains["domains"]] == list(range(84))
        k = {edge(a+15, b+15) for a, b in candidate["overlap_edges_outer_zero_based"]}
        assert len(k) == 168
        base = scaffold | k
        assert all(not {e for e in cut["literals"] if cut["center"] in e and (e[0] if e[1] == cut["center"] else e[1]) in cut["wanted"]} & base for cut in cuts)
        original_counts = [len(row["domain_masks_hex"]) for row in domains["domains"]]
        matching, cut_rows = {}, []
        direct_checks = 0
        for cut in cuts:
            center, outer = cut["center"], cut["center"]-15
            core_matches = cut["core"] <= k
            missing = sorted(cut["core"]-k)
            hit_ids = []
            for domain_id, mask in enumerate(domains["domains"][outer]["domain_masks_hex"]):
                selected = mask_neighbors(mask)
                assert len(selected) == 8
                fast = core_matches and selected == cut["wanted"]
                direct = direct_clause_hit(base, center, selected, cut["literals"])
                direct_checks += 1
                assert fast == direct, "Fast/core and direct-edge containment disagree"
                if direct:
                    hit_ids.append(domain_id)
                    matching.setdefault((outer, domain_id), set()).add(cut["id"])
            cut_rows.append(dict(cut_path=cut["id"], center_full99=center, K_prerequisites_match=core_matches,
                                 missing_K_prerequisite_edges=missing, matching_original_domain_ids=hit_ids))
        removed = []
        for (outer, domain_id), clause_ids in sorted(matching.items()):
            mask = domains["domains"][outer]["domain_masks_hex"][domain_id]
            selected = mask_neighbors(mask)
            center = outer+15
            graph = base | {edge(center, v) for v in selected}
            checked = independent_matching_check(graph, center)
            assert not checked["matching_exists"], "Candidate cut removed a star with a permissive matching"
            removed.append(dict(outer_vertex=outer, original_domain_id=domain_id, original_mask_hex=mask,
                                hit_cut_paths=sorted(clause_ids), direct_literal_containment=True,
                                separate_matching_feasibility=checked))
        removed_counts = Counter(r["outer_vertex"] for r in removed)
        survivors = [count-removed_counts[u] for u, count in enumerate(original_counts)]
        pair_intersections = []
        hit_sets = {c["cut_path"]: {(c["center_full99"]-15, d) for d in c["matching_original_domain_ids"]} for c in cut_rows}
        for a, b in combinations(sorted(hit_sets), 2):
            overlap = hit_sets[a] & hit_sets[b]
            if overlap:
                pair_intersections.append(dict(cuts=[a, b], original_ID_pairs=sorted(overlap)))
        record = dict(family=item["family"], proposal_index=item["proposal_index"],
                      candidate_path=item["candidate_path"], original_domains_path=item["original_domains_path"],
                      original_choices=sum(original_counts), per_vertex_original_choices=original_counts,
                      per_cut_results=cut_rows, direct_literal_checks=direct_checks,
                      removed_original_choices=removed, unique_removed_choices=len(removed),
                      clause_hit_count=sum(len(c["matching_original_domain_ids"]) for c in cut_rows),
                      hit_multiplicity_histogram=dict(Counter(len(r["hit_cut_paths"]) for r in removed)),
                      overlapping_clause_pairs=pair_intersections, per_vertex_survivors=survivors,
                      surviving_choices=sum(survivors), empty_domains=[u for u, n in enumerate(survivors) if n == 0],
                      full_K_exclusion_claimed=False, independent_application_review=False)
        name = f"{item['family']}_index_{item['proposal_index']}.json"
        save(args.out / name, record)
        records.append(dict(path=name, sha256=digest(args.out / name), family=record["family"], proposal_index=record["proposal_index"],
                            original_choices=record["original_choices"], unique_removed_choices=len(removed),
                            clause_hit_count=record["clause_hit_count"], surviving_choices=record["surviving_choices"],
                            direct_literal_checks=direct_checks, matching_feasibility_checks=len(removed), empty_domains=record["empty_domains"]))
    assert all(digest(ROOT / name) == expected for name, expected in bindings.items()), "Inputs changed during application"
    summary = dict(timestamp=stamp(), status="CANDIDATE_APPLICATION_COMPLETE" if len(records) == 29 else "CANDIDATE_APPLICATION_CAPPED",
                   manifest_sha256=digest(args.out / "manifest.json"), controls=tested_controls, records=records,
                   selected_candidate_records=29, completed_candidate_records=len(records),
                   original_choices=sum(r["original_choices"] for r in records),
                   unique_removed_choices=sum(r["unique_removed_choices"] for r in records),
                   clause_hit_count=sum(r["clause_hit_count"] for r in records),
                   surviving_choices=sum(r["surviving_choices"] for r in records),
                   direct_literal_checks=sum(r["direct_literal_checks"] for r in records),
                   matching_feasibility_checks=sum(r["matching_feasibility_checks"] for r in records),
                   empty_candidate_domains=[dict(family=r["family"], proposal_index=r["proposal_index"], outer_vertex=u) for r in records for u in r["empty_domains"]],
                   unit="Named(candidate record,outer vertex,original domain ID) tuples; no isomorphism quotient or target coverage",
                   elapsed_seconds=time.monotonic()-started, independent_application_review=False,
                   full_K_exclusion_claimed=False, target_resolution=False)
    save(args.out / "summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("status", "completed_candidate_records", "original_choices", "unique_removed_choices", "clause_hit_count", "direct_literal_checks", "matching_feasibility_checks", "empty_candidate_domains", "elapsed_seconds")}))


if __name__ == "__main__":
    main()
