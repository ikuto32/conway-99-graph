# Independent fixed-core decoded-object checker

The checker binds the exact four-instance encoding audit and its complete
raw input inventory. It reuses the frozen independently authored base factor
decoder and integer Gram, margin, column-cap, mixed-cap and partial99 checks.
It imports no producer. The declared base source hash and all transitive
independent checker bindings are checked before use.

For an actual SAT output it checks every one of the 110,904 signed IDs,
agreement with native DIMACS v-lines, all 518,184 actual clauses, every one
of the 132 matching and 144 permutation values, and literal equality of the
decoded cubic core with the selected raw core. It independently reconstructs
the factor and partial99 graph, then optionally compares the supplied raw
producer object. The factor is not a completed target graph: residual D is
still wholly absent.

Calibration uses the independently checked SRG243 fixture as a nonempty
generic positive for the same raw factor and partial-graph path. Rook9 is a
separate smaller positive with empty outside set. Corrupted binary entries,
canonical C0, factors and core values must fail. Four full-size synthetic
native/CNF codec cases include the exact research fixing units but use
synthetic base clauses. These are explicitly not research SAT witnesses.
The native parser, assignment and actual-clause rejection paths are exercised
with missing/duplicate IDs, false units, bad headers and missing clauses.

```
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_connected_fixed_core_object.py calibrate --out acceleration/results/20260930_independent_review/connected_fixed_core_object_calibration
```

Actual SAT checking (replace INDEX and RUN with one exact saved case):

```
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_connected_fixed_core_object.py sat --core-index INDEX --assignment RUN/main/parsed_model.json --native-output RUN/main/solver.stdout.log --decoded RUN/main/decoded_factor.json --out AUDIT_OUTPUT
```
