# Exact source2601 kernel--port exclusion

Status: `INDEPENDENT_SOURCE2601_KERNEL_PORT_EXCLUSION_PASS` in
`scratch_theory_e71_source2601_kernel_port_audit.json`.

Assume that an `srg(99,14,1,2)` has a root whose `E0=71` compression is one
of the two canonical source2601 macros.  Write `B` for adjacency on the 84
vertices at distance two, `M` for their `84 x 21` four-fibre incidence
matrix, `Q=M/2`, and `C=M^T B M`.  The columns of `Q` are orthonormal.

Let `X` be the `84 x 14` incidence from the outer vertices to the root
neighbours.  The outer--outer block of

```
A^2 = 12I - A + 2J
```

is `B^2+XX^T=12I-B+2J`.  Moreover `M^TM=4I`, `M^TJM=16J`, and direct fibre
incidence gives `M^TXX^TM=8LL^T`, where `L` is the unsigned `K7` incidence
matrix.  Therefore, for

```
W=(I-QQ^T)BQ,
```

exact multiplication gives

```
K4 := 16W^TW = 192I+128J-4C-32LL^T-C^2.             (1)
```

Put `C0=12I+4J-4LL^T` and `Z=C0-C`.  The exact full-Gram circulation has
`ZL=ZJ=0`; expanding (1), using that the `C0` case has zero defect, yields

```
K4=28Z-Z^2.                                           (2)
```

If outer vertex `x` is in fibre `G`, then

```
8W[x,F]=4 deg(x,F)-C[G,F].                            (3)
```

Thus `c in ker(K4)` implies `Wc=0`, because
`c^T K4 c=16||Wc||^2`.  Applying (3) pointwise gives

```
4 sum_F c_F deg(x,F)=(Cc)_G.                          (4)
```

For source2601, exact integer matrix multiplication verifies

```
spec^+(Z)  = {8,9,9},
spec^+(K4) = {160,171,171},
c=e_{02}-e_{14} in ker(K4).
```

For `G=04` and `G=12`, the completed compression has

```
C[G,02]=C[G,14]=2.
```

Equation (4) consequently requires `deg(x,02)=deg(x,14)` for every vertex
of either fibre.  But the internal state and port stubs give the following
degree vectors in the canonical four-vertex order:

```
state 1, G=04: into 02 = (1,1,0,0), into 14 = (1,0,1,0)
state 1, G=12: into 02 = (0,0,1,1), into 14 = (0,1,0,1)

state 4, G=04: into 02 = (0,1,0,1), into 14 = (0,0,1,1)
state 4, G=12: into 02 = (1,0,1,0), into 14 = (1,1,0,0).
```

A group matching may choose the opposite endpoint of each used stub, but
cannot change these source-side incidence vectors.  Hence every matching
choice violates a required pointwise equality.  Each macro has 8,192 raw
overlap products and labelled catalogue coverage 131,072.  Both macros are
therefore impossible, excluding exactly 262,144 labelled macro coverage.

The audit reconstructs `C,Z,K4`, checks the two annihilating polynomials,
checks `K4c=0`, rebuilds every filtered group domain from the catalogue, and
recomputes all four port-incidence vectors.  No floating-point eigensolver or
SAT result enters the proof.
