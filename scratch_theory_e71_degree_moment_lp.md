# Exact quadratic degree-moment certificates from a small convex relaxation

This is an identity-discovery filter on the **already frozen** 132-macro,
140-profile E71 frontier.  It does not enumerate any matching, overlap
product, local graph completion, or lower E0 layer.  The numerical LP is
used only to find short integer certificates; an LP status is never itself
an exclusion certificate.

The first three control profiles reproduce the independently audited
source694 contradiction and allow source724's known degree-Gram control.
The complete frozen-profile run takes about 29 seconds and emits exact
integer Farkas certificates for 68 profiles, covering all retained profiles
of 66 macros.  Their union has labelled coverage 22,675,456.  The separate
model/domain/certificate audit has now passed, and was replayed by the root
agent.  The scoped inventory credits exactly these 66 macros, plus the
disjoint prior source724 exclusion.

## Necessary row moments

Let `B` be the outer 84-vertex adjacency matrix at a graph root, and `P`
the 84-by-21 incidence of its four-vertex fibres.  Write

```text
C=P^T B P,       Z=C0-C,       K4=28Z-Z^2,
R=4BP-PC.
```

The rooted SRG equations imply

```text
R^T R = 4K4,             P^T R=0.                    (1)
```

In particular each residual row lies in `row(K4)`.  If vertex `x` belongs
to fibre `G`, its row is

```text
R_x = 4d_x-C[G,*],
```

where all 21 fibre degrees are integers in `0,...,4`, summing to 12.
These conditions have small exact row domains for the frozen profiles.
Fix a pivot column set `I` of `K4` and write `v_x=R_x[I]`.  The remaining
coordinates of `R_x` are uniquely determined by `v_x`.

The proof of (1) is independent of numerical eigensolvers.  Since
`P^T P=4I`, expansion gives `R^T R=16P^T B^2P-4C^2`.  The outer SRG
equation then yields

```text
K4=192I+128J-4C-32 L L^T-C^2,
```

where `L` is the 21-by-7 support incidence matrix.  This agrees exactly
with `28Z-Z^2` on the frozen full-Gram profiles.

## The convex model

For each fibre `G` and each internal degree `d`, let `m_Gd` be the number
of its four vertices with that fixed degree.  Exceptional internal graphs
are recorded explicitly in the macro.  Ordinary fibres necessarily induce
a four-cycle, so all four of their internal degrees are two.

Introduce a nonnegative weight `w_Gd,v` on every raw residual row whose
own-fibre degree equals `d`.  An actual graph supplies nonnegative integer
weights, but integrality is deliberately relaxed.  The only equations are

```text
sum_v w_Gd,v = m_Gd,                         for every (G,d),
sum_(d,v) w_Gd,v v = 0,                     for every G,
sum_(G,d,v) w_Gd,v v_i v_j = 4K4[I_i,I_j],  for every i<=j.       (2)
```

There is no requirement here to realize any adjacency block.  There is no
enumeration of four-row products.  The model even permits different
positions of the same internal degree to be combined fractionally.  Thus
failure of (2) is a sound obstruction; passing it is a weak necessary
condition, not evidence of a realizable graph.

## A certificate is a pointwise quadratic inequality

Write (2) as `A w=b, w>=0`.  Each emitted integer multiplier `y` is checked
by exact arithmetic to satisfy

```text
A^T y >= 0,              b^T y < 0.                    (3)
```

This is a finite, solver-independent proof: summing the nonnegative
column inequalities with the hypothetical weights would give
`0 <= w^T A^T y = b^T y < 0`.

Equivalently, the multiplier has a constant `alpha_Gd`, a linear fibre
coefficient `beta_G`, and a common quadratic coefficient vector `h` such
that every allowed row satisfies

```text
alpha_Gd + beta_G dot v + sum_(i<=j) h_ij v_i v_j >= 0,
```

but its sum forced by the graph identities is

```text
sum_(G,d) m_Gd alpha_Gd + 4 sum_(i<=j) h_ij K4[I_i,I_j] < 0.
```

This is the reusable mathematical output, not merely an infeasible LP.
The coefficients found in the complete run have at most 14 bits.  All
target pairings are at most -32.  No floating tolerance appears in the
acceptance of (3): rationalization is accepted only after checking every
integer column and the target exactly.

The earlier affine-support test is a special case, with each pointwise
quadratic value constant after fixing its own-fibre degree.  Besides the
source694 `4 != 52` equality, it finds source901 square identities with
forced value 384 and Gram-required value 512.  The convex test can also
use inequalities and fibre first moments, and is substantially stronger.

## Controls, files, and claim boundary

```text
scratch_theory_e71_degree_moment_lp_probe.py
scratch_theory_e71_degree_moment_lp_probe.json      # initial three controls
scratch_theory_e71_degree_moment_lp_frontier.json   # all frozen profiles
```

The exact reconstruction/audit is in the separate
`scratch_theory_e71_degree_moment_lp_audit` files.  Its status is
`INDEPENDENT_E71_DEGREE_MOMENT_LP_AUDIT_PASS`.  The producer imports
existing compression/RREF helpers; the independent checker reconstructs
all 23,137 raw rows by principal-matrix inversion and all 140 equality
matrices without those imports or an LP solver.  It checks every integer
column inequality and requires certificates for every frozen full-Gram
profile of a macro before crediting that macro.

The source724/Q2 profile passes this weaker moment model, as expected from
its explicit degree-Gram witness.  Its exclusion by pointwise transport
and a residual-projector row norm remains an independent cut.  The audited
disjoint union leaves 65 macros, coverage 26,378,240, in this particular
132-macro frontier.  `scratch_root_e71_theory_frontier_inventory.py/.json`
checks hashes, coverage, and disjointness; it does not replace the linked
mathematical audits.

No positive pointwise `E0` lower bound, exclusion of the full E71 layer,
or Conway graph construction is asserted.  E72 calculations are unchanged.
The frozen 916 order-eight classes and coefficient matrices are not
regenerated.  No `submission.txt` is created.
