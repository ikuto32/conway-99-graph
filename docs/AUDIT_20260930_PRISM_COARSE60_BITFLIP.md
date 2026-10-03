# Independent review of the six-bit coarse60 normalization

The frozen base formula describes a fixed list of60 coarse columns for the
fixed six-prism core. This review uses its independently checked equivalence
to binary factors, including the outside-column intersection caps. It does
not assume a solution, or an automorphism of a hypothetical target graph.

Index core rows by fibre g, component a, and bit b. Swapping the two bits of
one component simultaneously in all three fibres preserves every core edge:
matching edges reverse their endpoints and cross-fibre edges still join the
same bit. The action fixes fibres and components. Therefore it preserves the
prescribed Gram, coarse column choices, row margins and all column overlaps.
Each action sends a satisfying factor to another factor in the same encoded
family. Its local domain masks are either unchanged or complemented. The
checker reconstructs all18 complement permutations, all64 complete row,
selector and signed-bit maps, and their group law from raw labels.

For any first-column six-bit vector x, flipping exactly its one-components
makes that vector zero. The action is invertible. Thus every base solution
has a relabelled solution of the unit-augmented formula. Conversely every
solution of the augmented formula satisfies the base. The precise six
negative literals are obtained from the column-zero metadata and are checked
against all360 raw bit labels. The entire new CNF body is checked byte for
byte against the original body followed by those six units.

Prefix variables require a new assignment, rather than a signed permutation.
After transporting each one-hot selector, its prefix variables are the
running Boolean OR. An independent checker evaluates every actual exact-one
clause for all136 single-choice assignments in each of18 domains. The
previous base encoding audit supplies the remaining encoding equivalence.
This establishes satisfiability equivalence, without asserting that the
auxiliary-variable clauses have a direct permutation symmetry.

The checker independently reconstructs all135 pair-compatibility relations
by four integer bit-pair counts on the raw column positions. This checks all
2,496,960 selector pairs against the authenticated base tables. Under either
endpoint flip the four counts are permuted, so equality to a common required
value is preserved. All1770 column-pair intersections are preserved because
the action is a single row permutation; no exhaustive assignment census is
claimed. Fresh corrupted maps, target bits, suffixes, and prefix values are
rejected. Local codec controls are not full research factors.

Conclusion: the specified5238-variable85698-clause formula is SAT if and only
if the specified5238-variable85704-clause formula is SAT. This is restricted
to this fixed60-column template. Residual D, arbitrary coarse templates, and
the unrestricted Conway problem are outside the statement. No solver is run
by this review, and no novelty claim is made.
