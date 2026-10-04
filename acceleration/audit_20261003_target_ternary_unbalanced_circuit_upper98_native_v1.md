# Independent written audit of the upper98 unbalanced-circuit consequence

Verifier: `/root/native_driver`. Discovery and candidate proof: `/root/structural`.
This is a complete written derivation and attempted falsification of candidate
`docs/CANDIDATE_20261003_TARGET_TERNARY_UNBALANCED_CIRCUIT_UPPER98_V1.md`, SHA256
`c44d774b841b1466ce7e040df261a99b15b44502a74dc2d32c71804a29682dd5`.
No mathematical program, computational fixture, formal prover or external reviewer
was used. The candidate and the earlier ROOT-origin affine idea were read and are
shared origins; the reasoning below was independently reconstructed. No ledger,
index, Git, target-resolution or execution approval follows from this audit.

The exact target implication survives the checks below: for every simple graph
on99 vertices of degree14 with adjacent common-neighbor count1 and nonadjacent
count2, let B contain every actual triangle once. Over GF(3), the minimum support
of a word in ker(B) having nonzero coordinate sum is at most98. Its selected
columns are a circuit and its nonzero coefficients are +1 or -1.

The explicit uses_result dependency is revision1 of
`C-UNRESTRICTED-TARGET-TERNARY-AFFINE-OBSTRUCTION-UNBALANCED-CIRCUIT-LE99`,
Native report `acceleration/results/20261003_independent_review/target_ternary_affine_unbalanced_circuit01/summary.json`,
SHA256 `985fa1cc5898f71ec38ed0644513adbb0fe1e58f7fb1eeb8af7c27ec7bca6fb0`.
Its written audit has SHA256
`f3e1cffd93fe3dfc32cdb0b764c118f13b56d010d6bc6b6f0ea13ee1ba081e13`.
That dependency is not a claim about its current ledger registration. I also
reconstruct its needed algebra below. Neither withdrawn rank55-for-P nor any
numerically observed incidence rank is a premise.

## Minimum words and the exact general lemma

Work over GF(3). A word is unbalanced when its coordinate sum is nonzero.
Let D have N pairwise distinct columns, each literally a binary0/1 vector,
and rank r. Assume N>r+1 and an unbalanced word exists in ker(D). I establish
that its minimum possible support w is at most r.

First, a minimum unbalanced word has circuit support. A proper-subset kernel
word with nonzero sum already contradicts minimality. If a nonzero proper-subset
kernel word has zero sum, subtract an appropriate nonzero scalar multiple to
cancel one selected coordinate of the minimum word. The resulting kernel word
still has the original nonzero sum and a strictly smaller support. Thus no
proper subset is dependent. Removing one column from a circuit leaves an
independent set, so w-1<=r and w<=r+1. If r=0, pairwise distinct columns are all
zero and permit at most one column, contradicting N>1. Hence the only case
needing exclusion is r>=1 and w=r+1.

Suppose w=r+1. Its first r columns b_i are a basis of the entire column space.
Normalize the last coefficient to write the remaining circuit column as

    b = sum c_i b_i,   every c_i in {1,-1},   alpha = 1-sum c_i !=0.

Every extra column d has a unique expression d=sum a_i b_i; put
delta=1-sum a_i. For theta=1 or -1 the relation

    b - theta*d - sum (c_i-theta*a_i)b_i =0

has coefficient sum alpha-theta*delta. The two leading columns are distinct
and have nonzero coefficients. Whenever this sum is nonzero, at most one
basis coefficient may vanish: two or more vanishings would leave support at
most 2+r-2=r, contradicting w=r+1. This bound is the source of both branches.

If delta=0, both theta values are unbalanced. Each nonzero a_i makes precisely
one of c_i-a_i or c_i+a_i vanish, because c_i/a_i is +1 or -1. At most one
vanishing is allowed for each theta, so at most two a_i are nonzero. Their
sum is1. Zero nonzero coefficients is impossible. One forces a_i=1 and
d=b_i, a duplicate. Two force both coefficients to be -1, since in GF(3)
the other possibilities sum to0 or-1. Then d=-b_i-b_j. Distinct literal binary
b_i and b_j have a coordinate with exactly one entry1. Their negative sum
has entry2 there, so d cannot be a literal binary column. This exhausts delta0.

If delta!=0, the relation d-sum a_i b_i is unbalanced. Its support is
1+|supp(a)|, so minimality forces all r coefficients a_i to be nonzero.
Write eta=delta/alpha, which is +1 or -1, and choose theta=-eta.
Then alpha-theta*delta=2alpha!=0. A basis coefficient vanishes precisely
when a_i=-eta*c_i. At most one may do so; every other coefficient therefore
equals eta*c_i.

With no exceptional coefficient, delta=1-eta*sum c_i=eta*alpha implies
1=eta, hence d=b, a duplicate. With one exception at i, replacing eta*c_i
by -eta*c_i changes the sum by eta*c_i, since -2=1 in GF(3). Thus

    1-eta*(sum c_i+c_i) = eta*(1-sum c_i),
    1 = eta*(1+c_i).

If c_i=-1 the right side is0. Thus c_i=1 and eta=-1. The coefficient vector
is a=-c-e_i, making d=-b-b_i. The two columns b and b_i are distinct literal
binary vectors, so their negative sum again has an entry2. It is not binary.

Both branches exclude every extra column. This contradicts N>r+1, proving
w<=r. No row regularity, equal column weights, graph interpretation,
real positivity or extra rank bound was used.

## Reconstructed target algebra and application

Every edge lies in exactly one triangle because adjacent vertices have exactly
one common neighbor. The graph has 99*14/2=693 edges and hence231 actual
triangles. The fourteen neighbors of a vertex split into seven disjoint pairs
through those triangles, so each row of B has weight7, and each column has
weight3. Distinct actual triangles give distinct literal binary columns.
Integer identities are

    A^2=12I-A+2J,   BB^T=7I+A.

Modulo3, set N=A+I and P=N-J. Direct multiplication gives N^2=P.
Also N1=15*1=0, NJ=JN=0, J^2=99J=0, P^2=P and P1=0.
The incidence identities become BB^T=N, B1=1 and B^T1=0.

If B^T x=1_231, summing coordinates gives 7*sum(x)=231=0, so Jx=0.
Multiplication by B gives Nx=1, hence Px=1. But P^2=P then implies
P1=1, contradicting P1=0. The affine system has no solution. If the
coordinate-sum functional were zero on all of ker(B), nondegeneracy of the
coordinate pairing would put 1_231 in rowspace(B), giving that very affine
solution. Therefore an unbalanced right-kernel word exists.

The nonzero constant vector lies in the left kernel of B, so r=rank(B)<=98.
Its231 distinct binary columns satisfy231>r+1. The independently proved
general lemma yields w<=r<=98. The selected columns form a circuit by the
minimum-support argument, with each nonzero coefficient one of the two
nonzero field elements. This applies to every exact target without symmetry
or a retained construction decomposition assumption.

## Hand falsification and hypothesis boundaries

1. The strict population condition is essential. D=J4-I4 has four distinct
   binary columns. D1=0; on the three-dimensional coordinate-sum-zero space
   D=-I, and that space is complementary to span(1_4) because sum(1_4)=1.
   Thus r=3, ker(D)=span(1_4), and its minimum unbalanced support is4=r+1.
   Here N=r+1, so the example does not meet the lemma's strict inequality.
2. Distinctness is essential. Repeating these four column classes makes N
   arbitrarily large. Aggregating coefficients in each class gives a word
   in the original kernel. Any nonzero-sum aggregate is a nonzero multiple
   of1_4 and needs a nonzero coefficient in each class. Minimum unbalanced
   support therefore remains4 despite the multiset population increase.
3. Literal binary entries are essential. In GF(3)^2 take e_1=(1,0),
   e_2=(0,1), b=(1,2) and d=(2,2). These are four nonzero pairwise
   projectively distinct columns of rank2, so no support1 or2 dependence
   exists. The relation b-e_1+e_2=0 has sum1 and support3=r+1, while
   N=4>r+1. Entries2 put this exact counterexample outside the binary lemma.
4. A zero column, when r>=1, gives an unbalanced support1 word and satisfies
   the conclusion. Rank0 under the strict distinct-population premise is
   impossible, as handled before the basis proof.
5. The coefficient-sum cancellation is necessary: ordinary circuit
   minimality alone would not justify retaining unbalancedness after a
   proper-subset dependence. Both balanced and unbalanced subcases above
   preserve the required quantifier.
6. A rank98 target is not excluded by the conclusion, and a minimum
   circuit of size98 is not ruled out. The proof establishes neither
   rank<=97 nor another left-kernel vector, and does not force support12.

The candidate's subsidiary determinant direction was checked on paper:
det(BB^T)=21*10^54*3^44 has3-adic valuation45. Divisibility of99-minors by
3^(99-r) gives2(99-r)<=45 and r>=77. That is a lower rank bound, not an
upper bound and not a premise of this proof. No separate rank claim or
computational minor verification is made here.

## Verification limits

The audit is a different-author complete written verification of a conditional
necessary implication. It does not resolve target existence/nonexistence,
sharpness, novelty, a prescribed circuit configuration or any external claim.
All hand examples are algebraically derived, not executed or calibrated.
The prior affine discovery and Structural candidate are disclosed shared
origins; the new case analysis and boundary counterexamples were reconstructed
independently. A future claim adapter must bind the exact prior revision and
this report; no ledger registration or computational approval is supplied.
