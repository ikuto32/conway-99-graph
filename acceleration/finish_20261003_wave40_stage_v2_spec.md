# Exact Wave40 receipt appendix and raw-index finisher V2

Source SHA256: `e87ef83fe8196027213cb891bc7226962a489c5c0c03dd58b44dc51a9c624d55`.
Ancestor: `finish_20261003_wave39_stage_v1.py`, actual SHA256
`ced978e9327e5bcbfda0936cee6736cc77c534a828f64993a7670516287e9973`.
V1 is preserved unexecuted; its incorrectly transcribed ancestor literal was
caught before any dispatch. V2 also preserves V1 and its explanation.

This is engineering bookkeeping, not mathematical verification. It requires
the exact Wave40 apply report `c3aae6f5862ee1ce4fa3bac54905a0ff66c6f1dccc387a1362a7820f75caca45`,
the unchanged post-apply index, and ledger `f66b82fb0bac49b7e0732eef177cb283f5338b1e433f980dce7e55ee64acf2ae`.
It checks the registry's actual validation result and the actual 56-test log;
all four selected supervisor receipt sets must show exit zero, reaping and an
empty contained Job. Only its explicit appendix is staged.

All selected paths, including the 1439 prior approved paths, are compared with
their raw Git blob SHA1. The four current document files must equal their
prepared bytes and retain the complete prior byte suffix. Unselected index
entries and Gitlinks must remain unchanged; the ledger is not edited.

Before staging, a streaming marker scan of selected uncompressed bytes uses
one benign and four synthetic veto controls. It prints no matched values.
Compressed bytes are skipped. This bounded marker check is not a guarantee
that every possible credential format has been detected.

Launch through the supported Windows Job supervisor, before locked/offline uv:
120 seconds outer, 100 worker, 20 shutdown and at least 20 worker save reserve.
Success requires a literal PASS report, exact indexed bytes, no outside index
change, and an empty terminal Job. The operation does not commit, push, change
availability, run scientific workers, or approve a mathematical claim.
