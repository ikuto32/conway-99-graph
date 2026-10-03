"""Independent frozen343-to350 impact; no registrar imports or math replay."""
import argparse,copy,hashlib,json,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline
from audit_20261003_wave37_transition_v1 import AuditError,need,save,transition
from audit_20261002_wave31_transition_v1 import UniqueLoader,indexed

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261003_independent_review/'
GF2='C-UNRESTRICTED-ROOTED8-CONTENT-DIVIDED-GF2-FOUR-PRIMALS'
RESET='C-HYPERGRAPH-WEIGHT60-V2-GRAPH-ONLY-SEED61-RESET'
WARM='C-HYPERGRAPH-WEIGHT60-V2-WARM01-SAVED-OBJECTS'
CODE='C-BINARY-CODE-LENGTH99-EVEN36TO60-RATIONAL-DUAL-SIZE-BOUND'
LOW67='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67'
CENSUS='C-HYPERGRAPH-WEIGHT60-WARM01-TWO-GRAPH-WARM-ROOT-CENSUS'
LOW76='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER76'
BINDINGS={
 GF2:(BASE+'root8_mod2_full01/claim_binding.json','49f8bf5af0f9c634ff751b41a572bc6219e91b07bb75126ad9575c03b5f76bc1','3c3888a8ef1f9a4183cbee405760bc1338060b6a3fe0f3a809d42b66e11c6f17'),
 RESET:('acceleration/results/20261003_weight60_reset_binding01/claim_binding_schema2_draft.json','24bda9181cef4d872db8d1bb5e309b4c101cf9ce0b5489fc77faf730ddcab501','a339491ebef854d7fe5c7cce74f7c8a8959c51ebb0c8744bb3b1a01a5fe33f1a'),
 WARM:(BASE+'weight60_warm01/claim_binding.json','96b65295d36bcb115b5bb384b03b34baa70671547ee4dd12e3f3a48f2b35cc07','94a621772e867c5c9c244f43758c04721a053f12f73a225ca85c811f3563c272'),
 CODE:(BASE+'incidence_code_dual_full01/code_size_claim_binding.json','e5c7bbd5f80a39470a29c066ea92dff3527e44d6773d849375043890ad19cd98','8872bfa74a0390434bdb6ec29c5a9a2e64601c2da60974bfe7c1a0dcd5318f69'),
 LOW67:(BASE+'incidence_griesmer01/claim_binding.json','4e018e2be2705f4684b31266797571d0eaab1eeb5ce15603d4765a77265e4848','7428f61543f9ac9089a72f9bd6527cf356b2d3b82d6d29e31d039cd9e7405e04'),
 CENSUS:('acceleration/results/20261003_weight60_warm_root_census_binding01/claim_binding_schema2_draft.json','e49ba355e4ca8cf99e883d69594d6a972480b55aade5c6f60ecf9fe7d4566bff','1508b65ec8f621cb3ac81f6263c52452c68269e3e76a2857c1b142d2404bf3a6'),
 LOW76:(BASE+'incidence_code_dual_full01/incidence_rank_claim_binding.json','c2a0da6c599f3a00356728aa07bfe4b9b12096e6904dba29e57961e14acacccf','c56bd5177fbeb2d5d90a0a02feb58e98fce996eb6baec7ffa44f94499f15331c')}
CHAIN=[
 ('01','b2df016825e41180c2d22d04835ce3922d13384b4c3803e9adb39d56b204384d','e9ad9a705ba06e14816c097af2703f0c37226313c47fd4c508f1b40142267bab',[GF2,RESET],'00326caf7d0a8a4ad8fade9f570e759c16754bcbc58c91340a289816af7534f4','v11_2'),
 ('02','e9ad9a705ba06e14816c097af2703f0c37226313c47fd4c508f1b40142267bab','879892c682f0a98e20373341621629407e5f5fba74b19be04db0776ca5e7c7a9',[WARM,CODE],'4d23cc3e4d6e56593c9cac8c7ac80d114fa2ebbcb2e37bb44b2e8a702b54b925','v11_2'),
 ('03','879892c682f0a98e20373341621629407e5f5fba74b19be04db0776ca5e7c7a9','5a09ea228f3977c30dd4c1726ad05a54e68f4fae5fae1cc4672c302e2b445554',[LOW67,CENSUS],'cede1c69d02479ab69f9f5552b31a448e2cd3d68852086715b0fcd0d50879900','v12'),
 ('04','5a09ea228f3977c30dd4c1726ad05a54e68f4fae5fae1cc4672c302e2b445554','cc8184dbe3c0c1bc6d539e8925fc392b80a3a4344c29e051118af0157d948a2c',[LOW76],'c9b9af423a5f0aede49e8a1b206c46e12ee383e4b48c72de53bdcbb27a44a069','v12')]
SOURCES={'v11_2':'c8ae676ac9785b99f7be10dd8569088e0aa084ab4137a1bcdf37fa9c3098c67d','v12':'70d4082b2f73fd23e4d8fb295e36eeb0092976c01f78e99fcd342f3a96598044'}

def projection(cid,b,r):
    need(b['id']==cid and b['revision']==b['claim_revision']==1 and b['review_state']=='CLEAR' and b['status']=='VERIFIED','EXACT_REVISION_STATUS')
    need(hashlib.sha256(b['statement'].encode('utf8')).hexdigest()==BINDINGS[cid][2],'EXACT_STATEMENT')
    need(set(b['scope'])=={'description','unrestricted_target','target_resolution'} and b['scope']['target_resolution']=='NONE' and b['scope']['unrestricted_target'] is (cid in (LOW67,LOW76)),'EXACT_NARROW_SCOPE')
    roles={GF2:('/root/structural','/root','independent_artifact_check'),RESET:('/root/native_driver','/root','independent_artifact_check'),WARM:('/root/native_driver','/root/structural','independent_artifact_check'),CODE:('/root','/root/structural','independent_artifact_check'),LOW67:('/root/structural','/root','independent_derivation'),CENSUS:('/root/structural','/root','independent_artifact_check'),LOW76:('/root','/root/structural','independent_derivation')}
    need((b['producer'],b['verifier'],b['method'])==roles[cid] and isinstance(b['shared_components'],list) and b['shared_components'],'EXACT_INDEPENDENT_ROLES_SHARED')
    if cid==GF2:
        need(r['status']=='INDEPENDENT_UNRESTRICTED_ROOT8_CONTENT_DIVIDED_MOD2_LITERAL_CHECK_V1_PASS' and r['normalization_rows_checked']==86434 and r['complete_scalar_primal_row_checks']==345736 and r['complete_scalar_relation_column_checks']==0 and r['profile_population']==r['compatible_profiles']==651 and r['excluded_profiles']==0 and r['rank_asserted'] is False and r['target_resolution']=='NONE','EXACT_GF2_SCOPE')
        need(b['dependencies']==[{'id':'C-UNRESTRICTED-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING','revision':1,'relation':'verification_dependency','reason':'Independent complete necessary-encoding reconstruction supplies the target interpretation; scalar certificate checking does not rederive it.'}],'EXACT_GF2_DEPENDENCY')
    elif cid==RESET:
        need(r['status']=='INDEPENDENT_WEIGHT60_GRAPH_ONLY_RESET_V1_PASS' and r['complete_reset_scalar_entries']==39204 and r['graphs_preserved']==['current','best','first_current','first_best'] and (r['lambda_energy'],r['mu_energy'],r['identity_mismatches'])==(0,3608,4934) and r['target_resolution']=='NONE','EXACT_RESET_SCOPE')
        need(r['parameters']=={'seed':99032061,'mix_steps':0,'schedule_steps':80000000,'t_start':8.0,'t_end':0.1,'forced':0,'step':0,'admissible':0,'accepted':0,'best_updates':0} and b['dependencies']==[],'EXACT_RESET_CONFIG')
    elif cid==WARM:
        need(r['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS' and (r['saved_state_files'],r['complete_integer_saved_current_best_objects'],r['sparse_records'],r['full_anchored_proposals'],r['unanchored_records'])==(103,206,3047,2147,900) and r['target_zero_candidates']==0 and r['target_resolution'] is False and r['first_selection_earliest_full_trajectory'] is False,'EXACT_SAVED_SCOPE')
        for key in ('final_current_diagnostics','final_best_diagnostics'):
            q=r[key];need(q['domain_valid'] is True and q['srg_valid'] is False and (q['identity_mismatches'],q['lambda_energy'],q['mu_energy'],q['weighted_energy'],q['base_energy'])==(4764,0,3480,3480,3480),'EXACT_NON_SRG_OBJECT')
        need(r['first_lambda0_step']==0 and (r['first_graph_diagnostics']['lambda_energy'],r['first_graph_diagnostics']['mu_energy'])==(0,3608) and b['mathematical_scope']['exact_mu_reduction']==128 and b['mathematical_scope']['full_trajectory_checked'] is False,'EXACT_INITIAL_COMPARISON')
        need([d['id'] for d in b['dependencies']]==['C-HYPERGRAPH-WEIGHT60-EXCLUSIVE-SWAP-V2-FINITE-ENGINEERING-CONTROLS',RESET] and all(d['revision']==1 and d['relation']=='verification_dependency' for d in b['dependencies']),'EXACT_SAVED_DEPENDENCIES')
    elif cid in (CODE,LOW76):
        need(r['status']=='INDEPENDENT_INCIDENCE_CODE_COMPLETE_DUAL_V1_PASS' and (r['complete_coefficients_checked'],r['complete_nonnegative_dual_coordinates_checked'],r['complete_weight_inequalities_checked'])==(1287,99,13) and r['exact_size_upper']==[86920436866892624754510357784136,6261965357389189817043215] and r['maximum_linear_dimension']==23 and r['conditional_incidence_rank_lower']==76 and r['optimum_asserted'] is False and r['rank_upper_assumed'] is False and r['target_resolution']=='NONE','EXACT_RATIONAL_CODE_BOUND')
        if cid==CODE:need(b['dependencies']==[],'EXACT_GENERIC_DOMAIN')
        else:
            need(b['premise_state']=='UNKNOWN' and b['dependencies']==[{'id':CODE,'revision':1,'relation':'uses_result','reason':'The exact code-size bound gives kernel dimension at most23.'},{'id':LOW67,'revision':1,'relation':'uses_result','reason':'ONLY the independently established even kernel-weight36..60 derivation in its pinned written proof is reused; the numerical rank67 conclusion is not the premise of rank76.'}],'EXACT_RANK76_PREMISE')
    elif cid==LOW67:
        need(r['status']=='INDEPENDENT_CONDITIONAL_TRIANGLE_INCIDENCE_GRIESMER_DERIVATION_V1_PASS' and (r['minimum_rank'],r['maximum_kernel_dimension'])==(67,32) and r['nonzero_kernel_weights']==list(range(36,61,2)) and r['target_resolution']=='NONE' and r['graph_constructed'] is False and r['target_nonexistence'] is False and r['rank_upper72_status'].startswith('UNKNOWN;'),'EXACT_CONDITIONAL_RANK67')
        need(b['premise_state']=='UNKNOWN' and b['dependencies']==[],'EXACT_RANK67_PREMISE')
    else:
        need(r['status']=='INDEPENDENT_WEIGHT60_WARM_TWO_GRAPH_DENSE_ROOT_CENSUS_V2_PASS' and (r['raw_graphs'],r['complete_roots'],r['literal_triangle_population'],r['complete_scalar_matrix_entries'])==(2,198,313698,19602) and r['target_resolution']=='NONE','EXACT_CENSUS_SCOPE')
        need([(q['label'],q['matching_roots'],q['fully_cn2_roots'],q['minimum_mu_row_residual'],q['minimum_root_ties'],q['selected_root'],q['triangle_count'],q['global_mu_energy']) for q in r['graph_records']]==[('final_best',99,0,52,[11,41,77],11,231,3480),('first_lambda0',99,0,50,[81],81,231,3608)] and b['dependencies']==[],'EXACT_ZERO_WARM_ROOTS')
    paths={BINDINGS[cid][0]:BINDINGS[cid][1],b['report']:b['report_sha256']}
    def add(p,h):need(p not in paths or paths[p]==h,'CONSISTENT_CLOSURE');paths[p]=h
    for p,h in b.get('inputs_sha256',{}).items():add(p,h)
    for key in ('artifacts','evidence'):
        values=b.get(key,[])
        if isinstance(values,dict):
            for k,p in values.items():
                if not k.endswith('_sha256'):need(k+'_sha256' in values,'PAIRED_EVIDENCE');add(p,values[k+'_sha256'])
        else:
            need(isinstance(values,list),'EVIDENCE_COLLECTION')
            for q in values:
                if isinstance(q,dict) and 'path' in q:add(q['path'],q['sha256'])
    return {'paths':paths,'controls':b.get('controls',r.get('controls',r.get('corrupted_controls_rejected')))}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Metadata343to350 exact7r1 fourregistrations independentclosure hashes and strictsemantic controls;150worker20reserve; no mathematical replay')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'BOUNDED_OUTPUT');out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'DEADLINE_RESERVE')
        if p in pins:need(h is None or h==pins[p],'INPUT_HASH');return pins[p]
        with (ROOT/p).open('rb') as stream:a=hashlib.file_digest(stream,'sha256').hexdigest()
        need(h is None or h==a,'INPUT_HASH',p);pins[p]=a;return a
    def read(p,h=None):pin(p,h);return json.loads((ROOT/p).read_bytes())
    def ledger(p,h):pin(p,h);return yaml.load((ROOT/p).read_text(encoding='utf8'),Loader=UniqueLoader)
    try:
        live=pin('CLAIMS.yaml',CHAIN[-1][2]);index=pin('.git/index')
        bs={cid:read(q[0],q[1]) for cid,q in BINDINGS.items()};rs={cid:read(b['report'],b['report_sha256']) for cid,b in bs.items()};gold={cid:projection(cid,bs[cid],rs[cid]) for cid in bs}
        snapshots=[];terminals=[]
        for n,beforeh,afterh,ids,summaryh,version in CHAIN:
            reg='acceleration/results/20261003_wave38_registration'+n;s=read(reg+'/summary.json',summaryh)
            need(s['before_ledger_sha256']==beforeh and s['ledger_sha256']==afterh and s['new_claim_ids']==ids and s['mathematical_replays']==0 and s['new_exclusions']==0 and s['target_resolution']=='UNKNOWN' and s['source_sha256']==SOURCES[version],'FROZEN_EXACT_CHAIN')
            source='acceleration/register_20261003_bound_claims_'+version+'.py';pin(source,SOURCES[version]);pin(source.replace('.py','_spec.md'))
            expectedcmd=[s['command'][0],source,'--out',reg,'--previous-sha256',beforeh]
            for cid in ids:expectedcmd+=['--binding',BINDINGS[cid][0],'--binding-sha256',BINDINGS[cid][1]]
            need(s['command']==expectedcmd,'EXACT_REGISTRAR_ARGV')
            before,after=ledger(reg+'/CLAIMS.before.yaml',beforeh),ledger(reg+'/CLAIMS.after.yaml',afterh)
            if snapshots:need(snapshots[-1][1]==before,'CONTIGUOUS_EXACT_SEMANTICS')
            transition(before,after,ids,bs,gold);snapshots.append((before,after))
            sup='acceleration/results/20261003_wave38_registration_supervision'+n;r=read(sup+'/summary.json');m=read(sup+'/manifest.json')
            need(r['command_exit_code']==0 and r['cleanup']['reaped'] is True and r['cleanup']['job_active_zero_observed'] is True and r['cleanup']['cleanup_errors']==[] and r['invocation_id']==m['invocation_id'],'ACTUAL_CONTAINED_REGISTRATION')
            need(m['command'][1:]==s['command'][1:] and m['seconds']==180 and m['shutdown_reserve_seconds']==30 and m['source_sha256']==pin('acceleration/run_compute_command.py'),'EXACT_OUTER_RECEIPT')
            terminals.append({'path':sup+'/summary.json','sha256':pins[sup+'/summary.json'],'manifest_sha256':pins[sup+'/manifest.json'],'elapsed_seconds':r['elapsed_seconds'],'exit_code':0,'reaped':True,'job_empty':True})
        before,after=snapshots[0][0],snapshots[-1][1];old,new,arts=transition(before,after,BINDINGS,bs,gold)
        need(len(old)==343 and len(new)==350 and Counter(c['status'] for c in new.values())=={'VERIFIED':342,'CANDIDATE':3,'REFUTED':5} and all(c['review_state']=='CLEAR' for c in new.values()),'EXACT_CLAIM_POPULATIONS')
        controls=[]
        def reject(label,stage,fn):
            try:fn()
            except AuditError as e:need(e.stage==stage,'CONTROL_EXACT_STAGE',str(e));controls.append({'label':label,'stage':e.stage,'outcome':'REJECTED'})
            else:raise AuditError('CONTROL_FALSE_ACCEPT',label)
        changes=[('prior_claim','ALL_PRIOR_CLAIMS_UNCHANGED',lambda x:x['claims'][0].update(statement='changed')),
          ('prior_artifact','ALL_PRIOR_ARTIFACTS_UNCHANGED',lambda x:x['artifacts'][0].update(availability='MISSING')),
          ('false_resolution','TOPLEVEL_SEMANTICS_UNCHANGED',lambda x:x['target'].update(status='VERIFIED')),
          ('gf2_integer_realization','BOUND_FIELD',lambda x:indexed(x['claims'])[GF2].update(statement='651 graphs exist')),
          ('census_one_fullroot','BOUND_FIELD',lambda x:indexed(x['claims'])[CENSUS].update(statement='One SAT scaffold certified')),
          ('rank76_target_exclusion','BOUND_SCOPE',lambda x:indexed(x['claims'])[LOW76]['scope'].update(target_resolution='NONEXISTENCE')),
          ('generic_code_as_target','BOUND_SCOPE',lambda x:indexed(x['claims'])[CODE]['scope'].update(unrestricted_target=True)),
          ('wrong_relation','BOUND_DEPENDENCY_RELATION',lambda x:indexed(x['claims'])[LOW76]['dependencies'][1].update(relation='premise')),
          ('wrong_revision','BOUND_DEPENDENCY_RELATION',lambda x:indexed(x['claims'])[LOW76]['dependencies'][0].update(revision=2)),
          ('lost_weight_only_reason','BOUND_DEPENDENCY_REASON',lambda x:indexed(x['claims'])[LOW76]['unknowns'].update(dependency_notes='[]')),
          ('established_target_premise','BOUND_PREMISE_STATE',lambda x:indexed(x['claims'])[LOW67]['unknowns'].update(premises='"VERIFIED"')),
          ('self_approval','BOUND_VERIFICATION_ROLE_METHOD',lambda x:indexed(x['claims'])[CODE]['verification'][0].update(verifier='/root')),
          ('wrong_method','BOUND_VERIFICATION_ROLE_METHOD',lambda x:indexed(x['claims'])[LOW76]['verification'][0].update(method='independent_artifact_check')),
          ('missing_shared','BOUND_SHARED_COMPONENTS',lambda x:indexed(x['claims'])[WARM]['verification'][0].update(shared_components=[])),
          ('hash_changed','EXACT_REVISION_HASH_BINDING',lambda x:indexed(x['claims'])[GF2]['verification'][0]['artifact_hashes'].update({indexed(x['claims'])[GF2]['evidence'][0]:'0'*64})),
          ('false_PUBLIC','NO_UNCONFIRMED_PUBLIC_PROMOTION',lambda x:indexed(x['artifacts'])[indexed(x['claims'])[RESET]['evidence'][0]].update(availability='PUBLIC')),
          ('lost_sparse_limit','BOUND_FIELD',lambda x:indexed(x['claims'])[WARM].update(limitations=[]))]
        for label,stage,change in changes:
            bad=copy.deepcopy(after);change(bad);reject(label,stage,lambda:transition(before,bad,BINDINGS,bs,gold))
        reporttests=[('gf2_false_rank',GF2,'EXACT_GF2_SCOPE',lambda x:x.update(rank_asserted=True)),('reset_wrong_seed',RESET,'EXACT_RESET_CONFIG',lambda x:x['parameters'].update(seed=61)),('saved_missing_gap',WARM,'EXACT_SAVED_SCOPE',lambda x:x.update(unanchored_records=0)),('saved_zero_target',WARM,'EXACT_NON_SRG_OBJECT',lambda x:x['final_best_diagnostics'].update(srg_valid=True)),('code_optimum',CODE,'EXACT_RATIONAL_CODE_BOUND',lambda x:x.update(optimum_asserted=True)),('code_bound_denominator',CODE,'EXACT_RATIONAL_CODE_BOUND',lambda x:x['exact_size_upper'].__setitem__(1,1)),('rank_upper72',LOW76,'EXACT_RATIONAL_CODE_BOUND',lambda x:x.update(rank_upper_assumed=True)),('rank67_universal_existence',LOW67,'EXACT_CONDITIONAL_RANK67',lambda x:x.update(graph_constructed=True)),('census_false_fullroot',CENSUS,'EXACT_ZERO_WARM_ROOTS',lambda x:x['graph_records'][0].update(fully_cn2_roots=1)),('census_wrong_tie',CENSUS,'EXACT_ZERO_WARM_ROOTS',lambda x:x['graph_records'][0].update(minimum_root_ties=[11]))]
        for label,cid,stage,change in reporttests:
            bad=copy.deepcopy(rs[cid]);change(bad);reject(label,stage,lambda:projection(cid,bs[cid],bad))
        for label,cid,stage,change in [('binding_statement',LOW76,'EXACT_STATEMENT',lambda x:x.update(statement='rank(B)>=77')),('binding_role',GF2,'EXACT_INDEPENDENT_ROLES_SHARED',lambda x:x.update(verifier='/root/structural')),('binding_status',LOW67,'EXACT_REVISION_STATUS',lambda x:x.update(status='CANDIDATE')),('binding_unconditional_premise',LOW76,'EXACT_RANK76_PREMISE',lambda x:x.update(premise_state='VERIFIED')),('binding_wrong_relation',GF2,'EXACT_GF2_DEPENDENCY',lambda x:x['dependencies'][0].update(relation='encoding_equivalence'))]:
            bad=copy.deepcopy(bs[cid]);change(bad);reject(label,stage,lambda:projection(cid,bad,rs[cid]))
        for g in gold.values():
            for p,h in g['paths'].items():pin(p,h)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_wave38_transition_v1_spec.md','acceleration/audit_20261003_wave37_transition_v1.py','acceleration/audit_20261002_wave31_transition_v1.py','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml']:pin(p)
        gates=[]
        for p,h,status in [(BASE+'registrar_v11_engineering01/summary.json','d973da97edf0f532928b7e27688418a436148ee7ed3797d827d5f42d43f28a02','INDEPENDENT_REGISTRAR_V11_EXACT_ADAPTER_ENGINEERING_PASS'),(BASE+'registrar_v12_engineering01/summary.json','25e2d4a3f5b73f3769e4be126423fcb2787d7ed3bac25ba998ec7eee6994d015','INDEPENDENT_REGISTRAR_V12_EXACT_ADAPTER_ENGINEERING_PASS')]:
            q=read(p,h);need(q['status']==status,'INDEPENDENT_ENGINEERING_GATES');gates.append({'path':p,'sha256':h,'status':status})
        need(hashlib.file_digest((ROOT/'CLAIMS.yaml').open('rb'),'sha256').hexdigest()==live and hashlib.file_digest((ROOT/'.git/index').open('rb'),'sha256').hexdigest()==index,'LIVE_LEDGER_INDEX_UNCHANGED')
        report={'status':'INDEPENDENT_WAVE38_EXACT343_TO350_TRANSITION_PASS','timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/checkpoint_audit','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,'before_frozen_ledger_sha256':CHAIN[0][1],'after_frozen_ledger_sha256':CHAIN[-1][2],'unchanged_prior_claims':343,'current_claims':350,'new_claim_ids':list(BINDINGS),'status_counts':dict(Counter(c['status'] for c in new.values())),'review_counts':dict(Counter(c['review_state'] for c in new.values())),'controls':controls,'terminal_records':terminals,'registrar_engineering_gates':gates,'mathematical_replays':0,'new_exclusions':0,'target_resolution':'UNKNOWN','overall_search_coverage':'UNKNOWN; no validated denominator.','live_ledger_unchanged':True,'index_unchanged':True,'shared_components':['Pinned independent duplicate-key/ID YAML parsing and prior metadata transition projection; no registrar or discovery imports.','Python SHA256/JSON/integers and supported command deadline/Windows Job containment.'],'limitations':['All343 prior claim/verification records and every prior artifact field preserved. This is a metadata/evidence-identity impact audit, not fresh mathematical approval.','Generic code theorem uses only its stated weight domain; rank67/rank76 implications retain hypothetical target premise UNKNOWN. The rank76 use of rank67 evidence is explicitly ONLY its independent kernel-weight derivation. No upper72 premise or target exclusion.','Parity certificates exclude zero651profiles and establish no integer count feasibility, rank or realized graph.','Reset is graph-only; warm proposal counters/sparse900gaps and unknown earliest selection do not certify full trajectory. Both pinned raw graphs remain non-SRG and have no full CN2 roots.','New evidence remains LOCAL_ONLY until separate immutable publication/recovery. No new scientific workers launched or historical mathematics replayed.'],'elapsed_seconds':time.monotonic()-start,'deadline':deadline.status()}
        save(out/'summary.json',report);print(json.dumps({'status':report['status'],'report_sha256':pin((out/'summary.json').relative_to(ROOT).as_posix()),'elapsed_seconds':report['elapsed_seconds'],'controls':len(controls)}),flush=True)
    except BaseException as e:
        save(out/'failure.json',{'error':repr(e),'stage':getattr(e,'stage',None),'inputs_sha256':pins,'elapsed_seconds':time.monotonic()-start,'outputs_preserved':True});raise
if __name__=='__main__':main()
