# Frozen partial-K binary arc-consistency preparation

Question: does the complete partial-K family retain pairwise-compatible full
center neighborhoods after exact propagation? This is a necessary relaxation,
not an equivalence to SRG existence and not a test of unrestricted Conway-99.

Input is the independently audited 54,478 original local-star choices over
84 centers, 162 prescribed K edges, and 1,740 unknown edges. Other prescribed
absences remain fixed. A separately audited neighborhood-matching filter may
select original IDs before propagation; its report, status and artifact hashes
must be bound. The filtered population must never be called the original
complete table. Eight or nine added neighbors complete each center to degree14.

For centers u,v and local choices i,j, construct full99-bit neighborhoods
Nu=F[u] union added(i), Nv=F[v] union added(j). A pair is allowed exactly when
their uv edge decisions agree and popcount(Nu intersection Nv)=2−edge(uv).
This retains the common-neighbor contributions omitted by linear cap models.
All3,486 unordered outer pairs are constrained, including fixed nonedges and
fixed edges. Pairs involving the root scaffold are already established by the
audited local domains. Every target completion in this frozen partial scope
induces compatible choices; removing a choice with no remaining support
therefore preserves every such completion. Induction over recorded deletions
is the complete pruning argument. A nonempty arc-consistent fixed point does
not prove simultaneous extendibility.

The historical Rust parser cannot be used unchanged: it assumes168K edges,
partial degree6, exactly eight added neighbors, and disjoint supports only.
The new standard-library Python adapter imports no producer or native code.
It rebuilds the root scaffold from the immutable manifest, validates all
original masks and maps retained original IDs explicitly.

Frozen pilot: deterministic directed-arc queue, initially increasing domain
product then center indices; ascending original IDs and support IDs. Complete
each directed arc atomically. If a choice has no supporting opponent, save its
original ID and the complete opponent-ID set. On deletion requeue all incoming
arcs except the reverse arc already protected by symmetry. Stop on an empty
domain, queue exhaustion, ten million exact pair checks, or180seconds per
invocation. An incomplete arc commits no deletion and returns to the front of
the saved queue. Caps are neither closure nor exclusion. Fresh output folders
preserve every run. Resume binds exact input hashes and prior result hash and
uses the saved queue and surviving original IDs; expensive support relations
are recomputed. If one arc exceeds a cap, changing limits requires a separate
protocol revision rather than silently broadening this run.

Controls: positive singleton-neighborhood3x3 rook SRG(9,4,1,2), corrupted edge,
incorrect intersection, asymmetry, one-check cap and exact resume. These are
producer controls, not independent validation. Independent input review must
approve the actual source, original-ID mapping and premises before propagation.
Independent artifact checking must replay every deletion using a separate set
intersection implementation, verify saved queue/closure semantics, and test
corrupt witnesses before any exclusion or reduced-domain LP is promoted.

Preparation command (no propagation):

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_partial_pair_ac.py --out acceleration/results/20260917_partial_pair_ac_preparation/base
```

Filtered preparation additionally requires `--filter-dir`, `--filter-audit`
and `--filter-audit-sha256`. Execution adds `--run --input-review PATH
--input-review-sha256 SHA` and a fresh output folder. No LP is run here. There
is no random seed or floating-point mathematical threshold; only wall time
uses floating point. Overall search coverage: UNKNOWN; no validated denominator.
