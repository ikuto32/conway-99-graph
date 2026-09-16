# Source150 largest-macro shard and causal-core audit

Status: **SOURCE150_M47_EXACT_SHARD_AUDIT_PASS**.

This is a full sweep of the two source150 macros `(4,0)` and `(7,0)`, whose
catalogue coverage is 524,288 each. It checks every canonical local-graph
orbit: records `0..1055` of `(4,0)` and records `0..1311` of `(7,0)`.

| macro | exact excluded local orbits | labelled coverage |
|:---:|---:|---:|
| `(4,0)` | 1,056 | 524,288 |
| `(7,0)` | 1,312 | 524,288 |
| total | 2,368 | 1,048,576 |

All 2,368 branches are exact local UNSAT.  The original head/tail shards use
the synchronized exceptional recurrence and pair-upper CSP; two tail
branches initially satisfy that subsystem but are excluded after the exact
ordinary-fibre pair-map feasibility test.  The added contiguous `(4,0)`
records `16..1039` all use that same exact ordinary-fibre pair filter and have
no SAT or UNKNOWN result.  So do the added `(7,0)` records `10..265`.
For records `266..1295`, the two-block existential projection rejects 323
orbits directly; the remaining 707 are all rejected by the ordinary-fibre
pair filter.  No DRAT certificate is claimed.

## Common two-block causal kernel

For one low-node representative of each macro, existentially project away
ten of the twelve disjoint exceptional--exceptional blocks.  The remaining
two blocks already form a cardinality-minimal UNSAT relaxation:

```
02 -- 13
03 -- 12
```

These are local fibre pairs `[0,5]` and `[1,4]` in the source150 ordering.

- For macro `(7,0)`, recurrence at the endpoints of `02--13` permits only
  global ordinary configurations 4 through 15, while `03--12` permits only
  52 through 63.  The sets are disjoint.
- For macro `(4,0)`, recurrence eliminates every block-option pair except
  `(1,1)`.  That pair creates two common neighbours for the nonadjacent pairs
  with labels `(0,4),(0,7)` and `(3,5),(3,7)`, whose pair-upper bound is one.
  Thus the only recurrence-compatible choice forces a local `C4` collision.

The complete DRAT-ready list of 2,368 canonical masks, orbit masses,
evidence artifacts, and the two projected cores is stored in
`scratch_root_e72_source150_m47_shard_audit.json`.  The producer inputs are
hash-bound there.  Each row contains a 45-literal assumption set for the
existing full CNF: selector 817289 or 817291 followed by the 44 positive
internal/overlap edge variables. No DRAT run is claimed here. Both macros
are completely excluded by this exact local subsystem.
