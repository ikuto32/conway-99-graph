# Independent written derivation of the analytic quinary dual

Native independently reviews Structural's exact frozen paper609c0164 and
candidate packet. Root proposed the truncated multiplication discovery;
Structural supplied the s=122,t=10 recurrence. This is shared discovery context.
I do not treat their agreement or the earlier numerical outcomes as a proof.
This audit uses character products and integer inequalities on paper. No
coefficient-generation program, imported producer, LP, code enumeration or
target certificate check is executed. Actual coefficient and value arrays,
the resulting bound and adjacent powers remain separately unverified here.

## Normalization reconstructed from additive characters

Fix a primitive fifth root and the standard dot-product additive characters
chi_u(x) on F5^n. Summing chi_u(x) over vectors u of weight j gives
K_j(wt(x)): a zero coordinate of x contributes four nonzero choices, while a
nonzero coordinate contributes the sum -1. Thus

    sum_j K_j(i) z^j = (1+4z)^(n-i) (1-z)^i.

For a linear code C, sum_(x in C) chi_u(x) is |C| if u lies in its ordinary
dual, and zero otherwise. If A_i and B_j count the code and dual weights,
then sum_i A_i K_j(i)=|C|B_j. There is no shell-size factor on B_j. K_0=1,
A_0=B_0=1 and the zero code is permitted. These conventions agree with the
independent generating-function fold in Native0333, without using Structural's
signed binomial-sum implementation.

For a fixed vector w of weight h, the number of pairs (u,v), of weights a,b,
with u+v=w is a coefficient in

    (1+4XY)^(n-h) (X+Y+3XY)^h.

At a coordinate where w=0 there is either u=v=0, or four nonzero opposite
pairs. At a nonzero w-coordinate, there is one u=w,v=0 option, one u=0,v=w
option and three options with both nonzero. This count depends on h, not on
the particular nonzero entries of w. Expanding character products and grouping
by w therefore proves K_a K_b=sum_h q_(a,b)^h K_h with these nonnegative
integer coefficients. No orthogonal-polynomial positivity theorem is assumed.
Every contributing pair has h<=a+b; at h=0 the coefficient vanishes unless
a=b, and then equals 4^a binomial(n,a).

For a=1, separate the three ways to change a coordinate in a weight-j vector.
The identity is

    K_1 K_j = (j+1)K_(j+1) + 3j K_j + 4(n-j+1)K_(j-1).

For n=99 the last coefficient is 4(100-j). When collecting coefficient K_k
in K_1 sum_j p_j K_j, the preceding coefficient is k p_(k-1), the central
coefficient 3k p_k and the following coefficient 4(99-k)p_(k+1). This shifted
index is crucial; using 4(100-k) in the recurrence would be wrong.

## Exact positivity of the truncated recurrence

Let p_-1=0,p_0=1, and choose p_(k+1) for k0..9 to annihilate K_k in
g=(K_1-122)p. The recurrence in the candidate follows immediately:

    p_(k+1)=((122-3k)p_k-k p_(k-1))/(4(99-k)).

Write r_k=p_(k+1)/p_k. r_0=61/198 lies strictly between308/1000 and309/1000:
the two cross-product margins are16 and182. For k>0 the ratio map
((122-3k)-k/r)/(4(99-k)) is increasing on positive r. To verify the entire
table without floating point, denote the previous lower/upper numerators by
L,U and the proposed new lower/upper numerators by l,u, with denominator1000.
The two required positive integer margins are

    1000*((122-3k)*L-1000k)-4*(99-k)*L*l,
    4*(99-k)*U*u-1000*((122-3k)*U-1000k).

I hand-evaluated them as follows. Each row is strictly positive on both sides.

|k|previous L,U|new l,u|lower margin|upper margin|
|---|---|---|---:|---:|
|1|308,309|295,296|34880|82888|
|2|295,296|281,282|56740|51136|
|3|281,282|266,267|50536|46896|
|4|266,267|249,251|91080|96460|
|5|249,251|230,232|109480|38232|
|6|230,232|209,211|37960|82144|
|7|209,211|183,185|34104|53880|
|8|183,185|148,151|75424|38340|
|9|148,151|94,99|51680|36640|

Induction therefore proves every p_j>0. For g the coefficients0..9 vanish
exactly. The only remaining coefficients are
g_10=10p_9-92p_10 and g_11=11p_10. Since r_9<99/1000,
g_10/p_10>10000/99-92=892/99>0. Both are positive, not merely nonnegative.

## Product, constant, degree and the 45 signs

For f=g*p the structure constants just derived make every Krawtchouk basis
coefficient nonnegative. Only a=b=10 contributes to the constant term, giving
a_0=g_10*p_10*4^10*binomial(99,10)>0. The g_11*p_10 term contributes positively
to K_21; for h=21 its coefficient is binomial(21,11)>0. All other terms have
degree at most21. Thus f has degree exactly21, and F=f/a_0 has constant
coefficient one and all remaining basis coefficients nonnegative. Padding
coefficients22..32 by zero changes neither F nor its positivity.

K_1(i)=396-5i. At i>=55 it is at most121, strictly less than122. Consequently

    F(i)=(K_1(i)-122)*p(i)^2/a_0 <=0

at every one of the45 weights55..99. A root of p is harmless: a zero tail is
allowed. At weight zero K_1(0)-122=274>0, and p(0)>0 because every p_j>0 and
K_j(0)=4^j binomial(99,j)>0. Hence F(0)>0.

Summing F over a linear C with no nonzero weights below55 gives

    |C| <= |C|*(1+sum_(j>=1)y_j B_j)
         = sum_i A_i F(i) <= F(0).

This proves the conditional bound. It does not force C nonzero or a target
left code of positive dimension. For C={0}, the inequality requires F(0)>=1;
the character identity supplies that too. With M=5^k, the largest integer
k with5^k<=F(0) is the resulting dimension upper bound, without a logarithmic
rounding step. No actual rational F(0), dimension, optimum or improvement over
27 is claimed by this symbolic audit.

## Written counterchecks and implementation boundary

For n=2, K_1^2=8K_0+3K_1+2K_2. The three K_1 values8,3,-2 square to64,9,4,
confirming both shell normalization and the product coefficients. The full-space
n=2 dual y1=y2=1 is25 at weight0 and zero at weights1,2. Its dimension bound2
is sharp. Changing constant8 to9 breaks the product identity, while changing
a multiplier to-1 defeats the nonnegative-coefficient hypothesis. These are
written checks of mathematical boundaries, not claims that a control worker
ran during this audit.

The analytic source's exact combinatorial term formula agrees with the
coordinate count: d opposite nonzero pairs are chosen among n-h zero positions;
c both-nonzero positions and u single-u positions are chosen among h nonzero
positions; the last v positions are single-v. Its factor
binomial(h,c) binomial(h-c,u)3^c binomial(n-h,d)4^d is therefore correct when
c,u,v>=0 and u+v+c=h. I do not use that producer algorithm to check an actual
certificate. The shared Native certificate() instead uses fresh coordinate
folds for every required K_j(i), exact canonical Fractions and exact powers.

A new source/runtime applicability adapter is still required for the analytic
caller; the old numerical ac47 runtime is not its execution contract. The
Native own68 finite qualification approves the unchanged generic arithmetic
path only within its recorded scope. It does not authenticate an analytic
summary, original source, output population, runtime or coefficient trace.
Those require the new wrapper's positive/corrupt controls and genuine actual
packet. Actual all45 tails and bound/powers checking remain pending.

For target application the independently accepted minimum-support55 theorem
is a declared additional premise, not proved by this polynomial. The analytic
producer honestly records that it does not authenticate that premise inside
its own worker. Earlier numerical status2 runs remain UNKNOWN. No graph,
nonconstant codeword, rank improvement, global exclusion or scientific parser
guarantee follows from this written derivation alone.
