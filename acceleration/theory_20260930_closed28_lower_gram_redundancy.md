# Candidate redundancy of the complementary closed-neighborhood Gram test

Status: **CANDIDATE mathematical derivation, pending separate review.**
No floating-point result is used as a premise.

Let H be a finite simple graph whose vertices are `N[v] ∪ N[u]`, where v
and u are nonadjacent, each has degree14, and for each center c and every
other vertex x the exact equality
`|N(c) ∩ N(x)| = 2 - adjacency(c,x)` holds. No other pair caps are assumed.
The candidate conclusion is that `A(H)+4I` is positive semidefinite and
has rank27 (and nullity1).

The two centers have exactly two common neighbors, so H has28vertices.
Delete the centers to obtain R of size26. Let B be its adjacency matrix,
n and m the two center-neighborhood indicators on R, j the all-one vector,
`t=n+m`, `d=n-m`, and `c=t-j`. Then c is the indicator of the two common
neighbors; t has24entries1 and2entries2. Therefore

`||t||²=32`, `||c||²=2`, `cᵀt=4`, `||d||²=24`.

The center equalities give `Bn=2j-n` and `Bm=2j-m`, hence
`Bt=4j-t` and `Bd=-d`. Since every entry of t is at least1,
`degree_B(i) ≤ (Bt)_i ≤ 3`. Define `M=B+4I`. The exact identity

`zᵀ(M-I)z = Σ_{ij∈E(B)}(z_i+z_j)² + Σ_i(3-degree_B(i))z_i²`

shows `M ⪰ I`, so M is positive definite and `M⁻¹ ⪯ I`.
In particular `r=cᵀM⁻¹c ≤ cᵀc=2`.

The useful additional identity is

`Mt=4j+3t=7t-4c`, thus `M⁻¹t=t/7+(4/7)M⁻¹c`.

By symmetry of the inverse,

`tᵀM⁻¹t = 32/7 +(4/7)tᵀM⁻¹c`
`             = 32/7 +(4/7)(4/7 +(4/7)r)`
`             = (240+16r)/49 ≤ 272/49 < 8`.

Order H as the two centers followed by R. Its shifted adjacency is

`Q = [[4I₂, Cᵀ], [C, M]]`, where `C=[n m]`.

Since M is positive definite, Q is congruent to the direct sum of M and
the2by2 Schur complement `S=4I₂-CᵀM⁻¹C`. From `Md=3d`,
`nᵀM⁻¹d=(14-2)/3=4` and `mᵀM⁻¹d=(2-14)/3=-4`.
Consequently `S(1,-1)ᵀ=0`. As S is symmetric, its other eigendirection is
`(1,1)`, with eigenvalue

`4 - (1/2)tᵀM⁻¹t ≥ 4-136/49 = 60/49 > 0`.

Thus S is positive semidefinite of rank1; Q is positive semidefinite of
rank `26+1=27`. Its kernel is precisely the span of
`(n-m)-3(e_v-e_u)` (interpreting n,m as zero on the two centers).

This would establish redundancy of the lower Gram test under the same
center equalities as the other closed-neighborhood redundancy theorem.
It neither establishes extendability of H nor excludes any target family.
The numerical2688case screen motivated the question, but is not evidence
for the universal implication beyond calibrated examples.
