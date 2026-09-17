# Candidate exclusion of the two-coordinate partial-K family

Proposed claim: `C-PARTIAL-K-TWO-COORDINATE-EXCLUSION`, revision 1. Status at production: CANDIDATE, independent exact-certificate verification pending.

For every graph on the fixed root-scaffold labels retaining the 156 K edges and all prescribed absences in `../20260917_partial_two_matchings/manifest.json`, and allowing changes only among its 120 same-sign matching-coordinate edges at root group 0 and 1,680 disjoint-support edges, no completion satisfies SRG(99,14,1,2).

This is a conditional family exclusion. Both same_0 and same_1 coordinates of root group 0 may vary; the other twelve same-sign matchings and all seven cross matchings remain fixed. No nontrivial automorphism is assumed. No unrestricted target resolution or target-wide coverage denominator is claimed.

The new domain universe consists of all 89,308 unfiltered original local stars across 84 centers. Independent completeness and scope verification is `../20260917_independent_review/two_matchings/summary.json`, SHA-256 `f3d2ba90be5e8c27bc64c2e4941174d36fc3ddfcbc29ce25da872df652383acb`. Independent exact necessity/matrix verification is `../20260917_independent_review/two_matching_moments.json`, SHA-256 `5af1f353a70a16fc5f915195b911d782e360ffc0690463936b7a9dea983197ed`. Those approvals are dependencies and do not by themselves approve this new bound.

The complete model has 84 hard simplex equations, 1,800 hard reciprocal-edge equations, and 3,486 full co-neighbor moment equalities with L1 phase-I slacks. Any actual completion gives residual zero. The equation and necessity derivation are in `TWO_COORDINATE_MOMENT_MODEL.md`.

The certificate saves integer moment weights y with |y| <= 1048576, arbitrary integer reciprocity weights q, and all 84 maxima across the complete new per-center domains. Exact evaluation of the support-function expression gives

    [ y*b - sum_t max_S (M^T*y + R^T*q)_(t,S) ] / 1048576
      = 469399553 / 1048576
      > 0.

The approximate display value is 447.6542978286743. It is a lower bound for this named model, not a percentage of Conway-99 solved. The old one-coordinate certificate was not inherited: a separately preserved weight-transfer attempt gave a negative bound, and this run produced new weights for the larger domain.

Certificate: `exact_support_bound.json`, SHA-256 `708434c9485ba144a62fd4bf7d220dbf672c6fb3ee72a262cfb95e7584b55680`. The independent checker must rederive every new domain column directly from raw full neighborhoods, calculate all maxima and the RHS dot product, and test corrupted controls before promotion.

HiGHS 1.15.1 completed after 605.953 solver seconds within the preregistered 900-second cap, reporting valid primal/dual vectors and numerical objective 447.65452528574735. Solver optimality and this floating value are not the proof. Raw vectors are in `numeric_lp.json`, SHA-256 `63582dd460a81586b2bd184f7437c8336ebafc36d2890d24c04647dc62194c05`. The exact integer matrix, command, versions, input hashes, solver log and all raw vectors remain preserved.

No process remains running at completion. Later independent approval or rejection must be recorded separately, without changing these candidate artifacts.
