# Candidate kernel-invariance criteria and five prescribed Gram ranks

This is a new derivation awaiting independent review. It does not extend any
VERIFIED label by inheritance. The finite producer artifacts are frozen under
`acceleration/results/20260930_five_core_modular_gram`; all operations are over
the stated prime field. No factor for a99-vertex target was found.

Let C be a symmetric three-cell core with exactly one neighbor in each cell.
Write B=blockdiag(J_n,J_n,J_n) and G=nI-C-C^2+2J-B. Since CB=BC=J and
CJ=JC=3J, C commutes with G over the integers and every field. Consequently
N=kerG is C-invariant. For any field matrix F satisfying FF^T=G, its left
kernel L=ker(F^T) is a subspace of N. The equation FD=H is solvable columnwise
if and only if x^T H=0 for every x in L. D here is an arbitrary field matrix;
symmetry, diagonal, degree, binary-entry and quadratic conditions are absent.

Over GF(2), assume each cell indicator r_i satisfies r_i^T F=0, as follows
from the required integer column count2. Their three-dimensional span R lies
inside L. R is C-invariant because C r_i=j. If the induced action of C on
N/R is a scalar, every intermediate subspace R<=L<=N is C-invariant. For
x in L, both x^T F and (Cx)^T F vanish, so x^T H=0 for
H=2J-(I+C)F=(I+C)F. Hence some field D exists.

An immediately sufficient special case is rank(G)>=3n-4. The inequalities
rank(G)<=rank(F)<=3n-3 leave only L=R or L=N (including equality), both
C-invariant. This also follows because dim(N/R)<=1. This statement is broader
than the separately verified maximal-factor-rank lemma, whose hypothesis is
rank(F)=3n-3; it does not assume that hypothesis was forced by G.

The frozen five cases have the following producer-calculated exact ranks:

|Raw core|n|rank(G), GF2|rank(G), GF3|Known rank(F), GF2/GF3|
|---|---:|---:|---:|---|
|connected_00|12|22|27|Unavailable|
|connected_01|12|24|29|Unavailable|
|connected_02|12|24|29|Unavailable|
|connected_03|12|26|29|Unavailable|
|known243|20|30|27|57 /47|

Every rank has full invertible row operations, transformation, RREF and kernel
basis saved for separate checking. The first four factor-rank upper bounds are
33 overGF2 and34 overGF3. None of these Gram ranks alone reaches its upper
bound. All five GF2 quotient actions are nonscalar, so neither new sufficient
test closes the binary compatibility route for these cores. Failure of those
tests does not prove an incompatible factor exists.

There is a separate useful GF3 corollary for three of the recorded n=12 cores.
Let R be the span of r_0-r_2 and r_1-r_2. Column count2 gives R<=L; also
C kills R. The producer certificates for connected_01,02,03 give a zero
induced action of C on N/R. Thus C-invariance holds for every L between R
and N. Exact row count10 gives F j=10j=j overGF3, so x in L additionally
satisfies x^T j=0. Therefore
x^T H=2(x^T j)j^T-x^T F-(Cx)^T F=0, and every putative factor of one of
these three fixed cores has a solution to FD=H overGF3. The zero quotient
action is a finite computed premise pending independent checking. The
connected_00 action is nonscalar and the known243 row count18 vanishes mod3;
neither is covered by this particular corollary.

These conclusions concern only modular linear compatibility. They do not
produce a symmetric or binary residual graph, and they impose no target
automorphism. The four selected P=I domains are deliberate restrictions. The
243-vertex graph is a known positive fixture. No all3,580-core census, novelty,
target exclusion or general construction is claimed.
