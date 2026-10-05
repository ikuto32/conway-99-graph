# Variable-core binary-factor preflight only

After preparing the fixed-core full36column-cap pilot, estimate a different
necessary model in which both internal matchings M1,M2 and the crossmatching
P are free. M0 is the standard matching, and cross01/cross02 are identities.
Keep canonical C0 as the60nonmatching edges of K12-M0. All1440entries of
C1,C2 are free. This is not an actual CNF build or solver run, and is not an
independent normalization/coverage approval. The separate normalization
producer/auditor must establish the target implication before any future
research solve. No fixed component-count or old fixed-core kernel is used.

Convention: P[a,b] joins A1 coordinate a to A2 coordinate b. The proposed
Gram blocks are Gii=9I+J-Mi,
G01=2J-I-M0-M1-P^T, G02=2J-I-M0-M2-P,
and G12=2J-I-P-M1P-PM2. Compare every entry of these formulas with a direct
integer computation12I-B-B²+2J-diag(J12,J12,J12) for several deterministic
raw matching/permutation fixtures. These are calibration examples, not
proof of coverage or a substitute for the exact block derivation.

Allocate132matching-edge bits,144permutation bits, and1440incidence bits.
Require exact degree1 for every matching row and permutation row/column;
incidence row weights10 and fibre-column weights2. Rewrite Gram equations
as nonnegative sums equal to the small fixed right side by moving each
matching/permutation term left. Use independent ANDs for each quadratic
incidence and matching-permutation product. Count the actual frozen prefix
encoder output without writing a research CNF. Append77,760four-literal
column-cap clauses, justified prospectively by within-fibre Gram/margins
forcing distinct2-subset columns. These caps remain target-derived.

Record exact constraint/product counts, variable/clause size, arithmetic
calibration outcomes, source/locked-environment hashes and command. Limit
this deterministic preflight to120seconds/8GiB with zero solver calls and
no target witness or exclusion claim. No comparative speed claim follows.

Command with `UV_PROJECT_ENVIRONMENT=build/research-venv`:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_variable_core_factor_preflight.py --out acceleration/results/20260930_variable_core_factor_preflight`
