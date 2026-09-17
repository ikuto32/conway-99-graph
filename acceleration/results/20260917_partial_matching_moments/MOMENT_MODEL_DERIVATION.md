# Full center-star co-neighbor moment pilot

Status at preparation: CANDIDATE formulation and computation, pending independent review. The family fixes the same 162 outer K edges and prescribed absences as the frozen partial-matching experiment. Only its 60 freed-coordinate edges and 1,680 disjoint-support edges can vary. This is not the unrestricted Conway-99 problem.

For each of the 84 outer centers t, choose a domain S from its frozen complete local-star table. Its full outer neighborhood is H(t,S) = N_B,outer(t) union S, of size 12. The variable z(t,S) is nonnegative and has unit sum for each center. The 1,740 unknown-edge reciprocal marginals must agree. The primary projection x(v,w) uses the smaller endpoint's marginal for unknown pairs and is zero for all other pairs. Fixed outer edges are represented separately by B(v,w).

For any actual completion, the common neighbors of distinct outer vertices v,w consist of their shared root-neighborhood support vertices plus outer centers t whose selected neighborhood contains both v,w. The distinguished root itself is not adjacent to either outer vertex. Thus the target equation gives the necessary equality

    sum_(t,S) 1[{v,w} subset H(t,S)] z(t,S) + x(v,w)
      = 2 - |support(v) intersect support(w)| - B(v,w).

Every actual completion chooses one star at each center and therefore satisfies all these equations. Fractional star mixtures need not decode to a graph. Each full outer neighborhood contributes 66 pair incidences; all 3,486 unordered outer pairs are retained, including prescribed zero pairs and fixed edges. This includes the co-neighbor terms omitted by the earlier partial-B linear caps.

The pilot makes all 84 simplex equations and all 1,740 reciprocity equations hard. It adds positive and negative residual slacks only to the 3,486 moment equations, minimizing their sum. Its objective is `PARTIAL_K_FULL_CENTER_STAR_MOMENT_PHASE1_V1`, a distinct model from the earlier phase-I cap objective. Numerical zero would not certify a graph or exact feasibility.

Let Rz=0 be reciprocity, Mz=b the moments, and z range over the hard nonnegative star simplices. For any rational vector y with |y_i| <= 1 and any rational reciprocity multiplier q,

    ||Mz-b||_1 >= y*b - (M^T y + R^T q)*z
                >= y*b - sum_t max_(S in domain(t)) (M^T y + R^T q)_(t,S).

Consequently a strictly positive exact value of this support-function expression excludes every completion in the declared family, provided domain completeness, model necessity and arithmetic are independently checked. This certificate does not depend on a solver optimality declaration. The producer rounds a valid solver dual to denominator 2^20, clips moment multipliers to [-1,1], checks integer-product overflow bounds, and saves all exact numerators and all per-center maxima. An unavailable solver dual is explicitly recorded and yields no attempted certificate.

Calibration uses the actual 9-vertex rook graph with its own parameters (9,4,1,2), all nine roots, and either zero or one fixed outer edge. Eighteen exact witness evaluations pass; changing one nonzero moment coefficient or one RHS independently rejects each witness. These are producer controls, not independent approval.

The preregistration is `manifest.json`; exact row/column identities and all bounds and costs are in `model.json`; the complete augmented sparse integer matrix is `integer_augmented_csr.npz`. The raw solution arrays, including invalid arrays if the solver reports invalidity, are preserved in `numeric_lp.json`. Interpret only arrays whose validity flag is true. `summary.json` and `exact_support_bound.json` record the eventual outcome. The solver cap is 60 seconds, one HiGHS IPM thread with crossover disabled. No primary artifact is modified.

Replay from repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --cache-dir .uv-cache-20260917 python acceleration/theory_20260917_partial_matching_moments.py --out acceleration/results/FRESH_OUTPUT_DIRECTORY
```

The output directory must be empty. Source commit, exact invocation, versions and input hashes are recorded before the computation; saved output hashes bind the completed run. The published availability of these newly created artifacts is a separate question from their local existence.
