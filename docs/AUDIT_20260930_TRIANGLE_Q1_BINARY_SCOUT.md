# Independent three-factor and row27 audit

The fixed core is T=K3 with three named12-vertex cells, standard matching
inside each, cross matchings I,I,shift6, and the canonical C0 whose columns
are the60 lexicographically ordered nonmatching pairs on twelve labels.
No nontrivial automorphism of a hypothetical target is assumed. All claims
here concern explicitly saved finite objects.

## Raw factors and exact scope

For each saved Q1 permutation, reconstruct C1[a,d]=1 iff a belongs to
E[Q1[d]]. The checker builds the full raw99 partial graph from this definition,
the core and C0; C2 and the60-vertex residual graph remain entirely unknown.
It compares every entry with the saved raw99 artifact. No forced assignments
or template copied from another factor are used.

For the cubic36-vertex inner core adjacency L, the target identity implies

    C C^T =12I-L-L^2+2J-diag(J12,J12,J12).

The checker computes this expression by integer matrix multiplication and
extracts its first24 rows and columns. It independently computes every
entry of(C0;C1)(C0;C1)^T and checks equality, plus row/column degrees.
This avoids the producer's hand-written G01 formula and bitset Gram routine.
The two archived Q1 matrices are fetched from their pinned Git blobs and
checked afresh as controls; historical verification labels are not inherited.

## Complete restricted coordinate orbits

Every permutation commuting with M=(01)(23)... chooses a permutation of its
six pairs and one orientation per pair:46,080 possibilities. The independent
checker constructs this entire finite universe and retains exactly those
also commuting with P=shift6. Exactly384 remain. This proves completeness
of the named coordinate group, without claiming completeness for other
notions of graph isomorphism.

Such a permutation p acts on the60 C0 columns by its induced edge permutation
pE. Literal incidence comparisons check C0[p(a),pE(d)]=C0[a,d] and the
prescribed Gram's invariance. The transported Q1 is defined by

    Q1'[pE(d)] = pE(Q1[d]).

Every transported C1 is checked by the analogous literal incidence identity.
All images of all five factors are computed and saved, and the five complete
sets must be pairwise disjoint. This verifies three additional coordinate
orbits relative to the two exact archived inputs, only under this group.
It is not an enumeration of all possible factors or target graphs.

## Row obstructions

For u=27, all60 outside entries remain unknown. Degree14 minus its four
known core neighbors forces exactly ten selected outside entries. Every
row at vertices3,...,26 is completely fixed, yielding24 exact common-neighbor
equations. For each pair of outside endpoints already having their maximum
known common neighbors, both cannot become neighbors of u. Direct raw99
reconstruction gives108 such incompatible pairs per factor.

These133 necessary constraints need not be sufficient for a full completion.
Their infeasibility nevertheless excludes the respective exact factor.
The frozen independent checker from the earlier row29 audit is reused with
its source hash bound. It checks each forced bit by giving it the opposite
value and deriving an impossible interval, demands both children of every
split, validates every contradictory leaf, and rejects cycles, reused or
unreachable nodes. Every actual raw certificate is checked completely.

Small SAT and UNSAT truth-table controls and a masked known-valid rook graph
are rerun. Each actual row proof is corrupted by removing a branch, changing
a force, and falsifying a leaf counter; all must be rejected. Factor and
coordinate-map corruptions are checked separately.

The saved512,000-swap annealing attempt with zero new zero-score hits is
preserved and hash-bound. This audit does not rerun that heuristic or claim
its statistics as independently reproduced research coverage. No failed
attempt or raw artifact is overwritten.

## Replay

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_q1_binary_scout.py --out acceleration/results/20260930_independent_review/triangle_q1_binary_scout
```

Use a new output directory. All raw factors, matrices, orbit maps and images,
trees, commands, source hashes and exact results are retained. The locked
environment is unchanged. No producer implementation or SAT solver is used.
