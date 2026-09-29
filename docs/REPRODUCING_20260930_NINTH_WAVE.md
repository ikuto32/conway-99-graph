# Ninth milestone: fixed-core binary factors and capped attempts

The [registration receipt](../acceleration/results/20260930_ninth_registration/summary.json)
records seven new, independently checked claims. The
[catalog](../acceleration/results/20260930_ninth_artifact_packaging/catalog.json)
lists the exact publication payload and two LOCAL_ONLY incomplete traces.
The fixed 39-vertex triangle core is an explicit assumption; no nontrivial
automorphism of a hypothetical target is assumed. Neither factor formula
includes the remaining 60-by-60 adjacency block. There is no target resolution.

Run these commands from the repository root with the unchanged lockfile.
Recorded execution used uv 0.11.25 and Python 3.12.10. Every output directory
below must be new. Replaying a frozen checker is repeated execution of an
independent checking path, not a new independent discovery or review.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_q1_binary_scout.py --out build/ninth-q1-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_joint_factor_cnf.py --out build/ninth-base-encoding-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_joint_factor_object_v2.py calibrate --out build/ninth-base-object-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_factor_components.py --out build/ninth-component-encoding-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_component_factor_object.py calibrate --out build/ninth-component-object-recheck
```

The [Q1 audit](../acceleration/results/20260930_independent_review/triangle_q1_binary_scout/summary.json)
checks three raw factors, their prescribed Gram matrices and three complete
row-27 impossibility trees (167, 321 and 167 nodes). It also checks disjointness
of the five saved factors under the explicitly defined 384 coordinate maps;
this is not a census under all graph isomorphisms. The unsuccessful heuristic
512,000-swap attempt remains in `generation.json`; it was not independently
rerun and proves no exclusion.

The [base encoding audit](../acceleration/results/20260930_independent_review/triangle_joint_factor_cnf/summary.json)
checks all 203,748 clauses and 58,860 variables. Both unknown incidence blocks
are free. The [component audit](../acceleration/results/20260930_independent_review/triangle_factor_components/summary.json)
independently derives three equal component counts per column from exact
kernel vectors, checks the five saved partial-factor overflows, and verifies
the appended 180 equations (212,580 clauses and 61,296 variables in total).
The component argument gives another reason for those same five exclusions;
these exclusions must not be added as disjoint search coverage.

Both raw CNFs and models are below 10 MiB and are included directly. The
`artifact_packages.json` files in their respective directories also describe
ordered gzip parts, exact lengths and SHA-256 identities. The encoding audits
check these compressed packages against the raw files. Earlier dependencies
can be recovered using the [seventh guide](REPRODUCING_20260930_SEVENTH_WAVE.md).

The original object-checker calibration failed because a purported corrupted
fixture was still accepted. Its source and `failure.json` are preserved in
`triangle_joint_factor_object_calibration`; the corrected v2 calibration is
the actual gate. Its partial 24-row positive fixtures and synthetic full-size
codecs are not a valid 36-by-60 factor of the research Gram matrix.

The following commands audit the two saved UNKNOWN execution records. They
require the original local traces at the catalogued paths for current size
checks; the auditors authenticate the original copy/hash receipts rather
than freshly reading every trace byte. Public users without those LOCAL_ONLY
files can inspect the published receipts but cannot claim these exact
commands were fully replayed. The packaging check separately streams both
local traces and verifies their identities.

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_joint_factor_unknown.py --out build/ninth-base-unknown-recheck
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_factor_unknown_pair.py --out build/ninth-two-unknown-recheck
```

The [combined execution audit](../acceleration/results/20260930_independent_review/triangle_factor_two_unknown_runs/summary.json)
has SHA-256 `ad8a46d564f2fcb59f50bda2a5f1e4b0502709d37bfee34fbfc35967764c42aa`.
Both saved native attempts returned exit 0 and UNKNOWN. The base attempt
reported 1,000,000 conflicts and 69.55 real seconds; the strengthened attempt
reported 1,000,002 conflicts and 81.39 real seconds. These are observations
from different formulas, not a controlled performance comparison.

Optional new native attempts use Windows with WSL Ubuntu-24.04 and pristine
CaDiCaL 1.9.5, commit `146207318796f094dcded87349a64f0c6927309e`.
The wrappers bind the original authenticated executable, checker binary,
native CLI calibration and ext4 proof-location calibration. These local tools
must exist with their exact recorded hashes; a different build requires its
own calibration and truthful receipts rather than altered historical gates.
Build provenance and prerequisites are linked in the
[seventh guide](REPRODUCING_20260930_SEVENTH_WAVE.md). First run only preflight:

```powershell
$baseArgs=@('--out','build/ninth-base-preflight','--encoding-gate','acceleration/results/20260930_independent_review/triangle_joint_factor_cnf/summary.json','--encoding-gate-sha256','5a6ebade41cf1ab35796ca5d5ce3840c23b624ab06d0ed5a4ff327327ea2b97f','--object-gate','acceleration/results/20260930_independent_review/triangle_joint_factor_object_calibration_v2/summary.json','--object-gate-sha256','f0a23a0d4f0d81a6a789cb46f8f11d757e1ee753dbfea692c3eb47834999a464')
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_triangle_joint_factor.py --preflight @baseArgs
$componentArgs=@('--out','build/ninth-component-preflight','--encoding-gate','acceleration/results/20260930_independent_review/triangle_factor_components/summary.json','--encoding-gate-sha256','03d84677f34e0a209f9331c32efcd0b843dae60b97dbf9e9102b85171a5fef5b','--object-gate','acceleration/results/20260930_independent_review/triangle_component_factor_object_calibration/summary.json','--object-gate-sha256','5c6250b7282f8c513355e523c15c106f4a13f4cc78bc2c1b621a1394b5a351db')
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_triangle_component_factor.py --preflight @componentArgs
```

To execute the same two configurations in fresh directories, run:

```powershell
$baseArgs[1]='build/ninth-base-research'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_triangle_joint_factor.py --research @baseArgs
$componentArgs[1]='build/ninth-component-research'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_triangle_component_factor.py --research @componentArgs
```

Each wrapper invokes `--no-binary -c 1000000` under a 300-second native wall
limit, 4 GiB address-space cap, 10 GiB file cap and five-second kill grace.
The outer Windows guard is 320 seconds; host and ext4 free-space checks run
first. There is no automatic retry. New runtimes and incomplete trace bytes
need not match the historical attempt. Any future SAT factor requires the
separate raw-object checker and still is not a complete target graph. An
UNSAT output requires a complete independently checked proof for the exact
formula before any fixed-family exclusion can be promoted.

The two incomplete historical `main/proof.drat` files are 574,434,634 and
646,423,799 bytes, respectively. Their exact workspace paths, hashes and
Linux source/copy receipts are retained in the catalog and run summaries.
They are LOCAL_ONLY, are excluded from Git publication, and are not checked
UNSAT certificates. No public proof replay is claimed for either UNKNOWN
attempt.

The catalog can be reconstructed in the original workspace at the registered
ninth-ledger state, including the two local traces, with:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_ninth_catalog.py --out build/ninth-catalog-recheck --additional-audit-directory acceleration/results/20260930_independent_review/triangle_factor_two_unknown_runs --additional-audit-source acceleration/audit_20260930_triangle_factor_unknown_pair.py
```

Its allowlist excludes the subsequent Q1 projection, residual-D derivation
and candidate proof-core extraction. Catalog/hash checks establish artifact
identity and publication scope; they do not establish mathematics. Overall
search coverage: UNKNOWN; no validated denominator.
