# Local-row native launcher V2: binary DRAT

SOURCE_ONLY. Preserve the text launcher V1, its specification, native runs and
all prior proof checks. The sole execution delta is removal of `--no-binary`
from the final CaDiCaL argv. Comment, argument count, UID1000, workspace,
duration whitelist10|1800, source-list checks, absent-output check, seed0,
8GiB address-space/4GiB file/core limits, foreground timeout and5-second
TERM/KILL grace remain byte-equivalent. No syntax test, solver or proof checker
has run during preparation. The source diff is a single standard hunk.

Pinned CaDiCaL's options.hpp defaults binary=1, and its drattracer.cpp writes
an `a` or `d` byte, variable-length literals2*abs(lit)+(lit<0), and a zero byte
terminator. This is a source observation; the fresh native controls must
confirm actual binary output from the exact pinned executable. The file's
`.drat` extension does not establish its format. SAT model/status stdout is
unchanged, and complete signed assignment/clauses must still be independently
checked. SAT exit10 with an empty proof is not an UNSAT certificate.

## Preserved containment and prospective native controls

Use the unchanged supported Linux SUP2, runtime scope
LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2. WSL can transport the Linux invocation;
a Windows wsl.exe timeout is not the containment mechanism. Six historical
nonescaping hard/reassessment guard controls qualify only that pinned runtime
component. They do not approve this format change, a fresh solver/proof result
or a future scientific formula. Fresh two-host scoped ownership/resource
observations must attribute any still-live Root text invocation rather than
infer absence from plans or historical PIDs.

The five new controls are separately authorized invocations, not an automatic
chain: two-variable SAT, four-clause UNSAT, bad CNF checksum, unsupported11
seconds, and a pre-existing sentinel proof path. Each uses60outer/10native/
20shutdown, with5 inner grace. The native positive/negative exit expectations
are10/20/1/64/1. Each new SUP directory must be absent. The existing-output
case refers to the separately preserved sentinel input, which must not change.
Lists contain exactly the formula, V2 launcher and pinned CaDiCaL SHA256 rows;
the negative list changes only the formula hash. The launcher does not validate
arbitrary-list population itself, so Root admission compares every exact row.

Every case needs COMMAND_EXITED, exact integer child code, null error,
deadline=false, reaped/observed-empty original Linux group and no cleanup
errors. Preserve SUP2's literal nonzero-child NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET
status even when a tiny expected SAT protocol/rejection completed successfully.
A separate engineering verdict must not rename those immutable fields.

## Fresh binary proof qualification and a Windows portability veto

Old text-proof gates do not transfer. The preserved Windows checker23d161
opens proof input with `fopen(...,"r")` and its portability patch changes
headers/time only. No binary-mode setting was found in its authenticated source.
The MSVC CRT documentation says text input recognizes byte0x1a as EOF and
translates CRLF into LF. Therefore two-variable binary traces alone do not
qualify that checker for arbitrary binary DRAT. Do not patch or approve the
historical checker. A distinct pinned upstream-source Linux build is proposed
in build_20261004_local_sat_binary_drat_linux_v1.sh/spec; its actual binary and
Root build acceptance remain null until separately admitted and executed.

The independent raw verifier must decode all record prefixes, unsigned
base128 literal payloads, terminators and EOF from byte-preserving reads.
Require complete final added empty clause and exact input/proof identities
before and after replay. A merely well-formed empty clause or native20 is
insufficient. New direct Linux checker controls, each60outer/30checker/
20shutdown, are:

* the authentic new native UNSAT proof, with fresh hash/size filled only after
  native closure; expect0 and exactly one `s VERIFIED`;
* a hand-encoded eight-byte RUP proof on variables13,14, containing+13=0x1a;
* a hand-encoded twelve-byte RUP proof whose first record contains adjacent
  payload bytes0x0d0a; translating them would change its first clause into a
  clause that is neither RUP nor RAT for the declared formula;
* only the binary empty addition `61 00` on the original nontrivial four-clause
  UNSAT formula; expect1/unique `s NOT VERIFIED`;
* the authentic native proof supplied to the satisfiable two-clause formula;
  expect1/unique `s NOT VERIFIED`;
* a hand malformed-derivation trace on variables13,14 that duplicates one
  original clause and then adds empty without a propagation conflict; expect
  1/unique `s NOT VERIFIED`.

The hand positives prove parser-sensitive behavior independent of whether
native remapping heuristics happen to emit those bytes. Their exact clauses,
byte sequences and written RUP/RAT checks are in the finite control packet.
No force-binary, forward/deletion bypass or weakened exit convention is added.
Different-author raw arithmetic/byte/receipt review remains mandatory. An
unexpected code/status, malformed input, timeout or error is an unmet case,
preserved without automatic retry. A truncated/corrupt prefix is not accepted
merely because an earlier contradictory prefix happens to replay.

## Scientific eligibility remains deferred

The existing text science command is not changed, restarted or superseded by
this packet. No new scientific vector is provided. A future binary run needs
accepted new native controls, the newly compiled Linux checker identity and
all binary positive/negative controls, plus exact complete encoding/result
gates and a new Root ONE. No expected performance or success probability is
claimed. Text-proof file growth and low CPU-to-wall ratio suggest an I/O
hypothesis only; no measured causal attribution was made here.

Reference for the Windows portability boundary:
[Microsoft fopen file modes](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/fopen-wfopen?view=msvc-170).
The primary pinned local tracer/checker sources are the implementation evidence.
