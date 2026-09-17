# Identity-cut application to 29 frozen original-domain records

Status: **CANDIDATE application result, independent application review pending**.
The mathematical clauses themselves were already independently approved in
`matching_positive_cuts_recheck.json`, SHA-256
`3e807d158c7fea05e5a31ec631105fa1733e3ca86ad96549cc46a14dcf3e5fc9`.
The application checked that gate and its bound dependencies before any counts.

The preregistered corpus is the 16 fresh and 13 same-sign candidate records in
`../20260917_matching_cut/next_application_protocol.json`. Original candidate,
outer-vertex, and domain-array IDs are retained throughout. No original domain
file, prior result, or independently audited derivation was changed.

| Named candidate-record population | Candidate records | Original choices | Unique removed choices |
|---|---:|---:|---:|
| fresh16 | 16 | 413,610 | 152 |
| same13 | 13 | 333,454 | 172 |
| Combined disjoint record populations | 29 | 747,064 | 324 |

A choice is a `(candidate record, outer vertex, original domain ID)` tuple.
There are 324 clause hits and 324 unique removed choices; this identity-clause
application has no overlapping hits. All 29 records have removals. The counts
range from 5–13 per fresh candidate and 11–15 per same-sign candidate.
Every vertex retains choices. No full-K exclusion is claimed.

The fast path tests all positive K prerequisites and equality of the selected
eight-neighbor star with the cut's star. A separate direct path constructs the
full positive edge set and tests every literal, for every original choice at
all sixteen named cut centers, including nonhits: 138,556 comparisons agree.
Other centers cannot satisfy a cut because all its eight disjoint star edges
are absent from K/scaffold and one other-center star can add at most one of them.

All 324 removed choices also received a separate full-graph set-neighborhood
check. It adds the entire candidate K and the named original star, reconstructs
the fourteen-neighbor induced matching prerequisites, considers every missing
free-neighbor edge without support/fibre restrictions, checks exact affected
pair caps by set intersection, and searches the resulting graph for a perfect
matching. All 324 searches found none. This is an internal checking path in the
application producer, not a substitute for independent application approval.
The source imports no prior graph builder, cut producer, or matching checker.

Six synthetic controls passed before execution, including positive/negative
literal containment, duplicate-hit union accounting, a permissive windmill,
and rejection of a corrupted adjacent cap. The controls-only run is preserved
separately in `../20260917_matching_cut_application_controls/controls.json`.

The run completed 29 of 29 selected records in 2.078 seconds of measured wall
time, within the preregistered 180-second limit. Exact commands, interpreter,
source commit, hashes, and the independent cut gate are in `manifest.json`.
`summary.json` binds all 29 per-candidate outputs, which preserve each clause's
missing/matched K prerequisites, hit original IDs and masks, union membership,
overlap sets, matching-check graphs, and surviving-domain counts.

Reproduction from the repository root, using an unused output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_matching_cut_apply.py --out build/matching-cut-application-new --seconds 180
```

The script refuses a changed gate/corpus or an existing completed output. It
does not perform any root-sign-flip or wider orbit expansion. This finite
application establishes no overall target coverage, minimality, or unrestricted
nonexistence. Overall search coverage: UNKNOWN; no validated denominator.
