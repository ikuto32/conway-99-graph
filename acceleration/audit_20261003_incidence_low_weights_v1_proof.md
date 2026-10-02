# Independent triangle-image low-weight and character derivation V1

Scope: let G be any finite simple graph whose every edge has exactly one
common neighbor. Let its actual complete triangle set have size m; let t_v
be each vertex's triangle incidence count. Let B be binary vertex/triangle
incidence, D=im(B) over GF2, C=ker(B^T), and M=|C|. This written derivation
is independent of discovery source execution; finite fixtures only test it.
No target graph, novelty, rank consequence or nonexistence is asserted.

Each edge has exactly one triangle completion. Thus distinct actual triangles
intersect in at most one vertex and their binary incidence columns are
distinct weight3 words. There are at least m such words in D.

A meeting pair {v,a,b},{v,c,d} has four distinct remaining vertices and
binary sum supported on S={a,b,c,d}. Edges ab and cd exist. If any cross
edge joins those two pairs, one of va,vb already completed by its original
triangle gains a second completion using the other pair, contradicting the
hypothesis. Therefore the graph induced on S consists of precisely the
two disjoint edges ab and cd. Recover these edges from S, then recover v
as each edge's unique common neighbor. The original unordered triangle pair
is thereby uniquely determined by its binary word. Meeting pairs have one
intersection vertex, so their number is Q=sum_v binom(t_v,2); all these Q
words are distinct of weight4.

A disjoint pair of triangles has a six-element union S, equal to its word
support. A different triangle inside S must mix the two parts and therefore
contain two vertices in one original triangle. Their edge already has its
unique completion in that original triangle. A vertex from the other part
cannot be a second completion. Hence exactly the original two triangles
are contained in S, recovering the pair uniquely. All disjoint pairs give
distinct weight6 words, in number binom(m,2)-Q. Additional sums of more
triangles may produce other words at those weights; these are lower bounds.

Linearity of source triples alone does not justify either recovery argument.
The Pasch four-line configuration gives duplicate weight4 pair sums despite
linear source incidences; its point graph fails unique edge completion.
K6 supplies ten distinct disjoint-triangle pairs with the same six-support
word and also fails unique edge completion. These counterexamples establish
the need for the stated graph hypothesis, not a target-specific exclusion.

For a target A, the diagonal of A²=12I-A+2J gives every degree14, and an
edge's off-diagonal entry gives exactly one common neighbor. The693 edges
are partitioned by231 actual triangles. Each vertex's14 incident edges
are paired by7 triangles. Thus Q=99*binom(7,2)=2079 and the disjoint count
binom(231,2)-2079=24486. The image therefore has at least231 weight3,
2079 weight4 and24486 weight6 words. There is no target automorphism or
prism/rank/profile premise in this derivation.

Under the nondegenerate binary dot product, im(B) lies in ker(B^T)^perp.
Both spaces have dimension rank(B) by rank-nullity, so they are equal.
For any u, sum_x∈C (-1)^(u·x) equals M if u∈D and0 otherwise: in the
second case choose x0∈C with u·x0=1 and pair x with x+x0. That involution
has no fixed points and cancels every summand.

For x of weight w, summing its character over all u of weight j yields
K_j(w), the coefficient of z^j in (1-z)^w(1+z)^(n-w). Therefore, writing
A_w for the kernel's weight multiplicities and A_0=1,
sum_w A_w K_j(w)=M*|D_j|. If |D_j|>=N_j, remove exactly the zero-word
term K_j(0)=binom(n,j), obtaining
sum_w>0 A_w K_j(w)>=N_j*M-K_j(0).
Using M=1+sum_w>0 A_w, rearrange to
sum_w>0 A_w*(N_j-K_j(w))<=K_j(0)-N_j.
For target j3,4,6 the denominator on the right is strictly positive, giving
the normalized upper row with exact rational coefficients and RHS1.

The proposal's alternative (N_j-K_j(0))*M RHS is weaker but valid: the
strong RHS exceeds it by K_j(0)*(M-1)>=0. It is not the normalized sharp
constant convention. Missing A_0 is an actual mistake and is falsified by
the single-triangle finite character control.

All coefficients can be evaluated for every positive weight1..99; the
additional target kernel interval36..60 belongs to the separately pinned
Griesmer derivation and is not needed for these all-weight inequalities.
Using that interval in another LP must retain its own dependency. Exact
count bounds alone do not establish a new rank bound or optimum.

Independent finite checking constructs adjacency sets and support symmetric
differences, exhausts complete ambient/kernel/image words on five small
graphs, and evaluates characters through repeated integer polynomial
multiplication. It compares every saved raw support/inverse/word/histogram/
character inequality, plus complete Pasch/K6 collision records. Known rook9
and precise corruption controls calibrate this checking path; the universal
implications above are mathematical arguments rather than fixture agreement.
Trusted components: exact Python arithmetic/Fraction/JSON/SHA256 and the
shared invocation deadline/supported supervisor; no producer imports.
