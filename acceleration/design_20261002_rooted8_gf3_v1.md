# Rooted8 literal GF(3) diagnostic, proposed version 1

The preceding normalized GF(2) invocation completed on source commit
`96049d9929b87de97858a8fded03c47d672cf0b6`: 85.144070145 seconds outer and
75.211297253 seconds inside the native guard. It produced three 23,019-bit
vectors. A separate scalar checker checked all 85,874 rows for each of the
three components (257,622 row-component checks), reporting PASS at
`independent_review/normalized_gf2_full_artifact01/summary.json`, SHA-256
`5e4eaad1a1d8945e33435d2fb09bb113f648f3adc1c7f568fc000f28a132bc14`.
Thus this particular normalized parity test excludes no parameter parity.
It does not establish integer, nonnegative or graph feasibility.

Measured resource evidence is limited: the final GF(2) checkpoint is
343,414,964 bytes, its sparse input 5,079,920 bytes and its normalized literal
stream 12,191,989 bytes. There are 22 saved completed-prefix records. Peak RSS
and CPU/I/O separation were not measured; file size is not memory usage.
The native command used a 4 GiB address-space limit and completed successfully.
No performance guarantee or calibrated GF(3) completion probability follows.
The historical rooted7 GF(3) screen is a CANDIDATE report with zero recorded
affine relations and 210 survivors; it is not used as a verified exclusion.

## Exact question and scope

Apply GF(3) to the same 23,019-column, 85,874-row original literal integer
operator, SHA-256 `a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b`.
Emit either three complete ternary vectors satisfying the three affine RHS
components, or one complete original-row coefficient relation with zero left
side and a nonzero three-component affine RHS. No rank is claimed. This is a
modular test of the literal rows; necessary target interpretation remains
conditional on the UNKNOWN prism-free premise and its separate encoding gate.

Use original rows, including signed and duplicated literal terms. Aggregate
each column modulo 3 only in the derivative input. The independently checked
integer row contents are 1, 2 or 4, all invertible modulo 3, so normalizing these
rows gives the same GF(3) solution set. The new producer must independently
recompute and match every raw/normalized row hash and divisor in the existing
normalization manifest; it must not merely infer this from a narrative.

## Producer algorithm and formats

New files will be `rooted8_gf3_20261002_v1.cpp`,
`prepare_20261002_rooted8_gf3_v1.py` and its versioned specification.
Shared implementation ancestry with the GF(2) producer is disclosed. The
independent checker must import neither producer nor its scorer/eliminator.

Represent each coefficient by two disjoint uint64 bit planes (one and two).
For packed addition, derive zero planes from the union of the nonzero planes,
then use the nine-element scalar truth table:
`z1=(x0&y1)|(x1&y0)|(x2&y2)` and
`z2=(x0&y2)|(x2&y0)|(x1&y1)`.
Multiplication by two swaps planes. Mask unused final-word bits. Eliminate at
the least nonzero column, scale a new basis pivot to one, and update all three
RHS components in GF(3). Descending scalar back-substitution sets free values
to zero. Basis rows carry their original row and scaling factor, plus weighted
references to earlier inserted basis rows. Expand this acyclic DAG backwards
to emit a sorted complete original-row relation if an inconsistency appears.

The sparse text format is `GF3_AFFINE_SPARSE_V1 n m`, followed by rows
`rhs_const rhs_a rhs_b term_count col0 coefficient0 ...`. RHS residues are
0..2; coefficients are 1 or 2; columns are unique, ordered and in range.
Vectors are `GF3_AFFINE_PRIMAL_V1 n label` followed by exactly n digits 0..2.
Relations use `ORIGINAL_LITERAL_GF3_ROW_RELATION_CANDIDATE_V1`, dimensions,
`rhs_affine_residue:[const,a,b]` and sorted `original_row_coefficients:[[row,c]]`
with c=1 or 2. These coefficients refer to ORIGINAL literal rows.

Checkpoint format/version will be new and will contain exact input SHA-256,
dimensions, completed row count, both basis planes, all three RHS components,
pivot/insertion ordering and complete weighted DAG. Strict restoration checks
cover coefficients, leading-one/prefix/padding/plane invariants, references and
exact end. A checkpoint saves only completed rows; an interrupted current row
is not represented as completed. No automatic retry or deadline extension.

## Engineering controls and independent gate

Before scientific use, exhaustively check all nine scalar coefficient pairs
and all 27 three-RHS combinations, including packed boundaries 0/63/64/65/127,
trailing padding and plane disjointness. Use separately replayable raw fixtures:

- A small full-rank feasible matrix, signed coefficients, divisor 2/4 rows,
  duplicated terms that cancel mod3, three RHS components and zero rows.
- A singular feasible matrix with free variables, dependent rows and all three
  RHS components; whole versus completed-prefix split/resume comparison.
- An inconsistent dependent row requiring weighted coefficients 1/2; raw
  scalar summation must check every column and all three affine RHS residues.
- A multiword sparse matrix exercising leading pivots on both sides of bit63.

Save actual command vectors, receipts, exact raw fixtures, derivative hashes,
vectors/relations/checkpoints and measured native wall/RSS (getrusage). Strict
corrupted controls cover coefficient/sign/RHS/vector/relation row/weight,
checkpoint input hash/prefix/plane/padding/DAG and malformed sparse input.
Require exact expected rejection stages; unrelated exceptions cannot satisfy
a negative control. Independently enumerate tiny ternary assignments and check
raw scalar vectors/relations; another execution of producer code is not an
independent checking path.

## Allocation and scientific launch conditions

Engineering build: 180 outer / 150 producer / 120 compiler seconds, selected
from the prior 1.105-second compiler run while allowing changed code diagnostics.
Engineering controls: 300 outer / 270 producer / 15 native seconds per tiny
case, with all children sharing the producer deadline. Independent control
gate has its own declared supported invocation.

Proposed scientific allocation is 900 outer / 850 producer / 750 native
(745 cooperative) seconds, with 4 GiB AS and per-file limits. This is a proposal,
not an inherited default: the measured GF(2) native time was 75.211 seconds;
GF(3) has more Boolean work, two planes and larger weighted-DAG checkpoints.
Its expected overhead is not calibrated. Instrument real RSS and checkpoint
bytes; reassess on significant evidence. Reserve 8 GiB available host memory,
32 GiB host disk and 8 GiB ext4 disk. Preserve an incomplete prefix on stop.
Change this proposal explicitly if new engineering evidence warrants it.

No scientific launch until the exact changed source/binary/build/control gate
and independent scientific endpoint checker are reviewed, committed and pinned
by a fresh launch plan, with exact recoverable raw input closure and fresh fully
observable empty native-worker/resource checks. If three vectors appear,
independently check all 257,622 original raw row-component sums modulo 3.
If a relation appears, independently check every column and affine RHS from the
complete original rows. A nonzero relation restricts only its declared literal
scope; one relation does not establish exhaustive parameter screening. Retain
all GF(2) and failed/preflight artifacts unchanged.
