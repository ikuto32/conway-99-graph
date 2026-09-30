# Compact equivalent column-cap encoding for the 25-row projection

Freeze this new experiment before construction. Do not modify the original
25-row CNF, model, scope, proof logs, gates, or native pilot. This changes
only the encoding, not the declared finite mathematical problem.

Let x_d be the selected C2 entry in column d. Each C1 column has exactly
two ones. Its within-fibre Gram is 9I-M+J: paired rows never occur together,
and each nonpaired row pair occurs together exactly once. Therefore the
60 C1 columns are precisely the 60 distinct nonmatching two-subsets of
the twelve coordinates. In particular, distinct C1 columns overlap in
zero or one row. Canonical C0 columns have the same property.

For distinct B columns d,e let k be their fixed C0 overlap, and q their
C1 overlap. The full selected-25-row overlap is k+q+x_d*x_e. If k=0, the
required upper bound 2 follows from q<=1 and binary x. If k=1, the upper
bound is equivalent, under q<=1, to forbidding the simultaneous occurrence
of x_d=x_e=1 and any common C1 row r. For each such r this is exactly:

`not C1[r,d] or not C1[r,e] or not x_d or not x_e`.

This proof uses the retained C1 column margins and exact within-C1 Gram;
it is not an unconditional replacement for arbitrary Boolean arrays.
There are exactly 540 unordered C0-intersecting column pairs, because
each of twelve C0 vertices lies in ten columns and each pair of distinct
columns has at most one common endpoint: 12*choose(10,2)=540.

Retain the original CNF body verbatim through its final component-capacity
counter, including all primary variables, row-Gram ANDs, margins, Gram
equations, and component caps. Remove exactly the suffix consisting of
column-overlap ANDs and counters. Append the four-negative-literal clauses
for all 540 pairs and all twelve C1 rows. A clause with any fixed-zero
entry is tautological and omitted; preserve every omission and its exact
zero-coordinate reason in the recipe. Do not silently deduplicate clauses.

The new model keeps all retained variable IDs and counter metadata. Save
the exact old-body cutoff clause and maximum retained variable, every
candidate tuple, every emitted clause, and every omission. The independent
gate must establish complete byte identity of the retained prefix and
complete coverage of the new clause universe, in addition to the exact
mathematical equivalence above. The original target implication and raw
25-row scope stay unchanged. No abstract-factor or target-wide claim is
broadened.

Before construction, exhaust small exact pair-set controls comparing the
original overlap inequality and the four-literal replacement under the
distinct-two-subset premise. Include a deliberate repeated-column control
showing why that premise cannot be dropped. Limit deterministic build to
120 seconds and 8 GiB; make no solver call. Save gzip reconstruction data.
No performance claim follows from file size or from unmatched pilot runs.
A later native pilot requires its own new encoding/object gates and root
launch authorization; the old gates alone do not authorize solving this file.

Command, with `UV_PROJECT_ENVIRONMENT=build/research-venv`:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_one_c2_compact.py --out acceleration/results/20260930_triangle_one_c2_compact`
