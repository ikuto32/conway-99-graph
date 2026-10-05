# Order-eight marked extension endpoint null control

Discovery status: **CANDIDATE**, pending an independent raw-artifact check.
The exact statement proposed for checking is:

> The specified nonnegative integer vector of 1,223 induced-class aggregate
> counts satisfies all 4,543 equations in the frozen marked-extension model,
> has induced N3 count 4,158, and gives positive semidefinite 66-by-66 and
> 87-by-87 pair-root moment matrices under the frozen Wave147 coefficients.

This is one feasible aggregate count vector in a necessary relaxation. It does
not place vertices in a graph, establish all overlaps, exclude any target
graph, or provide a target-wide coverage fraction. No exact new bound is
claimed. Independent checking must bind the statement to the listed raw bytes;
producer calibration and this derivation do not approve the discovery.

## Frozen artifacts and conventions

- Model: `acceleration/results/20261002_order8_marked_extension_v4/model.json.gz`.
  Compressed SHA-256:
  `d3c36efaaf715eb6877bcf5931260581f7e60a490f4ab30f5cf91666218d4c35`.
  Decompressed payload SHA-256:
  `5dbde1ff01ebb32cc9b125ceb59d827e46dcdda307a2fc4df97f7ad10d6b5994`.
- Witness: `acceleration/results/20261002_order8_psd_cuts/integer_null_witness.json`.
  SHA-256:
  `97b3762b9559c5d7d7a93478b35909ed7faa4125ba60e1d016d85e7d2bd55a98`.
- Exact matrices and rational outer-product certificates:
  `acceleration/results/20261002_order8_exact_endpoint/`.
- Archived coefficient source:
  `external_conway99_research/attempts/wave147-alternative-lane/coefficients.json.gz`.
  Gzip SHA-256:
  `a46d8a8b6fd3ae339cdf7c9b633a661d917e3481bed762ae6aa70f1b4886cf1e`.
- Archived source repository:
  `https://github.com/YesterdaysLemon/conway-99-research`, pinned commit
  `85e705cc6c2a14d123120c93a847e30aaab1789e`, claim
  `C-WAVE147-PAIR-ROOT-001`. Its original identity and historical review are
  retained. The historical verifier sampled ordinary class coefficient
  reconstruction; this is not represented as fresh complete coefficient review.

The model's `variables` array is the complete zero-based index-to-graph mapping:
index `j` means the class `[h,m]` at that position. The graph has vertices
`0,...,h-1`. Bit positions enumerate `(u,v)` with `u<v` lexicographically;
bit one means an edge. Each value `x_j` counts unordered vertex subsets
inducing that unlabelled class.

For orders four through seven the frozen Wave45 masks use unrestricted
lexicographic labels. The new model relabels those masks into degree-cell
canonical labels: collect equal-degree cells in increasing degree order,
place the cells in consecutive target labels, and choose the least edge mask
among all permutations within those cells. Order-eight masks already use this
convention. These are explicit bijections of class identities; the archived
input bytes are never edited. Orders one through three are enumerated directly.
The class populations are `1,2,4,9,21,62,208,916` for orders one through eight.
Completeness beyond order three is an inherited premise of the frozen class
streams, with its historical provenance and limitations.

Each equation records its kind, smaller class order/mask, orbit mark (or null),
integer RHS, and sparse integer `[variable_index,coefficient]` terms. Its exact
meaning is `sum coefficient*x[index] = rhs`. The population has 8 total rows,
307 deletion rows, 1,233 vertex-orbit degree rows, and 2,995 unordered-pair-orbit
common-neighbor rows, with 35,761 nonzero coefficients. The orbits quotient marks
under `Aut(H)` of a small induced class only; no automorphism of a target graph
is assumed or required.

## Necessary counting derivation

For a class `H` of order `h<=7`, count pairs `(S,v)` where the induced subgraph
on `S` is `H` and `v` lies outside `S`.

1. Deletion: there are `(99-h)*x_H` such pairs. A larger induced class `K` of
   order `h+1` contributes once for each deleted vertex whose remainder is `H`.
2. Vertex-orbit degree: for a vertex orbit `O` of `Aut(H)`, the left coefficient
   is `sum_{u in O}(14-deg_H(u))`. For each deletion in `K`, translate the new
   vertex's neighbors into the canonical copy of `H`; its coefficient is the
   number of translated neighbors in `O`.
3. Pair-orbit common-neighbor: for an unordered-pair orbit `O`, the left
   coefficient is `sum_{uv in O}(t_uv-|N_H(u) intersect N_H(v)|)`, with `t_uv=1`
   on an edge and `t_uv=2` on a nonedge. Each deletion contributes the number
   of pairs of `O` lying wholly inside the translated neighbor set.

Choice of the translating isomorphism changes the marks only by `Aut(H)`, so
these orbit totals are well-defined. This is exact double counting with no
division by group orders. At each order the total row says
`sum_H x_H = binomial(99,h)`.

## Frozen pair-root PSD formula

Use the ordered adjacent or nonadjacent two-vertex root. A flag adds an
unordered free triple, with roots fixed pointwise and only free labels
identified. The ordered flag masks are stored in the archived Wave147
`exact-results.json` under each family's `flag_masks`. The basis dimensions
are 66 and 87. For a copy of class `H` of order `h` from five through eight,
`C_H` counts every ordered root embedding and every ordered pair `(P,Q)` of
free triples whose union is all `h-2` other vertices. Their intersection has
size `8-h`. Its symmetric upper-triangular integer entries are in the archived
gzip. Both off-diagonal entries are reconstructed from one stored upper entry.

For each actual root `theta`, let `c(theta)` count extensions by flag. Then

```text
M_family = sum_H x_H*C_H = sum_theta c(theta)*c(theta)^T.
```

Therefore these PSD conditions are necessary for every target graph under the
stated complete coefficient convention. The new endpoint integer vector gives
the following exact candidate decompositions, with the vectors supplied in
the certificate JSON files:

```text
M_ordered_edge    = 5544*u*u^T, dimension 66, rank 1.
M_ordered_nonedge = 8316*v*v^T, dimension 87, rank 1.
```

The weights are positive integers. Thus a checker can verify every matrix
entry by one integer outer product without using an eigensolver or trusting
the producer's LDL implementation. The moment source convention and raw
coefficient identity remain separate from this elementary PSD check.

## Discovery record and preserved failures

All invocations used the pinned `uv.lock` environment and the per-command
supervisor. Exact argv, current source commit, source/input/output hashes,
versions, and elapsed times appear in the saved manifests and receipts.

The first supervisor launch used an unqualified interpreter name that suspended
Windows process creation could not resolve; no worker was launched. Producer
v1 selected the pair-root stream, which stops at order six. Producer v2
mistakenly assumed the Wave45 mask convention was degree-cell canonical.
Producer v3 corrected the input translation, passed exact rook controls,
and built the entire model, but JSON serialization failed on a NumPy scalar
after its first LP completed. These failures and old source versions remain
unchanged. Producer v4 fixes serialization and explicitly reuses v3's completed
model. Its three HiGHS diagnostics give min approximately zero, max
approximately 4,158, and endpoint feasibility. They are not exact bounds.

Rounding the endpoint counts by at most `0.0028781890869140625` yields the
integer vector above. Producer exact evaluation finds no negative count and
zero failed rows. Its selected-PSD-cut loop finds no informative cut, and the
separate exact producer saves the two rank-one certificates. These outputs
are mathematical candidates pending an independent checking path.

The producer's positive control counts all induced subsets of the known
`srg(9,4,1,2)` rook graph under the corresponding `n=9,k=4` equations. It passes
every row. Deliberately altered edge counts and a degree coefficient are
rejected. The exact PSD producer also accepts a positive 2-by-2 matrix and a
zero matrix and rejects a deliberately indefinite 2-by-2 matrix. These are
producer controls, not independent verification.

If independently verified, this null control shows that these particular
marked count equations and pair-root order-eight PSDs do not alone exclude
the endpoint. A useful next layer would constrain mutually consistent rooted
extensions on larger unions, integer/local realizability, or a different
structural object. Repeating this same SDP cannot produce a valid strict upper
bound from only these frozen premises.

Subsequent same-wave work reconstructed all 2,414 archived coefficient matrices
and 272,054 nonzero upper entries with a separate adjacency-set implementation,
including a nonvacuous rook expansion control. See
`acceleration/results/20261002_wave147_all_coefficients/`. This strengthens the
historical sampled coefficient checking without re-enumerating the full class
universe or approving the new null witness by its producer. Root review remains
the separate approval path.

The selected root-local screen and the complete rooted five-flag systems are
documented in `docs/DERIVATION_20261002_ROOTED5_MOMENT_RIGIDITY.md`. They identify
an established five-vertex regularity theorem and explicit candidate target
vectors, explaining the endpoint's rank-one moments. No mathematical novelty
or new exclusion is claimed from that identification.
