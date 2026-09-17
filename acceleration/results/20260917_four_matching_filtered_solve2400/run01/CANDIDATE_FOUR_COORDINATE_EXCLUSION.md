# Candidate exclusion of the four-coordinate family

Proposed claim: `C-PARTIAL-K-FOUR-COORDINATE-EXCLUSION`, revision 1. Status at production: CANDIDATE, pending independent checking of the exact bound and its composition with the matching-filter proof.

For every graph on the fixed root-scaffold labels retaining the 144 K edges and prescribed absences in `../../20260917_partial_four_matchings/manifest.json`, and permitting changes only among the 240 legal same-sign coordinate edges at root groups 0 and 1 and the 1,680 disjoint-support edges, no completion satisfies SRG(99,14,1,2).

Both same-sign coordinates at root groups 0 and 1 may vary. All seven cross matchings and the ten other same-sign matchings remain fixed. This is a conditional family exclusion, not an unrestricted Conway-99 resolution; no nontrivial automorphism is assumed.

The complete original local-domain universe has 290,460 choices across 84 centers. The independently reviewed neighborhood-matching filter excludes exactly 59,581 original choices and retains 230,879, with no empty domain. Therefore every actual completion must select one of the retained stars at every center. The filtered moment model preserves the original 5,490 rows and 6,972 slack columns, selecting precisely those surviving probability columns by their original IDs.

The independent filter proof is `../../20260917_independent_review/four_coordinate_matching_filter/summary.json`. The independently checked filtered model is `../../20260917_independent_review/four_matching_filtered_moments.json`, SHA-256 `472b7f332a99560fd961d7b6a411edd5db619504c21dd6285470f579e0ba2c51`. The run manifest binds both exact audit hashes. Those approvals do not themselves approve this newly produced bound.

Let Mz=b be the full co-neighbor moment equations and Rz=0 be the 1,920 reciprocal-edge equations. Variables z range over the 84 hard nonnegative surviving-star simplices. Every completion gives zero moment residual. The certificate provides integer moment weights y with |y| <= 1048576 and integer reciprocity weights q. Its exact support-function lower bound is

    [ y*b - sum_t max_(S retained at t) (M^T*y + R^T*q)_(t,S) ] / 1048576
      = 275944444 / 1048576
      = 68986111 / 262144
      > 0.

The approximate display value is 263.16112899780273. The result is a lower bound on the named filtered moment objective, not a measure of target-wide search coverage. The independent verifier must evaluate every one of the 230,879 retained columns directly from its original raw neighborhood, reproduce all 84 maxima, verify the removed/retained partition and proof dependencies, and test corruptions before promoting the exclusion.

Certificate: `exact_support_bound.json`, SHA-256 `51d74ca27a16e624bbe898fa7053e2ac9a8ddab4bbd7be5d824e2657dfc371e9`. The filtered model's original-ID maps are in `../../20260917_four_matching_filtered_moments/model.json`. No numerical solver-feasibility or optimality assumption is needed for the rational support bound.

HiGHS 1.15.1 completed in 1432.875 solver seconds within the preregistered 2400-second limit, reporting valid primal and dual vectors and numerical objective 263.1613994433284. These numerical facts are not the proof. Raw vectors are `numeric_lp.json`, SHA-256 `731736041873e28753bbd5cc32a97f114259c76184c604c91c142d03cda1738f`; its 12,830,534 bytes remain local and are also preserved as two byte-exact companion parts in `chunk_manifest.json`.

Immutable heartbeat records preserve actual execution-session observations, including the final exit-zero observation. The solver was not restarted. No process remains running. Any later approval or rejection must be recorded separately, preserving this candidate statement and original evidence.
