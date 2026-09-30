# Twelfth resumed milestone, 2026-09-30 JST

Four independently verified claims were added since the [eleventh milestone](RESEARCH_20260930_ELEVENTH_WAVE.md). The triangle-factor normalization and its necessary CNF now cover arbitrary target cores. A separate six-prism encoding covers every column pattern for that fixed core. Exact rational and modular witnesses show why three linear relaxations cannot exclude that model. Both native pilots ended UNKNOWN.

**As of:** 2026-09-30T00:27:50.973454+00:00; source commit `415a8702cf27e1166ddf14ddd7289db3eaadde2e`. [Checkpoint](../acceleration/results/20260930_resume/twelfth_milestone_checkpoint.json), [ledger snapshot](../acceleration/results/20260930_resume/claims_at_twelfth_milestone.yaml); previous report: eleventh milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all four claims are revision 1.

| Claim | Scope and evidence |
| --- | --- |
| `C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION` | Every unrestricted target admits the stated normalized arbitrary-core factor form. Conversely the factor conditions establish only the stated partial99 specification, with residual D absent. [Audit](../acceleration/results/20260930_independent_review/unrestricted_triangle_factor/summary.json). |
| `C-UNRESTRICTED-TRIANGLE-NECESSARY-FACTOR-CNF-ENCODING` | Universally necessary target relaxation covering all target graphs up to the independently proved triangle labels; no fixed core, component, prism or automorphism restriction. [Audit](../acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json). |
| `C-SIX-PRISM-COMPLETE-COLUMN-FACTOR-CNF` | Only the explicitly fixed identity-cross, standard-internal-matching six-prism39core. All normalized Gram factors, not all target cores. [Audit](../acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json). |
| `C-SIX-PRISM-COLUMN-LINEAR-RELAXATION-WITNESSES` | Three specifically defined linear relaxations of one fixed six-prism abstract factor model; no binary integer factor or target feasibility follows. [Audit](../acceleration/results/20260930_independent_review/prism_column_modular/summary.json). |

**Work completed:** the universal derivation starts with any edge and its unique triangle. Relabelling makes M0 standard and two cross matchings identity, while M1, M2 and P remain arbitrary. The 60 C0 columns are bijectively the nonmatching coordinate pairs. No prism-free, commuting-matching, symmetric-P or automorphism restriction is introduced. The 110,904-variable, 518,160-clause model encodes all Gram equations, margins, mixed bounds and column-pair bounds. Independent checking reconstructed every clause and calibrated the raw-object path. A SAT factor would still omit the residual 60-vertex graph.

The separate fixed six-prism model retains all 96 possible column supports for each of 60 canonical columns: 5,760 distinct choices. The independent reviewer enumerated all 46,656 component-label states to establish the complete domain, checked all 540 exact equations and every one of 874,800 clauses. Its 245,880-variable formula encodes abstract Gram factors; outside-column bounds and residual D are absent. This removes the earlier five-matching and complement-pairing restrictions only within the specified core.

| Native attempt | Result | Saved conflicts | Wrapper seconds |
| --- | --- | --- | --- |
| variable_core_factor | UNKNOWN_CONFLICT_LIMIT | 1000000 | 146.078 |
| prism_all_columns | UNKNOWN_TIMEOUT | 817260 | 300.047 |

Each model had one attempt with a 300-second limit and 1,000,000 configured conflicts, with additional memory/file guards. These are single-run measurements in different models, not a speed comparison. Neither produced a factor or complete proof. Independent run audits authenticate inputs, actual outcomes and complete hashes of the retained incomplete traces; hashing an incomplete trace is not proof checking.

The 540 primary linear equations admit the exact rational vector with every coordinate 1/96 in [0,1]. Two separate saved residue vectors satisfy their reductions modulo 2 and modulo 3. Direct independent evaluation checked every equation and rejected fourteen altered witnesses. These three witnesses belong to different domains and are not combined into a binary solution. Modular rank reported by the producer remains unpromoted telemetry.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. Universal encoding coverage means every target supplies a model; it is not a completed exhaustive search. No unrestricted branch or complete fixed-core family was excluded. Ledger population: 126 claims, 124 VERIFIED/CLEAR and 2 CANDIDATE/CLEAR.

**Best result:** independently verified universal necessary encoding and complete coverage of the fixed six-prism column domain. No validated full factor, new graph candidate or target-wide bound was obtained.

**Problems:** both native outcomes are UNKNOWN. The linear rational/modular relaxations are feasible and therefore cannot alone prove the integer model impossible. The initial variable-core checker expected an obsolete metadata key and stopped; its original failure and corrected checker are preserved. The independent all-column audit explicitly binds the transitive validator import omitted by the producer manifest. Large raw CNF/model files have authenticated gzip recovery, while incomplete native traces remain LOCAL_ONLY.

**Execution:** both named native attempts are complete. Fresh observation at 2026-09-30T00:27:51.345676+00:00: `NO_CADICAL_PROCESS_OBSERVED`. Exact command and logs are in the checkpoint; an observed later process does not reopen either completed attempt. The user's continuation instruction remains active.

**Next experiment:** independently establish and test two coordinate relabelling reductions: one first-column choice for the six-prism formula, and eleven first-matching orbit representatives for the arbitrary-core formula. These must preserve all target coverage without assuming a target automorphism.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/415a8702cf27e1166ddf14ddd7289db3eaadde2e), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../acceleration/results/20260930_twelfth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_TWELFTH_WAVE.md). Public evidence pointers are bound after immutable remote publication is confirmed.
