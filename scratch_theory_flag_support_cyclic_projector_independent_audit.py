"""Independent exact audit of the rank-44 circulant projector no-go."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path


INPUT = Path("scratch_theory_flag_support_cyclic_projector_search.json")
SOURCE = Path("scratch_theory_flag_support_cyclic_projector_search.py")
OUTPUT = Path("scratch_theory_flag_support_cyclic_projector_independent_audit.json")


def prime_factors(n):
    result = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            result.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        result.append(n)
    return result


def phi(n):
    result = n
    for p in prime_factors(n):
        result = result // p * (p - 1)
    return result


def mu(n):
    factors = prime_factors(n)
    product = 1
    for p in factors:
        product *= p
    if product != n:
        return 0
    return -1 if len(factors) % 2 else 1


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def ramanujan_via_divisors(order, displacement):
    # c_q(k)=sum_{d|gcd(q,k)} d*mu(q/d).
    common = math.gcd(order, displacement)
    return sum(d * mu(order // d) for d in divisors(common))


def main():
    stored = json.loads(INPUT.read_text(encoding="utf-8"))
    assert stored["status"] == "EXACT_CIRCULANT_PROJECTOR_ORBIT_SEARCH_COMPLETE"
    n = 231
    orders = divisors(n)
    sizes = {order: phi(order) for order in orders}
    supports = []
    for bits in itertools.product((0, 1), repeat=len(orders)):
        chosen = tuple(order for order, bit in zip(orders, bits) if bit)
        if sum(sizes[order] for order in chosen) == 44:
            supports.append(chosen)
    assert supports == [(3, 11, 21, 33)]

    chosen = supports[0]
    numerators = [sum(ramanujan_via_divisors(order, k) for order in chosen)
                  for k in range(n)]
    assert numerators[0] == 44
    off_histogram = Counter(
        value // 11 if value % 11 == 0 else f"{value}/11"
        for value in numerators[1:]
    )
    assert off_histogram == Counter({0: 132, "-3/11": 60,
                                     "-7/11": 22, 1: 10, "30/11": 6})
    assert any(value % 11 for value in numerators)

    result = {
        "status": "INDEPENDENT_EXACT_CYCLIC_PROJECTOR_NO_GO_AUDIT_PASS",
        "input_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "order": n,
        "required_rank": 44,
        "unique_Galois_stable_Fourier_support": list(chosen),
        "support_orbit_sizes": [sizes[order] for order in chosen],
        "scaled_entry_histogram_off_diagonal": {
            str(k): v for k, v in sorted(off_histogram.items(), key=lambda item: str(item[0]))
        },
        "integral": False,
        "conclusion": (
            "No rational circulant order-231 rank-44 projector P makes "
            "M=21P integral.  A rational circulant idempotent has a Galois-"
            "stable 0/1 Fourier support; rank 44 leaves the unique audited "
            "orbit union, whose Ramanujan sums have nonintegral /11 entries."
        ),
        "scope": (
            "This excludes only the circulant repair of the abstract control; "
            "it does not exclude noncirculant endpoint projectors or an SRG."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
