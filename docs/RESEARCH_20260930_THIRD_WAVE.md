# Third resumed milestone, 2026-09-30 JST

Five scoped claims were independently checked and added since the
[second milestone](RESEARCH_20260930_SECOND_WAVE.md). All six new support
bounds are nonpositive. Eight more locally valid SAT graphs have exact Gram
extension obstructions. Neither experiment resolves the target.

**As of:** 2026-09-29T20:10:23.553933+00:00; source base
`dacbbaa157f30182f877dc38b2017f790ddc5938`;
[checkpoint](../acceleration/results/20260930_resume/third_milestone_checkpoint.json),
[ledger snapshot](../acceleration/results/20260930_resume/claims_at_third_milestone.yaml).
Previous report: [second milestone](RESEARCH_20260930_SECOND_WAVE.md).

**Verdict:** target resolution UNKNOWN. No independently validated target graph
or general nonexistence proof. No candidate target resolution is under external
review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) contains
scoped research and remains unmerged by this agent.

**Verified changes:** all revision 1.

| Claim | Exact result and evidence |
| --- | --- |
| `C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS` | Every target has `G²=63G` for `G=27I-9A+J`, hence `G` is PSD. A negative principal quadratic yields a clause on its nonzero free-edge coefficients. [Lemma](../acceleration/results/20260930_independent_review/target_gram_support_lemma.json). |
| `C-ROOK-FOUR-FACTOR-MINIMIZED-GRAM-NOGOOD` | One exact 45-value pattern forces quadratic `-176426969710399200` and cannot extend to a target. [Binding](../acceleration/results/20260930_independent_review/minimized_gram_nogood_claim_binding.json). |
| `C-GPU-LARGE-MOMENT-PDHG-CALIBRATION` | Four guard-only source changes; 14 parser controls and 16 checkpoints across four CPU comparison inputs pass. Engineering evidence only. [Binding](../acceleration/results/20260930_independent_review/large_gpu_calibration_claim_binding.json). |
| `C-PARTIAL-K-EIGHT-COORDINATE-GPU-FROZEN-SUPPORT-ATTEMPTS` | Exact numerators `[-77488,-88510,-211,-26216,-1,-13149]`, all over `1048576`. Every retained star checked for every attempt. [Binding](../acceleration/results/20260930_independent_review/eight_gpu_support_run02_claim_binding.json). |
| `C-ROOK-GRAM-NOGOOD-WAVE01` | Nine solver attempts: eight distinct checked local graphs, eight negative Gram certificates and checked new cuts; one UNKNOWN. Nine accepted cuts include the prior initial cut. [Binding](../acceleration/results/20260930_independent_review/rook_lazy_wave01_binding.json). |

**Work completed:** the GPU retry completed checkpoints 1000, 5000 and 10000.
The independent exact checker evaluated 1,875,214 retained stars per attempt:
11,251,284 star evaluations across six attempts and 504 center maxima. All six
attempts completed; none was skipped, erroneous or positive. The failed first
run has six separate skipped records and zero bound evaluations. These counts
are pipeline stages, not additional distinct candidates. The registry snapshot
has 60 claims: 58 VERIFIED/CLEAR and 2 CANDIDATE/CLEAR.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.
Local exclusions can overlap; no union size or branch fraction is claimed.
A local 59-vertex witness is not a target graph.

**Best result:** the best of these six attempted support bounds is exactly
`-1/1048576`. It is weaker than the objective's trivial lower bound zero and
establishes no exclusion. Nonpositive attempts establish neither exact LP
feasibility nor the impossibility of stronger weights. The earlier positive
six-coordinate bound concerns a different, narrower fixed family.

**Problems and execution:** GPU run01's import failure and all skip records
are preserved. Run02 and its full independent support audit completed. SAT
wave01 ended with UNKNOWN at the remaining solver-time limit; it produced
neither an UNSAT proof nor a Gram-compatible survivor. Native worker cleanup
failures followed saved models; the raw models passed independent checks.
The aggregate audit's first path-normalization failure was preserved and
corrected without changing mathematical artifacts. The
[process observation](../acceleration/results/20260930_resume/third_milestone_process_observation.json)
is time-specific, not perpetual status.

**Next experiment:** independently validate stronger Gram clauses by maximizing
the exact linear quadratic over omitted Boolean edges, then run a new bounded
local SAT wave. A separate structural investigation checks whether further
neighborhood conditions add information to the current relaxation.

**References and recovery:** the
[second-wave guide](REPRODUCING_20260930_SECOND_WAVE.md) covers common inputs.
GPU checkpoint gzip files recover from run02 `chunk_manifest.json`, then
`compressed_artifacts.json`; this exact reconstruction was independently
checked. Each augmented SAT instance recovers from the base CNF and ordered
cuts using `acceleration/restore_20260930_rook_cnf.py`. All nine reconstructed
byte streams matched saved hashes. Compiled binaries and oversized originals
are separately catalogued.
