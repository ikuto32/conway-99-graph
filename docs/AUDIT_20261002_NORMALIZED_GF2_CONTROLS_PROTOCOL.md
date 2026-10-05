# Independent normalized GF2 engineering control audit

Verifier `/root/structural`, producer `/root/native_driver`. This protocol
precedes the verifier invocation. It approves tested engineering behavior and
full integer row-content identity, with no full native solve or rank claim.

Freeze producer v2 source, spec, plan, build/binary and eight saved control
receipts through `controls_manifest.json`, SHA256
`00f3fccb582133180583c48f1502c5dbc0f980324a92d295a3b1cd41ff601bf8`.
Required exits are exactly `0,4,0,3,4,3,2,2`, in the manifest's declared order.
The verifier imports no producer code and executes no native solver.

Independently hand-specify the four-variable, five-row integer fixtures.
Reconstruct every divisor with Python `math.gcd`, every normalized literal and
canonical hash, and all sparse parity bytes. Enumerate all 16 binary vectors
separately for each of the three affine RHS components: feasible domains have
four members each, inconsistent domains have respectively zero, four and four.
Check every saved full primal through raw integer division and scalar sums.
Check the inconsistent witness against every original column, including exact
integer sum diagnostics, with rows `[0,1,2]` and mask `1`.

Read all six positive/interrupted/inconsistent binary checkpoints independently
using the pinned little-endian format. Reconstruct each pivot from its original
row and earlier DAG dependencies; verify insertion ordering, pivot bits, padding,
input hash, dimensions and exact end. Compare all three exhaustive solution
domains of its completed raw prefix against its stored basis. Confirm whole and
resumed final primal bytes and original-row XOR bytes are identical.

Native malformed controls must have exit 2, empty stdout and the precise stderr
diagnostic `sparse ordered column range` or `checkpoint exact input hash`.
Unrelated exceptions do not pass these controls. Independently reject the saved
changed primal coordinate, raw coefficient/RHS and XOR indices/mask, nondividing,
zero and negative divisors; also calibrate syntax-only sparse input rejection and
input-hash checkpoint rejection before relying on later stages.

As a separately scoped full normalization check, recompute all 85,874 raw root8
row contents, complete literal hashes and the canonical normalized stream against
the pinned independent manifest
`47c9f0158084a1cf04b9ce2f84db93ee748e5e3226d759f276090aa50bdfe91c`.
This does not replay the native full-model computation or establish parity rank.

Allocate supported outer 300 / worker 260 seconds with a 20-second internal
checkpoint reserve, based on eight tiny saved runs and about one million raw
literal coefficients. On any failed pin, domain, checkpoint or diagnostic,
preserve failure evidence and issue no approval. Success emits
`INDEPENDENT_NORMALIZED_GF2_PRIMAL_XOR_CONTROLS_V1_PASS` with exact code, binary,
build, receipts, input and verifier pins. Shared components are the policy
deadline/supervisor, standard Python library and locked environment. Mathematical
model necessity and any later native output require their separate audits.
