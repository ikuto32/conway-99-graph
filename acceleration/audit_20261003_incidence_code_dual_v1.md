# Independent derivation of the binary-code dual certificate interpretation

Verifier `/root/structural`; producer `/root`. Assume only a binary linear
code C of length n whose nonzero weights belong to a declared set W. There
is no lower bound on its dimension. Let A_w count codewords of weight w,
so A_0=1 and sum A_w=M=|C|.

For a fixed binary word x of weight w, let K_j(w) be the sum of the signs
`(-1)^(u dot x)` over all words u of weight j. The generating polynomial is
`(1+z)^(n-w)(1-z)^w`. Its derivative satisfies
`(1-z^2)F'=(n-2w-nz)F`. Equating coefficients of z^j gives
`(n-2w)K_j=(j+1)K_(j+1)+(n-j+1)K_(j-1)`, starting with
K_0=1 and K_1=n-2w. The independent checker uses this integer recurrence and
requires exact divisibility. K_j(0)>0 counts words of weight j.

For fixed u, the sum of its character over C equals M if u belongs to C's
orthogonal code. Otherwise take an x0 in C with u dot x0=1; the bijection
x -> x+x0 pairs equal and opposite signs, so the character sum is zero.
Interchanging these finite sums yields
`sum_w A_w K_j(w)=M times the number of orthogonal words of weight j >=0`.
Therefore, for j>=1 and G_wj=-K_j(w)/K_j(0),
`sum_(w in W) A_w G_wj <=1`.

If an exact rational vector y_j is nonnegative and every weight satisfies
`sum_j y_j G_wj >=1`, multiply the last inequalities by y_j and sum. Since
A_w>=0, this proves
`M-1=sum_(w in W)A_w <=sum_j y_j`, hence M<=1+sum_j y_j.
This is valid for any feasible dual; no numerical optimum is required.
For a binary linear code M=2^t. Exact rational comparisons with powers of two
give the dimension bound; floating logs are unnecessary.

For a hypothetical Conway target, use only the separately independently
derived premise that every nonzero triangle-incidence kernel word has even
weight between36 and60 (ROOT's written Griesmer audit65d8ee... and report
f6d370...). With n=99, the dimension upper bound t then implies triangle
incidence rank>=99-t by rank-nullity. This supplies no upper rank, target
construction or contradiction. The zero kernel is covered: M=1.

The checker calibrates the recurrence by direct sign enumeration and tests
character positivity for complete small codes, including all16 words of the
rook9 triangle kernel. Those are finite falsification controls, not a substitute
for the character derivation above. Shared premises are disclosed, but no
producer arithmetic or optimizer is imported. Novelty and external review
remain UNKNOWN.
