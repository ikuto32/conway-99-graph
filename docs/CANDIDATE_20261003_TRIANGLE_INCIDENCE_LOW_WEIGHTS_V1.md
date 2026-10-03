# Candidate exact low-weight triangle-image bounds

Discovery question: `/root`; collision derivation and finite controls:
`/root/structural`. Status: **CANDIDATE**, pending a separate complete written
audit. This is a conditional mathematical implication, with no target graph,
general nonexistence proof, incidence-rank upper bound, optimizer run, novelty
claim or external review. The finite controls do not prove the universal claim.

## Precise statement and assumptions

Let G be any finite simple graph in which each edge has exactly one common
neighbor. Let T be the set of **all actual graph triangles**, let m=|T|, and
let t_v count the triangles containing vertex v. Let B be its binary
vertex-by-triangle incidence matrix and D=im_GF(2)(B). Then D contains at least

* m distinct words of weight3;
* Q=sum_v binom(t_v,2) distinct words of weight4;
* binom(m,2)-Q distinct words of weight6.

These are lower bounds: sums of three or more triangles may produce additional
words of the same weights. They do not assert that all words of these weights
have one of the described representations.

For every99x99 binary symmetric zero-diagonal A satisfying
`A^2=12I-A+2J` over the integers, the diagonal and off-diagonal entries give
degree14 and one common neighbor on every edge. Its693 edges are partitioned
into231 triangles, with seven triangles at each vertex. The preceding statement
therefore gives `(N_3,N_4,N_6)=(231,2079,24486)`, since
`99*binom(7,2)=2079` and `binom(231,2)-2079=24486`.

The statement concerns every hypothetical target with these exact parameters.
There is no target automorphism, prism absence, fixed local configuration,
uniform rooted profile or previously rejected generic rank lemma assumption.

## Meeting triangle pairs: the collision argument

Distinct triangles cannot share an edge: its two distinct triangle completion
vertices would be two common neighbors of that edge. Thus triangle intersection
has size0 or1. An unordered meeting pair has the form `{v,a,b}`, `{v,c,d}`, with
four distinct vertices a,b,c,d. Its binary sum has support S={a,b,c,d}.

The edges ab and cd occur. No cross edge between {a,b} and {c,d} can occur,
because together with v it would give a triangle using an edge incident to v
already completed by its original triangle. Hence G[S] is exactly two disjoint
edges. From S recover this unique pair of induced edges. The unique common
neighbor of each recovered edge is v. This recovers both original triangles,
so two different meeting pairs cannot give the same weight4 word.

Every meeting pair has a unique intersection vertex; the total number of these
unordered pairs is therefore Q. Linearity of an arbitrary triple system alone
would not suffice: the preserved Pasch control has four linear triples whose
two different meeting pairs have the same sum. Its point graph has additional
triangles and violates the edge-unique-triangle hypothesis.

## Disjoint triangle pairs: the collision argument

For an unordered disjoint pair T1,T2, its binary sum is the characteristic
vector of S=T1 union T2, of size6. The only graph triangles contained in S are
T1 and T2. Indeed a different triangle would use vertices from both parts;
among its three vertices two lie in one part and their edge already has the
unique completion inside that original triangle. This contradicts a different
completion in the other part.

Consequently S recovers its two graph triangles and the original unordered
pair. The map from disjoint triangle pairs to weight6 words is injective.
All unordered distinct triangle pairs are either meeting or disjoint, giving
the count binom(m,2)-Q. A complete-six-vertex control preserves an explicit
collision when the edge-unique-triangle hypothesis is dropped.

## Exact character inequality and constant convention

Let C=ker_GF(2)(B^T). Under the ordinary binary dot product,
`C^perp=im_GF(2)(B)=D`: inclusion is immediate, and equality follows from
rank-nullity. Define A_w as the number of C words of weight w, A_0=1,
M=|C|=1+sum_(w>0) A_w, and

`K_j(w)=sum_s (-1)^s binom(w,s) binom(n-w,j-s)`.

For a fixed u, its character sum over C is M if u is in C^perp and zero
otherwise, by pairing x with x+x0 when u dot x0=1. Summing these characters
over all u of weight j gives exactly

`sum_(w>=0) A_w K_j(w) = M * |{u in D:wt(u)=j}|`.

If the above lower count is N_j, the **nonzero-weight** inequality is therefore

`sum_(w>0) A_w K_j(w) >= N_j*M-K_j(0)`.

Equivalently, substituting M=1+sum_(w>0) A_w,

`sum_(w>0) A_w*(N_j-K_j(w)) <= K_j(0)-N_j`.

For the target at j=3,4,6 the denominator K_j(0)-N_j is strictly positive,
so an LP row with right side1 is

`sum_(w>0) A_w*(N_j-K_j(w))/(K_j(0)-N_j) <= 1`.

The initial question's `(N_j-K_j(0))*M` right side for the nonzero sum is a
weaker valid consequence when M>=1; it omits the sharper constant convention.
It is preserved here as the initial proposal, not used for the normalized row.
These inequalities use the same exact character orthogonality as the previously
audited generic code bound; the new graph-specific information is N_j only.

For a hypothetical target, the independently derived nonzero kernel weights
are the even integers36..60 (the written ROOT Griesmer audit). That existing
weight premise can restrict the rows above. The already established rank>=76
bound, its numerical guide and its generic-code dual certificate are not
premises of this derivation. No new rank consequence has been computed here.

## Finite falsification protocol and limits

The separate new standard-library-only controls source enumerates every actual
triangle and unordered triangle pair on five frozen small literal graphs:
one triangle, two disjoint triangles, a three-triangle friendship graph,
a four-triangle loose cycle, and rook9. It checks every generated pair support,
its inverse, all binary incidence-image/kernel words, literal orthogonality,
all character degrees, and the sharp shifted constants. Rook9 is also checked
against its known exact integer SRG parameters(9,4,1,2).

Deliberate matrix corruption, an overstated dual count, a missing A_0 constant,
the linear Pasch configuration and K6 test the hypotheses/collision gaps.
No known243graph or99graph is enumerated, no floating point or LP solver is
imported, and no new scientific graph search is performed. All finite raw
graphs, pair supports, full image/kernel words, collision witnesses, exact
character counts and dependency hashes are saved in the run directory.

The predeclared contained allocation is90seconds outer,60seconds worker,
20seconds internal serialization reserve and10seconds outer cleanup guard,
based on at most512 ambient words and six triangle generators per positive
fixture. A timeout or failed control leaves the universal claim unverified.
Required next verification: a different author must review both recovery
arguments and constant conventions and independently inspect raw collision
and complete-code controls. This note/source does not approve itself.

## Pinned context and provenance

* `acceleration/audit_20261003_incidence_griesmer_v1.md`, SHA256
  `65d8eea3f4d72eb56391284f95eb43ad021e92a88a41fdcc2fe7a2e10f9dd92d`,
  supplies the independently derived target kernel-weight36..60 context.
* `acceleration/audit_20261003_incidence_code_dual_v1.md`, SHA256
  `9fd1522fc60cc001c57e03559ac77582fecee9be75f556a702226a0503376a67`,
  supplies the previously checked character convention. The new control source
  imports neither code implementation.
* The pinned archive `external_conway99_research/attempts/wave102-prism-incidence-code/derivation.md`
  discusses the triangle image/kernel and weight interval. A bounded local text
  search on2026-10-03 JST of that directory and both claim ledgers for the
  numbers2079/24486 and low-weight/Krawtchouk terms did not identify these exact
  pair-count statements. This is provenance only; novelty and global literature
  coverage remain UNKNOWN. Historical verification labels are not transferred.

All source/control outputs remain candidate evidence until separate checking.
Claim-ledger mutation, mathematical promotion and execution of a new LP are
outside this protocol.
