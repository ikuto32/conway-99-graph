"""Independent wave29 registry/checkpoint consistency, without science reruns."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse, copy, hashlib, json, re, sys, time, traceback, yaml

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'; N='acceleration/results/20261001_'
I=B+'independent_review/'; J=N+'independent_review/'
CP=N+'resume/twentyninth_milestone_checkpoint.json'
SNAP=N+'resume/claims_at_twentyninth_milestone.yaml'
REPORT='docs/RESEARCH_20261001_TWENTYNINTH_WAVE.md'
OLD=B+'resume/claims_at_twentyeighth_milestone.yaml'
OLDCP=B+'resume/twentyeighth_milestone_checkpoint.json'
MAN=B+'exact_eight_campaign_preparation/campaign_manifest.json'
REGS=[B+'twentyninth_initial_registration',N+'twentyninth_followup_registration']
GF3=I+'sizeclass16_gf3_affine_weights/summary.json'
UNIFORM=J+'exact_eight_uniform_gram/summary.json'
PROOFS=[(I+n+'/summary.json',count,pin) for n,count,pin in [
 ('exact_eight_first12_proofs',12,'a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9'),
 ('exact_eight_next32_proofs',32,'21ee1b189c8b250eabcaedad43a79b9025978d540a1480f1c03eaeb446acee4c'),
 ('exact_eight_sizeclass16_proofs',16,'04d47a627081f42def048826f08bdf2574eff67479275d46112033bf994e4494'),
 ('exact_eight_next64_proofs',64,'7e2cab83b264a30e35a5797137b4948fb59d30e1b1b234ed5ab54e517c13881f')]]
PINS={OLD:'c2889537ea68b90736a5d51e13b6aafd6163b9a1e98d2f05eb1bd6e4331cf441',
 OLDCP:'87eed00b74925fc752375a1aaa4884eeb4221fef4b499ec7767a8bb03ba9875a',
 MAN:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',
 GF3:'232a38f1a761915f1c5308a1597f9f7ba121dd9372198a7b5a0b6ff55b125834',
 UNIFORM:'c911f7a0d9156c12e91491061f96eb691e1f7d8360f862e5cf45bd7114cff38e',
 I+'exact_eight_first12_union_v2/summary.json':'9ce71dea74e323a4f06d20cdf50c80ca75ce0b26d0c7feb18d54f928eb116726'}
IDS=[
 'C-FIXED-HADAMARD-EXACT-EIGHT-NEXT64-GRAM-ENCODINGS',
 'C-FIXED-HADAMARD-EXACT-EIGHT-NEXT64-LITERAL-PROFILE-EXCLUSIONS',
 'C-FIXED-HADAMARD-SIZECLASS16-GF3-AFFINE-GRAM-WITNESSES',
 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH02-GRAM-ENCODINGS',
 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH02-LITERAL-PROFILE-EXCLUSIONS',
 'C-FIXED-HADAMARD-EXACT-EIGHT-UNIFORM-GRAM-MIXTURE-FAILURES']
INPUTS={}

def need(x,m):
    if not x: raise ValueError(m)

def eq(x,y,m): need(x==y,m)

def path(name):
    q=Path(name);q=q.resolve() if q.is_absolute() else(ROOT/q).resolve()
    need(q.is_relative_to(ROOT),'repository containment');r=q.relative_to(ROOT).as_posix()
    need(q.name!='PROMPT.md' and not r.startswith('tools/') and r!=I+'hadamard_oriented_unknown/process.stdout.log','protected path')
    need('exact_eight_prefix64_batch03' not in r,'future cohort excluded')
    return q

def sha(name):
    if isinstance(name,str) and name in INPUTS:return INPUTS[name]
    q=path(name);r=q.relative_to(ROOT).as_posix()
    if r not in INPUTS:
        with q.open('rb') as f:INPUTS[r]=hashlib.file_digest(f,'sha256').hexdigest()
    return INPUTS[r]

def bind(pins):
    for p,h in pins.items():eq(sha(p),h,'input hash '+str(p))

def load(p):sha(p);return json.loads(path(p).read_bytes())
def ledger(p):sha(p);return yaml.safe_load(path(p).read_bytes())

def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def index(rows):
    d={r['id']:r for r in rows};eq(len(d),len(rows),'unique registry IDs');return d

def binding_check(cl,b,claims):
    for key in ['id','revision','statement','kind','basis','status','assumptions','created_at','updated_at']:
        eq(cl[key],b[key],'bound claim '+key)
    eq((cl['revision'],cl['status'],cl['review_state']),(1,'VERIFIED','CLEAR'),'new verified revision1')
    eq(cl['scope'],dict(description=b['scope'],unrestricted_target=False,target_resolution='NONE'),'exact restricted scope')
    eq(cl['dependencies'],b['dependencies']+b.get('verification_dependencies',[]),'exact typed dependencies')
    eq(cl['limitations'],b.get('limitations',[b['scope']]),'exact limitations')
    for d in cl['dependencies']:
        p=claims[d['id']];eq((p['revision'],p['status'],p['review_state']),(d['revision'],'VERIFIED','CLEAR'),'trusted current premise')
    v=cl['verification'][0];eq(v['shared_components'],b['shared_components'],'shared checking components')
    eq(v['verifier'],b['verifier'],'actual independent verifier');need(b['method'] in v['controls'],'verbatim checking method retained')
    if cl['id']==IDS[2]:need('rank' not in cl['statement'].lower() and 'no rank' in cl['scope']['description'].lower(),'GF3 witness only')

def metrics(c,proofs):
    eq((c['claim_population'],c['claim_status_counts'],c['claim_review_counts']),
       (300,dict(VERIFIED=293,CANDIDATE=3,REFUTED=4),dict(CLEAR=300)),'300 exact statuses')
    eq(c['new_verified_ids'],IDS,'six exact new verified IDs');eq(c['new_candidate_ids'],[],'no new candidate');eq(c['new_refuted_ids'],[],'no new refutation')
    eq(c['target_resolution'],'UNKNOWN','target unknown');eq(c['external_review'],None,'no external review')
    need(all(c[k]==0 for k in ['new_complete99_graphs','new_whole_support_exclusions','new_unrestricted_exclusions']),'no target/support promotion')
    eq(len(c['literal_batches']),5,'five literal batches');need(len(proofs)==5,'five complete proof gates');ids=[];sizes=[]
    for cp,proof,n in zip(c['literal_batches'],proofs,[12,32,16,64,64]):
        rs=proof['case_records'];actual=[r['case_id'] for r in rs]
        eq(len(rs),n,'actual case count');eq(len(set(actual)),n,'within-batch uniqueness')
        eq(proof['completed_proof_replays'],n,'complete replay count');eq(proof['pending_case_ids'],[],'no pending')
        eq(proof['UNKNOWN'],0,'no UNKNOWN');eq(proof.get('SAT_verified',proof.get('SAT_pending')),0,'no SAT')
        for k in ['selected','attempted','completed','independent_complete_proof_replays','UNSAT']:eq(cp[k],n,'checkpoint count '+k)
        for k in ['SAT','UNKNOWN','errors']:eq(cp[k],0,'checkpoint count '+k)
        size=sum(r['trace']['bytes'] for r in rs);eq(cp['proof_bytes'],size,'checkpoint trace bytes');eq(proof['proof_bytes'],size,'proof report bytes')
        ids+=actual;sizes.append(size)
    eq(len(set(ids)),188,'cross-batch disjointness');z=c['literal_campaign']
    eq(z['excluded_case_ids'],ids,'ordered exact literal IDs')
    eq((z['population'],z['distinct_literal_exclusions'],z['unresolved'],z['new_literal_exclusions']),(792,188,604,128),'finite coverage counts')
    g=c['gf3_witnesses'];eq((g['profiles'],g['residue_entries'],g['affine_normalizations'],g['rank_checked']),(16,20736,320,False),'GF3 witnesses only')
    u=c['uniform_diagnostic'];eq((u['profiles'],u['uniform_witnesses'],u['uniform_counterexamples']),(792,0,792),'uniform counterexamples only')
    need('not adjudicated' in u['scope'],'arbitrary convex weights undecided')
    eq(c['excluded_future_cohort'],['exact_eight_prefix64_batch03'],'future excluded')
    return ids,sizes

def report_check(text,c,claims,sizes):
    rows=re.findall(r'^\| (C-[A-Z0-9-]+) r(\d+) \| (.+) \|$',text,re.M)
    eq([(a,b) for a,b,_ in rows],[(cid,'1')for cid in IDS],'six exact report rows')
    for cid,_,body in rows:need(body.startswith(claims[cid]['scope']['description']+' [Evidence]'),'verbatim bound report scope')
    markers=['target resolution UNKNOWN','Two new 64-case batches add 128 distinct literal exclusions',
        'The two algebraic diagnostics add no exclusions.','Earlier claim records remain unchanged.',
        'disjoint union of 188 cases','604 remain unresolved','72 explicitly checked labelled tables',
        'No sixfold expansion is applied to the later cases','historical overlapping exclusions are not added',
        '20,736 residues and 320 group normalizations','does not verify the producer\'s rank claim',
        'not complete matrix rechecks; unequal convex weights can still be possible',
        '300 claims: 293 VERIFIED/CLEAR, three CANDIDATE/CLEAR and four REFUTED/CLEAR',
        'does not measure fractions of graphs, computational difficulty or remaining runtime',
        'No whole-support or unrestricted nonexistence follows.','Later batch03 work is outside this cutoff.',
        'finite launcher controls are not a universal operating-system guarantee',
        f'{sum(sizes[-2:]):,} bytes',c['execution']['state']]
    for marker in markers:need(marker in text,'report scope marker '+marker)

def main():
    ap=argparse.ArgumentParser()
    for name in ['checkpoint','report','ledger','initial-summary','followup-summary']:
        ap.add_argument('--'+name+'-sha256',required=True)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();need(out.is_relative_to(ROOT),'contained output');out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();bad=[]
    def reject(label,fn):
        try:fn()
        except(ValueError,KeyError,TypeError,IndexError):bad.append(label);return
        raise ValueError('accepted corrupted metadata '+label)
    try:
        bind(PINS);bind({CP:args.checkpoint_sha256,REPORT:args.report_sha256,SNAP:args.ledger_sha256,
                        REGS[0]+'/summary.json':args.initial_summary_sha256,REGS[1]+'/summary.json':args.followup_summary_sha256})
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:sha(p)
        c=load(CP);eq(c['ledger_snapshot_sha256'],args.ledger_sha256,'checkpoint snapshot pin');bind(c['evidence_sha256'])
        bind({'acceleration/record_20261001_twentyninth_checkpoint.py':c['writer_sha256']})
        eq(c['previous_checkpoint_sha256'],PINS[OLDCP],'previous checkpoint')
        old,final=ledger(OLD),ledger(SNAP);oc,fc=index(old['claims']),index(final['claims']);eq((len(oc),len(fc)),(294,300),'old/new populations')
        need(all(fc.get(k)==v for k,v in oc.items()),'all294 old claim records unchanged')
        first=ledger(REGS[0]+'/CLAIMS.before.yaml');need(all(first[k]==old[k]for k in old if k not in ['updated_at','artifacts']),'publication leaves science unchanged')
        oa,fa=index(old['artifacts']),index(first['artifacts']);eq(set(oa),set(fa),'same pre-registration artifacts');published=[]
        for aid in oa:
            if oa[aid]==fa[aid]:continue
            need(set(oa[aid])==set(fa[aid])and all(oa[aid][k]==fa[aid][k] for k in oa[aid] if k not in ['availability','retrieval','unavailable_reason']),'only publication metadata changed')
            eq((oa[aid]['availability'],fa[aid]['availability'],fa[aid]['unavailable_reason']),('LOCAL_ONLY','PUBLIC',None),'actual publication transition')
            eq(fa[aid]['retrieval'],'https://github.com/ikuto32/conway-99-graph/blob/c35d3e885e674d44b35dd0bf55eedead9f764ac3/'+fa[aid]['path'],'immutable wave28 evidence URL');published.append(aid)
        eq(len(published),16,'sixteen prior evidence availability updates')
        prior=path(REGS[0]+'/CLAIMS.before.yaml').read_bytes();chain=[];added=[]
        eq(c['registration_chain'],[dict(directory=d,summary_sha256=sha(d+'/summary.json'))for d in REGS],'exact two registration receipts')
        for i,d in enumerate(REGS):
            s=load(d+'/summary.json');bp,ap=d+'/CLAIMS.before.yaml',d+'/CLAIMS.after.yaml'
            bind({bp:s['previous_ledger_sha256'],ap:s['ledger_sha256']});eq(path(bp).read_bytes(),prior,'continuous byte chain')
            before,after=ledger(bp),ledger(ap);bc,ac=index(before['claims']),index(after['claims']);ba,aa=index(before['artifacts']),index(after['artifacts'])
            need(all(ac.get(k)==v for k,v in bc.items())and all(aa.get(k)==v for k,v in ba.items()),'registrar preserves all previous records')
            eq(s['new_claim_ids'],IDS[i*3:i*3+3],'three exact additions in order');eq(set(ac)-set(bc),set(s['new_claim_ids']),'only expected additions')
            eq((len(bc),len(ac)),(294+3*i,297+3*i),'294 to297 to300')
            need(s['validation']['valid'] and not s['registrar_performs_mathematical_verification'],'registration validation only')
            source=next(p for p in s['command'] if p.startswith('acceleration/')and p.endswith('.py'))
            expected=s.get('registrar_sha256',s['checked_input_bindings'].get(source));eq(sha(source),expected,'exact executed registrar source')
            # Only the authenticated historical live-ledger reference is mapped
            # to this receipt's before-snapshot. No other alias is admitted.
            for p,h in s['checked_input_bindings'].items():
                actual=bp if p=='CLAIMS.yaml'and h==s['previous_ledger_sha256'] else p
                bind({actual:h})
            added+=s['new_claim_ids'];prior=path(ap).read_bytes();chain.append(dict(directory=d,source=source,before=len(bc),after=len(ac)))
        eq(prior,path(SNAP).read_bytes(),'final snapshot byte identity');eq(added,IDS,'exact six additions')
        arts=index(final['artifacts']);reviewed=[];reports_by_claim={}
        for cid in IDS:
            cl=fc[cid];ev=[arts[a] for a in cl['evidence']];need(len(ev)==2 and all(a['availability']=='LOCAL_ONLY'for a in ev),'two new local evidence artifacts')
            bind({a['path']:a['sha256']for a in ev});bp=next(a['path']for a in ev if a['path'].endswith('/claim_binding.json'));b=load(bp);binding_check(cl,b,fc)
            v=cl['verification'][0];eq(len(cl['verification']),1,'one independent verification');eq((v['claim_revision'],v['outcome']),(1,'PASS'),'bound verification')
            eq(v['artifact_hashes'],{a['id']:a['sha256']for a in ev},'verification exact evidence hashes');need(v['command_or_audit']in {a['path']for a in ev},'actual evidence report')
            q=load(v['command_or_audit']);need(q['status'].startswith('INDEPENDENT_')and q['status'].endswith('_PASS'),'actual independent PASS')
            eq(v['timestamp'],q.get('timestamp',q.get('created_at')),'actual verification time');reports_by_claim[cid]=(v['command_or_audit'],q)
            reviewed.append(dict(id=cid,statement=cl['statement'],scope=cl['scope'],dependencies=cl['dependencies'],binding_path=bp,evidence={a['path']:a['sha256']for a in ev}))
        proof_specs=PROOFS+[(reports_by_claim[IDS[4]][0],64,sha(reports_by_claim[IDS[4]][0]))]
        proofs=[]
        for cp,(p,n,h) in zip(c['literal_batches'],proof_specs):bind({p:h});eq((cp['summary_path'],cp['summary_sha256']),(p,h),'checkpoint proof gate');proofs.append(load(p))
        ids,sizes=metrics(c,proofs);eq(load(OLDCP)['literal_campaign']['excluded_case_ids'],ids[:60],'previous60 reused once')
        universe={r['case_id']:r for r in load(MAN)['records']};eq(len(universe),792,'literal manifest population')
        raw_records=[];tables=set();proofbytes=0
        for proof,cp in zip(proofs,c['literal_batches']):
            folder=cp['summary_path'].rsplit('/',1)[0]
            for r in proof['case_records']:
                u=universe[r['case_id']];eq(u['full_count_profile_sha256'],r['full_count_profile_sha256'],'exact manifest profile')
                for stem in ['cnf','scope','run_summary','native_receipt']:bind({r[stem+'_path']:r[stem+'_sha256']})
                tr,rp=r['trace'],r['replay'];bind({tr['path']:tr['sha256']});eq(path(tr['path']).stat().st_size,tr['bytes'],'entire retained host trace')
                need(r['outcome']=='UNSAT_VERIFIED'and tr['complete_proof']and rp['accepted']and rp['actual_exit_code']==0,'saved complete proof acceptance')
                eq((rp['proof_sha256'],rp['cnf_sha256']),(tr['sha256'],r['cnf_sha256']),'saved exact replay inputs')
                for suffix in ['stdout','stderr']:bind({folder+'/'+rp['name']+'.'+suffix+'.log':rp[suffix+'_sha256']})
                need('s VERIFIED' in path(folder+'/'+rp['name']+'.stdout.log').read_text(encoding='utf8'),'literal saved checker result')
                scope=load(r['scope_path']);t=scope['coordinate_group_fibre_counts'];need(len(t)==12 and all(len(row)==20 and all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)for v in row)for row in t),'strict raw count shape')
                raw720=bytes(x for row in t for v in row for x in v);eq(hashlib.sha256(raw720).hexdigest(),r['full_count_profile_sha256'],'720-byte raw identity')
                eq(t,u['raw_representative']['counts'],'full raw manifest equality');tables.add(raw720)
                need(scope['within_group_column_caps_encoded']and not scope['cross_group_column_caps_encoded']and not scope['residual_D_encoded'],'precise literal formula scope')
                proofbytes+=tr['bytes'];raw_records.append(dict(case_id=r['case_id'],count_sha256=r['full_count_profile_sha256'],trace=tr))
        eq(len(tables),188,'188 different literal raw count tables');eq(proofbytes,sum(sizes),'whole saved trace bytes')
        gf3=load(GF3);uniform=load(UNIFORM);eq((gf3['cases'],gf3['residue_entries'],gf3['affine_normalizations']),(16,20736,320),'authentic GF3 audit counts')
        eq((uniform['profiles'],uniform['independent_nonzero_entries'],uniform['uniform_witnesses'],uniform['arbitrary_convex_feasibility']),(792,792,0,'UNKNOWN'),'uniform-only independent result')
        bind(uniform['outputs_sha256']);witnesses=load(J+'exact_eight_uniform_gram/literal_counterexamples.json')
        eq({r['case_id']for r in witnesses},set(universe),'all792 saved counterexamples');need(all(r['nonzero_residual'][0]!=0 and r['nonzero_residual'][1]>0 for r in witnesses),'recorded nonzero residuals')
        union=load(I+'exact_eight_first12_union_v2/summary.json');eq((union['canonical_profiles_excluded'],union['labelled_profiles_excluded']),(12,72),'only existing first12 image union')
        ex=c['execution'];need('-C'in ex['command']and ex['command'][ex['command'].index('-C')+1]=='cadical','targeted process scope')
        for suffix in ['stdout','stderr']:bind({N+'resume/twentyninth_process_snapshot.'+suffix+'.log':ex[suffix+'_sha256']})
        lines=path(N+'resume/twentyninth_process_snapshot.stdout.log').read_bytes().splitlines()
        state='CADICAL_PROCESS_OBSERVED'if ex['exit_code']==0 else 'NO_CADICAL_PROCESS_OBSERVED'if ex['exit_code']==1 and len(lines)<=1 else 'UNKNOWN_OBSERVATION_ERROR'
        eq(ex['state'],state,'saved observation only')
        text=path(REPORT).read_text(encoding='utf8');report_check(text,c,fc,sizes)
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if target.startswith('https://'):continue
            q=(path(REPORT).parent/target).resolve();need(q.is_relative_to(ROOT)and q.is_file(),'report local link');sha(q)
        mutations=[('claim count',['claim_population'],301),('verified count',['claim_status_counts','VERIFIED'],294),('target',['target_resolution'],'SOLVED'),('whole support',['new_whole_support_exclusions'],1),('literal count',['literal_campaign','distinct_literal_exclusions'],189),('unresolved',['literal_campaign','unresolved'],603),('rank promotion',['gf3_witnesses','rank_checked'],True),('uniform witness',['uniform_diagnostic','uniform_witnesses'],1)]
        for label,keys,value in mutations:
            q=copy.deepcopy(c);d=q
            for k in keys[:-1]:d=d[k]
            d[keys[-1]]=value;reject(label,lambda q=q:metrics(q,proofs))
        p=copy.deepcopy(proofs);p[-1]['case_records'][0]['case_id']=p[0]['case_records'][0]['case_id'];reject('cross-batch duplication',lambda:metrics(c,p))
        cl=copy.deepcopy(fc[IDS[2]]);cl['statement']+=' Rank193 is verified.';binding=load(next(arts[a]['path']for a in fc[IDS[2]]['evidence']if arts[a]['path'].endswith('/claim_binding.json')));reject('unreviewed statement extension',lambda:binding_check(cl,binding,fc))
        reject('wrong raw hash codec',lambda:eq(hashlib.sha256(json.dumps(next(iter(tables)).hex()).encode()).hexdigest(),raw_records[0]['count_sha256'],'raw bytes only'))
        reject('expanded image union',lambda:report_check(text.replace('No sixfold expansion is applied to the later cases','A sixfold expansion is applied to later cases'),c,fc,sizes))
        reject('convex infeasibility wording',lambda:report_check(text.replace('not complete matrix rechecks; unequal convex weights can still be possible','complete matrix rechecks; no unequal convex weights are possible'),c,fc,sizes))
        reject('future path',lambda:path(N+'exact_eight_prefix64_batch03_native/summary.json'))
        reject('private path',lambda:path(I+'hadamard_oriented_unknown/process.stdout.log'))
        save(out/'checked_records.json',dict(registration_chain=chain,claims=reviewed,published_artifacts=published,literal_records=raw_records,controls_rejected=bad))
        need(time.monotonic()-start<120,'120-second metadata allocation')
        result=dict(status='INDEPENDENT_TWENTYNINTH_CHECKPOINT_CONSISTENCY_PASS',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),total_claims=300,status_counts=c['claim_status_counts'],registration_transitions=2,new_verified=6,old_claims_unchanged=294,prior_publication_only_artifacts=16,distinct_literal_cases=188,new_literal_cases=128,unresolved_cases=604,complete_saved_proof_bytes_authenticated=proofbytes,gf3_witness_profiles=16,gf3_rank_checked=False,uniform_counterexample_profiles=792,arbitrary_convex_feasibility='UNKNOWN',first12_labelled_images_only=72,controls_rejected=bad,inputs_sha256=INPUTS,outputs_sha256={(out/'checked_records.json').relative_to(ROOT).as_posix():hashlib.sha256((out/'checked_records.json').read_bytes()).hexdigest()},scientific_reverification=False,catalog_approval=False,native_calls=0,DRAT_replays=0,ledger_changes=0,elapsed_seconds=time.monotonic()-start)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],sha256=hashlib.sha256((out/'summary.json').read_bytes()).hexdigest(),seconds=result['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=INPUTS));raise

if __name__=='__main__':main()
