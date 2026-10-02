# Wave35 evidence staging v1

Authenticate only new artifact records relative to the329-entry wave35 baseline,
fixed334-current-ledger hash, declared completed run roots and explicit extras.
Use the unchanged published wave33 packages for raw-model byte recovery. Skip
the494930751-byte mod3 checkpoint after exact SHA256/size checking; it remains
LOCAL_ONLY and is not the mathematical primal certificate. Every other direct
member must be below50MiB, have bounded repository paths and match its recorded
hash. Never stage unrelated worktree files or active scientific outputs.

Run in the pinned root uv.lock environment via run_compute_command.py, with
240seconds outer/200worker and10seconds shutdown reserve. Prior comparable
wave34 staging completed6.453seconds; larger local-only checkpoint hash is
included in this allowance. Success is the exact frozen staging manifest and
index bytes, with no claim promotion or availability change. Independent
publication audit remains separate and must authenticate the actual pushed
commit before new artifact metadata is marked PUBLIC. Source becomes frozen
at first invocation; additional completed files use --extra with a fresh output
root rather than altering executed source.
