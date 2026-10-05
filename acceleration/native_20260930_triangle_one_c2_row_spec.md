# Native pilot for the 25-row target-necessary projection

Preserve all previous sources and runs. This pilot uses exactly the newly
built 74,814-variable, 256,151-clause CNF for free C1 plus C2 coordinate 0.
Its scope includes exact selected-row Gram and margins, partial component
capacities, and all selected-row column-pair overlaps at most 2. This is a
necessary projection for targets containing one fixed triangle core. It
does not claim that every abstract full factor projects to this problem.

Require the separately authored full encoding gate and raw-25-row object
checker calibration, binding the exact CNF/model/scope and kernel premises.
The runner takes their actual immutable hashes as explicit CLI arguments.
Its preflight makes no research solver call. Root controls research launch.

Use the authenticated native CaDiCaL 1.9.5 executable and the existing,
separately calibrated WSL ext4 proof transport. Reuse and disclose the
frozen subprocess, native-output parser, and exact-copy helpers. This is
not a performance comparison and introduces no new solver options.

The single attempt uses ASCII proof output, configured 1,000,000 conflicts,
300 seconds native wall time, 4 GiB address-space hard limit, 10 GiB output
file hard limit, a five-second termination grace, and a 320-second outer
guard. Record actual counters and actual exit status; configured conflict
limits need not equal the final reported number. No automatic retry.
Require at least 11 GiB free ext4 space and 21 GiB free host space before
launch. Preserve the original ext4 proof and any complete or partial copy.

SAT saves all 74,814 signed assignment literals and a producer-decoded
25 by 60 binary array, Q1 permutation, and selected C2 row. The producer
check is not approval. A separate checker must parse native stdout, check
every raw clause, and check the exact raw 25-row mathematical conditions.
Even a valid SAT object is neither a complete factor nor a target graph.

UNSAT is pending independent complete DRAT replay. If that replay succeeds,
the exclusion concerns targets with this fixed core only; no unrestricted
coverage is claimed. UNKNOWN, resource interruption, incomplete proof, or
cleanup failure is not an exclusion. Preserve all receipts and artifacts.

Run with `UV_PROJECT_ENVIRONMENT=build/research-venv` and the existing locked
uv command. The CLI is:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/native_20260930_triangle_one_c2_row.py --preflight --out NEW_DIRECTORY --encoding-gate ENCODING_REPORT --encoding-gate-sha256 EXACT_SHA --object-gate OBJECT_CALIBRATION_REPORT --object-gate-sha256 EXACT_SHA`

Only after the gates and preflight pass may root replace `--preflight`
with `--research` and select a fresh output directory.
