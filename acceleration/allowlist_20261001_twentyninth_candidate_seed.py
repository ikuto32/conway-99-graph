"""Unexecuted wave29 allowlist seed, not a final inventory/publication catalog.

No filesystem access, imports, scanning, hashing, native or ledger action.
Root must freeze actual checkpoint/registration and final supplements first.
Batch03 and all later allocations are deliberately absent.
"""
B='acceleration/results/20260930_'
N='acceleration/results/20261001_'
I=B+'independent_review/'
J=N+'independent_review/'
DIRECTORIES=[
 B+'exact_eight_next64_selection',B+'exact_eight_next64_launch_preparation',
 B+'exact_eight_next64_cnfs_part00',B+'exact_eight_next64_cnfs_part01',
 B+'exact_eight_next64_cnfs_part02',B+'exact_eight_next64_cnfs_part03',
 B+'exact_eight_next64_consolidated',B+'exact_eight_next64_native_preflight',B+'exact_eight_next64_native_pilot',
 I+'exact_eight_next64_selection',I+'exact_eight_next64_cnfs_v3',I+'exact_eight_next64_object_calibration',I+'exact_eight_next64_proofs',
 B+'exact_eight_four_builds_plan',B+'exact_eight_four_builds_plan_v2',
 B+'exact_eight_four_builds_preparation',B+'exact_eight_four_builds_preparation_v2',B+'exact_eight_four_builds_v2_correction',I+'four_serial_build_engineering',
 B+'exact_eight_prefix64_source_preparation',I+'exact_eight_prefix64_source_review',
 N+'exact_eight_prefix64_batch02_request',N+'exact_eight_prefix64_batch02_selection',
 N+'exact_eight_prefix64_batch02_execution',N+'exact_eight_prefix64_batch02_build_launcher',
 N+'exact_eight_prefix64_batch02_cnfs_part00',N+'exact_eight_prefix64_batch02_cnfs_part01',
 N+'exact_eight_prefix64_batch02_cnfs_part02',N+'exact_eight_prefix64_batch02_cnfs_part03',N+'exact_eight_prefix64_batch02_consolidated',
 J+'exact_eight_prefix64_batch02_selection',
]
# Future in this already allocated batch: add only after terminal immutable pins.
EXPECTED_BATCH02_LATER_DIRECTORIES=[
 J+'exact_eight_prefix64_batch02_cnfs_v3',J+'exact_eight_prefix64_batch02_object_calibration',
 N+'exact_eight_prefix64_batch02_native_preflight',N+'exact_eight_prefix64_batch02_native_pilot',
 J+'exact_eight_prefix64_batch02_proofs',
]
FILES=[
 'acceleration/select_20260930_exact_eight_next64.py',
 'acceleration/theory_20260930_exact_eight_next64_plan.md',
 'acceleration/audit_20260930_exact_eight_next64_selection.py',
 'acceleration/audit_20260930_exact_eight_next64_selection_spec.md',
 'acceleration/prepare_20260930_exact_eight_next64_launch.py',
 'acceleration/execute_20260930_exact_eight_next64_builds.py',
 'acceleration/run_20260930_exact_eight_four_builds.py',
 'acceleration/run_20260930_exact_eight_four_builds_spec.md',
 'acceleration/run_20260930_exact_eight_four_builds_v2.py',
 'acceleration/run_20260930_exact_eight_four_builds_v2_spec.md',
 'acceleration/check_20260930_exact_eight_four_builds_preparation.py',
 'acceleration/check_20260930_exact_eight_four_builds_preparation_v2.py',
 'acceleration/audit_20260930_four_serial_build_engineering.py',
 'acceleration/audit_20260930_four_serial_build_engineering_spec.md',
 'acceleration/select_20260930_exact_eight_prefix64.py',
 'acceleration/select_20260930_exact_eight_prefix64_spec.md',
 'acceleration/check_20260930_exact_eight_prefix64_preparation.py',
 'acceleration/audit_20261001_exact_eight_prefix64_selection.py',
 'acceleration/audit_20261001_exact_eight_prefix64_selection_spec.md',
 'docs/REVIEW_20260930_EXACT_EIGHT_PREFIX64_SOURCE.md',
 'acceleration/theory_20261001_exact_eight_prefix64_batch02_plan.md',
 'acceleration/audit_20260930_exact_eight_explicit_batch_v3.py',
 'acceleration/audit_20260930_exact_eight_explicit_batch_v3_spec.md',
 'acceleration/audit_20260930_exact_eight_explicit_batch_proofs_v2.py',
 'acceleration/audit_20260930_exact_eight_explicit_batch_proofs_v2_spec.md',
]
BOUNDARY={
 'status':'CANDIDATE_SOURCE_ONLY_NOT_EXECUTED',
 'scope':'Explicit requested engineering and first-next64/batch02 seed only; not final wave29 closure.',
 'required_later_additions':['Root-frozen registration/checkpoint/report/replay and independent publication metadata.',
     'Root-selected separately gated GF3 witness and uniform-Gram diagnostic cohorts.',
     'Exact terminal batch02 encoding/object/native/proof identities; retain all failures if any.',
     'Complete authenticated raw-model and proof recovery packages if required by public size limits.'],
 'excluded':['Any batch03 or later allocation/build/attempt.','Protected private oriented log, PROMPT, tools/submodule content.','Unregistered or unrelated loose historical paths.'],
 'claim_count_frozen':False,'inventory_executed':False,'mathematical_approval':False,
}
