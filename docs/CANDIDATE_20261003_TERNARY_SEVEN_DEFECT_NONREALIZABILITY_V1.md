# Seven nonzero ternary defects are impossible

Producer: /root. Frozen source timestamp: 2026-10-03T05:16:17+00:00.
Status: CANDIDATE pending independent written derivation. No mathematical
program, graph fixture, claim registration or target resolution is asserted.

## Exact proposed statement

For every symmetric binary zero-diagonal 99-by-99 matrix A with exactly14
ones in every integer row, let F3 be the number of unordered pairs {u,v}
with (A^2)_uv+A_uv-2 nonzero modulo3. Then F3 is not7. This statement alone
does not exclude any other value or resolve Conway-99.

The sole proposed uses_result dependency is
C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-RESTRICTION r1:
the whole nonempty connected nonisolated residual support cannot have both
at most12 vertices and maximum degree at most3. Its binding is
`acceleration/results/20261003_independent_review/ternary_subcubic_connected_support01/claim_binding_schema2.json`,
SHA256 562676e3af281e33384265824f9e115dfce27cca498b94f3b46cd0100346edd3.
Its independent report is SHA256
e3b6ea1f00bea171554867b68667bdf6d25ed57a3c8c1438d8654cfed01aba15;
its written proof is
`acceleration/audit_20261003_ternary_subcubic_connected_support_v1.md`,
SHA256 1233903ac6449e354f8aead02d222b9b2594b617f06dfa0ce8c07800611809ed.
No stronger later support theorem is needed. No lambda1, incidence,
automorphism, fixed adjacency configuration or numerical premise is used.

## Complete seven-edge support reduction

Put D=A^2+A-12I-2J over the integers and M=D modulo3. Binary symmetry and
degree14 give D_uu=0 and complete row sum196+14-12-198=0. Also AJ=JA=14J,
so expansion gives AD=DA and hence AM=MA modulo3. The simple nonisolated
support H of M has an edge for each nonzero unordered off-diagonal entry.
Each edge label is +1 or -1 and every support row sums to0 modulo3.
Consequently a nonisolated support vertex has degree at least2. Degree2
forces opposite incident labels; degree3 forces three equal labels;
degree4 forces exactly two labels of each sign.

Assume H has exactly7 edges. Every nonempty component has at least3 edges
by minimum degree2. A three-edge component would be a triangle with every
vertex of degree2. Alternating signs around that odd cycle are impossible.
Thus every component has at least4 edges, and7 edges force H connected.
The handshaking identity and minimum degree give m=|V(H)|<=7. If H were
subcubic, the pinned prior theorem would exclude it. It therefore has a
vertex of degree at least4. Since sum degrees=14, all other degrees>=2,
and a simple m-vertex graph has degree<=m-1, the only possibilities are:

* m=5, degrees (4,4,2,2,2) or (4,3,3,2,2);
* m=6, degrees (4,2,2,2,2,2).

Indeed m<=4 allows at most6 edges; m=7 forces all degrees2; m=6 has only
two excess degrees over the baseline2, and m=5 has four such excess
degrees with each excess at most2. Degree5 would require m>=6 and total
degree at least5+5*2=15, a contradiction. The reduction includes all labels
and all simple support graphs; it makes no assumption about adjacency in A.

### Five vertices, two degree4 vertices

Call the degree4 vertices a,b. Both are universal in H, are joined by an
edge of label s=+1 or -1, and the other three vertices are adjacent precisely
to a and b. At each of those degree2 vertices, its two labels are opposite.
Add the zero-row equations for a and b modulo3. All six spokes cancel in
pairs, leaving2s=0 modulo3, impossible for s nonzero.

### Six vertices, one degree4 vertex

Call the degree4 vertex a. Exactly four of the other five vertices are its
neighbors; let z be the remaining nonneighbor. Removing a leaves a simple
three-edge graph with degree sequence (2,1,1,1,1), with z the degree2
vertex. This graph is exactly a path of length2 centered at z and a separate
single edge. (The two neighbors of z exhaust two edges; the other two
degree1 vertices must be joined by the last edge.) Reattaching a creates a
four-cycle through z and a triangle sharing only a.

All vertices of these two cycles except a have degree2. On the triangle,
the two incident labels at a must be equal, say t,t. Along the four-cycle,
the two incident labels at a are opposite, say s,-s. Thus the a row sums
to2t, which is nonzero modulo3. This excludes the whole degree sequence.

### Five vertices, degrees4,3,3,2,2

Call the universal vertex a, the degree3 vertices b,c, and the degree2
vertices d,e. Removing a leaves a graph on four vertices with degrees
(2,2,1,1), hence a path d-c-b-e after relabeling d,e. It cannot be a
triangle plus an isolated vertex, or another cycle, because all four
residual degrees are positive and exactly two are1. The complete support
edges are a joined to b,c,d,e and the three path edges d-c,c-b,b-e.

Because b,c have degree3 and share an edge, all their incident labels are
the same nonzero s. The degree2 equations force the labels a-d and a-e
to be -s. The degree4 row of a is then s+s-s-s=0, so this support is not
discarded merely by its modular zero-row equations.

Here the binary commutator supplies the additional obstruction. For any z
outside the whole support S={a,b,c,d,e}, its M row is0 and AM=MA gives
the binary vector x_u=A_zu the equations x*M[S,S]=0 modulo3. The degree2
columns d,e force x_a=x_c and x_a=x_b. The degree3 columns b,c have equal
nonzero labels; their three binary neighbor coordinates sum to0 modulo3,
and therefore are all0 or all1. They force x_e=x_a and x_d=x_a as well.
Thus all five coordinates of x agree, for every outside vertex z.

Every support vertex has the same outside neighborhood in A. Its degree14
and at most4 internal neighbors give at least10 outside neighbors, so any
two support vertices have at least10 common neighbors. The pair d,e is
not a support edge, so its integer residual r_de=(A^2)_de+A_de-2 is
divisible by3 and at least8; hence r_de>=9. In any complete integer residual
row, a good pair is divisible by3 and at least-2, so its residual is
nonnegative. Each bad pair is at least-2. Vertex d has exactly two bad
pairs; its row sum is therefore at least9-4=5>0, contradicting its exact
zero row sum. No value for A_de, internal adjacency or symmetry was assumed.

All possible seven-edge support graphs are now excluded, proving the
proposed statement F3!=7.

## Independent verification requirements and limits

A different verifier must reproduce the prior literal scope and all degree
and component coverage arguments, including the omitted degree5 bound.
Challenge the two exact residual-row sums, signed degree2/3/4 rules,
triangle odd-cycle obstruction and the three degree sequences. Reconstruct
the four-vertex path and the five-vertex path-plus-edge classifications
without importing producer code. In the first two cases verify signs at
the shared vertex and the nonzero value2s modulo3.

The last support is a legitimate signed zero-row modular support, so it
must be challenged using the binary outside commutator, not rejected from
labels alone. Verify that all five binary coordinates agree for every
outside vertex, the common outside-neighbor lower bound10, and the exact
rounding8 to the good residual bound9. A support nonedge need not be an
adjacency nonedge; A_de>=0 suffices. Check that only two bad pairs are
charged in d's complete row, and that all remaining good residuals are
nonnegative integers. These are proposed paper checks, not executed fixtures.

No graph realization, exhaustive graph computation, new validator approval,
novelty, formalization or external review is claimed. Existing candidate and
audit bytes remain unchanged. Any combined bound on other F3 values must
pin the additional results explicitly. Overall search coverage: UNKNOWN;
no validated denominator.
