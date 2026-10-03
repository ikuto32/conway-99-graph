"""Source-only/restoration engineering controls; no mathematical verification."""
from copy import deepcopy
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results/20261001_twentyninth_recovery_controls';M=ROOT/'acceleration/results/20261001_twentyninth_raw_recovery/manifest.json';SCRIPT=ROOT/'acceleration/recover_20261001_twentyninth_raw_artifacts.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def main():
    out=B/'corruptions';out.mkdir(exist_ok=False);original=json.loads(M.read_bytes());fresh=json.loads((B/'fresh_recovery.json').read_bytes());assert fresh['status']=='TWENTYNINTH_RAW_ARTIFACT_RECOVERY_PASS' and fresh['originals']==len(original['records']) and fresh['action_counts']=={'RESTORED_MISSING':len(original['records'])};rows=[]
    for case in ['manifest_hash','raw_length','part_hash','part_gap','duplicate_part','path_escape','existing_raw_conflict']:
        data=deepcopy(original);dest=ROOT/'build/twentyninth-recovery-negative';bad_target=None
        if case=='raw_length':data['records'][0]['bytes']+=1
        if case=='part_hash':data['records'][0]['parts'][0]['gzip_sha256']='0'*64
        if case=='part_gap':data['records'][0]['parts'][0]['raw_offset']=1
        if case=='duplicate_part':data['records'][0]['parts'].append(deepcopy(data['records'][0]['parts'][0]))
        if case=='path_escape':data['records'][0]['path']='../escape'
        if case=='existing_raw_conflict':
            dest=ROOT/'build/twentyninth-recovery-existing-conflict';bad_target=dest/data['records'][0]['path'];bad_target.parent.mkdir(parents=True,exist_ok=True);bad_target.open('xb').write(b'wrong-existing-original')
        p=out/(case+'.fixture');p.write_text(json.dumps(data)+'\n',encoding='utf8',newline='\n');receipt=out/(case+'.unexpected.json');digest='0'*64 if case=='manifest_hash'else sha(p)
        cp=subprocess.run([sys.executable,'-B',str(SCRIPT),'--manifest',str(p),'--manifest-sha256',digest,'--destination-dir',str(dest),'--verify-only','--receipt',str(receipt)],cwd=ROOT,capture_output=True,timeout=20)
        (out/(case+'.stdout.log')).write_bytes(cp.stdout);(out/(case+'.stderr.log')).write_bytes(cp.stderr)
        assert cp.returncode!=0 and not receipt.exists(),case
        if bad_target:assert bad_target.read_bytes()==b'wrong-existing-original'
        rows.append(dict(case=case,rejected=True,exit_code=cp.returncode,fixture_path=key(p),fixture_sha256=sha(p),no_success_receipt=True))
    summary=dict(status='TWENTYNINTH_RECOVERY_ENGINEERING_CONTROLS_PASS',inputs_sha256={key(SCRIPT):sha(SCRIPT),key(M):sha(M),key(Path(__file__)):sha(Path(__file__))},fresh_recovery_receipt=dict(path=key(B/'fresh_recovery.json'),sha256=sha(B/'fresh_recovery.json')),controls=rows,outputs_sha256={key(p):sha(p)for p in out.iterdir()},scope='Seven malformed manifest/part/path/existing-file controls plus complete fresh restoration of every manifest original. No mathematical promotion.',native_calls=0)
    (B/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8',newline='\n');print(sha(B/'summary.json'))
if __name__=='__main__':main()
