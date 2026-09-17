"""Candidate cut instantiation under 7 cyclic group shifts and 128 sign flips.

These are coordinate relabelings of hypothetical graphs, not assumed graph
automorphisms. No existing producer, audit, or artifact is modified.
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
GATE = "acceleration/results/20260917_independent_review/matching_positive_cuts_recheck.json"
GATE_HASH = "3e807d158c7fea05e5a31ec631105fa1733e3ca86ad96549cc46a14dcf3e5fc9"
CORPUS = "acceleration/results/20260917_matching_cut/next_application_protocol.json"
IDENTITY = "acceleration/results/20260917_matching_cut_application/summary.json"


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def save(path, data, compact=False):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, indent=None if compact else 2, separators=(",", ":") if compact else None)
        handle.write("\n")


def stamp():
    return datetime.now(timezone.utc).isoformat()


def edge(a, b):
    assert a != b
    return min(a, b), max(a, b)


def labels():
    return [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2) for s in (0, 1) for t in (0, 1)]


def scaffold():
    result = {edge(0, v) for v in range(1, 15)} | {(2*g+1, 2*g+2) for g in range(7)}
    for v, pair in enumerate(labels(), 15):
        result |= {edge(v, s+1) for s in pair}
    assert len(result) == 189
    return result


def relabel(shift, mask):
    symbol = {}
    for s in range(14):
        g, b = divmod(s, 2)
        target = (g+shift) % 7
        symbol[s] = 2*target + (b ^ ((mask >> target) & 1))
    lookup = {tuple(pair): v for v, pair in enumerate(labels(), 15)}
    mapping = [0] + [symbol[s]+1 for s in range(14)]
    mapping += [lookup[tuple(sorted((symbol[a], symbol[b])))] for a, b in labels()]
    return mapping


def mapped_edges(edges, mapping):
    return tuple(sorted(edge(mapping[a], mapping[b]) for a, b in edges))


def check_map(mapping):
    assert len(mapping) == 99 and sorted(mapping) == list(range(99)), "full99 bijection"
    assert mapping[0] == 0, "root fixed"
    assert set(mapped_edges(scaffold(), mapping)) == scaffold(), "positive scaffold preserved"


def edge_bits(edges):
    return sum(1 << (99*a+b) for a, b in set(edges))


def controls():
    records = []
    for shift, mask in ((0, 0), (0, 127), (6, 85)):
        mapping = relabel(shift, mask)
        check_map(mapping)
        if (shift, mask) == (0, 0):
            assert mapping == list(range(99))
        records.append(dict(name=f"valid_shift{shift}_mask{mask}", outcome="PASS"))
    for name in ("duplicate_image", "wrong_outer_label", "moved_root"):
        mapping = relabel(0, 0)
        if name == "duplicate_image":
            mapping[98] = mapping[97]
        elif name == "wrong_outer_label":
            mapping[15], mapping[19] = mapping[19], mapping[15]
        else:
            mapping[0], mapping[1] = mapping[1], mapping[0]
        try:
            check_map(mapping)
        except AssertionError as exc:
            records.append(dict(name=name, outcome="REJECT", reason=str(exc)))
        else:
            raise ValueError("Corrupt mapping accepted")
    assert edge_bits([(1, 4), (4, 8)]) & edge_bits([(1, 4)]) == edge_bits([(1, 4)])
    assert len({mapped_edges([(1, 4), (2, 5)], list(range(99))), mapped_edges([(2, 5), (1, 4)], list(range(99)))}) == 1
    records.append(dict(name="edge_mask_containment_and_literal_set_dedup", outcome="PASS"))
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=240)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    assert not (args.out / "manifest.json").exists(), "Choose fresh evidence directory"
    bindings = {}
    def read(name):
        bindings[name] = digest(ROOT / name)
        return json.loads((ROOT / name).read_bytes())
    assert digest(ROOT / GATE) == GATE_HASH, "Changed base-cut review"
    gate, corpus, identity = read(GATE), read(CORPUS), read(IDENTITY)
    assert gate["status"] == "INDEPENDENT_POSITIVE_MATCHING_CUTS_PASS"
    assert gate["claim_id"] == "C-MATCHING-POSITIVE-CUTS-16" and gate["claim_revision"] == 1
    for collection in (gate["inputs_sha256"], corpus["inputs_sha256"]):
        for name, expected in collection.items():
            assert digest(ROOT / name) == expected, "Changed frozen dependency: " + name
            bindings[name] = expected
    base_summary = read("acceleration/results/20260917_matching_cut/summary.json")
    parents = []
    for raw in base_summary["records"]:
        name = f"acceleration/results/20260917_matching_cut/vertex_{raw['outer_vertex']:02d}_domain_{raw['domain_id']}.json"
        record = read(name)
        assert bindings[name] == gate["inputs_sha256"][name]
        parents.append(dict(path=name, center=record["center_full99"], core=record["retained_K_edges_full99"],
                            star=record["center_star_edges_full99"], literals=record["cut"]["positive_full99_edge_literals"]))
    assert len(parents) == 16 and len(corpus["corpus"]) == 29
    baseline = {}
    for record in identity["records"]:
        name = "acceleration/results/20260917_matching_cut_application/" + record["path"]
        detail = read(name)
        assert bindings[name] == record["sha256"]
        baseline[detail["family"], detail["proposal_index"]] = {(r["outer_vertex"], r["original_domain_id"]) for r in detail["removed_original_choices"]}
    bindings["acceleration/theory_20260917_matching_cut_cyclic.py"] = digest(__file__)
    bindings["acceleration/GROUP_ORBIT_VALIDITY.md"] = digest(ROOT / "acceleration/GROUP_ORBIT_VALIDITY.md")
    manifest = dict(timestamp=stamp(), source_commit=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(),
                    command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()), python=platform.python_version(),
                    question="Do896 explicitly checked scaffold-preserving relabelings of16 approved clauses eliminate additional original-domain choices in the frozen29candidate records?",
                    gate=dict(path=GATE, sha256=GATE_HASH, claim_id=gate["claim_id"], revision=1),
                    map_selection="Exactly shift r=0..6 and mask m=0..127; symbol(g,b) maps to ((g+r) mod7, b XOR bit_m[(g+r)mod7])",
                    maps_selected=896, parents_selected=16, generated_images_expected=14336,
                    scope="Coordinate relabelings; no hypothetical graph automorphism assumption. Fixed29 original-domain corpus only; no full645120group.",
                    deduplication="Exact sorted unordered full99 positive-literal sets; preserve every parent-cut/map witness",
                    application="PositiveK-prerequisite containment plus exact original8star mask lookup; direct positivegraph literal check of every claimed hit",
                    independent_comparison="Separately reconstruct candidate neighbors and evaluate all parentcut+map-image literals for every reported hit; original16identity union compared exactly",
                    acceptance="All896maps full99bijections preserving all189positive scaffold edges; no tolerance; everyreportedhit passes directliteral check; identityunion subset newunion",
                    falsification="Any map/scaffold mismatch, wrong image/witness, changed basecut/corpus hash, duplicate-ID accounting discrepancy, or false literal hit",
                    time_limit_seconds=args.seconds, checkpoints="Maps and deduplicated bank saved before applications; each completed candidate saved separately; cappedrun has explicit partial summary",
                    inputs_sha256=bindings, independent_relabeling_review=False, independent_application_review=False,
                    numerical_thresholds=None, numerical_thresholds_reason="Exact integer/set membership only", status="PREREGISTERED")
    save(args.out / "manifest.json", manifest)
    started = time.monotonic()
    control_records = controls()
    maps, bank, bank_keys = [], [], {}
    for shift in tqdm(range(7), desc="Scaffold map generation", unit="rotation"):
        for mask in range(128):
            mapping = relabel(shift, mask)
            check_map(mapping)
            map_id = len(maps)
            maps.append(dict(map_id=map_id, group_shift=shift, target_group_sign_mask=mask, full99_vertex_map=mapping,
                             bijection_verified=True, positive_scaffold_verified=True))
            for parent_id, parent in enumerate(parents):
                literals = mapped_edges(parent["literals"], mapping)
                witness = dict(parent_cut=parent_id, map_id=map_id)
                if literals in bank_keys:
                    bank[bank_keys[literals]]["witnesses"].append(witness)
                    continue
                center = mapping[parent["center"]]
                core = mapped_edges(parent["core"], mapping)
                star = mapped_edges(parent["star"], mapping)
                selected = {b if a == center else a for a, b in star}
                assert len(selected) == 8 and all(center in e for e in star)
                assert set(literals) == set(core) | set(star) and len([e for e in core if center in e]) == 4
                ident = len(bank)
                bank_keys[literals] = ident
                bank.append(dict(cut_id=ident, positive_literals=literals, rhs=len(literals)-1,
                                 center_full99=center, positive_K_prerequisites=core, selected_star_edges=star,
                                 original_star_mask_hex=hex(sum(1 << (v-15) for v in selected)), witnesses=[witness]))
        assert time.monotonic()-started < args.seconds, "Map stage exceeded cap; no application claim"
    assert len(maps) == 896 and sum(len(c["witnesses"]) for c in bank) == 14336
    save(args.out / "maps.json", dict(maps=maps, controls=control_records), compact=True)
    save(args.out / "cut_bank.json", dict(parent_cut_paths=[p["path"] for p in parents], generated_images=14336,
                                          unique_clauses=len(bank), cuts=bank), compact=True)
    prepared = [(cut, edge_bits(cut["positive_K_prerequisites"]), int(cut["original_star_mask_hex"], 16)) for cut in bank]
    fixed = scaffold()
    records = []
    for item in tqdm(corpus["corpus"], desc="Cyclic/sign cuts on frozen29", unit="candidate"):
        if time.monotonic()-started >= args.seconds:
            break
        candidate, domains = read(item["candidate_path"]), read(item["original_domains_path"])
        assert domains["complete_domain_enumeration"] is True
        assert [r["outer_vertex"] for r in domains["domains"]] == list(range(84))
        K = {edge(a+15, b+15) for a, b in candidate["overlap_edges_outer_zero_based"]}
        assert len(K) == 168
        Kbits = edge_bits(K)
        positive_base = fixed | K
        lookups = [{int(mask, 16): i for i, mask in enumerate(row["domain_masks_hex"])} for row in domains["domains"]]
        assert all(len(lookups[u]) == len(row["domain_masks_hex"]) for u, row in enumerate(domains["domains"]))
        matched_core, missing_star, hits = [], [], {}
        direct_checks = 0
        for cut, corebits, wanted in prepared:
            if Kbits & corebits != corebits:
                continue
            matched_core.append(cut["cut_id"])
            center = cut["center_full99"]
            outer = center-15
            if wanted not in lookups[outer]:
                missing_star.append(cut["cut_id"])
                continue
            domain_id = lookups[outer][wanted]
            selected = {v+15 for v in range(84) if wanted >> v & 1}
            assert len(selected) == 8
            actual_graph = positive_base | {edge(center, v) for v in selected}
            assert all(tuple(e) in actual_graph for e in cut["positive_literals"]), "False optimized hit"
            # Separate reconstruction from the retained map witness, without
            # trusting the bank's already-materialized image literal list.
            witness = cut["witnesses"][0]
            parent = parents[witness["parent_cut"]]
            mapping = maps[witness["map_id"]]["full99_vertex_map"]
            assert all(edge(mapping[a], mapping[b]) in actual_graph for a, b in parent["literals"])
            direct_checks += 1
            hits.setdefault((outer, domain_id), []).append(cut["cut_id"])
        identity_ids = baseline[item["family"], item["proposal_index"]]
        removed_ids = set(hits)
        assert identity_ids <= removed_ids
        per_vertex = Counter(u for u, _ in removed_ids)
        original_counts = [len(row["domain_masks_hex"]) for row in domains["domains"]]
        original_total = sum(original_counts)
        unique_parent_map_hits = sum(sum(len(bank[c]["witnesses"]) for c in ids) for ids in hits.values())
        result = dict(family=item["family"], proposal_index=item["proposal_index"], candidate_path=item["candidate_path"], original_domains_path=item["original_domains_path"],
                      original_choices=original_total, unique_removed_choices=len(hits), surviving_choices=original_total-len(hits),
                      unique_clause_hits=sum(map(len, hits.values())), generated_image_hits=unique_parent_map_hits,
                      core_matching_cut_ids=matched_core, core_matching_but_star_absent_cut_ids=missing_star,
                      removed_choices=[dict(outer_vertex=u, original_domain_id=d, mask_hex=domains["domains"][u]["domain_masks_hex"][d],
                                            hit_unique_cut_ids=sorted(ids), covered_by_original16identity=(u, d) in identity_ids)
                                       for (u, d), ids in sorted(hits.items())],
                      unique_choice_hit_multiplicity_histogram=dict(Counter(len(ids) for ids in hits.values())),
                      original16identity_removed=len(identity_ids), intersection_with_original16identity=len(identity_ids & removed_ids),
                      additional_unique_removed=len(removed_ids-identity_ids),
                      per_vertex_removed=[per_vertex[u] for u in range(84)], per_vertex_original=original_counts,
                      empty_domains=[u for u in range(84) if original_counts[u] == per_vertex[u]],
                      direct_literal_and_witness_checks=direct_checks,
                      full_K_exclusion_claimed=False, independent_relabeling_application_review=False)
        name = f"{item['family']}_index_{item['proposal_index']}.json"
        save(args.out / name, result)
        records.append(dict(path=name, sha256=digest(args.out / name), **{k: result[k] for k in (
            "family", "proposal_index", "original_choices", "unique_removed_choices", "unique_clause_hits", "generated_image_hits",
            "original16identity_removed", "intersection_with_original16identity", "additional_unique_removed", "empty_domains", "direct_literal_and_witness_checks")}))
    assert all(digest(ROOT / name) == expected for name, expected in bindings.items()), "Input changed"
    summary = dict(timestamp=stamp(), status="CANDIDATE_CYCLIC_SIGN_APPLICATION_COMPLETE" if len(records) == 29 else "CANDIDATE_CYCLIC_SIGN_APPLICATION_CAPPED",
                   manifest_sha256=digest(args.out / "manifest.json"), maps_sha256=digest(args.out / "maps.json"), cut_bank_sha256=digest(args.out / "cut_bank.json"),
                   maps_checked=896, generated_clause_images=14336, unique_clauses=len(bank), deduplicated_images=14336-len(bank),
                   selected_candidate_records=29, completed_candidate_records=len(records), records=records,
                   **{k: sum(r[k] for r in records) for k in ("original_choices", "unique_removed_choices", "unique_clause_hits", "generated_image_hits",
                                                             "original16identity_removed", "intersection_with_original16identity", "additional_unique_removed", "direct_literal_and_witness_checks")},
                   empty_candidate_domains=[dict(family=r["family"], proposal_index=r["proposal_index"], outer_vertex=u) for r in records for u in r["empty_domains"]],
                   elapsed_seconds=time.monotonic()-started, independent_relabeling_review=False, independent_application_review=False,
                   unit="Distinct(candidate record,outer vertex,original domain ID) tuples within the frozen29 corpus; clause/image hit counts overlap",
                   root_relabeling_is_not_automorphism_assumption=True, full_group_645120_not_searched=True,
                   full_K_exclusion_claimed=False, target_resolution=False)
    save(args.out / "summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("status", "maps_checked", "generated_clause_images", "unique_clauses", "completed_candidate_records", "original_choices", "unique_removed_choices", "original16identity_removed", "additional_unique_removed", "empty_candidate_domains", "elapsed_seconds")}))


if __name__ == "__main__":
    main()
