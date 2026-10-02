# Rejected codomain-isotropy inference: preserved argument and exact counterexample

This is a candidate audit protocol until its separate checker completes. It
preserves a failed structural proposal, rather than a target-resolution claim.
The proposal's author is `/root/structural`; the counterexample was supplied
by `/root`. The checker imports no counterexample-producing code.

The proposed argument began with a hypothetical target's binary triangle
incidence matrix B, M=BB^T=I+A, and P=I-M=A. The adjacency identity gives
A^2=A over GF(2), rank(A)=54 and rank(M)=45. It then set C=PB and correctly
calculated CC^T=0, but incorrectly inferred rank(C)<=27 by treating the
54-dimensional codomain as the isotropic space. That invalid inference was
used to propose rank(B)<=72 and dimension(ker(B^T))>=27. Neither proposed
target bound is established. The relevant archived overlap is the pinned
external_conway99_research/attempts/wave102-prism-incidence-code/derivation.md,
section1, which records only45<=rank(B)<=99 and support constraints; historical
labels are not fresh verification. No novelty is asserted.

CC^T=0 says that C's rowspace is totally isotropic in its231-coordinate domain;
it does not say that its columns are mutually orthogonal in the99-coordinate
codomain. Even [I54 I54] has zero row Gram and rank54.

For the exact99x231 counterexample, let P have27 diagonal3x3 blocks J3+I3
and18 zero coordinates. Let M=I+P. B initially has27 disjoint weight3 block
indicators and18 remaining unit columns. For each3-block append two copies
of e0+e2 and two copies of e1+e2. Append78 zero columns, giving231 columns.
The duplicated columns cancel in BB^T. The complete factor has rank99;
PB has rank54 while (PB)(PB)^T=0. This refutes the claimed generic linear
algebra implication. The synthetic columns include weights0,1 and2, so the
counterexample does not refute any independently stated rank bound restricted
to actual linear3uniform7regular target incidence matrices. Conway-99 remains
UNKNOWN.

Before launch, freeze this exact raw construction and checking criteria:
full integer scalar dot products modulo2 establish P symmetry/zero diagonal,
P^2=P, M^2=M, PM=0, BB^T=M, C=PB and CC^T=0; a separate row elimination
computes ranks54,45,99,54. Preserve the raw matrix bitsets and all pins.
Controls include [I54 I54], one changed duplicate factor column which must
break BB^T=M, and one changed diagonal in P which must break idempotence.
Any disagreement vetoes the counterexample audit. No target graph is decoded,
and no code-size computation or scientific search is performed.

The contained allocation is30seconds outer/20seconds worker/10seconds reserve,
based on only99x231 bitsets and complete99x99 products. Record source commit,
exact command, Python/environment pins, artifact hashes, actual exit and cleanup.
An independent counterexample check establishes only the rejected-step scope;
it cannot establish a graph-specific bound or its negation.
