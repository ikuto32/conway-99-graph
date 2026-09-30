"""Construct a count-only SAT witness for the exact interval formula, no solver."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';BASE=B+'hadamard_count_master_cnf/';DATA=B+'count_interval_cnf/';INV=B+'count_interval_inventory/';ASS=B+'hadamard_count_master_native_pilot_v2/main/parsed_model.json';PROFILE=B+'independent_review/count_master_sat_outcome/independent_count_profile.json';GATE=B+'independent_review/count_master_sat_outcome/summary.json'
PINS={ASS:'e2a2a5f6daa251d153aa7396759731332a74031ed4c50d4e45d6d81370ad1077',PROFILE:'0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152',GATE:'61e7eb9643902c866617a270d856a521f71f5b2723c0e731edae3896baba484d',BASE+'model.json':'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',INV+'configuration.json.gz':'97794c8be67bf32276763a0439edc3e83ba81a1fa8ee88604f2d75c5721c1099',DATA+'instance.cnf':'5ee253b41de8cfcc5529175c4685c0fc9a8886b8d6c3600e435ae9db5146cbab',DATA+'model.json':'ae40c085c48dc44b7a7438b4c707f2c16408258d4501e855b151200ef1b6c995',DATA+'scope.json':'5e7e1ee1dd23e327609dde81a6a137f8efb46171b1d7eca9907b4f20058ca6e3',DATA+'summary.json':'224eb5e1d016bda6ac903de5c59ab489c1c3d4c0abdc5ecf342c97d4f2ea0a84','acceleration/native_20260930_count_interval.py':'60e378aaae9b250dc4eba3287e473e17a8417e52508d6d024d51681627008abc','acceleration/native_20260930_count_interval_spec.md':'6769423d47ed8fe9fcf2f7f8fc7a1315f79cbb35d6f77c3c673e0c5dfc471e60'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def values(a,n):
    need(len(a)==n and all(type(x)is int and 0<abs(x)<=n for x in a)and len({abs(x)for x in a})==n,'complete signed unique assignment')
    v=[False]*(n+1)
    for x in a:v[abs(x)]=x>0
    return v
def token(x,v):return x if type(x)is bool else v[abs(x)]==(x>0)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    try:
        for p,h in PINS.items():need(sha(ROOT/p)==h,'pin '+p);pins[p]=h
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=sha(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),limits=dict(cooperative_seconds=60,planning_memory_bytes=512*1024**2,native_calls=0)))
        a=read(ASS)['assignment'];v=values(a,155939)+[False]*(185963-155939);model=read(BASE+'model.json');profile=read(PROFILE);need(profile['profile_sha256']=='d2b0c89bb1d8f0d75b47f541603e952618cebe9b7ecccd8e1b2c23a279ac8dd9'and profile['exception_count']==8,'literal checked count profile')
        config=json.loads(gzip.decompress((ROOT/(INV+'configuration.json.gz')).read_bytes()));positions={}
        for d in model['group_domains']:
            selected=[i for i,x in enumerate(d['selectors'])if v[x]];need(len(selected)==1,'unique raw group choice');positions[d['group']]=selected[0]
        for c in config['channels']:v[c['variable']]=bool(int(c['selector_index_mask_hex'],16)>>positions[c['group']]&1)
        screens=[]
        for c in config['cells']:
            for rec in [c['lower_counter'],c['upper_counter']]:
                for r in rec['states']:v[r['id']]=token(r['q'],v)or(token(r['x'],v)and token(r['r'],v))
            lo=sum(token(x,v)for x in c['lower_inputs']);hi=sum(token(x,v)for x in c['upper_inputs']);need(lo<=c['target']<=hi,'literal interval count sums');screens.append(dict(cell=c['index'],coordinates=c['coordinates'],fibres=c['fibres'],lower=lo,target=c['target'],upper=hi))
        full=[i if v[i]else-i for i in range(1,len(v))];need(full[:155939]==sorted(a,key=abs),'all authentic base values unchanged');values(full,185963)
        changed=[config['channels'][0]['variable'],config['cells'][0]['lower_counter']['states'][0]['id'],config['cells'][-1]['upper_counter']['states'][-1]['id']];corrupt={x:None for x in changed};count=0
        with (ROOT/(DATA+'instance.cnf')).open('r',encoding='ascii')as f:
            need(next(f)==b'p cnf 185963 7659287\n'.decode(),'exact actual header')
            for line in f:
                c=list(map(int,line.split()));need(c and c[-1]==0 and all(0<abs(x)<=185963 for x in c[:-1]),'actual literal/terminator');c=c[:-1];count+=1;need(any(token(x,v)for x in c),'literal actual clause '+str(count))
                for x in changed:
                    if corrupt[x]is None and any(abs(t)==x for t in c):
                        if not any(token(t,v)^(abs(t)==x)for t in c):corrupt[x]=dict(clause_index=count,clause=c)
                if count%250000==0:need(time.monotonic()-start<60,'60-second allocation')
        need(count==7659287 and all(corrupt.values()),'all actual clauses and changed-bit rejections')
        for bad in [full[:-1],full[:-1]+[full[0]],full[:-1]+[185964]]:
            try:values(bad,185963)
            except ValueError:pass
            else:raise ValueError('malformed assignment accepted')
        save(out/'assignment.json',dict(assignment=full,construction='Authentic base assignment plus deterministic interval auxiliary extension.',native_output_fabricated=False,full_factor=False,target_graph=False));save(out/'all540_intervals.json',dict(records=screens,profile_sha256=profile['profile_sha256']));save(out/'count_profile.json',profile);save(out/'controls.json',dict(changed_auxiliary_clause_witnesses=corrupt,malformed_assignment_rejections=3,actual_clauses_checked=count))
        save(out/'prepared_native_unused.json',dict(wrapper_path='acceleration/native_20260930_count_interval.py',wrapper_sha256=PINS['acceleration/native_20260930_count_interval.py'],spec_path='acceleration/native_20260930_count_interval_spec.md',spec_sha256=PINS['acceleration/native_20260930_count_interval_spec.md'],preflight_calls=0,native_calls=0,reason='Root chose direct auxiliary extension of an already checked count witness after all540 intervals survived; no interval solver call is needed to construct this candidate.'))
        summary=dict(status='CANDIDATE_COUNT_INTERVAL_ASSIGNMENT_CONSTRUCTED',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},variables=185963,actual_clauses_checked=count,unchanged_base_variables=155939,new_OR_values=8244,new_prefix_values=21780,interval_cells_checked=540,exception_count=8,profile_sha256=profile['profile_sha256'],elapsed_seconds=time.monotonic()-start,native_calls=0,solver_calls=0,independent_approval=False,full_factor=False,target_graph=False,artifact_availability='LOCAL_ONLY');save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in ['inputs_sha256','outputs_sha256']}));print('summary_sha256',sha(out/'summary.json'))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins,elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
