"""Exact search for rational circulant 21-projectors of order 231.

A rational circulant orthogonal projector has a Galois-stable Fourier
support, hence a union of exact-order character orbits.  The integral
triangle projector would be M=21P, with rank 44 and diagonal four.  This
script enumerates every union of cyclotomic orbits of total size 44 and
tests its Ramanujan-sum entries against the triangle-projector alphabet.
"""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from pathlib import Path


OUTPUT = Path("scratch_theory_flag_support_cyclic_projector_search.json")
N = 231
SCALE_DENOMINATOR = 11  # 21/231


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def phi(n: int) -> int:
    return sum(math.gcd(i, n) == 1 for i in range(1, n + 1))


def mobius_squarefree(n: int) -> int:
    primes = []
    trial = 2
    left = n
    while trial * trial <= left:
        if left % trial == 0:
            left //= trial
            primes.append(trial)
            if left % trial == 0:
                return 0
            while left % trial == 0:
                left //= trial
        trial += 1
    if left > 1:
        primes.append(left)
    return -1 if len(primes) % 2 else 1


def ramanujan(order: int, displacement: int) -> int:
    common = math.gcd(order, displacement)
    quotient = order // common
    return mobius_squarefree(quotient) * phi(order) // phi(quotient)


def main() -> None:
    orders = divisors(N)
    orbit_sizes = {order: phi(order) for order in orders}
    candidates = []
    for bits in itertools.product((0, 1), repeat=len(orders)):
        support = [order for order, bit in zip(orders, bits) if bit]
        if sum(orbit_sizes[order] for order in support) != 44:
            continue
        numerators = [
            sum(ramanujan(order, displacement) for order in support)
            for displacement in range(N)
        ]
        integral = all(value % SCALE_DENOMINATOR == 0 for value in numerators)
        entries = [
            value // SCALE_DENOMINATOR if value % SCALE_DENOMINATOR == 0
            else f"{value}/{SCALE_DENOMINATOR}"
            for value in numerators
        ]
        off_diagonal_counts = Counter(entries[1:])
        alphabet_ok = integral and set(entries[1:]) <= {-2, -1, 0, 1}
        endpoint_profile = (
            alphabet_ok
            and entries[0] == 4
            and off_diagonal_counts == Counter({0: 162, 1: 32, -1: 36})
        )
        candidates.append(
            {
                "orders": support,
                "orbit_sizes": [orbit_sizes[order] for order in support],
                "integral": integral,
                "diagonal": entries[0],
                "off_diagonal_counts": {
                    str(key): value
                    for key, value in sorted(off_diagonal_counts.items(), key=lambda item: str(item[0]))
                },
                "alphabet_ok": alphabet_ok,
                "endpoint_profile": endpoint_profile,
                "negative_one_positive_displacements": [
                    displacement
                    for displacement in range(1, (N + 1) // 2)
                    if entries[displacement] == -1
                ],
                "positive_one_positive_displacements": [
                    displacement
                    for displacement in range(1, (N + 1) // 2)
                    if entries[displacement] == 1
                ],
            }
        )

    result = {
        "status": "EXACT_CIRCULANT_PROJECTOR_ORBIT_SEARCH_COMPLETE",
        "order": N,
        "rank": 44,
        "scale": "21/231=1/11",
        "cyclotomic_orbit_sizes": {str(k): v for k, v in orbit_sizes.items()},
        "candidate_count": len(candidates),
        "endpoint_profile_count": sum(item["endpoint_profile"] for item in candidates),
        "candidates": candidates,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
