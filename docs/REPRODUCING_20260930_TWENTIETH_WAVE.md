# Twentieth wave: complete balanced-family proof

This wave excludes every balanced binary 36×60 factor on the literal six-prism Hadamard support. Balance means that, for each of the six coordinates in a repeated-support group, its three columns use all three fibres once. It is an extra restriction. Unbalanced factors, other supports, residual completion and the unrestricted Conway-99 problem remain unresolved.

Use the root locked environment and fresh output directories:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_balanced_proof_packages.py --out build/twentieth-transport-replay --recovery-dir build/twentieth-proof-recovery
```

The recovery checker validates all six ordered parts, the complete compressed stream, raw length and SHA256. The mathematical trace is 227,098,316 bytes, SHA256 `94d2ab35c76b61f3deb01ebfd9ca0dc70452bddf847383d5838b2b2ca902396b`. The compressed stream is 52,339,920 bytes. If the original raw file exists, the checker also compares every recovered byte with it. Ten corrupted transport controls are rejected. Recovery is an identity check, not a proof check.

The exact CNF is `acceleration/results/20260930_hadamard_balanced_gram_cnf/instance.cnf`, SHA256 `c2d780f94dac4dda955743df03f8db2e8ec0f51217c671eb19fc5e42ed69ba37`. Its 10,480 variables and 74,200 clauses cover all 150 normalized local choices in each of 20 groups, including both constant and mixed choices. Independent checking reconstructs the local universe and every clause. The normalization only relabels three identical-support columns; no target automorphism is assumed. No outside-column cap premise is used.

The saved independent paths are:

| Check | Source and saved report directory under acceleration/ |
| --- | --- |
| Complete balanced encoding and object controls | audit_20260930_hadamard_balanced_gram_v2.py; results/20260930_independent_review/hadamard_balanced_gram_cnf_v2/ |
| Complete exact proof and proof controls | audit_20260930_hadamard_balanced_gram_unsat_v2.py; results/20260930_independent_review/hadamard_balanced_gram_unsat_v2/ |
| Lossless proof transport | audit_20260930_balanced_proof_packages.py; results/20260930_independent_review/hadamard_balanced_proof_packages/ |
| Oriented projection and UNKNOWN receipt | audit_20260930_hadamard_oriented_triples.py and audit_20260930_hadamard_oriented_unknown.py; corresponding independent_review directories |
| At-most-two row-margin implication and refuted intersection guess | audit_20260930_hadamard_two_group_margin_cancellation.py; results/20260930_independent_review/hadamard_two_group_margin_cancellation/ |

Read each saved command and substitute a fresh output directory. Python 3.12.10, uv 0.11.25 and the pinned uv.lock were used. Original source commits, exact commands, hashes, tool versions and resource limits remain in manifests. Do not rerun one-shot registrars or overwrite completed artifacts.

The balanced native call used CaDiCaL 1.9.5, returned UNSAT (exit20), and completed after 248,698 conflicts and 22.19 native wall seconds. The independently authenticated DRAT checker accepted the entire trace in 28.155 seconds; a valid tiny proof and four corrupted proof/input controls were checked. Six corrupted native receipts were rejected. Solver correctness is not trusted for the proof.

The historical wrapper authenticates the exact saved checker binary, compiler records and native tools and therefore cannot be promised to run unchanged on a fresh machine. Its checker is pinned to upstream drat-trim commit 2e3b2dc0ecf938addbd779d42877b6ed69d9a985, with a disclosed Windows timing shim. Public source, patch and build records are in [checker_build](../acceleration/results/20260930_rook_sat_independent_proof/checker_build/). The saved executable remains LOCAL_ONLY. The [seventeenth replay guide](REPRODUCING_20260930_SEVENTEENTH_WAVE.md) describes restoration of historical checker source paths.

A separately rebuilt checker can validate the public mathematical input directly:

```text
<rebuilt-drat-trim> acceleration/results/20260930_hadamard_balanced_gram_cnf/instance.cnf build/twentieth-proof-recovery/proof.drat
```

Record its own source, build command, toolchain, executable hash, calibration controls and complete result. Different compiler output is not a reason to rewrite historical provenance. Complete proof replay and the separately checked encoding are both required for the family exclusion.

The earlier oriented-triple native call is UNKNOWN at 1,000,000 conflicts. Its 331,620,166-byte incomplete trace remains LOCAL_ONLY and is not a certificate. The broad process stdout from that independent receipt review is private and omitted; the public narrow observation and hash-only availability sidecar preserve the limitation. No mathematical result depends on that private snapshot.

A cap-augmented formula was built but never independently approved or searched. The completed build and cancellation record are retained as candidate preparation; the base balanced Gram proof made its search unnecessary. Its large raw CNFs remain LOCAL_ONLY. The first balanced CNF checker and proof-checker wrapper each failed for a checker defect; original sources, failures and correction records are preserved. A tentative claim that distinct supports intersect only in zero or three coordinates is REFUTED by an exact size-two intersection.

The frozen milestone contains 194 claims: 191 VERIFIED/CLEAR, two CANDIDATE/CLEAR and one REFUTED/CLEAR. Five verified claims and one refuted claim were added. These counts do not measure target coverage. Overall search coverage: UNKNOWN; no validated denominator. Few-exception and four-group circuit work belongs to the next wave. No target-resolution artifact is under external review.

