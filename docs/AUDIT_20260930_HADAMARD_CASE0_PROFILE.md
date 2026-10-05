# Independent case0 full-Gram encoding and object audit

This audit fixes the raw six-prism Hadamard support and the literal case0 profile: exceptional groups 0,7,9,19 with signs 1,-1,-1,1 at coordinates 2,4, deviations (-1,0,1) and (1,0,-1). It asserts no orbit coverage, balance WLOG, target automorphism, or residual graph.

The checker enumerates all 117480 unordered triples of the 90 balanced six-coordinate colour words. Literal within-triple column intersections and row-pair Gram upper bounds retain exactly 31110 local triples. Filtering the recorded count profile retains all 48 initial options at each exceptional group; no 36-option arc-consistent subset is substituted. The remaining 16 groups use all 150 balanced triples. Sorting exceptional colour words or normalizing the first coordinate in a balanced triple merely permutes its three identical-support columns. Duplicates cannot occur under within-triple column caps. Relabelling these columns preserves the Gram and optional completion after the corresponding residual relabelling.

For each of 540 nonmatched coordinate/fibre cells, the checker calculates a selected option's contribution by literal membership of the two full row labels in each of its three column sets. The values are 0,1,2. Exact one-hot constraints and two bidirectional OR channels q1=[c>=1], q2=[c>=2] give c=q1+q2. The complete subset clauses enforce the sum of ten flags to be 1 for equal fibres or 2 for different fibres. Empty OR inputs force false. The prefix one-hot recurrence and both OR directions give unique auxiliary extensions; complete truth controls test this including contribution two and empty ORs.

These 540 equations give the remaining off-diagonal Gram entries. Diagonals are 10 from the 36 independently added profile margins. Distinct fibres at one coordinate have zero overlap since each column selects only one fibre at that coordinate. Matched coordinates have zero overlap because every fixed support contains one endpoint of each matching edge. Symmetry supplies reverse entries. Thus all 1296 Gram entries are accounted for, with every 187408 actual clause and header reconstructed independently.

Cross-group column caps are omitted from the formula and cannot be silently imposed by the object checker. A SAT object must pass every actual clause, every native/JSON assignment entry, all raw Gram entries, margins, fixed support, profiles, and within-triple caps. All 1770 column intersections and 2160 mixed quantities are reported separately. First-fibre columns are independently checked to form all 60 nonmatching pairs before canonicalization. Residual D remains absent.

The implementation imports only frozen independently authored balanced-v2 helpers and its independent native/JSON codec. Shared code includes elementary clause patterns, literal integer raw-factor checks, and canonicalization; no producer module is imported. New controls cover all ten-bit exact counts, weighted channels, full-size synthetic native/JSON/clause handling, genuine SRG243 incidence data and its reordered version, and malformed domain, clause, assignment and factor cases. The SRG243 control is not a Conway99 witness; no research positive is assumed.

Run in the unchanged locked environment with `UV_PROJECT_ENVIRONMENT=build/research-venv`:

```
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_case0_profile.py audit --out acceleration/results/20260930_independent_review/hadamard_case0_profile_cnf
```

Use `calibrate` with explicit `--encoding-gate` and `--encoding-gate-sha256` for the object gate. Use `sat` with those same arguments plus `--assignment`, `--native-output`, optional `--decoded`, and a fresh `--out`. No command in this checker launches a solver.
