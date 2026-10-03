# A connected small subcubic ternary support cannot be realized

Producer: /root. Frozen version timestamp 2026-10-03T04:46:08+00:00.
Status: CANDIDATE pending separate written verification. No execution or
adjacency realization is asserted.

## Exact conditional necessary restriction

For every symmetric binary zero-diagonal 99-by-99 matrix A whose integer
rows have exactly14 ones, define D=A^2-12I+A-2J and M=D modulo3. Let H be
the simple graph of its nonzero unordered off-diagonal entries, and discard
isolated vertices. If H is nonempty and connected, then it cannot simultaneously
have at most12 vertices and maximum degree at most3.

This statement is a necessary restriction on the residual support. It does
not assume that A is connected, that A has any automorphism or lambda1,
or that the support H is an induced subgraph of A. It makes no claim about
disconnected supports, supports larger than12 or vertices of support degree4.
No target existence or nonexistence conclusion follows.

## Exact derivation

The diagonal of D is14-12-2=0; every full row sum is196-12+14-198=0.
For a distinct pair put r_uv=(A^2)_uv+A_uv-2. Then r_uv>=-2. If M_uv=0,
the integer residual is a multiple of3 and therefore nonnegative. Every
nonisolated support vertex has degree at least2. At support degree2 the two
nonzero residues are opposite, and at degree3 all three agree.

Since A is symmetric14-regular, AJ=JA=14J, so AD=DA and AM=MA. Write S for
the m nonisolated support vertices. For each z outside S, the z-row of M is
zero, and commutation gives x*M_S,S=0 over GF(3), where x_u=A_zu is binary.

At any support vertex j of degree2, the column equation is s*x_u-s*x_v=0,
so its two support-neighbor coordinates are equal as integers. At degree3
the equation is s*(x_u+x_v+x_w)=0. A sum of three binary integers divisible
by3 is either0 or3; hence all three neighbor coordinates agree. Thus, for
each outside z, the coordinates x are constant along every even-length walk
in H. In a connected graph these even-walk classes are precisely its two
bipartition classes if bipartite, and a single class otherwise. To see the
latter, a path to an odd cycle, that odd cycle, and a return path produce an
odd closed walk; it can change the parity of any connecting walk. No graph
automorphism is used in this propagation.

Consequently, two vertices in the same even-walk class have identical
outside neighborhoods. Every support vertex has at least14-(m-1)=15-m
outside neighbors. Any such pair has at least15-m common neighbors, giving
r_uv>=13-m, without fixing any adjacency inside S.

If H is not bipartite, every support vertex has the same outside neighborhood.
For m<=12, every support-pair residual is at least13-m>=1. At least two of
these positive residuals occur in every nonisolated support row, and every
good residual is nonnegative. Its integer row sum is positive, contradicting0.

If H is bipartite, let P be its larger bipartition class, with p>=ceil(m/2).
Minimum degree2 and simplicity force m>=4. Choose any u in P. The p-1 other
vertices of P are all good pairs with u and have identical outside neighborhoods.
Their residuals are multiples of3 at least13-m. Let k be the smallest multiple
of3 at least13-m. The at most3 bad residuals in row u have total at least-6;
every other good residual is nonnegative. Its complete row sum is at least

 (p-1)*k-6 >= (ceil(m/2)-1)*k-6.

The exact lower bounds for every possible m are:

| m | k | (ceil(m/2)-1)*k-6 |
| --- | --- | --- |
| 4 | 9 | 3 |
| 5 | 9 | 12 |
| 6 | 9 | 12 |
| 7 | 6 | 12 |
| 8 | 6 | 12 |
| 9 | 6 | 18 |
| 10 | 3 | 6 |
| 11 | 3 | 9 |
| 12 | 3 | 9 |

Every lower bound is strictly positive, again contradicting the exact row sum0.
Both connected cases are excluded, proving the stated restriction.

## Verification boundaries and limitations

Reconstruct both row arithmetic and field sign rules independently. Challenge
the outside commutator equation, binary sum inference at degree3, even-walk
classification including an odd closed walk, common-neighbor bound despite
arbitrary internal adjacency, bipartition size and all nine exact table rows.

The binary inference would fail for arbitrary integer adjacency entries; the
degree3 inference cannot be reused at degree4. If H is disconnected, outside
neighborhoods cannot simply be counted relative to one component: the argument
uses the full nonisolated set S. If m>=13 the stated strict bound fails. These
boundaries are left open, not declared impossible.

This proof reproduces its elementary identities and has no prior mathematical
claim dependency. It unifies some support shapes discussed in the separate
small-support, four-defect and six-defect papers, without revising their bytes
or asserting that their whole statements follow from this restriction alone.
All proposed controls are written checks. Executed fixture count is0. Formal
proof, external review, novelty and realization of remaining supports are unknown.
Overall search coverage: UNKNOWN; no validated denominator.
