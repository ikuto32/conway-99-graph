"""Independent profile relabelling/covariance audit, not an AC-correctness audit."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from itertools import permutations
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
import numpy as np
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';PROD=B+'hadamard_six_fibre_orbits/';ARC=B+'hadamard_six_profile_arc/';DOM=B+'hadamard_six_profile_local_domains/';RAW=B+'hadamard20_support/six_prism.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json';FIX=B+'srg243_residual_fixture/triangle_blocks.json'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def gz(p):return json.loads(gzip.decompress((ROOT/p).read_bytes()))
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def bits(encoded,n):
    val=int(encoded,16);need(0<=val<1<<n,'mask range');return np.unpackbits(np.frombuffer(val.to_bytes((n+7)//8,'little'),dtype=np.uint8),bitorder='little')[:n]
def relation(record,field,n,m):
    need(len(record[field])==n,'matrix row count');return np.array([bits(x,m)for x in record[field]],dtype=np.uint8)
def covariance(a,b,rows,cols):
    need(sorted(rows)==list(range(a.shape[0]))and sorted(cols)==list(range(a.shape[1]))and b.shape==a.shape,'relation index bijections')
    need(np.array_equal(a,b[np.ix_(rows,cols)]),'every dense relation entry covariance')
def psig(p):return tuple(p['group_ids']),tuple(x for row in p['coordinate_fibre_deviations']for f in row for x in f)
def controls(raw):
    rejected=[]
    def reject(name,fun):
        try:fun()
        except(ValueError,IndexError,KeyError):rejected.append(name);return
        raise ValueError('corruption accepted '+name)
    a=np.array([[0,1,1],[1,0,0]],dtype=np.uint8);r=[1,0];c=[2,0,1];target=np.zeros_like(a);target[np.ix_(r,c)]=a;covariance(a,target,r,c)
    bad=target.copy();bad[0,0]^=1;reject('changed_relation_bit',lambda:covariance(a,bad,r,c));reject('bad_row_bijection',lambda:covariance(a,target,[0,0],c));reject('bad_column_bijection',lambda:covariance(a,target,r,[0,0,2]));reject('mask_overflow',lambda:bits('0x8',3))
    fixture=read(FIX);F=np.array(fixture['factor60x180'],dtype=np.int64);C=np.array(fixture['cubic_core60'],dtype=np.int64);D=np.array(fixture['residual180x180'],dtype=np.int64)
    need(np.array_equal(F@D,2-F-C@F),'genuine243 mixed prerequisite');need(np.array_equal(D@D+F.T@F,20*np.eye(180,dtype=np.int64)-D+2),'genuine243 residual prerequisite')
    p=[20*((f+1)%3)+a for f in range(3)for a in range(20)];q=list(reversed(range(180)));N=F[np.ix_(p,q)];NC=C[np.ix_(p,p)];ND=D[np.ix_(q,q)]
    need(np.array_equal(N@N.T,(F@F.T)[np.ix_(p,p)])and np.array_equal(N@ND,2-N-NC@N)and np.array_equal(ND@ND+N.T@N,20*np.eye(180,dtype=np.int64)-ND+2),'exact complete positive covariance')
    bad=ND.copy();bad[0,1]^=1;reject('changed_residual_edge',lambda:need(np.array_equal(N@bad,2-N-NC@N)and np.array_equal(bad@bad+N.T@N,20*np.eye(180,dtype=np.int64)-bad+2),'corrupted completion'))
    cr=np.array(raw['core_adjacency'],dtype=np.int64);rp=[12*((f+1)%3)+a for f in range(3)for a in range(12)];bad=cr.copy();bad[0,1]^=1;reject('changed_fixed_core',lambda:need(np.array_equal(bad,bad[np.ix_(rp,rp)]),'literal fixed core'))
    return dict(rejected_corruptions=rejected,dense_relation_positive_entries=6,genuine243_Gram_entries=3600,genuine243_mixed_entries=10800,genuine243_residual_entries=32400,research_positive=False,numerical_arithmetic='Exact uint8 indexing and int64 products with entries/products bounded far below overflow; no floating point.')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(path,h=None):
        actual=sha(ROOT/path);need(h is None or actual==h,'input hash '+path);pins[path]=actual
    try:
        pin(PROD+'summary.json','ccba6e3aa029f1053039da2e31cb50eaca51e553cdf654b0a4d2e569970d651c');summary=read(PROD+'summary.json')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(p,h)
        raw=read(RAW);local=read(LOCAL);inv=read(ARC+'inventory/inventory.json');cp=read(ARC+'run01/checkpoint.json');profiles=[json.loads(line)for line in gzip.decompress((ROOT/(DOM+'profiles.jsonl.gz')).read_bytes()).splitlines()]
        need(len(profiles)==984 and len(inv['endpoints'])==1572 and len(inv['relations'])==12648,'frozen populations');save(out/'controls.json',controls(raw))
        C=np.array(raw['core_adjacency'],dtype=np.int64);G=np.array(raw['prescribed_Gram36'],dtype=np.int64);C2=C@C
        need(np.array_equal(G,12*np.eye(36,dtype=np.int64)+2-np.array([[int(i//12==j//12)for j in range(36)]for i in range(36)])-C-C2),'raw Gram formula')
        words=local['words'];triples=local['survivors'];word_index={tuple(w):i for i,w in enumerate(words)};triple_index={tuple(t):i for i,t in enumerate(triples)}
        actions=[];savedactions=gz(PROD+'local_actions.json.gz')
        for ai,tau in enumerate(permutations(range(3))):
            rp=[12*tau[f]+a for f in range(3)for a in range(12)];need(np.array_equal(C,C[np.ix_(rp,rp)])and np.array_equal(G,G[np.ix_(rp,rp)]),'fixed matrices fibre action')
            wm=[word_index[tuple(tau[f]for f in w)]for w in words];tm=[];orders=[]
            for t in triples:
                # Match each sorted target word directly to its old column, not producer bit indices.
                transformed=[tuple(tau[f]for f in words[w])for w in t];target=sorted(transformed);oldorder=[transformed.index(w)for w in target]
                ti=triple_index[tuple(word_index[w]for w in target)];tm.append(ti);orders.append(oldorder)
                need([[tau[f]for f in words[t[k]]]for k in oldorder]==[words[w]for w in triples[ti]],'every literal local column image')
            need(sorted(wm)==list(range(90))and sorted(tm)==list(range(31110)),'complete local bijections')
            record=dict(fibre_old_to_new=list(tau),core_row_old_to_new=rp,word_map=wm,local_triple_map=tm,column_new_to_old=orders);need(record==savedactions[ai],'all saved local action fields');actions.append(record)
        eps=inv['endpoints'];ep_lookup={(e['group'],frozenset(e['local_survivor_indices'])):e['index']for e in eps};epmaps=[];savedep=gz(PROD+'endpoint_maps.json.gz')
        need(len(ep_lookup)==1572,'unique endpoint domains')
        for e in eps:pin(e['domain_path'],e['domain_sha256'])
        for ai,act in enumerate(actions):
            em=[]
            for e in eps:
                mapped=[act['local_triple_map'][t]for t in e['local_survivor_indices']];target=ep_lookup[e['group'],frozenset(mapped)];position=[eps[target]['local_survivor_indices'].index(t)for t in mapped]
                need(sorted(position)==list(range(e['count'])),'whole endpoint-domain bijection');em.append(dict(target_endpoint=target,option_position_map=position))
            need(em==savedep[ai],'all saved endpoint actions');epmaps.append(em)
        matrices=[]
        for i,ref in enumerate(tqdm(cp['completed_relations'],desc='Independent dense relation inputs')):
            pin(ref['path'],ref['sha256']);r=gz(ref['path']);ends=inv['relations'][i]['endpoints'];need(r['index']==i and r['endpoints']==ends,'exact relation identification');n,m=[eps[e]['count']for e in ends]
            matrices.append((relation(r,'gram_forward',n,m),relation(r,'combined_forward',n,m)))
        rel_lookup={tuple(r['endpoints']):r['index']for r in inv['relations']};savedrel=gz(PROD+'relation_maps.json.gz');entrycount=0
        for ai in tqdm(range(6),desc='Independent dense covariance'):
            maps=[]
            for ri,rel in enumerate(inv['relations']):
                left,right=[epmaps[ai][e]for e in rel['endpoints']];target=rel_lookup[left['target_endpoint'],right['target_endpoint']];maps.append(target)
                for k in(0,1):covariance(matrices[ri][k],matrices[target][k],left['option_position_map'],right['option_position_map']);entrycount+=matrices[ri][k].size
            need(maps==savedrel[ai]and len(set(maps))==12648,'all saved relation permutations')
        ac=[]
        for ref in cp['completed_profiles']:pin(ref['path'],ref['sha256']);ac.append(gz(ref['path']))
        lookup={psig(p):i for i,p in enumerate(profiles)};need(len(lookup)==984,'unique raw profiles');pm=[];orbits=defaultdict(set)
        for i,p in enumerate(profiles):
            destinations=[]
            for ai,act in enumerate(actions):
                tau=act['fibre_old_to_new'];image=[ [row[tau.index(f)]for f in range(3)]for row in p['coordinate_fibre_deviations']];target=lookup[(tuple(p['group_ids']),tuple(x for row in image for f in row for x in f))];destinations.append(target)
                need([epmaps[ai][e]['target_endpoint']for e in inv['profiles'][i]['endpoints']]==inv['profiles'][target]['endpoints'],'whole profile domains')
                for field in['gram_ac','gram_caps_ac']:
                    need(ac[i][field]['empty']==ac[target][field]['empty'],'candidate classification invariant')
                    for side,e in enumerate(inv['profiles'][i]['endpoints']):
                        pos=epmaps[ai][e]['option_position_map'];n=len(pos);need(np.array_equal(bits(ac[i][field]['final_masks'][side],n),bits(ac[target][field]['final_masks'][side],n)[pos]),'all saved fixed-point elements covary')
            need(len(set(destinations))==6,'free six-action orbit');rep=min(destinations,key=lambda j:profiles[j]['id']);orbits[rep].add(i)
            pm.append(dict(index=i,id=p['id'],profile_sha256=p['profile_sha256'],action_target_indices=destinations,representative_index=rep,representative_id=profiles[rep]['id'],representative_action=destinations.index(rep)))
        need(pm==gz(PROD+'profile_maps.json.gz'),'all5904 profile images and reps');orbitrecords=[]
        for rep,members in sorted(orbits.items(),key=lambda x:profiles[x[0]]['id']):
            need(members==set(pm[rep]['action_target_indices']),'complete orbit partition');orbitrecords.append(dict(representative_index=rep,representative_id=profiles[rep]['id'],members=sorted(members),member_ids=[profiles[j]['id']for j in sorted(members)],Gram_empty=ac[rep]['gram_ac']['empty'],Gram_caps_empty=ac[rep]['gram_caps_ac']['empty']))
        need(orbitrecords==read(PROD+'orbits.json')['orbits']and len(orbits)==164 and entrycount==154159488,'complete census counts')
        empty=sum(r['Gram_caps_empty']for r in orbitrecords);need(empty==109 and sum(x['gram_caps_ac']['empty']for x in ac)==654,'raw recorded labels count')
        save(out/'independent_orbits.json',dict(orbits=orbitrecords,classification_scope='Only recorded-label covariance checked here; AC validity is a separate dependency.'))
        # Fresh actual-data corruptions beyond generic controls.
        changed=matrices[0][0].copy();changed[0,0]^=1
        try:covariance(changed,matrices[0][0],list(range(changed.shape[0])),list(range(changed.shape[1])))
        except ValueError:pass
        else:raise ValueError('actual relation corruption accepted')
        need(pm[0]['representative_index']!=pm[1]['representative_index']or psig(profiles[0])!=psig(profiles[1]),'distinct raw profile control')
        save(out/'counts.json',dict(local_triple_images=186660,endpoint_domain_images=9432,relation_images=75888,relation_entry_images=entrycount,profile_images=5904,orbits=164,recorded_Gram_caps_empty_profiles=654,recorded_Gram_caps_empty_orbits=109,recorded_nonempty_profiles=330,recorded_nonempty_orbits=55,AC_correctness_review=None,AC_correctness_review_null_reason='Separate parent audit not a premise checked by this normalization report.'))
        for p in[Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_SIX_FIBRE_ORBITS.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p.resolve().relative_to(ROOT).as_posix())
        ts=datetime.now(timezone.utc).isoformat();save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-SIX-EXCEPTION-FIBRE-NORMALIZATION',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='On the pinned fixed six-prism Hadamard support, all six global fibre relabellings, followed by sorting each local triple within its three identical-support columns, are reversible bijections of full incidence factors and any residual completions. They preserve the prescribed Gram, all column and mixed caps, and transport the984 frozen six-exception profiles into exactly164 orbits of size6. All saved local domains, pair relations and saved fixed-point masks covary under the recorded maps.',scope='Exactly the pinned984-profile fixed-support universe; no hypothetical target automorphism is assumed. The raw654 empty labels form109 orbits and330 nonempty labels form55 orbits, but their exclusion validity requires a separate AC correctness audit.',assumptions=['Pinned fixed core/support and independently checked initial profile/domain universe.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-EXCEPTION-LOCAL-DOMAIN-FILTER',revision=1,relation='premise')],verifier='/root/eight_domain_audit',producer='/root/state_literature_audit',checking_method='Own literal word/column mappings and dense Boolean matrix reindexing of154159488 entries, every profile/fixed-point image and exact residual covariance controls.',trusted_components=['Python standard library and NumPy exact integer/Boolean indexing.','Pinned raw inputs; no producer imports or shared transformation helpers.'],limitations=['Does not independently validate AC deletion soundness or reproduce its maximal fixed point.','A surviving orbit does not prove joint choices or a full factor.','No target-level resolution.'],artifact_availability='LOCAL_ONLY',availability_reason='Awaiting parent publication.',external_review=None,external_review_reason='Internal independent audit.',created_at=ts,updated_at=ts,inputs_sha256=pins))
        result=dict(status='INDEPENDENT_HADAMARD_SIX_EXCEPTION_FIBRE_NORMALIZATION_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},profiles=984,orbits=164,relation_entry_images=entrycount,recorded_empty_orbits=109,recorded_nonempty_orbits=55,AC_exclusion_validity_approved=False,solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
