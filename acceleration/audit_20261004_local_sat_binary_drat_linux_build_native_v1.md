# Independent source-only review of the Linux DRAT build component

The frozen one-source build component has no material static veto within its
stated engineering scope. This review does not qualify binary parsing, the
finite proof-control packet, the V2 native launcher for science, or any proof.
The separate original byte-sensitive fixture coverage veto remains in force.

Reviewed sources are the whole new Bash build, whole specification, complete
logical build plan and literal18/2 argv. Seventeen small identities were
freshly checked: the plan's15 direct pins, the plan itself and the packet
freeze. The exact upstream source d834 is the build input. Its historical
manifest/receipt were read as provenance; the old Windows patched checker
is not used as either the source or the produced Linux binary.

## Literal path and command checks

The builder requires zero arguments, checks actual Linux UID1000 and changes
to the fixed /mnt/c workspace. The original upstream C file must exist and
the new build directory must be absent. The original SHA256 is checked before
copying. Plain mkdir, without -p, refuses a preexisting output directory.
Copying is followed by an exact SHA256 check on the copied source. No
unreviewed dirty submodule, alternate source, Windows patch or fallback
compiler flags are consulted.

The compiler argv is exactly six words:

    /usr/bin/gcc build/fixed17-local-sat-binary-drat-linux-v1/drat-trim.c -std=c99 -O2 -o build/fixed17-local-sat-binary-drat-linux-v1/drat-trim

This is a prospective argv, not an executed compiler receipt. The GCC file
hash and observed version are null pending a fresh Root admission. The
source prints Bash, GCC, sha256sum, timeout and prlimit version information;
Root must bind their actual host identities rather than treating these
textual names as a compiler or utility qualification. No --version command
was executed by Native during this review.

The outer command is the supported inside-Linux SUP2 using its unchanged
464102 source and9876 deadline helper. There are18 supervisor words:
the16-word fixed prefix ends with -- and the two-word child is /usr/bin/bash
plus the build source. command and supervisor_argv are identical and the
child is their exact suffix. Neither Windows wsl.exe supervision nor an
unsupported cross-host process tree is proposed.

The compiler itself is wrapped by prlimit with8GiB address space,
128MiB maximum file size and zero core dumps. Foreground timeout permits90
compiler seconds with5 seconds TERM/KILL grace. The180-second invocation
also includes source copy, hashes, version output and the closing build seal,
with20 seconds allocated to supervisor shutdown. These limits fit inside
one invocation's user ceiling; this is an explicit short engineering
allocation, not a reinstated historical default build cap. Source inspection
does not prove hard real-time stopping. Only the actual SUP receipt can
show elapsed time, original group identity, cleanup and reaping.

Shell set -eu stops an ordinary failing required command. A failure of
hash/copy/compile prevents the success seal. The binary is checked for
executable status after compilation, then build.sha256 records the copied
source and binary. No produced checker or solver is run by this builder.
An executable file and two hashes are build outputs, not a semantic proof
checker gate. Failure may leave the newly created directory, source or
partial binary; they must be preserved rather than reused in an automatic
retry. A new Root ONE is required for any successor.

## Required admission and actual acceptance

The plan retains null HEAD/ledger/index, compiler hash/version, actual
invocation/binary/terminal and Root authority. They are future fields, not
assertions of present absence or successful build. Root must save and read
fresh two-host scoped ownership/resource observations, exact current
context, plan pins, original source, compiler/utilities and output absence
before authorizing this one command. Available memory and disk guards are
admission requirements, not measurements performed by this source review.

Success requires compiler exit0, the three declared build files, fresh
source/binary hashes and a clean supported original Linux group without
error or deadline. Preserve every literal supervisor status. The six old
hard/reassessment controls are inherited qualification of the unchanged
nonescaping supervisor component only; this review neither reruns them nor
transfers a Windows text-proof result to a Linux binary checker.

POSIX r-mode proof reads avoid the historical Windows CRT text translation,
but build success alone does not test the reader. The original finite
Ctrl-Z/CRLF positives have a backward-core coverage issue identified
separately. New dependency-bearing byte fixtures and explicit damaged-byte
negatives must pass with the new authenticated Linux executable before
binary format eligibility is considered. Complete scientific proof replay,
formula identity, record/EOF validation and independent result acceptance
remain separately required.

This review records20 source/plan boundaries and zero executed controls,
compiler calls, solver/checker calls, imports or scientific launches. All
sources and historical receipts are unchanged. No ledger/index/Git query or
mutation occurred. Root remains the prospective executor and must supply
actual receipts; Native has no computational worker.

