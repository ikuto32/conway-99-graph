# Independent exact audit of `E0=77`

## Outcome

The three local-port survivor support orbits were audited independently.  Two
die under an exact finite local expansion.  The remaining support orbit has
512 labelled local graphs, forming three symmetry orbits.  All three exact
84-outer-vertex lifts are computationally UNSAT in CaDiCaL and independently
INFEASIBLE in OR-Tools CP-SAT.

No checkable UNSAT certificate was emitted.  This is therefore a
finite-computational elimination of `E0=77`, not a formally certified proof
and not a construction of `srg(99,14,1,2)`.

## Independent fibre and support audit

[`scratch_e77_sat_audit.py`](scratch_e77_sat_audit.py) enumerates all 64
simple graphs on one four-vertex support fibre, using only:

- the BP capacity of one in every `(support coordinate, required sign)` bin;
- the same-fibre outer-pair upper bound.

The admissible counts by number of internal edges are `1,6,7,4,1` for
`0,1,2,3,4` edges.  Consequently:

- deficit one has exactly four labelled states, all `P4` (three square sides);
- deficit two has exactly seven labelled states: four adjacent-side pairs,
  two opposite-side pairs, and the pair of diagonals.

The weighted support indices, orbit sizes, and pairwise nonisomorphism of the
three port survivors were recomputed under all 5040 group permutations.  An
independent simple-edge matching DFS (not the earlier Hall shortcut) again
finds exactly 16 feasible labelled fibre-state assignments in each survivor.
Full data are in [`scratch_e77_sat_audit.json`](scratch_e77_sat_audit.json).

## Exhaustive local representatives

[`scratch_e77_sat_reps.py`](scratch_e77_sat_reps.py) independently expands
all state assignments and all distinct-simple-edge overlap matchings.  It
then checks induced common-neighbour upper bounds and the exact unsigned BP
support-count equations forced by every ordinary `C4` fibre.

| support survivor | overlap completions | after pair upper bound | after ordinary-`C4` BP |
|---|---:|---:|---:|
| `2+1^5`, orbit 0 | 1,024 | 576 | 0 |
| `1^7`, orbit 2 | 1,024 | 1,024 | 0 |
| `1^7`, orbit 22 | 1,024 | 1,024 | 512 |

For orbit 22, exhaustive canonicalization under the full support stabilizer
and all active coordinate flips gives three orbits of sizes `256,128,128`.
Their explicit 35-edge local representatives are stored in
[`scratch_e77_sat_reps.json`](scratch_e77_sat_reps.json).  Canonicalizing the
separately generated representatives in
`scratch_general_e77_local_reps.json` under this implementation gives the
same set of three orbits.

## Exact full models and safety boundary

[`scratch_e77_sat_exact.py`](scratch_e77_sat_exact.py) and
[`scratch_e77_sat_cpsat.py`](scratch_e77_sat_cpsat.py) construct the models
separately.  For each representative:

- all seven exceptional fibres and their 14 overlap edges are fixed by the
  local representative;
- all 14 other fibres are ordinary `C4`s;
- all 105 disjoint-support blocks remain present, giving 1,680 edge
  variables;
- the 46 ordinary--ordinary blocks have two exact-one sides (a permutation);
- the 48 ordinary--exceptional blocks have only the rigorously implied
  exceptional-vertex exact-one side;
- the 11 exceptional--exceptional blocks are unrestricted `4 x 4` blocks;
- all 1,176 `BP=PA0` equalities and all 3,486 outer-pair equalities are exact;
- all 65,520 Boolean products are encoded as equivalences, not one-way
  implications.

The block rule follows directly from an ordinary `C4`: its six internal-pair
equations give at most one neighbour in that fibre to every outside vertex.
Its four vertices require 40 external incidences, and exactly 40 vertices on
the ten disjoint support fibres are eligible, so every eligible vertex has
exactly one neighbour in it.  This gives two sides only if both fibres are
ordinary.

[`scratch_e77_sat_model_audit.py`](scratch_e77_sat_model_audit.py) separately
checks the fixed local graphs, edge classification, block counts, quota
coverage, pair bounds, equation counts, and agreement of both result files;
[`scratch_e77_sat_model_audit.json`](scratch_e77_sat_model_audit.json) has
`"ok": true`.

## Solver results

| local branch | local orbit size | CaDiCaL | seconds | CP-SAT | seconds |
|---:|---:|---|---:|---|---:|
| 0 | 256 | UNSAT | 4.640 | INFEASIBLE | 23.250 |
| 1 | 128 | UNSAT | 3.734 | INFEASIBLE | 17.703 |
| 2 | 128 | UNSAT | 9.422 | INFEASIBLE | 15.062 |

The detailed logs are
[`scratch_e77_sat_exact_portfolio.json`](scratch_e77_sat_exact_portfolio.json)
and [`scratch_e77_sat_cpsat.json`](scratch_e77_sat_cpsat.json).  This model
does not use the redundant aggregate rows present in the separate
`scratch_general_e77_exact_*` implementation, so the matching elimination is
an additional encoding-level cross-check.

