# Exact unrestricted rooted SAT experiments

## Model

`scratch_general_exact_sat.py` encodes the complete rooted 84-vertex
reduction, without assuming any graph automorphism.  Its primary variables
are all 3,486 possible edges of the unknown outer graph `B`.

The 1,176 equations `BP=PA0` force outer degree 12 and settle every SRG
condition involving the root or its 14 neighbours.  For every outer pair it
then imposes

`common_outer(u,v) + edge(u,v) <= 2 - |label(u) intersect label(v)|`.

These upper bounds are collectively exact.  Their actual left sides sum to
`84*C(12,2)+504=6048`, equal to the sum of all right sides.  Thus any SAT
assignment expands to an `srg(99,14,1,2)`; the code also independently checks
all 4,851 pairs before writing a scratch witness.

The generated DIMACS has 817,278 variables and 1,622,502 clauses.  Its
SHA-256 is
`91D22E62625E1221DD46B819E89494DB8141DD4DDC9A06F13B9ABDB530B83242`.

## Safe first-level symmetry branches

For any outer vertex, let `a,s,d` be its numbers of neighbours on the same,
singly overlapping, and disjoint two-coordinate supports.  The rooted
equations give `2a+s=4` and `a+s+d=12`, so `d=8+a`: a disjoint-support edge
always exists.  The scaffold group is transitive on ordered such edges, so
the model safely fixes `{0,2}--{4,6}`.

The same-support possibilities at `{0,2}` have four viable orbits:

* `a0`;
* `a1_complement`;
* `a1_cross`;
* `a2_crosses`.

The nominal fifth orbit `a2_mixed` is inconsistent already with a rooted
coordinate equation and CaDiCaL proves it UNSAT by propagation (0.906 s,
zero conflicts).  The four viable branches each remained UNKNOWN after 600
seconds.  Overall status is therefore UNKNOWN, not UNSAT.  Results are in
`scratch_general_exact_portfolio.json`.

## Safe second-level triangle branches

The fixed disjoint edge has a unique common outer neighbour.  Its label is
symbol-disjoint from both endpoints.  `scratch_general_triangle_portfolio.py`
enumerates the residual scaffold group for each viable first-level branch
and mechanically partitions all 42 possible third labels into orbits.  This
gives 26 exhaustive branches (6, 6, 8, and 6 respectively).

With at most four workers and 30 seconds per branch, CaDiCaL returned:

* 9 branches UNSAT by propagation;
* 17 branches UNKNOWN;
* no SAT witness.

The full orbit lists and branch records are in
`scratch_general_triangle_portfolio.json`.  This experiment does not prove
nonexistence and did not create `submission.txt`.
