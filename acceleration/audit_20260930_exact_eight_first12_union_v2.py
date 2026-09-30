"""Independent finite union of authenticated literal proofs and fibre transport."""
import argparse, copy, gzip, hashlib, itertools as it, json, platform, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';I=B/'20260930_independent_review'
SRC=Path(__file__).resolve();SPEC=SRC.with_name(SRC.stem+'_spec.md');DOC=ROOT/'docs/AUDIT_20260930_EXACT_EIGHT_FIRST12_UNION_V2.md'
PG=I/'exact_eight_first12_proofs/summary.json';CG=I/'exact_eight_campaign_coverage_v2/summary.json';EG=I/'exact_eight_campaign/summary.json';POP=B/'20260930_exact_eight_campaign_preparation/campaign_manifest.json';RAW=B/'20260930_hadamard20_support/six_prism.json'
PINS={PG:'a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9',CG:'f6b468e80410caaedbbb88ce02cef79e0a693168df0eb9134d8d4d8e62b96223',EG:'e334293416c1048cf3a6e7c4bd8242892dc84e7f7d773bd388b506fdde77ea27',POP:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',PG.parent/'claim_binding.json':'c45d918208521189f2c9b4dba5c05c080513e8e89a41fd60cc49d6698eeeec1b',CG.parent/'claim_binding.json':'8ff5ec8a91cada98a03c2ce63f192aef0e1d63ad8be2861c1c5fc164265d006d'}
PINS.update({ROOT/'acceleration/audit_20260930_exact_eight_first12_union.py':'754667cbb5089e58ec274c7883c0c8126c77394a70bd8f83e151121e8ee4a9e4',ROOT/'acceleration/audit_20260930_exact_eight_first12_union_spec.md':'eec2936e9901e9fa540be11d5765886a73d571aa3e7465ea94d44ceb9aed0633',ROOT/'docs/AUDIT_20260930_EXACT_EIGHT_FIRST12_UNION.md':'800776cace4745767ab807491d443545e0280794387dc49491a99c789602ceaf',I/'exact_eight_first12_union/failure.json':'6b22397acbc313155df58f5b3428407073931f7130348d31a33c77063ec3e3db'})
HIST={
'prior_single_pilot':(B/'20260930_exact_eight_next_lift/scope.json','d8a05714c5297495c2a2d28835bd0c41de90a956162f998158dea39f78cf04b1'),
'first_historical_count':(I/'count_master_sat_outcome/independent_count_profile.json','0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152'),
'second_historical_count':(I/'count_master_eight_orbit_cut_sat_outcome/independent_count_profile.json','7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'),
'third_historical_count':(I/'count_master_partial_cut_sat_outcome/independent_count_profile.json','03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e')}
def need(x,m):
    if not x:raise ValueError(m)
def eq(a,b,m):need(a==b,m)
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def flat(c):
    need(len(c)==12 and all(len(r)==20 and all(len(v)==3 and all(type(n)is int and 0<=n<=3 for n in v)for v in r)for r in c),'raw table shape')
    return bytes(x for row in c for v in row for x in v)
def digest(v):return hashlib.sha256(v).hexdigest()
def image(v,p):
    eq(sorted(p),[0,1,2],'fibre permutation');need(len(v)==720,'raw table length')
    return bytes(v[j+p[f]]for j in range(0,720,3)for f in range(3))
def inverse(p):return tuple(p.index(f)for f in range(3))
def images(v):return {image(v,p)for p in it.permutations(range(3))}
def proof_contract(r,e):
    for k in ['case_id','case_index','subset_index','full_count_profile_sha256','cnf_path','cnf_sha256','scope_path','scope_sha256']:eq(r[k],e[k],'proof/encoding '+k)
    need(r['outcome']=='UNSAT_VERIFIED'and r['trace']['complete_proof']is True,'complete literal exclusion')
    q=r['replay'];need(q['accepted']is True and q['actual_exit_code']==0 and q['expected_acceptance']is True,'accepted complete replay')
    eq(q['cnf_sha256'],r['cnf_sha256'],'replay exact formula');eq(q['proof_sha256'],r['trace']['sha256'],'replay exact trace')
def scope_contract(scope,record,raw):
    eq(scope['coordinate_group_fibre_counts'],record['raw_representative']['counts'],'proof table is manifest table')
    eq(scope['core_adjacency36'],raw['core_adjacency'],'same core');eq(scope['prescribed_Gram36'],raw['prescribed_Gram36'],'same Gram');eq(scope['L12x60'],raw['L'],'same support')
    need(scope['within_group_column_caps_encoded']is True and scope['cross_group_column_caps_encoded']is False and scope['residual_D_encoded']is False,'exact exclusion scope')
    need(scope['arc_pruning_used']is False and scope['orbit_coverage_used']is False and scope['assumed_target_automorphism']is None,'literal unpruned domain scope')
    eq(scope['campaign_case_id'],record['case_id'],'scope case identity')
def unique_orbits(vectors):
    out=set()
    for v in vectors:
        orbit=images(v);eq(len(orbit),6,'six images established literally');need(not out&orbit,'distinct proved orbits');out.update(orbit)
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.monotonic();bad=[]
    def pin(p,h=None):
        p=p.resolve();name=key(p);need('hadamard_oriented_unknown/process.stdout.log'not in name,'protected input');v=sha(p);need(h is None or v==h,'hash '+name);pins[name]=v
    def reject(name,fn):
        try:fn()
        except(ValueError,AssertionError,KeyError,IndexError,TypeError):bad.append(name);return
        raise ValueError('accepted corruption '+name)
    try:
        for p,h in PINS.items():pin(p,h)
        for p in[SRC,SPEC,DOC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        pg,cg,eg,pop,raw=[read(p)for p in[PG,CG,EG,POP,RAW]]
        eq(pg['status'],'INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS','literal proof gate');eq(cg['status'],'INDEPENDENT_EXACT_EIGHT_CAMPAIGN_COVERAGE_TRANSPORT_PASS','transport gate');eq(eg['status'],'INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS','literal encoding gate')
        eq(pg['completed_proof_replays'],12,'all12 proofs');eq(pg['SAT_pending'],0,'no pending SAT');eq(pg['UNKNOWN'],0,'no unknown');eq(pg['pending_case_ids'],[],'no pending cases')
        for gate in[cg,pg]:
            for name,h in gate['outputs_sha256'].items():pin(ROOT/name,h)
        eq(pg['inputs_sha256'][key(EG)],PINS[EG],'same encoding premise');eq(cg['inputs_sha256'][key(POP)],PINS[POP],'same whole population')
        proof_binding=read(PG.parent/'claim_binding.json');eq(proof_binding['id'],'C-FIXED-HADAMARD-EXACT-EIGHT-FIRST12-LITERAL-PROFILE-EXCLUSIONS','proof claim identity');eq(proof_binding['revision'],1,'proof revision')
        coverage=read(CG.parent/'all_labelled_transports.json.gz');local=read(CG.parent/'complete_local_transport.json.gz');groups=coverage['group_supports'];cols=coverage['group_columns'];words=local['words'];triples=local['triples'];classes=local['signature_classes'];actions=local['actions']
        eq(len(coverage['records']),792,'full coverage records');eq([a['pull_fibre_permutation']for a in actions],[list(p)for p in it.permutations(range(3))],'all explicit actions')
        class_ids={tuple(c['signature']):j for j,c in enumerate(classes)};triple_ids={tuple(t):j for j,t in enumerate(triples)};word_ids={tuple(w):j for j,w in enumerate(words)}
        def signatures(v):return [class_ids[tuple(v[60*a+3*g+f]for a in groups[g]for f in range(3))]for g in range(20)]
        def covariance(source_classes,dest_classes,p,act):
            inv=inverse(p)
            for g,(s,t)in enumerate(zip(source_classes,dest_classes)):
                got=[]
                for rank in classes[s]['ranks']:
                    transformed=[word_ids[tuple(inv[f]for f in words[j])]for j in triples[rank]];order=sorted(range(3),key=lambda j:transformed[j]);dest=triple_ids[tuple(transformed[j]for j in order)]
                    eq(act['triple_image'][rank],dest,'literal triple relabelling');eq(act['normalized_new_column_to_old_column'][rank],order,'equal-support sorting map');got.append(dest)
                eq(sorted(got),classes[t]['ranks'],'complete selected domain bijection')
        for act in actions:
            p=tuple(act['pull_fibre_permutation']);row=[12*p[f]+a for f in range(3)for a in range(12)];eq(act['core_row_order'],row,'row action')
            for matrix in[raw['core_adjacency'],raw['prescribed_Gram36']]:eq([[matrix[row[i]][row[j]]for j in range(36)]for i in range(36)],matrix,'literal fixed matrix covariance')
        universe={r['case_id']:r for r in pop['records']};covered={r['case_id']:r for r in coverage['records']};encoded={r['case_id']:r for r in eg['checked_cases']}
        selected=pop['first_batch_case_ids'];eq(pg['selected_case_ids'],selected,'same exact selection');eq([r['case_id']for r in pg['case_records']],selected,'ordered proof coverage');eq(eg['selected_case_ids'],selected,'ordered encoding coverage');eq(len(set(selected)),12,'12 distinct canonical profiles')
        # Controls attack composition before any union conclusion.
        pr=pg['case_records'][0];er=encoded[pr['case_id']]
        for label,mutate in [('incomplete proof',lambda r:r['trace'].__setitem__('complete_proof',False)),('wrong formula',lambda r:r.__setitem__('cnf_sha256','0'*64)),('wrong proof replay',lambda r:r['replay'].__setitem__('proof_sha256','0'*64)),('failed replay',lambda r:r['replay'].__setitem__('accepted',False))]:
            damaged=copy.deepcopy(pr);mutate(damaged);reject(label,lambda damaged=damaged:proof_contract(damaged,er))
        reject('missing proof record',lambda:eq([r['case_id']for r in pg['case_records'][:-1]],selected,'complete proof set'))
        balanced=bytes(1 if a in groups[g]else 0 for a in range(12)for g in range(20)for f in range(3));eq(len(images(balanced)),1,'balanced stabilizer positive');reject('assumed free action',lambda:unique_orbits([balanced]))
        vectors=[];records=[];proof_bytes=0
        for r in pg['case_records']:
            cid=r['case_id'];e=encoded[cid];m=universe[cid];cr=covered[cid];proof_contract(r,e)
            for stem in['cnf','scope','model','profile','summary']:
                name=e[stem+'_path'];h=e[stem+'_sha256'];pin(ROOT/name,h);eq(eg['inputs_sha256'].get(name),h,'direct encoded artifact')
            for stem in['run_summary','native_receipt']:pin(ROOT/r[stem+'_path'],r[stem+'_sha256']);eq(pg['inputs_sha256'][r[stem+'_path']],r[stem+'_sha256'],'direct proof receipt binding')
            tr=r['trace'];pin(ROOT/tr['path'],tr['sha256']);eq((ROOT/tr['path']).stat().st_size,tr['bytes'],'whole proof size');proof_bytes+=tr['bytes'];eq(pg['inputs_sha256'][tr['path']],tr['sha256'],'direct complete proof binding')
            receipt=PG.parent/(r['replay']['name']+'.receipt.json');eq(read(receipt),r['replay'],'literal replay receipt')
            log=PG.parent/(r['replay']['name']+'.stdout.log');err=PG.parent/(r['replay']['name']+'.stderr.log');eq(sha(log),r['replay']['stdout_sha256'],'replay stdout hash');eq(sha(err),r['replay']['stderr_sha256'],'replay stderr hash');need('s VERIFIED'in log.read_text(encoding='utf8').splitlines(),'complete accepted replay log')
            scope=read(ROOT/e['scope_path']);profile=read(ROOT/e['profile_path']);scope_contract(scope,m,raw);eq(profile['coordinate_group_fibre_counts'],scope['coordinate_group_fibre_counts'],'same selected raw profile');eq(scope['groups'],groups,'same support group order');eq(scope['group_columns'],cols,'same actual raw columns')
            v=flat(scope['coordinate_group_fibre_counts']);eq(digest(v),r['full_count_profile_sha256'],'same raw full count hash');eq(min(images(v)),v,'literal canonical table');vectors.append(v);base_classes=signatures(v);eq(base_classes,cr['canonical_initial_domain_class_ids'],'canonical complete class IDs')
            model=read(ROOT/e['model_path'])
            for g,d in enumerate(model['domains']):
                actual=sorted(triple_ids[tuple(word_ids[tuple(w)]for w in c['colour_words'])]for c in d['choices']);eq(actual,classes[base_classes[g]]['ranks'],'actual encoded full initial domain')
            ims=[]
            for saved,act in zip(cr['images'],actions):
                p=tuple(act['pull_fibre_permutation']);w=image(v,p);eq(saved['pull_fibre_permutation'],list(p),'image action identity');eq(saved['full_counts_flat'],list(w),'all literal transformed count entries');eq(saved['labelled_count_sha256'],digest(w),'image hash');target=signatures(w);eq(saved['initial_domain_class_ids'],target,'image initial domain classes');covariance(base_classes,target,p,act);eq(image(w,inverse(p)),v,'inverse count action')
                ims.append(dict(pull_fibre_permutation=list(p),inverse_pull_fibre_permutation=list(inverse(p)),count_table_flat=list(w),count_table_sha256=digest(w),initial_domain_class_ids=target))
            eq(len(ims),6,'saved image coverage');eq({bytes(i['count_table_flat'])for i in ims},images(v),'exact orbit set')
            records.append(dict(case_id=cid,case_index=r['case_index'],subset_index=r['subset_index'],canonical_count_sha256=digest(v),proof_cnf_path=e['cnf_path'],proof_cnf_sha256=e['cnf_sha256'],scope_path=e['scope_path'],scope_sha256=e['scope_sha256'],trace=tr,replay=r['replay'],images=ims))
        union=unique_orbits(vectors);eq(len(union),72,'computed union cardinality');eq(proof_bytes,pg['proof_bytes'],'full trace byte total')
        entire={bytes(im['full_counts_flat'])for row in coverage['records']for im in row['images']};need(union<=entire,'images belong to authenticated population');eq(len(entire),4752,'literal complete population size')
        reject('duplicate canonical proof',lambda:unique_orbits(vectors+[vectors[0]]));damage=copy.deepcopy(records[0]['images']);damage[-1]=copy.deepcopy(damage[0]);reject('duplicate image',lambda:eq({bytes(x['count_table_flat'])for x in damage},images(vectors[0]),'complete image set'))
        damage=copy.deepcopy(records[0]['images'][0]);damage['count_table_flat'][0]^=1;reject('changed image counts',lambda:eq(bytes(damage['count_table_flat']),image(vectors[0],damage['pull_fibre_permutation']),'raw action'))
        s=read(ROOT/encoded[selected[0]]['scope_path']);s['cross_group_column_caps_encoded']=True;reject('changed exclusion scope',lambda:scope_contract(s,universe[selected[0]],raw))
        ac=copy.deepcopy(actions[1]);ac['triple_image'][classes[signatures(vectors[0])[0]]['ranks'][0]]=-1;reject('changed complete domain transport',lambda:covariance(signatures(vectors[0]),signatures(image(vectors[0],tuple(ac['pull_fibre_permutation']))),tuple(ac['pull_fibre_permutation']),ac))
        histories=[];historical_sets={}
        for label,(p,h)in HIST.items():
            pin(p,h);v=flat(read(p)['coordinate_group_fibre_counts']);ims=images(v);canonical=min(ims);historical_sets[label]=ims
            histories.append(dict(label=label,path=key(p),sha256=h,literal_count_sha256=digest(v),canonical_count_sha256=digest(canonical),literal_in_first12_canonical_tables=v in set(vectors),literal_in_excluded_labelled_union=v in union,canonical_in_all792=('exact_eight_'+digest(canonical))in universe,orbit_size=len(ims),labelled_intersection_with_union_sha256=sorted(digest(x)for x in ims&union),canonical_first12_matches=[records[j]['case_id']for j,x in enumerate(vectors)if x in ims],all_orbit_count_sha256=sorted(digest(x)for x in ims)))
        prior=historical_sets['prior_single_pilot'];eq(len(prior&union),6,'earlier pilot orbit repeats first batch');eq(histories[0]['canonical_first12_matches'],pg['prior_literal_overlap']['matching_case_ids'],'independent prior comparison')
        pairwise=[dict(left=a,right=b,shared_labelled_count_sha256=sorted(digest(x)for x in historical_sets[a]&historical_sets[b]))for a,b in it.combinations(HIST,2)]
        save(out/'proved_labelled_union.json',dict(complete=True,canonical_count=12,labelled_count=len(union),records=records,sorted_labelled_count_sha256=sorted(digest(x)for x in union)))
        save(out/'historical_comparisons.json',dict(records=histories,pairwise_historical_intersections=pairwise,comparison_only=True,additional_exclusion_premises=False,historical_claims_summed=False,prior_pilot_distinct_canonical_overlap=1,new_canonical_profiles_beyond_prior_pilot=11))
        save(out/'controls.json',dict(rejected=bad,balanced_profile_orbit_size=1,all_real_image_inverse_checks=72,selected_domain_bijections=1440,proof_bytes_authenticated=proof_bytes,DRAT_replays_this_audit=0))
        elapsed=time.monotonic()-start;need(elapsed<120,'120s audit allocation');stamp=datetime.now(timezone.utc).isoformat();cid='C-FIXED-HADAMARD-EXACT-EIGHT-FIRST12-FIBRE-IMAGE-EXCLUSIONS'
        summary=dict(status='INDEPENDENT_EXACT_EIGHT_FIRST12_FIBRE_UNION_PASS',created_at=stamp,command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},claim_id=cid,claim_revision=1,canonical_profiles_excluded=12,labelled_profiles_excluded=len(union),complete_population_canonical=792,complete_population_labelled=4752,prior_pilot_canonical_overlap=1,historical_comparisons=histories,proof_bytes_authenticated=proof_bytes,controls_rejected=len(bad),native_calls=0,new_DRAT_replays=0,elapsed_seconds=elapsed,scope='Exactly the explicitly enumerated72 labelled count tables of12 canonical profiles, on the fixed support with full prescribed Gram and within-triplicate caps. No other count-profile or target exclusion.',method='Compose separately authenticated complete literal proof/encoding gates with literal fibre actions, inverse maps, complete initial-domain transports and exact raw-table set comparisons; no producer imports.',artifact_availability='LOCAL_ONLY')
        save(out/'summary.json',summary)
        binding=dict(id=cid,revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='No binary36x60 factor on the fixed six-prism Hadamard support with full prescribed integer Gram and within-triplicate column caps has any of the72 distinct labelled count tables explicitly obtained by global fibre relabelling of the twelve independently proved first-batch canonical profiles. These72 tables form exactly twelve disjoint six-element orbits; the prior single-pilot orbit is one of these twelve.',scope=summary['scope'],assumptions=['Pinned fixed core/support/Gram and exactly-eight count population; complete initial local domains.','Global fibre and equal-support column relabelling, with no target automorphism assumption.'],dependencies=[dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-FIRST12-LITERAL-PROFILE-EXCLUSIONS',revision=1,relation='uses_result'),dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-CAMPAIGN-FIBRE-COVERAGE',revision=1,relation='normalization'),dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-CAMPAIGN-FIRST12-GRAM-ENCODINGS',revision=1,relation='encoding_equivalence')],verifier='/root/state_literature_audit',method=summary['method'],created_at=stamp,updated_at=stamp,verification=dict(report=key(out/'summary.json'),report_sha256=sha(out/'summary.json'),source=key(SRC),source_sha256=sha(SRC),status=summary['status']),evidence=[key(out/'summary.json'),key(out/'proved_labelled_union.json'),key(out/'historical_comparisons.json'),key(DOC)],limitations=['No complete792 exclusion.','Historical comparisons do not add exclusions or assume their scopes.','No cross-group caps or residualD premise is needed for this already weaker factor exclusion.','No new solver or DRAT replay; prior independently verified proof gate is a premise.'],artifact_availability='LOCAL_ONLY')
        save(out/'claim_binding.json',binding);print(json.dumps(dict(status=summary['status'],summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'),seconds=elapsed)))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=pins));raise
if __name__=='__main__':main()
