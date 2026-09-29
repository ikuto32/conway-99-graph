# Bounded joint two-star discovery, pending independent review

As of2026-09-29T22:04:41.439387+00:00, source commit
8c0523f90bf652bc36261da51d62778cc96905cd. No target graph or general
nonexistence proof was obtained. All new mathematical outcomes below are
CANDIDATE until independently checked. No solver process was launched.

The final useful artifact is a proposed36-literal clause for the unrestricted
root scaffold. It excludes one positive-edge configuration:23 edges fix and
saturate two adjacent center stars, and13 further edges obstruct every
possible assignment at one other vertex. It does not exclude the original
two stars across all matching choices, any whole branch, or the target.

The certificate is
`acceleration/results/20260930_two_star_empty_domain_cut/run01/certificate.json`,
SHA256 `1a0c77282656c61675974f29e31e63af075d48c440f57be622630d6fe64abaa4`.
It contains the raw99 known-edge matrix, full model hash, negative clause,
complete460-pattern universe and a literal pair-cap witness for every pattern.
The summary is SHA256
`6db7caba94a7981c91828eef85cc8d25716fdce01eda2e85b296f17f4008ef45`.
The proposed scoped claim is that every target extending the unrestricted
root scaffold satisfies this exact clause; it is therefore redundant in the
independently audited exact unrestricted CNF. No minimality is claimed.

The recorded stages have different populations and are not additive:

| Stage | Frozen population and actual outcome |
|---|---|
| Joint local matchings |32 distinct sampled pairs of quota-valid stars, eight per recorded first-level branch; all32 have explicit two-internal-plus-one-cross matching witnesses;544 search nodes,66 individual edge prunes. |
| Individual outside domains |First local witness from each branch,61 outside vertices each:244 complete domains,297024 full patterns,64436 surviving patterns,zero empty domains. |
| Coupled outside search |Only case00;20000 DFS nodes and4674032 pattern attempts; node cap reached after31.156seconds, deepest partial assignment29 of61 vertices. UNKNOWN, no complete witness and no two-star exclusion. |
| Exact obstruction extraction |Next outside vertex63 at that saved prefix has460 candidate patterns, all rejected. Starting from118 positive outer edges,95 optional-edge deletion tests remove82 while retaining the complete empty-domain proof. Final36-literal candidate. |

Enumeration times reported by each producer are1.188seconds,4.562seconds,
31.156seconds and0.860seconds respectively; these are measurements with
different boundaries, not speedup or general performance claims. All loops
ended. The bounded-search checkpoint is a saved deepest partial assignment,
not a resumable DFS stack. Replaying the coupled search starts its deterministic
order from the beginning. No ongoing execution is implied.

The first joint matching source had an incorrect negative-control expectation:
adding one outer edge sharing one inner neighbor is permissible. That run
stopped before population generation. Its source, manifest and failure record
remain in `20260930_joint_two_star_matching/run01`. Version2 uses an actual
cap-violating triangle; it writes a separate run02. The mistake concerns the
control expectation, not an asserted target theorem.

The sources and exact commands are bound in the per-run manifests. Replay
with the existing locked environment, directing a copy/version to a fresh
output path because these producers refuse to overwrite original evidence:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_joint_two_star_matching_v2.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_two_star_outside_domains.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_two_star_coupled_domains.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_two_star_empty_domain_cut.py
```

The first producer does not import earlier producer code. Later producers
explicitly reuse the frozen outside-domain helper; that reuse is part of
discovery and calibration, not independent verification. Parent/another
checker must reconstruct the scaffold, full star saturation, all460 patterns,
each cap witness and every clause literal before promotion or solver use.
Artifacts are currently LOCAL_ONLY pending parent publication.

Prior-work inspection found existing conditional matching-pair filtering and
archived triangle-factor work. The new experiment specifically couples
sampled unrestricted scaffold stars. No novelty claim is made.
Overall search coverage: UNKNOWN; no validated denominator.
