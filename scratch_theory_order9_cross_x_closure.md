# Targeted 28-column closure of the distinct-`X` Gram block

## Result

The nine previously identified locally admissible H9 masks are exactly the
missing order-nine support of each of the three products

```text
X_0 X_1,  X_0 X_2,  X_1 X_2.
```

After adjoining only these masks to the 19 visible columns, the natural
four-flag block `{X_0,X_1,X_2,P}` closes.  At the Wave163 endpoint `T=0` its
exact raw integral Gram matrix is

```text
        X_0     X_1     X_2       P
X_0  199584  199584  199584       0
X_1  199584  199584  199584       0
X_2  199584  199584  199584       0
P         0       0       0       0
```

It is PSD of rank one.  Its nonzero eigenvalue is `598752`, and an integral
kernel basis is

```text
X_0-X_1,  X_0-X_2,  P.
```

Thus this minimal closure gives no negative direction at `T=0`.

## The nine columns and their complete deletion decks

In the following order, write their H9 counts as `e0,...,e8`:

```text
e0   1452696264
e1   3667223248
e2   3669518466
e3   6091774020
e4  10042630856
e5  14681708612
e6  36940436610
e7  61422027409
e8  61424673410
```

All `9*9=81` one-vertex deletion slots were canonicalized independently.
They occupy 24 distinct H8 masks, every one belonging to the frozen list of
916 locally admissible H8 classes.  All 24 also have positive Wave163 H8
count.  The certificate records every slot, its frozen index, and its
Wave163 count.

No ambient H9 census was generated in this check.

## Why the cross entries are forced

The nine masks have no `X_j` diagonal coefficient and no coefficient
involving `P`.  Their coefficient in each distinct-`X` cross entry is

```text
(2,6,2,2,6,2,2,6,2).
```

The 19-column value of each such cross entry was `29352`.  At `T=0`, every
one of the 231 target triangles has `q=12`, there are six ordered rootings of
each triangle, and `P=0`.  Therefore every `X_j X_k` entry must equal

```text
231 * 6 * 12^2 = 199584.
```

Consequently the added counts obey the one exact mass equation

```text
e0 + 3e1 + e2 + e3 + 3e4 + e5 + e6 + 3e7 + e8 = 85116.       (G)
```

## Newly closed H8-to-H9 rows

On 28 columns, the targeted local extension scan touches 46 unmarked, 165
marked-vertex, and 505 ordered-pair rows.  No unmarked or marked-vertex row
closes.  There are 31 closed ordered-pair rows: the old 21 plus 10 new rows.
The 10 new rows occur in reverse-root pairs and reduce to five independent
equations of rank five:

```text
6e7 + 2e8                  =  11844
2e4 + e6                   =  10224
2e4 + 2e5                  =  13584
6e1 + e2 + 2e4             =  25986
2e0 + e2 + 2e3 + e6        = 108594.                         (D)
```

Equation `(G)` is exactly one half of the sum of these five equations.  The
closed Gram cross mass therefore adds no independent equality beyond the
new deletion rows.

The complete integer solution of `(D)` can be written with
`a=e1,b=e4,c=e7,d=e0` as

```text
e0 = d
e1 = a
e2 = 25986 - 6a - 2b
e3 = 36192 + 3a + 2b - d
e4 = b
e5 = 6792 - b
e6 = 10224 - 2b
e7 = c
e8 = 5922 - 3c.
```

Nonnegativity requires

```text
a,b,c,d >= 0,  3a+b <= 12993,  b <= 5112,
c <= 1974,      d <= 36192+3a+2b.
```

In particular `e2` and `e6` are even.  These are coordinate congruence
consequences, not a new congruence obstruction on the frozen Wave163 data.

The following integral point satisfies `(G)`, all 31 closed rows, and every
open-row upper bound:

```text
(e0,...,e8) = (0,0,25986,36192,0,6792,10224,0,5922).
```

As in the earlier 19-column projection, the nonnegative slacks of different
open rows are not claimed to come from one simultaneous ambient H9
distribution.  The claim here is exactly the targeted 28-column projection.

## Exact next missing data

Among all 74 triangle-rooted order-six flags previously extracted from the
19 masks, a complete diagonal glue scan finds that only
`X_0,X_1,X_2,P` have diagonals closed on the 28 columns.  For an open
diagonal, the smallest possible missing support has size two.  It occurs for
the six rooted flag masks

```text
24699, 24939, 25147, 25507, 27179, 27299
```

and in every case the two missing H9 masks are

```text
46817920192, 56196485312.
```

This is the smallest next *diagonal* data requirement in the frozen
74-flag family.

If the next step is instead required to adjoin one complete natural matching
flag to `{X_0,X_1,X_2,P}`, `R0` is the cheapest choice.  It needs seven new
H9 masks (each `R1_j` needs 17):

```text
1292419201
3668590721
13610256401
14889779459
24436319376
32214460576
35652157569
```

## Scope and replay

The producer is
`scratch_theory_order9_cross_x_closure.py`; its exact certificate is
`scratch_theory_order9_cross_x_closure.json`.  The independent audit is
`scratch_theory_order9_cross_x_closure_audit.py`, with output
`scratch_theory_order9_cross_x_closure_audit.json`.

The audit imports no producer code.  It independently reconstructs all 81
deletions, all 28 raw H9 coefficient matrices, the three distinct-`X` glue
supports, 74 diagonal supports, 20 natural next-enlargement products, and all
716 touched local extension rows.  It passes.

The frozen 916/208/944/4440/2414 assets were not regenerated, no general
order-nine census was attempted, and `submission.txt` was not created.
