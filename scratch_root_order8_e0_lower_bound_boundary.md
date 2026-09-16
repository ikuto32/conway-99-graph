# Order-eight boundary for an `E0` lower bound

Status: `ORDER8_E0_POSITIVE_LOWER_BOUND_BOUNDARY_PASS` after running
`scratch_root_order8_e0_lower_bound_boundary.py`.

## What the existing package really supplies

The independently verified Wave147/148 data contain exactly the resources
listed in the user correction:

```text
locally admissible order-eight classes       916
ordinary 7 -> 8 deletion rows                208
marked-vertex rows                           944
marked ordered-pair rows                   4,440
pair-root coefficient matrices             2,414
```

The matrices are the complete order-five flag-product coefficients for an
ordered edge root (`66 x 66`) and ordered nonedge root (`87 x 87`).  Their
products have union order at most eight.  The marked rows impose the exact
degree and common-neighbour extension counts.

## Exact null boundary

There is a later sealed rational pseudowitness using the same base system.
Wave161 independently verifies that it has nonnegative order-seven/eight
coordinates, satisfies all 10,310 nontrivial base equalities, and also
satisfies fifteen retained scalar cuts from the four-root lane.  In its
order-seven deck,

```text
n3                  = 4158
z11                 = 16632
z11/4               = 4158
P                   = 0
count(mask 120568)  = 0
```

Mask `120568` is the independently audited graph
`H_delta = Z2 = Hamiltonian H18`, and each copy contributes one diagonal
flag.  Hence both exact first-moment evaluations give

```text
sum_r E0(r)
  = 6 P + N(H_delta)
  = 0,

sum_r E0(r)
  = 8316 - n3 - z11/4
  = 0.
```

Consequently no positive pointwise bound can be obtained solely as a conic
or linear consequence of this checked relaxation: `E0(r)>=L` for all 99
roots would imply `sum_r E0(r)>=99L`, whereas this feasible relaxation point
has total zero.

This is a boundary of the relaxation, not a counterexample graph.  The same
pseudowitness has exact negative directions in the full four-root covariance
blocks for root masks 3 and 12.  Thus those full blocks, rather than the
already exhausted pair-root order-eight system, remain a legitimate route.

## Why the second moment is not already among the 916 variables

A single `E0` event is a rooted triangular-prism side flag (six vertices) or
a rooted `H_delta` diagonal flag (seven vertices).  Two such flags sharing
only their root can have union orders

```text
side + side          11
side + diagonal      12
diagonal + diagonal  13.
```

Therefore the factorial part of `sum_r E0(r)^2` is not automatically a
linear functional of the 916 order-eight counts.  The order-eight deck does
capture the more-overlapping subcases, and the marked identities can reduce
some extensions, but a complete reduction would itself be a new identity
and must be proved.  The exact zero-total pseudowitness rules out any hidden
positive first-moment consequence of the current pair-root package.

## Exact direct-pair decomposition

The audit reconstructs the rooted fibre square without importing any search
code.  There are 84 square sides and 42 diagonals, hence 126 possible `E0`
events at a fixed root.  Of the `C(126,2)=7,875` unordered distinct pairs,
the BP target-one equations reject exactly the 168 same-fibre side--diagonal
pairs: a chosen diagonal consumes both mate-symbol quotas at each endpoint,
so every incident square side is forbidden.  All remaining 7,707 minimal
forced unions pass the induced `lambda/mu` common-neighbour upper tests.

Their exact union-order census is

| union order | candidate event pairs |
|---:|---:|
| 8 | 84 |
| 9 | 483 |
| 10 | 1,890 |
| 11 | 3,150 |
| 12 | 1,680 |
| 13 | 420 |

The only order-eight case is a pair of adjacent sides in one fibre.  Its
forced induced graph has 14 edges, degree sequence `(3,3,3,3,4,4,4,4)`,
automorphism group order 8, global least mask `14333541`, and Wave147's
degree-cell canonical mask `127242964` (zero-based order-eight index 515).
Direct recognition finds four rooted adjacent-side-pair roles in every copy.
Thus, writing

```text
T   = sum_r E0(r),
M_E = sum_r binom(E0(r),2),
R_q = number of event pairs whose flag union has order q,
```

the exact decomposition is

```text
M_E = 4 x_127242964 + R_9 + R_10 + R_11 + R_12 + R_13,

sum_r E0(r)^2
  = T + 8 x_127242964
      + 2(R_9 + R_10 + R_11 + R_12 + R_13).
```

Here the numbers in the census are sizes of the possible labelled-pair
catalogue at one root; `R_q` are their actual occurrence totals in a graph.
The order-11, order-12, and order-13 maxima are not merely loose set-size
bounds: the script constructs respectively side--side, side--diagonal, and
diagonal--diagonal forced unions that satisfy both partial BP and every
induced pair upper bound.  This is only local admissibility, not an extension
to a 99-vertex SRG.

One notation warning matters.  If the triangle-support note calls

```text
K_support = sum_r binom(84-E0(r),2)
```

its `M2`, then this is not `M_E`; rather

```text
K_support = 99 binom(84,2) - 83 T + M_E
          = 345114 - 83 T + M_E.
```

They contain the same unresolved higher-order information after `T` is
known.  Likewise an aggregate `YY^T` identity does not determine this support
functional, which uses `Z=1_(Y>0)` and hence `ZZ^T`.

## What Wave147/148 sees, and what it does not

Mask `127242964` is present in the 916-class stream.  It contributes to 37
upper-triangular entries in each pair-root family, always with coefficient 8.
No individual entry isolates it: the smallest order-eight support of an entry
containing it is 9 classes for the ordered-edge family and 3 for the ordered-
nonedge family.  It also occurs in two ordinary deletion rows, four marked-
vertex rows, and nine marked-pair rows; none of those rows has it as its sole
order-eight term.  These are direct support checks, not a rational row-span
or SDP-dual impossibility theorem.

Wave148 is a one-exterior-vertex identity from a marked order-seven object to
order eight.  A generic `R_9,...,R_13` term needs at least two simultaneous
exterior vertices, including their mutual adjacency and joint incidences.
Iterating a one-point marginal would require an order-eight-to-nine extension
layer, which is absent.  Wave147 products instead use order-five flags sharing
an ordered two-vertex root and therefore have union order at most eight.
Consequently no existing row or matrix coefficient directly contracts the
five residuals above.  An indirect rational-span or PSD consequence is not
logically ruled out, but it needs a separate explicit certificate; it is not
contained mechanically in the 2,414 matrices or 5,384 marked rows.

## Revised target

Do not regenerate the 916 classes.  Reuse them to identify the order-at-most-
eight portion of `M2`, but seek the missing strength in one of:

1. the full nine four-root covariance blocks (not merely sampled cuts);
2. an overlapping-root consistency identity coupling different roots;
3. explicit order-nine through order-thirteen pair-flag variables, introduced
   sparsely only for the unresolved `M2` configurations; or
4. a graph-level integrality/rank lemma that excludes the rational
   pseudowitness before any larger motif enumeration.

No graph or nonexistence proof is claimed.
