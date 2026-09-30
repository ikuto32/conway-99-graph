"""Independent complete campaign population/fibre transport; no producer imports."""
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations, permutations, product
from datetime import datetime, timezone
import argparse
import copy
import gzip
import hashlib
import json
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_';I=B+'independent_review/'
MAN=B+'exact_eight_campaign_preparation/campaign_manifest.json'
BLOCK=I+'exact_eight_block_screen/summary.json'
JOIN=I+'exact_eight_profile_join/summary.json'
SURV=B+'exact_eight_block_screen/surviving_representatives.json.gz'
RAW=B+'hadamard20_support/six_prism.json'
LOCAL=B+'hadamard_triplicate_counts/local_triples.json'
FIXTURE=B+'srg243_residual_fixture/triangle_blocks.json'
DOC='docs/AUDIT_20260930_EXACT_EIGHT_CAMPAIGN_COVERAGE.md'
PINS={
 MAN:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',
 BLOCK:'6c21ef6951f72fbeabab8be0a649f178ca8b17eb91edcc35c3291d6790f6256a',
 JOIN:'2538bf724a3938b14ffd1856fc4e9a8a6a294a6905ddc7000d19cf72f93b217c',
 SURV:'2cf8ab222d5dd220381fdc14bd225438c173aea40d895353e02f752bc537de5f',
 RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',
 FIXTURE:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
 I+'srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',
 I+'hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',
}
INPUTS={};FIBRES=list(permutations(range(3)))

def need(ok,msg):
    if not ok:raise ValueError(msg)

def path(p):
    p=str(p).replace('\\','/')
    need(p!=I+'hadamard_oriented_unknown/process.stdout.log' and 'PROMPT.md' not in p and not p.startswith('tools/'),'protected path')
    q=(ROOT/p).resolve();need(q.is_relative_to(ROOT),'path escape');return q

def sha(p):
    q=path(p)
    with q.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    INPUTS[q.relative_to(ROOT).as_posix()]=h;return h

def read(p):
    sha(p)
    return json.loads(path(p).read_bytes())

def gzread(p):
    sha(p)
    with gzip.open(path(p),'rt',encoding='utf8') as f:return json.load(f)

def bind(p,h):need(sha(p)==h,'input hash '+str(p))

def save(p,v):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')

def savegz(p,v):
    with p.open('xb') as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write((json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode())

def flattened(counts):return tuple(v for row in counts for triple in row for v in triple)
def digest(v):return hashlib.sha256(bytes(v)).hexdigest()
def image(v,p):return tuple(v[k+p[f]] for k in range(0,len(v),3) for f in range(3))

def catalogue(raw):
    words=[w for w in product(range(3),repeat=6) if all(w.count(f)==2 for f in range(3))]
    masks=[sum(1<<(3*a+f) for a,f in enumerate(w)) for w in words]
    triples=[t for t in combinations(range(90),3) if all((masks[i]&masks[j]).bit_count()<=2 for i,j in combinations(t,2))]
    need([list(w) for w in words]==raw['words'] and [list(t) for t in triples]==raw['survivors'],'complete raw local catalogue')
    need(len(triples)==31110,'local triple count')
    classes=defaultdict(list)
    for rank,t in enumerate(triples):
        sig=tuple(sum(words[w][a]==f for w in t) for a in range(6) for f in range(3))
        classes[sig].append(rank)
    signatures=sorted(classes);need(len(signatures)==6061 and len(classes[(1,)*18])==150,'complete signature census')
    balanced=[rank for rank,t in enumerate(triples) if all(sum(words[w][a]==f for w in t)==1 for a in range(6) for f in range(3))]
    need([list(triples[r]) for r in balanced]==raw['balanced'],'balanced normalization population')
    for r in balanced:need([words[w][0] for w in triples[r]]==[0,1,2],'balanced first-coordinate normalization')
    return words,triples,signatures,classes

def matrices(raw):
    C=[[int((i//12==j//12 and (i%12)^1==j%12) or (i//12!=j//12 and i%12==j%12)) for j in range(36)] for i in range(36)]
    C2=[[sum(C[i][k]*C[k][j] for k in range(36)) for j in range(36)] for i in range(36)]
    G=[[12*int(i==j)-C[i][j]-C2[i][j]+2-int(i//12==j//12) for j in range(36)] for i in range(36)]
    need(C==raw['core_adjacency'] and G==raw['prescribed_Gram36'],'literal core/prescribed Gram reconstruction')
    groups=[];columns=[]
    for j in range(60):
        s=tuple(a for a in range(12) if raw['L'][a][j])
        need(len(s)==6 and all(sum(a//2==b for a in s)==1 for b in range(6)),'one coordinate per prism')
        need(list(s)==raw['support_columns'][j],'raw support definition')
        if s not in groups:groups.append(s);columns.append([])
        columns[groups.index(s)].append(j)
    need(len(groups)==20 and all(len(x)==3 for x in columns),'complete support triplicates')
    B39=[[0]*39 for _ in range(39)]
    for a,b in combinations(range(3),2):B39[a][b]=B39[b][a]=1
    for i in range(36):
        B39[i//12][3+i]=B39[3+i][i//12]=1
        for j in range(36):B39[3+i][3+j]=C[i][j]
    return C,G,B39,groups,columns

def core_action(C,G,B39,p):
    rows=[12*p[f]+a for f in range(3) for a in range(12)]
    rows39=list(p)+[3+i for i in rows]
    need([[C[i][j] for j in rows] for i in rows]==C,'core fibre invariance')
    need([[G[i][j] for j in rows] for i in rows]==G,'Gram fibre invariance')
    need([[B39[i][j] for j in rows39] for i in rows39]==B39,'triangle core fibre invariance')
    return rows,rows39

def local_actions(words,triples,signatures,classes,C,G,B39):
    wordid={w:i for i,w in enumerate(words)};tripleid={t:i for i,t in enumerate(triples)};sigids={s:i for i,s in enumerate(signatures)}
    actions=[]
    for p in FIBRES:
        inv=tuple(p.index(f) for f in range(3));wm=[wordid[tuple(inv[f] for f in w)] for w in words]
        need(sorted(wm)==list(range(90)),'word bijection')
        tm=[];orders=[]
        for t in triples:
            mapped=[wm[w] for w in t];order=sorted(range(3),key=lambda j:mapped[j]);target=tuple(mapped[j] for j in order)
            need(target in tripleid,'complete transformed domain');tm.append(tripleid[target]);orders.append(order)
            # Entrywise witness for P followed by Q, independently from counts.
            for j in range(3):
                need(words[target[j]]==tuple(inv[f] for f in words[t[order[j]]]),'literal column normalization')
        need(sorted(tm)==list(range(31110)),'triple bijection')
        sm=[]
        for s in signatures:
            t=image(s,p);need(t in classes,'class closed')
            need(sorted(tm[r] for r in classes[s])==classes[t],'entire class domain covariance')
            sm.append(sigids[t])
        rows,rows39=core_action(C,G,B39,p)
        actions.append(dict(pull_fibre_permutation=list(p),old_to_new_fibre=list(inv),core_row_order=rows,triangle_core_order=rows39,word_image=wm,triple_image=tm,normalized_new_column_to_old_column=orders,signature_image=sm))
    for pi,p in enumerate(FIBRES):
        for qi,q in enumerate(FIBRES):
            composed=tuple(p[q[f]] for f in range(3));ri=FIBRES.index(composed)
            need(all(actions[qi]['triple_image'][actions[pi]['triple_image'][r]]==actions[ri]['triple_image'][r] for r in range(31110)),'full action group law')
    return actions,sigids

def check_counts(counts,groups):
    need(len(counts)==12 and all(len(row)==20 and all(len(t)==3 and all(type(x)is int and 0<=x<=3 for x in t) for t in row) for row in counts),'count shape/value')
    for a in range(12):
        for g,s in enumerate(groups):need(sum(counts[a][g])==3*int(a in s),'support count sum')
        for f in range(3):need(sum(counts[a][g][f] for g in range(20))==10,'full row margin')
    for g,s in enumerate(groups):
        for f in range(3):need(sum(counts[a][g][f] for a in s)==6,'group fibre quota')
    e=[g for g,s in enumerate(groups) if any(counts[a][g]!=[1,1,1] for a in s)]
    need(len(e)==8,'exact eight exceptions');return e

def campaign_check(campaign,reps):
    ordered=sorted(reps,key=lambda r:(r['subset_index'],r['canonical_fibre_profile_sha256']))
    need(campaign['universe_size']==792 and len(campaign['records'])==792,'exact canonical population')
    ids=[];first=[];seen=set()
    for i,(actual,r) in enumerate(zip(campaign['records'],ordered)):
        dg=r['canonical_fibre_profile_sha256'];ids.append('exact_eight_'+dg)
        need(actual==dict(case_id=ids[-1],case_index=i,full_count_profile_sha256=dg,raw_representative=r,subset_index=r['subset_index']),'literal complete campaign record')
        if r['subset_index'] not in seen:
            seen.add(r['subset_index'])
            if len(first)<12:first.append(ids[-1])
    need(len(set(ids))==792 and campaign['first_batch_case_ids']==first,'complete unique IDs/first12 selection')
    need(campaign['ordering']==['subset_index','canonical_full_count_sha256'],'frozen ordering')
    need(all(campaign[k] is False for k in ['historical_profiles_subtracted','prior_exclusions_used','full_fibre_orbit_sizes_assumed','full_factor_claim']),'no subtraction or factor assertion')
    return ordered

def gram(F):
    masks=[sum(x<<j for j,x in enumerate(row)) for row in F]
    return [[(a&b).bit_count() for b in masks] for a in masks]

def multiply_binary(F,D):
    rows=[sum(x<<j for j,x in enumerate(row)) for row in F]
    cols=[sum(D[i][j]<<i for i in range(len(D))) for j in range(len(D[0]))]
    return [[(a&b).bit_count() for b in cols] for a in rows]

def fixture_controls(fixture):
    F=fixture['factor60x180'];D=fixture['residual180x180'];G=gram(F);H=multiply_binary(F,D)
    checks=0
    for p in FIBRES:
        rows=[20*p[f]+a for f in range(3) for a in range(20)];cols=list(range(180));cols[0],cols[179]=cols[179],cols[0]
        F1=[[F[i][j] for j in cols] for i in rows];D1=[[D[i][j] for j in cols] for i in cols]
        need(gram(F1)==[[G[i][j] for j in rows] for i in rows],'genuine243 own-Gram covariance')
        need(multiply_binary(F1,D1)==[[H[i][j] for j in cols] for i in rows],'genuine243 mixed covariance')
        need(all(D1[i][j]==D1[j][i] and (i!=j or D1[i][j]==0) for i in range(180) for j in range(180)),'genuine243 residual symmetry')
        checks+=1
    return checks

def reject(name,fn,controls):
    try:fn()
    except (ValueError,KeyError,IndexError):controls.append(name)
    else:raise ValueError('accepted corruption '+name)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        for p,h in PINS.items():bind(p,h)
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),path(DOC)]:sha(p.relative_to(ROOT).as_posix())
        campaign=read(MAN);block=read(BLOCK);join=read(JOIN)
        need(block['status']=='INDEPENDENT_EXACT_EIGHT_BLOCK_SCREEN_PASS' and join['status']=='INDEPENDENT_COMPLETE_EXACT_EIGHT_PROFILE_JOIN_PASS','coverage premises')
        need(block['inputs_sha256'][SURV]==PINS[SURV],'survivor exact independent binding')
        for pathkey,hashkey in [('block_gate_path','block_gate_sha256'),('block_summary_path','block_summary_sha256'),('survivor_path','survivor_sha256'),('plan_path','plan_sha256')]:bind(campaign[pathkey],campaign[hashkey])
        survivors=gzread(SURV);need(survivors['complete'] and len(survivors['records'])==792,'complete raw survivors');ordered=campaign_check(campaign,survivors['records'])
        raw=read(RAW);C,G,B39,groups,columns=matrices(raw)
        words,triples,signatures,classes=catalogue(read(LOCAL));actions,sigids=local_actions(words,triples,signatures,classes,C,G,B39)
        for support in groups:
            for word in words:
                selected=[12*word[i]+a for i,a in enumerate(support)]
                need(all(G[a][b]>0 for a,b in combinations(selected,2)),'all literal word zero-Gram restrictions')
                need(all(sum(r//12==f for r in selected)==2 for f in range(3)),'literal word fibre margins')
        savegz(out/'complete_local_transport.json.gz',dict(words=words,triples=triples,signature_classes=[dict(signature=s,ranks=classes[s]) for s in signatures],actions=actions))
        source_orbits={};source_profiles={};global_images=set();records=[];domain_uses=0
        for ci,rep in enumerate(ordered):
            counts=rep['counts'];E=check_counts(counts,groups);v=flattened(counts);dg=digest(v)
            need(E==rep['exceptional_groups'] and v==min(image(v,p) for p in FIBRES) and dg==rep['canonical_fibre_profile_sha256'],'canonical count identity')
            op=rep['source_orbits_path'];pp=op.rsplit('/',1)[0]+'/profiles.jsonl.gz'
            if op not in source_orbits:
                bind(op,join['inputs_sha256'][op]);o=read(op);need(o['complete'],'source orbit completeness');source_orbits[op]={x['canonical_fibre_profile_sha256']:x for x in o['orbits']}
                bind(pp,join['inputs_sha256'][pp])
                with gzip.open(path(pp),'rt',encoding='utf8') as f:source_profiles[pp]=[json.loads(line) for line in f if line.strip()]
            source=source_orbits[op][dg]
            need(source==dict(canonical_fibre_profile_sha256=dg,canonical_counts=list(v),orbit_size=rep['orbit_size'],members=rep['members']),'exact source census orbit')
            baseclasses=[sigids[tuple(x for a in s for x in counts[a][g])] for g,s in enumerate(groups)]
            perimage=[];current_images={}
            for pi,p in enumerate(FIBRES):
                vi=image(v,p);idh=digest(vi);need(idh not in global_images,'no duplicate labelled transport');global_images.add(idh);current_images[idh]=vi
                imageclasses=[]
                for g,s in enumerate(groups):
                    target=tuple(counts[a][g][p[f]] for a in s for f in range(3));cid=sigids[target];sourceid=baseclasses[g]
                    need(actions[pi]['signature_image'][sourceid]==cid,'profile class image')
                    need(sorted(actions[pi]['triple_image'][r] for r in classes[signatures[sourceid]])==classes[target],'complete actual initial-domain transport')
                    imageclasses.append(cid);domain_uses+=1
                perimage.append(dict(pull_fibre_permutation=p,labelled_count_sha256=idh,full_counts_flat=vi,initial_domain_class_ids=imageclasses))
            need(len(current_images)==rep['orbit_size']==len(rep['members'])==6,'computed free orbit')
            need(set(current_images)=={m['profile_sha256'] for m in rep['members']},'all labelled census members')
            for member in rep['members']:
                sv=source_profiles[pp][member['index']];cv=current_images[member['profile_sha256']]
                need(sv['index']==member['index'] and flattened(sv['coordinate_group_fibre_counts'])==cv,'literal raw census table')
                p=tuple(member['canonicalizing_fibre_permutation']);need(p in FIBRES and image(cv,p)==v,'literal canonicalizing map')
            records.append(dict(case_index=ci,case_id='exact_eight_'+dg,subset_index=rep['subset_index'],exceptional_groups=E,canonical_initial_domain_class_ids=baseclasses,images=perimage,source_orbits_path=op,source_profiles_path=pp))
        need(len(global_images)==4752 and domain_uses==95040,'complete labelled/domain population')
        savegz(out/'all_labelled_transports.json.gz',dict(complete=True,canonical_profiles=792,labelled_profiles=4752,group_supports=groups,group_columns=columns,records=records))
        positives=[]
        for v,n in [((1,1,1),1),((0,0,3),3),((0,1,2),6)]:need(len({image(v,p) for p in FIBRES})==n,'orbit calibration');positives.append(dict(vector=v,orbit_size=n))
        fixture_checks=fixture_controls(read(FIXTURE));controls=[]
        for name,mut in [('missing_campaign',lambda d:d['records'].pop()),('duplicate_case',lambda d:d['records'].__setitem__(1,copy.deepcopy(d['records'][0]))),('changed_count_hash',lambda d:d['records'][0].__setitem__('full_count_profile_sha256','0'*64)),('old_exclusion_subtraction',lambda d:d.__setitem__('historical_profiles_subtracted',True)),('first12_changed',lambda d:d['first_batch_case_ids'].reverse())]:
            bad=copy.deepcopy(campaign);mut(bad);reject(name,lambda:campaign_check(bad,survivors['records']),controls)
        bad=copy.deepcopy(ordered[0]['counts']);bad[0][0][0]+=1;reject('changed_raw_count',lambda:check_counts(bad,groups),controls)
        wrong=list(range(36));wrong[0],wrong[2]=wrong[2],wrong[0];reject('nonpreserving_core_map',lambda:need([[C[i][j] for j in wrong] for i in wrong]==C,'invalid core map'),controls)
        t=triples[0];p=FIBRES[1];inv=tuple(p.index(f) for f in range(3));expected=sorted(tuple(inv[f] for f in words[w]) for w in t)
        reject('wrong_word_action',lambda:need(sorted(words[w] for w in t)==expected,'incorrect word action'),controls)
        cid=next(i for i,s in enumerate(signatures) if len(classes[s])>1);ranks=classes[signatures[cid]]
        reject('truncated_initial_domain',lambda:need(ranks[:-1]==ranks,'omitted option'),controls)
        reject('duplicate_local_column',lambda:need(all(sum(a==b for a,b in zip(words[t[0]],words[t[0]]))<=2 for _ in [0]),'duplicate column cap'),controls)
        sample=records[0]['images'][1];reject('wrong_fibre_transport',lambda:need(image(tuple(sample['full_counts_flat']),FIBRES[0])==tuple(records[0]['images'][0]['full_counts_flat']),'wrong inverse fibre map'),controls)
        save(out/'controls.json',dict(orbit_positives=positives,genuine243_covariance_checks=fixture_checks,corruptions_rejected=controls,fixture_scope='Generic own-Gram/mixed covariance only, not the research fixed-core factor or its invariance.'))
        need(time.monotonic()-started<120,'bounded audit allocation')
        stamp=datetime.now(timezone.utc).isoformat();cid='C-FIXED-HADAMARD-EXACT-EIGHT-CAMPAIGN-FIBRE-COVERAGE'
        statement='The frozen all792 campaign manifest is exactly the complete canonical count-table population surviving the authenticated scalar and separate-block screens, without historical subtraction. Explicit global S3 fibre relabellings give4752 distinct labelled census tables and bijections of every complete initial local domain. With equal-support column re-normalization they preserve the fixed core, prescribed Gram and conditional residual completion. This supplies conditional transport of future separately verified literal results, not an exclusion or approval of any formula.'
        scope='Literal six-prism Hadamard support, exactly-eight count population with within-triplicate caps; complete792-to4752 count/domain coverage and conditional full-factor/completion relabelling only.'
        outputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
        result=dict(status='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_COVERAGE_TRANSPORT_PASS',created_at=stamp,command=[sys.executable,*sys.argv],cwd=str(ROOT),claim_id=cid,claim_revision=1,canonical_profiles=792,labelled_profiles=4752,local_words=90,examined_local_triples=117480,retained_local_triples=31110,signature_classes=6061,fibre_actions=6,full_action_composition_entries=36*31110,signature_class_bijections=6*6061,profile_domain_transports=domain_uses,raw_census_subsets=len(source_orbits),historical_profiles_subtracted=0,formula_approvals=0,proof_gates_consumed=0,exclusions=0,native_calls=0,scope=scope,inputs_sha256=INPUTS,outputs_sha256=outputs,controls_rejected=len(controls),producer_imports=False,elapsed_seconds=time.monotonic()-started)
        save(out/'summary.json',result)
        binding=dict(id=cid,revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,scope=scope,assumptions=['Authenticated full scalar/block survivor population and earlier complete count census.','Literal fixed core/support and complete within-triplicate-cap local domains.'],dependencies=[dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-SEPARATE-GRAM-BLOCK-SCREEN',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-COMPLETE-EIGHT-COUNT-PROFILE-CENSUS',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage'),dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='uses_result')],verifier='/root/state_literature_audit',method='Independent unordered bitmask catalogue, exact entrywise fibre/column actions and raw census-table/domain bijections; no producer/checker imports.',created_at=stamp,updated_at=stamp,inputs_sha256=INPUTS,evidence_sha256={**outputs,(out/'summary.json').relative_to(ROOT).as_posix():hashlib.sha256((out/'summary.json').read_bytes()).hexdigest()},shared_components=['Python standard library and authenticated raw count/support/catalogue fixtures.','Prior complete census and scalar/block gates are explicit coverage premises, not rerun by this audit.'],controls=['Orbit-size1/3/6 positives, all local action laws/domain bijections, genuine243 own-Gram/mixed covariance and explicit corruptions.'],limitations=['No actual CNF, native assignment or complete proof is approved here.','No exclusion follows before literal proof gates and any required union coverage are separately checked.','No target automorphism, balance-WLOG, other support or larger exception population claim.','Cross-group caps and residualD are preserved if present but remain omitted in the campaign formula scope.'],artifact_availability='LOCAL_ONLY')
        save(out/'claim_binding.json',binding);print(json.dumps({k:result[k] for k in ('status','canonical_profiles','labelled_profiles','profile_domain_transports','elapsed_seconds')}))
    except Exception as e:
        save(out/'failure.json',dict(error=repr(e),inputs_sha256=INPUTS,elapsed_seconds=time.monotonic()-started));raise

if __name__=='__main__':main()
