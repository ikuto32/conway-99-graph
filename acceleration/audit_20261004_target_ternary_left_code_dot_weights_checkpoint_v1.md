# Independent written audit: target ternary left-code dot form and weights

Verifier: `/root/checkpoint_audit`. Discovery producer: `/root/structural`.
The exact revision reviewed is
`C-UNRESTRICTED-TARGET-TERNARY-LEFT-CODE-DOT-FORM-WEIGHTS42-78`, revision 1,
in the unchanged paper with SHA256
`653a21966651c9bf47fab5bdbaec4d9299d8faea3e6cc81c6a511ab3338161d8`
and unchanged raw statement with SHA256
`0e256cfc7280e7cc9b1c7ad4c05ee6e453a128028515fd35766c6a41b4915208`.

Outcome: PASS for the exact universal conditional statement. This is an
independent written derivation and hand falsification attempt, with no
mathematical program, enumeration, solver, formal checker, scientific artifact
replay or external review. No ledger, status, source, index or Git change is
performed. Root contributed an earlier dot-form outline and therefore cannot
be the independent mathematical verifier of that discovery. I reconstructed
the algebra, local geometry and boundary counts separately; shared target
hypotheses and reading the candidate are disclosed.

## Integral form identity, including every divisibility condition

Use the complete hypothetical simple target adjacency A and its complete
actual-triangle incidence N. Each edge belongs to its unique triangle, the
neighborhood of a vertex consists of seven disjoint edges, and hence
H=NN^T=A+7I. Expanding the integer target identity gives

    H^2=A^2+14A+49I=61I+13A+2J=13H-30I+2J.

On reduction modulo 3, G^2-G=2J. If Gx=0 then G^2x=0, so 2Jx=0;
2 is a unit in F3 and thus the sum of any integer lift X of x is divisible
by 3. HX is also divisible by 3 coordinatewise. Both facts are needed.

For x,y in ker G and arbitrary integer lifts X,Y, let
b=X^T H Y/3 and d=X^T Y. The numerator defining b is divisible by 3.
The product (HX)^T(HY) and 2 sum(X)sum(Y) are divisible by 9. Substituting
the integral identity therefore gives 39b-30d=0 modulo 9, equivalently
3(b-d)=0 modulo 9. It follows that b=d modulo 3. This is integer
divisibility by 9, not division by a nonunit inside F3.

Replacing X by X+3u changes b by u^T H Y, zero modulo 3; the analogous
change of Y also vanishes. A simultaneous replacement adds the further
term 3u^T H v after the division, also zero modulo 3. Thus the form is
well-defined for every lift and equals the ordinary residue dot product.

If x,y belong to L=ker(N^T mod 3), then N^T X=3z and N^T Y=3w, giving
X^T H Y=9z^T w. Also Hx=NN^T x=0 modulo 3, so L is inside ker G.
The divided form and hence the ordinary dot product vanish on L times L.
The constant vector j belongs to L since each column contains three ones.
Its norm is 99=0 modulo 3. These are coordinate identifications of the same
form, not two independent restrictions or a stronger incidence rank bound.

## Triangle geometry and exact color populations

Over F3, a triple has sum zero precisely when its colors are all equal or
all distinct: the six patterns with exactly two equal entries have a
nonzero sum. Thus every actual triangle is monochromatic or rainbow.
Every edge is in a triangle. If a nonconstant word used only two colors,
all edges would be monochromatic. The complete target is connected:
two nonadjacent vertices have two common neighbors, and adjacent vertices
are already connected. Two nonempty colors would therefore contradict
connectedness. All three classes of a nonconstant word are positive.

Orthogonality to j gives n1-n2=0 modulo 3, while self-orthogonality gives
n1+n2=0 modulo 3. Since 2 is invertible, n1 and n2, and then n0, are
divisible by 3. The argument does not apply the positive-class estimates
to the constant words 0,j,-j.

For a vertex v let r_v count its incident rainbow triangles. The unique
edge-triangle partitions its fourteen neighbors into seven disjoint pairs.
Each monochromatic triangle contributes two same-color neighbors; each
rainbow triangle contributes one in each other class. The degree counts are
14-2r_v,r_v,r_v, with 0<=r_v<=7. If m counts rainbow triangles, each
class has sum r_v=m. A pair of different classes has exactly m edges;
a class of size c has internal edge count 7c-m. These identities require
no uniform individual profile or equitable partition.

## Independent spectral bound and the rejected 18-point boundary

On j-perp, A^2+A-12I=0. Symmetry makes all nonprincipal eigenvalues
real roots 3 or -4, so z^T A z<=3 z^T z for every z perpendicular to j.
For z=1_C-(c/99)j, direct substitution of the internal edge count gives

    14c-2m-14c^2/99 <= 3(c-c^2/99),
    m >= 11c(99-c)/198.

Let a be the smallest class and c the largest. Positivity gives a>0;
the remaining class is at least a, so
(99-a)/2<=c<=99-2a. For 0<a<=18 the lower endpoint of this interval
has strictly larger value of f(c)=c(99-c) than the upper endpoint, since

    4[f((99-a)/2)-2a(99-2a)]
       =9801-792a+15a^2=3(99-5a)(33-a)>0.

Concavity places the minimum at the upper endpoint, giving
m>=11a(99-2a)/99. Together with m<=7a, cancellation of the positive a
gives 693>=1089-22a and a>=18. This excludes every positive a<18;
there is no reversed inequality or unproved integral rounding.

At a=18 both bounds force m=126 and f(c)=f(63). Strict concavity and
the strictly larger lower-endpoint value force the unique allowed c=63.
The remaining class is 18. In either 18-class, eighteen integers r_v<=7
sum to 126, forcing every r_v=7. These two classes are independent, and
the graph between them is 7-regular. The constant profile here is forced
by equality, not assumed for other class sizes.

Choose one vertex in the first 18-class. Its seven neighbors in the second
class each have six other neighbors in the first class, yielding 42 walks
of length two to the other seventeen points of the first class. Each of
those seventeen pairs is nonadjacent in the complete target and has exactly
two common neighbors in the whole graph. Therefore at most 34 such walks
can pass through the second class. The contradiction 42>34 excludes this
last boundary even if additional common neighbors lie in the 63-class.

All color sizes therefore exceed 18 and are divisible by 3; they lie in
[21,57]. The weight 99-n0 lies in {42,45,...,78}. Constants retain
weights 0,99,99. The translates x,x+j,x-j remain nonconstant, permute
which class is zero and have weight sum 198. No graph automorphism is used.

## Deliberate falsification boundaries and bounded comparison

1. The constant line span(j) satisfies every form constraint. Its two empty
   classes invalidate the positive-class premise, so it is not excluded.
2. V must be ker(H mod 3), not an arbitrary vector space or partial support.
   The sum-divisibility and coordinate-divisibility steps fail otherwise.
3. The full integer identity is essential. In rook(9,4,1,2), H=A+2I
   instead satisfies H^2=3H+2J. The four-corner +/-1 vector is an integer
   left dependency with dot norm 4=1 modulo 3. It does not refute the target
   proof and refutes a parameter-free shortcut instead.
4. For Q=J4-I4, Q has column weight 3 and H=QQ^T=I+2J. Then Hj=9j,
   j^T H j/3=12=0 modulo 3, while j dot j=4=1. Column weight 3 alone
   is insufficient; Q is not complete lambda-one target incidence.
5. The counts (18,18,63),m=126 pass the initial rainbow totals and the
   spectral inequality, but fail the two-walk count. Counting those walks
   as 7*7 would incorrectly include return walks; the correct number is
   7*6=42. The upper bound uses 17*2=34 in the whole graph.
6. The scalar counts (33,33,33),m=132 are left possible. Eleven entries
   each of r=3,4,5 give total 132 and square sum 550 per class. Independently
   expanding (A1_C)^T(A1_C) gives 3Z_C+Z_total=2c^2-198c+58m.
   Summing gives Z_total=(sum c_i^2-9801+87m)/3=1650 and Z_C=550.
   This is hand scalar feasibility, not an actual code or graph construction.
7. The old divided-Gram/rank77 paper already supplies beta-isotropy and
   the incidence rank floor 77. Its generic rook warning remains sound;
   the present additional target identity identifies beta in vertex
   coordinates. No stronger rank follows from treating these as separate
   forms. Its wording contrasting beta with an ordinary Euclidean product
   is read as the generic lift/domain warning; this new target-specific
   identification is an explicit additional derivation.
8. The October3 nonconstant-kernel design already gives monochromatic/
   rainbow counts, local r_v profiles and exact color second moments.
   Population congruences are overlapping consequences, not new execution.
9. Wave170 contains the earlier Gram rank 55 and triangle-block profiles;
   it does not state the current point-code dot/weight result. Wave171's
   self-orthogonal code has 231 block coordinates, so it is not this L.
10. Wave191 discusses L inside a 45-space with an additional centered-rank
    11 endpoint. Its bounds and nonzero form expression have that extra
    premise. It is not an unrestricted premise here. No endpoint theorem
    or historical computational status is promoted by this comparison.
11. Wave174 has a special prism-free weight-three block-dual premise and
    derived color sizes (36,3c,63-3c). It supplies no arbitrary left-word
    conclusion. The binary self-orthogonality paper is over F2 and has no
    transferable ternary dot or weight premise.
12. No nonconstant word is forced, no small right circuit follows, and no
    fixed17 code is extended to all 99 points. A later enumerator would
    need a separately checked exact model and cannot exclude the target
    merely by excluding nonconstant L.

The named whole comparisons do not contain the exact unrestricted combined
dot identity and nonconstant interval in the reviewed passages. This is a
bounded comparison only, not exhaustive novelty or external literature review.
The exact identities, color congruences and prior rank floor overlap as stated.
I find no material mathematical veto of the precise revision 1 statement.

Written review boundaries: 29, itemized in the accompanying report. All
candidate/comparison bytes remain unchanged. Recommended VERIFIED/CLEAR is
limited to this written conditional claim, with target resolution NONE;
registration and executable source approval remain separate.
