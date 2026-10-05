# Fifth resumed milestone, 2026-09-30 JST

Six independently checked claims were added since the [fourth milestone](RESEARCH_20260930_FOURTH_WAVE.md). A complete raw CNF now has an independent unrestricted equivalence and coverage proof. This verifies the problem encoding, not its satisfiability. The earlier conditional full99 pilot ended UNKNOWN. A new local rook witness passed every clause but has two exact Gram obstructions.

**As of:** 2026-09-29T21:09:06.198251+00:00; source commit `8c0523f90bf652bc36261da51d62778cc96905cd`. [Checkpoint](../acceleration/results/20260930_resume/fifth_milestone_checkpoint.json), [ledger snapshot](../acceleration/results/20260930_resume/claims_at_fifth_milestone.yaml); previous report: [fourth milestone](RESEARCH_20260930_FOURTH_WAVE.md).

**Verdict:** target resolution UNKNOWN. No independently validated target graph or general nonexistence proof, and no candidate target resolution under external review. Draft [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged by this agent.

**Verified changes:** all revision1.

| Claim | Scope and evidence |
| --- | --- |
| `C-PARTIAL-K-EIGHT-COORDINATE-FULL99-SAT-ENCODING` | Only the pinned189scaffold/120fixedK/2160unknown family; not unrestricted target coverage. [Audit](../acceleration/results/20260930_independent_review/eight_full99_cnf/summary.json). |
| `C-PARTIAL-K-EIGHT-FULL99-W81-GRAM-BOX-NOGOOD` | One explicit clause within the exact frozen 120-fixed-K/2160-free-edge full99 family; a redundant strengthening of its exact CNF, with no additional graph assumptions. [Audit](../acceleration/results/20260930_independent_review/eight_full99_w81_gram_cut/summary.json). |
| `C-ROOK-ORBIT-AUGMENTED-LOCAL59-WITNESS` | Only central10vertex matching and four exact incidence blocks fixed. All780pairs among the40right vertices independently variable, constrained by their stated labelled block degrees; no nontrivial automorphism assumed. [Audit](../acceleration/results/20260930_independent_review/rook_orbit_sat_replay_v2/summary.json). |
| `C-ROOK-ORBIT-LOCAL59-DUAL-GRAM-EXCLUSION` | One exact local59 witness surviving352 prior target cuts. No family-wide or unrestricted nonexistence claim; no graph automorphism assumption. [Audit](../acceleration/results/20260930_independent_review/rook_orbit_gram/summary.json). |
| `C-ROOK-ORBIT-LOCAL59-GRAM-BOX-CUT43` | One explicit43literal forbidden Boolean edge pattern in the pinned780edge central-factor family; not a full-family exclusion. [Audit](../acceleration/results/20260930_rook_orbit_gram_box01/independent_box_nogood.json). |
| `C-UNRESTRICTED-FULL99-PREFIX-CNF-ENCODING` | Unrestricted target equivalence via universally available root normalization; all3486outerpairs are free and no nontrivial automorphism is assumed. [Audit](../acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json). |

**Work completed:** the conditional encoding audit reconstructed all1,684,724 clauses and485,165 variables. The unrestricted audit reconstructed all4,136,454 clauses and1,186,500 variables, with all3,486 outer pairs free. It separately checked the universal root normalization and threshold semantics. These are two different encodings, not disjoint graph populations.

The orbit pilot produced one independently checked assignment satisfying3,690,172 clauses and its complete local59 conditions. Its two integer Gram quadratics are negative; the specific graph cannot extend to the target. A separately checked43literal box clause follows. The conditional full99 pilot made one attempt, returned UNKNOWN after1,000,001 conflicts and257.546 seconds including loading, and saved no model or proof. Its native wrapper cleanup exit3221226505 is preserved. Registry population: 80 claims, 78 VERIFIED/CLEAR and2 CANDIDATE/CLEAR.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. The unrestricted equivalence covers the target definition, but there is no justified percentage of its search space exhausted.

**Best result:** an exact, independently checked unrestricted SAT equivalence with no fixed outer-edge pattern or automorphism premise. This is a logical equivalence, not a numerical bound or proof of either answer. The44literal eight-family Gram clause has exact maximum `-5868` for its own fixed vector; the43literal rook clause concerns a different vector and model, so their values are not compared.

**Problems:** the original orbit checker stopped on legacy path-separator metadata. Its source, failed log and correction are preserved; v2 checked the complete saved object without a solver retry. The w81 cut's original wording about a weaker CNF was corrected in a separate scope note: the clause is entailed by the exact conditional full99 encoding. Native Windows cleanup errors do not replace object/proof checks. The separate unrestricted preflight text-read correction is preserved.

**Execution:** the conditional solver and stated audits completed. The native Linux solver was built from pristine CaDiCaL1.9.5 commit `146207318796f094dcded87349a64f0c6927309e`; its calibration and unrestricted object-checker gates are subsequent work. This snapshot makes no persistent live-process assertion and records no unrestricted solver result.

**Next experiment:** one bounded native proof-producing solve of the unrestricted CNF after the two checking gates. SAT must pass a separate complete99 matrix identity check; UNSAT must have a complete proof replay on the exact CNF. Timeout or a resource limit remains UNKNOWN and triggers a new research choice.

**References:** [source base](https://github.com/ikuto32/conway-99-graph/commit/8c0523f90bf652bc36261da51d62778cc96905cd), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [unrestricted derivation](AUDIT_20260930_UNRESTRICTED_FULL99_ENCODING_DERIVATION.md), [artifact catalog](../acceleration/results/20260930_resume/fifth_artifact_catalog.json), [prior recovery guide](REPRODUCING_20260930_FOURTH_WAVE.md). Ordered gzip parts recover the complete unrestricted input/model; the exact raw byte identities were independently checked. Claim artifact availability changes only after immutable publication is confirmed.
