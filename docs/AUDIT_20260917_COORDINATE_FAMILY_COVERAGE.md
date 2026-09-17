# Written review: matching assignments and the excluded partial family

The coverage interpretation is valid within the frozen labeled configuration.
This note does not independently reapprove the matching enumeration: its
producer also wrote this note. The enumeration/count/partial-cap conclusion
is taken from the separate root agent's independent inclusion-exclusion,
list and dense integer-matrix audit, `coordinate_universe.json` (SHA256
`d7284d73e75f3fe49160c1a2f8ba97eb0263424e727661db25ac1cf631ba8c57`).
The exclusion premise is the independent verifier's `moment_positive600.json`
(SHA256 `d435c7789bd2f181e3a870b2019ae309cdbf2d9530bc21b2d987d40671444bc8`),
with the metadata correction in `moment_positive600_claim_binding.json`:
the moment encoding is a necessary implication, not an equivalence.
The exact raw list is `matchings.json` (SHA256
`d0a306070044f2885df38d2abab264965e4f067873d8dfc13c8b8d0c41104734`).
All paths and hashes, including this written note, are bound by the accompanying
`coordinate_coverage.json` report. No ledger entry is changed by this review.

## Set inclusion

Let F denote the family defined by the immutable partial manifest (SHA256
`dcc0118cc35993743e94bf7b548e6870526e33f3d4fe4015a48cdacb0c1fc05c`).
It fixes the root scaffold,162 outer K edges, and every prescribed absence.
Only60 edges Y of the single freed coordinate and1,680 disjoint-support
edges D remain unknown. The count audit and exclusion audit bind this exact
same manifest; no replacement baseline or absent-edge convention is used.

For each listed perfect matching M, define F_M by additionally setting Y=M
(the six edges of M present, every other edge of Y absent), leaving D free.
Every edge of M belongs to Y; none conflicts with a prescribed positive or
negative edge. Therefore F_M is a subfamily of F. The verified nonexistence
of a target graph in F implies nonexistence in every F_M. This implication
uses only scope inclusion and the independently established exclusion;
passing partial upper caps is neither sufficient nor needed for the inference.
The count6,040 labels coordinate assignments, not completed graphs or
isomorphism classes. Every assignment can pass partial caps while every
associated completion problem is nevertheless excluded by stronger equations.

## Why a target completion must choose a perfect matching

Use full graph labels0 for the distinguished root,1 for inner symbol0 and2
for its paired inner symbol1. The fixed neighborhood of vertex1 comprises
vertex0, vertex2 and the twelve outer vertices S bearing symbol0. The root
scaffold saturates degree14 at vertex1, so its neighborhood cannot grow.
For a target graph, each vertex w adjacent to1 has exactly one neighbor
inside N(1), because the off-diagonal target equation for (1,w) gives
|N(1) intersection N(w)|=1. Thus the induced graph on N(1) is1-regular.

Vertices0 and2 are adjacent. Vertex0 has no outer neighbors. Vertex2 has no
neighbor in S: outer labels contain at most one symbol from each root pair,
and all root-to-outer incidences are fixed by the scaffold. Hence {0,2} is
an isolated edge of this induced neighborhood. The remaining twelve vertices
S must induce a perfect matching. Within the declared scope, the only
unfixed edges in S are precisely the60 legal Y edges; the six same-fibre
pairs are prescribed absent and no fixed K edge lies within S. Consequently
the chosen matching is one of the6,040 legal assignments in the independent
complete list.

Equivalently, the set of target solutions in F is the union of the target
solution sets in F_M over the listed assignments. This is a statement about
potential target solutions, not equality between F and the union of all
partial graph states F_M: F also permits nonmatching Y patterns before
target constraints are imposed. The family exclusion did not require this
counting argument and is not6,040 independently solved LP instances.

## Boundaries of this review

No nontrivial automorphism is assumed. All labels and fixed coordinates are
retained. There is no claim that every unrestricted target admits this
specific162-edge configuration or its prescribed absences. No union is
computed with historical fixed-configuration exclusions; overlaps are not
added to any count. This note adds a scope interpretation, not a new exact
LP certificate or a recounting of the original list. The independently
checked domains, necessary moment model, exact certificate and their
availability remain dependencies of the family exclusion.

Overall search coverage: UNKNOWN; no validated denominator for Conway-99.
