# Independent written audit: the connected subcubic support lower bound

Discovery producer: ROOT. Independent verifier: Checkpoint.
The unchanged source is
`docs/CANDIDATE_20261003_TERNARY_CONNECTED_SUBCUBIC_SUPPORT_LOWER45_V1.md`,
SHA256 4948749bfa84348792f04628f5dd24dee3c7837f6bc7d1c30933f23a01b2902f.
All work here is an exact human-checkable written derivation. No mathematical
program, graph fixture, solver or exhaustive computation was executed. Prior
support claims are context only; no earlier theorem is a premise.

## Exact statement checked

For every 99-by-99 symmetric binary zero-diagonal matrix A with exactly 14 ones
in each integer row, put M=(A^2+A-12I-2J) modulo 3 and let H be its simple
nonzero unordered off-diagonal support, with isolated vertices discarded.
Suppose H is nonempty, connected and has maximum degree at most 3. Let m be
its number of vertices; if H is bipartite let p be the size of a larger part,
and otherwise let p=m. Then p*(48-m)<=72. Consequently m>=45, and if H is
not bipartite, m>=47. No allowed support is asserted realizable; disconnected
or higher-degree supports and target existence/nonexistence are outside this
claim.

Connectivity concerns the whole nonisolated residual support, not A. No
automorphism, lambda1, incidence, fixed graph, prescribed internal adjacency,
numerical relaxation or uniform graph profile is assumed. This statement is a
new broader claim than the separately preserved at-most12 restriction.

## Reproduced prerequisites

Write D=A^2+A-12I-2J over the integers and r_uv=D_uv for u!=v.
Symmetry and binary degree14 give (A^2)_uu=14 and D_uu=0. Each complete
common-neighbor row sums to196, giving the complete off-diagonal residual sum
(196-14)+14-2*98=0. All r_uv>=-2; every good pair, meaning r_uv divisible
by3, therefore has r_uv>=0.

Exact symmetry and regularity imply AJ=JA=14J. Direct product expansion gives
AD=DA, so AM=MA. Nonzero residues are shared undirected signs+1 or-1. Each
support row sums to zero modulo3, forcing minimum support degree two. At
degree two the two labels are opposite; at degree three all labels agree.

Let S=V(H). If z is outside S, its entire M-row is zero, so x*M[S,S]=0 for
the binary vector x_u=A_zu. A degree-two column forces equality of its two
neighbor coordinates. A degree-three column forces their three-term binary
sum to be zero or three, making all three coordinates equal. Thus coordinates
are constant along every length-two walk and consequently every even walk.

In a connected bipartite H, same-side paths are even and cross-side walks are
odd. In a connected nonbipartite H, a path to an odd cycle, the cycle and the
reverse path give an odd closed walk at any starting vertex. Prefixing it
flips an odd connecting path into an even walk. Hence the equality classes are
the two sides in the first case and all of S in the second. This is binary
coordinate propagation, not a graph automorphism.

Choose P as a larger bipartition side, or all of S in the nonbipartite case.
Set p=|P|. Every u in P has exactly the same outside neighborhood, of size t,
and therefore internal degree d=14-t in S. Minimum support degree two and
simplicity ensure p>=2 and m>0, so every denominator below is positive.

## Independent double count and rational lower bound

For each w in S, let a_w=|N_A(w) intersect P|. Counting incidences between
P and S from both endpoints, using symmetry, gives

 sum_[w in S] a_w = p*d.

Each of the t common outside vertices is adjacent to every vertex in P and
contributes exactly choose(p,2) to the sum of common-neighbor counts on P.
Each internal vertex w contributes choose(a_w,2). These are disjoint choices
of the common-neighbor vertex and cover every term, giving

 T = sum_[u<v in P] CN(u,v)
   = choose(p,2)*t + sum_[w in S] choose(a_w,2).

No degree or pattern of internal adjacency is silently prescribed. In
particular a_w may include an internal vertex of P among its neighbors, but
the zero diagonal automatically prevents a common-neighbor term equal to an
endpoint. There is no loop contribution to correct by hand.

An independently expanded sum of squares proves the needed bound:

 0 <= sum_[w in S] (a_w-p*d/m)^2
   = sum a_w^2 - p^2*d^2/m.

Thus, dividing the exact pair count by choose(p,2)>0,

 T/choose(p,2)
 >= t + (p*d^2/m-d)/(p-1)
  = 14 + p*(d^2/m-d)/(p-1)
  = 14 - p*m/(4*(p-1))
       + p*(d-m/2)^2/(m*(p-1))
 >= 14 - p*m/(4*(p-1)).

This is exact rational algebra and a nonnegative square for every permitted
integer d. It does not require equality in the bound, equal internal degrees
a_w, independence of neighborhoods or feasibility of the real minimizer m/2.

## Independent upper bound and conclusion

If H is bipartite, every pair inside P is good. For u in P, at most three
bad pairs occur elsewhere in its complete residual row, with total at least
-6. Every other good entry is nonnegative and the row totals zero, so
sum_[v in P,v!=u] r_uv<=6. Sum over P: each unordered pair is counted twice,
giving sum_[u<v in P]r_uv<=3p.

If H is not bipartite, P=S. All pairs from S to its complement are good and
nonnegative. The exact zero row instead gives sum_[v in S,v!=u]r_uv<=0,
whether internal pairs are bad or good. Thus the same weaker bound 3p also
holds. Internal bad pairs are not incorrectly declared nonnegative.

Using CN(u,v)=r_uv+2-A_uv and A_uv>=0 in either case yields

 T/choose(p,2) <= 2 + 6/(p-1).

Compare the rational lower and upper bounds and multiply by 4*(p-1)>0:

 56*(p-1)-p*m <= 8*(p-1)+24,
 p*(48-m) <=72.

For the size consequences, minimum support degree two gives m>=3 in the
nonbipartite case, while simplicity of a bipartite support gives both sides
at least two vertices and m>=4. Always p>=m/2 when m>=4. If 4<=m<=44, the
factor 48-m is positive. The exact factorization

 m*(48-m)/2 -88 = (m-4)*(44-m)/2 >=0

gives p*(48-m)>=88>72. This independently checks the producer's concavity
step without accepting a numerical endpoint plot. The remaining m=3 case
is nonbipartite with p=m, yielding135>72. Therefore m>=45. When H is
nonbipartite, p=m; at m=45 and46 the left sides are135 and92, respectively,
again larger than72. Hence this case requires m>=47.

## Written falsification inventory (12 checks, zero executed fixtures)

1. Exact symmetry/binary degree14 fixes diagonal14 and complete CN row196;
   subtracting the diagonal gives the exact off-diagonal residual row0.
2. Expand both commutator products before reducing modulo3; both AJ and JA
   must be14J.
3. Reproduce degree-two/opposite and degree-three/equal sign rules, binary
   neighbor equations and both even-walk cases, including odd closed walks.
4. Establish p>=2 and m>0 before dividing; p=1 is not silently admitted.
5. Outside equality gives a literal common neighborhood count t and exact
   internal degree d=14-t for every vertex of P. Uniformity of a_w is not used.
6. Common-neighbor double counting covers each internal or outside vertex once,
   with endpoint/loop terms excluded automatically by A's zero diagonal.
7. Symmetric incidence counting gives sum a_w=pd; a directed graph would not
   justify the replacement of the sums by these degrees.
8. Expand the rational sum of squares to recover Cauchy directly. All terms,
   including the linear sum pd, are included and no independence is assumed.
9. Check the completed square and its positive coefficient. The real value
   d=m/2 need not be an allowable integer degree for the bound to hold.
10. Bipartite same-side pairs are all good; at most three bad entries supply
    only six negative budget, and unordered summation requires the factor1/2.
11. In the nonbipartite case the stronger upper bound follows from good outside
    pairs. Internal pairs may be bad; no false all-good premise is used.
12. Preserve inequality directions when multiplying by4*(p-1). Factor the
    interval bound exactly and check m3/45/46 as135/135/92. No floating-point
    score, approximate bound or table percentage supplies the conclusion.

## Verdict and limits

VERIFIED for the exact necessary inequality and its stated size corollaries
by this independent written derivation. The sum-of-squares expansion, literal
common-neighbor double count and factorized interval lower bound are separate
checking paths. Twelve falsification boundaries were checked on paper; zero
mathematical programs, graph fixtures or adjacency realizations were produced.

Definitions and elementary integer/GF(3) arithmetic are shared with discovery,
but neither producer code nor prior small-support claims are premises. Degree
four lacks the binary three-neighbor propagation rule, and disconnected
support does not justify the one- or two-class propagation across all of S.
Those cases are excluded from the statement, not declared impossible. The
result does not resolve target existence, classify realizability of any
remaining support, establish novelty or peer review, or approve an engine.
The older at-most12 candidate and audit stay unchanged. Any stronger inference
would be a separate claim. Overall search coverage: UNKNOWN; no validated
denominator.
