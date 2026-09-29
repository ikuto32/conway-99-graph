# Independent modular-rank necessity derivation

Let `A` be any symmetric binary99by99 matrix with zero diagonal satisfying
`A^2=12I-A+2J`. Every assertion below is conditional on this exact target;
no graph automorphism, selected scaffold, or local completion is assumed.

The diagonal gives degree14, so `A j=14j`. Over the rationals, the space
splits as the line spanned by `j` and its98dimensional orthogonal complement.
The latter is invariant under `A`, and the target identity there reads
`(A-3I)(A+4I)=0`. The distinct roots give a direct sum of the3 and−4 eigenspaces.
If their dimensions are `f,g`, then `f+g=98`. The zero trace of `A` gives
`14+3f-4g=0`. Therefore `f=54,g=44`, and the exact characteristic polynomial is

`chi_A(t)=(t-14)(t-3)^54(t+4)^44`.

These are exact integer polynomial coefficients, so reducing them modulo a
prime gives the characteristic polynomial of the reduced integer matrix.
This uses the determinant polynomial itself, without reducing rational
eigenvectors or assuming that their bases remain independent modulo a prime.

Modulo2 the target identity gives `A^2=A`, with squarefree annihilator
`t(t+1)`. Its reduced characteristic polynomial is `t^45(t+1)^54`.
An idempotent splits as its kernel and image, acting as0 and1 respectively.
Thus `rank_F2(A)=54` exactly.

Modulo3, `A^2+A=-J`, while `(A+I)J=0` because `AJ=14J=-J` in this field.
Consequently `A(A+I)^2=0`. The reduced characteristic polynomial is
`t^54(t+1)^45`. The factors `t` and `(t+1)^2` of the annihilator are coprime,
so the space is the direct sum `ker(A)` and `ker((A+I)^2)`. The first has
characteristic factor `t^dim`; on the second, `A` is invertible and has only
eigenvalue−1, with possible nontrivial Jordan blocks. Comparison with the
characteristic polynomial gives `dim ker(A)=54`, hence `rank_F3(A)=45`.
The simple zero factor is essential; diagonalizability modulo3 is not assumed.

For `G=27I-9A+J`, the preceding rational decomposition shows eigenvalue0 on
`j` and on the54dimensional3-eigenspace, and eigenvalue63 on the44dimensional
−4-eigenspace. Hence `chi_G(t)=t^55(t-63)^44`. Direct expansion using
`AJ=JA=14J` and `J^2=99J` also gives `G^2=63G`. Modulo2 this is idempotence,
and the characteristic polynomial is `t^55(t+1)^44`, proving
`rank_F2(G)=44` exactly.

Deleting rows or columns cannot increase rank over any field. If a raw graph
`H` on59 vertices were an induced principal subgraph of a target, then
`rank_F3(H)<=45` and `rank_F2(27I59-9H+J59)<=44`. A46by46 minor with nonzero
determinant modulo the relevant prime is therefore a complete lower-bound
certificate excluding that particular induced graph from every target.
The row and column index lists need not be identical; both must refer to
distinct selected rows/columns of the raw principal matrix.

The new review does not need to verify the producer's reported full local
ranks. It independently extracts46by46 minors and checks their literal integer
determinants by fraction-free Bareiss elimination, with a separate modular
elimination selector. The final determinant is reduced only after the exact
integer calculation. Determinant controls include known matrices, exhaustive
small direct Leibniz calculations, singular corruptions, and altered
certificate claims. These finite controls calibrate the implementations;
they do not replace the universal derivation above.

All eleven saved raw59 adjacency matrices were already excluded by earlier
Gram or local arguments. These modular certificates supply different necessary
condition evidence for the same exact objects; they do not exclude their whole
fixed family, prove that a target contains one of them, or establish target
nonexistence. No novelty claim is made. The original producer's Python3.12
spacing SyntaxWarnings are preserved as provenance, not treated as a refutation
of its mathematical statements or silently fixed in its source.
