"""Declared twelve singleton tests, reusing frozen exact block support kernel."""
import argparse,gzip,hashlib,importlib.util,json,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';BASE=B/'20260930_first_third_proof_obstructions';SOURCE=ROOT/'acceleration/theory_20260930_first_third_proof_obstructions.py'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def need(x,m):
    if not x:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def one(h,model,initial,choice,out,deadline):
    domains=[set(d) for d in initial];domains[16]={choice};blocks=h.derive_blocks(model);checks=0;sweep=0;removed=0;status='RUNNING'
    with (out/'checks.jsonl.gz').open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as f:
            while status=='RUNNING':
                sweep+=1;changed=False
                for bi,b in enumerate(blocks):
                    if time.perf_counter()>=deadline:status='PARTIAL_RESOURCE_BOUND';break
                    inputs=[sorted(domains[g]) for g in b['groups']];pops=[{b['projections'][i][k] for k in ks} for i,ks in enumerate(inputs)]
                    allowed,prefix,suffix=h.supports(pops,b['target']);changes=[]
                    for i,g in enumerate(b['groups']):
                        bad=[k for k in inputs[i] if b['projections'][i][k] not in allowed[i]]
                        if bad:changes.append(dict(group=g,removed=bad));domains[g].difference_update(bad)
                    r=dict(index=checks,sweep=sweep,block=bi,coordinates=b['coordinates'],groups=b['groups'],input_domains=inputs,projected_populations=[sorted(s) for s in pops],prefix=[sorted(s) for s in prefix],suffix=[sorted(s) for s in suffix],supported_vectors=[sorted(s) for s in allowed],changes=changes)
                    f.write((json.dumps(r,separators=(',',':'))+'\n').encode());checks+=1;n=sum(len(c['removed']) for c in changes);removed+=n;changed|=bool(n)
                    if any(not domains[g] for g in b['groups']):status='EMPTY_NECESSARY_DOMAIN';break
                if status=='RUNNING' and not changed:status='FIXED_POINT_UNRESOLVED'
    result=dict(status=status,condition=dict(group=16,choice_index=choice),sweeps=sweep,checks=checks,removed_options=removed,initial_domains=initial,final_domains=[sorted(d) for d in domains]);save(out/'summary.json',result)
    return {k:v for k,v in result.items() if k not in ['initial_domains','final_domains']}|dict(final_domain_sizes=list(map(len,domains)))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();deadline=start+60;pins={};results=[]
    def pin(p,s=None):
        actual=sha(p);need(s is None or actual==s,'identity '+key(p));pins[key(p)]=actual
    try:
        pin(SOURCE,'0aaefa897eeeeb8fed7cf193c1793ad5bffb239eeabd250f18db7d44c180d6ba');pin(BASE/'summary.json','018b134a4f6682e177ba4c95cb98a77036e4a05c42735608cd07dc53af2f1951');base=read(BASE/'summary.json')
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        sp=importlib.util.spec_from_file_location('frozen_block_kernel',SOURCE);h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h);save(out/'reused_controls.json',h.controls())
        for name,directory,_,_,_ in h.CASES:
            modelpath=B/directory/'model.json';pin(modelpath,base['inputs_sha256'][key(modelpath)]);model=read(modelpath)
            prior=BASE/name/'domain_propagation.json';pin(prior,base['outputs_sha256'][key(prior)]);initial=read(prior)['final_domains'];need(initial[16]==[54,55,56,90,91,92],'exact preregistered six choices')
            for choice in initial[16]:
                co=out/(name+'_'+str(choice));co.mkdir();r=one(h,model,initial,choice,co,deadline);r['profile']=name;results.append(r);print(json.dumps(r),flush=True)
                if time.perf_counter()>=deadline:break
            if time.perf_counter()>=deadline:break
        r=dict(status='CANDIDATE_DECLARED_SINGLETON_BLOCK_SCREEN',created_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.rglob('*') if p.is_file()},configured_wall_seconds=60,elapsed_seconds=time.perf_counter()-start,records=results,planned_cases=12,completed_cases=len([r for r in results if r['status']!='PARTIAL_RESOURCE_BOUND']),new_sat_calls=0,claim_status='CANDIDATE',scope='Two pinned literal profiles only; no broad profile or factor existence conclusion.')
        save(out/'summary.json',r);print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),elapsed_seconds=r['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex)));raise
if __name__=='__main__':main()
