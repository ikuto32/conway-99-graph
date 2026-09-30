# Independent review of the balanced phase matrix form

This review concerns the fixed six-prism Hadamard support and the additional
balanced-triple hypothesis. It establishes a reformulation of necessary linear
conditions, not a factor construction, an exclusion, or a universal rank claim.
The discovery was proposed by `/root` and implemented by
`/root/state_literature_audit`; the reviewer is `/root/structural_attack`.

## Definitions and scalar equivalence

The 60 raw support columns consist of three copies of each of 20 distinct
six-coordinate supports. Let L be their 12 by 20 incidence matrix. In a group,
the normalized affine permutations have the form x -> s_a x + t_a over GF(3),
with s_a in {+1,-1}, first-coordinate sign +1 and phase zero. Put S_ag=s_a on
the support and zero elsewhere, and T_ag=t_a there and zero elsewhere.
Define U=S entrywise multiplied by T. These are not dense independent phase
variables: T has precisely the 120 supported entries.

For an ordered pair (a,b), direct matrix multiplication gives

    (L T^T - U S^T)_ab = sum_g (t_b - s_a s_b t_a),

where the sum is over groups containing both coordinates. Split this sum into
O, the groups with opposite signs, and E, the equal-sign groups. Reversing the
coordinates leaves each odd summand unchanged and negates each even summand.
The two matrix entries are O+E and O-E. The inverse transformation is
O=2[(O+E)+(O-E)] and E=2[(O+E)-(O-E)] in GF(3). Thus requiring both ordered
entries to vanish is exactly equivalent to the two scalar phase-sum rows.
The diagonal and the six matched pairs contribute identically zero rows.
One ordered equation alone is insufficient: O=1,E=2 is a counterexample.

For a mixed group, let A and B be the sums of phases on positive and negative
sign coordinates. The two matrix column sums are A+B and A-B; the same
invertible transformation proves equivalence with A=B=0. For a normalized
constant group all signs are positive, so the two matrix rows are identical
and impose only the single local phase sum. No constant-group pairwise phase
distinctness follows or is being added. The twenty gauge equations t_first=0
must remain explicit: the matrix equations do not replace them.

Consequently the general necessary scalar phase system is equivalent to

    L T^T = (S ∘ T) S^T,
    1^T T = 0,       1^T (S ∘ T) = 0,

together with the twenty gauges. This algebra applies to every normalized
constant/mixed sign configuration on the support; necessity for an actual
balanced factor comes from the separately verified general phase theorem.
It does not assert sufficiency for local multiplicities, phase inequalities,
the full Gram, outside-column caps, or a residual graph.

## Universal all-mixed signed Gram identity

The raw support independently supplies: each coordinate occurs in ten groups,
each matched pair in zero groups, and every other coordinate pair in five.
Let any all-mixed normalized parity projection on this support satisfy the
zero-or-three disagreement condition. Every S column has three +1 and three
-1 entries, so S^T 1=0 over the integers. For a coordinate a, its diagonal
entry in SS^T is 10; its matched partner contributes zero. Each of its ten
other partners contributes 5-2d, which is 5 if d=0 and -1 if d=3. If z_a
counts the zero-disagreement partners, row a therefore sums to
10+5z_a-(10-z_a)=6z_a. It also sums to zero since SS^T 1=0. Exact integer
arithmetic gives z_a=0. Every one of the sixty disagreements is therefore
three, and

    S S^T = 11 I + M - J,

where M is the coordinate matching. This is a quantified derivation, not an
extrapolation from the finite saved branch. Dropping column balance invalidates
it: S=L has all disagreements zero and satisfies the zero-or-three condition,
but has nonzero row sums. Integer arithmetic is essential; reducing the row
sum 6z modulo three would erase the conclusion.

## Degenerate phase solution and the rank boundary

For any allowed constant/mixed normalized parity projection satisfying the
zero-or-three condition, let t_a=(1-s_a)/2 on each support. These are precisely
the parity bits, with zero first phase. On any shared group the relative phase
t_b-s_as_bt_a equals (1-s_as_b)/2, the indicator of opposite signs. Its sum
is d, zero in GF(3) for d in {0,3}. A constant group has all t=0. A mixed
group has three t=0 and three t=1; both column sums vanish in GF(3). Hence
T=(L-S)/2 is a solution of the matrix and gauge equations. It is nonzero if
there is a mixed group, but its same-sign phases coincide, violating the mixed
local bijection requirement. This vector gives no exclusion without further
nullspace information. No rank is computed or certified by this review.

## Independent exact checks and limits

The new checker imports no producer or prior phase-checker code. It reconstructs
the literal support incidence, derives the scalar rows from signs and relative
affine phases, and derives matrix coefficients by evaluating ordinary matrix
multiplication on all 120 phase basis vectors. It checks all 144 saved ordered
rows, all 40 column-sum rows, all 20 gauges, the 144 integer Gram entries, and
the saved degenerate vector. Local controls enumerate all 11 permitted sign
patterns and all 729 phase assignments, with all three phase shifts; pair
controls enumerate all 1,024 sign arrangements on five shared groups and each
phase basis vector. Positive zero and degenerate solutions are separated from
valid coloring claims. Deliberately corrupted coefficients, signs, gauges and
null vectors are rejected. An explicit nongauged null vector shows why the
gauges cannot be omitted. These finite checks calibrate the universal written
argument; they do not enumerate all twenty-group parity projections.

Reproduce in the repository root, using a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_balanced_phase_matrix_form.py --out acceleration/results/20260930_independent_review/balanced_phase_matrix_form
```

Shared trusted components are the pinned raw support/parity evidence, the
previous general necessity statement, and Python's exact integer/JSON runtime.
There is no producer-code import, solver call, floating arithmetic, new phase
search, or claim about automorphisms of a hypothetical target.
