# Eleventh milestone: a 25-row factor and restricted construction exclusions

The [first registration](../acceleration/results/20260930_eleventh_preparation_registration/summary.json)
and [second registration](../acceleration/results/20260930_eleventh_factor_registration/summary.json)
add eight verified claims. They concern a fixed-core 25-row projection and its
explicit SAT object, an equivalent compact encoding, the object's extension
obstruction, two complement-pairing exclusions, a broader fixed-pattern
exclusion, and a full-factor encoding with column caps. None resolves target
existence. The unrestricted triangle normalization and variable-core work are
outside this milestone. No nontrivial target automorphism is assumed.

Use the unchanged root uv lock (saved runs: uv 0.11.25, Python 3.12.10). Run
from the repository root, with new replay output directories. Preserve all
frozen reports. Exact artifact checking does not require repeating the SAT
searches. The complement-design audit does replay its complete DRAT proof.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_eleventh_recipe.py
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_one_c2_row_cnf.py --out build/eleventh-25-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_one_c2_row_object.py calibrate --out build/eleventh-25-controls
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_one_c2_row_object.py sat --assignment acceleration/results/20260930_triangle_one_c2_row_native_pilot/main/parsed_model.json --native-output acceleration/results/20260930_triangle_one_c2_row_native_pilot/main/solver.stdout.log --decoded acceleration/results/20260930_triangle_one_c2_row_native_pilot/main/decoded_factor.json --out build/eleventh-25-object
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_one_c2_row_sat_binding.py --out build/eleventh-25-binding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_one_c2_compact.py --out build/eleventh-25-compact
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_one_c2_compact_object.py calibrate --out build/eleventh-25-compact-controls
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_one_c2_extension_rows.py --out build/eleventh-25-extension
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_complement_design.py --out build/eleventh-complement-proof
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_prism_unpaired_kernel.py --out build/eleventh-unpaired-kernel
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_factor_column_caps.py --out build/eleventh-36-encoding
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_column_cap_factor_object.py calibrate --out build/eleventh-36-controls
```

The [25-row encoding audit](../acceleration/results/20260930_independent_review/triangle_one_c2_row_cnf/summary.json)
checks 74,814 variables and 256,151 clauses. The
[SAT-object audit](../acceleration/results/20260930_independent_review/triangle_one_c2_row_sat_object/summary.json)
checks all native assignment values and raw clauses, then the prescribed
25-by-60 incidence factor. The
[binding](../acceleration/results/20260930_independent_review/triangle_one_c2_row_sat_binding/summary.json)
and synthetic/raw25 controls distinguish target-specific hypotheses from
generic positive codec fixtures. The original attempt returned native SAT
exit 10. The factor contains C0, C1 and one C2 row; it does not supply the
remaining eleven rows or the residual adjacency matrix D.

The [compact equivalence](../acceleration/results/20260930_independent_review/triangle_one_c2_compact/summary.json)
reduces that projection to 22,379 variables and 81,366 clauses while preserving
the primary solutions, with the removed original auxiliaries recoverable.
Its positive calibration uses the saved original assignment; no additional
research SAT search is claimed. The
[extension audit](../acceleration/results/20260930_independent_review/one_c2_extension_rows/summary.json)
keeps the exact saved row27 and rebuilds the raw99 fixed/free matrix. All
eleven necessary domains, rows28 through38, are empty. It checks all 1,037
tree nodes and every forced bit, branch and contradiction. These are eleven
explanations of one fixed-object exclusion, not eleven disjoint exclusions
or a census of all possible partial factors.

The [complement-design audit](../acceleration/results/20260930_independent_review/prism_complement_design/summary.json)
checks the restricted 450-variable, 2,010-clause design and its complete DRAT
trace. The native result was UNSAT exit20. It authenticates the existing
drat-trim Windows executable and upstream source/build provenance, including
the disclosed portability patch; this is not a fresh diverse checker build.
Positive and corrupted proof controls are preserved. The independent written
parity argument also excludes any six-prism factor whose 60 columns admit
30 pairs preserving cell choices and complementing all six bits. This broader
restriction is still not a nonexistence theorem for arbitrary six-prism
factors or for Conway-99. See the
[precise proof](AUDIT_20260930_PRISM_COMPLEMENT_DESIGN.md).

Removing complement pairing produced a separate 1,260-variable,
29,655-clause model with 360 independent bits. Its single five-second pilot
ended UNKNOWN at the wall limit. The later
[exact kernel audit](../acceleration/results/20260930_independent_review/prism_unpaired_kernel/summary.json)
excludes that entire fixed five-matching, 30-cell-pattern family independently
of the unsuccessful search. It reconstructs 18 integer matrices, checks
nonzero nine-dimensional minors and full-support null vectors, and verifies
the type/parity argument. This does not cover arbitrary cell-pattern choices.

The [full36 encoding audit](../acceleration/results/20260930_independent_review/triangle_factor_column_caps/summary.json)
checks 61,296 variables and 256,320 clauses for the fixed39 core, including
43,740 appended column-cap clauses. It leaves the residual D unencoded.
The object checker is calibrated; no positive full36 research factor was
found. The [recorded pilot audit](../acceleration/results/20260930_independent_review/triangle_column_cap_factor_unknown/summary.json)
checks native UNKNOWN exit0, 1,000,001 observed conflicts against a configured
1,000,000 limit, and 83.219 seconds of wrapper time. It authenticates the
complete local bytes of the incomplete trace and rejects five corrupted
receipts. UNKNOWN supplies no mathematical exclusion or feasibility result.

Four raw files are LOCAL_ONLY and excluded from the public Git payload:

| Raw artifact | Bytes | Meaning and recovery |
| --- | ---: | --- |
| `triangle_one_c2_row_native_pilot/main/proof.drat` | 97,685,312 | SAT-run trace; not positive evidence or an UNSAT certificate. |
| `prism_unpaired_design_pilot/proof.drat` | 14,161,920 | Incomplete UNKNOWN-run trace. |
| `triangle_column_cap_factor_native_pilot/main/proof.drat` | 657,451,587 | Incomplete UNKNOWN-run trace. |
| `triangle_factor_column_caps/clause_recipe.json` | 12,025,031 | Exactly recoverable from the public 582,248-byte gzip part. |

Paths in that table are relative to `acceleration/results/20260930_`.
The recovery command above authenticates the package, compressed bytes and
decompressed length/hash, creating only a missing raw recipe and refusing to
overwrite different bytes. It may instead write a new workspace path using
`--destination`. The complete complement-design proof is 10,345,534 bytes,
below the 10 MiB public-file threshold, and is included. The other three
solver traces cannot be retrieved from their hashes. Saved native source
locations and transfer receipts identify the retained local copies; fresh
runs may generate different traces. Public readers can check the saved SAT
assignment and all mathematical certificates without these three traces.

The full recorded-run audit requires the local incomplete trace and the
authenticated local executables. It can be replayed only where those bytes
are available; do not describe it as a current public replay otherwise:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_column_cap_factor_unknown.py --out build/eleventh-36-run-audit
```

Native searches are optional new capped computations. The authenticated
CaDiCaL1.9.5 build, WSL Ubuntu-24.04, ext4 proof location and checker build
are described in the [ninth guide](REPRODUCING_20260930_NINTH_WAVE.md).
The two larger pilots used 300 native seconds, one million configured
conflicts, 4 GiB address space, 10 GiB file cap, five-second kill grace and
320-second outer guard. No seed is invented where native defaults were used.
Run preflight before an optional new attempt, using a different output path:

```powershell
$oneArgs=@('--out','build/eleventh-25-preflight','--encoding-gate','acceleration/results/20260930_independent_review/triangle_one_c2_row_cnf/summary.json','--encoding-gate-sha256','661062b1fbdf0d9e076082867b44353509fb892d9946dc142d1c70b91f59558d','--object-gate','acceleration/results/20260930_independent_review/triangle_one_c2_row_object_calibration/summary.json','--object-gate-sha256','3e33674feff8b5914547c8a459b83e12c0b11dd86c43bc6706882509d0d91b6a')
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_triangle_one_c2_row.py --preflight @oneArgs
$oneArgs[1]='build/eleventh-25-research'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_triangle_one_c2_row.py --research @oneArgs
$fullArgs=@('--out','build/eleventh-36-preflight','--encoding-gate','acceleration/results/20260930_independent_review/triangle_factor_column_caps/summary.json','--encoding-gate-sha256','675dae8635175088bff026c59e171c1d2b2b66a4a880cd6a10500ae66bb74331','--object-gate','acceleration/results/20260930_independent_review/triangle_column_cap_factor_object_calibration/summary.json','--object-gate-sha256','1c90436973c4483016eb55fca50adf6859849adb58cb3f574889302acb6b4452')
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_triangle_column_cap_factor.py --preflight @fullArgs
$fullArgs[1]='build/eleventh-36-research'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_triangle_column_cap_factor.py --research @fullArgs
```

The smaller prism pilots used five seconds, 100,000 configured conflicts,
256 MiB address space and 128 MiB file cap, with two-second kill grace and
15-second outer guard. Their producer commands reconstruct the exact model
and run controls without a search unless `--research` is supplied:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_prism_factor_design.py --out build/eleventh-complement-design-rebuild
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_prism_unpaired_design.py --out build/eleventh-unpaired-design-rebuild
```

The [catalog](../acceleration/results/20260930_eleventh_artifact_packaging/catalog.json)
uses exact allowlists and preserves both registration snapshots. It checks
hash references and gzip recovery without changing the ledger, ignore rules
or index. Its full local replay requires all four excluded raw files and the
registered eleventh ledger state:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_eleventh_catalog.py --out build/eleventh-catalog-recheck
```

Catalog validity and CI are bookkeeping checks, not mathematical verification.
Overall search coverage: UNKNOWN; no validated denominator.
