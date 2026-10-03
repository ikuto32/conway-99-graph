# Independent C4-count triangle-kernel endpoint implication

Prepared 2026-10-02 UTC by /root, before inspecting any new endpoint output.
Let B denote all231 actual triangles of a hypothetical target, and
C=ker(B transpose) over GF(2), M=|C|, Aw its weight counts, A0=1.
The independently reviewed interval65d8 restricts nonzero weights to
36,38,...,60. No nontrivial automorphism or nonzero kernel is assumed.

The independent image audits626e and75bf give L3=231,L4=2079,L5=22869,
L6=24486 and Lj=0 elsewhere. The stronger fifth count uses the universal
at-most-two inverse plus induced-C4 injection, not an assumed rook absence.
For every j, character orthogonality gives sum Aw Kj(w)=M Dj, with Dj>=Lj.
Consequently sum over nonzero w of Aw*(Lj-Kj(w)) <= binom(99,j)-Lj.
The zero word supplies the binomial constant; every denominator is positive.

Write Gj(w)=(Lj-Kj(w))/(binom(99,j)-Lj).
Any complete y>=0 with sum yj Gj(w)>=1 at all13 permitted nonzero weights
therefore proves M-1<=sum yj and M<=1+sum yj.
A candidate chooses nonzero entries at degrees4/5 using endpoint weights36/60.
Its unnormalized matrix is [-3465,30429;3543,6909], determinant -131749632.
Exact Gaussian elimination gives z4=23520/131749632,z5=7008/131749632.
These are multiplied by the respective denominators3762297 and71500275.

These endpoint equations alone do not prove feasibility: all13 inequalities
must be independently checked after output. If they pass and the complete
exact dual sums to U12187808/2723, then U<8192=2^13.
M is a power of two, so dim C<=12 and rank B>=87.
No rank upper bound, forced kernel vector, contradiction or target resolution follows.

Verification uses product polynomial convolution and rational Gaussian
elimination independently of the producer's binomial sum and closed inversion.
Prior proof dependencies and shared exact runtime/arithmetic are explicit.
External review and novelty: null, neither established.

