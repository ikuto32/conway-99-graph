# Finite strengthened-parity sampling with candidate general phase screens

This protocol is frozen before calibration or research execution. Source creation does not launch any process. The parent researcher owns the eventual research invocation. No ledger or repository publication operation is performed by this driver.

## Question and scope

Do at most sixteen fresh native SAT projections of the checked 520-variable, 4,541-clause necessary balanced-parity formula yield a mixed-group phase difference that the general GF(3) equations force to zero?

The raw support is the single saved six-prism Hadamard support. Balance is an additional construction restriction. Neither balance, the support, nor a target automorphism is assumed without restriction. A SAT projection is not a full factor; a surviving phase screen is not a nonlinear solution. No residual D is encoded. Overall search coverage is UNKNOWN; there is no validated target denominator.

The initial blocked projection is the independently checked second parity witness, whose particular GF(3) exclusion has a separate immutable review. It is not one of the sixteen fresh cases. Subsequent blocking clauses are **sampling bookkeeping**, irrespective of the new screen's result. They are not automatically mathematical nogoods. A terminal augmented UNSAT is UNVERIFIED and cannot establish a balanced-family exclusion without a complete trace replay and independent proof that every blocked branch is unliftable.

## Gates and sharing

The driver requires explicit paths and SHA256 values for three reports:

- `INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_ENCODING_PASS`;
- `INDEPENDENT_GENERAL_BALANCED_GF3_PHASE_NECESSITY_PASS`;
- `INDEPENDENT_HADAMARD_PARITY_PHASE_BATCH_OBJECT_CALIBRATION_PASS`.

The third gate must bind the same first two reports, the exact original CNF/model, the driver and this spec, every imported repository source, `uv.lock`, and `pyproject.toml`. All gate-bound inputs are freshly hashed. The pinned native CLI/ext4 calibrations and binary are also required. No reviewer label substitutes for exact artifact bindings.

The producer repeats the frozen independently authored native/JSON/actual-clause/raw-parity checks during its run. This is not a fresh independent approval. The general phase builder shares the original candidate producer's exact RREF routine. A separate checker must reconstruct the phase equations and inspect the literal row certificate without importing these producers. Every new result remains CANDIDATE pending that review.

## Frozen selection and limits

One serial native attempt per case, using CaDiCaL's default seed and first returned SAT assignment. Case directories are `case_00` through `case_15`. Case index k has exactly k+1 ordered blocks: the initial witness followed by every prior fresh SAT projection. A block is the twenty negative selected group-selector IDs, in group order. No shortened blocks or learned semantic cuts are added.

Each attempt has a 10-second GNU timeout wall limit, 20,000 conflict setting, 4 GiB address-space limit, 10 GiB trace-file limit, five-second TERM-to-KILL interval, and 18-second Windows outer guard. A conflict setting may be exceeded by the solver's observed final counter; the exact raw counter is retained. CPU time is not separately capped. The batch has a **cooperative 180-second research budget**, starting just before fresh ext4 workspace creation, after gated preflight and initial resource observations. A new call is permitted only with at least 25 seconds remaining. Actual overrun is recorded; no hard end-to-end guarantee is claimed.

Before each native call the driver checks at least 11 GiB free on ext4 and 21 GiB free on the host. A failed reserve stops the batch; no artifacts are deleted. UNKNOWN, UNSAT, native outer-guard expiry, malformed output, an exact-check failure, or another error stops the batch without retry. A completed SAT whose linear screen has no obstruction does not stop sampling: its full projection may be blocked solely to obtain a distinct next case.

All traces remain at fresh, preserved ext4 paths. Size and hash collection each use a bounded helper and are skipped or recorded unavailable if the cooperative budget cannot accommodate them. Missing hashes are explicit nulls with reasons. Copying or fully hashing a large retained trace is a separate explicit archival action outside the research budget; no automatic copy is scheduled. Raw CNF, native logs, parsed assignment, projection, and phase artifacts are saved locally for every completed SAT. A terminal UNSAT trace is only a raw unverified artifact.

## Exact general phase system

Each group has six affine maps `pi_i(x)=s_i*x+t_i` over GF(3), with signs s=1 for parity0 and s=2 for parity1. The group support ordering is derived directly from the raw L, in first column-occurrence order. There are120 variables indexed6g+i. Gauge t_(g,0)=0 fixes the common column shift after the normalized first sign is positive.

`phase_system.json` uses schema `GENERAL_BALANCED_GF3_PHASE_SYSTEM_V1`. It saves raw groups/patterns/signs, all variables, complete equation rows and metadata, all60 relative-map pair records, and necessary local nonzero functionals. Every row has `index`, `kind`, 120 coefficients in{0,1,2}, `rhs:0`, and `parity_dependency_groups`.

Exact row order:

1. Twenty gauge rows, group ascending, dependency list empty.
2. Groups ascending: a constant group has one full six-phase sum row; a mixed group has positive-sign sum then negative-sign sum. Each depends on that one group.
3. Sixty nonmatched coordinate pairs in lexicographic order. Each has odd-relative sum then even-relative sum, **including a zero odd row when the disagreement count is zero**. Relative phase for coordinates a<b in a group is `t_b-s_b*s_a*t_a`. Each pair row's dependency list is all five incident groups, even when its own coefficient contribution from a group vanishes.

With m mixed groups there are160+m rows. Necessary nonzero functionals are ONLY the six mixed-group same-sign differences per group: group ascending, sign1 then2, position-pair combinations ascending. There are6m. This first batch does not add pair-derived inequalities or impose distinctness in constant groups.

`phase_screen.json` uses schema `GENERAL_BALANCED_GF3_PHASE_SCREEN_V1`. It saves `rank`, `nullity`, complete `linear_certificate` (RREF, row transform, elementary operations, pivots, free columns, nullspace basis), `functionals_attempted`, and `obstruction:null` or the first vanishing functional. An obstruction contains the exact full condition and a `row_combination` with one GF(3) coefficient per original ordered equation row. The producer multiplies this combination literally before saving it. Status is `CANDIDATE_PHASE_OBSTRUCTION` or `UNKNOWN_LINEAR_SCREEN`; neither is independent approval. No shortened nogood is emitted.

## Per-case records and restart semantics

`blocked_projections.json` is an ordered JSON list. Each record contains `projection_path`, `projection_sha256`, `selected_group_selector_ids`, purpose `DISTINCT_CANDIDATE_SAMPLING`, and an explicit independent-exclusion field. Only the initial witness is already approved. New producer screens do not change that field.

Each attempted case saves `instance.cnf`, `launch.json`, `solver.stdout.log`, `solver.stderr.log`, and `solver.receipt.json`. On SAT it additionally saves `parsed_model.json` with all520 signed IDs exactly once, `decoded_projection.json` in the checked strengthened-parity schema, `phase_system.json`, and `phase_screen.json`. Every actual CNF clause, including all sampling blocks, is checked, followed by the independent raw-pattern path for the original4541 clauses and all60 support cuts.

An append-only `checkpoint_XX.json` follows each completed attempt. It includes the ordered blocks, saved outcomes and elapsed budget, distinguishing fresh SAT candidates from attempted native calls and candidate obstructions. A final summary records all errors/stops, actual timing, and output hashes. There is no automatic resume or rerun. Any later continuation requires a new protocol/output directory that names the exact prior checkpoint and its chosen new resource allocation.

## Locked invocation (not executed during source preparation)

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_hadamard_parity_phase_batch.py --preflight --out NEW_PREFLIGHT_DIRECTORY --encoding-gate ENCODING_REPORT --encoding-gate-sha256 EXACT_SHA --general-necessity-gate GENERAL_REPORT --general-necessity-gate-sha256 EXACT_SHA --object-gate BATCH_CALIBRATION_REPORT --object-gate-sha256 EXACT_SHA
```

Only after separate review does the parent substitute `--research` and a fresh output directory. Source/spec preparation and static syntax inspection are not calibration, research execution, or mathematical verification.
