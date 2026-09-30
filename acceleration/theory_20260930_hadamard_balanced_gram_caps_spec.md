# Complete outside-column-cap extension for the balanced Gram model

Freeze before build: enumerate **all**190 pairs of distinct support groups and all150-by150 local-option pairs in each, with no ranking, sampling, omitted case or symmetry assumption. Also check every pair of the three raw columns inside each of the3000 local options. No native solver is invoked.

Base input remains the exact10,480-variable/74,200-clause balanced fixed-support Gram formula. This new artifact appends constraints only. It does not rewrite the base CNF, model, scope, source or prior results. The base construction class fixes one Hadamard support and imposes balance; neither is WLOG for Conway99. No target automorphism is assumed. Residual D is not encoded.

For selected local options in groups g<h, a cap conflict means that at least one of their nine actual36-row column pairs has intersection larger than two. Such a pair of options is forbidden by the negative two-selector clause. A within-option cap conflict, if present, yields a negative selector unit. Existing exact-one constraints ensure these clauses are equivalent to all outside-column common-core-neighbour caps.

The twenty groups partition the sixty columns. There are60 within-group column pairs and1710 between-group column pairs, totaling all1770 without overlap. There are9000 within-option intersections and4,275,000 between-group option pairs; the build computes all nine literal bit intersections for each latter pair (38,475,000 intersections). These are model-population counts, not counts of full factors or target coverage.

## Exact fast route and full comparison

Let S be the shared coordinate set of two supports. A raw column intersection can only occur at a shared coordinate with the same fibre color. An intersection exceeds two exactly when some three-element subset of S has equal color words in one left and one right column. For each shared triple, encode its three-color word in base3 (0..26); represent each local option's three projected words by a27-bit mask. A nonempty mask intersection for any shared triple is therefore precisely a forbidden option pair. If |S|<3, no cap conflict is possible.

This argument covers arbitrary observed shared-support sizes; it does not assume the anticipated0/3 sizes. The build records the actual support-intersection histogram. For **every** research option pair, the fast predicate is compared with all nine literal36-row bit intersections. A mismatch stops the build and preserves the record. The fast path does not approve itself or replace the later independent full input/domain/clause audit.

Before the research enumeration, calibrate all216 ordered local permutation profiles on three shared coordinates against one another (46,656 pairs), a positive cap conflict and corrupted projection mask, negative binary nogood truth tables, and a deliberately duplicated within-option column. Reuse the frozen base's generic SRG243 factor arithmetic controls with explicit code sharing; this is not a research-family factor witness.

## Artifacts and limits

Allocation120 seconds for one exact build, no solver. tqdm reports progress over190 support-group pairs. After each pair save an immutable pair record and append a progress checkpoint containing its hashes/counts. A failed prefix remains intact. No automatic retry/resume is scheduled; any later continuation must name its exact checkpoint and preserve its source/protocol.

Artifacts: raw `clauses.cnfpart`; each pair's150 forbidden-right bitmaps and exact count/offset; `within_group_checks.json`; a frozen `extension.json` indexing all pair records and binding base inputs; a new `scope.json`; and `instance.cnf`, which is exactly the original base body plus the new suffix under a changed clause-count header. All inputs, source commit, command, dependency versions, result and output hashes are recorded. No claim is promoted by construction.

The base independent encoding/object gate is an explicit necessary review dependency. If it is still being produced at build time, the manifest says so with null/reason rather than inventing a report. Independent review of this extension must bind the subsequently frozen exact base gate before use.

Decoder API `decode(assignment, extension_path, cnf_path)` first checks the complete augmented assignment/formula, calls the pinned base decoder on the original formula, and then requires all1770 cap diagnostics empty. It preserves the base raw36-by60 factor/schema/canonical C0 order, adding extension and augmented-CNF hashes. Any SAT result is still a partial incidence factor, not a99-vertex graph or a residual completion.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_balanced_gram_caps.py --out acceleration/results/20260930_hadamard_balanced_gram_caps
```
