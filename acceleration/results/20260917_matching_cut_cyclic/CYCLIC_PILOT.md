# Bounded cyclic/sign instantiation: no additional removals in the frozen corpus

Status: **CANDIDATE**, independent relabeling/application review pending.
The base sixteen clauses were gated on the independently checked
`C-MATCHING-POSITIVE-CUTS-16` revision 1 report, SHA-256
`3e807d158c7fea05e5a31ec631105fa1733e3ca86ad96549cc46a14dcf3e5fc9`.
Their sources, raw records, and frozen derivation were not changed.

The preregistered pilot uses exactly seven cyclic permutations of the seven root
groups, each with all 128 root-pair sign flips. For shift `r` and mask `m`,
the symbol `(g,b)` maps to

```text
((g+r) mod 7, b XOR bit_m[(g+r) mod 7]).
```

Vertex 0 is fixed. Each root-neighbor symbol and every outer unordered
root-label pair maps accordingly. All 896 resulting full-99 maps were checked
as bijections and checked to preserve the entire 189-positive-edge scaffold.
Positive map controls and corrupt duplicate-image, wrong-label, and moved-root
controls passed. The historical `GROUP_ORBIT_VALIDITY.md` was inspected and
hash-bound, but fresh explicit map checks were performed.

This is a coordinate relabeling argument. If a target graph has the scaffold,
its inverse-relabeled graph also has that scaffold. Applying an approved base
clause to the inverse-relabeled graph yields the transported clause for the
original graph. Permuting vertices preserves symmetry, binary entries, the zero
diagonal, and `A² = 12I - A + 2J`. The target graph need not admit any of these
maps as an automorphism. This explanation and the new map/application data remain
subject to independent review.

The 896 maps applied to sixteen parent clauses generated 14,336 positive-literal
sets. Deduplication by exact sorted unordered full-99 edge sets found 14,336
distinct clauses, so no duplicate images occurred in this bank. Every clause
retains its parent-cut and full-map witness. This does not imply inequivalence
under other maps, minimality, or novelty.

The frozen corpus consists of 29 named candidate records containing 747,064
original `(candidate record, outer vertex, original domain ID)` choices.
The result is **324 unique removed choices**, exactly the 324 already removed
by the original sixteen identity clauses. The union contributes **zero new
choices**. There were 324 distinct-clause hits and 324 generated-image hits;
their counts coincide here but are represented separately. No domain became
empty and no complete K exclusion is claimed.

Across the named candidate/clause pairs, 370 satisfy the positive K prerequisites.
For 46 of those pairs the exact eight-neighbor star is absent from the pinned
original domain. The other 324 pairs are hits. Each hit was checked directly in
the candidate's full positive scaffold+K+star graph and by reconstructing the
parent clause through its saved full-99 map. Every identity removal belongs to
the new union. These are internal producer checks, not independent approval.

This run completed all 29 candidate records in 1.593 seconds of measured wall
time, within the preregistered 240-second limit. Timing is a single observation.
The result is a useful failure of the narrowly selected bank to enlarge the
removal set. It neither refutes the clauses nor establishes that a larger group,
different positive cores, or a different K population would provide no benefit.
The full 645,120-element root-relabeling group was not searched.

Artifacts:

- `manifest.json`: preregistration, exact command, source commit, gate and input hashes.
- `maps.json`: all 896 full-99 maps and map controls.
- `cut_bank.json`: all 14,336 distinct clauses, center/star/K decomposition, parent/map witnesses.
- Per-candidate JSON files: prerequisite hits, absent stars, exact removed IDs,
  original-identity overlap, multiplicity data, and surviving counts.
- `summary.json`: hash-bound inventory and combined counts with explicit units.

Source: `acceleration/theory_20260917_matching_cut_cyclic.py`. Replay from the
repository root with a fresh output directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_matching_cut_cyclic.py --out build/matching-cut-cyclic-new --seconds 240
```

All counts are confined to this finite bank and corpus. Overall search coverage:
UNKNOWN; no validated denominator. No target-resolution claim is made.
