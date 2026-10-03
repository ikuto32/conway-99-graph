"""Replay frozen independent audits into a fresh directory; never rerun searches."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1]
I='acceleration/results/20260930_independent_review/'
NAMES=['exact_eight_next_lift','exact_eight_next_lift_object_calibration','exact_eight_next_lift_unsat','triplicate_psd_kernel_options','exact_eight_psd_screen','exact_eight_campaign','exact_eight_campaign_object_calibration','exact_eight_campaign_coverage_v2','exact_eight_campaign_inventory','exact_eight_first12_proofs']


def h(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--plan-only',action='store_true');args=ap.parse_args()
    out=(ROOT/args.out).resolve();assert out.is_relative_to(ROOT) and not out.exists()
    assert out.is_relative_to(ROOT/'build'/'research-local'),'Replay outputs must stay in build/research-local'
    checkpoint=read('acceleration/results/20260930_resume/twentyseventh_milestone_checkpoint.json')
    plan=[]
    for name in NAMES:
        sp=I+name+'/summary.json';summary=read(sp)
        assert checkpoint['evidence_sha256'].get(sp,h(sp))==h(sp)
        record=summary;rp=sp
        if 'command' not in record:rp=I+name+'/execution_receipt.json';record=read(rp)
        saved=record['command'];assert isinstance(saved,list) and '--out' in saved
        script_index=next(i for i,v in enumerate(saved) if v.startswith('acceleration/audit_') and v.endswith('.py'));script=saved[script_index]
        pins=summary.get('inputs_sha256',{})|record.get('inputs_sha256',{})
        assert pins.get(script)==h(script),('checker source binding',script)
        command=[sys.executable,'-B',*saved[script_index:]];command[command.index('--out')+1]=str(out/name)
        plan.append(dict(name=name,saved_command_record=rp,saved_command_record_sha256=h(rp),saved_command=saved,
                         command=command,checker_sha256=h(script),expected_status=summary['status']))
    if args.plan_only:
        print(json.dumps(dict(status='TWENTYSEVENTH_AUDIT_REPLAY_PLAN_CHECKED',commands=plan),indent=2));return
    out.mkdir(parents=True,exist_ok=False)
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
                  source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  wrapper_sha256=h(Path(__file__).relative_to(ROOT)),plan=plan,
                  limitations=['Repeated execution of frozen independent checkers; not a new independent implementation.','No producer or native search is launched; the retained complete proof is replayed.'])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    results=[]
    for item in tqdm(plan,desc='Replay wave27 audits',mininterval=1):
        p=subprocess.run(item['command'],cwd=ROOT,capture_output=True,timeout=180)
        (out/(item['name']+'.stdout.log')).write_bytes(p.stdout);(out/(item['name']+'.stderr.log')).write_bytes(p.stderr)
        results.append(dict(name=item['name'],exit_code=p.returncode))
        (out/'checkpoint.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf8')
        assert p.returncode==0,item['name']
        actual=json.loads((out/item['name']/'summary.json').read_bytes())
        assert actual['status']==item['expected_status'],item['name']
    (out/'summary.json').write_text(json.dumps(dict(status='TWENTYSEVENTH_AUDIT_REPLAY_PASS',completed=len(results),results=results),indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
