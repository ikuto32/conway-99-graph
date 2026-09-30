# Prepared independent residual-object checking path

Preparation only. No complete research factor or residual D is assumed,
constructed or searched by this note. The next action is conditional on an
independently validated arbitrary-core factor appearing.

## Existing authenticated prerequisites

- `C-TRIANGLE-FACTOR-RESIDUAL60-COMPLETION-EQUIVALENCE` revision 1, independent
  report `acceleration/results/20260930_independent_review/triangle_residual60/summary.json`,
  SHA256 `16120b7fe6a2645b9de8cb81e4eb4c9a6852bad0c513e4978fb116effdab7a73`.
- Universal normalization report
  `acceleration/results/20260930_independent_review/unrestricted_triangle_factor/summary.json`,
  SHA256 `a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd`.
- Arbitrary-core encoding gate
  `acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json`,
  SHA256 `ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0`.
- Raw factor checker
  `acceleration/audit_20260930_variable_core_factor_object.py`, SHA256
  `8146a2d1c3eedd9d623ee5074b96b0657da5d2786f1f556898c720352165ee82`;
  its calibration report SHA256 is
  `7577bbb79dfa5b334badc71cac820364d169edfe11f0eeaccd7eedbca9b1d40a`.
- Separate generic full-graph integer validator
  `acceleration/audit_20260930_full99_sat_object.py::validate_srg`, source SHA256
  `65d90a85be5fe67c510e561839901e9b8b7c3b9fc1ab7439af0e6bd3746a380c`.

The existing residual equivalence is general: C may be any symmetric cubic
36-vertex core with one neighbour in each of the three cells, provided the
stated factor Gram and fibre-column conditions hold. However, the producer
helper `theory_20260930_triangle_residual60.py::analyze_factor` hardcodes all
three standard matchings and the shift6 permutation. It must not be called
unchanged for a newly discovered arbitrary-core factor.

## Factor admission before residual work

Use the frozen arbitrary-core object checker on the complete native stdout,
parsed assignment, and producer-decoded object. This verifies all 110,904
assignment values, all 518,160 clauses, the actual M1/M2/P matrices, raw
integer Gram and margins, both cap families and all 99 partial vertices.
The resulting `independent_factor_and_partial99.json`, its report and every
input hash become immutable prerequisites. A future residual checker should
rerun the raw factor predicate on those bytes; it must obtain C from their
actual M1/M2/P, never from the historical shift6 example.

## Cheap exact rejection path

Independently compute T=F transpose F and H=2J-F-CF. Every actual completion
has H nonnegative. An edge y--z is permitted only if y differs from z,
T[y,z]<=1, F[:,z]<=H[:,y] and F[:,y]<=H[:,z]. These are necessary conditions
at both endpoints. A local residual star at y must choose exactly eight
permitted neighbours, their F columns must sum to H[:,y], and every two
chosen neighbours z,w must have T[z,w]<=1 because they already share y.

Record exact arrays, their hashes and direct raw partial-adjacency checks.
Degree or coordinate shortages have short exact witnesses. An empty row
domain needs a complete replayable enumeration or proof trace; a timeout
does not exclude the factor. Nonempty individual domains do not establish
simultaneous symmetric feasibility. Excluding one supplied factor does not
exclude all factors or the target. The automatic H row/column/cell sums
80/48/16 are consistency checks, not new evidence of feasibility.

## Complete residual object path

A future checker takes the admitted factor, its exact gate/hash, and a raw
60 by 60 matrix D. If D came from SAT, require that solver's separately
audited scope and complete native/JSON assignment plus all raw CNF clauses.
That scope is not certified by the current residual theorem alone.

Check strict integer binary entries, symmetry and zero diagonal. Check all
60 row sums eight explicitly. With separate integer loops check all 2,160
entries of FD=H and all 3,600 entries of

    D squared + F transpose F = 12I - D + 2J.

Then independently assemble A by filling only the 1,770 unknown Y--Y pairs
of the admitted raw partial graph. Check that every previously fixed entry
is unchanged. Require the separate full-graph validator to check binary
symmetry, zero diagonal, every degree 14 and every one of the 9,801 integer
entries of A squared = 12I - A + 2J. Also compare literal set-intersection
common counts with the block residuals for a separate calculation path.
The full identity is the decisive positive certificate, even if a block
check or producer decoder reports success.

Calibration before use includes the known-valid rook9 complete graph with
nonempty residual under its alternate bipartition for generic block tests,
the saved random full-size block polynomial fixtures (not valid factors),
and the full-graph validator's known SRGs. Corrupt D symmetry, diagonal,
degree-preserving edges, one factor bit, a core permutation and an input hash;
each must be rejected by the appropriate independent path. Do not pretend
that a valid full-size research F is currently available for a positive test.

An accepted full99 graph would be an internally verified candidate resolution
pending external review, with raw matrix, exact solver inputs, artifacts and
all independent reports made available. A residual UNSAT proof would exclude
only its authenticated supplied factor unless separate exhaustive factor
coverage were also established. No residual search or new completion checker
execution is recorded by this preparation note.
