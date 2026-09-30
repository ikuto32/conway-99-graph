"""Append-only correction of premature artifact availability metadata."""
from datetime import datetime,timezone
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'acceleration/results/20260930_independent_review/factor_annealer_pilot/summary.json'
EXPECTED='97858230f5e777d601554e51184f0cb3b57ce6d39ed022a3850005b49c27fdd5'

def digest(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    assert digest(REPORT)==EXPECTED
    old=json.loads(REPORT.read_bytes());assert old['artifact_availability']=='PUBLIC'
    relative=REPORT.relative_to(ROOT).as_posix();command=['git','ls-files','--error-unmatch','--',relative]
    observation=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    result=dict(status='ARTIFACT_AVAILABILITY_METADATA_CORRECTION',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
      corrected_report=dict(path=relative,sha256=EXPECTED,claim_id=old['claim_id'],claim_revision=old['claim_revision']),
      field='artifact_availability',original_value='PUBLIC',corrected_value='LOCAL_ONLY',reason='The pilot cohort had not been published when this independent report was created. Public retrieval at an immutable pushed commit has not yet been confirmed. The original PUBLIC metadata was premature.',
      retrieval='Existing local paths pinned by the original report. A later separate publication binder may establish PUBLIC availability with immutable retrieval links.',
      exact_metadata_scope='This correction changes availability metadata only. The checked artifact bytes, exact objective scores, verifier method, calibration outcomes and scoped saved-state statement remain unchanged.',
      original_report_unchanged=digest(REPORT)==EXPECTED,public_publication_confirmed=False,mathematical_status_changed=False,target_resolution=False,
      read_only_index_observation=dict(command=command,exit_code=observation.returncode,stdout=observation.stdout,stderr=observation.stderr),
      inputs_sha256={relative:EXPECTED,Path(__file__).resolve().relative_to(ROOT).as_posix():digest(Path(__file__))})
    p=args.out/'summary.json'
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(sha256=digest(p),corrected_value='LOCAL_ONLY')))

if __name__=='__main__':main()
