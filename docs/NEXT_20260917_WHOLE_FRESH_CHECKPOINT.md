# Whole fresh v2 checkpoint indexing

This indexing addendum does not change the cohort, ranking, shortlist, or LP protocol. `acceleration/build_fresh_whole_v2_checkpoint.py` is a separate copy of the frozen historical fresh-star checkpoint builder, narrowed to the actual whole-family v2 statuses and union16 selection. It preserves the existing scientific indexing checks and adds whole-family original native ID and multiple-cycle metadata checks. The old builder remains unchanged and hash-bound as provenance.

The prior checkpoint is `acceleration/results/20260917_same_star_round/checkpoint.json`, SHA256 `4319fe3c2b4d33fc24aea779bc70159689d7d688090930ac723cb43da40933a0`. Every referenced hash from that checkpoint is rechecked and retained. The builder performs no solver call, domain enumeration, or scientific replay. Its indexing status is not independent mathematical verification.

Before creating an output, the builder requires the actual independent whole-shortlist scope report (`INDEPENDENT_WHOLE_FRESH_STAR_SHORTLIST_AUDIT_PASS`) and raw arithmetic report (`THIRD_PATH_EXACT_FIXED_K_STAR_REVIEW_PASS`). The scope report must bind the exact summary, raw report, and explicitly pinned checker source. All16 raw exact intervals must agree with the selected producer records and the scope report; the chosen best must agree too. Scope/import flags, original mask identity, independently complete original84 domains, exact certificate/integer replay receipts, and all prior source bindings are checked separately. This deliberately supports the fully reviewed16-pass continuation; partial evaluations stay in their execution records and require a separately scoped continuation rather than passing this gate.

Adoption still requires an independently audited positive lower bound and upper bound strictly below the parent's exact incumbent lower bound, followed by the strict audited edge warm-start chain. Parent comparison is recomputed without overwriting the experiment's own baseline-relative claim. If no such fully checked improvement exists, the incumbent remains unchanged. Pending work remains explicit. No CP round, target witness, general nonexistence proof, or exhaustive coverage is inferred.

Producer controls are in `acceleration/results/20260917_whole_fresh_v2_balanced/checkpoint_adapter_controls.json` (37 corruption rejections, historical exact-domain/warm/adoption positives plus new whole-metadata positive) and `checkpoint_review_gate_controls.json` (18 corruption rejections and one positive). The latter deliberately uses in-memory association fixtures and bypasses filesystem hashes; it is not evidence of independent scientific verification. The first sandboxed controls invocation could not read the historical `.deps/pysat/__init__.py` hash; the same locked command passed with workspace dependency read access. No checkpoint or solver output was produced by the controls.

Builder SHA256: `fdc321d788d4fb6fccd82580112036001c6506c4a14dca0bd8b048a4a0a20536`. Scope-checker source pin at preparation: `b153d8305ae73516df4f3b5515536dd202c067fc412f38fc0788673dfad50fed`; the actual independent report must bind that source before execution. The parent agent supplies the final genuine scope/raw report paths and a fresh checkpoint output. Run with the existing locked environment, using the following arguments; add `--validate-only` to perform all checks without creating the checkpoint:

```text
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/build_fresh_whole_v2_checkpoint.py
  --previous acceleration/results/20260917_same_star_round/checkpoint.json
  --previous-sha256 4319fe3c2b4d33fc24aea779bc70159689d7d688090930ac723cb43da40933a0
  --evaluation acceleration/results/20260917_whole_fresh_v2_balanced/shortlist/summary.json
  --scope-review ACTUAL_INDEPENDENT_SCOPE_REPORT
  --scope-auditor acceleration/audit_20260917_whole16_scope.py
  --scope-auditor-sha256 b153d8305ae73516df4f3b5515536dd202c067fc412f38fc0788673dfad50fed
  --exact-review ACTUAL_INDEPENDENT_RAW_REPORT
  --out FRESH_CHECKPOINT_OUTPUT
```

Set `UV_PROJECT_ENVIRONMENT=build/research-venv` before running. This document records readiness only; actual indexing output and process state must be read from the eventual command receipt. Overall search coverage: UNKNOWN; no validated denominator.
