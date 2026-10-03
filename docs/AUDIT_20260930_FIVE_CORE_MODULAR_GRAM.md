# Independent kernel-invariance and finite rank audit

Let C be a symmetric adjacency matrix on three equal nonempty cells of size
n, with precisely one neighbor in each cell. Let B have three diagonal J_n
blocks. Counting entries gives CB=BC=J and CJ=JC=3J, hence C commutes over
the integers with G=nI-C-C²+2J-B. Thus N=ker G is invariant over every field.
If FFᵀ=G and L=ker Fᵀ, then L is contained in N. Linear consistency of FD=H
is equivalent to each column of H being orthogonal to L. This equivalence
uses the nondegenerate ordinary coordinate pairing, not a positivity claim
over finite fields.

Over GF2 the cell-column sums2 put the three cell indicators in L. Their
span R has dimension3 and is C-invariant because C maps each indicator to
the all-ones vector. If the induced action on N/R is multiplication by a
scalar a, then Cx-ax belongs to R for every x in L. Consequently Cx belongs
to L. Symmetry of C now gives xᵀ(I+C)F=0. The inhomogeneous term2J vanishes,
so FD=2J-(I+C)F has a solution over GF2. If rank G≥3n-4 then dim(N/R)≤1,
and every endomorphism of this quotient is scalar. This proves the claimed
sufficient condition without assuming maximal rank of F. It is conditional
on the stated factor and cell relations, and says nothing about a symmetric
or binary D.

Over GF3 let R be spanned by the first-minus-third and second-minus-third
cell indicators. The cell-column sums imply R≤L. C kills R. In the three
specified cores connected01,02,03, the independently checked finite action
certificates give C(N)⊆R. It follows that C(L)⊆L for any putative factor.
Its integer row sum10 implies Fj=j over GF3. Therefore xᵀj=0 for x in L,
and both the inhomogeneous term2J and the two F terms in xᵀH vanish. This
proves conditional field consistency for those three cores only. Row sum18
of the243 fixture vanishes in GF3; that fixture is deliberately excluded
from this particular corollary. No analogous claim is made for connected00.

The executable audit reconstructs prescribed G using literal neighbor-set
intersections, checks integer commutation using neighbor sums, and replays
every invertible row operation in all14 saved rank certificates. An
independent rightmost-pivot incremental span basis checks ranks and complete
kernel bases, separately from the producer's leftmost-pivot full RREF.
All10 quotient actions are checked directly by mapping each raw-coordinate
kernel basis vector with C and verifying its saved coordinates. No producer
elimination, coordinate solving or arithmetic routine is imported.

Positive controls enumerate all64 binary and729 ternary2×3 matrices and
compare rank with explicitly enumerated row-span cardinality. The known243
nonempty fixture also checks the complete integer Gram, exact margins and
actual residual mixed equation in both fields. Ten altered certificate,
kernel/action and raw-core controls must fail. These controls supplement,
and do not replace, the universal written argument above.

The verified GF2 ranks are22,24,24,26,30; GF3 ranks27,29,29,29,27. The order
is connected00,01,02,03,known243. All five GF2 quotient actions are nonscalar.
Thus the new GF2 sufficient tests do not settle these cases. This failure
does not demonstrate an inconsistent factor. The three GF3 corollaries can
prevent repeated attempts to find a GF3 linear obstruction in those fixed
domains, but leave all other residual constraints unresolved.

No target automorphism, target asymmetry, unrestricted identity-P reduction,
all-core census, new factor, target graph, exclusion or novelty is asserted.

```
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_five_core_modular_gram.py --out acceleration/results/20260930_independent_review/five_core_modular_gram
```
