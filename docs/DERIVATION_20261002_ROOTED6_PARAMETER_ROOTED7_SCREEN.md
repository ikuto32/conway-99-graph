# Rooted-six parameter domain and rooted-seven extension screen

These experiments concern necessary induced-subgraph counts per actual ordered
pair. They assume no nontrivial target automorphism. The prism-free statements
retain the additional premise that the hypothetical target contains no induced
triangular prism. Passing a count model does not construct a graph.

## Exact rooted-six parameters

The complete rooted-six nonedge necessary model has 567 variables and 1,445
integer rows. Its triangular-prism-free face adds one zero-count row. The source
`acceleration/theory_20261002_rooted6_exact_parameter_domain.py` freezes those raw
rows, uses exact modular elimination to guide rational reconstruction, and checks
each proposed vector on every integer row. Explicit independent null vectors
give upper rank bounds, while modular ranks give matching lower bounds: the base
rank is 564, with nullity three; the conditional rank is 565, with nullity two.

The two conditional free coordinates are the actual count of rooted-six masks
8024 and 15540, at raw indices 552 and 566. Every coordinate is an integer affine
function of their values `(a,b)`. Exact nonnegativity gives the rectangle
`0 <= a <= 20`, `0 <= b <= 9`. All 210 integer points give distinct nonnegative
integer vectors satisfying all 1,446 raw rows. The old feasible witness remains
preserved. These are 210 solutions of a necessary local count model, not 210
graphs or a target-wide coverage fraction.

The independent audit
`acceleration/results/20261002_independent_review/rooted6_nonedge_domain01/summary.json`,
SHA256 `65081849ccf721eae5bdf569b16f44c88255e0421f5fab1ec26a7fa7f36e8271`,
reconstructed every basis/row/coefficient, checked a different-prime rank,
checked the explicit kernels and every integer point, and proved the rectangle
using coordinate witnesses and all four corners independently of producer
clipping. The root ledger records the exact claims and their status.

## Rerooted universal rooted-five identities

Dependency: `C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY` revision 1, relation
`uses_result`. Its universal rooted-five counts apply to every actual ordered
edge and nonedge without a graph symmetry assumption. The domain dependency is
`C-PRISMFREE-ORDERED-NONEDGE-ROOTED6-INTEGER-DOMAIN` revision 1.

Fix the primary root `(u,v)`, choose an anchor `u` or `v`, and partition an external
vertex `w` by its adjacency bits to `(u,v)`. For a primary nonedge the four
partition cardinalities are `(71,12,12,2)`; for an edge they are
`(72,12,12,1)`. Let `F` be a five-vertex flag rooted at the anchor and `w`, and let
its universal count be `c_F`. Summing this count over the chosen `w` partition
gives `partition_size * c_F`.

Each counted flag has three free vertices. If the other primary root is absent,
the union consists of the primary pair, `w` and those three vertices: a primary
rooted-six flag. If the other primary root is present, it is one of the three
free vertices and the union is a primary rooted-five flag. These cases are
disjoint and exhaustive. On each raw induced representative, enumerate all
possible marked free vertices `w`, retain the correct partition, reroot the
selected five vertices, and increment that flag's coefficient. This yields a
complete linear identity including both union and collision terms.

`acceleration/results/20261002_rooted6_reroot5_screen/reroot5_rows.json`,
SHA256 `b8644f9e15579c1aaff53a1582bf1f273dacdf9f4fec5911829c0457f37c6904`,
contains all 612 nonedge-primary rows. Substitution of the exact two-parameter
affine domain makes every residual identically zero. All 210 frozen profiles
survive; no profile is excluded. The producer calibrated the identities on all
72 rook-nine rooted-five counts and all 36 ordered nonedge rooted-six counts,
and rejected a corrupted count. This specific rerooting adds no restriction to
the recorded conditional necessary space; a separate coefficient audit is needed
before ledger promotion of that null result.

## Fresh rooted-seven catalogue and stronger necessary rows

The new catalogue does not use the archived order-seven enumeration. Every
rooted-seven graph has a free-vertex deletion to a rooted-six graph. Enumerate
all 456 independently checked rooted-six nonedge representatives and all 64
possible neighborhoods of an added vertex. Test exact local common-neighbor
caps, canonicalize only the free labels, then test every six-vertex subset for
an induced triangular prism. The 29,184 labelled augmentation attempts produce
2,770 locally admissible rooted-seven classes, of which 2,750 are prism-free.

Independent catalogue coverage was checked by the different method of testing
all 1,048,576 labelled seven-vertex masks with the root nonedge fixed. Its report
is
`acceleration/results/20261002_independent_review/rooted7_catalogue01/summary.json`,
SHA256 `3355afb38656eadc83eff6e0db3818eded9621f890c9d46f489fdb0324370758`.
Catalogue coverage does not itself validate the following model's rows.

The exact model is
`acceleration/results/20261002_rooted7_extension_model/model.json`, SHA256
`21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595`.
It has 2,766 nonnegative variables, 11,749 rows and 86,129 nonzero coefficients.
The first 2,750 variables count the conditional rooted-seven classes. The
remaining variables are four aggregate `(a_w,b_w)` pairs and their nonnegative
upper-bound slacks.

Ordinary deletion, marked degree and marked common-neighbor rows extend each
rooted-six class by one free vertex. Finite automorphism orbits of an induced
representative normalize marks; they are not target automorphisms. The complete
frozen descriptors record each orbit and exact coefficient. Substituting the
fixed rooted-six affine profile moves its contribution to the right side,
which is an integer affine function of `(a,b)`.

Rerooted rooted-six sums use the same disjoint union/collision argument above,
now giving primary rooted-seven and rooted-six terms. For a new edge root, use
the independently checked conditional universal rooted-six edge counts,
`C-PRISMFREE-ORDERED-EDGE-ROOTED6-RIGIDITY` revision 1. For a new nonedge root, use
the count's affine dependence on its two local parameters. Summing over the
selected `w` partition introduces aggregate variables `A=sum a_w`, `B=sum b_w`
with exact bounds `0 <= A <= 20*partition_size` and
`0 <= B <= 9*partition_size`. Explicit slack rows turn those bounds into equality
rows with nonnegative variables. No equality among different actual roots is
presumed.

The producer controls used the prism-free Petersen graph `srg(10,3,0,1)`, with
its own parameters: all 60 primary ordered nonedges passed exact rooted-seven
extension and rerooted-six rows; all 90 rooted-six pair counts were checked
directly; a corrupted seven-count was rejected. Target-model row derivation
and coefficients still require independent review.

## Exact modular and numerical screens

All 210 profiles were frozen before evaluation. Complete GF2 and GF3 reductions
found ranks 2,718 and 2,742 respectively and no nonzero affine parameter
consistency relations. Every profile survives both necessary integer tests.
The GF3 code uses packed trits for discovery and separately replays any relation
with ordinary modular integer sums. No modular exclusion was produced.

The initial unscaled four-corner HiGHS guides reported three numerical
infeasibilities and one UNKNOWN. No exact Farkas reconstruction passed; these
failed guides and raw rays are preserved in
`acceleration/results/20261002_rooted7_corner_certificates/`. They were never
promoted as mathematical exclusions. One diagnostic initially failed during
JSON serialization at Python's 4,300-digit conversion guard; its original source
and incomplete output remain preserved. The bounded v2 diagnostic recorded the
large exact fractional diagnostics without that serialization failure.

New v2 corner guides scale count variables and every row using explicitly
preserved integer scales, then undo those scales before certification. The
unchanged raw model admits exact nonnegative integer vectors at all four
rectangle corners `(0,0)`, `(20,0)`, `(0,9)`, `(20,9)`. Thus the earlier unscaled
numerical infeasibilities were misleading numerical guides.

For every frozen point `(a,b)`, use the corner weights
`((20-a)(9-b), a(9-b), (20-a)b, ab)/180`. They are nonnegative, sum to one and
give the correct affine parameters. The producer explicitly reconstructed all
210 vectors and checked every row and coordinate over exact fractions. All 210
have nonnegative rational necessary-model extensions; only the four corners of
this particular witness family are integral. This does not exclude an integer
extension at any other point and does not establish graph realizability.

The raw report is
`acceleration/results/20261002_rooted7_corner_certificates02/summary.json`,
SHA256 `fedf66532921bef75ea3435c9ae2e479ae74954ed391ee253a44dc1c2c68bd28`.
Its preserved manifest/receipts give the exact commands, source commit, tool
versions, source/model hashes, numerical settings, allocation and actual outcomes.
The supported invocation completed in 24.734 observed seconds with exit zero,
reaped descendants and observed empty Windows Job. Exact corner vectors and
their convex coverage require separate artifact checking; the model derivation
requires separate review. No target graph or general nonexistence proof emerged.
