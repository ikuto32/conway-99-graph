# One gated count-master partial-cut native attempt

Prepared source only. The author does not import, preflight, or run this wrapper;
the parent controls any later execution after independent gates and source review.
No automatic retry is authorized.

The fixed formula is
`results/20260930_count_master_scalar_cuts/instance.cnf`: 155,939 variables and
705,845 clauses, SHA256 baca89a7014e10e1fea9fd1873ef5dde4a090ab02dfe1791b4734a196677880b.
It is the original >=7 count-table CSP plus six independently justified whole
count-profile exclusions and six necessary scalar-bound clauses. The latter are
the six ordered distinct-fibre instances on coordinates9,11. This is a count
relaxation; full Gram realization, cross-group column caps and residual D are
not encoded. SAT is not a factor or graph. No target automorphism is assumed.

One native call only: 60 seconds wall, 1,000,000 conflicts, 4 GiB address space,
10 GiB trace file, 5-second kill grace and 70-second outer guard. Before launch
require ext4 /tmp and at least11 GiB free there plus21 GiB free on the host.
The guard concerns the native call, not hashing, transfer or independent checking.
Keep all receipts and attempted outputs. Immediately hash/copy the ext4 trace to
the host after normal wrapper return; authenticate both identities. A later loss
of the ephemeral ext4 path is possible: record creation observation and retention
intent, with future availability UNKNOWN. Never claim permanent preservation.

Preflight is fail-closed. Require exact raw new CNF/model/scope/summary and inherited
metadata, all producer-summary inputs/outputs, native helper/tool pins, and both
independent reports. Exact statuses:

* INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_CNF_PASS
* INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_OBJECT_CALIBRATION_PASS

The object report must bind the same encoding report and the entire loaded
repository source/spec closure, independent checker source, solver and proof
checker. The wrapper imports only the frozen native engineering helpers; no
count producer or decoder is imported. Targeted `ps -C cadical` observations
accept exit1 with header-only output as no exact-named process observed.

On exit10, parse all155,939 distinct signed IDs from native stdout and save
`main/parsed_model.json`. Invoke the separately gated checker exactly as:

`sat --variant at_least_seven --encoding-gate PATH --encoding-gate-sha256 SHA --assignment JSON --native-output LOG --out NEWDIR`.

The checker reconstructs the count object; the wrapper supplies no optional
producer-decoded object. The wrapper records SAT_RAW_UNCHECKED even if a checker
receipt exists: approval is the separate report. On exit20, save the complete
trace as UNSAT_TRACE_UNCHECKED pending full independent replay. UNKNOWN excludes
nothing. No ledger/publication changes.

CLI requires mutually exclusive --preflight or --research plus --out,
--encoding-gate/--encoding-gate-sha256, --object-gate/--object-gate-sha256 and
--object-checker. Every output directory must be new. No default gates or hashes.

Engineering template: the unchanged native_20260930_count_interval.py and
native_20260930_count_master_eight_orbit_cuts.py. Their mathematical scope is not
inherited; this wrapper binds the new scalar-cut model and independent gates.
