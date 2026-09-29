# Frozen native proof-location calibration and small comparison

Question: does the existing pristine native CaDiCaL1.9.5 CLI preserve exact
SAT/DRAT artifacts when its proof is written to WSL ext4 and copied back, and
what are the measured timings on one fixed small UNSAT control?

No Conway-99 instance is solved in this experiment. Keep the first unrestricted
pilot and its source untouched. Run new Python only through the existing locked
Windows uv environment. WSL executes existing native commands only.

Use the already authenticated binary and checker from the native CLI calibration.
Create one fresh `mktemp -d /tmp/conway99-native-proof-XXXXXX` directory; record
the actual path, filesystem, CPU/kernel and inherited limits. Preserve that
directory and all copied artifacts. Input remains on `/mnt/c` in both arms;
only the proof destination changes. Stdout and stderr remain on Windows.

First calibrate a satisfiable 2-variable formula and a four-binary-clause UNSAT
formula through the ext4 path. Check complete SAT values and nonempty UNSAT
reasoning, copy-back byte identity using native SHA256 and an independent Windows
streaming hash, and the authenticated DRAT verifier. Reject an empty-only proof.
Apply 4 GiB virtual-address-space and 10 GiB per-output-file limits, no core dump.
Verify the inherited limits, a 16-byte ext4 file-size corruption probe, and
bounded timeout behavior. These are engineering controls, not solver correctness
proofs or research exclusions.

Comparison input: ordinary pigeonhole CNF for 9 pigeons and 8 holes, exactly one
or more hole for each pigeon and at most one pigeon per hole. Pigeon-at-most-one
clauses are intentionally absent in both arms. Save the raw CNF and its hash.
Run three repetitions per arm, sequentially in fixed order Windows/ext4,
ext4/Windows, Windows/ext4. Each invocation uses the same default options and
input, ASCII DRAT, 15-second timeout, 1000000 conflicts, and the above limits.
No retries or parameter changes. Record incomplete runs as incomplete; never
omit them from the report. Total comparison solver budget is at most 90 seconds;
overall calibration/comparison budget is 240 seconds. Do not start a new run
after the overall limit; record remaining work as skipped.

Record native subprocess wall time separately from native SHA256/copy-back and
Windows verification/hash time. The comparison boundary `solver_plus_copy` is
native subprocess wall time plus the copy subprocess wall time (zero for Windows).
It excludes setup, source/input validation, checksums and DRAT replay. Retain
all boundaries so this narrow convention cannot be confused with end-to-end time.
Record concurrent process observations; the active unrestricted pilot may cause
contention. Make no general speedup or research-instance prediction. A timing
comparison is descriptive only, with all six outcomes and medians where complete.

An ext4-path engineering gate requires the calibration cases and corruption/
resource controls to pass; the moderate timing cases may time out without
invalidating those correctness controls. Any future branch runner must separately
bind its independent encoding, coverage, actual augmented bytes and object gates.
