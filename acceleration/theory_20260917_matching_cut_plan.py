"""Freeze a future cut-application corpus without evaluating any cut."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "acceleration/results/20260917_matching_cut/next_application_protocol.json"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    bindings = {}
    def bind(name):
        name = name.replace("\\", "/")
        bindings[name] = digest(ROOT / name)
        return name
    def read(name):
        return json.loads((ROOT / bind(name)).read_bytes())
    pilot = read("acceleration/results/20260917_matching_cut/summary.json")
    corpus = []
    for family, directory in (
        ("fresh16", "acceleration/results/20260917_fresh_star_shortlist"),
        ("same13", "acceleration/results/20260917_same_star_round/star_shortlist"),
    ):
        summary = read(directory + "/summary.json")
        for row in summary["records"]:
            if row["audited"]:
                phase_path = directory + f"/index_{row['proposal_index']}/phase1.json"
                phase = read(phase_path)
                corpus.append(dict(family=family, proposal_index=row["proposal_index"], phase1_path=phase_path,
                                   candidate_path=bind(phase["candidate_path"]),
                                   original_domains_path=bind(phase["domains_path"]),
                                   original_domain_audit_path=bind(phase["domain_audit_path"]),
                                   domain_identity="outer_vertex0..83; original zero-based array index in domain_masks_hex; never renumber after filtering"))
    assert len(corpus) == 29
    for name in pilot["result_artifacts_sha256"]:
        bind("acceleration/results/20260917_matching_cut/" + name)
    bind("acceleration/theory_20260917_matching_cut.py")
    bind("acceleration/theory_20260917_matching_cut_plan.py")
    bind("uv.lock")
    protocol = dict(timestamp=datetime.now(timezone.utc).isoformat(),
                    source_commit=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(),
                    command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()),
                    status="PREREGISTERED_NOT_EXECUTED_AWAITING_INDEPENDENT_CUT_REVIEW",
                    question="Do independently approved positive-only clauses remove original-domain choices across the saved29 changed-K records?",
                    required_gate=dict(audit_path=None, reason="Independent exact-scope cut review is pending; no clause evaluation authorized by this protocol until its PASS binds the frozen cut artifacts"),
                    selection_rule="All16 frozen identity clauses applied to all29 saved candidate original-domain records; no score-based subselection",
                    clauses=16, candidate_records=29, corpus=corpus, inputs_sha256=bindings,
                    algorithm="For every candidate and every original star, form its positive partial graph from scaffold+candidate K+the8star edges; an approved cut fires iff every positive literal is present. Keep original domain IDs. A fast core/mask lookup must agree with direct edge-set evaluation on all hits and predetermined controls.",
                    frozen_universe="Named29 candidate records, each of84 original domain arrays at the pinned hashes; no changes to domain completeness or IDs",
                    acceptance_threshold="Exact edge membership only; no numerical tolerance",
                    cpu_pilot_wall_limit_seconds=180,
                    success="At least one approved cut removes a named original star in a changed-K record, with independent direct-literal replay",
                    falsification="No application outside original baseline, mapping inconsistency, any false fast-path hit, or a cut whose independently reviewed bytes differ",
                    reporting="Report per-candidate original population, unique removed(center,original_domain_id) pairs, survivors, number of hit clauses, multiplicities, and intersection/union counts. Never sum overlapping removals or reinterpret a star removal as a K exclusion; every empty domain requires separate independent complete-domain coverage review.",
                    controls=["Apply only independently approved exact artifact hashes", "Maintain original candidate/center/domain mapping", "Direct graph-literal evaluation for all claimed hits", "Positive original witness control and controls with an essential literal deleted; do not expect arbitrary literal removal to repair an obstruction"],
                    actual_elimination_results=None, actual_elimination_results_reason="Not evaluated; prerequisite independent cut review pending",
                    phase2_root_sign_flips=dict(status="IDEA_ONLY_NOT_LAUNCHED", proposed_maps="All128 sign flips of7 matched root pairs; bijectively transport symbols, root-label outer vertices, and every positive edge of each clause",
                                               soundness_condition="Independent review of bijection and scaffold preservation before any orbit application; transported full14-neighbor prerequisites must remain exact",
                                               explanation="A relabeling maps any hypothetical target graph to another labeled target graph. It does not require that a graph have that relabeling as an automorphism.",
                                               counting="Deduplicate exact sorted mapped clause edge sets; distinguish generated128*16 images from unique clauses and unique eliminated stars"),
                    target_resolution=False, mathematical_claim_promotion=False)
    with OUT.open("x", encoding="utf-8") as stream:
        json.dump(protocol, stream, indent=2)
        stream.write("\n")
    print(json.dumps(dict(status=protocol["status"], candidate_records=len(corpus), eliminated_choices_counted=False)))


if __name__ == "__main__":
    main()
