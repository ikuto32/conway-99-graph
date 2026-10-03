# Wave23: remaining54 six-exception representative formulas

Freeze the complete55 surviving orbit minima using the independently checked six-fibre normalization gate `ea4289a741ed19231d88fec5d917428b3ffc2c497a116268c90344448b665109` and independent AC gate `82be6d4389596959365d5551694f3e1361d0bc855405f2647a682784be1f34ba`. Reconcile the raw984 profiles, every orbit member, and the independently reconstructed AC classifications. Choose the lexicographically smallest profile ID in each surviving orbit; preserve all55 records and their full initial domain references.

Remove only `rank4_00_profile_0000` from the new build list because its literal formula has already been built and attempted. This is execution bookkeeping, not an assumption that its native result is an independently checked exclusion. Do not rerun it and do not add a proof claim. Keep its original formula and native receipts untouched. The remaining54 IDs are frozen in lexicographic order, with exact raw profile hashes, groups, six initial domain hashes/sizes and expected selector/formula dimensions.

The selection source performs exact coverage/uniqueness/minimum checks and rejects deliberately duplicated orbit members, incorrect minima and altered classification covariance. It uses no unreviewed orbit diagnostic. No solver call, ledger or publication mutation is performed. This inventory belongs to wave23, outside wave22's frozen cutoff.

After selection, a new bounded serial build wrapper invokes the unchanged `theory_20260930_hadamard_six_profile_cnf.py` once for each selected ID. Keep all initial exceptional local options and all150 options in each of14 balanced groups; do not substitute AC-pruned options. Record attempted, completed, failed and pending builds separately. Each output retains raw CNF/model/scope and its exact gzip model recovery. Future independent clause/object gates are required before native research.

Build allocation:180 actual wall seconds per invocation, checked between cases; require at least5 seconds before starting the next small child build, and pass the remaining allocation as its outer timeout. Save each completed case's immutable checkpoint and a final summary. On failure or timeout preserve all partial files and stop, without an automatic retry. An explicit resume starts a new output directory and authenticates a prior checkpoint SHA, immutable selection/source hashes and every completed artifact, then skips the completed prefix. Prior failures remain retained and are disclosed if the pending case is explicitly resumed in a new directory. No formula or prior output is overwritten.

Require at least3GiB host disk free before the batch and each build, given the expected raw models plus formulas. The selected population and resulting dimensions are measured rather than assumed. Controls and gzip identities are producer engineering checks, not independent mathematical approval.

Locked selection command:
```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/select_20260930_hadamard_six_remaining_profiles.py --out acceleration/results/20260930_hadamard_six_remaining_selection
```
The separately frozen batch wrapper records its exact command and actual selection hash before execution.
