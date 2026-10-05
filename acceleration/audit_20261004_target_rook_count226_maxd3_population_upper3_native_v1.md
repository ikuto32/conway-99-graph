# Independent written review: maxd3 at R226 gives at most three D3 triangles

Completed verification 2026-10-04T21:40:23.9735048+00:00.
Producer /root/structural; distinct written verifier /root/native_driver.
No scientific program, import, AST, census, solver or worker. Metadata
creation and Root acceptance are separate; all historical bytes preserved.

## Literal statement and objects

Whole paper
docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_D3_POPULATION_UPPER3_V1.md
has SHA691bf52a1885b37372fea5594f28cfdcacd5c361574431e441c8dc6208ab079a;
whole candidate01 has SHA
fe6ec41312582f56842e9da64b1a575994b1e0522e43069252b7717c0ebb5684.
Exact ID C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-D3-POPULATION-UPPER3 r1.
The literal claim assumes a complete finite simple SRG(99,14,1,2), actual
rook-nine count226, and every actual triangle deficiency in{0,1,2,3}; it
concludes only c<=3. Its logical dependency list is empty. The separate
max3 theorem, reviewed elsewhere, is not silently inherited here.

Every actual edge lies in exactly one triangle by lambda1. Hence there are
693 edges/231 triangles, two triangles share at most one point, and three
cannot meet pairwise at three different points. A covered intersecting
triangle pair has a unique actual induced rook-nine completion. Each rook
contains six triangles, so D=sum(6-r_T)=6(231-R)=30. The simple local
defect graph at a point has degree d_T at its triangle node: there are six
other local triangles, and each covered pair accounts for one of the r_T
rook completions. With positive populations a,b,c, a+2b+3c=30 and
P=a+b+c=30-b-2c.

Local parity gives r1+r3 even. Each focal root of deficiency i contributes
itself and2i distinct external defect partners at its two other points.
One external triangle cannot meet two fan outerpoints: either linearity
or the three-distinct-intersections veto applies. Thus3r1+5r2+7r3<=P.
This count uses actual triangles and points, without equity or induced
support assumptions. Other edges do not invalidate it.

## Pairwise disjointness when c>=3

Then P<=24-b. With two local D3 roots parity makes r1 even. If r1=0,
degree3 needs at least two D2 roots, so fan>=24 while b>=2 makes P<=22.
If r1=2 and no D2, (3,3,1,1) is nongraphical: both degree3 nodes would
be universal, forcing the leaves degree2. Adding any D2 costs fan25>P.
With r1>=4 the cost is>=26>P. These exhaust two-D3 profiles.

For three D3, r1 odd. Minimal(3,3,3,1) is nongraphical: three degree3
nodes in a four-node simple graph are universal, so the leaf has degree3,
not1. Adding one D2 already costs29, or two more lows costs30, beyond24.
At least four D3 at one point cost28, while c>=4 gives P<=22.
Thus all c D3 triangles are pairwise disjoint. Their3c actual points are
distinct; no F four-cycle count or global graph triangle-freeness is used.

## Large-c coverage retains the valid exceptional point

Take c>=4, so P<=22-b. At each selected D3 point there is exactly one
D3; r1 is odd. If r1=1, degree3 requires r2>=2 and fan>=20. The local
sequence(3,2,2,1) is valid: its three highs form a triangle and the low
is a leaf at D3. I retain it as a possible bad point, not a local veto.
Bad points cannot occur at b0/1, since two D2 do not exist, or b>=3,
since P<=19. At b2 they use both D2; at mostonepoint is possible by
triangle linearity. Let h be the actual bad-point count, at most1 there
and0 elsewhere. No constant local profile is asserted.

For each D1 triangle L, t_L=|L intersect S| lies in0..3. At every nonbad
D3 point there are at least three D1, and at bad points at least one.
Thus sum t_L>=9c-2h, and also sum t_L<=3a. Even at h1, integer a satisfies
a>=ceil(3c-2/3)=3c. Substituting the exact mass equation gives6c+2b<=30.
Under c>=4 this leaves only c4/b0,1,2,3 and c5/b0. It excludes every
c>=6; it does not prematurely assume c4 or throw away zero-incidence lows.

## Ordinary actual support Gram bound

The c central triangles supply3c edges in S. A D1 triangle supplies
binom(t_L,2) further edges. They are distinct from the central edges and
one another by unique actual triangle partners. For t0..3,
binom(t,2)>=t-1; the negative right side at t0 is valid. Consequently
e(S)>=3c+sum binom(t_L,2)>=12c-2h-a. All additional actual support
edges raise this lower bound; no selected inducedness is assumed.

From A²=12I-A+2J and Aj=14j, the nonconstant adjacency eigenvalues are
3,-4. Q=3I-A+J/9 has eigenvalues0,7,0 and is PSD. For the ordinary
indicator of S, size3c, chi Q chi=9c+c²-2e(S)>=0. Therefore
a>=(15c-c²)/2-2h. The five exact hand rows are:

|c|b|actual a|h upper bound|required a minimum|
|---:|---:|---:|---:|---:|
|4|0|18|0|22|
|4|1|16|0|22|
|4|2|14|1|20|
|4|3|12|0|22|
|5|0|15|0|25|

Every row fails. Thus c>=4 is impossible, proving precisely c<=3 under
the literal maxd3/R226 assumptions. The proof is self-contained and avoids
any collapsed F4 correspondence, uniform incidence, automorphism or existence
of a nonconstant codeword.

## Written checklist and falsification limits

Twenty-eight proof checks: target edge count; triangle count; edge uniqueness;
linearity; no loose triple; covered-pair rook uniqueness; D30; mass equation;
P equation; local degrees; odd parity; two external root points; one fan
intersection per external triangle; fan bound; two-D3/r1=0 coverage;
two-D3/r1=2 failure; two-D3/r1>=4 coverage; three-D3 nongraphical minimum;
larger-D3 exclusion; actual disjoint support; valid bad profile; bad b cases;
one bad point via linearity; integer coverage a>=3c; complete large-c domain;
distinct selected edges; exact PSD quadratic; all five table contradictions.

Ten failure/boundary challenges: max3 is an assumption rather than a supplied
upper3 gate; D1 parity alone is false at the valid(3,2,2,1) point; an
abstract degree pattern without actual fan can evade a required constraint;
the bad graph is genuinely graphical; h1 is not rounded to zero; integer
a is required for its ceiling; t0 is not deleted; central/low edges must not
be double counted; additional edges remain present; no faithful square count
can be presumed with four high roots. None falsified the exact claim.
These38 checks and five hand rows are written only, not executed tests.

PASS for the literal r1 population bound only. Root outlined discovery and
Structural independently produced the candidate; Native reconstructed this
whole proof separately. Prior fan/parity/Gram overlap is disclosed, with no
archive absence or novelty claim. Neither surviving c0..3 populations,
R226 nor the target are excluded. No ledger was parsed; no protected,
Git/index/publication or original-artifact mutation occurred. Root-reported
baseline457 has not been used as a scientific premise. Root acceptance and
registration are separately pending.
