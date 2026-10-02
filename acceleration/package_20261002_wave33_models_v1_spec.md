# Frozen lossless model publication payload

This engineering invocation packages exactly the four immutable raw files pinned
in the accompanying v1 source. It preserves original bytes and splits each into
8 MiB raw chunks, deterministic gzip level9/mtime0. Every part is decoded and
compared literally before its receipt; full raw identity and length are checked.
Each completed file has a separate resumable record; no original is overwritten.

Allocation: outer600s, worker560s with20s orderly-stop reserve. Approximately
122 MiB of JSON is a finite compression task, independent of mathematical search.
Success: four exact complete records and a manifest usable by the unchanged
`recover_20261001_twentyninth_raw_artifacts.py`. Independent verification must
stream all parts through that separate checker, bind the raw hashes to the
independent model reports, and check failure controls where applicable. A raw
hash identifies an artifact; it does not approve equations or their scope.

No ledger, availability or mathematical status changes occur here. Publication
and immutable Git identity need separate recorded checks. Existing root uv.lock
applies; use the locked offline environment and contained computation supervisor.
