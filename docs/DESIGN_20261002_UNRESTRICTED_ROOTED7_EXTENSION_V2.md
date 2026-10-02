# Candidate unrestricted root7 continuation, 2026-10-02

This design follows the independently checked rooted5/6/7 reductions. It changes
no conditional source or result. Two cheap exact domain calculations have been
completed, with fresh independent review still required before model use.

The nonedge candidate domain is the full 567-coordinate affine space with actual
rooted6 parameters (c,a,b)=(mask7100,mask8024,mask15540). It has
0<=c<=2, 0<=a<=20, 0<=b<=9+c/2 and 651 integer triples: 210 at c=0,
210 at c=1, and 231 at c=2. The six facet witnesses are raw columns
328:2-c, 368:20-a, 493:18+c-2b, 514:c, 552:a, 566:b. Every affine coordinate
is nonnegative at all eight vertices. The c=0 local face equals the old210-point
domain algebraically; c=0 at one root does not imply global prism absence.

Raw candidate: `acceleration/results/20261002_rooted6_unrestricted_domain01/domain.json`,
SHA256 `dcf63f8a34784fe0a125d52a12423239f72559bfeeb370bc8ccda0b5404c3381`.
Discovery source `theory_20261002_rooted6_unrestricted_domain_v1.py`, SHA256
`a7c3266e521bddbda99bd4721276c575bb3ec9eedfa83bc5cfde4a8f609b4fd2`.
The full693 bounding triples were inspected;651 pass all567coordinates and
all1,445rawrows. The separately authored checker must establish this exact scope.

The secondary-edge candidate domain has two actual prism counts
s=mask8025 (triangle edge), t=mask15541 (matching edge), in rawcolumns382,393.
The frozen1099-row394-variable operator has candidate exact rank392 and two
independent exact integral kernel vectors. The nonnegative integer domain is
0<=s<=12, 0<=t<=6:91 profiles, all rawrows checked, with four rectangle vertices.
Raw domain: `acceleration/results/20261002_rooted6_unrestricted_edge_domain01/domain.json`,
SHA256 `e2cade276f89c87ece74df8544c99704ce116bb55d84a5bd5e364c6264d75c95`.
Raw exact kernel: `unrestricted_edge_nullspace.json`, SHA256
`06fd7396f07f6d1eb894a5d0f05dffcee4299921e60176debb2c2a6487c199b0`.
The old exact modular-lifting helper was reused and explicitly disclosed; these
discovery checks are not independent review.

Proposed model uses all2770 independently enumerated locally admissible root7
nonedge classes, including the20 classes omitted by the old prism-free model.
Use the existing456 parent nonedge-six classes, all marked degree/pair extension
rows, and all rerooted-six rows. Primary RHS has four components (constant,c,a,b).
For the four anchor/partition groups giving secondary nonedges, introduce three
aggregates (C,A,B); for the four giving edges, introduce two (S,T). The20
aggregates replace the old eight. No target automorphism is assumed: permutations
of induced free labels serve only to classify local flag isomorphism types.

For a primary nonedge (u,v), external vertices have adjacency partitions
d=(71,12,12,2), indexed by adjacency to u plus twice adjacency to v. Nonedge
aggregate groups satisfy 0<=C<=2d, 0<=A<=20d and 0<=2B<=18d+C. Edge groups
satisfy 0<=S<=12d and 0<=T<=6d. Introduce20 slack variables for the20 upper
facet equations. Projection convexity justifies these necessary aggregate bounds;
they do not assert that aggregate coordinates can be distributed into graphs.

Estimated size before global coupling:2770 graph variables+20aggregate variables
+20slacks=2810 variables. The conditional operator has8689 extension/total rows,
3052 reroot rows and8upper-bound rows. Reusing the geometry therefore gives
11761 rows after20new upper-bound rows. This is an estimate obtained from frozen
row types, not a completed new operator. Extra nonzeros will arise from20new
classes, the third nonedge basis and the two edge bases. Existing catalogue
bytes and old model bytes remain immutable.

Potential exact global coupling strengthens this necessary model. Let T_u be
the number of induced prism six-sets through u. For actual secondary pairs,
sum_nonedge c(u,w)=2T_u, sum_edge s(u,w)=2T_u, and sum_edge t(u,w)=T_u,
because each prism through u has two nonneighbors, two triangle edges and one
matching edge incident to u. These are graph incidence double counts and require
no target symmetry. Combine them with the separately reviewed identities
sum_nonedge a(u,w)+2T_u=k(k-2) and
sum_nonedge b(u,w)+T_u=n-k-1; for the target both right sides after doubling b
are168. This dependency must be explicitly pinned before any model promotion.

For each anchor i, let N_i be its two nonedge external partitions and E_i its
two edge external partitions. The primary pair contributes known(c,a,b) to the
complete nonedge sum. Proposed four equalities per anchor are

    sum_N(A+C) = 168-a-c
    sum_N(2B+C) = 168-2b-c
    sum_E S - sum_N C = c
    2 sum_E T - sum_N C = c

Hence eight additional candidate coupling rows give11769 estimated rows. The
first two require the independently reviewed almost-prism mean derivation; the
last two follow from the explicit prism incidence bijections above. Redundancy
with existing marked identities must be measured rather than assumed. These
constraints and c<=2 suggest a candidate bound T_u<=84, T<=1386 for the target,
but it must be independently derived/bound before any claim is recorded.

Cheap controls for a future build: rook9 srg(9,4,1,2) has six prisms and pervertex
T_u=4, and supplies positive-prism geometry/root controls. Its raw actual lower
flag counts must be used with n=9,k=4 and matching partition cardinalities; the
target99 affine origin must not be substituted into the9vertex fixture. The
saved exact243vertex SRG can test positive prism incidence counts via local
embedding paths, with no choose(243,6) exhaustive enumeration. Corrupt a graph
edge, count, coefficient/sign, lower-mask transport, affine RHS and every domain
bound to require the relevant exact checking stage. Test all generated classes
and all marked coefficient transports, and independently reconstruct necessity.

Suggested next experiment after domain approval is a NEW source-frozen
unrestricted root7 coefficient build and controls, then an eight-corner scaled
continuous screen with exact rational witnesses or original-row Farkas
certificates. A valid corner family gives only rational necessary-model
feasibility. Any integer/exclusion screen must cover all651 frozen profiles and
preserve errors, timeouts and pending verification separately. This design
authorizes no expensive build or solver; parent approval and new engineering/
semantic gates are required. Overall graph search coverage remains UNKNOWN.
