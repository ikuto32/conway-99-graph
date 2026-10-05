"""Register only the three completed, independently bound initial wave30 claims."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, copy, hashlib, json, os, re, subprocess, sys, yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-GRAM-ENCODINGS':'/root/structural_attack',
 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-LITERAL-PROFILE-EXCLUSIONS':'/root/structural_attack',
 'C-FIXED-HADAMARD-EXACT-EIGHT-CASE0-CORE-FOOTPRINT':'/root',
}
REPORTS={
 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-GRAM-ENCODINGS':('exact_eight_prefix64_batch03_cnfs_v3','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS'),
 'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-LITERAL-PROFILE-EXCLUSIONS':('exact_eight_prefix64_batch03_proofs','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS'),
 'C-FIXED-HADAMARD-EXACT-EIGHT-CASE0-CORE-FOOTPRINT':('exact_eight_case0_core','INDEPENDENT_EXACT_EIGHT_CASE0_CORE_PASS'),
}
FORBIDDEN='acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log'

def need(value, message):
    if not value: raise ValueError(message)

def safe(name):
    p=(ROOT/name).resolve(); need(p.is_relative_to(ROOT),'repository containment')
    rel=p.relative_to(ROOT).as_posix()
    need(rel!=FORBIDDEN and rel!='PROMPT.md' and not rel.startswith('tools/'),'protected artifact')
    return p

def sha(name):
    with safe(name).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def read(name): return json.loads(safe(name).read_bytes())

def save(path, value):
    with path.open('x',encoding='utf8',newline='\n') as f: json.dump(value,f,indent=2); f.write('\n')

def admissible(row, report):
    need(row['id'] in EXPECTED and row['verifier']==EXPECTED[row['id']], 'independent verifier identity')
    need(row['revision']==1 and row['status']=='VERIFIED' and row['review_state']=='CLEAR','exact promotion state')
    need(report['status']==REPORTS[row['id']][1],'exact independent report outcome')
    for field in ['statement','scope','assumptions','dependencies','method','shared_components','created_at','updated_at']:
        need(bool(row[field]),'nonempty bound field '+field)

def compare_batch(rows,reports):
    byid={r['id']:(r,q) for r,q in zip(rows,reports,strict=True)}
    allids=[]
    for batch in (3,):
        prefix=f'C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH{batch:02d}-'
        erow,enc=byid[prefix+'GRAM-ENCODINGS']
        prow,proof=byid[prefix+'LITERAL-PROFILE-EXCLUSIONS']
        need(erow['checked_cases']==enc['checked_cases'] and prow['case_records']==proof['case_records'],'binding/report populations')
        ids=[r['case_id'] for r in enc['checked_cases']]
        need(len(ids)==len(set(ids))==64 and ids==enc['selected_case_ids']==proof['selected_case_ids']==[r['case_id'] for r in proof['case_records']],'same ordered64 cases')
        for a,b in zip(enc['checked_cases'],proof['case_records'],strict=True):
            for field in ['case_id','case_index','subset_index','full_count_profile_sha256','cnf_path','cnf_sha256','scope_path','scope_sha256']:
                need(a[field]==b[field],'literal formula/proof '+field)
            need(a['all_initial_domains'] and a['complete_raw_clause_reconstruction'],'complete literal encoding')
            need(b['outcome']=='UNSAT_VERIFIED' and b['trace']['complete_proof'] and b['replay']['accepted'] and b['replay']['actual_exit_code']==0,'accepted complete proof')
        need(enc['complete_formulas']==proof['completed_attempts']==proof['completed_proof_replays']==64 and proof['SAT_verified']==proof['UNKNOWN']==0 and proof['pending_case_ids']==[],'complete64 batch outcomes')
        need(set(ids).isdisjoint(enc['skipped_verified_case_ids']) and proof['prior_literal_overlap']['overlap_with_skipped_cases']==[],'disjoint prior literals')
        need(len(enc['skipped_verified_case_ids'])==60+64*(batch-1),'exact preceding literal count')
        need(set(allids)<=set(enc['skipped_verified_case_ids']),'new batches chained through authenticated prior cases')
        allids.extend(ids)
    need(len(allids)==len(set(allids))==64,'one complete disjoint64 population')
    crow,core=byid['C-FIXED-HADAMARD-EXACT-EIGHT-CASE0-CORE-FOOTPRINT']
    stats=core['statistics']
    need((core['core_clauses'],core['original_clauses'],len(stats['semantic_support_groups']),len(stats['coordinate_pairs']),len(stats['gram_cells']))==(53914,167416,20,60,527),'exact core footprint')
    need(stats['duplicate_origin_clauses']==0 and stats['core_variables']==8507,'exact raw core counts')
    need([r['accepted']for r in core['checker_calls']]==[True,False,False,True],'independent positive/corrupt/complete core replay')
    need(crow['claim_originator']=='/root/state_literature_audit' and core['verifier']=='/root' and crow['additional_literal_exclusions']==0,'distinct core producer and verifier; no new exclusion')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--expected-ledger-sha256',required=True)
    ap.add_argument('--cohort',nargs=4,action='append',required=True,metavar=('REPORT','REPORT_SHA','BINDING','BINDING_SHA'))
    ap.add_argument('--out',required=True); args=ap.parse_args()
    out=safe(args.out); need(not out.exists(),'fresh output'); out.mkdir(parents=True)
    bindings={}; before=(ROOT/'CLAIMS.yaml').read_bytes(); ledger_replaced=False
    def pin(name,digest):
        need(re.fullmatch('[0-9a-f]{64}',digest) is not None,'SHA256 syntax')
        if name in bindings: need(bindings[name]==digest,'consistent repeated reference'); return
        need(sha(name)==digest,'artifact identity '+name); bindings[name]=digest
    try:
        pin('CLAIMS.yaml',args.expected_ledger_sha256)
        need(args.expected_ledger_sha256=='9d9d37c36a695bdfb4833311bdf649b4485ac87e6a185bf66790419afed3b3c2','exact published300 baseline')
        old=registry.read_ledger(ROOT/'CLAIMS.yaml'); data=copy.deepcopy(old)
        need(len(old['claims'])==300 and Counter(c['status'] for c in old['claims'])==dict(VERIFIED=293,CANDIDATE=3,REFUTED=4),'starting population')
        need(len(args.cohort)==3,'exact three completed bound additions'); rows=[]; reports=[]
        for report_path,report_sha,binding_path,binding_sha in args.cohort:
            pin(report_path,report_sha); pin(binding_path,binding_sha)
            report,row=read(report_path),read(binding_path); admissible(row,report)
            expected_folder='acceleration/results/20261001_independent_review/'+REPORTS[row['id']][0]+'/'
            need(report_path==expected_folder+'summary.json' and binding_path==expected_folder+'claim_binding.json','exact report/binding association')
            if 'independent_report' in row:
                need(row['independent_report']==dict(path=report_path,sha256=report_sha),'explicit independent report binding')
            for obj in [report,row]:
                for field in ['inputs_sha256','outputs_sha256','evidence_sha256','artifact_hashes']:
                    for p,d in obj.get(field,{}).items(): pin(p,d)
            rows.append(row); reports.append(report)
        need([r['id'] for r in rows]==list(EXPECTED),'exact identities in dependency order')
        compare_batch(rows,reports)
        controls=[]
        for field,value in [('revision',2),('status','CANDIDATE'),('review_state','NEEDS_RECHECK'),('verifier','/root'),('id','C-UNREVIEWED-CLAIM')]:
            bad=copy.deepcopy(rows[0]); bad[field]=value
            try: admissible(bad,reports[0])
            except ValueError: controls.append(field)
            else: raise AssertionError('corrupt binding accepted: '+field)
        bad=copy.deepcopy(reports); bad[0]['status']='INDEPENDENT_UNRELATED_PASS'
        try: admissible(rows[0],bad[0])
        except ValueError: controls.append('unrelated independent status')
        else: raise AssertionError('unrelated report accepted')
        bad=copy.deepcopy(reports); proof_index=next(i for i,r in enumerate(rows) if r['id'].endswith('LITERAL-PROFILE-EXCLUSIONS')); bad[proof_index]['case_records'][0]['cnf_sha256']='0'*64
        try: compare_batch(rows,bad)
        except ValueError: controls.append('mismatched literal proof formula')
        else: raise AssertionError('mismatched literal proof accepted')
        now=datetime.now(timezone.utc).isoformat(); ids=[]
        for index,(row,report,cohort) in enumerate(zip(rows,reports,args.cohort,strict=True)):
            rp,rh,bp,bh=cohort; evidence=[]; hashes={}
            for j,(p,d) in enumerate([(rp,rh),(bp,bh)]):
                aid=f'thirtieth-initial-{index}-evidence{j}'; need(aid not in {a['id'] for a in data['artifacts']},'new artifact ID')
                data['artifacts'].append(dict(id=aid,path=p,sha256=d,availability='LOCAL_ONLY',retrieval='Exact workspace path; independent reports bind raw artifacts and checking paths.',unavailable_reason='Immutable wave30 evidence publication not yet confirmed.'))
                evidence.append(aid); hashes[aid]=d
            dependencies=copy.deepcopy(row['dependencies']+row.get('verification_dependencies',[]))
            for dep in dependencies:
                premise=next((c for c in data['claims'] if c['id']==dep['id']),None)
                need(premise is not None and premise['revision']==dep['revision'] and premise['status']=='VERIFIED' and premise['review_state']=='CLEAR','exact current trusted dependency')
            need(row['id'] not in {c['id'] for c in data['claims']},'new claim ID')
            limitations=copy.deepcopy(row.get('limitations',[row['scope']]))
            timestamp=report.get('timestamp',report.get('created_at')); need(timestamp is not None,'actual verification timestamp')
            verification=dict(claim_revision=1,verifier=row['verifier'],method='independent_artifact_check',command_or_audit=rp,timestamp=timestamp,outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=row['shared_components'],controls=[row['method'],'Actual positive and corrupted controls are recorded in the bound report. Registration performs no mathematical replay.'],limitations=limitations)
            data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],dependencies=dependencies,evidence=evidence,verification=[verification],limitations=limitations,created_at=row['created_at'],updated_at=row['updated_at'],external_source=None,unknowns=dict(external_source='Internal independent artifact checking; no external review asserted.'),reproducibility=dict(manifest=evidence[0])))
            ids.append(row['id'])
        need(data['claims'][:-3]==old['claims'] and data['artifacts'][:-6]==old['artifacts'],'all previous records unchanged')
        data['updated_at']=now; validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old)
        need(validation['valid'],repr(validation['errors'])); need(len(data['claims'])==303,'ending population')
        after=yaml.safe_dump(data,sort_keys=False,width=110).encode(); (out/'CLAIMS.before.yaml').write_bytes(before); (out/'CLAIMS.after.yaml').write_bytes(after)
        save(out/'controls.json',dict(rejected=controls)); save(out/'validation.json',validation)
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]: bindings[p.relative_to(ROOT).as_posix()]=sha(p)
        result=dict(status='THIRTIETH_INITIAL_REGISTERED',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),new_claim_ids=ids,claim_population=len(data['claims']),status_counts=dict(Counter(c['status'] for c in data['claims'])),checked_input_bindings=bindings,validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN',binding_editorial_adaptations=['Statements, assumptions, dependencies, exact scopes, shared components and original timestamps preserved.','If the binding omits a redundant limitations list, preserve its exact scope as the sole limitation.'])
        # Prepare every byte and an immutable journal before touching the live ledger.
        pending=out/'CLAIMS.pending.yaml'
        with pending.open('xb') as stream:
            stream.write(after); stream.flush(); os.fsync(stream.fileno())
        prepared=dict(result)
        prepared['status']='THIRTIETH_INITIAL_REGISTRATION_PREPARED'
        prepared['intended_final_status']=result['status']
        prepared['scope_note']='Preparation is not evidence that the live ledger was replaced.'
        save(out/'registration.prepared.json',prepared)
        result['ledger_write_protocol']='Prepared same-volume temporary file then atomic os.replace; final receipt is published only after ledger replacement.'
        result['recovery_journal']=(out/'transaction.json').relative_to(ROOT).as_posix()
        pending_summary=out/'summary.pending.json'
        with pending_summary.open('x',encoding='utf8',newline='\n') as stream:
            json.dump(result,stream,indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        save(out/'transaction.json',dict(status='PREPARED_NOT_COMMITTED',
            before_sha256=result['previous_ledger_sha256'],after_sha256=result['ledger_sha256'],
            pending_ledger=pending.relative_to(ROOT).as_posix(),
            prepared_receipt=pending_summary.relative_to(ROOT).as_posix(),
            prepared_receipt_sha256=hashlib.sha256(pending_summary.read_bytes()).hexdigest(),
            recovery='If final summary is absent, compare the live ledger against immutable before/after snapshots. Do not rerun or overwrite this transaction. Record a separate recovery audit before any further registration.',
            trusted_components=['Python os.replace and the local filesystem atomic rename semantics; no universal power-loss durability guarantee.']))
        need(pending.read_bytes()==after,'prepared ledger exact bytes')
        need((ROOT/'CLAIMS.yaml').read_bytes()==before,'unchanged live ledger before atomic replacement')
        os.replace(pending,ROOT/'CLAIMS.yaml'); ledger_replaced=True
        os.replace(pending_summary,out/'summary.json')
        print(json.dumps(dict(claim_population=303,new_verified=3,ledger_sha256=result['ledger_sha256'])))
    except BaseException as ex:
        observed=None; observed_reason=None
        try: observed=sha('CLAIMS.yaml')
        except BaseException as observation_error: observed_reason=repr(observation_error)
        before_hash=hashlib.sha256(before).hexdigest()
        after_hash=hashlib.sha256(after).hexdigest() if 'after' in locals() else None
        commit_state=('UNCHANGED_BEFORE' if observed==before_hash else
                      'REPLACED_WITH_EXPECTED_AFTER' if after_hash is not None and observed==after_hash else
                      'UNKNOWN_OR_UNEXPECTED_BYTES')
        save(out/'failure.json',dict(error=repr(ex),checked_input_bindings=bindings,
            replacement_flag_diagnostic_only=ledger_replaced,commit_state=commit_state,
            observed_ledger_sha256=observed,observation_unavailable_reason=observed_reason,
            before_sha256=before_hash,prepared_after_sha256=after_hash,
            prepared_after_unavailable_reason=None if after_hash is not None else 'Failure before final ledger serialization.',
            recovery_required=commit_state!='UNCHANGED_BEFORE')); raise

if __name__=='__main__': main()
