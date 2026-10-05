# Target ternary left code: ordinary dot form and nonconstant weights42..78

State CANDIDATE, exact written derivation by `/root/structural`, 2026-10-04.
Zero mathematical executions, enumerations, imported programs, formal checks
or external checks. Root challenged an earlier outline; agreement is not
independent approval. Historical papers and the frozen four-claim roster stay
unchanged. A different author must review this exact version.

## Exact claim

Let A be the adjacency of a complete simple SRG(99,14,1,2), and N its integer
99-by-231 incidence of all actual triangles, each once. Write

    H=NN^T=A+7I, G=H mod3, V=ker G, L=ker(N^T mod3).

For arbitrary integer lifts X,Y of x,y in V, the divided form

    beta(x,y)=X^T H Y/3 mod3

equals the ordinary coordinate dot product x dot y. Consequently L is
ordinary ternary self-orthogonal. Its constant vectors have weights0 or99.
Every nonconstant x in L uses all three vertex colors, each color class has
size divisible by3 in [21,57], and

    wt(x) in {42,45,48,51,54,57,60,63,66,69,72,75,78}.

These are conditional necessary constraints, not existence of a nonconstant
left dependency. L=span(j) remains allowed. This gives no rank improvement,
right-circuit weight bound, fixed17 implication, target construction or target
exclusion. In particular it does not assert that any proposed ternary code or
color-count data are realized by a graph.

## The divided form is ordinary dot on the target kernel

Over the integers A^2=12I-A+2J and Aj=14j. Therefore

    H^2=13H-30I+2J.                                      (1)

Reducing gives G^2-G=2J. If x in V, then Jx=0, so every integer lift X has
sum(X) divisible by3. Also HX is divisible coordinatewise by3. Thus for
x,y in V,

    X^T H^2 Y=(HX)^T(HY) is divisible by9,
    2 sum(X)sum(Y) is divisible by9.

Put b=X^T H Y/3, an integer. Substituting (1) modulo9 yields

    39b-30 X^T Y=0 mod9,
    3(b-X^T Y)=0 mod9,
    beta(x,y)=x dot y mod3.                              (2)

The divided form is lift-independent: replacing X by X+3u changes it by
u^T H Y, zero modulo3 since y in V; likewise for Y. Equation (2) also
identifies its value with the lift-independent ordinary residue dot product.
No Smith form, congruence elimination, numerical rank or determinant bound is
needed for this identity.

For x,y in L, choose lifts with N^T X=3z and N^T Y=3w. Then

    X^T H Y=(N^T X)^T(N^T Y)=9 z^T w,

so beta vanishes on L times L. By (2), x dot y=0 for every such pair.
The constant vector j belongs to L since N^T j=3 1_231. These statements
identify the previously accepted divided-form isotropy in ordinary vertex
coordinates. They are not two independent bilinear restrictions, and are not
advertised as a stronger dimension bound than the existing rank77 argument.

## Vertex colors and their populations

Color each point by x_v in {0,1,2}, with2 represented by-1. Every actual
triangle has color sum0 and hence is monochromatic or rainbow: its colors
are000,111,222 or012. Every edge belongs to a triangle. If a nonconstant x
used only two colors, all triangles and edges would be monochromatic, which
would disconnect the target. The target is connected, because any nonedge
has two common neighbors. Thus all three classes are nonempty.

Let their populations be n0,n1,n2. Orthogonality to j gives n1-n2=0 mod3,
and self-orthogonality gives n1+n2=0 mod3. Since2 is invertible modulo3,
n1 and n2 are divisible by3, and so is n0=99-n1-n2. This remains valid for
the constant words, whose two empty classes should not be subjected to the
following positive-class argument.

Let m count rainbow triangles. For a vertex v in class i, let r_v be its
number of incident rainbow triangles. The other7-r_v triangles are
monochromatic. Uniqueness of the triangle through each edge makes their
neighbors disjoint, so the vertex has

    14-2r_v neighbors of its own color,
    r_v neighbors of each other color, 0<=r_v<=7.

Each rainbow triangle meets each class once. Therefore sum_(v in class i)
r_v=m, m<=7 min(n_i), and every distinct pair of color classes has exactly m
edges. In particular the internal edge count of class i is7n_i-m.

## The smallest color class has at least21 points

The nonprincipal target adjacency eigenvalues are3 and-4: on j-perp they
are the roots of t^2+t-12=0, derived directly from the integer SRG equation.
For a class C of size c, put z=1_C-(c/99)j. Since z is orthogonal to j,

    z^T A z <=3 z^T z.

Using its internal edge count7c-m gives

    14c-2m-14c^2/99 <=3(c-c^2/99),
    m >= (11/198)c(99-c).                               (3)

Write a=min(n_i) and c=max(n_i). Suppose a<=18. Since the remaining class
has size at least a and c is at least their mean,

    (99-a)/2 <= c <=99-2a.

The concave function f(c)=c(99-c) attains its minimum on this closed
interval at an endpoint. The upper endpoint gives2a(99-2a), and the
lower endpoint is no smaller, because

    4[f((99-a)/2)-2a(99-2a)]
      =3(99-5a)(33-a)>0 for0<a<=18.

Thus (3) and m<=7a imply

    m >=11a(99-2a)/99,   7a >=11a(99-2a)/99,
    a>=18.                                               (4)

The only remaining a<=18 boundary is a=18. Equality in (4) forces m=126.
The endpoint comparison above is strict at the lower endpoint; concavity
then makes c=99-2a=63 the unique possible minimizing value. Consequently
the class sizes are18,18,63. On each18-class the sum of eighteen r_v is126
with every r_v<=7, so each r_v=7. Both18-classes are independent sets and
the bipartite graph between them is7-regular.

Fix a vertex in the first18-class. Its seven neighbors in the second class
each have six other neighbors in the first class. This counts42 two-step
walks to the other seventeen same-class points. Every one of those pairs
is nonadjacent and has exactly two common neighbors in the complete target;
at most34 such walks can pass through the second class. The contradiction
42>34 rules out a=18. Hence a>18; all class sizes are multiples of3, so

    21<=n_i<=99-21-21=57.                                (5)

No equality case of a hypothetical automorphism or equitable partition is
used. The individual r_v are not assumed constant except where their literal
upper bound and total force r_v=7 in the rejected boundary.

Since wt(x)=99-n0, (5) proves the asserted nonconstant weight interval and
divisibility. The translates x,x+j,x-j remain nonconstant and their three
weights sum198; their zero color classes are the three original classes.
This is a further exact coordinate consequence, not three separately chosen
codewords or a graph symmetry assumption.

## Hand falsification boundaries

1. For the constant vectors0,+j,-j the weights are0,99,99 and classes are
   (99,0,0) up to permutation. They satisfy dot orthogonality because99=0
   mod3. The positive-class premise is false; excluding these would be an
   invalid claim that a nonconstant dependency is forced.
2. In rook9, the four-corner vector with values
   [[1,-1,0],[-1,1,0],[0,0,0]] is an exact integer left dependency of its
   six row/column triangle columns, but has dot norm4=1 mod3. Here the
   incidence row degree is2 and H=A+2I satisfies H^2=3H+2J, not (1).
   Thus neither (2) nor the target weight bound transfers to this analogue.
3. Q=J4-I4 is binary with three ones per column. Its ternary left kernel
   contains j4 with dot norm4=1, while its divided Gram value is0. It is
   not lambda-one triangle incidence. Column weight3 alone cannot establish
   the new target assertion.
4. The hypothetical18,18,63/m126 color-count boundary passes the first
   degree/rainbow totals and saturates (3). Its explicit42-versus34
   common-neighbor obstruction shows why those first moments are insufficient.
5. Counts33,33,33 and m132 are not excluded by this paper. In each class,
   eleven values each r=3,4,5 give sum132 and square sum550; the saved old
   color moment formulas also give550. This is hand scalar feasibility,
   not a code or graph construction, and prevents treating (5) as a
   nonexistence or constant-only-kernel proof.
6. A proposed vector outside ker(H mod3), or a partial incidence with no
   complete SRG identity, cannot be tested by substituting it into (2).
   No fixed17 left dependency is implicitly extended to the full99 rows.

## Bounded overlap and use

The October4 divided-Gram/rank77 paper already proves beta-isotropy of L;
the new identity (2) expresses that same form in ordinary coordinates. Its
rook boundary rejected a generic ordinary-dot shortcut, which remains
correct: the complete target identity (1) is essential here. The earlier
October3 binary self-orthogonality paper is over F2 and is not a ternary
premise. No binary rank87 or ternary rank77 improvement is asserted.

The October3 nonconstant-kernel design already contains all triangle-color
counts and exact color second moments, including integrality restrictions.
Those old identities can also force color population divisibility by3;
they are explicitly overlap. The direct form identity and the hand18-class
exclusion are retained here without a new finite color-count enumeration.
The archived Wave171 self-orthogonal code is on231 block coordinates, not
this99-coordinate point code. Wave191's more detailed left-code form uses
the separate prism-free endpoint and is not an unrestricted premise;
Wave174's color argument likewise comes from a special weight-three-dual
configuration. Their conditional assertions stay unchanged.

Bounded text searches and the listed comparison sections found no recorded
unrestricted statement of this exact point-code form identity and42..78
nonconstant weight interval. This is not an exhaustive literature or archive
novelty check. All cited artifacts are comparison/provenance, not transferred
approvals or logical assumptions beyond the explicitly derived target facts.

A useful later exact code screen could incorporate the fixed words0,+j,-j,
the thirteen nonconstant weights, dot orthogonality and the three-translate
weight identity. No enumerator, feasibility optimizer or improved dimension
claim is supplied or authorized. The existing possibility L=span(j) survives;
any code result excluding only nonconstant L would not resolve Conway99.
