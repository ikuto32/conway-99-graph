"""Independent standalone-mode adversarial check of editorial migration gate."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

from test_validate_claims import EditorialMigrationTests
from validate_claims import validate

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_independent_review/editorial_migration_veto'
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    names=['acceleration/validate_claims.py','acceleration/test_validate_claims.py','docs/claims.schema.json','docs/CLAIMS_SCHEMA.md']
    pins={name:digest(ROOT/name) for name in names}
    expected='48c886bed1a60c63d7e7c2ad0decb29811cfa0f1f0b3b6f38bdecddc9b0c3644'
    if pins[names[0]]!=expected:raise ValueError('original reviewed implementation already changed; use its saved snapshot')
    for name in names:(OUT/Path(name).name).write_bytes((ROOT/name).read_bytes())
    EditorialMigrationTests.setUpClass()
    fixture=EditorialMigrationTests();fixture.setUp()
    try:
        positive=validate(fixture.data,fixture.root,fixture.schema,hash_mode='none',previous=None)
        fixture.first['limitations']=['Unapproved deletion of restrictions']
        corrupted=validate(fixture.data,fixture.root,fixture.schema,hash_mode='none',previous=None)
        outcome='VETO_UNAPPROVED_FIELD_ACCEPTED' if positive['valid'] and corrupted['valid'] else 'UNEXPECTED_CONTROL_RESULT'
        report=dict(status=outcome,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),python=platform.python_version(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),inputs_sha256=pins,verifier='/root independent code reviewer',checking_path='Independent adversarial mutation and code inspection; positive fixture reused from producer tests, explicitly synthetic.',positive_valid=positive['valid'],corrupted_valid=corrupted['valid'],corrupted_errors=corrupted['errors'],claim_id=fixture.first['id'],mutation={'field':'limitations','value':['Unapproved deletion of restrictions']},scope='Validator standalone mode at exact migration revision; no root ledger was changed.',required_correction='At the exact approved migration revision, enforce all permitted field changes against the immutable old snapshot even without --previous. Preserve future revision impact rules.',mathematical_claim_changed=False,target_resolution=False)
        (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(dict(status=outcome,sha256=digest(OUT/'summary.json'))))
    finally:fixture.tearDown()
if __name__=='__main__':main()
