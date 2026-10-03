# Independent written audit of complete ternary adjacency exactness

Verifier: /root/structural. Timestamp: 2026-10-03T02:00:16.8017443+00:00. Discovery/source producer: /root.
Method: independent_derivation; exact integer matrix defect argument below.
Outcome: PASS for the exact source claim revision1. This is written review,
not mathematical promotion by a YAML schema, agent agreement, a numerical
experiment or an executable-control gate. No computation or scientific worker
was launched, and no live ledger/index was changed. No external review or
novelty claim. Source context00ffb6fdd7d91bd38269e1cc5e6b214ebf7591c8.

## Exact revision and immutable artifact being checked

Source: docs/CANDIDATE_20261003_TERNARY_DEGREE14_EXACTNESS_V1.md
SHA256274ce3fb355f69068bec254782f9f7d72c5b28e7e0dd53ca655c292dd6361582.
Claim revision1 states: for every99-by99 symmetric binary zero-diagonal matrix
A with exactly14 ones in each row, A^2=12I-A+2J over the integers if and only
if A^2=-A+2J over GF(3). Both equations are complete entrywise statements;
I,J have order99. No lambda1, automorphism, incidence factor, nonzero kernel,
rank, connectedness or fixed configuration premise is included.

The entire source document was read and authenticated before this audit. The
verifier's earlier paper note424e9ee705ea9a46fb2ca755e7470992c4825d7ac508ee3b34a2d2673be02170
predates the frozen discovery artifact, so it is supporting prior derivation
rather than silently relabelled as a revision-bound review. The present audit
binds the exact274ce3 source. A future authoritative claim ID/binding remains
ROOT's metadata task; this review does not invent a current registry entry.

## Separate exact matrix checking path

Assume the recorded domain and complete ternary equation. Define the INTEGER
matrix
 D=A^2-12I+A-2J.
The ternary equation makes every entry of D divisible by3. Simplicity,
symmetry and row degree14 give(A^2)_uu=sum_v A_uv*A_vu=14, so D_uu=14-12-2=0.
For u!=v, each common-neighbor count c=(A^2)_uv is a nonnegative integer and
A_uv is either0 or1. Hence
 D_uv=c+A_uv-2>=-2.
A multiple of3 at least-2 cannot be negative. Every off-diagonal entry of D
is therefore nonnegative, as are its zero diagonal entries.

Write1 for the all-ones column vector of length99. Exact regularity gives
 A1=14*1 and A^2*1=196*1; J1=99*1. Thus
 D1=(196-12+14-198)*1=0.
A finite nonnegative matrix with all row sums zero has every entry zero.
Therefore D=0, the full integer target equation. This checks every entry
through a universal sign/row-sum argument; it is not sampled verification.
Conversely reduction of the integer equation modulo3 deletes12I and gives
exactly the source ternary equation. The stated equivalence follows.

This argument independently reconstructs the mathematics using nonnegative
integer defect entries. It does not rely on the discovery source's partition
of fourteen adjacent versus eighty-four nonadjacent endpoints, though that
source walk-count derivation is consistent with it.

## Falsification and applicability boundaries

All of the following possible weaknesses were checked on paper:
- Degree14 is an INTEGER premise. Modulo3 degree congruence cannot replace
  the exact zero row-sum identity for D. The separately candidate95/98-degree
  reduced-Gram example violates this premise and supplies no counterexample.
- Symmetric binary zero-diagonal adjacency is used for diagonal(A^2)=14 and
  the off-diagonal lower bound. Directed, weighted, signed or nonbinary matrix
  variants are not asserted by the theorem; no untested graph counterexample
  for those different scopes is invented.
- A complete congruence is required. Rank/spectrum/diagonal/principal-submatrix/
  sampled residue assertions do not make every D_uv a multiple of3.
- The proof uses exact integer common-neighbor counts. Floating residuals or
  approximate numerical zero are not a certificate.
- Modulo2 permits a negative defect-2, so the defect-nonnegativity step fails.
  Arithmetic defects-2,+2 have zero sum and correct even residues. This is
  an explicit sign-step countercontrol, not an asserted graph construction.
- The genuine degree14/lambda1 ternary incidence rank98 fixture fails the
  full integer SRG validator and therefore cannot satisfy the full ternary
  adjacency identity. No extra-incidence-kernel statement or rank bound
  follows here, and it must not be combined with the synthetic Gram example
  as if they were one artifact satisfying all hypotheses.
- A zero binary incidence kernel remains possible; no proof of a nonzero
  kernel, rank upper bound or target nonexistence is claimed.

## Exact review scope and reporting limitations

The only reviewed result is the universal conditional/equivalence statement
in274ce3 at revision1. It applies to the unrestricted target adjacency domain,
but neither produces a graph nor rules one out. Target resolution: NONE;
repository existence verdict remains UNKNOWN. No executable fixtures or
controls were run for this written theorem audit. No solver, test command,
reviewer identity or successful computational check is invented.

A future residue-defect heuristic has the same zero set only when its domain
and complete residue evaluation satisfy the premises. Its speed, search
quality, encoding efficiency and implementation are unestablished. The proposed
scalar819820F3+E ordering has a correct crude boundE<=binom(99,2)*13^2=819819
within the same simple14-regular99 domain, but this audit does not approve
any new engine, state format, move kernel or search command. The current
strict-lex construction pipeline remains separate.

Shared trusted components: finite exact integer arithmetic and the literal
source statement; no source imports, producer code, cached candidate computation,
software elimination, SAT proof checker or floating-point solver is used.
The earlier paper derivation and discovery source are disclosed above.
Overall search coverage: UNKNOWN; no validated denominator.
