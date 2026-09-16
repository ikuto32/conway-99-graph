# An exact averaged degree-row control at E0=0

There is a rational nonnegative degree-row distribution satisfying the
symmetrized first and second fibre moments at E0=0, with every individual
row integral and all fourteen root-label quotas exact. It shows that these
averaged constraints alone cannot establish a positive E0 lower bound.
The control does not realize a simultaneous integral compression matrix or
an adjacency matrix.

## Moment normalization

Let `B` denote the unknown 84-vertex second-layer adjacency matrix and `U`
the 84-by-21 support-fibre incidence matrix. Write

```text
D=BU, C=U^T B U=U^T D.
```

With `L` the 21-by-7 unsigned support incidence matrix, the SRG block
identity gives

```text
D^T D = 48I+32J-C-8LL^T.                            (1)
```

Rows of D are integral vectors in `{0,1,2,3,4}^21` of sum12. Column sums
are48. Its diagonal second moment is `64-C[F,F]`, and
`tr(C)=2E0`. At E0=0 all own-fibre degrees vanish.

After averaging the root-pair symmetry, the compression is

```text
Cbar[S,F]=0 if S=F,
Cbar[S,F]=8/5 if S,F overlap in one group,
Cbar[S,F]=16/5 if S,F are disjoint.                  (2)
```

This note constructs a weighted row population meeting (1) with C replaced
by (2). All equalities in that averaged population are exact rational
equalities.

## One integral row and its root-label realization

Fix source support `{0,1}`. The following ten nonzero fibre degrees define
the row:

```text
degree1: 02,03,14,15,26,36,46,56,
degree2: 23,45.
```

All other degrees, including degree01, are zero. The row sum is12, its
square sum is16, and the seven root-group incidence totals are
`(2,2,4,4,4,4,4)`.

Here is an explicit set of twelve distinct second-layer neighbour labels:

```text
(0,4), (1,6), (2,8), (3,10),
(4,6), (5,7), (8,10), (9,11),
(5,12), (7,12), (9,13), (11,13).
```

Labels0 through3 each occur once; labels4 through13 each occur twice.
These are exactly the required common-neighbour quotas against the fourteen
first-layer vertices. No selected neighbour belongs to the source fibre.
The same degree row works for each of the four exact source corners by
flipping the corresponding within-pair labels.

As a stronger local check, expose all99 vertices with the fixed root and
first-neighbour incidences, and assign only this one vertex's twelve
second-layer edges. Every known-edge common-neighbour lower bound is at
most1 and every other pair's lower bound at most2. All4,851 pair caps pass.
The unassigned second-layer edges remain unknown; this partial check is
not a graph completion.

## Exact symmetrization and weights

Apply all5,040 permutations of the seven root-neighbour pairs to the base
row. There are630 distinct `(source,degree-row)` outcomes, each occurring
eight times, and30 degree rows for each source. Equivalently, for a fixed
source choose one of five external hub groups and one of six two-element
subsets of the other four external groups to connect to the first source
group. This independently constructs the same630 outcomes.

Each exact source vertex assigns weight1/30 to each of its30 degree rows.
There are four vertices per source fibre, so the aggregate weight of each
source/degree outcome is2/15. The total weighted row mass is84. Every row
has a concrete root-label realization; no fractional degree coordinate is
used within a row.

For a fixed source the row has total degree4 into the ten overlapping
fibres and8 into the ten disjoint fibres. Averaging therefore gives the
first moment `Cbar/4` per row, or exactly (2) for its four-vertex population.
The weighted column sums are48.

## All second moments follow from the square sum

For any row with the displayed group totals, let `q=sum_F d_F^2`. Counting
the squares of its seven group degrees gives

```text
88 = 2q + 2 sum_(unordered overlapping F,G) d_F d_G.
```

For this row q=16, hence the overlapping-pair sum is28. The total
unordered pair sum is `(12^2-16)/2=64`, leaving36 on disjoint pairs.
There are21 diagonal positions and105 unordered pairs of each off-diagonal
type. Symmetry across the84 weighted rows now gives

```text
Gbar[F,F]=64,
Gbar[F,G]=112/5 on overlapping pairs,
Gbar[F,G]=144/5 on disjoint pairs.
```

These are exactly `48I+32J-Cbar-8LL^T`, so every one of the231 independent
entries in (1) is satisfied.

Let the support-space orthogonal projectors of ranks1,6,14 be `E1,E6,E14`.
The exact decomposition is

```text
Cbar = 48E1-8E6,
Gbar = 576E1+16E6+48E14.
```

For the fixed-mean residual row `r=4d-Cbar[source,*]`, each row has
`||r||^2=128` and lies in the unsigned support cycle space. Its aggregate
second moment is

```text
sum_weight r^T r = 16Gbar-4Cbar^2 = 768E14 = 4K4bar,
K4bar=192E14.
```

Thus the averaged residual Gram relation is also satisfied exactly.

## Limitation

This is a rational weighted population of integer rows. It does not select
one row for each of84 vertices with simultaneous edge reciprocity, actual
column sums48, or pointwise equation (1). In particular Cbar has fractional
entries, so it is not an integral block-total matrix. The covariance cost
of an actual integral compression and compatibility of the shared edge
variables are omitted. A lower-bound argument using those omitted
constraints remains possible; the present control only identifies the
limitation of the listed symmetrized row moments and quotas.

## Reproduction

```text
python scratch_theory_uniform_e0_zero_degree_moment_control.py
python scratch_theory_uniform_e0_zero_degree_moment_control_audit.py
```

The independent audit imports no producer code. It reconstructs the hub/pair
templates, checks all5,040 group actions and exact weights, verifies2,520
label realizations including all four source corners, and checks all231
entries of each of the first, second and residual moment matrices.
Status: `INDEPENDENT_UNIFORM_E0_ZERO_DEGREE_ROW_CONTROL_AUDIT_PASS`.
No lower-layer completion enumeration or graph construction is claimed.
