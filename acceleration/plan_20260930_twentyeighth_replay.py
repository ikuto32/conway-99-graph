"""Derive replay commands from exact saved audits; do not execute them."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
PINS={
'exact_eight_next32_cnfs':'92c101caade4529dfccc5e0f9315608e8c953ee9faab024b1a4dea55b331d347',
'exact_eight_next32_object_calibration':'e99094394072ccf07333d7d02ed058bfd2b37fac5c3c6fe80b2edc17820377c8',
'exact_eight_next32_proofs':'21ee1b189c8b250eabcaedad43a79b9025978d540a1480f1c03eaeb446acee4c',
'exact_eight_first12_union_v2':'9ce71dea74e323a4f06d20cdf50c80ca75ce0b26d0c7feb18d54f928eb116726',
'exact_eight_sizeclass16_cnfs_v2':'b5e5a90ecc9a52996200e3e8cc4988fd04a85122be22b7355de73678ddcb2b0a',
'exact_eight_sizeclass16_object_calibration':'70f0899373d1a4383a9553f936a795e709983309f1b50d6b7569e64c54d1b3f9',
'exact_eight_sizeclass16_proofs':'04d47a627081f42def048826f08bdf2574eff67479275d46112033bf994e4494',
'exact_eight_kernel_redundancy':'6e12ed8b6147d2db20691fe93ec9f45be3f08ef68d541c617e1ffcae505a2a55'}
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    commands=[]
    for name,pin in PINS.items():
        p=I+name+'/summary.json';assert h(p)==pin;r=json.loads((ROOT/p).read_bytes());saved=r['command']
        index=next(i for i,v in enumerate(saved)if v.startswith('acceleration/audit_')and v.endswith('.py'));script=saved[index]
        assert r['inputs_sha256'][script]==h(script)and '--out'in saved
        replay=[sys.executable,'-B',*saved[index:]];replay[replay.index('--out')+1]='build/research-local/wave28-replay/'+name
        commands.append(dict(name=name,original_report=p,original_report_sha256=pin,original_command=saved,replay_command=replay,expected_status=r['status'],source_sha256=h(script)))
    out=ROOT/'acceleration/results/20260930_resume/twentyeighth_replay_plan.json'
    result=dict(status='TWENTYEIGHTH_REPLAY_COMMANDS_AUTHENTICATED_NOT_EXECUTED',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=h(Path(__file__).relative_to(ROOT)),commands=commands,replay_calls=0,native_search_calls=0,skipped_checks=['No fresh repeat of the eight already successful independent mathematical audits during publication preparation; their original complete execution records remain authoritative.'],limitations=['This plan verifies source/command identities, not mathematical correctness.','Use a fresh output root when replaying; preserve any failure and do not overwrite original evidence.'])
    with out.open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(commands=len(commands),replay_calls=0,sha256=h(out.relative_to(ROOT)))))
if __name__=='__main__':main()
