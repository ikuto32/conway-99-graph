# Conway-99 rooted search checkpoint v5

## Status

No `srg(99,14,1,2)` has been constructed.  No `submission.txt` has been
created.  Every saved 693-edge heuristic graph has a positive independently
recomputed SRG residual energy and is therefore invalid.

The strongest current *search normalization* is:

```
every putative target admits a choice of root with E0 <= 73.
```

This statement combines a self-contained mathematical side bound with
solver-terminal local exclusions.  The latter have independent model audits
but no DRAT/LRAT proof certificates, so this is not a formal nonexistence
theorem.

## Self-contained side bound

For a root `r`, its 84 distance-two vertices form 21 support fibres of four.
Write

```
S(r) = selected fibre sides (four positions per fibre),
D(r) = selected fibre diagonals (two positions per fibre),
E0(r) = S(r)+D(r).
```

The earlier proposed identity `sum E0=6P` was wrong and remains quarantined.
The correct identity is only

```
sum_r S(r)=6P,
```

where `P` is the number of induced triangular prisms.

`scratch_root_side_bound_selfcontained.md` reconstructs the triangle
intersection projector and its integral Schur lift directly from the SRG
axioms.  If `n3` counts two disjoint triangles joined by two independent
cross edges, it proves

```
tr(A4)=84*(n3-693),
tr(A4)>=4*231,
3 divides n3,
n3>=705.
```

The same triangle-pair moments give `n3+3P=4158`, hence `P<=1151` and

```
sum_r S(r)<=6906<99*70.
```

Thus some root has `S(r)<=69`.  The arithmetic script reports
`ARITHMETIC_VERIFIED`; the separately written logical/arithmetic audit
`scratch_root_side_bound_selfcontained_audit.json` reports
`LOGIC_AND_ARITHMETIC_VERIFIED`, `ok=true`, and zero errors.  No external
`n3>=708` premise is needed.

The corrected CNF `scratch_root_side_le69.cnf` counts exactly 84 side
variables and omits all 42 diagonals.  Its byte-level counter audit remains
valid.  Its 20,000-conflict branch portfolio is `9 UNSAT, 17 UNKNOWN, 0 SAT`.

## Rooted E0 exclusions

The fibre compression proves arithmetically that `E0=81,82,83` are
impossible.  Separate exact encodings have solver-terminal, independently
audited exclusions for `E0=84,80,79,78,77,76,75`.  These checks cover all
rooted local orbits in their stated classes; none currently has a proof-log
certificate.

For `E0=74`, choosing the guaranteed root with `S<=69` forces `D>=5`.
The notation in the local census calls this diagonal count `Q`.  The
`Q>=5` pipeline is complete:

```
11 support rows
89 fibre-state assignments
1,461,248 exact local completions
617,864 after induced-pair upper bounds
16,384 after forced-C4 BP
188 S7 local-graph orbits (all Q=8)
188 terminal UNSAT, 0 SAT, 0 UNKNOWN
```

The independent audit `scratch_e74_independent_q5_audit.json` reports
`ok=true`, zero errors.  It independently reconstructs the 128 group actions,
the `16,384 -> 188` orbit quotient, weights `32:24 / 64:84 / 128:80`, the
local edge catalog, the exact CNF contract, assumption hashes, core subsets,
and all recorded solver statuses.  Three representatives also received fresh
fixed-local CNFs and independently returned UNSAT.

Consequently, a target graph would admit a root with `E0<=73`.  This is an
existence-normalizing root statement, not a claim that every root has that
bound.

## Current E0=73 frontier

At the selected root, `E0=73` and `S<=69` force `Q=D>=4`.  This scope is now
self-contained rather than dependent on the public `n3>=708` endpoint.

The completed compression/port discovery currently records:

```
total deficit:                              11
partitions:                                 27
all labelled support placements:            79,841,895
all raw S7 support orbits:                   21,699
removed immediately by Q-capacity:          14 partitions / 8,469 orbits
capacity-surviving support orbits:           13,230
balanced + exact-real support orbits:        295
their labelled weight:                      865,830
Q>=4 exact fibre-state products examined:   4,758,382
port-feasible support rows:                  58
port-feasible labelled state assignments:   980
Q histogram:                                4:708, 5:144, 6:104, 7:16, 8:8
```

Independent brute-force port audit, local-graph expansion, orbit reduction,
and exact SAT are the active next stages.  No exclusion is claimed until
those stages and independent audits finish.

## Direct strengthened CNF and constructive search

`scratch_root_side69_e0le73.cnf` adds the computationally justified
`E0<=73` counter to the audited `S<=69` formula.  It has 822,182 variables,
1,632,236 clauses, and SHA-256

```
7FAB56D135701EB8CAE8F7179E337B85E0EC679E571F5BA6D186E93CD50E7923
```

Its first 20,000-conflict portfolio also ended
`9 UNSAT, 17 UNKNOWN, 0 SAT`.  This formula is a candidate-search
strengthening: SAT would still be checked directly, while UNSAT alone would
inherit the no-proof-log caveat of the E0 exclusions.

The best exact-BP heuristic incumbent has residual-square energy `3136`, not
zero.  A 40-round wide linearized LNS and a 240-state minimum-circuit walk did
not improve it.  The smallest nonzero `+/-1` exact-BP move found by CP-SAT has
support 16 (an 8-for-8 incidence-circuit trade), with `OPTIMAL` solver status
but no formal optimality certificate.  These invalid incumbents are retained
only as warm starts and diagnostics.

## Claim boundary

- There is no graph and no valid submission yet.
- Arithmetic and finite catalogs are independently replayed where stated.
- Solver-terminal UNSAT without a proof log is reproducible computational
  evidence, not a formal proof.
- `UNKNOWN` branches are not counted as exclusions.
- The quarantined all-six-pairs `E0<=69` CNF was never solved and is not used.
