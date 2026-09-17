"""Replay frozen positive checker in a Git-only checkout, redirecting one output path."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback

CHECKER='acceleration/audit_20260917_moment_positive600.py'
REPORT='acceleration/results/20260917_independent_review/moment_positive600.json'
REPORT_HASH='d435c7789bd2f181e3a870b2019ae309cdbf2d9530bc21b2d987d40671444bc8'
def require(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def route(value,mode,isolated,original_output,new_output):
    p=Path(value).resolve()
    if p==original_output:return new_output
    if any(c in mode for c in 'wax+'):
        raise PermissionError('Only the frozen exact output target may be redirected')
    require(p.is_relative_to(isolated),'Repository Path.open outside isolated root')
    return p
def provenance_command_allowed(command):
    return command == ['git','rev-parse','HEAD'] or command == 'git rev-parse HEAD'
def controls(root,out):
    old=root/REPORT;results=[]
    cases=[('exact_output_write',old,'x',out),('exact_output_final_hash_read',old,'rb',out),('ordinary_input',root/'uv.lock','rb',root/'uv.lock'),('different_write',root/'other.json','x',None),('output_prefix_collision',Path(str(old)+'.extra'),'x',None),('outside_root_read',root.parent/'private.json','rb',None)]
    for name,p,mode,expected in cases:
        try:r=route(p,mode,root,old,out);passed=expected is not None and r==expected
        except(PermissionError,ValueError):passed=expected is None
        require(passed,'Mapping control '+name);results.append(dict(name=name,outcome='PASS'))
    for command,expected in [(['git','rev-parse','HEAD'],True),('git rev-parse HEAD',True),('git rev-parse HEAD & echo x',False),('git rev-parse HEAD; echo x',False),(['git','rev-parse','HEAD','--other'],False),('git status',False)]:
        require(provenance_command_allowed(command)==expected,'Strict provenance argv control')
        results.append(dict(name='strict_provenance_argv',command=command,expected=expected,outcome='PASS'))
    return results
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--commit',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('--controls-only',action='store_true');args=ap.parse_args()
    root=args.root.resolve();out=args.out.resolve();receipt=args.receipt.resolve();old=root/REPORT
    require(out!=receipt and out!=old and receipt!=old,'Output collision');require(not out.exists()and not receipt.exists(),'Preserve prior evidence')
    out.parent.mkdir(parents=True,exist_ok=True);receipt.parent.mkdir(parents=True,exist_ok=True);control_results=controls(root,out)
    header=dict(timestamp=datetime.now(timezone.utc).isoformat(),command_argv=[sys.executable,*sys.argv],cwd=str(Path.cwd()),isolated_root=str(root),requested_source_commit=args.commit,wrapper_sha256=digest(__file__),python=platform.python_version(),mapping_controls=control_results)
    if args.controls_only:
        receipt.write_text(json.dumps(dict(**header,status='PUBLIC_MOMENT_OUTPUT_MAPPING_CONTROLS_PASS',scientific_checker_executed=False),indent=2));print('PUBLIC_MOMENT_OUTPUT_MAPPING_CONTROLS_PASS');return 0
    def git(*cmd):return subprocess.check_output(['git','-C',str(root),*cmd])
    require(len(args.commit)==40 and all(c in '0123456789abcdef'for c in args.commit),'Full immutable commit required')
    require(Path(git('rev-parse','--show-toplevel').decode().strip()).resolve()==root,'Require a real isolated Git checkout; nested loose extraction could observe parent HEAD')
    require(git('rev-parse','HEAD').decode().strip()==args.commit,'Isolated Git HEAD mismatch')
    # Verify the exact runtime closure as Git blobs before importing any checker.
    seed=git('show',args.commit+':'+REPORT);require(hashlib.sha256(seed).hexdigest()==REPORT_HASH,'Published audit pin')
    published=json.loads(seed);inventory=dict(published['inputs_sha256']);inventory[REPORT]=REPORT_HASH
    require(CHECKER in inventory,'Scientific source must be hash-bound')
    for rel,want in inventory.items():
        p=(root/rel).resolve();require(not Path(rel).is_absolute()and p.is_relative_to(root),'Unsafe inventory path')
        blob=git('show',args.commit+':'+rel);require(hashlib.sha256(blob).hexdigest()==want and digest(p)==want,'Git-only byte identity '+rel)
    allowed={str((root/p).resolve()):v for p,v in inventory.items()};opened=set();rejected=[];redirects=[];environment=[Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()]
    original_open=Path.open;output_paths={out,receipt};sys.dont_write_bytecode=True
    def audit(event,values):
        if event=='subprocess.Popen':
            command=values[1];require(provenance_command_allowed(command),'Only frozen checker provenance Git query allowed');return
        if event!='open' or not values or not isinstance(values[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(values[0])).resolve();flags=values[2]if len(values)>2 and isinstance(values[2],int)else 0;mode=values[1]if len(values)>1 and isinstance(values[1],str)else ''
        writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))or any(c in mode for c in 'wax+')
        if p in output_paths:return
        if writing:rejected.append(str(p));raise PermissionError('Replay forbids all input/environment writes')
        if str(p)in allowed:opened.add(str(p));return
        if any(p.is_relative_to(base)for base in environment):return
        rejected.append(str(p));raise PermissionError('Replay input outside verified Git closure or trusted environment: '+str(p))
    def redirected_open(self,mode='r',*pargs,**kwargs):
        p=self.resolve()
        if p==old:
            redirects.append(dict(from_path=str(p),to_path=str(out),mode=mode));return original_open(out,mode,*pargs,**kwargs)
        return original_open(self,mode,*pargs,**kwargs)
    os.chdir(root);sys.path=[str(root/'acceleration')]+[p for p in sys.path if p and any(Path(p).resolve().is_relative_to(base)for base in environment)]
    sys.addaudithook(audit);Path.open=redirected_open;started=time.monotonic();status='FAIL';error=None
    try:
        spec=importlib.util.spec_from_file_location('frozen_positive_moment_checker',root/CHECKER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        require(module.ROOT.resolve()==root,'Imported scientific root mismatch');sys.argv=[str(root/CHECKER)];module.main()
        result=json.loads(out.read_bytes());require(result['status']=='INDEPENDENT_PARTIAL_K_POSITIVE_MOMENT_EXCLUSION_PASS','Unexpected checker result')
        require(result['exact_bound']==published['exact_bound']and result['checked_original_choices']==54478,'Scientific replay result mismatch');status='PASS'
    except Exception as exc:error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    finally:Path.open=original_open
    require(all(digest(Path(p))==want for p,want in allowed.items()),'Input changed during replay')
    record=dict(**header,status='PUBLIC_FROZEN_MOMENT_CHECKER_REPLAY_'+status,error=error,source_checker_sha256=inventory[CHECKER],frozen_source_and_raw_artifacts_unchanged=True,verified_git_blob_count=len(inventory),verified_git_inputs_sha256=inventory,opened_git_paths=sorted(Path(p).relative_to(root).as_posix()for p in opened),rejected_paths=rejected,output_redirections=redirects,output_sha256=digest(out)if out.exists()else None,elapsed_seconds=time.monotonic()-started,limitations=['Repeated execution of the existing independent checker, not another independent mathematical discovery or review.','Only the exact frozen report Path.open target is redirected; scientific code, artifact bytes and arithmetic are unchanged.','Python installation and packages beneath interpreter prefixes remain trusted environment; all other data reads must be verified Git blobs.','Git subprocess is restricted to the frozen checker provenance query, with independently confirmed isolated top-level and immutable HEAD.'])
    with receipt.open('x',encoding='utf8')as f:json.dump(record,f,indent=2)
    print(record['status']);return 0 if status=='PASS'else 1
if __name__=='__main__':raise SystemExit(main())
