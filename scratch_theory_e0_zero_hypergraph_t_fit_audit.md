# E0=0 fixed-control T-fit independent audit

Status: `FIXED_CONTROL_T_FIT_AUDIT_PASS`.

The sealed CP-SAT run supplied a **feasible**, not certified optimal, T: objective
`2646.0`, solver lower bound `2452.0`.  Independently replayed,
T has 84 edges, degree 2, no triangle, and is the union
of the 14 required exact-label 1-factors.  B=T+D has 504 edges and degree
12.

## Direct residual

For `E=B^2+B-(10I+2J-Q)`, the witness has unordered L1
`2646`, `2086` bad unordered entries, and
`||E||_F^2=7708`.  B has 263 triangles,
split by the number of T sides as `{'0': 227, '1': 30, '2': 6}`.

## First unavoidable failure for this fixed D

D already has 227 triangles: 140 selected-block triangles and
87 outside Berge triangles.  Adding T cannot delete them.
Consequently

`tr(BE)=tr(B^3)-840=6*(triangles(B)-140) >= 522`.

The stronger coordinatewise fixed-D check starts at T=0 with positive residual mass
774.  Every T contribution is nonnegative, while
every final 12-regular residual has total sum zero, so any T over this D obeys the rigorous
unordered L1 lower bound `1548`.

More generally, writing `beta(D)` for the number of D-triangles outside the 140
selected blocks,

`triangles(B)-140 = beta(D) + mixed_1T + mixed_2T + triangles(T)`.

All four terms are nonnegative.  Thus every exact E0=0 candidate must have `beta(D)=0`
and no mixed or T triangle.  Cauchy--Schwarz also gives the general quantitative bound
`||E||_F^2 >= beta(D)^2/28`.  The rule is general; the value `beta(D)=87` is specific
to this control.

The replay also checks `[B,Q]=[B,E]`.  Cauchy--Schwarz gives
`||E||_F^2 >= 15129/28` for this witness;
the commutator gives `||E||_F^2 >= 2323/72`.

## Boundary

This is a rigorous rejection of **one explicit D/U control only**.  The bounded CP-SAT
objective is not proved optimal, and none of the positive numerical bounds excludes all
E0=0 controls.  The trace and commutator formulas themselves are general necessary
identities for an admissible 12-regular B=T+D.
