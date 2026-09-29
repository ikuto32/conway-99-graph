# Independent rook-cell necessity, compatibility, and census audit

Auditor: `Codex subagent /root/state_literature_audit`. Discovery agent and
producer implementation are separate. Status: **PASS within the exact scopes
below**. Timestamp, source commit, commands, environment and artifact hashes
are in [audit.json](audit.json), SHA-256
`c014761ebd559f01127a3c4cf9a0e5c72316fcbacb0ea384f5483b8b6209d7d8`.
The [protocol](PROTOCOL.md) was saved before execution. The independent checker
is `acceleration/audit_20260930_rook_cell_independent.py`.

## Bound claims

`C-ROOK-CELL-LOCAL-FACTOR-COMPATIBILITY`, revision 1:

For every target containing an induced rook9, at each ten-vertex outside
cell the four degree-two incidence blocks necessarily obey
`sum C_j C_j^T = 7I + J - F`, and the pinned raw witness satisfies this
identity with simple binary degree-two blocks and compatible individual
right-cell perfect matchings.

This claim has two quantified parts: necessity for every target satisfying
the explicit rook-containment premise, and the existence of the saved local
matrix witness. It says nothing about compatibility of all nine outside
cells. It depends on `C-ROOK-NINE-REGULAR-SET-ENCODING` revision 1 as a
`uses_result` dependency. The prior verified encoding's recheck artifact is
hashed in this report; its entire historical replay was not repeated here.

`C-ROOK-CELL-TWO-FACTOR-CENSUS`, revision 1:

Exactly 89,000 labelled simple spanning two-factors of K10 avoid the fixed
matching `{(0,1),(2,3),(4,5),(6,7),(8,9)}`, and the pinned
`factor_masks.txt` contains each exactly once.

This second claim concerns a finite local graph population. It has no
unrestricted Conway-99 coverage interpretation and is not necessary merely
to verify the saved compatibility witness. Neither claim excludes a target.

## Independent necessity derivation

Take the previously established conditional rook representation
`A=[[B,T],[T^T,H]]`, with nine ten-vertex cells and `T=I9 tensor 1_10^T`.
For a target satisfying that representation,

```text
TH = (2J9-B-I9)T,
H² = 12I90-H+2J90-T^T T.
```

For an external vertex in cell i the first equation gives exactly one
neighbor in cell i, one in each of the four rook-adjacent cells, and two in
each of the other four cells. Symmetry therefore forces the internal block
F to be a perfect-matching matrix, the four adjacent-cell blocks P to be
permutation matrices, and each of the remaining four blocks C to have
binary entries and row/column sums two.

In the diagonal cell block of the second equation, `T^T T` is `J10`.
Because `F²=I10` and each `P P^T=I10`, block multiplication gives

```text
I10 + 4 I10 + sum C C^T = 12 I10-F+J10,
sum C C^T = 7 I10+J10-F.
```

Every Gram summand has diagonal two and nonnegative integral entries.
The off-diagonal total is zero on F and one on all other pairs. Thus each
individual off-diagonal entry is zero or one, no summand uses an F edge,
and every permitted pair occurs in exactly one summand. Since
`C C^T 1 = 4 1`, deleting its diagonal leaves degree two at every vertex.
The four simple spanning two-factors partition `K10-F`. This also forbids
a four-cycle in each bipartite C block. Its connected components have even
cycle lengths `2m`, with `m>=3`; their left-side projections are m-cycles.
The only possible partitions of ten into integers at least three are
`10`, `3+7`, `4+6`, `5+5`, and `3+3+4`.

An individual right-cell matching F_j must also avoid pairs of right
vertices sharing a neighbor in the left cell: such a matched pair already
has its common rook neighbor. The supplied four right matchings obey this
additional necessary condition. Their existence does not enforce the
remaining right-cell diagonal equations or any cross-cell equation.
No relabeling argument here assumes a graph automorphism.

## Exact raw witness checks

The verifier read the unmodified JSON witness with SHA-256
`da71c5381af0a68f8a7e7dea36535b92cbcfc67d95e3b57d6cc3591dd1dda33f`.
It checked all 100 entries of the summed Gram identity, every binary
incidence entry, all row/column degrees, mask/edge/incidence consistency,
the perfect matching, the disjoint partition of all 40 allowed edges, and
all four right matchings. Each factor has cycle partition `3+3+4`.
The summed integer residual has zero nonzero entries.

Six corrupted witness controls were rejected: missing edge, altered
incidence entry, overlapping factors, repeated matching endpoint, altered
saved total, and a right matching producing a forbidden triangle.
The report preserves the individual rejection reasons.

## Independent complete census

The enumeration algorithm was not imported or rerun. Instead, for every
vertex subset S, an independent Hamilton-path dynamic program starts at
the least vertex and counts paths visiting exactly S. Closing those paths
to their start counts both orientations of each undirected simple cycle,
so division by two is exact. The recurrence never reuses a vertex and
never traverses a forbidden edge.

A second recurrence partitions the full vertex set into cycles. It picks
the subset containing the least remaining vertex, multiplies its cycle
count by the recursively counted complement, and accumulates counts by
component sizes. That anchor distinguishes the component order uniquely;
cycle direction was already removed by the factor of two. Induction on
the number of remaining vertices proves that every labelled two-factor
is counted exactly once.

All 89,000 raw masks were then decoded independently using lexicographically
ordered allowed unordered pairs. The checker established validity, distinctness,
and the same cycle-type counts as the DP. Since a distinct valid subset has
the cardinality of the entire independently counted finite universe, it is
the complete universe. This is full coverage of the named local population,
not a sampled check.

| Cycle partition | Independent DP and raw-artifact count |
|---|---:|
| 10 | 56,256 |
| 3+7 | 13,440 |
| 4+6 | 11,680 |
| 5+5 | 5,664 |
| 3+3+4 | 1,960 |
| Total | 89,000 |

Positive DP controls on complete graphs K3, K4, K5, K6 and K10 match the
standard factorial cycle counts, including all 286,884 unfiltered K10
two-factors. Three census corruption controls reject a repeated mask,
an incomplete population and a bit outside the 40-edge universe.

Trusted components shared with the producer are the Python interpreter,
standard library and tqdm; no research code or numerical solver is shared.
The mathematics of the two recurrences is supplied above, not inferred from
agreement with the producer. Nine corrupted controls passed in total.

## Boundaries

There is no complete 90-by-90 H or 99-by-99 target matrix here. Equations
between different right cells, off-diagonal blocks of H², full right-cell
diagonal equations and target eigenvalue multiplicities are untested.
Rook containment is a premise, not a theorem about every possible target.
The failed attack is specifically that the stated one-cell necessary
conditions might themselves already be inconsistent: the raw witness
demonstrates their consistency. General existence and nonexistence remain
**UNKNOWN**. Overall search coverage: UNKNOWN; no validated denominator.
