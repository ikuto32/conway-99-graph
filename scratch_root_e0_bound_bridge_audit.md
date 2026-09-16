# Independent audit: root E0/prism bridge and bound CNF

## Outcome

**The mechanical DIMACS construction passes, but the mathematical bridge fails
for the quantity actually encoded.** Do not use the current `E0<=69` CNF as an
exhaustive conditional search.

## Bridge discrepancy

A four-vertex fibre has six candidate edges: four square sides whose two root
supports intersect in one neighbour, and two diagonals whose supports are
disjoint. The triangular-prism construction in the bridge starts by choosing
the shared root-neighbour, so it applies exactly to a side edge. Conversely,
every induced prism containing the root gives exactly such a side edge. Hence
the valid bijection is

```text
sum_r S(r) = 6P,
```

where `S(r)` counts side edges. The encoded quantity uses all 126 same-fibre
variables and is `E0(r)=S(r)+D(r)`, including 42 diagonal candidates. Locally
admissible one-diagonal and two-diagonal fibre states are already present in
the independent structural audit. Thus `sum_r E0(r)=6P` does not follow.

## External-premise arithmetic

Without replaying the public `n3` proof, accepting `n3>=708` and
`n3+3P=4158` gives `P<=1150`, then
`floor(6*1150/99)=69`. Combined with the corrected identity, this proves
`min_r S(r)<=69`; it does **not** prove `min_r (S(r)+D(r))<=69`.

## Mechanical CNF audit

- The builder selects exactly 126 variables: 84 sides plus 42 diagonals.
- The saved condition is exactly an at-most-69 PySAT sequential counter on all
  126 variables.
- Base header: `p cnf 817278 1622502`.
- Conditioned header: `p cnf 821211 1630356`.
- It adds 3,933 auxiliary variables and 7,854 clauses.
- Every base clause is preserved byte-for-byte; the suffix matches a fresh
  PySAT sequential-counter reconstruction clause-for-clause.
- Saved headers, line counts, maximum variable, and SHA-256 metadata all match.

A sound repair is to encode at-most 69 on only the 84 side variables. No heavy
SAT sweep was run. The external proof of `n3>=708` remains explicitly outside
this audit, and direct SAT witnesses would remain valid under either encoding.

## Quarantine audit

The corrected note explicitly retracts the E0 identity and records only the S
identity. The generated metadata is marked
`QUARANTINED_UNSOUND_PREMISE_NEVER_SOLVED`, a conspicuous marker says not to use
the CNF, and no portfolio or solution artifact exists. `main()` begins with an
unconditional exception; an independent `--sweep` invocation returned exit 1
with the quarantine message and changed none of the artifact hashes. No active
pipeline source references this conditioned CNF. This is sufficient containment
for the unused artifact, while retaining it for audit provenance.
