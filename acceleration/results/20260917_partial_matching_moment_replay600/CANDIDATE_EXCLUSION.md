# Candidate exclusion of the one-coordinate partial-K family

Proposed claim: `C-PARTIAL-K-ONE-COORDINATE-EXCLUSION`, revision 1. Status: CANDIDATE, pending independent verification of the exact bound. This is a conditional family exclusion, not a resolution of Conway-99.

For every graph on the fixed root-scaffold labels that retains the 162 fixed K edges and all prescribed absences recorded by `../20260917_partial_matching/manifest.json`, and permits changes only among its 60 freed matching-coordinate edges and 1,680 disjoint-support edges, no completion satisfies the full SRG(99,14,1,2) equation.

The candidate proof uses all 54,478 frozen original partial-K star choices, without the later matching filter. Independent complete-domain verification is recorded in `../20260917_independent_review/partial_matching/summary.json`; independent necessity and exact integer matrix verification are recorded in `../20260917_independent_review/partial_moments.json` (SHA-256 `1d4d08ecc9e73a00e06d210fa5137e7885e677756dc8f33b016fa3227ddec5e1`). These are dependencies, not approval of this newly produced certificate.

The model makes 84 star simplices and 1,740 reciprocal edge equations hard. Its phase-I objective is the L1 residual of all 3,486 full outer-pair co-neighbor moment equations. An actual completion must give objective zero. The frozen mathematical derivation is `../20260917_partial_matching_moments/MOMENT_MODEL_DERIVATION.md`.

For integer moment weights y bounded by 1048576 in magnitude and integer reciprocity weights q, `exact_support_bound.json` records every weight and all 84 maxima over the original per-center domain tables. Exact evaluation gives

    [ y*b - sum_t max_S (M^T*y + R^T*q)_(t,S) ] / 1048576
      = 590533056 / 1048576
      = 9227079 / 16384
      > 0.

The approximate value is 563.1762084960938. This is a lower bound on the named moment objective; it is not a graph quality score or a percentage of the unrestricted search. The certificate's validity depends on the exact algebra and complete domain maxima, not on floating-point optimality. The independent verifier must reproduce the weights, all domain evaluations and maximum sums, test corruptions, and approve the implication before this claim is promoted.

Certificate SHA-256: `bbc507e6c6734c056caf6198027541c86e2a8ecb2319788adedc2537369e2008`.

HiGHS 1.15.1 completed the 600-second-capped run in 268.687 solver seconds, reporting valid primal and dual vectors and numerical objective 563.1764056322008. This numerical objective is not the certificate. Full raw arrays are in `numeric_lp.json`, SHA-256 `10f59227ec47a499dfe551585de62835f1df3dce4121db2debcd1acc20ec9b5c`. The failed 60- and 240-second runs, invalid-vector diagnostics, and negative exact extractions remain preserved in their original directories.

No automorphism is assumed. No claim is made here about the number of coordinate matchings, exhaustive coverage of any larger K family, or the unrestricted target. No other coordinate is relaxed. No process remains running after this run's completion. A later review must be recorded separately without changing this candidate evidence.
