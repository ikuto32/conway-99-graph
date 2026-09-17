# Fresh original-star GPU ranking from the whole same-sign family

Prepared; **no fresh native-domain, GPU, or LP computation has been launched**.
The active request is the balanced revision in
`acceleration/results/20260917_whole_fresh_v2_balanced/request.json`, SHA256
`a862f335257ab6bc3c674f9804cfb1eebc0999fa8151dd7fa3005404936b897e`.
Its validate-only preflight passes. Independent review of the new family
mapping is required before execution; a separate ranking audit is required
before selecting up to 16 candidates for independent domain/LP evaluation.

## Exact population and selection

The bound family is
`acceleration/results/20260917_same_star_round/family/all.json`. Its existing
independent audit establishes 81,000 legal noninitial configurations obtained
by replacing one of the 14 same-sign matchings at the single fixed base K.
It does not enumerate arbitrary overlap configurations or Conway graphs.

Saved 2,000-iteration refined old-edge GPU upper scores exist for 2,048
distinct members of this family. The new selection uses only this named
scored population. Exact graph identities exclude 86 of these: the 64
already LP-evaluated members from the current same-sign run and 22 graph
identities recorded in its bound previous-candidate inventory. Thus 1,962
unused refined-score members are eligible. These stages are not additive.
The old-edge scores are heuristic selection inputs, not certificates.

The balanced request freezes 128 distinct eligible graph identities:

1. Choose the 64 smallest `(refined_upper, whole_family_index)` values.
2. Remove those 64. Partition the remaining candidates first into the 14
   sorted coordinates `(root_group, matching_class)`, then within each
   coordinate into sorted alternating-cycle shapes. A shape is the sorted
   list of numbers of changed matching edges in all its cycles, for example
   `[2,4]`; it is not a fabricated single cycle size.
3. Cycle through all 14 coordinates. On each coordinate's turn, rotate
   through its fixed sorted shape list from its retained cursor, skipping
   empty buckets, and take the smallest `(refined_upper,index)` from the
   first nonempty bucket. Advance the shape cursor after every inspected
   bucket, including empty buckets. Repeat until 64 further members have
   been selected.

Every coordinate has eligible entries for this wave. Its diversity half
contains five choices from each of the first eight sorted coordinates and
four from each of the other six. Both halves together cover all 14
coordinates. This is stratified sampling, not exhaustive family ranking.

## Preserved pre-result protocol correction

The first preparation, request SHA256
`91fac98fd7fab7b1e040421de4c77e0218afa09d9d104cd9e19d98d8905c8ae5`,
used a flat lexicographic loop over `(coordinate,cycle_shape)` strata. Its
64 diversity choices covered 64 different shapes/coordinate strata but only
seven coordinates. The lead researcher rejected that selection policy
before any GPU result. Its source, raw candidates, request, successful
preflight and 15 producer controls remain intact under
`acceleration/results/20260917_whole_fresh_v2/`.

The active balanced revision changes the sampling rule only. It preserves
the first 64 global choices, objective, 500-iteration budget, model, exporter,
GPU code, and acceptance rules. The two preparations overlap in 99 candidate
identities; they must not be reported as 256 distinct evaluated candidates.
Neither has evaluated any candidate in a new numerical run.
`protocol_deviation.json` in the balanced directory binds both request
hashes, policies, source hashes, and stage-specific coordinate counts.

## Honest whole-family mapping

The old ranker accepted a cross-cycle extraction with an
`original_native_indices` remapping. This whole family is already the
original native output. Its zero-based family row is its native index:
`proposal_index = whole_family_index = original_native_index`. The request
states `ZERO_BASED_COMPLETE_WHOLE_FAMILY_ROW` explicitly. No cross-family
status or fake extraction table is introduced.

Each request record preserves `root_group`, `matching_class` (`same_0` or
`same_1`), `changed_edges`, and `alternating_cycle_sizes`, including disjoint
multiple cycles and 2–6 changed edges. Preflight reconstructs each selected
matching replacement from its removed/added edges and the fixed base,
checks its actual partial graph, and binds a separately materialized raw
candidate JSON plus a canonical 168-edge hash. It replays the deterministic
score selection and excludes already evaluated exact graph identities.

The active code is `acceleration/rank_fresh_whole_v2_balanced.py`, with
producer controls in `acceleration/qa_fresh_whole_v2_balanced.py`. The
superseded attempt's separately named sources remain unchanged. Existing
rankers, auditors, model builders, native executables, and GPU source were
not edited. The v2 wrapper reuses hash-pinned schema/checking helpers and
copies the original batch execution structure with whole-family metadata
and version changes. The numerical model builder and binary exporter remain
the existing pinned implementations.

## Execution scope and safeguards

The intended numerical objective is `ORIGINAL_STAR_SIMPLEX_PDHG_V1`:
one probability simplex over each **original** native star domain, reciprocal
edge marginals and the original retained linear caps. It is the original-star
ranking model, not `TRIANGLE_PAIR_FILTERED_STAR_SIMPLEX_V1`. Neither reciprocal
nor full-pair propagation survivors replace the original domains.

The wave is fixed at 128 candidates and 500 GPU iterations, with uniform
per-simplex probabilities, zero dual initialization, and float64 arithmetic.
Saved scores cover the initial state and the requested last/average
checkpoint. The existing per-candidate native caps remain one second,
2,000,000 nodes, and 20,000 choices per vertex. Existing binary/GPU limits
are preserved, including 8,192 choices per simplex, 100,000 variables per
model, 32 candidates per chunk, and the other manifest limits. Capped, empty,
or unsupported cases remain explicitly unavailable; they are not exclusions
and are not silently replaced with more favorable candidates.

The producer controls test positive mapping, duplicate/already-used IDs,
fake cross status, wrong native index, cycle shape/class, graph/file hash,
score, objective, iteration cap, source binding, corrupted cycles, and the
unreviewed execution gate. They are engineering controls, not independent
mathematical verification. The independent mapping reviewer should derive
cycle shapes separately from actual removed/added edge components and
reproduce the full selection.

`--execute` refuses to start without an
`INDEPENDENT_WHOLE_FRESH_V2_MAPPING_PASS` report binding the exact active
source, old shared helper source, request, family and family audit, and the
exact selected indices. This is an internal evidence gate, not an additional
user-permission request. The wrapper does not perform shortlist evaluation.
After a separate ranking audit, the intended shortlist is the union of the
eight lowest numerical upper and eight lowest numerical lower scores,
filling overlaps in upper-score order to 16 where enough scored candidates
exist. Independent complete-domain checking and exact LP certificates remain
separate obligations for each evaluated member.

## Commands and state

Preparation and preflight used source commit
`3daebfb05d39aa31afea6fdbb6b80d6b108f1262`, with new source hashes recorded
separately. Use the existing locked environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/rank_fresh_whole_v2_balanced.py --validate-only --indices acceleration/results/20260917_whole_fresh_v2_balanced/request.json --out acceleration/results/20260917_whole_fresh_v2_balanced/ranking
```

After a mapping PASS exists, the concrete execution command is:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/rank_fresh_whole_v2_balanced.py --execute --indices acceleration/results/20260917_whole_fresh_v2_balanced/request.json --out acceleration/results/20260917_whole_fresh_v2_balanced/ranking --mapping-audit PATH_TO_BALANCED_MAPPING_AUDIT.json
```

The output must not already exist. At preparation delivery, neither attempt
has a ranking output directory or launched domain/GPU/LP subprocess. No
mathematical claim has changed through this preparation. Target resolution
remains UNKNOWN. Overall search coverage: UNKNOWN; no validated denominator.
