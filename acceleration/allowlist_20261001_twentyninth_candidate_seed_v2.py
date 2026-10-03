"""Unexecuted wave29 seed correction, preserving the original seed verbatim.

No directory is scanned, no file is hashed and no inventory is emitted by this
module. Root still must freeze final cohort/checkpoint before any inventory.
"""
from allowlist_20261001_twentyninth_candidate_seed import DIRECTORIES as ORIGINAL_DIRECTORIES,EXPECTED_BATCH02_LATER_DIRECTORIES,FILES as ORIGINAL_FILES,BOUNDARY as ORIGINAL_BOUNDARY,B,I
DIRECTORIES=ORIGINAL_DIRECTORIES+[
 B+'exact_eight_next64_launch_execution',
 B+'exact_eight_next64_build_launcher',
 I+'exact_eight_next64_proof_preparation',
]
FILES=[p for p in ORIGINAL_FILES if p!='acceleration/audit_20260930_exact_eight_explicit_batch_proofs_v2_spec.md']+[
 'docs/AUDIT_20260930_EXACT_EIGHT_EXPLICIT_BATCH_PROOFS_V2.md',
 'acceleration/allowlist_20261001_twentyninth_candidate_seed.py',
 'acceleration/allowlist_20261001_twentyninth_candidate_seed_v2.py',
]
BOUNDARY=dict(ORIGINAL_BOUNDARY,version=2,correction='Remove nonexistent guessed proof_v2_spec path; use actual frozen proof-audit document and explicitly include three first-next64 provenance directories. No inventory or publication execution.')
CORRECTION_PINS={
 'acceleration/allowlist_20261001_twentyninth_candidate_seed.py':'83790b7b011494ea5491b05bcb6e3320d2a4cb49cd8035617b4f2bb7a8d4653f',
 'docs/AUDIT_20260930_EXACT_EIGHT_EXPLICIT_BATCH_PROOFS_V2.md':'932da705a7626a59dd5734983b213e27ef56c93777ab3bc342ac01699807a5c0',
}
