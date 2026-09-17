# Same-model 240-second replay

The frozen unfiltered full-moment model passed independent formulation review in `../20260917_independent_review/partial_moments.json` (SHA-256 `1d4d08ecc9e73a00e06d210fa5137e7885e677756dc8f33b016fa3227ddec5e1`). This run loads that exact integer matrix, keeping all 54,478 original partial-K choices. It does not use the separate matching-filtered domains.

Before this run, a separate exact extraction from the failed 60-second run's arbitrary raw weights gave -3898195488/1048576. A separately preregistered four-sign test retained all four results; every bound was negative. These artifacts remain in `../20260917_partial_matching_moment_arbitrary_weights/` and `../20260917_partial_matching_moment_four_signs/`.

HiGHS 1.15.1 IPM with one thread and no crossover reached the 240-second limit after 240.187 measured solver seconds. It returned neither a valid primal nor a valid dual. The raw summary objective of zero is unusable. The internal iteration objectives also are not certificates.

The algebraic support-function bound accepts any finite row weights, without assuming that they are solver-feasible. Using the saved raw weights, rounded with denominator 1048576 and moment weights clipped to [-1,1], produced

    -123695226349 / 1048576 = approximately -117964.960431.

This is negative and establishes no exclusion. It is a producer exact-arithmetic calculation pending independent review. The discrepancy between this bound and positive internal solver objectives has not been explained; no assertion is made that invalid returned arrays correspond to a useful unpresolved dual.

The exact bound, raw arrays, validity flags, solver log, immutable model references and command are preserved in this directory. The larger cap allowed HiGHS's automatic presolve dependency search a larger time allowance; it removed 84 additional redundant rows. The underlying saved integer model was unchanged. This is not a performance comparison.

No process remains running at completion. No exact feasibility, conditional exclusion, or target resolution was obtained. Scope remains the one-coordinate family with 162 fixed K edges and all prescribed absences; overall search coverage is UNKNOWN.
