"""Candidate exact fibre relabelling census; no producer AC imports or solver."""
from collections import Counter
from datetime import datetime,timezone
from itertools import permutations
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
ARC=B/'20260930_hadamard_six_profile_arc';DOM=B/'20260930_hadamard_six_profile_local_domains'
RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
FIX=B/'20260930_srg243_residual_fixture/triangle_blocks.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',DOM/'profiles.jsonl.gz':'221d913515ad8e8dedfbca6a9453b2dce1f538462bce1c7cb9f66b202a3bc2a0',B/'20260930_independent_review/hadamard_six_profile_local_domains/summary.json':'976e673b02c8742503a33d091e6ddf4650c13289e25fd859cb7854deb0174235',ARC/'inventory/inventory.json':'5f41560faa33278529e190babb3e2595f763de85d821998d055338bf6aea7255',ARC/'run01/summary.json':'44805fae16a3f988ac4fa575c1b38bb2a5f5121c5e7521e46f45990b8f83a9b1',ARC/'run01/checkpoint.json':'6e2f93b995b0d0ddc6e8afe0c3327761fe8eccea2929f04b4430314f438361f6',FIX:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',B/'20260930_independent_review/srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def gzread(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def gzsave(p,x):
    with Path(p).open('xb') as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as g:g.write(json.dumps(x,separators=(',',':')).encode()+b'\n')
def row_map(p,n=12):
    need(sorted(p)==[0,1,2],'fibre permutation');return [n*p[f]+a for f in range(3) for a in range(n)]
def invariant(m,p):return all(m[p[i]][p[j]]==m[i][j] for i in range(len(p)) for j in range(len(p)))
def profile_image(d,p):
    v=[[[0]*len(d[0][0]) for f in range(3)] for a in range(len(d))]
    for a in range(len(d)):
        for old,new in enumerate(p):v[a][new]=d[a][old][:]
    return v
def bit_image(mask,position_map):
    result=0
    while mask:
        low=mask&-mask;result|=1<<position_map[low.bit_length()-1];mask-=low
    return result
def masks_covary(source,target,left_map,right_map):
    need(len(source)==len(left_map) and len(target)==len(left_map),'relation row counts')
    for i,mask in enumerate(source):need(bit_image(mask,right_map)==target[left_map[i]],'exact relation covariance')
def controls(raw):
    rejected=[]
    for p in ((0,0,2),(0,1,3)):
        try:row_map(p)
        except ValueError:rejected.append('invalid_'+str(p))
        else:raise ValueError('invalid permutation accepted')
    bad=[r[:] for r in raw['core_adjacency']];bad[0][1]^=1;need(not invariant(bad,row_map((1,0,2))),'changed fixed core');rejected.append('changed_core')
    masks_covary([1,2],[2,1],[1,0],[0,1])
    try:masks_covary([1,2],[3,1],[1,0],[0,1])
    except ValueError:rejected.append('changed_relation_bit')
    else:raise ValueError('changed relation accepted')
    fixture=read(FIX);f=fixture['factor60x180'];c=fixture['cubic_core60'];d=fixture['residual180x180'];p=row_map((1,2,0),20);ip=[p.index(i) for i in range(60)];q=[(j//3)*3+(j+1)%3 for j in range(180)]
    nf=[[f[ip[i]][q[j]] for j in range(180)] for i in range(60)];nc=[[c[ip[i]][ip[j]] for j in range(60)] for i in range(60)];nd=[[d[q[i]][q[j]] for j in range(180)] for i in range(180)]
    rowbits=[sum(x<<j for j,x in enumerate(r)) for r in f];newbits=[sum(x<<j for j,x in enumerate(r)) for r in nf];dbits=[sum(nd[k][j]<<k for k in range(180)) for j in range(180)]
    need(all((newbits[i]&newbits[j]).bit_count()==(rowbits[ip[i]]&rowbits[ip[j]]).bit_count() for i in range(60) for j in range(60)),'genuine243 Gram covariance')
    need(all((newbits[i]&dbits[j]).bit_count()==2-nf[i][j]-sum(nc[i][k]*nf[k][j] for k in range(60)) for i in range(60) for j in range(180)),'genuine243 residual mixed identity after relabelling')
    return dict(genuine243_Gram_entries=3600,genuine243_mixed_entries=10800,rejected_controls=rejected,research99_positive=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for p,h in PINS.items():need(sha(p)==h,'input pin '+key(p))
        inputs={key(p):h for p,h in PINS.items()}
        for p in (Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_six_fibre_orbits_spec.md'),ROOT/'docs/DERIVATION_20260930_SIX_PROFILE_FIBRE_NORMALIZATION.md',ROOT/'uv.lock',ROOT/'pyproject.toml'):inputs[key(p)]=sha(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,cooperative_wall_seconds=120,solver_calls=0))
        raw=read(RAW);local=read(LOCAL);inv=read(ARC/'inventory/inventory.json');cp=read(ARC/'run01/checkpoint.json');summary=read(ARC/'run01/summary.json');need(summary['completion']=='COMPLETE','full candidate AC population')
        with gzip.open(DOM/'profiles.jsonl.gz','rt',encoding='utf-8') as f:profiles=[json.loads(line) for line in f]
        need(len(profiles)==len(cp['completed_profiles'])==984 and len(cp['completed_relations'])==12648,'frozen complete population');save(out/'controls.json',controls(raw))
        words=local['words'];triples=local['survivors'];word_index={tuple(w):i for i,w in enumerate(words)};triple_index={tuple(t):i for i,t in enumerate(triples)};actions=[]
        for tau in permutations(range(3)):
            rp=row_map(tau);need(invariant(raw['core_adjacency'],rp) and invariant(raw['prescribed_Gram36'],rp),'fixed literal matrices')
            wm=[word_index[tuple(tau[v] for v in w)] for w in words];tm=[];orders=[]
            for triple in triples:
                transformed=[wm[w] for w in triple];order=sorted(range(3),key=lambda j:transformed[j]);tm.append(triple_index[tuple(transformed[j] for j in order)]);orders.append(order)
            need(len(set(wm))==90 and len(set(tm))==31110,'word/triple bijections')
            # Actual literal local row and column mapping, all31110 triples.
            for old,ti in enumerate(tm):
                for j,k in enumerate(orders[old]):need([tau[v] for v in words[triples[old][k]]]==words[triples[ti][j]],'literal local image')
            actions.append(dict(fibre_old_to_new=list(tau),core_row_old_to_new=rp,word_map=wm,local_triple_map=tm,column_new_to_old=orders))
        wrong=actions[1]['local_triple_map'][0];need(wrong!=actions[1]['local_triple_map'][1],'distinct image corruption control');save(out/'local_image_control.json',dict(distinct_inputs=[0,1],actual_images=actions[1]['local_triple_map'][:2],altered_collision_rejected=True))
        gzsave(out/'local_actions.json.gz',actions)
        eps=inv['endpoints'];ep_lookup={(e['group'],tuple(e['local_survivor_indices'])):e['index'] for e in eps};ep_images=[]
        for action in actions:
            images=[];tm=action['local_triple_map']
            for ep in eps:
                target_ids=sorted(tm[i] for i in ep['local_survivor_indices']);target=ep_lookup[ep['group'],tuple(target_ids)];lookup={v:i for i,v in enumerate(eps[target]['local_survivor_indices'])};position=[lookup[tm[i]] for i in ep['local_survivor_indices']];need(sorted(position)==list(range(ep['count'])),'endpoint domain bijection');images.append(dict(target_endpoint=target,option_position_map=position))
            ep_images.append(images)
        gzsave(out/'endpoint_maps.json.gz',ep_images)
        relations=[]
        for ref in tqdm(cp['completed_relations'],desc='Authenticate relation inputs',mininterval=1):
            path=ROOT/ref['path'];need(sha(path)==ref['sha256'],'frozen relation hash');record=gzread(path);relations.append((record['endpoints'],[int(x,16) for x in record['gram_forward']],[int(x,16) for x in record['combined_forward']]))
        relation_lookup={tuple(r['endpoints']):r['index'] for r in inv['relations']};relation_images=[];entry_checks=0
        for ai,action in enumerate(tqdm(actions,desc='All six complete relation actions',mininterval=1)):
            mapped=[]
            for ri,(ends,gm,both) in enumerate(relations):
                le,re=(ep_images[ai][ep] for ep in ends);target=relation_lookup[le['target_endpoint'],re['target_endpoint']];target_record=relations[target]
                masks_covary(gm,target_record[1],le['option_position_map'],re['option_position_map']);masks_covary(both,target_record[2],le['option_position_map'],re['option_position_map']);mapped.append(target);entry_checks+=2*inv['relations'][ri]['option_pairs']
                if ri%256==0:need(time.monotonic()-start<120,'bounded relation census')
            need(len(set(mapped))==12648,'relation bijection');relation_images.append(mapped);save(out/f'action_{ai}_progress.json',dict(action=ai,relations=len(mapped),relation_entries_checked_so_far=entry_checks,elapsed_seconds=time.monotonic()-start))
        gzsave(out/'relation_maps.json.gz',relation_images)
        profile_lookup={p['profile_sha256']:i for i,p in enumerate(profiles)};ac_records=[]
        for ref in cp['completed_profiles']:
            path=ROOT/ref['path'];need(sha(path)==ref['sha256'],'frozen profile AC hash');ac_records.append(gzread(path))
        records=[];orbits={}
        for pi,p in enumerate(tqdm(profiles,desc='All six profile fixed-point actions',mininterval=1)):
            maps=[]
            for ai,action in enumerate(actions):
                image=profile_image(p['coordinate_fibre_deviations'],action['fibre_old_to_new']);target=profile_lookup[digest(dict(groups=p['group_ids'],deviations=image))];tp=profiles[target];need(tp['group_ids']==p['group_ids'],'group IDs unchanged');mapped_eps=[ep_images[ai][e]['target_endpoint'] for e in inv['profiles'][pi]['endpoints']];need(mapped_eps==inv['profiles'][target]['endpoints'],'profile domain images')
                for field in ('gram_ac','gram_caps_ac'):
                    a=ac_records[pi][field];b=ac_records[target][field];need(a['empty']==b['empty'],'classification covariance')
                    for side,e in enumerate(inv['profiles'][pi]['endpoints']):need(bit_image(int(a['final_masks'][side],16),ep_images[ai][e]['option_position_map'])==int(b['final_masks'][side],16),'entire fixed-point domain covariance')
                maps.append(target)
            rep=min(maps,key=lambda i:profiles[i]['id']);orbits.setdefault(rep,set()).add(pi);records.append(dict(index=pi,id=p['id'],profile_sha256=p['profile_sha256'],action_target_indices=maps,representative_index=rep,representative_id=profiles[rep]['id'],representative_action=maps.index(rep)))
            need(time.monotonic()-start<120,'bounded profile census')
        orbit_records=[]
        for rep,members in sorted(orbits.items(),key=lambda pair:profiles[pair[0]]['id']):
            need(set(records[rep]['action_target_indices'])==members,'complete orbit partition');r=cp['completed_profiles'][rep];orbit_records.append(dict(representative_index=rep,representative_id=profiles[rep]['id'],members=sorted(members),member_ids=[profiles[i]['id'] for i in sorted(members)],Gram_empty=r['gram_empty'],Gram_caps_empty=r['combined_empty']))
        gzsave(out/'profile_maps.json.gz',records);save(out/'orbits.json',dict(orbits=orbit_records,selection_rule='Lexicographically smallest raw profile ID per full six-action orbit.',normalization_not_yet_independently_approved=True))
        surviving=[o for o in orbit_records if not o['Gram_caps_empty']];need(surviving,'at least one candidate survivor');first=surviving[0];pi=first['representative_index'];save(out/'first_surviving_profile.json',dict(selection=first,profile=profiles[pi],arc_result_ref=cp['completed_profiles'][pi],scope='Literal profile selection only; orbit coverage remains CANDIDATE.'))
        result=dict(status='CANDIDATE_SIX_EXCEPTION_FIBRE_PROFILE_NORMALIZATION',inputs_sha256=inputs,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},profiles=984,fibre_actions=6,profile_images=5904,orbits=len(orbit_records),orbit_size_histogram=dict(Counter(len(o['members']) for o in orbit_records)),Gram_empty_orbits=sum(o['Gram_empty'] for o in orbit_records),Gram_caps_empty_orbits=sum(o['Gram_caps_empty'] for o in orbit_records),Gram_caps_surviving_orbits=len(surviving),all_relation_entry_images_checked=entry_checks,first_surviving_representative=first,elapsed_seconds=time.monotonic()-start,independent_approval=False,solver_calls=0,target_resolution=False,artifact_availability='LOCAL_ONLY',limitations=['AC exclusions require their separate independent audit.','Surviving representatives do not establish simultaneous choices or full factors.','Fixed six-prism Hadamard support only; no target automorphism is assumed.'])
        save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256')}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__)),complete=False));raise
if __name__=='__main__':main()
