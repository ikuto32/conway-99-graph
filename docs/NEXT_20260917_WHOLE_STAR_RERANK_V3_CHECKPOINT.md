# V3 reranking shortlist: checkpoint preparation

`acceleration/build_whole_star_rerank_v3_checkpoint.py` is a separately named indexing adapter. The prior checkpoint is `acceleration/results/20260917_whole_fresh_v2_checkpoint.json`, SHA256 `5ad8fd58795a8bf4a37468d8f45b9aad031d41deb22882e53d26703fd200e39d`. The builder binds and retains every prior referenced artifact; the earlier builders and checkpoints remain unchanged.

It requires the actual new scope report `INDEPENDENT_WHOLE_STAR_RERANK_V3_SHORTLIST_AUDIT_PASS` and the separate raw report `THIRD_PATH_EXACT_FIXED_K_STAR_REVIEW_PASS`. The scope report must bind its checker source, the exact evaluation summary and the raw report. All16 raw rational intervals must match the producer records; independently reviewed best selection must match too. No checkpoint can be produced from preparation status or agreement among agents.

The model-reuse scope remains explicit: an earlier independent128-model reconstruction plus a complete payload-identity audit, with no claim of new128-model reconstruction. The parent checkpoint's16 LP-tested records must exactly equal the excluded ID list. The new shortlist is independently rebuilt from112 eligible cases using the frozen union rule;128 reranked cases are not counted as new candidates. All original-domain identity, independent completion, exact LP audit and integer replay checks are retained. Limits remain30seconds LP and60seconds independent pair audit.

The incumbent changes only for a positive independently checked fixed-K bound with exact upper below the parent's incumbent exact lower, and a separately strict-audited edge warm start. The historical parent-relative adoption and pending-state rules are unchanged. This indexes a fully reviewed16-case result; an incomplete or nonpositive-case wave remains in its run/failure records and cannot pass this particular final gate. It makes no target-wide or CP-completion claim. Overall search coverage: UNKNOWN; no validated denominator.

Builder SHA256: `3c7538cc9764275ca7555912dd12ee0006917b8c2b25d5bd4c947af2aa43fd36`.

Producer engineering checks under `acceleration/results/20260917_whole_star_rerank_v3/`:

- `checkpoint_adapter_controls.json`:40 corruption checks rejected, with existing original-domain, exact warm-state and parent-adoption positive controls plus honest whole reranking metadata.
- `checkpoint_review_gate_controls_v2.json`:18 corruption checks rejected and one positive synthetic review-gate control. These in-memory fixtures deliberately bypass filesystem hashes and are not scientific artifacts.
- `checkpoint_control_correction.json`:the first selection-helper control exposed that excluded calibration scores were not tested for finiteness. The corrected helper checks all128 raw score fields. The pre-fix source and old gate-control report are preserved; no scientific run or checkpoint was produced by the failed control.

Use the locked environment with `UV_PROJECT_ENVIRONMENT=build/research-venv`. After the genuine final reports exist, run the separate builder with `--previous` and `--previous-sha256` above, `--evaluation acceleration/results/20260917_whole_star_rerank_v3/shortlist/summary.json`, the actual `--scope-review`, `--scope-auditor`, `--scope-auditor-sha256`, `--exact-review`, and a fresh `--out`. Add `--validate-only` to check all bindings and semantics without creating an output. Exact final command, checker pin and outcome belong in the eventual command receipt. This preparation document does not assert a live indexing or solver process.
