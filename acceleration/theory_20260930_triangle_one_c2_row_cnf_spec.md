# Exact 25-row target-necessary projection

Freeze before building. The question is whether the fixed Wave149 triangle
core permits a binary 25 by 60 incidence array consisting of canonical C0,
all twelve free C1 rows, and C2 coordinate 0 (incidence row 24, graph vertex
27). No target automorphism or general containment of this core is assumed.
The selected row is a named coordinate, not a representative orbit.

The approved capacity-compatible Q1 has been excluded by twelve complete
single-row domain checks. This experiment leaves Q1 free and retains the
constraints that could exclude its selected C2 row. It does not fix that Q1
or use any propagated zero from the old fixed-Q1 graph experiments.

Use the fixed 36-row Gram and known incidence map of the independently
checked joint-factor encoding. Select rows 0 through 24. C0 is fixed by
canonical column labeling. All 650 remaining, non-zero-folded C1/C2 entries
are free Boolean variables; the zero folds have the original zero-Gram
justification. Require:

- Every selected row has weight 10; constant C0 rows are checked directly.
- Each C1 column has weight 2. There is no complete C2 column margin because
  eleven C2 rows are absent.
- Every selected row pair has its exact prescribed Gram entry.
- Every component-column total over the selected rows is at most 2, using
  the independently verified component-kernel necessity.
- Every pair of distinct B columns has overlap at most 2 over the selected
  25 rows. This includes dynamic forbidden-pair constraints: the unknown
  C1 contributions and the selected C2 contribution are all encoded.

The last constraints follow from the target common-neighbor identity,
since every two target vertices have at most two common neighbors. They
are not asserted for every abstract complete factor satisfying only its
Gram and margins. The exact scope is CNF equivalence to this finite 25-row
problem, together with the one-way implication that every target graph
containing this fixed core can be relabeled to yield a model. No converse
extension to a 36-row factor or a 99-vertex graph is claimed.

Each nonconstant quadratic product has its own bidirectional AND gate.
Each exact sum or upper bound uses the frozen bidirectional prefix-threshold
encoder. Save the entire fixed/free array, selected original row indices,
target Gram, components, variable mapping, product clause intervals, and
counter metadata. Preserve the original base and all completed experiments.

Expected row populations before construction: 13 row margins, 60 complete
C1 column margins, 156 C0 cross-Gram equations, 78 unknown-row Gram equations,
180 component-column caps, and 1,770 unordered column-pair overlap caps.
That is 307 equality rows and 1,950 upper-bound rows. Counter truth-table
and exact AND controls run before any research solver. Checker calibration
may use a synthetic positive with a different Gram, explicitly identified
as not a witness for the research Gram.

Build is deterministic exact arithmetic, limited to 120 seconds and 8 GiB,
with zero solver calls. An independently audited encoding and a separately
calibrated raw-25-row object checker are required before a research pilot.
The prospective pilot has the existing native 300-second, 1,000,000-conflict,
4-GiB address-space and 10-GiB proof-file limits; root controls its launch.
A SAT object is only this 25-row projection. An UNSAT result needs a complete
independently replayed proof and excludes only this fixed-core target family.

Build command, with `UV_PROJECT_ENVIRONMENT=build/research-venv`:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_one_c2_row_cnf.py --out acceleration/results/20260930_triangle_one_c2_row_cnf`
