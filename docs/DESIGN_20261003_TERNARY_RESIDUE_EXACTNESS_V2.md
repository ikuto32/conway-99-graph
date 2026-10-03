# Candidate degree-only ternary residue exactness

Status: CANDIDATE written proof and source-only heuristic design; independent
review and calibrated checking remain pending. No computation, optimizer,
claim-ledger change, engine change, novelty or resolution claim. This stronger
statement was proposed by ROOT and is outside the frozen356 publication cutoff.
Written checking author: /root/structural. Created_at: 2026-10-03T01:50:14.5501845+00:00. Source context:
00ffb6fdd7d91bd38269e1cc5e6b214ebf7591c8; new separately pinned working note.

The preserved V1 note72ac111beff5095550a93223b7029eeac19758c9120772274be29209ce5a07e5
assumed adjacent-CN1. Its exact narrower statement is not refuted. The present
quantifiers are broader, so a future ledger theorem requires a distinct claim
rather than silently enlarging that V1 statement or scope.

## Precise stronger statement

For every99-by99 symmetric binary matrix A with zero diagonal and exactly14
ones in every row, the following are equivalent:

(i) A^2=12I-A+2J exactly over the integers;
(ii) A^2=-A+2J over GF(3).

No prior adjacent-CN1, triangle decomposition, incidence-rank, kernel,
connectedness, automorphism or source-candidate assumption is required.
The symbols I and J denote the identity and all-ones matrices of order99.
Matrix (ii) is a complete entrywise congruence, not a sampled test, spectrum,
rank, diagonal-only condition or selected-principal-submatrix assertion.

## Integer derivation and attempted falsification

Fix a vertex u. Put c_uv=(A^2)_uv=|N(u) intersect N(v)| for u!=v. All these
counts are nonnegative integers. Regularity gives

sum_(v!=u) c_uv =14*14-14=182.

There are14 adjacent and84 nonadjacent endpoints. Congruence(ii) says
 c_uv congruent1 (mod3) for each adjacent v,
 c_uv congruent2 (mod3) for each nonadjacent v.
Write adjacent c_uv=1+3*s_v and nonadjacent c_uv=2+3*t_v. The integer counts
are nonnegative, hence every s_v,t_v is a nonnegative integer. Thus
 182 =14*1+84*2+3*(sum s_v+sum t_v)=182+3*(sum s_v+sum t_v).
Every s_v and t_v vanishes. All adjacent pairs have exactly1 common neighbor
and all nonadjacent pairs exactly2. Diagonal entries(A^2)_uu=14 agree with
12+2. This proves(i). Reduction of(i) modulo3 proves(ii), since12I vanishes.

Attempts to weaken the premises expose the actual proof boundary:
- Degree congruent14 modulo3 does not fix the integer row sum182; the saved
  degree95/98 reduced-Gram example lies outside the quantified domain.
- Selected/sampled residue equations leave other counts unconstrained and do
  not force the sum of the nonnegative excesses to vanish.
- Nonnegative integer counts are essential. Negative residues such as-2 and-1
  would invalidate the minimum1/2 argument; floats are not exact certificates.
- Modulo2 has adjacent minimum1 but nonadjacent minimum0; the lower bound14
  does not saturate182. The literal arithmetic pair0,4 has mean2 and residue0,
  and cannot be used to infer that both values equal2. This is an arithmetic
  countercontrol, not an asserted14-regular graph counterexample.
- The genuine saved99 degree14/lambda1 rank98 fixture fails the full SRG scalar
  validator; it therefore must violate at least one complete modulo3 equation.
  Its constant-only ternary incidence kernel does not refute this equivalence.
- The synthetic ternary factor and the actual regular14 fixture are different
  artifacts. Combining their separately satisfied premises is invalid.

Every root argument is identical and uses no target-graph symmetry. A graph
with(ii) would be an exact target solution, but the proof neither constructs
one nor proves none exists.

## Prospective residue-defect experiment, not execution approval

On the fixed domain of99-vertex14-regular simple graphs define
 F3(A)=number of unordered pairs{u,v} for which
       ((A^2)_uv modulo3)!=(2-A_uv).
It is a nonnegative exact integer objective. By the proved implication under
the stated domain, F3=0 has precisely the SRG target zero set. Its value is
not a progress percentage, feasibility certificate, rank measure or bound.
A complete independent integer SRG validator remains mandatory for any zero.

Define the separate ordinary integer defect
 E(A)=sum_(u<v) ((A^2)_uv-(2-A_uv))^2.
Either F3 alone with E diagnostics or the exact lexicographic pair(F3,E) could
be a newly declared heuristic. If a scalar implementation is desired,
 819820*F3+E gives the same lexicographic order because
 0<=E<=binom(99,2)*13^2=819819 in this fixed domain.
The crude bound uses0<=CN<=14 and target counts1/2; it is only an engineering
ordering bound, not an SRG existence or exclusion result.

The residue objective deliberately has different nonzero-state ordering.
For example CN5 is residue-correct for a nonadjacent pair while having
ordinary squared defect9. Regularity forces compensating deviations elsewhere
unless every pair is exact; their residue defects keep F3 positive. This
explains why residue zeros cannot conceal a target violation, but does not
predict faster search or superiority of the objective.

A future experiment must preserve the current strict-lex pipeline and be
separately versioned with fresh engine/state/proposal/checker gates. A graph
2-switch may preserve degree14; the existing linear-triple domain is a
proper subset and must not be presented as unrestricted graph coverage.
Root-only modular defects certify only a root when the relevant row walk sum
and residue conditions are fully checked; they do not certify the full graph.

Cheap prospective controls: independently count every9-vertex rook CN and
its k4 balanced row sum12; exact missing-row/changed-degree/asymmetry/diagonal/
nonbinary/residue corruption; negative0,4 modulo2 arithmetic; a synthetic
nonnegative row pattern reaching182 with the correct14+84 minima; a changed
unsaturated row sum; and a separately validated exact99 graph artifact if
available. No such new execution occurred for this note, and no old gate
approves the new objective or strengthened statement.

Existing context only, reused not freshly computed:
- Actual current.adj hash3f910d235e38191b5ac47523c22166f1abfc4d1f3ad285b60d4c684392a6670d.
- ROOT independent GF3 full report c7a65c9a91599b83bee38f22d5031ae5ca7a357818efe1e40541ebf2afd3db02.
- Candidate reduced-Gram note hash5a5c564e052a46c4958b5e07c3d318d61e3a6fd6e84b86011866080ddc33d95a.

Overall search coverage: UNKNOWN; no validated denominator.
