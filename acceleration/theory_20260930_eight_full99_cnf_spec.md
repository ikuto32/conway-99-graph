# Preregistered full99 eight-coordinate SAT encoding build

Frozen before production build. This is a new direct integer completion model
for the already pinned eight-coordinate family. No solver invocation is part
of this build, and no research solve may start before an independently authored
whole-clause and mathematical-necessity gate passes.

## Frozen question and scope

Construct a CNF equivalent to the full99 SRG equations within the exact family
recorded by `results/20260917_partial_eight_matchings/manifest.json`:189 root
scaffold edges and120 outer K edges fixed present;2160 outer pairs variable
(480 released same-sign-coordinate plus1680 disjoint-support pairs); all other
prescribed pairs absent. The source manifest and independent domain binding
are hash-bound by the build receipt. No target automorphism or unrestricted
family coverage is assumed. A SAT model could be a target graph only after a
complete independent full99 validator passes; UNSAT would concern this family.

## Direct equations and exact gates

Allocate one Boolean variable per unknown graph edge. Fold fixed0/1 entries
when forming all99 equations `sum_v A[u,v]=14` and all4851 inequalities
`sum_w A[u,w]*A[v,w]+A[u,v] <= 2`. Each product of two unknown edges has a fresh
helper with the three clauses expressing exact AND equivalence. Products with
constants are folded; constant row contributions reduce integer bounds.

Each remaining nonconstant cardinality row uses exact prefix thresholds:
`t(i,j) = t(i-1,j) OR (x_i AND t(i-1,j-1))`, with `t(i,0)=true` and `t(i,j)=false`
for `j>i`. Compute only thresholds through bound+1. A full bidirectional AND,
OR or combined OR/AND gate is emitted after constant folding. Exact-degree
rows assert threshold k and forbid threshold k+1; upper caps forbid k+1.
Every input, bound, state reference and graph/product variable is preserved in
the raw model, enabling reconstruction without importing producer code or a
third-party cardinality generator.

For a symmetric binary zero-diagonal graph of degree14, the sum of common
neighbor counts over unordered vertex pairs is `99*C(14,2)=9009`. There are693
edges. Thus the sum of all cap left sides is9702, equal to `2*C(99,2)`.
All4851 integer inequalities must be equalities. Hence they give common counts
1on edges and2on nonedges and exactly `A^2=12I-A+2J`. The converse is immediate
from that identity. This derivation and the actual encoding require independent
review; the producer does not approve its own equivalence claim.

## Controls, resource caps and artifacts

Before the research build, exhaustively check small threshold rows and all
Boolean gate assignments, including deliberately wrong auxiliary assignments.
Calibrate a separate pure-integer adjacency validator on the pentagon,3x3rook,
Petersen,triangular5 and Clebsch graphs with their correct SRG parameters and
loop, symmetric-edge-flip, asymmetric and nonbinary corruptions. No known-valid
99-target fixture is available, and none is invented.

The build is capped at120seconds and8GiB process working-set memory, checked
periodically while clauses are written. A cap or failure preserves partial
outputs and records no completed encoding. No mathematical floating acceptance
threshold exists. Use exact Python integers and immutable output directories.
Save the source commit, exact command/cwd, Python/platform/uv-lock identities,
all raw input/output hashes, full known/free99scaffold, edge/product/state maps,
counter controls and validator controls. Gzip-package completed large artifacts
as independently hashed binary chunks each strictly smaller than10MiB; record
ordered concatenation and decompression instructions. Raw artifacts remain
available locally and compressed chunks permit public reconstruction.

The solver environment remains pinned under `acceleration/environments/rook-sat`.
The producer imports no solver and no third-party cardinality encoder. Any later
solver call and proof trace will use a separate protocol and independent gate.
