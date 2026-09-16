# E0=78 K2,3 orbit 3 / local representative 6 encoding audit

This is a branch audit, not an exhaustive E0=78 or full 99-graph result.
Representative 6 is one of eight inequivalent local K2,3 graphs.  Its orbit
has size 96; the eight orbit sizes sum to 512.

## Coordinates and fixed structure

The 84 outer vertices are the unordered symbol pairs `{a,b}` from `0..13`
with `a//2 != b//2`.  Their support is `{a//2,b//2}`.  There are 21 support
fibres of four vertices each.

The six exceptional P4 supports are

```
(2,5) (2,6) (3,5) (3,6) (4,5) (4,6).
```

They form K2,3 as edges on the seven support groups.  The other 15 fibres are
the unique coordinate C4s.  Among the `C(84,2)=3486` outer pairs:

* 90 fixed present: 60 ordinary-C4 internal, 18 exceptional-P4 internal,
  and 12 exceptional-overlap edges from representative 6;
* 1716 fixed absent nondisjoint-support pairs;
* 1680 initially variable pairs, namely 105 disjoint-support 4x4 blocks.

The JSON field `fixed_absent_nondisjoint_outer_pairs_zero_based` contains only
the 150 absent nondisjoint pairs among the 24 exceptional local vertices.  It
must not be mistaken for the complete set of 1716 fixed absent pairs.

The 105 variable blocks split into 51 C4--C4, 48 C4--P4, and 6 P4--P4
blocks.

## Sound block consequences

For a coordinate C4, every pair already exhausts its same-fibre outer-pair
equation internally.  Hence an outside vertex has at most one neighbour in
that C4.  BP gives outer degree 12.  An ordinary-fibre vertex has internal
degree 2 and no overlap-support neighbours, so all ten disjoint blocks have
total size four.  Therefore:

* each C4--C4 block is a 4x4 permutation matrix;
* in a C4--P4 block, every P4 vertex has exactly one neighbour in the C4;
* imposing the converse, one neighbour in the P4 for every C4 vertex, is not
  justified and can overconstrain the branch.

For representative 6, aggregate BP by support group fixes both row counts of
every exceptional vertex into its two disjoint exceptional fibres.  Across
the 48 directed rows, 12 targets are zero and 36 are one.  Equivalently, each
P4--P4 block has one prescribed zero row, one prescribed zero column, and a
3x3 permutation matrix on the remaining cells:

| supports | zero vertex on left | zero vertex on right |
|---|---:|---:|
| (2,5)--(3,6) | 64 | 87 |
| (2,5)--(4,6) | 72 | 95 |
| (2,6)--(3,5) | 75 | 84 |
| (2,6)--(4,5) | 67 | 88 |
| (3,5)--(4,6) | 78 | 91 |
| (3,6)--(4,5) | 81 | 92 |

The table uses one-based graph vertices.  Thus each low--low block has exactly
three edges.  Forty-two cells are safely fixed absent, leaving 1638 genuine
edge variables.  A direct block encoding can use 42 negative units and, per
block, exact-one constraints on the three active rows and three active
columns.

The block totals are consequently 4 on the other 99 disjoint blocks and 3 on
the six P4--P4 blocks.  They contribute `99*4 + 6*3 = 414` variable edges;
together with the 90 fixed edges this gives all 504 outer edges.

## Exact equations

There are 1176 BP equations.  Their target histogram is 336 equations with
target 1 and 840 with target 2.  For every outer pair `u,v`, impose

```
e(u,v) + sum_{w != u,v} (e(u,w) AND e(v,w))
    = 2 - |label(u) intersect label(v)|.
```

There are 3486 such equations, with target histogram `{1:924, 2:2562}`.
After the 90/1716 base fixed-edge simplification, the exact encoding has
65520 nonlinear AND terms, 7200 direct terms, and 108 fixed common-neighbour
terms.  No symbolic equation contains a duplicate literal and no fixed part
already exceeds its target.  After eliminating the 42 additionally forced
low--low zero cells, these counts become 62376 AND terms, 6972 direct terms,
and 108 fixed terms.

Because these constraints are equalities, each helper must be a full
equivalence `z <-> (a AND b)`.  Using only `(a AND b) -> z` or only
`z -> a,b` is unsound here.  The three clauses
`(-a,-b,z)`, `(a,-z)`, `(b,-z)` are correct.

The fixed inner common neighbours contribute
`|label(u) intersect label(v)|`; omitting this subtraction changes both
targets.  Same-support pairs (126 of them) must remain included unless their
equations are separately proved and encoded.

## Independent seed checks

`scratch_root_e78_k23_rep6_layer.json` was checked without importing a search
generator or existing verifier.  It has the exact rooted scaffold, 693 unique
edges, degree 14 at all 99 vertices, exact BP, exact 126 same-support pair
equations, and satisfies every block consequence above.  It is not a full
SRG: energy 3574 and 2104 bad pairs.

The machine-readable audit is
`scratch_e78_rep6_encoding_audit_subagent.json`.

The baseline CNF in `scratch_fibre_e78_rep6_exact_sat.py` matches the safe
1680-variable specification and explicitly avoids the unsafe C4-to-P4
converse.  Its encoder-dependent counts are 280410 total variables, 652760
clauses, and 65520 product helpers.  CaDiCaL 1.9.5 and 3.0.0 both reported
UNSAT for that same CNF.  The emitted DRAT trace has not yet been checked by
an independent proof checker, so it should not be described as a certified
UNSAT proof until that step is done.
