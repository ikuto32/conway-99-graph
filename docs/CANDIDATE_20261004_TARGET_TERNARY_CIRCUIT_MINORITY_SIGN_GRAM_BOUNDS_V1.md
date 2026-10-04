# Minority-sign Gram bounds for actual triangle circuits

Status: **CANDIDATE**, written 2026-10-03T23:47:12+00:00 by
`/root/structural`. This is a new discovery proposal for different-author
verification, not an independent report or self-approval. It applies to an
arbitrary actual-triangle circuit of a hypothetical full Conway99 target.
No vertex symmetry, induced selected geometry, or forced small circuit is
assumed. No mathematical program, enumeration, formal proof checker, or
external review was used. No ledger, index, historical source, or graph is
changed. Preparation context is HEAD
`28742325c2c4d11aec5d7c243ed560f3298368f3`, ledger SHA256
`b7d07a8be5cbbce8c2125e631d58f4035ed56a66c2b1e79db27cb56500859f8a`,
index SHA256
`e411963d8a7ae05b3f1076f0b5dd14a628016d4a317872fc52865ec2cde7734a`.

## Exact proposed statement

Let A be a simple degree-14 graph on 99 vertices with adjacent CN=1 and
nonadjacent CN=2. Select w distinct actual triangles whose incidence columns
form a circuit over GF(3). Write its nonzero dependence coefficients as +1
and -1. After a global sign reversal if needed, let q be the smaller sign
population, so 0<=q<=w/2. Suppose the coefficient sum is nonzero over GF(3).
Let S be the n used points, H=A[S,S], and e the number of edges of H beyond
the selected triangle edge union. Then

```
w <= n <= w+q,
F = n^2+27n-54w-18e >= 0,
sum_(v in S) (n+27-9*deg_H(v))^2 <= 63F.
```

Consequently an unbalanced circuit with q=0,1,2,3 has, respectively,

```
w >= 28, 25, 23, 19.
```

If q=1 and w=25, then n=26 and e=0. Its three minority-triangle points
have selected degree two, the other 23 points have selected degree three,
and H is exactly the selected edge union. Every external point's number k
of neighbors in S obeys the necessary total moments

```
sum k = 214,       sum k^2 = 638,       external population = 73.
```

This does not assert that a target has a circuit with q<=3, or that any
remaining sign pattern or support can be completed. In particular, the
existence of an unbalanced circuit does not force it to be one-sign.

## 1. The historical universal Gram premise

The sole uses-result dependency proposed here is
`C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS` revision 1. Its independently checked
report is
`acceleration/results/20260930_independent_review/target_gram_support_lemma.json`,
SHA256
`e194ca054dfe0596ae2b9ff1070ef59289c7c0401497a63c77eb62e217bd1ac6`.
The written derivation
`docs/DERIVATION_20260930_TARGET_GRAM_NOGOODS.md`, SHA256
`a450e71f0d566c218123b831a6ad07b3b2bd17e8c78edaab2cb380d306693153`,
was read in full for this proposal. Its verifier was
`/root/eight_domain_audit independent checking agent`, not the present author.

For completeness, the needed identity is also reconstructed here. The target
identity is A^2=12I-A+2J, with AJ=JA=14J and J^2=99J. Thus

```
G = 27I-9A+J,       G^2 = 63G.
```

Symmetry gives x^T G x=||Gx||^2/63>=0 for every real x. This is exactly
the historical target Gram consequence; neither PSD nor the projector
identity is claimed as new. The use of its support mass with circuit sign
counts is the present proposed deduction.

## 2. Field rank gives a point lower bound

Let C be the incidence matrix on the used n points and selected w actual
triangles, over GF(3). Circuit minimality means rank(C)=w-1. Every column
has three ones, hence 1_n^T C=0. Because S is nonempty, 1_n is a nonzero
left-kernel vector, so rank(C)<=n-1. Therefore w<=n.

This step applies to a circuit, not to an arbitrary larger dependent word.
No claimed real rank, binary rank, incidence rank<=72, or numerical modular
spectrum is used. The separate minimum-unbalanced-support argument shows
why a minimum unbalanced word is a circuit, but existence and that argument
are not assumptions needed for this conditional statement.

## 3. Minority incidences give a point upper bound

For v in S, let d_v be its selected triangle degree and m_v its number of
minority-sign selected triangles. A nonzero word in the incidence kernel
cannot have d_v=1. If d_v=2, its two coefficients are opposite, so m_v=1.
If d_v>=3, then d_v+m_v>=3 automatically. Thus at every used point,

```
3 <= d_v+m_v.
```

Summing and using three points per selected triangle yields

```
3n <= sum d_v + sum m_v = 3w+3q,
```

so n<=w+q. Equality is particularly restrictive: each used point must have
either (d_v,m_v)=(2,1) or (3,0). There are then exactly 3q degree-two points
and n-3q majority-only degree-three points. In particular, the minority
triangles are pairwise point-disjoint. When q=0, the two rank bounds force
n=w and every used point has selected degree exactly three; degree-six
points in a one-sign word are incompatible with circuit minimality.

## 4. Actual extra edges are retained exactly

Adjacent CN=1 makes every graph edge belong to a unique actual triangle.
Distinct selected actual triangles have disjoint edge sets. They therefore
provide 3w distinct edges of H. Write the remaining e edges as extra actual
edges; e is a nonnegative integer, and |E(H)|=3w+e.

Apply G to the full99-vector x=1_S. Its quadratic is

```
x^T G x = 27n-18|E(H)|+n^2 = F.
```

For a used point v, its image coordinate is

```
(Gx)_v = n+27-9*deg_H(v).
```

The full identity ||Gx||^2=63F proves both F>=0 and the stated inside-square
budget. Discarding outside squares weakens a necessary condition; it does
not assume that they vanish. If a_v counts extra-edge incidences at v,
deg_H(v)=2d_v+a_v and sum a_v=2e. No inducedness assumption was inserted.

Since n^2+27n is strictly increasing for nonnegative n and n<=w+q, the
coarser general necessary sign-imbalance inequality is

```
(w+q)^2+27(w+q)-54w >= 0.
```

Equivalently this is w^2+(2q-27)w+q^2+27q>=0. Its satisfaction is not
sufficient for local geometry, Gram positivity, or a target extension.

## 5. Complete handwritten q=0,1,2,3 exclusions

Unbalancedness means w-2q is not divisible by three. The coarse polynomial
immediately excludes these integer intervals:

| q | Necessary w>=2q | Strictly negative polynomial interval |
| --- | --- | --- |
| 0 | w>=1 | 1 through 26 |
| 1 | w>=2 | 2 through 23 |
| 2 | w>=4 | 4 through 20 |
| 3 | w>=6 | 7 through 14 |

For q=3, w=6 is balanced. The endpoint values of the polynomial on the
nonzero-q intervals are respectively (-18,-18), (-18,-2), and (-8,-8).
Convexity bounds every intervening value above by the larger endpoint value,
which is still negative. For q=0 the factorization w(w-27) is negative on
its listed interval. No finite enumeration is hidden in this argument.

The remaining boundary cases have the following values before extra edges:

| (q,w) | Forced n=w+q | F at e=0 | F at n-1,e=0 | Inside squared norm at e=0 | 63F at e=0 |
| --- | --- | --- | --- | --- | --- |
| (1,24) | 25 | 4 | -72 | 3*16^2+22*(-2)^2=856 | 252 |
| (2,21) | 23 | 16 | -56 | 6*14^2+17*(-4)^2=1448 | 1008 |
| (3,16) | 19 | 10 | -54 | 9*10^2+10*(-8)^2=1540 | 630 |
| (3,17) | 20 | 22 | -44 | 9*11^2+11*(-7)^2=1628 | 1386 |

The negative n-1 entries, monotonicity, and n<=w+q force the displayed n.
The equality characterization in section 3 fixes every selected degree.
In the first three rows F>=0 permits e=0 only, and each inside norm exceeds
63F. Thus those cases are impossible even before adding outside squares.

In the fourth row e is either zero or one. Zero is already impossible. A
single extra edge changes two inside coordinates by -9. The degree-two
coordinates 11 have square change 2^2-11^2=-117; the degree-three coordinates
-7 have square change (-16)^2-(-7)^2=207. Even allowing an extra edge between
two degree-two points, the new inside norm is at least 1628-234=1394, whereas
63F=63*(22-18)=252. This relaxed endpoint bound excludes every possible
single extra edge without assuming which pairs are actually permissible.

Finally (q,w)=(0,27),(2,22),(3,15),(3,18) are balanced and cannot occur in
the quantified unbalanced case. These exclusions prove precisely the four
stated lower bounds. They do not exclude the next listed weights or imply
sharpness.

## 6. The first q=1 boundary retains a concrete family

If q=1,w=25, monotonicity forces n=26: at n=25,e=0 the quadratic is -50.
At n=26,e=0 it is 28, so e can only be zero or one. Equality n=w+q gives
three degree-two points on the sole minority triangle and 23 degree-three
points elsewhere. At e=0 the inside image norm is

```
3*17^2+23*(-1)^2=890.
```

An extra edge cannot join two degree-two points: all three already form the
actual minority triangle. On a degree-two point its square change is
8^2-17^2=-225; on a degree-three point it is (-10)^2-(-1)^2=99. Hence a
minority/majority endpoint pair leaves norm 764, and a majority/majority
pair leaves norm 1088. Both exceed 63*(28-18)=630. Thus e=1 is impossible,
and H must be exactly the selected triangle edge union.

The cut to the 73 external points has 14*26-6*25=214 edges. The total target
CN sum on unordered pairs in S is 26*25-3*25=575. The inside contribution
is 3*choose(4,2)+23*choose(6,2)=363. Thus external points contribute
sum choose(k,2)=212, and sum k^2=2*212+214=638.

These scalar moments are consistent as an abstract histogram: eight points
with k=2, 62 with k=3, and three with k=4 have total population73, sum214,
and squared sum638. This is a written arithmetic negative control against
claiming that the two moments alone refute the boundary family. It does not
construct exterior types, incidence geometry, or a target.

## 7. Falsification boundaries and the next meaningful attack

The following limitations were checked explicitly on paper:

1. The n>=w rank step fails for a general nonminimal dependent word; the
   statement therefore retains circuit minimality.
2. A one-sign word can have degree-six points; only circuit rank plus the
   column-sum relation removes them here.
3. A degree-two point needs one coefficient of each sign, which is why the
   minority-incidence inequality is legitimate.
4. Switching the global coefficient sign changes neither q nor the bounds.
5. A coefficient sum is computed as w-2q in GF(3), not as w or the point sum.
6. Actual extra edges contribute -18e to F and -9 per endpoint to Gx; they
   were not silently omitted or treated as always monotone in the norm.
7. The (3,17) endpoint minimization allows even forbidden endpoints, making
   its lower bound weaker and still sufficient.
8. The (1,25) single-edge check uses the actual minority triangle to forbid
   the only endpoint class that could reduce the norm enough.
9. Inside image norm alone is bounded above by the full projector norm;
   equating the two would be an unjustified outside-zero assumption.
10. The q=1,w=25 histogram survives the aggregate exterior moments.
11. None of q<=3, w=25, one-signness, or this histogram is forced to occur
    in an arbitrary target. The bound does not bridge the full12..98 range.
12. No automorphism, fixed17 class, LP feasibility, or inherited local
    incidence countermodel is used as a target premise.

The proposed next structural task is to apply this same circuit sign-mass
and exact projector-image budget to arbitrary minority q and actual selected
degree distributions, with complete extra-edge corrections. For the smallest
q=1 survivor, any further exclusion must address the 24-positive/one-negative
triangle geometry on26 points and exact exterior types, not merely its two
already feasible degree moments. No computational family enumeration is
authorized or proposed as having run.

## Archive and role disclosure

The universal Gram matrix, its positivity, and its full norm identity are
historical and independently verified as pinned above. Earlier archive
spectral equality arguments already restrict6-regular induced supports;
there is no claim to novelty for that method. Bounded literal searches for
minority-sign circuit wording and these formulas found no exact duplicate,
which is not a novelty guarantee.

The already written affine/circuit and upper98 notes were read for context.
Their author is the present author, and their different-author verifications
do not self-approve this new deduction. Their existence/upper-bound statements
are not used as premises of this conditional circuit filter. The rejected
binary-rank<=72 implication and the preserved non-target incidence/cap
countermodels remain untouched. A hypothetical target is still UNKNOWN.
