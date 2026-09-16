"""Native mode parity, reproducibility, and atomic-family corruption controls."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess

from audit_atomic_cycle_family import audit, digest, key
from audit_certificate import full_graph, require

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260916_atomic_cycle_qa'
EXE=ROOT/'acceleration/build/overlap_cycle_neighbors.exe'


def read(path):
    return json.loads(path.read_bytes())


def run(input_path, output, mode=None):
    args=[str(EXE),str(input_path),str(output)]
    if mode is not None: args.append(mode)
    return subprocess.run(args,capture_output=True,text=True,timeout=30)


def semantic(data):
    result=deepcopy(data);result.pop('elapsed_seconds');return result


def main():
    require(not (OUT/'qa.json').exists(),'Preserve prior QA')
    candidate_path=ROOT/'acceleration/results/20260916_two_trade_pilot/best_candidate.json'
    candidate=read(candidate_path);both=read(OUT/'both.json')
    mode_paths=[];mode_counts={}
    for mode in ('3','4','both'):
        path=OUT/f'mode_{mode}.json';require(not path.exists(),'Preserve mode output')
        require(run(OUT/'input.txt',path,mode).returncode==0,'Native mode failed')
        output=read(path)
        if mode=='both': require(semantic(output)==semantic(both),'Native run not deterministic')
        else:
            size=int(mode);indices=[i for i,m in enumerate(both['moves']) if m['cycle_size']==size]
            require(output['moves']==[both['moves'][i] for i in indices],'Move mode subset differs')
            require(output['overlap_candidates']==[both['overlap_candidates'][i] for i in indices],'Candidate mode subset differs')
            require(output['by_class']==[c for c in both['by_class'] if c['cycle_size']==size],'Count mode subset differs')
            require(output['raw_cycles']==sum(c['raw_cycles'] for c in output['by_class']) and output['legal_cycles']==len(indices),'Mode total mismatch')
        mode_counts[mode]={'raw':output['raw_cycles'],'legal':output['legal_cycles'],'seconds':output['elapsed_seconds']}
        mode_paths.append(path)
    default_path=OUT/'mode_default.json';require(not default_path.exists(),'Preserve default output')
    require(run(OUT/'input.txt',default_path).returncode==0,'Default mode failed')
    require(semantic(read(default_path))==semantic(read(OUT/'mode_3.json')),'Default differs from mode3')

    controls=[];tokens=(OUT/'input.txt').read_text(encoding='ascii').split();mutations={}
    t=tokens.copy();t[0]='BAD';mutations['bad_header']=t
    t=tokens.copy();t[1]='2';mutations['wrong_candidate_count']=t
    t=tokens.copy();t[2:4]=t[4:6];mutations['duplicate_edge']=t
    t=tokens.copy();t[2]='-1';mutations['negative_endpoint']=t
    t=tokens.copy();t[3]='84';mutations['range_endpoint']=t
    t=tokens.copy();t[2:4]=['0','1'];mutations['same_fibre_edge']=t
    t=tokens.copy();t.pop();mutations['missing_endpoint']=t
    t=tokens.copy();t.append('0');mutations['trailing_token']=t
    for name,t in mutations.items():
        path=OUT/(name+'.txt');require(not path.exists(),'Preserve bad input');path.write_text(' '.join(t)+'\n',encoding='ascii')
        output=OUT/(name+'_must_not_exist.json');result=run(path,output,'both')
        require(result.returncode!=0 and not output.exists(),'Invalid input accepted '+name)
        controls.append(dict(name=name,rejected=True,message=result.stderr.strip()))
    for mode in ('2','5','BOTH'):
        output=OUT/('invalid_mode_'+mode+'_must_not_exist.json');result=run(OUT/'input.txt',output,mode)
        require(result.returncode!=0 and not output.exists(),'Invalid cycle size accepted')
        controls.append(dict(name='invalid_mode_'+mode,rejected=True,message=result.stderr.strip()))
    before=digest(OUT/'both.json');result=run(OUT/'input.txt',OUT/'both.json','3')
    require(result.returncode!=0 and before==digest(OUT/'both.json'),'Existing output overwritten')
    controls.append(dict(name='existing_output',rejected=True,message=result.stderr.strip()))

    # A separate declared-completeness check must reject omission/duplication,
    # while metadata and explicit cycle encodings are independently checked.
    small=read(OUT/'mode_3.json');corruptions={}
    x=deepcopy(small);x['moves'].pop();x['overlap_candidates'].pop();corruptions['omitted_move']=x
    x=deepcopy(small);x['moves'][1]=deepcopy(x['moves'][0]);x['overlap_candidates'][1]=deepcopy(x['overlap_candidates'][0]);corruptions['duplicate_move']=x
    x=deepcopy(small);x['moves'][0]['root_group']=(x['moves'][0]['root_group']+1)%7;corruptions['wrong_class']=x
    x=deepcopy(small);x['moves'][0]['alternating_cycle'][0]=x['moves'][0]['alternating_cycle'][1];corruptions['invalid_cycle']=x
    proof_controls=[]
    for name,corrupted in corruptions.items():
        try: audit(candidate,corrupted)
        except ValueError as e: proof_controls.append(dict(name=name,rejected=True,message=str(e)))
        else: raise ValueError('Independent audit accepted '+name)

    sources=[Path(__file__),ROOT/'acceleration/overlap_cycle_neighbors.rs',EXE,
             ROOT/'acceleration/audit_atomic_cycle_family.py',ROOT/'acceleration/audit_certificate.py',
             candidate_path,OUT/'input.txt',OUT/'both.json',OUT/'both_audit.json',default_path]+mode_paths
    report=dict(status='ATOMIC_CYCLE_NATIVE_QA_PASS',inputs_sha256={key(p):digest(p) for p in sources},
                modes=mode_counts,deterministic=True,default_is_three=True,complete_independent_audit=key(OUT/'both_audit.json'),
                native_negative_controls=controls,independent_audit_negative_controls=proof_controls,
                schema=dict(root_group='0..6',matching_class=['same_0','same_1','cross'],cycle_size=[3,4],
                            alternating_cycle='2k distinct zero-based outer vertices; removed edges at (0,1),(2,3),...; added at (1,2),(3,4),...,(2k-1,0); no repeated closure'),
                scope='Complete only for the declared single-matching alternating-cycle subfamily; no intermediate-state, star-domain, pair-AC or graph-completion claim.')
    (OUT/'qa.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('inputs_sha256','native_negative_controls','independent_audit_negative_controls','schema')}))


if __name__=='__main__': main()
