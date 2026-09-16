# BP + same-support fibre layer: exact SAT experiment

## Result

The fresh SAT model did not find a feasible intermediate-layer seed within
the bounded run.  Four viable exhaustive symmetry branches remain UNKNOWN;
the deliberately retained locally impossible branch is UNSAT:

| branch | result | bound / evidence |
|---|---|---|
| `a0` | UNKNOWN | stopped at the common 60 s batch deadline |
| `a1_complement` | UNKNOWN | stopped at the common 60 s batch deadline |
| `a1_cross` | UNKNOWN | stopped at the common 60 s batch deadline |
| `a2_crosses` | UNKNOWN | stopped at the common 60 s batch deadline |
| `a2_mixed` | UNSAT | CaDiCaL, 0 conflicts, 0.157 s |

UNKNOWN is not interpreted as UNSAT.  No SAT model was available to expand,
so `scratch_fibre_layer_sat_strong_solution.json` was not created.

## Exact model

`scratch_fibre_layer_sat_strong.py` asserts exactly:

* all 1,176 equations of `BP = PA0`;
* all 126 same-support outer-pair equations;
* full Tseitin equivalences for the 10,332 required wedge products.

The pair targets split into 84 square sides with target 1 and 42 fibre
diagonals with target 2.  Both lower and upper cardinality bounds are explicit;
this encoding does not rely on the global-sum shortcut used by the full
general baseline.

The generated DIMACS has 27,510 variables and 287,616 clauses.  Its SHA-256
is
`BC489DE4E59DFBC1DF5090D9F6F2E44ED67D383E06F17878B929FB86BEA87553`.

## Symmetry safety

For any outer vertex, BP gives `d = 8 + a`, where `d` is its number of
neighbours on disjoint supports and `a` its same-support degree.  Hence a
disjoint-support edge always exists.  The rooted scaffold group is transitive
on ordered pairs of labels using four distinct groups, so fixing
`{0,2}--{4,6}` loses no solution.

At `u={0,2}`, the two mate-symbol target-one equations prohibit selecting a
fibre diagonal together with either incident side.  The five locally
compatible labelled patterns reduce under the remaining coordinate swap to
`a0`, `a1_complement`, `a1_cross`, and `a2_crosses`.  `a2_mixed` was retained
as an independent propagation check and was indeed UNSAT.  Thus the four
UNKNOWN branches exhaust every possible solution of this intermediate model
up to the stated safe symmetry.

## Audit and artifacts

`scratch_fibre_layer_sat_audit.py` independently recomputes the 21 fibres,
126 pair count, target histogram, and allowed incident patterns.  It also
checks every DIMACS clause line, maximum variable, header counts, SHA-256,
branch units, and reported statuses.  The audit passed; its machine-readable
record is `scratch_fibre_layer_sat_audit.json`.

Main artifacts:

* `scratch_fibre_layer_sat_strong.py`
* `scratch_fibre_layer_sat_strong.cnf`
* `scratch_fibre_layer_sat_strong_build.json`
* `scratch_fibre_layer_sat_strong_portfolio.json`
* `scratch_fibre_layer_sat_audit.py`
* `scratch_fibre_layer_sat_audit.json`

All solver processes were collected after the run.  This intermediate model
does not establish a full SRG, and no `submission.txt` was created.
