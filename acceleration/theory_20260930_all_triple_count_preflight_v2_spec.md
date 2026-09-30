# Preregistered unrestricted local-triple/count-master Gram preflight

Only a size/design inventory is authorized here: no research CNF, native SAT,
LP, MIP, or heuristic campaign. Allocation 120 cooperative seconds and 512 MiB
observed peak working set. On failure retain the manifest and failure; do not
change the protocol or claim a completed inventory.

Select every one of the 31,110 frozen valid sorted local triples at each of
the twenty literal support groups, giving 622,200 new selectors. The catalogue
includes within-group Gram upper bounds and three within-group Y-column caps.
There is no exception-count selection, fibre quotient, balance assumption,
target automorphism, cross-group cap or residual-D constraint. Sorted triples
only permute the three identical-support columns. All signatures are linked
to the separately verified arbitrary-exception count-master. A triple whose
signature is absent from that group's soundly filtered master domain receives
a negative selector unit; its ID is retained and counted explicitly.

Inventory two exact prospective formulas, separately: original baseline body,
or original at-least-seven body, followed by the same type of lift. The latter
adds a necessary restriction for potential fixed-support target factors with
all Y caps; it is not implied by the baseline or by Gram plus within-group caps
alone. Do not replace seven with eight. The baseline is equivalent, up to
equal-support column sorting, to full prescribed Gram plus within-group caps
on this literal support. The augmented formula additionally requires at least
seven unbalanced groups. Neither formula imposes cross-group caps or D.

IDs: retain the exact chosen base IDs, then all new triple selectors in
group/catalogue order, then n-1 sequential exactly-one auxiliaries for each
group, then 5,400 weighted channels in lexicographic nonmatching coordinate
pair, fibre pair, incident group, threshold order. Use the count-master's
explicit sequential at-most-one scheme: one long positive clause; first
(-x0,s0); internal (-xi,si),(-s_prev,si),(-xi,-s_prev); final
(-x_last,-s_last). For n>=2 this has 3n-3 clauses. Link every triple selector
to its existing exact master signature selector by (-triple,signature), or
the above unit if that signature is absent.

For each of 60 nonmatching coordinate pairs and each of nine fibre pairs,
the five incident groups contribute coefficients c in {0,1,2}. For each group
use two fresh channels q_t iff OR of its triple selectors with c>=t, t=1,2,
encoded by all (-x,q_t) and one (-q_t,all x). Empty channels use -q_t.
Do not deduplicate channels in this declared design. Exact one group choice
gives c=q_1+q_2. For the ten channels of each cell, use every negative
(bound+1)-subset and every positive (10-bound+1)-subset, bound1 on same-fibre
and bound2 otherwise. The 36 diagonal Gram entries are 10 because the linked
coordinate count master enforces all36 row totals; these are checked explicitly
as a semantic premise and are not presumed from a fixed profile. The remaining
90 upper-triangular zero entries follow literal L/one-fibre-per-coordinate
support. Thus 540 positive off-diagonal cells plus36 diagonals cover all666
upper-triangular entries and hence all1,296 ordered entries.

The source must independently recount actual local coefficient multiplicities,
all signature links, and the target decomposition before applying any formula.
Compute exact clauses, literal occurrences and DIMACS ASCII bytes from compact
arrays and closed-form OR/one-hot byte sums, not giant clause lists. Calibrate
those byte sums against literal small clause streams, exhaustive small gate
truth tables, full10-input exact counts, known balanced/count-only positives
and corrupted count/channel cases. These positives are explicitly not a full
research factor. Save local mask hashes, group and cell inventories, source
and input identities, actual working set, and symbolic construction-memory
estimates. Actual SAT memory/performance is unknown.

Repository overlap inspection covers the existing 5,400-selector ordered
single-column full-L CNF, the all-triple descent, affine-GF2 relaxation,
count-master preflight/build, and fixed-count weighted group CNF. This is a
different joint selector/count encoding of a scope already covered more
broadly by the ordered-column model (which also includes cross-group caps),
not a new coverage or novelty claim. Compare exact sizes without claiming
speedup. Reusing 49*S+60400 from fixed-count builds without the count links and
row-marginal proof is explicitly forbidden.

Streaming implementation plan: preserve the base body; emit one-hot clauses,
signature links, then each cell's channel clauses and ten-input exact count.
Keep one local catalogue and its 270 threshold masks, never 20 copied domains
or millions of Python clause lists. A future builder would need fresh source,
allocation, independently checked encoding/object gates and exact input pins.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_all_triple_count_preflight_v2.py --out acceleration/results/20260930_all_triple_count_preflight_v2
```

## Preserved v1 failure and v2 correction

V1 stopped before the clause inventory because it compared the master first-occurrence group order to the lexicographically sorted multiplicity list. Both describe the same20 supports. V2 authenticates master order against raw support_columns first occurrences, and separately checks equality of the unordered support populations. No catalogue, count table, variable ordering, clause rule, scope or resource allocation changes. The original source/spec/manifest/failure remain untouched and are bound directly.
