# Global root fusion-frame identity for the `E0` defect

Status: `GLOBAL_ROOT_FUSION_FRAME_IDENTITY_PASS` (discovery audit; an
independent replay is still required).

This note assumes a putative `srg(99,14,1,2)`.  It derives a global
eigenspace interpretation of

```text
tau(r)=84-E0(r).
```

It is an identity and a new route for a lower bound, not such a bound by
itself.

## Closed-neighbourhood fusion frames

Let

```text
E_-=(3I-A+J/9)/7,       rank(E_-)=44,
E_+=(A+4I-2J/11)/7,     rank(E_+)=54
```

be the two nonprincipal primitive idempotents.  For a vertex `r`, put
`S_r=N[r]`.  The induced graph on `S_r` is the cone over `7K2`.  The
principal block `E_-[S_r,S_r]` has nonzero spectrum

```text
(4/7)^7, (2/7)^6, (20/21)^1
```

and kernel `(4,1^14)`.  If `L_r^-` is the projector in the global minus-four
space onto the span of the 15 coordinate columns indexed by `S_r`, exact
pseudoinversion and the SRG pair counts give

```text
sum_r L_r^- = (63/2) E_-.
```

Thus the projectors onto the minus-four eigenvectors supported on
`V\S_r` form the complementary tight fusion frame

```text
sum_r Pi_r^- = (135/2) E_-.
```

The analogous plus-three blocks have nonzero spectrum

```text
(3/7)^7, (5/7)^6, (69/77)^1
```

and kernel `(-3,1^14)`, yielding

```text
sum_r L_r^+  = (77/3) E_+,
sum_r Pi_r^+ = (220/3) E_+.
```

No vertex transitivity is used.  After inserting the exact pseudoinverse,
the sum over roots has one value on the diagonal, one on adjacent pairs,
and one on nonadjacent pairs, hence lies in the three-dimensional
Bose--Mesner algebra.  Its trace fixes the displayed scalar.

## The rooted fibre projector

At root `r`, let `P_r` be the rank-14 projector onto functions that are
constant on each of the 21 four-point fibres and whose 21 fibre values lie
in the kernel of the unsigned vertex-edge incidence matrix of `K7`.
Inside `Gamma_2(r)`, its entries are

```text
same fibre:       1/6
overlap support: -1/30
disjoint support: 1/60.
```

It is zero outside `Gamma_2(r)`.  The support-incidence equations make
`P_r` orthogonal to both `L_r^-` and `L_r^+`.  Counting the three types of
outer edges gives

```text
tr(P_r A)=E0(r)/2.
```

Since `P_r 1=0`, the global projectors now give the exact pointwise bridge

```text
tr(E_- P_r) = (3*14-E0(r)/2)/7 = (84-E0(r))/14,
tr(E_+ P_r) = 14-(84-E0(r))/14.
```

Equivalently, the Gram-circulation defect is 28 times the compression of
`E_-` to this fibre space.  Its trace `2 tau(r)` is therefore the principal-
angle mass between two canonical subspaces of the full graph, rather than
only a local compression statistic.

## Motif and cross-root form

Using the already audited first moment

```text
sum_r E0(r)=8316-n3-z11/4,
```

we obtain

```text
tr(E_- sum_r P_r) = (n3+z11/4)/14.
```

The tight frame and the same-root orthogonality also turn this into a pure
cross-root energy:

```text
sum_{r != s} tr(P_r L_s^-)
    = (9/4) (n3+z11/4).
```

Every summand is nonnegative.  This recovers only the trivial lower side
`n3+z11/4>=0`; it does **not** yet upper-bound the expression and therefore
does not prove `E0(r)>=L`.  The concrete missing lemma is now an upper bound
on the paired cross-root energy, preferably separated according to `r~s`
and `r not~s`.  Such a bound necessarily uses compatibility between roots
and is a natural place to connect the known four-root mask-3 and mask-12
covariance obstructions.

There is an exact first separation.  Let `T_r` be the two-factor of outer
edges sharing one exact root neighbour, put

```text
K_r^-=E_- P_r E_-,       h_r=tr(K_r^- T_r).
```

Summing the closed-neighbourhood pseudoinverses over the 14 neighbours of
`r` and restricting to `Gamma_2(r)` gives

```text
sum_(s in N(r)) tr(P_r L_s^-)
    = 3 tau(r)/8 + 7 h_r/8.
```

The free fibre space is in the `-2` eigenspace of the exact-support matrix,
which is what collapses all other terms.  Since `T_r` is 2-regular,
`|h_r|<=tau(r)/7`; consequently

```text
tau(r)/4 <= adjacent-root energy <= tau(r)/2,
7 tau(r)/4 <= nonadjacent-root energy <= 2 tau(r).
```

These intervals again allow every nonnegative `tau`.  Their value is that
they isolate the first genuinely missing scalar as the noncommutative
placement `tr(E_- P_r E_- T_r)`, rather than another trace polynomial in
`B` and the support matrix.

The exact rational audit is
`scratch_theory_global_root_fusion_frame.py/.json`.
