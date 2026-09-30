# V2 inventory field-name correction

The preserved v1 failed before producing outputs because it expected the prior
inventory conflict-field name. V2 checks recorded_hash_conflicts, the exact
field in the frozen wave28 inventory. All recovery semantics remain unchanged.

# Wave28 raw recovery packaging

Consume only the explicitly supplied, SHA256-authenticated wave28 inventory.
Every oversized entry must have its original bytes and hash available. Reuse
an existing exact gzip package only after authenticating its manifest; otherwise
write fresh deterministic gzip parts containing at most8MiB of raw bytes each.
Every public part must be at most10MiB. Never overwrite or remove originals.

Compare every decompressed byte with the original, in addition to checking part
offsets, compressed and raw lengths and hashes. Preserve the exact original
identity in the normalized recovery manifest. Reject absent/mismatched bytes,
unsafe paths and known private paths before reading. Record source commit,
commands, source/spec and input hashes. No solver, mathematical or claim-status
verification is performed. Independent fresh-destination recovery and corrupted
manifest controls remain required before public recovery is advertised.
