# 2026-09-17 user-requested research stop

Research stopped at the user's request to preserve token resources. Do not start
another experiment until the user explicitly requests continuation. This is not
a mathematical resolution or an external research blocker.

## Result and verification state

The unrestricted target `srg(99,14,1,2)` remains **UNKNOWN**. No independently
validated target graph or general nonexistence proof exists in this repository.
External review of a target resolution is not applicable. Overall search
coverage: UNKNOWN; no validated denominator.

The newest independently checked mathematical result is
`C-PARTIAL-K-SIX-COORDINATE-EXCLUSION`, revision 1: the prescribed family with
132 fixed K edges, the fixed root scaffold and recorded absences is excluded.
Only 360 freed coordinate edges and 1,680 disjoint-support edges may vary.
The exact support lower bound is `906048/1048576 = 14157/16384 > 0`.
No automorphism is assumed. This is a conditional exclusion only.

Independent raw-neighborhood checking covered all 712,721 retained choices and
84 maxima for each of six frozen coefficient attempts. Four attempts had
positive bounds; two did not. They are attempts on one conditional family,
not six graph instances or a target-wide coverage measure.

- Exact audit: `acceleration/results/20260917_independent_review/six_gpu_support.json`
  (SHA256 `0814b6d5e660b876247cf83dc4e37cfaa0e86ec1d1b05b59ab8b6fd63ebbcf80`).
- Scope/revision binding: `acceleration/results/20260917_independent_review/six_exclusion_claim_binding.json`
  (SHA256 `3221d8c86c6bee1aadf801316541de992ba96650c777466bc32cd1fff010c7f0`).
- Previous frozen milestone: `acceleration/results/20260917_four_coordinate_exclusion_checkpoint.json`
  (SHA256 `9f6bf0bbc1e7bbb44216a6cbe54feb2971e298e969a57aba0738b04b307fc64c`).

Read the root `CLAIMS.yaml` for exact dependencies, scopes, availability and
verification records. The stop checkpoint and ledger validation report supply
programmatically derived current counts. Older checkpoints remain unchanged.

## Execution and unfinished work

The six-coordinate GPU run completed all checkpoints and all six exact-bound
attempts. Its CPU counterpart ended in HiGHS/IPX `SolveError` after 666.407
seconds; it did not reach its 5,400-second cap. Returned zero weights gave a
zero bound and no feasibility/exclusion result. Both outcomes are preserved.

The next eight-coordinate domain pilot was interrupted at the user's stop.
Its completed center files and immutable checkpoints are retained as
**CANDIDATE partial evidence**, not complete coverage or an exclusion. Consult
its user-stop receipt for exact counts, stopped process and inventory. A saved
partial domain is not a recursive-stack restart checkpoint.

The machine process observation is
`acceleration/results/20260917_resume/user_stop_process_observation.json`.
It records an actual observation, not a conclusion inferred from old PIDs.
No research process was observed; unrelated applications and editor language
servers were left alone. Subsequent save/validation/publication utilities do
not resume research.

The original rook-nine checker source was lost in a source-name collision.
Preserve that failure. The current verified conditional encoding uses a fresh,
separately named independent checker and does not rely on the missing source.
Neither universal rook containment nor single-rook impossibility was proved.

## Restart procedure — only after a new user instruction

1. Read this document, `ACTIVE_RESEARCH.md`, the root ledger and the stop
   checkpoint `acceleration/results/20260917_user_requested_stop.json`.
   Confirm Git HEAD/branch and the current remote state before continuing.
   Work remains on `codex/fresh-star-audit-20260917`; PR2 is the review thread.
   PR1 was externally merged; do not automatically merge any claimed result.
2. Set up the pinned environment from repository root:

   ```powershell
   $env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
   uv sync --locked --cache-dir .uv-cache-20260917
   uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/validate_claims.py --hashes available
   ```

   Missing local artifacts require documented recovery from exact compressed
   or byte-part companions; see `docs/local-artifacts.json` and
   `docs/REPLAY_20260917_COMPRESSED_AND_CHUNKED.md`. Hashes alone do not provide
   artifact access. Keep the existing working directory and local artifacts.
3. Read `docs/NEXT_20260917_EIGHT_COORDINATE_DOMAIN_PILOT.md` and its stop
   receipt. The strongest next pending computational step is completing and
   independently auditing that broader domain family. Freeze a continuation
   protocol first. The current producer refuses existing output paths and
   has no exact recursive-stack resume. A fresh full run, if chosen, uses:

   ```powershell
   uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260917_partial_eight_matchings.py --out acceleration/results/20260917_partial_eight_matchings_restart01
   ```

   Do not execute merely while editing this documentation. A future
   checkpoint-aware continuation may reuse independently checked completed
   centers, but must preserve the interrupted run and explicitly establish
   completeness. Do not build an LP before the domain audit gate passes.
4. Preserve the independent discovery/checking separation. Unique new source
   and report filenames are required to avoid another checker collision.
   Do not modify `PROMPT.md`, the historical external ledger or the user's
   preexisting `tools/drat-trim` changes.

The previous report is `docs/RESEARCH_20260917_EIGHTH_WAVE.md`. This stop record
supersedes its prospective CPU/GPU execution instructions, while preserving
its historical claim and checkpoint contents.
