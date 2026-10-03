"""Exact four-group joint enumeration, with immutable outer-choice chunks."""
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import argparse, gzip, hashlib, importlib.util, json, platform, subprocess, sys, time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
SCREEN=B/'20260930_hadamard_four_group_local_screen/summary.json'
RAW=B/'20260930_hadamard20_support/six_prism.json'
LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
HELPER=ROOT/'acceleration/theory_20260930_hadamard_four_group_local_screen.py'
PINS={SCREEN:'7773d527456ea88913a543a19d0d49c0b5c339f7dfdccddce604822682620b7d',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',HELPER:'2c1e1278b55c000689bea7cc0416163dc30067210bcb90ece80a4c4628b14072'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def indices(mask):
    while mask:
        bit=mask&-mask;yield bit.bit_length()-1;mask-=bit
def merge(left,right,diagonal_limits=None):
    if left['one']&right['one'] or left['double']&right['occ'] or right['double']&left['occ']:return None
    diagonal=[x+y for x,y in zip(left['diagonal'],right['diagonal'])]
    if any(x>limit for x,limit in zip(diagonal,diagonal_limits or [10]*len(diagonal))):return None
    return dict(one=left['one']|right['one'],occ=left['occ']|right['occ'],double=left['double']|right['double']|(left['occ']&right['occ']),diagonal=diagonal)
def controls(helper):
    base=helper.controls();toy1=dict(one=1,occ=2,double=0,diagonal=[1]*36);toy2=dict(one=4,occ=2,double=0,diagonal=[1]*36)
    two=merge(toy1,toy2);need(two is not None and two['double']==2,'two singles form double')
    three=dict(one=8,occ=2,double=0,diagonal=[1]*36);need(merge(two,three) is None,'three singles exceed cap2')
    need(merge(toy1,toy1) is None,'target1 collision')
    fixture=read(helper.FIXTURE)['factor60x180'];target=[[sum(fixture[i][d]*fixture[j][d] for d in range(180)) for j in range(60)] for i in range(60)]
    cols=[sum(fixture[i][d]<<i for i in range(60)) for d in range(24)];parts=[]
    for j in range(8):
        ft=helper.feature(cols[3*j:3*j+3],target);ft['diagonal']=[ft['counts'].get((i,i),0) for i in range(60)];parts.append(ft)
    for ids in combinations(range(8),4):
        state=parts[ids[0]]
        for j in ids[1:]:state=merge(state,parts[j],[target[i][i] for i in range(60)]);need(state is not None,'literal valid243 four-part merge')
        selected=[col for j in ids for col in parts[j]['columns']]
        need(all(sum(((col>>i)&1)&((col>>j)&1) for col in selected)<=target[i][j] for i in range(60) for j in range(i,60)),'243 literal joint Gram')
    return dict(shared_helper_controls=base,srg243_four_part_positive_controls=70,new_controls=['two_singles_to_double','third_single_rejected','target1_overlap_rejected'])
def first_witness(features,chosen,groups,gram):
    cols=[c for side,index in enumerate(chosen) for c in features[side][index]['columns']]
    factor=[[(c>>i)&1 for c in cols] for i in range(36)]
    contribution=[[sum(factor[i][d]*factor[j][d] for d in range(12)) for j in range(36)] for i in range(36)]
    residual=[[gram[i][j]-contribution[i][j] for j in range(36)] for i in range(36)]
    need(all(x>=0 for row in residual for x in row),'literal full joint Gram upper bound')
    need(all((x&y).bit_count()<=2 for x,y in combinations(cols,2)),'literal all66 partial column caps')
    pair_checks=[]
    for a,b in combinations(range(12),2):
        if b==(a^1):continue
        count=5-sum(a in s and b in s for s in groups)
        matrix=[[residual[12*f+a][12*g+b] for g in range(3)] for f in range(3)]
        need(all(sum(row)==count for row in matrix) and all(sum(matrix[f][g] for f in range(3))==count for g in range(3)),'automatic residual permutation margins')
        pair_checks.append(dict(coordinates=[a,b],remaining_groups=count,matrix=matrix))
    return dict(factor36x12=factor,residual_Gram36=residual,remaining_balanced_pair_margins=pair_checks,target_graph=False,completion_claim=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--resume',type=Path);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for path,digest in PINS.items():need(sha(path)==digest,'pin '+key(path))
        spec=importlib.util.spec_from_file_location('candidate_local_screen_feature_helpers',HELPER);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
        inputs={key(path):digest for path,digest in PINS.items()}
        for path in [ROOT/'acceleration/theory_20260930_hadamard_four_group_joint.py',ROOT/'acceleration/theory_20260930_hadamard_four_group_joint_spec.md',B/'20260930_hadamard_four_group_joint/failure.json']:inputs[key(path)]=sha(path)
        for path in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_four_group_joint_v2_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(path)]=sha(path)
        previous={}
        if args.resume:
            previous_summary=read(args.resume/'summary.json');need(previous_summary['inputs_sha256']==inputs,'resume source/input exact identity')
            for checkpoint in previous_summary['checkpoints']:
                cp=ROOT/checkpoint['path'];need(sha(cp)==checkpoint['sha256'],'resume checkpoint pin');rec=read(cp)
                for entry in rec['outputs']:need(sha(ROOT/entry['path'])==entry['sha256'],'resume chunk pin')
                previous[(rec['case'],rec['outer_index'])]=checkpoint
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,shared_components=['Frozen producer local-feature helper; not an independent checking path.'],limits=dict(seconds=120,native_solver_calls=0),resume=None if args.resume is None else str(args.resume)))
        save(out/'controls.json',controls(helper))
        screen=read(SCREEN);raw=read(RAW);local=read(LOCAL);gram=raw['prescribed_Gram36'];words=local['words'];triples=local['survivors']
        allgroups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)))
        todo=[r for r in screen['case_summaries'] if not r['gram_caps_ac_empty']];population=sum(__import__('math').prod(r['final_sizes']) for r in todo)
        checkpoints=[];case_results=[];stopped=False
        for record in tqdm(todo,desc='Joint four-group profiles',mininterval=1):
            path=ROOT/record['path'];need(sha(path)==record['sha256'],'saved profile bytes');case=read(path);case_index=case['case'];caseout=out/f'case_{case_index:03d}';caseout.mkdir()
            groups=[allgroups[g] for g in case['groups']];domains=case['local_survivor_indices'];masks=list(map(lambda x:int(x,16),case['gram_caps_ac']['final_masks']))
            features=[]
            for side,domain in enumerate(domains):
                sidefeatures=[]
                for index in domain:
                    cols=[sum(1<<(12*words[w][pos]+a) for pos,a in enumerate(groups[side])) for w in triples[index]]
                    ft=helper.feature(cols,gram);ft['diagonal']=[ft['counts'].get((i,i),0) for i in range(36)];sidefeatures.append(ft)
                features.append(sidefeatures)
            tables={(r['sides'][0],r['sides'][1]):list(map(lambda x:int(x,16),r['both_forward_masks'])) for r in case['pairs']}
            total_count=triple_count=four_count=0;witness_saved=False;outer_done=[]
            for i in indices(masks[0]):
                if (case_index,i) in previous:
                    cp=previous[(case_index,i)];checkpoints.append(cp);old=read(ROOT/cp['path']);total_count+=old['survivors'];triple_count+=old['compatible_triples'];four_count+=old['four_clique_candidates'];outer_done.append(i);witness_saved|=old['survivors']>0;continue
                if time.monotonic()-start>=120:stopped=True;break
                chunk=caseout/f'outer_{i:03d}.jsonl.gz';count=tc=fc=0
                with chunk.open('xb') as rawstream:
                    with gzip.GzipFile(filename='',mode='wb',fileobj=rawstream,mtime=0) as stream:
                        for j in indices(masks[1]&tables[(0,1)][i]):
                            first=merge(features[0][i],features[1][j]);need(first is not None,'pair table/merge agreement')
                            for k in indices(masks[2]&tables[(0,2)][i]&tables[(1,2)][j]):
                                second=merge(first,features[2][k])
                                if second is None:continue
                                tc+=1
                                for l in indices(masks[3]&tables[(0,3)][i]&tables[(1,3)][j]&tables[(2,3)][k]):
                                    fc+=1;merged=merge(second,features[3][l])
                                    if merged is None:continue
                                    chosen=[i,j,k,l];ids=[domains[s][chosen[s]] for s in range(4)]
                                    stream.write((json.dumps(dict(option_indices=chosen,local_survivor_indices=ids),separators=(',',':'))+'\n').encode());count+=1
                                    if not witness_saved:
                                        save(caseout/'first_witness.json',dict(case=case_index,groups=case['groups'],chosen=chosen,local_survivor_indices=ids,**first_witness(features,chosen,groups,gram)));witness_saved=True
                outputs=[dict(path=key(chunk),sha256=sha(chunk))]
                if (caseout/'first_witness.json').exists():outputs.append(dict(path=key(caseout/'first_witness.json'),sha256=sha(caseout/'first_witness.json')))
                cp=caseout/f'checkpoint_{i:03d}.json';save(cp,dict(case=case_index,outer_index=i,source_case_sha256=record['sha256'],compatible_triples=tc,four_clique_candidates=fc,survivors=count,outputs=outputs));checkpoints.append(dict(path=key(cp),sha256=sha(cp)));total_count+=count;triple_count+=tc;four_count+=fc;outer_done.append(i)
            complete=outer_done==list(indices(masks[0]));case_results.append(dict(case=case_index,complete=complete,outer_done=outer_done,cartesian_population=__import__('math').prod(m.bit_count() for m in masks),compatible_triples=triple_count,four_clique_candidates=four_count,surviving_partial_objects=total_count,status='COMPLETE' if complete else 'UNKNOWN_RESOURCE_LIMIT'))
            save(caseout/'summary.json',case_results[-1])
            if stopped:break
        summary=dict(status='CANDIDATE_JOINT_FOUR_GROUP_COMPLETE' if not stopped else 'CANDIDATE_JOINT_FOUR_GROUP_PARTIAL',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,checkpoints=checkpoints,case_results=case_results,selected_profiles=len(todo),cartesian_population=population,completed_profiles=sum(r['complete'] for r in case_results),unattempted_profiles=len(todo)-len(case_results),complete_empty_profiles=sum(r['complete'] and r['surviving_partial_objects']==0 for r in case_results),profiles_with_partial_object=sum(r['surviving_partial_objects']>0 for r in case_results),surviving_partial_objects=sum(r['surviving_partial_objects'] for r in case_results),elapsed_seconds=time.monotonic()-start,native_solver_calls=0,independent_approval=False,target_resolution=False,scope='Twelve-column partial objects only; no remaining48-column realization or full factor. Cases incomplete at deadline are UNKNOWN.')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','checkpoints','case_results')}))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
