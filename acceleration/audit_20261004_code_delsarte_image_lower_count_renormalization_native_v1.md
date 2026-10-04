# Independent written challenge: image lower-count renormalization

Producer: `/root/structural`. Verifier: `/root/native_driver`.
Method: independent derivation and exact hand counterexample challenge.
Scope: the literal generic conditional statement in the frozen candidate;
no target coefficient computation, source execution, or artifact approval.

This audit was written after the candidate and its paper were read in full.
Root supplied the discovery rescaling idea. Agreement with that outline is
not the verification method: the character sum, bound, normalization and
premise failures below are independently reconstructed. Verification ends
at the authentic timestamp stored in the accompanying report. No worker
start is inferred from writing time.

Frozen paper:
`docs/CANDIDATE_20261004_CODE_DELSARTE_IMAGE_COUNT_RENORMALIZATION_V1.md`,
SHA256 `102ab220a98c72599c762996af55c82109e13411f89c6b9ac4f8a1e3994b08ec`.
Frozen raw candidate:
`acceleration/results/20261004_code_delsarte_image_count_renormalization_candidate01.json`,
SHA256 `803240e9e551b19552a538b02f1ba4581f845d50b4bce3ca9817e93d70dc616b`.
Exact claim: `C-CODE-DELSARTE-IMAGE-LOWER-COUNT-RENORMALIZATION`, revision 1.

## Derivation from characters

Let the code C be a linear subspace of F_q^n and let D=C-perp for the usual
nondegenerate coordinate pairing. Use a nontrivial additive character of F_q.
For a vector v of weight i, the sum of its characters against vectors z of
weight j is the coefficient of X^j in

    (1+(q-1)X)^(n-i) (1-X)^i.

Indeed, a zero coordinate of v contributes q-1 nonzero choices, each with
character one. A nonzero coordinate contributes the sum of the nontrivial
characters over nonzero choices, which is -1. This derives the q-ary
Krawtchouk convention and fixes all factors of q, q-1 and code cardinality.
This works for prime-power q, with the trace character when needed.

Sum over v in C first. The inner character sum is |C| for z in D and zero
otherwise: a nontrivial character of a finite additive group sums to zero.
Consequently, with A_i and B_j the actual weight distributions of C and D,

    sum_i A_i K_j(i) = |C| B_j.

For j=0 this gives |C| on both sides because K_0=1 and B_0=1. The code
contains the zero vector exactly once, so A_0=1. These are the normalization
facts required for the proposed statement; no Fourier factor is omitted.

Write F=1+sum_(j=1)^h y_j K_j with all y_j nonnegative. Assume F(i)<=0 for
every nonzero weight that the code can have. We do not require signs at weights
already excluded by genuine premises. Then

    S := sum_i A_i F(i)
       = |C| (1+sum_j y_j B_j)
       >= |C| (1+sum_j y_j ell_j)
       = |C| d.

The inequality uses each nonnegative multiplier separately and the genuine
lower count B_j>=ell_j. On the other hand, A_i>=0 and every occurring
nonzero tail term is nonpositive, so S<=A_0 F(0)=F(0). Since ell_j>=0,
d>=1. Division preserves direction and yields |C|<=F(0)/d. This also proves
F(0)>=d>0 for every code to which all the stated premises apply.

## Exact normalization

Put y'_j=y_j/d. A direct expansion, without an inequality, gives

    1+sum_j y'_j (K_j(i)-ell_j)
      = [d+sum_j y_j K_j(i)-sum_j y_j ell_j]/d
      = [1+sum_j y_j K_j(i)]/d
      = F(i)/d.

Thus every sign at every weight is retained. The standard lower-count dual
has expression constant one before the ell subtraction; its Krawtchouk
coefficient at K_0 is 1/d, not one. This distinction is essential when a
consumer distinguishes a fresh baseline from an already rescaled dual.
The normalized evaluation at zero is exactly F(0)/d, and every multiplier
remains nonnegative. No rounding or floating sign test occurs in this proof.

If some y_j ell_j>0, then d>1 and F(0)>0, so the rational size upper bound
strictly decreases. A dimension upper bound for a linear code is the largest
integer k with q^k<=the bound, so strict rational decrease can still leave
that integer unchanged. For example, two valid upper bounds of six and
eleven both permit dimension at most one when q=5. The statement does not
promise a strict dimension decrease, optimality, or a nonzero code.

## Hand checks and attempted falsifications

For q=5,n=2, the three K_1 values are 8,3,-2 and the three K_2 values are
16,-4,1. With y_1=y_2=1, F is therefore 25,0,0. For the zero code C={0},
the dual is all of F_5^2, with actual B_1=2*4=8 and B_2=4^2=16. Taking
ell_1=8 and ell_2=16 gives d=25 and y'_1=y'_2=1/25. The lower-count form
evaluates to one at zero and zero at both nonzero weights, yielding the
sharp size bound one. Direct character normalization agrees:
25=|C|*(1+8+16).

For C=F_5^2, B_1=B_2=0, so the same positive lower counts are false.
The claimed bound one for this code would contradict its size25, precisely
because the lower-count premise failed. With the true lower counts zero,
d=1 and the unchanged valid bound is25. This is a genuine premise-boundary
test, not an alleged counterexample to a theorem with true lower counts.

Further exact boundaries:

1. Zero lower counts give d=1 and preserve the original polynomial and bound.
2. A multiplier zero at every positive lower count also gives d=1; positive
   counts by themselves do not force a gain.
3. Empty permitted nonzero weight sets allow the zero code; constant F=1,
   all multipliers zero, d=1 is valid there. The paper's impossibility of
   all-zero multipliers is correctly restricted to a nonempty tail set.
4. If one tail value is positive at an actually occurring weight, S<=F(0)
   need not hold. A sign premise cannot be replaced by numerical guidance.
5. If a multiplier is negative, B_j>=ell_j reverses its contribution; the
   lower-count estimate is no longer justified.
6. Negative lower counts or a nonpositive denominator are outside the exact
   stated hypotheses; they are not a valid strengthening of this argument.
7. Reapplying the baseline formula to an already lower-count expression while
   silently treating its K_0 coefficient as one changes the input polynomial.
   The equality above does not license that operation.
8. Counts must concern the actual dual of the actual code. A lower count for
   another image, length, field, or dot-product convention is not substitutable.

The boolean/type and serialization restrictions of a producer are engineering
requirements. This written proof works with exact real coefficients; a rational
certificate checker may deliberately accept only canonical rational strings.
This audit approves neither implementation nor its finite fixture actions.

## Target and overlap boundaries

The generic theorem has no dependency on the target graph. Applying it to the
hypothetical length99 quinary left code still requires its genuine support55
premise and each applicable dual-image lower count. The candidate mentions
924,8316,24948,391776 at weights3,4,5,6; those are not recalculated or newly
approved in this audit. Every actual derived rational candidate still needs
all45 tail values, all32 multiplier signs, exact zero evaluation, and dimension
power comparisons checked in a newly applicable artifact path.

Zero left-code dimension remains possible. Neither the general inequality nor
a target application creates a nonconstant codeword or resolves target graph
existence. The rescaling is algebraically the previously declared lower-count
MacWilliams dual inequality. Root's discovery sharing and this direct overlap
are disclosed; literature novelty is not claimed.

## Review conclusion and exact population

No material mathematical veto was found in the literal conditional revision1.
The review consists of24 written checks: character coordinate factor,
prime-power pairing, character orthogonality, j0 normalization, A0 uniqueness,
nonnegative tail weighting, nonnegative multiplier weighting, lower-count
applicability, d positivity, F0 positivity, bound division, exact rescaling,
K0 coefficient distinction, sign preservation, strict rational gain, integer
dimension boundary, explicit K1/K2 table, zero-code counts, full-space premise
counterexample, zero-count boundary, empty-tail boundary, signed/negative
premise boundaries, repeated-normalization boundary, and target/overlap scope.
Executed mathematical programs, enumeration, source imports, formal proof
commands and external review: all zero. Only file reads, hashing and metadata
writing were used to preserve this source-only written review.
