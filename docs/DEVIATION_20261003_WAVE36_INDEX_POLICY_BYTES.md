# Wave36 Git-index policy-byte mismatch

The first exact [index check](../acceleration/results/20261003_wave36_index01/summary.json)
authenticated1839 paths and vetoed one mismatch: `docs/COMPUTE_POLICY.md`.
The unchanged working policy is SHA256
`9d3f57e8e36376e71fe5fb2733d19d6c0eacf92c71f763e66224dda95f59e136`.
Its raw Git-blob identity is `89562b851f115e3b5b94a5110571b7d51a1896bf`.
The index and priorHEAD instead have normalized blob
`2f1b767988b151f00ac81b69b6427a5fb23349f3`.

No policy text or working evidence bytes were edited. An exact `.gitattributes`
override disables text normalization for this one source, followed by explicit
renormalization of that path. This preserves the raw source pinned by the new
engineering closures in the forthcoming commit. Earlier commits, hashes and the
failed check remain historical evidence; this does not rewrite them or change
any policy deadline, claim or scientific approval. A fresh index check is required
before committing. Other historical sources are not mass-renormalized.
