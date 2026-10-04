# Candidate: prime-five triangle left code has minimum nonzero support54

This is a written, source-only candidate requiring different-author review.
No mathematical program, enumeration, imported module or backend has run.
It does not assert that the code has a nonzero word or resolve Conway99.

## Exact statement and hypotheses

For every finite simple SRG(99,14,1,2), let A be its integer adjacency matrix
and let N be the99x231 binary incidence matrix containing every actual triangle
exactly once. Let L5=ker(N^T mod5) in F5^99. Every nonzero x in L5 has
Hamming weight at least54. The code may be zero. No automorphism, equitable
color profile, induced scaffold, extra ternary dependency or rank improvement
is asserted.

The proof uses exactly

    A^2=12I-A+2J,  Aj=14j,  NN^T=H=A+7I,
    Nj_231=7j_99,  N^Tj_99=3j_231,

with A symmetric binary and zero-diagonal, each edge in its unique actual
triangle, and every point on seven actual triangles. These follow from the
complete target parameters. The ordinary adjacency eigenvalues are14 on j
and3,-4 on j-perp, with multiplicities54,44; H has eigenvalues21,10,3.
The hypotheses do not assume a target exists.

## Centered lifts and the scalar-pair identity

Represent field elements by0,1,2,-2,-1. For x choose its centered ordinary
integer lift X and let S be its support, s=|S|>0. Write p=#|X_v|1 and
q=#|X_v|2, so p+q=s and ||X||^2=p+4q.

Each actual triangle has sum divisible by5. Since its three centered entries
are in[-2,2], its integer sum is0,5 or-5. Let t count triangles with
nonzero sum. The exact Gram identity and its least eigenvalue give

    25t=||N^T X||^2=X^T H X >=3(p+4q).             (1)

Let X2 be the centered lift of2x. Multiplication by2 is multiplication of
the same word in the field, not a permutation or automorphism of the graph:

    1 ->2,  2 ->-1,  -1 ->-2,  -2 ->1.

Thus its squared norm is4p+q. The only possible fully nonzero triangle
multisets with field sum zero are, up to sign and ordering,

    (1,2,2) with integer sum5;
    (1,1,-2) with integer sum0.

Multiplication by2 exchanges these two types. Triangles with exactly two
supported points have opposite values and remain integer-sum-zero; a triangle
with exactly one supported point cannot occur. If m3 is the number of actual
triangles wholly contained in S, the winding count t2 of X2 therefore satisfies

    t+t2=m3.

Applying(1) to X2 and adding yields the exact necessary inequality

    25m3 >=3[(p+4q)+(4p+q)]=15s,
    m3 >=3s/5.                                      (2)

No pointwise color-neighbor counts are assumed constant. No all-word or all-
graph enumeration is concealed in this two-scalar argument.

## The support upper bound forces s>=53

Let m2 count triangles meeting S in exactly two points and let e be the
number of induced edges on S. There are no one-point intersections. Counting
incidences and using unique edge triangles gives

    7s=2m2+3m3,   e=m2+3m3,
    2e=7s+3m3.                                      (3)

For the centered support indicator z=chi_S-(s/99)j, the upper nonprincipal
adjacency eigenvalue3 gives z^T A z<=3||z||^2. Expanding this inequality gives

    2e <=3s+s^2/9.

This also holds at s=99, where z=0. Combining it with(3),

    27m3 <=s(s-36).                                 (4)

Since s>0, inequalities(2),(4) imply

    81/5 <=s-36,   s>=ceil(261/5)=53.                (5)

Every integer support size1..52 is covered by this symbolic inequality.
The zero word is outside the division by s, and no nonzero word is forced.

## Exact integer residue excludes s=53

Suppose s=53. From(2), m3>=ceil(159/5)=32. From(4),
m3<=floor(901/27)=33. Equation(3) shows m3 has the parity of s, so m3=33
and2e=7*53+3*33=470.

Define the ordinary integer upper projector

    Q=27I-9A+J.

Exact target multiplication gives Qj=0 and Q^2=63Q. For chi=chi_S,

    chi^T Q chi=27*53-9*470+53^2=10.

Let Y=Qchi. It is an integer99-vector with

    sum(Y)=0,
    Y_v=27chi_v-9(Achi)_v+53 ==-1 mod9,
    ||Y||^2=chi^T Q^2 chi=63*10=630.

Write Y=9a-j with a an ordinary integer99-vector. Its zero sum gives
sum(a)=11. Its squared norm gives

    630=81sum(a_v^2)-18*11+99,
    sum(a_v^2)=9.

This is impossible: for every ordinary integer a_v, a_v(a_v-1)>=0, hence
sum(a_v^2)>=sum(a_v)=11. Thus s=53 cannot occur, proving s>=54.
This final integrality step is not a floating eigenvalue estimate, a field
norm argument, a nonnegative-coordinate assumption or an equitable partition.

## Related consequences and explicit boundaries

The left code is also ordinary self-orthogonal overF5. For x,y in L5 and
integer lifts X,Y, N^T X,N^T Y are5-divisible, as are HX,HY. Moreover
7sum(X)=j_231^T N^T X is5-divisible, so sum(X) and sum(Y) are5-divisible.
In the exact identity

    H^2-13H+30I-2J=0,

the H^2,H and J bilinear terms on X,Y are25-divisible. Therefore
30 X^T Y is25-divisible, forcing X dot Y=0 mod5. This observation is not
needed in the stronger two-scalar support proof. A nonzero constant is not
in L5 because N^T(cj)=3c j_231.

The elementary determinant bound rank_F5(N)>=72 remains compatible and is
not improved here. A code of dimension0, including rank_F5(N)=99, satisfies
the theorem. The current ternary left-kernel and binary rank bounds are
different characteristic claims and are not strengthened by this proof.

The smaller rook9 incidence is a falsification boundary for transferring the
claim to arbitrary lambda1/mu2 graphs. Its nine points have only six row/
column triangle columns, row incidence degree2 and H=A+2I singular. The
centered integer array with rows(1,-1,0),(-1,1,0),(0,0,0) has every row and
column sum zero, so lies in ker(N^T mod5) and has weight4. No target-specific
Gram eigenvalue3 or degree7 step applies to it.

Replacing actual triangles by an incomplete column selection would invalidate
the seven-point incidence count, the complete Gram matrix, and potentially
the unique-edge count in(3). A bare fixed17 exterior-count witness does not
contain the complete N needed to apply this theorem. The source-only3-adic
rank98 non-obstruction model likewise has neither ordinary binary entries
nor these exact real support inequalities.

## Comparison, origin and remaining work

Root requested a new ordinary-integer incidence attack at primes2,5,7 after
the3-adic relaxed countermodel. Structural first obtained a weaker hand bound43
using one centered lift and small triangle-free graph bounds; that preliminary
message was not frozen or promoted. The two-scalar partition then gave53, and
the exact upper-projector residue excluded53. Native was notified of the
stronger54 statement before this first frozen version. Agreement by any agent
is not an independent review.

Bounded comparison inspected the current research map, the exact target
modular-rank audit, Wave23 prime-rank failed routes, Wave168 full incidence
Gram/energy derivation, the new mod9 and3-adic boundary papers, and targeted
Markdown searches for characteristic-five incidence/support statements. The
Q^2=63Q identity, incidence Gram/spectrum and general support Rayleigh bound
are historical tools. No matching F5 minimum-support54 statement was found
in the named comparison; this is not exhaustive novelty verification.

Independent review must check the complete triangle-type exchange, the two
incidence counts, scalar support inequality and the exact53 integer residue.
No executable controls or scientific run are authorized or proposed by this
paper. Utility is a necessary screen for a proposed complete incidence/code;
whether any nonzero F5 left word exists, or this condition yields an actual
exclusion, remains UNKNOWN. Global target and coverage remain UNKNOWN.
