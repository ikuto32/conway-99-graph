"""Read-only fifteenth ledger/checkpoint/report consistency audit, no promotion."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse,hashlib,json,platform,re,subprocess,sys
import yaml

ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
def need(x,s):
    if not x:raise ValueError(s)
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
class UniqueLoader(yaml.SafeLoader):pass
def mapping(loader,node,deep=False):
    result={}
    for a,b in node.value:
        k=loader.construct_object(a,deep=deep);need(k not in result,'duplicate YAML key');result[k]=loader.construct_object(b,deep=deep)
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
def ledger(p):return yaml.load(Path(p).read_bytes(),Loader=UniqueLoader)

def checkpoint_counts(cp,data,ids,gpu):
    claims=data['claims'];need(len({c['id'] for c in claims})==len(claims),'unique claims')
    sc=dict(Counter(c['status'] for c in claims));rc=dict(Counter(c['review_state'] for c in claims))
    need(cp['claim_population']==len(claims)==148 and cp['claim_status_counts']==sc=={'VERIFIED':146,'CANDIDATE':2},'exact claim populations')
    need(cp['claim_review_counts']==rc=={'CLEAR':148} and cp['verified_clear']==146,'review counts')
    need(cp['new_verified_ids']==ids and len(ids)==10,'new ten IDs')
    need((cp['completed_native_attempts'],cp['native_SAT_results'],cp['native_UNSAT_results'],cp['native_UNKNOWN_results'])==(5,0,0,5),'native population')
    need(cp['target_resolution']=='UNKNOWN' and cp['external_review'] is None and cp['coverage']=='Overall search coverage: UNKNOWN; no validated denominator.','target/coverage scope')
    for k in ['complete99_graphs','independently_validated_new_target_factors','new_complete_unsat_traces','newly_closed_unrestricted_branches']:need(cp[k]==0,'no result inflation '+k)
    for k in ['new_saved_proposal_records','distinct_initialized_chains','phase_chain_endpoints','chunk_best_states','phase_final_current_states','phase_final_best_states','checkpoint_current_scores_checked','checkpoint_best_scores_checked']:need(cp['gpu'][k]==gpu[k],'GPU count '+k)
    need(cp['gpu']['completed_phases']==len(gpu['cases'])==12 and cp['gpu']['individual_campaign_transitions_replayed'] is False,'finite saved-state scope')
    minima=[dict(core='connected_'+str(i).zfill(2),phase_minima=[c['final_best_score'] for c in gpu['cases'] if c['case']['core_index']==i]) for i in range(4)]
    need(cp['gpu']['minima']==minima,'exact saved minima')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    bindings={}
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'bound artifact '+key(p));bindings[key(p)]=value;return value
    def load(p,h=None):pin(p,h);return read(p)
    try:
        cp=load(B/'20260930_resume/fifteenth_milestone_checkpoint.json');snapshot=B/'20260930_resume/claims_at_fifteenth_milestone.yaml';pin(snapshot);data=ledger(snapshot)
        for p,h in cp['evidence_sha256'].items():pin(ROOT/p,h)
        previous=load(B/'20260930_resume/fourteenth_milestone_checkpoint.json',cp['previous_checkpoint_sha256'])
        need(previous['claim_population']==138,'previous cohort population')
        ids=[];chain=[];old_after=None
        for name in ['preparation','modular','coarse','bitlift']:
            d=B/f'20260930_fifteenth_{name}_registration';r=load(d/'summary.json');before=d/'CLAIMS.before.yaml';after=d/'CLAIMS.after.yaml'
            pin(before,r['previous_ledger_sha256']);pin(after,r['ledger_sha256']);a,b=ledger(before),ledger(after)
            if old_after is not None:need(before.read_bytes()==old_after,'exact consecutive registrar chain')
            old_after=after.read_bytes();old={c['id']:c for c in a['claims']};new={c['id']:c for c in b['claims']}
            added=[c['id'] for c in b['claims'] if c['id'] not in old];need(added==r['new_claim_ids'],'exact registrar additions')
            need(all(new[k]==v for k,v in old.items()),'existing claim records retained exactly')
            need(all(new[k]['revision']==1 and new[k]['status']=='VERIFIED' and new[k]['review_state']=='CLEAR' for k in added),'new scoped verified revisions')
            need(r['registrar_performs_mathematical_verification'] is False,'registration not math proof')
            ids+=added;chain.append(dict(name=name,before_sha256=digest(before),after_sha256=digest(after),added=added))
        need(old_after==snapshot.read_bytes(),'snapshot exact final registrar bytes')
        claims={c['id']:c for c in data['claims']};artifacts={a['id']:a for a in data['artifacts']}
        need(len(claims)==148 and len(artifacts)==len(data['artifacts']),'unique registry identities')
        verified_evidence=[]
        for cid in ids:
            c=claims[cid];need(c['scope']['target_resolution']=='NONE','new claim not a target resolution')
            for dep in c['dependencies']:need(dep['id'] in claims and claims[dep['id']]['revision']==dep['revision'],'exact dependency revision')
            for eid in c['evidence']:
                a=artifacts[eid];pin(ROOT/a['path'],a['sha256']);need(a['availability']=='LOCAL_ONLY','new evidence not prematurely public')
                verified_evidence.append(eid)
            need(c['verification'],'verification records exist')
            for v in c['verification']:
                need(v['claim_revision']==1 and v['outcome']=='PASS','exact verified revision')
                for eid,h in v['artifact_hashes'].items():need(artifacts[eid]['sha256']==h,'verification artifact binding')
        gp=B/'20260930_independent_review/connected_core_portfolio_states/summary.json';gpu=load(gp,'44dd89648beb0fce71aa16fe43ab863097d1a2b893593d042b78c81b163206c1')
        checkpoint_counts(cp,data,ids,gpu)
        run_checks=[]
        for row in cp['native_runs']:
            raw=load(ROOT/row['summary'],row['summary_sha256']);audit=load(ROOT/row['audit'],row['audit_sha256'])
            r=raw['receipt'];parsed=audit['outcome'];need(raw['research_calls']==row['attempts']==audit['actual_attempts']==1,'one actual native call')
            need(row['result']=='UNKNOWN_CONFLICT_LIMIT' and parsed['recorded_outcome']=='UNKNOWN_NATIVE_CONFLICT_CAP','explicit scoped UNKNOWN')
            need(row['exit_code']==raw['actual_exit_code']==r['actual_exit_code']==0,'native exit zero')
            for field,other in [('observed_conflicts','observed_final_conflicts'),('wrapper_wall_seconds','wrapper_wall_seconds')]:need(row[field]==parsed[other],'native checkpoint measure '+field)
            need(row['configured_conflicts']==audit['configured_limits']['conflicts']==2000000 and row['configured_seconds']==audit['configured_limits']['native_seconds']==300,'configured limits')
            t=audit['trace'];need(row['incomplete_trace_bytes']==t['bytes'] and row['incomplete_trace_sha256']==t['sha256'] and row['incomplete_trace_availability']==t['availability']=='LOCAL_ONLY','partial trace metadata')
            need(t['proof_checked'] is False and t['unsat_certificate'] is False and audit['checked_UNSAT_proofs']==audit['checked_SAT_objects']==0,'no outcome promotion')
            for channel in ['stdout','stderr']:pin(ROOT/r[channel],r[channel+'_sha256'])
            log=(ROOT/r['stdout']).read_text();need(not re.search(r'^s (?:UNSATISFIABLE|SATISFIABLE)$',log,re.M),'no decisive native status')
            counts=re.findall(r'^c conflicts:\s+(\d+)',log,re.M);need(counts and int(counts[-1])==row['observed_conflicts'],'literal conflict statistic')
            need('conflict limit' in log and row['observed_conflicts']>=2000000,'actual native stop boundary')
            run_checks.append(dict(name=row['name'],outcome=parsed['recorded_outcome'],trace_hash_checked_by=audit['timestamp'],whole_trace_rehashed_in_this_consistency_audit=False))
        execution=cp['execution'];stdout=B/'20260930_resume/fifteenth_process_snapshot.stdout.log';stderr=B/'20260930_resume/fifteenth_process_snapshot.stderr.log'
        pin(stdout,execution['stdout_sha256']);pin(stderr,execution['stderr_sha256'])
        rows=stdout.read_text().splitlines()[1:];active=[s for s in rows if '/20260930_prism_coarse60_bitflip/instance.cnf ' in s]
        need(execution['state']=='CADICAL_PROCESS_OBSERVED' and execution['exit_code']==0 and len(rows)==len(active)==1,'saved separate running process at observation time')
        need(all('/'+r['name']+'/' not in active[0] for r in cp['native_runs']),'running process outside cohort')
        correction=load(B/'20260930_fifteenth_report_correction/correction.json')
        for name in ['original_report','corrected_report']:pin(ROOT/correction[name]['path'],correction[name]['sha256'])
        old=(ROOT/correction['original_report']['path']).read_text(encoding='utf-8');new=(ROOT/correction['corrected_report']['path']).read_text(encoding='utf-8')
        need(old.count(correction['original_sentence'])==1 and old.replace(correction['original_sentence'],correction['corrected_sentence'])==new,'exact single-sentence correction')
        need(correction['claim_statement_changed'] is False and correction['counts_changed'] is False and correction['original_preserved'] is True,'no claim/count revision')
        modular=load(B/'20260930_independent_review/five_core_modular_gram/summary.json','b5bf625c820b6cbae9779b7dd40e8263dada10dad54b36d433ffdcff7951b34e')
        binary=[c for c in modular['cases'] if c['field']==2];need(len(binary)==5 and all(c['scalar_values']==[] and c['Gram_rank']<3*c['n']-4 for c in binary),'exact scope of failing sufficient premises')
        known=[c for c in binary if c['label']=='known243'][0];need(known['known_factor_rank']==57==3*known['n']-3,'distinct maximal-factor-rank positive')
        ternary=[c for c in modular['cases'] if c['field']==3 and c['zero_quotient_verified']];need([c['label'] for c in ternary]==['connected_01','connected_02','connected_03'],'three conditional GF3 cases')
        for cid in ids:need(new.count('`'+cid+'`')==1,'each new ID once in report table')
        for token in ['148 claims, 146 VERIFIED/CLEAR and 2 CANDIDATE/CLEAR','1,572,864','96 chunk-best','192 phase-final-current','192 phase-final-best','3,580','2,806','2,496,960','1,770','85,698','32']:
            if token!='32':need(token in new,'reported count token '+token)
        need('Campaign transition deltas and acceptance trajectories were not all replayed.' in new,'limited GPU verification explicit')
        need('without symmetry or graph completion' in new and 'LOCAL_ONLY' in new and 'no validated denominator' in new,'scope and availability language')
        failure=load(B/'20260930_fifteenth_checkpoint_failure/failure.json');pin(ROOT/'acceleration/record_20260930_fifteenth_checkpoint.py',failure['source_sha256']);pin(ROOT/'acceleration/record_20260930_fifteenth_checkpoint_v2.py')
        need(failure['outputs_written_before_failure'] is False and failure['exit_code']==1,'preserved initial recorder failure')
        packaging=load(B/'20260930_fifteenth_artifact_packaging/summary.json');need(packaging['claim_ids']==ids and packaging['incomplete_traces']==5 and packaging['public_recoverable_raw_GPU_JSON_files']==192,'catalog population')
        for p,h in packaging['output_hashes'].items():pin(ROOT/p,h)
        catalog=read(B/'20260930_fifteenth_artifact_packaging/catalog.json');need(catalog['mathematical_reverification_performed'] is False,'catalog not math review')
        need(all(e['availability'] in ['LOCAL_ONLY','READY_FOR_PUBLICATION'] for e in catalog['entries']),'publication planning availability')
        controls=[]
        for label in ['claim_count','unknown_count','GPU_minimum','review_total']:
            bad=deepcopy(cp)
            if label=='claim_count':bad['claim_population']+=1
            elif label=='unknown_count':bad['native_UNKNOWN_results']-=1
            elif label=='GPU_minimum':bad['gpu']['minima'][0]['phase_minima'][0]=0
            else:bad['verified_clear']-=1
            try:checkpoint_counts(bad,data,ids,gpu)
            except ValueError:controls.append(label)
            else:raise ValueError('accepted corrupt checkpoint '+label)
        for p in [Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'docs/REPRODUCING_20260930_FIFTEENTH_WAVE.md']:pin(p)
        report=dict(status='INDEPENDENT_FIFTEENTH_CHECKPOINT_CORRECTED_REPORT_CONSISTENCY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),yaml_version=yaml.__version__,inputs_sha256=bindings,registrar_chain=chain,new_claim_ids=ids,counts=dict(claims=148,verified_clear=146,candidate_clear=2,new_claims=10,UNKNOWN_native_attempts=5),native_checks=run_checks,GPU_summary=cp['gpu'],saved_process_observation=dict(timestamp=execution['observed_at'],row=active[0],current_process_state='UNKNOWN; this review authenticates the historical snapshot, not a current observation'),editorial_veto_resolved=dict(original_sha256=correction['original_report']['sha256'],authoritative_corrected_sha256=correction['corrected_report']['sha256'],reason=correction['reason'],no_mathematical_claim_or_count_change=True),corrupt_controls=controls,shared_components=['PyYAML and Python standard library; no producer/registrar imports.','Prior independent mathematical and raw artifact audits are authenticated and compared, not rerun here.'],verifier='/root/state_literature_audit',scope='Only checkpoint, corrected report, registration and saved-run consistency; not new mathematical verification.',limitations=['Partial traces were not rehashed again; their full prior independent hash records and raw summaries/logs were checked.','No campaign transition replay, proof checking, new claim promotion or current process-state assertion.','Catalog output hashes and population metadata checked; its full payload closure was not rerun.'],artifact_availability='LOCAL_ONLY',ledger_changed=False,git_changed=False,target_resolution='UNKNOWN')
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
