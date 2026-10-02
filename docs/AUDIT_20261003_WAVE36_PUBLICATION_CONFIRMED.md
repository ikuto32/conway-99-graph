# Wave 36 public artifact availability confirmation

As of 2026-10-03T01:39:18+09:00, the published research source is
`43175e0a96ed4abbf6b03e16b67adff6f6f40b20` on
`codex/eight-coordinate-continuation-20260930`, with
[draft PR 3](https://github.com/ikuto32/conway-99-graph/pull/3).
This addendum records availability after the frozen
[wave 36 milestone](RESEARCH_20261003_THIRTYSIXTH_WAVE.md); it does not rewrite
the historical milestone or its pending-publication statements.

The independently checked publication transition changes 937 new artifact
records from LOCAL_ONLY to PUBLIC. All 337 material claim records remain
unchanged: 330 VERIFIED, 3 CANDIDATE, and 4 REFUTED, all with CLEAR review state.
The published six raw replay inputs are recoverable from 32 compressed parts;
the recovery checks covered all 242,396,575 uncompressed bytes. No mathematical
replay or fresh historical verification is inferred from this availability audit.

The producer used pinned Git objects and complete decompression; the independent
checker used a separate Git archive and streaming decompression path. It checked
1,891 immutable blobs, 1,860 distinct publication paths, all six packaged raw
inputs, and 13 strict corrupted controls. The availability audit passed in a
separately contained command, with the computational process group observed
empty on exit. These counts describe the named publication populations only.

Evidence:

- Producer receipt:
  `acceleration/results/20261003_wave36_public_confirmation01/receipt.json`,
  SHA256 `466d7ae65236ac23ca06675374bf5a72611258897b974123a53cfd3094e76aab`.
- Independent complete audit:
  `acceleration/results/20261003_independent_review/wave36_availability01/summary.json`,
  SHA256 `53c83fecb2f9109de5872c0802ad9fa6db2e18d95a748f9998df755bd11bfa92`.
- Independent calibration:
  `acceleration/results/20261003_independent_review/wave36_availability_calibration01/summary.json`,
  SHA256 `293ac4e89060f691cd8c2db7801cd49889dfd36bd55676065d0eb4ca08334eaa`.
- Before ledger SHA256:
  `8f8d39f5e4fcaf8cb8ec2681e0a9ec795439c80e2c8bd1d8a5903ef1087d342d`.
- After availability-only ledger SHA256:
  `5bd21f4126fea49e84e54b6d4bd63e4401b31d62727b72198d2c97c36c9e0ed3`.

The exact commands, source identities, versions, control outcomes and retrieval
instructions remain in the linked receipts and root claim ledger. Publication
confirmation is evidence of artifact availability, not peer review or acceptance.
Target resolution remains UNKNOWN. Overall search coverage: UNKNOWN; no
validated denominator.
