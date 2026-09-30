"""Independent wave28 registration/report/record consistency; no producer imports."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import argparse,copy,hashlib,json,re,sys,time,traceback,yaml
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
CP=B+'resume/twentyeighth_milestone_checkpoint.json';SNAP=B+'resume/claims_at_twentyeighth_milestone.yaml';OLD=B+'resume/claims_at_twentyseventh_milestone.yaml';REPORT='docs/RESEARCH_20260930_TWENTYEIGHTH_WAVE.md'
PINS={CP:'87eed00b74925fc752375a1aaa4884eeb4221fef4b499ec7767a8bb03ba9875a',SNAP:'c2889537ea68b90736a5d51e13b6aafd6163b9a1e98d2f05eb1bd6e4331cf441',OLD:'5ea04f21e5964b6f987d00a600a69d4472bfebdd0fea7f564e4dfec1af5cb237',REPORT:'32eebbebb8518743c6d5591899e3a4caf07998f8f37bc74dba18ac39f704b571'}
REGS=['initial_registration','kernel_sizeclass_registration','sizeclass_proof_registration','launcher_refutation_registration']
GATES=['exact_eight_next32_cnfs','exact_eight_next32_proofs','exact_eight_first12_union_v2','exact_eight_sizeclass16_cnfs_v2','exact_eight_kernel_redundancy','exact_eight_sizeclass16_proofs','parallel_build_deadline_binding','windows_job_assignment_race_binding']
PINS.update({'acceleration/audit_20260930_twentyeighth_checkpoint.py':'26c57f7ca6f838efd35f4fb2cc03fd391a455747b26750e9e96f14d2022ea91e','acceleration/audit_20260930_twentyeighth_checkpoint_spec.md':'a6354dbd8cc495eb077338563b355ce4ae83ab1ce6f1a993eb53caf3f68cc29e',I+'twentyeighth_checkpoint/failure.json':'dd5fec5a14053696b429476038be02d7811a4a2c7d3c2826ee0e593ecc07de4f'})
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
def bind(d):
    for p,h in d.items():eq(sha(p),h,'hash '+p)
def load(p):sha(p);return json.loads(path(p).read_bytes())
def yload(p):sha(p);return yaml.safe_load(path(p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def indexed(xs):
    d={x['id']:x for x in xs};eq(len(d),len(xs),'unique IDs');return d
def binding_check(c,b,allclaims):
    for k in ['id','revision','statement','kind','status']:eq(c[k],b[k],'binding '+k)
    eq(c['revision'],1,'new revision1');eq(c['review_state'],'CLEAR','clear review');eq(c['basis'],b['basis']if isinstance(b['basis'],list)else[b['basis']],'basis')
    ds=[dict(id=d.get('id',d.get('claim_id')),revision=d['revision'],relation=d['relation'])for d in b['dependencies']];eq(c['dependencies'],ds,'dependencies');eq(c['scope']['description'],b['scope']['description']if isinstance(b['scope'],dict)else b['scope'],'scope');eq(c['scope']['target_resolution'],'NONE','no target result');eq(c['external_source'],None,'no external review')
    for d in ds:need(d['id']in allclaims and allclaims[d['id']]['revision']==d['revision'],'exact dependency revision')
def checks(c,proofs,union,kernel):
    eq((c['claim_population'],c['claim_status_counts'],c['claim_review_counts']),(294,dict(VERIFIED=287,CANDIDATE=3,REFUTED=4),dict(CLEAR=294)),'population/status');eq(len(set(c['new_verified_ids'])),6,'six V');eq(len(set(c['new_refuted_ids'])),2,'two R');eq(c['new_candidate_ids'],[],'no new candidate');eq(c['target_resolution'],'UNKNOWN','target unknown');eq(c['external_review'],None,'no external review')
    need(all(c[k]==0 for k in ['new_complete99_graphs','new_unrestricted_exclusions','new_whole_support_exclusions']),'no broader resolution')
    ids=[]
    for row,p,n,size in zip(c['literal_batches'],proofs,[12,32,16],[56815018,105031599,37502220]):
        actual=[r['case_id']for r in p['case_records']];eq(len(actual),n,'literal batch cardinality');eq(len(set(actual)),n,'literal batch distinctness');eq(p['completed_proof_replays'],n,'complete replay count');eq(p['proof_bytes'],size,'proof byte count');eq(p['UNKNOWN'],0,'no UNKNOWN');eq(p.get('SAT_verified',p.get('SAT_pending')),0,'no SAT');eq(p.get('pending_case_ids',[]),[],'no pending')
        for k in ['selected','attempted','completed','UNSAT','independent_complete_proof_replays']:eq(row[k],n,'checkpoint batch '+k)
        for k in ['SAT','UNKNOWN','errors']:eq(row[k],0,'checkpoint batch '+k)
        eq(row['proof_bytes'],size,'checkpoint batch bytes');ids+=actual
    eq(len(set(ids)),60,'three batches disjoint');z=c['literal_campaign'];eq(z['excluded_case_ids'],ids,'ordered complete literal union');eq((z['population'],z['distinct_literal_exclusions'],z['unresolved'],z['new_literal_exclusions']),(792,60,732,48),'literal counts')
    u=c['first12_fibre_union'];eq((u['canonical_cases'],u['distinct_labelled_images'],u['new_DRAT_replays'],u['overlap_with_prior_pilot']),(12,72,0,1),'only first12 image union');eq((union['canonical_profiles_excluded'],union['labelled_profiles_excluded'],union['prior_pilot_canonical_overlap'],union['new_DRAT_replays']),(12,72,1,0),'raw union metrics')
    for k,v in dict(profiles=792,kernel_dimension=14,initial_options=1687356,removed_options=0).items():eq(c['common_kernel'][k],v,'checkpoint kernel '+k);eq(kernel[k],v,'raw kernel '+k)
    eq(c['excluded_future_cohort'],['exact_eight_next64','four_chunk_suspended_launcher'],'next cohort omitted')
    return ids
def report_check(text,c,claims):
    rows=re.findall(r'^\| (C-[A-Z0-9-]+) r(\d+) \| (VERIFIED|REFUTED) \|',text,re.M);eq(rows,[(cid,'1',claims[cid]['status'])for cid in c['new_verified_ids']+c['new_refuted_ids']],'exact report claims')
    markers=['target resolution UNKNOWN','earlier claim statements and verification records remain unchanged','add48 distinct exclusions','105,031,599 and37,502,220 bytes','completed22 formulas','ten-case continuation','contains60 of the frozen792 canonical campaign cases;732 remain unresolved','72 distinct labelled count-table exclusions','later48 literal cases are not included in that image-union count','zero of1,687,356 initial options','294 ledger claims:287 VERIFIED/CLEAR, three CANDIDATE/CLEAR and four REFUTED/CLEAR','not equal fractions of graphs, computational difficulty or time remaining','neither whole-support nonexistence nor unrestricted nonexistence follows','not escaped historical research runs or invalid mathematical proofs','never establish universal containment','Next64 selection and replacement suspended-launch preparation are outside this checkpoint']
    for m in markers:need(m in text,'report scope marker '+m)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bad=[]
    def reject(label,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):bad.append(label);return
        raise ValueError('accepted corruption '+label)
    try:
        bind(PINS)
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:sha(p.relative_to(ROOT).as_posix())
        c=load(CP);bind(c['evidence_sha256']);eq(sha('acceleration/record_20260930_twentyeighth_checkpoint.py'),c['writer_sha256'],'writer');eq(sha(B+'resume/twentyseventh_milestone_checkpoint.json'),c['previous_checkpoint_sha256'],'previous checkpoint');eq(c['ledger_snapshot_sha256'],PINS[SNAP],'snapshot')
        old,final=yload(OLD),yload(SNAP);oc,fc=indexed(old['claims']),indexed(final['claims']);eq((len(oc),len(fc)),(286,294),'old/final population');need(all(fc.get(k)==v for k,v in oc.items()),'all286 old claim records unchanged')
        first=B+'twentyeighth_initial_registration/CLAIMS.before.yaml';initial=yload(first);need(all(initial[k]==old[k]for k in old if k not in ['updated_at','artifacts']),'prior science unchanged');oa,ia=indexed(old['artifacts']),indexed(initial['artifacts']);eq(set(oa),set(ia),'prior artifacts same set');published=[]
        for k in oa:
            if oa[k]==ia[k]:continue
            need(set(oa[k])==set(ia[k])and all(oa[k][f]==ia[k][f]for f in oa[k]if f not in ['availability','retrieval','unavailable_reason']),'only prior publication metadata differs');eq((oa[k]['availability'],ia[k]['availability'],ia[k]['unavailable_reason']),('LOCAL_ONLY','PUBLIC',None),'prior publication transition');eq(ia[k]['retrieval'],'https://github.com/ikuto32/conway-99-graph/blob/ad1bebcff23e7f331941293a26bf4446d837ebda/'+ia[k]['path'],'immutable published retrieval');published.append(k)
        eq(len(published),19,'19 prior publication updates');prior=path(first).read_bytes();chain=[];added=[]
        eq(c['registration_chain'],[B+'twentyeighth_'+r for r in REGS],'exact ordered registration paths')
        for r in REGS:
            d=B+'twentyeighth_'+r+'/';s=load(d+'summary.json');bind({d+'CLAIMS.before.yaml':s['previous_ledger_sha256'],d+'CLAIMS.after.yaml':s['ledger_sha256']});eq(path(d+'CLAIMS.before.yaml').read_bytes(),prior,'literal byte chain');before,after=yload(d+'CLAIMS.before.yaml'),yload(d+'CLAIMS.after.yaml');bc,ac=indexed(before['claims']),indexed(after['claims']);ba,aa=indexed(before['artifacts']),indexed(after['artifacts']);need(all(ac.get(k)==v for k,v in bc.items())and all(aa.get(k)==v for k,v in ba.items()),'prior records unchanged in registrar');eq(set(ac)-set(bc),set(s['new_claim_ids']),'new IDs exact');source=next(p for p in s['command']if p.startswith('acceleration/')and p.endswith('.py'));eq(sha(source),s['registrar_sha256'],'registrar bytes');need(s['validation']['valid']is True,'saved validation valid');added+=s['new_claim_ids'];prior=path(d+'CLAIMS.after.yaml').read_bytes();chain.append(dict(path=d,before=len(bc),after=len(ac),new_ids=s['new_claim_ids'],source=source,summary_sha256=INPUTS[d+'summary.json']))
        eq(prior,path(SNAP).read_bytes(),'exact final snapshot');eq(added,c['new_verified_ids']+c['new_refuted_ids'],'exact chronological additions');eq(Counter(x['status']for x in final['claims']),c['claim_status_counts'],'computed statuses');eq(Counter(x['review_state']for x in final['claims']),c['claim_review_counts'],'computed reviews')
        arts=indexed(final['artifacts']);bs={};claims=[]
        for n in GATES:
            p=I+n+'/claim_binding.json';b=load(p);bs[b['id']]=(b,p)
        for cid in added:
            cl=fc[cid];b,bp=bs[cid];binding_check(cl,b,fc);ev=[arts[a]for a in cl['evidence']];need(all(a['availability']=='LOCAL_ONLY'for a in ev),'new evidence not publicly asserted');bind({a['path']:a['sha256']for a in ev});need(bp in {a['path']for a in ev},'binding evidence');eq(len(cl['verification']),1,'one current verification');v=cl['verification'][0];eq((v['claim_revision'],v['outcome']),(1,'PASS'if cl['status']=='VERIFIED'else'FAIL'),'verification revision/outcome');need(v['command_or_audit']in {a['path']for a in ev},'verification named evidence');eq(v['artifact_hashes'],{a['id']:a['sha256']for a in ev},'verification exact artifact hashes');claims.append(dict(id=cid,status=cl['status'],statement=cl['statement'],scope=cl['scope'],dependencies=cl['dependencies'],verification=v,evidence={a['path']:a['sha256']for a in ev}))
        proofs=[load(row['summary_path'])for row in c['literal_batches']]
        for row in c['literal_batches']:eq(INPUTS[row['summary_path']],row['summary_sha256'],'checkpoint exact proof gate')
        union=load(I+'exact_eight_first12_union_v2/summary.json');kernel=load(I+'exact_eight_kernel_redundancy/summary.json');ids=checks(c,proofs,union,kernel);bind(union['outputs_sha256']);rawunion=load(I+'exact_eight_first12_union_v2/proved_labelled_union.json');eq((rawunion['complete'],rawunion['canonical_count'],rawunion['labelled_count']),(True,12,72),'literal saved union');eq([r['case_id']for r in rawunion['records']],ids[:12],'only first12 union records');eq(len(set(rawunion['sorted_labelled_count_sha256'])),72,'72 distinct saved image hashes')
        manifest=load(B+'exact_eight_campaign_preparation/campaign_manifest.json');mids={r['case_id']:r for r in manifest['records']};eq(len(mids),792,'manifest distinct792');tables=[];proofbytes=0;proof_records=[]
        for gate,row in zip(proofs,c['literal_batches']):
            need(gate['status'].endswith('_PASS'),'proof audit pass');folder=str(Path(row['summary_path']).parent).replace('\\','/')
            for r in gate['case_records']:
                need(r['case_id']in mids,'literal universe member');eq(r['full_count_profile_sha256'],mids[r['case_id']]['full_count_profile_sha256'],'raw profile binding')
                for stem in ['cnf','scope','run_summary','native_receipt']:bind({r[stem+'_path']:r[stem+'_sha256']})
                tr=r['trace'];bind({tr['path']:tr['sha256']});eq(path(tr['path']).stat().st_size,tr['bytes'],'complete host trace bytes');proofbytes+=tr['bytes'];rp=r['replay'];need(tr['complete_proof']and rp['accepted']and rp['actual_exit_code']==0,'complete recorded checker acceptance');eq((rp['proof_sha256'],rp['cnf_sha256']),(tr['sha256'],r['cnf_sha256']),'exact proof/formula replay')
                for suffix in ['stdout','stderr']:bind({folder+'/'+rp['name']+'.'+suffix+'.log':rp[suffix+'_sha256']})
                need('s VERIFIED'in path(folder+'/'+rp['name']+'.stdout.log').read_text(encoding='utf8'),'actual saved checker verdict');sc=load(r['scope_path']);t=sc['coordinate_group_fibre_counts'];digest=hashlib.sha256(bytes(v for a in t for g in a for v in g)).hexdigest();eq(digest,r['full_count_profile_sha256'],'literal table hash');tables.append(t);need(sc['within_group_column_caps_encoded']and not sc['cross_group_column_caps_encoded']and not sc['residual_D_encoded'],'literal scope omissions');proof_records.append(dict(case_id=r['case_id'],count_sha256=digest,proof=tr,replay_sha256=rp['proof_sha256']))
        reject('wrong JSON serialization digest',lambda:eq(hashlib.sha256(json.dumps(tables[0],separators=(',',':')).encode()).hexdigest(),proofs[0]['case_records'][0]['full_count_profile_sha256'],'raw bytes required'));eq(len({json.dumps(t,separators=(',',':'))for t in tables}),60,'60 different raw tables');eq(proofbytes,199348837,'60 complete saved proof bytes');pilot=load(B+'exact_eight_next_lift/scope.json');eq(sum(t==pilot['coordinate_group_fibre_counts']for t in tables),1,'prior pilot counted once')
        # Verify raw engineering counterexample metrics, without rerunning processes.
        dl=load(I+'parallel_build_deadline/summary.json');eq((dl['positive_zero_delay_cancelled_at'],dl['delayed_cleanup_cancelled_at'],dl['deadline'],dl['real_process_calls']),(1.0,5.025,1.0,0),'simulation distinction');race=load(I+'windows_job_assignment_race/summary.json');eq((race['observed_escaped_applications'],race['actual_owned_handles'],race['real_research_processes']),(3,6,0),'live harmless interleaving only');need(all(race[k]==dl[k]==0 for k in ['native_calls','formula_builds']),'no research execution in countercontrols')
        ex=c['execution'];eq((ex['state'],ex['exit_code']),('NO_CADICAL_PROCESS_OBSERVED',1),'saved native observation');need('-C'in ex['command']and ex['command'][ex['command'].index('-C')+1]=='cadical','targeted process scope')
        for suffix in ['stdout','stderr']:bind({B+'resume/twentyeighth_process_snapshot.'+suffix+'.log':ex[suffix+'_sha256']})
        need(len(path(B+'resume/twentyeighth_process_snapshot.stdout.log').read_bytes().splitlines())<=1,'no saved process row');text=path(REPORT).read_text(encoding='utf8');report_check(text,c,fc)
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if target.startswith('https://'):continue
            p=(path(REPORT).parent/target).resolve();need(p.is_relative_to(ROOT)and p.is_file(),'report link exists');sha(p.relative_to(ROOT).as_posix())
        mutations=[('population',['claim_population'],295),('verified count',['claim_status_counts','VERIFIED'],288),('refuted count',['claim_status_counts','REFUTED'],2),('target',['target_resolution'],'SOLVED'),('whole support',['new_whole_support_exclusions'],1),('literal multiplicity',['literal_campaign','distinct_literal_exclusions'],61),('unresolved',['literal_campaign','unresolved'],731),('unreviewed images',['first12_fibre_union','distinct_labelled_images'],360),('kernel pruning',['common_kernel','removed_options'],1)]
        for label,ks,value in mutations:
            q=copy.deepcopy(c);t=q
            for k in ks[:-1]:t=t[k]
            t[ks[-1]]=value;reject(label,lambda q=q:checks(q,proofs,union,kernel))
        p=copy.deepcopy(proofs);p[1]['case_records'][0]['case_id']=p[0]['case_records'][0]['case_id'];reject('cross-batch duplicate',lambda:checks(c,p,union,kernel))
        for label,field,value in [('statement','statement','global target exclusion'),('status','status','VERIFIED'),('revision','revision',2)]:
            cl=copy.deepcopy(fc[added[-1]]);cl[field]=value;reject('binding '+label,lambda cl=cl:binding_check(cl,bs[added[-1]][0],fc))
        reject('report implied broader union',lambda:report_check(text.replace('later48 literal cases are not included in that image-union count','later48 literal cases are included in that image-union count'),c,fc));reject('report mathematical invalidation',lambda:report_check(text.replace('not escaped historical research runs or invalid mathematical proofs','escaped historical research runs and invalid mathematical proofs'),c,fc))
        save(out/'checked_records.json',dict(chain=chain,claims=claims,prior_publication_artifacts=published,literal_records=proof_records,first12_image_hashes=rawunion['sorted_labelled_count_sha256'],controls_rejected=bad,process_observation='Saved timestamp only; no current process assertion.'))
        elapsed=time.monotonic()-start;need(elapsed<120,'bounded metadata review');summary=dict(status='INDEPENDENT_TWENTYEIGHTH_CHECKPOINT_CONSISTENCY_PASS',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),registration_transitions=4,total_claims=294,status_counts=c['claim_status_counts'],new_verified=6,new_refuted=2,old_claims_unchanged=286,prior_publication_only_artifacts=19,distinct_literal_cases=60,new_literal_cases=48,unresolved_canonical_cases=732,first12_labelled_images_only=72,complete_saved_proof_bytes_authenticated=proofbytes,common_kernel_initial_options=1687356,common_kernel_removed=0,controls_rejected=bad,report_scope_approved=True,scientific_reverification=False,catalog_approval=False,limits=dict(native_calls=0,formula_calls=0,DRAT_replays=0,ledger_changes=0),inputs_sha256=INPUTS,outputs_sha256={str((out/'checked_records.json').relative_to(ROOT)).replace('\\','/'):hashlib.sha256((out/'checked_records.json').read_bytes()).hexdigest()},elapsed_seconds=elapsed);save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],sha256=sha((out/'summary.json').relative_to(ROOT)),seconds=elapsed)))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=INPUTS));raise
if __name__=='__main__':main()
