# Wave41 raw-byte index V1 source-only review

As of 2026-10-03 03:04:50 UTC. Reviewer: `/root/checkpoint_audit`.
Subject producer: ROOT. No subject command, calibration, Git staging, shadow
index operation or mathematical replay was run in this review.

The complete source and specification were read, including every control,
calibration, shadow and application branch. Exact subjects:

- `acceleration/stage_20261003_wave41_index_v1.py`, SHA256
  `633d8f6cbd0d80a0120d4284408d9642794bbbffe331ad58fbf09bbc3ff733bd`.
- Its specification, SHA256
  `3dc02f7d9c12db79982ff662c6666282b657042f123441ca966cfe2d2be5cde6`.
- Shared preserved `stage_20261003_wave40_index_v2.py`, exact source pin
  `11150733d86ee7154eab2c0cc98b239019fb625d0ff44ff16071218d270661f3`.
  Its relevant boundary, streaming raw/SHA256/Git-blob and index-parser
  implementations were also read. V1 calls none of its old mains or scope
  controls and changes no old globals.

## Static veto before calibration: historical suffix identity

The document loop reads the generator's `.before` and `.prepared` files and
checks `current == prepared` and `prepared.endswith(old)`. Neither that loop
nor an earlier branch authenticates the four `old` byte strings against an
independent pre-write identity. The source's immutable manifest pin authenticates
the generator's recorded output, but that output and both comparison files
were produced by the same generator. The reviewer authored that generator and
therefore cannot treat their agreement as independent preservation checking.

For example, a producer could supply a shortened `.before`, supply a matching
`.prepared` ending in that shortened text, write that same prepared text to the
current document, and record these as self metadata. This loop would pass while
historical prose had been removed. The negative is hypothetical and has not
been executed against the subject or actual files.

The four exact pre-write document identities need a separate immutable anchor.
If their raw bytes match the recorded HEAD `00ffb6fdd7d91bd38269e1cc5e6b214ebf7591c8`,
authenticate the corresponding Git blobs; otherwise use previously recorded
independently authenticated raw working-byte hashes and disclose any EOL
transformation. Do not silently equate Git blob and working bytes. A new source
version and a precise negative control should reject a changed historical
baseline even when `.prepared` and the current file were changed consistently.
Preserve V1 and its specification. This is an engineering completeness gap,
not evidence against either mathematical claim or against the actual generated
historical bytes.

## Other inspected behavior and scope

The synthetic inventory on paper is one positive plus 22 negatives: 21
manifest mutations and one duplicate JSON key. Negative `ValueError` handling
compares the complete exact diagnostic; unrelated exception types and wrong
stages cannot count as a passing control. Float count and Boolean replay
aliases have explicit rejection paths. These are source observations only;
no actual controls were evaluated by this review.

The actual path recomputes raw SHA256, size and unfiltered Git blob IDs, checks
the exact NUL set, requires the eight old raw identities and the archived
external Git/workspace bytes, and compares every unrelated index entry and
existing Gitlink. Shadow uses a copied index and application requires an exact
successful shadow plus the unchanged original live index. A Git filter/EOL
transformation becomes a raw-index veto. Deadline checks precede hashes/Git
calls and the supported outer supervisor remains required. A calibration or
source read establishes no mathematical verification or public availability.

The scope is the separately supplied frozen actual manifest, not a general
approval of arbitrary manifests. Extra completed staging/control/admission
receipts require the separate explicit appendix described in the specification.
Historical package identity checks do not constitute fresh decompression,
independent model replay or an observation of a remote clean checkout.

The frozen writer has a cosmetic unescaped `|C|` in a table scope. ROOT chose
to preserve that original output/manifest and record a later editorial escape
after its first immutable publication. This review changes none of those bytes.

Review result: `STATIC_HISTORICAL_SUFFIX_ANCHOR_VETO_V1`. No execution approval,
calibration gate, publication approval or mathematical refutation is produced.
