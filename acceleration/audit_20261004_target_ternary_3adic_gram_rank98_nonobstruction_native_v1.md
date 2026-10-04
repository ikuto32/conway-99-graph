# Native independent written audit: prescribed 3-adic Gram rank98 nonobstruction

State: written PASS within the exact field and relaxed-entry scope below. This audit is a separately authored derivation and falsification attempt by Native. Structural authored the candidate; Root proposed the direction and will separately review this packet. Agreement is not approval. No interpreter/import/AST, numerical matrix calculation, solver, enumeration, formal/external checker, actual factor export or protected-state action occurred.

Candidate paper: docs/CANDIDATE_20261004_TARGET_TERNARY_3ADIC_GRAM_RANK98_NONOBSTRUCTION_V1.md, SHA e696616dd5d9e7bb52debaa9b4a8cf8d9bc1675c46229ebd61b809d969426309.
Raw exact statement: acceleration/results/20261004_target_ternary_3adic_gram_rank98_nonobstruction_candidate01.json, SHA a1acb8ecff3b972092c5dbc14c7f088871a2727e76ea7c4a94abe16edbda8502.
Original raw claim_id/revision are null; this audit invents no historical identity. Final report timestamp is recorded separately; original start is unknown/null.

## Exact statement read and field boundary

For every symmetric integer 99-by-99 matrix H with Hj=21j whose ternary reduction G satisfies Gj=0, G^2-G=2J and rank(G)=55, there exists a 99-by-231 matrix M over the 3-adic integers with MM^T=H, M1=7j, M^Tj=3*1 and rank_F3(M)=98. For every m>=1 an ordinary integer matrix with the same exact margins and rank98 can be chosen whose Gram is H modulo3^m, with coherent successive residues. This does not require or assert binary entries, nonnegative entries, triangle supports, or an ordinary integer exact-Gram factor.

In the second sentence, rank98 is read as rank over F3, explicitly specified in the paper's exact displayed statement and the preceding raw sentence. It is not an ordinary rational rank claim. For the actual target H, at precision m>=46 every such ordinary matrix necessarily has rational row rank99: determinant congruence transfers H's inherited valuation45, so its Gram determinant cannot be zero. Future canonical wording must retain rank_F3 explicitly.

The theorem constructs unrestricted Z3 entries for a prescribed compatible H, and ordinary integer approximants with congruent Gram, not an ordinary integer exact factor. The target application is conditional on existence of A and its known rank55 Gram; no actual target H is constructed. Constant-only left kernel is allowed by this relaxation. No claim that actual binary incidence has constant-only kernel, or that a nonconstant kernel is excluded, is verified.

## 1. Independent first-field reduction

All operations here are in F3. With G squared-G=2J=-J, Gj0, symmetry and99=0:
GJ=JG=0, J squared=0 and G cubed=G squared.
Set E=G squared. Then E squared=E, E is symmetric and G=E+J.

Its image and kernel are direct complements, and symmetry makes them orthogonal.
Ej0, so j is in kerE and outside imE. For an arbitrary coordinate vector e, put z=(I-E)e.
Then Ez0 and sumz=1 because j-transpose E0. Thus Gz=Jz=j.
On imE, G is the identity. On kerE, G=J. Consequently
imG=imE directsum<j>, rankE=55-1=54.

Take any98-dimensional complement to<j>, for example the first98 coordinate vectors.
Because j is already in radG, restriction to this complement retains rank55;
its radical therefore has dimension43. This does not assume that radG itself is only<j>.

Diagonalization of this restricted symmetric form follows directly from polarization:
if every vector has norm0, odd-characteristic polarization forces the form0.
Otherwise split a nonzero norm direction and continue.
The55 nonzero diagonal entries are1 or2. Two entries2,2 can be replaced by
sum/difference directions, whose norms are1,1 and cross product0. The change
matrix has determinant-2=1, so is invertible. Thus at most one2 remains.

Realize each1 direction by one standard coordinate; a lone2 by(1,1).
Each zero radical direction is realized by a separate(1,1,1), which is nonzero
but has norm3=0. Disjoint supports give all required cross products and row independence.
The55 nondegenerate directions use at most56 coordinates;43 radical directions
use129 more. Total at most185, leaving at least46 unused out of231.
Undoing the congruence gives98 independent rows B with BB-transpose=D.

Add row99 as minus the sum of these98 rows. Since Gj0, the prescribed last
row and column of G are exactly recovered, including the last diagonal.
The resulting N0 has N0N0-transpose=G, N0-transpose j0 and rank98;
its left kernel is precisely<j>.

## 2. Obtain the row-margin residue by an explicit isometry

The above z satisfies Gz=j and sumz=1. Therefore v=N0-transpose z has
v dotv=z-transpose Gz=1. Choose t=(1,1) on two unused coordinates.
Then t dott=2, v dott0 and N0t0. Thus w=v+t is nonzero isotropic and N0w=j.
The all-one q of length231 is also nonzero isotropic.

For nonzero isotropic u,v with c=u dotv nonzero, r=u-v has norm-2c nonzero.
The reflection R_r(x)=x-2(x dotr)/(r dotr)r sends u to v.
If u dotv0 and they are independent, nondegeneracy permits y with
u doty=v doty=1. Put h=y-(y doty)u/2. Its norm is0 and both h dotu,h dotv are1.
For v=a*u, choose u doty=1; then h dotv=a is still nonzero.
Two allowed reflections send u to h and then h to v in both zero-dot cases.
No division by an isotropic reflecting norm is permitted.

Choose an isometry O with Ow=q and define N=N0 O-inverse.
Then Nq=N0w=j, NN-transpose=G, N-transpose j0 and rank98.
The inverse orientation on columns is necessary; using O without justification
does not establish the required row margin.

## 3. The crucial q-not-row-image check

If N-transpose x=q, then Gx=Nq=j. Applying E gives Ex0;
then Jx=j implies sumx=1. But
q dotq=x-transpose Gx=sumx=1,
contrary to q dotq=231=0. Thus q is outside imN-transpose.
Rank98 by itself would not provide this fact; both the Gram and Nq=j are used.

## 4. Independent exact margin repair

Lift the entries of N to any ordinary integer B0.
The differences alpha=(7j-B0q)/3 and beta=(3q-B0-transpose j)/3 are integers.
Their total sums agree because both target totals are693.

For any such pair of integer margin vectors, place alpha_i in the last column
of each nonlast row, beta_a in the last row of each nonlast column,
and the corner alpha_last-sum(beta_nonlast).
The nonlast margins and last row are correct by construction;
equal totals give the final column. Negative entries are essential permissions.

M1=B0+3S has exact row7/column3 margins, reduces to N,
and M1M1-transpose=H modulo3. This establishes only a first congruence,
not binary entries or an exact ordinary Gram.

## 5. Independent coherent lifting argument

Assume Mk has these exact margins and Gram correct modulo3^k, k>=1.
Dk=(H-MkMk-transpose)/3^k is an integer symmetric matrix.
Its product with j is exactly0:
Hj21j, while MkMk-transpose j=Mk(3q)=21j.

Let Dbar be its reduction. Define T on the98-dimensional image imN-transpose by
T(N-transpose x)=Dbar*x/2.
It is well-defined because kerN-transpose=<j> and Dbar j0.
Symmetry makes all values lie in j-perp.
The separately proved q-not-image fact allows extension with Tq0;
complete a basis and send any other directions to0 in j-perp.
Then TN-transpose=Dbar/2 and T-transpose j0.

For any integer lift That, B=Mk+3^k That satisfies
BB-transpose=MkMk-transpose+3^k(TN-transpose+NT-transpose) modulo3^(k+1).
The bracket is Dbar with the correct plus sign.
The quadratic term is divisible by3^(2k), hence by3^(k+1);
k=1 already gives9, so the first nontrivial lift is valid.

Both B-margin errors are multiples of3^(k+1), and their totals agree.
The same unrestricted margin construction supplies an addition3^(k+1)S
restoring them exactly without altering the newly correct Gram residue.
Thus Mk+1 agrees with Mk modulo3^k, retains N modulo3 and has the next precision.

The entrywise sequence is Cauchy in the complete ring Z3.
Its limit M has exact GramH and exact margins by polynomial continuity.
Its reduction is still N, so ker_F3(M-transpose)=<j>.
No convergence in the ordinary real metric, bounded entries or common
ordinary integer matrix exact at all levels is deduced.

## 6. Target-specific right inverse and module consequences

This section additionally assumes H=A+7I for an actual hypothetical target A.
Direct expansion using A squared=12I-A+2J gives
H(6I-A)=42I-A-A squared=30I-2J.
For P=7M-transpose(6I-A)+2qj-transpose:
MP=7(30I-2J)+2(7j)j-transpose=210I.

Since210=3*70 and70 is a Z3 unit, 3Z3^99 is contained in imM.
The cokernel is killed by3. Its reduction dimension99-rank(N)=1
therefore gives cokerM exactlyF3, not a factor9 and not GramH's cokernel.
Smith equivalence here is for the rectangular module map; it is not a
symmetric congruence statement for H. MP also gives Q3 row rank99.

For a modulo9 left vector X reducing to c*j, write X=c*j+3z.
M-transpose X=3(cq+N-transpose z) modulo9.
If c is nonzero, q would belong to imN-transpose, impossible.
Vectors3z reducing to0 can remain in the modulo9 kernel; they do not refute nonlifting.

K=kerN has dimension231-98=133.
On L=<j>, the divided pairing is gamma(j,u)=sumu because M-transpose j=3q.
This functional is nonzero on K: otherwise q belongs to K-perp=imN-transpose.
Its kernel has dimension132, so the quotient pairing is one-dimensional and perfect.

Smith form has98 unit directions, one factor3 and132 zero columns.
The exact Z3 right relation module is a direct summand of rank132.
Equivalently its quotient by the kernel is imM, a free torsion-free module.
Its reduction embeds in K. Every relation is balanced since
0=j-transpose Mu=3 q-transpose u in the characteristic-zero domain Z3.
Its132-dimensional reduction is therefore precisely ker(sum|K).
This is liftability to a Z3 relation, not an assertion that an arbitrary
3-adic matrix has132 ordinary Z relations. The old actual integer-incidence
theorem has the stronger Z-lattice interpretation; the formal factor does not export it.

The Gram is the same prescribed H, so the inherited determinant valuation45
and divided-form rank43/radical<j> remain applicable. L=<j> is beta-isotropic.
Nothing in those retained facts forces another left vector.

## 7. Falsification boundaries with actual field restrictions

1. A zero radical vector can be embedded by a nonzero triple(1,1,1).
   A single1 or a pair(1,1) would have nonzero norm and would corrupt the required Gram.
2. A reflection in u-v is invalid when u dotv0; the bridge h is required.
   Odd prime3, division by2 and nondegenerate ambient dot space are used explicitly.
3. Width231 is not cosmetic:185 coordinates implement the rank55/radical43 embedding,
   and two more unused coordinates are available for t. A short-column generalization is unproved.
4. If the desired column margin were2q while the row margin stayed7j,
   totals462 and693 would disagree; an exact joint margin repair would be impossible.
5. At k0 the quadratic term need not vanish modulo3. The induction starts at k1.
6. An arbitrary integer lift need not have the correct Gram modulo9.
   The derivative T and second margin repair are essential, not optional heuristics.
7. For the target and m>=46, ordinary Q row rank98 contradicts the known determinant valuation45.
   Only the finite matrices' F3 rank98 is verified.
8. The small binary Q=J4-I4 has QQ-transpose=I+2J, Qj=3j and determinant-3;
   its left/right ternary kernels are constant lines and gamma(j,j)=4=1.
   It supplies a constant-only/perfect-pairing boundary at different dimensions,
   and its Gram polynomial is not this target polynomial.
9. Rook9 has singular A+2I, real rank5 and different modular identities.
   The target P/right-inverse/rank55 data do not transfer to that example.
10. An ordinary integer exact target factor would already be binary:
    each row has sum m_ia=7 and sum m_ia squared=Hii=7, so
    sum m_ia(m_ia-1)=0. Each integer summand is nonnegative,
    hence every entry is0 or1. Column sum3 gives triangle supports;
    off-diagonal Gram entries0or1 force every edge once and forbid duplicated triangles.
    Thus omitting ordinary integer exact Gram is a substantive boundary even
    without an explicit separate binary assumption.
11. The general theorem cannot be strengthened to ordinary integer exact factors.
    Start with any compatible formal G (the old concrete F3 example supplies one),
    obtain the first exact-margin integer M1 above and put H1=M1M1-transpose.
    For u=e1-e2, Hc=H1-3c*uu-transpose retains Hj21j and the same G.
    Sufficiently large ordinary c makes u-transpose Hc u negative.
    Such Hc has no ordinary integer exact Gram factor, but meets the theorem's Z3 hypotheses.
    This is a written existence/corruption argument, not an exported numerical matrix.
12. Exact finite Gram congruence does not make row sum-of-squares exactly7.
    Large nonbinary approximants and a 3-adic limit remain possible.
    No ordinary bounded/binary support is recovered by coherent precision alone.

## 8. Bounded archive comparison and outcome

The six pinned candidate inputs were compared in their stated scopes.
The old reduced-Gram design produces one F3 example at degree residues;
its ordinary multipartite adjacency has degrees95/98 and is not a target.
The current theorem supplies every prescribed compatible H and exact margins/all
3-adic precisions. This is a genuine scope extension, not a reapproval of that old example.

The mod9 pairing and rank77 papers explicitly allow constant-only L;
their ordinary incidence conclusions are not contradicted.
Wave170 gives rank55 and elementary incidence upper98.
Waves171/172 concern the centered block code and marked prism-free weight-three
constraints; their extra endpoint hypotheses cannot be silently imposed here.
None is a proof that arbitrary Z3 factors force a nonconstant kernel.
No exhaustive literature/archive novelty search or external attribution is claimed.

The combined archive read had a629-token clipped middle of the rank77 text;
that exact local-congruence/isotropy section was reread in a separate bounded call.
No inference relies on clipped scientific evidence. Other reads were the whole
new paper/raw, whole reduced-Gram/mod9 sources and whole Wave170--172 Markdown.
Only text/metadata hashes were handled; no stored scientific matrix population was calculated.

Independent written outcome: PASS for the exact relaxed-entry statement, with
the finite rank field and Z3-versus-Z lifting interpretations explicitly retained.
The failed implication is only that the enumerated unrestricted 3-adic
Gram/margin/module conditions alone force a second left ternary dependency.
No claim about binary target incidence, target existence/nonexistence,
nonconstant left-code existence, ordinary exact Gram, novelty or search coverage is approved.

## Written boundary inventory

1. Exact general hypothesis: prescribed symmetric integer H, Hj=21j and stated F3 identities/rank, without a binary hypothesis.
2. j is nonzero and isotropic because99=0 inF3; q is nonzero isotropic because231=0.
3. Symmetry plus Gj=0 gives GJ=JG=0, and J squared is0.
4. E=G squared is a symmetric idempotent and G=E+J.
5. imE and kerE are complementary and orthogonal; j lies in kerE.
6. The independent z=(I-E)e argument gives imG=imE directsum<j>, hence rankE54.
7. The98-coordinate complement to<j> gives D rank55 with radical43.
8. Odd-characteristic polarization gives a nonzero-norm pivot for every nonzero symmetric form.
9. Two diagonal2 coefficients become1,1 by the invertible sum/difference basis change.
10. Unit coefficients1 and the possible single2 embed in at most56 standard coordinates.
11. Forty-three radical directions use disjoint nonzero isotropic triples(1,1,1).
12. At most185 coordinates suffice, leaving at least46 unused coordinates.
13. Undoing congruence preserves independence and the prescribed D Gram.
14. The negative sum99th row recovers precisely the missing G row/column.
15. N0 rank98 and N0-transpose j0 imply left kernel exactly<j>.
16. The same z has coordinate sum1 and Gz=j.
17. v=N0-transpose z has norm1.
18. Two unused coordinates give t norm2, perpendicular to v and killed byN0.
19. w=v+t is nonzero isotropic and N0w=j.
20. The required all-one q is nonzero isotropic in the ambient231-dimensional dot space.
21. Reflection in u-v sends u to v when u dotv is nonzero.
22. Zero-dot independent u,v admit y with both dot constraints1; the corrected h is isotropic.
23. The proportional isotropic case likewise has a two-reflection bridge.
24. Correct inverse column-isometry orientation gives Nq=j while preserving Gram/kernel/rank.
25. q outside imN-transpose follows from Gx=j and incompatible norms0 versus1.
26. An arbitrary entrywise lift has the required row/column residues modulo3.
27. Target totals99*7=231*3=693 agree before every margin repair.
28. The last-row/last-column integer margin construction works without positivity constraints.
29. M1 has exact margins, prescribed Gram residue and rankF3=98.
30. Dk j0 holds exactly from the exact margins and Hj=21j.
31. The prescription T(N-transpose x)=Dbar x/2 is well-defined on the98-dimensional image.
32. Its image lies in j-perp by symmetry and Dbar j0.
33. q outside the row image permits Tq0 and a full extension into j-perp.
34. The two linear Gram corrections add to Dbar with the required sign.
35. The quadratic correction vanishes at the next precision even for k1.
36. A second unrestricted integer margin repair preserves the newly achieved Gram residue.
37. Coherence gives an entrywise Z3 limit, exact Gram/margins and unchanged ternary reduction.
38. Finite ordinary matrices have F3 rank98; ordinary rational rank98 is not asserted.
39. For the target A, the direct identity H(6I-A)=30I-2J is independently expanded.
40. MP=210I follows with the exact factor7 and rank-one correction2qj-transpose.
41. OverZ3, cokerM is killed by3 and modrank98 gives exactly oneF3 factor.
42. Modulo9 a nonzero ternary left vector cannot lift, including the constant vector.
43. On the constant left kernel gamma(j,u)=sumu is nonzero on the right ternary kernel.
44. The balanced right subspace has dimension132 and equals reductions of the Z3 relation summand.
45. Target determinant/divided-form facts are inherited exact H facts; no new determinant calculation.
46. Ordinary integer exact target Gram plus row7 forces each entry0or1.
47. An indefinite compatible generalH falsifies an unqualified ordinary integer exact-factor strengthening.
48. Q=J4-I4 is a small constant-only/perfect-pairing boundary, not a target or this general-domain example.
49. Singular rook Gram has incompatible dimensions/polynomial/cokernel hypotheses and cannot be transferred.
50. Column width, odd prime and omitted ordinary bounded-entry conditions are explicitly checked.
51. Bounded comparison of six pinned derivations preserves historical overlap and endpoint assumptions.
52. No target existence/exclusion, nonconstant-kernel existence, novelty or actual matrix export follows.

There are52 itemized written checks and12 hand falsification boundaries,
zero executed controls/formal/external checks. All candidate/source bytes remain
unchanged. Native owned no computational worker and performed no ledger/index/Git mutation.

