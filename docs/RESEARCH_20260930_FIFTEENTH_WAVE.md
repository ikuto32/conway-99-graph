# Fifteenth resumed milestone, 2026-09-30 JST

Ten verified claims were added since the [fourteenth milestone](RESEARCH_20260930_FOURTEENTH_WAVE.md): four connected construction domains and their finite GPU/SAT checks, conditional modular results, and a distinct 60-pattern six-prism construction model. All five native attempts ended UNKNOWN. No target resolution or new exclusion was obtained.

**As of:** 2026-09-30T02:31:40.088808+00:00; source commit `36bb1d156f3a4332f6301ab5b7a26e0b66eef30b`. [Checkpoint](../acceleration/results/20260930_resume/fifteenth_milestone_checkpoint.json), [ledger snapshot](../acceleration/results/20260930_resume/claims_at_fifteenth_milestone.yaml); previous report: fourteenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated 99-vertex graph or general nonexistence proof. No target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all ten claims are revision 1, restricted to their exact statements.

| Claim | Exact scope and evidence |
| --- | --- |
| `C-TRIANGLE-GF2-MAXIMAL-RANK-MIXED-CONSISTENCY` | Conditional linear solvability over GF2; valid triangle cores supply the left-action premise by symmetry, and valid factors supply even cell-column parity. Full binary rank remains an explicit premise. [Evidence](../acceleration/results/20260930_independent_review/triangle_gf2_maxrank/summary.json). |
| `C-FOUR-CONNECTED-IDENTITY-CORE-PORTFOLIO` | Finite four local construction domains from the authenticated matching-pair census with chosen P=I; no full factor, residual D or target graph. [Evidence](../acceleration/results/20260930_independent_review/connected_identity_cores/summary.json). |
| `C-FOUR-CONNECTED-CORE-ANNEALER-CALIBRATION` | Four frozen core IDs only; native algorithm unchanged, with independent exact domains and finite T3.25 two-chain23+41/64 controls. [Evidence](../acceleration/results/20260930_independent_review/factor_portfolio_v4/summary.json). |
| `C-CONNECTED-CORE-PORTFOLIO-ANNEALER-SAVED-STATES` | Exact saved scores, domain membership and checkpoint carry for this finite four-core portfolio only. [Evidence](../acceleration/results/20260930_independent_review/connected_core_portfolio_states/claim_binding.json). |
| `C-FOUR-CONNECTED-FIXED-CORE-FACTOR-CNF` | Four particular raw connected identity-P cores; necessary incidence factors with all base caps, no residual D. [Evidence](../acceleration/results/20260930_independent_review/connected_fixed_core_claim_binding/claim_binding.json). |
| `C-TRIANGLE-GF2-SCALAR-KERNEL-MIXED-CONSISTENCY` | Conditional universal GF2 linear compatibility; no residual graph constraints. [Evidence](../acceleration/results/20260930_independent_review/five_core_modular_gram/summary.json). |
| `C-FIVE-CORE-MODULAR-GRAM-RANKS-ACTIONS` | Exact finite ten matrix/action cases, with known243 factor ranks57 and47 checked independently. [Evidence](../acceleration/results/20260930_independent_review/five_core_modular_gram/summary.json). |
| `C-THREE-CONNECTED-CORE-GF3-MIXED-CONSISTENCY` | Three fixed cores only; a conditional modular linear solution, without symmetry or graph completion. [Evidence](../acceleration/results/20260930_independent_review/five_core_modular_gram/summary.json). |
| `C-SIX-PRISM-COMPLEMENT60-SINGLE-ROW-DOMAINS` | Exactly one selected fixed-six-prism60-pattern template and all of its18local single-row domains; not a joint bit lift, full factor, residual completion or target graph. [Evidence](../acceleration/results/20260930_independent_review/prism_coarse_complement/summary.json). |
| `C-SIX-PRISM-COARSE60-EXACT-BITLIFT-CNF` | Exact equivalence for one specified60-pattern fixed-core family; arbitrary bits and no symmetry fixing, residual D, full99adjacency or all-template coverage. [Evidence](../acceleration/results/20260930_independent_review/prism_coarse60_bitlift_cnf/summary.json). |

**Work completed:** deterministic selection inspected all 3,580 ordered-matching-pair representatives with chosen P=I, finding 2,806 connected cores and selecting the first qualifying core in each of the first four qualifying stages. The four selected cores are construction restrictions, not a cover of the target. Their GPU admission and actual public-checkpoint continuation passed independent finite calibration. The pilot completed 12 phases, 96 chunks and 1,572,864 proposal records across 64 continuing chains; 192 phase-chain endpoints are overlapping stages. Independent checking covered 96 chunk-best, 192 phase-final-current and 192 phase-final-best raw factors, all 1,536 current and 1,536 best checkpoint scores, and carry between checkpoints. Campaign transition deltas and acceptance trajectories were not all replayed.

Each of the four fixed-core CNFs appends exactly 24 units to the audited original variable-core encoding. All four complete clause bodies and semantic units were checked, and a separate native/raw-object checker was calibrated. Each formula has 110,904 variables and 518,184 clauses.

The alternative six-prism template uses all 90 balanced component-to-fibre patterns except the prior 30-pattern support, leaving 60 distinct patterns. Independent enumeration checks all 18 local bit domains: 136 survivors among 184,756 balanced words per domain. These 2,448 local survivors are not full factors. The joint model includes all 2,496,960 pairwise domain compatibility tests and all 1,770 Y-column caps. Its 5,238 variables and 85,698 clauses were fully independently reconstructed before native search; no complement-column pairing or target automorphism was imposed.

| Completed native attempt | Result | Observed conflicts | Wrapper seconds |
| --- | --- | ---: | ---: |
| connected_fixed_core_native_00 | UNKNOWN_CONFLICT_LIMIT | 2000002 | 158.656 |
| connected_fixed_core_native_01 | UNKNOWN_CONFLICT_LIMIT | 2000000 | 174.266 |
| connected_fixed_core_native_02 | UNKNOWN_CONFLICT_LIMIT | 2000000 | 118.125 |
| connected_fixed_core_native_03 | UNKNOWN_CONFLICT_LIMIT | 2000001 | 171.641 |
| prism_coarse60_native_pilot | UNKNOWN_CONFLICT_LIMIT | 2000000 | 139.938 |

All five attempts had 300-second and two-million-conflict limits plus memory/file guards. Each ended at its conflict limit and received a separate execution audit including all retained partial-trace bytes. These are not complete UNSAT proofs; no decoded factor was produced. Timings on different inputs are not performance comparisons.

**Mathematical findings:** a conditional maximal-rank GF(2) lemma and a more general scalar-kernel-action lemma establish only field-valued linear residual consistency. Exact rank/action certificates for four selected cores and the known 243-vertex fixture show that the tested GF(2) sufficient premises fail in all five cases; this supplies no incompatible factor. For connected cores 01, 02 and 03, every actual integer factor would automatically admit some GF(3) solution of FD=H. Therefore this modular linear test cannot prune those factors. Symmetry, zero diagonal, binary entries and the quadratic residual equation remain unproved requirements on D.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch or fixed core was excluded. Ledger population: 148 claims, 146 VERIFIED/CLEAR and 2 CANDIDATE/CLEAR.

**Best result:** exact saved minima under `TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1` were:

| Chosen core | T=1 → T=0.25 → T=0 |
| --- | --- |
| connected_00 | 168 → 154 → 140 |
| connected_01 | 170 → 134 → 132 |
| connected_02 | 172 → 146 → 128 |
| connected_03 | 166 → 144 → 134 |

This objective is the sum of squared integer residuals of the three cross-fibre Gram blocks on each fixed permutation domain, minimized by a heuristic using floating acceptance probabilities. Positive values are not bounds, exclusions or factors. No complete target factor was obtained.

**Problems:** all five native attempts were UNKNOWN. The initial outcome parser rejected an authentic conflict-limit annotation; its source, failed audit and corrected calibration remain preserved. A misspelled dependency ID in the original fixed-core audit is corrected by a bound append-only record. Raw GPU checkpoint/trace JSON has lossless recovery packages; native binaries and incomplete solver traces remain LOCAL_ONLY. Later component-bit normalization and identity-P completion lemmas are outside this cohort.

**Execution:** all cohort searches completed. Fresh native observation at 2026-09-30T02:31:40.562621+00:00: `CADICAL_PROCESS_OBSERVED`. Exact logs are in the checkpoint; any later normalized attempt is separate. The user's continuation instruction remains active.

**Next experiment:** complete the separate coarse60 attempt with its first column's six bits normalized. Its normalization and complete-object gates passed independent checking after this cohort was frozen; the later experiment will receive its own outcome audit. A factor still requires residual completion and full graph validation.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/36bb1d156f3a4332f6301ab5b7a26e0b66eef30b), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../acceleration/results/20260930_fifteenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_FIFTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
