# Independent written audit: four ternary defects in the degree14 domain

Discovery producer: ROOT. Independent verifier: Checkpoint.
The unchanged candidate is
`docs/CANDIDATE_20261003_TERNARY_FOUR_DEFECT_NONREALIZABILITY_V1.md`,
SHA256 08845d97676d050b137e8183f10d38bf3df2424b71aa2997db9fb82384f86364.
This is a separate exact written derivation. No mathematical program, graph
fixture, solver or exhaustive computation was executed. The modular support
checks below are written matrices, not adjacency realizations. External review,
formalization and novelty are not established.

## Exact statement checked

For every 99-by-99 symmetric binary zero-diagonal matrix A with exactly 14 ones
in each integer row, put r_uv=(A^2)_uv+A_uv-2 for u<v and let F3 count all
unordered residuals not divisible by 3. Then F3 is not 4. Together with
C-UNRESTRICTED-DEGREE14-TERNARY-SMALL-DEFECT-SUPPORT r1, this gives F3=0 or
F3>=6. No realization of any allowed value and no target existence or
nonexistence conclusion is asserted.

The exact prior premise is the necessary support-shape result, whose binding is
`acceleration/results/20261003_independent_review/ternary_small_defect_support01/claim_binding_schema2.json`,
SHA256 764dfa3e0684ee26ff8fbd332260263e1ff32acd82385052cc4f399f100c9f1c.
Its separate written audit is f083053e29d51488d9dc4e6d624fde2781b36a5921a25912ae9d57b7058bcab8,
and its report is 74b3043bb5ea79603db65bf6d6f11504274cf5be189525a204d8f6c014946246.
That theorem asserted no adjacency realization of a four-cycle support. The
present result strengthens it; it does not refute or revise its original claim.

## Separate derivation and row-budget contradiction

Define the integer matrix D=A^2+A-12I-2J. Because A is symmetric and binary,
(A^2)_uu=14. Consequently D_uu=14-12-2=0. For each vertex u, the complete
common-neighbor row sums to 14*14=196, so its off-diagonal residual row sums to

 (196-14)+14-2*98=0.

Equivalently D times the all-ones vector is zero. This is an exact complete-row
identity; degree known only modulo 3 or a partial row would not suffice.

Symmetry and exact regularity imply AJ=JA=14J. Expanding both products gives

 AD=A^3+A^2-12A-2AJ,
 DA=A^3+A^2-12A-2JA.

Thus AD=DA over the integers. Reduction modulo 3 gives AM=MA, where M=D mod 3.
This calculation uses neither a target spectral assumption nor a numerical
matrix identity.

Assume F3=4. The pinned prior theorem forces the support of M to be a simple
four-cycle with alternating nonzero residues. Name its vertices a,b,c,d in
cyclic order, and write

 M_ab=s, M_bc=-s, M_cd=s, M_da=-s,

where s is either nonzero field element. Every other unordered entry is zero.
These names are a choice of notation, not an automorphism assumption about A.
The four-cycle is a residual-support graph; none of its pairs is prescribed to
be an adjacency edge.

For any vertex z outside these four, the entire z-row of M is zero. Evaluate
the (z,a) entry of AM=MA. The right side is zero and the left side is
s*A_zb-s*A_zd. Since s is invertible, A_zb=A_zd modulo 3. Binary entries can
differ only by -1,0,1, so this is also equality of the literal integers. Hence
b and d have the same neighbors outside the four-vertex support.

At most three of b's 14 neighbors lie inside that support. Therefore at least
11 lie outside it and are also neighbors of d, giving (A^2)_bd>=11. Since
A_bd>=0,

 r_bd=(A^2)_bd+A_bd-2>=9.                         (1)

There is an independent upper bound from b's complete integer row. Every
off-diagonal residual is at least -2. A good pair has residual divisible by 3,
so the lower bound -2 makes every good residual nonnegative. Row b has only
two bad pairs, ba and bc. Their sum is at least -4. All its good residuals are
nonnegative, and the whole row sums to zero. In particular r_bd<=4. It is a
good residual, hence a multiple of 3, which improves this to

 0<=r_bd<=3.                                      (2)

The bounds (1) and (2) contradict one another. Equivalently, the good pair bd
would have at most five common neighbors, while commutation forces at least
11. This completes the proof for every possible internal adjacency among the
four support vertices and every possible integer residual on the two bad pairs.

## Written falsification inventory (12 checks, zero executed fixtures)

1. Recompute the diagonal from symmetry and literal binary entries: 14-12-2=0.
   Weighted entries could change both the diagonal and this domain argument.
2. Recompute each complete off-diagonal row as 182+14-196=0. The zero sum is
   integer, not just modular or global across all rows.
3. Expand AD and DA separately. Both AJ and JA equal 14J; regularity without
   the required column degrees would not justify their equality.
4. Recheck the prior four-edge classification: minimum support degree two and
   four edges force a connected C4; degree-two row sums force alternating signs.
   This uses the pinned theorem, rather than an unverified support catalogue.
5. For both s=1 and s=2, column a has exactly the entries s at b and -s at d.
   The commutator equation has no omitted third term or sign choice.
6. The outside z-row of M is literally zero. Vertices a,b,c,d themselves are
   not substituted into that equation; they may have arbitrary internal edges.
7. The three binary differences -1,0,1 have only one value divisible by 3.
   In contrast, weighted entries 3 and 0 are congruent but unequal; that proposed
   weakening of the binary premise would invalidate the twin conclusion.
8. A support vertex has at most three distinct internal neighbors. Allowing
   all three gives the weakest outside-neighbor bound, 14-3=11, and still fails.
9. Symmetry turns each common outside neighbor into a positive term of
   (A^2)_bd. Whether b and d themselves are adjacent cannot reduce this count.
10. A good residual is a multiple of 3 and at least -2, so none can be negative.
    A hypothetical -3 would violate nonnegative CN plus binary adjacency.
11. Both bad residuals can be given their most favorable lower bound -2.
    Even this relaxation permits at most 4 total good residual in the row;
    divisibility bounds the single good pair bd by 3. No bad-residue sign or
    extra nonnegative good term can remove the contradiction with 9.
12. The alternating modular C4 still has zero complete support-row sums and is
    a valid written modular control. The new obstruction is its realization as
    a commuting residual of this adjacency domain; no claim is made that the
    prior positive support control was wrong or represented a graph.

## Verdict and limits

VERIFIED within the exact statement above by this independent written
derivation. The argument separately reconstructs AD=DA, uses the other pair of
opposite support vertices, and compares an integer row-budget upper bound with
the common-neighbor lower bound. Agent agreement and finite example counts are
not evidence for the universal conclusion.

The exact prior support theorem is a mathematical dependency. Its producer is
ROOT and its verifier is this same Checkpoint identity; that prior shared
verification is disclosed, and its raw proof and report are pinned. No prior
energy, incidence, lambda1, rank, fixed graph, symmetry, numerical or search
result is required. The new producer remains ROOT, distinct from this verifier.

This excludes only the value F3=4 in the stated degree14/order99 domain. It
does not exclude F3=0, classify all larger supports, construct an adjacency
realization, prove Conway-99 nonexistence, approve an engine or establish a
target-wide coverage percentage. Formalization, external review and novelty
remain unestablished. Overall search coverage: UNKNOWN; no validated denominator.
