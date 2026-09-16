# Four alternative overlap assignments and their exact exclusions

Four additional complete overlap assignments were constructed at the
saved sharp integral compression C. Each has 168 overlap edges, and each
is distinct from the original and its predecessors under all 128
within-group root-label flips. All four 357-edge partial graphs pass the
independent rooted-skeleton, quota, compression-total, degree, and 4,851
pair-cap checks.

All four nevertheless have exact independently checked weighted-capacity
contradictions for real disjoint-edge variables in [0,1], without assuming
any disjoint compression block total. Thus these four prescribed overlap
assignments cannot complete. This does not exclude all assignments at C,
all sharp compressions, or E0=0.

| Candidate | Generation seconds | Prior sign images excluded | Original cut | Minimum over its 128 sign images | Exact contradiction RHS |
|---|---:|---:|---:|---:|---:|
| r0 | 3.594 | 128 | 10940 | 8654 | -819 |
| r1 | 3.219 | 256 | 10661 | 9265 | -793 |
| r2 | 3.735 | 384 | 11379 | 9015 | -796 |
| r3 | 3.547 | 512 | 10842 | 9088 | -797 |

The original cut and its sign orbit reject none of these candidates. The
new certificates therefore add rejection power. Each independently
checked certificate combines quota equalities, pair-cap inequalities,
and edge upper bounds to obtain a nonnegative left side bounded by the
negative RHS shown above.

The first primal LP runs reported INFEASIBLE for r0 and r3. They reported
GLOP status 4, ABNORMAL, for r1 and r2; these are numerical/execution
failures and establish no mathematical conclusion. No unchanged primal
run was retried. Separate bounded dual problems produced exact integer
certificates for all four, resolving the feasibility question for these
fixed assignments independently of those primal statuses.

Each construction used a copy of the original overlap model, one worker,
and a 45-second limit. No-good constraints excluded each complete
168-edge assignment in the prior sign orbits. Each dual had a 30-second
limit and finished within that limit. All original sealed proof artifacts
and the central ledger remain unchanged.

Candidate and proof files use
`scratch_next_overlap_alternatives_r{0,1,2,3}.json` and
`scratch_next_overlap_alternatives_r{0,1,2,3}_farkas.json`.
The independent proof checker is
`scratch_next_overlap_alternatives_farkas_audit.py`; its result for each
candidate has status `INDEPENDENT_ALTERNATIVE_INTEGER_FARKAS_AUDIT_PASS`.
All source hashes, initial LP outcomes, and final audit references are in
`scratch_next_overlap_alternatives_summary.json`.

Reassemble the summary using only saved artifacts:

```text
& 'C:/Users/ikuto/.local/bin/python3.12.exe' -B scratch_next_overlap_alternatives_summary.py
```

Distinction here is under the specified sign subgroup. No claim of
nonisomorphism under every vertex permutation is made. No 99-vertex
graph or submission file was produced.
