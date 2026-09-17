# Exact saved-point odd-set diagnostic and capped strengthened LP

Status: **CANDIDATE diagnostic; independent domain/model review pending**.
This does not establish an exact feasible point, a whole-coordinate exclusion,
or target-level nonexistence. The primary partial-K run remains unchanged.

The frozen universe is every odd subset of the twelve freed matching-coordinate
vertices: 2,048 subsets of sizes 1, 3, 5, 7, 9, and 11. There are 1,024
complementary pairs. These are related tests, not 3,072 independent cases.
Both members were evaluated explicitly.

For a perfect matching with edge marginals `y`, every odd vertex set `S`
necessarily satisfies

```text
sum(y_ab for a,b in S) <= (|S|-1)/2.
```

The diagnostic interprets every saved primary probability as an exact binary
rational using `Fraction.from_float`, then divides each center's probabilities
by their exact sum. The resulting normalized rationals need not themselves have
power-of-two denominators. Negative values would have caused an abort rather
than clipping; none occurred. Matching-edge marginals use the smaller endpoint,
as the primary projection convention requires.

Exactly **one** of the 2,048 subset inequalities is strictly violated by this
rationally normalized saved point: the eleven-element subset with bit mask
2047 in the recorded affected-vertex order. Its excess is approximately
**3.921432605295674e-15**; the exact fraction is preserved in
`oddset_diagnostic.json` and `summary.json`. No subset of size 3, 5, 7, or 9
violates its inequality. This is a tiny defect in a saved numerical point,
not evidence of a substantial fractional odd-cycle obstruction.

Although each center's own local matching marginal has exact degree one, the
projected edge values have small nonzero reciprocity and degree defects.
Consequently complementary odd-set excesses need not be identical. For every
one of the 1,024 complementary pairs, the diagnostic checks exactly that

```text
excess(S) - excess(V\S)
 = (sum_{u in S}(degree(u)-1) - sum_{u outside S}(degree(u)-1))/2.
```

Thus complement equivalence is not silently assumed for this numerical point.
The one violated complement pair contains this eleven-set and its singleton
complement. The exact-perfect-matching control passes all 2,048 inequalities;
a degree-one half-weight pair of triangles correctly violates its odd-set
bound by one half. Four saved control records cover these checks and population
accounting.

## Separately labeled strengthening and its failure to finish

The manifest preregistered a strict-positive-excess trigger without numerical
tolerance. Even this tiny violation therefore triggered a separate LP with
**all 2,048 odd-set inequalities hard**, on the same 54,478 partial-K local
choices. No constraint was added to the frozen primary run. The new identifier
is `PARTIAL_K_STAR_RECIPROCITY_CAP_WITH_ALL_ODDSETS_V2`.

The strengthened LP has 7,358 rows, 61,444 columns, and 9,136,138 nonzeros. It
retains the original reciprocity/cap slack objective but restricts a different
feasible domain with hard odd-set rows. HiGHS 1.15.1, single-thread IPM without
crossover, reached the prescribed 60-second solver limit after approximately
60.047 seconds. The whole diagnostic/strengthening run took 62.625 seconds.

**There was no valid saved primal or dual solution.** Both corresponding
arrays are null. The raw HiGHS information field `objective_value: 0.0` is not
a valid incumbent or an exact zero; it must not be reported as feasibility or
compared with the primary optimum. The outcome is a time limit with no usable
point, preserved in `strengthened_numeric_lp.json`. No exact proof certificate
was attempted or obtained.

## Evidence and remaining obligations

`manifest.json` freezes the selection, arithmetic, complement policy, trigger,
model label, all input hashes, and commands. `oddset_diagnostic.json` preserves
all exact normalized marginals, normalization sums, projected degree defects,
2,048 individual inequalities, and 1,024 complement identities.
`strengthened_model.json` preserves all odd-subset masks, row bounds, unknown
edge order, and the referenced primary cap model. `summary.json` hashes all
outputs, including the capped numerical solve.

Source: `acceleration/theory_20260917_partial_matching_oddsets.py`.
Replay with a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_partial_matching_oddsets.py --out build/partial-matching-oddsets-new
```

The generic partial-domain completeness proof, all fixed-presence/absence
assumptions, the primary generalized cap matrix, and this strengthened model
still need independent review before a family-exclusion certificate could have
its intended scope. Saved-point arithmetic is not that review. No domain or
objective is relabeled as the historical complete-K star model. Overall search
coverage: UNKNOWN; no validated denominator.
