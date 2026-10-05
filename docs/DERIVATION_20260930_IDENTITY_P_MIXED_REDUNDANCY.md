# Candidate identity-P factor-column and mixed-cap lemma

Status: **CANDIDATE**, pending independent review. This is a redundancy lemma in
an explicitly restricted core family, not a factor construction or exclusion.

Let the 36 inner vertices be `(g,a)`, where `g=0,1,2` and `a=0,...,11`. Let each
`M_g` be any perfect matching on the twelve coordinates. Join matching pairs
inside each fibre and join `(g,a)` to `(h,a)` for every `g != h`. Write its
adjacency as C, and let T be the 3-by-36 fibre incidence matrix. Suppose a binary
36-by-60 matrix F satisfies, exactly over the integers,

`F F^T = G = 12I + 2J - C - C^2 - T^T T`.

For distinct fibres g,h and the same coordinate a, C has entry 1, C-squared has
entry 1 (the third vertex of their coordinate triangle), and T-transpose T has
entry 0. Matching edges provide no extra common neighbor because a matching has
no fixed point. Consequently `G[(g,a),(h,a)] = 2-1-1 = 0`.
The corresponding Gram entry is a sum of nonnegative binary products. Every
summand is therefore zero. Thus in every column of F at most one of the three
rows with coordinate a is selected.

The closed neighborhood of `(g,a)` in C consists precisely of its coordinate
triangle and the additional row `(g,M_g(a))`. A column contributes at most one
from the former and at most one from the latter. Hence every entry of `(I+C)F`
is at most 2. This proves mixed-cap redundancy for any choices of the three
matchings; connectedness and component-size restrictions are unnecessary.

If in addition every column has two ones in each fibre, its six selected rows
have six distinct coordinates. The two selected coordinates in fibre g cannot
be a matching pair: for matching endpoints within that fibre, C is 1,
C-squared is 0 and T-transpose T is 1, so G is zero. These extra margin and
within-fibre statements do not assert that every individually allowed column
belongs to a full factor. Pairwise column caps remain separate requirements.

All cross matchings being identity is an assumption about this family. The
proof assumes no automorphism of a hypothetical target. It does not apply to
arbitrary P without another argument. Four finite enumerations supplied beside
this note are controls, not proof of universal coverage. They are deliberately
separate from the already registered local-core construction and pair-cap
claims. No novelty assertion is made.
