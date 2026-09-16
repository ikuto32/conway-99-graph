# Two-trade overlap proposals

`overlap_two_neighbors.rs` is a dependency-free Rust candidate generator. It
copies the geometry of frozen `overlap_neighbors.rs` into a separate source;
the original source and executable are unchanged.

```powershell
rustc -O -C target-cpu=native acceleration/overlap_two_neighbors.rs -o acceleration/build/overlap_two_neighbors.exe
acceleration/build/overlap_two_neighbors.exe INPUT.txt OUTPUT.json 128 20260922
```

Input is `C99OVERLAPS1 1`, followed by 168 canonical zero-based overlap edges.
The optional sample limit defaults to 128 and must be in 1..4096. The seed is
an unsigned 64-bit integer, default zero. Existing output files are rejected.

Output contains `overlap_candidates` and aligned `trade_paths`. Each path has
exactly two objects, using the existing `{removed: [[u,v],[w,x]], added: ...}`
trade format. Both the intermediate and final states preserve the complete
partial graph's degree constraints, all 4,851 common-neighbor caps, and exact
own-label quotas. Overlap block totals may change. No star-domain or pair-AC
filter is applied to either state by this generator; a caller may apply these
filters only to the final candidate.

Final states are unique and differ from the input in at least three removed
edges, so none is a backtrack or a state reachable by one two-edge swap.
The first legal trades are enumerated, deterministically shuffled, and at most
`min(first_legal_trades, max(sample_limit, 16))` intermediate branches are
visited. Each branch's legal second trades are shuffled and a bounded quota
of distinct final states is selected. Modulo-based shuffling and this branch
allocation are **not uniform sampling**. The result may contain fewer than
the requested number. Counters describe the visited branches; they do not
claim exhaustive coverage of two-step paths.

## Saved validation

`results/20260916_two_trade_qa/qa.json` binds source, binary, input, outputs and
independent checker hashes. From the coupled-alt best candidate:

- 128 proposals generated in 0.0869 seconds, excluding input parsing.
- `audit_two_trade_proposals.py` replayed all 257 initial/intermediate/final
  partial graphs using Python set neighborhoods: 1,246,707 pair-cap checks and
  86,352 exact own-label quota checks passed.
- The same seed reproduced every semantic output field exactly. A second
  seed produced a distinct sample that also passed independent replay.
- Nine malformed-input/CLI/output-preservation controls and five corrupted
  path/output controls were rejected. Legally commuting swaps remained valid
  when their order was reversed.

The independently replayed `known_detour.json` binds the saved global-pilot
path from numerical merit 22.22012 through 19.97120 to 17.51056. The intermediate
has a saved native pair-AC-empty result, while the final has a saved native
pair-AC-nonempty result. The two trades remove three net original edges, so a
one-trade transition cannot jump directly to that final state. Those saved AC
results are referenced, not independently re-audited by this test. This exact
detour is not claimed to occur in the random sample.

These are candidate-generation controls. Neither a successful replay nor
pair-AC survival constructs a Conway graph or proves exhaustive coverage.

To independently replay a new saved sample:

```powershell
python -B acceleration/audit_two_trade_proposals.py --candidate INITIAL.json --input INPUT.txt --proposals OUTPUT.json --out AUDIT.json
```
