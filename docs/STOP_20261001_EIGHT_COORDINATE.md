# User-requested clean stop — 2026-10-01 JST

**Research is stopped. Do not launch any search or mathematical replay until a
new explicit user instruction resumes research.** The stop request was
「今回の実行をきりが良いところで正常に終了してください。」
This instruction supersedes all earlier continuation and batch authorizations.
The objective is paused, not completed or blocked.

As of: see the timestamp in the [machine-readable stop checkpoint](../acceleration/results/20261001_user_stop/checkpoint.json).
Research source commit: `cc55ad8bd7ad3ef35d33cae35232f9cc8eb264e5`, with
executed source hashes preserved in the run records. Previous report:
[wave29](RESEARCH_20261001_TWENTYNINTH_WAVE.md), public evidence commit
`d43ab1ca6638b565d555b0765044668761de6a64`.

Verdict: target resolution **UNKNOWN**. This repository has neither an
independently validated 99-vertex target graph nor a general nonexistence proof.
No candidate target resolution is under external review. This is a repository
status statement, not a current worldwide literature claim.

Verified changes: eight VERIFIED/CLEAR additions since the published
300-claim cutoff. The root [CLAIMS.yaml](../CLAIMS.yaml) now records 308 claims:
301 VERIFIED/CLEAR, three CANDIDATE/CLEAR and four REFUTED/CLEAR. No claim was
promoted merely because of a timeout or agreement among agents.

| Claim ID (revision 1) | Independently checked scope |
| --- | --- |
| C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-GRAM-ENCODINGS | Complete reconstruction of 64 selected literal formulas |
| C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-LITERAL-PROFILE-EXCLUSIONS | Complete proof replay for those 64 literal instances |
| C-FIXED-HADAMARD-EXACT-EIGHT-CASE0-CORE-FOOTPRINT | Exact mapping and proof replay of one extracted core; no additional exclusion or minimality claim |
| C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH04-GRAM-ENCODINGS | Complete reconstruction of 64 selected formulas, including eight checkpoint-continuation outputs |
| C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH04-LITERAL-PROFILE-EXCLUSIONS | Complete proof replay for those 64 literal instances |
| C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH05-GRAM-ENCODINGS | Complete reconstruction of 64 formulas; no solver result |
| C-REIMBAYEV-Z82-CONDITIONAL-IDENTITY-AND-ARCHIVE-OVERLAP | Conditional identity and exact overlap with archived counting rows; no new exclusion |
| C-WAVE205-LITERAL-T6H1-THIRD-STAR-EXCLUSION | Only the literal induced t6_h1 configuration, under prism-free and rank-11 premises; not the entire rank-11 branch |

Exact statements, assumptions, immutable hashes, independent verifier identities,
controls and limitations are bound in the ledger and its referenced reports.
Registration and checkpoint generation are bookkeeping, not additional
mathematical verification. The written structural audits are
[Z82](AUDIT_20261001_REIMBAYEV_Z82.md) and
[the literal third star](AUDIT_20261001_WAVE205_LITERAL_THIRD_STAR.md).

Work completed: batch03 and batch04 add 128 distinct, independently replayed
literal exclusions, with 310,784,721 bytes of complete proof traces. The checked
disjoint campaign union is 316 cases, with 908,646,622 total proof bytes.
Batch05 has 64 selected, built and fully encoding-checked formulas containing
10,532,344 clauses. Its object calibration also completed successfully.
Batch05 has **zero native preflight calls, zero native research calls, zero
proof audits and zero new exclusions**. These pipeline stages overlap and
must not be summed.

Coverage: 316 of the frozen 792 literal representatives on one fixed six-prism
Hadamard support have complete checked exclusions; 476 remain unresolved.
This support is not without loss of generality. No blanket expansion to all
labelled fibre images is claimed. The third-star claim adds no cases to this
campaign. **Overall search coverage: UNKNOWN; no validated denominator.**
Best result: the previously verified conditional fixed-support lower bound
of eight unbalanced groups is unchanged. No new comparable heuristic score
or target-wide mathematical bound is claimed.

Execution: all four batch05 builders exited successfully and were reaped,
with empty Windows Jobs. The terminal object-calibration session exited zero.
The saved [process observation](../acceleration/results/20261001_exact_eight_prefix64_batch05_execution/final_stop_process_observation.json)
found zero matching Windows campaign workers and no WSL CaDiCaL or drat-trim
processes. It is a timestamped observation, not a perpetual live-process claim.
All research agents reported no active sessions. Batch06 allocation and the
t6 integer-lift inventory were never executed. No automatic continuation is
scheduled or authorized by this checkpoint.

Problems and preserved failures:

- Batch04's original four bounded builds stopped at their deadlines: 56 accepted
  checkpoint records followed 60 producer calls. Explicit continuation made eight
  more calls. Four cases were repeated; 68 calls produced 64 accepted formulas.
  The original incomplete runs are preserved.
- Batch05's first outer invocation refused an incorrect expected status string
  before launching any child. The corrected invocation and original refusal are
  both saved.
- The case0 core producer's first mapping failed after proof extraction; the
  corrected mapping and independent check preserve that history.
- The first Z82 fixture run failed because the known 243-vertex fixture has no
  relevant induced pattern. The correction records that vacuity explicitly.
- The N3-free/Hamming route did not establish a new universal covering theorem;
  its bounded record is not promoted here.
- The wave30 full evidence closure remains **LOCAL_ONLY**. This small stop package
  preserves reports, sources and metadata; complete public replay of the new
  package has not been established. Raw CNFs, proofs and logs remain at their
  recorded local paths. Hashes do not replace missing public artifacts.
- The old 380-case checkpoint/inventory and followup registrar were never run
  and are superseded. Do not run them: batch05 has no proof result.

Next experiment, only after an explicit resume: authenticate the existing
batch05 input/gate bytes, perform its bounded native preflight, then evaluate
those same 64 formulas and independently check each actual result. The aim is
only to resolve those literal encoded cases. Do not rebuild the completed
formulas or start batch06 first.

The [saved resume plan](../acceleration/results/20261001_user_stop/resume_plan.json)
contains exact argv arrays, cwd, environment and source hashes. **These commands
were saved, not executed.** Use `uv` with the existing pinned `uv.lock` and
`UV_PROJECT_ENVIRONMENT=build/research-venv`; recheck current processes, disk
reserves, source hashes and fresh output paths before launching. Require an
actual successful preflight. Independently validate a decoded SAT object or
the complete exact UNSAT proof before registering any further result.

References: [batch05 stop receipt](../acceleration/results/20261001_exact_eight_prefix64_batch05_execution/user_stop_checkpoint.json),
[initial registration](../acceleration/results/20261001_thirtieth_initial_registration/summary.json),
[completed-result registration](../acceleration/results/20261001_stop_registration/summary.json),
[draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3).
The PR remains a draft and must not be automatically merged as a resolution.
