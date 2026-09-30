# Independent shared-block rule audit

The exact five populations in the producer's frozen certificate are
`A,A,B,B` and the six 3 by 3 permutation matrices; the raw group order is
`A,B,A,B,P`. No target automorphism is assumed. We check a conditional finite
matrix implication and its literal first/third-profile instantiations.

Write x for the number of second A matrices and y for the number of second B
matrices. The four exceptional matrices contribute zero at (1,1), so a sum
equal to 2J-I forces P to fix 1. Thus P is the identity or swaps 0 and 2.
The entries (0,2), (2,0), (0,0) give, respectively,
`x=P[0,2]`, `y=P[2,0]`, `x+y+P[0,0]=1`.
The swap gives 2=1, so P=I and x=y=0. Conversely, twice A0 plus twice B0
plus I is exactly 2J-I. This proves the implication over the integers.

Before running: independently check all 96 finite combinations, reconstruct
all raw choice projections for both profiles, derive all retained indices,
check all six common fibre relabellings, and reject changed targets, vectors,
retained indices and alleged extra solutions. The checker imports no producer
code and relies on prior independently checked encoding/domain coverage.
Budget: 60 seconds, no solver, no floating point, full finite checks.

The rule removes choices but excludes neither profile by itself. The proof
cores, other propagation counts and numerical LP results in the producer's
broader analysis are not independently approved by this narrowly scoped audit.
