"""Independent dense seven-profile covariance and normalization audit."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from itertools import permutations
from pathlib import Path
import argparse, gzip, hashlib, json, platform, subprocess, sys, time, traceback
import numpy as np
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
PROD=B+'hadamard_seven_fibre_orbits/';ARC=B+'hadamard_seven_profile_arc_v2/';DOM=B+'hadamard_seven_profile_local_domains/'
RAW=B+'hadamard20_support/six_prism.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json'
HELPER='acceleration/audit_20260930_hadamard_six_fibre_orbits.py';HELPER_HASH='29bbf8d32ea579a54beedfc87fc761ebbce01753386b7bc9df63b674b77243c2'
if hashlib.sha256((ROOT/HELPER).read_bytes()).hexdigest()!=HELPER_HASH:raise ValueError('independent helper source changed')
from audit_20260930_hadamard_six_fibre_orbits import bits, relation, covariance, controls, psig

def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def gz(p):
    with gzip.open(ROOT/p,'rt',encoding='utf-8')as f:return json.load(f)
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def mask_covariance(a,b,mapping):
    need(sorted(mapping)==list(range(len(a)))and len(a)==len(b),'final-domain index bijection')
    need(np.array_equal(a,b[mapping]),'entire final-domain image')
def directed_images(source,target,relation_images):
    expected_pairs=[(l,r)for l in range(7)for r in range(l+1,7)]
    need([tuple(p['sides'])for p in source['pairs']]==expected_pairs and [tuple(p['sides'])for p in target['pairs']]==expected_pairs,'all21 unordered profile pairs')
    records=[]
    for a,b in zip(source['pairs'],target['pairs']):
        l,r=a['sides'];need(a['sides']==b['sides']and relation_images[a['relation']]==b['relation'],'directed relation source/target identity')
        records.extend([[l,r,a['relation'],b['relation']],[r,l,a['relation'],b['relation']]])
    need({tuple(r[:2])for r in records}=={(l,r)for l in range(7)for r in range(7)if l!=r},'exact42 directed arcs')
    return records

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        if p not in pins:pins[p]=sha(ROOT/p)
        need(h is None or h==pins[p],'input hash '+p)
    try:
        pin(PROD+'summary.json','c0be7200a63b851d979454f2a106b20de6376996afe9ba72875bb69c59844fc8');summary=read(PROD+'summary.json')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(p,h)
        pin(HELPER,HELPER_HASH)
        acgatepath=I+'hadamard_seven_profile_arc/summary.json';pin(acgatepath,'eeb0a947e6dde99c65578c6de323951f6c6654fdafeb31b22d053e117e84467d');acgate=read(acgatepath)
        need(acgate['status']=='INDEPENDENT_SEVEN_EXCEPTION_PROFILE_ARC_SCREEN_PASS','separate complete AC correctness premise')
        outcomespath=I+'hadamard_seven_profile_arc/profile_outcomes.json';pin(outcomespath,acgate['outputs_sha256'][outcomespath]);outcomes=read(outcomespath)['records']
        cbpath=I+'hadamard_seven_profile_arc/claim_binding.json';pin(cbpath,acgate['outputs_sha256'][cbpath]);acclaim=read(cbpath);need(acclaim['revision']==1 and acclaim['status']=='VERIFIED'and acclaim['review_state']=='CLEAR','exact AC premise revision')
        localgatepath=I+'hadamard_seven_profile_local_domains/summary.json';localgate=read(localgatepath);need(localgate['status']=='INDEPENDENT_SEVEN_EXCEPTION_LOCAL_DOMAIN_FILTER_PASS','complete initial domains independently reviewed')
        raw=read(RAW);local=read(LOCAL);inv=read(ARC+'inventory/inventory.json');cp=read(ARC+'run02/checkpoint.json')
        with gzip.open(ROOT/(DOM+'profiles.jsonl.gz'),'rt',encoding='utf-8')as f:profiles=[json.loads(line)for line in f]
        need(len(profiles)==len(cp['completed_profiles'])==1608 and len(inv['endpoints'])==2016 and len(cp['completed_relations'])==len(inv['relations'])==24732,'frozen complete populations')
        need([r['id']for r in outcomes]==[p['id']for p in profiles]and [r['index']for r in outcomes]==list(range(1608)),'independent AC labels cover same literal population')
        need(acgate['inputs_sha256'][DOM+'profiles.jsonl.gz']==pins[DOM+'profiles.jsonl.gz']and acgate['inputs_sha256'][ARC+'inventory/inventory.json']==pins[ARC+'inventory/inventory.json'],'AC/profile inventory shared identity')
        calibrated=controls(raw);save(out/'base_controls.json',calibrated)
        C=np.array(raw['core_adjacency'],dtype=np.int64);G=np.array(raw['prescribed_Gram36'],dtype=np.int64)
        need(np.array_equal(G,12*np.eye(36,dtype=np.int64)+2-np.array([[int(i//12==j//12)for j in range(36)]for i in range(36)])-C-C@C),'raw prescribed Gram from literal core')
        words=local['words'];triples=local['survivors'];word_index={tuple(w):i for i,w in enumerate(words)};triple_index={tuple(t):i for i,t in enumerate(triples)};actions=[];savedactions=gz(PROD+'local_actions.json.gz')
        for ai,tau in enumerate(permutations(range(3))):
            row_image=[12*tau[f]+a for f in range(3)for a in range(12)]
            need(np.array_equal(C,C[np.ix_(row_image,row_image)])and np.array_equal(G,G[np.ix_(row_image,row_image)]),'fixed literal core/Gram under all six row bijections')
            wordmap=[word_index[tuple(tau[f]for f in w)]for w in words];triplemap=[];orders=[]
            for triple in triples:
                transformed=[tuple(tau[f]for f in words[w])for w in triple];sortedwords=sorted(transformed);order=[transformed.index(w)for w in sortedwords];target=triple_index[tuple(word_index[w]for w in sortedwords)]
                need([[tau[f]for f in words[triple[k]]]for k in order]==[words[w]for w in triples[target]],'literal columns of every triple')
                triplemap.append(target);orders.append(order)
            need(sorted(wordmap)==list(range(90))and sorted(triplemap)==list(range(31110)),'complete word/triple bijections')
            record=dict(fibre_old_to_new=list(tau),core_row_old_to_new=row_image,word_map=wordmap,local_triple_map=triplemap,column_new_to_old=orders);need(record==savedactions[ai],'all raw local action fields');actions.append(record)
        action_index={tuple(a['fibre_old_to_new']):i for i,a in enumerate(actions)};group_law=[]
        for a in actions:
            row=[]
            for b in actions:
                k=action_index[tuple(a['fibre_old_to_new'][b['fibre_old_to_new'][f]]for f in range(3))];row.append(k)
                need([a['word_map'][j]for j in b['word_map']]==actions[k]['word_map']and [a['local_triple_map'][j]for j in b['local_triple_map']]==actions[k]['local_triple_map'],'all36 composition identities')
            group_law.append(row)
        need(read(PROD+'group_law.json')['composition_table']==group_law,'saved group law')
        eps=inv['endpoints'];need([e['index']for e in eps]==list(range(2016)),'complete indexed endpoint domain universe');lookup={(e['group'],frozenset(e['local_survivor_indices'])):e['index']for e in eps};need(len(lookup)==2016,'unique raw endpoints')
        domains={}
        for e in eps:
            pin(e['domain_path'],e['domain_sha256']);d=read(e['domain_path']);domains[e['domain_path']]=d
            need(d['local_survivor_indices']==e['local_survivor_indices']and d['count']==e['count'],'full initial-domain list, no AC replacement')
            need(localgate['inputs_sha256'][e['domain_path']]==e['domain_sha256'],'previous complete local-domain audit identity')
        for pi,p in enumerate(profiles):
            ip=inv['profiles'][pi];need(ip['index']==pi and ip['id']==p['id']and ip['profile_sha256']==p['profile_sha256']and ip['groups']==p['group_ids'],'literal profile inventory')
            need(len(ip['endpoints'])==len(p['local_domains'])==7,'all seven domains')
            for ei,ref in zip(ip['endpoints'],p['local_domains']):
                e=eps[ei];need(e['group']==ref['group']and e['count']==ref['count']and e['domain_sha256']==ref['sha256']and e['domain_path']==ref['path'],'complete profile endpoint reference')
        endpointmaps=[];savedep=gz(PROD+'endpoint_maps.json.gz')
        for ai,a in enumerate(actions):
            images=[]
            for e in eps:
                targetlist=[a['local_triple_map'][t]for t in e['local_survivor_indices']];target=lookup[e['group'],frozenset(targetlist)];positions=[eps[target]['local_survivor_indices'].index(t)for t in targetlist]
                need(sorted(positions)==list(range(e['count'])),'entire local-domain permutation');images.append(dict(target_endpoint=target,option_position_map=positions))
            need(images==savedep[ai],'all recorded endpoint maps');endpointmaps.append(images)
        matrices=[]
        for ri,ref in enumerate(tqdm(cp['completed_relations'],desc='Authenticate seven-profile relations',mininterval=1)):
            pin(ref['path'],ref['sha256']);r=gz(ref['path']);ends=inv['relations'][ri]['endpoints'];need(ref['index']==r['index']==ri and r['endpoints']==ends,'every exact relation identity');n,m=[eps[e]['count']for e in ends]
            matrices.append((relation(r,'gram_forward',n,m),relation(r,'combined_forward',n,m)))
        rel_lookup={tuple(r['endpoints']):r['index']for r in inv['relations']};savedrel=gz(PROD+'relation_maps.json.gz');relationmaps=[];entrycount=0
        for ai in tqdm(range(6),desc='Complete dense covariance',mininterval=1):
            images=[]
            for ri,r in enumerate(inv['relations']):
                le,re=[endpointmaps[ai][e]for e in r['endpoints']];target=rel_lookup[le['target_endpoint'],re['target_endpoint']];images.append(target)
                for k in(0,1):covariance(matrices[ri][k],matrices[target][k],le['option_position_map'],re['option_position_map']);entrycount+=matrices[ri][k].size
            need(images==savedrel[ai]and sorted(images)==list(range(24732)),'complete saved relation permutations');relationmaps.append(images)
            save(out/f'action_{ai}_progress.json',dict(completed_actions=ai+1,relation_entries_checked=entrycount,elapsed_seconds=time.perf_counter()-start))
        ac=[];maskarrays=[]
        for pi,ref in enumerate(cp['completed_profiles']):
            pin(ref['path'],ref['sha256']);r=gz(ref['path']);need(r['index']==pi and r['id']==profiles[pi]['id']and r['profile_sha256']==profiles[pi]['profile_sha256']and r['endpoint_indices']==inv['profiles'][pi]['endpoints'],'all completed AC records identified')
            need(r['gram_ac']['empty']==outcomes[pi]['gram_pair_empty']and r['gram_caps_ac']['empty']==outcomes[pi]['combined_empty'],'separate audited AC classifications')
            ac.append(r);maskarrays.append({field:[bits(mask,eps[e]['count'])for mask,e in zip(r[field]['final_masks'],r['endpoint_indices'])]for field in ['gram_ac','gram_caps_ac']})
        profilelookup={psig(p):i for i,p in enumerate(profiles)};need(len(profilelookup)==1608,'unique full profile arrays');pm=[];orbits=defaultdict(set);savedarcs=gz(PROD+'directed_arc_maps.json.gz');directedcount=0
        for pi,p in enumerate(tqdm(profiles,desc='All profile and directed-arc images',mininterval=1)):
            destinations=[];profilearcs=[]
            for ai,a in enumerate(actions):
                tau=a['fibre_old_to_new'];delta=[[row[tau.index(f)]for f in range(3)]for row in p['coordinate_fibre_deviations']];target=profilelookup[(tuple(p['group_ids']),tuple(x for row in delta for f in row for x in f))];destinations.append(target)
                mappedends=[endpointmaps[ai][e]['target_endpoint']for e in inv['profiles'][pi]['endpoints']];need(mappedends==inv['profiles'][target]['endpoints'],'all profile domains mapped')
                for field in ['gram_ac','gram_caps_ac']:
                    need(ac[pi][field]['empty']==ac[target][field]['empty'],'audited classification covariance')
                    for side,e in enumerate(inv['profiles'][pi]['endpoints']):mask_covariance(maskarrays[pi][field][side],maskarrays[target][field][side],endpointmaps[ai][e]['option_position_map'])
                arcs=directed_images(inv['profiles'][pi],inv['profiles'][target],relationmaps[ai]);directedcount+=42*2;profilearcs.append(dict(action=ai,target_profile=target,mapped_endpoints=mappedends,directed_relation_images=arcs))
            need(savedarcs[pi]==dict(index=pi,actions=profilearcs),'every saved directed arc record')
            need(len(set(destinations))==6,'six distinct fibre images');rep=min(destinations,key=lambda x:profiles[x]['id']);orbits[rep].add(pi)
            pm.append(dict(index=pi,id=p['id'],profile_sha256=p['profile_sha256'],action_target_indices=destinations,representative_index=rep,representative_id=profiles[rep]['id'],representative_action=destinations.index(rep)))
        need(pm==gz(PROD+'profile_maps.json.gz'),'all9648 profile image records');orbitrecords=[]
        for rep,members in sorted(orbits.items(),key=lambda pair:profiles[pair[0]]['id']):
            need(members==set(pm[rep]['action_target_indices']),'complete six-element orbit partition')
            orbitrecords.append(dict(representative_index=rep,representative_id=profiles[rep]['id'],members=sorted(members),member_ids=[profiles[x]['id']for x in sorted(members)],Gram_empty=outcomes[rep]['gram_pair_empty'],Gram_caps_empty=outcomes[rep]['combined_empty']))
        need(orbitrecords==read(PROD+'orbits.json')['orbits']and len(orbits)==268,'complete literal268 orbit census')
        need(entrycount==37784232*12 and directedcount==1608*6*42*2,'defined exact matrix/directed image counts')
        empty=sum(r['Gram_caps_empty']for r in orbitrecords);first=next((r for r in orbitrecords if not r['Gram_caps_empty']),None);savedfirst=read(PROD+'first_surviving_profile.json');need(first==savedfirst['selection'],'first-surviving literal selection')
        need(empty==52 and sum(r['Gram_empty']for r in orbitrecords)==46 and sum(r['combined_empty']for r in outcomes)==312,'independently audited counts in orbit units')
        save(out/'independent_orbits.json',dict(orbits=orbitrecords,classification_scope='Exclusion labels use the separately authenticated independent AC gate; this normalization audit establishes reversible covariance and complete orbit coverage.'))
        fresh=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,IndexError,KeyError):fresh.append(name);return
            raise ValueError('corruption accepted '+name)
        bad=matrices[0][0].copy();bad[0,0]^=1;reject('actual_relation_bit',lambda:covariance(bad,matrices[0][0],list(range(bad.shape[0])),list(range(bad.shape[1]))))
        sample=np.array([0,1,1],dtype=np.uint8);reject('changed_domain_member',lambda:mask_covariance(sample,np.array([1,1,1],dtype=np.uint8),[0,1,2]));reject('duplicate_domain_image',lambda:mask_covariance(sample,sample,[0,0,2]))
        bad=deepcopy(inv['profiles'][0]);bad['pairs'][0]['relation']=24732;reject('directed_relation_outside_universe',lambda:directed_images(inv['profiles'][0],bad,relationmaps[0]))
        bad=deepcopy(inv['profiles'][0]);bad['pairs'][0]['sides']=[0,0];reject('missing_directed_pair',lambda:directed_images(inv['profiles'][0],bad,relationmaps[0]))
        def first_surv(records):return next((r for r in records if not r['Gram_caps_empty']),None)
        need(first_surv([])is None and first_surv([dict(Gram_caps_empty=True)])is None and first_surv([dict(Gram_caps_empty=True),dict(Gram_caps_empty=False)])==dict(Gram_caps_empty=False),'empty/nonempty selection controls')
        save(out/'fresh_controls.json',dict(rejected_corruptions=fresh,base_controls_shared_source=HELPER,zero_survivor_positive=True,no_positive99_factor=True))
        save(out/'counts.json',dict(local_word_images=540,local_triple_images=186660,group_composition_word_checks=3240,group_composition_triple_checks=1119960,endpoint_images=12096,relation_images=148392,dense_relation_entry_images=entrycount,profile_images=9648,directed_arc_predicate_images=directedcount,complete_directed_arcs_per_profile_action=42,distinct_profiles=1608,orbits=268,first_predicate_empty_profiles=276,combined_empty_profiles=312,nonempty_profiles=1296,first_predicate_empty_orbits=46,combined_empty_orbits=52,nonempty_orbits=216,classification_scope='Both predicates require within-group caps in the initial domains. Nonempty does not imply a simultaneous choice or factor.'))
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_HADAMARD_SEVEN_FIBRE_ORBITS.md','uv.lock','pyproject.toml']:pin(p)
        ts=datetime.now(timezone.utc).isoformat();save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-SEVEN-EXCEPTION-FIBRE-NORMALIZATION',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='On the pinned six-prism Hadamard support, the six global fibre relabellings followed by within-group equal-support column reorderings are reversible bijections of the full factor and residual-completion families. They preserve the fixed core, prescribed Gram and all column/mixed caps, transport all1608 frozen exactly-seven-exception profiles into268 size-six orbits, and give the recorded complete domain/relation/fixed-point covariance. The separately independently checked AC classifications form46 first-predicate-empty orbits,52 combined-empty orbits and216 combined-nonempty orbits.',scope='Exactly the frozen1608-profile fixed-support universe and all its six relabellings. Both AC predicates start with within-group-cap-filtered domains. No simultaneous factor existence or whole-support/target conclusion.',assumptions=['Pinned raw fixed core/support, complete local-profile/domain universe and separately independently checked AC records.'],dependencies=[dict(id='C-FIXED-HADAMARD-SEVEN-EXCEPTION-LOCAL-DOMAIN-FILTER',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-SEVEN-EXCEPTION-PAIRWISE-PROFILE-SCREEN',revision=1,relation='uses_result')],verifier='/root/eight_domain_audit',producer='/root/structural_attack',checking_method='Literal word/column transformations and all36 composition laws; complete dense Boolean relation reindexing, all endpoint/profile/final-domain images and42 directed arcs; separate exact F and D covariance proof and genuine243 controls.',trusted_components=['Reuses pinned independently authored six-normalization dense bitmap/covariance/control helpers, not producer code.','Python standard library, NumPy exact Boolean/integer arithmetic and tqdm.','Separate exact-hash local-domain coverage and AC-correctness gates.'],limitations=['Does not rerun AC deletion algorithm or local catalogue enumeration; those are explicit independently reviewed premises.','No automorphism of an unknown target is assumed.','No feasibility of a nonempty orbit is established.','No source code is shared with the seven-normalization producer beyond the same raw data and standard libraries.'],artifact_availability='LOCAL_ONLY',availability_reason='Awaiting parent publication.',external_review=None,external_review_reason='Internal independent normalization audit.',created_at=ts,updated_at=ts,inputs_sha256=pins))
        result=dict(status='INDEPENDENT_HADAMARD_SEVEN_EXCEPTION_FIBRE_NORMALIZATION_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},profiles=1608,orbits=268,relation_entry_images=entrycount,directed_arc_predicate_images=directedcount,combined_empty_orbits=52,combined_nonempty_orbits=216,AC_exclusion_validity_source=acgatepath,solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),elapsed_seconds=result['elapsed_seconds'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
