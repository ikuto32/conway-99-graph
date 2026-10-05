# Exact Boolean-box Gram cuts

This is a distinct, more general conditional cut rule than the complete
nonzero-support rule in `DERIVATION_20260930_TARGET_GRAM_NOGOODS.md`.
It has no unrestricted existence or nonexistence conclusion.

Let a symmetric binary zero-diagonal adjacency matrix of order99 satisfy
`A²=12I-A+2J`. The previously derived identity `G²=63G`, for
`G=27I-9A+J`, implies `xᵀGx=||Gx||²/63≥0`. Every principal matrix is
positive semidefinite by extending its vector by zeros.

Fix a principal vertex set, its constant edges, a distinct Boolean variable
`t_e` for each remaining unordered pair, and an exact integer vector `w`.
The principal quadratic is affine in those edge variables:

`q(t)=c+Σ_e d_e t_e`, where `d_{uv}=-18 w_u w_v`.

For any subset `F` of variables with prescribed values `a_e∈{0,1}`, define

`U(F,a)=c+Σ_{e∈F}d_e a_e+Σ_{e∉F}max(0,d_e)`.

For every Boolean assignment preserving `F`, each free term is at most
`max(0,d_e)`, so its quadratic is at most `U(F,a)`. Equality is attained
over this Boolean box by assigning each free variable1 when its coefficient
is positive and0 when it is negative; zero coefficients permit either value.
Thus this is an exact maximum over the box. Local degree/common-neighbor
constraints may restrict the actual graph assignments, but restricting the
box cannot increase the maximum.

If the verified box maximum is **strictly negative**, this rule certifies
that every target extension must change at least one value in `F`.
The valid target-extension clause is the disjunction of these changes:
positive variable `t_e` for `a_e=0`, negative literal `¬t_e` for `a_e=1`.
A zero upper bound supplies no contradiction. This sufficient test is not
asserted to recognize all valid cuts.

All coefficients must be included in the maximization: omitted nonzero
coefficients cannot silently be held fixed. Edges outside the principal
vertex set do not affect this quadratic. An empty `F` with negative `U`
would exclude this entire fixed-edge family; that special case requires its
own exact certificate and is not asserted by the current21literal example.

The old complete-support rule is the special case fixing every nonzero
coefficient. A box cut can be a strict literal subset of its parent support
clause, excluding a larger pattern family. The exact certificate must be
rechecked after this change; the parent audit alone does not verify it.

The independent checker constructs the maximizing corner as a raw59vertex
adjacency matrix and evaluates its full ordered integer quadratic. It also
checks the separate coefficient sum and the parent-value-plus-gains sum,
all780edge mappings, and complete nonzero/zero-coefficient coverage. The
maximizing corner need not satisfy local graph constraints; no such claim
is made or needed. Calibrations exhaust all1,728 three-bit coefficient,
fixed-mask and prescribed-value cases and reject malformed certificates.
