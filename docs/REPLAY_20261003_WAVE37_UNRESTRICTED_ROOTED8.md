# Exact public recovery for the unrestricted rooted8 model

The complete independent catalogue and necessary-operator checks are separate
from byte packaging. Their reports are respectively
`acceleration/results/20261003_independent_review/rooted8_unrestricted_catalogue01/summary.json`
(SHA256 `1cf70d9caed5235bcce437fbc57280a0778c1f9a6cd9d628766de586516f9a6a`)
and `acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/summary.json`
(SHA256 `ec5073a22027c512e29dac1d49048a507f272cb8ce1a0a79d2ca1f663f1be974`).
The independent written necessity derivation is
`acceleration/audit_20261003_rooted8_unrestricted_model_proof_v1.md`
(SHA256 `f14c53a486bf6db35664e381937911d770939cc436e86618af0ab61beefb9dc7`).
These establish necessary local count equations, not graph realization,
profile exclusion, or nonexistence.

The new lossless manifest is
`acceleration/results/20261003_wave37_rooted8_package01/manifest.json`
(SHA256 `ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14`).
It represents two raw files in16gzip parts, total124,864,726raw bytes and
4,416,662compressed bytes:

| Raw artifact | Bytes | SHA256 |
| --- | ---: | --- |
| `acceleration/results/20261003_rooted8_unrestricted_extension01/model.json` | 59,358,049 | `b143c129fce1f450b54a397d6d508ecb81a67870c2bafd2e9f50dee0bda83f1a` |
| `acceleration/results/20261003_independent_review/rooted8_unrestricted_model01/reconstructed_rows.json` | 65,506,677 | `033778d196dcf7d21f76b2460018944b291c1b34b38602ce9f66c24e198dbd70` |

The raw files exceed the declared50MiB direct staging threshold. Preserve their
bytes locally and publish the lossless package with the replay code. They are
not truncated, simplified, or edited to fit that threshold.

With the committed locked uv environment, recover all eight current package
inputs through the supported local supervisor:

```text
uv run --locked python acceleration/run_compute_command.py --seconds 300 --allocation-reason "Eight exact raw public inputs, shared deadline" --success-criterion "Complete raw hashes and sizes, no overwrite" --verification-criterion "Byte recovery only; mathematical audits separate" --out build/wave37-recovery-supervision --cwd . -- python acceleration/recover_20261003_wave37_public_inputs_v1.py --seconds 270 --out build/wave37-recovery
```

On Windows set `UV_PROJECT_ENVIRONMENT=build/research-venv` and supply the absolute
locked-environment Python executable after `--`, as in the actual saved Windows
receipt. On Linux keep supervisor and computational children inside Linux; a
Windows WSL transport timeout is not containment. Fresh output directories are
required. Existing raw files are checked against complete identities and never
replaced.

The new eight-input wrapper preserves the earlier six-input wrapper and exact
restorer. Its fresh-destination check recovered all8 files:367,261,301raw bytes,
48parts and11,723,542compressed bytes. All8 actions were RESTORED_MISSING and four
corrupted population controls rejected. The saved run report is
`acceleration/results/20261003_wave37_recovery_clean01/summary.json`
(SHA256 `5091fc02647848d5330943a440387007f66cf905748a2c908af84c415eab5499`).
This wrapper test is byte recovery only. Independent package recovery and
immutable publication confirmation are separate records; artifact availability
must be read from the root ledger rather than inferred from this document.

Expensive mathematical or solver checks are not run by the CI recovery step.
No source changes, rank assertions, target graph, or exhaustive coverage follow
from a successful decompression or green schema check.
