# Thirteenth milestone: normalization and nonempty verification controls

Four revision-1 claims were independently checked and entered by the
[preparation registrar](../acceleration/results/20260930_thirteenth_preparation_registration/summary.json).
The frozen ledger has 130 records: 128 VERIFIED/CLEAR and two CANDIDATE/CLEAR.
Target resolution remains UNKNOWN. No target-resolution artifact has been
submitted for external review. The GPU and complete ordered-pair experiments
are separate later cohorts and are not included in these totals or outcomes.

The [SRG243 audit](../acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json)
checks every entry of a complete 243-vertex adjacency matrix against
`A²=20I-A+2J`, plus its raw triangle blocks. This is a nonempty positive
control for factor and residual checking, not a Conway-99 candidate or a
novelty claim. Its factor is 60 by 180 and its residual has degree 16. Seven
corruptions include a degree-preserving switch that fails common-neighbour
counts. The failed initial source parse is preserved, not overwritten.

The [dynamic residual-screen audit](AUDIT_20260930_DYNAMIC_RESIDUAL_SCREEN.md)
establishes necessary conditions for an arbitrary valid specified core/factor.
It checks candidate residual edges and exact degree/coordinate quotas, using
the independent nonempty control and exhaustive small quota cases. No actual
research factor is supplied or excluded. Passing this screen does not imply
completion. The older shift-six-specific wrapper must not be substituted for
the dynamic wrapper on arbitrary cores.

The [first-choice normalization audit](AUDIT_20260930_PRISM_FIRST_CHOICE_NORMALIZATION.md)
checks 384 relabellings, all 207,360 equation images, all 147,456 group
compositions and 96 transports. They show transitivity of the first column's
96 choices in the fixed six-prism model. Appending the positive unit `1 0`
therefore preserves satisfiability up to relabelling. The new formula has
245,880 variables and 874,801 clauses. This is a fixed-core normalization;
it does not assert that every target graph has that core or an automorphism.

The [M1 normalization audit](AUDIT_20260930_VARIABLE_CORE_M1_ORBITS.md)
checks all 10,395 transports to eleven first-matching representatives and
623,700 canonical C0 column images. The appended eleven selectors and 67
clauses preserve arbitrary-core coverage by simultaneous relabelling. M2 and
P remain free. The formula has 110,915 variables and 518,227 clauses; it is
equisatisfiable up to relabelling, not identical on labelled primary states.
The explicit claim-binding addendum maps frozen audit dependencies to stable
root claim IDs without rewriting the original audit.

Use the existing pinned environment. Fresh output directories are required;
the following checks do not launch research solvers:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_twelfth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_thirteenth_inputs.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_srg243_residual_fixture.py --out build/thirteenth-243
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_dynamic_residual_screen.py --out build/thirteenth-residual
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_first_choice_normalization.py --out build/thirteenth-prism-normalization
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_first_choice_object.py calibrate --out build/thirteenth-prism-object
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_variable_core_m1_orbits.py --out build/thirteenth-m1-normalization
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_variable_core_m1_orbits_object.py calibrate --out build/thirteenth-m1-object
```

Both object checkers independently verify all native literals and all enlarged
clauses before passing projected assignments to the frozen raw-core/factor
checker. Their synthetic full-shape codec controls and the rook positive
control are calibration fixtures, not positive research factors.

The two native attempts each used CaDiCaL 1.9.5, 900 seconds, five million
configured conflicts, 4 GiB address space, a 10 GiB proof-file limit, a
five-second kill grace and a 920-second outer guard. The exact commands,
source commits, gates, build hashes, launch receipts and outcome audits are
saved with each run. There was no automatic retry or invented solver seed.

The M1 attempt ended UNKNOWN at 5,000,003 observed conflicts, native wall
788.36 seconds and CPU 786.31 seconds. The first-choice prism attempt ended
UNKNOWN through timeout/SIGTERM at 2,137,390 conflicts, native wall 900.00
seconds and CPU 896.31 seconds. Different instances and stopping mechanisms
do not establish a speed comparison. Neither supplied a factor or complete
proof. The independent engineering audits authenticate the entire retained
incomplete traces and reject altered outcome records; this is not DRAT proof
checking or a mathematical exclusion.

Three raw artifacts are LOCAL_ONLY: the 17,046,979-byte first-choice formula
(exactly recoverable from public gzip) and the two incomplete native traces.
The catalog records their exact sizes/hashes and local receipt paths. The
recovery helper reuses the prior package checker, verifies raw bytes and
refuses to overwrite different existing files. Its inherited console label
mentions the prior milestone; the selected package is explicitly thirteenth.
The failed first native preflight imported unavailable psutil; that source
and failure are preserved, and the corrected runner uses the standard Windows
memory API without changing uv.lock.

With the exact local trace files available, replay the outcome checks:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_variable_core_m1_orbits_unknown.py --out build/thirteenth-m1-run
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_first_choice_unknown.py --out build/thirteenth-prism-run
```

Optional new native attempts must use fresh directories and the saved
encoding/object gate hashes from their manifests. Each runner has explicit
`--preflight` and `--research` modes; preflight launches no research solver.
The historical manifests preserve the actual original command. Completed
experiments and registrations must not be rerun into their frozen paths.

The [explicit catalog](../acceleration/results/20260930_thirteenth_artifact_packaging/catalog.json)
checks artifact hash closure, gzip recovery, the registration snapshot and
the selected public payload. Catalog and schema checks are bookkeeping,
not mathematical verification. At the frozen registered ledger state, its
command is:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_thirteenth_catalog.py --out build/thirteenth-catalog-recheck
```

The first catalog attempt mistakenly required the deliberately false all-zero
hash inside a negative-control gate to match its fixture. That attempt and
source are preserved. The corrected catalog authenticates the control bytes
and records this one explicit false binding separately from evidence bindings.
A second attempt exposed an omitted allowlist entry for a prior raw input;
its source and failure are preserved too. Prior raw dependencies retain their
authenticated public gzip recovery and are not duplicated in this payload.

Overall search coverage: UNKNOWN; no validated denominator.
