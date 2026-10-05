"""Independent wave23 metadata/public-byte review; no mathematical reapproval."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse, gzip, hashlib, json, platform, subprocess, sys
from audit_20260930_sixteenth_checkpoint import sha, write
from audit_20260930_twentythird_checkpoint_boundaries import require, claim_counts, calibrate_boundaries, privacy, process_receipts, PRIVATE
from audit_20260930_twentythird_registry_metadata import audit_chain, NEW_IDS, REGISTRARS
from audit_20260930_twentythird_artifact_bytes import recovery_population, recover, audit_catalog

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'; I=B+'independent_review/'
CP=B+'resume/twentythird_milestone_checkpoint.json'; SNAP=B+'resume/claims_at_twentythird_milestone.yaml'
REPORT='docs/RESEARCH_20260930_TWENTYTHIRD_WAVE.md'; GUIDE='docs/REPRODUCING_20260930_TWENTYTHIRD_WAVE_V2.md'
LH='58c016225a6d55933f6db7b99eb729c32b379dac034e04e79657001eee51714b'
GATES={
 'proofs':('hadamard_fiftyfour_profile_proofs','01cfb489e617f16f9c1773e7f10a579de018d87af39738427f52352593d53ee0'),
 'union':('hadamard_six_profile_union','6a7b34f7feaf7d9330ce07f4c615f4198e8cdc0c8ac22dd7fb5e673ba59311df'),
 'seven':('hadamard_seven_profile_arc','eeb0a947e6dde99c65578c6de323951f6c6654fdafeb31b22d053e117e84467d'),
 'orbits':('hadamard_seven_fibre_orbits','930f8d9a6e6b5986a61627cf21208c65691254c50fb2a71f6ddc0c4504b94e6f'),
 'eight':('hadamard_eight_exception_census','95176ae42241c3745fe1e017fbeca3798b04bc49f1113455605c3ed928e204f6'),
 'coordinates':('coordinate_marginal_domains','9d08476ace166438321273b13161d759dbc858c782b16d8a2f0e9801d424cf39'),
 'descent':('hadamard_all_triple_descent','d16968f418a7fac753d20941e33571378054d3493a2f845b65019bf41107d36d'),
 'transport':('hadamard_fiftyfour_proof_transport','84d033953ecd02215e4f090a1386bbb577a3bbe5f1be93044d782ca355059553')}

def counts(cp, ledger):
    claim_counts(cp,ledger['claims'])
    require(cp['new_verified_ids']==NEW_IDS and cp['evidence_only_revision_changes']==[],'thirteen exact additions only')
    require(cp['necessary_unbalanced_counts']==dict(at_least=7,scope='Literal fixed support, prescribed full integer Gram and all outside-column overlap caps.'),'conditional lower bound')
    require(cp['six_profile_union']==dict(profile_population=984,AC_exclusions=654,proof_representatives=55,proof_orbit_members=330,duplicate_coverage=0,missing_profiles=0,authenticated_complete_proof_bytes=563744101),'disjoint six-profile union')
    require(cp['native_batch']==dict(selected=54,attempted=54,completed=54,SAT=0,UNSAT=54,UNKNOWN=0,complete_independent_proof_replays=54,proof_bytes=555334934,wrapped_solver_wall_seconds=97.59600000013597,end_to_end_wall_seconds=149.5470000000205,scope='54 literal fixed-support profile formulas; cross-group caps and residualD omitted.'),'actual native batch and scope')
    require(cp['separate_literal_pilot']==dict(selected=1,attempted=1,completed=1,UNSAT=1,complete_independent_proof_replays=1,proof_bytes=8409167),'separate literal pilot')
    require(cp['seven_profile_screen']==dict(labelled_profiles=1608,relations=24732,distinct_option_pairs=37784232,checked_deletions=351630,checked_surviving_supports=3487644,Gram_pair_empty_profiles=276,combined_empty_profiles=312,nonempty_profiles=1296,all_profile_orbits=268,combined_empty_orbits=52,combined_nonempty_orbits=216,scope='Both predicates start with within-group cap-filtered domains. Nonempty outcomes are not joint/full-factor feasibility.'),'seven profile domains and scope')
    require(cp['eight_subset_screen']==dict(subsets=125970,rank_counts={'7':118484,'6':7468,'5':18},class_counts=dict(EXCLUDED_ONE_DIMENSIONAL_LARGE_COEFFICIENT=28400,EXCLUDED_FORCED_BALANCED_GROUP=92723,EXCLUDED_ONE_DIMENSIONAL_SMALL_COMMON_SUPPORT=663,RETAINED_HIGHER_DIMENSION_KERNEL=4184),retained_kernel_subsets=4184,scope='Necessary prescribed-Gram integer-count conditions only.'),'eight necessary kernel counts')
    require(cp['coordinate_domains']==dict(coordinates=12,full_bounded_vectors_checked=12582912,integer_vectors=291,ordered_pairs=7561,ordered_fibre_profiles=2226,scope='Complete individual-coordinate integer/count relaxation on one fixed support, with arbitrary exception counts; no cross-coordinate coupling, local word-triple existence, full Gram factor or target graph.'),'coordinate scope')
    require(cp['saved_descent']==dict(checked_checkpoints=408,checked_checkpoint_objects=816,checked_logged_updates=8000,minimum_logged_score=296,objective_version='FIXED_L_FULL_GRAM_FROBENIUS_SQUARED_V1',minimum_candidate_evaluations_verified=0,intermediate_rng_replay=False,scope='Finite saved artifacts and all logged transition scores only. Exact move optimality, tie counts, complete intermediate RNG trajectory and248880000 hypothetical candidate evaluations are not independently reproduced.'),'descent checked population and limitations')
    require(cp['raw_recovery']==dict(models=55,proofs=54,originals=109,restored_to_fresh_tree=109,identity_only=True),'raw recovery scope')

def proof_metadata(proof):
    require(proof['status']=='INDEPENDENT_FIXED_HADAMARD_FIFTYFOUR_PROFILE_UNSAT_PASS' and proof['claim_id']==NEW_IDS[6],'exact proof collection claim')
    require(proof['completed_attempts']==proof['completed_proof_replays']==54 and proof['SAT_pending_separate_review']==proof['UNKNOWN']==0 and proof['unattempted_profiles']==[],'exact proof outcomes')
    require(proof['proof_bytes']==555334934 and proof['retained_two_copy_bytes']==1110669868,'distinct trace populations')
    require([r['profile_id'] for r in proof['profile_records']]==proof['selected_profiles'] and len(set(proof['selected_profiles']))==54,'literal proof selection')
    for r in proof['profile_records']:
        t,q=r['trace'],r['replay']
        require(r['outcome']=='UNSAT_VERIFIED' and q['accepted'] and q['expected_acceptance'] and q['actual_exit_code']==0 and q['cnf_sha256']==r['cnf_sha256'] and q['proof_sha256']==t['sha256'],'complete proof identity/replay')
        require(proof['inputs_sha256'][r['cnf_path']]==r['cnf_sha256'] and proof['inputs_sha256'][t['path']]==t['sha256'],'exact input bindings')
    require(sum(r['trace']['bytes'] for r in proof['profile_records'])==555334934,'actual proof byte sum')
    require(len(proof['controls'])==58 and sum(r['accepted'] for r in proof['controls'])==1 and all(r['accepted']==r['expected_acceptance'] for r in proof['controls']),'positive and57 negative proof controls')
    require(len(proof['native_receipt_corruptions_rejected'])==324 and proof['new_solver_calls']==0,'receipt controls, no solver repeat')

def no_future(paths):
    require(all(not any(x in p for x in ['count_master','count_gram_intervals','hadamard_seven_profile_cnf','hadamard_seven_profile_native']) for p in paths),'future coupled count-master/seven literal work excluded')

def report_check(text,guide,cp,claims):
    for cid in NEW_IDS:require(text.count(cid+' r1')==1 and claims[cid]['scope']['description'] in text,'exact claim report row '+cid)
    for phrase in ['Thirteen independently checked claims','555,334,934','8,409,167','984 necessary profiles','654 pair-screen exclusions','330 disjoint images','55 proof-excluded representatives','37,784,232','351,630','3,487,644','268 six-member orbits','216 remain unresolved','within-group cap-filtered domains','125,970','4,184','12,582,912','2,226','exactly 296','37 outside-column cap violations','not comparable with earlier cross-Gram permutation scores','229 claims: 226 VERIFIED/CLEAR, two CANDIDATE/CLEAR and one REFUTED/CLEAR','No complete factor or target graph','LOCAL_ONLY','Four older missing traces and prior privacy omissions remain unchanged','Overall search coverage: UNKNOWN; no validated denominator.']:
        require(phrase in text,'report scope/count '+phrase)
    for phrase in ['all 109 originals','55 models and 54 campaign proofs','Recovery checks identity, not mathematical validity','99 independent gzip streams','563,744,101','within-group column caps','omitting cross-group caps and residual','LOCAL_ONLY checker executable','fresh machine must independently rebuild','229 claims: 226 VERIFIED/CLEAR','32MiB only','Research payloads retain the 10MiB limit','outside this cutoff','--campaign-summary-sha256 4d649f76d27cb14eb4e4db325ef617d68c5c6bcef3b52e1efc7f8cd46855fb22','positional mode `audit`','`--encoding-gate` and `--encoding-gate-sha256`']:
        require(phrase in guide,'guide scope/replay '+phrase)
    require(cp['timestamp'] in text and cp['source_commit'] in text and cp['next_experiment'] in text,'report provenance/continuation')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint-sha256',required=True);ap.add_argument('--catalog-summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};cache={}
    def pin(path,h=None):
        require(path!=PRIVATE,'private historical stdout never read or hashed')
        if path not in cache:cache[path]=sha(ROOT/path)
        require(h is None or cache[path]==h,'identity '+path);pins[path]=cache[path];return cache[path]
    def load(path,h=None):pin(path,h);return json.loads((ROOT/path).read_bytes())
    try:
        index_before=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT)
        chain=audit_chain(load,pin,LH);ledger=chain['ledger'];claims=chain['claims']
        cp=load(CP,a.checkpoint_sha256);counts(cp,ledger);pin(SNAP,LH);pin('CLAIMS.yaml',LH)
        require(cp['ledger_snapshot_sha256']==LH and (ROOT/SNAP).read_bytes()==chain['ledger_bytes']==(ROOT/'CLAIMS.yaml').read_bytes(),'frozen ledger exact bytes')
        require(subprocess.check_output(['git','show',cp['source_commit']+':CLAIMS.yaml'],cwd=ROOT)==(ROOT/(B+'twentythird_base_results_registration/CLAIMS.before.yaml')).read_bytes(),'immutable Git starting ledger')
        prev=load(B+'resume/twentysecond_milestone_checkpoint.json',cp['previous_checkpoint_sha256']);require(prev['claim_population']==216 and cp['previous_report']=='docs/RESEARCH_20260930_TWENTYSECOND_WAVE.md','prior publication boundary')
        for p,h in cp['evidence_sha256'].items():pin(p,h)
        gates={key:load(I+directory+'/summary.json',h) for key,(directory,h) in GATES.items()}
        proof=gates['proofs'];proof_metadata(proof)
        require(all(gates['union'][k]==v for k,v in cp['six_profile_union'].items()),'union independent saved result')
        for k in ['relations','distinct_option_pairs','checked_deletions','checked_surviving_supports','Gram_pair_empty_profiles','combined_empty_profiles','nonempty_profiles']:
            require(gates['seven'][k]==cp['seven_profile_screen'][k],'seven saved count '+k)
        require(gates['seven']['profiles']==1608 and gates['orbits']['orbits']==268 and gates['orbits']['combined_empty_orbits']==52 and gates['orbits']['combined_nonempty_orbits']==216,'orbit vs AC saved results')
        require(gates['eight']['population']==125970 and gates['eight']['retained']==4184 and gates['eight']['rank_counts']==cp['eight_subset_screen']['rank_counts'] and gates['eight']['class_counts']==cp['eight_subset_screen']['class_counts'],'eight independent census binding')
        require(all(gates['coordinates'][k]==v for k,v in cp['coordinate_domains'].items()) and all(gates['descent'][k]==v for k,v in cp['saved_descent'].items()),'coordinate/descent exact scope binding')
        native=load(B+'hadamard_six_profile_batch_campaign/summary.json','4d649f76d27cb14eb4e4db325ef617d68c5c6bcef3b52e1efc7f8cd46855fb22')
        require(native['selected_profiles']==proof['selected_profiles'] and native['completed_attempts']==54 and native['unattempted_profiles']==[] and native['stop_reason']=='ALL_SELECTED_PROFILES_ATTEMPTED','actual native population')
        require(native['wrapped_solver_wall_seconds']==cp['native_batch']['wrapped_solver_wall_seconds'] and native['end_to_end_wall_seconds']==cp['native_batch']['end_to_end_wall_seconds'],'native measured boundaries')
        packages=recovery_population(load)
        catalog=audit_catalog(load,pin,a.catalog_summary_sha256,NEW_IDS,packages)
        no_future(set(catalog['public_paths'])|set(catalog['stage']['paths']))
        rawrec=load(B+'resume/twentythird_raw_recovery.json','d06903f35c5db04de692b68b63c0af4b1f96a240bb93a658494143d8158096f6')
        require(rawrec['models']==55 and rawrec['proofs']==54 and len(rawrec['records'])==109 and all(r['action']=='RESTORED_MISSING' for r in rawrec['records']),'saved fresh-tree recovery record')
        pin('acceleration/recover_20260930_twentythird_raw_artifacts.py',rawrec['source_sha256'])
        correction=load(B+'resume/twentythird_replay_guide_correction.json')
        require(correction['status']=='REPLAY_COMMAND_EDITORIAL_CORRECTION' and correction['mathematical_claim_changed'] is False and correction['original_preserved'] is True,'guide correction exact boundary')
        pin(correction['prior_path'],'53327fb5faece6ad3e22cdde437388bec13bb4aaee6a0758d83e3611e6fb2254');pin(GUIDE,'6b58e24f523517bfabb07504490338a0aa7d8203a78a1ed86449cb6e1c39ed68')
        require(correction['corrected_path']==GUIDE and correction['corrected_sha256']==pins[GUIDE],'corrected guide binding')
        pin(REPORT);report_check((ROOT/REPORT).read_text(encoding='utf8'),(ROOT/GUIDE).read_text(encoding='utf8'),cp,claims)
        pin('acceleration/record_20260930_twentythird_checkpoint.py',cp['writer_sha256'])
        for p in ['README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']:
            pin(p);require('TWENTYTHIRD_WAVE' in (ROOT/p).read_text(encoding='utf8'),'current entry point '+p)
        private=load(I+'hadamard_oriented_unknown/process_snapshot_availability.json','3b8c2c2549c5b70e84345f696d8029ac169304f26b922ffcf9c73be654f419d0')
        require('LOCAL_ONLY' in json.dumps(private) and 'OMIT' in json.dumps(private),'historical privacy limitation preserved')
        ex=cp['execution'];process_receipts(ex)
        require(ex['state']=={0:'CADICAL_PROCESS_OBSERVED',1:'NO_CADICAL_PROCESS_OBSERVED'}.get(ex['exit_code'],'UNKNOWN_OBSERVATION_ERROR'),'saved targeted process state')
        for channel in ['stdout','stderr']:pin(B+'resume/twentythird_process_snapshot.'+channel+'.log',ex[channel+'_sha256'])
        controls=calibrate_boundaries();rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,TypeError,EOFError,gzip.BadGzipFile):rejected.append(label)
            else:raise ValueError('accepted corruption '+label)
        for label,path,value in [('count',['claim_population'],230),('target',['target_resolution'],'VERIFIED'),('whole_support',['new_whole_support_exclusions'],1),('Gram_only_scope',['necessary_unbalanced_counts','scope'],'Gram only'),('AC_as_factor',['seven_profile_screen','scope'],'Full factors'),('AC_as_coverage',['seven_profile_screen','nonempty_profiles'],1608),('missing_proof',['native_batch','complete_independent_proof_replays'],53),('overlapping_union',['six_profile_union','duplicate_coverage'],1),('proof_byte_population',['native_batch','proof_bytes'],1110669868),('unverified_move_optimality',['saved_descent','minimum_candidate_evaluations_verified'],248880000),('coordinate_feasibility',['coordinate_domains','scope'],'Full factors'),('eight_all_excluded',['eight_subset_screen','retained_kernel_subsets'],0)]:
            bad=deepcopy(cp);where=bad
            for key in path[:-1]:where=where[key]
            where[path[-1]]=value;reject(label,lambda bad=bad:counts(bad,ledger))
        reject('future_cohort_included',lambda:no_future([B+'hadamard_count_master_preflight/summary.json']))
        bad=deepcopy(proof);bad['profile_records'][0]['replay']['accepted']=False;reject('ignored_proof_veto',lambda:proof_metadata(bad))
        bad=deepcopy(proof);bad['profile_records'][0]['cnf_sha256']='0'*64;reject('wrong_proof_input',lambda:proof_metadata(bad))
        package=next(p for p in packages if len(p['parts'])>1);parts=[(ROOT/p['path']).read_bytes() for p in package['parts']]
        reject('reversed_recovery',lambda:recover(package,list(reversed(parts))));reject('truncated_recovery',lambda:recover(package,[parts[0][:-1]]+parts[1:]));bad=deepcopy(package);bad['sha256']='0'*64;reject('wrong_recovered_hash',lambda:recover(bad,parts))
        stamp=datetime.now(timezone.utc).isoformat();proc=subprocess.run(ex['command'],cwd=ROOT,capture_output=True,timeout=15)
        for channel,data in [('stdout',proc.stdout),('stderr',proc.stderr)]:
            with (out/('current_process.'+channel+'.log')).open('xb') as f:f.write(data)
        observation=dict(timestamp=stamp,command=ex['command'],exit_code=proc.returncode,state={0:'CADICAL_PROCESS_OBSERVED',1:'NO_CADICAL_PROCESS_OBSERVED'}.get(proc.returncode,'UNKNOWN_OBSERVATION_ERROR'),scope='Separate fresh targeted observation only; later-cohort activity does not change this frozen checkpoint.')
        require(subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT)==index_before,'Git index unchanged')
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20260930_sixteenth_checkpoint.py','acceleration/audit_20260930_twentythird_checkpoint_boundaries.py','acceleration/audit_20260930_twentythird_registry_metadata.py','acceleration/audit_20260930_twentythird_artifact_bytes.py','docs/AUDIT_20260930_TWENTYTHIRD_CHECKPOINT_PLAN.md','uv.lock','pyproject.toml']:pin(p)
        write(out/'summary.json',dict(status='INDEPENDENT_TWENTYTHIRD_CHECKPOINT_REPORT_CONSISTENCY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},registrar_chain=chain['chain'],new_claim_ids=NEW_IDS,counts=dict(claims=229,verified_clear=226,candidate_clear=2,refuted_clear=1,new_verified=13,public_payloads=len(catalog['public']),public_bytes=sum(r['bytes'] for r in catalog['public']),local_originals=109,complete_campaign_proof_bytes=555334934,separate_pilot_proof_bytes=8409167,gzip_streams=154,reference_bindings=catalog['reference_records'],referenced_files=catalog['unique_references']),recovery=catalog['recovered'],checkpoint_sha256=pins[CP],report_sha256=pins[REPORT],snapshot_sha256=LH,boundary_controls=controls,corruptions_rejected=rejected,saved_execution=ex,current_execution=observation,verifier='/root/structural_attack',scope='Metadata, literal bytes, public recovery and reporting only; no mathematical reapproval.',shared_components=['Prior independent duplicate-key-safe YAML/hash/write helpers and newly separate metadata/boundary/recovery helpers; no producer/registrar/recorder/packager imports.','Reviewer authored some earlier mathematical gates; their frozen metadata are bound here without new mathematical approval.'],limitations=['No native solver or DRAT replay.','Recovery checks byte identity, not proof validity.','Private historical stdout never read, hashed or published.','Later coupled count-master work excluded.','Readiness is not confirmation of remote publication.'],target_resolution='UNKNOWN',solver_calls=0,proof_replays=0))
        print(json.dumps(dict(status='INDEPENDENT_TWENTYTHIRD_CHECKPOINT_REPORT_CONSISTENCY_PASS',summary_sha256=sha(out/'summary.json'))))
    except BaseException as e:
        write(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise

if __name__=='__main__':main()
