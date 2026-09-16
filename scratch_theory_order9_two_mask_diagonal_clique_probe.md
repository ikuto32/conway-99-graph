# Two-mask diagonal / six-flag clique probe

This is the bounded follow-up to the 35-column `R0` closure.  It does not
continue to the natural `R1` flags and does not enumerate general H9 graphs.

The six previously identified rooted flag masks

```text
24699, 24939, 25147, 25507, 27179, 27299
```

all need exactly the same two H9 masks to close their diagonals:

```text
46817920192, 56196485312.
```

Both masks are locally admissible.  Their 18 vertex deletions use 11 frozen
H8 classes, all lying in the frozen 916 catalogue and all having positive
Wave163 count.

After provisionally adding only these two masks to the 35-column universe,
all six diagonals close.  However, none of the 15 off-diagonal flag products
closes.  The closure graph on the six flags is therefore edgeless and has
maximum clique size one.  In particular, there is no licensed nontrivial
`2x2` or larger Gram block to evaluate at this boundary.

The exact off-diagonal support-deficit histogram is

```text
deficit 2:   6 products
deficit 9:   6 products
deficit 15:  3 products.
```

The six minimum-deficit products split into two missing-mask pairs, each
used by three products:

```text
14681719440, 56449716416
46748225728, 47606550720
```

Adding either pair would create three closed `2x2` blocks, but neither pair
is introduced or assigned a count here.  Consequently this probe makes no
PSD or negative-direction claim beyond proving that the shared diagonal
pair alone cannot yield one.

Artifacts:

```text
scratch_theory_order9_two_mask_diagonal_clique_probe.py
scratch_theory_order9_two_mask_diagonal_clique_probe.json
scratch_theory_order9_two_mask_diagonal_clique_probe_audit.py
scratch_theory_order9_two_mask_diagonal_clique_probe_audit.json
```

The independent audit recomputes all 18 deletions and all 21 products without
importing the probe producer.  It passes.  No `R1` extension, general H9
census, frozen order-8 regeneration, or `submission.txt` creation was done.
