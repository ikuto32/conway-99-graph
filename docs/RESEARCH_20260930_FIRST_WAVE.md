# First resumed milestone, 2026-09-30 JST

Changes since the September17 stop: five independently checked scoped claims
were added, plus one CANDIDATE literature finding. No target-level mathematical
conclusion changed.

**As of:** 2026-09-29T19:23:49.741823+00:00, source base
`048ff18824f076898652da87f4213d74147a0a95`; checkpoint
[`first_milestone_checkpoint.json`](../acceleration/results/20260930_resume/first_milestone_checkpoint.json).
Previous report: [September17 stop](STOP_20260917_SIX_COORDINATE.md).

**Verdict:** target resolution UNKNOWN. No independently validated target
graph or general nonexistence proof. External target review is not applicable;
[draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) reviews scoped research.

**Verified changes:** all claim IDs below are revision1.

| Claim | Exact scope and evidence |
| --- | --- |
| `C-PARTIAL-K-EIGHT-COORDINATE-DOMAINS` | Exactly all2,290,122 local center-star choices across84centers in the120-fixed-K family, with879,449 prior embeddings. [Independent complete-set audit binding](../acceleration/results/20260930_independent_review/eight_domains_claim_binding.json). |
| `C-EIGHT-COORDINATE-FROZEN-WEIGHT-NONPOSITIVITY` | One specified zero-extended coefficient vector has support bound at most `-940695/262144`; it cannot give a positive exclusion bound on this family. [Independent84-star witness check](../acceleration/results/20260930_independent_review/eight_transfer_witness_binding.json). |
| `C-ROOK-CELL-LOCAL-FACTOR-COMPATIBILITY` | Rook-containing targets satisfy the one-cell factor identity; the pinned witness satisfies that local subsystem. [Independent derivation and raw check](../acceleration/results/20260930_rook_cell_independent/AUDIT.md). |
| `C-ROOK-CELL-TWO-FACTOR-CENSUS` | Exactly89,000 labelled two-factors avoid one fixed matching in K10; independently counted by subset DP and component convolution. [Audit](../acceleration/results/20260930_rook_cell_independent/audit.json). |
| `C-ROOK-FROZEN-WINDOW-ROW-EXCLUSION` | One exact frozen50-vertex external window cannot complete its two missing blocks:167of200 prospective edges violate monotone caps and8rows have insufficient possible neighbors. [Literal59-vertex independent check](../acceleration/results/20260930_independent_review/rook_frozen_window_v2.json). |

All are conditional or finite local results. None assumes a graph automorphism.
The weaker rook witness remains valid for its weaker subsystem despite its
later completion obstruction. The v1 window arithmetic audit is preserved;
v2 repeats it with stronger mutated-record controls.

**Claim registry:** schema/dependency/hash checks passed. The current population
is48 root claim records:46 VERIFIED/CLEAR and2 CANDIDATE/CLEAR. This is a registry
count, not a count of graphs or new mathematical results. New literature claim
`C-LITERATURE-20260930-PRIMARY-SOURCE-AUDIT` stays CANDIDATE. Its
[dated search report](../acceleration/results/20260930_literature_audit/AUDIT.md)
records the post-stop arXiv revision and the order7 source conflict. The bounded
search did not identify a resolution; this is not a statement of worldwide openness.

**Work completed:** domain producer reused17center files and completed67new
centers. The independent path re-enumerated all84 centers and checked every
saved leaf. These center populations form one disjoint84-center batch. The
matching-filter producer subsequently evaluated the same2,290,122 choices,
reporting414,908 rejections and1,875,214 survivors with no empty domain. Those
filter decisions are pending full independent verification at this milestone;
do not add them to the domain counts or current verified outcomes.

**Execution:** domain producer and complete-domain checker ended successfully.
The separate matching-filter audit was observed active; its completed per-center
receipts are resumable. The saved
[process observation](../acceleration/results/20260930_resume/first_milestone_process_observation.json)
is time-specific, not perpetual liveness. Separate fixed-rook-star SAT encoding
preparation is ongoing. No eight-coordinate LP/GPU solve has been launched.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator.
Complete local domain enumeration covers this precisely frozen conditional
domain universe only. The89,000factor count is a different local population.

**Best result:** the prior exact positive six-coordinate support bound
`14157/16384` remains the latest exclusion in the widening coordinate series.
The new eight-coordinate nonpositive transfer result is about a different
family; it is neither a worse target graph nor evidence of feasibility.

**Problems and pending work:** no independent veto occurred in the completed
audits. The full matching-filter verification, moment-matrix construction and
audit, and fixed-star SAT encoding review remain outstanding. Filter raw records
above10MiB have exact gzip companions indexed in their manifest and
`docs/local-artifacts.json`. Public replay must restore these exact bytes.
The first registrar preparation rejected a string where the schema required
an array; no ledger was written until that bookkeeping error was corrected.

**Next experiment:** finish the full independent matching-filter audit, then
build the [exact moment model](NEXT_20260930_EIGHT_MOMENT_BUILD.md) and check every
column independently before numerical optimization. The separate SAT lane
tests a fixed rook-cell star and cannot establish unrestricted nonexistence.
