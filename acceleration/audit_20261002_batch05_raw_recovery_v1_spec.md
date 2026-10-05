# Independent batch05 lossless recovery audit

The frozen population is the native batch05 manifest direct pins, the previous
complete independent64proof audit direct pins, their summaries, and an explicit
packaging/source/environment helper set. The independent consumer reconstructs
this union itself, compares the exact case IDs and raw proof/CNF/model/scope
bindings, and requires the normalized manifest to cover every distinct member.
Historical mathematical gates are not recursively repackaged. Two platform
binaries are separately authenticated and disclosed as LOCAL_ONLY.

Before full launch, acceptance requires every compressed part hash/size, every
contiguous offset, every decompressed part hash/size, every raw record hash/size,
and literal equality of every reconstructed byte against the available frozen
original. Decompression reads no more than one byte beyond the declared part
bound. Empty files and multiple parts are positive controls; modified raw and
gzip hashes, wrong lengths, noncontiguous/duplicated parts, conflicting original
bytes, decompression bounds and path escapes must fail. The packaging module
and historical recovery implementation are not imported.

Full allocation: a supported600-second Windows Job invocation, internal570seconds
with30seconds reserved for output/shutdown. The population is about1.13GB raw
and108MB compressed, with934members/936parts. Native producer compression took
71seconds; independent decompression/hashing/byte equality is expected to be
cheaper, but this estimate is not a performance claim. tqdm reports completed
member count. Positive/corrupted controls are run separately before the full
audit and again within it. Every failure and unfinished population is preserved.

The result establishes local byte recovery only. Previous mathematical proof
replay is identity-bound but not repeated by this engineering check. PUBLIC
availability requires actual publication/independent metadata checks, and
complete raw direct closure is distinct from recursive historical gate closure.
