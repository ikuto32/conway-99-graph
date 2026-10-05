# Native pilot for the complete six-prism column universe

Question: does the fixed identity-cross, standard-matching six-prism Gram
admit any binary36-by-60 factor? The exact formula has245880 variables and
874800 clauses, with all96 supports per canonical C0 column. No five-matching
cell-pattern restriction, complement pairing or target automorphism is
assumed. This fixed-core experiment is not unrestricted target coverage.
Outside-column overlap bounds and residual D are omitted.

Before research, authenticate the raw CNF/model, native/checker executables,
prior native CLI and ext4 calibration, independent complete encoding gate
and independent raw-object calibration gate. Recheck all bound input hashes.
The source and this protocol are frozen before preflight. Root alone launches
the research mode after it passes. Preflight launches no solver.

One ASCII-proof-enabled CaDiCaL1.9.5 attempt has300 native seconds,
1000000 configured conflicts,4 GiB address-space limit,10 GiB output-file
cap, five-second kill grace and320-second outer guard. Require21 GiB host
and11 GiB ext4 free space. Preserve the unique ext4 proof location, complete
or partial local copy, exact copy/hash receipts and raw stdout/stderr. Native
defaults are used without inventing a random seed. No automatic retry.

On SAT preserve all245880 signed IDs, then call the frozen producer API
`decode(model, assignment)` for explicitly CANDIDATE output. The raw decoded
field is `factor`, a36-by-60 array, with `selected_choice_ids` and
`target_graph:false`. Producer exact checks and all1770 column-overlap
diagnostics are saved, but cannot approve a discovery. The independent
checker must validate the complete raw assignment, native stdout, every CNF
clause and all raw factor equalities. Omitted column caps are reported
separately; a violation prevents target completion but does not invalidate
the abstract factor SAT result. A factor passing caps still needs residual D.

On UNSAT retain the full proof for independent replay. Only the exact
encoding plus a complete checked proof can exclude this fixed core's factor
family. On UNKNOWN preserve limits and partial output without an exclusion
claim. Do not infer performance comparisons from one attempt.

Locked command from the repository root, with
`UV_PROJECT_ENVIRONMENT=build/research-venv`:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_prism_all_columns.py --preflight --out NEW_DIRECTORY --encoding-gate acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json --encoding-gate-sha256 07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3 --object-gate OBJECT_REPORT --object-gate-sha256 EXACT_OBJECT_REPORT_SHA
```

After preflight, root may replace `--preflight` with `--research` and provide
a fresh output directory. The old runs and their evidence remain unchanged.
