# Independent written check: focal-neighbor matching necessity

Discovery producer: Root. Written verifier: Structural. Subject: the complete
five-item theorem in
`docs/CANDIDATE_20261004_FOCAL_NEIGHBOR_MATCHING_NECESSITY_V1.md`, SHA256
`30be5b396aadf848e73ad24ae3c49a9a2734d9b62944f756d057a95843b57858`.
The original paper is unchanged. This review uses no mathematical program,
matrix census, solver, native command, formal verification or external review.
Root's proposed proof is shared source material; the argument and rook examples
below were independently reconstructed. No novelty is claimed.

Verdict: the five mathematical items are correct. The printed encoding is a
necessary relaxation, with two interface qualifications below. It is not a
proved complete encoding of all supplied pair-bit restrictions or of the full
local/common-neighbor completion problem. These qualifications do not refute
the five-item theorem or the valid UNSAT implication for a necessary relaxation.

## Complete proof

Let G be finite and simple, k-regular, with one common neighbor on every edge
and two on every distinct nonedge. Let S be an induced support, x outside S,
T=N(x) intersect S independent, W=N(x) minus S, s=|T|, and
U_w=N(w) intersect S for w outside S. We reason about distinctly labelled actual
vertices, not type classes or an equitable partition.

For y in N(x), its degree in the induced neighborhood G[N(x)] is exactly
|N(y) intersect N(x)|=1, because xy is an edge. Hence the neighborhood is a
finite1-regular simple graph: every component is a single edge. This also
proves k is even whenever a focal vertex exists (including the vacuous k=0
case). There is no numerical spectral or isomorphism premise.

Because T is independent, no matching edge of G[N(x)] has both endpoints in T.
Each u in T therefore has exactly one partner p(u) in W. The function p is
injective: otherwise one chosen partner would have two neighbors inside N(x).
For any w in W, its neighbors in T are precisely T intersect U_w, so this
intersection has size at most one. If it has size one, w is the corresponding
p(u). Thus the set P of these vertices is exactly p(T), has s elements, and
each w in P already uses its unique neighborhood edge to its support partner.
It has no W-neighbor. This establishes items1 and2, including both existence
and uniqueness for each u.

The remaining vertices R=W minus P have no neighborhood partner in T or P.
Their unique partners lie in R. Consequently G[R] is a perfect matching,
all other W-edges are absent, and |R|=|W|-|P|=(k-s)-s=k-2s is nonnegative and
even. In particular s<=k/2. The empty matching when R is empty is included.
This proves item3.

For distinct w,z in W, x is already a common neighbor and is outside S.
Every element of U_w intersect U_z supplies a different additional common
neighbor. If that intersection has at least two elements, w,z have at least
three common neighbors, contradicting either prescribed value1 or2. If it
has one, their two known common neighbors preclude adjacency, since an edge
has exactly one common neighbor. Thus every adjacent pair of selected W
vertices, necessarily a matching edge in R, has disjoint support types.
This proves every part of item4. No bound is asserted on the eventual unknown
common neighbors of a disjoint nonmatched pair.

Two distinctly labelled selected W vertices of equal type U with |U|>=2
have support intersection of size at least two, which was just excluded.
Their type can therefore occur at most once in W. This is a focal selection
bound only: it is not a global assertion that the exterior count n_U<=1.
Empty and singleton types are deliberately outside this unit bound. Item5
follows independently of copy exchangeability.

## Selector/matching contract and the precise local sufficiency

The focal incidence equation can also be obtained without a block-code import.
For u in S, the common neighbors of x,u in S number (H t)_u. The common
neighbors outside S are exactly the selected W vertices whose type contains u.
Hence their sum is b_u=2-t_u-(H t)_u. For u in T, independence makes (H t)_u=0,
so b_u=1. Together with the degree |W|=k-s and the prohibition of selected
types having |T intersect U|>=2, this ensures exactly one selected partner
for each support vertex in T.

For a fully specified local matching predicate, take q on labelled copies
other than x, and unordered m variables only on pairs of selected R-candidates
with disjoint types and permitted adjacency. Require m=>q at both endpoints,
at most one m per endpoint and q_R=>at least one m. Set every other W-pair
edge to zero. P vertices have their one support partner and no W-edge;
R vertices have their one m partner. These clauses are necessary for an
actual focal neighborhood and sufficient to construct a1-regular induced
neighborhood on exactly the selected T union W. They prove nothing about
simultaneously constructing all other exterior rows or completing all graph
common-neighbor equalities.

There are two explicit qualifications to the frozen paper's encoding paragraph:

1. The selected-copy prohibition |T intersect U_w|>=2 must be explicit, or
   must follow from a certified focal adjacency-bit predicate containing the
   CN<=1 condition. The generic phrase "necessary bits" alone need not provide
   that implication: a weak necessary bit set {0,1} may retain a forbidden
   adjacency. The already accepted fixed17 pair predicate includes CN caps;
   this review does not import its implementation or certify a new one.
2. To express all supplied pair restrictions faithfully, a selected pair with
   allowed mask0 must be prohibited, including Gram-only incompatible pairs
   whose support intersection is0 or1. The frozen paragraph explicitly
   prohibits overlap>=2 and handles adjacency-only pairs, but does not state
   the additional mask0 simultaneous-selection clause. Missing that clause
   weakens the relaxation. An actual target still satisfies the clauses stated,
   so this omission does not turn a sound necessary-relaxation UNSAT result
   into a false exclusion. It does prevent claiming exact enforcement of every
   supplied bit restriction from the paragraph alone.

For a permitted set {0}, the existing matching-edge eligibility forbids m;
for {1}, selected endpoints must have m or be jointly excluded; for {0,1},
either choice may remain. For mask0, neither choice is permitted, so joint
selection must be excluded. At the copy level x itself must always be omitted.
No per-type uniform neighbor profile is required for this semantics.

## Hand examples and attempted falsifications

The nine-vertex rook graph has vertices (r,c), r,c in{0,1,2}, adjacent when
they share a row or a column. Each has degree4. An adjacent pair has exactly
the third vertex of its row/column as common neighbor. A nonadjacent pair has
exactly the two opposite corners of its rectangle. This directly verifies the
lambda1/mu2 premise; no external graph catalogue is used.

For x=(0,0) and the four-corner support
S={(1,1),(1,2),(2,1),(2,2)}, T is empty and W=(01,02,10,20).
The selected support types in that order are
{11,21}, {12,22}, {11,12}, {21,22}. The two matching edges are01--02
and10--20; their types are disjoint. Each of the four row-column cross pairs
has support overlap1 and is nonadjacent. All four types have size2 and are
distinct. Against every support coordinate the sum of selected incidences
is2, agreeing with b=2 and degree4.

Remove matching edge01--02 without changing q: the incidence sums still pass,
but its two endpoints lack a matching partner, violating q_R=>one incident m.
Replace the two matching edges by01--10 and02--20: every selected vertex
still has one neighborhood partner, but both proposed edges have one common
support vertex in addition to x and violate adjacent CN1. This is a paper
corruption control for the disjoint-type matching-edge restriction.

A corrupted supplied-mask control makes the cross pair01,10 have mask0 while
keeping the other rook data. The usual two matching edges, q and incidence
sums still satisfy the printed matching clauses and overlap>=2 exclusions.
They do not satisfy that new supplied mask0 restriction. This tests exact
encoding semantics only: the corrupted mask is not claimed a necessary bit
set for the rook graph, nor a counterexample to the five-item theorem.

With S={11}, T is empty. Selected vertices01 and10 both have the singleton
type {11}; selected vertices02 and20 both have the empty type. The same two
matching edges remain. This falsifies a stronger cap of one for empty or
singleton types while validating the actual size>=2 qualification.

With S={01}, T={01}, P={02}, R={10,20}; the P vertex's support partner is01
and the R matching is10--20. With S={01,10}, T is independent, P={02,20}
and R is empty. These verify s=1 and maximal s=2 with the empty matching.
In contrast, S={01,02} gives a nonindependent T. Those two T vertices match
each other, P is empty and R={10,20}. Applying |P|=s or |R|=k-2s there is
wrong: this is a direct falsifier of dropping the independence hypothesis.

Twenty written boundaries checked: local degree1; integer/even count;
independence; injective T partners; P isolation; R matching; empty R;
support-overlap>=2 exclusion; overlap1 nonadjacency; disjoint matched types;
equal-type size>=2; empty/singleton repeat; four-corner rook premise and rows;
deleted matching control; overlapping replacement matching; corrupted mask0;
focal CN-bit qualification; self-copy omission; no equitable/automorphism
premise; and local versus full-completion sufficiency.

No executable encoding, floating solver output, actual fixed17 focal result,
runtime gate, formula equivalence, UNSAT proof, graph completion or Conway99
resolution is approved by this written review. The claim is outside the frozen
eighteen V22 descriptor and current400 ledger.
