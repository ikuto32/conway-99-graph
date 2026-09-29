# Fixed Wave154 row29 exact obstruction protocol

Frozen before execution. The independently replayed completion proof has a
producer-extracted core whose primary edge variables all join vertex29 to B.
Test this as a direct combinatorial feasibility problem, without a SAT solver.

Inputs: fixed propagated Wave154 raw99 matrix, itself separately audited;
the original fixed family and all 563 forced zeros remain explicit premises.
Let x_b=A[29,b] for each remaining unknown in row29. Its degree is exactly14.
For every vertex in A0 or A1, its complete known row gives an exact linear
common-neighbour equation in these x_b. For every pair b,c in B with two
already known common neighbours other than29, x_b+x_c<=1 is necessary.
If a B edge is fixed1, use its bound1 instead. No unknown other-row product
is subtracted or assigned a guessed value. These are necessary conditions
only; a satisfying row would not certify completion.

Run exact exhaustive binary recursion with degree/equality/upper-bound
propagation. Every force cites an input constraint, every conflict records an
exact violated interval, and every split emits both branches. Save the full
proof tree. Test the implementation against exhaustive truth tables on small
positive and contradictory systems before the research run. A discovered
empty domain is CANDIDATE until an independent checker rebuilds constraints
from raw99 and verifies the entire tree or a separate exhaustive search.

Limits: 120 seconds total, 1,000,000 recursive nodes, 8 GiB working set;
deterministic choices, no random seed or floating point. Do not launch SAT,
change the full CNF, or modify any older evidence. On a limit save incomplete
state and report UNKNOWN. No general triangle-core or target exclusion.

Command: `uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_row_obstruction.py --out acceleration/results/20260930_triangle_wave154_row29_obstruction`, with `UV_PROJECT_ENVIRONMENT=build/research-venv`.
