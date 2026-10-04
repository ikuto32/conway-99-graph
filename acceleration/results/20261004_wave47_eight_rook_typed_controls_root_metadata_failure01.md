# Preserved Root administrative receipt failure

The first Root raw-controls receipt command exited 1 before saving an acceptance. The command attempted to hash the output directory itself because PowerShell split unparenthesized concatenations inside an array literal. Its `Get-FileHash` error reported access denied for `acceleration/results/20261004_wave47_eight_rook_typed_controls01` (tool chunk `82ce2b`).

The exact failed command is preserved alongside this note. The correction parenthesized the three concatenated summary/manifest paths in that final array. The corrected command checked the original saved controls again and saved a separate authentic acceptance. No subject worker was rerun, no fixture/evidence/ledger/index changed, and this metadata failure is not a mathematical refutation.
