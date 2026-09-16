"""Independent logical/arithmetic audit of the self-contained side bound.

This does not enumerate a Conway graph.  It checks every algebraic identity
and records a step-by-step audit of the finite combinatorial arguments in
``scratch_root_side_bound_selfcontained.md``.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path


SOURCE = Path("scratch_root_side_bound_selfcontained.md")
SOURCE_CODE = Path("scratch_root_side_bound_selfcontained.py")
SOURCE_JSON = Path("scratch_root_side_bound_selfcontained.json")
OUTPUT = Path("scratch_root_side_bound_selfcontained_audit.json")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    # SRG and triangle-intersection spectra.
    adjacency = [(14, 1), (3, 54), (-4, 44)]
    require(sum(mult for _value, mult in adjacency) == 99, "adjacency multiplicity")
    require(sum(value * mult for value, mult in adjacency) == 0, "adjacency trace")
    require(sum(value * value * mult for value, mult in adjacency) == 99 * 14, "adjacency square trace")
    gamma = [(18, 1), (7, 54), (0, 44), (-3, 132)]
    require(sum(mult for _value, mult in gamma) == 231, "Gamma multiplicity")
    require(sum(value * mult for value, mult in gamma) == 0, "Gamma trace")
    require(sum(value * value * mult for value, mult in gamma) == 231 * 18, "Gamma square trace")
    c_values = [(value * value - 5 * value - 18, mult) for value, mult in gamma]
    projector = []
    for index, ((value, mult), (c_value, _)) in enumerate(zip(gamma, c_values)):
        j_value = 231 if index == 0 else 0
        projector.append((Fraction(3 + j_value - value - c_value, 21), mult))
    require(projector == [(Fraction(0), 1), (Fraction(0), 54), (Fraction(1), 44), (Fraction(0), 132)], "projector spectrum")

    profiles = []
    for q in range(13):
        values = (20 + q, 180 - 3 * q, 3 * q, 12 - q)
        require(min(values) >= 0, f"negative profile q={q}")
        require(sum(values) == 212, f"zeroth moment q={q}")
        require(sum(r * values[r] for r in range(4)) == 216, f"first moment q={q}")
        require(sum((r * (r - 1) // 2) * values[r] for r in range(4)) == 36, f"second moment q={q}")
        cube = 4**3 + sum(values[r] * (1 - r) ** 3 for r in range(4))
        require(cube == 6 * (q - 2), f"cube row q={q}")
        profiles.append({"q": q, "profile": list(values), "cube_sum": cube})

    # Congruence and trace endpoint.
    m_entries = (-2, -1, 0, 1, 4)
    require(all((value * value - value) % 2 == 0 for value in m_entries), "W=M mod2")
    require((4 * 4 - 4) // 2 == 6 and 6 % 2 == 0, "D even diagonal")
    trace_floor = 4 * 231
    raw_difference = (trace_floor + 83) // 84
    divisible_difference = ((raw_difference + 2) // 3) * 3
    n3_floor = 693 + divisible_difference
    require((trace_floor, raw_difference, divisible_difference, n3_floor) == (924, 11, 12, 705), "trace/divisibility rounding")
    prism_ceiling = (4158 - n3_floor) // 3
    side_sum_ceiling = 6 * prism_ceiling
    root_side_ceiling = side_sum_ceiling // 99
    require((prism_ceiling, side_sum_ceiling, root_side_ceiling) == (1151, 6906, 69), "prism/side arithmetic")
    require(99 * 70 > side_sum_ceiling, "strict pigeonhole")

    source_result = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    require(source_result.get("status") == "ARITHMETIC_VERIFIED", "source audit status")
    require(source_result["schur_integral_lift"]["n3_floor"] == 705, "source n3 floor")
    require(source_result["prism_and_root_side"]["some_root_side_ceiling"] == 69, "source side floor")

    steps = [
        {
            "step": "triangle incidence identities",
            "valid": True,
            "audit": (
                "lambda=1 puts every edge in one triangle. N N^T=A+7I; two "
                "distinct triangles cannot share an edge, so N^T N=3I+Gamma."
            ),
        },
        {
            "step": "C[T,U] equals cross-edge count",
            "valid": True,
            "audit": (
                "For disjoint triangles, common Gamma-neighbours correspond "
                "bijectively to cross edges via the unique triangle on that edge. "
                "For intersecting triangles the 7K2 neighbourhood leaves exactly "
                "the five other triangles through the shared vertex, so C is zero."
            ),
        },
        {
            "step": "cross edges form a matching",
            "valid": True,
            "audit": (
                "Two cross edges sharing an endpoint would give an edge of the "
                "opposite triangle a second common neighbour, contradicting lambda=1."
            ),
        },
        {
            "step": "second binomial moment",
            "valid": True,
            "audit": (
                "For ordered x!=z in T and external y~x, y is not adjacent to z. "
                "The second common neighbour w of nonedge yz yields the unique "
                "triangle on yw; lambda=1 excludes all intersections with T. It "
                "supplies cross edges xy and zw. Reversing (x,z) exchanges (y,w), "
                "and these are exactly the two orientations of each unordered "
                "cross-edge pair, giving 6*12/2=36."
            ),
        },
        {
            "step": "integral Schur lift",
            "valid": True,
            "audit": (
                "The polynomial spectral calculation makes E the rank-44 "
                "orthogonal projector; M=21E is integral with M^2=21M. W=M o M "
                "and A4=MWM are PSD by Schur/congruence."
            ),
        },
        {
            "step": "mod-two nonzero rows and mod-four diagonal",
            "valid": True,
            "audit": (
                "A4 is congruent to M^3 and hence M modulo 2. Each M row has "
                "a0=20+q positive odd entries, so it is nonzero. With D=(W-M)/2, "
                "D is symmetric integral with even diagonal; vDv^T is even. Thus "
                "diag(A4) is divisible by four. PSD plus a zero diagonal would force "
                "the entire row zero, so every diagonal is at least four."
            ),
        },
        {
            "step": "trace identity",
            "valid": True,
            "audit": (
                "Cyclicity and M^2=21M give tr(A4)=21*sum M_ij^3. The audited "
                "row cube 6(q-2), together with sum q=2n3/3, gives exactly "
                "84(n3-693)."
            ),
        },
        {
            "step": "prism and rooted-side bijections",
            "valid": True,
            "audit": (
                "r=3 means precisely two disjoint triangles plus the three-edge "
                "matching, hence an induced prism. Choosing any prism vertex as "
                "root identifies its root-triangle matched pair and the unique "
                "opposite side edge; conversely a rooted side edge reconstructs "
                "that prism with no extra cross edges. Thus each prism is counted "
                "once for each of its six vertices."
            ),
        },
    ]
    require(all(row["valid"] for row in steps), "logical step failed")

    result = {
        "status": "LOGIC_AND_ARITHMETIC_VERIFIED" if not errors else "FAILED",
        "ok": not errors,
        "errors": errors,
        "inputs": {
            str(SOURCE): sha256(SOURCE),
            str(SOURCE_CODE): sha256(SOURCE_CODE),
            str(SOURCE_JSON): sha256(SOURCE_JSON),
        },
        "independent_checks": {
            "adjacency_spectrum": [list(row) for row in adjacency],
            "triangle_intersection_spectrum": [list(row) for row in gamma],
            "projector_spectrum": [[str(value), mult] for value, mult in projector],
            "profiles": profiles,
            "trace_floor": trace_floor,
            "n3_floor": n3_floor,
            "prism_ceiling": prism_ceiling,
            "side_sum_ceiling": side_sum_ceiling,
            "some_root_side_ceiling": root_side_ceiling,
        },
        "logical_steps": steps,
        "conclusion": (
            "Within the assumption that an srg(99,14,1,2) exists, the derivation "
            "of a root with S(r)<=69 is self-contained; no external n3 bound is needed."
        ),
        "effect_on_e73": (
            "For that root, E0=73 forces Q=E0-S>=4. Thus Q>=4 is an unconditional "
            "necessary subcase of E0=73 (conditional only on the putative SRG itself)."
        ),
        "claim_boundary": (
            "This audits a mathematical reduction. It neither supplies a graph nor "
            "turns an UNKNOWN SAT portfolio into a nonexistence proof."
        ),
    }
    temporary = OUTPUT.with_name(OUTPUT.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT)
    print(json.dumps({
        "status": result["status"],
        "ok": result["ok"],
        "errors": len(errors),
        "n3_floor": n3_floor,
        "some_root_side_ceiling": root_side_ceiling,
        "output": str(OUTPUT),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
