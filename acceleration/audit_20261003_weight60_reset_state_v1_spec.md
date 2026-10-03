# Independent graph-only V2 reset checker

The frozen checker receives the raw original V2 state, one derivative V2 state,
their exact hashes, the producer receipt, and its own pre-output calibration.
No producer source, native graph implementation, or existing parser is imported.
Shared trusted inputs are the serialized V2 format, native splitmix seed
specification, Python exact integers, and the existing deadline/supervisor.

The required derivative preserves the ordered current triples. Current, best,
initial first-lambda0 current, and initial first-lambda0 best all refer to that
same graph. It sets seed99032061, zero counters/mix, 80,000,000 cooling steps,
temperatures8 and0.1, fixed weight60, and kernelV2. The four RNG words must equal
the separately calculated seed expansion. It is graph-only import with reset
configuration, not continuation of the old RNG trajectory.

Calibration must precede derivative inspection. Two positive controls check a
known-valid rook srg(9,4,1,2), including every scalar entry and a complete serialized
state. Fifteen strict corrupted controls cover graph labels, cache, scores,
configuration, RNG, snapshots, old format, truncation and trailing records.
Finite controls do not establish a general parsing theorem.

Full checking uses literal integer products for every source/reset graph and
full CN cache equality. Any numerical zero must separately satisfy the full
matrix identity. A complete report is bound to the exact checker/calibration
and raw artifact hashes; original input bytes are not edited.

Allocate120 outer seconds and100 worker seconds with5 seconds internal reserve
for each calibration or full check, based on prior103-state dense verification
in11.266 seconds and a four-state control size. Keep full output or failure
receipts. Success is exact narrow derivative validation, not a scientific
solution, arbitrary adapter approval, or performance claim. Run via locked uv
and the supported local Windows Job supervisor.
