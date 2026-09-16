# Corrected side-bound CNF audit

`scratch_root_side_le69.cnf` passes the independent mechanical and scope
audit (`scratch_root_side_bound_audit.json`, `ok: true`, no errors or
warnings).  This audit did not run a SAT solver.

## Encoded variables

Independent reconstruction of the 84 outer labels gives 21 support fibres,
each with six same-fibre pairs:

- four square sides, characterized by exactly one shared root-neighbour;
- two diagonals, characterized by no shared root-neighbour.

The counter inputs are exactly the `21*4 = 84` side variables.  The target
selector and metadata lists match the independent reconstruction.  All 42
diagonals are absent from the counter input.

This is therefore the condition `S(r) <= 69`, not the unsupported condition
`E0(r)=S(r)+D(r) <= 69`.  The old quarantined input set has 126 variables and
is exactly the disjoint union of these 84 sides and 42 diagonals; the corrected
input set is exactly the old set minus the diagonals.

## DIMACS reconstruction

| item | value |
|---|---:|
| base header | `p cnf 817278 1622502` |
| corrected header | `p cnf 818313 1624518` |
| side inputs | 84 |
| added sequential-counter auxiliaries | 1,035 |
| appended sequential-counter clauses | 2,016 |

The corrected file preserves the complete base clause body byte for byte.
Rebuilding `CardEnc.atmost(sides, 69, top_id=817278,
EncType.seqcounter)` independently reproduced the appended suffix byte for
byte.  The suffix uses every side variable, no diagonal, no pre-existing base
auxiliary, and the contiguous new auxiliary range through variable 818,313.
The header, line count, and build metadata agree with the file hashes.

- Base SHA-256:
  `91D22E62625E1221DD46B819E89494DB8141DD4DDC9A06F13B9ABDB530B83242`
- Corrected CNF SHA-256:
  `C2B9C01DC6E11EC03E5B387060FCA71FEDA893BA12C007F0105326A1D7CB9828`
- Appended suffix SHA-256:
  `B118A5E6BFBAD999FDD1B09258B181B73C0B434B984991932D793E01A00FE648`

The builder now has the time-independent status `BUILT` and rejects every
bound other than 69 before writing an artifact, which prevents the fixed
external arithmetic statement from being mislabeled as a generic bound.

## Claim boundary

Only the arithmetic from the stated premises was checked:

```
n3 >= 708,  n3 + 3P = 4158
=> P <= 1150
=> sum_r S(r) = 6P <= 6900
=> min_r S(r) <= floor(6900/99) = 69.
```

The proof of `n3 >= 708`, the identity `n3+3P=4158`, and the corrected prism
bijection were not replayed in this audit.  Thus a future exhaustive UNSAT
result would remain conditional on those external premises.  A SAT result
would still require and receive direct verification on all 99 vertices.

An already-existing 20,000-conflict probe is `UNKNOWN` (9 branch UNSAT, 17
UNKNOWN); it was not used as evidence here and establishes no exclusion.
