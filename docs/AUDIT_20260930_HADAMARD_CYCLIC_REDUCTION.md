# Exact reduction within an explicitly restricted cyclic-fibre construction

The fixed six-prism Hadamard aggregate has 20 distinct supports, each repeated
three times. Restrict their three F columns to the colourings c, c+1 and c+2
modulo three in ascending raw-column order, where c assigns the six support
coordinates two to each fibre. This is an additional construction restriction
on F. It is not without loss of generality for arbitrary factors on this L,
and imposes no automorphism or cyclic action on a residual graph D.

There are 90 balanced words. Subtracting c at the first sorted coordinate
produces a word whose first entry is zero, leaving exactly 30 possibilities.
The three new columns are a cyclic permutation of the old three columns.
Relabelling those outside vertices preserves the aggregate support and any
potential completion after conjugating D. Thus this gauge covers precisely
the chosen cyclic subclass modulo legitimate column relabelling. It cannot
justify the extra cyclic restriction itself. The checker constructs the 30
words by choosing the other zero coordinate and two one coordinates, then
checks all 1,800 group-specific raw phase transports.

Every coordinate occurs in ten of the 20 base supports. Each selected cyclic
triple places it once in each fibre, so all 36 row sums are ten regardless of
the choices. Each column has two entries per fibre. Different copies of the
same coordinate never share a column. A standard matching pair never occurs
in a support. These observations give the required diagonal and zero Gram
entries automatically.

Each of the 60 nonmatching coordinate pairs a<b belongs to exactly five base
supports. In a selected colouring c of one such group, the contribution to
the Gram entry between (g,a) and (h,b) is exactly one if
h-g=c(b)-c(a) modulo three, and zero otherwise: among the three phases there
is exactly one placing a in fibre g. Consequently all the remaining prescribed
Gram entries are equivalent to requiring the five colour differences to have
histogram (1,2,2). There are 180 exact primary-selector equations. Together
with 20 one-choice equations, these characterize the full 36-by-36 prescribed
Gram within this subclass. All 81,000 local Gram coefficients and every saved
equation input list are independently checked. The first fibre's 60 columns
then realize every nonmatching coordinate pair exactly once, as each such
pair has exact within-fibre Gram entry one.

Within one cyclic triple, every two columns are disjoint. For choices c,d in
two different support groups, let n_delta count their common coordinates a
with d(a)-c(a)=delta. The overlap of phase r of c and phase s of d is
n_(r-s). Thus all nine lifted column caps hold exactly when all three counts
are at most two. The checker compares these independently computed three
counts to all nine literal set intersections for all 171,000 group-choice
pairs. This covers 60 within-group and 1,710 cross-group actual column pairs,
and reproduces all 28,674 forbidden choice pairs. It does not sample caps.

The scope, raw supports, group/choice mappings, gauge transports and exact
abstract equation/cap predicates are all bound by the report. The checking
path reuses the frozen independent raw-domain helper from the uniform/order
review; that shared component is disclosed and pinned. It imports no producer,
counter builder or solver code. Generic cyclic truth tables and corrupted
scope, choice, coefficient and cap records calibrate the review.

This is a semantic reduction gate only. It does not approve threshold
auxiliaries or every DIMACS clause; a separate independent encoding gate and
raw-object checking path are required before interpreting any solver result.
No full factor, residual adjacency or target graph is constructed. An UNSAT
result in this explicit subclass would not exclude other colourings on the
same aggregate support, much less other supports or the unrestricted target.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_cyclic_reduction.py --out build/hadamard-cyclic-reduction-review-new
```
