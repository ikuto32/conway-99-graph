# Candidate Hadamard construction of collapsed identity-P supports

Assume an identity-cross inner core with arbitrary perfect matchings M0,M1,M2.
For a binary target incidence F, let L[a,d] be the sum of its three fibre rows
at coordinate a. The already checked Gram-zero lemma makes this sum binary.
Its row sums are30 and column sums6. Summing the nine fibre blocks of the exact
factor Gram gives

`L L^T = 15I + 15J - 5(M0+M1+M2)`.

Consequently X=2L-J has row sums0 and satisfies
`X X^T = 20(3I-M0-M1-M2)`.

The producer explicitly constructs and checks a20-by20 sign matrix H with
H^T H=20I, a constant first column and balanced other columns. For matching
M_g, assign six distinct nonconstant columns of H to its six ordered pairs.
Place that sign column on one endpoint and its negative on the other, viewed
as a12-by20 matrix X_g. Orthogonality then gives
`X_g X_g^T=20(I-M_g)`. Its row sums are zero, and each column has six signs of
each type because pair endpoints are opposite. Concatenating X0,X1,X2 gives
the required X identity and L=(X+J)/2 has all required collapsed margins and
Gram. This is an explicit construction of L, not of the full F.

In this experiment H is computed by the stated quadratic-character formula
modulo19 and its400entries of H^T H are checked directly. No unverified
Hadamard-existence theorem or floating computation is needed for this finite
construction. The choice of the first six nonconstant H columns, pair ordering,
and endpoint signs is a restriction of the construction search.

To lift L to F, each of its six selected coordinates in a column must be
assigned exactly one fibre, two to each fibre. Pair assignments contradicting
a zero full-Gram entry are forbidden. In each fibre all sixty nonmatching
coordinate pairs must occur exactly once, so a column-to-pair perfect matching
is a necessary projection. Pairwise column overlap caps and exact Gram-entry
capacities give other necessary projections. Passing all such tests does not
make their separate choices jointly compatible, and supplies no F or D.

This note is CANDIDATE pending independent verification. The support identity
and construction may overlap archive or literature results; no novelty is
claimed. The recorded archive keyword search has limited scope, not exhaustive
coverage. No automorphism of a hypothetical target is assumed. Failed lifts of
one selected L cannot exclude other supports or the unrestricted target.
