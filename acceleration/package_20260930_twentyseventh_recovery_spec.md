# Wave27 exact oversized-raw recovery

Freeze source before packaging. Use candidate inventory381d1130...: exactly14
oversized raw artifacts,13 models with existing deterministic gzip packages and
the complete792 domain-inventory records11,735,054 bytes. Preserve all existing
raw/package/model bytes. Create one deterministic gzip stream for that inventory
only, and normalize all14 identities into WAVE27_NORMALIZED_RAW_RECOVERY_V1.
Parts retain repository-relative path, gzip hash/length, contiguous raw offset,
raw hash/length. Each public gzip is at most10MiB.

Authenticate every old model package against the inventory's raw identities;
stream every gzip and compare literal bytes, chunk/whole hashes and lengths with
the retained original. No claim/proof replay or mathematical approval occurs.
The thirteen complete native proofs are small enough to remain public raw and
are not included in this oversized recovery list. The separate fresh restorer
uses exact prescribed paths, no-overwrite except matching existing identity,
stream validation and corruption controls before publication.
