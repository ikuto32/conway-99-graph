# Canonical C4-fibre ansatz: SAT status

## Model checked

- The 84 outside vertices are `(ij,a,b)`, for `ij in C([7],2)` and two signs.
- Each four-state fibre `ij` has the fixed `C4` (flip exactly one sign).
- Distinct overlapping fibres have no edges.
- Every disjoint pair of fibres (an edge of `KG(7,2)`) carries a variable
  perfect matching.  There are `105 * 16 = 1680` possible D-edge variables.
- The CNF includes the equations with the 14 fixed neighbours (sign balance),
  and, at full stage, every outside/outside common-neighbour equation.

## Results (PicoSAT through pycosat 0.6.6)

| stage | variables | clauses | result |
|---|---:|---:|---|
| matching | 1,680 | 5,880 | SAT |
| balance | 1,680 | 59,640 | SAT (0.018 s) |
| overlap | 11,760 | 256,200 | unresolved after a bounded run |
| full | 16,800 | 444,360 | unresolved after a bounded run |

The full run was stopped after about 90 seconds and roughly 780,000 conflicts.
Thus this experiment gives neither a satisfying full model nor an UNSAT proof.
No candidate edge list was produced.  `submission.txt` was not modified.

## Reproduction

- `scratch_canonical_blocksat.py`: compact block encoding and direct 99-vertex
  verifier for any SAT model.
- `scratch_canonical_full.cnf`: generated full DIMACS instance.
- `scratch_canonical_overlap.cnf`: generated overlap-stage DIMACS instance.
- `scratch_canonical_sat.py`: slower literal-by-literal cross-check encoding.

The compact encoding uses one equality variable for a common neighbour through
an intermediary four-state fibre.  Because both incident matching rows are
one-hot, 16 clauses exactly encode equality of their selected states.
