# Canonical C4-fibre ansatz: exhaustive computational elimination

## Scope

This result concerns only the **canonical C4-fibre ansatz** used by
`scratch_canonical_blocksat.py`:

- the 84 vertices outside a fixed vertex and its 14 neighbours are
  `(ij,a,b)`, with `ij in C([7],2)`;
- every four-state fibre `ij` contains the fixed Hamming-distance-one `C4`;
- overlapping distinct fibres have no edges;
- every disjoint pair of fibres carries a perfect matching.

Fixing those 21 internal `C4`s is an additional assumption.  It is **not** a
WLOG reduction for an arbitrary `srg(99,14,1,2)`.  Therefore the result below
does not solve Conway's 99-graph problem and produces no `submission.txt`.

## Why the four branches are exhaustive

A matching between two four-state fibres is an element of `S4`.  The allowed
coordinate sign flips and the interchange of the two coordinates in either
fibre induce an independent square automorphism group `D8` at each endpoint.
Direct enumeration of all 24 permutations gives two `D8 \\ S4 / D8` double
cosets, of sizes 8 and 16.

1. If at least one of the 105 matchings is in `D8`, transitivity of `S7` on
   disjoint fibre pairs moves it to `01--23`, and endpoint `D8` actions make it
   the identity.  The diagonal `D8` stabilizer at `01` and the independent
   `D8` at a second fibre split the matching `01--45` into two orbits.  Residual
   `S3` on coordinates `4,5,6` lets us select a member of the first occurring
   orbit.  These are branches `d8_qd8` and `d8_qnond8`; in the second branch,
   all three matchings from `01` to `45,46,56` are constrained non-`D8`.
2. Otherwise all 105 matchings are non-`D8`.  Normalize `01--23` to
   `(0,3,2,1)`.  The projection of its `D8 x D8` stabilizer onto the `01`
   states has order 4.  Its action with the target `D8` splits a second `S4`
   matching into three orbits of size 8.  The first orbit is exactly `D8` and
   is impossible in this family.  Residual `S3` then leaves the two exhaustive
   hierarchical branches `nond8_q1` and `nond8_q2`.

All group sizes, disjointness, and coverage statements above are checked by
enumerating `S4` in `audit_double_cosets()` before every run.  After the two
matching normalizations, the unused sign flip of coordinate 6 supplies one
last WLOG bit normalization.

## Compact CNF

`scratch_canonical_v2_sat.py` makes two exact simplifications to the original
cell-level CNF:

- one Boolean output bit is shared for each coordinate of each directed
  permutation row; the equality of two selected states then needs 8 clauses;
- of the two complementary sign-balance equations, only the `1`-sign equation
  is retained.  Four one-hot rows ensure that exactly two `1`s is equivalent
  to exactly two `0`s.

It also omits redundant column-at-least-one clauses: four exactly-one rows plus
column-at-most-one already make a permutation matrix.

| exhaustive branch | variables | clauses | CaDiCaL 1.9.5 | time | conflicts |
|---|---:|---:|---|---:|---:|
| `d8_qd8` | 18,480 | 277,629 | UNSAT | 1.094 s | 12,021 |
| `d8_qnond8` | 18,480 | 277,641 | UNSAT | 0.951 s | 9,338 |
| `nond8_q1` | 18,480 | 278,073 | UNSAT | 0.206 s | 2,068 |
| `nond8_q2` | 18,480 | 278,121 | UNSAT | 0.256 s | 3,879 |

The generated DIMACS files and SHA-256 hashes are:

| file | SHA-256 |
|---|---|
| `scratch_canonical_v2_full_d8_qd8.cnf` | `92557E7DF13D8CCC9A20EC04B08CD34F06282FF6E5C435C33E539F4B86C5FFAD` |
| `scratch_canonical_v2_full_d8_qnond8.cnf` | `B88CCA359596797F496F9995A59FB16F0FD31F768C572857B6763A4B0C5B4EF0` |
| `scratch_canonical_v2_full_nond8_q1.cnf` | `EAF9E040084C160120B497F788DCEA4FB866DDA560F6192F219473D87F9A7D3F` |
| `scratch_canonical_v2_full_nond8_q2.cnf` | `4A64ECC0DE32B3A734134F2FBFDE35A72048CF9BAC6695373A8405CC29DCCBCE` |

## Independent checks

Two independent checks reached the same four terminal results.

1. `scratch_canonical_v2_crosscheck.py` retains the original 16-clause
   cell-level equality gadget, both original sign-balance equations, and all
   444,360 original clauses.  It adds only the d-variable WLOG scaffold.  All
   four branches are UNSAT under CaDiCaL:

   | branch | clauses | time | conflicts |
   |---|---:|---:|---:|
   | `d8_qd8` | 444,369 | 3.420 s | 26,761 |
   | `d8_qnond8` | 444,381 | 1.585 s | 10,404 |
   | `nond8_q1` | 444,813 | 0.321 s | 1,242 |
   | `nond8_q2` | 444,861 | 0.251 s | 452 |

2. `scratch_canonical_v2_cpsat.py` is a separate OR-Tools model.  It uses
   integer permutation rows, `AddInverse`, reified integer equality, and six
   parallel workers, rather than DIMACS gadgets.  It returned `INFEASIBLE` for
   all four branches in 21.03--25.93 seconds.

The overlap-only and balance-only stages remain satisfiable or unresolved as
recorded in their JSON files; the terminal contradiction uses the full set of
disjoint-fibre common-neighbour equations.

## Reproduction

In PowerShell from this directory:

```powershell
$env:UV_CACHE_DIR = (Resolve-Path .uv-cache).Path

$branches = 'd8_qd8','d8_qnond8','nond8_q1','nond8_q2'
foreach ($branch in $branches) {
  uv run --with python-sat python scratch_canonical_v2_sat.py `
    --stage full --branch $branch --solver cadical195 --conflicts 1000000
}

foreach ($branch in $branches) {
  uv run --with ortools python scratch_canonical_v2_cpsat.py `
    --stage full --branch $branch --seconds 60 --workers 6
}

foreach ($branch in $branches) {
  uv run --with pycosat --with python-sat python `
    scratch_canonical_v2_crosscheck.py --branch $branch --conflicts 1000000
}
```

## Caveat on proof status

The solver statuses are terminal and agree across two formulations and two
engines, but these runs did not emit DRAT/LRAT certificates.  They are strong
reproducible computational evidence, not a formally checked UNSAT proof.
