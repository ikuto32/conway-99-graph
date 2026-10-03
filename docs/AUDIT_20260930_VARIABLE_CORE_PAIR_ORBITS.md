# Independent ordered matching-pair normalization audit

Reviewer: `/root/eight_domain_audit`; producer: `/root/structural_attack`.
The checker imports no producer or earlier orbit-checker implementation. It
uses the exact earlier encoding, complete census, first-stage normalization,
and universal triangle-normalization audit reports as pinned premises.

Let U be all perfect matchings of twelve labelled coordinates. Independent
enumeration recursively joins the least unpaired coordinate to each possible
partner, so every matching occurs once. The recursion gives |U|=11!!=10395.
The raw frozen universe equals this independently enumerated set exactly.
M0 is the standard matching i↔i xor1. For every M in U, the first-stage record
provides a bijection h with h M0 h^-1=M0 and h M h^-1=R_s, where R_s is one
of the eleven first representatives. Every first record and its sixty induced
canonical C0 column images is rechecked in this audit.

For each s, every second-stage record is checked directly: its k is a coordinate
bijection preserving M0 and R_s, and k N k^-1 is the recorded second matching
representative S. The record's first-stage/second-orbit membership and exact
representative agree with the previously independently audited census. Each
of the eleven stage files contains one record for every N in U. Thus the
114345 checked maps are complete for their declared stage populations.
No correctness claim rests on reexecuting the producer's generator traversal.

For an arbitrary ordered pair (M1,M2), use the complete first-stage map h for
M1, obtaining (R_s,N), N=h M2 h^-1. A bijection of coordinates sends every
perfect matching to a perfect matching; its inverse supplies an inverse map
on U. Consequently N belongs to the complete second-stage table for s.
Choose that record's k and put l=k h. Then

    l M0 l^-1=M0, l M1 l^-1=R_s, l M2 l^-1=S.

This proves coverage of all10395^2=108056025 labelled ordered pairs, without
iterating their Cartesian square. The recorded10395 composed examples are
separate controls, not the coverage proof. The weighted census computation
sum_s |first_orbit_s|*10395 gives the same named population. Representatives
number3580, and their exact order and distinctness are checked against the
frozen census. Distinctness of group orbits uses that census as an explicit
premise; no stronger classification of triples (M1,M2,P) is claimed.

Apply any such l simultaneously to all three fibres, fix the distinguished
triangle, and permute the sixty remaining vertex labels by
{a,b}↦{l(a),l(b)}. This is a permutation of the canonical nonmatching pairs
because l preserves M0. Let R and Q be the resulting row and column permutation
matrices. The transformed core and factor are C'=R C R^T and F'=R F Q^T.
The identity cross matchings remain identity. P becomes l P l^-1 and ranges
over all permutations, with no involution, commutation or fixed-point condition.
C0 remains its exact canonical incidence matrix. Row and fibre-column margins
are preserved. By associativity and permutation inverses,

    F'F'^T=R(FF^T)R^T,
    (I+C')F'=R((I+C)F)Q^T,
    F'^TF'=Q(F^TF)Q^T.

The prescribed Gram 12I-C-C^2+2J-diag(J12,J12,J12) transforms by R, since R
preserves fibres. Therefore all Gram equations, all mixed caps and all
distinct-column caps are preserved for every binary F and every allowed P.
This is a universal algebraic identity. The literal matrix controls are checks
of an implementation of it; they are not the justification for universality.
The transformation relabels a possible graph; it does not assume the graph
has a nontrivial automorphism. No component restrictions are introduced.

The new CNF is the byte-identical original arbitrary-core formula body plus
42961 clauses: one positive disjunction over3580 fresh selector variables,
and twelve binary implications for each representative's six M1 and six M2
positive edges. The independently checked base exact-one matching rows imply
that these twelve positive edges determine both matchings completely. Two
distinct representative pairs differ in at least one edge; both cannot be
selected simultaneously. Hence the suffix is exactly the union of the3580
listed matching-pair cases. The checker derives the66 lexicographic edge IDs
per matching from the primary-variable layout and reconstructs every clause.
No P, incidence or base-auxiliary literal is newly constrained by the suffix.

Every base primary solution has a relabelled primary solution satisfying the
suffix. The audited bidirectional auxiliary encoding supplies auxiliary values
for that solution; no literal permutation of prefix-state variables is needed.
Conversely, projecting an augmented assignment to base variables gives a base
assignment. Thus the two formulas are equisatisfiable, though their sets of
labelled primary assignments differ. With the separate universal triangle
normalization premise, every Conway99 target graph yields an augmented-model
solution. The converse does not yield a complete graph: residual D is absent.
SAT establishes at most a necessary factor; UNSAT would require an actual
complete independently replayed proof. This audit launches no solver.
