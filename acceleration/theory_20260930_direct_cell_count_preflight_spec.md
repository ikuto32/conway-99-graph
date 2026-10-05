# Direct fixed-support F cells and count-master: preflight only

Freeze before inventory. Budget120 cooperative seconds,512MiB positive checked
Win32 peak working set. No research CNF is written, no native/LP/MIP call.
On failure preserve artifacts and use a new version for a correction.

Read the literal six-prism Hadamard L and existing count-master baseline/≥7
model and independent gate. Search/compare the existing direct binary-factor
Wave149/shift6 model, variable-core model, ordered fixed-L single-column model
and previous triple-count preflight. This is not a novelty claim. Prior
ordered595464/3336642 encodes all column caps, but no residual D.

Allocate1080 labelled primary cells x[d,a,f] for every actual outside column d,
one of its six support coordinates a, and fibre f=0,1,2. Preserve literal column
labels; impose no equal-support ordering or target automorphism. Deterministic
allocation order is master group first-occurrence order, its three raw column
indices ascending, its six coordinates ascending, fibre ascending. Encode
exactly one of the three fibres at each of360 coordinate/column positions by
one positive3-clause and three negative2-clauses. Encode exactly two entries
per fibre/column in180 length6 rows with all negative3-subsets and positive
5-subsets (26 clauses per row).

Three candidate prefix choices are counted separately: standalone (no master),
unchanged count baseline, unchanged count≥7. Standalone imposes every one of36
row totals10 over30 allowed column cells via full bidirectional exact prefix
threshold states through11, with lower10 and upper11 units. In master variants,
link each existing incidence count-value selector c for (a,g) to exact counts
over its three raw columns, separately for f=0,1,2. For every assignment of
those three bits whose weight differs from the selected count k=0..3, emit
the clause (-c, the three-literal maxterm excluding that assignment). Existing
exactly-one count channels give literal equality. All master coordinate-domain
rows must be checked to imply row totals10; no fixed-profile assumption.

For every60 nonmatching coordinate pairs(a,b), nine ordered fibre pairs(f,h),
and15 common outside columns, create q iff x[d,a,f] AND x[d,b,h] with all three
equivalence clauses, in pair/fibre/group/column order. No duplicates or product
sharing are assumed: count exact keys. On each540-row list of15 q variables,
encode exact cardinality1 if f=h,2 otherwise by every negative(k+1)-subset
and positive(16-k)-subset. The remaining90 upper-triangular Gram entries are
structurally zero from L and one-fibre-per-coordinate;36 diagonals are row totals.

Within-group caps are included in each main variant. For each of60 pairs of
columns in the same support group and each of their six shared coordinates,
use a fresh e meaning their chosen fibre is equal. Under the already encoded
one-hot triples x,y, this equivalence has six clauses: for each f,
(-x_f,-y_f,e) and (-x_f,y_f,-e). This avoids separate three fibrewise ANDs.
Require at most2 of the six equality flags, using all negative3-subsets.
No cap product is shared with a Gram product: Gram uses one column and two
coordinates; cap equality uses two columns and one coordinate.

Also inventory a separate optional all-cross-group-cap suffix. Iterate every
remaining1710 raw column pair; if their supports intersect in s<=2 coordinates,
the cap is automatic. Otherwise create s exact equality flags with the same
six-clause gadget and all negative3-subsets. Use the actual support intersection
histogram; never the refuted0-or3 assumption. Record all1770 pair accounts.

Baseline master and standalone versions both describe the literal fixed-support
full integer Gram plus within-group caps, with no group balance restriction.
Master tables follow necessarily from those constraints and therefore do not
change their raw-F solution set. Conversely their count selectors/channels
extend each such F because the local sorted triple belongs to the complete
catalogue and the complete marginal domains contain its counts. The ≥7 master
is an additional necessary target-family restriction justified with all Y caps;
it is not claimed entailed by the within-only formula. Optional all-caps version
has the same factor scope as the old ordered model up to equal-support column
permutation. No variant encodes residual D or a full99 graph.

Controls precede inventory: all eight AND assignments; exact count gadgets for
length6 and15; every valid one-hot fibre-pair/equality-flag assignment plus
deliberately wrong flags; all10 count triples and27 three-column colour tuples;
tiny full prefix counters and corrupted states; ASCII counter versus literal
small streams including digit-boundary IDs. Count-only positive fixtures are
the all-balanced and independently checked eight-count profiles; their local
triple representatives are explicitly not full-Gram positives. Save complete
raw cell/product/channel/cap-row recipes and exact per-section variables,
clauses, literal counts, DIMACS bytes, measured memory and input/source hashes.
No full formula file or large retained clause list is permitted.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_direct_cell_count_preflight.py --out acceleration/results/20260930_direct_cell_count_preflight
```
