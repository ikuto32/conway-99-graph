# Global fibre relabelling of the fixed-support profile family

This audit concerns only the frozen six-prism Hadamard support. The already
checked exactly-four-exception screen gives108 labelled necessary profiles
for prescribed-Gram factors satisfying outside-column overlap caps. It does
not establish a factor for any of the96 nonempty arc-consistency outcomes.

Write a row as(f,a), where f is one of three fibres and a is a coordinate.
For every permutation tau of the three fibres, let P send(f,a) to(tau(f),a).
The literal six-prism core C and prescribed Gram K obey PCP^T=C and PKP^T=K.
The three distinguished triangle vertices are permuted by the same tau.
The coordinate support L is unchanged: summing the three fibre entries at
each coordinate is unaffected by a fibre permutation.

Within each repeated-support group, transform the three colour words by tau
and sort them in the saved increasing-word order. Let Q be the resulting
column permutation matrix, with Q[old_column,new_column]=1. Q only permutes
columns having identical coordinate support. Then the relabelled factor is
F'=PFQ, and F'F'^T=PKP^T=K. Row and column margins, binary entries and every
outside-column overlap are preserved. Distinctness of the three words follows
from the within-fibre Gram bound: duplicate columns would repeat a row pair
whose required Gram entry is one. Sorting is therefore a bijective local
normalization, not a restriction on a hypothetical graph's automorphisms.

If a residual adjacency D completes F, relabel it as D'=Q^T D Q. For
H=2J-F-CF and T=F^T F, the transformed values satisfy H'=PHQ and T'=Q^T T Q.
Thus FD=H becomes F'D'=H'; and D^2+T=12I-D+2J becomes
D'^2+T'=12I-D'+2J. Symmetry, binary entries, zero diagonal and residual
degree are also preserved. Equivalently the complete99-vertex adjacency is
conjugated by the block permutation of the triangle, core rows and outside
columns. This proves preservation of target completion whenever one exists.
It does not say that this permutation fixes the original graph. No symmetry
of an unknown target or of its residual graph is assumed.

For a count-profile row v, the action is v'[tau(f)]=v[f]. Exceptional group
IDs and support coordinates are unchanged. The six saved actions are checked
on all90 balanced words and every31,110 cap-compatible increasing triple.
The exact108-profile population is closed under these actions. Each nonzero
profile contains a permutation of(-1,0,1), so no nonidentity fibre permutation
fixes it. Consequently each orbit has size six. The minimum saved case ID
selects18 representatives, including two orbits of excluded profiles and16
orbits of the96 nonempty screen outcomes.

For each saved case-to-representative action, local option sets are bijective.
The pair-Gram predicate is invariant because its integer contribution matrix
is conjugated by P and its upper bound K is fixed. The column-cap predicate
is invariant because row permutations preserve set intersections and column
permutations merely reorder the nine comparisons. The checker separately
reconstructs all pair predicates from sparse integer contributions and literal
column sets, compares all saved tables, and recomputes arc consistency using
simultaneous set updates rather than the producer's ordered bitmask deletions.
It checks both pair-Gram and Gram-plus-cap fixed points and their transport.

Thus every target completion in this exactly-four-exception, fixed-support
family has a relabelled completion in one of the16 unresolved representative
profiles. The reduction does not assert any representative is feasible, does
not exclude the remaining family, and does not cover arbitrary supports or
factors with a different number of exceptional groups. Eighteen and16 are
counts in this finite profile population, not percentages of Conway99.

Controls include the identity and inverse actions on complete finite domains,
literal algebraic covariance on a saved synthetic factor and residual cycle,
positive and empty relation fixed points, and corrupted permutations, maps,
pair tables, fixed points and residual transports. The synthetic factor is
explicitly not asserted to have the prescribed full Gram or to be a target.
Prior screen and calibration gates are separate premises. No producer code
is imported, no native search is run, and no claim is made about target
automorphism groups or completeness of any larger relabelling group.
