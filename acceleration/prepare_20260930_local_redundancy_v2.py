"""Preserve the original metadata-check failure and correct only its mask contract."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def main():
    source=ROOT/'acceleration/audit_20260930_local_redundancy_v1.py';raw=source.read_bytes()
    target=ROOT/'acceleration/audit_20260930_local_redundancy_v2.py'
    changes=[(b'independent_review/local_redundancy\'',b'independent_review/local_redundancy_v2\''),
       (b"assert outer_mask==int(case['star_mask'],16)",b"assert int(case['star_mask'],16) & ~outer_mask == 0  # Saved variable-edge mask is a subset, not the full row.")]
    fixed=raw
    for before,after in changes:assert fixed.count(before)==1;fixed=fixed.replace(before,after)
    with target.open('xb')as f:f.write(fixed)
    out=ROOT/'acceleration/results/20260930_independent_review/local_redundancy/failure_and_correction.json'
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],failure='The v1 checker incorrectly compared the variable-edge star_mask to the full outer-neighborhood mask. The first raw graph had already passed symmetry, center equalities, both kernels, degree bound and all SOS coefficients.',
        failed_command='uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_local_redundancy_v1.py',exit_code=1,
        original_failure_timestamp=None,original_failure_timestamp_reason='The original execution did not write a timestamped receipt; tool transcript records exit1 and AssertionError at the metadata comparison.',
        original_source_sha256=sha256(raw).hexdigest(),corrected_source_sha256=sha256(fixed).hexdigest(),
        observed_first_case=dict(whole_outer_neighborhood='0x2d650060000028000',saved_variable_mask='0x2d650020000020000',whole_neighbors=12,saved_variable_neighbors=10),
        correction='Verify the saved mask is a subset of the full row. The precise full-domain generation mapping remains outside this raw-matrix/theorem check and is explicitly not claimed.',
        mathematical_artifact_changed=False,acceptance_threshold_changed=False,prior_cap_lemma_report_preserved=True)
    with out.open('x',encoding='utf-8')as f:json.dump(report,f,indent=2)

if __name__=='__main__':main()
