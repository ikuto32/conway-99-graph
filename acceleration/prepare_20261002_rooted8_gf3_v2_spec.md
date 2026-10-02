# Original literal GF(3) worker, wrapper version 2 / C++ version 1

Version 1's partial control run is preserved. Its divided scope fixture passed
raw scalar membership, then failed a stronger assertion requiring one particular
hand-written witness. That fixture has three solutions per RHS; the native
least-column pivots can choose another witness. Version 2 removes only that
particular-vector equality. Exact scalar membership, explicit different raw and
divided scope, all inputs and the complete finite population remain mandatory.
The C++ source/binary algorithm is unchanged. New wrapper/spec/build/control
bindings are required; this correction does not approve the original failed run.

This source/build/control population is new. Neither preserved GF(2) gates nor
repeated producer execution approve it. Arithmetic source shares disclosed
policy/CLI/checkpoint ancestry with the GF(2) producer, but uses new two-plane
ternary addition, three independent RHS residues and weighted original-row DAG.
No producer import is permitted in the independent scalar checking path.

The scientific input is the exact original 23,019-column/85,874-row JSON operator
`a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b`.
Recompute every integer content/raw/normalized row hash and full normalized
stream against manifest `47c9f0158084a1cf04b9ce2f84db93ee748e5e3226d759f276090aa50bdfe91c`.
Sparse GF(3) coefficients come from ORIGINAL rows, aggregating signed/repeated
terms modulo 3. Actual contents 1/2/4 are units modulo 3. The content3 toy is
explicitly different: raw and divided GF(3) solution sets need not coincide.

Wire format: `GF3_AFFINE_SPARSE_V1 n m`, then each row has three RHS residues
0..2, a term count, and ordered unique `(column,coefficient)` pairs. Coefficients
are 1 or 2; no zero or out-of-range columns. Output vectors are
`x_const.trits`, `x_a.trits`, `x_b.trits`, each headed
`GF3_AFFINE_PRIMAL_V1 n label`, then exactly n digits 0..2 and final newline.

The alternative `original_row_relation.json` is
`ORIGINAL_LITERAL_GF3_ROW_RELATION_CANDIDATE_V1`: `matrix_rows`,
`matrix_columns`, `rhs_affine_residue:[const,a,b]` and strictly increasing
`original_row_coefficients:[[raw_row,coefficient1or2],...]`. Coefficients refer
to original integer rows, with no hidden division or rank assertion. First
nonzero affine relation only; no exhaustive affine-relation claim.

Checkpoint bytes on the pinned Linux x86_64 little-endian platform:

- 17 ASCII bytes `GF3_PRIMAL_CP_V1\n`, then 64 exact input SHA-256 ASCII bytes.
- Four uint64 values: n, m, words=ceil(n/64), completed-row prefix.
- For each potential pivot column p in order: one presence byte 0/1.
- If present: three RHS trit bytes; one original-row scale byte 1/2; uint64
  original row, insertion-order index and dependency count; dependency records
  `(uint32 pivot_column, uint8 coefficient1or2)` in strictly increasing pivot
  order; `words` uint64 one-plane values; `words` uint64 two-plane values.
- No additional tail. References must point to present earlier inserted rows.
  Planes are disjoint, pivot trit is one, lower prefix and unused padding zero.

The weighted DAG identity for a basis row is its recorded original-row scale
times that original sparse row, plus recorded coefficients of prior basis
rows. A negative relation expands these identities backwards; the independent
checker must reproduce every column/RHS using raw scalar arithmetic.
Only completed rows enter a checkpoint. Mid-row timeout retains the previous
completed state, and no automatic restart or deadline extension occurs.

Every tiny native call records command/cwd/input hash, GNU guard, prlimit,
actual exit, logs/hashes, artifacts and getrusage RUSAGE_SELF (Linux KiB peak
RSS; process only, no whole-group peak/performance guarantee). Exit0 means raw
three-vector candidates; exit3 means raw relation candidate; exit4 means saved
incomplete prefix; exit2 is a declared engineering parser failure only.

Finite controls freeze five literal cases: singular original, full-rank original,
inconsistent original, multiword original, and divided content3 scope control.
Original singular/negative fixtures have repeated/negative terms and contents
2/4/3. Independent tiny assignment enumeration and scalar raw-row checks must
decide their scopes. Four original cases use whole/prefix/resume; primal and
relation output bytes must agree. The multiword case uses n130, including
columns0/63/64/65/127/129. An arithmetic trace contains 18 packed-add records
(nine value pairs times scales1/2) and 81 RHS-add records (27 triples times
scales0/1/2), with exact padded planes.

Eleven declared native negative cases cover ordered column/range, coefficient,
RHS, duplicate columns, checkpoint hash/RHS/scale/disjoint planes/leading one/
padding/weighted-DAG coefficient. Each requires exact expected stderr and empty
stdout. Additional producer scalar corruption diagnostics remain producer-only.
Independent controls must falsify malformed states/artifacts through a separate
implementation and bind the exact source/binary/build/input population.

Build and controls use CommandDeadline and Linux-contained run_compute_command,
locked native_budget_env_v1 with pinned tqdm and g++13.3 compiler hash. The
compiler has a supported child guard/resource limit; engineering allocations are
declared in the saved plan. Scientific mode additionally requires exact new
`INDEPENDENT_ORIGINAL_GF3_PRIMAL_RELATION_CONTROLS_V1_PASS` source/binary gate
and `INDEPENDENT_GF3_LITERAL_ENDPOINT_CHECKER_CALIBRATION_V1_PASS` checker gate.
Root must bind committed source, recoverable raw input package and fresh observable
worker/resource preflight before scientific use. Producer outputs remain
CANDIDATE pending raw independent checks. No rank, integer/nonnegative graph
feasibility or Conway-99 resolution follows. Necessary target interpretation
remains conditional on the UNKNOWN prism-free premise.
