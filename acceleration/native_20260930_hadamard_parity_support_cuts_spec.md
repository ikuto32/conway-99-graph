# Prepared native sixty-cut parity projection pilot

Source and protocol preparation only. Do not execute preflight or a research
solver as part of this task. Root separately reviews and authorizes execution
after both fresh independent gates are available. Previous parity witnesses,
their audits, and the selected-branch zero-row exclusion remain unchanged.

Question: does the necessary balanced parity projection admit any assignment
after adding all sixty constant-group support clauses? This ranges over all
twenty-group parity patterns in the strengthened formula, not only the earlier
selected assignment. Pin the new CNF
db9816ddf037250efc04b1e093e407eac0ec2c4fadf2f24b5774fb3249eba07f
and model
c477693bbf634609c234bf5b791c499f8f9ded091795b01bec297746288b4f4f.
There are 520 variables, 4,541 clauses, 220 selectors, twenty groups of eleven
patterns, sixty pair-disagreement relations, the previous nonconstant clause,
and sixty new support clauses. The complete original body is retained by the
separately audited producer. No new auxiliary variable is needed.

The new clause for each coordinate pair says that at least one of its five
containing groups disagrees in parity at that pair or selects the constant
pattern. The exact general lemma is independently checked in
independent_review/hadamard_balanced_parity_cuts/summary.json, SHA256
31c47c1faccc8ae043433f814932e2d419e1c2a188ffc1bd54a53b21ceeca6c1.
These are necessary conditions for the prescribed Gram with the additional
balanced-triplet assumption. They do not construct a color lift.

The nonconstant clause still requires the earlier complete cyclic-factor
exclusion when used as a necessary condition for balanced full factors WITH
all outside-column caps. Its gate is pinned to
83029350b25523c015dfe916d8056324c0970021d2b024d68941dd41fb8c2b70.
Neither balancing nor cyclicity is a general normalization. No target
automorphism is assumed, and no residual D is encoded. Even a proved UNSAT
outcome concerns only this necessary projection and, with the full independently
checked implication and premises, the balanced fixed-support family.

Require fresh encoding gate
INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_ENCODING_PASS at
independent_review/hadamard_parity_support_cuts_encoding/summary.json, and
object gate
INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_OBJECT_CHECKER_CALIBRATION_PASS at
independent_review/hadamard_parity_support_cuts_object_calibration/summary.json.
Supply their real hashes as mandatory arguments; none is invented here.
Both must bind the exact new CNF/model. The object gate must bind the same
encoding gate. The encoding gate directly binds the sixty-cut lemma and prior
cyclic exclusion. Check all gate-bound inputs and native provenance afresh.

Use one unchanged authenticated native CaDiCaL1.9.5 call with a 60-second WALL
guard, 100,000 configured conflicts, 4 GiB address-space limit, 10 GiB proof-file
limit, five-second termination grace and an 80-second outer Windows guard.
There is no CPU rlimit. Keep the calibrated native/ext4 helpers and native
default seed; no retry or reset. Reserve 21 GiB host and 11 GiB ext4 disk.
Stream ASCII proof bytes to a new ext4 directory, retain them, and copy the
exact trace back with hashes. Preserve every failure, partial trace, stdout,
stderr, actual process receipt and transfer anomaly. Observe actual CPU/wall
and conflict totals afterward. After outer-guard expiry process state is
UNKNOWN until a new observation.

On SAT preserve all 520 signed native literals and the candidate projection.
The decoder rederives all sixty disagreement counts and all sixty support-cut
checks from the chosen raw parity patterns. The new field support_cut_checks
is a list of records with coordinates, disagreement_count,
selected_constant_groups and satisfied. It also compares each condition with
the associated actual clause. This matches the independent checker contract.
The original pattern/index/support-mask fields remain, with hex interpreted as
integers by the independent corrected checking path. Every native assignment,
all 4,541 clauses, and the raw projection require separate approval. SAT does
not produce F, prove outside-cap feasibility, or construct a graph.

On UNSAT retain a complete proof for independent replay; never promote exit20
alone. UNKNOWN, timeout, errors or incomplete proof traces are not exclusions.
Do not invalidate the prior projection witness: it satisfied a weaker formula.
Its inability to lift was a different independently checked result.

The new file is derived from the frozen prior parity runner. It reuses the same
authenticated native parser and ext4 control helpers, with changed input pins,
gate contracts, output names and candidate decoder checks only. The manifest
binds all these sources, the exact command and source commit, locked environment,
tool binaries, scope and resource limits.

Later root-controlled CLI uses the root locked uv environment, a fresh --out,
one of --preflight or --research, and --encoding-gate,
--encoding-gate-sha256, --object-gate, --object-gate-sha256. Preflight performs
zero research solver calls. Source preparation itself executes neither mode.
