"""Two bounded dependency-impact reviews; no ledger or historical artifact edits.

Reuses immutable prior encoding audits as premises, but imports no producer or
mathematical checker. Fresh exact quadratic calculations supplement the written
review. This is not a replay of the large CNF or a new search.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import platform
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "acceleration/results/20260930_independent_review/editorial_dependent_impact"
EDITORIAL = "acceleration/results/20260930_independent_review/automorphism_assumption_editorial/summary.json"
EDITORIAL_SHA = "1584c3c0ef52fdee47c056fec317260d6952fdbd46a9e47e0742ce1f6d711388"
DUAL = "C-ROOK-ORBIT-LOCAL59-DUAL-GRAM-EXCLUSION"
W81 = "C-PARTIAL-K-EIGHT-FULL99-W81-GRAM-BOX-NOGOOD"


def need(test, message):
    if not test:
        raise ValueError(message)


class Loader(yaml.SafeLoader):
    pass


Loader.yaml_implicit_resolvers = {k: [(t, r) for t, r in vs if t != "tag:yaml.org,2002:timestamp"]
                                 for k, vs in Loader.yaml_implicit_resolvers.items()}


def unique(loader, node, deep=False):
    result = {}
    for k, v in node.value:
        key = loader.construct_object(k, deep=deep)
        need(key not in result, "duplicate ledger key")
        result[key] = loader.construct_object(v, deep=deep)
    return result


Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def quadratic(a, vector, diagonal, adjacency, constant):
    n = len(a)
    need(len(vector) == n and all(type(x) is int for x in vector), "integer vector")
    need(all(len(row) == n for row in a), "square matrix")
    need(all(type(a[i][j]) is int and a[i][j] in (0, 1) and a[i][j] == a[j][i]
             and (i != j or a[i][j] == 0) for i in range(n) for j in range(n)), "simple graph")
    return sum(vector[i] * (diagonal * int(i == j) + adjacency * a[i][j] + constant) * vector[j]
               for i in range(n) for j in range(n))


def negative(value, expected):
    need(type(expected) is int and value == expected and value < 0, "exact strict negative certificate")


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    snapshot = OUT / "CLAIMS.before_impact_review.yaml"
    snapshot.write_bytes((ROOT / "CLAIMS.yaml").read_bytes())
    ledger = yaml.load(snapshot.read_text(encoding="utf-8"), Loader=Loader)
    claims = {c["id"]: c for c in ledger["claims"]}
    artifacts = {a["id"]: a for a in ledger["artifacts"]}
    bindings = {}

    def bind(path, expected=None):
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        key = p.relative_to(ROOT).as_posix()
        actual = digest(p)
        need(expected is None or actual == expected, "artifact identity: " + key)
        need(key not in bindings or bindings[key] == actual, "conflicting artifact identity")
        bindings[key] = actual
        return p

    def read(path, expected=None):
        return json.loads(bind(path, expected).read_text(encoding="utf-8"))

    editorial = read(EDITORIAL, EDITORIAL_SHA)
    bind(editorial["reviewed_ledger_snapshot"], editorial["reviewed_ledger_sha256"])
    reviewed = {r["claim_id"]: r for r in editorial["records"]}
    need(editorial["mathematical_claim_changed"] is False, "editorial scope")
    reports = {}
    material_claims = {DUAL, W81} | {d["id"] for cid in (DUAL, W81) for d in claims[cid]["dependencies"]}
    for cid in sorted(material_claims):
        claim = claims[cid]
        need(claim["revision"] == 1 and claim["status"] == "VERIFIED" and claim["review_state"] == "CLEAR", "expected original claim state")
        if cid in reviewed:
            row = reviewed[cid]
            need(canonical(claim) == row["reviewed_claim_sha256"] and claim["assumptions"] == row["original_assumptions"], "exact reviewed premise")
            need(row["recommended_assumptions"] == [editorial["approved_replacements"].get(s, s) for s in claim["assumptions"]], "only approved editorial change")
        for aid in claim["evidence"]:
            artifact = artifacts[aid]
            bind(artifact["path"], artifact["sha256"])
        for v in claim["verification"]:
            for aid, expected in v["artifact_hashes"].items():
                bind(artifacts[aid]["path"], expected)
        v = claim["verification"][-1]
        reports[cid] = read(v["command_or_audit"])
        # Authenticate each declared direct audit input. This does not replay
        # every upstream computation or recursively assert all archive checks.
        for path, expected in reports[cid].get("inputs_sha256", {}).items():
            bind(path, expected)

    dual_audit, box_audit = reports[DUAL], reports[W81]
    need(dual_audit["status"] == "INDEPENDENT_ORBIT_LOCAL59_DUAL_GRAM_EXCLUSION_PASS", "dual audit status")
    need(box_audit["status"] == "INDEPENDENT_FULL99_GRAM_BOOLEAN_BOX_NOGOOD_PASS", "box audit status")
    for cid, audit in ((DUAL, dual_audit), (W81, box_audit)):
        need(audit["statement"] == claims[cid]["statement"] and audit["scope"] == claims[cid]["scope"]["description"]
             and audit["assumptions"] == claims[cid]["assumptions"], "exact current claim matches old audit")

    graph_path = "acceleration/results/20260930_independent_review/rook_orbit_sat_replay_v2/independent_full59.json"
    graph = read(graph_path, dual_audit["graph_sha256"])["adjacency_full59"]
    cert = read("acceleration/results/20260930_rook_orbit_gram01/result.json", dual_audit["certificate_sha256"])
    need(len(graph) == 59, "raw59 order")
    dual_results = []
    for row in cert["tests"]:
        coefficients = {"27I-9A+J": (27, -9, 1), "A+4I": (4, 1, 0)}[row["matrix"]]
        result = row["result"]
        q = quadratic(graph, result["integer_negative_vector"], *coefficients)
        negative(q, result["quadratic_value"])
        dual_results.append({"matrix": row["matrix"], "exact_quadratic": q, "ordered_terms": 59 * 59})
    need({r["matrix"] for r in dual_results} == {"27I-9A+J", "A+4I"}, "both obstructions")

    cut = read("acceleration/results/20260930_eight_raw29_gram_cut/certificate.json", box_audit["certificate_sha256"])
    model = read(cut["encoding_model"], cut["encoding_model_sha256"])
    known = model["known_adjacency_full99"]
    vector = cut["integer_vector_full99"]
    unknown = {(i, j) for i, j in combinations(range(99), 2) if known[i][j] == -1}
    edges = {r["id"]: (r["u"], r["v"]) for r in model["edge_variables"]}
    need(len(unknown) == len(edges) == 2160 and set(edges) == set(range(1, 2161))
         and set(edges.values()) == unknown, "all free-edge mappings")
    base = [[max(0, a) for a in row] for row in known]
    constant = quadratic(base, vector, 27, -9, 1)
    coefficients = {v: -18 * vector[i] * vector[j] for v, (i, j) in edges.items()}
    clause = cut["nogood_clause"]
    need(clause == box_audit["verified_clause"] and len(clause) == len({abs(x) for x in clause}) == 44, "exact audited clause")
    fixed = {abs(x): int(x < 0) for x in clause}
    corner_values = {v: fixed[v] if v in fixed else int(c > 0) for v, c in coefficients.items()}
    upper = constant + sum(coefficients[v] * corner_values[v] for v in edges)
    corner = deepcopy(base)
    for v, (i, j) in edges.items():
        corner[i][j] = corner[j][i] = corner_values[v]
    need(upper == quadratic(corner, vector, 27, -9, 1), "independent literal maximizing corner")
    negative(upper, -5868)
    need(cut["global_boolean_box_upper_bound"] == box_audit["exact_boolean_box_upper_bound"] == upper, "same bound")
    raw = read(cut["raw_artifact"], cut["raw_artifact_sha256"])["records"][cut["raw_record_index"]]
    embedding = raw["full99_vertex_map"]
    extended = [0] * 99
    for i, v in enumerate(embedding):
        extended[v] = raw["integer_negative_vector"][i]
    need(extended == vector and len(set(embedding)) == 29, "raw29 vector identity")
    negative(quadratic(raw["adjacency_full29"], raw["integer_negative_vector"], 27, -9, 1), -5868)

    # Positive acceptance and deliberately wrong values exercise the new exact
    # calculations. Historic broad corruption controls remain separately bound.
    k5 = [[int(i != j) for j in range(5)] for i in range(5)]
    star = [[int(i != j and (i == 0 or j == 0)) for j in range(26)] for i in range(26)]
    negative(quadratic(k5, [1] * 5, 27, -9, 1), -20)
    negative(quadratic(star, [5] + [-1] * 25, 4, 1, 0), -50)
    rejected = []
    for name, actual, expected in [("wrong_negative_value", -20, -21), ("zero_not_obstruction", 0, 0),
                                   ("wrong_box_bound", upper, upper - 1)]:
        try:
            negative(actual, expected)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("corruption accepted")
    boxes = 0
    for cs in product((-2, 0, 3), repeat=3):
        for spec in product((None, 0, 1), repeat=3):
            exact = max(sum(c * b for c, b in zip(cs, bs)) for bs in product((0, 1), repeat=3)
                        if all(s is None or s == b for s, b in zip(spec, bs)))
            need(exact == sum(max(0, c) if s is None else c * s for c, s in zip(cs, spec)), "Boolean maximum control")
            boxes += 1

    premise_uses = {
        DUAL: [{"id": "C-ROOK-ORBIT-AUGMENTED-LOCAL59-WITNESS", "relation": "derived_from",
                "actual_use": "Authenticates the exact raw59 graph and provenance as a local SAT survivor. The dual-Gram nonextension argument itself uses only that raw graph, the saved integer vectors, and the defining target matrix identity; local SAT feasibility is not a logical premise of negativity.",
                "automorphism_role": "None. Every literal matrix entry is used directly; no equality with a relabelled matrix, orbit restriction, or asymmetric-target requirement is invoked."}],
        W81: [{"id": "C-TARGET-GRAM-BOOLEAN-BOX-NOGOODS", "relation": "uses_result",
               "actual_use": "Applies separable maximization of the affine Gram quadratic over all remaining Boolean edges after the44 falsifying values are fixed. Every coefficient is included; no orbit quotient is used.", "automorphism_role": "None; the lemma quantifies over arbitrary target adjacencies and fixed principal sets."},
              {"id": "C-PARTIAL-K-EIGHT-COORDINATE-FULL99-SAT-ENCODING", "relation": "encoding_equivalence",
               "actual_use": "Converts target necessity within the exact fixed189-scaffold/120K/2160free-edge family into an entailed clause of its exact CNF. Raw99 degree14 and all pair caps saturate by the global count9009+693=2*C(99,2); gate/threshold equivalences concern independent Boolean variables.", "automorphism_role": "None; the fixed family is conditional scope, not a purported normalization by a target automorphism."},
              {"id": "C-CLOSED29-TWO-SPECIFIC-GRAM-OBSTRUCTIONS", "relation": "derived_from",
               "actual_use": "Identifies source record1, its indicated raw29 embedding and exact integer vector. The zero-extended vector and raw value-5868 are rechecked here; the new box bound is independently calculated rather than inferred from the two-pattern exclusion.", "automorphism_role": "None; only the exact indicated induced matrix and vector are used."}],
    }
    written = """# Two dependent-claim impact reviews

The review concerns only the approved clarification that no nontrivial target
automorphism is assumed and exact dependency revision repinning. It changes
neither dependent statement, assumptions, mathematical scope, nor evidence bytes.
No symmetry or asymmetry premise appears in either proof.

For the local59 dual-Gram exclusion, the upstream witness authenticates the
same raw graph. For any target, its diagonal identity gives degree14 and thus
AJ=JA=14J. Exact expansion gives G^2=63G for G=27I-9A+J and P^2=77P for
P=11A+44I-2J. Hence G is positive semidefinite and A+4I=(P+2J)/11 is positive
semidefinite. Principal submatrices inherit this property by zero extension.
The two saved strict negative integer quadratics disprove occurrence of this
one induced graph regardless of its provenance, or any graph automorphisms.
No entire rook family is excluded.

For w81, the distinct free-edge variables of the exact full99 family change
the quadratic by coefficients-18*w_u*w_v. Falsifying the44literal clause fixes
those44 bits. Maximizing each other Boolean term separately gives-5868, also
obtained from the literal ordered99x99 quadratic of the constructed maximizing
corner. This box may include degree-infeasible graphs; that is a safe superset.
Target Gram positivity forbids every assignment in the box. The audited full99
encoding identifies CNF models with target graphs within the exact fixed family,
so the clause is redundant in that CNF. Its direct counting/equivalence proof
requires no target automorphism. The old certificate's weaker-CNF wording was
already corrected by its preserved SCOPE_CLARIFICATION.md and independent audit.

Each downstream claim can retain VERIFIED/CLEAR at revision2, with precisely
the listed revision2 dependency pins, conditional on those premises being
migrated exactly as approved and retaining their bound independent evidence.
This does not approve any unrelated future premise change. Original revision1
verification records must be preserved, and this impact review appended at
revision2. All original ledger fields except normal revision/evidence/pin
bookkeeping remain unchanged. No ledger is edited by this review.

The reviewer previously authored the dual-Gram independent checker and the
editorial wording review, but did not produce that original Gram discovery,
the w81 cut, its independent original checker, or the CNF. This is not a claim
of a new external review. Python exact integers/JSON, PyYAML ledger parsing,
and immutable prior audited encoding/cut artifacts are shared trusted inputs.
Full CNF clause replay, SAT search, and graph discovery are not performed here.
"""
    (OUT / "review.md").write_text(written, encoding="utf-8")
    bind(OUT / "review.md")
    bind(snapshot)
    bind(__file__)
    for p in ("uv.lock", "pyproject.toml"):
        bind(p)
    outputs = []
    for cid, name in ((DUAL, "dual_gram"), (W81, "w81_nogood")):
        claim = claims[cid]
        new_dependencies = [dict(d, revision=2) for d in claim["dependencies"]]
        need({(x["id"], x["relation"]) for x in new_dependencies} == {(x["id"], x["relation"]) for x in premise_uses[cid]}, "complete dependency-use review")
        result = {
            "status": "INDEPENDENT_EDITORIAL_DEPENDENCY_IMPACT_PASS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "command": [sys.executable, *sys.argv], "working_directory": str(Path.cwd()),
            "python": platform.python_version(), "PyYAML": yaml.__version__,
            "verifier": "/root/state_literature_audit independent dependency-impact reviewer",
            "verification_type": "Exact artifact identity and written dependency-use impact review, supplemented by fresh literal integer calculations; prior full encoding audit reused",
            "claim_id": cid, "claim_revision": 2, "previous_revision": 1,
            "old_claim_sha256": canonical(claim), "statement": claim["statement"], "scope": claim["scope"],
            "assumptions": claim["assumptions"], "kind": claim["kind"],
            "old_dependencies": claim["dependencies"], "recommended_dependencies": new_dependencies,
            "recommendation": "VERIFIED", "review_state": "CLEAR",
            "recommendation_condition": "Exactly the approved editorial wording and normal revision/evidence bookkeeping are applied; these exact premises retain VERIFIED/CLEAR at revision2 with immutable prior audits. This report does not approve unrelated edits.",
            "dependency_uses": premise_uses[cid],
            "dependency_editorial_bindings": [{"id": d["id"], "from_revision": 1, "to_revision": 2,
                "old_claim_sha256": reviewed[d["id"]]["reviewed_claim_sha256"],
                "old_assumptions": reviewed[d["id"]]["original_assumptions"],
                "approved_assumptions": reviewed[d["id"]]["recommended_assumptions"]} for d in claim["dependencies"]],
            "original_verification_records_preserved": claim["verification"],
            "math_unchanged_without_automorphism_assumption": True,
            "written_audit": (OUT / "review.md").relative_to(ROOT).as_posix(),
            "inputs_sha256": bindings,
            "fresh_exact_calculation": dual_results if cid == DUAL else dict(affine_constant=constant, exact_box_upper=upper,
                free_edge_mappings=2160, fixed_literals=44, zero_extended_vector_agrees=True, literal_ordered_terms=99*99),
            "controls": {"known_negative_quadratics": {"K5_G": -20, "K1_25_H": -50}, "corruptions_rejected": rejected,
                         "exhaustive_three_variable_box_cases": boxes,
                         "historic_controls": "Original independent audit controls authenticated, not all replayed"},
            "shared_components": ["Python standard library exact integers and JSON", "PyYAML exact ledger parsing",
                "Immutable previous independent audits; full encoding proof replay is not repeated",
                "Reviewer also authored the old independent dual-Gram checker and editorial review; original Gram and w81 discoveries are by other agents"],
            "limitations": ["Editorial dependency-impact retention only; no broader theorem or scope change",
                "No new claim of target existence, unrestricted nonexistence, external review, CNF SAT/UNSAT, or candidate feasibility",
                "The two dependent claim assumptions themselves are unchanged; only their stated dependency pins are revised",
                "No schema source, original artifact, or ledger is modified"],
            "artifact_availability": "LOCAL_ONLY", "solver_calls": 0,
        }
        path = OUT / (name + ".json")
        with path.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
        outputs.append({"claim_id": cid, "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)})
    need(all(digest(ROOT / p) == expected for p, expected in bindings.items()), "input stability")
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
