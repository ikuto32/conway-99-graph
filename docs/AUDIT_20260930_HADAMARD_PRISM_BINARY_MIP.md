# Independent binary MIP model and incumbent checking

The independent checker rebuilds all5400 choices by subset enumeration, all726
integer equality rows and forty signed rank inequalities from the raw support.
Binary bounds, integrality, zero objective, row bounds and all coefficient IDs
must agree exactly with the saved model. A separate column-major native model
roundtrip checks every coefficient and bound without running the optimizer or
using the producer's SciPy conversion. The actual source and locked libraries
are bound. Known243, a tiny integral native control and deliberately corrupted
models/rows/cuts calibrate different parts of this path.

Saved native numbers are checked against their hexadecimal IEEE encodings.
Their exact rational distance to zero or one must be at most1/10000000 before
rounding. Integer equations, rank inequalities and every earlier cut are then
checked exactly. A numerical tolerance alone never certifies feasibility.
The checker reconstructs raw F from coordinates and colour choices, all1296
Gram entries, row/fibre margins, fixed L, canonical C0 bijection, all1770 column
intersections and all2160 mixed caps. Cap-violating exact Gram objects remain
saved under their weaker classification. A cap-valid object additionally uses
the prior separate full raw-factor validation path.

Every new cut must forbid two actual options from different columns whose raw
intersection exceeds two. Complete prior model suffixes and all newly selected
violations are checked before the next attempted call. Numerical infeasibility,
timeout and no incumbent are never exclusions. The same solver instance and
cooperative shared120-second limit are source/record claims, not an independently
measured hard process limit. No optimizer is run by this checker; root controls
the research calls. No target automorphism, cyclic relation, residual D or
coverage of other supports is assumed.
