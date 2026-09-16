# Exact computational elimination of the E0=80 branch

## Scope and structural completeness

Let `E0=C+Q` be the total number of outer edges whose endpoints have the same
two-group support.  The unconditional fibre-compression audit proves
`E0` is not 81, 82, or 83.  At `E0=80`, equality analysis forces exactly:

- 17 same-support fibres inducing `C4`;
- four fibres inducing `P4`;
- the four exceptional supports form a four-cycle on four of the seven
  groups; their overlap graph is `C4` and their disjointness graph is `2K2`;
- adjacent exceptional fibres have a two-edge perfect matching between their
  `P4` endpoints;
- opposite exceptional fibres have a two-edge perfect matching between their
  internal-degree-two vertices.

`scratch_general_e80_coverage_audit.py` independently enumerates all
`C(21,4)=5,985` exceptional-support sets.  Of these, 3,990 fail the required
block row sums, 1,890 fail the compression square bound, and exactly 105
survive.  They are the `C(7,4)*3=105` group four-cycles and form one `S7`
orbit.  Thus it is WLOG to use supports `(01,12,23,30)`.

There are `4^4 * 2^6=16,384` choices of the four labelled `P4`s and the six
exceptional two-point matchings.  Exact-symbol BP quotas leave 128.  The
effective residual action is the cycle `D8` together with independent flips
of its four groups, of order 128.  Direct orbit enumeration gives sizes
`16,32,32,32,16`.  An independent Burnside check gives fixed-point sum 640,
hence `640/128=5` orbits, and their sizes sum to all 128 configurations.

## Correct compact model

For a `C4` fibre `F`, the fibre common-neighbour identity has zero external
collision budget.  Consequently every vertex on a support disjoint from `F`
has exactly one neighbour in `F`, and overlapping supports have no edges to
`F`.  This gives three kinds of disjoint-support blocks after normalization:

- 67 `C4--C4` blocks are two-sided 4-by-4 permutation matrices;
- 36 `C4--P4` blocks have degree one only at every vertex on the `P4` side;
- the two `P4--P4` disjoint blocks are already fixed by the local orbit.

The asymmetry in the second item is essential: a `C4`-side vertex need not
have degree one in each individual `P4` block.  Its totals are coupled across
blocks by BP.

For each of the five local representatives,
`scratch_general_e80_compact_sat.py` leaves all 1,648 cells of the 103
variable blocks free, applies exactly the block conditions above, and then
encodes:

```
BP = PA0,
common_outer(u,v) + edge(u,v) = 2 - |label(u) intersect label(v)|
```

for every outer vertex/symbol and every one of the 3,486 outer pairs.  Every
AND helper is a full equivalence.  These equations are precisely the
root/inner and outer/outer blocks of the SRG matrix equation; fixed fibre and
overlap edges plus the 103 variable disjoint blocks exhaust every possible
outer edge in the classified branch.  Therefore the model is equivalent to
the complete rooted equations subject only to the rigorously derived
`E0=80` structure and a WLOG local-orbit representative.

## Terminal results

CaDiCaL 1.9.5 returned `UNSAT` on all five corrected branches:

| branch | orbit size | variables | clauses | seconds | conflicts |
|---|---:|---:|---:|---:|---:|
| `e80_o00` | 16 | 270,640 | 630,124 | 1.578 | 1,423 |
| `e80_o01` | 32 | 270,568 | 630,020 | 1.609 | 1,478 |
| `e80_o02` | 32 | 270,640 | 630,124 | 1.656 | 1,386 |
| `e80_o03` | 32 | 270,568 | 630,020 | 1.609 | 1,504 |
| `e80_o04` | 16 | 270,640 | 630,124 | 0.578 | 334 |

The independent OR-Tools model
`scratch_general_e80_compact_cpsat.py` uses `AddExactlyOne`, linear BP/pair
equalities, and `AddMultiplicationEquality`, rather than DIMACS cardinality
gadgets.  It returned `INFEASIBLE` on all five branches in respectively
19.515, 26.516, 18.562, 13.375, and 16.484 seconds.  Each model has 64,769
proto variables and 68,462 proto constraints.

These two agreeing terminal portfolios provide reproducible computational
elimination of `E0=80`.  They do not include DRAT/LRAT proof certificates, so
this is computational evidence rather than a formally checked proof.

## Superseded restricted-subcase run

An earlier model mistakenly imposed two-sided permutation matrices also on
the 36 `C4--P4` blocks.  Its fast UNSAT/INFEASIBLE results apply only to that
extra restricted subcase.  The files
`scratch_general_e80_compact_portfolio.json` and
`scratch_general_e80_compact_cpsat.json` are explicitly marked
`RESTRICTED_SUBCASE_*` and must not be cited as the `E0=80` result.  The valid
corrected logs are:

- `scratch_general_e80_corrected_sat_portfolio.json`;
- `scratch_general_e80_corrected_cpsat.json`.

Combining this corrected result with the separate computational elimination
of the `E0=84` all-`C4` class and the rigorous exclusions of 81--83 gives the
computationally conditional restriction `E0 <= 79` for any putative graph.
