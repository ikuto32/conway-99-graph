# Independent eight-coordinate domain and weight audits

The two audits below establish conditional results only. Neither supplies a
99-vertex target graph or general nonexistence proof. No automorphism is assumed.

## Complete local domains

The independent checker
`acceleration/audit_20260930_eight_domains_independent_v1.py` reconstructs the
fixed graph from raw baseline candidate 18481. It checks exactly 120 retained K
edges, 480 freed same-sign coordinate edges, and 2,160 unknown edges including
1,680 disjoint-support edges. All other prescribed absences remain fixed.

The producer uses binary include/exclude branching with a changing root-label
choice. The independent enumerator, reused from
`audit_20260917_partial_matching.py`, chooses the first unsatisfied root label
and branches over its complete demanded subset. It imports no producer module.
Every retained leaf is independently checked by actual graph mutation through
`audit_20260917_affected_star_caps.py`. This shared independent checker code is
disclosed; these are not two entirely unrelated mathematical implementations.

The enumeration argument is as follows. Every valid completion chooses exactly
the demanded number of neighbors carrying each root label. For the first
unsatisfied label, branching over every subset of that size partitions all
possible choices. Removing vertices whose labels or capacities are exhausted
cannot remove a valid choice. A candidate failing the single-edge graph test
cannot be repaired by further edge additions: degrees and common-neighbor
counts only increase, while adding adjacency only lowers the corresponding
common-neighbor cap. Pair conflicts record exactly the new common center of
two newly selected neighbors. The independent enumerator's capacity for vertex
`w` records the change in the center–`w` common-neighbor count, together with
the one-unit cap decrease when `w` itself is selected. Thus every pruning rule
is a necessary condition; final exact set equality checks completeness as well
as soundness.

For leaf checking, only center–other pairs and pairs with one newly selected
neighbor and another final center neighbor can change. Every pair in this
union is recomputed from the mutated graph. All other pair caps were checked
in the fixed graph and remain unchanged. All changed degrees and all 14 exact
root-neighbor quotas are checked. This is a complete check of the full graph's
upper caps using an unchanged-pair argument, not a sampled cap check.

Before enumeration, six restricted candidate universes were compared against
direct checking of all 4,851 unordered full-99 pairs. Positive stars, missing
and extra edges, empty stars, self loops, out-of-range bits, duplicate domain
rows, missing rows, wrong declared counts, and a loop in the fixed base were
tested. These controls alone are not evidence of large-domain completeness.

Saved runs:

- `acceleration/results/20260930_independent_review/eight_old17_controls01/`
  contains the initial calibration run.
- `acceleration/results/20260930_independent_review/eight_old17_full01/`
  independently enumerated 17 saved centers, 996,947 choices, and checked
  383,195 original-ID embeddings.
- `acceleration/results/20260930_independent_review/eight_new67_full01/`
  independently enumerated the other 67 centers, 1,293,175 choices, and checked
  496,254 original-ID embeddings.
- `acceleration/results/20260930_independent_review/eight_domains_claim_binding.json`
  checks the disjoint union, byte identity of reused center tables, and all
  audit input/output hashes. SHA256:
  `170871c99ed16a160bf1403e4f6443275ca00c3a6ce68775fb56ba5f02783302`.

The resulting recommendation is **VERIFIED** for
`C-PARTIAL-K-EIGHT-COORDINATE-DOMAINS`, revision 1: all 84 local domains contain
exactly 2,290,122 choices, and all 879,449 prior six-coordinate choices embed
injectively within their respective centers with unchanged full center
neighborhoods. Local domains alone do not establish global feasibility or
exclusion. Overall search coverage: UNKNOWN; no validated denominator.

Both full runs used a fixed 1,800-second wall cap and 5,000,000-node cap per
center; neither cap was hit. Each run saves per-center receipts and immutable
checkpoints. Reusing a receipt requires exact source and input hashes plus
the same raw center bytes; an incomplete recursive search is never treated as
complete. The binding audit checks coverage controls with a missing center,
an extra duplicate center, and a replacement duplicate center.

## One transferred vector cannot give a positive bound

The separate standard-library-only checker
`acceleration/audit_20260930_eight_transfer_witness_v1.py` imports no producer or
prior checker module. It reconstructs the family with set adjacency, checks
the 84 saved stars against all full-99 pair caps and root quotas, and checks
each edge of the 84 saved neighborhood-matching witnesses separately by graph
mutation. It recomputes integer column scores from the mathematical moment
and reciprocity row incidences.

The frozen vector is the exact six-coordinate `10000_last.json` vector, with
reciprocity coefficients zero-extended on newly freed edges. The independently
computed RHS dot product is 2,543,434 and the sum of the 84 valid witness scores
is 6,306,214. If `H_u` is the local domain surviving the individually permitted
matching test, then each witness belongs to `H_u`, so

```text
(y*b - sum_u max_{s in H_u} score_u(s)) / 1048576
    <= (2543434 - 6306214) / 1048576
    = -940695 / 262144 < 0.
```

The audit therefore recommends **VERIFIED** for
`C-EIGHT-COORDINATE-FROZEN-WEIGHT-NONPOSITIVITY`, revision 1. This is only an
upper bound for this one fixed vector. It neither computes all maxima nor
establishes feasibility or excludes other weights. The selected stars need
not agree globally, and individually permitted matching edges need not be
jointly valid. Full matching counts, screening order, and producer attempt
counts were not independently checked.

The report is
`acceleration/results/20260930_independent_review/eight_transfer_witness_binding.json`,
SHA256 `148113d7779df565cbe11ffe73099677b2856dc22255c8fa0c9cda43201b6f8d`.
Controls include a known perfect matching, missing and duplicate matching
edges, a raw positive star, altered score, altered star mask, and corrupted
matching witnesses.

## Locked replay

Run from the repository root. Use new output paths to preserve prior evidence.
The saved manifests contain expanded exact arguments, source commits, working
directories, Python/uv versions, source hashes, and input/output inventories.
The environment is pinned by the repository's `uv.lock` and `pyproject.toml`.

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_eight_domains_independent_v1.py --domain-dir acceleration/results/20260930_eight_domains/run01 --out acceleration/results/20260930_independent_review/eight_replay_all84 --centers all --seconds 1800
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_eight_transfer_witness_v1.py --run acceleration/results/20260930_eight_transfer_screen/run01 --out acceleration/results/20260930_independent_review/eight_transfer_witness_replay.json
```

The original split audits and their union binding remain the historical
evidence; the all-84 command is a replay option and was not represented as an
already executed command. All review is internal; no external review or peer
review is asserted. Artifact availability is recorded separately in the
reports and may be updated after publication without changing these checks.
