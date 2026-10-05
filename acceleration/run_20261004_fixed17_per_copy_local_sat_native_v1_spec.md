# Fixed-count local-row native SAT launcher, version 1

This is a SOURCE_ONLY sibling of the immutable October 3 unrestricted launcher
V2. The new source changes only its scope comment and allowed duration literals
from `10|3300` to `10|1800`. The original source/spec and all historical receipts
remain unchanged. No shell syntax test, import, native execution, proof replay or
scientific invocation has occurred during preparation.

The launcher takes four arguments: CNF path, new text-DRAT output path, exact
SHA256-list path, and literal duration `10` or `1800`. It checks argument count,
UID1000, the duration whitelist, existing CNF/list files and absent proof path;
prints tool versions; verifies the complete submitted checksum list; then uses
`exec prlimit` with 8GiB address space, 4GiB file size and zero core limit, followed
by `timeout --foreground --signal=TERM --kill-after=5s`, the pinned CaDiCaL binary,
`--no-binary --seed=0`, the CNF and proof path. No background child, new session,
daemon or launch retry is added. Native SAT/UNSAT return codes are intentionally
not converted to zero.

The Bash file does not itself validate that an arbitrary checksum list contains
all required identities or confine arbitrary argument paths. Each future exact
plan must authenticate the list's bytes and complete rows, using only the fixed
workspace paths, and must include the submitted CNF, this source and the unchanged
CaDiCaL binary. Fresh-output checks and source/list/input hashing belong inside
the supported bounded invocation or an explicitly allocated pre-seal command.
The launcher has no calculation receipt writer: supported SUP2 owns containment
and durable stdout/stderr/progress/manifest/terminal receipts. Root supplies a
separate bounded closing identity/result observation. A race with another writer
or an unobserved escaping descendant is outside the contract.

Use unchanged `run_compute_command_v2.py` on Linux, runtime scope
`LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2`, in the same workspace/UID context. The six
previously reviewed native/ordinary-descendant/mixed hard and missed-reassessment
controls qualify only that unchanged nonescaping containment component. Their
raw review identities are explicit plan dependencies. They do not calibrate this
new duration selector, tiny native outcomes, SAT interpretation, proof bytes or
a future local formula. A Windows WSL timeout is not containment. WSL may be a
transport into an already supported Linux SUP2 invocation; it must not be used
as the sole native guard. Preserve original-group scans and exact known descendant
identities when required; never infer global process absence from one empty group.

## Proposed finite controls

Five separately authorized Linux invocations, each 60outer/10native/20shutdown,
are proposed. They are not an automatic sequence or five launches authorized by
this file. Every new output directory must be absent before its ONE command.

1. SAT: two variables, clauses `(1 or 2)` and `(-1 or 2)`. Require actual native
   integer10 and a unique `s SATISFIABLE`. Independently parse every `v` token,
   require exactly variables1,2 once with no opposite/duplicate/zero-in-middle,
   terminal zero and no extra assignment tokens, and evaluate both raw clauses.
   The second variable must be true; either first sign is permitted. Native status
   or exit10 alone is insufficient. No proof interpretation is needed for SAT.
2. UNSAT: all four sign combinations on two variables. Require integer20 and a
   unique `s UNSATISFIABLE`, closed nonempty text DRAT with final added empty
   clause, then a separately authorized direct replay by the qualified unchanged
   `build/rook-drat-checker/drat-trim.exe`. Replay requires actual integer0,
   exactly one status `s VERIFIED`, clean supported Windows SUP2 terminal and
   matching pre/post formula/proof byte identities. This is an empty-clause proof,
   not acceptance of an empty proof file. The nontrivial fixture avoids the
   checker's known parse-trivial UNSAT exit limitation.
3. Wrong checksum: the SAT list changes only its CNF digest to 64 zeroes. Require
   exit1 before native launch and no created proof file. Actual stderr must report
   checksum failure; no native SAT/UNSAT line may be present.
4. Unsupported duration11: require exit64 before version/checksum/native output
   and no proof file. Whitelist acceptance for1800 is statically reviewed here;
   no long native control is proposed or claimed as executed.
5. Pre-existing proof path: a literal `sentinel\n` file is supplied. Require exit1
   before version/checksum/native output and byte-identical sentinel afterwards.
   It is deliberately an existing input fixture, never a purported native proof.

After authentic UNSAT closure, fill a separate read-only proof-check plan from
the new proof's actual hash/size. The Windows qualified DRAT component has five
historical positive/corrupt controls; no changed proof algorithm is proposed.
Fresh replay of the new proof is still required. Two new negative direct checks
are proposed: only `0\n` for the nontrivial UNSAT formula must be rejected, and
the new UNSAT trace against the SAT formula must be rejected. Actual integer1
and unique `s NOT VERIFIED` are expected; an unexpected status, timeout or error
is preserved and not reclassified as a passing negative. No weakened exit rule
or deletion/forward flags are allowed. A whole-file proof change control is not
a substitute for native closure and bounded pre/post seals.

SUP2 normally returns2/`NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET` when its child exits
10,20,1 or64, even if the tiny intended control completed. Preserve those literal
fields. A separate engineering control verdict requires `COMMAND_EXITED`, exact
expected child code, null error, no deadline, reaped/observed-empty original Linux
group, empty cleanup errors and actual elapsed within its60-second allocation.
Do not rename the supervisor status or infer mathematical incompleteness from the
expected nonzero SAT protocol. All case and independent-check outcomes remain
null until actual execution/review. No automatic retries or chain to science.

## Future local SAT proposal

The current science allocation proposal is1800native/2400outer/180shutdown with
a Root reassessment by1750 active seconds. The inner TERM/KILL grace shares the
same outer deadline. This proposal is based on a smaller necessary local formula
and the separate per-copy MIP UNKNOWN after1200 native seconds; it is a ceiling,
not a performance forecast or cumulative budget subtraction. The local encoding
must first receive a genuine complete different-author clause/EOF gate. Current
actual formula/model/config/encoding-gate/proof references remain null.

A verified SAT assignment would establish only this fixed-count exterior local
row system's feasibility; no outside-pair CN equations or full99 graph acceptance
are implied. Native20 requires complete closed text proof and independently
qualified exact replay before excluding even this one count profile. Timeout,
partial DRAT, native UNKNOWN or numerical MIP UNKNOWN excludes nothing. All native,
proof and required hash/check transfers have their own declared inclusive command
allocation. Keep live ledger/index/Git untouched and preserve every failure.
