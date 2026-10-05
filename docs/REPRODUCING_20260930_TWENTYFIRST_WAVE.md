# Twenty-first wave: unbalanced groups and the first profile proof

The fixed-support problem remains unresolved. The new exact results require at least four unbalanced groups, exclude exactly five, and restrict exactly six to six saved group subsets with984 labelled marginal profiles. In the exactly-four family with column caps,108 profiles reduce to18 fibre-label orbits;12 profiles fail the local screen, and the literal case0 full-Gram formula has a complete independently replayed UNSAT proof. The other15 nonempty-orbit representatives belong to the next campaign.

Use the root locked environment and fresh output destinations:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_case0_model.py --receipt build/case0-model-recovery-new.json
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_case0_model_package.py --out build/case0-model-transport-new
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_case0_profile.py audit --out build/case0-encoding-new
```

The model is13,208,093 bytes, SHA256
`6705e33a26c332d093e3a2bff6dcd5dca276c6b50da2b24c61c7cbf891e0629c`.
Its public576,941-byte gzip part has an independently checked lossless recovery path. The helper refuses to replace different bytes. The encoding checker reconstructs all187,408 clauses and all initial domains:16 groups with150 balanced options each and four exceptional groups with48 options each. It does not substitute the smaller AC domains.

The CNF is `acceleration/results/20260930_hadamard_case0_profile_cnf/instance.cnf`, SHA256
`2e949832491635b794e02b525ac983c0920d66cf91ee4e039564c5920008b22e`.
The complete trace is `acceleration/results/20260930_hadamard_case0_profile_native_pilot/main/proof.drat`,
9,139,513 bytes, SHA256
`01ee3198778714f32bf0e7e0c4a89ab3d29ecceb088ccf392ee0e2749418d07d`.
Both raw files are public payloads. A rebuilt DRAT-trim can check them directly:

```text
<drat-trim> acceleration/results/20260930_hadamard_case0_profile_cnf/instance.cnf acceleration/results/20260930_hadamard_case0_profile_native_pilot/main/proof.drat
```

The historical checker is pinned to upstream2e3b2dc0ecf938addbd779d42877b6ed69d9a985 with the disclosed Windows timing shim. Its executable remains LOCAL_ONLY. Public source, patch, build records and replay limitations are described in the [twentieth guide](REPRODUCING_20260930_TWENTIETH_WAVE.md). Record a rebuilt checker's own version, hash, calibration controls and complete result. Do not rewrite historical provenance to match a different environment. With the exact saved tools present, the historical independent proof wrapper is `audit_20260930_hadamard_case0_profile_unsat.py --out NEW` under acceleration/.

The native call returned UNSAT after12,232 conflicts,1.82 native wall seconds and1.08 CPU seconds. Complete replay, a positive proof, four invalid proof/input controls and six receipt corruptions were independently checked. This proves only literal case0, with within-group caps. Cross-group caps and residualD were omitted. Any transfer to another labelled profile requires the separately checked relabelling map. No target automorphism is assumed.

The other independent paths are:

| Statement | Checker under acceleration/ |
| --- | --- |
| At-most-three marginal implication and scoped exclusion | audit_20260930_hadamard_few_exception_marginals.py |
| Four-group circuit necessity | audit_20260930_hadamard_four_group_circuits.py |
| Complete108-profile local screen | audit_20260930_hadamard_four_group_local_screen.py |
| Fibre-label normalization | audit_20260930_hadamard_fibre_profile_orbits.py |
| Exactly-five exclusion | audit_20260930_five_unbalanced_groups.py |
| Complete saved partial-object intervals | audit_20260930_four_group_joint_v2.py |
| First partial object's residual PSD | audit_20260930_first_partial_psd.py |
| All38,760 six-group ranks/kernels | audit_20260930_hadamard_six_exception_census.py |
| Nine-case exact integer marginal enumeration | audit_20260930_hadamard_six_rank4_profiles.py |

Use the exact saved report commands with fresh output directories. Python3.12.10 and uv0.11.25 were used; source commits, tools, inputs, outputs, shared components and controls are bound by the reports.

The joint partial enumeration stopped at its predeclared120-second allocation:35 complete profiles, one partial prefix and60 unattempted. Every one of7,335,060 saved tuples and all36 first witnesses were independently checked. The first witness's residual is exactly PSD of rank29/nullity7. These facts do not construct the remaining48 columns. The v1 positive-control failure and corrected v2 source are preserved. Do not restart the checkpoint merely to replay its evidence.

The six-group census checked38,760 subsets and retained nine rank-four subsets. Independent direct enumeration of121,869 coordinate-profile sequences then checked all108 DP layers and excluded three of those nine. The984 surviving labelled marginal profiles are not factors. The later local-domain filter of those profiles, extra input-coordinate relabelling diagnostic, and remaining15-formula campaign are outside this milestone.

The ledger snapshot contains206 claims:203 VERIFIED/CLEAR, two CANDIDATE/CLEAR and one REFUTED/CLEAR. Twelve verified claims were added; no target resolution exists. Overall search coverage: UNKNOWN; no validated denominator. Do not rerun one-shot registrars or overwrite any completed evidence.

