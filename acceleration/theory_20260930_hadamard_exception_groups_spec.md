# Few exceptional support groups: two distinct scopes

Freeze before execution; no solver or full-factor search. Allocation120 seconds. Preserve the original fixed support and the independently checked31,110 local triples. No target automorphism or balance-WLOG premise is introduced.

## Full-Gram consequence (candidate theorem)

Let t[p,a,f] count fibre f for coordinate a among support group p's three columns, and let delta=t-1. A full prescribed-Gram factor on this exact support satisfies the already independently checked triplicate marginal equations: for fixed a,f, the sum of delta over all ten groups containing a is zero, and for every nonmatched b the sum over groups containing both a,b is zero.

The coefficient matrix A_a has a leading all-one row and ten binary incidence rows. Its ten columns are distinct: two different supports containing a must differ at a coordinate b other than a or its mate. Any three distinct vertices of a binary cube are affinely independent over the rationals. Otherwise a nontrivial affine relation on three points would express one as a strict convex combination of the other two (after separating coefficient signs); a0/1 cube vertex cannot be a strict convex combination of two distinct cube vertices. Thus every nonzero vector in ker(A_a) has support at least four.

If at most three support groups were unbalanced, every delta vector would have support at most three, hence be zero. Therefore every such factor is entirely balanced. Equivalently an unbalanced full-Gram factor has at least four unbalanced groups. This is a conditional implication within this exact support, not a target or support-level nonexistence claim. It does not require the new balanced-CNF UNSAT result as a premise.

For exactly two groups, the shorter proof is useful: outside their intersection a deviation is isolated by the row-margin equation. On their intersection the two deviations cancel; a coordinate b in one support but not the other makes a summed-Gram equation isolate either deviation. All therefore vanish. No assumption about intersection size is used.

The executable binds the prior immutable marginal/census audit and checks every one-, two- and three-column subset of all twelve raw A_a matrices using exact nonzero minors. This finite input check calibrates and instantiates the written argument, which remains candidate until separate review. A synthetic four-corner binary square supplies a nonzero four-column relation, demonstrating that the abstract proof alone does not extend to four.

## Weaker row-margin-only two-group census

Separately consider only the36 row margins and each group's local Gram upper bounds/within-group column caps. With two nominated exceptional groups, all their nonshared coordinates must be balanced, while count deviations on shared coordinates must cancel. Do not use the full summed-Gram marginals in this weaker census. It may contain many configurations that the stronger theorem rules out.

Enumerate all actual190 support-group pairs. The original proposed assertion that intersections were only0 or3 is explicitly tested and refuted by a raw pair witness; actual sizes are used throughout. Index the31,110 immutable locally valid triples by six-bit balanced-position masks. Save the exact domain for each of64 required-balanced masks, including balanced and genuinely unbalanced counts. For each actual pair, map its shared coordinates to positions on both sides, histogram the exact three-fibre deviations, and count opposite-signature pairings. Record both the all-balanced combinations and the pairs with both groups genuinely unbalanced, without enumerating a huge Cartesian product or asserting that they satisfy intergroup Gram/caps.

Column permutations inside a support group are normalized only by increasing indices of three distinct90-word choices, exactly as in the prior audited census. No first-coordinate affine normalization is imposed on unbalanced triples. The complete survivor indices refer to that immutable catalogue; historical VERIFIED labels are not treated as a new independent review of this producer.

Controls: literal balanced and unbalanced local triples; exact cancellation/uncancelled deviation vectors; all triples of distinct3-bit cube vertices; a duplicate-column failed minor and a four-corner dependency. If a row-margin-compatible unbalanced pair exists, save its two raw local triples and an explicit summed-Gram marginal witness that it violates. This is a countercontrol distinguishing the two scopes, not a full-factor construction.

Outputs contain source/command/environment/input hashes, all64 filtered catalogues, all190 pair records with profile counts and witnesses, all twelve marginal matrices/minor certificates, the exact support-intersection refutation, and summary. No native calls, ledger updates or automatic mathematical promotion occur.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_exception_groups.py --out acceleration/results/20260930_hadamard_exception_groups
```
