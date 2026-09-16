# E0=0 walk with changing overlap compression

`overlap_wide_walk.rs` is a separate derivative of the frozen Rust kernel. It
removes the two-edge trade requirement that the old and new edges occupy the
same pair of compression blocks. The original scorer and walk remain unchanged.

Every accepted state still has 168 overlap edges on 84 outer vertices, degree
four, exactly one neighbor carrying each of the four labels in its own two root
groups, at most two carrying any other label, and all partial common-neighbor
caps. Every edge joins supports sharing exactly one root group. Same-fibre
edges remain absent. The 1,680 disjoint-support variables are still unknown.
This is a larger local search inside E0=0, not an enumeration of that class.

```powershell
rustc -O -C target-cpu=native acceleration/overlap_wide_walk.rs -o acceleration/build/overlap_wide_walk.exe
acceleration/build/overlap_wide_walk.exe walk acceleration/results/20260916_controls/candidate_5.txt build/wide_walk.json 2000 20260916
python -B acceleration/audit_wide_walk.py build/wide_walk.json --initial scratch_follow_overlap_walk.json --out build/wide_walk_audit.json
```

The saved run is `results/20260916_wide_walk_2000.json`. It took 1.280 seconds,
visited 1,995 distinct edge sets and 1,491 distinct overlap-compression matrices,
and changed compression on 1,498 of 2,000 trades. The original candidate had
511 legal unrestricted trades, compared with 137 at fixed compression.
There are 101 stored snapshots; the farthest, snapshot 36, has compression L1
distance 116 from the initial matrix over unordered block pairs.

`audit_wide_walk.py` independently rebuilds the entire 99-vertex partial graph
after every trade. The saved audit checked 2,001 full graphs, 9,706,851 pair
caps and 2,353,176 label quotas. It binds the trace, initial candidate, generator,
binary and auditor hashes. It does not recheck legal-alternative counts or the
random choice. The seed and full trace permit deterministic replay.

The ten audited capacity inequalities remain valid when overlap compression
changes: their formula uses root-label equalities, pair caps and box bounds,
with no overlap or disjoint compression totals assumed. The existing native
scorers evaluated all 101 × 10 × 128 values, and all 100 noninitial snapshots
survived. See `results/20260916_wide_bank/` for exact score parity artifacts.
Score passage is only a necessary condition. Local star filters and continuous
completion probes remain necessary before attempting a full graph.

The existing `probe_walk.py` deliberately requires a *fixed-compression* walk
audit. For this separate experiment, candidate JSON files are taken from the
independently audited wide trace and passed directly to `ray_probe.py`; its
certificate checker again builds the full partial graph and checks all integer
multipliers. Results live in `results/20260916_wide_probes/`.

The independent local-star filter rejected 55 of the 100 noninitial snapshots;
45 passed all 84 separate star tests. A star witness at every vertex need not
share consistent edge decisions. Snapshots 15, 37 and 100 survived this filter
but were each rejected by a directly extracted HiGHS infeasibility ray, followed
by exact integer reconstruction and independent full-graph certificate checking:

| Snapshot | Compression L1 from initial | Exact combined RHS |
| --- | ---: | ---: |
| 15 | 108 | -14,549 |
| 37 | 104 | -15,145 |
| 100 | 78 | -14,004 |

This generator therefore widens the tested compression domain, but these
particular tests still yield no continuous completion or 99-vertex graph.
