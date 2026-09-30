# Explicit ordered exact-eight build batches — source-only preparation

No execution is authorized by this file itself. Root chooses a later selection
after reviewing the first12 outcomes; this source is prepared without calling its
plan/build modes, any producer build, or a native solver. It never infers an
unattempted population by reading outcome directories, never drops historical
profiles, and never treats native exit20 as a verified exclusion.

CLI:

```text
plan|build --selection PATH --selection-sha256 SHA
  --attempt-id LABEL --seconds 1..120 --out NEW
```

The root-controlled selection must be a separately saved JSON artifact:

```json
{
  "schema": "EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1",
  "campaign_manifest_path": "acceleration/results/20260930_exact_eight_campaign_preparation/campaign_manifest.json",
  "campaign_manifest_sha256": "e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba",
  "ordered_case_ids": ["exact_eight_<full canonical 64hex digest>"],
  "selection_reason": "Root's explicit scientific allocation; not inferred by the builder.",
  "authorization_record_path": "<repository-relative frozen plan or instruction record>",
  "authorization_record_sha256": "<exact SHA256>"
}
```

The plan record authenticates the stated selection provenance, not an automated
proof of user authorization. Ordered IDs must be nonempty, unique, and literal
members of the complete authenticated792 universe. The ordering is supplied by
the caller; no sorting, prior-proof subtraction, deduplication or autoskip occurs.
Both selection and authorization bytes are hash-bound. Absolute/escaping paths,
changed manifest, unknown or repeated IDs, unsafe attempt IDs and invalid budgets
are refused. There is no automatic resume option.

`plan` authenticates inputs and writes the exact child commands only. `build`
invokes only the frozen parameterized Python producer in the existing locked
environment. It allocates at most the explicit cumulative120-second budget,
preserves every command/stdout/stderr/exit/timeout receipt and complete-prefix
checkpoint, and stops on the first failure or exhausted budget. The child may
leave an incomplete folder on timeout; that case remains pending and never gains
a complete-formula record. All output folders must be new. A subsequent attempt
requires a new explicit selection and new output/attempt paths. Selecting an
already built or proved case deliberately rebuilds it; no prior result is reused.

Each successful case summary and every declared source/output hash are checked.
The result retains stable case/index/subset/full-count identity and a separate
build attempt identity, plus all20 initial sizes and actual CNF/model/scope/profile
and rank-list/package pins. The frozen producer, its weighted helper, balanced
helper, specs, environment locks, manifest and its independent all792 population
gate are pinned. The independent gate approves the existing12 encodings only;
each newly built formula remains CANDIDATE and requires a new encoding audit.

No native command or SAT outcome handling exists in this source. Future native
allocation, object calibration and complete proof/outcome gates remain separate.
New selection artifacts and build results are not created during source-only
preparation. AST and isolated selection/error controls may run without invoking
the wrapper or importing any repository module.
