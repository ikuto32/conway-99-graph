# Candidate exactness of the complete ternary adjacency equation

Producer: `/root`. Status: CANDIDATE pending an independently revision-bound
written audit and claim-ledger registration. Source context is public commit
00ffb6fdd7d91bd38269e1cc5e6b214ebf7591c8; this new working document is separately
identified by its SHA256. No computation or scientific worker is launched here.

Claim revision 1: For every 99-by-99 symmetric binary matrix A with zero
diagonal and exactly 14 ones in every row, A^2 = 12I - A + 2J over the integers
if and only if A^2 = -A + 2J over GF(3). Both equations refer to every matrix
entry. I and J have order 99. No adjacent-common-neighbor assumption, incidence
rank, automorphism, connectedness or fixed local configuration is assumed.

Fix a row u. The off-diagonal entries c_uv of A^2 are nonnegative integer common
neighbor counts. Regularity gives their sum as 14^2 - 14 = 182. There are 14
adjacent endpoints and 84 nonadjacent endpoints. The ternary equation requires
c_uv congruent to 1 at adjacent endpoints and to 2 at nonadjacent endpoints.
Nonnegativity therefore gives respective lower bounds 1 and 2. Their total
lower bound is 14 + 84*2 = 182, already equal to the row sum. Every bound must
be attained: adjacent counts are 1 and nonadjacent counts are 2. The diagonal
entries are 14 = 12 + 2. Thus the full integer equation holds. Conversely,
reducing that integer equation modulo 3 removes 12I and proves the ternary
equation.

This equivalence is not a construction or exclusion. Existence remains UNKNOWN.
An incomplete set of ternary equations, a rank condition, degrees correct only
modulo 3, floating-point residues, or a synthetic factor with different integer
degrees does not establish its premise. Any discovered adjacency must still
pass the separate complete integer SRG validator. Novelty and external review
are UNKNOWN. Overall search coverage: UNKNOWN; no validated denominator.

The different-author paper-only note
DESIGN_20261003_TERNARY_RESIDUE_EXACTNESS_V2.md, SHA256
424e9ee705ea9a46fb2ca755e7470992c4825d7ac508ee3b34a2d2673be02170,
contains a separate derivation and weakened-premise checks. That note predates
this frozen producer artifact, so it is not by itself a hash-bound audit of
this particular claim revision. A separate written identity/scope audit is
required before registration; no successful audit is invented here.
