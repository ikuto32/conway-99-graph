"""Independent fresh restoration/full byte comparison of one bound fixture census."""
import argparse,hashlib,json,platform,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
import audit_20261002_wave33_model_recovery_v1 as calibration
import audit_20261002_batch05_raw_recovery_v1 as core
ROOT=Path(__file__).resolve().parents[1]
RAW='acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/srg243_all_primary_coupling_records.json'
RAW_SHA='447d922b1a0ad28b3b7d459f84b8c02e55da7b9cc8da8615a5e882b6482d4919'
AUDIT='acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/summary.json'
AUDIT_SHA='e7631851f9cc5716c9d8a1bf5b30f9a4644d8e2170f116d1bb30378fbeb16d70'
PINS={'acceleration/recover_20261001_twentyninth_raw_artifacts.py':'d55e458b2fb980691f416ca346782ba371bf713c80b8ecb055c5240f794a5730','acceleration/audit_20261002_batch05_raw_recovery_v1.py':'8b44efe2ce1d839526a0ed2348d97b66b7eb0c1c54580a18ed72bd7bf14448ca','acceleration/audit_20261002_wave33_model_recovery_v1.py':'d9299167b78c63eca917de18c2d3a7990ade2ed499a1abfb76b815e69de52700'}
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(p):
    with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def save(p,obj):
    with p.open('x',encoding='utf8',newline='\n') as s:json.dump(obj,s,indent=2,sort_keys=True);s.write('\n')
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',required=True);ap.add_argument('--manifest-sha256',required=True);ap.add_argument('--destination',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    start=time.monotonic();d=CommandDeadline(a.seconds,allocation_reason='One57,902,243-byte census fresh restore and independent complete streaming/original comparison, positive/corrupt controls;180outer150worker30reserve,no math replay')
    out=a.out.resolve();need(out.is_relative_to(ROOT),'bounded fresh audit output');out.mkdir(parents=True,exist_ok=False);pins={}
    def tick():need(not d.status()['stop_required'] and d.status()['remaining_seconds']>30,'not completed within the allocated budget')
    def pin(p,h=None):
        tick();name=Path(p);need(not name.is_absolute() and '..' not in name.parts,'literal contained input');f=(ROOT/name).resolve();need(f.is_relative_to(ROOT),'bounded input path');actual=sha(f);need(h is None or actual==h,'exact input hash:'+p);pins[p]=actual
    try:
        calibrated=calibration.controls(d)
        for p,h in PINS.items():pin(p,h)
        pin('acceleration/package_20261003_wave36_coupling_control_v1.py','fa56aded4d9a993180aaf59489ca409dae666f3d07ad9ea86547f95901ef89c9')
        pin('acceleration/package_20261003_wave36_coupling_control_v1_spec.md','e7361579083f6f30af52fd348ae42d494dd0952044677ca8536cbc6ceab69249')
        supervisor_name='acceleration/results/20261003_wave36_coupling_package_supervision01/summary.json';pin(supervisor_name)
        supervisor=json.loads((ROOT/supervisor_name).read_bytes());need(supervisor['command_exit_code']==0 and supervisor['cleanup']['reaped'] is True and supervisor['cleanup']['job_active_zero_observed'] is True,'actual packaging terminal containment')
        for p in [Path(__file__).resolve().relative_to(ROOT).as_posix(),'acceleration/audit_20261003_wave36_census_recovery_v1_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']:pin(p)
        pin(AUDIT,AUDIT_SHA);audited=json.loads((ROOT/AUDIT).read_bytes());need(audited['inputs_sha256'][RAW]==RAW_SHA,'bound prior complete fixture audit hash')
        pin(a.manifest,a.manifest_sha256);manifest=json.loads((ROOT/a.manifest).read_bytes());need(len(manifest['records'])==1,'exact one census member')
        need(manifest['source_sha256']==pins['acceleration/package_20261003_wave36_coupling_control_v1.py'],'exact frozen packaging source')
        row=manifest['records'][0];need(row['raw_path']==RAW and row['raw_sha256']==RAW_SHA and row['raw_bytes']==57902243 and len(row['parts'])==7,'exact bound census identity/population')
        for part in row['parts']:pin(part['path'],part['gzip_sha256']);need((ROOT/part['path']).stat().st_size==part['gzip_bytes'],'compressed exact size')
        destination=a.destination.resolve();need(destination.is_relative_to(ROOT/'build') and not destination.exists(),'fresh build destination/no original overwrite')
        receipt=out/'restoration_receipt.json';argv=[sys.executable,'-B','acceleration/recover_20261001_twentyninth_raw_artifacts.py','--manifest',a.manifest,'--manifest-sha256',a.manifest_sha256,'--destination-dir',str(destination),'--receipt',str(receipt)]
        with (out/'restore.stdout.log').open('xb') as stdout,(out/'restore.stderr.log').open('xb') as stderr:
            result=subprocess.run(argv,cwd=ROOT,stdout=stdout,stderr=stderr,timeout=max(1,d.status()['remaining_seconds']-30),check=False)
        need(result.returncode==0,'unchanged restorer exit zero');raw_receipt=json.loads(receipt.read_bytes());need(raw_receipt['status']=='TWENTYNINTH_RAW_ARTIFACT_RECOVERY_PASS' and raw_receipt['action_counts']=={'RESTORED_MISSING':1},'exact one clean missing restore')
        normalized={'path':RAW,'sha256':RAW_SHA,'bytes':57902243,'parts':row['parts']}
        with (ROOT/RAW).open('rb') as original:checked=core.recover(normalized,lambda p:(ROOT/p).read_bytes(),original,d)
        restored=destination/RAW;pin(RAW,RAW_SHA);need(sha(restored)==RAW_SHA and restored.stat().st_size==57902243,'complete restored hash/size')
        with restored.open('rb') as fresh,(ROOT/RAW).open('rb') as original:
            while True:
                tick();x=fresh.read(1048576);y=original.read(1048576);need(x==y,'complete restored/original byte equality')
                if not x:break
        record=dict(**checked,fresh_destination=str(restored),restored_every_byte_matches=True,mathematical_audit_fixture_hash=RAW_SHA)
        report={'status':'INDEPENDENT_WAVE36_SRG243_COUPLING_CENSUS_RECOVERY_V1_PASS','timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/checkpoint_audit','producer':'/root/native_driver','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,'manifest':a.manifest,'manifest_sha256':a.manifest_sha256,'originals':1,'raw_bytes':57902243,'gzip_parts':7,'gzip_bytes':sum(p['gzip_bytes'] for p in row['parts']),'records':[record],'destination':str(destination),'fresh_restore_argv':argv,'fresh_restore_receipt_sha256':sha(receipt),'controls':calibrated,'mathematical_verification':False,'public_availability_established':False,'target_resolution':False,'shared_components':['Unchanged pinned historical restorer CLI, prior independent bounded streaming every-byte checker/calibration, Python gzip/SHA256 and supported Job supervisor.'],'limitations':['Byte recovery only; prior necessary-operator/fixture theorem is hash-bound, not replayed.','Original raw is never overwritten. Temporary clean recovered duplicate underbuild is not a Git publication member.','Future public availability needs exact immutable commit and full package confirmation; this report makes no PUBLIC assertion.'],'elapsed_seconds':time.monotonic()-start,'deadline':d.status()}
        save(out/'summary.json',report);print(json.dumps({'status':report['status'],'report_sha256':sha(out/'summary.json'),'elapsed_seconds':report['elapsed_seconds']}),flush=True)
    except BaseException as e:save(out/'failure.json',{'error':repr(e),'inputs_sha256':pins,'elapsed_seconds':time.monotonic()-start,'mathematical_verification':False,'original_overwritten':False});raise
if __name__=='__main__':main()
