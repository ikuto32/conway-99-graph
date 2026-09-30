# Eleven row domains with the accepted C2 coordinate held fixed

Freeze before this run. Input is the independently accepted 25-row native
SAT artifact, SHA256 e81ee7f51591ee2de265ddf9d64892fa7bad9fe176502a450cc6db29c304263c,
with gate e4693a9bb52831e26ecdeb350565123df4cac58917a66db4762ea31e161809b1.
The gate must bind exactly this decoded artifact before testing it.

Assemble a fresh partial 99-vertex adjacency using the original fixed core,
C0, C1 and C2 coordinate0 (graph row27). All other C2-to-B entries and all
B-B offdiagonal entries remain unknown. No old forced-zero propagation,
fixed-Q1 exclusion, or unapproved construction is a premise. Recheck
known-one common-neighbor caps as a cheap consistency check.

Test vertices28 through38 in ascending order, with60 binary variables each.
Require its remaining degree10, exact common-neighbor counts against all
25 fully known incidence rows (graph vertices3..27), and every necessary
forbidden B-pair whose existing known common-neighbor cap is already full.
The new equation against fixed row27 is essential; the old24row constraint
builder is not reused unchanged. No sum is replaced by a floating score.

Reuse the frozen bounded integer recursion only. Before these tests,
calibrate it against all ordered pairs of interval-sum constraints on
three bits, comparing with complete truth-table enumeration. Also check
the new common-equation construction against literal symbolic completion
on a small six-unknown-entry synthetic matrix and a deliberate changed
bound. These are producer controls, not independent result approval.

Attempt all eleven domains with2seconds/20,000nodes per row and120seconds/
8GiB total. Save all raw constraints, complete UNSAT trees or SAT witnesses,
and any UNKNOWN partial tree. Every meaningful outcome requires separate
raw99 reconstruction and full certificate/witness checking. An empty row
excludes only this fixed Q1 plus the fixed selected C2 row, not every Q1
or every possible selected C2 row. Eleven individually feasible rows would
not establish a simultaneous completion.

Command, with `UV_PROJECT_ENVIRONMENT=build/research-venv`:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_one_c2_extension_rows.py --out acceleration/results/20260930_one_c2_extension_rows`
