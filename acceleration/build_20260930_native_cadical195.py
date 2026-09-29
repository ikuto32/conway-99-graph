"""Build the pristine pinned native solver under the existing WSL distribution."""
from datetime import datetime,timezone
from hashlib import sha256
import json,platform,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'build/research-cadical195/source'
OUT=ROOT/'acceleration/results/20260930_native_cadical195_build'
WSL='/mnt/c/Users/ikuto/projects/conway-99-graph/build/research-cadical195/source'
PIN='146207318796f094dcded87349a64f0c6927309e'
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    OUT.mkdir(exist_ok=False)
    assert subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip()==PIN
    assert not subprocess.check_output(['git','-C',str(SOURCE),'status','--porcelain'],text=True).strip()
    archive=OUT/'cadical-1.9.5-source.tar.gz'
    subprocess.run(['git','-C',str(SOURCE),'archive','--format=tar.gz','--output',str(archive),'HEAD'],check=True)
    save(OUT/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'source_sha256':h(Path(__file__)),
        'upstream':'https://github.com/arminbiere/cadical','upstream_version':'rel-1.9.5','upstream_commit':PIN,'source_archive_sha256':h(archive),
        'scope':'Engineering build only; no mathematical verification and no research solver invocation.',
        'selection':'Same named solver release as the Windows wrapper, now pristine native CLI; no performance comparison assumed.',
        'limits':{'configure_seconds':30,'build_seconds':240,'make_jobs':4},'source_changes':[],'research_calls':0})
    records=[]
    for name,seconds,argv in [('compiler',10,['g++','--version']),('platform',10,['uname','-a']),('configure',30,['./configure']),('make',240,['make','-j4']),('help',10,['build/cadical','-h'])]:
        cmd=['wsl','-d','Ubuntu-24.04','--cd',WSL,'--','timeout','--signal=TERM','--kill-after=5',str(seconds),*argv]
        started=time.monotonic();r=subprocess.run(cmd,capture_output=True,timeout=seconds+20)
        log=OUT/(name+'.log');log.write_bytes(r.stdout+r.stderr)
        record={'name':name,'command':cmd,'exit_code':r.returncode,'wall_seconds':time.monotonic()-started,'log_sha256':h(log)}
        records.append(record)
        if r.returncode:
            save(OUT/'failure.json',{'records':records,'status':'BUILD_OR_INSPECTION_FAILED','research_calls':0})
            raise RuntimeError(record)
        print(json.dumps({'completed':name,'seconds':record['wall_seconds']}),flush=True)
    native=SOURCE/'build/cadical'
    assert not subprocess.check_output(['git','-C',str(SOURCE),'diff','--name-only'],text=True).strip()
    save(OUT/'receipt.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'status':'PRODUCER_NATIVE_BUILD_COMPLETE','records':records,
        'native_path':str(native),'native_sha256':h(native),'native_bytes':native.stat().st_size,'source_archive_sha256':h(archive),'source_changes':[],
        'availability':'LOCAL_ONLY','retrieval':'Rebuild the pinned source archive with the recorded compiler and commands; exact runtime binary hash retained.',
        'independent_calibration_pending':True,'research_calls':0})
    print(json.dumps({'status':'PRODUCER_NATIVE_BUILD_COMPLETE','native_sha256':h(native)}),flush=True)
if __name__=='__main__':main()
