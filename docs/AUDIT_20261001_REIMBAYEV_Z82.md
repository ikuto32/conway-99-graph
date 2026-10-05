# Independent review of one conditional seven-vertex count

Reviewer: `/root`, separate from producer `/root/state_literature_audit`.
Completed written review: 2026-09-30T17:03:51+00:00 (2026-10-01 in Japan).
Source commit: `cc55ad8bd7ad3ef35d33cae35232f9cc8eb264e5`.

**PASS within the exact scope below.** This adds no exclusion. The arithmetic
report is `acceleration/results/20261001_independent_review/reimbayev_z82/summary.json`,
SHA256 `9f270d2792de23296d8348cf9911aaed7c24be12fc3535f0a3f0409e7cc35278`.
Its complete command, input/output hashes, interpreter, controls and timings are
saved in that report. It completed in 1.140 seconds with no solver calls.

Let H consist of two disjoint triangles and exactly two matching cross edges.
In any srg(n,k,1,2), an outside vertex has at most one neighbor in either
triangle, hence at most two in H. There are 6k-16 incidences from H to its
complement. Summing prescribed common-neighbor counts over H's eight edges
and seven nonedges gives 22. H itself contributes 14, so precisely eight
outside vertices have two neighbors in H. The counts with one and zero
neighbors are consequently 6k-32 and n-6k+18. These are conditional identities;
they assert neither that an H copy exists nor that a target graph exists.

Every H has n-6k+18 isolated extenders. Conversely H plus an isolated vertex
has exactly one isolated vertex, giving a bijection. Thus the induced subset
counts satisfy z82=(n-6k+18)n3, specializing to z82=33n3 for the target.
This derivation uses no triangle normalization, support, automorphism or
archived spectral/lattice bound.

The primary source is Reimbayev, arXiv:2608.19410v1, Section 2, unnumbered z82
formula on PDF page 10. The exact TeX formula was checked against the downloaded
source archive. On 2026-09-30 at approximately 17:03 UTC I visually inspected
the versioned PDF at `https://arxiv.org/pdf/2608.19410v1#page=5` in Chrome:
panel 82 shows two disjoint triangles joined by two horizontal matching edges,
and a seventh isolated point above. The unchanged transparent figure extraction
was initially illegible in the image viewer; that observation alone was not used
to approve the panel alignment. The browser screenshot is an observed checking
path, not a saved public artifact; no screenshot hash is invented.

I inspected the pinned archive's
`attempts/wave23-weighted-extensions/model.py` row construction (lines 436-573).
It gives one deletion contribution per distinguished root, one contribution
for every neighboring vertex to its unique vertex orbit, and one per unordered
neighbor pair to its unique pair orbit. Therefore the sum of vertex rows is d
and the sum of pair rows is binom(d,2), without extra orbit-size division.
The corresponding right sides sum to (n-6), (6k-16), and 8 per H copy.
Deletion minus the vertex sum plus the pair sum has coefficient
1-d+binom(d,2), equal to the isolated-extender indicator for d<=2. This
establishes the claimed overlap with those row definitions.

The independent code imported neither the producer nor the archive model. It
used adjacency sets and recognition by actual disjoint triangles/matching cross
edges, instead of their permutation-orbit/bitset path. It checked every root
contribution on all 208 saved archive masks and all64 possible H attachments.
The single selected archive coordinate is 23265=33*705, with zero slope in its
Hamiltonian parameter. This does not reapprove the archive's full matrix,
feasibility interval, rank, completeness classification or endpoint bounds.
The immutable archive is YesterdaysLemon/conway-99-research at
`85e705cc6c2a14d123120c93a847e30aaab1789e`; its historical related record is
`CLAIMS.yaml`, original ID `C-WAVE23-WEIGHTED-EXTENSIONS-020`.
That historical VERIFIED label is not a fresh dependency or approval here.

The independent validator accepted the 3x3 rook SRG and rejected diagonal/edge
corruptions. H recognition accepted H and rejected one-cross and three-cross
variants. The exact 243 adjacency matrix was revalidated; its complete census
of disjoint triangle pairs has 133650 zero-cross, 240570 one-cross and 8910
three-cross pairs, with zero two-cross pairs. Hence this is a vacuous H control.
The nonvacuous synthetic local fixture satisfies all six core degrees and 15
core pair equations, but is explicitly not a full SRG. Changed coefficient,
histogram, archive coordinate and falsely nonvacuous controls were rejected.
The original producer's failed control expectation remains preserved.

Trusted/shared components are Python exact integer arithmetic and the raw
primary/archive input bytes. This is internal independent derivation and raw
artifact checking, not external review. It establishes only one conditional
identity and its redundancy in the inspected row families. No claim about the
other 207 paper formulas, literature novelty, or target resolution follows.
