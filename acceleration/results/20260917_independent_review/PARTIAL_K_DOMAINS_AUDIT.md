# Independent partial-K domain completeness and cap review

The complete checking record is `partial_matching/summary.json`, SHA256
`ed1d5b464466562cff722e45593095ec89c63bda761cfa7f784994abfc308b17`.
It supports `C-PARTIAL-K-ONE-COORDINATE-DOMAINS`, revision 1, within the
precise restricted scope below. Its 84 per-center records and preregistered
checking manifest are saved beside it. The checker imports no producer.

Starting from the fixed baseline18481 labeling, exactly six edges of the
root-group-0, same-sign-0 matching are removed. The other 162 overlap edges
remain present. Same-fibre and unlisted other-coordinate edges remain absent.
There are exactly 60 support-permitted unknown matching edges on the twelve
affected vertices, plus the original 1,680 disjoint-support unknown edges.
This is one conditional family, not all normalized targets.

An affected center needs nine further neighbors; each other center needs
eight. Each domain consists exactly of incident unknown-edge subsets that
complete the center's degree, respect every partial full99 common-neighbor
cap, and attain all fourteen exact root-neighbor common-count quotas.
Independent enumeration reproduces all 54,478 choices in all 84 raw tables.
All 26,250 saved baseline choices embed by restoring the removed incident
matching edge when applicable. Two restricted universes are checked by brute
subset enumeration, and an empty corrupt star is rejected.

The independent search branches differently from the producer. At every
node it chooses the first unsatisfied root symbol and branches over every
subset of remaining candidates of exactly that symbol's remaining demand.
It then removes all candidates containing the now-satisfied symbol. Every
valid completion has exactly one such demanded subset, so these branches
cover all completions without duplication. The process terminates because
each branch satisfies a further symbol.

Pruning is sound. An individually invalid added edge cannot become valid after
positive additions. For a center x and another vertex w, adding x-v raises
`(B²+B)_xw` by exactly `B_wv + [w=v]`; the resource capacity test records this
nonnegative increment. For a pair of newly chosen endpoints v,w, their common
center creates one new common neighbor, so a pair already at its fixed cap
cannot be chosen together. Other non-center cap changes involving a fixed
neighbor were already covered by the single-edge test. Root-symbol demands
are exact and nonnegative, so exceeding one cannot be repaired. Finally every
accepted leaf is independently checked by directly constructing its full99
partial adjacency and testing all caps and quotas. Completeness therefore
does not rest on matching output counts alone.

The checker separately reconstructs all 3,486 retained outer-pair linear
caps on the 1,740-edge unknown universe from the direct derivative
`BE+EB+E`. For a completion A=B+E, the remaining contribution E² has
nonnegative off-diagonal entries. Thus the saved caps are necessary after
discarding that contribution. This checks the integer cap data, not a
serialized complete solver matrix, which was not supplied in the pilot.

No exact LP feasibility, positive lower bound, family exclusion, or target
resolution is established. The new domain/objective differs from the old
fixed-K star objective, so its floating score is not an incumbent improvement.

The separately checked saved-point report `partial_oddsets.json`, SHA256
`d36ba6b7389b1f98075285ab0182b412d3122255c94a2bf069ade3061865e8ff`,
uses exact integer-scaled representations of every stored binary float and
normalizes each star simplex rationally. Among all 2,048 odd subsets, only
mask2047 has a positive excess, about 3.9214e-15. All 1,024 complement identities
are checked with their projected degree defects. Projected degrees and
reciprocity are not exact; this is a diagnostic of one saved rational point,
not a structural matching obstruction or feasibility certificate.
