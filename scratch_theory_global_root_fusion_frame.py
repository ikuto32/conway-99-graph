"""Exact audit of a global/local eigenspace bridge for rooted fibres.

This is a necessary-condition calculation for a hypothetical
srg(99,14,1,2).  It uses only rational arithmetic and the fixed induced
graph on a closed neighbourhood.  It does not assume that the target graph
exists and it does not prove a positive lower bound for E0.
"""

from __future__ import annotations

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


N = 15


def zeros(n: int, m: int | None = None):
    if m is None:
        m = n
    return [[F(0) for _ in range(m)] for _ in range(n)]


def eye(n: int):
    out = zeros(n)
    for i in range(n):
        out[i][i] = F(1)
    return out


def add(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def sub(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(c, a):
    return [[c * x for x in row] for row in a]


def transpose(a):
    return [list(row) for row in zip(*a)]


def mul(a, b):
    bt = transpose(b)
    return [[sum((x * y for x, y in zip(row, col)), F(0)) for col in bt] for row in a]


def rank(a):
    a = [row[:] for row in a]
    n = len(a)
    m = len(a[0]) if n else 0
    r = 0
    for c in range(m):
        pivot = next((i for i in range(r, n) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        z = a[r][c]
        a[r] = [x / z for x in a[r]]
        for i in range(n):
            if i != r and a[i][c]:
                z = a[i][c]
                a[i] = [x - z * y for x, y in zip(a[i], a[r])]
        r += 1
        if r == n:
            break
    return r


def mat_eq(a, b):
    return all(x == y for ar, br in zip(a, b) for x, y in zip(ar, br))


def star_adjacency():
    """The cone over seven disjoint edges on [root, 14 neighbours]."""
    a = zeros(N)
    for u in range(1, 15):
        a[0][u] = a[u][0] = F(1)
    for j in range(7):
        u, v = 1 + 2 * j, 2 + 2 * j
        a[u][v] = a[v][u] = F(1)
    return a


def primitive_block(which: str, a):
    i = eye(N)
    j = [[F(1) for _ in range(N)] for _ in range(N)]
    if which == "minus4":
        # E_-4=(3I-A+J/9)/7.
        return scale(F(1, 7), add(sub(scale(F(3), i), a), scale(F(1, 9), j)))
    if which == "plus3":
        # E_3=(A+4I-2J/11)/7.
        return scale(F(1, 7), sub(add(a, scale(F(4), i)), scale(F(2, 11), j)))
    raise ValueError(which)


def pair_projectors():
    pd = zeros(N)
    pc = zeros(N)
    for q in range(7):
        u, v = 1 + 2 * q, 2 + 2 * q
        pd[u][u] = pd[v][v] = F(1, 2)
        pd[u][v] = pd[v][u] = F(-1, 2)
    for u in range(1, 15):
        for v in range(1, 15):
            same_pair = (u - 1) // 2 == (v - 1) // 2
            pc[u][v] = (F(1, 2) if same_pair else F(0)) - F(1, 14)
    return pd, pc


def outer_projector(which: str):
    """Moore-Penrose inverse of the primitive-idempotent star block."""
    pd, pc = pair_projectors()
    if which == "minus4":
        # Nonzero eigenvalues: 4/7 on pair differences, 2/7 on
        # centred pair constants, 20/21 on (7,-2,...,-2).
        w = [F(7)] + [F(-2)] * 14
        pw = [[x * y / F(105) for y in w] for x in w]
        return add(add(scale(F(7, 4), pd), scale(F(7, 2), pc)), scale(F(21, 20), pw))
    if which == "plus3":
        # Nonzero eigenvalues: 3/7, 5/7, 69/77; the last vector is
        # (14,3,...,3), of squared norm 322.
        w = [F(14)] + [F(3)] * 14
        pw = [[x * y / F(322) for y in w] for x in w]
        return add(add(scale(F(7, 3), pd), scale(F(7, 5), pc)), scale(F(77, 69), pw))
    raise ValueError(which)


def category_values(h):
    return {
        "root_root": h[0][0],
        "root_neighbour": h[0][1],
        "neighbour_diag": h[1][1],
        "neighbour_mate": h[1][2],
        "neighbour_nonmate": h[1][3],
    }


def aggregate_middle_categories(vals):
    """Sum the embedded local pseudoinverses over all 99 roots.

    For a fixed diagonal entry there is one root-role and 14 neighbour-roles.
    An adjacent pair has two root/neighbour roles and its unique common root
    sees the pair as mates.  A nonedge has two common roots, both seeing a
    nonmate pair.
    """
    return {
        "diagonal": vals["root_root"] + 14 * vals["neighbour_diag"],
        "adjacent": 2 * vals["root_neighbour"] + vals["neighbour_mate"],
        "nonadjacent": 2 * vals["neighbour_nonmate"],
    }


def bm_eigenvalue(cats, theta: int):
    # H=(d-n)I+(a-n)A+nJ; J vanishes on nonprincipal eigenspaces.
    return cats["diagonal"] - cats["nonadjacent"] + theta * (
        cats["adjacent"] - cats["nonadjacent"]
    )


def fibre_free_projector():
    """Projector onto ker(unsigned K7 vertex-edge incidence), order 21."""
    edges = [(i, j) for i in range(7) for j in range(i + 1, 7)]
    out = zeros(21)
    for x, ex in enumerate(edges):
        for y, ey in enumerate(edges):
            common = len(set(ex) & set(ey))
            out[x][y] = (F(1) if x == y else F(0)) - F(common, 5) + F(1, 15)
    return out


def fs(x: F):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def map_fractions(obj):
    if isinstance(obj, F):
        return fs(obj)
    if isinstance(obj, dict):
        return {k: map_fractions(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [map_fractions(v) for v in obj]
    return obj


def main():
    a = star_adjacency()
    report = {
        "status": "GLOBAL_ROOT_FUSION_FRAME_IDENTITY_PASS",
        "scope": "exact necessary identities; no positive E0 lower bound or Conway-99 resolution",
        "closed_neighbourhood": {},
        "tight_fusion_frames": {},
        "free_fibre_projector": {},
        "motif_bridge": {},
        "boundary": {},
    }

    expected = {
        "minus4": {"rank": 14, "kernel": [F(4)] + [F(1)] * 14, "tight": F(63, 2)},
        "plus3": {"rank": 14, "kernel": [F(-3)] + [F(1)] * 14, "tight": F(77, 3)},
    }
    for which in ("minus4", "plus3"):
        g = primitive_block(which, a)
        h = outer_projector(which)
        gh = mul(g, h)
        assert rank(g) == expected[which]["rank"]
        assert mat_eq(mul(mul(g, h), g), g)
        assert mat_eq(mul(mul(h, g), h), h)
        assert mat_eq(gh, transpose(gh))
        ker = expected[which]["kernel"]
        assert all(sum((g[i][j] * ker[j] for j in range(N)), F(0)) == 0 for i in range(N))
        vals = category_values(h)
        cats = aggregate_middle_categories(vals)
        theta = -4 if which == "minus4" else 3
        tight = bm_eigenvalue(cats, theta)
        assert tight == expected[which]["tight"]
        # 99 local complements of rank 14 have the same trace as the
        # asserted scalar times the global primitive-idempotent rank.
        global_rank = 44 if which == "minus4" else 54
        assert tight * global_rank == 99 * 14
        report["closed_neighbourhood"][which] = {
            "rank": rank(g),
            "kernel_vector": list(map(fs, ker)),
            "pseudoinverse_categories": map_fractions(vals),
            "summed_middle_categories": map_fractions(cats),
        }
        report["tight_fusion_frames"][which] = {
            "sum_local_evaluation_complement_projectors": f"{fs(tight)} E_{which}",
            "sum_supported_projectors": (
                f"{fs(F(99)-tight)} E_{which}"
            ),
        }

    pf = fibre_free_projector()
    assert rank(pf) == 14
    assert mat_eq(mul(pf, pf), pf)
    assert all(sum(row, F(0)) == 0 for row in pf)
    edges = [(i, j) for i in range(7) for j in range(i + 1, 7)]
    values = {}
    for x, ex in enumerate(edges):
        for y, ey in enumerate(edges):
            common = len(set(ex) & set(ey))
            key = "same" if x == y else ("overlap" if common else "disjoint")
            values.setdefault(key, pf[x][y] / 4)  # lift through four-point fibres
            assert values[key] == pf[x][y] / 4
    assert values == {"same": F(1, 6), "overlap": F(-1, 30), "disjoint": F(1, 60)}

    # The ordered adjacent-pair contribution is twice the unordered sum.
    # There are E0 same-fibre, 168-2E0 overlapping, and 336+E0
    # disjoint-support outer edges.  Check constant and E0 coefficients.
    same, overlap, disjoint = values["same"], values["overlap"], values["disjoint"]
    constant = 2 * (168 * overlap + 336 * disjoint)
    e0_coefficient = 2 * (same - 2 * overlap + disjoint)
    assert constant == 0 and e0_coefficient == F(1, 2)

    report["free_fibre_projector"] = {
        "rank": 14,
        "lifted_entry_values": map_fractions(values),
        "row_sum": 0,
        "trace_P_r_A": "E0(r)/2",
        "trace_P_r_E_minus4": "(84-E0(r))/14",
        "trace_P_r_E_plus3": "14-(84-E0(r))/14",
        "orthogonality": "P_r is orthogonal to both local evaluation-complement spaces L_r^- and L_r^+",
    }
    report["motif_bridge"] = {
        "sum_r_(84-E0(r))": "n3+z11/4",
        "trace_Eminus_sumPr": "(n3+z11/4)/14",
        "trace_Eplus_sumPr": "1386-(n3+z11/4)/14",
        "minus_cross_root_energy": "sum_{r!=s} tr(P_r L_s^-)=9/4*(n3+z11/4)",
    }
    # Split the cross-root energy according to s adjacent/nonadjacent to r.
    # On Gamma_2(r), summing the embedded minus-four pseudoinverses over
    # s in N(r) gives 2*c*I + e*Q + (d-e)*T, where Q records a common exact
    # root neighbour and T=B o Q is the two-factor of exact-symbol edges.
    vm = category_values(outer_projector("minus4"))
    assert 2 * (vm["neighbour_diag"] - vm["neighbour_nonmate"]) == F(21, 4)
    assert vm["neighbour_mate"] - vm["neighbour_nonmate"] == F(7, 8)
    # If K_r^-=E_- P_r E_-, then tr(K)=tau/14 and QK=-2K.
    # Hence X_adj=3*tau/8+(7/8)h, h=tr(KT).  Since ||T||<=2,
    # |h|<=tau/7, giving the exact interval below.  The complement follows
    # from X_adj+X_nonadj=9*tau/4.
    report["adjacent_nonadjacent_split"] = {
        "definition": "K_r^-=E_- P_r E_-, h_r=tr(K_r^- T_r), tau_r=84-E0(r)",
        "adjacent_exact": "sum_{s in N(r)} tr(P_r L_s^-)=3*tau_r/8+7*h_r/8",
        "operator_bound": "|h_r|<=tau_r/7 because T_r is 2-regular",
        "adjacent_interval": "tau_r/4 <= sum_{s in N(r)} tr(P_r L_s^-) <= tau_r/2",
        "nonadjacent_interval": "7*tau_r/4 <= sum_{s in Gamma_2(r)} tr(P_r L_s^-) <= 2*tau_r",
        "scope": "a localization of the missing cross-root invariant, not a bound on tau_r",
    }
    report["boundary"] = {
        "new_numerical_lower_bound_on_E0": None,
        "reason": "Tight-frame positivity gives only n3+z11/4>=0; an upper bound on the paired cross-root energy is still missing.",
        "next_target": "bound tr(P_r L_s^-) by the relation r~s versus r not~s, or couple the frame to four-root mask-3/mask-12 covariance",
    }

    out = Path(__file__).with_suffix(".json")
    payload = json.dumps(map_fractions(report), indent=2, sort_keys=True) + "\n"
    out.write_text(payload, encoding="utf-8", newline="\n")
    print(report["status"])
    print(hashlib.sha256(payload.encode()).hexdigest())


if __name__ == "__main__":
    main()
