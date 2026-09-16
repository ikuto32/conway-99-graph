# Corrected root-fibre/prism bridge (the proposed `E0` bound is invalid)

## Audit outcome

The initially proposed identity `sum_r E0(r)=6P` was wrong. It conflated the
four square **side** pairs in a support fibre with all six pairs in that
fibre. This was caught before the derived CNF was ever solved or used to
exclude a branch.

Write

```
S(r) = selected side edges in the 21 fibres at root r,
D(r) = selected diagonal edges in those fibres,
E0(r) = S(r) + D(r).
```

Diagonal fibre edges are genuinely allowed by the rooted SRG equations; the
existing fibre-state catalog includes one-diagonal and two-diagonal states.

## What is true

A fibre side edge `xy` shares exactly one root-neighbour `u`. If the
other two root-neighbours on the support are the matched pair `v,v'`, then

```
{u,x,y} and {r,v,v'}
```

are triangles, joined by the matching `ur,xv,yv'` (up to exchanging `v,v'`).
The SRG common-neighbour conditions forbid every additional cross-edge, so
these six vertices induce a triangular prism.

Conversely, if an induced triangular prism contains `r`, its triangle through
`r` supplies a matched pair `v,v'`; the unique opposite vertex adjacent to
`r` is a root-neighbour `u`, and the other two opposite vertices have root
supports `{u,v}` and `{u,v'}`. Their prism edge is therefore one fibre side
edge counted by `S(r)`.

Thus `(r, fibre side edge)` is in bijection with `(induced prism, a
chosen vertex of that prism)`, and hence

```
sum_r S(r) = 6 P.                                       (1)
```

This argument uses only the SRG equations and is independent of the SAT
computations.

## What the public `n3` bound would imply

The public `conway-99-research` audit reports the exact identity

```
n3 + 3 P = 4158
```

and its strongest internally verified necessary bound `n3 >= 708`.  Taken as
an external premise, these give `P <= 1150`; combining with (1),

```
min_r S(r) <= floor(6*1150/99) = 69.                    (2)
```

This gives no bound `min_r E0(r)<=69` without an additional bound on `D(r)`.
The generated `scratch_root_e0_le69.cnf` counted all `126=21*6` same-fibre
variables and is therefore unsupported. It was never solved, is quarantined,
and contributes no result. The self-contained frontier remains `E0<=75`.

Public source consulted for the external premise (not fully replayed here):

https://github.com/YesterdaysLemon/conway-99-research
