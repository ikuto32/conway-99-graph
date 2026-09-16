# Complete atomic matching-cycle subfamilies

`overlap_cycle_neighbors.rs` implements the three-edge and four-edge atomic
matching cycles specified in [ATOMIC_CYCLE_PLAN.md](ATOMIC_CYCLE_PLAN.md).
It is dependency-free and separate from every previously frozen generator.

```powershell
rustc -O -C target-cpu=native acceleration/overlap_cycle_neighbors.rs -o acceleration/build/overlap_cycle_neighbors.exe
acceleration/build/overlap_cycle_neighbors.exe INPUT.txt OUTPUT.json 3
acceleration/build/overlap_cycle_neighbors.exe INPUT.txt OTHER_OUTPUT.json both
```

Input is `C99OVERLAPS1 1` followed by exactly 168 canonical, zero-based overlap
edges. The optional final argument is `3`, `4`, or `both`, defaulting to `3`.
Existing output files are rejected. There is no seed or sampling limit: every
legal final candidate in the selected subfamily is emitted deterministically.

The input is checked for overlap support, duplicate/range errors, degree four
in K, all full-99 partial pair caps and exact own-label quotas. The 21 perfect
matchings are recovered and their sizes and degree-one property checked.
Every replacement is applied atomically; all affected full-99 row pairs and
own-label quotas are checked only on the final state. Intermediate legality
is not required. Neither star domains nor pair AC are computed here.

## Output contract

The status is `COMPLETE_ATOMIC_CYCLE_SUBFAMILY_ENUMERATION`.
`overlap_candidates[i]` is the complete sorted 168-edge final K for `moves[i]`.
Each move contains:

- `removed`, `added`: sorted lists of `k` canonical zero-based edges;
- `root_group`: integer in `0..6`;
- `matching_class`: `same_0`, `same_1`, or `cross`, referring to signs within
  the selected root group;
- `cycle_size`: integer `k`, either three or four;
- `alternating_cycle`: `2k` distinct zero-based outer vertices with no
  repeated closure. Removed edges are `(v0,v1),(v2,v3),...`; added edges are
  `(v1,v2),(v3,v4),...,(v[2k-1],v0)`.

Top-level `cycle_size` is the requested mode string. `raw_cycles` and
`legal_cycles` give totals. `by_class` contains one record per requested size
and matching class, with raw, support-rejected, cap-rejected and legal counts.
All outputs have distinct final edge sets; a duplicate is an implementation
error, not silently removed.

Completeness covers **one connected alternating cycle inside one matching**
for the requested sizes. It does not cover multi-cycle replacements, all
degree-preserving moves, other E0 regimes, or the global graph search space.
Raw counts are always 5,320 for size three and 30,870 for size four; legal
counts depend on K. A caller must still perform its chosen final necessary
conditions, such as complete-domain pair AC.

## Independent validation and timing

`results/20260916_atomic_cycle_qa/qa.json` binds the source, executable, input,
native results, independent audit and mode checks. The authoritative saved
7.3321220137 seed produced:

| Mode | Raw moves | Legal final states | Native seconds |
| --- | ---: | ---: | ---: |
| `3` | 5,320 | 2,940 | 0.0266 |
| `4` | 30,870 | 13,359 | 0.1279 |
| `both` | 36,190 | 16,299 | 0.1571 |

Times include enumeration and JSON formatting, excluding input parsing and
the final file write. They describe this finite control, not a guaranteed
runtime for a complete search.

`audit_atomic_cycle_family.py` uses a different construction: recursively
enumerated endpoint perfect matchings, or bipartite bijections, followed by a
connected-cycle test. It independently checks the raw-count formula,
full-99 set-neighborhood constraints, exact own-label quotas, each final edge
set, metadata and cycle encoding. The complete legal set matched Rust exactly
in 4.26 seconds, with 13,172,589 affected row-pair checks plus the initial full
graph check. No native generator, search driver, or solver is imported.

All per-class rejection counts matched as well. Separate `3` and `4` outputs
equal their exact subsets of `both`; repeated execution and the default mode
matched. Twelve invalid-input/CLI/output-preservation controls were rejected.
The independent auditor rejected omitted moves, duplicate moves, wrong
matching metadata and malformed cycle encodings.

To independently certify a fresh output's stated subfamily coverage:

```powershell
python -B acceleration/audit_atomic_cycle_family.py --candidate INITIAL.json --input INPUT.txt --native OUTPUT.json --out AUDIT.json
```

Frozen Rust source SHA256:
`d6c6563b974050246b14e996a737feb9936d18094257a3b47993d64339aaf41c`.
Windows executable SHA256:
`812373d00ac43e069bd961ed9b173e9c6a83bdac1a7cb34fbd02f4cfee2e8e56`.
These finite generation and completeness controls do not construct a Conway
graph, establish global exhaustion, or certify final pair-AC survival.
