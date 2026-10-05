# Candidate: exact prime-five triangle-image weight lower counts

This is a source-only written necessary condition and a possible input for a
future exact code-enumerator experiment. No LP, code enumeration or target
calculation was executed. All previous support and signed-design notes remain
unchanged. Different-author written review is required.

## Exact statement

Let T be any finite linear triple system: its distinct3-subsets intersect in
at most one point. Let m=|T|, Q=sum_v binom(t_v,2), and N its binary
point-by-triple incidence. In the code D=im_F5(N), let B_j count distinct
words of Hamming weight j. Then

    B_3 >=4m,
    B_4 >=4Q,
    B_5 >=12Q,
    B_6 >=16*(binom(m,2)-Q).

If its point count n is greater than6 and j_n belongs to D, additionally

    B_(n-3) >=4m,
    B_n >=12m+4.

Each is a lower bound; no exhaustive description of all image words or additive
combination of coincident weight indices is asserted.

For any complete finite simple SRG(99,14,1,2), its actual triangles form such
a linear triple system, m=231 and Q=99*binom(7,2)=2079. Row sums7 give
j_99=3N j_231 overF5. Thus its triangle-image code obeys

|j|3|4|5|6|96|99|
|---|---:|---:|---:|---:|---:|---:|
|Lower count N_j|924|8316|24948|391776|924|2776|

There is no assumed nonzero left code, graph automorphism, equitable profile,
triangle factor, rank improvement or target resolution.

## Single columns and cancelling meeting pairs

The four nonzero scalar multiples of each column are distinct, giving4m
words of weight3. Their nonzero supports recover the original triple.

Every unordered meeting pair has a unique common point v and can be written
T1={v,a,b}, T2={v,c,d}, with four distinct outer points. Its coefficient
pair(alpha,-alpha), alpha nonzero, cancels v. The resulting word has value
alpha on{a,b} and -alpha on{c,d}. These two values are distinct overF5.
From the word recover the two outer pairs, and recover each triple as the
unique triple containing its outer pair. Linearity permits at most one such
completion. This recovers the original pair and its coefficient assignment,
so every pair supplies four distinct weight4 words without collisions.

Unlike the binary collision proof, no induced graph edge recovery is needed:
the two nonzero values retain the partition. Linearity is sufficient here.
The number of meeting pairs is exactly Q because each has one common point.

## Noncancelling meeting pairs

For alpha,beta nonzero with alpha+beta nonzero, the word has value alpha on
the two outer points of T1, beta on those of T2, and alpha+beta on v.

If alpha differs from beta, the central value differs from both outer values.
Its multiplicity is one, while the outer value multiplicities are two each.
The word therefore recovers v, both outer pairs, their triples and coefficients.

If alpha=beta, the central value2alpha is distinct from alpha. It identifies
v uniquely, and the four outer points all have value alpha. For each outer
point u, there is at most one triple containing{v,u}, by linearity. The two
original triples and the outer partition are therefore recovered uniquely
even though the four outer values coincide.

There are4 choices for alpha and3 nonzero choices for beta other than-alpha,
giving12 assignments per unordered meeting pair. Coefficients are assigned to
an arbitrary fixed order of the two triples; the recovery ensures distinct
words and prevents a factor-of-two overcount. Hence B_5>=12Q.

## Disjoint pairs

A disjoint pair T1,T2 with nonzero coefficients alpha,beta gives weight6.
If alpha differs from beta, the two triples are recovered as the two three-point
value classes. If alpha=beta, the support alone suffices: the only triples of
the linear system contained in T1 union T2 are T1 and T2. Any other triple
would contain two points from one of the original triples and violate linearity.

Thus coefficients and the pair are recoverable, and there are16 distinct
words per disjoint pair. There are binom(m,2)-Q such pairs. This yields B_6.
Sums of three or more columns may give more words at all these weights.

## Adding the constant word

Assume n>6 and j_n is in D. For c nonzero and a=-c, the word c j_n+a N_T
vanishes exactly on T, producing4m distinct words of weight n-3.

For c,a nonzero with a differing from-c, it is nonzero on every point.
For any two triples, a point outside their union exists since n>6. Equality
of two such words first gives the same c at that point, and then the same
triple and a from their nonzero difference. This recovers12m distinct words
of weight n. They differ from the four nonzero constant words, yielding12m+4.

The n>6 boundary is essential to this proof; it is not imposed on the earlier
four low-weight bounds. If a high and low weight coincide in a smaller example,
their lower counts must not be added without another disjointness proof.

## Exact character rows for a future experiment

Let C=ker_F5(N^T), A_w its ordinary weight counts, M=|C| and A_0=1.
Ordinary dot orthogonality gives C^perp=D. Define the quinary Krawtchouk
polynomial by the explicit finite integer expression

    K_j(w)=sum_h (-1)^h 4^(j-h) binom(w,h) binom(n-w,j-h).

Choose any nontrivial additive character of F5. Its sum over C is M for an
element of C^perp and zero otherwise. Summing over all ambient words of
weight j therefore gives exactly

    sum_w A_w K_j(w)=M B_j.

For any displayed lower count N_j, the constant-preserving necessary row is

    sum_(w>0) A_w*(N_j-K_j(w)) <= K_j(0)-N_j.

This convention includes A_0=1; replacing the right side by an untracked
multiple of M would discard the exact constant. The character identity is
classical and shared with the pinned binary image-count note; only the present
F5 coefficient recovery/counts are being proposed here.

Once an applicable support55 result is independently accepted, a finite
necessary relaxation could restrict A_w to55..99, add A_w>=0, M=1+sum A_w,
scalar closure4|A_w, the six displayed character rows, all nonnegative dual
coefficients, and the independently justified self-orthogonality C subset D.
No optimum, dimension bound or complete enumerator is computed or predicted.
Even a rational feasible enumerator need not come from any code or graph.
The zero code C={0}, D=F5^99 is allowed and satisfies these lower-count rows.

## Hand boundaries and failed simpler routes

For the actual3x3 rook graph, m=6 and Q=9. The construction gives separate
lower counts24,36,108,96 at weights3,4,5,6 and high counts24,76 at weights6,9.
The two weight6 counts overlap: complementing a row triangle is the sum of the
other two row columns. They must not be added. This is a hand interpretation,
not a complete3125-word enumeration or new rook-code gate.

The linear Pasch system123,145,246,356 explains the characteristic boundary.
OverF2, the two meeting-pair sums123+145 and246+356 both have support2345,
so linearity alone does not prove the analogous binary weight4 count. OverF5,
the cancelling words instead have different value partitions; the proof above
retains precisely the data lost in characteristic two.

A simple quinary Griesmer use of distance55 gives only dim(C)<=33:
55+11+3+30 ones=99 for dimension33, and one more unit violates99.
The determinant already gives dim(C)<=27, so this route is weaker.
The abstract one-dimensional code generated by(1^55,0^44) is balanced and
self-orthogonal overF5 and has enumerator1+4z^55. It does not satisfy actual
triangle-incidence conditions. It falsifies only a contradiction inferred
from those generic code constraints, not the target-specific theorem.

## Bounded overlap and scope limits

The named binary low-image note proves its231/2079/24486 counts with graph
edge recovery. The new coefficient labels make the present odd-characteristic
proof valid for every linear triple system. Targeted searches of docs and the
named Wave102/141/171 coding sources found binary24948 counts, F7 endpoint
enumerator obstructions and earlier characteristic-specific conditions, but
no matching quinary six-count package. This is not exhaustive novelty checking.

Root requested a genuinely different follow-up to support55/signed design.
Structural supplied this mathematical candidate. No code source, solver,
backend, import, ledger/Git change, general code feasibility result or global
Conway99 resolution is authorized or supplied by this note.
