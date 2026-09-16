# Fixed E78 K2,3 representative-6 exact SAT result

## Scope

This is one labelled local subbranch only: compression orbit 3, K2,3 support
pattern, canonical local representative 6.  That representative has orbit
size 96 among the 512 labelled K2,3 local states and is one of eight local
orbits.  Therefore this result is **not** an exhaustive elimination of E0=78
and is not a solution of the 99-graph problem.

## Independently audited phase seed

`scratch_root_e78_k23_rep6_energy_best.json` was independently expanded and
checked by `scratch_fibre_layer_sat_v2_root_seed_audit.py`:

- 693 distinct simple edges and degree 14 at all 99 vertices;
- exact rooted scaffold and all 84 outer labels;
- all 1,176 BP equations;
- all 126 same-support outer-pair equations;
- E0=78, with 15 C4 fibres and six P4 fibres on the declared K2,3 supports;
- full-SRG energy 3,148 and 2,055 bad pairs, so the phase seed itself is not a
  full SRG.

Audit output: `scratch_fibre_e78_rep6_exact_seed_audit.json`.

## Exact CNF

Builder: `scratch_fibre_e78_rep6_exact_sat.py`.

- Fixed outer pairs: 90 present and 1,716 absent.
- Primary variables: all 1,680 disjoint-support outer pairs.
- Safe redundant blocks: 51 C4--C4 permutation blocks and the P4-side
  exact-one columns in 48 C4--P4 blocks.  No unsafe C4-side row equality was
  added for C4--P4 blocks.
- BP equalities: 1,176.
- Outer-pair equalities: all 3,486, comprising 126 same-support and 3,360
  cross-support pairs.
- Full Tseitin AND equivalences: 65,520.
- DIMACS size: 280,410 variables and 652,760 clauses.
- DIMACS SHA-256:
  `48C650E5E51F228D48A9C12AEFF35F0F7664DC3447E2C08A1CD3337A459E25E6`.

An independent structural audit obtained the same 90/1,716/1,680 split and
the same 51/48/6 block classification.  Its artifact is
`scratch_e78_rep6_encoding_audit_subagent.json`.

## Solver result

The fixed subbranch is **UNSAT**.

- CaDiCaL 1.9.5: 8.907 s, 28,091 conflicts, 43,060 decisions, 101,434,583
  propagations.
- CaDiCaL 3.0.0, separately loading the identical DIMACS: 9.922 s, 28,881
  conflicts, 38,380 decisions, 92,962,786 propagations.

The CaDiCaL 1.9.5 run emitted a 54,696,079-byte proof trace with 1,271,820
text records:

- file: `scratch_fibre_e78_rep6_exact_unsat.drat`
- SHA-256:
  `F81356365C2E4C62F4E1AC9FD075D95587E399C1F39008AE8043D8657628782A`

No independent DRAT/DRUP checker was available locally, so the trace is
preserved but explicitly marked `independently_checked=false`.  The UNSAT
solver answer itself was reproduced with the separate CaDiCaL 3.0.0 backend.

Machine-readable results are in
`scratch_fibre_e78_rep6_exact_portfolio.json` and
`scratch_fibre_e78_rep6_exact_crosscheck_cadical300.json`.
