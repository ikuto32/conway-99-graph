# Twenty-second wave: four-exception exclusion and six/seven-group screens

This wave excludes the exactly-four-unbalanced subfamily on one literal six-prism Hadamard support. Combining the independently checked at-most-three and exactly-five exclusions gives a lower bound of six unbalanced groups for any factor on that support satisfying the full integer Gram and outside-column overlap caps. This does not exclude the whole support, other supports or Conway-99. No target automorphism is assumed.

Use the existing repository and locked environment. Each output path below must be fresh:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twentysecond_raw_artifacts_v2.py --receipt build/twentysecond-recovery.json
```

The recovery helper restores missing originals at their recorded repository paths and refuses to replace different existing bytes. It authenticates all fifteen model packages and all fifteen proof packages, decompresses every chunk, and verifies complete raw lengths and SHA256 values. `--destination-dir build/fresh-recovery` creates a separate recovered tree; `--verify-only` checks streams without writing originals. The successful development recovery wrote all thirty originals into a fresh ignored tree; its [receipt](../acceleration/results/20260930_resume/twentysecond_raw_recovery.json) is preserved. Version1 stopped before writing files because the proof manifest names its raw path differently from the model manifest; its source and failure record are retained.

The [proof package manifest](../acceleration/results/20260930_hadamard_four_profile_proof_package/package_manifest.json), SHA256 `e55ce731d5ca1d18c4f5f5c9fc3195bc934f20f45b0172fc867ca1781e976250`, describes 149,571,922 raw proof bytes in 25 gzip parts totaling 27,706,059 bytes. Each part is a separate gzip stream covering a contiguous raw chunk; concatenate the **decompressed** chunks in the listed order. The model packages each contain one gzip stream. Original raw model/proof paths remain LOCAL_ONLY with public lossless recovery. Identity recovery is not DRAT verification.

The fifteen new literal case IDs are `6,12,18,24,30,36,42,48,51,72,78,84,90,96,102`. Each formula has 10,564 variables and 187,408 clauses, with 16 balanced domains of 150 choices and four complete initial exceptional domains of 48 choices. Within-group column caps are included; cross-group caps and residual `D` are omitted. The [batch manifest](../acceleration/results/20260930_hadamard_four_profile_cnfs/summary.json) pins every exact CNF, model, scope and recovery package.

Independent reconstruction of all formulas and all 2,811,120 clauses:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_fifteen_profiles.py audit --out build/replay-fifteen-encodings
```

The original bounded campaign made one call per formula, with a 60-second wall limit and 1,000,000-conflict limit per case. All fifteen returned UNSAT. The saved aggregate reports 25.904 wrapped-solver seconds and 41.219 end-to-end seconds; transfer and checking costs are distinct. These are single-campaign measurements, not general performance claims. All 149,571,922 proof bytes were independently replayed against their exact CNFs, with positive and corrupted proof controls and receipt checks.

The historical complete proof wrapper is:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_fifteen_profile_unsat_v2.py --out build/replay-fifteen-proofs
```

That wrapper authenticates the original checker executable, compiler and environment records and cannot be promised to run unchanged on a fresh machine. It uses drat-trim upstream commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`, with the disclosed Windows timing shim. The executable remains LOCAL_ONLY; [public build provenance](../acceleration/results/20260930_rook_sat_independent_proof/checker_build/) and the [twentieth replay guide](REPRODUCING_20260930_TWENTIETH_WAVE.md) explain the trusted build and historical restoration requirements. A separately rebuilt checker can replay each public mathematical input directly:

```text
<rebuilt-drat-trim> acceleration/results/20260930_hadamard_four_profile_cnfs/case_006/instance.cnf acceleration/results/20260930_hadamard_four_profile_native_campaign/case_006/main/proof.drat
```

Repeat for every listed case, recording the new checker's source, build command, toolchain, executable hash, controls and complete result. Do not rewrite historical records to match a different environment.

The [independent union audit](../acceleration/results/20260930_independent_review/hadamard_four_profile_union/summary.json) checks the exact population of 108 necessary profiles: 12 local-screen exclusions and 96 disjoint images of 16 proof-excluded representatives, with zero gaps or duplicate coverage. The sixteenth proof is the prior case0 proof. It composes these recorded premises without rerunning the native solvers:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_four_profile_union.py --out build/replay-four-union
```

Further complete checking paths are:

| Result | Independent checker under `acceleration/` |
| --- | --- |
| All 984 six-exception profiles' individual local domains | `audit_20260930_hadamard_six_profile_local_domains.py` |
| All 12,846,624 option pairs and every AC deletion/support | `audit_20260930_six_profile_arc_v3.py` |
| Six-fibre profile/domain/relation normalization | `audit_20260930_hadamard_six_fibre_orbits.py` |
| All 77,520 seven-group subsets and rank/null certificates | `audit_20260930_hadamard_seven_exception_census.py` |
| All 154,214 marginal sequences across 200 retained septets | `audit_20260930_hadamard_seven_rank5_profiles.py` |
| All 46,080 matching-preserving coordinate permutations | `audit_20260930_hadamard_input_relabeling.py` |

Each accepts `--out` with a fresh directory. The corresponding saved independent reports bind the original source commit, exact commands, inputs, outputs, dependency versions and calibrated controls. Python 3.12.10, uv 0.11.25 and the pinned `uv.lock` were used; the direct relation checker uses exact NumPy uint16 arithmetic with explicitly bounded sums, not floating point.

Both six-profile AC variants start from within-group cap-filtered domains. The first empties 582 profiles using only summed-Gram cross-group relations; adding cross-group caps empties 654 and leaves 330, in 55 relabelling classes. Neither count is a Gram-only-family exclusion. The seven-group marginal screen leaves 38 septets with 1,608 labelled profiles. These nonempty relaxations do not supply local triples, full factors or target graphs.

Preserve failed checker versions: the AC v1/v2 metadata assumptions, the fifteen-proof v1 manifest-field assumption, and the recovery v1 path-field assumption. Their corrected versions do not alter producer evidence or thresholds. Do not rerun completed one-shot registrars, checkpoint writers, catalog builders or publishers.

The frozen milestone has 216 claims: 213 VERIFIED/CLEAR, two CANDIDATE/CLEAR and one REFUTED/CLEAR. Ten verified claims were added. Registry validation and publication checks are not mathematical verification. Overall search coverage: UNKNOWN; no validated denominator. The six-exception literal pilot, remaining-54 preparation and unrestricted-exception construction experiment belong to later research, outside this publication cutoff.
