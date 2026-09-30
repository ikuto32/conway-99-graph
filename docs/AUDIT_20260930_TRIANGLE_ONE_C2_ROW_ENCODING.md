# Independent one-C2-row target projection

The fixed core, its forced 36-by-36 incidence Gram and C0 column
normalization are the same as in the independently audited joint-factor
problem. The retained rows are all twelve C0 rows, all twelve C1 rows and
the labelled coordinate-zero row of C2 (incidence row24, core vertex27).
This choice is a restriction of any fixed-core target; it is not a
normalization requiring an automorphism.

Every retained row has ten outside neighbors. The first two complete
fibres have two incidences per outside column. Their principal 25-by-25
Gram is forced by the target identity. Only the previously justified zero
C0-cross Gram entries are folded into fixed zeros; every other position
in C1 and the selected C2 row remains a free binary entry.

The component-kernel result for the full target incidence factor says that
each of the three core components contributes exactly two ones per outside
column. Since omitted C2 entries are nonnegative, the sum of retained
entries in each component-column is at most two.

For two distinct outside vertices d,e, the retained incidence overlap

    sum(r=0..24) C[r,d]*C[r,e]

counts only some of their common neighbors in a target. The exact SRG
identity gives their total number of common neighbors as 2-A[d,e], at most
two. Thus each of the 1,770 retained column-pair overlaps is at most two.
These bounds use a target extension premise. They have NOT been proved for
every abstract 36-row factor of K alone, since that factor model omits the
residual graph D. The audit does not claim preservation of all such
abstract factors.

The encoded problem is exactly the binary25x60 matrix with the stated
fixed entries, principal Gram, retained complete-fibre margins and the two
families of capacities. Each exact product gate denotes its raw incidence
product. Independently checked prefix thresholds impose equalities or upper
bounds as appropriate. Full row/product/column metadata and raw-clause
reconstruction establish CNF satisfiability if and only if this explicit
25-row problem is feasible.

Every target containing the fixed39core, after the harmless outside-column
relabeling, supplies such a model. Conversely a satisfying25-row matrix
does not supply the omitted C2 rows, a36-rowfactor, or the residual graph.
Therefore a complete independently checked UNSAT proof would exclude
targets containing this core only; a SAT object establishes a partial
incidence construction only.

For object validation, all625 principal Gram entries are evaluated by
literal integer dot products. Every retained row margin,120complete-fibre
column margins,180component capacities and1770column-pair capacities are
checked separately, then Q1 is decoded from the twelve C1 rows and
round-tripped. Known-positive calibration uses a synthetic25-row matrix
against its own explicitly different Gram; no research-positive25-row
fixture is assumed. Corruptions are required to fail the corresponding
exact checking paths.
