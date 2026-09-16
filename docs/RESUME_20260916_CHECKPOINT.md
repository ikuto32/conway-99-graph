# Resume checkpoint, 2026-09-16

At restart, saved results had progressed beyond the September5 section of
`ACTIVE_RESEARCH.md`. Its new September16 section now links this audit. No valid
`srg(99,14,1,2)` or complete nonexistence proof is established by this audit.
This review did not start any search, change the central ledger, edit historical
artifacts, or write inside `external_conway99_research`.

## E72 small5: another complete macro is available

The independent catalog/hash/result audit was replayed against the monotone
union of the stopped and latest runner manifests. All outputs use new
`scratch_resume_20260916_*` paths. The new audit scripts are copies of the
existing independent auditors with only their output paths, union path, and
corresponding audit-module import changed; producer and solver were not imported.

| Macro in source 150 | Audited records | Catalog mass | Outcome |
|---|---:|---:|---|
| `(1,0)` / m10 | 96 / 96 | 8,192 | Complete, all UNSAT; previously credited |
| `(3,3)` / m33 | 116 / 116 | 8,192 | Complete, all UNSAT; credited in the isolated successor ledger |
| `(9,0)` / m90 | 0 / 52 | 4,096 | No completed primary shard audited |
| `(10,0)` / m100 | 0 / 63 | 8,192 | No completed primary shard audited |
| `(11,0)` / m110 | 0 / 73 | 8,192 | No completed primary shard audited |

The current independent total is **27 / 52 shards, 212 / 400 records, and
16,384 UNSAT mass**. The preserved September5 history says 26 shards, 204 records,
15,840 mass, and m33 missing records 104–111. Those eight records completed in
`scratch_theory_e72_source150_sync_jointprimary_small5_m33_r104_112.json`
(SHA256 `2304109FC631708E51E922E25DB831CAC4F5E0B26AC35A9970AE5187039C3582`).
Their mass is 544. All m33 records are now covered exactly once.

The new immutable m33 evidence is
`scratch_resume_20260916_small5_m33_complete_audit.json`, SHA256
`90B2D1FD30D58B63092900BE225247322FFE652D5B34367001EA664AA5A6B929`.
This is hash-bound finite-CSP executable evidence, without DRAT. It excludes
only the specified restricted macro under its audited encoding; it is not a
full E72 or Conway nonexistence proof. The replay validates saved execution
results and independently reconstructs the catalog; it does not rerun the CSP.

The unchanged central inventory SHA256 is
`A9F2F186B6818E5A4B953607EB419B1CBE7744BED1E715E965BAE2C451A91D98`.
It still reports unresolved coverage 450,560, source150 open coverage 28,672,
and exact executable non-DRAT coverage 4,833,280. It remains preserved as the
historical ledger. Current accounting is now in the isolated successor
`scratch_resume_20260916_e72_complete_coverage_inventory.json`, SHA256
`17B70058E3AF50A839AE71203982DA5292369CF0B3114934527A274FF1F035FB`.
Its unresolved coverage is **442,368**, source150 open coverage **20,480**,
and exact executable non-DRAT coverage **4,841,472**.

`scratch_resume_20260916_m33_inventory.py` creates this successor after
checking all 25 historical input hashes, the immutable certificate and code
hashes, the macro catalog, and all 116 records across 15 shards. A separate
process runs `scratch_resume_20260916_m33_inventory_audit.py`; this checker
imports no inventory producer and independently reverses the exact m33
transition. The restored whole document equals the historical inventory.
Both inventories' bucket and macro partitions also balance. See
`scratch_resume_20260916_m33_inventory_delta_audit.json`. Only macro
`(150,3,3)` moves by 8,192; prior m10/m03 credits, DRAT, and unproved-terminal
coverage are unchanged. The historical ledger bytes and producer are untouched.

## Process state and failures

At **2026-09-16 11:36:18 +09:00**, no small5 runner, synchronized-config CSP
worker, or m03 runner was found. The historical PIDs 8280 and 22500 were absent.
See `scratch_resume_20260916_process_snapshot.json`. The saved manifest's
`RUNNING` string and `ACTIVE_RESEARCH.md` statements that small5 remains live
are stale; neither is liveness evidence.

The latest small5 log ends on 2026-09-05 at 13:17:13 JST after five failed m90
shards. Ranges 0–8, 8–16, 16–24, and 24–32 returned code 1; range 32–40 returned
1073807364. Saved stdout/stderr tails are empty, so their cause is undiagnosed.
No mathematical outcome or exclusion follows from these failures. Restarting
the original runner unchanged would conceal this unresolved execution problem.

## Latest overlap work is beyond the five-cut CP-SAT UNKNOWN

The independent walk audit was replayed successfully. Three legal two-edge
trades take the original overlap assignment to
`scratch_follow_overlap_walk.json`, SHA256
`6a6bf921f1c6cf37e722ed5a256382cf1a9de03d3449e6e4814529ce85be661a`.
All 14,553 pair-cap checks across the three intermediate 99-vertex partial
graphs pass, as do overlap totals and label quotas. The final assignment has
168 overlap edges and 357 exposed graph edges.

It passes **all 640 sign-conjugate compiled cuts**. The five orbit minima are
`[292, 7207, 9083, 8957, 7522]`. This is a genuine candidate for stronger
completion checks, although 336 disjoint edges are still missing. Passing
the cut bank is not a completion witness. The new replay result is
`scratch_resume_20260916_overlap_walk_audit.json`.

The saved continuous completion attempt has 4,662 constraints and explicitly
omits disjoint compression totals. It ended `LP_ABNORMAL_NO_CONCLUSION`.
Its separate 30-second dual attempt ended `NO_EXACT_CERTIFICATE`. At that
historical checkpoint the walk survivor had neither a linear-completion
witness nor a checked infeasibility certificate. Neither historical status
is UNSAT. The new result below resolves this fixed-assignment uncertainty.

The independent cycle-capacity audit was also replayed successfully to a new
output. The five historical assignments have 630 integer flow witnesses,
798 implied cycle-union Hall inequalities, and 133 weighted cycle tests in
total. These are positive controls for weaker projections; the same five
assignments remain excluded by their stronger checked capacity certificates.

The historical trade audit records all 135,240 alternate matchings from 67,620
disjoint source-edge pairs, yielding 677 legal one-trade neighbors across five
sources. All 677 still violate a conjugate own cut. Its source code and all
14 recorded input hashes match the saved audit; the full 677-graph audit was
not rerun in this checkpoint review. The three-step survivor goes beyond that
one-trade obstruction.

The saved parity experiment supplies a mod-2 control. Its later mod-4 file
states that this particular parity control has no carry lift. Those results
were inspected, not independently replayed here; they cannot exclude all
parities, the compression, or E0=0.

## New completion result during this resume

The new HiGHS run in `acceleration/results/20260916_walk_highs.json` produces
an integer capacity certificate for the three-trade survivor. The separate
standard-library checker `acceleration/audit_certificate.py` rebuilds the
full 99-vertex adjacency and derives each selected constraint without importing
the producer or solver. It verifies 678 signed label equalities, 398 pair
caps with nonnegative weights, and 196 positive edge upper-bound weights.
All 1,680 combined variable coefficients are nonnegative, while the combined
right-hand side is **-107,551**. Consequently this specific overlap assignment
has no completion even in the necessary continuous linear relaxation without
disjoint compression totals. See
`acceleration/results/20260916_walk_highs_audit.json`.

The separate `acceleration/review_linear_mapping.py` compares the producer's
actual pure row-building code to the independent full-graph semantics. All
4,199 emitted rows agree: 840 equalities and 3,359 pair caps. The 463 rows
omitted from the earlier 4,662-row model are exactly 336 empty equality
tautologies and 127 empty pair-cap tautologies. Eight deliberate certificate
corruptions are rejected, and a missing certificate remains a no-conclusion
result. See `acceleration/results/20260916_walk_linear_mapping_review.json`.

The additional sixth cut is useful: its source assignment survived all 640
old cuts. Direct full-graph evaluation agrees with the prepared reusable cut
on all 128 sign images. The sixth-cut orbit minimum is -107,551, with exactly
one negative fixed-index sign image. Its full 128-sign family is therefore
needed just like the previous five families. See
`acceleration/results/20260916_sixth_cut_semantic_review.json`.

## Concrete next actions

1. Use the audited three-trade assignment as an accelerated-search seed and
   include its newly checked sixth cut when screening different assignments.
   Before trusting a new Rust/GPU kernel, compare its exact trade legality,
   pair-cap checks, and 640-cut scores against the independent Python outputs.
   Keep exact independent validation at candidate and certificate boundaries.
2. Apply the repaired HiGHS completion path to new cut survivors, retaining
   independent checks of every reconstructed exact dual certificate. A passing
   linear relaxation still needs integer reciprocity and all nonlinear
   common-neighbor equalities.
3. If E72 m90 is resumed, first diagnose the failed shard under captured stderr
   and bounded resource use. Do not restart m03 or re-enumerate credited macros.

Replay commands from the repository root:

```text
python scratch_resume_20260916_small5_audit.py
python scratch_resume_20260916_overlap_walk_audit.py
python scratch_resume_20260916_cycle_capacity_audit.py
python scratch_resume_20260916_m33_inventory_audit.py
```
