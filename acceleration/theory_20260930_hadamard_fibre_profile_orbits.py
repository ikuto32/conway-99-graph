"""Exact global fibre relabelling, candidate normalization; no solver."""
from pathlib import Path
from datetime import datetime,timezone
from itertools import permutations
from collections import Counter
import argparse,hashlib,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json'
LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json'
SCREEN=B/'20260930_hadamard_four_group_local_screen'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',SCREEN/'summary.json':'7773d527456ea88913a543a19d0d49c0b5c339f7dfdccddce604822682620b7d'}
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def h(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,obj):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def need(ok,msg):
    if not ok:raise ValueError(msg)
def rows(tau):
    need(sorted(tau)==[0,1,2],'fibre permutation')
    return [12*tau[f]+a for f in range(3)for a in range(12)]
def invariant(matrix,perm):return all(matrix[perm[a]][perm[b]]==matrix[a][b]for a in range(36)for b in range(36))
def profile(p,tau):
    result=[]
    for row in p:
        v=[None]*3
        for old,new in enumerate(tau):v[new]=row[old]
        result.append(v)
    return result
def sig(c):return tuple(c['groups']),tuple(tuple(v)for v in c['profile'])
def mask_ids(c,side):return {c['local_survivor_indices'][side][i]for i in range(len(c['local_survivor_indices'][side]))if int(c['gram_caps_ac']['final_masks'][side],16)>>i&1}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    try:
        for p,sha in PINS.items():need(h(p)==sha,'input hash');pins[key(p)]=sha
        raw=read(RAW);local=read(LOCAL);summary=read(SCREEN/'summary.json')
        need(summary['completed_cases']==108,'complete frozen input universe')
        words=local['words'];word_ids={tuple(w):i for i,w in enumerate(words)}
        triples=local['survivors'];need(len(words)==90 and len(triples)==31110,'local population')
        # Saved local catalogue uses triples of word indices.
        triple_ids={tuple(t):i for i,t in enumerate(triples)}
        cases=[]
        for i in range(108):
            p=SCREEN/f'case_{i:03d}.json';need(h(p)==summary['outputs_sha256'][key(p)],'case hash');pins[key(p)]=h(p);cases.append(read(p))
        lookup={sig(c):c['case']for c in cases};need(len(lookup)==108,'unique profiles')
        taus=list(permutations(range(3)));maps=[];rowchecks=[]
        for tau in taus:
            perm=rows(tau)
            need(invariant(raw['core_adjacency'],perm)and invariant(raw['prescribed_Gram36'],perm),'fixed core/Gram invariance')
            wm=[word_ids[tuple(tau[x]for x in w)]for w in words];need(len(set(wm))==90,'word bijection')
            tm=[triple_ids[tuple(sorted(wm[x]for x in t))]for t in triples];need(len(set(tm))==31110,'triple bijection')
            maps.append(tm);rowchecks.append(dict(tau=tau,rows=perm,word_map=wm))
        records=[];orbits={};relation_entries=0
        for c in tqdm(cases,desc='fibre profile maps'):
            need(time.perf_counter()-start<120,'120-second resource bound')
            actions=[lookup[(tuple(c['groups']),tuple(tuple(v)for v in profile(c['profile'],tau)))]for tau in taus]
            need(len(set(actions))==6,'free action on each nonzero profile')
            rep=min(actions);j=actions.index(rep);target=cases[rep];tm=maps[j];orbits.setdefault(rep,set()).add(c['case'])
            positionmaps=[]
            for side in range(4):
                domain=c['local_survivor_indices'][side];other=target['local_survivor_indices'][side];inv={t:i for i,t in enumerate(other)}
                need({tm[t]for t in domain}==set(other),'domain equivariance')
                need({tm[t]for t in mask_ids(c,side)}==mask_ids(target,side),'AC domain equivariance')
                positionmaps.append([inv[tm[t]]for t in domain])
            targets={tuple(r['sides']):r for r in target['pairs']}
            for r in c['pairs']:
                left,right=r['sides'];tr=targets[(left,right)];lp,rp=positionmaps[left],positionmaps[right]
                for field in ['gram_forward_masks','both_forward_masks']:
                    for i,encoded in enumerate(r[field]):
                        bits=int(encoded,16);otherbits=int(tr[field][lp[i]],16)
                        for k,q in enumerate(rp):need((bits>>k&1)==(otherbits>>q&1),'pair relation equivariance');relation_entries+=1
            records.append(dict(case=c['case'],representative=rep,tau=taus[j],orbit_actions=actions,local_position_maps=positionmaps,screen_empty=c['gram_caps_ac']['empty']))
            with(out/'progress.jsonl').open('a',encoding='utf8')as f:f.write(json.dumps(dict(completed=len(records),elapsed_seconds=time.perf_counter()-start))+'\n')
        need(all(len(v)==6 for v in orbits.values()),'complete size-six orbits')
        rejected=[]
        for tau in [(0,0,2),(0,1,3)]:
            try:rows(tau)
            except ValueError:rejected.append(list(tau))
            else:raise ValueError('invalid permutation accepted')
        bad=[r[:]for r in raw['core_adjacency']];bad[0][1]^=1
        need(not invariant(bad,rows((1,0,2))),'perturbed core rejected')
        save(out/'maps.json',dict(fibre_actions=rowchecks,local_triple_maps=maps,case_maps=records,orbits=[dict(representative=k,members=sorted(v),screen_empty=cases[k]['gram_caps_ac']['empty'])for k,v in sorted(orbits.items())]))
        save(out/'controls.json',dict(invalid_permutations_rejected=rejected,perturbed_core_rejected=True))
        for p in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=h(p)
        result=dict(status='CANDIDATE_GLOBAL_FIBRE_PROFILE_NORMALIZATION',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):h(p)for p in out.iterdir()if p.is_file()},cases=108,permutations=6,orbits=len(orbits),screen_survivor_orbits=sum(not cases[k]['gram_caps_ac']['empty']for k in orbits),screen_empty_orbits=sum(cases[k]['gram_caps_ac']['empty']for k in orbits),relation_entries_checked=relation_entries,independent_approval=False,solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start,scope='Label-normalization on one literal fixed core/support, not an automorphism assumption of a target. Prior screen exclusions require separate independent verification.')
        save(out/'summary.json',result);print(json.dumps({k:result[k]for k in['status','orbits','screen_survivor_orbits','elapsed_seconds']}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=h(Path(__file__))));raise
if __name__=='__main__':main()

