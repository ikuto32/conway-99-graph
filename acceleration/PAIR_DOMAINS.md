# Exact pair constraints between completed stars

`pair_domains.rs` is separate from the frozen star-domain generators. A domain
value completes the entire neighborhood of one outer vertex. For two domain
values at vertices `u` and `v`, compatibility requires:

1. The two values agree whether the edge `u-v` exists.
2. Their completed neighborhoods intersect in exactly one vertex if adjacent,
   or exactly two vertices otherwise.

The Rust implementation caches both directions of each compatibility relation
as packed 64-bit support bitsets. It matches the Python producer's deterministic
arc queue and emits the target vertex, support vertex, removed domain IDs and
before/after sizes for every deletion.

```powershell
rustc -O -C target-cpu=native acceleration/pair_domains.rs -o acceleration/build/pair_domains.exe
acceleration/build/pair_domains.exe CANDIDATE.txt DOMAINS.txt OUTPUT.json 30 10000000
```

The candidate uses `C99OVERLAPS1` with one valid overlap graph. The domain input
starts `C99DOMAINS1 84`; for each vertex in order, write its positive domain count
and that many strictly sorted hexadecimal masks. Use the **original complete
domains**, including values subsequently removed by edge-only reciprocity.
The current CLI rejects initially empty domains; their local exclusion is
already available from the star-domain evaluator.

The native parser validates graph invariants and the shape, support type and
ordering of masks. It does not establish that the supplied list is a complete
domain enumeration. Its raw output therefore records
`complete_initial_domains_audited: false`. Establish completeness independently
before treating a resulting empty domain as a fixed-assignment exclusion.

```powershell
python -B acceleration/audit_goal_theory_pairs.py --candidate candidate.json --domains complete_domains.json --pair-certificate OUTPUT.json --out pair_audit.json
```

The independent checker re-enumerates every used domain from the actual partial
graph, then verifies each deletion with ordinary Python set intersections.
It binds the candidate, complete-domain data and native proof bytes by SHA256.

The time and domain-pair budgets are explicit. A cap yields `INCOMPLETE` and no
exclusion. Relation construction checks its required budget before allocating
large support tables. On this preflight cap path, `domain_pairs_evaluated` is
the charged budget counter (`limit + 1`), not an executed-comparison timing
measure; completed runs report actual pair comparisons.

Saved controls under `results/20260916_rust_pair_domains/` establish full Python
parity, independent replay and cap behavior:

| Candidate | Relations | Domain pairs | Deletion events | Empty vertex | Rust kernel time |
| --- | ---: | ---: | ---: | ---: | ---: |
| Guided pilot | 6 | 673 | 7 | 25 | 0.0000122 s |
| Wide snapshot 15 | 1 | 5 | 1 | 24 | 0.0000040 s |

These tiny kernel timings exclude parsing, table setup and process launch; they
are correctness-control observations, not end-to-end search speed claims.
The pilot had passed ordinary edge-reciprocity arc consistency, so this
neighborhood-count filter is strictly stronger on the recorded control.
Nonempty pair arc consistency would still not give a simultaneous graph choice.
