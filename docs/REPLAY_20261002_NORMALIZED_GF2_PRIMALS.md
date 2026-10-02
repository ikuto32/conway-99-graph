# Replay the public literal parity certificate

This checks the three-vector mathematical certificate without a producer run,
native binary or 343MB native resume checkpoint. It repeats the calibrated
independent scalar checking path; it is not a fresh encoding/rank review.

First recover the exact raw rooted8 model from the wave33 public packages using
the existing [recovery helper](../acceleration/recover_20261002_wave33_public_models_v1.py)
and its locked setup documented in REPRODUCING.md. The literal model must be
`acceleration/results/20261002_rooted8_universal5_product_model02/model.json`,
SHA-256 `a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b`.
The three vector files are in
`acceleration/results/20261002_rooted8_normalized_gf2_solve01/solve/`.
Their exact identities and scope are in the [immutable binding](../acceleration/results/20261002_independent_review/normalized_gf2_full_artifact01/claim_binding.json).

Use locked uv and the existing per-command supervisor for checking. The essential
scalar call is:

```python
import json
from pathlib import Path
import audit_20261002_normalized_gf2_controls_v1 as independent

model = json.loads(Path("acceleration/results/20261002_rooted8_universal5_product_model02/model.json").read_bytes())
vectors = independent.read_vectors(Path("acceleration/results/20261002_rooted8_normalized_gf2_solve01/solve"), 23019)
independent.check_vectors(model, vectors)
```

Put `acceleration` on Python's import path and authenticate the pinned model,
helper and vectors before checking. The helper source SHA-256 is
`675e393b8ba1cb20b78565b40cb6a478c96dc01e4a6b50de51f5272fb19bc3f0`.
Its independently calibrated scalar function divides each original integer row
by its positive literal content and checks all three RHS components over F2.
All 85,874 rows are required; a sampled check is insufficient. A changed vector
coordinate must fail at `PRIMAL_SCALAR_ROW`. The three complete vectors yield
all four affine parameter parities and hence all 210 currently frozen profiles.

The original full artifact audit additionally hashed producer receipts,
normalized/parity streams and the resume checkpoint. Those provenance checks
remain disclosed and are not asserted by this minimal mathematical replay.
No rank, nonnegative integer lift, graph realization, exclusion or unrestricted
target resolution follows from passing this certificate check. Global prism
absence remains UNKNOWN for its conditional graph interpretation.
