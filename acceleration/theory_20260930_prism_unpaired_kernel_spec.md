# Exact marginal-kernel test after the one capped unpaired pilot

This is a new producer-only mathematical task; no solver retry. The earlier
five-second1260variablepilot returnedUNKNOWN and its artifacts remain frozen.
Keep exactly the same five-matching30cellpatterns, each repeated twice.
Question: do the bit-margin equations force enough complementary component
bits to contradict the odd pairwise Hamming distances required by the Gram?

For each component a and cell g, select its ten patterns. Define one integer
u_t=x_(2t,a)+x_(2t+1,a)-1 in {-1,0,1} per selected pattern. For each of the
other five components b and each of its three cells h, the frozen bit-margin
condition becomes the homogeneous equation

`sum_{t: cells(t,a)=g, cells(t,b)=h} u_t = 0`.

Construct all18literal15x10zero-one matrices. Use exact Fraction row
operations, retaining every operation, row transformation, reduced matrix,
pivot columns and full nullbasis. Check the conjecture: every rank is9 and
its nullspace generator has every coordinate in{+1,-1}. Freeze any contrary
matrix as a counterexample; do not silently alter the claim or selection.
The time limit is120seconds, no floating thresholds, no search seed.

If the conjecture passes, write a conditional proof: each(a,g) has either
all complementary column-pair bits (u=0) or all identical column-pair bits
(u=+/-v). At most one component per cell can have the identical type,
because its joint bits with any second identical component would occur an
even number of times in their four same-cell columns, instead of once each.
Thus at least three components are complementary in every cell. The Gram
requires their full60column pairwise bit distances30, giving distances15
on30representatives, impossible for three binary words.

The resulting candidate theorem would exclude only the frozen five-matching
cell-pattern family with independent bits. It would not exclude arbitrary
six-prism incidence factors or the unrestricted target. No target
automorphism or universal core occurrence is assumed. The new algebraic
certificate requires independent review; producer computations and controls
do not approve their own theorem.

Controls: known exact ranks/nullspaces, identity and zero matrices;
row-operation replay and raw-kernel products; deliberately changed reduced
entries/kernel entries/row-operation indices; literal parity truth tables;
the even-count contradiction in all sixteen possible two-pattern equal-bit
choices. All artifacts remain exact and replayable.
