# E0=79 local P4 lift audit

## Result

The `E0=79` case has no locally BP-compatible lift once the exact
fibre-compression classification has forced the deficit partition
`1+1+1+1+1`.

This conclusion does not require a full 84-vertex SAT or CP-SAT solve.  The
remaining contradiction uses only the P4 fibres and the rooted equations
`BP=PA0`.

## Endpoint deficits

Let an exceptional fibre have support `{g,h}`.  Its induced graph is a P4,
obtained from the coordinate square by deleting one side.  Suppose the
deleted side varies coordinate `g` and has fixed `h`-sign `s`.  Its two
endpoints are `(0,s)` and `(1,s)`.

For endpoint `(t,s)`, the sole same-fibre neighbour is `(t,1-s)`.  In the
four BP equations belonging to the two support groups, this leaves exactly
two deficits:

- through group `g`, a neighbour having sign `1-t`;
- through group `h`, a neighbour having sign `s`.

A C4 fibre has deficit zero.  Its total overlap-block row sum is therefore
zero, so every block between a C4 fibre and an overlapping support is empty.
Consequently both deficits above must be supplied by other exceptional P4
fibres.  In particular, if `H` is the five-edge graph on the seven base
groups whose edges are the P4 supports, every nonisolated vertex of `H` has
degree at least two.

## Port compatibility and the odd-cycle obstruction

At one base group, describe the two endpoint ports of an incident P4 as one
of three categories:

- `V`: the missing edge varies this group; the two `(vertex sign, required
  neighbour sign)` pairs are `(0,1)` and `(1,0)`;
- `F0`: the group is fixed at sign zero; both pairs are `(0,0)`;
- `F1`: the group is fixed at sign one; both pairs are `(1,1)`.

An overlap edge must satisfy the BP requirement at both endpoints.  Hence a
`V` port can pair only with the complementary port of another `V` fibre,
an `F0` port only with `F0`, and an `F1` port only with `F1`.  Ports from the
same fibre cannot pair because a distinct two-group support shares at most
one group.

With five support edges and minimum nonzero degree at least two, `H` is
necessarily either:

- `C5`, with degree sequence `2,2,2,2,2`; or
- `K4-e`, with degree sequence `3,3,2,2`.

At a degree-two or degree-three base group, all incident fibres must have the
same port category: splitting two or three fibres among multiple categories
leaves a category represented by exactly one fibre, whose two ports cannot
be paired outside that fibre.  But on every support edge the missing side is
`V` at exactly one endpoint and `F0` or `F1` at the other.  Thus the port
categories would give a bipartition of `H`.  Both `C5` and `K4-e` are
non-bipartite, a contradiction.

This argument actually disposes of every placement of five P4 supports, not
only the twelve support orbits retained by the spectral square filter.

## Exhaustive audit and symmetry

[`scratch_general_e79_lift_orientation_audit.py`](scratch_general_e79_lift_orientation_audit.py)
performs a solver-free audit of the same conclusion.

For each of the twelve retained support representatives it:

1. checks all `4^5 = 1024` missing-side orientations;
2. derives endpoint ports and exhaustively counts compatible perfect
   matchings independently at all seven base groups;
3. recomputes the exact setwise support stabilizer in `S7`;
4. applies that stabilizer together with all `2^7` coordinate flips,
   deduplicates the induced actions, and forms complete orientation orbits;
5. checks that the orientation-orbit sizes sum to 1024.

The orientation-orbit counts for support IDs
`0,1,2,3,4,5,6,7,8,9,10,16` are respectively

```
34, 38, 51, 56, 45, 9, 12, 38, 24, 58, 12, 24.
```

Every one of the `12 * 1024 = 12288` labelled orientation assignments has
zero compatible overlap-port matchings.  Full machine-readable data are in
[`scratch_general_e79_lift_orientation_audit.json`](scratch_general_e79_lift_orientation_audit.json).

## Claim boundary

- The endpoint-deficit and odd-cycle contradiction above is analytic.
- The new orientation/matching audit is a finite, solver-free exhaustive
  computation with no symmetry-breaking assumption.
- The prior statement that `E0=79` forces five P4 fibres depends on the exact
  finite compression computation in
  `scratch_general_e79_compression_audit.py/.json`.  That audit used CP-SAT,
  independently cross-checked by bounded CNFs, for three boundary
  exclusions, but did not emit formal UNSAT proof certificates.

Accordingly, `E0=79` is eliminated relative to that reproducible compression
classification.  No claim of a formally certified global theorem, and no
claim that an SRG(99,14,1,2) has been constructed, is made here.
