# Independent oriented-triple projection and encoding review

The scope is the fixed six-prism Hadamard support, the additional balanced
identical-support triples, and the additional condition that every group is
mixed. No automorphism of a hypothetical target is assumed. This is a screen
for local mixed conditions and even relative-phase equations. Odd equations,
outside-column caps and residual D are absent.

In a mixed group the six affine maps x -> s*x+t are all six elements of S3.
The positive and negative signs each have three distinct phases. Their phase
differences define a directed three-cycle: u -> v means t_v-t_u=1 mod3.
Conversely an oriented three-cycle determines its phases up to an additive
constant. The triple containing the least support coordinate is positive;
its phase at that coordinate is gauged to zero. The negative triple retains
one independent additive offset. There are ten unordered sign partitions and
two cycle orientations for each triple: 40 choices. Equivalently, the 120
gauged local mixed phase assignments fall into 40 classes of three negative
offsets. The independent checker enumerates these phase assignments directly,
then forms their arc classes; it does not import the producer enumerator.

Every nonmatched coordinate pair belongs to five groups. For an all-mixed
balanced factor, the separately checked integer signed-Gram argument forces
three odd and two even relative permutations. The two even relative phases
are nonzero, since each comes from distinct phases in a local sign triple.
Their sum is zero if and only if they are 1 and 2. That is precisely one copy
of each directed arc between the coordinates. Thus a full factor in this
conditional class yields a choice in each group covering all 120 arcs once.

Conversely a 120-arc cover places each unordered coordinate pair in the same
sign triple twice and opposite sign triples three times. Give each chosen
cycle phases 0,1,2 in its cyclic order. The local mixed condition and all even
relative-phase sums hold; one negative-triple offset per group remains free.
The cover does not settle any odd equation. This establishes exact equivalence
to the stated screen, not to a complete factor. The producer decoder's saved
phases are representatives with both triples' least coordinates at phase zero.

For each of the twenty groups, one of its forty choices must hold. For each
of the 120 directed arcs, exactly one of the forty choices containing it must
hold. Each of the resulting 140 rows is encoded by its positive disjunction
and all negative pairs. These clauses are logically equivalent to exactly
one true variable in that row: the positive clause forbids zero, and a pair
clause forbids each possible pair of true variables. All 800 variables are
primary choice selectors; there are no auxiliary variables. The full formula
contains 140*(1+binomial(40,2))=109340 clauses. The independent checker rebuilds
every row, clause and byte from the raw support and the phase-derived choices.

The object checker requires a complete 800-variable signed JSON assignment,
an independently parsed native SAT stdout with exactly the same assignment,
and satisfaction of every actual raw clause. It decodes choices independently
and literally counts each directed arc. Optional producer metadata must match
the independent result, including every phase representative and scope flag.

Calibration separates positive scopes: all local mixed phase assignments,
the generic tetrahedron's oriented-face cover, and an 800-variable /109340
clause synthetic codec formula. None is claimed to be a positive instance of
the research formula. Exhaustive small exact-one truth tables and corrupt
domains, rows, clauses, native models, arc covers and local phases are checked.
The checker performs no optimization or SAT solving. Actual SAT/UNSAT outcomes
require their own independent artifact checks; an UNSAT proof would exclude
only this all-mixed balanced fixed-support class.

The independent implementation uses only standard-library exact arithmetic,
the frozen raw input data, and separately reviewed mathematical statements.
No producer or prior object-checker code is imported. Reproduction from the
repository root uses the locked research environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_oriented_triples.py audit --out NEW_ENCODING_DIRECTORY
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_oriented_triples.py calibrate --encoding-gate ENCODING_SUMMARY --encoding-gate-sha256 SHA256 --out NEW_CALIBRATION_DIRECTORY
```

Actual object mode is `sat --encoding-gate PATH --encoding-gate-sha256 HASH
--assignment JSON --native-output LOG [--decoded JSON] --out NEW_DIRECTORY`.
