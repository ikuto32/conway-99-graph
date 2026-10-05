"""Preserve the observed v1 pointer assertion failure and independently enumerate published identities."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ledger=ROOT/'CLAIMS.yaml';assert h(ledger)=='297d6d915c244ccc6dd82c39939eef917a2b0ffa8a76126185b386774a097baf'
    commit='d43ab1ca6638b565d555b0765044668761de6a64';found=[];missing=[]
    for row in yaml.safe_load(ledger.read_bytes())['artifacts']:
        if row['availability']!='LOCAL_ONLY' or not row['path']:continue
        run=subprocess.run(['git','show',commit+':'+row['path']],cwd=ROOT,capture_output=True)
        if run.returncode:missing.append(row['id']);continue
        assert hashlib.sha256(run.stdout).hexdigest()==row['sha256']
        found.append(dict(id=row['id'],path=row['path'],sha256=row['sha256']))
    source=ROOT/'acceleration/publish_20261001_twentyninth_evidence_pointers.py'
    result=dict(recorded_at=datetime.now(timezone.utc).isoformat(),source_commit=commit,
        original_execution_timestamp=None,original_execution_timestamp_reason='The tool response did not supply a UTC start timestamp; this record timestamps the subsequent diagnosis.',
        original_tool_chunk_id='ca35cf',original_exit_code=1,original_error='AssertionError at assert len(changed)==12 and data[claims]==old[claims], before any ledger write.',
        original_command=['uv','run','--locked','--offline','--cache-dir','.uv-cache-20260917','python','-B',source.relative_to(ROOT).as_posix(),'--commit',commit],
        environment={'UV_PROJECT_ENVIRONMENT':'build/research-venv'},cwd=str(ROOT),original_source_sha256=h(source),
        diagnosis_command=[sys.executable,*sys.argv],diagnosis_source_sha256=h(Path(__file__)),
        unchanged_ledger_sha256=h(ledger),published_local_artifacts=found,remaining_local_ids=missing,
        diagnosis='Fourteen exact published artifacts were found, including two older source/build records. V1 expected only the twelve new evidence records.',
        mathematical_claim_changes=[],ledger_mutations=0)
    out=ROOT/'acceleration/results/20261001_twentyninth_publication_pointer_failure';out.mkdir(exist_ok=False)
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(found=len(found),remaining=len(missing),summary_sha256=h(out/'summary.json'))))
if __name__=='__main__':main()
