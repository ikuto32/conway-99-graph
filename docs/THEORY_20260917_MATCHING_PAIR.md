# Independently verified update

Claims `C-STAR-MATCHING-PAIR-18481` and `C-STAR-FILTER-COMPARISON-18481`, revision1,
are VERIFIED/CLEAR in [the root ledger](../CLAIMS.yaml). The independent checker
replayed806 deletions and all final directed arcs, leaving15,335 original-ID
choices. See [written audit](../acceleration/results/20260917_independent_review/MATCHING_PAIR_AUDIT.md)
and [second milestone](RESEARCH_20260917_SECOND_WAVE.md). No new fixed-K exclusion
or target resolution follows from nonempty arc consistency.

## Preserved producer-stage report

# Exact pair propagation after the verified neighborhood matching filter

Status: **CANDIDATE, pending independent review**. The bounded continuation
completed with no empty domain. It leaves 15,335 star choices across all 84
outer vertices of baseline18481. This is a stronger necessary local
relaxation, not a simultaneous graph or a new fixed-K exclusion.

## Starting point and frozen question

The input is precisely the 19,494 surviving choices from
`C-STAR-TRIANGLE-FILTER-18481` revision 1, whose independent audit is
`acceleration/results/20260917_independent_review/triangle_matching/summary.json`.
The 26,250 historical original choices and their IDs remain unchanged.
The new input is explicitly a **sound filtered subdomain**, and is never
labeled an original complete domain enumeration. No additional restriction
from the old pair-AC survivor set was imposed before this experiment.

The manifest, written before the two propagation phases, asks whether exact
reciprocity followed by all completed-neighborhood pair constraints empties
one of these filtered domains. It freezes the matching survivor IDs, all
input/source/executable hashes, the rules, a 60-second limit per phase, and
500,000,000 choice-pair comparisons for the native phase. A cap or execution
error gives an incomplete result rather than an exclusion. The run uses no
randomness, numerical optimizer, or floating-point acceptance criterion.

## Necessary propagation and index mapping

For each original star ID `i` at vertex `u`, let `S(u,i)` be its eight chosen
disjoint-support outer neighbors, and let `N(u,i)` contain these neighbors
plus all fixed root-label and overlapping-support neighbors. The latter is
the full 14-vertex final neighborhood selected by that star.

The first phase requires reciprocal disjoint-edge decisions. Remove choice
`i` at `u` if no current choice `j` at `v` satisfies

```text
[v in S(u,i)] = [u in S(v,j)].
```

The second phase additionally requires, for every outer pair,

```text
[v in N(u,i)] = [u in N(v,j)]
|N(u,i) intersect N(v,j)| = 2 - [v in N(u,i)].
```

These are necessary in every completion. A choice belonging to a global
completion has a supporting choice at every other vertex from that same
completion, so induction shows every unsupported-choice deletion preserves
all global completions. This argument is conditional on the independently
validated matching-filter premise and the fixed overlap assignment. No
nontrivial automorphism is assumed. Nonempty arc consistency is insufficient
because the supporting choices for different pairs need not agree globally.

The wrapper first implements exact Boolean reciprocity propagation. It then
reuses the existing hash-pinned `acceleration/build/pair_domains.exe` without
altering its Rust source or binary. The native input uses packed consecutive
indices, while `packed_to_original_ids.json` freezes their map to the
historical original IDs. `native.json` is preserved unchanged;
`translated_pairs.json` translates every deletion and survivor back to
original IDs. These files explicitly state their filtered-domain scope.

## Saved producer outcome

| Stage | Star choices | Deletion events |
| --- | ---: | ---: |
| Verified matching-filter input | 19,494 | Not a new propagation stage |
| New reciprocal-edge closure | 19,494 | 0 |
| New exact full-pair closure | 15,335 | 806 |

The pair phase removes 4,159 choices from its input. It completes all 3,486
unordered outer-vertex relations and 187,493,780 star-choice comparisons.
Every vertex retains choices, and no resource cap is hit. Observed phase
times were 0.081108 seconds for reciprocity and 0.452641 seconds for native
pair propagation; these are individual measurements, not general speed
guarantees. The populations in the table are successive stages, not
disjoint sets to be added together.

Producer controls include reciprocal singleton acceptance, a forced
reciprocity deletion, deliberately inconsistent singleton rejection, and
zero-time-cap handling. Native controls use the actual filtered input:
a one-comparison limit produces `INCOMPLETE` with `DOMAIN_PAIR_CAP`, while
a deliberately zero-bit star is rejected by the parser and produces no
result artifact. These are calibration checks by the producer, not the
independent verification of this result.

## Reproducibility and independent review

Source at execution: `3daebfb05d39aa31afea6fdbb6b80d6b108f1262`.
The new wrapper's uncommitted bytes are additionally bound in the manifest.

Producer: `acceleration/theory_20260917_matching_pair.py`.
Evidence directory:
`acceleration/results/20260917_theory/matching_pair_baseline18481/`.

`manifest.json` freezes the question, all initial original IDs and hashes;
`reciprocity.json` records the first closure;
`packed_to_original_ids.json`, `candidate.txt`, and `domains.txt` fix the
native input; `native.json` and `translated_pairs.json` retain every new
deletion; and `summary.json` binds the complete output inventory. Exact
native commands, working directory, timestamps, exit codes, and output/log
hashes are in their corresponding `*_receipt.json` files. All existing
research source and evidence files were left unchanged.

The independent verifier receives the raw artifacts and should:

1. Verify the matching-filter audit's exact hash bindings and the complete
   input-to-packed-to-original index mapping.
2. Reconstruct final neighborhoods independently and replay every deletion
   using explicit reciprocity and common-neighbor set intersections.
3. Check that every final choice has a compatible final choice at every
   other vertex, or verify an empty-domain trace if one is claimed.
4. Run separate positive/corrupted controls. Merely rerunning the wrapper
   or agreeing with its output is insufficient.

Use the existing pinned environment and a fresh output directory to replay:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_matching_pair.py --out build/matching_pair_replay --seconds 60 --pair-cap 500000000
```

The actual run used the command above with output
`acceleration/results/20260917_theory/matching_pair_baseline18481`.
No new environment was created. The lockfile and binary hashes identify
the required execution components; a replay machine must have the pinned
native executable or rebuild its unchanged source and record the resulting
compiler version/binary hash separately.

Completed stages, original IDs, and deletion trails form a retained
checkpoint. An interrupted reciprocity phase also saves its pending arcs.
The frozen native input can be rerun with a fresh result filename and a
documented larger cap. A subsequent implementation may start from recorded
survivor IDs only after preserving and checking all earlier deletions;
the current native engine rebuilds its relation cache and does not resume
an in-memory queue. This completed run left no computational worker running.

## Unrestricted obstacle and next experiment

The surviving 15,335 choices still require one mutually compatible global
selection. The matching filter only establishes separately permissible
matching edges; those edges can conflict when added together. Baseline18481
was already excluded by independent linear evidence, so no graph-construction
or target-level conclusion follows from continuing to refine this control.

After independent review, a concrete next structural test is to require
each matching to be jointly addable with all partial pair caps, then repeat
the existing propagation. Applying the validated cheap filter to fresh
overlap candidates is a separate construction-search use. Overall search
coverage: UNKNOWN; no validated denominator.
