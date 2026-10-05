"""Independent frozen checkpoint/report/registration consistency, no producer imports."""
import argparse,copy,hashlib,json,re,sys,time,traceback
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
CP=B+'resume/twentyseventh_milestone_checkpoint.json';SNAP=B+'resume/claims_at_twentyseventh_milestone.yaml';OLD=B+'resume/claims_at_twentysixth_milestone.yaml';REPORT='docs/RESEARCH_20260930_TWENTYSEVENTH_WAVE.md';PSD='C-FIXED-HADAMARD-EXACT-EIGHT-SURVIVOR-PSD-SCREEN'
PINS={CP:'ee5fb89ff01a69d3c7e6cb61809906a5ef4804dedb5890c2469e2412b687991c',SNAP:'5ea04f21e5964b6f987d00a600a69d4472bfebdd0fea7f564e4dfec1af5cb237',OLD:'8bcdad8f4b2e871b6c0bdf6ef72736033a8d84624af029e1b01c2951bc4b8146',REPORT:'764890cfb3c28510d6bd2e7295662f24ce2973b0eb513aed06e3fbc399db8596'}
REGS=['pilot_registration','psd_candidate_registration','campaign_gates_registration','psd_promotion','first12_proof_registration','inventory_registration']
GATES=['exact_eight_next_lift','exact_eight_next_lift_unsat','triplicate_psd_kernel_options','exact_eight_psd_screen','exact_eight_campaign','exact_eight_campaign_coverage_v2','exact_eight_first12_proofs','exact_eight_campaign_inventory']
INPUTS={}
def need(x,m):
    if not x:raise ValueError(m)
def eq(a,b,m):need(a==b,m)
def path(p):
    p=str(p).replace('\\','/');need('PROMPT.md'not in p and not p.startswith('tools/')and p!=I+'hadamard_oriented_unknown/process.stdout.log','protected input');q=(ROOT/p).resolve();need(q.is_relative_to(ROOT),'path escape');return q
def sha(p):
    q=path(p)
    with q.open('rb')as f:v=hashlib.file_digest(f,'sha256').hexdigest()
    INPUTS[q.relative_to(ROOT).as_posix()]=v;return v
def bind(m):
    for p,h in m.items():eq(sha(p),h,'hash '+p)
def load(p):sha(p);return json.loads(path(p).read_bytes())
def yload(p):sha(p);return yaml.safe_load(path(p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def indexed(xs):
    d={x['id']:x for x in xs};eq(len(d),len(xs),'unique IDs');return d
def binding_check(c,b,allclaims):
    eq(c['id'],b.get('id',b.get('claim_id')),'bound claim ID');eq(c['revision'],b['revision'],'bound revision');eq(c['status'],b.get('status',b.get('status_recommendation')),'bound status');eq(c['review_state'],'CLEAR','clear review')
    for f in ['statement','kind']:eq(c[f],b[f],'bound '+f)
    eq(c['basis'],b['basis']if isinstance(b['basis'],list)else[b['basis']],'basis schema normalization')
    ds=[dict(id=d.get('id',d.get('claim_id')),revision=d['revision'],relation=d['relation'])for d in b['dependencies']];eq(c['dependencies'],ds,'exact dependencies');eq(c['scope']['description'],b['scope'],'exact scope');eq(c['scope']['target_resolution'],'NONE','no target result')
    for d in ds:need(d['id']in allclaims and allclaims[d['id']]['revision']==d['revision'],'resolved dependency revision')
    eq(c['external_source'],None,'no external review promoted')
def check_cp(c,g):
    eq(c['claim_population'],286,'claim population');eq(c['claim_status_counts'],dict(VERIFIED=281,CANDIDATE=3,REFUTED=2),'statuses');eq(c['claim_review_counts'],dict(CLEAR=286),'review states');eq(len(set(c['new_verified_ids'])),8,'eight new V');eq(c['new_candidate_ids'],[],'no final new candidate');eq(c['new_refuted_ids'],[],'no new refuted')
    eq(c['promoted_revisions'],{PSD:{'from':1,'to':2}},'single promotion');eq(c['target_resolution'],'UNKNOWN','target unknown');eq(c['external_review'],None,'external review null')
    need(all(c[k]==0 for k in['new_complete99_graphs','new_unrestricted_exclusions','new_whole_support_exclusions']),'no target/unrestricted/support result')
    p=g['exact_eight_first12_proofs'];z=c['literal_campaign']
    expected=dict(selected=12,attempted=12,completed=12,UNSAT=12,UNKNOWN=0,SAT=0,errors=0,complete_independent_proof_replays=12,proof_bytes=p['proof_bytes'],distinct_literal_cases=12,overlap_with_preceding_single_pilot=1,additional_beyond_single_pilot=11,scope='Literal full-Gram instances only. No orbit or historical-profile union exclusion is inferred.')
    eq(z,expected,'exact literal campaign scope');eq(p['completed_proof_replays'],12,'raw proof count');eq(p['proof_bytes'],56815018,'raw proof size');eq(p['UNKNOWN'],0,'raw no UNKNOWN');eq(p['SAT_pending'],0,'raw no SAT')
    ps=g['exact_eight_psd_screen'];eq(c['psd'],dict(canonical_profiles=792,PSD=792,rank=22,excluded=0,exact_arithmetic='rational certificates independently checked by integer congruences'),'792 PSD checkpoint');eq((ps['canonical_profiles'],ps['PSD_profiles'],ps['excluded_profiles'],ps['rank_counts']),(792,792,0,{'22':792}),'independent PSD metrics')
    inv=g['exact_eight_campaign_inventory'];eq(c['inventory'],dict(canonical_profiles=792,initial_domains=15840,size_classes=16,actual_saved_formulas=16,actual_campaign_formulas=12,historical_formula_controls=4,unbuilt_dimensions='Conditional recipe estimates only'),'inventory scope');eq((inv['cases'],inv['initial_domains'],len(inv['formula_dimension_distribution']),inv['actual_formula_measurements'],inv['actual_first12'],inv['historical_controls']),(792,15840,16,16,12,4),'actual inventory metrics')
    kernel=g['triplicate_psd_kernel_options'];eq(len(kernel['results']),3,'three historical kernel profiles');eq((kernel['total_options'],kernel['total_removed']),(6444,0),'no local pruning')
    cov=g['exact_eight_campaign_coverage_v2'];eq((cov['canonical_profiles'],cov['labelled_profiles'],cov['exclusions']),(792,4752,0),'coverage not exclusion')
    eq(c['excluded_future_cohort'],['exact_eight_next32','first12_orbit_union'],'future cohorts excluded')
def report_check(text,c,claims):
    rows=re.findall(r'^\| (C-[A-Z0-9-]+) r(\d+) \|',text,re.M);eq(rows,[(cid,str(claims[cid]['revision']))for cid in c['new_verified_ids']],'exact report table order/revisions')
    markers=['286 ledger claims:281 VERIFIED/CLEAR, three CANDIDATE/CLEAR, two REFUTED/CLEAR','target resolution UNKNOWN','PSD screening was first registered CANDIDATE at revision1 and promoted only after independent checking at revision2','All56,815,018 proof bytes','11 additional distinct exclusions beyond that pilot','must not be summed as13 distinct cases','Every matrix R=3G-NN^T is positive semidefinite of rank22','only three historical profiles','is not promoted to all792 profiles','conditional relabelling argument, not an exclusion by itself','Formula dimensions for unbuilt cases are conditional recipe estimates','No whole-support or unrestricted exclusion was added.','first12 orbit-union audit are later-wave work']
    for m in markers:need(m in text,'report scope marker '+m)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bad=[]
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):bad.append(name);return
        raise ValueError('accepted corruption '+name)
    try:
        bind(PINS)
        for p in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:sha(p.relative_to(ROOT).as_posix())
        c=load(CP);bind(c['evidence_sha256']);eq(sha('acceleration/record_20260930_twentyseventh_checkpoint.py'),c['writer_sha256'],'checkpoint writer');eq(sha(B+'resume/twentysixth_milestone_checkpoint.json'),c['previous_checkpoint_sha256'],'previous checkpoint');eq(c['ledger_snapshot_sha256'],PINS[SNAP],'frozen ledger identity')
        old,final=yload(OLD),yload(SNAP);oc,fc=indexed(old['claims']),indexed(final['claims']);need(len(oc)==278 and len(fc)==286 and all(fc.get(k)==v for k,v in oc.items()),'all prior278 claims unchanged')
        initial=yload(B+'twentyseventh_pilot_registration/CLAIMS.before.yaml');eq(set(initial),set(old),'prior root schema');need(all(initial[k]==old[k]for k in old if k not in['updated_at','artifacts']),'prior scientific records unchanged')
        oa,ia=indexed(old['artifacts']),indexed(initial['artifacts']);eq(set(oa),set(ia),'prior artifact population');published=[]
        for k in oa:
            if oa[k]==ia[k]:continue
            need(set(oa[k])==set(ia[k])and all(oa[k][f]==ia[k][f]for f in oa[k]if f not in['availability','retrieval','unavailable_reason']),'publication only changes')
            eq((oa[k]['availability'],ia[k]['availability'],ia[k]['unavailable_reason']),('LOCAL_ONLY','PUBLIC',None),'availability publication direction');eq(ia[k]['retrieval'],'https://github.com/ikuto32/conway-99-graph/blob/046b4eab2514a344cfbe948f9907bb631ac8dbb0/'+ia[k]['path'],'immutable prior publication URL');published.append(k)
        eq(len(published),22,'22 prior artifacts published');prior=path(B+'twentyseventh_pilot_registration/CLAIMS.before.yaml').read_bytes();chain=[];added=[];promotion=None
        for name in REGS:
            d=B+'twentyseventh_'+name+'/';s=load(d+'summary.json');bind({d+'CLAIMS.before.yaml':s['previous_ledger_sha256'],d+'CLAIMS.after.yaml':s['ledger_sha256']});eq(path(d+'CLAIMS.before.yaml').read_bytes(),prior,'exact registry byte chain');before,after=yload(d+'CLAIMS.before.yaml'),yload(d+'CLAIMS.after.yaml');bc,ac=indexed(before['claims']),indexed(after['claims']);ba,aa=indexed(before['artifacts']),indexed(after['artifacts'])
            source=next(v for v in s['command']if v.startswith('acceleration/')and v.endswith('.py'));eq(sha(source),s['registrar_sha256'],'frozen registrar source');need(s['validation']['valid']is True,'registrar validation receipt')
            if name=='psd_promotion':
                eq(set(ac),set(bc),'promotion adds no statement');changed=[k for k in bc if bc[k]!=ac[k]];eq(changed,[PSD],'only PSD revision changed');r1,r2=bc[PSD],ac[PSD]
                for field in['id','statement','scope','assumptions','dependencies','created_at','kind','basis']:eq(r1[field],r2[field],'preserved promotion '+field)
                eq((r1['revision'],r1['status'],r1['verification']),(1,'CANDIDATE',[]),'actual candidate r1');eq((r2['revision'],r2['status']),(2,'VERIFIED'),'actual independently verified r2');eq(s['dependent_claims'],[],'no stale dependent revisions')
                for k in ba:
                    if ba[k]==aa[k]:continue
                    need(k.startswith('twentyseventh-psd-candidate-evidence'),'only candidate availability explanation');eq({f:v for f,v in ba[k].items()if f!='unavailable_reason'},{f:v for f,v in aa[k].items()if f!='unavailable_reason'},'candidate raw identity preserved')
                promotion=dict(id=PSD,from_revision=1,to_revision=2,statement_unchanged=True,before_sha256=s['previous_ledger_sha256'],after_sha256=s['ledger_sha256'])
            else:
                need(all(ac.get(k)==v for k,v in bc.items())and all(aa.get(k)==v for k,v in ba.items()),'existing records unchanged');eq(set(ac)-set(bc),set(s['new_claim_ids']),'exact additions');added.extend(s['new_claim_ids'])
                if name=='psd_candidate_registration':eq((ac[PSD]['revision'],ac[PSD]['status'],ac[PSD]['verification']),(1,'CANDIDATE',[]),'candidate not prematurely verified')
                else:need(s['registrar_performs_mathematical_verification']is False,'metadata registrar boundary')
            prior=path(d+'CLAIMS.after.yaml').read_bytes();chain.append(dict(name=name,before=len(bc),after=len(ac),summary_sha256=INPUTS[d+'summary.json'],source=source,new_ids=s.get('new_claim_ids',[])))
        eq(prior,path(SNAP).read_bytes(),'final exact snapshot');eq(added,c['new_verified_ids'],'new final verified IDs');eq(Counter(x['status']for x in final['claims']),c['claim_status_counts'],'actual statuses');eq(Counter(x['review_state']for x in final['claims']),c['claim_review_counts'],'actual review states')
        arts=indexed(final['artifacts']);claims=[];g={n:load(I+n+'/summary.json')for n in GATES};bindings={}
        for n in GATES:
            b=load(I+n+'/claim_binding.json');bindings[b.get('id',b.get('claim_id'))]=(b,I+n+'/summary.json',I+n+'/claim_binding.json')
        for cid in added:
            cl=fc[cid];b,rp,bp=bindings[cid];binding_check(cl,b,fc);v=cl['verification'];eq(len(v),1,'single valid current verification');eq((v[0]['claim_revision'],v[0]['outcome'],v[0]['command_or_audit']),(cl['revision'],'PASS',rp),'verification exact revision/report')
            ev=[arts[a]for a in cl['evidence']];need(all(a['availability']=='LOCAL_ONLY'for a in ev),'new evidence not yet published');bind({a['path']:a['sha256']for a in ev});need({rp,bp}<={a['path']for a in ev},'both raw audit/binding evidence')
            evmap={a['id']:a['sha256']for a in ev if a['path']in[rp,bp]};eq(v[0]['artifact_hashes'],evmap,'exact current verification hashes');need(load(rp)['status'].endswith('_PASS'),'actual independent gate PASS');claims.append(dict(id=cid,revision=cl['revision'],statement=cl['statement'],scope=cl['scope'],dependencies=cl['dependencies'],evidence={a['path']:a['sha256']for a in ev},scientific_reverification=False))
        check_cp(c,g)
        pg=g['exact_eight_first12_proofs'];native=load(B+'exact_eight_first12_native_pilot/summary.json');eq(sha(B+'exact_eight_first12_native_pilot/summary.json'),pg['inputs_sha256'][B+'exact_eight_first12_native_pilot/summary.json'],'proof consumes actual batch');eq(native['native_calls'],12,'actual attempts');eq(native['pending_case_ids'],[],'actual no pending');eq(native['stop_reason'],'ALL_FIRST12_ATTEMPTED','actual terminal batch');eq(native['automatic_retry'],False,'no automatic retry')
        literal=[];proofbytes=0
        for r in pg['case_records']:
            for stem in['cnf','scope','run_summary','native_receipt']:bind({r[stem+'_path']:r[stem+'_sha256']})
            trace=r['trace'];bind({trace['path']:trace['sha256']});eq(path(trace['path']).stat().st_size,trace['bytes'],'complete retained proof bytes');proofbytes+=trace['bytes'];need(trace['complete_proof']and r['replay']['accepted']and r['replay']['actual_exit_code']==0,'complete independent proof acceptance');eq(r['replay']['proof_sha256'],trace['sha256'],'accepted exact proof');eq(r['replay']['cnf_sha256'],r['cnf_sha256'],'accepted exact formula')
            for suffix in['stdout','stderr']:bind({I+'exact_eight_first12_proofs/'+r['replay']['name']+'.'+suffix+'.log':r['replay'][suffix+'_sha256']})
            need('s VERIFIED'in path(I+'exact_eight_first12_proofs/'+r['replay']['name']+'.stdout.log').read_text(encoding='utf8'),'saved complete checker verdict');scope=load(r['scope_path']);literal.append(scope['coordinate_group_fibre_counts']);need(scope['within_group_column_caps_encoded']and not scope['cross_group_column_caps_encoded']and not scope['residual_D_encoded'],'literal proof omission scope')
        eq(proofbytes,c['literal_campaign']['proof_bytes'],'actual byte sum');need(len({json.dumps(x)for x in literal})==12,'12 distinct literal raw count tables');pilot=load(B+'exact_eight_next_lift/scope.json');eq(sum(x==pilot['coordinate_group_fibre_counts']for x in literal),1,'raw prior pilot overlap')
        ex=c['execution'];eq(ex['state'],'NO_CADICAL_PROCESS_OBSERVED','saved process observation');eq(ex['exit_code'],1,'ps no exact-name process');need('-C'in ex['command']and ex['command'][ex['command'].index('-C')+1]=='cadical','targeted process command')
        for suffix in['stdout','stderr']:bind({B+'resume/twentyseventh_process_snapshot.'+suffix+'.log':ex[suffix+'_sha256']})
        need(len(path(B+'resume/twentyseventh_process_snapshot.stdout.log').read_bytes().splitlines())<=1,'no saved process rows')
        failures=[I+'exact_eight_campaign_coverage/failure.json',B+'exact_eight_population_inventory/failure.json',B+'exact_eight_campaign_native_preparation/failure.json',B+'exact_eight_campaign_native_preparation/correction_setup_failure.json'];failure_records=[]
        for p in failures:
            x=load(p);need(x.get('error')is not None,'preserved preparation failure');failure_records.append(dict(path=p,sha256=INPUTS[p],error=x['error']))
        correction=load(B+'exact_eight_population_inventory/correction.json');eq(correction['change'],'Add missing local same-fibre1/different-fibre2 Gram bounds to raw catalogue reconstruction, preserving full overlap-cap check.','local predicate correction');eq(correction['native_calls'],0,'no native inventory calls');nativefix=load(B+'exact_eight_campaign_native_preparation/correction.json');eq(nativefix['native_calls'],0,'native source correction only');load(B+'exact_eight_campaign_native_preparation_v2/summary.json')
        text=path(REPORT).read_text(encoding='utf8');report_check(text,c,fc)
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if target.startswith('https://'):continue
            q=(path(REPORT).parent/target).resolve();need(q.is_relative_to(ROOT)and q.is_file(),'report local link');sha(q.relative_to(ROOT).as_posix())
        mutations=[('claim count',['claim_population'],287),('status',['claim_status_counts','VERIFIED'],282),('target',['target_resolution'],'SOLVED'),('support exclusion',['new_whole_support_exclusions'],1),('double-count pilot',['literal_campaign','distinct_literal_cases'],13),('missed overlap',['literal_campaign','overlap_with_preceding_single_pilot'],0),('PSD population',['psd','canonical_profiles'],3),('PSD rank',['psd','rank'],23),('inventory actuals',['inventory','actual_saved_formulas'],792),('PSD promotion revision',['promoted_revisions',PSD,'to'],1)]
        for name,ks,value in mutations:
            damaged=copy.deepcopy(c);t=damaged
            for k in ks[:-1]:t=t[k]
            t[ks[-1]]=value;reject(name,lambda damaged=damaged:check_cp(damaged,g))
        sample=fc[added[0]];sb=bindings[added[0]][0]
        for name,field,value in [('claim statement','statement','a broader exclusion'),('claim dependency','dependencies',[]),('claim revision','revision',2)]:
            damaged=copy.deepcopy(sample);damaged[field]=value;reject(name,lambda damaged=damaged:binding_check(damaged,sb,fc))
        reject('report all792 kernel extension',lambda:report_check(text.replace('is not promoted to all792 profiles','applies to all792 profiles'),c,fc));reject('report thirteen instances',lambda:report_check(text.replace('must not be summed as13 distinct cases','supply13 distinct cases'),c,fc))
        save(out/'checked_records.json',dict(registration_chain=chain,promotion=promotion,claims=claims,previous_publication_only_artifacts=published,preserved_failures=failure_records,controls_rejected=bad,process_observation_scope='Saved timestamp only; no current process assertion.',catalog_approval=False))
        elapsed=time.monotonic()-start;need(elapsed<120,'bounded checkpoint audit');result=dict(status='INDEPENDENT_TWENTYSEVENTH_CHECKPOINT_CONSISTENCY_PASS',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),registration_transitions=6,new_verified=8,total_claims=286,status_counts=c['claim_status_counts'],old_claims_unchanged=278,previous_publication_only_artifacts=22,PSD_candidate_r1_to_verified_r2_statement_unchanged=True,scientific_reverification=False,complete_saved_proof_bytes_authenticated=proofbytes,distinct_literal_cases=12,prior_pilot_overlap=1,report_scope_approved=True,future_union_excluded=True,controls_rejected=bad,inputs_sha256=INPUTS,outputs_sha256={str((out/'checked_records.json').relative_to(ROOT)).replace('\\','/'):hashlib.sha256((out/'checked_records.json').read_bytes()).hexdigest()},limits=dict(native_calls=0,solver_calls=0,DRAT_replays=0,ledger_changes=0,catalog_approval=False),elapsed_seconds=elapsed)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha((out/'summary.json').relative_to(ROOT)),seconds=elapsed)))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=INPUTS));raise
if __name__=='__main__':main()
