# Two root-group-0 same-sign coordinates

This is a new conditional family, labeled `PARTIAL_K_TWO_SAME_SIGN_COORDINATES_ROOT0_V1`. Both same_0 and same_1 coordinates of baseline 18481 at root group 0 are free. Exactly 156 baseline K edges remain fixed, including all seven cross matchings and the twelve other same-sign matchings. All same-fibre and unlisted other-coordinate absences remain fixed. The only unknown edges are 120 edges in the two freed coordinates and 1,680 disjoint-support edges.

The 24 affected centers have partial degree 5 and require nine further outer neighbors. The other 60 centers require eight. The producer reuses the previous frozen quota/conflict/resource-cap enumeration helpers; this shared code is disclosed and is not an independent checking path.

The preregistered pilot centers were 0, 2, 24, followed by all other centers in ascending order. Limits were 180 enumeration seconds, ten million search nodes, one million domains per center, and 200,000 total completed domains. All 84 centers completed without reaching a cap: 89,308 domain choices, largest center 3,218, 746,473 search nodes including calibration, 4.766 measured seconds.

All 54,478 choices from the preceding one-coordinate family embed. For every center the producer adds precisely those neighbors that were fixed before and are now unknown, then checks equality of the full old and new outer neighborhoods. Each new domain record preserves the old-to-new domain-ID mapping. This embedding is a containment control; it does not establish completeness of the larger family.

Three small restricted universes, at centers 0, 2, 24, were also enumerated by direct subset insertion in the full 99-vertex partial graph. Each agrees with the optimized enumerator, and each deliberately missing-edge corruption fails. Complete-domain status remains CANDIDATE until the separate verifier independently reconstructs all 84 domain sets under this new scope.

Every completed center has its own immutable domain file and checkpoint hash inventory. The run finished completely, so there is no pending center to resume. A reproduction must use a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --cache-dir .uv-cache-20260917 python acceleration/theory_20260917_partial_two_matchings.py --out acceleration/results/FRESH_TWO_COORDINATE_REPLAY
```

No LP was launched. The one-coordinate positive certificate does not automatically apply to this broader family. A new moment matrix must be built and checked against these new domain IDs and fixed-neighbor sets before an exclusion can be claimed. Target resolution remains UNKNOWN, and no process remains running at completion.
