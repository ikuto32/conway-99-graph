# Entailed component-column equations for the fixed joint factor

Build a separate strengthened CNF; the original58,860-variable/203,748-clause
joint factor encoding is immutable. No solver. Exact arithmetic,120second
build cap and8GiB working set; no random seed or numerical thresholds.

Reconstruct the36vertex cubic core directly from the frozen scope matchings
and cross bijections, and enumerate its connected components. For this fixed
core there are three components of size12, each meeting each fibre in4
vertices. Use raw exact Gram K to check K*v=0 for component indicator
contrasts v=1_comp0-1_comp1 and1_comp0-1_comp2.

For any real C with CC^T=K, the exact identity
||C^T v||^2=v^T K v=0 implies C^T v=0. Thus all three component counts in
each column are equal. The factor's three fibre-column sums2 give total6,
so each component contributes exactly2 per column. No PSD conjecture,
target symmetry or general component-rank theorem is used.

Append all180 component-column equations to the complete frozen base body,
using only original entry variables and new exact prefix-threshold auxiliaries.
Constants from C0 and forced zeros are folded; each metadata row records the
component, column, raw row support, known constant and exact bound. Preserve
the suffix bytes and the exact reconstructed full DIMACS file. New variable
IDs begin after58,860. A new model retains all old entry/product/row mappings
and appends explicit component-counter rows. The input gate does not thereby
approve the extension: independent kernel, implication and clause-replay
review is required before a strengthened solver invocation.

Also cheaply inspect the two archived and three newly generated Q1 factors:
if C0+C1 already contributes more than2 entries to a core component in one
column, record that raw overflow as a candidate simple obstruction. Otherwise
record no obstruction from this test, not extendability. This is an exact
five-case diagnostic, not a census of Q1 factors.

Command: `uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_factor_components.py --out acceleration/results/20260930_triangle_factor_components`, with `UV_PROJECT_ENVIRONMENT=build/research-venv`.
