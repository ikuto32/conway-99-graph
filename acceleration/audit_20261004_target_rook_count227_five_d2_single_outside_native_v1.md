# Independent written audit: ordinary b5 support with one outside point

Verification completed **2026-10-04T20:25:05.4030478Z** by Native
(`/root/native_driver`), method `independent_derivation`. Structural is the
mathematical producer. No computational executor or worker is involved.

## Exact source and result

Whole paper
`docs/CANDIDATE_20261004_TARGET_ROOK_COUNT227_FIVE_D2_SINGLE_OUTSIDE_POINT_V1.md`,
SHA256 `2127b52a44b3f667131c357a41972e631d7c3242d22bfe59e9af46dc65932492`,
and whole raw
`acceleration/results/20261004_target_rook_count227_five_d2_single_outside_point_candidate01.json`,
SHA256 `6b152c9bb6138078fa1324690ca64251c9deec23d6c8a4e8cbcaffd87c344819`,
were independently reconstructed and challenged.
Exact ID `C-UNRESTRICTED-TARGET-ROOK-COUNT227-FIVE-D2-NO-SINGLE-OUTSIDE-POINT` r1.

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once by their vertex sets and put d_T=6-r_T for each actual
triangle. Suppose R=227, every d_T belongs to {0,1,2}, and exactly five actual
triangles have deficiency two. Suppose further that every vertex used by
the deficiency-one triangles lies in exactly two of them. Let S be that
selected vertex support. It is impossible that exactly one outside-S vertex
lies in any deficiency-two triangle.

**PASS for this exact conditional branch.** Multiplicity-two and the sole
outside point are explicit assumptions. Dependencies are empty. No previous
weighted-boundary gate is needed, and none is transferred. Other outside
counts, fourfold support, b5 as a whole and R227 remain outside this result.
The Root pointwise/Cauchy outline and Structural reconstruction are disclosed
discovery inputs, not the verification itself.

## Target counts, local fan and exact selected support

Lambda1 makes each14-point induced neighborhood a matching, giving seven
triangles through each vertex and231 total. Triangles are linear; a triple
of actual triangles meeting pairwise at three distinct points would give
an actual edge a second triangle partner. Two intersecting triangles can
lie in at most one rook: their four outer cross pairs each have a fixed
second common neighbor, determining its nine vertices. Thus a triangle T
at any of its points has local uncovered-partner degree6-r_T=d_T.
A D0 triangle cannot supply a defect partner.

A rook contains six actual triangles. Total deficiency is6(231-R)=24,
so five D2 leave fourteen D1 and P=19 positive triangles. A positive fan
with r1 D1 and r2 D2 roots needs2r1+4r2 external partners at its distinct
outer points. An external actual triangle meets at most one such point,
by linearity and the no-loose-triple fact. Hence19>=3r1+5r2.

The assumed selected multiplicity2 gives42/2=21 support points. Fourteen
D1 triangles give42 distinct internal edges; at every S point its two
selected triangles give four distinct S neighbors. No support-inducedness
is asserted.

Let p be the sole outside-S point on D2. At p no D1 occurs. Local degree2
needs at least three incident D2 roots; the fan bound permits at most
three. Those three roots have six distinct other vertices, all in S.
The other two D2 roots are wholly in S. Their ordinary internal edge
counts are three single edges plus two triples of edges, totaling9;
lambda1 keeps them distinct from one another and the42 selected edges.
Thus e(S)=51+z for an integer z>=0, including every extra actual S edge.

## Full ordinary Gram, internal increments and remaining excess

A^2+A=12I+2J and Aj=14j imply that Q=3I-A+J/9 is PSD, Qj=0,
Q^2=7Q and AQ=-4Q. These are ordinary real/rational identities from
the complete target; there is no finite-field or extra code premise.
With Y=3Qchi_S,

    Y=9chi_S-3Achi_S+7j,  sumY=0,  AY=-4Y,
    Y=16-3deg_S inside S and7-3deg_S outside,
    every coordinate is1 modulo3,
    ||Y||^2=63(112-2e)=630-126z.

The factor63 is9*7. The preserved factor-nine failed outline is not used.
Let K_v=deg_S(v)-4>=0. Then sum_S K=18+2z, Y_v=4-3K_v and
sum_S Y=30-6z. The two wholly-S D2 roots force sum K(K-1)>=12.
If disjoint, six vertices each have K>=2; if intersecting, the common
vertex has K>=4 and the other four K>=2, giving at least20. Distinct
edges and all additional edges are retained. Consequently

    sum_S K^2>=30+2z,
    ||Y_S||^2>=336-24(18+2z)+9(30+2z)=174-30z.

Write deg_S(p)=6+a, with0<=a<=8 by the six known neighbors and degree14.
Then Y_p=-11-3a. Exactly77 outside coordinates remain besides p, with

    their sum=-19+6z+3a,
    their norm<=335-96z-66a-9a^2.

For each integer y=1+3t, F(y)=y^2+y-2=9t(t+1)>=0. Their complete
residue excess Delta therefore obeys

    Delta<=162-90z-63a-9a^2<=162.

No older e51/52 or a<=2 refinement is assumed here. Nonnegativity of
each residue excess, not of each Y coordinate, is used.

## Pointwise neighbor equation gives the contradiction

Each of the six known S endpoints of p's three D2 roots has one additional
internal edge beyond its four selected neighbors; hence its K>=1 and
Y<=1. Each of the other a S neighbors has K>=0 and Y<=4, without a
location or uniformity assumption. Thus p's S-neighbor Y sum is<=6+4a.
From AY=-4Y, its complete neighbor sum is44+12a. Its outside-neighbor
subset lies in the77 remaining outside coordinates, has m=8-a points,
and sum B>=38+8a.

At a8 the subset is empty but must have positive sum, impossible. Otherwise
1<=m<=8 and B>=38. Ordinary Cauchy gives

    sum_subset F(Y)>=B^2/m+B-2m
                       >=38^2/8+38-16=405/2>162.

Every coordinate outside this subset contributes nonnegative F to Delta.
The lower405/2 thus contradicts the upper162. The strict rational gap
does not require equality, an averaged neighborhood or a proposed graph.

## Twenty proof checks and six hand challenges

Checks1..20 are: target triangle counts/linearity; local rook uniqueness/
degree/fan; D24/a14/P19; S21/42edges/four selected neighbors; exactly
three roots at p; six distinct endpoints/two wholly-S roots/9edges;
e51+z with extras; Q identities; exact Y scaling/residue/eigenvector/norm;
increment sum; disjoint/shared wholly-S increment excess; internal norm;
p degree6+a/domain0..8; exact remaining77 sums/norm; residue nonnegativity;
Delta upper162; six endpoint values<=1/extras<=4; pointwise B>=38+8a;
empty/positive subset and Cauchy floor; final exact branch contradiction.

Hand challenges:

1. The two wholly-S roots may meet once. Four distinct incident edges
   there give K>=4, strengthening the proof rather than invalidating it.
2. Three distinct roots through p have six distinct outer points. Extra
   p-to-S edges or overlap with the wholly-S roots do not weaken K>=1.
3. The global scalar inequalities alone can retain equality patterns;
   AY=-4Y supplies the new local obstruction, not a presumption that
   the older surviving scalar rows were impossible.
4. Six abstract Y4 and two Y7 have sum38, norm194 and excess216,
   consistent with the weaker Cauchy floor405/2. No target extension
   or uniform-neighbor assumption is inferred from this scalar control.
5. The a8 zero-subset case is explicitly rejected by its positive required
   sum; Cauchy is applied only to nonempty subsets.
6. Negative residue values such as-2 have zero excess and remain allowed.
   Additional edges stay in z/a; the outside subset never includes S or p.

This is26 written checks (20 proof,6 hand), with zero executed, formal,
external, solver or scientific checks.

## Provenance and boundaries

The weighted necessary-boundary paper is comparison only, not an inherited
logical premise. The unchanged scaling veto receipt
`59638497433f0601414a2e335d4ae2f01bac5681c96b1535d4ca0b46a7ec3e5b`
records a message-only failed formula, not a REFUTED theorem. This proof
freshly uses the correct norm630-126z. Shared parity/fan/Gram/increment
mechanisms and Root's new pointwise outline are disclosed without novelty
or archive-completeness claims.

Only selected small source/metadata reads/hashes and new written artifacts
were made. No mathematical program, import, AST/syntax/backend, worker,
census, solver, ledger parse, Git/index/publication operation or protected
edit occurred. Start/executor times remain null; Root acceptance is null
at creation. Only this literal branch is excluded, pending separate Root
exact review/nextWave47 registration outside the closed cutoff449.
