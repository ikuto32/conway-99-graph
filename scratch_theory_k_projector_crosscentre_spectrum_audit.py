"""Independent arithmetic and noncommutative cubic expansion audit."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from math import comb
from pathlib import Path


CERT = Path("scratch_theory_k_projector_crosscentre_spectrum.json")
OUT = Path("scratch_theory_k_projector_crosscentre_spectrum_audit.json")


def trace_reduction(word: str) -> tuple[str, int]:
    if not word:
        return "constant", 231
    if word == "M":
        return "constant", 924
    if word == "K":
        return "constant", 0
    if len(word) == 2:
        return "constant", {"MM": 19404, "MK": -8316,
                             "KM": -8316, "KK": 8316}[word]
    if word == "MMM":
        return "constant", 441 * 924
    if word.count("M") == 2:
        return "constant", 21 * -8316
    if word.count("M") == 1:
        return "q", 21
    assert word == "KKK"
    return "d", 1


def expand_trace(factors: tuple[str, ...]) -> dict[str, int]:
    terms = {"P": (("M", 1), ("K", 1), ("", -4)),
             "K": (("K", 1),)}
    answer = Counter()
    for selection in itertools.product(*(terms[factor] for factor in factors)):
        coefficient = 1
        for _, value in selection:
            coefficient *= value
        variable, multiplier = trace_reduction("".join(word for word, _ in selection))
        answer[variable] += coefficient * multiplier
    return dict(answer)


def main() -> None:
    certificate = json.loads(CERT.read_text(encoding="utf-8"))
    assert certificate["source_note_sha256"] == hashlib.sha256(
        Path("scratch_theory_e0_zero_triangle_flag_relation.md").read_bytes()).hexdigest()
    expanded = []
    schur_rank = Counter()
    for row in certificate["spectral_table"]:
        sector = row["sector"]
        k = int(row["K"])
        multiplicity = int(row["multiplicity"])
        m = 21 * int(sector == "E")
        j = 231 * int(sector == "constant")
        p = m + k - 4
        z = j - 1 - p - k
        s = m + 12 + 2 * k
        assert (m, p, z, s) == tuple(row[name] for name in ("M", "P", "Z", "S"))
        # Independently expanded Schur products in the I,J,M,K basis.
        products = {
            "E0_E0": Fraction(j, 53361),
            "E0_E": Fraction(m, 4851),
            "E0_F": Fraction(1, 231) - Fraction(j, 53361) - Fraction(m, 4851),
            "E_E": Fraction(m + 12 + 2 * k, 441),
            "E_F": Fraction(792 - 12 * m - 22 * k, 4851),
            "F_F": Fraction(34023 + 143 * m + 242 * k + j, 53361),
        }
        for name, value in products.items():
            assert value >= 0
            assert value == Fraction(row["schur_projector_expression_eigenvalues"][name])
            if value > 0:
                schur_rank[name] += multiplicity
        expanded.extend([{"sector": sector, "K": k, "M": m, "P": p, "Z": z, "S": s}]
                        * multiplicity)
    assert len(expanded) == 231
    assert Counter(row["sector"] for row in expanded) == Counter({"constant": 1, "E": 44, "F": 186})
    assert dict(schur_rank) == certificate["schur_expression_ranks"]

    def trace(word: str) -> int:
        result = 0
        for row in expanded:
            value = 1
            for letter in word:
                value *= row[letter]
            result += value
        return result

    words = {"tr_M": "M", "tr_M2": "MM", "tr_K": "K", "tr_K2": "KK", "tr_K3": "KKK",
             "tr_P": "P", "tr_P2": "PP", "tr_Z": "Z", "tr_Z2": "ZZ", "tr_MK": "MK",
             "tr_PK": "PK", "tr_MK2": "MKK", "tr_P3": "PPP", "tr_P2K": "PPK",
             "tr_PK2": "PKK", "tr_S": "S", "tr_S2": "SS"}
    assert {name: trace(word) for name, word in words.items()} == certificate["traces"]
    assert trace("KKK") == 0 and trace("KK") == 8316
    q = Fraction(trace("MKK"), 21)
    eta = sum((row["K"] + 9) ** 2 for row in expanded if row["sector"] == "E")
    assert q == 4212 and eta == q - 3564 == 648
    assert Fraction(certificate["q"]) == q and Fraction(certificate["eta"]) == eta
    assert trace("KKK") + 42 * eta == 24948 + trace("PPK")
    assert expand_trace(("P", "P", "P")) == {"constant": -219912, "q": 63, "d": 1}
    assert expand_trace(("P", "P", "K")) == {"constant": -174636, "q": 42, "d": 1}
    assert expand_trace(("P", "K", "K")) == {"constant": -33264, "q": 21, "d": 1}
    relation_counts = {}
    for profile, claimed in certificate["all_ten_induced_relation_triangle_counts"].items():
        distinct = len(set(profile))
        divisor = {1: 6, 2: 2, 3: 1}[distinct]
        value, remainder = divmod(trace(profile), divisor)
        assert remainder == 0 and value == claimed and value >= 0
        relation_counts[profile] = value
    assert len(relation_counts) == 10 and sum(relation_counts.values()) == comb(231, 3)
    # Recompute every edge-colour incidence and every centred wedge incidence.
    degrees = {"P": 32, "K": 36, "Z": 162}
    for colour, degree in degrees.items():
        assert sum(profile.count(colour) * count for profile, count in relation_counts.items()) == 231 * degree // 2 * 229
    for a, b in itertools.combinations_with_replacement(degrees, 2):
        actual = 0
        for profile, count in relation_counts.items():
            for left, right in itertools.combinations(profile, 2):
                if sorted((left, right)) == sorted((a, b)):
                    actual += count
        expected = 231 * (comb(degrees[a], 2) if a == b else degrees[a] * degrees[b])
        assert actual == expected
    result = {
        "status": "INDEPENDENT_K_PROJECTOR_CROSSCENTRE_SPECTRAL_AUDIT_PASS",
        "producer_imported": False,
        "certificate_sha256": hashlib.sha256(CERT.read_bytes()).hexdigest(),
        "expanded_eigenvalue_slots": len(expanded),
        "pairwise_schur_projector_expressions_checked": 6,
        "general_noncommutative_cubic_expansions_checked": 3,
        "induced_relation_triples_checked": 10,
        "q": str(q), "eta": str(eta), "tau_K": 0,
        "entrywise_signed_projector_or_graph_claimed": False,
        "positive_E0_bound_claimed": False,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
