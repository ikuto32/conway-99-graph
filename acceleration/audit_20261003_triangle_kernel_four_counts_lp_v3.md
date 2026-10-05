# Independent four-image-count kernel dual derivation

Written 2026-10-03 by /root before any new four-count numerical guide or raw
certificate was inspected. Preserve the independently checked old seven-weight
V2 source/proof and the unexecuted four-count V1/V2 preparations. This new theorem
is conditional on a target graph; target existence remains UNKNOWN.

Let B be the complete actual triangle-incidence matrix of a hypothetical
target and C=ker(B transpose) over GF(2). Write A_w for its word counts and
M=|C|, with A_0=1. The independent interval proof65d8ee restricts nonzero
weights to W13={36,38,...,60}. The independently written divisibility proof
0231d687 additionally restricts them to W7={36,40,...,60}. A certificate must
state its chosen domain; the W7 premise is not used in the W13 relaxation.
The zero kernel is allowed in both domains.

The separately checked actual-triangle image-count theorem626e and the new
weight-five universal inverse8844/full raw auditdedb give lower counts
L3=231,L4=2079,L5=12474,L6=24486 and Lj=0 otherwise. L5 counts distinct
binary image words, not paths:24948 unordered paths have fibers of size at
most two. Every statement retains its graph and actual-triangle assumptions.

Binary character orthogonality gives sum_w A_w K_j(w)=M D_j, where D_j is
the image's weight-j word count. Therefore D_j>=Lj implies

    sum_(w in W) A_w (Lj-K_j(w)) <= binom(99,j)-Lj,

including the zero word's K_j(0)=binom(99,j) contribution. Every denominator
is strictly positive. Put G_j(w)=(Lj-K_j(w))/(binom(99,j)-Lj). If a complete
exact vector y in Q^99 is nonnegative and satisfies sum_j yj G_j(w)>=1 for
every w in the explicitly selected W, then

    M-1=sum_w A_w <= sum_j yj sum_w A_w G_j(w) <= sum_j yj.

Thus M<=U=1+sum_j yj. Since M is a power of two, exact U<2^(d+1) gives
dim C<=d and rank B>=99-d. No optimum, rank upper bound, forced nonzero
kernel, graph construction, general exclusion or contradiction follows.

The separate checker derives every coefficient by multiplying the integer
polynomial (1-z)^w(1+z)^(99-w), rather than calling the producer's binomial
sum or optimizer. It uses Fractions for all dual inequalities and compares
powers of two exactly. It checks all1287 cells/13 inequalities for W13 or
all693 cells/seven inequalities for W7, all99 coordinates and the explicit
domain field. An incomplete model or domain substitution cannot pass.

Known rook9 has16 kernel words and32 image words with actual image counts
(6,9,9,6) at degrees3,4,5,6. The complete synthetic rook dual has U=512/31;
both weight4 and6 inequalities equal one. Its weight6 does not calibrate
target divisibility. Independent literal characters check the sharp zero
constant and the new fifth-degree coefficients1/39 and5/39.

For both target-sized domain fixtures, use the synthetic vector
yj=(binom(99,j)-Lj)/39271. For every nonzero weight, sum_(j>=1)K_j(w)=-1,
by evaluating its generating polynomial at z=1. Since sum Lj=39270, all
row inequalities equal one and U=2^99/39271. This synthetic bound is only a
control, not a useful target estimate. Fresh calibration challenges complete
models in both domains and precise corruptions before any guide output.

Producer:/root/structural. Independent derivation/checker:/root. Shared trusted
components include the earlier ROOT polynomial/rational algorithm, exact
premise proofs, Python integer/Fraction arithmetic, JSON and SHA256, Git and
the pinned uv/deadline environment. Finite controls do not establish the
universal graph premises. External review:null because none is recorded;
novelty:null because no novelty audit was performed. Artifacts are LOCAL_ONLY
pending separate publication; source commit denotes context, while actual
new working source/protocol bytes are separately hashed.
