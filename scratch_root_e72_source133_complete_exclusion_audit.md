# E72 source 133: complete five-macro exclusion bridge

The five canonical macro branches have total labelled catalog coverage
`2,502,656`.  They split without overlap into four regular branches
(`2,490,368`) and the adjacent-side nonregular branch 4 (`12,288`).

For regular branches, the Gram/balance identities reduce every remaining
completion to explicit maps between labelled four-point fibres.  For an
exceptional vertex `x` and a bottom-outside fibre `U`, the induced-pair upper
bound becomes a collision restriction on the image map `phi_U`: repeated
images must lie at the C4-opposite point in the disjoint case, with the
corresponding bit restriction in the overlap case.  Exact joins then impose
exception--exception collision budgets and finally the within-target
`U_i^5`--`U_i^6` overlap budget.  The standard-library enumeration is

```text
5,138 masks -> 81 -> 1 -> 0
mass 1,129,056 -> 9,952 -> 16 -> 0.
```

This solver-free enumeration is independently reproduced by the fixed local
CNF category census.  Its macro policies use only `EE_same`, `EE_disjoint`,
`EU_disjoint`, and (where needed) `UU_overlap`; all 5,138 formulas are UNSAT.
Here `E` denotes an exceptional vertex and `U` a bottom-outside vertex, while
the suffix records whether their two-support labels are equal, overlap, or
are disjoint.  These are necessary upper bounds because any omitted outside
edges can only add common neighbours.

Branch 4 does not satisfy the regular H/F hypothesis and is kept separate.
Selector `817283` isolates it in the full-SRG CNF.  The derived CNF is UNSAT,
and its DRUP proof is accepted by pinned `drat-trim`.  The deterministic audit
checks the selector tail, source-CNF byte identity, hashes, and coverage.

The machine-readable bridge is
`scratch_root_e72_source133_complete_exclusion_audit.json`; its producer
asserts both catalog and canonical-local coverage partitions and pins every
input by SHA-256.  The 5,286 canonical local masks also have explicit 276-edge
full-SRG assumption vectors in
`scratch_root_e72_source133_local_assumption_manifest.json`.

This closes source 133 conditional on the separately audited upstream
support/Gram/catalog completeness.  The regular finite enumeration is exact
but is not itself a DRAT proof; branch 4 has the externally checked DRUP.
