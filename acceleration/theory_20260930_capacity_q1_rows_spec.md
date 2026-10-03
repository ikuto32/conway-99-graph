# C2 row domains for the new capacity-compatible Q1

Preregister before scientific run. Input is the native SAT24x60 factor,
SHA25694904b766b487e579f656e685643449c23a6aabf07825cac17e9fd8e241427c5,
independently approved by gate34eec921b8c149c2bd49860e2f0208c4d2fa472e953c55a89dc867a9d8c2605d.
The producer checks the gate status and exact decoded input binding before
deriving any new result. This is the fixed Wave149 core only.

Assemble a fresh raw99partial adjacency from the frozen core and decoded
C0,C1. All C2-to-B entries and all B-B offdiagonal entries remain unknown.
No prior Q1's forced-zero propagation or UNSAT result is a premise.
Check known-one pair caps as a cheap raw input consistency check.

Evaluate all twelve C2 vertices27..38 in ascending order. For each, use60
binary B-neighbour variables, degree10,24 exact common-neighbour equations
against completely known A0/A1 rows, and every necessary forbidden B-pair
from its already known common-neighbour cap. This is the same independently
reviewed row-domain formulation used for the earlier Q1 exclusions. Reuse
the frozen bounded integer recursion and its saved positive/corrupt controls;
that shared producer code is explicitly not an independent new review.

Limits:2seconds/20,000recursive nodes per row, all12rows attempted,120seconds
and8GiB overall. Deterministic branching, no seed or floating comparisons.
Save all constraints and complete UNSAT trees or complete SAT assignments.
Preserve UNKNOWN partial trees if a limit is reached; do not count them as
exclusions or feasible rows. Each result awaits independent raw99/constraint
reconstruction and full tree/witness checking. A single empty row excludes
this one Q1. Independently feasible rows do not prove one simultaneous C2,
a36row factor, any residual D, or a99vertex graph.

Command: `uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_capacity_q1_rows.py --out acceleration/results/20260930_capacity_q1_rows`, with `UV_PROJECT_ENVIRONMENT=build/research-venv`.
