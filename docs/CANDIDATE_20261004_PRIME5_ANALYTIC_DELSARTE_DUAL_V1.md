# Candidate exact analytic q5 Delsarte dual

Root proposed the positive truncated Krawtchouk multiplication route.
Structural supplies the explicit rational s=122, t=10 construction below.
This is source-only: the coefficient arithmetic has not been executed, and
an independently implemented exact certificate check remains required.

Use q=5, n=99 and K_j(i)=[z^j](1+4z)^(99-i)(1-z)^i.
K_1(i)=396-5i, so K_1(i)<=121 for every i=55,...,99.
The exact multiplication identity is
K_1 K_j=(j+1)K_(j+1)+3j K_j+4(100-j)K_(j-1).

Set p_-1=0,p_0=1 and for k=0,...,9 set
p_(k+1)=((122-3k)p_k-k p_(k-1))/(4(99-k)).
Let p=sum_(j=0)^10 p_j K_j and g=(K_1-122)p.
The coefficients of K_0,...,K_9 in g vanish by construction.
Its remaining coefficients are g_10=10p_9-92p_10 and g_11=11p_10.

Here is a hand interval proof that all p_j and both remaining g coefficients
are positive. Put r_k=p_(k+1)/p_k. First r_0=61/198, and
r_k=(122-3k-k/r_(k-1))/(4(99-k)). This map is increasing in its positive
previous ratio. The following strict rational enclosures propagate directly:

|k|lower r_k|upper r_k|
|---|---:|---:|
|0|308/1000|309/1000|
|1|295/1000|296/1000|
|2|281/1000|282/1000|
|3|266/1000|267/1000|
|4|249/1000|251/1000|
|5|230/1000|232/1000|
|6|209/1000|211/1000|
|7|183/1000|185/1000|
|8|148/1000|151/1000|
|9|94/1000|99/1000|

In particular g_10/p_10=10/r_9-92>10000/99-92=892/99>0.

Krawtchouk products have nonnegative integer structure coefficients.
For a fixed vector w of weight h in F5^99, the number of ordered vectors
u,v of respective weights a,b with u+v=w is
[X^aY^b](1+4XY)^(99-h)(X+Y+3XY)^h.
Character sums therefore give K_a K_b=sum_h q_(a,b)^h K_h with those coefficients.
This derives positivity rather than assuming an orthogonal-polynomial label.

Let f=g p=(K_1-122)p^2=sum a_h K_h. Every a_h is nonnegative,
and the constant coefficient is
a_0=g_10 p_10 4^10 binomial(99,10)>0.
The term g_11 p_10 has positive K_21 coefficient, and no degree exceeds21.
Thus F=f/a_0 has constant Krawtchouk coefficient one and all other
coefficients y_h=a_h/a_0 nonnegative. Pad y_22,...,y_32 by zero.

For all45 weights55,...,99,
F(i)=(K_1(i)-122)p(i)^2/a_0<=0.
A zero of p only gives equality, which is allowed by the dual inequality.
At weight zero F(0)=274p(0)^2/a_0>0.

For a linear q5 code of length99 with minimum nonzero weight at least55,
MacWilliams orthogonality gives sum_i A_i K_h(i)=|C|B_h>=0.
Since A_0=1 and each nonzero support is in the tail, summing F over C
gives |C|<=F(0). No nonzero code, optimum, target graph or automorphism
is assumed. In particular C={0} remains permitted.

The exact size and largest integer k with5^k<=F(0) are deliberately not
reported here: they require the new contained rational calculation and a
different checker. A rough hand magnitude estimate may be weaker than the
existing dimension upper27; no rank improvement or performance claim is made.
The earlier numerical status2 outcomes remain UNKNOWN, since they do not
prove dual infeasibility.

The proposed producer records every p/g/a coefficient, all46 values at
weight0 and55..99, the two neighboring powers5, and the normalized degree32
certificate. Its small controls include the hand identity
K_1^2=8K_0+3K_1+2K_2 at n2, a sharp full-space n2 dual, and deliberately
corrupted coefficient/sign cases. These qualify engineering only. The
new source is not approved by old numerical-producer gates.
