# Fifteen literal profile proof audit

This review checks every completed run in the frozen serial campaign, without
running CaDiCaL again. Its population is exactly cases 6,12,18,24,30,36,42,48,51,
72,78,84,90,96,102. The complete independent encoding gate binds each formula,
model and scope. These formulas impose the full prescribed Gram and within-group
column caps on the fixed six-prism Hadamard support. They omit cross-group caps
and residual D. This review does not transfer exclusions along fibre orbits or
assert coverage of all four-exception profiles.

The checker reauthenticates the preserved DRAT-trim build, including its immutable
upstream source, reviewed Windows portability patch and compiler identity. It
uses the independently authored authentication/replay helper from the balanced
Gram proof audit; no producer Python is imported. The checker implementation,
compiler and runtime remain trusted. Solver correctness is not a premise.

Before complete research replays, a truth-table checked two-variable UNSAT
fixture must accept its reasoning trace; missing reasoning, a fresh unsupported
unit, and the same trace against a SAT formula must fail. An empty-only trace
must also fail against every actual formula. Every complete saved research trace
is then checked, never a sample or a prefix. Each replay has a 180-second limit;
timeout is a failed audit, not a proof or a refutation of the claim.

Native commands, actual exit/status/statistics, exact input hashes, immediate
ext4 hash and host-copy receipts, resource reservations, serial checkpoint
prefixes and final aggregate counts are checked. Corrupt receipt controls are
tested separately. The availability label remains LOCAL_ONLY pending publication;
a successful local proof replay does not establish public retrieval.

Run from the repository root with the existing locked environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_hadamard_fifteen_profile_unsat.py --out acceleration/results/20260930_independent_review/hadamard_fifteen_profile_unsat
```
