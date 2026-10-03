# Twenty-fourth wave: seven-group exclusion and exact count relaxations

The verified lower bound is eight unbalanced groups, conditional on the literal six-prism Hadamard support, its prescribed integer Gram and all outside-column overlap caps. This wave also excludes one eight-count profile and its six explicit global fibre images. It does not exclude the entire support or resolve Conway-99. No target automorphism is assumed.

Use the existing checkout and pinned environment. All replay outputs and receipts must have fresh paths:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twentythird_raw_artifacts.py --receipt build/wave23-recovery.json
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twentyfourth_raw_artifacts.py --manifest acceleration/results/20260930_twentyfourth_raw_recovery/manifest.json --manifest-sha256 2311cebb8617c95c3ae3a4225def8ce2dce8992ae9621cdcfd8cf0684806c3c8 --receipt build/wave24-recovery.json
```

The second helper restores the 443 originals in the hash-bound [manifest](../acceleration/results/20260930_twentyfourth_raw_recovery/manifest.json), totaling 3,548,174,273 bytes from 484 gzip streams. It restores missing files at their recorded paths, verifies existing ones, and refuses to overwrite different bytes. Use `--destination-dir build/fresh-wave24-recovery` to create a separate tree, or `--verify-only` to check streams without creating originals. The [development receipt](../acceleration/results/20260930_resume/twentyfourth_raw_recovery.json) records all 443 originals restored into a fresh tree. Recovery checks identity, not mathematical validity. Earlier dependencies retain their own historical recovery/build instructions; completed records are never rewritten to match a new environment.

The [215-proof package](../acceleration/results/20260930_hadamard_seven_profile_proof_package/package_manifest.json), SHA256 `05a524f429c2750e6cb8097a0f9235dddf9ad8a5c22176f411871bd977a78d4e`, reconstructs 577,482,170 raw bytes from 223 gzip parts totaling 90,689,391 bytes. Concatenate decompressed chunks in manifest order. A separate [transport audit](../acceleration/results/20260930_independent_review/hadamard_twohundredfifteen_proof_transport/summary.json) checked every byte against the independently replayed originals and rejected sixteen corruptions. The separate seven-profile pilot contributes a 7,440,373-byte proof; the eight-count literal proof has 7,811,117 bytes.

The [formula batch](../acceleration/results/20260930_hadamard_seven_remaining_cnfs/run02/summary.json) gives the exact 215 profile IDs and each formula's paths/hashes. It completes the explicitly resumed build after the initial allocation ended. Every formula retains all initial domains. They enforce full Gram and within-triplicate caps, omitting cross-group caps and residual D. Independent replay uses:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_twohundredfifteen_profiles_v2.py --batch-summary acceleration/results/20260930_hadamard_seven_remaining_cnfs/run02/summary.json --batch-summary-sha256 eabd989bd427c6fcfc57564d62b907d80630f1b5c7b7d56df17fa09f2df16119 --out build/replay-wave24-encodings
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_twohundredfifteen_profile_proofs.py --campaign-dir acceleration/results/20260930_hadamard_seven_profile_batch_native --campaign-summary-sha256 02520b91d50c0f448fc966b61348da0215d520a5f2082767d09918632b0b0b46 --object-gate acceleration/results/20260930_independent_review/hadamard_twohundredfifteen_profile_object_calibration/summary.json --object-gate-sha256 1302fdcb58227c27fd88d1ce31b5b11d11d36e4da9b87b51c3b0c5ef8de9aa7a --out build/replay-wave24-proofs
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_seven_profile_union.py final --proof-gate acceleration/results/20260930_independent_review/hadamard_twohundredfifteen_profile_proofs/summary.json --proof-gate-sha256 14d5064f7d09f491899f25113844df53b0b49658abc549ed784ed0b92ad55210 --out build/replay-wave24-seven-union
```

Historical proof wrappers authenticate the original LOCAL_ONLY checker executable and recorded environment. On a fresh machine, independently rebuild and calibrate the checker; do not change historical pins to make the wrapper pass. The checker is based on drat-trim commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` with the disclosed Windows timing shim. See the [public build record](../acceleration/results/20260930_rook_sat_independent_proof/checker_build/) and [earlier guide](REPRODUCING_20260930_TWENTIETH_WAVE.md). Direct replay with a separately recorded checker is:

```text
<rebuilt-drat-trim> <cnf_path from the exact batch record> acceleration/results/20260930_hadamard_seven_profile_batch_native/<profile_id>/main/proof.drat
```

The CNF paths span the two preserved build directories; use each actual record rather than assuming all reside in run02. Replay all 215 cases. Record the new source/build/toolchain/hash, calibrated positive and corrupted controls, commands and complete outputs. The first seven pilot uses `hadamard_seven_profile_cnf/profile_0001/instance.cnf` and `hadamard_seven_profile_native_pilot/main/proof.drat`. The eight pilot uses `eight_count_profile_lift/instance.cnf` and `eight_count_profile_native_pilot/main/proof.drat`.

The union is over a frozen population of 1,608 necessary exactly-seven profiles. The 312 pair-screen exclusions and 1,296 disjoint images of 216 proof-excluded representatives cover it exactly once. Combined with the independently established at-most-six exclusion, it yields the conditional at-least-eight result. Union replay authenticates the exact premise records and coverage; it does not run a new solver.

The count master has 155,939 variables and 705,833 clauses in its at-least-seven variant. The saved eight-group count witness is a positive of this necessary relaxation. The interval formula adds exact scalar local-signature bounds, giving 185,963 variables and 7,659,287 clauses. Its witness is a constructed extension, with no new solver call:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_count_master_cnf_v2.py --out build/replay-wave24-count-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_count_interval_cnf.py --out build/replay-wave24-interval-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_count_interval_object.py constructed --encoding-gate acceleration/results/20260930_independent_review/count_interval_cnf/summary.json --encoding-gate-sha256 03bc6b052a831eb0e5d3dacce7647ec88a81410e5f63ec81c88246575cd6baa6 --assignment acceleration/results/20260930_count_interval_witness/assignment.json --out build/replay-wave24-interval-witness
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_eight_count_profile_lift.py audit --out build/replay-wave24-eight-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_eight_count_profile_unsat.py --out build/replay-wave24-eight-proof
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_count_master_eight_orbit_cuts.py --out build/replay-wave24-six-cuts
```

All 540 scalar intervals and all 60 individual 3×3 blocks pass for this count witness, yet its full-Gram lift is excluded. The six resulting cuts forbid exactly its global fibre images; they are not consequences of the old count CSP alone. None of these results invalidates the weaker-model witness records.

Additional exact audit commands are preserved verbatim in their reports. Use fresh `--out` paths:

| Result | Independent checker under `acceleration/` |
| --- | --- |
| All 6,061 count classes and exact local Gram extrema | `audit_20260930_count_gram_intervals.py` |
| Refutation of the exact Frechet-extrema formula | `audit_20260930_local_frechet_equality.py` |
| All 60 separate 3×3 block witnesses | `audit_20260930_count_profile_gram_blocks.py` |
| All 217 affine Gram parity models and exact span ranks | `audit_20260930_hadamard_gram_affine_gf2.py` |
| Complete compressed proof transport | `audit_20260930_hadamard_twohundredfifteen_proof_transport.py` |

The exact-extrema counterexample refutes equality with the proposed loose formula; it does not refute the loose inequalities. The 217 parity certificates establish only affine consistency modulo2. Independent review does not certify the producer's aggregate Frechet mismatch count. No numerical or heuristic score is used as a proof.

Python 3.12.10, uv 0.11.25 and the pinned lockfile were used. Preserve failed source versions, the explicit build resume, corrected checker controls, refused native invocation and registrar schema failures. Never rerun completed one-shot registrars, checkpoint writers, catalogs or publishers.

The wave freezes 248 claims: 244 VERIFIED/CLEAR, two CANDIDATE/CLEAR and two REFUTED/CLEAR. Eighteen verified claims and one refutation are new. Reference-audit metadata is chunked into hash-bound gzip parts, each at most 25,000 records and 10 MiB; the named catalog/stage/root-reference wrappers retain their explicit 32 MiB limits. Schema, transport and CI checks are not mathematical verification. The later count search after the six cuts and joint-model inventories belong to the next wave. Overall search coverage: UNKNOWN; no validated denominator.
