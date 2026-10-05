# Full binary factor with target column-overlap caps

Freeze before construction or solve. Select the existing component-constrained
36 by 60 factor problem for the fixed Wave149 triangle core. C0 has canonical
column labels; all C1 and C2 entries remain free subject to the audited zero
folds. Keep the exact existing core, Gram, row and fibre-column margins, and
component-column totals. Neither earlier fixed factors nor their exclusions
are premises. No target automorphism or unrestricted containment is assumed.

The new question adds every distinct B-column overlap bound
`sum_r C[r,d]*C[r,e] <= 2`. An actual target satisfies this because two
vertices have at most two common neighbors. These inequalities are new
necessary target-extension conditions, not asserted consequences of the
abstract factor Gram and margins. SAT would provide a complete factor
satisfying these conditions, without a residual D or a full target graph.
UNSAT would exclude targets containing this fixed core only, after a full
encoding and proof audit.

Use a compact equivalent encoding of the new caps under retained premises.
In each fibre, each column has exactly two ones, paired rows have Gram zero,
and each nonpaired row pair has Gram one. Hence its sixty columns are the
sixty distinct nonmatching two-subsets of twelve coordinates. Distinct
columns therefore overlap at most once within any one fibre.

For distinct columns d,e, write k,q1,q2 for their overlaps in C0,C1,C2.
Each is zero or one. If k=0, q1+q2<=2 holds already. If k=1, the total cap
is equivalent to not having q1=q2=1. For every C1 row r and C2 row s, this
is exactly the clause

`not C[r,d] or not C[r,e] or not C[s,d] or not C[s,e]`.

There are 540 intersecting C0-column pairs and144 C1/C2 row pairs, giving
77,760 candidate clauses. The actual fixed-zero map removes34,020 tautologies;
43,740 clauses remain. Preserve every candidate's endpoints, row indices,
variable references, emitted position or exact zero-coordinate omissions.
Do not silently deduplicate. Disjoint C0-column pairs are omitted for the
proved reason above, not a sampled test.

The resulting file consists of the original 212,580-clause component-base
body byte for byte followed by this new suffix. No new variables are
introduced: expected61,296variables and256,320clauses. Save the original
base hashes, new exact raw scope/model, full template recipe, suffix, CNF,
source hash and deterministic gzip reconstruction packages. Original files
and all previous partial proof traces remain untouched.

Calibrate the compact relation on exhaustive small distinct-pair examples
before building. Include a deliberate duplicate-column example showing why
the retained uniqueness premise matters. Producer controls do not establish
independent mathematical verification. The independent gate must check
complete template coverage, zero folds, new scope necessity and all bytes.
A new raw36 object checker must additionally verify all1,770 column caps.

Deterministic build limit120seconds/8GiB; zero solver calls. The later
single native pilot is separately gated, with300seconds, configured1million
conflicts,4GiB address space and10GiB proof file limits. Root launches it only
after the fresh encoding/object gates and preflight. No performance claim
is made from clause counts or unmatched runs. The deferred26-row experiment
is not being run in parallel.

Command with `UV_PROJECT_ENVIRONMENT=build/research-venv`:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_factor_column_caps.py --out acceleration/results/20260930_triangle_factor_column_caps`
