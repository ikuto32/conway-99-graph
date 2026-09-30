"""Independent frozen wave19 ledger/report/catalog coherence, not new mathematics."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
from audit_20260930_sixteenth_checkpoint import read_ledger,require,sha,write

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
I=B+'independent_review/'
CP=B+'resume/nineteenth_milestone_checkpoint.json'
SNAP=B+'resume/claims_at_nineteenth_milestone.yaml'
GEN='acceleration/record_20260930_nineteenth_checkpoint.py'
REPORT='docs/RESEARCH_20260930_NINETEENTH_WAVE.md'
PACK=B+'nineteenth_artifact_packaging/'
PREVIOUS_COMMIT='75243dc84ee6c37852a62f0935e45562094fe3ca'


def check_counts(cp,ledger,ids,batch,enum,orders):
    require(cp['claim_population']==len(ledger['claims'])==188,'claim population')
    require(cp['claim_status_counts']==dict(Counter(c['status'] for c in ledger['claims']))=={'VERIFIED':186,'CANDIDATE':2},'claim status population')
    require(cp['claim_review_counts']==dict(Counter(c['review_state'] for c in ledger['claims']))=={'CLEAR':188},'review state population')
    require(cp['verified_clear']==186 and cp['candidate_clear']==2,'current verified/candidate totals')
    require(cp['new_verified_ids']==ids and len(set(ids))==len(ids)==10 and cp['evidence_only_revision_changes']==[],'ten exact new claims')
    require(cp['target_resolution']=='UNKNOWN' and cp['external_review'] is None
            and cp['coverage']=='Overall search coverage: UNKNOWN; no validated denominator.','target unresolved')
    for key in ['new_full_factors','complete99_graphs','new_whole_support_exclusions','new_core_exclusions','new_unrestricted_exclusions']:
        require(cp[key]==0,'no scope inflation '+key)
    require(cp['batch_counts']==batch['counts'] and cp['batch_elapsed_seconds']==batch['batch_elapsed_seconds'],'exact batch stage counts')
    require(cp['batch_counts']==dict(native_attempts=4,distinct_fresh_SAT_projections=3,independently_checked_SAT_projections=3,
        exact_local_phase_exclusions=2,linear_screen_survivors=1,UNKNOWN_native_outcomes=1,UNSAT_native_outcomes=0,full_factors=0,target_graphs=0),'native projections separate from phase exclusions')
    require(cp['enumeration']==dict(frozen_universe=2187,completed_vectors=enum['counts']['kernel_vectors_enumerated'],
        local_survivors=enum['counts']['local_profile_survivors'],first_failure_counts=enum['first_failure_counts'],
        independent_gate=I+'hadamard_phase_case01_enumeration/summary.json'),'complete enumeration boundary')
    require(cp['enumeration']['completed_vectors']==2187 and cp['enumeration']['local_survivors']==0
            and cp['enumeration']['first_failure_counts']=={'mixed_phase_distinctness':1611,'constant_phase_multiplicity':576},'all2187 local failures')
    require(cp['new_exact_selected_parity_exclusions']==4,'four complete selected assignments')
    require(cp['reduction_orders']==orders['completed_recorded_orders']==12
            and cp['distinct_overlapping_reduced_exclusions']==orders['unique_clauses']==11
            and cp['minimum_recorded_fixed_patterns']==orders['minimum_in_this_batch']==14,'finite reduction-order counts')
    require(cp['union_cardinality'] is None and cp['union_cardinality_null_reason']=='No checked union calculation.', 'no additive coverage for overlapping families')
    require(cp['missing_batch_trace_files']==4 and batch['current_trace_availability']==['MISSING']*4,'missing versus historically hashed traces')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(path,expected=None):
        digest=sha(ROOT/path);require(expected is None or digest==expected,'exact artifact '+path);pins[path]=digest;return digest
    def load(path,expected=None):
        pin(path,expected);return json.loads((ROOT/path).read_bytes())
    try:
        ids,chain,last=[],[],None
        for name in ['selected_lift','general_phase','premise_collection','matrix_form','phase_batch','case01']:
            prefix=B+'nineteenth_'+name+'_registration/'
            receipt=load(prefix+'summary.json');before=prefix+'CLAIMS.before.yaml';after=prefix+'CLAIMS.after.yaml'
            pin(before,receipt['previous_ledger_sha256']);pin(after,receipt['ledger_sha256'])
            old,new=read_ledger(ROOT/before),read_ledger(ROOT/after)
            if last is not None:require((ROOT/before).read_bytes()==last,'continuous registration chain')
            else:
                publication=load(B+'resume/eighteenth_publication_pointer_receipt.json')
                priorpath=B+'resume/claims_at_eighteenth_milestone.yaml';pin(priorpath)
                preserved=B+'resume/claims_before_eighteenth_publication.yaml';pin(preserved,publication['previous_ledger_sha256'])
                require((ROOT/priorpath).read_bytes()==(ROOT/preserved).read_bytes(),'publication starts at immutable wave18 snapshot')
                require(sha(ROOT/before)==publication['ledger_sha256'],'wave19 starts at authenticated public ledger')
                committed=subprocess.check_output(['git','show',PREVIOUS_COMMIT+':CLAIMS.yaml'],cwd=ROOT)
                require(committed==(ROOT/before).read_bytes(),'exact publicly committed starting ledger')
                prior=read_ledger(ROOT/priorpath)
                require(prior['claims']==old['claims'] and set(prior)==set(old),'publication preserves every semantic claim and schema')
                require(all(prior[k]==old[k] for k in prior if k not in ['updated_at','artifacts']),'publication changes metadata only')
                pa,pb={r['id']:r for r in prior['artifacts']},{r['id']:r for r in old['artifacts']}
                require(set(pa)==set(pb),'publication artifact population')
                changed=[k for k in pa if pa[k]!=pb[k]]
                require(set(changed)==set(publication['new_public_artifact_ids']) and len(changed)==18,'eighteen exact availability transitions')
                for key in changed:
                    require(all(pa[key].get(k)==pb[key].get(k) for k in set(pa[key])|set(pb[key]) if k not in ['availability','retrieval','unavailable_reason']),'publication artifact identities unchanged')
                    require(pa[key]['availability']=='LOCAL_ONLY' and pb[key]['availability']=='PUBLIC'
                            and pb[key]['unavailable_reason'] is None and publication['published_commit'] in pb[key]['retrieval'],'immutable public retrieval pointers')
                require(publication['mathematical_claim_changes']==[] and publication['published_commit']==publication['confirmed_remote_ref'],'publication did not approve new mathematics')
            aa,bb={c['id']:c for c in old['claims']},{c['id']:c for c in new['claims']}
            require(all(bb[k]==v for k,v in aa.items()),'old claim revisions unchanged')
            oa,na={a['id']:a for a in old['artifacts']},{a['id']:a for a in new['artifacts']}
            require(all(na[k]==v for k,v in oa.items()),'old artifact records unchanged by registrar')
            added=[c['id'] for c in new['claims'] if c['id'] not in aa]
            require(added==receipt['new_claim_ids'] and receipt['registrar_performs_mathematical_verification'] is False,'approved integration only')
            validation=load(prefix+'validation.json');require(validation['valid'] is True and validation['errors']==[],'saved schema validation')
            ids+=added;chain.append(dict(name=name,previous_sha256=sha(ROOT/before),next_sha256=sha(ROOT/after),added=added));last=(ROOT/after).read_bytes()
        ledger=new;claims={c['id']:c for c in ledger['claims']};artifacts={a['id']:a for a in ledger['artifacts']}
        for cid in ids:
            c=claims[cid]
            require(c['revision']==1 and c['status']=='VERIFIED' and c['review_state']=='CLEAR'
                    and c['scope']['target_resolution']=='NONE' and c['scope']['unrestricted_target'] is False,'exact conditional claim promotion')
            for d in c['dependencies']:require(d['id'] in claims and claims[d['id']]['revision']==d['revision'],'exact dependency revision')
            for eid in c['evidence']:pin(artifacts[eid]['path'],artifacts[eid]['sha256'])
            for verification in c['verification']:
                require(verification['claim_revision']==1 and verification['outcome']=='PASS','verification exact revision')
                for aid,digest in verification['artifact_hashes'].items():require(artifacts[aid]['sha256']==digest,'verification artifact pin')
        cp=load(CP,'068c221aabfd48dd35e229bc8e5564b18c2081bd8e6651d7cedac09f05a6636f')
        pin(SNAP,cp['ledger_snapshot_sha256']);require((ROOT/SNAP).read_bytes()==last,'complete final snapshot identity')
        require((ROOT/'CLAIMS.yaml').read_bytes()==last,'current ledger has not advanced since this checkpoint')
        for path,digest in cp['evidence_sha256'].items():pin(path,digest)
        previous=load(B+'resume/eighteenth_milestone_checkpoint.json',cp['previous_checkpoint_sha256'])
        require(previous['claim_population']==178 and cp['source_commit']==PREVIOUS_COMMIT,'correct prior cohort and source boundary')
        batch=load(I+'hadamard_parity_phase_batch_outcome/summary.json','b620e76595c8709cb58c4bcd4432c681620d046da905e87aef7fd58ee2479635')
        enum=load(I+'hadamard_phase_case01_enumeration/summary.json','35050d72c18c3a5836ec9628b74463bedfdb8a4c181ab70d04cb98d59b05fe84')
        orders=load(I+'hadamard_phase_premise_orders/summary.json','5bc72f2b3154d3e927c7b690e70d5c4b3dc0c362fffb739b6bf5ccab13ed3910')
        check_counts(cp,ledger,ids,batch,enum,orders)
        for report in [batch,enum,orders]:
            for path,digest in report['outputs_sha256'].items():pin(path,digest)
        projections=[load(I+'hadamard_parity_support_cuts_sat/independent_projection.json')['selected_group_selector_ids']]
        for index in range(3):projections.append(load(I+f'hadamard_parity_phase_batch_cases/case_{index:02d}/independent_projection.json')['selected_group_selector_ids'])
        require(len({tuple(p) for p in projections})==4,'four exact excluded complete assignments are distinct')
        failures=load(I+'hadamard_phase_case01_enumeration/counts.json')
        require(failures['counts']==enum['counts'] and failures['first_failure_counts']==enum['first_failure_counts'],'enumeration count records')
        unique=load(I+'hadamard_phase_premise_orders/unique_clauses.json')
        require(len(unique['clauses'])==11,'eleven raw unique clause records')
        for version in ['', '_v2']:
            failed=load(B+'hadamard_phase_case01_enumeration'+version+'/failure.json')
            require(failed['counts']=={},'setup failure before vector enumeration')
        load(I+'balanced_phase_matrix_form/failure.json')
        decision=load(I+'hadamard_general_f3_phase_necessity/unsearched_cnf_execution_decision.json')
        require(decision['authorized_solver_attempts_completed']==0 and decision['execution_state']=='CANCELLED_BEFORE_RESEARCH_SOLVER','prepared branch CNF was not searched')
        pin(GEN);require(cp['command'][1]==GEN,'actual recorder source')
        pin(REPORT);report=(ROOT/REPORT).read_text(encoding='utf-8')
        for cid in ids:require(report.count('`'+cid+'`')==1 and claims[cid]['scope']['description'] in report,'exact scope in report table')
        for token in ['Ten independently checked claims','188 claims:186 VERIFIED/CLEAR and two CANDIDATE/CLEAR',
                      'four specified balanced parity assignments','eleven overlapping exclusions','four native calls',
                      'rank113/nullity7','all2,187 vectors','1,611 first fail','576 first fail','Zero new whole-support, core or unrestricted exclusions',
                      'All four deferred batch traces are now MISSING','Their loss cause is UNKNOWN','not establish universal phase rank',
                      'No research vector reaches the pair, full-Gram or outside-cap stages']:
            require(token in report,'report statement '+token)
        require(cp['timestamp'] in report and cp['source_commit'] in report and cp['next_experiment'] in report,'report provenance/next action')
        execution=cp['execution']
        for channel in ['stdout','stderr']:pin(B+'resume/nineteenth_process_snapshot.'+channel+'.log',execution[channel+'_sha256'])
        saved_stdout=(ROOT/(B+'resume/nineteenth_process_snapshot.stdout.log')).read_text(encoding='utf-8')
        saved_stderr=(ROOT/(B+'resume/nineteenth_process_snapshot.stderr.log')).read_text(encoding='utf-8')
        require(execution['command']==['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
                and execution['exit_code']==1 and execution['state']=='NO_CADICAL_PROCESS_OBSERVED'
                and len(saved_stdout.splitlines())==1 and 'PID' in saved_stdout,'saved fresh process census header only')
        require(saved_stderr.strip() in ['', 'your 131072x1 screen size is bogus. expect trouble'],'observed harmless terminal-size warning')
        catalog_summary=load(PACK+'summary.json');require(catalog_summary['status']=='NINETEENTH_EXPLICIT_PUBLICATION_INVENTORY_PASS'
                and catalog_summary['claim_ids']==ids,'final publication cohort')
        for path,digest in catalog_summary['output_hashes'].items():pin(path,digest)
        catalog=load(PACK+'catalog.json');entries=catalog['entries'];paths={e['path'] for e in entries}
        require(len(entries)==len(paths)==catalog_summary['selected_files']==catalog_summary['public_research_files'],'exact public payload population')
        require(sum(e['bytes'] for e in entries)==catalog_summary['public_research_bytes'],'public payload byte total')
        for entry in entries:
            pin(entry['path'],entry['sha256']);require((ROOT/entry['path']).stat().st_size==entry['bytes']<=10*1024*1024,'current public payload bytes')
            require(not any(x in entry['path'] for x in ['hadamard_oriented','hadamard_full_balanced','hadamard_signed_graph','balanced_gram_grouped']), 'future wave20 excluded')
        for path in [B+'hadamard_phase_case01_enumeration/failure.json',B+'hadamard_phase_case01_enumeration_v2/failure.json',
                     I+'balanced_phase_matrix_form/failure.json',B+'hadamard_parity_phase_batch_trace_archive/failure.json',
                     I+'hadamard_parity_phase_batch_outcome/trace_availability.json']:
            require(path in paths,'preserved failure/availability artifact')
        require(catalog_summary['new_local_only_research_artifacts']==0 and catalog_summary['new_gzip_streams']==0,'new available payloads are public bytes, missing traces separately recorded')
        refs=load(PACK+'reference_checks.json');require(refs['status']=='EXACT_HASH_CLOSURE_PASS'
                and len(refs['records'])==catalog_summary['reference_bindings']
                and len({r['path'] for r in refs['records']})==catalog_summary['unique_referenced_files'],'saved exact closure counts')
        require(load(PACK+'reference_diagnostics.json')=={'errors':[],'count':0},'no unresolved reference diagnostics')
        inventory=load(PACK+'stage_inventory.json');require(paths<=set(inventory['paths']),'explicit stage payload')
        for entry in inventory['entries']:pin(entry['path'],entry['sha256'])
        gitbytes=load(PACK+'git_byte_checks.json');require(gitbytes['status']=='CURRENT_GIT_FILTER_BYTES_PASS','saved Git bytes gate')
        for row in gitbytes['records']:
            raw=(ROOT/row['path']).read_bytes();require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob_sha1'],'literal raw Git blob identity')
        guide='docs/REPRODUCING_20260930_NINETEENTH_WAVE.md';pin(guide);guide_text=(ROOT/guide).read_text(encoding='utf-8')
        for token in ['Every replay must use a fresh output directory','All four batch learned traces are currently MISSING',
                      'No solver rerun is needed','not automatically mathematical cuts','not an UNSAT run','families\noverlap']:
            require(token in guide_text,'replay limitation '+token)
        for path in ['README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']:
            pin(path);require('NINETEENTH_WAVE' in (ROOT/path).read_text(encoding='utf-8'),'entry point latest frozen milestone')
        corruptions=[]
        for label,route,value in [('claim_count',['claim_population'],189),('broad_exclusion',['new_whole_support_exclusions'],1),
            ('new_graph',['complete99_graphs'],1),('native_UNSAT',['batch_counts','UNSAT_native_outcomes'],1),
            ('fewer_enum_vectors',['enumeration','completed_vectors'],2186),('false_local_survivor',['enumeration','local_survivors'],1),
            ('overlap_union',['union_cardinality'],11),('extra_assignment',['new_exact_selected_parity_exclusions'],5),
            ('missing_trace_omitted',['missing_batch_trace_files'],3),('exaggerated_orders',['reduction_orders'],13)]:
            bad=deepcopy(cp);where=bad
            for key in route[:-1]:where=where[key]
            where[route[-1]]=value
            try:check_counts(bad,ledger,ids,batch,enum,orders)
            except ValueError:corruptions.append(label)
            else:raise ValueError('corruption accepted '+label)
        # Separate fresh observation now; it does not rewrite the earlier snapshot.
        observed=datetime.now(timezone.utc).isoformat();command=execution['command']
        process=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=10)
        for channel,data in [('stdout',process.stdout),('stderr',process.stderr)]:
            with(out/('current_process.'+channel+'.log')).open('xb') as stream:stream.write(data)
        fresh=dict(observed_at=observed,command=command,exit_code=process.returncode,
            state='CADICAL_PROCESS_OBSERVED' if process.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if process.returncode==1 else 'UNKNOWN_OBSERVATION_ERROR',
            scope='Separate current native census; any later-cohort processes do not change the frozen wave19 result.')
        for path in ['acceleration/audit_20260930_nineteenth_checkpoint.py','acceleration/audit_20260930_sixteenth_checkpoint.py','uv.lock','pyproject.toml']:pin(path)
        write(out/'summary.json',dict(status='INDEPENDENT_NINETEENTH_CHECKPOINT_REPORT_CONSISTENCY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},registrar_chain=chain,
            new_claim_ids=ids,counts=dict(claims=188,verified_clear=186,candidate_clear=2,new_claims=10,distinct_selected_assignments_excluded=4,
                reduction_orders=12,overlapping_reduced_families=11,native_attempts=4,native_SAT_projections=3,native_UNKNOWN=1,native_UNSAT=0,
                enumerated_phase_vectors=2187,local_survivors=0,missing_traces=4,catalog_payloads=len(entries),catalog_bytes=catalog_summary['public_research_bytes'],
                reference_bindings=catalog_summary['reference_bindings'],referenced_files=catalog_summary['unique_referenced_files']),
            corruptions=corruptions,checkpoint_sha256=sha(ROOT/CP),report_sha256=sha(ROOT/REPORT),snapshot_sha256=sha(ROOT/SNAP),
            saved_execution=execution,current_execution=fresh,verifier='/root/eight_domain_audit',
            scope='Independent registration/checkpoint/report/catalog consistency; previous mathematical reviews authenticated rather than rerun.',
            shared_components=['Frozen own YAML/hash/write helpers; no recorder or registrar imports.',
                'This reviewer authored one approved-claim integration script and some prior mathematical checks; no new mathematical claim is approved by this coherence audit.'],
            limitations=['Snapshot18 predates18 publication-pointer changes; all claims are unchanged and exact public75243dc8 ledger is authenticated.',
                'All current catalog payload bytes are freshly checked; saved transitive closure is authenticated, not a new replay of every historical dependency.',
                'No overall search denominator, full factor, complete graph or target resolution.'],target_resolution='UNKNOWN'))
        print(json.dumps(dict(status='INDEPENDENT_NINETEENTH_CHECKPOINT_REPORT_CONSISTENCY_PASS',sha256=sha(out/'summary.json'))))
    except BaseException as exc:
        write(out/'failure.json',dict(error=repr(exc),source_sha256=sha(Path(__file__))))
        raise


if __name__=='__main__':main()
