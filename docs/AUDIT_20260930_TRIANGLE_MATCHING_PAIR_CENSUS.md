# Independent finite ordered-matching-pair census

Fix M0=(01)(23)(45)(67)(89)(10 11). Let X be the set of perfect matchings
on twelve labelled points, and H the permutations preserving M0. The claim
concerns H acting simultaneously on the ordered pair (M1,M2) in X times X.
It does not concern full triangle cores or target graph completions. No
nontrivial target automorphism is assumed.

## Complete finite universes

There are 11!! = 10,395 perfect matchings: pair the least remaining vertex
with any other, and repeat, giving11*9*7*5*3*1 possibilities. Each valid
matching has a unique such sequence. Every saved mate array is checked to
be a fixed-point-free involution; all10,395 are distinct. Therefore the saved
list is exactly X, without relying on the producer's enumeration routine.

A permutation in H permutes the six M0 edges and chooses an orientation
independently on each one. Conversely each such choice is in H and uniquely
determines its permutation. Thus |H|=6!*2^6=46,080. The checker constructs
every such permutation, verifies its bijectivity and edge preservation,
and checks cardinality and uniqueness. The producer's emitted generators
are separately checked to generate this exact full group.

## Independent orbit and stabilizer checks

For each saved first-stage representative M1, the checker evaluates its
unordered-edge-set image under every element of H. This full set must
equal the saved orbit. The eleven saved sets must be pairwise disjoint
and cover all of X. It directly selects H1={h in H:h(M1)=M1}; its size
must equal the saved stabilizer order, and the supplied stabilizer
generators must generate exactly H1. Alternating component sizes of
M0 union M1 are reconstructed independently from their undirected edges.

For every saved second-stage representative M2, every element of H1 is
applied directly. Its complete image set must equal the saved second orbit,
and the number of elements fixing M2 is counted explicitly. This verifies
the saved joint stabilizer H12, as well as the orbit-stabilizer identity.
For each M1 all second-orbit sets must be disjoint and cover X.

These checks use direct full-group images of unordered edges. The producer
uses generator breadth-first traversal on mate arrays. No producer code is
imported. A separate literal adjacency-matrix permutation checks the action
direction on small controls, and deliberately corrupted partitions,
stabilizers, permutations and population counts must be rejected.

## Why the two-stage partition covers ordered pairs exactly

Every ordered pair (m1,m2) can first be carried by H to one of the eleven
first representatives M1. Two resulting pairs with the same first component
are H-equivalent if and only if their second components are equivalent under
the actual stabilizer H1: any relabeling between them must fix M1. Pairs
with first components in different first-stage orbits cannot be equivalent.
Thus summing the second-stage orbit counts gives the exact number of
simultaneous ordered-pair orbits. Weighting each first-stage orbit by
|X| counts every labelled ordered pair once, giving10,395^2=108,056,025.

Nothing here fixes or classifies the additional bijection P between the
named fibres. The product |X|^2*12! counts labelled choices including an
arbitrary P only; it is not a quotient count or a feasible-core count.
Likewise, a trivial stabilizer of (M0,M1,M2) does not imply that a completed
target graph has no automorphisms. No graph-feasibility test is part of this
census, and no target-wide coverage percentage follows.

## Replay

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_matching_pair_census.py --out acceleration/results/20260930_independent_review/triangle_matching_pair_census
```

Use a new output directory. The unchanged uv.lock fixes the environment.
The report pins all raw producer artifacts and source, audit source,
controls and per-stage receipts. Exact comparisons use integer arithmetic
and finite sets only. A timeout cannot produce a successful final report.
