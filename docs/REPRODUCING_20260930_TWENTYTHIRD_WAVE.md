# Twenty-third wave: six-exception exclusion and broader necessary domains

This wave excludes exactly six unbalanced groups on one literal six-prism Hadamard support. Together with the prior at-most-five result, any factor on that support satisfying the prescribed full integer Gram and all outside-column overlap caps needs at least seven unbalanced groups. This does not exclude the whole support, any unrestricted core family or Conway-99. No automorphism of a hypothetical graph is assumed.

Use the existing checkout and pinned environment. All replay output directories and receipt paths must be fresh:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twentythird_raw_artifacts.py --receipt build/wave23-recovery.json
```

The helper restores missing originals at their recorded repository paths, verifies existing originals, and refuses to overwrite different bytes. `--destination-dir build/fresh-wave23-recovery` instead reconstructs a separate tree; `--verify-only` checks all compressed streams without creating originals. The development [recovery receipt](../acceleration/results/20260930_resume/twentythird_raw_recovery.json) records restoration of all 109 originals to a fresh ignored tree: 55 models and 54 campaign proofs. Recovery checks identity, not mathematical validity. The earlier literal-model helper is a historical preservation check that expects the retained raw original; use the general helper above for a fresh public checkout.

The [54-proof package manifest](../acceleration/results/20260930_hadamard_six_profile_proof_package/package_manifest.json), SHA256 `46edb96dd42e7c41105bd0cd2997ddec98e1e631a8aad268aeab0c0923058f5c`, describes 555,334,934 raw bytes in 99 independent gzip streams totaling 103,334,312 compressed bytes. Concatenate the **decompressed** chunks in listed order. A separate [transport audit](../acceleration/results/20260930_independent_review/hadamard_fiftyfour_proof_transport/summary.json) compared all recovered bytes against the independently checked originals and rejected sixteen corruptions. The first literal profile's 8,409,167-byte proof is published directly. Thus 55 representative proofs exist, totaling 563,744,101 bytes; the 54-proof campaign and first pilot are separate runs.

The [54-formula batch](../acceleration/results/20260930_hadamard_six_remaining_cnfs/run01/summary.json) pins its exact selection, models, scopes and CNFs. These formulas use every initial exceptional domain, without AC-domain pruning. Thirty-two formulas have 10,048 variables and 174,766 clauses; twenty-two have 10,156 variables and 177,412 clauses. They impose the full Gram equation and within-group column caps, omitting cross-group caps and residual `D`. The separate first literal formula has 10,156 variables and 177,412 clauses.

Independent formula reconstruction and proof replay commands are:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_fiftyfour_profiles.py --out build/replay-wave23-encodings
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_fiftyfour_profile_proofs.py --out build/replay-wave23-proofs
```

The original campaign attempted each of 54 formulas once, with a 60-second wall limit and 1,000,000-conflict limit per call. All returned UNSAT and all complete proof traces were independently checked. Saved wrapped-solver time is 97.596 seconds; end-to-end time is 149.547 seconds. These are one campaign's measurements, not performance guarantees.

The historical proof wrapper authenticates the original LOCAL_ONLY checker executable and recorded environment. A fresh machine must independently rebuild and calibrate its checker; it should not rewrite historical records to fit a new environment. The checker provenance is drat-trim commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` with the disclosed Windows timing shim. See the [public build record](../acceleration/results/20260930_rook_sat_independent_proof/checker_build/) and [twentieth replay guide](REPRODUCING_20260930_TWENTIETH_WAVE.md). Direct replay with a newly recorded checker is:

```text
<rebuilt-drat-trim> acceleration/results/20260930_hadamard_six_remaining_cnfs/run01/<profile_id>/instance.cnf acceleration/results/20260930_hadamard_six_profile_batch_campaign/<profile_id>/main/proof.drat
```

Repeat for the exact 54 IDs in the batch manifest. The separate literal proof uses `hadamard_six_profile_cnf/profile_0000/instance.cnf` and `hadamard_six_profile_native_pilot/main/proof.drat`. Record the new checker source, build command, toolchain, executable hash, positive/corrupted controls and complete outputs.

The [six-profile union audit](../acceleration/results/20260930_independent_review/hadamard_six_profile_union/summary.json) checks the complete frozen population of 984 necessary profiles: 654 independently excluded by pairwise propagation and 330 disjoint images of 55 proof-excluded representatives. There are no gaps or duplicate coverage. It composes the independently pinned kernel, marginal, local-domain, normalization, encoding and proof premises; it does not rerun native search.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_six_profile_union.py --out build/replay-wave23-six-union
```

Other independent checking paths are listed below. Each uses `--out` with a fresh directory; the seven-profile AC checker additionally requires the exact `--run` and `--run-summary-sha256` arguments shown in its saved command.

| Result | Independent checker under `acceleration/` |
| --- | --- |
| First literal six-profile encoding and decoded-object calibration | `audit_20260930_hadamard_six_profile.py` |
| First literal complete UNSAT proof | `audit_20260930_hadamard_six_profile_unsat.py` |
| All 1,608 seven-group profiles and 11,256 local domains | `audit_20260930_hadamard_seven_profile_local_domains.py` |
| All 37,784,232 option pairs and complete AC deletion/support replay | `audit_20260930_seven_profile_arc.py` |
| All seven-profile fibre relabellings and completion covariance | `audit_20260930_hadamard_seven_fibre_orbits.py` |
| All 125,970 eight-group subsets and necessary kernel exclusions | `audit_20260930_hadamard_eight_exception_census.py` |
| All bounded coordinate vectors and complete marginal profiles | `audit_20260930_coordinate_marginal_domains.py` |
| Saved all-triple descent scores and transitions | `audit_20260930_hadamard_all_triple_descent.py` |

Each bound audit report preserves exact commands, source commit, dependencies, inputs, outputs and controls. Python 3.12.10, uv 0.11.25 and the pinned `uv.lock` were used. Integer/Boolean NumPy paths use explicitly bounded sums; no floating-point result is promoted to a certificate.

The seven-group combined pair screen excludes 312 of 1,608 profiles, leaving 1,296 in 216 relabelling classes. Both pair predicates start with within-group-cap-filtered domains. The eight-group kernel census retains 4,184 necessary subsets; it does not test full factors. The coordinate audit directly enumerates all `4^10` vectors at each of twelve coordinates, checking 12,582,912 vectors in total. It confirms 291 coordinate-specific vectors and 2,226 ordered three-fibre profiles, without proving joint feasibility across coordinates.

The all-triple experiment ran four chains, 2,000 updates each. Its saved best full squared Frobenius Gram error is exactly 296 with 37 outside-column cap violations. Objective `FIXED_L_FULL_GRAM_FROBENIUS_SQUARED_V1` is integer-valued and lower is better; it is not comparable to earlier cross-Gram permutation objectives. Independent review checked all saved checkpoints and 8,000 score transitions, not every replacement score, tie choice or intermediate random trajectory. It produced no full factor or exclusion.

Preserve the seven-AC v1 allocation refusal at 512MiB and the separately preregistered v2 increase to 768MiB. The v2 first invocation stopped at its 180-second limit before classifying any profiles; an explicit authenticated resume completed all cases. Do not overwrite these records or rerun completed registrars, checkpoint writers, catalog builders or publishers.

This milestone freezes 229 claims: 226 VERIFIED/CLEAR, two CANDIDATE/CLEAR and one REFUTED/CLEAR; thirteen verified claims are new. Publication metadata allows at most 32MiB only for the six explicitly named catalog/stage/reference wrappers in the preparation/final catalog directories. Research payloads retain the 10MiB limit. Schema, catalog and CI checks do not establish mathematics. The subsequent coupled count-master experiment is outside this cutoff. Overall search coverage: UNKNOWN; no validated denominator.
