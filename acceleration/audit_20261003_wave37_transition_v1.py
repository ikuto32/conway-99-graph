"""Independent frozen337-to343 impact check; no registrar imports or math replay."""
import argparse,copy,hashlib,json,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline
from audit_20261002_wave31_transition_v1 import UniqueLoader,indexed

ROOT=Path(__file__).resolve().parents[1]
START='5bd21f4126fea49e84e54b6d4bd63e4401b31d62727b72198d2c97c36c9e0ed3'
MIDDLE='924760d3ffbb74840d0f65b59b2e40b5c8ef0d0608e42cf158f62c97f349feba'
REG1='acceleration/results/20261003_wave37_registration01'
REG2='acceleration/results/20261003_wave37_registration02'
BASE='acceleration/results/20261003_independent_review/'
PILOT='C-HYPERGRAPH-WEIGHT60-V2-PILOT01-SAVED-OBJECTS'
GF2='C-UNRESTRICTED-ROOTED7-CONTENT-DIVIDED-GF2-FOUR-PRIMALS'
CENSUS='C-HYPERGRAPH-WEIGHT60-PILOT01-TWO-GRAPH-WARM-ROOT-CENSUS'
REF='C-GENERIC-BINARY-PROJECTION-CODOMAIN-ISOTROPY-RANK-LEMMA'
CAT='C-UNRESTRICTED-ROOTED8-NONEDGE-LOCAL-CATALOGUE-COVERAGE'
MODEL='C-UNRESTRICTED-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING'
BINDINGS={
 PILOT:(BASE+'weight60_pilot01/claim_binding.json','f0c43192a25e9a99e428b181877b5d61890a152c8d5575a90d9fa2987547f063'),
 GF2:(BASE+'root7_mod2_full02/claim_binding.json','59be79ef4fed77ee65ce500dcbaf22eb1f4788dd53d187f97166e909d2b881e3'),
 CENSUS:('acceleration/results/20261003_weight60_root_census_binding01/claim_binding_schema2_draft.json','b3fd150fe6a36c0bac66984c4940fe48957c64dd323fbeb15ba7c91069feb2fb'),
 REF:(BASE+'rejected_incidence_rank01/claim_binding.json','518ac2e90784fe6d14d0ac5a933f77ca4fd4255ad1ab58b48262b5c6b4a64d4b'),
 CAT:(BASE+'rooted8_unrestricted_catalogue01/claim_binding_schema2.json','34f1290562689a1204794cf484a65d5b851ceeb8d138cbebb233d83c2491e3c8'),
 MODEL:(BASE+'rooted8_unrestricted_model01/claim_binding_schema2.json','45e8878f0addc74b92a75d3a70af30bca2923f9407e4fdb5969e031d2a89bdd2')}

class AuditError(ValueError):
    def __init__(self,stage,detail=''):self.stage=stage;super().__init__(stage+(': '+detail if detail else ''))
def need(ok,stage,detail=''):
    if not ok:raise AuditError(stage,detail)
def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')

def projection(cid,b,r):
    need(b['id']==cid and b['revision']==b['claim_revision']==1 and b['review_state']=='CLEAR','EXACT_REVISION')
    need(b['status']==('REFUTED' if cid==REF else 'VERIFIED'),'EXACT_BOUND_STATUS')
    need(set(b['scope'])=={'description','unrestricted_target','target_resolution'} and b['scope']['target_resolution']=='NONE','EXACT_NARROW_SCOPE')
    need(b['producer']!=b['verifier'] and isinstance(b['shared_components'],list),'INDEPENDENT_ROLE_DISCLOSURE')
    if 'statement' in r:need(r['statement']==b['statement'],'EXACT_REPORT_STATEMENT')
    if cid==PILOT:
        need((b['producer'],b['verifier'],b['method'])==('/root/native_driver','/root/structural','independent_artifact_check'),'PILOT_ROLES')
        need(r['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS' and r['saved_state_files']==103 and r['complete_integer_saved_current_best_objects']==206 and r['sparse_records']==3047 and r['full_anchored_proposals']==2147 and r['unanchored_records']==900 and r['target_zero_candidates']==0 and r['target_resolution'] is False,'EXACT_SAVED_OBJECT_SCOPE')
        for key in ('final_current_diagnostics','final_best_diagnostics'):
            q=r[key];need(q['domain_valid'] is True and q['srg_valid'] is False and q['identity_mismatches']==4934 and q['lambda_energy']==0 and q['mu_energy']==3608 and q['weighted_energy']==q['base_energy']==3608,'EXACT_NON_SRG_OBJECT')
        need(r['first_selection_earliest_full_trajectory'] is False and b['scope']['unrestricted_target'] is False,'NO_COMPLETE_TRAJECTORY_OR_TARGET_PROMOTION')
    elif cid==GF2:
        need((b['producer'],b['verifier'],b['method'])==('/root/structural','/root','independent_artifact_check'),'GF2_ROLES')
        need(r['status']=='INDEPENDENT_UNRESTRICTED_ROOT7_CONTENT_DIVIDED_MOD2_LITERAL_CHECK_V1_PASS' and r['normalization_rows_checked']==11769 and r['complete_scalar_primal_row_checks']==47076 and r['profile_population']==r['compatible_profiles']==651 and r['excluded_profiles']==0 and r['rank_asserted'] is False and r['target_resolution']=='NONE','EXACT_GF2_NO_EXCLUSION')
        need(b['dependencies']==[{'id':'C-UNRESTRICTED-ROOTED7-MARKED-REROOT-MEAN-NECESSARY-ENCODING','revision':1,'relation':'verification_dependency','reason':'Pinned independently reconstructed necessary-model semantics supplies the interpretation; literal mod2 certificates do not rederive this encoding.'}],'EXACT_GF2_REUSED_DEPENDENCY')
    elif cid==CENSUS:
        need((b['producer'],b['verifier'],b['method'])==('/root/native_driver','/root','independent_artifact_check'),'CENSUS_ROLES')
        need(r['status']=='INDEPENDENT_WEIGHT60_TWO_GRAPH_DENSE_ROOT_CENSUS_V1_PASS' and (r['raw_graphs'],r['complete_roots'],r['literal_triangle_population'],r['complete_scalar_matrix_entries'])==(2,198,313698,19602) and r['target_resolution']=='NONE','EXACT_LITERAL_CENSUS_SCOPE')
        values=[(q['label'],q['matching_roots'],q['fully_cn2_roots'],q['minimum_mu_row_residual'],q['minimum_root_ties']) for q in r['graph_records']]
        need(values==[('final_best',99,0,50,[81]),('first_lambda0',99,0,66,[29])] and b['dependencies']==[],'EXACT_ZERO_WARM_ROOTS')
    elif cid==REF:
        need((b['producer'],b['verifier'],b['method'])==('/root','/root/structural','independent_artifact_check') and b['original_false_argument_originator']=='/root/structural','REFUTATION_ROLES_ORIGIN')
        need(r['status']=='INDEPENDENT_REJECTED_CODOMAIN_ISOTROPY_COUNTEREXAMPLE_PASS' and r['ranks']=={'P':54,'M':45,'B':99,'C':54} and r['target_bound_status']=='UNKNOWN' and r['counterexample_sha256']=='94d4c5331f30bf86db9d0cac0fb7821ee37d3d770536880429b55267a1d33faf' and r['target_resolution'] is False,'ONLY_GENERIC_LEMMA_REFUTED')
        need(b['scope']['unrestricted_target'] is False and b['dependencies']==[],'NO_TARGET_RANK_REFUTATION')
    elif cid==CAT:
        need((b['producer'],b['verifier'],b['method'])==('/root/structural','/root/checkpoint_audit','independent_artifact_check'),'CATALOGUE_ROLES')
        need(r['status']=='INDEPENDENT_COMPLETE_UNRESTRICTED_ROOTED8_CATALOGUE_PASS' and (r['parent_classes'],r['labelled_augmentation_attempts'],r['locally_admissible_extensions'],r['complete_unrestricted_rooted_classes'],r['exact_labelled_image_checks'])==(2770,354560,134594,20524,14777280) and r['prism_filter_applied'] is False and r['target_resolution'] is False and r['new_exclusions']==0,'EXACT_COMPLETE_FINITE_CATALOGUE')
        need(b['dependencies']==[{'id':'C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE','revision':1,'relation':'coverage'}] and b['scope']['unrestricted_target'] is True,'EXACT_COVERAGE_DEPENDENCY')
    else:
        need((b['producer'],b['verifier'],b['method'])==('/root/structural','/root/checkpoint_audit','independent_derivation'),'OPERATOR_ROLES')
        need(r['status']=='INDEPENDENT_UNRESTRICTED_ROOTED8_MARKED_UNIVERSAL5_PRODUCT_MODEL_PASS' and (r['variables'],r['rows'],r['nonzeros'],r['inherited_rows'],r['marked_extension_rows'],r['upper_pair_product_rows'],r['free_deletions_checked'],r['every_lower_isomorphism_checks'])==(23334,86434,985893,11769,70837,3828,123144,4838942) and r['target_resolution'] is False and r['graph_realizability_asserted'] is False,'EXACT_NECESSARY_OPERATOR_SCOPE')
        need(b['dependencies']==[{'id':'C-UNRESTRICTED-ROOTED7-MARKED-REROOT-MEAN-NECESSARY-ENCODING','revision':1,'relation':'uses_result'},{'id':'C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY','revision':1,'relation':'uses_result'},{'id':CAT,'revision':1,'relation':'coverage'}] and b['scope']['unrestricted_target'] is True and b['written_proof']['sha256']=='f14c53a486bf6db35664e381937911d770939cc436e86618af0ab61beefb9dc7','EXACT_NECESSARY_DEPENDENCIES_PROOF')
    if cid in (GF2,CENSUS):need(b['scope']['unrestricted_target'] is False,'FINITE_CHECKING_SCOPE')
    paths={BINDINGS[cid][0]:BINDINGS[cid][1],b['report']:b['report_sha256']}
    for p,h in b.get('inputs_sha256',{}).items():need(p not in paths or paths[p]==h,'CONSISTENT_CLOSURE');paths[p]=h
    for key in ('artifacts','evidence'):
        values=b.get(key,[])
        if isinstance(values,dict):
            for k,p in values.items():
                if not k.endswith('_sha256'):
                    need(k+'_sha256' in values,'PAIRED_EVIDENCE');h=values[k+'_sha256'];need(p not in paths or paths[p]==h,'CONSISTENT_CLOSURE');paths[p]=h
        else:
            need(isinstance(values,list),'EVIDENCE_COLLECTION')
            for q in values:
                if isinstance(q,dict) and 'path' in q:need(q['path'] not in paths or paths[q['path']]==q['sha256'],'CONSISTENT_CLOSURE');paths[q['path']]=q['sha256']
    return {'paths':paths,'controls':b.get('controls',r.get('controls',r.get('corrupted_controls_rejected')))}

def transition(before,after,ids,bindings,gold):
    old,new=indexed(before['claims']),indexed(after['claims']);oldarts,arts=indexed(before['artifacts']),indexed(after['artifacts'])
    need(set(new)-set(old)==set(ids) and set(old)<=set(new),'EXACT_NEW_IDS')
    need(all(new[cid]==q for cid,q in old.items()),'ALL_PRIOR_CLAIMS_UNCHANGED')
    need(after['claims'][:len(before['claims'])]==before['claims'],'ALL_PRIOR_ORDER_UNCHANGED')
    need(set(oldarts)<=set(arts) and all(arts[aid]==q for aid,q in oldarts.items()),'ALL_PRIOR_ARTIFACTS_UNCHANGED')
    for key in set(before)|set(after):
        if key not in ('claims','artifacts','updated_at'):need(before[key]==after[key],'TOPLEVEL_SEMANTICS_UNCHANGED')
    need(after['target']['status']=='UNKNOWN' and after['target']['overall_search_coverage'] is None,'TARGET_AND_COVERAGE_UNKNOWN')
    new_evidence=set()
    for cid in ids:
        c,b,g=new[cid],bindings[cid],gold[cid]
        for key in ('id','revision','statement','kind','basis','status','review_state','assumptions','limitations'):need(c[key]==b[key],'BOUND_FIELD',cid+':'+key)
        need(c['scope']==b['scope'],'BOUND_SCOPE');deps=[{k:d[k] for k in ('id','revision','relation')} for d in b['dependencies']]
        need(c['dependencies']==deps,'BOUND_DEPENDENCY_RELATION')
        for d in deps:need(d['id'] in new and new[d['id']]['revision']==d['revision'],'ACTUAL_PINNED_DEPENDENCY')
        notes=[{k:d[k] for k in ('id','revision','reason')} for d in b['dependencies'] if 'reason' in d]
        need(json.loads(c['unknowns']['dependency_notes'])==notes,'BOUND_DEPENDENCY_REASON')
        need(json.loads(c['unknowns']['premises'])==b.get('premise_state',b.get('mathematical_scope',{})),'BOUND_PREMISE_STATE')
        need(c['unknowns']['original_binding_method']==b['method'] and c['unknowns']['original_binding_kind']==b['kind'] and c['unknowns']['original_binding_scope']=='No schema projection; binding uses the schema scope fields directly.','BOUND_ORIGINAL_NOTES')
        need(c['external_source'] is None and len(c['verification'])==1,'ONE_INDEPENDENT_RECORD')
        q=c['verification'][0];need((q['claim_revision'],q['verifier'],q['method'],q['outcome'])==(1,b['verifier'],b['method'],'PASS'),'BOUND_VERIFICATION_ROLE_METHOD')
        need(q['timestamp']==b['verification_timestamp'] and q['command_or_audit']==b['report'] and q['scope']==b['scope']['description'] and q['limitations']==b['limitations'],'BOUND_VERIFICATION_SCOPE')
        need(q['shared_components']==b['shared_components'],'BOUND_SHARED_COMPONENTS');need(len(q['controls'])==1 and json.loads(q['controls'][0])==g['controls'],'BOUND_CONTROLS')
        actual={arts[aid]['path']:arts[aid]['sha256'] for aid in c['evidence']}
        need(actual==g['paths'] and len(c['evidence'])==len(actual) and [arts[aid]['path'] for aid in c['evidence']]==sorted(actual),'COMPLETE_EXACT_BOUND_EVIDENCE')
        need(set(q['artifact_hashes'])==set(c['evidence']) and all(q['artifact_hashes'][aid]==arts[aid]['sha256'] for aid in c['evidence']),'EXACT_REVISION_HASH_BINDING')
        need(all(arts[aid]['availability']=='LOCAL_ONLY' for aid in c['evidence']),'NO_UNCONFIRMED_PUBLIC_PROMOTION')
        need(c['reproducibility']['manifest'] in c['evidence'] and arts[c['reproducibility']['manifest']]['path']==b['report'],'EXACT_REPRODUCIBILITY_ENTRY')
        need(all(datetime.fromisoformat(c[k]).tzinfo is not None for k in ('created_at','updated_at')),'TIMEZONE_RECORDS')
        new_evidence.update(c['evidence'])
    need(set(arts)-set(oldarts)==new_evidence,'NO_UNBOUND_NEW_ARTIFACTS')
    return old,new,arts

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--registration02-summary-sha256',required=True);ap.add_argument('--final-sha256',required=True);args=ap.parse_args()
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Frozen337to343 six exactr1 statements/dependencies/roles/status and directhash evidence impact; metadata only150worker20reserve')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'BOUNDED_OUTPUT');out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'DEADLINE_RESERVE')
        if p in pins:need(h is None or pins[p]==h,'INPUT_HASH');return pins[p]
        with (ROOT/p).open('rb') as stream:a=hashlib.file_digest(stream,'sha256').hexdigest()
        need(h is None or h==a,'INPUT_HASH',p);pins[p]=a;return a
    def read(p,h=None):pin(p,h);return json.loads((ROOT/p).read_bytes())
    def ledger(p,h):pin(p,h);return yaml.load((ROOT/p).read_text(encoding='utf8'),Loader=UniqueLoader)
    try:
        bs={cid:read(p,h) for cid,(p,h) in BINDINGS.items()};rs={cid:read(b['report'],b['report_sha256']) for cid,b in bs.items()};gold={cid:projection(cid,bs[cid],rs[cid]) for cid in bs}
        summaries=[read(REG1+'/summary.json','88ecd369eed6073bd5714cc2f6516a703b5119ff6b01533f988a213f966a8e42'),read(REG2+'/summary.json',args.registration02_summary_sha256)]
        expected=[(START,MIDDLE,list(BINDINGS)[:4]),(MIDDLE,args.final_sha256,list(BINDINGS)[4:])];snapshots=[]
        for reg,s,(beforeh,afterh,ids) in zip((REG1,REG2),summaries,expected):
            need(s['before_ledger_sha256']==beforeh and s['ledger_sha256']==afterh and s['new_claim_ids']==ids and s['mathematical_replays']==0 and s['new_exclusions']==0 and s['target_resolution']=='UNKNOWN','FROZEN_EXACT_CHAIN')
            before,after=ledger(reg+'/CLAIMS.before.yaml',beforeh),ledger(reg+'/CLAIMS.after.yaml',afterh)
            if snapshots:need(snapshots[-1][1]==before,'CONTIGUOUS_EXACT_SEMANTICS')
            transition(before,after,ids,bs,gold);snapshots.append((before,after))
        before,after=snapshots[0][0],snapshots[-1][1];old,new,arts=transition(before,after,BINDINGS,bs,gold)
        need(len(old)==337 and len(new)==343 and Counter(c['status'] for c in new.values())=={'VERIFIED':335,'CANDIDATE':3,'REFUTED':5} and all(c['review_state']=='CLEAR' for c in new.values()),'EXACT_CLAIM_POPULATIONS')
        for g in gold.values():
            for p,h in g['paths'].items():pin(p,h)
        terminals=[]
        for n in ('01','02'):
            p='acceleration/results/20261003_wave37_registration_supervision'+n+'/summary.json';r=read(p);need(r['command_exit_code']==0 and r['cleanup']['reaped'] is True and r['cleanup']['job_active_zero_observed'] is True,'ACTUAL_CONTAINED_REGISTRATION');terminals.append({'path':p,'sha256':pins[p],'elapsed_seconds':r['elapsed_seconds'],'exit_code':0,'reaped':True,'job_empty':True})
        controls=[]
        tests=[('prior_claim','ALL_PRIOR_CLAIMS_UNCHANGED',lambda x:x['claims'][0].update(statement='changed')),
          ('prior_artifact','ALL_PRIOR_ARTIFACTS_UNCHANGED',lambda x:x['artifacts'][0].update(availability='MISSING')),
          ('generic_REFUTED_to_VERIFIED','BOUND_FIELD',lambda x:indexed(x['claims'])[REF].update(status='VERIFIED')),
          ('generic_target_rank_statement','BOUND_FIELD',lambda x:indexed(x['claims'])[REF].update(statement='Every target incidence rank is refuted')),
          ('gf2_integer_feasibility','BOUND_FIELD',lambda x:indexed(x['claims'])[GF2].update(statement='651 integer graphs exist')),
          ('census_false_warmroot','BOUND_FIELD',lambda x:indexed(x['claims'])[CENSUS].update(statement='One warm scaffold certified')),
          ('operator_prismfree','BOUND_SCOPE',lambda x:indexed(x['claims'])[MODEL]['scope'].update(description='Assume prism absence')),
          ('operator_target_resolution','BOUND_SCOPE',lambda x:indexed(x['claims'])[MODEL]['scope'].update(target_resolution='NONEXISTENCE')),
          ('catalogue_omitted_prism','BOUND_FIELD',lambda x:indexed(x['claims'])[CAT].update(statement='Prism-free catalogue only')),
          ('wrong_dependency','BOUND_DEPENDENCY_RELATION',lambda x:indexed(x['claims'])[MODEL]['dependencies'][0].update(relation='premise')),
          ('wrong_dependency_reason','BOUND_DEPENDENCY_REASON',lambda x:indexed(x['claims'])[GF2]['unknowns'].update(dependency_notes='[]')),
          ('self_approval','BOUND_VERIFICATION_ROLE_METHOD',lambda x:indexed(x['claims'])[MODEL]['verification'][0].update(verifier='/root/structural')),
          ('missing_shared_disclosure','BOUND_SHARED_COMPONENTS',lambda x:indexed(x['claims'])[PILOT]['verification'][0].update(shared_components=[])),
          ('hash_changed','EXACT_REVISION_HASH_BINDING',lambda x:indexed(x['claims'])[CAT]['verification'][0]['artifact_hashes'].update({indexed(x['claims'])[CAT]['evidence'][0]:'0'*64})),
          ('new_availability_promotion','NO_UNCONFIRMED_PUBLIC_PROMOTION',lambda x:indexed(x['artifacts'])[indexed(x['claims'])[MODEL]['evidence'][0]].update(availability='PUBLIC')),
          ('sparse_gap_limitation_omitted','BOUND_FIELD',lambda x:indexed(x['claims'])[PILOT].update(limitations=[]))]
        for label,stage,change in tests:
            bad=copy.deepcopy(after);change(bad)
            try:transition(before,bad,BINDINGS,bs,gold)
            except AuditError as e:need(e.stage==stage,'CONTROL_EXACT_STAGE',str(e));controls.append({'label':label,'stage':e.stage,'outcome':'REJECTED'})
            else:raise AuditError('CONTROL_FALSE_ACCEPT',label)
        for label,cid,stage,change in [('target_rank_refuted_report',REF,'ONLY_GENERIC_LEMMA_REFUTED',lambda x:x.update(target_bound_status='REFUTED')),('false_warmroot_report',CENSUS,'EXACT_ZERO_WARM_ROOTS',lambda x:x['graph_records'][0].update(fully_cn2_roots=1)),('gf2_rank_report',GF2,'EXACT_GF2_NO_EXCLUSION',lambda x:x.update(rank_asserted=True)),('prism_filter_report',CAT,'EXACT_COMPLETE_FINITE_CATALOGUE',lambda x:x.update(prism_filter_applied=True)),('operator_rows_omitted',MODEL,'EXACT_NECESSARY_OPERATOR_SCOPE',lambda x:x.update(rows=86433))]:
            bad=copy.deepcopy(rs[cid]);change(bad)
            try:projection(cid,bs[cid],bad)
            except AuditError as e:need(e.stage==stage,'CONTROL_EXACT_STAGE',str(e));controls.append({'label':label,'stage':e.stage,'outcome':'REJECTED'})
            else:raise AuditError('CONTROL_FALSE_ACCEPT',label)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_wave37_transition_v1_spec.md','acceleration/audit_20261002_wave31_transition_v1.py','acceleration/register_20261003_bound_claims_v10.py','acceleration/register_20261003_bound_claims_v10_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml']:pin(p)
        engineering=read(BASE+'registrar_v10_engineering01/summary.json','0692c7aa0b9bc00678da58c7508af8d59ff150a1d140f64d69a4ba17c151df54');need(engineering['status']=='INDEPENDENT_REGISTRAR_V10_EXACT_ADAPTER_ENGINEERING_PASS','INDEPENDENT_ENGINEERING_GATES')
        report={'status':'INDEPENDENT_WAVE37_EXACT337_TO343_TRANSITION_PASS','timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/checkpoint_audit','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,'before_frozen_ledger_sha256':START,'after_frozen_ledger_sha256':args.final_sha256,'unchanged_prior_claims':337,'current_claims':343,'new_claim_ids':list(BINDINGS),'status_counts':dict(Counter(c['status'] for c in new.values())),'review_counts':dict(Counter(c['review_state'] for c in new.values())),'controls':controls,'terminal_records':terminals,'mathematical_replays':0,'new_exclusions':0,'target_resolution':'UNKNOWN','overall_search_coverage':'UNKNOWN; no validated denominator.','shared_components':['Pinned prior independent duplicate-key/ID YAML parsing only. No registrar or discovery imports.','Python exact SHA256/metadata checks and supported deadline/Windows Job containment.'],'limitations':['All337 prior claims, their verification records and every prior artifact field are preserved. This audit does not reapprove mathematics or infer live global process state.','REFUTED generic lemma retains exact generic scope; PASS refers to checking its counterexample. Target-specific incidence rank<=72 remains UNKNOWN.','ROOT verifier roles are admitted only for two exact hash-bound finite claims; no target promotion.','Rooted8 catalogue covers finite local flags, and operator is necessary only; no realized graph, feasible count solution, optimizer outcome or unrestricted exclusion.','Saved-object sparse gaps and unknown earliest snapshot remain disclosed; saved lambda0 graphs still fail the exact target identity.','All new evidence remains LOCAL_ONLY pending separate immutable publication/recovery.'],'elapsed_seconds':time.monotonic()-start,'deadline':deadline.status()}
        save(out/'summary.json',report);print(json.dumps({'status':report['status'],'report_sha256':pin((out/'summary.json').relative_to(ROOT).as_posix()),'elapsed_seconds':report['elapsed_seconds']}),flush=True)
    except BaseException as e:
        save(out/'failure.json',{'error':repr(e),'stage':getattr(e,'stage',None),'inputs_sha256':pins,'elapsed_seconds':time.monotonic()-start,'outputs_preserved':True});raise
if __name__=='__main__':main()
