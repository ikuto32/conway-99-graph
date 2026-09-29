# Eighth milestone: exact core counts and local-test limitations

This milestone has six independently checked claims. Read the
[report](RESEARCH_20260930_EIGHTH_WAVE.md),
[ledger snapshot](../acceleration/results/20260930_resume/claims_at_eighth_milestone.yaml)
and [artifact catalog](../acceleration/results/20260930_eighth_artifact_packaging/catalog.json).
All mathematical files selected for this milestone are below 10 MiB and are
published directly; no new oversized recovery or native solver is required.
This does not describe the separate subsequent joint-factor solver run.

Use the unchanged root locked environment. Existing one-shot output directories
must not be overwritten; choose fresh `--out` paths when repeating commands.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_triangle_matching_pair_census.py --out build/eighth-matching-census-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_triangle39_gram_sos.py --out build/eighth-gram-sos-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_triangle_core_identity.py --out build/eighth-identity-construction-recheck
```

The [matching audit](../acceleration/results/20260930_independent_review/triangle_matching_pair_census/summary.json)
checks direct images under every stated centralizer/stabilizer element,
independently of the producer's generator-BFS. The 3,580 orbit classes concern
ordered pairs of perfect matchings on twelve labels, not full target graphs.
The additional permutation is counted in a separate calculation; no target
automorphism is assumed.

The [pair-cap derivation](../acceleration/results/20260930_independent_review/triangle_core_paircap_theorem/summary.json)
establishes the exact reduced permutation conditions. The
[complete recount](../acceleration/results/20260930_independent_review/triangle_core_permutation_census_v2/summary.json)
uses an independently authored squarefree coefficient computation, reversed
pair order, and exhaustive small controls. Use its saved `command` with a new
output directory to reproduce the precise mode and arguments. It checks all
3,580 counts and raw local witnesses. Only 29 distinct permutation arrays occur
among those witnesses across different matching-pair cases.

The first recount wrapper failed on an incorrect expected status name before
counting. Both versions and the failure/correction records are retained. The
matching producer's original output-path formatting failure is likewise
retained; its completed mathematical stage files were byte-identical to the
corrected run. Neither failure refutes a mathematical statement.

The [39-core Gram audit](../acceleration/results/20260930_independent_review/triangle39_gram_sos/summary.json)
contains a universal invariant-subspace/SOS proof, all raw coefficient checks
and independent Fraction-based rank calculations. The 15 fixtures calibrate the
proof; they are not its coverage argument. The
[identity construction audit](../acceleration/results/20260930_independent_review/triangle_core_identity/summary.json)
separately proves that identity cross-fibre matchings supply local witnesses for
all positive even orders. It does not allow replacing an arbitrary target's
permutation by identity without loss of generality.

The [direct row29 audit](../acceleration/results/20260930_independent_review/triangle_wave154_row29_obstruction/summary.json)
reconstructs the necessary constraints from the exact partial graph and checks
all branches and forced bits. It does not use the extracted SAT core as a
premise. Its 139-node tree explains the same fixed Wave154 exclusion already
proved in the seventh milestone, adding no exclusion coverage. Replay its
saved command into a fresh output directory after following the
[seventh guide](REPRODUCING_20260930_SEVENTH_WAVE.md) for any earlier dependencies.

The [archive-overlap record](../acceleration/results/20260930_triangle39_gram_sos/archive_overlap.json)
pins repository, commit, paths and inspected sections. The related 36-factor
Gram mechanism was already present in the archive. Historical VERIFIED labels
are not imported as new verification, and no novelty or complete literature
search is claimed.

Exact source commits, commands, tool versions, raw hashes, control populations,
scope limitations and failure history are in the linked manifests and audits.
Repeating a saved auditor is repeated execution, not a further independent
derivation. Schema/CI checks validate bookkeeping. Overall search coverage:
UNKNOWN; no validated denominator.
