# Independent written audit: six ternary defects in the degree14 domain

Discovery producer: ROOT. Independent verifier: Checkpoint.
The unchanged candidate is
`docs/CANDIDATE_20261003_TERNARY_SIX_DEFECT_NONREALIZABILITY_V1.md`,
SHA256 ae2e422fb1b45b5eaa98385d2ab829dc8c9c14958d005769d7cfddbec8594801.
This audit is a separate exact written derivation, with a complement-graph
classification instead of the producer's suppressed-path classification.
No mathematical program, fixture, solver or exhaustive computation was executed.
Written modular matrices are not adjacency realizations.

## Exact statement checked

For every 99-by-99 symmetric binary zero-diagonal matrix A with exactly 14 ones
in each integer row, put r_uv=(A^2)_uv+A_uv-2 for u<v and let F3 count all
unordered residuals not divisible by 3. Then F3 is not 6. This statement alone
does not exclude any other positive value or establish the existence or
nonexistence of the target; no remaining value is asserted realizable.

No earlier mathematical claim is a premise. The row identities, modular
support rules and complete six-edge classification are derived here. The prior
small-support and four-defect audits supply historical context only. There is
no lambda1, triangle incidence, fixed graph, numerical or automorphism premise.

## Reconstructed identities and binary outside-neighborhood lemma

Let D=A^2+A-12I-2J over the integers. Symmetry and binary degree14 give
(A^2)_uu=14, hence D_uu=0. For every u, sum_v(A^2)_uv=14*14=196.
The complete off-diagonal residual sum is therefore

 (196-14)+14-2*98=0.

Every off-diagonal r_uv is at least -2. If divisible by 3, it is nonnegative.
Since AJ=JA=14J, direct expansion yields AD=DA; hence AM=MA over GF(3),
where M is the reduction of D modulo 3.

Let H be the simple undirected graph of nonzero unordered entries of M, with
each edge labelled +1 or -1. A complete support row has sum zero in GF(3).
Every nonisolated vertex thus has degree at least two. At degree two, the two
labels are opposite. At degree three, all three labels agree: the possible
integer sign sums are -3,-1,1,3, of which only -3 and 3 vanish modulo 3.

Let S be the nonisolated support vertices. For any z outside S, its entire
M-row is zero, so the commutator equation states

 x M[S,S]=0, where x_u=A_zu for u in S.

Each x_u is binary. A congruence x_u=x_v modulo 3 is therefore equality of the
literal integers. If the column equations force this for all outside z, u and
v share every outside neighbor. Their degree14 then supplies at least
14-(|S|-1)=15-|S| common outside neighbors, with no restriction on internal
adjacency. Consequently r_uv>=13-|S|. If uv is not a support edge, round this
lower bound up to a multiple of 3.

For a support vertex u with d_H(u) bad pairs, its complete row has at most
2*d_H(u) available negative budget. Thus every collection of its good
residuals sums to at most 2*d_H(u). This row bound includes every other vertex;
an unlisted residual cannot be discarded if negative unless it is a bad pair.

## Independent complete six-edge classification

Assume H has six edges, and count only its nonisolated vertices. Minimum degree
two gives v<=6; simplicity gives v>=4. Each nontrivial connected component
needs at least three edges. A disconnected six-edge support must therefore
consist of two three-edge components, each a triangle. Odd degree-two sign
alternation rejects each triangle. Thus H is connected.

* If v=6, total degree12 and minimum degree two make it a connected
  2-regular graph: C6.
* If v=4, its six edges include every pair: K4.
* If v=5, the excess degree over the ten required by minimum degree two is
  exactly two. The only degree sequences are (4,2,2,2,2) and (3,3,2,2,2).
  In the first case, the degree-four center meets all four leaves. Each leaf
  needs exactly one additional incident edge, so the other two edges are a
  perfect matching of the leaves. This is the bowtie.

For the other five-vertex degree sequence, take Q=K5 minus H. Q has degrees
(1,1,2,2,2) and four edges. Every component of this simple maximum-degree-two
graph is a path or a cycle, with no isolated vertex. Its two degree-one
vertices are the endpoints of exactly one path. The only decompositions on
five vertices are P5 and P2 plus C3: a cycle needs at least three vertices, and
there are exactly two path endpoints. Thus no suppressed-path arrangement is
left unclassified.

If Q=P2 plus C3, H is K2,3. If Q=P5, label its path a,x,y,z,b. In H, a and b
have degree three and are adjacent, forcing every support edge at either
endpoint to have the same sign s. But y is adjacent to both a and b in H,
has support degree two, and now has incident labels s,s. Its row sum is
2s, nonzero. This directly rejects the shape whose suppressed path lengths
would be (1,2,3), without assuming that suppression preserves a simple graph.

The only surviving modular support shapes are C6, K2,3, bowtie and K4.

## All four realization contradictions

### C6

Name the cyclic vertices 1,...,6 and choose the first edge label s. All edge
labels alternate. The outside equations at columns 2,4,6 give x1=x3=x5,
and those at 1,3,5 give x2=x4=x6. Vertices 1 and 3 form a good pair and
have at least nine common outside neighbors. Hence r13>=7; being a multiple
of 3 gives r13>=9. Row 1 has only two bad pairs, so its good budget is at
most four and the individual good multiple-of-three r13 is at most three.
Contradiction. This holds for both choices of s.

### K2,3

Let a,b be the degree-three vertices and x,y,w the degree-two vertices.
Every edge at a has sign s. The degree-two rule makes every edge at b have
sign -s. Each leaf-column outside equation is s*x_a-s*x_b=0, forcing a,b
to be outside twins. With five support vertices they have at least ten common
outside neighbors. The good pair ab has r_ab>=8, hence r_ab>=9. Row a has
three bad pairs, giving at most six good budget. Contradiction.

### Bowtie

Write its triangles c,x,y and c,u,v. The leaf degree-two rules give labels
cx=cy=s, xy=-s and cu=cv=t, uv=-t. The center's row gives
2s+2t=0, so t=-s. At leaf columns x and y the outside equations give
x_c=x_y and x_c=x_x; at u and v they give x_c=x_v and x_c=x_u.
Thus every support vertex has the same outside neighbors. The pair x,u is
good and has at least ten common outside neighbors, so r_xu>=9 after rounding
to a multiple of 3. Row x has only two bad pairs and at most four good budget.
Contradiction, for either nonzero s. The argument explicitly covers this
degree-four support shape; it is not silently subsumed under a subcubic case.

### K4

Degree-three rules and each shared edge force all six support labels to equal
one nonzero s. Thus M[S,S]=s*(J4-I4). For an outside binary vector x, let
T be the sum of its four coordinates in GF(3). Each column equation is
T-x_i=0. Hence all four coordinates agree modulo 3 and therefore as integers.
Every support vertex has at least eleven neighbors outside S, all common
with every other support vertex. Each of its three bad-pair residuals is at
least nine; all other residuals in its row are good and nonnegative. Its
complete row sum is at least 27, contradicting zero. No bound that treats a
bad residual as divisible by 3 is used here.

All possible six-edge supports have now been covered and contradicted in the
adjacency domain, proving F3 is not six.

## Written falsification inventory (12 checks, zero executed fixtures)

1. Reproduce D diagonal0, complete integer row sum0 and both products AD,DA.
   Binary symmetry, exact degree and order99 are used before modular reduction.
2. Exhaust degree-two and degree-three signs; opposite and equal signs,
   respectively, are necessary, not an assumption of uniform support labels.
3. Challenge disconnected six-edge supports: each component needs three edges,
   so only two C3 components are possible; both violate odd alternation.
4. Exhaust v=4,5,6 by handshaking and simplicity. For v=5, excess degree two
   leaves exactly the two recorded degree sequences.
5. Check the complement degree sequence (1,1,2,2,2): P5 or P2+C3 are the only
   decompositions. Degree-zero, doubled-edge or two-cycle components are absent
   because Q is simple and its degree sequence has no zero.
6. Complement P5 gives one degree-two H vertex with the same sign from both
   degree-three endpoints; it cannot be repaired by any alternate path sign.
7. For both signs, alternating C6 gives two outside equality classes. The
   selected pair lies in one class and is not a support edge.
8. Signed K2,3 allows the two parts to have different outside coordinate values;
   the proof only needs equality of the two degree-three coordinates.
9. Bowtie leaf equations force all five coordinates equal, while the center
   enforces the opposite signs on its two triangles. Its degree-four row is
   not incorrectly assigned the degree-three all-equal sign rule.
10. In K4, x*(J4-I4)=0 forces every coordinate equal to T. Written x=(0,0,0,0)
    and (1,1,1,1) satisfy it since 4=1 in GF(3); neither is a graph fixture.
11. Worst-case internal neighborhoods give common-neighbor bounds9,10,10,11
    for C6,K2,3,bowtie,K4. All internal pairs are permitted arbitrary adjacency.
    Good pairs round residuals7/8/8 to9; K4 bad pairs retain the unrounded9.
12. C6, K2,3, bowtie and K4 written support labels do satisfy zero modular
    rows. Their rejection uses the extra commuting adjacency realization and
    integer row budget, not a false claim that these modular controls fail.

## Verdict and limits

VERIFIED for the exact statement by this independent complete written proof.
The complement classification and explicit row-budget contradictions attempt
to falsify the producer's path reduction and all field-sign cases. Four
legitimate written modular support patterns are preserved as such; zero graph
realizations or executable fixtures were produced.

Discovery and verification share only exact definitions and elementary
integer/GF(3) arithmetic. The prior small-support/four-defect proofs are context
and not dependencies of this standalone proof. No producer code, finite graph
agreement, solver result, numerical guide or agent agreement is a premise.
Formalization, external review and novelty remain unestablished. This does not
exclude any other positive residual value, resolve Conway-99, approve an engine
or measure overall graph-space coverage. Overall search coverage: UNKNOWN;
no validated denominator.
