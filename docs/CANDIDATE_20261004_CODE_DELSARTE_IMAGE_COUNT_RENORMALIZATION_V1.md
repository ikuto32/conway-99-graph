# Candidate: exact image-count rescaling of a code dual

Root supplied this algebraic improvement to the earlier analytic candidate.
Structural derives the formula and its premise boundaries here. No rational
target calculation or code enumeration ran. This is a separate source-only
mathematical candidate; an independent written challenge remains required.

Let C be a linear code over a prime-power field with length n and dual D.
Let K_j be its q-ary Krawtchouk polynomials and suppose
F(i)=1+sum_(j=1)^h y_j K_j(i), with y_j>=0 and F(i)<=0 at every permitted
nonzero weight of C. Write A_i for C's weight distribution and B_j for D's.
MacWilliams character orthogonality gives
sum_i A_i K_j(i)=|C| B_j.

Suppose separately justified lower counts ell_j satisfy 0<=ell_j<=B_j.
Put d=1+sum_j y_j ell_j. Then d>=1, and
sum_i A_i F(i)=|C|(1+sum_j y_j B_j)>=|C|d.
Since A_0=1 and all remaining F values are nonpositive, the same sum is at
most F(0). Consequently |C|<=F(0)/d.

Equivalently set y'_j=y_j/d and use the standard lower-count dual form
F'(i)=1+sum_j y'_j(K_j(i)-ell_j).
Expanding its constant gives F'(i)=F(i)/d exactly, at all weights.
Therefore every tail sign is retained and the new exact size bound is F(0)/d.
If some y_j ell_j>0, the rational size bound is strictly smaller; the integer
dimension bound need not change. No rank improvement is promised.

For q5/n2, y1=y2=1 gives F values25,0,0. For the zero code C={0}, its dual
is the full space, with B1=8 and B2=16. These exact lower counts give d25,
multipliers1/25,1/25 and F' values1,0,0: the sharp size bound is one.
For C equal to the full space, its dual is zero and those positive lower
counts are false. Applying the same bound one to that size25 code would
therefore be an invalid premise, not a counterexample to the algebra.

Zero lower counts return the original bound. All-zero multipliers cannot
produce a nonempty-tail dual in the first place. Negative lower counts,
negative multipliers, a nonpositive denominator, boolean numerical aliases
or repeatedly treating an already lower-count dual as a new baseline lie
outside the declared construction; the new producer rejects them as specified.

The target application uses only the independently accepted image lower
counts B3>=924,B4>=8316,B5>=24948,B6>=391776, together with the support55 theorem.
It must preserve their exact applicability and a new independent artifact
check of every resulting rational certificate. It does not force a nonzero
left code or exclude the target. This is an explicit rescaling of the
previously declared lower-count Delsarte inequality, not a claim of literature
novelty or a new general coding theorem unsupported by the premises.
