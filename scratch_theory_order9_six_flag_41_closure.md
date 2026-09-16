# Exact 41-column closure of the six variable flags

## Scope

Starting from the certified 35 columns, this lane adds only

```text
diagonal pair: 46817920192, 56196485312
cross pair B:  14681719440, 56449716416
cross pair A:  46748225728, 47606550720
```

and studies the six rooted order-six flag masks

```text
0: 24699
1: 24939
2: 25147
3: 25507
4: 27179
5: 27299.
```

No other H9 mask, natural `R1` flag, or ambient order-nine census is used.

## Closure graph

The exact 21-product glue scan gives the closed off-diagonal products

```text
(0,1), (0,2), (1,3), (2,4), (3,5), (4,5).
```

This graph is the six-cycle

```text
0--1--3--5--4--2--0.
```

Hence its maximum clique size is two.  There are exactly six licensed
nontrivial `2x2` principal blocks and no licensed `3x3` block.

Among the remaining nine off-diagonal products, six still miss nine H9
masks and three miss fifteen.  In particular every chord needed to create a
triangle requires at least nine additional masks, outside this bounded lane.

## Added-mask deletion decks

All 36 vertex deletions of the four newly added cross masks lie in the frozen
916-class H8 catalogue.  They use 18 distinct H8 shadows, all with positive
Wave163 counts.  The two diagonal masks had already passed the analogous
18-slot check in the preceding probe.

## Local identities fix all six new counts

Use variable order

```text
d0,d1,c0,c1,c2,c3
 = counts of
46817920192, 56196485312,
14681719440, 56449716416,
46748225728, 47606550720.
```

The 41-column extension scan touches

```text
81 unmarked, 269 vertex-rooted, 757 ordered-pair rows.
```

Exactly 58 ordered-pair rows close.  Relative to the 35-column stage, 24 are
newly closed.  Their restriction to the six new variables has rank six and
uniquely forces

```text
(d0,d1,c0,c1,c2,c3)
 = (8316,74844,8316,74844,8316,66528).
```

The full closed-row rank on all 22 nonfixed H9 variables is 13.

Together with the previous 16-variable witness, these six values give a
nonnegative integral 41-column point satisfying all 58 closed rows and every
open-row upper bound.  No new congruence obstruction appears.  As in the
earlier targeted lifts, simultaneous ambient realization of the separate
open-row slacks is not claimed.

## Exact Gram blocks

All 1,205 frozen coefficient classes on union orders 6 through 9 were
replayed for this six-flag family.  After substituting the uniquely forced
counts, each of the six licensed blocks is exactly

```text
[ 199584  199584 ]
[ 199584  199584 ].
```

Thus every block is PSD of rank one, has determinant zero, and has kernel
vector `(1,-1)`.  There is no negative direction and therefore no coefficient
translation to a positive `E0` lower bound.

The six newly carried H9 masks have zero coefficient in the previously
closed natural `{R0,X_0,X_1,X_2,P}` block, so that earlier rank-one Gram is
unchanged.

## Claim boundary

This branch terminates here:

- the closure graph has no clique larger than two;
- all six available `2x2` tests collapse to the same rank-one PSD boundary;
- obtaining even one closed `3x3` block requires at least nine more H9 masks.

The calculation therefore supplies neither an endpoint exclusion nor an
`E0` lower bound.  A different synchronization statistic, such as the
endpoint relation's `K`-triangle compatibility, is a more appropriate next
lane than extending this flag-support branch.

Artifacts:

```text
scratch_theory_order9_six_flag_41_closure.py
scratch_theory_order9_six_flag_41_closure.json
scratch_theory_order9_six_flag_41_closure_audit.py
scratch_theory_order9_six_flag_41_closure_audit.json
```

The audit imports no 41-column producer.  It independently replays the 36
new deletions, 21 closure products, 1,205 coefficient classes, 1,107 local
rows, the rank-six count determination, and all six PSD blocks.  It passes.

Frozen order-8 assets were read only; no order-8 class was regenerated and
`submission.txt` was not created.

## Subsequent structural explanation

The connected rank-one `2x2` blocks already force the full PSD completion
to be `199584 J6`; explicit coefficient closure of a `3x3` block is not
needed for that conclusion.  More strongly, the bijection proved in
`scratch_theory_six_flag_uniformity.md` shows that all six flag counts equal
12 at every ordered triangle in **every** `srg(99,14,1,2)`, without assuming
`T=0`.  Thus adding the missing chords in this same family supplies only
universal equalities, not a new endpoint obstruction.  The original
41-column certificate is unchanged.
