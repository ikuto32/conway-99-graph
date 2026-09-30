# Nineteenth wave: exact phase obstructions and finite sampling

Use the existing repository and the locked environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --offline --cache-dir .uv-cache-20260917
```

Python 3.12.10 and uv 0.11.25 were used. The saved manifests bind the exact
`uv.lock`, producer/checker sources, input/output hashes, source commit and
commands. Every replay must use a fresh output directory. Do not rerun the
one-shot ledger registrars or overwrite historical artifacts.

The principal independent checking paths, relative to `acceleration/`, are:

| Exact statement | Independent checker and saved report directory |
| --- | --- |
| Second parity branch's uniform rational lift primal | `audit_20260930_hadamard_support_cut_lift_primal.py`; `results/20260930_independent_review/hadamard_support_cut_lift_primal/` |
| Second parity branch's GF(3) obstruction | `audit_20260930_hadamard_f3_phase_obstruction.py`; `results/20260930_independent_review/hadamard_f3_phase_obstruction/` |
| General balanced phase necessity | `audit_20260930_hadamard_general_f3_necessity.py`; `results/20260930_independent_review/hadamard_general_f3_phase_necessity/` |
| Fourteen fixed-pattern exclusion | `audit_20260930_hadamard_phase_premise_subset.py`; `results/20260930_independent_review/hadamard_phase_premise_subset/` |
| Twelve reduction orders, eleven overlapping exclusions | `audit_20260930_hadamard_phase_premise_orders.py`; `results/20260930_independent_review/hadamard_phase_premise_orders/` |
| Matrix formulation and signed-Gram implication | `audit_20260930_balanced_phase_matrix_form_v2.py`; `results/20260930_independent_review/balanced_phase_matrix_form_v2/` |
| Three sampled parity projections and phase screens | `audit_20260930_hadamard_parity_phase_batch.py`; `results/20260930_independent_review/hadamard_parity_phase_batch_cases/` |
| Four native receipts, exact counts and missing trace availability | `audit_20260930_hadamard_parity_phase_batch_outcome.py`; `results/20260930_independent_review/hadamard_parity_phase_batch_outcome/` |
| Complete case01 phase enumeration | `audit_20260930_hadamard_phase_case01_enumeration.py`; `results/20260930_independent_review/hadamard_phase_case01_enumeration/` |

Read each report's saved command, replace only its output destination with a
fresh directory, and run its Python command through
`uv run --locked --offline --cache-dir .uv-cache-20260917 python -B`.
Producer reruns alone are not independent checking. The checked GF(3) arithmetic,
literal certificates and exhaustive 2,187-vector enumeration need no SAT solver.
Preserve the original failed sources and reports: the matrix checker initially
used the wrong gauge metadata key; enumeration setup had an input-hash typo and
then a raw-key mismatch before any vectors were evaluated.

The finite native sampler is
`theory_20260930_hadamard_parity_phase_batch.py`, governed by its adjacent `_spec.md`.
Its saved manifest records all three exact gate arguments. The original run
attempted four cases and stopped at UNKNOWN under its frozen stop rule. Cases
00, 01 and 02 have complete saved assignments, CNFs and phase artifacts.
No solver rerun is needed to validate these three SAT objects or phase exclusions.
An augmented formula's sampling blocks are not automatically mathematical cuts.

All four batch learned traces are currently MISSING. The successful historical
stat/hash receipts and later failed archive/independent availability observations
are retained. Their cause of disappearance is UNKNOWN. Neither an UNSAT proof
nor a mathematical exclusion depends on those traces; no native UNSAT occurred.
The raw files cannot currently be replayed from their recorded hashes alone.

The second parity lift's prepared 240-selector CNF was never searched: the exact
phase obstruction made that fixed-branch search unnecessary. Its source, full
CNF/model and cancellation decision remain available. This is not an UNSAT run.

All exclusions in this wave are conditional on explicitly specified balanced
patterns on one fixed six-prism support. The eleven reduced pattern families
overlap; no union size, all-support exclusion or target-wide percentage is claimed.
No full factor or 99-vertex graph was produced. The oriented-triple pilot and
later full balanced Gram formulation belong to the following research cohort.

The [milestone](RESEARCH_20260930_NINETEENTH_WAVE.md) and its frozen ledger snapshot
identify the authoritative claim revisions. The publication catalog records
exact payload bytes and retrieval scope. Schema/CI success is not mathematical
verification; expensive native reruns and external review are not implied.
