# Fresh Linux DRAT checker build for binary proof controls

SOURCE_ONLY; no compiler, syntax test or proof checker has executed. This new
physical Bash source builds only preserved upstream-drat-trim.c at SHA256
d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee,
whose historical manifest authenticates upstream commit
2e3b2dc0ecf938addbd779d42877b6ed69d9a985. It does not read the dirty submodule
as build input and does not apply the Windows portability patch. All old
source/build binaries and receipts remain unchanged.

The zero-argument builder requires UID1000 and the fixed workspace, requires
the new build/fixed17-local-sat-binary-drat-linux-v1 directory absent, checks
the exact original SHA256, prints Bash/GCC/sha256sum/timeout/prlimit versions,
creates the new directory, copies source bytes and verifies that copy. It
then runs the literal compiler command

    /usr/bin/gcc build/fixed17-local-sat-binary-drat-linux-v1/drat-trim.c -std=c99 -O2 -o build/fixed17-local-sat-binary-drat-linux-v1/drat-trim

under prlimit8GiB/128MiB-file/core0 and a foreground90-second timeout with
5-second TERM/KILL grace. Supported Linux SUP2 owns180outer/20shutdown,
including copy/hash/version/compile/closing seals. GCC and Bash children must
remain in the original contained group. No other binary, formula or proof
is executed. On success the fresh executable and copied source receive
build.sha256; the SUP owns raw version/compiler logs and durable receipts.
Root must authenticate actual compiler/runtime/utility identities and source,
full literal argv, absent output and resources immediately before its ONE.
Prospective compiler hashes/actual binary/elapsed/Root acceptance are null.

The source uses no guessed compiler hash or inherited build gate. Its exact
hash and version are observed in the new Root admission and completion. This
one-file build's short allocation is an evidence-based engineering proposal,
not the historical120-second cap. A compile error or timeout remains a failed
build with partial outputs preserved, no fallback flag/source change/retry.

POSIX file reads preserve bytes when fopen mode is r. The unmodified source
supports binary detection and base128 literals, but that source observation
is not an executed format qualification. Root must separately authorize all
new hand0x1a/CRLF-sensitive positives, genuine native proof and negatives,
then obtain different-author raw reviews. No old Windows text qualification,
compiler identity or semantic proof approval transfers to this Linux binary.
No scientific invocation or target/count-profile conclusion follows from build
success or the finite controls.
