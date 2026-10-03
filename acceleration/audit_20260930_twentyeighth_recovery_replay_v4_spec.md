# V4 literal concatenation syntax correction

Preserve v3 failure. Static literal argument loops now support nested string concatenations such as prefix+name+suffix; expressions with calls or unknown names remain unhandled/rejected. No evaluated checker code. Prior controls and exact input evidence unchanged.

# V3 nonliteral-loop exclusion

Preserve v2 and its failure. Before inspecting a loop, require every element to be a literal string; ignore scientific loops containing names. This is the declared static-only behavior, not an evidence or command change.

# V2 literal argparse-loop AST correction

Preserve v1 source/spec/failure. Expand only static literal-string-list loops that call add_argument with a constant prefix plus the loop variable. No producer or checker execution. All input pins, byte checks and scopes unchanged; unknown-flag control retained.

# Independent wave28 recovery and replay-command preflight

Freeze before run. Authenticate the47-entry normalized recovery manifest
33b00a791e57a732a27d18061c52f1ac6b3e71d964d9bf03c1e986ae12c82c89,
524,689,195 raw bytes, helper/source identities, root fresh-restoration receipt,
and seven root corrupted controls. Independently decode each single gzip member
with zlib and compare literal full bytes with both retained originals and the
fresh restored tree. Check every offset, part length/hash and whole digest.
Reject truncated/concatenated members, wrong raw hashes/offsets, missing parts.

Authenticate the eight saved original audit commands and planned replay vectors;
derive permitted changes directly from saved command arrays. Inspect argparse
syntax without importing or executing any checker. Verify flag spellings, literal
required arguments and mode choices, plus every path/hash argument pair. Inspect
the frozen guide recovery command and precise scope/disclosure. This is NOT a
fresh mathematical replay: all eight publication reruns were explicitly skipped.

No producer/restorer imports; only stdlib. No file restoration by this checker,
native or scientific calls, Git/ledger/index changes or protected paths read.
120seconds, ordinary memory. Save exact input pins and controls; preserve failures.
Output is a preliminary metadata gate, not catalog/staging approval.
CLI: python -B acceleration/audit_20260930_twentyeighth_recovery_replay_v4.py --out NEW
