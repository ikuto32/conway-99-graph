# Arbitrary normalized triangle-core factor with both necessary cap families

Freeze before building. No solver is authorized by this build. The candidate
normalization source is the exact unrestricted triangle/core derivation at
`results/20260930_unrestricted_triangle_factor/summary.json`, SHA256
fecb50f01e6548c79e486068eeea3ca41dd6922ed4cf74686d9757ae0061b2eb.
Before the first build, its independent normalization gate arrived at
`independent_review/unrestricted_triangle_factor/summary.json`, SHA256
a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd.
Pin both the original candidate and this separate approval. A complete
encoding audit and calibrated object checker are still mandatory before
any future research solver launch. No historical record is overwritten.

Let M0 be the standard perfect matching on twelve coordinates. Fix cross01
and cross02 to identity and label the60outside columns by lexicographically
ordered nonmatching pairs of M0, defining canonical C0. Leave both perfect
matchings M1,M2 and the entire permutation P (rowsA1, columnsA2) arbitrary.
P is not constrained to be an involution or derangement. No commuting,
component, prism-free, factor orbit, or target automorphism assumption is
made. All1440entries of C1 and C2 are free, with no inherited zero folds.
There is no residualD. A SAT object is only a necessary partial specification.

Require matching row degrees1, permutation row/column degrees1, incidence
row weights10, and fibre-column weights2. The exact Gram equations are:

`Gii=9I+J-Mi; G01=2J-I-M0-M1-P^T; G02=2J-I-M0-M2-P; G12=2J-I-P-M1P-PM2`.

Move all matching/permutation terms to the left, leaving fixed nonnegative
small bounds. Each quadratic incidence or matching-permutation product gets
a distinct exact bidirectional AND. Retain all132within-unknown-fibre Gram
equations,144C1/C2 equations and288C0cross equations. Use the existing exact
prefix-threshold counter for all sums. Record every symbolic term, gate,
counter state and clause interval in the model.

Enforce all1,770distinct-column overlaps at most2. The retained fibre Gram
and column margins imply that each fibre uses all60distinct nonmatching
pairs for its own matching. Thus each within-fibre column overlap is0or1.
For each of540intersecting C0-column pairs and each C1/C2 row pair, append
the corresponding four-negative-literal clause. All77,760clauses occur;
there are no inherited fixed-zero omissions. This compact equivalence must
be independently checked for variable matchings, not inferred from old
fixed-core gates.

Enforce every mixed cap `(I+B)F<=2` using four720-bit output arrays:
U1=M1*C1, U2=M2*C2, V1=P*C2, V2=P^T*C1. For each possible selector entry S[a,k],
each column d, input x and output z, emit
`not S or not x or z` and `not S or x or not z`.
Exactly one selector is true per output row, so these clauses give the
unique selected input bit and hence the exact product. Retain all2,880
outputs, with no channel elimination. The four groups contain66,240ternary
clauses. Mixed cap sums are:

- A0: C1[a,d]+C2[a,d] <= 2-C0[a,d]-C0[M0(a),d].
- A1: C1[a,d]+U1[a,d]+V1[a,d] <= 2-C0[a,d].
- A2: C2[a,d]+U2[a,d]+V2[a,d] <= 2-C0[a,d].

Save all2,160mixed-cap counter rows, including tautological rows through the
same exact counter convention. Do not assume fixed-core component margins.

Controls before build: complete small threshold truth tables; exhaustive
one-hot selector/input/output truth tables for sizes1..4; the missing-one-hot
counterexample; and the prior twelve independently labeled raw-core algebra
fixtures as explicitly shared producer calibration. Controls do not prove
universal normalization or establish independent encoding approval.

Build limit120seconds/8GiB, deterministic exact arithmetic, zero solver
calls. Preserve source/commit/locked environment hashes, full raw variable
maps, model, scope, CNF and gzip packages below10MiB per part. A separate
decode mode accepts a complete signed assignment and saves the36core/F
object plus99partial adjacency (allY-Y offdiagonal values unknown), with
producer-only exact Gram, margin and cap checks. A new independent checker
must validate every raw clause and all object conditions before promotion.

Build command with `UV_PROJECT_ENVIRONMENT=build/research-venv`:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_variable_core_factor_cnf.py build --out acceleration/results/20260930_variable_core_factor_cnf`

Decoder CLI: `...py decode --model MODEL.json --assignment MODEL_ASSIGNMENT.json --out NEW_RAW_OBJECT.json`.
