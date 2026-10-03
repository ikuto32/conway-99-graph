# Eight-coordinate continuation, 2026-09-30

The user explicitly resumed research. Source baseline is remote main commit
`90f1a32de21faea3519c3635677d5739f86ad734`; the September 17 stop remains
immutable evidence. PR2 has been merged externally. The current branch is
`codex/eight-coordinate-continuation-20260930`.

Question: do complete necessary local star domains exist for all 84 outer
centers in the previously frozen eight-coordinate family? Keep precisely 120
baseline K edges and prescribed absences; allow 480 same-sign coordinate edges
at root groups 0,1,2,3 and 1680 disjoint-support edges. This is conditional,
with no automorphism assumption or target-level coverage claim.

Selection: retain the old deterministic center order. Verify the old stop
receipt, checkpoint and each referenced completed-center byte hash, reuse the
17 completed domains, then enumerate the remaining 67 centers. The resumed
enumeration uses the unchanged retained-partial enumerator. No recursive stack
from the interrupted center is available; that center is recomputed. Old and
new evidence are separate. Reuse is bookkeeping, not independent validation.

Before the new enumeration, replay the original six restricted-universe
positive/corruption controls against direct full-graph brute force. Check all
saved six-to-eight-coordinate embeddings against new domain membership when
each center completes. Bind every input and source hash in a new manifest.

Limits fixed before execution: 1800 seconds for enumeration, 300,000,000 new
recursive nodes, 1,000,000 choices per center, and 10,000,000 total choices
including reused centers. Save completed centers and immutable checkpoints;
retain partial masks and any triggering leaf on a cap or interrupt. A timeout
or cap is an incomplete experiment, never an exclusion. No randomization or
floating-point acceptance threshold is used.

Success requires 84 complete domains, exact membership of all 879,449 saved
prior embeddings, no hash changes, and independent completeness/admissibility
checking by a separate enumeration path with positive and corrupted controls.
Producer completion alone remains CANDIDATE. No LP is built before that audit
gate. Any subsequent matching filter or solve needs its own frozen protocol.

Run from repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_eight_resume.py --out acceleration/results/20260930_eight_domains/run01
```

This protocol authorizes a bounded experiment within ongoing research. Its cap
does not stop the overall research objective. Further experiments are selected
from the saved outcome and independently established facts.
