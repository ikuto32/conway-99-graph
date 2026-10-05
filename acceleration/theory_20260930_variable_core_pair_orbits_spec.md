# Ordered matching-pair orbit normalization, version 1

Question: can the original arbitrary-core necessary factor formula be
restricted by relabelling to the 3,580 ordered (M1,M2) representatives in the
already independently audited matching-pair census? P remains an arbitrary
permutation, and all incidence variables remain free. No target automorphism
or component restriction is assumed.

Use the frozen 10,395 first-stage transports for M1 as a premise. If h sends
M1 to first representative R_s while preserving M0, it sends the arbitrary
M2 to another matching M2'. For each of the eleven R_s, traverse the already
audited stabilizer generators to save a permutation k for every one of the
10,395 M2' matchings. Require k to fix M0 and R_s and send M2' to its saved
second-stage representative. Then k composed with h sends the original
ordered pair to that representative. The required second-stage population is
11*10,395=114,345 transport records, organized in eleven stage files.

Completeness uses every first-stage record and every second-stage matching
record. Each h permutes the entire matching universe bijectively, so this
composition covers all 10,395^2=108,056,025 labelled ordered pairs without
materializing them. Explicit composed controls exercise one deterministic M2
for each of the 10,395 first-stage records; these controls alone are sampled
pair tests and are not the coverage argument. Preserve that distinction.
Every saved k is checked against the three relevant raw matching vectors
and all sixty induced canonical C0 column labels. Exact first/second orbit
memberships and representative order must agree with the archived census.

Apply the resulting coordinate map simultaneously to all three fibres and
relabel each canonical C0 column {a,b} as {k(h(a)),k(h(b))}. This preserves
Gram equations, row and fibre-column margins, mixed caps and distinct-column
caps by the previously independently checked general index-substitution
argument. P is conjugated bijectively and remains unrestricted. Prefix
auxiliaries are regenerated, not asserted to admit literal CNF permutations.

Append selectors 110905,...,114484 to the original 110904-variable,
518160-clause arbitrary-core base. Add one at-least-one selector clause and,
for each representative pair, twelve implications to its six positive M1
and six positive M2 matching edges. Base matching degree constraints force
the other edges false. Two different ordered representative pairs cannot
both be selected, so no extra at-most-one clauses are necessary. The exact
expected result is 114484 variables and 561121 clauses (42961 added clauses).
This construction is equisatisfiable after relabelling, not equal as a set of
primary assignments. Preserve the entire base body and all older extensions.

Predeclared resource limits: 120 seconds, 8 GiB working set, zero solver calls,
deterministic exact arithmetic. Stop without coverage promotion if any stage
is incomplete. Preserve raw transports, generator references, matching IDs,
the exact extension, source and input hashes. Package large artifacts with
lossless gzip parts below 10 MiB. Calibrate transport composition and selector
semantics with positive and deliberately corrupted finite controls.

Status remains CANDIDATE until a separate reviewer checks the exact coverage
and appended bytes. The target implication still requires the prior universal
triangle/core normalization. A SAT object is only a necessary factor and
partial graph; no D or complete99 graph is encoded. No solver is authorized
by this build, and no numerical threshold or heuristic selection is used.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_variable_core_pair_orbits.py --out acceleration/results/20260930_variable_core_pair_orbits
```
