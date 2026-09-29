# Independent necessity derivation for the eight-coordinate moment model

This document specifies the checking argument before the new full model is
available. It does not assert that a serialized matrix has passed its audit.
The corresponding checker is
`acceleration/audit_20260930_eight_filtered_moments_v1.py`. Running it requires
the completed model and separately authenticated domain and filter audits.

## Exact family and premises

Fix the recorded root scaffold and the eight-coordinate family derived from
baseline candidate 18481. The 120 retained outer K edges are fixed; all
recorded other absences remain fixed. Let `E` be the 2,160 unknown outer pairs,
including 480 freed same-sign coordinate edges and 1,680 disjoint-support
pairs. This is a conditional family, with no nontrivial automorphism assumed.

For each outer vertex `u`, let `B(u)` be its fixed outer neighborhood and
`H_u` its complete local-star domain after the necessary neighborhood-matching
filter. The two independently checked premises required by the encoding are:

1. Every completion in the family chooses a member of the recorded complete
   local domain at each center.
2. Every such choice survives the recorded matching filter. A positive
   matching witness is only a necessary condition; no joint validity of its
   individually permitted edges is assumed.

The checker must authenticate the exact domain/filter revisions and all raw
center tables before using these premises. It must reconstruct retained
original IDs as the complement of the exact independently checked rejection
sets. A missing or incomplete filter audit does not satisfy this gate.

## Rows and coefficients

There is a nonnegative variable `x[u,S]` for each retained original star
`S in H_u`. Its full outer neighborhood is `F(u,S) = B(u) union S`.

For each of the 84 centers, the simplex row is

```text
sum_{S in H_u} x[u,S] = 1.
```

For each unknown pair `a < b`, reciprocity is

```text
sum_{S in H_a, b in S} x[a,S]
  - sum_{S in H_b, a in S} x[b,S] = 0.
```

For each of the 3,486 outer pairs `a < b`, let `L_a` and `L_b` denote their
two fixed root-neighbor symbols, and `B_ab` the fixed outer-edge indicator.
The full-neighborhood moment row is

```text
sum_{u,S} [a,b both in F(u,S)] x[u,S]
  + [ {a,b} in E ] sum_{S in H_a, b in S} x[a,S]
  - slack_minus[a,b] + slack_plus[a,b]
  = 2 - |L_a intersection L_b| - B_ab.
```

Both slack families are nonnegative. Every star variable has objective
coefficient zero and every slack has objective coefficient one. There are
5,730 equality rows: 84 simplex, 2,160 reciprocity, and 3,486 moment rows.
There are exactly 6,972 slack columns in addition to the retained star
columns. All lower bounds are zero; all upper bounds are positive infinity.

The coefficient of a single star column is thus independently reconstructible
from its raw neighbor mask. The first sum in a moment row contributes one
for each unordered pair in the full outer neighborhood. The second term
assigns unknown adjacency exactly once, through the smaller endpoint. These
two contributions cannot collide within one column: the center is never a
member of its own neighborhood. Coefficients are therefore exactly `+1` or
`-1` at the recorded nonzeros; zero entries are omitted.

## Conditional necessity proof

Assume an SRG completion in the prescribed family exists. At each center
choose its unique actual outer star, set its variable to one, and set every
other star variable to zero. The complete-domain and sound-filter premises
put all these chosen variables in the serialized model's retained universe.
Each simplex is satisfied. Undirected adjacency gives every reciprocity row.

For an outer pair `a,b`, the first moment sum counts its actual common outer
neighbors. Its fixed root-neighbor contribution is exactly
`|L_a intersection L_b|`; the distinguished root is adjacent to neither
outer vertex. The SRG identity gives

```text
common_outer(a,b) + unknown_adjacency(a,b)
    = 2 - |L_a intersection L_b| - B_ab.
```

Thus all moment equations hold with both slacks equal to zero. The objective
is zero. Consequently, every completion in the family induces a zero-objective
feasible point of this necessary LP, provided the serialized rows, coefficients,
selection, costs, and bounds match the independently derived definitions.

The converse is not claimed. Fractional variables can satisfy these equations
without describing any graph. A model check establishes neither a positive
lower bound nor an exclusion; a later exact bound requires its own independent
verification. Nothing in this conditional implication is an unrestricted
normalization or target-level proof.

## Planned exact artifact checks

The checker uses no producer sparse-builder code. Before loading the large
matrix it generates the 3-by-3 rook graph independently and checks all nine
roots with zero and one fixed actual outer edges. These 18 known-valid
one-hot witnesses must satisfy the independently constructed equations.
Altered coefficient and right-hand-side fixtures must fail, as must altered
individual column coefficients.

For the actual model, every retained column is reconstructed from the raw
full neighborhood; every slack column, right-hand side, cost, bound, original
ID, and offset is checked. Sparse coefficients must have exact integer type,
canonical indexing, and no duplicate or zero entries. Public byte parts are
compared sequentially to the exact audited raw bytes and checked by SHA256.
The checker shares NumPy/SciPy sparse storage and format conversion with the
producer, but does not use its construction routines or generated expected
columns. This trusted component is disclosed.

The run has a declared 1,800-second wall cap and immutable center receipts.
Array memory estimates are saved before sparse loading; these estimates are
not claims about measured peak memory. A stopped or failed check does not
establish complete encoding correctness. Actual result and scope promotion
must be recorded by a later immutable audit report.

## Completed artifact audit

The planned audit completed successfully at
`2026-09-29T19:40:28.188781+00:00` from recorded source commit
`dacbbaa157f30182f877dc38b2017f790ddc5938`. The immutable report is
`acceleration/results/20260930_independent_review/eight_filtered_moments/summary.json`,
SHA256 `7a1537ce139db72d48da277deabb7022788cde365bc5ff6c853206ac2dd2ebb5`.

It checked all 1,875,214 retained original star columns, all 6,972 slack
columns, all 156,321,767 exact integer nonzeros, and the full 5,730-row
system. The 414,908 removed choices are the independently authenticated
matching-filter rejections from the original 2,290,122-choice population.
Every bound, cost, RHS, original-ID map, offset, and distributed byte-part
identity passed. All 18 independently generated rook9 calibration cases
and their coefficient/RHS corruptions passed.

The audit recommends **VERIFIED** for
`C-PARTIAL-K-EIGHT-COORDINATE-MATCHING-FILTERED-MOMENT-ENCODING`, revision 1,
with the exact conditional necessity statement above. No solver was launched
by this audit, and no positive bound, family exclusion, target graph, or
unrestricted nonexistence result follows from this encoding verification.
