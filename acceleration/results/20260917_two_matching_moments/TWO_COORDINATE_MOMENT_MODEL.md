# Two-coordinate full moment model

Model: `PARTIAL_K_TWO_SAME_SIGN_COORDINATES_FULL_MOMENT_PHASE1_V1`. Status at build: CANDIDATE encoding, independent domain and matrix review pending. No solver was launched by the build stage.

This model uses every one of the 89,308 original domain choices from `../20260917_partial_two_matchings/`, with its new center-local sorted-mask IDs. It keeps the 156 fixed K edges and prescribed zeros of that family. Only the 120 edges of root-group-0 same_0 and same_1 coordinates and 1,680 disjoint-support edges are variable. No matching or pair-consistency filter is substituted.

For every outer pair v<w, the necessary equality is

    sum_(t,S) 1[{v,w} subset N_B,outer(t) union S] z(t,S) + x(v,w)
      = 2 - |support(v) intersect support(w)| - B(v,w).

Each full outer neighborhood has twelve vertices and contributes 66 co-neighbor pairs. The projected x(v,w) uses the smaller endpoint's local marginal on an unknown edge, and zero otherwise; fixed adjacency is accounted for by B. Common neighbors in the root neighborhood are exactly the support intersection. An actual graph completion selects one star for each center, has equal reciprocal edge marginals, and satisfies every equality. Thus a positive lower bound on the phase-I moment residual excludes only the declared family.

The complete integer matrix has 5,370 rows, 96,280 columns and 7,315,157 nonzeros: 84 hard simplex equations, 1,800 hard reciprocity equations, and 3,486 full moment equalities with negative and positive L1 slack variables. The probability columns total 89,308 and retain the original new-domain order. `model.json` saves row identities, offsets, fixed/unknown edges, supports, RHS, objective costs and bounds; `integer_augmented_csr.npz` saves the complete augmented integer matrix.

The builder reuses the earlier generic moment routines. Its 18 exact rook-graph witness controls and 36 coefficient/RHS corruption controls all pass. Those producer controls do not replace the required independent reconstruction of all new domains and all matrix columns.

The preregistration permits a 900-second HiGHS IPM solve with one thread and crossover disabled only after independent domain and model PASS receipts bind the exact artifacts. This is a larger domain than the one-coordinate run; the 900-second limit is a resource cap, not a runtime estimate. Automatic presolve sublimits remain at solver defaults and will be visible in the saved log. There is no automatic retry.

For exact arithmetic, arbitrary finite row weights may be rounded to denominator 2^20, with moment weights clipped to [-1,1]. The candidate lower bound is y*b minus the sum of the per-center maxima of M^T*y+R^T*q. A positive value still requires independent raw-neighborhood evaluation of every new column and every maximum. A numerical zero or solver objective alone is not a certificate.

Source, exact commands, versions and input hashes are in `build_manifest.json`. Later solver outputs must be written as new files without changing the frozen build or the earlier families. No unrestricted target claim or nontrivial automorphism assumption is made.
