# Four ternary defects cannot occur in the complete degree14 domain

Producer: /root. Prepared 2026-10-03T04:28:00+00:00.
Status: CANDIDATE pending separate written verification. Timestamp denotes
source preparation, not a computation or claimed graph discovery.

## Exact statement

For every symmetric binary zero-diagonal 99-by-99 matrix A with exact integer
row degree14, define r_uv=(A^2)_uv+A_uv-2 for u<v and let F3 count its
unordered residuals not divisible by3. Then F3 is not4.
Together with the independently reviewed small-support theorem, this implies
F3=0 or F3>=6. No realization of six or more defects is asserted; no target
existence or nonexistence conclusion is drawn.

The proof uses no adjacent-pair count, incidence decomposition, fixed graph,
target automorphism, numerical relaxation or search premise. Every pair and
complete vertex row is included. The four-cycle below is a residual support,
not a prescribed induced subgraph of A.

## Exact argument

As in the separate small-support proof, let D=A^2-12I+A-2J over the integers.
Its diagonal is0 and each complete row sum is0. Put M=D modulo3. It is a
symmetric zero-diagonal matrix over GF(3). Since A is symmetric14-regular,
AJ=JA=14J. Hence AD=DA exactly, and therefore AM=MA over GF(3).

Assume F3=4. The separately audited small-support result forces the four
nonzero unordered entries of M to form a four-cycle, with alternating
nonzero residues. Write its four labelled vertices as1,2,3,4 in cyclic order
for this proof only; this is a notation choice, not a target automorphism
assumption. For some nonzero s in GF(3),

 M_12=s, M_23=-s, M_34=s, M_41=-s,

with symmetric counterpart entries and every other entry zero. In particular
M_13=0. Let z be any of the95 vertices outside this residual support.
The z-row of M is zero, so the (z,2) entry of MA is zero. The corresponding
entry of AM is s*A_z1-s*A_z3. Commutation gives

 s*(A_z1-A_z3)=0 over GF(3).

The nonzero s can be cancelled. Both adjacency entries are literal binary
integers, so their difference belongs to{-1,0,1}; divisibility by3 forces
the exact integer equality A_z1=A_z3. Thus vertices1 and3 have identical
neighborhoods among the95 vertices outside the support.

Vertex1 has14 total neighbors and at most3 within the four-element support.
It has at least11 outside neighbors, all of them also neighbors of vertex3.
Consequently (A^2)_13>=11, and

 r_13=(A^2)_13+A_13-2>=9.

For every distinct pair u,v, nonnegative common-neighbor counts and binary
adjacency give r_uv>=-2. If M_uv=0, the integer r_uv is divisible by3;
a multiple of3 at least-2 must be nonnegative. In row1, only r_12 and r_14
have nonzero residues, so these two entries together are at least-4.
All other off-diagonal entries are nonnegative, and r_13 is at least9.
Thus the complete integer off-diagonal row sum at1 is at least9-4=5.
But exact degree14/order99 gives that sum0, a contradiction. Therefore
F3=4 cannot occur.

## Exact prior premise and falsification boundaries

The support-shape premise is the previously separately reviewed
C-UNRESTRICTED-DEGREE14-TERNARY-SMALL-DEFECT-SUPPORT r1, ordinary binding
764dfa3e0684ee26ff8fbd332260263e1ff32acd82385052cc4f399f100c9f1c.
Its original source d887daf8 and independent audit f083053e remain unchanged.
This new statement is a strengthening, not a correction or refutation of that
necessary-condition theorem, which explicitly asserted no realization of C4.
No new registrar route or changed scientific acceptance rule follows here.

The separate verifier should challenge:

* Full integer row sums and diagonals; exact degree, symmetry, binary entries,
  zero diagonal and order99 are used.
* AD=DA using both AJ=14J and JA=14J, before reduction modulo3.
* The precise residual C4 support and signs; column2 has only the two entries
  at1,3, and every outside row of M is literally zero.
* Conversion of a mod3 equality between binary entries to an integer equality;
  this inference would fail for unrestricted integer or weighted entries.
* The count of at least11 common outside neighbors despite all possible
  internal adjacency choices. No adjacency edge within the support is fixed.
* Every good residual's nonnegativity and the two bad residuals' lower bound;
  the complete row, not a partial sum or floating score, must be checked.
* The written alternating C4 modular support remains valid as a support matrix
  with zero row sums; it fails realization in this adjacency domain because of
  the additional commutation and degree argument, not because the modular
  support control was wrong.

All controls here are proposed written falsification checks. No mathematical
program, graph fixture, solver, formal proof or exhaustive search has run.
External review, novelty and any lower bound beyond six remain unestablished.
Overall search coverage: UNKNOWN; no validated denominator.
