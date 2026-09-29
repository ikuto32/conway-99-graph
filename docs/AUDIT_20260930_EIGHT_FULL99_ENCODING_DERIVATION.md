# Independent full99 encoding equivalence argument

This audit concerns the exact frozen189edge root scaffold,120 additional
fixed outer edges,2,160 variable outer pairs and all prescribed absences.
It supplies no exhaustive coverage of the unrestricted target.

For each unordered unknown pair the model has one Boolean edge variable.
The independently reconstructed known/free matrix and variable bijection
therefore decode every assignment to exactly one symmetric binary99matrix
with zero diagonal and precisely these prescribed entries.

For each row u the direct polynomial is `Σ_v A_uv=14`. For each unordered
pair u,v the direct polynomial is `A_uv+Σ_w A_uw A_vw≤2`. The checker derives
every constant, input edge, and product from this raw matrix. Fixed0/1
products are evaluated exactly; each remaining product gets a fresh Boolean
variable with exact AND equivalence. No numerical arithmetic is used.

The checker obtains each gate's CNF independently by enumerating its Boolean
truth relation and deriving every prime implicate, rather than importing or
copying the producer's clause-emission templates. It compares the complete
raw clause segment, including multiplicity. A missing reverse implication,
wrong literal sign, extra clause, changed product, wrong constant or input,
stale threshold reference, or unused variable is rejected.

For inputs `x_1,...,x_n`, let `T(i,j)` mean that at least j of the first i
inputs are true. Its boundary values are `T(i,0)=true` and `T(i,j)=false`
when j>i. Splitting according to x_i yields the exact identity

`T(i,j) = T(i-1,j) OR (x_i AND T(i-1,j-1))`.

The required thresholds through k+1 only refer to smaller prefixes and to
the same or smaller threshold, so truncation above k+1 loses no dependency.
Induction over i proves every saved state is exactly its stated threshold.
Constant and input aliases are checked as Boolean functions. Every other
state has a new output variable whose full truth equivalence is enforced.
Thus each input assignment has exactly one extension to all helper states.
Asserting T(n,k) and forbidding T(n,k+1) expresses exact k; forbidding the
latter alone expresses at most k. Empty rows, k=0 and k=n follow from the
same explicit boundaries. A cap exceeding its input count is vacuous.

The direct degrees and all unordered caps imply the full SRG identity.
Write c_uv for the common-neighbor count. Degree14 gives exactly693edges
and `Σ_{u<v} c_uv = Σ_w C(deg(w),2)=99*C(14,2)=9009`. Consequently

`Σ_{u<v}(c_uv+A_uv) = 9009+693=9702=2*C(99,2)`.

All4,851 summands are at most2 and their sum equals the sum of those upper
bounds. Every cap is therefore equality. This gives common counts1on edges
and2on nonedges. The diagonal of A² is degree14, exactly the diagonal of
`12I-A+2J`. Thus `A²=12I-A+2J` entrywise over the integers. Conversely that
identity gives degree14 and each cap equality. Hence this CNF is satisfiable
exactly when a target graph exists **within this fixed family**.

A later SAT assignment must still be checked against every raw clause and
decoded through a separate full99integer validator. A later UNSAT result
requires the complete exact proof trace and independent replay; even then
it excludes only this recorded family. No graph automorphism is assumed.
