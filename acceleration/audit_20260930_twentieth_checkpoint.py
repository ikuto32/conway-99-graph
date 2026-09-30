"""Independent frozen wave20 claim/report/publication coherence; no proof rerun."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys
from audit_20260930_sixteenth_checkpoint import read_ledger,require,sha,write

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
CP=B+'resume/twentieth_milestone_checkpoint.json';SNAP=B+'resume/claims_at_twentieth_milestone.yaml'
GEN='acceleration/record_20260930_twentieth_checkpoint.py';REPORT='docs/RESEARCH_20260930_TWENTIETH_WAVE.md'
GUIDE='docs/REPRODUCING_20260930_TWENTIETH_WAVE.md';PACK=B+'twentieth_artifact_packaging/'
PREVIOUS='4442207abbe24effffefb56ab323e3891bc3fafd'
PRIVATE=I+'hadamard_oriented_unknown/process.stdout.log'
PROOF=B+'hadamard_balanced_gram_native_pilot/main/proof.drat'
CNF=B+'hadamard_balanced_gram_cnf/instance.cnf'
PH='94d2ab35c76b61f3deb01ebfd9ca0dc70452bddf847383d5838b2b2ca902396b'
CH='c2d780f94dac4dda955743df03f8db2e8ec0f51217c671eb19fc5e42ed69ba37'
IDS=['C-FIXED-HADAMARD-ALL-MIXED-ORIENTED-TRIPLE-ENCODING','C-FIXED-HADAMARD-ORIENTED-TRIPLE-NATIVE-UNKNOWN',
     'C-FIXED-HADAMARD-COMPLETE-BALANCED-GRAM-ENCODING','C-FIXED-HADAMARD-BALANCED-GRAM-EXCLUSION',
     'C-FIXED-HADAMARD-AT-MOST-TWO-GROUP-MARGIN-CANCELLATION','C-FIXED-HADAMARD-SUPPORT-INTERSECTIONS-ZERO-OR-THREE']
LOCAL={B+'hadamard_balanced_gram_caps/clauses.cnfpart',B+'hadamard_balanced_gram_caps/instance.cnf',PROOF,
       B+'hadamard_oriented_triples_native_pilot/main/proof.drat',PRIVATE}

def check_counts(cp,ledger):
    require(cp['claim_population']==len(ledger['claims'])==194,'claim population')
    require(cp['claim_status_counts']==dict(Counter(c['status'] for c in ledger['claims']))==dict(VERIFIED=191,CANDIDATE=2,REFUTED=1),'exact three status populations')
    require(cp['claim_review_counts']==dict(Counter(c['review_state'] for c in ledger['claims']))==dict(CLEAR=194),'review population')
    require((cp['verified_clear'],cp['candidate_clear'],cp['refuted_clear'])==(191,2,1),'clear totals')
    require(cp['new_verified_ids']==IDS[:-1] and cp['new_refuted_ids']==IDS[-1:] and cp['evidence_only_revision_changes']==[],'six exact new records')
    require(cp['target_resolution']=='UNKNOWN' and cp['external_review'] is None and cp['external_review_null_reason'],'target and external review')
    require(cp['coverage']=='Overall search coverage: UNKNOWN; no validated denominator.','no target coverage percentage')
    require(cp['native_attempts']==dict(attempted=2,completed=2,sat=0,unsat=1,unknown=1,errors=0),'two separate native outcomes')
    require(cp['balanced_encoding']==dict(variables=10480,clauses=74200,groups=20,normalized_choices_per_group=150),'complete balanced local universe')
    require(cp['balanced_proof']==dict(raw_sha256=PH,raw_bytes=227098316,complete_independent_replay=True,
        independent_gate=I+'hadamard_balanced_gram_unsat_v2/summary.json',native_conflicts=248698,native_wall_seconds=22.19),'complete narrow proof')
    require(cp['proof_transport']==dict(parts=6,compressed_bytes=52339920,raw_bytes=227098316,
        independent_gate=I+'hadamard_balanced_proof_packages/summary.json'),'proof transport counts')
    require(cp['oriented_outcome']==dict(status='UNKNOWN',conflicts=1000000,incomplete_trace_bytes=331620166,trace_availability='LOCAL_ONLY'),'partial oriented trace is not proof')
    require(cp['cancelled_cap_preparation']==dict(build_completed=True,independent_encoding_approval=False,native_attempts=0),'unapproved completed cap build')
    require(cp['new_balanced_fixed_support_family_exclusions']==1,'one balanced subfamily exclusion')
    for key in ['new_full_factors','complete99_graphs','new_whole_support_exclusions','new_core_exclusions','new_unrestricted_exclusions']:
        require(cp[key]==0,'no broader resolution '+key)

def check_privacy(entries,stage):
    bypath={r['path']:r for r in entries}
    require(len(bypath)==len(entries),'unique catalog paths')
    require({p for p,r in bypath.items() if r['availability']=='LOCAL_ONLY'}==LOCAL,'five explicit local exclusions')
    require(bypath[PRIVATE]['availability']=='LOCAL_ONLY' and 'OMIT' in bypath[PRIVATE]['limitation'],'private stdout metadata only')
    require(not(LOCAL & set(stage)),'local excluded paths absent from staging')
    require(all(r['availability'] in ['LOCAL_ONLY','READY_FOR_PUBLICATION'] for r in entries),'no implied current publication')

def check_proof(gate,transport):
    require(gate['status']=='INDEPENDENT_FIXED_HADAMARD_BALANCED_GRAM_UNSAT_PASS' and gate['claim_id']==IDS[3] and gate['claim_revision']==1,'independent proof premise')
    require(gate['proof']['complete_independent_replay'] is True and gate['proof']['sha256']==PH and gate['proof']['bytes']==227098316,'complete proof identity')
    require(gate['inputs_sha256'][CNF]==CH and gate['inputs_sha256'][PROOF]==PH,'proof exact formula binding')
    replay=next(r for r in gate['replays'] if r['name']=='complete_research_proof')
    require(replay['actual_exit_code']==0 and replay['accepted'] is True and replay['cnf_sha256']==CH and replay['proof_sha256']==PH,'complete accepted replay receipt')
    controls=[r for r in gate['replays'] if r['name']!='complete_research_proof']
    require(len(controls)==5 and sum(r['accepted'] for r in controls)==1 and all(r['accepted']==r['expected_acceptance'] for r in controls),'positive and four bad proof controls')
    require(len(gate['native_receipt_corruptions_rejected'])==6,'six native receipt controls')
    require(transport['status']=='INDEPENDENT_BALANCED_GRAM_PROOF_TRANSPORT_PASS' and transport['parts']==6 and transport['corruptions_rejected']==10,'transport audit and controls')
    r=transport['recovery']
    require(r['raw_sha256']==PH and r['raw_bytes']==227098316 and r['compressed_bytes']==52339920 and r['literal_original_comparison'] is True,'lossless complete proof transport')
    require(transport['proof_replays']==0,'transport identity check is not another proof replay')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(path,expected=None):
        h=sha(ROOT/path);require(expected is None or h==expected,'artifact identity '+path);pins[path]=h;return h
    def load(path,expected=None):pin(path,expected);return json.loads((ROOT/path).read_bytes())
    try:
        ids=[];chain=[];last=None
        for name in ['encoding','balanced_exclusion','margin']:
            d=B+'twentieth_'+name+'_registration/';rec=load(d+'summary.json');before=d+'CLAIMS.before.yaml';after=d+'CLAIMS.after.yaml'
            pin(before,rec['previous_ledger_sha256']);pin(after,rec['ledger_sha256']);old,new=read_ledger(ROOT/before),read_ledger(ROOT/after)
            if last is not None:require((ROOT/before).read_bytes()==last,'continuous registration chain')
            else:
                pub=load(B+'resume/nineteenth_publication_pointer_receipt.json');priorpath=B+'resume/claims_at_nineteenth_milestone.yaml'
                pin(priorpath);saved=B+'resume/claims_before_nineteenth_publication.yaml';pin(saved,pub['previous_ledger_sha256'])
                require((ROOT/priorpath).read_bytes()==(ROOT/saved).read_bytes(),'prior frozen ledger before publication')
                require(sha(ROOT/before)==pub['ledger_sha256'],'published start ledger')
                require(subprocess.check_output(['git','show',PREVIOUS+':CLAIMS.yaml'],cwd=ROOT)==(ROOT/before).read_bytes(),'immutable public starting ledger')
                prior=read_ledger(ROOT/priorpath);require(prior['claims']==old['claims'] and set(prior)==set(old),'publication preserves all claims and schema')
                require(all(prior[k]==old[k] for k in prior if k not in ['updated_at','artifacts']),'only availability metadata changes')
                pa,pb={r['id']:r for r in prior['artifacts']},{r['id']:r for r in old['artifacts']};require(set(pa)==set(pb),'publication artifact population')
                changed={k for k in pa if pa[k]!=pb[k]};require(changed==set(pub['new_public_artifact_ids']),'exact publication transition list')
                for k in changed:
                    require(all(pa[k].get(f)==pb[k].get(f) for f in set(pa[k])|set(pb[k]) if f not in ['availability','retrieval','unavailable_reason']),'unchanged artifact identity')
                    require(pa[k]['availability']=='LOCAL_ONLY' and pb[k]['availability']=='PUBLIC' and pb[k]['unavailable_reason'] is None and pub['published_commit'] in pb[k]['retrieval'],'authenticated public pointers')
                require(pub['mathematical_claim_changes']==[] and pub['published_commit']==pub['confirmed_remote_ref'],'publication not new mathematics')
            aa,bb={c['id']:c for c in old['claims']},{c['id']:c for c in new['claims']}
            require(all(bb[k]==v for k,v in aa.items()),'old semantic claims unchanged')
            oa,na={a['id']:a for a in old['artifacts']},{a['id']:a for a in new['artifacts']}
            require(all(na[k]==v for k,v in oa.items()),'existing artifacts unchanged by registrar')
            added=[c['id'] for c in new['claims'] if c['id'] not in aa];require(added==rec['new_claim_ids'],'exact additions')
            require(rec['registrar_performs_mathematical_verification'] is False and rec['validation']['valid'] is True and rec['validation']['errors']==[],'bookkeeping-only registrar')
            ids+=added;chain.append(dict(name=name,previous=sha(ROOT/before),next=sha(ROOT/after),added=added));last=(ROOT/after).read_bytes()
        require(ids==IDS,'six exact cohort claims');ledger=new;claims={c['id']:c for c in ledger['claims']};artifacts={a['id']:a for a in ledger['artifacts']}
        for cid in IDS:
            c=claims[cid];require(c['revision']==1 and c['review_state']=='CLEAR' and c['status']==('REFUTED' if cid==IDS[-1] else 'VERIFIED'),'exact status and revision')
            require(c['scope']['target_resolution']=='NONE' and c['scope']['unrestricted_target'] is False,'narrow claim scopes')
            for dep in c['dependencies']:require(claims[dep['id']]['revision']==dep['revision'],'pinned dependency revision')
            for eid in c['evidence']:pin(artifacts[eid]['path'],artifacts[eid]['sha256'])
            for v in c['verification']:
                require(v['claim_revision']==1 and v['outcome']==('FAIL' if cid==IDS[-1] else 'PASS'),'exact recorded verification or counterexample outcome')
                for aid,h in v['artifact_hashes'].items():require(artifacts[aid]['sha256']==h,'verification hash binding')
        cp=load(CP,'111a32f92399fdc42f8deed6a13716f144d9f122f69c2536afa064e9b904f52c');check_counts(cp,ledger)
        pin(SNAP,cp['ledger_snapshot_sha256']);require((ROOT/SNAP).read_bytes()==last==(ROOT/'CLAIMS.yaml').read_bytes(),'frozen and current ledger identical')
        for p,h in cp['evidence_sha256'].items():pin(p,h)
        oldcp=load(B+'resume/nineteenth_milestone_checkpoint.json',cp['previous_checkpoint_sha256'])
        require(oldcp['claim_population']==188 and cp['source_commit']==PREVIOUS,'prior milestone and current source boundary')
        proof=load(I+'hadamard_balanced_gram_unsat_v2/summary.json','edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5')
        transport=load(I+'hadamard_balanced_proof_packages/summary.json','54f3d947df7c3387a6b2960e9a0b966014f731c8105854cc4f3b94bcda6d4393');check_proof(proof,transport)
        for report in [proof,transport]:
            for p,h in report['outputs_sha256'].items():pin(p,h)
        oriented=load(I+'hadamard_oriented_unknown/summary.json');require(oriented['actual_exit_code']==0 and oriented['observed_result']=='UNKNOWN'
            and oriented['metrics']['conflicts']==1000000 and oriented['trace_bytes']==331620166 and oriented['trace_is_complete_unsat_certificate'] is False,'independent UNKNOWN receipt')
        cancellation=load(B+'hadamard_balanced_caps_cancellation/cancellation.json');require(cancellation['native_cap_solver_calls']==0 and cancellation['cap_encoding_independently_approved'] is False,'candidate cap build cancelled')
        margin=load(I+'hadamard_two_group_margin_cancellation/summary.json');witness=load(I+'hadamard_two_group_margin_cancellation/refuted_intersection_premise.json')
        require(margin['support_intersection_histogram']=={'0':1,'1':16,'2':58,'3':60,'4':47,'5':8} and margin['group_pairs']==190,'exact finite intersection census')
        require(sorted(set(witness['supports'][0])&set(witness['supports'][1]))==witness['intersection']==[4,6] and witness['size']==2,'explicit refutation scope')
        package=load(B+'hadamard_balanced_gram_proof_packages/artifact_packages.json','788368dea343adff368a2d0fdd464e7e743a957625bbd6ec3c2f7f5523b138f9')
        require(package['raw_sha256']==PH and package['raw_bytes']==227098316 and len(package['parts'])==6 and sum(p['bytes'] for p in package['parts'])==52339920,'recoverable raw proof metadata')
        for p in package['parts']:pin(p['path'],p['sha256']);require((ROOT/p['path']).stat().st_size==p['bytes']<=10*1024*1024,'six public-size exact proof parts')
        pin(GEN,'818c03a31afcd578fcc243d08d1a95a0d87b56f69e8132cd33b792b428f0df6a');require(cp['command'][1]==GEN,'actual recorder source')
        pin(REPORT);text=(ROOT/REPORT).read_text(encoding='utf-8')
        for cid in IDS:require(text.count(cid+' r1')==1 and claims[cid]['scope']['description'] in text,'exact scoped claim table')
        for token in ['Five verified claims and one refuted claim','Unbalanced factors and Conway-99 remain unresolved','194 claims:191 VERIFIED/CLEAR,2 CANDIDATE/CLEAR and1 REFUTED/CLEAR',
            'one oriented projection ended UNKNOWN','227,098,316-byte trace passed independent DRAT','Six public-size compressed parts','never independently approved or searched',
            'Zero new whole-support, core or unrestricted exclusions','size-two intersection','private broad process snapshot is omitted','Four older learned traces remain MISSING']:
            require(token in text,'reported boundary '+token)
        require(cp['timestamp'] in text and cp['source_commit'] in text and cp['next_experiment'] in text,'report provenance and next action')
        summary=load(PACK+'summary.json','6bcc1d7fb42becb008d9129ea72cb6e80dc540ed1ee05f65215c1636c22ffdc0')
        require(summary['status']=='TWENTIETH_EXPLICIT_PUBLICATION_INVENTORY_PASS' and summary['claim_ids']==IDS,'catalog cohort')
        for p,h in summary['output_hashes'].items():pin(p,h)
        catalog=load(PACK+'catalog.json','8ac7d74c8a6ebcd0977e980a3d6003f6c198c4e38e5b132d797aded8f1e5c987');entries=catalog['entries']
        inventory=load(PACK+'stage_inventory.json','0f0c7d8d81e25ff19202aa94f14fd6cf2b008be842a71b81e7181e1103c82398');check_privacy(entries,inventory['paths'])
        public=[r for r in entries if r['availability']=='READY_FOR_PUBLICATION'];pubpaths={r['path'] for r in public}
        require(len(entries)==summary['selected_files']==416 and len(public)==summary['public_research_files']==411 and sum(r['bytes'] for r in public)==summary['public_research_bytes']==75040210,'exact public and local populations')
        require(summary['new_local_only_research_artifacts']==5 and summary['new_gzip_streams']==1,'explicit exclusions and one gzip stream')
        for r in entries:
            pin(r['path'],r['sha256']);require((ROOT/r['path']).stat().st_size==r['bytes'],'fresh catalog byte sizes')
            if r['availability']=='READY_FOR_PUBLICATION':require(r['bytes']<=10*1024*1024,'public payload size')
            require(not any(s in r['path'] for s in ['few_exception_marginals','hadamard_exception_groups','four_group','four_support_circuit']),'later wave21 absent')
        require(pubpaths<=set(inventory['paths']) and all(p['path'] in pubpaths for p in package['parts']),'all public proof parts staged')
        for r in inventory['entries']:pin(r['path'],r['sha256'])
        for p in [I+'hadamard_balanced_gram_cnf/failure.json',I+'hadamard_balanced_gram_unsat/failure.json',
                  I+'hadamard_two_group_margin_cancellation/refuted_intersection_premise.json',B+'hadamard_balanced_caps_cancellation/cancellation.json']:
            require(p in pubpaths,'preserved failure/correction artifact')
        refs=load(PACK+'reference_checks.json');require(refs['status']=='EXACT_HASH_CLOSURE_AND_GZIP_RECOVERY_PASS' and len(refs['records'])==summary['reference_bindings']==3666
            and len({r['path'] for r in refs['records']})==summary['unique_referenced_files']==439,'authenticated reference closure')
        require(load(PACK+'reference_diagnostics.json')==dict(errors=[],count=0),'no reference diagnostics')
        gitbytes=load(PACK+'git_byte_checks.json');require(gitbytes['status']=='CURRENT_GIT_FILTER_BYTES_PASS','Git filter gate')
        for row in gitbytes['records']:
            require(row['path']!=PRIVATE,'private snapshot not Git payload');raw=(ROOT/row['path']).read_bytes()
            require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob_sha1'],'literal Git payload bytes')
        pin(GUIDE);guide=(ROOT/GUIDE).read_text(encoding='utf-8')
        for token in ['It is an extra restriction','fresh output directories','Recovery is an identity check, not a proof check',
            'No outside-column cap premise is used','Solver correctness is not trusted','cannot be promised to run unchanged on a fresh machine',
            'private and omitted','Few-exception and four-group circuit work belongs to the next wave']:
            require(token in guide,'replay limitation '+token)
        for p in ['README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']:
            pin(p);require('TWENTIETH_WAVE' in (ROOT/p).read_text(encoding='utf-8'),'entry point updated')
        validation=load(B+'resume/twentieth_precommit_validation.json');require(validation['valid'] is True and validation['errors']==[],'precommit bookkeeping validation')
        ex=cp['execution']
        for channel in ['stdout','stderr']:pin(B+'resume/twentieth_process_snapshot.'+channel+'.log',ex[channel+'_sha256'])
        rawout=(ROOT/(B+'resume/twentieth_process_snapshot.stdout.log')).read_text(encoding='utf-8')
        require(ex['command']==['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args'] and ex['exit_code']==1 and ex['state']=='NO_CADICAL_PROCESS_OBSERVED'
            and len(rawout.splitlines())==1 and 'PID' in rawout,'saved targeted execution census')
        corrupt=[]
        def reject(label,fn):
            try:fn()
            except(ValueError,KeyError,TypeError):corrupt.append(label)
            else:raise ValueError('corruption accepted '+label)
        for label,route,value in [('claim_count',['claim_population'],195),('refuted_omitted',['refuted_clear'],0),('whole_support',['new_whole_support_exclusions'],1),
            ('native_SAT',['native_attempts','sat'],1),('private_trace_proof',['oriented_outcome','status'],'UNSAT'),('too_many_choices',['balanced_encoding','normalized_choices_per_group'],151),
            ('proof_not_complete',['balanced_proof','complete_independent_replay'],False),('one_missing_part',['proof_transport','parts'],5),('cap_research_run',['cancelled_cap_preparation','native_attempts'],1)]:
            bad=deepcopy(cp);where=bad
            for k in route[:-1]:where=where[k]
            where[route[-1]]=value;reject(label,lambda bad=bad:check_counts(bad,ledger))
        reject('private_file_in_stage',lambda:check_privacy(entries,inventory['paths']+[PRIVATE]))
        bad=deepcopy(entries);next(r for r in bad if r['path']==PRIVATE)['availability']='READY_FOR_PUBLICATION';reject('private_file_promoted',lambda:check_privacy(bad,inventory['paths']))
        bad=deepcopy(proof);bad['replays'][-1]['accepted']=False;reject('proof_replay_veto_ignored',lambda:check_proof(bad,transport))
        bad=deepcopy(transport);bad['recovery']['raw_sha256']='0'*64;reject('different_recovered_proof',lambda:check_proof(proof,bad))
        observed=datetime.now(timezone.utc).isoformat();proc=subprocess.run(ex['command'],cwd=ROOT,capture_output=True,timeout=10)
        for channel,data in [('stdout',proc.stdout),('stderr',proc.stderr)]:
            with(out/('current_process.'+channel+'.log')).open('xb') as f:f.write(data)
        fresh=dict(observed_at=observed,command=ex['command'],exit_code=proc.returncode,
            state='CADICAL_PROCESS_OBSERVED' if proc.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if proc.returncode==1 else 'UNKNOWN_OBSERVATION_ERROR',scope='Separate live census; later-cohort execution does not alter frozen wave20.')
        for p in ['acceleration/audit_20260930_twentieth_checkpoint.py','acceleration/audit_20260930_sixteenth_checkpoint.py','docs/AUDIT_20260930_TWENTIETH_CHECKPOINT_PLAN.md','uv.lock','pyproject.toml']:pin(p)
        write(out/'summary.json',dict(status='INDEPENDENT_TWENTIETH_CHECKPOINT_REPORT_CONSISTENCY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},registrar_chain=chain,new_claim_ids=IDS,
            counts=dict(claims=194,verified_clear=191,candidate_clear=2,refuted_clear=1,new_verified=5,new_refuted=1,native_attempts=2,native_UNSAT=1,native_UNKNOWN=1,
                new_balanced_family_exclusions=1,new_whole_support_exclusions=0,new_full_factors=0,public_payloads=411,public_bytes=75040210,local_exclusions=5,proof_parts=6,
                reference_bindings=3666,referenced_files=439),corruptions=corrupt,checkpoint_sha256=sha(ROOT/CP),report_sha256=sha(ROOT/REPORT),snapshot_sha256=sha(ROOT/SNAP),
            saved_execution=ex,current_execution=fresh,verifier='/root/eight_domain_audit',scope='Independent frozen ledger/checkpoint/report/publication consistency; exact prior mathematical gates authenticated, not replayed.',
            shared_components=['Frozen independent YAML/hash/write helpers only; no recorder, registrar or packaging producer imports.',
                'This reviewer authored the prior row-margin audit. This report performs no new mathematical promotion.'],
            limitations=['Historical wave19 publication changes are availability-only and authenticated against the immutable public ledger.',
                'Complete proof and transport gates are authenticated; no new DRAT replay or native search.',
                'Private broad process stdout remains local; its bytes are hashed but never copied into public output.',
                'Saved transitive closure is authenticated; this is not mathematical replay of all439 referenced inputs.'],target_resolution='UNKNOWN',solver_calls=0,proof_replays=0))
        print(json.dumps(dict(status='INDEPENDENT_TWENTIETH_CHECKPOINT_REPORT_CONSISTENCY_PASS',sha256=sha(out/'summary.json'))))
    except BaseException as exc:write(out/'failure.json',dict(error=repr(exc),source_sha256=sha(Path(__file__))));raise

if __name__=='__main__':main()
