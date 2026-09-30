# Complete independent six-profile pairwise audit

`C-FIXED-HADAMARD-SIX-EXCEPTION-PAIRWISE-PROFILE-SCREEN` revision1 is independently verified within its fixed-support scope. The producer was `/root/state_literature_audit`; verifier `/root` used a separate implementation with no producer imports.

The [final report](../acceleration/results/20260930_independent_review/hadamard_six_profile_arc_v3/summary.json), SHA256 `82be6d4389596959365d5551694f3e1361d0bc855405f2647a682784be1f34ba`, binds every input and checked artifact. The [exact claim binding](../acceleration/results/20260930_independent_review/hadamard_six_profile_arc_v3/claim_binding.json) has SHA256 `6b9e318f8f50914e2293fda369363b8274023803cbeb8db32f4b747aab258d7c`.

All 12,648 distinct relations were reconstructed over all 12,846,624 option pairs. Each comparison used the full 1,296 entries of the two partial Gram matrices and all nine cross-column inner products. Binary 36-by-3 matrices were rebuilt from literal coordinates and word triples. Exact uint16 products and sums cannot overflow here: the relevant bounds are at most 36 and six. This checking path differs from the producer's packed Gram masks.

All 984 labelled profiles were checked. The verifier replayed 208,608 deletions against their current neighbor domains and checked 815,040 surviving supports. A separate queue-based AC calculation confirmed the outcomes and every nonempty greatest fixed point. Calibration included 28 genuine SRG243 partial-factor pairs, all 4,096 binary-domain triangle relation systems and their actual satisfying assignments, two synthetic six-domain instances, and eight deliberate corruptions. These controls are not target graphs.

The first pair relation empties 582 profiles. Adding cross-group overlap caps empties 654, including all 582, and leaves 330 nonempty fixed points. **Both stages begin with within-group cap-filtered domains.** Thus neither exclusion count is asserted for the Gram-only family. Nonempty fixed points establish no joint six-choice solution, complete factor or residual completion. The full target remains UNKNOWN.

Two unsuccessful checker versions remain preserved. Version1 incorrectly compared stored full relation references with the inventory's pair descriptors. Version2 incorrectly expected an empty list of support arcs after all domains became empty; the producer instead records all 30 arcs with empty supports. Both versions had already reproduced every literal pair relation before stopping. Version3 authenticates the full relation references and verifies every recorded arc, including empty ones. These are checker metadata corrections, not refutations of a research result. No producer artifact or threshold changed.

The [frozen plan](AUDIT_20260930_SIX_PROFILE_ARC_PLAN.md) specifies the complete population and 600-second audit limit. The successful invocation finished in 33.109 seconds in its recorded environment; this is one run, not a performance guarantee. Source SHA256 is `7b5f4054b1046d24caf047526dced1562c952590aa7e7cb339fe09e30087ce0b`.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_six_profile_arc_v3.py --out build/replay-six-profile-arc
```

Use a fresh output directory. The prior independently checked complete local-domain population is an explicit coverage dependency; its enumeration is not repeated by this audit. NumPy and Python integer operations, standard parsers, raw fixed-support data and the calibrated SRG243 fixture are disclosed trusted components. There was no SAT solver call or target automorphism assumption.
