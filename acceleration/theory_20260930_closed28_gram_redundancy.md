# Candidate: closed-two-neighborhood Gram redundancy

Status: **CANDIDATE** pending a separately recorded independent review.
This follows the completed negative-certificate search; the earlier experiment
and necessity note remain unchanged.

Let `H` be a finite simple graph on `N[v] ∪ N[u]`, with nonadjacent distinguished
vertices `v,u`, each of degree 14, and for each `c ∈ {v,u}` suppose

```
|N(c) ∩ N(x)| = 2 - adjacency(c,x)  for every x ≠ c.
```

All neighborhoods and degrees here are in `H`; both complete center
neighborhoods are present. Then `27I-9H+J` is positive semidefinite. The
statement imposes no spectral assumption on a missing completion.

Write `R = V(H) \ {v,u}` and `B = H[R]`. Every vertex `x ∈ R` lies in at least
one of `N(v),N(u)`. Every remaining neighbor of `x` lies in their union, hence

```
deg_B(x) ≤ |N(x) ∩ N(v)| + |N(x) ∩ N(u)|
         = 4 - adjacency(v,x) - adjacency(u,x) ≤ 3.
```

Possible overlap only decreases the first bound.

Let `G = 27I-9H+J`. Direct substitution gives exact kernel vectors

```
k_v = 4e_v + 1_N(v),    k_u = 4e_u + 1_N(u).
```

For a center `c`, its own coordinate of `G k_c` is `4·28 - 14·8 = 0`.
For every `x ≠ c`, that coordinate is
`18 - 9 adjacency(c,x) - 9 |N(c)∩N(x)| = 0`.
Because the centers are nonadjacent, their two coordinates in these two kernel
vectors form the nonsingular diagonal matrix `4I`.

For any real vector `t` on `V(H)`, subtract
`(t_v/4)k_v + (t_u/4)k_u`. The new vector is zero at both centers and has
coordinates `z/4` on `R`, where

```
z_i = 4t_i - t_v·1_(i∈N(v)) - t_u·1_(i∈N(u)).
```

Subtracting kernel vectors does not change the quadratic form. Therefore

```
16 tᵀGt
 = zᵀ(27I - 9B + J)z
 = 9 Σ_{ij∈E(B)} (z_i-z_j)²
   + 9 Σ_{i∈R} (3-deg_B(i)) z_i²
   + (Σ_{i∈R} z_i)² ≥ 0.
```

All coefficients are nonnegative integers. This is an exact sum-of-squares
identity, not a floating eigenvalue argument.

The root scaffold and a completed retained center star have exactly the
required center-to-inner common-neighbor counts. The root-to-outer counts
come from the two recorded labels per outer vertex. Completing the induced
center neighborhood as a perfect matching supplies all remaining
center-to-neighbor counts. Thus every such matching-specific closed28 graph
meets the theorem's hypotheses, subject to the already stated graph-closure
argument and the independent domain/filter premises.

Consequently, checking this particular closed28 Gram matrix cannot discard a
matching that already satisfies those local equalities. A useful stronger
Gram test would need additional vertices or constraints beyond these two
complete neighborhoods. No claim is made here about the sufficiency of any
such enlargement or about target existence.

The numerical screen examined 2,688 frozen matching choices and found no
eigenvalue below its declared -1e-8 signal threshold. Its minimum reported
float64 value, approximately -3.1341e-14, is numerical guidance only. The
separately saved exact decomposition artifacts test the integer identities
for those same cases and retain full28 adjacency rows and full99 vertex maps
for a separate checker. Sampled agreement is not the general proof.
