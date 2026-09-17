# Fixed small-denominator support-certificate batch

Reuse the independently verified exact two-coordinate support certificate
469399553/1048576, all89,308 original complete star columns,1,800 reciprocity
rows and3,486 moment rows. The frozen156fixedK/two-coordinate/prescribedabsence
scope is unchanged. This experiment simplifies weights, not coverage.

Before seeing results, fix denominators1,2,4,8,16,32,64,128,256. For eachD,
round each original integer numerator timesD/1048576 to nearest integer,
with exact ties away fromzero. Calculate directly from original weights,
never from the preceding rounded case. Clip moment weights to[-D,D]; do
not clip reciprocity weights. Evaluate allninecases, retaining positive,
zero and negative values. No adaptive denominations, optimizer or solver.

Compute integer scores M^T y+R^T q on every original column. For eachcenter
save its exact maximum and first originalID attaining it. Save the full
weight vectors and integer numerator y*b−sum_center maxima. Dividing byD
gives the usual necessary L1-residual lower bound because|y|<=D and hard
reciprocity vanishes. Only a strictly positive exact numerator is an
exclusion certificate candidate. An unbounded Pythoninteger dot/sum and a
conservative L1-column/weight guard prevent fixed-width overflow in the
sparse products. Floating-point scores are not used.

Predefine 'simplest positive' as smallest testedD with positive numerator;
separately report the strongest exact rational value among positivecases.
Either is only a simpler certificate of the existing conditional result.

Controls: seven exact rounding cases including signedties; reproduce the
independently audited original numerator and all84 maxima; zero weights give
zero; doubled integer weights double numerator and denominator. Production
uses the already audited integer matrix, with no graph-helper import.
Independent review will reconstruct scores from raw neighborhoods, recheck
rounding, alloriginalcolumns and maxima, and attempt corrupt-witness tests.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/simplify_20260917_two_coordinate_certificate.py --out acceleration/results/20260917_two_coordinate_small_certificate
```

Stop after the finite nine-case batch. No ledger edits or target-resolution
claim; overall search coverage remains UNKNOWN without a validated denominator.
