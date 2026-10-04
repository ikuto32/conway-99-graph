# Completed Linux DRAT build: independent component review

Native reviewed the completed Root-executed build at
2026-10-04T15:28:26.5408633Z. The result is PASS for actual build provenance,
output identity and observed contained terminal only. It does not approve a
binary proof parser, any finite proof/native controls, a scientific command,
or a mathematical result. Native executed no compiler or checker and changed
no build/source/receipt/Git/ledger bytes.

The whole Root admission df758d41, manifest, terminal, stdout, stderr, one
progress row and one original-group cleanup row were read. Root's actual
inside-Linux invocation is `1b49e3e8b7a7493182edc2f25dead32c`. The manifest
names SUP464, scope `LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2`, fixed repository
cwd, child Bash plus the pinned builder, 180-second outer allocation and
20-second shutdown reserve. The two child words match the admitted literal
18-word supervisor command's suffix. No retry or cross-host containment was
used; WSL is only the Root transport.

The terminal retains its literal status `COMMAND_COMPLETED_VERIFICATION_PENDING`,
`COMMAND_EXITED`, child and cleanup exit 0, error null, deadline false,
hard_limit_observed true, elapsed 0.8230475840000002 seconds. Original PGID
418 was reaped and its one cleanup observation contains no members, live or
unreadable PIDs, and no cleanup errors. This describes that observed invocation;
Native made no new global process-absence or hard-real-time guarantee.

Root's admission records actual UID 1000 and Ubuntu GCC 13.3.0, plus six Linux
utility hashes. These remain Root-observed provenance, not Native executions
of version commands. Actual stdout agrees with the recorded compiler and
Bash/coreutils/prlimit versions and contains both pre-copy and copied-source
strict checksum successes. The statically reviewed builder used the declared
single-source `gcc -std=c99 -O2` command under the 90-second foreground compiler
timeout, five-second grace, 8 GiB address limit, 128 MiB file limit and zero
core limit. Its final executable test and build seal were reached before exit.

The exact build inventory has three regular files. The source copy is 59,546
bytes, SHA256 d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee.
Native read both source byte arrays and compared them in full: they are equal.
The binary is 51,216 bytes, SHA256
d506ecaaee43c9f8221764cd5d92db45ea5e5a9a192227e015ad9412bc8b0e27;
its first four bytes are ELF magic `7f 45 4c 46`. The 244-byte `build.sha256`
has exactly the two expected source and binary rows, matching fresh direct
hashes. The supervisor inventory has six files: manifest, summary, stdout,
stderr, progress and Linux cleanup observations. None was overwritten.

The preserved 325-byte stderr contains a GCC warning at source line 986:
`getc_unlocked` has an implicit declaration under these exact C99 flags.
This warning did not prevent the actual link or executable test. It is an
unresolved portability/declaration limitation of the authenticated upstream
source, not permission to edit source or pretend a warning-free build. The
actual binary still needs its separately admitted finite positive/negative
binary controls. A successfully linked executable is not a parser theorem.

The prior static build review b36c7e4c/03f8c93f and all admitted small pins are
retained. The original proof-fixture coverage veto 25726812/5caec9f1 is separate
and still valid. Replacement controls must use dependency-bearing sensitive
bytes plus their explicit corrupted counterfactuals and actual clean terminals.
No historical Windows text gate transfers to this Linux binary. No proof was
checked in this component review; target resolution remains UNKNOWN.
