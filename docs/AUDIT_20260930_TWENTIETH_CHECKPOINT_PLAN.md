# Wave20 independent checkpoint review plan

This is a preparation record, not a completed checkpoint audit. The recorder,
final checkpoint, report and publication inventory must be frozen before the
new independent checker is executed. No mathematical replay is implied by
bookkeeping or publication checks.

The three approved registration receipts form the exact chain
188 -> 191 -> 192 -> 194 claims. The six new records consist of five VERIFIED
claims and one REFUTED claim. The final population must be 191 VERIFIED/CLEAR,
two CANDIDATE/CLEAR and one REFUTED/CLEAR. Existing semantic claim records and
their revisions must be unchanged. The starting ledger is the public wave19
ledger at commit4442207abbe24effffefb56ab323e3891bc3fafd; differences from the
wave19 milestone snapshot must be authenticated publication metadata only.

The exact new IDs, in registration order, are:

- C-FIXED-HADAMARD-ALL-MIXED-ORIENTED-TRIPLE-ENCODING
- C-FIXED-HADAMARD-ORIENTED-TRIPLE-NATIVE-UNKNOWN
- C-FIXED-HADAMARD-COMPLETE-BALANCED-GRAM-ENCODING
- C-FIXED-HADAMARD-BALANCED-GRAM-EXCLUSION
- C-FIXED-HADAMARD-AT-MOST-TWO-GROUP-MARGIN-CANCELLATION
- C-FIXED-HADAMARD-SUPPORT-INTERSECTIONS-ZERO-OR-THREE (REFUTED)

The two native research calls have distinct outcomes and scopes. The oriented
800-variable109340-clause projection stopped UNKNOWN at1000000 conflicts;
its331620166-byte trace is partial, retained locally, and is not a proof.
The balanced10480-variable74200-clause model returned UNSAT and its complete
227098316-byte DRAT trace was independently replayed. Only the balanced
subfamily of one literal support is excluded. There is no new full factor,
whole-support exclusion, core exclusion or unrestricted target conclusion.

The balanced proof audit is pinned by SHA256
edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5.
It binds CNF c2d780f94dac4dda955743df03f8db2e8ec0f51217c671eb19fc5e42ed69ba37
and proof94d2ab35c76b61f3deb01ebfd9ca0dc70452bddf847383d5838b2b2ca902396b.
The checkpoint audit will authenticate its complete accepted replay, checked
positive/negative controls, checker provenance, exact encoding premise and
scope. It will not relaunch the solver or claim a second DRAT replay.

Proof transport audit54f3d947df7c3387a6b2960e9a0b966014f731c8105854cc4f3b94bcda6d4393
confirms exact recovery from six ordered gzip parts, totaling52339920 compressed
bytes. The public inventory must include every part and the recovery metadata;
the complete raw proof is recoverable, not omitted as an incomplete trace.
Each selected public payload must be at most10MiB and match its saved byte count,
SHA256 and Git-filter byte identity. Failed producers, checker failures and
correction records remain explicit publication payloads.

The private file
acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log
must be absent from the public catalog and stage inventory. Its original bytes
remain local. Historical hash references are preserved without publishing or
copying the private process listing into any new report. The recorded solver
stdout, which is a different file, is not subject to that specific omission.

The refuted intersection restriction stays separate from valid row-margin
cancellation: the full190-pair intersection histogram is
{0:1,1:16,2:58,3:60,4:47,5:8}, with an explicit size2 counterexample.
The newer full-Gram at-most-three-exception implication, its corollary and
four-support circuit work belong to wave21 and must not enter wave20 counts.

The executable review will test corrupt count, outcome, scope, proof identity,
transport and privacy records, authenticate the frozen process census, and
take a separately labelled fresh process observation. A live later-cohort
process does not change the historical outcomes. Overall search coverage stays
UNKNOWN because there is no validated target-wide denominator.
