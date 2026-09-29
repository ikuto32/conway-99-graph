# Tenth milestone: one capacity-compatible Q1 and its extension obstruction

The four new claims concern an exact Q1 projection encoding, its explicit
24-by-60 SAT factor, a complete exclusion of that factor from the fixed-core
target family, and a conditional residual-block equivalence. The
[first registration](../acceleration/results/20260930_tenth_preparation_registration/summary.json)
and [row-exclusion registration](../acceleration/results/20260930_capacity_q1_exclusion_registration/summary.json)
preserve the ledger before and after each change. Target existence remains
UNKNOWN; no target-resolution artifact is submitted for external review.

Use the unchanged pinned root environment from the repository root. Saved
commands used uv 0.11.25 and Python 3.12.10. All replay output directories must
be new; do not overwrite frozen evidence. No solver is needed for the exact
artifact audits below.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_q1_capacity_cnf.py --out build/tenth-q1-encoding-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_q1_capacity_object.py calibrate --out build/tenth-q1-object-controls
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_q1_capacity_object.py sat --assignment acceleration/results/20260930_triangle_q1_capacity_native_pilot/main/parsed_model.json --native-output acceleration/results/20260930_triangle_q1_capacity_native_pilot/main/solver.stdout.log --decoded acceleration/results/20260930_triangle_q1_capacity_native_pilot/main/decoded_factor.json --out build/tenth-q1-sat-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_q1_capacity_sat_binding.py --out build/tenth-q1-binding-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_capacity_q1_rows.py --run acceleration/results/20260930_capacity_q1_rows --summary-sha256 3e665beda8c3521b3fad27d1c31e52afe5be820476d5ba92950f58698d3593c3 --out build/tenth-q1-row-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_residual60.py --out build/tenth-residual60-recheck
```

The [encoding audit](../acceleration/results/20260930_independent_review/triangle_q1_capacity_cnf/summary.json)
checks all 68,328 clauses and 19,686 variables of the necessary 24-row
projection. The [positive-object audit](../acceleration/results/20260930_independent_review/triangle_q1_capacity_sat_object/summary.json)
checks the complete native assignment, every raw CNF clause, the decoded Q1,
all 576 prescribed Gram entries, all margins and all 180 component partial
capacities. Its [binding and extra controls](../acceleration/results/20260930_independent_review/triangle_q1_capacity_sat_binding/summary.json)
bind the precise construction claim. This is a valid partial incidence
factor; no C2 or residual adjacency matrix is supplied by this SAT result.

The [independent row audit](../acceleration/results/20260930_independent_review/triangle_capacity_q1_rows/summary.json)
then reconstructs all raw99 fixed/free entries with that exact Q1. All 720 C2
and 1,770 unordered residual edges remain initially unknown. Each of the
twelve chosen C2 rows has 60 binary variables, one degree equation, 24 exact
common-neighbour equations and 108 incompatible pairs. All twelve domains
are empty: 2,774 tree nodes, 1,381 splits and 1,393 contradiction leaves were
checked completely, including every forced bit. Positive fixtures and 50
fresh corruptions calibrate the checker. The
[claim binding](../acceleration/results/20260930_independent_review/triangle_capacity_q1_rows/claim_binding.json)
records twelve explanations of one fixed-Q1 exclusion, not twelve disjoint
families. No capacity-compatible Q1 census or whole-core exclusion follows.

The [residual equivalence audit](../acceleration/results/20260930_independent_review/triangle_residual60/summary.json)
checks the written block proof and exact coefficient/control artifacts. Given
an actual qualifying 36-by-60 factor F and cubic core C, a symmetric binary
zero-diagonal D completes the target exactly when

```text
F D = 2J - F - C F,
D^2 + F^T F = 12I - D + 2J.
```

Its degree eight follows from the diagonal equation and column weight six.
This is an equivalence conditional on the stated full factor hypotheses,
not a claim that such F or D was found. The raw 24-row SAT object cannot be
substituted for that 36-row premise. See the
[derivation](DERIVATION_20260930_TRIANGLE_RESIDUAL60.md) and
[independent proof](AUDIT_20260930_TRIANGLE_RESIDUAL60.md).

All selected research artifacts, including raw CNF/model/assignment/logs and
the 1,816,830-byte trace from the SAT attempt, are below 10 MiB and ready for
direct publication in the [catalog](../acceleration/results/20260930_tenth_artifact_packaging/catalog.json).
The trace is not an UNSAT certificate and supplies no positive evidence;
the decoded object and exact checks supply the positive projection result.
Compressed raw-input packages and their hashes are retained and checked by
the encoding auditor. Earlier fixed-core dependencies are in the
[ninth guide](REPRODUCING_20260930_NINTH_WAVE.md).

Optional native replay is a new capped computation, not required to verify
the saved SAT witness. It uses the same authenticated CaDiCaL 1.9.5 native
build, WSL Ubuntu-24.04, native CLI/ext4 calibrations and local checker binary
described in the ninth guide. The executable hashes are frozen; another
build needs its own truthful calibration rather than rewritten old gates.
Run preflight first, then explicitly launch with a different output path:

```powershell
$q1Args=@('--out','build/tenth-q1-preflight','--encoding-gate','acceleration/results/20260930_independent_review/triangle_q1_capacity_cnf/summary.json','--encoding-gate-sha256','78db3e5afd4a1a3a0cedc451ac3e36f14ccd3615e15babcd060a1bc1f7a81a22','--object-gate','acceleration/results/20260930_independent_review/triangle_q1_capacity_object_calibration/summary.json','--object-gate-sha256','b4ee539d112b2f4ebe659ece364781a7dd9db99ffd75bbedd14cf8f6e345f434')
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_triangle_q1_capacity.py --preflight @q1Args
$q1Args[1]='build/tenth-q1-research'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_triangle_q1_capacity.py --research @q1Args
```

Limits are 300 native seconds, 1,000,000 configured conflicts, 4 GiB address
space, 10 GiB output-file size, five-second kill grace and a 320-second outer
guard. Native default randomness is recorded without inventing a seed. There
is no automatic retry, and another run need not return the same factor or
trace. The original result was SAT and native exit 10; producer status text
remains preserved alongside the later independent gates. Fresh solver
objects always require separate checking.

The row producer's frozen limits were two seconds or 20,000 nodes per row,
all twelve rows, and 120 seconds overall. All twelve saved trees completed;
the verifier checks their exact branches rather than repeating the search.
The live 25-row experiment and separate identity-core/archive/spectral
reviews are outside this milestone. The catalog only selects explicit paths,
checks their hash closure and preserved registration chain, and leaves the
ledger/index unchanged. At the registered tenth ledger state, replay it with:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_tenth_catalog.py --out build/tenth-catalog-recheck
```

Catalog and CI validity are bookkeeping checks, not mathematical review.
Overall search coverage: UNKNOWN; no validated denominator.
