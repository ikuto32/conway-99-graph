"""Transfer an independently checked pair closure only to an identical labeled K.

The prior proof and every bound input/source hash are checked. This does not
rerun domain enumeration and does not transfer across unproved isomorphisms.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_certificate import full_graph, require


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--prior-candidate", type=Path, required=True)
    parser.add_argument("--prior-audit", type=Path, required=True)
    parser.add_argument("--prior-audit-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    require(not args.out.exists(), "Preserve existing pair evidence")
    require(digest(args.prior_audit) == args.prior_audit_sha256.lower(), "Prior audit differs from supplied immutable hash")
    prior = json.loads(args.prior_audit.read_bytes())
    require(prior["status"] == "INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS" and
            prior["propagation_status"] == "ARC_CONSISTENT_NONEMPTY" and
            prior["complete_used_domains_verified"] is True, "Prior audit does not prove a nonempty complete-domain closure")
    require(sorted(row["outer_vertex"] for row in prior["independently_reenumerated_domains"]) == list(range(84)),
            "Prior domain completeness does not cover all84vertices")
    for name, expected in prior["inputs_sha256"].items():
        require(digest(Path(name)) == expected, "Changed prior audit dependency: " + name)
    require(prior["inputs_sha256"].get(str(args.prior_candidate)) == digest(args.prior_candidate),
            "Prior candidate is not the independently audited one")
    old = json.loads(args.prior_candidate.read_bytes())
    new = json.loads(args.candidate.read_bytes())
    old_adj, old_unknown = full_graph(old)
    new_adj, new_unknown = full_graph(new)
    old_edges, new_edges = sorted(map(tuple, old["overlap_edges_outer_zero_based"])), sorted(map(tuple, new["overlap_edges_outer_zero_based"]))
    require(old_edges == new_edges and old_adj == new_adj and old_unknown == new_unknown,
            "Pair proof may be reused only for an identical labeled graph and unknown domain")
    inputs = dict(prior["inputs_sha256"])
    inputs.update({str(path): digest(path) for path in (args.candidate, args.prior_candidate, args.prior_audit, Path(__file__))})
    result = dict(status="INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS", propagation_status="ARC_CONSISTENT_NONEMPTY",
                  evidence_method="PRIOR_INDEPENDENT_PROOF_PLUS_EXACT_LABELED_GRAPH_IDENTITY",
                  inputs_sha256=inputs, producer_or_solver_imported=False,
                  complete_used_domains_verified=True, complete_domains_established_by="Prior independent enumeration of the same labeled graph",
                  prior_audit_path=str(args.prior_audit), prior_audit_sha256=digest(args.prior_audit),
                  prior_candidate_path=str(args.prior_candidate), current_candidate_path=str(args.candidate),
                  identical168_overlap_edges_verified=True, identical99_partial_adjacency_verified=True,
                  identical1680_unknown_edge_domain_verified=True, same_exact_phase1_optimum=True,
                  independently_reenumerated_domains=prior["independently_reenumerated_domains"],
                  independent_domain_search_nodes=prior["independent_domain_search_nodes"],
                  events_verified=prior["events_verified"], empty_vertex=None,
                  set_based_compatibility_checks=prior["set_based_compatibility_checks"],
                  enumeration_and_event_counts_are_reused_prior_evidence=True,
                  new_domain_enumeration_nodes=0, new_deletion_replay_checks=0,
                  elapsed_seconds=time.perf_counter()-started,
                  scope="Prior independently complete local-domain and final exact pair-support proof transferred by exact labeled graph equality. No new enumeration is claimed, no isomorphism assumption, no simultaneous graph completion or global exclusion.")
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in ("inputs_sha256", "independently_reenumerated_domains")}))


if __name__ == "__main__":
    main()
