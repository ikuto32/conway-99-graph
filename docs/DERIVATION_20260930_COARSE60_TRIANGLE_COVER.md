# Candidate coarse residual-triangle constraint

This package applies the independently checked, conditional identity-P
completion lemma from `AUDIT_20260930_IDENTITY_P_TRIANGLE_PARTITION.md`.
It assumes an actual SRG completion in the specified six-prism coarse60
family. It does not assume an automorphism of that completed graph.

That lemma partitions the outside sixty vertices into twenty triangles. If
outside vertices d,e share a triangle with f, their unique common neighbor
(lambda=1) is f. Therefore they cannot have a common inner neighbor, and their
binary incidence columns are disjoint. The three columns of each residual
triangle are consequently pairwise disjoint.

Each coarse column chooses one coordinate bit in one specified fibre for each
of the six prism components. For a given component and column triple, if all
three specified fibres coincide then two of the three bits must coincide, so
pairwise column disjointness is impossible. If exactly two fibres coincide,
those two bits must differ. If all three fibres differ, that component adds
no restriction. These six independent component tests characterize whether
the three columns can be made pairwise disjoint by choosing their bits freely.
They do not check any relation to other columns or the prescribed factor Gram.

Consequently any actual target completion of this fixed template induces an
exact cover of the sixty coarse columns by admissible triples, with the stated
opposite-bit implications. A found cover ignoring bits only shows that this
necessary coarse test is noncontradictory. Even bits chosen to satisfy its
twenty separate triangles need not satisfy row margins or Gram equations.

For a future independently reviewed strengthening, one may introduce a Boolean
selector for each admissible triple, require each column to occur in exactly
one selected triple, and for every selected triple and equal-fibre pair impose
the two conditional XOR clauses `(-t OR x OR y)` and
`(-t OR -x OR -y)`. This would encode the existence of a disjoint-column
triangle partition together with the original factor model. It is a new
target-necessary restriction; it is not asserted to follow from the abstract
Gram-only factor model. No such CNF or solver invocation is produced here.
