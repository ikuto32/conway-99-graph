# Replay the original mod-3 primal certificate

This checks the complete mathematical certificate using the public model package,
scalar helper and three ternary vectors. It needs no native binary, producer run
or494930751-byte native resume checkpoint. Availability is tracked separately in
CLAIMS.yaml; this recipe becomes public when its exact files are authenticated
at the published commit.

First recover the raw rooted8 model with the unchanged
[wave33 recovery helper](../acceleration/recover_20261002_wave33_public_models_v1.py)
and locked setup in REPRODUCING.md. Model path:
`acceleration/results/20261002_rooted8_universal5_product_model02/model.json`,
SHA256 `a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b`.
Authenticate helper SHA256
`698eb9bbe8b1ba6a257e8e6226a9e49517e17e966ce64afb11b98d17be08bafa`
and vector identities in the [immutable independent binding](../acceleration/results/20261002_independent_review/gf3_full_artifact01/claim_binding_v2.json).

The essential complete scalar check is:

```python
import json
from pathlib import Path
import audit_20261002_gf3_scalar_v1 as independent

model = json.loads(Path("acceleration/results/20261002_rooted8_universal5_product_model02/model.json").read_bytes())
vectors = independent.read_vectors(Path("acceleration/results/20261002_rooted8_gf3_solve01/solve"), 23019)
independent.scalar_vectors(model, vectors, "original")
```

Put `acceleration` on Python's import path. Use locked uv and the existing
per-command supervisor. The [tested minimal replay manifest](../acceleration/results/20261002_wave35_minimal_primal_replay_supervision01/manifest.json)
preserves its exact code/command and60-second allocation. Its
[receipt](../acceleration/results/20261002_wave35_minimal_primal_replay01.json)
checks all257622 scalar components across85874 original signed integer rows,
authenticates every input and rejects an actual ternary-coordinate corruption
at `GF3_ORIGINAL_PRIMAL_SCALAR_ROW`. It accesses no resume checkpoint. This
repeats the calibrated independent path; it is not another mathematical promotion.

Linear combination of the three verified vectors solves that fixed operator
for every integer parameter pair reduced modulo3. All210 frozen conditional
profiles therefore survive. No rank, integer/nonnegative feasibility, graph
realization, exclusion or target resolution follows. Global prism absence
remains UNKNOWN for the conditional graph interpretation. The full prior
artifact audit additionally checked literal stream/receipt/checkpoint identities;
those provenance checks are separately disclosed and not asserted here.
