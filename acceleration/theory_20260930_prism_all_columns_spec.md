# Complete six-prism column-domain encoding, version 1

Question: does the identity-cross, standard-internal-matching six-prism core
admit any binary 36x60 factor of its prescribed Gram matrix? This is a fixed
core only. No claim that all target graphs contain it is made.

Unlike the earlier five-matching construction attempts, every possible column
is allowed. Canonical C0 labels the 60 nonmatching pairs of twelve coordinates.
For each such column, its two selected prism components are assigned cell 0
with the fixed bits. Of the four remaining components, choose two for cell 1
and two for cell 2, then choose all four bits freely: exactly 6*16=96 columns.
All 60*96 choices are retained, without orbit pruning or complement pairing.

Necessity: in one prism, the six different factor rows have pairwise Gram
entry zero. Consequently at most one can be present in each column. Their
six row sums are ten, so exactly one is present in every one of the 60
columns. The two-per-fibre margins give precisely the stated column domain.
The canonical C0 relabelling follows from its within-fibre Gram: every
nonmatching coordinate pair occurs once and no matched pair occurs.

Introduce one variable per allowed column choice, and require exactly one
choice in each canonical column. For each pair of rows in different prism
components, except pairs both in C0, require the selected-column count to be
one within a fibre and two between fibres. There are 120 bound-one and 360
bound-two equations, in addition to the 60 exactly-one column equations.
Their incidence lists have 80,640 entries (fourteen per choice).

Sufficiency for the abstract factor: same-prism pair entries are zero by the
domains. The C0 block is fixed. All other off-diagonal Gram entries are
encoded. An unknown row has total overlap ten with the ten rows in its fibre
belonging to other prisms. Each selected column containing that row contains
exactly one such other row, so its row sum is ten. This supplies the diagonal
Gram entries without separate margin equations. Thus the encoding is intended
to be equivalent to the complete abstract fixed-core factor problem.

The mixed inequalities (I+C)F<=2 are automatic in this core: each column has
exactly one entry in each component, so every vertex's closed neighbourhood
meets that column at most once. Outside-column overlap bounds are deliberately
not encoded in this first version. A SAT factor must be independently checked
and screened for these bounds; it still does not provide residual D or a
99-vertex graph. UNSAT requires complete proof replay and encoding/coverage
review, and would exclude this core only.

Build limits: 120 seconds, 8 GiB working set, no solver calls. Reuse the pinned
exact prefix-threshold producer, preserve all clause metadata and raw domains,
and package oversized output losslessly. All arithmetic is integral. No random
seed or floating threshold applies. Build success means a completely emitted
model; verification remains pending until an independent reviewer checks the
whole domain, equations, CNF and calibrated object path.

Locked command from repository root (fresh output only):

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_prism_all_columns.py --out acceleration/results/20260930_prism_all_columns
```
