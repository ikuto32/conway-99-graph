# Conway 99-graph search: verified progress through `E0=77`

## Current outcome

No `srg(99,14,1,2)` witness has been found.  `submission.txt` is deliberately
absent.  The strongest positive near-candidate currently stored is
`scratch_root_e78_k23_rep6_energy_best.json`; it has 693 unique edges, every
degree 14, all 1176 rooted BP equations, and all 126 same-support outer-pair
equations exact, but its independently recomputed full residual energy is
3148 with 2055 bad pairs.  It is not a submission.

For a fixed root, let `E0` be the total number of edges inside the 21
four-vertex support fibres.  The finite computations below eliminate
`E0=84,80,79,78,77`; the analytic compression already excludes `81,82,83`.
Consequently any graph surviving these audited computations must have

```
E0 <= 76.
```

This is a computational search restriction, not a formally certified
nonexistence theorem: terminal UNSAT results do not all have externally
checked proof certificates.

## `E0=79`

The exact compression audit leaves twelve `S7` support orbits, necessarily
sixteen C4 fibres and five P4 fibres.  A P4 endpoint has one missing BP symbol
through each support group.  Its two ports at a group are either
`V={(0,1),(1,0)}` or `F_s={(s,s),(s,s)}`.  A degree-one support group is
impossible; the only five-edge support graphs without leaves are `K4-e` and
`C5`.  Compatibility forces either graph to be bipartite, whereas both are
nonbipartite.  Direct enumeration of all `4^5` P4 orientations independently
returns zero compatible completions in all twelve orbits.

Primary artifacts:

- `scratch_general_e79_compression_audit.py/.json`
- `scratch_general_e79_lift_orientation_audit.py/.json`
- `scratch_general_e79_summary.md`

## `E0=78`

All 229,789 labelled deficit placements form 170 exact `S7` orbits.  Exact
overlap recursion plus a rational spectral lower bound leaves 67; a
supplemental bounded-integer disjoint screen leaves 50.  Enumerating every
allowed labelled fibre state and every compatible local overlap matching
reduces the full 67-orbit set to `K2,3` and `C6`: 640 local graphs in ten exact
symmetry orbits (eight plus two).

CaDiCaL eliminates all ten exact lifts.  A separately constructed OR-Tools
model returns INFEASIBLE on the same ten branches.  The difficult final
OR-Tools branch terminates in 32.70 seconds on an isolated retry.  Ordinary
C4--C4 permutation blocks, one-sided C4--P4 blocks, and support aggregate
rows used here are explicitly derived consequences of BP, not extra
assumptions.

Primary artifacts:

- `scratch_general_e78_compression_audit.py/.json`
- `scratch_general_e78_local_ports_all.py/.json`
- `scratch_general_e78_local_reps.py/.json`
- `scratch_general_e78_k23_sat.py` and `_portfolio.json`
- `scratch_general_e78_k23_cpsat.py/.json`
- `scratch_general_e78_c6_cpsat.json`
- `scratch_general_e78_exact_summary.md`

An additional independent fixed-branch audit produced a 54.7 MB DRAT/DRUP
trace for K2,3 representative 6 and reproduced UNSAT with CaDiCaL 1.9.5 and
3.0.0.  The trace has not been checked by an external proof checker; see
`scratch_fibre_e78_rep6_exact_summary.md`.

## `E0=77`

All 883,179 labelled deficit placements form 459 exact `S7` orbits.  The
solver-free overlap and rational spectral screen leaves 172; the supplemental
integer screen leaves 165.  Across the larger 172-orbit set, all 1,566,224
allowed labelled fibre-state assignments were checked.  Exact port
matchability leaves three support orbits and 48 states.

Expanding their overlap edges gives 1024 local completions per support orbit.
Induced-pair upper bounds and necessary ordinary-C4 support BP rows eliminate
two support orbits.  The remaining 512 local graphs form exactly three
orbits of sizes `256,128,128` under the setwise support stabilizer and all
independent coordinate flips.

CaDiCaL returns UNSAT on the three exact lifts in 0.66, 2.64, and 0.63
seconds.  An independently rebuilt OR-Tools model returns INFEASIBLE in
8.58, 8.75, and 8.84 seconds.  Each final branch retains all 1680
disjoint-support edge variables and imposes every BP and outer-pair equality.

Primary artifacts:

- `scratch_general_e77_compression_audit.py/.json`
- `scratch_general_e77_port_audit.py/.json`
- `scratch_root_e77_local.py/.json`
- `scratch_general_e77_exact_sat.py` and `_portfolio.json`
- `scratch_general_e77_exact_cpsat.py/.json`
- `scratch_general_e77_exact_summary.md`

## Claim boundary and next frontier

- Spectral identities, BP equations, fibre-state classifications, and the
  formulas for redundant support rows are analytic necessities.
- Placement/orbit generation, port matching, local graph expansion, and
  symmetry quotienting are exact finite enumerations with internal coverage
  checks; several layers also have independent implementations.
- Full-lift exclusions at `E0=78,77` agree across CaDiCaL and OR-Tools, but no
  complete externally checked proof-certificate chain covers every branch.

The next active frontier is the exact compression and local classification at
`E0=76` (total fibre deficit eight).  Candidate generation outside the
eliminated high-`E0` strata remains active in parallel.
