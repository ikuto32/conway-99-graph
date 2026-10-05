"""Independent actual350-to353 impact; metadata only, no registrar imports."""
import argparse,copy,hashlib,json,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline
from audit_20261003_wave37_transition_v1 import AuditError,need,save,transition
from audit_20261002_wave31_transition_v1 import UniqueLoader,indexed

ROOT=Path(__file__).resolve().parents[1]
REG='acceleration/results/20261003_wave39_registration01'
SUP='acceleration/results/20261003_wave39_registration_supervision01'
BEFORE='ff94b87187d712bc2fce166b8afffaa3e2155db9fbdf8a4b3179b1f3fe2e304a'
AFTER='b2796504a736ef16872ee36812d3b8ddb6446d0ea28d4883525f9ab9a3dd5679'
INDEX='68b695ba680915be542d08a9522a2a3acd329f8fd05e471b35ae27a9e0523152'
SOURCE='acceleration/register_20261003_bound_claims_v14.py'
SOURCE_SHA='6cf12f3dcb3b1e95d692d773df9e266c73101ce6ed0e9bebba0e79d00669c79b'
LOW='C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS'
RANK='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER85'
CENSUS='C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS'
LOW67='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67'
BINDINGS={LOW:('acceleration/results/20261003_incidence_low_weight_bindings02/low_counts_claim_binding_schema2_v2.json','40022e026a8c3a479bbdee2a86cecd0fccae6081b2ab153560ad7b36f077fe05'),RANK:('acceleration/results/20261003_incidence_low_weight_bindings02/rank85_claim_binding_schema2_v2.json','2080894a078a0fa04b77e155be06e1ca67d41568e4a1a284cbf5b0da30331189'),CENSUS:('acceleration/results/20261003_fixed_two_line_census_binding03/claim_binding_schema2_draft.json','b01fc9a8faa71e22187128bc2b0affc1c4e8cb74fce83a8dad2b427208b0e0f1')}
REPORTS={LOW:'626e405502f6054483d7bc722610e83788c663d50d016f34a48b248edea4c2cd',RANK:'1037b20164daf037c7544d316032b15b3fcdc6413ee3b8f7a7b4d10ad9e80fd6',CENSUS:'1d3cecc2fd8d3e689966a334af59a9af7d0a2e8c66b356b98484aef3ed79e589'}
ROLE={LOW:('/root/structural','/root/checkpoint_audit','independent_derivation'),RANK:('/root/structural','/root','independent_artifact_check'),CENSUS:('/root/native_driver','/root','independent_artifact_check')}
def typed(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def equal(a,b,stage):need(typed(a)==typed(b),stage)
def load_unique(text):
 try:return yaml.load(text,Loader=UniqueLoader)
 except ValueError as error:
  if str(error).startswith('duplicate YAML key '):raise AuditError('DUPLICATE_YAML_KEY',str(error))from error
  raise
def digest(path):
 with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def closure(cid,b,r):
 paths={BINDINGS[cid][0]:BINDINGS[cid][1],b['report']:b['report_sha256']}
 def add(path,identity):need(path not in paths or paths[path]==identity,'CONSISTENT_CLOSURE');paths[path]=identity
 for path,identity in b['inputs_sha256'].items():add(path,identity)
 for key in('artifacts','evidence'):
  rows=b.get(key,[])
  if isinstance(rows,dict):
   for label,path in rows.items():
    if not label.endswith('_sha256'):need(label+'_sha256'in rows,'PAIRED_EVIDENCE');add(path,rows[label+'_sha256'])
  else:
   need(type(rows)is list,'EVIDENCE_COLLECTION')
   for row in rows:
    if type(row)is dict and'path'in row:add(row['path'],row['sha256'])
 return dict(paths=paths,controls=b.get('controls',r.get('controls',r.get('corrupted_controls_rejected'))))
def report_scope(cid,b,r):
 need(type(b['revision'])is int and b['revision']==1 and type(b['claim_revision'])is int and b['claim_revision']==1,'TYPED_BOUND_REVISION')
 need(b['id']==cid and b['status']=='VERIFIED'and b['review_state']=='CLEAR'and(b['producer'],b['verifier'],b['method'])==ROLE[cid],'EXACT_BOUND_ROLES')
 need(set(b['scope'])=={'description','unrestricted_target','target_resolution'}and b['scope']['unrestricted_target']is(cid!=CENSUS)and b['scope']['target_resolution']=='NONE','EXACT_BOUND_SCOPE')
 need(b['report_sha256']==REPORTS[cid],'EXACT_BOUND_REPORT')
 if cid==LOW:
  equal([r['status'],r['universal_derivation_checked'],r['target_lower_word_counts'],r['strict_negative_controls'],r['target_resolution'],r['rank_bound_claimed']],['INDEPENDENT_TRIANGLE_IMAGE_LOW_WEIGHT_COUNTS_CHARACTER_V1_PASS',True,{'3':231,'4':2079,'6':24486},10,'NONE',False],'EXACT_LOWWORD_SCOPE')
  need(b['dependencies']==[]and b['kind']=='mathematical result'and b['basis']==['DERIVED'],'EXACT_LOWWORD_DEPENDENCIES')
 elif cid==RANK:
  equal([r['status'],r['complete_exact_coefficients_checked'],r['complete_nonnegative_dual_coordinates_checked'],r['complete_exact_weight_inequalities_checked'],r['exact_size_upper'],r['maximum_linear_dimension'],r['conditional_incidence_rank_lower'],r['optimum_asserted'],r['target_resolution']],['INDEPENDENT_TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_DUAL_V1_PASS',1287,99,13,[216950223385397837448,11529151026462413],14,85,False,'NONE'],'EXACT_RANK85_SCOPE')
  equal([{k:d[k]for k in('id','revision','relation')}for d in b['dependencies']],[dict(id=LOW,revision=1,relation='uses_result'),dict(id=LOW67,revision=1,relation='uses_result')],'EXACT_RANK85_DEPENDENCIES')
  need('ONLY'in b['dependencies'][1]['reason']and b['premise_state']=='UNKNOWN','EXACT_WEIGHT_ONLY_PREMISE')
 else:
  equal([r['status'],r['complete_proposals_checked'],r['frozen_labelled_proposals'],r['complete_universe'],r['absence_of_descent_asserted'],r['aggregate']['counts'],r['aggregate']['unique_valid_neighbor_graphs'],r['aggregate']['best_mu'],r['aggregate']['best_proposal_ids'],r['target_resolution']],['INDEPENDENT_TWO_LINE_COMPLETE_FIXED_GRAPH_CENSUS_V2_PASS',239085,239085,True,True,{'invalid_linearity':87996,'invalid_selection':10395,'valid_lambda_changed':140507,'valid_lambda_preserving_mu_equal':2,'valid_lambda_preserving_mu_up':185},136536,3480,[68908,68912],'NONE'],'EXACT_FINITE_CENSUS_SCOPE')
  need(b['dependencies']==[]and b['kind']=='exclusion'and b['basis']==['COMPUTED'],'EXACT_FINITE_CENSUS_DEPENDENCIES')
def editorial(b,r):return dict(claim_id=LOW,claim_revision=1,binding_sha256=BINDINGS[LOW][1],report=b['report'],report_sha256=b['report_sha256'],written_derivation='acceleration/audit_20261003_incidence_low_weights_v1_proof.md',written_derivation_sha256='45e3e4fbb8f39547ea169f65ad0df456f09396442fceed23c4483fb9d2be9f4a',original_report_statement=r['statement'],original_report_statement_sha256='2ca15439483a3c908f42f03d4ae88e153bffec5e5546906cff15a7dbb28e8a6e',recorded_binding_statement=b['statement'],recorded_binding_statement_sha256='dc6bf21cf24d90fc2111ee366ac990bbe1437cb51e8e2e2cfaffe5023294a9f4',reason='Exact ROOT-reviewed editorial expansion gives explicit character/zero-word/three-degree convention already proved in the pinned written audit; no semantic inference by registrar and no raw statement overwritten.',mathematical_replays=0)
def checked_transition(before,after,bindings,gold,mapping):
 equal(after['claims'][:len(before['claims'])],before['claims'],'TYPED_PRIOR_CLAIMS');equal(after['artifacts'][:len(before['artifacts'])],before['artifacts'],'TYPED_PRIOR_ARTIFACTS')
 for key in set(before)|set(after):
  if key not in('claims','artifacts','updated_at'):equal(before.get(key),after.get(key),'TYPED_TARGET_TOPLEVEL')
 claims=indexed(after['claims']);need(list(claims)[len(before['claims']):]==list(BINDINGS),'EXACT_NEW_ORDER')
 for cid,b in bindings.items():
  c=claims[cid]
  for key in('id','revision','statement','kind','basis','status','review_state','assumptions','limitations','scope'):equal(c[key],b[key],'TYPED_BOUND_'+key)
  equal(c['dependencies'],[{k:d[k]for k in('id','revision','relation')}for d in b['dependencies']],'TYPED_DEPENDENCIES');need(type(c['verification'][0]['claim_revision'])is int,'TYPED_VERIFICATION_REVISION')
 transition(before,after,BINDINGS,bindings,gold)
 equal(json.loads(claims[LOW]['unknowns']['editorial_statement_mapping']),mapping,'EXACT_EDITORIAL_MAPPING');need(all('editorial_statement_mapping'not in claims[cid]['unknowns']for cid in(RANK,CENSUS)),'ONLY_ONE_EDITORIAL_MAPPING')
 return claims
def fixture(bindings,gold,mapping):
 before=dict(schema_version=2,updated_at='2026-10-03T00:00:00+00:00',claims=[dict(id=LOW67 if i==0 else'ENGINEERING_ONLY_'+str(i),revision=1,status='UNKNOWN',review_state='CLEAR')for i in range(350)],artifacts=[],target=dict(status='UNKNOWN',overall_search_coverage=None));after=copy.deepcopy(before)
 for cid,b in bindings.items():
  evidence=[];hashes={}
  for i,(path,identity)in enumerate(sorted(gold[cid]['paths'].items())):
   aid='fixture-'+cid+'-'+str(i);evidence.append(aid);hashes[aid]=identity;after['artifacts'].append(dict(id=aid,path=path,sha256=identity,availability='LOCAL_ONLY'))
  deps=[{k:d[k]for k in('id','revision','relation')}for d in b['dependencies']];notes=[{k:d[k]for k in('id','revision','reason')}for d in b['dependencies']if'reason'in d]
  claim={key:copy.deepcopy(b[key])for key in('id','revision','statement','kind','basis','status','review_state','assumptions','limitations','scope')};claim.update(dependencies=deps,evidence=evidence,external_source=None,created_at=before['updated_at'],updated_at=before['updated_at'],unknowns=dict(dependency_notes=json.dumps(notes),premises=json.dumps(b.get('premise_state',b.get('mathematical_scope',{}))),original_binding_method=b['method'],original_binding_kind=b['kind'],original_binding_scope='No schema projection; binding uses the schema scope fields directly.'),verification=[dict(claim_revision=1,verifier=b['verifier'],method=b['method'],outcome='PASS',timestamp=b['verification_timestamp'],command_or_audit=b['report'],scope=b['scope']['description'],limitations=b['limitations'],shared_components=b['shared_components'],controls=[json.dumps(gold[cid]['controls'])],artifact_hashes=hashes)],reproducibility=dict(manifest=next(aid for aid in evidence if indexed(after['artifacts'])[aid]['path']==b['report'])))
  if cid==LOW:claim['unknowns']['editorial_statement_mapping']=json.dumps(mapping)
  after['claims'].append(claim)
 return before,after
def controls(bindings,reports,gold,mapping):
 before,after=fixture(bindings,gold,mapping);checked_transition(before,after,bindings,gold,mapping);rows=[dict(label='complete_synthetic350to353',outcome='PASS')]
 def reject(label,stage,call):
  try:call()
  except AuditError as error:need(error.stage==stage,'PRECISE_CONTROL_STAGE',str(error));rows.append(dict(label=label,outcome='REJECTED',diagnostic=error.stage))
  else:raise AuditError('CORRUPTION_ACCEPTED',label)
 changes=[('prior_revision_bool','TYPED_PRIOR_CLAIMS',lambda a:a['claims'][0].update(revision=True)),('prior_status','TYPED_PRIOR_CLAIMS',lambda a:a['claims'][1].update(status='VERIFIED')),('prior_target','TYPED_TARGET_TOPLEVEL',lambda a:a['target'].update(status='VERIFIED')),('new_revision_bool','TYPED_BOUND_revision',lambda a:indexed(a['claims'])[LOW].update(revision=True)),('rank_scope_int','TYPED_BOUND_scope',lambda a:indexed(a['claims'])[RANK]['scope'].update(unrestricted_target=1)),('rank_dependency_float','TYPED_DEPENDENCIES',lambda a:indexed(a['claims'])[RANK]['dependencies'][0].update(revision=1.0)),('verification_revision_bool','TYPED_VERIFICATION_REVISION',lambda a:indexed(a['claims'])[RANK]['verification'][0].update(claim_revision=True)),('weight_only_reason','BOUND_DEPENDENCY_REASON',lambda a:indexed(a['claims'])[RANK]['unknowns'].update(dependency_notes='[]')),('premise_verified','BOUND_PREMISE_STATE',lambda a:indexed(a['claims'])[RANK]['unknowns'].update(premises='"VERIFIED"')),('self_approval','BOUND_VERIFICATION_ROLE_METHOD',lambda a:indexed(a['claims'])[LOW]['verification'][0].update(verifier='/root/structural')),('finite_as_target','TYPED_BOUND_scope',lambda a:indexed(a['claims'])[CENSUS]['scope'].update(unrestricted_target=True)),('PUBLIC_promotion','NO_UNCONFIRMED_PUBLIC_PROMOTION',lambda a:a['artifacts'][0].update(availability='PUBLIC')),('lost_editorial_string','EXACT_EDITORIAL_MAPPING',lambda a:indexed(a['claims'])[LOW]['unknowns'].update(editorial_statement_mapping='{}')),('missing_evidence','COMPLETE_EXACT_BOUND_EVIDENCE',lambda a:indexed(a['claims'])[CENSUS]['evidence'].pop())]
 for label,stage,change in changes:
  bad=copy.deepcopy(after);change(bad);reject(label,stage,lambda bad=bad:checked_transition(before,bad,bindings,gold,mapping))
 for cid,field,value,stage in[(LOW,'universal_derivation_checked',1,'EXACT_LOWWORD_SCOPE'),(LOW,'strict_negative_controls',True,'EXACT_LOWWORD_SCOPE'),(RANK,'maximum_linear_dimension',14.0,'EXACT_RANK85_SCOPE'),(RANK,'conditional_incidence_rank_lower',True,'EXACT_RANK85_SCOPE'),(RANK,'optimum_asserted',0,'EXACT_RANK85_SCOPE'),(CENSUS,'frozen_labelled_proposals',239085.0,'EXACT_FINITE_CENSUS_SCOPE'),(CENSUS,'complete_universe',1,'EXACT_FINITE_CENSUS_SCOPE')]:
  bad=copy.deepcopy(reports[cid]);bad[field]=value;reject('report_'+cid+'_'+field,stage,lambda bad=bad,cid=cid:report_scope(cid,bindings[cid],bad))
 reject('duplicate_yaml_key','DUPLICATE_YAML_KEY',lambda:load_unique('a: 1\na: 2\n'));return rows
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['calibrate','check'],required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256');args=ap.parse_args();start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent metadata350to353 impact from actualV14 plus own typed controls; prior protected31.7s supports150worker20reserve; no math or registrar import');out=args.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT_BOUNDARY');out.mkdir(parents=True,exist_ok=False);pins={}
 def pin(name,expected=None):
  need(deadline.status()['remaining_seconds']>20,'DEADLINE_RESERVE');path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'INPUT_BOUNDARY');actual=digest(path);need(expected is None or actual==expected,'INPUT_HASH',name);need(name not in pins or pins[name]==actual,'INPUT_STABLE');pins[name]=actual;return actual
 def read(name,expected=None):pin(name,expected);return json.loads((ROOT/name).read_bytes())
 try:
  for path in[Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261003_wave39_transition_v2_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml']:pin(path)
  pin('acceleration/audit_20261003_wave37_transition_v1.py','2dddfc6aa574692f45f1cf02e1f62d0793681687e1ff80b316bb967acb4c6a67');pin('acceleration/audit_20261002_wave31_transition_v1.py','5cdb4a68f14d19f97f6326d0fd594e84e8ca732c10225207b9a1b10f29e7b75e')
  bs={cid:read(*pair)for cid,pair in BINDINGS.items()};rs={cid:read(b['report'],REPORTS[cid])for cid,b in bs.items()};gold={cid:closure(cid,b,rs[cid])for cid,b in bs.items()}
  for cid in bs:report_scope(cid,bs[cid],rs[cid])
  mapping=editorial(bs[LOW],rs[LOW]);tested=controls(bs,rs,gold,mapping);save(out/'controls.json',tested)
  common=dict(timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/structural',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),mathematical_replays=0,registrar_imports=0,live_mutations=False)
  if args.mode=='calibrate':save(out/'summary.json',dict(**common,status='INDEPENDENT_WAVE39_TYPED_TRANSITION_CALIBRATION_V2_PASS',inputs_sha256=pins,positive_controls=1,strict_negative_controls=len(tested)-1,actual_transition_inspected=False));print('INDEPENDENT_WAVE39_TYPED_TRANSITION_CALIBRATION_V2_PASS');return
  need(args.calibration is not None and args.calibration_sha256 is not None,'CALIBRATION_REQUIRED');cal=read(args.calibration.resolve().relative_to(ROOT).as_posix(),args.calibration_sha256);need(cal['status']=='INDEPENDENT_WAVE39_TYPED_TRANSITION_CALIBRATION_V2_PASS'and cal['actual_transition_inspected']is False,'CALIBRATION_PREACTUAL');need(all(cal['inputs_sha256'].get(path)==identity for path,identity in pins.items()if path!=args.calibration.resolve().relative_to(ROOT).as_posix()),'EXACT_CALIBRATED_SOURCE_INPUTS')
  pin(SOURCE,SOURCE_SHA);pin(SOURCE.replace('.py','_spec.md'),'d4ea135b838fd6d536b9566ca2168d01481fa003adc7431bdf7c99ad405330db');gate=read('acceleration/results/20261003_independent_review/registrar_v14_engineering02/summary.json','13504413bfb43b9daaf6a97fdf014af721a439359482c12be4d4a2f707637e4a');need(gate['status']=='INDEPENDENT_REGISTRAR_V14_EXACT_EDITORIAL_ADAPTER_ENGINEERING_PASS','ENGINEERING_GATE')
  pin('.git/index',INDEX);pin('CLAIMS.yaml',AFTER);s=read(REG+'/summary.json','ce7bf68d13d6356fdb3fb267e7372b435a3958bfb91a56c6d0b63a062318402c');before=load_unique((ROOT/REG/'CLAIMS.before.yaml').read_text(encoding='utf8'));pin(REG+'/CLAIMS.before.yaml',BEFORE);after=load_unique((ROOT/REG/'CLAIMS.after.yaml').read_text(encoding='utf8'));pin(REG+'/CLAIMS.after.yaml',AFTER);claims=checked_transition(before,after,bs,gold,mapping)
  need(len(before['claims'])==350 and len(claims)==353,'EXACT_POPULATION');equal(dict(Counter(c['status']for c in claims.values())),{'VERIFIED':345,'CANDIDATE':3,'REFUTED':5},'EXACT_STATUS_COUNTS');need(all(c['review_state']=='CLEAR'for c in claims.values()),'EXACT_CLEAR_COUNT')
  expected=[s['command'][0],SOURCE,'--out',REG,'--previous-sha256',BEFORE]
  for cid,pair in BINDINGS.items():expected+=['--binding',pair[0],'--binding-sha256',pair[1]]
  equal(s['command'],expected,'EXACT_REGISTRAR_ARGV');equal([s['before_ledger_sha256'],s['ledger_sha256'],s['source_sha256'],s['new_claim_ids'],s['claim_records'],s['mathematical_replays'],s['target_resolution'],s['editorial_statement_mappings']],[BEFORE,AFTER,SOURCE_SHA,list(BINDINGS),353,0,'UNKNOWN',[mapping]],'EXACT_ACTUAL_REGISTRAR_REPORT')
  sup=read(SUP+'/summary.json');manifest=read(SUP+'/manifest.json');equal(manifest['command'][1:],expected[1:],'EXACT_SUPERVISOR_ARGV');need(manifest['seconds']==180 and manifest['shutdown_reserve_seconds']==30 and sup['invocation_id']==manifest['invocation_id']and sup['command_exit_code']==0 and sup['cleanup']['reaped']is True and sup['cleanup']['job_active_zero_observed']is True and sup['cleanup']['cleanup_errors']==[],'ACTUAL_EMPTY_JOB')
  for cid in BINDINGS:
   for path,identity in gold[cid]['paths'].items():pin(path,identity)
  pin(REG+'/validation.json');equal(load_unique((ROOT/'CLAIMS.yaml').read_text(encoding='utf8')),after,'LIVE_AFTER_MATCH');need(digest(ROOT/'.git/index')==INDEX and digest(ROOT/'CLAIMS.yaml')==AFTER,'LIVE_UNCHANGED')
  report=dict(**common,status='INDEPENDENT_WAVE39_EXACT350_TO353_TRANSITION_V2_PASS',inputs_sha256=pins,before_ledger_sha256=BEFORE,after_ledger_sha256=AFTER,unchanged_prior_claims=350,current_claims=353,new_claim_ids=list(BINDINGS),status_counts={'VERIFIED':345,'CANDIDATE':3,'REFUTED':5},review_counts={'CLEAR':353},new_finite_exclusion_kind_claims=1,new_unrestricted_exclusion_claims=0,exact_editorial_mapping=mapping,prior_claims_artifacts_target_unchanged=True,strict_negative_controls=len(tested)-1,index_before_sha256=INDEX,index_after_sha256=INDEX,target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator.',terminal_record=dict(path=SUP+'/summary.json',sha256=pins[SUP+'/summary.json'],elapsed_seconds=sup['elapsed_seconds'],reaped=True,job_empty=True),shared_components=['Pinned previous independently authored Wave37 field-projection/evidence checker and Wave31 duplicate-key/ID parsing, disclosed and independently wrapped in new exact typed comparisons/controls.','No registrar or mathematical discovery/verifier imports; SHA identity checking and standard YAML serialization only.'],limitations=['Actual registration metadata/evidence binding only; no mathematical replay or new mathematical approval.','One finite labelled-neighborhood exclusion is separate from zero unrestricted target exclusions.','New evidence remains LOCAL_ONLY; old availability fields including PUBLIC stay byte-for-field preserved.','Original report and editorial binding statement strings remain exact in a single explicit mapping.'],elapsed_seconds=time.monotonic()-start,deadline=deadline.status());save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=digest(out/'summary.json'),strict_negative_controls=report['strict_negative_controls'])))
 except BaseException as error:save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,outputs_preserved=True,live_mutations=False,deadline=deadline.status()));raise
if __name__=='__main__':main()
