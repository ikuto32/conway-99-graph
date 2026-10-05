# Independent general balanced affine-phase necessity review

Reviewer `/root/structural_attack` is separate from producer
`/root/state_literature_audit`. The checker imports no producer routines. Its
exact run report, rather than this prewritten document, records approval. Scope
is the extra balanced-triplet construction family on the fixed six-prism
Hadamard support. No graph automorphism or general containment is assumed.

Each balanced coordinate across a triple of columns is a permutation pi_i of
three fiber labels. Write pi_i(x)=s_i*x+t_i over GF(3); these are exactly the six
permutations. Reindexing the three column positions by the first permutation
normalizes pi_0 to the identity. Literal inverse tables establish the orientation
pi_i∘pi_0^−1 and pi_b∘pi_a^−1, whose relative slope is s_b*s_a and intercept
t_b−s_b*s_a*t_a. This is outside-vertex relabelling, preserving the repeated
support, Gram, column intersections and any correspondingly relabelled D.

Let e_r and o_s count the translations x→x+r and reflections x→−x+s.
Their permutation-matrix sum has entry e_(y−x)+o_(y+x). The map
(x,y)→(y−x,y+x) is a bijection over GF(3), so every combination of r,s appears.
For a local group the matrix equals2J. Thus every e_r has one common value a,
every o_s has one common value b, and a+b=2. Nonnegative integer multiplicities
permit only (a,b)=(2,0),(1,1),(0,2). After the first-map gauge, the two extreme
cases merge into the constant class: all signs are positive and phases have
multiset {0,0,1,1,2,2}. Their sum is zero. Repeated phases are required and no
blanket same-sign nonzero differences may be imposed. In the mixed class, there
are three maps of each sign and the phases in each class are exactly {0,1,2}.
Both sums are zero and all within-class differences are nonzero.

For a nonmatching coordinate pair, the five shared support groups supply a
relative permutation sum2J−I. The same entry transform gives
e_0+o_s=1 and e_1+o_s=e_2+o_s=2. Hence o_s=b for every s,
e_0=1−b and e_1=e_2=2−b. Nonnegative integrality gives b=0 or1.
For b=0 there are zero reflections and translation phases {0,1,1,2,2}.
For b=1 there are three reflections with phases {0,1,2} and two translations
with phases {1,2}. In both cases the reflection-phase sum and translation-phase
sum vanish modulo3; an empty sum is an explicit zero row. This argument applies
equally when some containing groups are constant. It establishes necessity,
not sufficiency of the homogeneous equations.

With m mixed groups the full prescribed equation list has20 gauge rows,
20+m local rows and120 pair-sign rows, including duplicates and zeros. Thus its
size is160+m by120. The first generalized rejection rule uses only a pairwise
phase difference inside a mixed same-sign class as the necessary nonzero
functional. Constant-group repeats are never used as a contradiction.

For a parity assignment p, suppose an independently checked row combination
over GF(3) expresses such a functional f as a combination of homogeneous
equations. Let U contain the group supporting f, every group supporting a used
local equation, and all five incident groups of each used pair-sign equation.
Only rows with nonzero combination coefficients are needed; gauges have no
parity dependency. If another assignment agrees with p on U, the selected
functional remains necessarily nonzero, and every used equation is exactly the
same coefficient row in the same gauged phase variables. Therefore the same
linear identity contradicts a factor in that assignment. The clause consisting
of the negatives of the chosen pattern selectors for U is sound. Retaining
additional groups, including all twenty, remains sound. This is a conditional
proof rule: it does not approve a particular generated clause without checking
its actual certificate, mapping, and union.

Looking only at nonzero phase coefficients is insufficient. A group currently
even contributes zero to an odd-pair row. Changing that omitted group's parity
can make its relative map odd, adding t_b+t_a to the row. The checker saves an
explicit five-group example. The union must conservatively retain all five
groups, even for an old zero row or a group with zero visible coefficients.
It checks all32 disagreement partitions and both sign rows, plus a toy
certificate, retained-group invariance and deliberately truncated dependencies.

The finite checking path constructs complete valid populations from these
multiplicity profiles, independently of the producer's6^n traversal. Local
ordered tuples are permutations of three translations each repeated twice,
three reflections each repeated twice, or all six permutations once:90+90+720
objects. Pair tuples are permutations of {translation0,translation1 twice,
translation2 twice}, or {translation1,translation2,all three reflections}:
30+120 objects. It checks every saved tuple literally and all150 normalized
local types, including30 constant and120 mixed. Gauge and relative composition
are checked through literal permutation inverses. Known constant repeats and
both pair profiles are positive controls; wrong multiplicities, wrong gauge,
incorrect classifications, omitted/duplicate records, linear-only false
positives and bad dependency/certificate claims must be rejected.

These local tables and the conditional row-dependency rule are the result being
reviewed. No research candidate, branch rank, actual shortened clause or factor
is produced by this audit. Any future16-case batch needs separate source/input,
native-object and certificate gates. A surviving nullspace does not establish a
factor, and none of this is an unrestricted Conway99 exclusion.

The audit also appends a separate scheduling record for the previously built
240-option CNF: it remains preserved and unsearched because its specific branch
already has an independent exact GF(3) exclusion. That execution decision does
not promote the CNF encoding or claim a new solver outcome.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_general_f3_necessity.py --out acceleration/results/20260930_independent_review/hadamard_general_f3_phase_necessity
```
