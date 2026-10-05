# Candidate: at R226 and max deficiency three, at most three d3 roots occur

Root proposed the pair-disjointness, one exceptional point and support-Gram
route. Structural independently reconstructed the full local possibilities,
the integer coverage bound and the five remaining parameter cases. This is
a separate written CANDIDATE; no mathematical program, enumeration, import,
solver or worker ran. The two previous R226 candidates remain unchanged.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle.
Suppose R=226 and every d_T belongs to {0,1,2,3}. Then the number c of
actual triangles with deficiency three is at most three.

The maximum-three hypothesis is literal. No gate for the separately pending
R226 upper-three theorem is presumed. The proof below derives its needed
fan and support constraints from the exact target and actual root labels;
it has no inherited logical claim dependency. It neither excludes R226 nor
asserts that any surviving population is realized.

Write a,b,c for the positive populations of deficiencies one,two,three.
Then

    a+2b+3c=30, P=a+b+c=30-b-2c.              (1)

At a point with r_i positive roots of deficiency i, their simple local
defect graph has degrees i. Thus r1+r3 is even. The actual fan gives

    3r1+5r2+7r3<=P.                            (2)

To recall why (2) counts actual triangles: a root of degree i in that
point's defect graph has two outer points, each meeting i external defect
partners. Every positive triangle not through the focal point can meet at
most one of these outer points across the entire fan. Two within one root
violate triangle linearity; two in different root buckets give three actual
triangles pairwise meeting at different points, contrary to lambda1 on
their intersection edge. Counting the focal roots and all their external
partners gives sum(2i+1)r_i<=P. Arbitrary other graph edges are retained.

## With at least three d3 roots they are pairwise disjoint

Assume c>=3, so P<=24-b. At a point with r3=2, r1 is even.

* If r1=0, the degree-three nodes require at least two d2 nodes to have four
  local nodes. Their fan has weight at least24, but b>=2 makes P<=22.
* If r1=2 and r2=0, degree sequence(3,3,1,1) is nongraphical. Its degree-three
  nodes would be universal, forcing both leaves to have degree at least two.
* If r1=2 and r2>=1, the fan is at least25>P.
* If r1>=4, its fan is at least26>P.

At a point with r3=3, parity makes r1 odd. The minimum r1=1,r2=0 has
degree sequence(3,3,3,1), also nongraphical: three high degree sums nine
and a single leaf force four high-high edges, more than the three available.
Any further node gives fan at least29, above P. Four or more d3 nodes have
fan at least28 while c>=4 implies P<=22.

This exhausts all multiple-d3 point possibilities, so the c actual d3
triangles are pairwise disjoint. Their points form a set S of size3c.
No automorphism or uniform point profile is assumed.

## For c>=4 there is at most one small low-incidence point

Now suppose c>=4, so P<=22-b. At each point of S exactly one d3 root
occurs, and r1 is odd. If r1=1, degree three needs r2>=2, and its fan is
at least20. Call such a point bad. If it is not bad, r1>=3.

There are no bad points when b=0 or1, because two d2 nodes are unavailable.
There are also none when b>=3, because P<=19<20. At b=2, a bad point
contains both actual d2 roots. There can be at most one: two different
points would give those two triangles two common vertices, violating
linearity. Thus the number h of bad points satisfies

    h=0 unless b=2, and h<=1 when b=2.         (3)

The valid bad local sequence(3,2,2,1) is retained; it is not wrongly declared
nongraphical. It supplies only one d1 incidence instead of the usual minimum
three, which is exactly the loss two in what follows.

Let t_L count the points in S of each actual d1 triangle L. Since its three
points are distinct and the d3 roots are disjoint, t_L belongs to {0,1,2,3}.
The local lower bounds and (3) give

    sum_L t_L >=9c-2h, sum_L t_L<=3a.

Therefore 3a>=9c-2h. In both h0 and h1 the integer a must satisfy a>=3c;
even h1 gives a>=ceil(3c-2/3)=3c. Substitution in (1) gives

    6c+2b<=30.                                (4)

This closes the large-c loophole without a computation. Under c>=4,
(4) leaves only c4 with b0,1,2,3, or c5 with b0. No c>=6 can survive.

## The ordinary support Gram contradicts all five cases

The c disjoint d3 triangles contribute3c distinct actual edges inside S.
A d1 triangle L contributes binom(t_L,2) such edges. These edges are
distinct from the d3 edges and from each other because every edge has its
unique actual triangle. For t=0,1,2,3, binom(t,2)>=t-1, including t0.
All additional actual edges only raise e(S). Consequently

    e(S)>=3c+sum_L binom(t_L,2)
        >=3c+(9c-2h)-a=12c-2h-a.             (5)

The exact target upper Gram Q=3I-A+J/9 is positive semidefinite. Applying
it to the indicator of the actual3c point set gives

    0<=chi_S^T Q chi_S=9c+c^2-2e(S),
    e(S)<=(9c+c^2)/2.                         (6)

Together (5)-(6) require

    a >= (15c-c^2)/2 -2h.                     (7)

At c4, the right side is22-2h. The four remaining cases give the complete
hand table:

| c | b | a=30-2b-3c | h bound | required a from (7) |
|---:|---:|---:|---:|---:|
|4|0|18|0|22|
|4|1|16|0|22|
|4|2|14|1|at least20|
|4|3|12|0|22|
|5|0|15|0|25|

Every row contradicts (7). No claim of realizability, selected inducedness
or equality structure is needed. Thus c>=4 is impossible and c<=3.

## Boundaries, overlap and review requirement

The failed local graphs(3,3,1,1) and(3,3,3,1) were separately challenged by
their literal degrees. The valid(3,2,2,1) graph is instead handled with its
one exceptional point and loss two. No parity of the d1 family alone is
used. The t0 inequality in (5) has a negative right side and remains valid;
it is not removed by a false positive-incidence assumption. Extra actual
edges are included by the lower bound, not discarded.

The argument uses the ordinary actual support indicator, rather than a
collapsed local four-cycle or an unproved faithful F4 census. The upper
Gram bound is target-specific and exact; no floating eigenvalue or
numerical feasibility result is used. The selected d3 points need not have
equal neighborhoods or uniform d1 counts.

This bounded R226 follow-up overlaps earlier fan/parity and target-upper-
Gram methods. Its new scope is the explicit maxd3/c<=3 population
restriction at D30. No whole-archive absence or novelty assertion is made.
The current publication cutoff remains unchanged. A distinct written
review must bind this exact paper and statement before any VERIFIED or
ledger use; pending R226 upper3 evidence does not approve it automatically.
