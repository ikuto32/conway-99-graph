# Native first-matching-normalized arbitrary-core pilot

Question: does the universally necessary arbitrary-core factor model, with
M1 normalized to its eleven complete matching orbits, produce a factor or a
complete UNSAT certificate within one bounded attempt? M2 and P remain
arbitrary; no target automorphism, fixed core, component restriction or
residual D is assumed. The exact input has 110,915 variables and 518,227
clauses. Its 67-clause suffix is equisatisfiable with the base necessary model
up to the independently verified relabelling.

This is a new run, not a continuation or overwrite of earlier UNKNOWN runs.
The reason for the longer budget is the new independently checked matching
normalization and the earlier shorter UNKNOWN baseline. No speedup or
performance comparison is inferred. Require the new normalization/byte gate
and new extended-object calibration, plus the frozen base encoding, universal
coverage, native CLI and ext4 proof-path gates. Preflight is read-only with
respect to all research artifacts and launches no solver. Root controls the
research launch.

Preregistered limits: one native CaDiCaL 1.9.5 attempt, 900 wall seconds,
configured 5,000,000 conflicts, 4 GiB address space and 10 GiB per proof file,
five seconds termination grace, and 920 seconds outer Windows subprocess
guard. Use ASCII proof output directly on observed WSL ext4. Require at least
11 GiB ext4 and 21 GiB host free space before launch. The configured conflict
limit may overshoot slightly; preserve and report actual stdout statistics.
No automatic retry. Keep the Linux proof and hash-checked host copy; an
incomplete or resource-limited trace is not a certificate.

On SAT, save the complete 110,915-variable assignment from actual native
stdout. Save its literal 110,904-variable projection for the frozen producer
base decoder. This decode is only a candidate. The new independent checker
must check all native/JSON values, every extended and base clause, the selected
representative, every exact raw Gram/margin/cap requirement and partial99
entries. An accepted factor still omits all 1,770 Y-Y adjacencies.

On UNSAT, preserve exact CNF, full trace, binaries, source identities and
actual process receipt for independent replay. The runner does not approve
an exclusion. Only complete replay plus all coverage/encoding gates could
support a target-level claim, which would still be an internally verified
candidate resolution pending external review. UNKNOWN, timeout, proof-file
limit or abnormal cleanup makes no mathematical exclusion.

Use the existing locked uv environment from the repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/native_20260930_variable_core_m1_orbits.py --preflight --out NEW_DIRECTORY --encoding-gate REPORT --encoding-gate-sha256 EXACT_SHA --object-gate REPORT --object-gate-sha256 EXACT_SHA
```

After gates and preflight pass, root may replace `--preflight` with `--research`
and choose a fresh output directory. Previous runs and proof artifacts remain
unchanged.
