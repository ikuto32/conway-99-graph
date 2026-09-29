# Preregistered bounded Boolean-box Gram lazy SAT wave

Frozen before the wave02 solver invocation on 2026-09-30 (Japan time).
The exact run timestamp, source commit, source/input hashes, versions and
command are written to the immutable run manifest before any solver call.

## Question and exact scope

Seek a local 59-vertex graph in the previously audited 780-edge fixed-central-star
family after strengthening all nine previous Gram clauses by exact Boolean-box
maximization. The central matching and four central incidence blocks remain
fixed; all right internal matchings and six right cross blocks remain free.
This is a conditional local search. It assumes neither a target automorphism nor
that every target contains this rook configuration. No target-wide denominator
or coverage percentage is available.

The initial ordered nine clauses are exactly those in
`results/20260930_rook_box_batch01/accepted_checkpoint.json`, independently bound
by `results/20260930_independent_review/rook_box_collection01.json` (SHA256
`b5a8ab884c157f40b32a4ebacf747e0d12596b0fb0ca01d3203fafd9dcf21cfd`).
The base CNF and encoding audit retain their frozen hashes from the 780-edge
model. Each round records the exact base plus ordered cuts and complete CNF hash.

## Selection, exact acceptance and failure criteria

Each round launches fresh deterministic-default CaDiCaL195, then independently
checks every clause, every Boolean assignment and the decoded full59 graph.
Exact rational Gram elimination checks `27I-9A+J` and `A+4I`. A negative direction
is reduced using the existing frozen descending-index greedy support minimizer.
Its support clause is independently checked, then weakened antecedents are
selected by freeing increasing exact maximum gains (ties by variable id) while
the maximizing Boolean corner remains strictly negative. The independently
authored box checker reconstructs coefficients and evaluates that corner over
the full59 matrix. A box clause is added only after this checker passes.
There are no floating thresholds. Exact zero never justifies a negative cut.

Stop on a verifier veto, worker error, UNKNOWN answer, exact Gram survivor,
unsupported Gram/rank obstruction, a complete UNSAT proof awaiting independent
replay, or a resource limit. Preserve every failed attempt. No same-wave restart
after a limit, and no changed threshold after seeing results.

## Configuration change and limits

The separately frozen v2 worker uses `with_proof=False` for SAT seeking and allows
up to five seconds for normal worker exit within the call limit. Small SAT,
unproved UNSAT and separate proof replay controls precede research and are saved
under `results/20260930_rook_solver_v2_calibration/`. Actual worker exit codes are
recorded; calibration does not establish that large-run cleanup is fixed.
No performance comparison or speedup claim is intended.

An UNSAT answer from this worker is explicitly unproved. If budget remains, the
same exact CNF is replayed through the frozen proof-enabled worker. Both calls
count toward the same budget. A saved complete proof still requires an
independent authenticated checker replay and scope review. An unfinished replay
does not prove exclusion.

Limits: at most 10 SAT-seeking rounds; 180 seconds cumulative solver process
wall time including proof replays; 60 seconds and 1,000,000 conflicts per solver
call; 600 seconds overall. Parent cleanup may add bounded termination overhead,
which is measured. Every completed graph and accepted cut remains usable after
a later timeout. Resumption takes an exact accepted-cut checkpoint into a fresh
directory and is a separately budgeted wave, not continuation of a live stack.

## Execution and replay

From the repository root in PowerShell:

```powershell
$env:UV_PROJECT_ENVIRONMENT=(Join-Path (Get-Location) 'build/rook-sat-venv')
uv run --project acceleration/environments/rook-sat --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_rook_box_lazy_loop.py --out acceleration/results/20260930_rook_box_lazy_wave02
```

The manifest binds the new loop, both frozen workers, both independent cut
checkers, the independent box-augmented SAT checker, exact Gram producer,
minimizer, box producer, model/CNF/audit, environment lock and calibration records.
Every subprocess invocation saves command, working directory, actual outcome,
time and log hashes. Final checkpoints preserve all ordered clauses and raw
certificates. Complete model assignments and raw graphs are never replaced by
scores. Checker subprocess success enables the next experiment but does not
constitute external review or authorize discovery-agent claim promotion.
