# Exact uniform-mixture Gram diagnostic

Question: for each of the frozen 792 canonical exact-eight literal count tables,
does choosing the uniform probability distribution on each group's complete
initial local-triple domain reproduce the prescribed integer Gram matrix?

Selection is all 792 records in the authenticated campaign manifest, in manifest
order. No profile is removed because a separate SAT proof already excludes it.
The raw local catalogue and domain inventory are previously independently checked.
This diagnostic reconstructs the count signatures directly from those raw inputs.

Use Python 3.12 and the existing uv.lock, with integer sums and a per-profile
common denominator equal to the LCM of all twenty domain sizes. Success means
every scaled Gram entry equals that denominator times the exact target. Failure
means at least one differing integer entry; preserve its coordinates and values.
No floating-point acceptance threshold, randomization, native solver or new
exclusion. A successful rational convex mixture need not select one option per
group, even when the corresponding integral instance has been proved UNSAT.

One allocation: at most 120 seconds of monitored calculation, checked between
catalogue classes and profiles. No implicit retry. Preserve source/input hashes,
actual command, source commit, versions, controls, class sums, results and failure
record. Checkpoints every 64 profiles permit diagnosis of an interrupted run;
resumption requires a separately recorded invocation, not silent appending.

Controls before the campaign: use actual binary columns from the known-valid
243-vertex fixture, with two identical choices per group, and check exact means.
Reject changed targets and invalid domain denominators. Also test the complete
balanced 150-choice domains on the fixed support, which have the exact prescribed
Gram in uniform expectation. This is a valid relaxation fixture, not a valid
Conway-99 graph. All research conclusions remain CANDIDATE until independently
checked by a separate literal-column implementation.
