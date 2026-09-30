"""Wave24 checkpoint/public-byte audit. No solver, ledger, index or producer imports."""
from copy import deepcopy
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import argparse,ast,hashlib,json,platform,shlex,subprocess,sys
from audit_20260930_sixteenth_checkpoint import sha,write,require
from audit_20260930_twentyfourth_registry_metadata import audit_chain,NEW_IDS,compare_binding
from audit_20260930_twentyfourth_artifact_bytes import recovery_population,audit_catalog,controls,cohort,PRIVATE,process_receipts,REC,REC_SHA
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
CP=B+'resume/twentyfourth_milestone_checkpoint.json';SNAP=B+'resume/claims_at_twentyfourth_milestone.yaml'
LH='ee94a175838c99a0021ec409dbf6a43c326008f8ca8d8223867f56f4ece2707a'
REPORT='docs/RESEARCH_20260930_TWENTYFOURTH_WAVE.md';GUIDE='docs/REPRODUCING_20260930_TWENTYFOURTH_WAVE.md'

def counts(cp,ledger):
    require(len(ledger['claims'])==cp['claim_population']==248,'248-claim cutoff')
    require(Counter(c['status'] for c in ledger['claims'])==cp['claim_status_counts']==dict(VERIFIED=244,CANDIDATE=2,REFUTED=2),'exact status census')
    require(Counter(c['review_state'] for c in ledger['claims'])==cp['claim_review_counts']==dict(CLEAR=248),'exact review census')
    require((cp['verified_clear'],cp['candidate_clear'],cp['refuted_clear'])==(244,2,2),'clear totals')
    require(cp['new_verified_ids']==[c for c in NEW_IDS if c!=NEW_IDS[3]] and cp['new_refuted_ids']==[NEW_IDS[3]],'18 verified and1 refuted exact additions')
    require(cp['target_resolution']=='UNKNOWN' and cp['external_review'] is None and cp['external_review_null_reason']=='No target-resolution artifact exists.','target/external status')
    require(cp['coverage']=='Overall search coverage: UNKNOWN; no validated denominator.','overall coverage')
    for key in ['new_full_factors','complete99_graphs','new_whole_support_exclusions','new_core_exclusions','new_unrestricted_exclusions']:require(cp[key]==0,'no broader result '+key)
    require(cp['necessary_unbalanced_counts']==dict(at_least=8,scope='Literal fixed support, prescribed full integer Gram and all outside-column overlap caps.'),'conditional bound scope')
    require(cp['seven_profile_union']==dict(profile_population=1608,AC_exclusions=312,nonempty_profile_members=1296,authenticated_complete_proofs=216,authenticated_complete_proof_bytes=584922543,duplicate_coverage=0,missing_profiles=0),'exact union metadata')
    require(cp['native_batch']==dict(selected=215,attempted=215,completed=215,UNSAT=215,SAT=0,UNKNOWN=0,complete_independent_proof_replays=215,proof_bytes=577482170,wrapped_solver_wall_seconds=203.5290000003297,end_to_end_wall_seconds=388.905999999959),'campaign population/boundaries')
    require(cp['separate_seven_pilot']==dict(complete_independent_proof_replays=1,proof_bytes=7440373),'separate seven pilot')
    require(cp['separate_eight_literal']==dict(complete_independent_proof_replays=1,proof_bytes=7811117,excluded_fibre_images=6,scope='One literal count profile and its six exact global fibre images only.'),'separate eight scope')
    require(cp['interval_witness']==dict(variables=185963,clauses_checked=7659287,exceptional_groups=8,scalar_cells=540,constructed_without_new_solver=True,full_factor=False),'constructed interval witness scope')
    require(cp['separate_block_witnesses']==dict(pairs=60,feasible=60,simultaneous_choice=False),'separate block scope')
    require(cp['affine_relaxations']==dict(models=217,consistent=217,full_catalogue_rank=323,fixed_count_rank=193,full_factor=False),'affine relaxation scope')

def proof_metadata(p,load,pin):
    require(p['status']=='INDEPENDENT_FIXED_HADAMARD_TWOHUNDREDFIFTEEN_PROFILE_UNSAT_PASS' and p['claim_id']==NEW_IDS[12],'literal proof collection')
    require(p['completed_attempts']==p['completed_proof_replays']==215 and p['SAT_pending_separate_review']==p['UNKNOWN']==0 and p['unattempted_profiles']==[],'all saved outcomes')
    require(p['proof_bytes']==577482170 and p['retained_two_copy_bytes']==1154964340,'unique proof versus retained copies')
    require([r['profile_id'] for r in p['profile_records']]==p['selected_profiles'] and len(set(p['selected_profiles']))==215,'complete literal identities')
    for r in p['profile_records']:
        t,q=r['trace'],r['replay'];require(r['outcome']=='UNSAT_VERIFIED' and q['accepted'] is True and q['expected_acceptance'] is True and q['actual_exit_code']==0 and q['cnf_sha256']==r['cnf_sha256'] and q['proof_sha256']==t['sha256'],'complete replay receipt')
        for kind in ['cnf','model','scope']:pin(r[kind+'_path'],r[kind+'_sha256'])
        pin(t['path'],t['sha256']);require((ROOT/t['path']).stat().st_size==t['bytes'],'complete trace bytes')
        for kind in ['run_summary','native_receipt']:pin(r[kind+'_path'],r[kind+'_sha256'])
        scope=load(r['scope_path']);require(r['literal_profile']['selected_profile_id']==r['profile_id'],'literal profile binding')
        require(p['inputs_sha256'][r['cnf_path']]==r['cnf_sha256'] and p['inputs_sha256'][t['path']]==t['sha256'],'replay inputs bound')
    require(sum(r['trace']['bytes'] for r in p['profile_records'])==p['proof_bytes'],'proof total')
    require(any(r['accepted'] for r in p['controls']) and sum(not r['accepted'] for r in p['controls'])>=215 and all(r['accepted']==r['expected_acceptance'] for r in p['controls']),'saved genuine/corrupt proof controls')
    require(len(p['native_receipt_corruptions_rejected'])>=6*215 and p['new_solver_calls']==0,'saved receipt controls')

def report_check(text,guide,cp,claims):
    for cid in NEW_IDS:require(text.count(cid+' r1')==1 and claims[cid]['scope']['description'] in text,'exact report claim row '+cid)
    for s in ['577,482,170','7,440,373','7,811,117','1,608','312','1,296','216','7,659,287','540','248 claims:244 VERIFIED/CLEAR','two CANDIDATE/CLEAR','two REFUTED/CLEAR','REFUTED','Overall search coverage: UNKNOWN; no validated denominator.']:
        require(s in text,'report count/scope '+s)
    for s in ['443 originals','3,548,174,273','484 gzip streams','Recovery checks identity, not mathematical validity','omitting cross-group caps and residual D','LOCAL_ONLY checker executable','independently rebuild and calibrate','25,000 records and 10 MiB','32 MiB','Never rerun completed one-shot registrars','217 parity certificates establish only affine consistency','later count search after the six cuts','--campaign-summary-sha256 02520b91d50c0f448fc966b61348da0215d520a5f2082767d09918632b0b0b46']:
        require(s in guide,'guide replay/scope '+s)
    require(cp['timestamp'] in text and cp['source_commit'] in text and cp['next_experiment'] in text,'exact report provenance/continuation')

def guide_commands(text,pin):
    checked=[]
    for line in text.splitlines():
        if not line.startswith('uv run ') or ' python -B ' not in line:continue
        tokens=shlex.split(line);start=tokens.index('-B')+1;p=tokens[start];args=tokens[start+1:];pin(p)
        source=(ROOT/p).read_text(encoding='utf8');tree=ast.parse(source)
        flags={v.value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' for v in n.args if isinstance(v,ast.Constant) and isinstance(v.value,str) and v.value.startswith('--')}
        # Several frozen small wrappers delegate their CLI to an independently pinned helper.
        if not flags:
            require('--out' in source or 'main' in source,'explicit delegated CLI source')
        else:require({v for v in args if v.startswith('--')}<=flags,'documented flags present in literal parser '+p)
        for key in ['manifest','batch-summary','encoding-gate','object-gate','proof-gate']:
            if '--'+key+'-sha256' in args:
                path=args[args.index('--'+key)+1];h=args[args.index('--'+key+'-sha256')+1];pin(path,h)
        if '--campaign-summary-sha256' in args:
            pin(args[args.index('--campaign-dir')+1]+'/summary.json',args[args.index('--campaign-summary-sha256')+1])
        if p.endswith('eight_count_profile_lift.py'):require(args[0]=='audit','required positional eight-lift audit mode')
        if p.endswith('count_interval_object.py'):require(args[0]=='constructed','constructed witness has no fabricated native output')
        if p.endswith('hadamard_seven_profile_union.py'):require(args[0]=='final','proof-dependent union final mode')
        checked.append(dict(source=p,arguments=args,execution=False))
    require(len(checked)==11,'all eleven guide Python replay commands')
    return checked

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint-sha256',required=True);ap.add_argument('--catalog-summary-sha256',required=True);ap.add_argument('--catalog-sha256',required=True);ap.add_argument('--stage-inventory-sha256',required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};cache={}
    def pin(path,h=None):
        require(path!=PRIVATE,'private historical stdout never read/hash')
        if path not in cache:cache[path]=sha(ROOT/path)
        require(h is None or cache[path]==h,'exact artifact identity '+path);pins[path]=cache[path];return cache[path]
    def load(path,h=None):pin(path,h);return json.loads((ROOT/path).read_bytes())
    try:
        index_before=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT)
        calibration=controls();write(out/'boundary_recovery_controls.json',calibration)
        chain=audit_chain(load,pin,LH);ledger=chain['ledger'];claims=chain['claims']
        cp=load(CP,a.checkpoint_sha256);counts(cp,ledger);pin(SNAP,LH);pin('CLAIMS.yaml',LH)
        require(cp['ledger_snapshot_sha256']==LH and (ROOT/SNAP).read_bytes()==chain['ledger_bytes']==(ROOT/'CLAIMS.yaml').read_bytes(),'exact frozen current ledger')
        require(subprocess.check_output(['git','show',cp['source_commit']+':CLAIMS.yaml'],cwd=ROOT)==(ROOT/(B+'twentyfourth_base_registration/CLAIMS.before.yaml')).read_bytes(),'immutable starting ledger')
        prev=load(B+'resume/twentythird_milestone_checkpoint.json',cp['previous_checkpoint_sha256']);require(prev['claim_population']==229 and cp['previous_report']=='docs/RESEARCH_20260930_TWENTYTHIRD_WAVE.md','prior boundary')
        for p,h in cp['evidence_sha256'].items():pin(p,h)
        proof=load(I+'hadamard_twohundredfifteen_profile_proofs/summary.json');proof_metadata(proof,load,pin)
        union=load(I+'hadamard_seven_profile_union/summary.json');require(all(union[k]==v for k,v in cp['seven_profile_union'].items()) and union['exclusion_approved'] and not union['pending_new_proof_gate'],'approved exact union metadata')
        native=load(B+'hadamard_seven_profile_batch_native/summary.json')
        require(native['selected_profiles']==proof['selected_profiles'] and native['completed_attempts']==215 and native['unattempted_profiles']==[],'actual native population')
        require(native['wrapped_solver_wall_seconds']==cp['native_batch']['wrapped_solver_wall_seconds'] and native['end_to_end_wall_seconds']==cp['native_batch']['end_to_end_wall_seconds'],'measured timing boundaries')
        interval=load(I+'count_interval_constructed_object/summary.json');require(interval['assignment_variables']==185963 and interval['actual_clauses_checked']==7659287 and interval['literal_interval_cells']==540 and interval['exception_count']==8 and interval['constructed_assignment'] and interval['solver_calls']==0,'constructed witness exact receipt')
        blocks=load(I+'count_profile_gram_blocks/summary.json');require(blocks['checked_pairs']==blocks['feasible_pairs']==60 and 'No consistent global factor' in blocks['scope'],'separate blocks')
        affine=load(I+'hadamard_gram_affine_gf2/summary.json');require(affine['models']==affine['positive_XOR_certificates']==217 and 'affine relaxation consistency only' in affine['statement'],'affine nonobstruction scope')
        transport=load(I+'hadamard_twohundredfifteen_proof_transport/summary.json');require(transport['proofs']==215 and transport['raw_bytes']==577482170 and transport['gzip_parts']==223 and transport['gzip_bytes']==90689391 and transport['literal_original_comparison'],'existing proof transport receipt')
        packages=recovery_population(load)
        rawrec=load(B+'resume/twentyfourth_raw_recovery.json','d1b72d68a9b9ea34ba776a080151c3c17a48c015a4c9cbb6b96f5671ff0f053b');require(rawrec['status']=='TWENTYFOURTH_RAW_ARTIFACT_RECOVERY_PASS' and len(rawrec['records'])==443 and all(r['action']=='RESTORED_MISSING' for r in rawrec['records']),'saved fresh-tree restoration')
        pin('acceleration/recover_20260930_twentyfourth_raw_artifacts.py',rawrec['source_sha256'])
        for p,h in load(REC,REC_SHA)['inputs_sha256'].items():pin(p,h)
        print('registry and frozen evidence metadata checked; inspecting final public closure',flush=True)
        catalog=audit_catalog(load,pin,a.catalog_summary_sha256,a.catalog_sha256,a.stage_inventory_sha256,NEW_IDS,packages)
        write(out/'independent_raw_recovery.json',dict(status='INDEPENDENT_LITERAL_443_RECOVERY_PASS',records=catalog['recovered'],raw_bytes=sum(r['bytes'] for r in catalog['recovered']),streams=sum(r['gzip_streams'] for r in catalog['recovered']),restoration_performed=False))
        pin(REPORT);pin(GUIDE,'895270eaa5f8fe12e7b2bb087a1cd93ec3063ca86542793f7ca1c6950475815b');report_check((ROOT/REPORT).read_text(encoding='utf8'),(ROOT/GUIDE).read_text(encoding='utf8'),cp,claims)
        write(out/'guide_command_review.json',dict(status='INDEPENDENT_LITERAL_GUIDE_COMMAND_REVIEW_PASS',commands=guide_commands((ROOT/GUIDE).read_text(encoding='utf8'),pin),limitations='Parser/source and exact input hash review only. Replay commands not executed. Fresh DRAT builds still require their own controls/provenance.'))
        pin('acceleration/record_20260930_twentyfourth_checkpoint.py',cp['writer_sha256'])
        for p in ['README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']:
            pin(p);require('TWENTYFOURTH_WAVE' in (ROOT/p).read_text(encoding='utf8'),'current entry point '+p)
        ex=cp['execution'];process_receipts(ex);require(ex['state']=={0:'CADICAL_PROCESS_OBSERVED',1:'NO_CADICAL_PROCESS_OBSERVED'}.get(ex['exit_code'],'UNKNOWN_OBSERVATION_ERROR'),'historical process observation')
        for channel in ['stdout','stderr']:pin(B+'resume/twentyfourth_process_snapshot.'+channel+'.log',ex[channel+'_sha256'])
        private=load(I+'hadamard_oriented_unknown/process_snapshot_availability.json');require('LOCAL_ONLY' in json.dumps(private) and 'OMIT' in json.dumps(private),'privacy omission preserved')
        rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,TypeError):rejected.append(label)
            else:raise ValueError('accepted corruption '+label)
        for label,path,value in [('count',['claim_population'],249),('status',['refuted_clear'],1),('target',['target_resolution'],'VERIFIED'),('whole_support',['new_whole_support_exclusions'],1),('missing_caps',['necessary_unbalanced_counts','scope'],'Gram only'),('duplicated_union',['seven_profile_union','duplicate_coverage'],1),('missing_proof',['native_batch','complete_independent_proof_replays'],214),('copy_bytes_as_proof',['native_batch','proof_bytes'],1154964340),('eight_family',['separate_eight_literal','scope'],'All eight profiles'),('interval_as_factor',['interval_witness','full_factor'],True),('block_jointness',['separate_block_witnesses','simultaneous_choice'],True),('affine_factor',['affine_relaxations','full_factor'],True)]:
            bad=deepcopy(cp);where=bad
            for k in path[:-1]:where=where[k]
            where[path[-1]]=value;reject(label,lambda bad=bad:counts(bad,ledger))
        bad=deepcopy(proof);bad['profile_records'][0]['replay']['accepted']=False;reject('ignored proof veto',lambda:proof_metadata(bad,load,pin))
        bad=deepcopy(proof);bad['profile_records'][0]['cnf_sha256']='0'*64;reject('wrong proof CNF',lambda:proof_metadata(bad,load,pin))
        require(subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT)==index_before,'Git index unchanged')
        require(sha(ROOT/'CLAIMS.yaml')==LH,'ledger unchanged throughout review')
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20260930_twentyfourth_registry_metadata.py','acceleration/audit_20260930_twentyfourth_artifact_bytes.py','acceleration/audit_20260930_sixteenth_checkpoint.py','acceleration/audit_20260930_twentythird_checkpoint_boundaries.py','docs/AUDIT_20260930_TWENTYFOURTH_CHECKPOINT_PLAN.md','uv.lock','pyproject.toml']:pin(p)
        write(out/'summary.json',dict(status='INDEPENDENT_TWENTYFOURTH_CHECKPOINT_REPORT_CONSISTENCY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},registrar_chain=chain['chain'],new_claim_ids=NEW_IDS,counts=dict(claims=248,verified_clear=244,candidate_clear=2,refuted_clear=2,new_verified=18,new_refuted=1,public_payloads=len(catalog['public_paths']),public_bytes=catalog['summary']['public_research_bytes'],local_originals=443,recovered_raw_bytes=3548174273,gzip_streams=484,reference_bindings=catalog['reference_records'],referenced_files=catalog['unique_references'],direct_input_bindings_checked=catalog['direct_input_bindings_checked']),checkpoint_sha256=pins[CP],report_sha256=pins[REPORT],snapshot_sha256=LH,boundary_recovery_controls=calibration,metadata_corruptions_rejected=rejected,saved_execution=ex,current_execution='Not sampled; saved checkpoint observation remains historical.',verifier='/root/eight_domain_audit',scope='Metadata, raw bytes, public recovery and reporting only; no new mathematical approval.',shared_components=['Prior independently authored duplicate-key-safe YAML/hash/write and process-receipt helpers; new registry comparison and streaming recovery/catalog paths. No producer/registrar/packager imports.','Reviewer authored some earlier evidence. Frozen mathematical verdicts are reused only as metadata premises; no proof reapproval.'],limitations=['No native solver or DRAT replay.','Recovery proves byte identity only.','All newly excluded443 original artifacts have exact public recovery; historical tools/omissions retain existing availability limitations.','Private historical stdout never read or hashed.','Later six-cut native result and second lift excluded.','Publication readiness is not remote publication.'],target_resolution='UNKNOWN',solver_calls=0,proof_replays=0))
        print(json.dumps(dict(status='INDEPENDENT_TWENTYFOURTH_CHECKPOINT_REPORT_CONSISTENCY_PASS',summary_sha256=sha(out/'summary.json'))))
    except BaseException as e:
        write(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
