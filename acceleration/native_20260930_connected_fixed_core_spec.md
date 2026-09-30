# Frozen native pilot for four fixed connected cores

Question: does each already selected fixed connected identity-P core admit a
factor satisfying the necessary exact Gram, mixed and Y-column constraints?
Use the four authenticated CNFs in the batch summary with SHA256
`39425b88f3fa5e46d95c3f4231b044c05484fc9d209250d7c045de6589cd82d6`.
Their order is core00 through core03. This selection predates the GPU pilot;
no cases are omitted based on heuristic scores. This is a fixed four-case
pilot, not coverage of all connected cores or unrestricted Conway99.

Before each research call, require the independent batch encoding gate and
the independently calibrated complete native-assignment/raw-object gate.
Bind both exact gate hashes in the command and manifest, require the object
gate to bind the exact encoding gate, and rehash every input named by either
gate. Reuse the frozen base native harness and its authenticated binary,
CLI/ext4 calibrations and decoder only for producer-side candidate decoding.
The separate object checker must verify any SAT result, including raw C
equality with the selected core and every clause of the exact fixed CNF.

Plan one serial attempt per core00..03, each limited to 300 seconds, two
million configured conflicts, 4 GiB address space, 10 GiB proof file, a
five-second termination grace, and a 320-second outer guard. There are no
automatic retries. Before each call require at least21 GiB host disk and
11 GiB ext4 disk. A resource-preflight failure is recorded, not interpreted
as UNSAT. Interrupted/completed attempts are never silently restarted.
No seed override; retain the native default. No floating acceptance test.

Pause the batch on a SAT result until complete independent raw checking and
residual completion analysis have been performed. On UNSAT, preserve and
independently replay the whole proof before reporting any fixed-core
exclusion. A checked fixed-core UNSAT still gives no unrestricted conclusion.
An UNKNOWN result is preserved and the next chosen core may be attempted.
An expired outer guard requires a fresh process-state check before launching
another instance. All native and transfer logs and incomplete traces are
retained. Successful SAT supplies only a necessary factor, not99 adjacency.

Per-call commands use the locked root environment, `--research` or
`--preflight`, `--core-index 0` (then1,2,3), a fresh `--out`, and exact
`--encoding-gate`, `--encoding-gate-sha256`, `--object-gate`,
`--object-gate-sha256` arguments recorded in the saved manifest.

