# Small ternary defect supports on the complete degree14 domain

Producer: /root. Prepared 2026-10-03T04:06:27+00:00.
Status: CANDIDATE pending a separate written derivation and falsification audit.
No executable calculation, scientific run or ledger promotion is claimed.

## Precise statement

For every symmetric binary zero-diagonal 99-by-99 matrix A having exact
integer row degree14, define the unordered integer residual
r_uv=(A^2)_uv+A_uv-2 for u<v, and let F3 count unordered pairs for which
r_uv is not divisible by3. Then

 F3 is in {0,4} union {6,7,8,...,4851}.

If F3=4, its four nonzero residue pairs form a simple four-cycle on four
vertices, whose residues alternate1,2,1,2 around the cycle. This is a
necessary condition only; no degree14 graph realizing four defects is
asserted. In particular the claim does not assert that the allowed values
are all realizable. No adjacent-pair count, incidence decomposition,
automorphism, floating arithmetic or search coverage premise is used.

## Written derivation

Put D=A^2-12I+A-2J over the integers. Exact degree14 gives
A*1=14*1 and A^2*1=196*1. Therefore

 D*1=(196-12+14-198)*1=0.

The diagonal entries of D are14-12-2=0. Reduce D modulo3, using residues
0,1,2, and call the resulting symmetric zero-diagonal matrix M. Its row
sums vanish over F3. The support graph H has an edge uv precisely when
M_uv is nonzero; its edge count is F3. A nonisolated vertex cannot have
support degree1, since its row would then have one nonzero summand. Thus
every nonisolated support vertex has degree at least2.

At support degree2, the two incident residues must be opposite (1 and2).
At support degree3, all three incident residues must agree: the possible
numbers of residues1 are0,1,2,3, and their integer sums are6,5,4,3;
only0 or3 choices give a sum divisible by3. These statements concern
the complete support row, including every nonzero residue pair.

Let e be the support edge count, and v the number of nonisolated vertices.
The degree lower bound gives v<=e. Simplicity gives at most binomial(v,2)
edges. Thus e=1 or2 is impossible. For e=3 the only possibility is a
triangle (v=3, all support degrees2). Degree2 forces opposite residues
on consecutive edges. Returning around an odd cycle contradicts the
initial nonzero residue. Consequently e=3 is impossible.

For e=4, v must be4: three vertices hold at most three simple edges.
All four degrees are2, so H is a four-cycle. The degree2 row condition
forces alternating residues, exactly as stated.

For e=5 there are only two possibilities. If v=5, every degree is2,
and H is a five-cycle, ruled out by odd-cycle alternation. If v=4,
H is K4 with one edge removed, with degrees3,3,2,2. Call the adjacent
degree3 vertices x,y and the nonadjacent degree2 vertices a,b. The
degree3 row condition at x forces M_xy=M_xa=M_xb=s for a nonzero s;
the degree3 row condition at y forces M_yx=M_ya=M_yb=t. Symmetry on
xy gives s=t. But the degree2 condition at a gives
M_ax+M_ay=s+t=2s, which is nonzero in F3. This is a contradiction.
At most three vertices cannot hold five edges. Hence e=5 is impossible.

These cases prove the statement without an enumeration program. They
classify small support matrices, not the existence of adjacency matrices
that give rise to them. Larger edge counts are left unresolved.

## Falsification boundaries for the separate verifier

* Check the complete integer row/diagonal calculation independently; degree,
  symmetry, zero diagonal and all99 vertices are required hypotheses.
* Challenge the transition from row sums to minimum support degree2; isolated
  vertices must be discarded from v, and no residue may be silently omitted.
* Check that degree3 admits only three equal nonzero residues over F3.
* Check all simple support possibilities with3,4,5 edges, including a possible
  disconnected support. A component with minimum degree2 needs at least3
  edges, so two nontrivial components need at least6 edges.
* Check the four-cycle positive support matrix with alternating residues:
  all four rows sum to0 modulo3. This is a written matrix control, not a
  degree14 adjacency fixture or a claimed realized defect.
* Check the six-edge positive support matrix K4 with every residue1: each
  row sums to3 modulo3. This shows the purely modular support argument
  cannot exclude every nonzero support. It is not an adjacency realization.
* Deleting one edge from either support control leaves a row with a forbidden
  sum. Allowing loops, asymmetric entries or a partial set of pair residuals
  invalidates this proof's support graph reduction.

## Scope and relationship to prior work

The earlier energy paper82f927 proves scalar metric bounds and global/per-row
residue congruences. This proof uses the same independently elementary row
sum calculation and the additional symmetry of the complete residual matrix;
it does not rely on a recorded claim status. It strengthens the earlier
necessary scalar condition on F3=2 without refuting that conditional condition.
The degree14 ternary-exactness paper274ce3 separately connects F3=0 to the
target integer identity; that theorem is not needed to exclude support sizes.
This result supplies neither a positive target graph nor a general
nonexistence proof. Overall search coverage: UNKNOWN; no validated denominator.
