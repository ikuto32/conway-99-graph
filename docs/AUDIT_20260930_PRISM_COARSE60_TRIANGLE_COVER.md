# Independent finite coarse-triangle census and witness review

The universe is all 34,220 unordered triples of the exact 60 labelled coarse
columns. The scope fixes the six-prism identity-cross core and this coarse
template. No complement pairing, bit normalization, target automorphism or
unrestricted target coverage is assumed.

For one component of a column triple, enumerate all eight coordinate-bit
assignments literally. The three selected row labels are (fibre,bit). They
are pairwise distinct precisely when all selected labels differ. This direct
table over all 27 fibre triples yields zero lifts when all fibres coincide,
four lifts when exactly two coincide, and eight when all three differ. In
the middle case the equal-fibre pair must use opposite bits. The six prism
components use disjoint row labels and disjoint variables, so these local
tables multiply. They characterize a single triple's disjointness completely,
independently of any global Gram equation.

The checker reconstructs every census record, all rejected components, all
required opposite-bit variable pairs, the contiguous admissible indices and
the exact product of local lift counts. It finds 18,440 admissible triples
and 15,780 rejected triples. This is complete coverage of that explicitly
frozen triple universe; it is not coverage of all factors or target graphs.

The saved 20-triple witness covers each of the 60 columns exactly once. Its
raw bits reconstruct the listed 36-row column supports, and all 60 pairs
within the selected triples are disjoint. The audit derives the prescribed
Gram directly from the literal 39-vertex partial adjacency and the target
identity, then computes all 1,296 entries of the witness Gram. Exactly 900
ordered entries disagree. This witness therefore demonstrates only the
coarse/local disjointness conditions, and is explicitly not a full factor.

The separate identity-cross completion premise has already been independently
checked in `AUDIT_20260930_IDENTITY_P_TRIANGLE_PARTITION.md`: an actual target
completion has 20 residual triangles partitioning its outside vertices.
For two vertices of one such triangle, the third is their unique common
neighbor. A shared core neighbor is impossible because lambda=1. Thus any
target completion within this exact coarse template must induce an admissible
triangle cover with the indicated opposite-bit conditions. Finding the cover
does not imply the converse; Gram equations and the residual graph remain.

The 25 recorded search nodes are independently checked as a finite traversal
record: remaining column sets, complete available triples, deterministic
minimum-degree branch choice, explored child prefix, local rejected subtrees
and successful covers. Every saved node must be reached once; cycles and
omitted branches are rejected. Stopping after a successful witness is allowed.
This review makes no exhaustive no-cover claim and does not rerun search.

Calibration runs before research checking: 216 component truth cases, all
190 pairs of three-sets on six vertices, a positive exact cover and corrupted
cover examples. Research corruptions change population records, local lift
counts, variable maps, bits, row supports, Gram claims and search-tree edges.
The checking code imports only the Python standard library. Shared raw inputs
and prior premise reports are disclosed; no producer or previous checker
implementation is imported.

The proposed claim is
`C-SIX-PRISM-COARSE60-DISJOINT-TRIPLE-CENSUS-AND-COVER`, revision 1, a VERIFIED/CLEAR
finite result conditional on its explicitly recorded scope and premises. No
target resolution, residual adjacency, performance guarantee or novelty is
claimed. Use a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_coarse60_triangle_cover.py --out build/coarse60-triangle-review-new
```
