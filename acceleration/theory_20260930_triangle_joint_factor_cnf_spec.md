# Exact joint binary factor encoding for one fixed triangle core

Frozen before build; candidate encoding, no solver authorization inferred.
Build limit120seconds/8GiB with calibrated exact prefix counters. All new
dependencies use the existing locked root uv environment. Deterministic,
integer-only, no random seed or numerical thresholds.

## Exact scope

The39vertex scaffold is the archived Wave149 choice: three internal
matchings M=(01)(23)...(10,11), identity cross matchings01 and02, and
P(i)=i+6 mod12 between fibres1 and2. It is one fixed core only.
Let G be its forced36x36 incidence Gram from the full target identity.
Its diagonal blocks are9I-M+J, blocks01=02 are2J-I-2M-P, and block12 is
2J-I-P-2MP. Require a binary36x60 matrix C with exactly two ones from each
twelve-row fibre in every column, row sums10, and C*C^T=G.

This is a necessary incidence factor of the fixed core; it does not include
the residual60vertex graph D. SAT is a local factor, not a target graph.
UNSAT after checked encoding and complete proof excludes this fixed core,
not unrestricted Conway99. No target automorphism is assumed.

## Harmless column normalization and forced zeros

Within each fibre, columnweight2 and diagonal Gram imply that columns are
the60distinct edges of K12-M, once each: matched vertex pairs have Gram0,
each nonmatched pair has Gram1, and there are60columns. Relabel the outside
vertices/columns so C0 is the lexicographic edge incidence matrix of K12-M.
This retains every binary factor up to column labelling. C1 and C2 stay free.

If G0i[a,b]=0, nonnegativity of the column products forces C_i[b,d]=0
whenever C0[a,d]=1. Fold exactly those zero incidences, recording every
zero's witnesses;120 per free fibre. The remaining1,200 entries have
consecutive SAT IDs in fibre,row,column order. Do not prescribe Q1 or Q2.

## Equations and exact encoding

There are24 unknown row margins10,120 column margins2,288 linear C0-cross
Gram equations, and276 Gram equations for unordered pairs among C1,C2 rows.
The latter use exact bidirectional AND gates for each nonconstant product.
Every equation uses the frozen bidirectional prefix threshold counter and
requires both >=k and not>=k+1. The model exposes all input literals,
threshold states, clause intervals and product IDs, enabling independent
complete reconstruction. Diagonal C0 and its row/column margins are fixed;
the remaining diagonal Gram entries follow row sums because entries binary.

The cheap scout predicts58,860 variables/203,748 clauses,11,400 exact ANDs
and708 equations. Build must agree or preserve a failure record. These are
size predictions, not a performance claim or independent encoding review.

## Controls and audit gate

Run frozen exhaustive small threshold controls. Independently within this
producer, construct both archived24x60 two-group factors and check every
integer Gram entry; reject a single-bit corruption. These controls calibrate
the object checking path only, not existence of a36row factor. No known
positive36row fixture exists. A future solver assignment must satisfy every
raw clause and decode to a binary36x60 factor checked by a separate
implementation. Complete proof replay and an independent encoding/coverage
gate are mandatory before an UNSAT exclusion is promoted.

Inputs and outputs receive exact source, command, environment and SHA256
records, plus gzip recovery packages. Prior fixed-Q1 exclusions and archive
bare UNSAT statuses are not premises. The reusable prefix producer is shared
with earlier encodings; this build is not independent verification.

Command: `uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_triangle_joint_factor_cnf.py --out acceleration/results/20260930_triangle_joint_factor_cnf`, with `UV_PROJECT_ENVIRONMENT=build/research-venv`.
