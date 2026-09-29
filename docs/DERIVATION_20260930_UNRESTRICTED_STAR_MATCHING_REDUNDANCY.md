# Candidate: unrestricted one-star triangle matching is redundant

Status: CANDIDATE, pending a different review path. This is a necessary local
consistency result, not a target construction, family exclusion or novelty claim.

Use the independently justified root scaffold: root r, fourteen inner symbols
0,...,13 paired by s xor 1, and one outer vertex for each unordered pair of
symbols from distinct root pairs. Fix u with label {0,2}. Let S be ANY set of
twelve distinct outer labels other than u, with incidence quotas one on
0,1,2,3 and two on each of 4,...,13. These are exactly the common-neighbor
equalities between u and the fourteen inner vertices after accounting for
their known mate: quota(s)=2-1[s in label(u)]-1[s xor 1 in label(u)].

The selected labels containing 0 and 2 are distinct, since label {0,2} itself
is excluded. In the neighborhood of u they are forced to pair with inner
vertices 0 and 2. Remove these two labels. The remaining ten labels avoid
0 and 2. Each symbol occurs at most twice, so each remaining label intersects
at most two of the other nine labels. Their disjointness graph therefore has
minimum degree at least seven and has a perfect matching.

For completeness, any even graph on n vertices with minimum degree at least
n/2 has a perfect matching. Otherwise take a maximum matching and two unmatched
vertices x,y. They cannot be adjacent. Every neighbor of either is matched;
each matched pair contributes at most two to deg(x)+deg(y), since three
incidences would permit replacing its one edge by two edges incident to x,y.
Thus deg(x)+deg(y) <= 2|M| <= n-2, contradicting deg(x)+deg(y) >= n.
This elementary proof uses no graph automorphism or numerical argument.

Add u--S and the five matched outer edges to the known root scaffold. Specify
all other u--outer edges absent, and specify all other edges within N(u)
absent. These specifications are consistent. Treat still unknown entries as
zero only when computing the already-forced common-neighbor LOWER counts.
The resulting known-edge graph P has maximum degree at most fourteen and
for every distinct x,y satisfies common_P(x,y)+P_xy <= 2:

* The root and two-inner cases are unchanged from the scaffold.
* For an inner symbol s and selected outer y, the sum in question is
  1[s xor 1 in label(y)] + 1[s in {0,2}] +
  1[s in label(partner(y))] + 1[s in label(y)], with the partner term
  present only for the ten newly matched labels. The first and last terms
  cannot both be one. If s is 0 or 2, the partner term is zero; otherwise
  the middle term is zero. Thus the sum is at most two.
  For unselected y the two added terms are absent.
* For two selected outer vertices other than u, their common outer neighbor
  is u and they share at most one inner symbol. They are joined by a new
  matching edge only when their labels are disjoint. There is no second
  common outer neighbor because the new edges on S are a matching.
* For u and a selected y there is exactly one common neighbor: its shared
  inner symbol if present, otherwise its matched partner. For u and an
  unselected outer y the forced common count is at most one.
* An unselected outer vertex has only its two scaffold edges. Hence a pair
  involving such a vertex has at most one shared inner symbol and no shared
  outer neighbor, except for the already treated u case.

All pairs involving u and an inner vertex have their exact required counts
by the quotas. N(u) induces exactly seven independent edges. All forced
degrees remain <=14: r and inner vertices already have degree14, u now has
degree14, and each other outer vertex has degree at most four.

Consequently the unrestricted single-star test consisting only of those
symbol quotas, an induced seven-edge matching in N(u), and all already-known
pair caps can never reject S. Any obstruction must use compatibility with
additional completed stars, fixed outer edges, or stronger global conditions.
The archived conditional matching filters do have additional fixed edges;
this theorem does not make them redundant. The twelve-neighbor labels may
include a normalized disjoint-support anchor, but no such anchor is needed
for this implication. Existence of P does not establish any completion to a
99-vertex target, and no sampled controls prove this quantified statement.

Prior-work inspection: scratch_general_triangle_portfolio.py already uses
42 possible third vertices of the anchored triangle; archive waves149,151,
154 already develop the 12+12+12+60 triangle partition and incidence factor.
Wave171 already records that an independent triple has at most one common
neighbor. Those lanes are not claimed as new discoveries here.
