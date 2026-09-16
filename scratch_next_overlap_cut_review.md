# Independent mathematical review of the generalized overlap capacity cut

Result: the current `scratch_next_overlap_cut.py` is a sound necessary
inequality for an arbitrary **complete** overlap assignment K at E0=0.
No mathematical error was found in its quota formula, pair-cap formula,
integer coefficient combination, or box correction. The current numerical
edge indexing and certificate provenance were independently checked.

The important scope restriction is that all unlisted overlapping-support
pairs are fixed nonedges. This is not a proved pruning rule for a partial
overlap search prefix in which more overlap edges may still be added.

## 1. Variables and the exact hypotheses

The84 outer vertices are indexed by the four signed corners of each of
the21 unordered pairs of seven root-neighbour groups. K is symmetric,
hollow, and supported only on pairs whose group supports intersect in
exactly one group. At E0=0 all same-fibre edges are absent. The remaining
unknown adjacency X is symmetric, hollow, and supported on disjoint group
supports. Thus a hypothetical completion has B=K+X.

The evaluator includes all1,680 disjoint-support pairs as variables. It
does not remove candidates using the original K, compression C, an
original block total, or a previously exposed forbidden-edge list.
The input need not independently pass all degree and local consistency
checks for the inequality to remain necessary: an invalid complete K
simply has no graph completion. Passing the cut does not certify validity
of K.

The CLI rejects duplicate, noncanonical, out-of-range, and non-overlap
edges. The function-level input is naturally a set of canonical pairs;
the orbit wrapper validates the original input before transforming it.

## 2. Label quotas

For an outer vertex u and first-layer symbol s, the required number of
outer neighbours carrying s is

```text
q0(u,s)=1 if the group of s belongs to the support of u,
        2 otherwise.
```

If s itself is a neighbour of u, lambda=1 gives the first case. If the
matching mate of s is a neighbour of u, that mate already contributes one
of the two common neighbours required by mu=2, leaving one outer common
neighbour. If neither sign is in the support, both common neighbours must
be outer. Therefore the residual equality is exactly

```text
sum_(v carrying s) X_uv
 = q0(u,s)-sum_(v in N_K(u)) [s in label(v)].          (1)
```

This proves the evaluator's `label_quota` branch for every complete K.
Any fixed multiplier of either sign may multiply (1). The certificate's
658 nonzero equality multipliers are not required to cover every quota.
Omitting unused necessary constraints only weakens the test.

## 3. The linear pair cap

Let t_uv be the number of shared exact first-layer labels. For distinct
outer vertices the SRG equation says

```text
(B^2)_uv+B_uv=2-t_uv.
```

Substitute B=K+X and discard the nonnegative term (X^2)_uv. This gives

```text
X_uv+(KX+XK)_uv
 <= 2-t_uv-K_uv-(K^2)_uv.                            (2)
```

Its left side is X_uv, when uv is a disjoint candidate, plus X_vw for each
known K-neighbour w of u and X_uw for each known K-neighbour w of v. Its
right side is exactly the evaluator's pair-cap bound. The condition does
not depend on a compression block total or the original known-edge set.
The376 used pair-cap multipliers are nonnegative, as required.

This argument also explains why the inequality remains necessary when
the unknown disjoint edges are relaxed to numbers in[0,1]: nonnegativity
is all that is used in discarding X^2. It does not claim the linear
relaxation enforces the original quadratic SRG equation.

## 4. Box correction and index provenance

Combining (1), (2), and selected valid upper bounds x_e<=1 gives

```text
sum_e w_e(K)x_e <= R(K).
```

For any0<=x_e<=1,

```text
sum_e w_e(K)x_e >= sum_e min(0,w_e(K)).
```

The lower bound is attained on the independent box by setting x_e=1
where its coefficient is negative and0 elsewhere. Consequently

```text
score(K)=R(K)-sum_e min(0,w_e(K)) >=0                 (3)
```

is necessary. The negative-part term is essential when moving K: the
original nonnegative combined coefficients need not stay nonnegative.
A negative score proves infeasibility even over the box relaxation;
a nonnegative score proves only passage of this one inequality.

The evaluator recomputes quota and cap bounds/terms from K rather than
reusing original targets. The only metadata it reuses are fixed semantic
coordinates and the certificate's fixed multiplier assignments. Discovery
using a particular C does not invalidate these multipliers on another K.

There is a numerical-index precondition: the edge upper-bound multiplier
id must identify the same disjoint pair in the reconstructed canonical
list. The current list agrees exactly with all1,680 `edge_variables` rows
in the semantic map. The checker also validates the signs/types of every
used multiplier and excludes every `block_total` group from the weighted
sum. Thus no hidden original-C assumption was found.

The base evaluator does not itself pin hashes or recheck this id map.
This is a provenance precondition for reusing or replacing its artifacts,
not a flaw in the current inequality. The review JSON records the current
certificate, metadata, and evaluator hashes.

## 5. Sign relabeling and the orbit wrapper

Each seven-bit sign mask swaps the two first-layer labels independently
within the indicated groups and induces a permutation of the84 corners.
It preserves overlap/disjoint relations, exact-label intersections, the
quota family, and the pair-cap family. Hence (3) applied to gK is valid
whenever K has a graph completion.

The fixed multipliers are not relabeled along with the input when the
same evaluator is applied to gK. Its score therefore need not equal its
score on K. The seven positive single-flip scores are expected; they are
not a soundness defect and are not completion witnesses.

For H=(C2)^7 the full orbit score

```text
F(K)=min_(g in H) score(gK)
```

is both necessary and H-invariant, since hK merely permutes the128 terms
by g -> gh. The new orbit wrapper loops over all128 masks, canonicalizes
each image, and takes their minimum; its handling is consistent with this
proof. Caching identical images does not change the minimum. These128
sign operations do not include the5,040 permutations of the seven groups.

## 6. Optional simplification, not a correction of an error

Once the box correction is used, the stored nonnegative edge-upper-bound
multipliers gamma can only weaken the resulting score. Let w0,R0 denote
the combination before adding them. Then

```text
score_gamma = R0+sum_e max(gamma_e,-w0_e),
score_0     = R0+sum_e max(0,-w0_e),
score_0 <= score_gamma.
```

Dropping gamma therefore gives another valid, at-least-as-strong necessary
cut. On the original assignment both scores are-807. On the seven tested
single flips the score decreases by37 to57, while remaining positive.
This optional simplification was checked and recorded only; the base cut
and certificate were not changed.

## 7. Independent finite checks and boundary

`scratch_next_overlap_cut_review.py` imports neither the base evaluator nor
a solver. It reconstructs coefficients from a symmetric multiplier
matrix and computes each disjoint-edge coefficient directly. It verifies:

- the original score-807 and all826 nonzero original coefficients;
- all eight previously recorded fixed-cut sign scores;
- all128 sign actions and all16,384 group compositions;
-10,458 pair-cap expansion identities and3,528 quota identities on three
  unrelated complete K assignments, using integer-scaled box variables
  taking values0,1/2,1;
- the coefficient-wise exact box lower bound and current id provenance.

The unrelated K assignments are semantic unit controls, not admissible
graphs or new completion candidates. The status is
`INDEPENDENT_ARBITRARY_COMPLETE_OVERLAP_CUT_REVIEW_PASS`, recorded in
`scratch_next_overlap_cut_review.json`.

This review proves soundness of the necessary cut in its stated scope. It
does not assert that all overlap assignments are excluded, that the cut
is complete, or that any positive score has a feasible linear or graph
completion. No solver, new graph search, or base-cut mutation was used.
