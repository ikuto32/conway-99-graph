"""Independent code-review controls following the root standalone-mode veto."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import copy
import json
import platform
import subprocess
import sys
from test_validate_claims import EditorialMigrationTests
from validate_claims import validate

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_independent_review/editorial_migration_corrected'
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    inputs=['acceleration/validate_claims.py','acceleration/test_validate_claims.py','docs/claims.schema.json','docs/claims.schema.v1.json','docs/CLAIMS_SCHEMA.md','uv.lock','acceleration/results/20260930_editorial_migration_tooling/correction_v2.json','acceleration/results/20260930_independent_review/editorial_migration_veto/summary.json',Path(__file__).relative_to(ROOT).as_posix()]
    pins={p:digest(ROOT/p) for p in inputs}
    EditorialMigrationTests.setUpClass();fixture=EditorialMigrationTests();fixture.setUp()
    try:
        original=copy.deepcopy(fixture.data)
        cid=fixture.first['id']
        baseline=validate(original,fixture.root,fixture.schema,hash_mode='none',previous=None)
        assert baseline['valid'],baseline['errors']
        outcomes=[]
        mutations={
            'limitations':lambda c:c.update(limitations=['Unapproved deletion of restrictions']),
            'basis':lambda c:c.update(basis=['CITED']),
            'scope':lambda c:c['scope'].update(description='unapproved broadened scope'),
            'statement':lambda c:c.update(statement='unapproved theorem'),
            'assumptions':lambda c:c['assumptions'].append('Assume target asymmetry'),
            'remove_dependency':lambda c:c.update(dependencies=[]),
            'change_relation':lambda c:c['dependencies'][0].update(relation='premise'),
            'creation_date':lambda c:c.update(created_at='2020-01-01T00:00:00Z'),
            'stale_editorial_pass':lambda c:c.update(revision=3),
        }
        for name,mutation in mutations.items():
            data=copy.deepcopy(original);current=next(c for c in data['claims'] if c['id']==cid)
            mutation(current)
            result=validate(data,fixture.root,fixture.schema,hash_mode='none',previous=None)
            assert not result['valid'],name
            outcomes.append(dict(case=name,rejected=True,errors=result['errors']))
        # Authentication must remain mandatory even if other artifact checks skip.
        review_path=fixture.root/fixture.review_name;review=review_path.read_bytes()
        review_path.write_bytes(review+b' ')
        result=validate(original,fixture.root,fixture.schema,hash_mode='none',previous=None)
        assert not result['valid'] and any('SHA-256 mismatch' in e for e in result['errors'])
        outcomes.append(dict(case='altered_review_bytes',rejected=True,errors=result['errors']))
    finally:fixture.tearDown()
    command=[sys.executable,'-B','-m','unittest','discover','-s','acceleration','-p','test_validate_claims.py','-v']
    run=subprocess.run(command,cwd=ROOT,capture_output=True)
    (OUT/'tests.stdout.log').write_bytes(run.stdout);(OUT/'tests.stderr.log').write_bytes(run.stderr)
    assert run.returncode==0,run.stderr.decode(errors='replace')
    assert b'Ran 56 tests' in run.stderr and b'OK' in run.stderr
    assert all(digest(ROOT/p)==value for p,value in pins.items())
    report=dict(status='INDEPENDENT_CORRECTED_EDITORIAL_MIGRATION_CHECKER_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),python=platform.python_version(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,verifier='/root independent code reviewer',original_veto_preserved=True,positive_standalone_fixture_pass=True,independent_corruptions=outcomes,suite=dict(command=command,exit_code=run.returncode,tests=56,stdout_sha256=digest(OUT/'tests.stdout.log'),stderr_sha256=digest(OUT/'tests.stderr.log')),code_review='Reviewed the full schema/validator/test diff. The correction authenticates the immutable review and original snapshot before exact initial-transition permitted-field comparison, regardless of previous argument. Mathematical changes stay outside the exception; original verification records and normal dependency impact checks remain required. Later revisions cannot use the revision2 editorial check as a current-revision approval.',shared_components=['Positive synthetic fixture is reused from producer tests; independent adversarial mutations are separately authored.','Registry validator itself is the system under test, not a mathematical verifier.','Python, PyYAML, jsonschema and immutable review artifacts are trusted components.'],limitations=['Finite engineering controls and code review, not a formal proof of validator correctness.','Synthetic fixture dependency PASS is not authorization for a real claim; actual dependent reviews are separately required.','No root ledger mutation or mathematical discovery occurs in this review.'],target_resolution=False)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],sha256=digest(OUT/'summary.json'))))
if __name__=='__main__':main()
