# Identity permutation constructs a cap-compatible triangle core

Candidate corollary, pending independent review.

For every positive even integer n and every three perfect matching matrices
M0, M1, M2 of order n, construct the named triangle and three n-vertex fibres
described by C-TRIANGLE-CORE-PERMUTATION-PAIR-CAP-REDUCTION revision 1. Set all
three cross-fibre permutation matrices equal to the identity, including P=I.
Then every distinct vertex pair of the resulting graph H satisfies
H[x,y] + (H squared)[x,y] <= 2.

Proof from the independently audited reduction: the unary restriction only
forbids P(i)=M0(i) at specified indices. Since P(i)=i and a perfect matching
has M0(i)!=i, none is violated. The other restriction forbids the conjunction
P(M1(b))=b and P(b)=M2(b). Its first equality would require M1(b)=b,
contradicting a perfect matching. Thus both necessary and sufficient rules
hold for every choice of the matchings.

Direct matrix check gives the same conclusion: the three cross-fibre cap
blocks become 2I+M0+M1, 2I+M0+M2, and 2I+M1+M2. Their diagonals equal 2
and each off-diagonal entry is at most 2. The other pair types are bounded
by the previously derived literal-neighborhood calculation.

This is a universal construction of local positive graphs, not an SRG
construction. At n=12 each graph has 39 vertices; the remaining 60 vertices
and their edges are not supplied. In particular, positive-core pair caps
alone cannot exclude any choice of M1,M2 when P is free. The identity choice
is not asserted without loss of generality in a target graph. No target
automorphism or target-wide coverage statement is assumed.

The accompanying run checks raw graphs for the 3,580 independently
classified matching-pair representatives and small controls. These are
implementation checks; the displayed argument establishes the universal
candidate statement. Its independent reviewer must be different from this
corollary's author.
