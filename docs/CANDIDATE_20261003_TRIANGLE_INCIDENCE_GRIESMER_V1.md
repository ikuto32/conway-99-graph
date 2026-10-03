# Candidate lower bound for binary triangle-incidence rank

Status: **CANDIDATE**, pending independent written derivation and controls.
This note proposes only a necessary consequence conditional on existence of an
unrestricted `srg(99,14,1,2)`. It is not an existence result, a nonexistence proof,
or a replacement for the refuted generic codomain-isotropy upper-bound argument.
No automorphism of the graph is assumed.

## Precise statement

For every simple graph with symmetric binary zero-diagonal adjacency matrix
`A` satisfying `A^2=12I-A+2J`, let `B` be its binary vertex/triangle incidence
matrix, with one column for every unlabelled triangle. Then

`rank_GF(2)(B) >= 67`.

Equivalently, its length-99 binary linear code `ker(B^T)` has dimension at most
32. No upper bound of 72 is asserted; the actual rank remains undetermined.

## Archived overlap and provenance

The pinned historical repository is
`https://github.com/YesterdaysLemon/conway-99-research`, commit
`85e705cc6c2a14d123120c93a847e30aaab1789e`. Its
`attempts/wave102-prism-incidence-code/derivation.md`, section 1, already records
the same nonzero kernel-word weight set `36,38,...,60`, obtained from restricted
spectral bounds, and the weaker displayed rank interval `45..99`.
Its file labels the argument DERIVED and requires independent verification.
No archived claim ID for this exact weight statement was found in the examined
historical `CLAIMS.yaml`; the immutable repository/commit/path/section identify
the source instead. This is not a fresh verification or novelty claim.

The incidence and Cauchy derivation below was proposed independently in the
current research conversation before this overlap was located. The additional
candidate step is the elementary binary Griesmer consequence, not the already
archived weight interval. The failed generic rank-upper argument and its checked
synthetic counterexample remain separate preserved artifacts.

## Exact incidence derivation

The target identity forces degree 14 and adjacent/nonadjacent common-neighbor
counts 1 and 2. Every edge therefore belongs to exactly one triangle. Each
vertex belongs to seven triangles, and the graph has `99*14/6=231` triangles.
Different triangles through one vertex have disjoint other vertices, since
otherwise their shared edge would belong to two triangles.

Take a nonzero vector `x` of `ker(B^T)` and put `S=supp(x)`, `s=|S|`.
Every triangle meets `S` in zero or two vertices. At each vertex in `S`, exactly
one of the other vertices of each of its seven triangles is in `S`. Thus
`G[S]` is 7-regular, `s` is even by the handshake identity, and `s<99`.
For `v` outside `S`, put `r_v=|N(v) intersect S|`. These integers are even, but
the following Cauchy step does not require their parity.

The cut has exactly `7s` edges, so `sum_out r_v=7s`. With ordinary integer
arithmetic, `x^T A x=7s` and

`x^T A^2 x = 12s-7s+2s^2 = 5s+2s^2`.

The contribution of vertices in `S` to this squared norm is `49s`. Consequently

`sum_out r_v^2 = 2s^2-44s = 2s(s-22)`.

Cauchy on the `99-s` outside coordinates gives

`(7s)^2 <= (99-s)*2s(s-22)`.

Since `s>0`, this is exactly

`(s-36)*(2s-121) <= 0`.

Hence `36<=s<=121/2`. Because `s` is even, every nonzero codeword has weight
in `{36,38,...,60}`. All manipulations are exact, and no numerical relaxation
or existence of a particular codeword is needed. If the kernel is zero, its
dimension bound already holds.

## Self-contained binary Griesmer argument

Let a nonzero binary linear code have length `n`, dimension `t`, and actual
minimum nonzero weight `d`. Choose a minimum-weight word `w`, and project the
code onto the complement of its support, a coordinate set of size `n-d`.
The kernel of this projection is exactly `{0,w}`: another nonzero word supported
inside that size-`d` support would need at least `d` ones, and hence would equal
`w`. The projected code has dimension `t-1`.

For a nonzero projected word, choose a preimage `z`. If `z` has `a` ones in
`supp(w)` and `b` ones outside, then `z+w` has `d-a` ones inside and the same
`b` outside. Both preimages are nonzero, so their weights are at least `d`.
Since `min(a,d-a)<=floor(d/2)`, it follows that `b>=ceil(d/2)`.

Induct on dimension, using this projection and
`ceil(ceil(d/2)/2^i)=ceil(d/2^(i+1))`. The base case of dimension one has
`n>=d`. Thus every such binary code satisfies

`n >= sum_{i=0}^{t-1} ceil(d/2^i)`.

For the incidence kernel, `d>=36`. Dimension at least 33 would require

`n >= 36+18+9+5+3+2+27*1 = 100`,

contradicting `n=99`. Therefore `dim ker(B^T)<=32`, and rank-nullity gives
`rank_GF(2)(B)>=99-32=67`.

## Literature access and verification limits

The coding inequality is classical: J. H. Griesmer, *A Bound for Error-Correcting
Codes*, IBM Journal of Research and Development 4(5), 532–542 (1960), DOI
`10.1147/rd.45.0532`. On 2026-10-03 JST, the original paper scan at
[Bitsavers mirror](https://bitsavers.trailing-edge.com/pdf/ibm/IBM_Journal_of_Research_and_Development/045/ibmrd0405M.pdf)
was read through its Section 2 recurrence and ensuing bound (Theorems 1–2).
The main `www.bitsavers.org` URL returned HTTP403 and the DOI fetch was
unavailable; those failed accesses do not refute the theorem. No contemporary
Conway-99 literature-status search or novelty audit was performed in this step.

The proof above is supplied in full so its validity does not depend on OCR or
access to that scan. It remains a discovery argument until a separate reviewer
checks the exact quantifiers, incidence reduction, integer moments, residual-code
proof and rank-nullity conclusion. Recommended calibrated controls are the
known-valid 3x3 rook graph's complete binary triangle kernel, altered incidence
columns, a general binary code with no triangle-incidence semantics, and a
deliberately invalid puncturing choice that is not a minimum-weight codeword.
No numerical code-feasibility LP, code enumeration or new rank calculation has
been launched by this note.
