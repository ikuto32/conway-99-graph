# Joint unrestricted local triples and exact count-master: candidate design

This is a prospective encoding and a size inventory, not an approved encoding
or a search result. It fixes the same literal six-prism Hadamard support as
the earlier ordered single-column formula. No unknown target automorphism is
assumed. There is no assertion that this support or a balance condition is
universal for Conway99 graphs.

For each of the twenty groups of three identical-support columns, sort the
three six-coordinate fibre-colour words. The complete 31,110-triple catalogue
contains exactly the sorted triples satisfying the local Gram upper bounds
and within-group Y-column caps. Duplicate words would overlap in six rows and
cannot occur under those caps. Sorting is only an outside-column relabelling;
any eventual residual graph must undergo the same column permutation. All
31,110 option IDs are allocated at every group, with no heuristic or orbit
pruning.

Each option determines its 18 count entries. Its selector implies the existing
count-master signature selector for that group. If that signature was removed
by the master's independently checked necessary unary filter, the new selector
has a negative unit. Exactly one triple and one signature are selected, so
these one-way implications enforce exact equality of their count tables. A
reverse implication is unnecessary: the selected triple supplies it through
the two exactly-one constraints. The complete coordinate count domains then
impose all 36 row totals of ten and the previously checked summed-Gram
marginals. This is the missing justification that fixed-profile builders could
obtain directly from their frozen count tables.

For distinct nonmatching coordinates a,b, each of five incident support groups
contributes a 3-by-3 integer overlap matrix. Local upper bounds make each entry
0,1, or2. At a given cell, introduce q1 for a positive contribution and q2 for
a contribution at least two. Under exactly-one group selection, q1+q2 equals
the literal contribution. The sum of ten such bits is one on a same-fibre cell
and two on a different-fibre cell. These are all 540 nonzero off-diagonal
upper-triangular Gram entries. The 36 diagonal entries are supplied by the
linked row totals. All other90 upper-triangular entries are zero directly from
the fixed support and one fibre choice per coordinate in each column. Thus the
whole 36-by-36 integer Gram matrix is covered, including arbitrary unbalanced
group counts.

Conversely, a factor satisfying the fixed support, full Gram and within-group
caps can be sorted groupwise into these local options. Its literal counts obey
the complete master domains and choose the corresponding signature selectors.
The one-hot prefixes and threshold channels can then be assigned their exact
truth values. This proves the proposed baseline equivalence, conditional on
the already checked catalogue and count-master coverage. It remains a new
producer derivation requiring an independent review before any claim use.

The at-least-seven version additionally fixes the master's separate lower
bound on the number of unbalanced groups. The bound is justified for possible
target factors that also satisfy all cross-group caps. It is not claimed to
follow from this formula's full Gram and within-group caps alone. Cross-group
caps and residual D are deliberately unencoded; even SAT would first supply
only a Gram factor, with all1,770 Y overlaps requiring literal diagnostics.

The older 595,464-variable/3,336,642-clause ordered-column formulation already
covers the full fixed support and also encodes all Y caps. The present design
changes representation and adds exact count propagation; it does not enlarge
that scope. The all-triple descent and affine-GF2 models also share the local
catalogue but are not this exact joint CNF. No speedup or novelty follows from
the new representation. Exact size, literal/ASCII accounting and measured
inventory memory are saved separately before any large build decision.
