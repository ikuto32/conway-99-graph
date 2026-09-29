# Preregistered pristine native CLI calibration and unrestricted pilot

The first research invocation is disabled until the independent unrestricted
encoding/coverage gate, independent unrestricted SAT-object checker calibration,
and this separate native CLI calibration have passed. Root controls launch.
Preparation, tiny calibration and read-only preflight are distinct modes.

Native solver: official CaDiCaL1.9.5 commit
`146207318796f094dcded87349a64f0c6927309e`, pristine archive/build provenance in
`results/20260930_native_cadical195_build/`. Expected executable SHA256
`021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7`.
Use the existing Ubuntu24.04 WSL distribution, no installation or shutdown.
Only pinned Windows uv Python runs new orchestration code. Linux execution uses
existing native `timeout` and `prlimit`, whose help/version outputs are recorded.

Inspect both `cadical -h` and `--help`; the latter confirms `-c <limit>` and
`--no-binary`. Native model output remains enabled. The command writes ASCII DRAT
directly to a file, avoiding Python-native proof-stream conversion. Actual
native exit codes10(SAT),20(UNSAT),0(UNKNOWN) are preserved through GNU timeout;
timeout124, forced-kill137, resource signals and unexpected exits remain
distinct engineering outcomes. Raw model/proof bytes remain available even
after abnormal exits and require independent checking.

Calibration uses a satisfiable2variable formula and the four2variable binary
clauses whose contradiction requires reasoning. The complete SAT assignment
is independently parsed and checked, with duplicate/missing/conflicting/sign/
termination corruptions rejected. The native UNSAT proof must include a
nonempty derived clause; replay it with the fresh source-authenticated Windows
DRAT checker SHA256
`23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac`.
An empty-only proof on that formula must be rejected. Preserve exact commands,
inputs, outputs, logs, hashes and actual exits. Calibration is not a research
exclusion or a performance comparison.

The first unrestricted pilot is one call on the frozen4,136,454clause CNF,
SHA256 `7029f5c0965d0121aec6ce24db2b9a3d2e201e85b72c8ef51595c63bb62b2138`.
Model SHA256
`77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e`.
The family fixes only the189root scaffold edges and leaves all3486outerpairs
free. No target automorphism, K pattern or branch unit is assumed.

Limits fixed before launch:300seconds under GNU timeout, TERM at deadline and
group KILL5seconds later;1000000native conflicts; virtual address space soft/hard
8589934592bytes(8GiB); each native output file soft/hard10737418240bytes(10GiB);
core dumps disabled. `prlimit` applies these limits before exec. A small file-size
probe and an exact inherited-limit probe calibrate enforcement. The outer
Windows subprocess has a320-second guard; if it times out unexpectedly, Linux
process state is UNKNOWN until separately observed. Do not claim cleanup merely
from a missing process receipt. No automatic solver retry or budget extension.

Record initial disk availability and require at least11GiB free before the
research call. Proof size may never exceed10GiB; any partial capped trace is
retained as incomplete evidence. No unconditional compression of a large proof
is part of the300-second pilot; preserve raw artifacts and a streaming SHA256,
then root can package them under a separately recorded resource budget.

On SAT, retain stdout, parse exactly all1186500variable literals, and save
`main/parsed_model.json` as `{"assignment":[signed integers]}`. Decode an explicit
`main/decoded_full99.json` containing `adjacency_full99`. Producer integer checks
are recorded, but target status is determined only by the separately authored
complete assignment/CNF/full99 checker. On UNSAT, preserve the exact input and
native complete trace, pending independent authenticated DRAT replay and the
already required unrestricted encoding/coverage review. No result is merged
or declared generally accepted automatically.
