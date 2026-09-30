# Independent audit of the finite modular-kernel failed route

Reviewer: `/root/eight_domain_audit`; producer: `/root/state_literature_audit`.
The new checker imports no producer code and uses Python-integer echelon
elimination with back-substitution, not the producer's NumPy Gauss-Jordan code.
It chooses the last available pivot row, eliminates only below pivots, and
constructs the canonical free-coordinate kernel basis by reverse substitution.
The canonical basis is determined uniquely by the column order and the free
coordinates; changing row pivot choices does not change the resulting basis.

The original producer saved a seed, complete source/protocol and per-attempt
rank/failure counts, but did not save successful u/v vectors or matrix hashes.
Consequently this audit cannot compare reconstructed matrices to original raw
matrix artifacts. It independently reconstructs the deterministic protocol
(Python random.Random seed20260930, p2 then p3, canonical free-coordinate basis,
identical draw order) and preserves all256 reconstructed u/v vectors, the
underlying basis, per-trial exact hashes and exact results. This is independent
protocol reconstruction and summary agreement, not retrospective authentication
of unrecorded original matrices. Original source and report bytes are unchanged.

The base is the independently checked SRG243 triangle fixture, C60×60,F60×180,
D180×180. It obeys the integer equations FFᵀ=K, FD=H=2J−F−CF,
and D²+FᵀF=20I−D+2J, row sums18 and fibre-column sums2. This fixture is not
Conway99. The audit checks those literal integer block identities independently
using set intersections/sums, then checks both primes exactly.

Each reconstructed trial selects v in ker([F;1ᵀ]) with v≠0 and vᵀv=0,
and u whose sum in every20-row fibre is0, then puts F'=F+uvᵀ modulo p.
The expansion

    F'F'^T = FF^T + (Fv)u^T + u(Fv)^T + (v^Tv)uu^T

and the two sum conditions explain Gram and margin preservation. The checker
also directly recomputes every modular Gram entry with independent bit-plane
dot products; no floating-point arithmetic is used. It computes an entire
left-kernel basis for each F', checks every basis vector against F', and checks
every basis-vector product with H'=2J−(I+C)F'. Vanishing on the basis is exactly
vanishing on the entire left kernel, hence equivalent to unconstrained linear
solvability of F'D=H' over the field, separately for all180 right-hand columns.
It does not require the same D as the fixture, symmetry, zero diagonal,
binary entries, a residual quadratic identity, or a graph completion.

The exact finite statement is: for the128 reconstructed trials at each prime,
all stated modular Gram/margin checks and left-kernel compatibility checks pass.
OverGF2 all trial row ranks are57 (left dimension3). OverGF3 the base rank is47,
whereas all128 perturbed ranks are48 (left dimension12). Counts are attempts,
not an assertion that all produced matrices are distinct; uniqueness is
reported separately from the saved factor hashes. No random sample represents
a quantified result about other perturbations or all modular factors.

The checker calibrates its own elimination before the experiment against all
field vectors for every2×3 matrix (64 overGF2,729 overGF3), plus false vectors.
The producer's separate tiny calibration was explicitly post-run; this audit
retains that timing and does not rewrite it as preregistered calibration.
The actual243 mixed equation passes, while a changed RHS fails both its known
integer D and an explicit modular left-kernel test. Additional bad vectors,
wrong rank claims and altered Gram entries are rejected.

Archive overlap is explicit: external_conway99_research at pinned commit
85e705cc6c2a14d123120c93a847e30aaab1789e, attempts/wave58-cross-incidence-rank/
derivation.md, §§1–2, already discusses real Gram/kernel/rank identities and
attributes them to earlier Wave36. That document is conditional on its stated
prism-free endpoint. This experiment imports none of that extra assumption and
claims no rank identity or novelty from the finite-field tests. The current
general residual-equation and exact target modular-rank audit documents are
also bound as context, not new discoveries. No literature-wide novelty claim
or Conway99 exclusion is made. This is a useful recorded failed approach only.
