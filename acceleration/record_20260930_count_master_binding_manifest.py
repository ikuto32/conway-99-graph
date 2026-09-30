"""Append manifest/summary to the already frozen count encoding claim binding."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'acceleration/results/20260930_independent_review/count_master_claim_binding'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    binding=D/'claim_binding.json';assert digest(binding)=='bb7d6e4ae74b7510f9647719529f2574a79949322742a026455e50d3ef7c06f8'
    inputs={binding.relative_to(ROOT).as_posix():digest(binding)}
    for p in ['acceleration/record_20260930_count_master_audit_bindings.py','acceleration/record_20260930_count_master_binding_manifest.py','acceleration/results/20260930_independent_review/hadamard_count_master_cnf_v2/summary.json','acceleration/results/20260930_independent_review/hadamard_count_master_object_calibration/summary.json','acceleration/results/20260930_independent_review/hadamard_count_master_cnf_correction/correction.json']:inputs[p]=digest(ROOT/p)
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,note='Append-only provenance for an already frozen binding; no statement, gate, claim or ledger mutation.')
    save(D/'manifest.json',manifest);save(D/'summary.json',dict(status='INDEPENDENT_COUNT_MASTER_ENCODING_CLAIM_BINDING_COMPLETE',inputs_sha256=inputs,outputs_sha256={(D/'manifest.json').relative_to(ROOT).as_posix():digest(D/'manifest.json'),binding.relative_to(ROOT).as_posix():digest(binding)},claim_id='C-FIXED-HADAMARD-ARBITRARY-EXCEPTION-COUNT-MASTER-ENCODING',revision=1,new_mathematical_check=False,registry_changed=False))
    print(digest(D/'summary.json'))
if __name__=='__main__':main()
