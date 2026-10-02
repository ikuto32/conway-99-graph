# Saved-object checker v1 source archival

The first scientific saved-object checker failed parsing before execution:
line186 repeats the keyword `controls`. Exact raw source SHA256 is
`fe41bd9996f93d0a7656ba91b25d2ec8c108f78f5a18df5a219d54318f3347ac`.
Its bytes are preserved at
[the archived source](../acceleration/audit_20261002_hypergraph_saved_objects_v1.py.failed-source.txt).
The original attempted command/source name was
`acceleration/audit_20261002_hypergraph_saved_objects_v1.py`; original receipts
remain unchanged. The later
[syntax receipt](../acceleration/results/20261002_wave33_syntax_supervision01/stderr.log)
independently observed the same parse error.

This rename separates an unrunnable failed artifact from maintained Python
tools without changing its bytes or extending the CI exception list. To replay
the historical parse failure, copy those exact bytes back to the original
filename in an isolated checkout and invoke the recorded command. Verify the
hash first. Do not claim that an unsuccessful parse ran scientific checks.

The v2 source/failed calibration also remains preserved. Its broad negative
control handling was vetoed; the independently reviewed v3 strict stage
controls and actual independent pilot verification supply the applicable gate.
No v1/v2 success or target result is inferred. The wave33 stager v2 manifest
records the original filename before archival; the final v3 staging manifest
records the byte-identical archived path. Neither changes historical manifests.
