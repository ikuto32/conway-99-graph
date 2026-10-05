# Distinct binary columns rule out a rank-plus-one minimum unbalanced circuit

Status CANDIDATE, source-only written derivation by `/root/structural`.
No mathematical program, fixture enumeration, formal prover or external review
was used. No self-verification, novelty claim, ledger/index/Git change, target
resolution or execution authorization follows. This is a new upper-bound
discovery, separate from the prior affine/lower12 discoveries and their audits.
Current source context is d0c0dd7db0d3de420b1d718b59122b069df01107, ledger
b7d07a8be5cbbce8c2125e631d58f4035ed56a66c2b1e79db27cb56500859f8a,
index618367410b57562be69a658a96c48f7dd1908bd3f58bac806d050cdab0c72632.

## Proposed target statement

For every simple degree14 graph on99 vertices with adjacent common-neighbor
count1 and nonadjacent common-neighbor count2, let B contain every actual
triangle once. Over GF(3), the minimum support of a vector in ker(B) having
nonzero coordinate sum is at most98. Its selected columns form a circuit and
its nonzero coefficients are +1 or -1. This is a necessary target consequence;
it neither forces a specific circuit size/configuration nor excludes a target.

The proposed uses_result premise is revision1 of
C-UNRESTRICTED-TARGET-TERNARY-AFFINE-OBSTRUCTION-UNBALANCED-CIRCUIT-LE99.
Its independently written Native report is
acceleration/results/20261003_independent_review/target_ternary_affine_unbalanced_circuit01/summary.json,
SHA985fa1cc5898f71ec38ed0644513adbb0fe1e58f7fb1eeb8af7c27ec7bca6fb0;
audit acceleration/audit_20261003_target_ternary_affine_unbalanced_circuit_v1.md,
SHAf3e1cffd93fe3dfc32cdb0b764c118f13b56d010d6bc6b6f0ea13ee1ba081e13.
That source proposition had a ROOT-origin affine idea, a Structural discovery
proof and a different-author Native verification. Its current ledger presence
must not be inferred from its report: it is outside the frozen389 cutoff.
This note does not independently approve that report or change it.

For transparency, its required algebra is also reconstructed: N=A+I and
P=A+I-J obey N squared=P, P squared=P, P1=0, BBt=N, B1=1 and Bt1=0 overGF3.
If Bt x=1 then sum(x)=231=0 and Nx=1, hence Px=1, contradicting idempotence
and P1=0. Nondegeneracy of the coordinate pairing therefore supplies a
nonzero-sum right-kernel word. Minimizing its support gives a circuit: a proper
unbalanced dependence is smaller, and a proper balanced dependence can be
subtracted to cancel one coordinate without changing the nonzero sum. Its
size w satisfies w-1<=rank(B)<=98. Thus w<=99 without using either numerical
Gram rank54/55 or any incidence rank upper bound beyond98.

## General column lemma, derived here

Let D overGF3 have N pairwise distinct columns, each literally a binary
0/1 vector. Put r=rank(D) and suppose N>r+1. If ker(D) has a nonzero-sum
word, then its minimum unbalanced support w satisfies w<=r.
No graph, column-weight equality, row regularity or Gram condition is required
for this lemma. Its binary/distinct-column hypotheses are essential below.

Assume contrariwise that w=r+1. A minimum unbalanced word is a circuit by
the preceding cancellation argument, so its first r columns b_1,...,b_r
are a basis of the entire column space. Denote the remaining circuit column b:

    b = sum_i c_i b_i,    c_i in {1,-1},
    alpha = 1-sum_i c_i !=0.

For any extra column d, distinct from all r+1 circuit columns, write uniquely

    d = sum_i a_i b_i,    delta = 1-sum_i a_i.

For theta=1 or -1 the column dependence

    b - theta*d - sum_i(c_i-theta*a_i)*b_i =0

has coefficient sum alpha-theta*delta. If that sum is nonzero, at most one
basis coefficient can vanish: two vanished coefficients would leave at most
2+(r-2)=r support columns, contradicting w=r+1. The two leading columns are
distinct and both have nonzero coefficients. This is the only support count
used in the following exhaustive two cases.

### Case delta=0

Both theta values give nonzero coefficient sum alpha. For each nonzero a_i,
the ratio c_i/a_i is one of the two nonzero field elements. Each ratio can
occur at most once, hence a has support at most two.

Since sum(a_i)=1, support zero is impossible. Support one has coefficient1,
making d a duplicate basis column. With support two, the two coefficients
must both be -1: 1+1=-1 and 1+(-1)=0, whereas (-1)+(-1)=1 overGF3.
Therefore d=-b_i-b_j for two distinct basis columns.

Two distinct literal binary vectors have a coordinate where exactly one is1.
At that coordinate their negative sum is2, which is not binary. Thus this
last possibility also cannot be an extra column of D.

### Case delta!=0

The dependence d-sum a_i b_i is itself unbalanced. By minimality it needs
r+1 support, so every a_i is nonzero. Put eta=delta/alpha in {1,-1} and
choose theta=-alpha/delta=-eta. This is the unbalancing choice because
alpha-theta*delta=2alpha!=0. At most one coefficient can vanish. A coefficient
vanishes exactly when a_i=-eta*c_i; consequently a_i=eta*c_i at every index
except possibly one.

With no exception, delta=1-eta*sum(c_i)=eta*(1-sum(c_i)) implies eta=1.
Then d=b, a duplicate.

With one exception at i, changing eta*c_i to -eta*c_i changes the field sum
by eta*c_i, since -2=1 overGF3. The equation delta=eta*alpha becomes

    1 = eta*(1+c_i).

It forces c_i=1 and eta=-1. Thus a=-c-e_i and d=-b-b_i. This again is the
negative sum of two distinct literal binary columns, and has a coordinate2.

Every extra-column possibility is excluded. Hence D could have at most r+1
distinct columns, contrary to N>r+1. This proves the proposed general lemma.
The contradiction also makes clear that no assumption about real positivity,
ambient symmetry or target completion was inserted in the basis exchange.

## Target application and boundaries

Actual triangle columns are pairwise distinct literal binary columns, and
there are231 of them. The constant left kernel gives r<=98, so231>r+1.
The independently supplied unbalanced-word existence plus the column lemma
gives w<=r<=98. Equivalently, one can only suppose w99; then r98 and the
above proof rules out each of the132 other distinct triangle columns.

The strict column-population boundary matters. D=J4-I4 overGF3 has four
distinct binary weight3 columns, rank3 and kernel spanned by1_4. That generator
has nonzero sum and support4=r+1. This is a hand-derived boundary example,
not a target or executed fixture. D has N=r+1, exactly outside the lemma.
Repeating its columns gives arbitrarily larger N but preserves minimum
unbalanced support4: every dependence aggregates by the four duplicate
classes, whose nonzero-sum aggregate must use all four. Thus distinctness
cannot be replaced by a multiset column count. No such repetitions exist
when every actual triangle is included once.

The binary step cannot be used for arbitrary ternary columns: the negative
sum of two such vectors can be another allowed column. The historical
reduced-Gram countermodel permits entries2 and zero columns and does not
refute this lemma. Conversely, this lemma does not refute that countermodel's
exact limited scope. It also neither proves r<98 nor forces a second left
kernel vector. A possible minimum circuit of size98 remains unexcluded.

## Failed shortcuts and archive overlap

The real Gram has positive eigenvalues21,10 (54 times),3 (44 times), so B has
real rank99. This is not a mod3 rank99 claim. Gram rank55 overGF3 is a lower
bound on incidence rank, not an upper bound; w<=56 cannot be inferred.
The independently checked non-target lambda1/degree14 rank98 fixture and the
reduced-Gram rank98 countermodel preserve those cautions. The latter archived
design is docs/DESIGN_20261003_TERNARY_REDUCED_GRAM_FULL_RANK_COUNTERMODEL_V1.md,
SHA5a5c564e052a46c4958b5e07c3d318d61e3a6fd6e84b86011866080ddc33d95a.

Likewise det(BBt)=21*10^54*3^44 has3-adic valuation45. Cauchy-Binet and the
elementary fact that an integer99minor of mod3 rankr is divisible by3^(99-r)
give 2(99-r)<=45, hence r>=77. This direction cannot shrink the circuit bound.
It is a subsidiary paper derivation here, not a separately verified rank
claim, novelty claim or computational minor check. The new w<=98 proof uses
none of this determinant calculation.

No conclusion forces a12-word or any17-point family. Earlier lower12/cap-core
and completion exclusions retain their exact independent premises and scopes.
No claim that w<=97, a particular balanced word exists, or any target is absent
is made. Different-author whole derivation/falsification is required before
any verified record or binding is prepared.
