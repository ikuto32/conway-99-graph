"""ROOT independent V16 metadata engineering: three protected copies, no math."""
import argparse, ast, copy, hashlib, importlib.util, json, os, platform, subprocess, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
OLD = 'acceleration/register_20261003_bound_claims_v15.py'
NEW = 'acceleration/register_20261003_bound_claims_v16.py'
C4 = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT'
RANK = 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER87'
BINDINGS = [('acceleration/results/20261003_weight5_c4_binding01/claim_binding_schema2.json','6525dae3734dc6c2f7eabcbd12db994f8c283019176388bb0f540690859225ee'),
 ('acceleration/results/20261003_triangle_rank87_binding01/claim_binding_schema2.json','dc079188f50e43ac31c9b9707e94a5f6db1fe9644c9b3dbccca4c9e02591a39d')]
PINS = {OLD:'0ab32f92cc61a4c5438a9a9a04ae8f22f99743632f5c0261cad3b1118b66ede9',NEW:'a8e7c2694817970df28ff1ec7be3d8265ba2f6e3ffe3d88798241832426c2026',
 'acceleration/register_20261003_bound_claims_v16_spec.md':'274bb9768c186225676f79ff8954a7d0a2832961d14f78d381f451b2898c8969',
 'acceleration/calibrate_20261003_registrar_v16_helpers_v1.py':'124a18798728ea38b5391346dc9a480e7648eee2d82f79495b4a6694752e44d9',
 'acceleration/calibrate_20261003_registrar_v16_helpers_v1_spec.md':'29e195675bdb9c695a662cd8a708f2a36312ddb9f29698195be7b8dce1d92fb7'}
BEFORE='a4f2f5b2ff41ea7aebf99413cdc825fc1e08f5269079d43e305da713f4af29ef'
INDEX='8bcd46056145e09d225a01e553151abd1958364077a85b5c6d1bc33fe4f4cacd'

class AuditError(ValueError): pass
class ProtectedWrite(RuntimeError): pass
def need(ok,message):
 if not ok: raise AuditError(message)
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
 with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
def equal(a,b):
 if type(a) is not type(b):return False
 if type(a) is dict:return set(a)==set(b) and all(equal(a[k],b[k]) for k in a)
 if type(a) in (list,tuple):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
 return a==b
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def structural_equivalence(old_text,new_text):
 old=ast.parse(old_text);new=ast.parse(new_text)
 def dump(n):return ast.dump(n,include_attributes=False)
 additions={'V16_EXACT','v16_role','v16_dependency_order','v16_report'};removed=[];kept=[]
 for node in new.body:
  name=node.name if isinstance(node,ast.FunctionDef) else node.targets[0].id if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) else None
  if name in additions:removed.append(name)
  else:kept.append(node)
 need(set(removed)==additions and len(removed)==4,'AST_FOUR_ADDITIONS');new.body=kept
 oldmain=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 main=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main')
 edits=[];body=[]
 for node in main.body:
  # Changes are in the existing per-binding loop. Transform only literal exact nodes.
  body.append(node)
 allowed={ast.dump(ast.parse(s).body[0],include_attributes=False):label for s,label in [
  ('exact_v16 = v16_role(cid, expected, binding)','role'),
  ("v16_dependency_order(cid, {c['id'] for c in data['claims']})",'order'),
  ('wave41_statement_mapping = v16_report(cid, report_sha, binding, report)','report'),
  ("if wave41_statement_mapping is not None:\n need(editorial_statement_mapping is None, 'v16 disjoint exact metadata adapter')\n editorial_statement_mapping = wave41_statement_mapping",'dispatch')]}
 oldguard=next(n for n in ast.walk(oldmain) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value=='separate checking identity for the exact recorded discovery')
 extended=copy.deepcopy(oldguard);extended.value.args[0].values[-1].values.append(ast.Name(id='exact_v16',ctx=ast.Load()))
 class Remove(ast.NodeTransformer):
  def visit(self,node):
   key=dump(node)
   if key in allowed:edits.append(allowed[key]);return None
   if key==dump(extended):edits.append('alternative');return copy.deepcopy(oldguard)
   return super().visit(node)
 Remove().visit(main)
 need(sorted(edits)==['alternative','dispatch','order','report','role'],'AST_FIVE_INSERTIONS')
 need(dump(old)==dump(new),'AST_OLD_FULL_RESTORED')
 return dict(top_level=sorted(removed),main_insertions=sorted(edits),complete_V15_AST_restored=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
 for name in ['author','terminal']:ap.add_argument('--'+name,required=True);ap.add_argument('--'+name+'-sha256',required=True)
 a=ap.parse_args();deadline=CommandDeadline(a.seconds,allocation_reason='Independent V16 metadata controls and protected356to358 copies; prior analogous34.453s;150worker/20save reserve;no mathematics')
 out=a.out.resolve();need(out.is_relative_to(ROOT) and not out.exists(),'FRESH_OUTPUT');out.mkdir(parents=True)
 before=(ROOT/'CLAIMS.yaml').read_bytes();pins={};controls=[];barriers=[]
 def pin(name,wanted=None):
  need(deadline.status()['remaining_seconds']>20,'SAVE_RESERVE');path=(ROOT/name).resolve();need(path.is_relative_to(ROOT) and path.is_file(),'INPUT_PATH')
  value=sha(path);need(wanted is None or value==wanted,'INPUT_IDENTITY:'+name);need(name not in pins or pins[name]==value,'INPUT_STABLE');pins[name]=value
 def reject(label,message,call):
  try:call()
  except ValueError as error:
   need(type(error) is ValueError and str(error)==message,'PRECISE_REJECTION:'+label);controls.append(dict(label=label,diagnostic=message,outcome='REJECTED'));return
  raise AuditError('ACCEPTED_CORRUPTION:'+label)
 try:
  need(hashlib.sha256(before).hexdigest()==BEFORE and sha(ROOT/'.git/index')==INDEX,'PROTECTED_BASELINE')
  for name,wanted in PINS.items():pin(name,wanted)
  for name in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_suffix('').name+'_spec.md']:
   pin(name if name.startswith('acceleration/') else 'acceleration/'+name)
  for name in ['pyproject.toml','uv.lock','acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json']:pin(name)
  pin(a.author,a.author_sha256);pin(a.terminal,a.terminal_sha256)
  author=json.loads((ROOT/a.author).read_bytes());ended=json.loads((ROOT/a.terminal).read_bytes())
  need(equal([author[k] for k in ['positive_controls','strict_negative_controls','harness_negative_controls','registrar_main_called','independent_approval']],[9,155,2,False,False]),'AUTHOR_SCOPE')
  need(ended['command_exit_code']==0 and type(ended['command_exit_code']) is int and ended['error'] is None and ended['deadline_reached'] is False and ended['cleanup']['reaped'] is True and ended['cleanup']['job_active_zero_observed'] is True and ended['cleanup']['cleanup_errors']==[],'AUTHOR_TERMINAL')
  for name,wanted in author['inputs_sha256'].items():pin(name,wanted)
  for name,wanted in author['artifacts'].items():pin(name,wanted)
  rawcontrols=json.loads((ROOT/next(k for k in author['artifacts'] if k.endswith('/controls.json'))).read_bytes())
  need(len(rawcontrols['positive'])==9 and len(rawcontrols['strict_negative'])==155 and len({r['label'] for r in rawcontrols['strict_negative']})==155 and all(r['expected_diagnostic']==r['actual_diagnostic'] and r['outcome']=='REJECTED' for r in rawcontrols['strict_negative']) and rawcontrols['harness_wrong_stage_and_type_rejected']==2,'AUTHOR_RAW_CONTROLS')
  oldtext=(ROOT/OLD).read_text(encoding='utf8');newtext=(ROOT/NEW).read_text(encoding='utf8');astcheck=structural_equivalence(oldtext,newtext)
  old=load('v16_old_subject',ROOT/OLD);new=load('v16_new_subject',ROOT/NEW);loaded=[];maps=[]
  need(list(new.V16_EXACT)==[C4,RANK],'EXACT_TWO_IDS')
  for path,identity in BINDINGS:
   pin(path,identity);b=json.loads((ROOT/path).read_bytes());pin(b['report'],b['report_sha256']);r=json.loads((ROOT/b['report']).read_bytes())
   for name,wanted in b['inputs_sha256'].items():pin(name,wanted)
   cid=b['id'];cfg=new.V16_EXACT[cid];need(cfg['binding_path']==path and cfg['binding_sha256']==identity and cfg['statement']==b['statement'] and equal(cfg['binding_metadata'],{k:b.get(k) if k in {'exact_certificate','original_independent_report_statement_field'} else b[k] for k in cfg['binding_metadata']}),'CONFIG_BOUND_TO_RAW')
   need(b['producer']=='/root/structural' and b['verifier']=='/root' and b['method']=='independent_derivation' and b['status']=='VERIFIED' and b['review_state']=='CLEAR','RAW_ROLES')
   need(new.v16_role(cid,identity,b) is True,'EXACT_ROLE');m=new.v16_report(cid,b['report_sha256'],b,r);maps.append(m);loaded.append((b,r))
   need(m['original_report_statement']==b['statement']==r[cfg['statement_field']] and m['raw_statement_changed'] is False and m['original_independent_report_method']==r['method']=='independent_derivation_and_complete_artifact_checking' and m['schema_method']=='independent_derivation' and m['mathematical_replays']==0,'LITERAL_METHOD_HEADLINE')
   for key,value,diagnostic in [('revision',True,'v16 exact typed revision status roles method kind basis'),('verifier','/root/structural','v16 exact typed revision status roles method kind basis'),('dependencies',[],'v16 exact scope assumptions dependencies and unresolved premise'),('statement','All graphs excluded','v16 exact literal statement primary report and no legacy fallback'),('inputs_sha256',{},'v16 complete literal binding metadata')]:
    bad=copy.deepcopy(b);bad[key]=value;reject(cid+':'+key,diagnostic,lambda bad=bad,cid=cid,identity=identity:new.v16_role(cid,identity,bad))
   bad=copy.deepcopy(r);bad[cfg['statement_field']]+=' altered';reject(cid+':headline','v16 exact existing raw headline field',lambda bad=bad,b=b:new.v16_report(b['id'],b['report_sha256'],b,bad))
   bad=copy.deepcopy(r);bad['inputs_sha256']={};reject(cid+':report_closure','v16 complete literal report metadata',lambda bad=bad,b=b:new.v16_report(b['id'],b['report_sha256'],b,bad))
  need(new.v16_role('C-OTHER','0'*64,{}) is False and new.v16_report('C-OTHER','0'*64,{},{}) is None,'ORDINARY_ROUTING')
  reject('reverse_dependency','v16 C4 dependency must precede rank87',lambda:new.v16_dependency_order(RANK,set()))
  for label,text,message in [('oldguard',newtext.replace("need(scope['target_resolution']=='NONE','no resolution promotion in this registrar')","need(True,'no resolution promotion in this registrar')"),'AST_OLD_FULL_RESTORED'),('rolecall',newtext.replace('exact_v16 = v16_role(cid, expected, binding)','exact_v16 = True'),'AST_FIVE_INSERTIONS')]:
   try:structural_equivalence(oldtext,text)
   except AuditError as error:need(str(error)==message,'PRECISE_AST_VETO');controls.append(dict(label=label,outcome='REJECTED',diagnostic=message))
   else:raise AuditError('AST_CORRUPTION_ACCEPTED')
  def dry(subject,label,items):
   need(deadline.status()['remaining_seconds']>20,'SAVE_RESERVE');dest=out/label;argv=sys.argv;replace=os.replace
   def barrier(source,target):
    need(Path(target).resolve()==ROOT/'CLAIMS.yaml' and Path(source).resolve()==dest/'CLAIMS.pending.yaml' and (ROOT/'CLAIMS.yaml').read_bytes()==before,'WRITE_BOUNDARY')
    save(dest/'protected_report.json',copy.deepcopy(sys._getframe(1).f_locals['report']));barriers.append(label);raise ProtectedWrite()
   try:
    os.replace=barrier;sys.argv=[str(ROOT/NEW),'--out',str(dest),'--previous-sha256',BEFORE]
    for path,identity in items:sys.argv+=['--binding',str(ROOT/path),'--binding-sha256',identity]
    try:subject.main()
    except ProtectedWrite:pass
    else:raise AuditError('NO_WRITE_BARRIER')
   finally:os.replace=replace;sys.argv=argv
   need((ROOT/'CLAIMS.yaml').read_bytes()==before,'LIVE_LEDGER_UNCHANGED');return yaml.safe_load((dest/'CLAIMS.after.yaml').read_text(encoding='utf8'))
  ordinary_source='acceleration/results/20261003_triangle_image_weight5_binding01/claim_binding_schema2.json'
  pin(ordinary_source,'e816aff2942094e61efc2652acc222fa5de8f60b9b2435c81750a4ba19e65ea7')
  ordinary=json.loads((ROOT/ordinary_source).read_bytes());ordinary.update(id='C-ENGINEERING-ONLY-V16-ORDINARY');ordinarypath=out/'ordinary_binding.json'
  # Ordinary synthetic comparison uses a separately saved exact ordinary report.
  pin(ordinary['report'],ordinary['report_sha256']);ordinaryreport=json.loads((ROOT/ordinary['report']).read_bytes());reportpath=out/'ordinary_report.json';save(reportpath,ordinaryreport)
  ordinary['report']=reportpath.relative_to(ROOT).as_posix();ordinary['report_sha256']=sha(reportpath);ordinary['inputs_sha256']=dict(ordinary['inputs_sha256']);ordinary['inputs_sha256'][ordinary['report']]=ordinary['report_sha256'];save(ordinarypath,ordinary)
  pair=[(ordinarypath.relative_to(ROOT).as_posix(),sha(ordinarypath))];one=dry(old,'ordinary_V15',pair);two=dry(new,'ordinary_V16',pair)
  def timeless(value):
   value=copy.deepcopy(value);value.pop('updated_at');value['claims'][-1]['created_at']=value['claims'][-1]['updated_at']=None;return value
  need(equal(timeless(one),timeless(two)),'ORDINARY_PROJECTION_EQUAL')
  after=dry(new,'two_exact_V16',BINDINGS);base=yaml.safe_load(before);need(len(base['claims'])==356 and len(after['claims'])==358,'EXACT356_TO358')
  need(equal(after['claims'][:356],base['claims']) and equal(after['artifacts'][:len(base['artifacts'])],base['artifacts']) and equal(after['target'],base['target']),'PRIOR_FULL_PRESERVATION')
  need([c['id'] for c in after['claims'][356:]]==[C4,RANK],'DEPENDENCY_ORDER')
  for c,(b,r),m in zip(after['claims'][356:],loaded,maps):
   need(equal({k:c[k] for k in ['id','revision','statement','kind','basis','status','review_state','scope','assumptions','limitations']},{k:b[k] for k in ['id','revision','statement','kind','basis','status','review_state','scope','assumptions','limitations']}),'CLAIM_LITERAL')
   need(equal(c['dependencies'],[{k:d[k] for k in ['id','revision','relation']} for d in b['dependencies']]),'DEPENDENCIES_LITERAL')
   v=c['verification'][0];need(v['verifier']=='/root' and v['method']=='independent_derivation' and v['claim_revision']==1 and v['command_or_audit']==b['report'],'VERIFICATION_REVISION')
   need(equal(json.loads(c['unknowns']['editorial_statement_mapping']),m),'COMBINED_METHOD_PRESERVED')
  copied=json.loads((out/'two_exact_V16/protected_report.json').read_bytes());need(copied['new_claim_ids']==[C4,RANK] and copied['claim_records']==358 and equal(copied['editorial_statement_mappings'],maps),'COPIED_REPORT')
  counts=Counter(c['status'] for c in base['claims']);counts['VERIFIED']+=2;need(Counter(c['status'] for c in after['claims'])==counts,'COUNTS')
  need((ROOT/'CLAIMS.yaml').read_bytes()==before and sha(ROOT/'.git/index')==INDEX,'PROTECTED_AFTER');save(out/'controls.json',controls);save(out/'mappings.json',maps)
  save(out/'summary.json',dict(status='INDEPENDENT_REGISTRAR_V16_TWO_EXACT_BINDINGS_ENGINEERING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/checkpoint_audit',verifier='/root',method='independent_engineering_artifact_check',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),AST_restoration=astcheck,author_subject_negatives=155,own_precise_negatives=len(controls),protected_write_barriers=barriers,claims_before=356,claims_after=358,new_claim_ids=[C4,RANK],prior_claims_artifacts_target_unchanged=True,status_counts=dict(counts),editorial_statement_mappings=maps,ledger_mutated=False,index_mutated=False,mathematical_replays=0,scientific_launched=False,target_resolution='UNKNOWN',deadline=deadline.status(),shared_components=['Subject V15/V16 modules are imported only as metadata engineering subjects; own structural AST subtraction/typed comparison and protected final os.replace interception.','YAML/schema validator, Python/JSON/SHA/deadline and exact existing evidence are trusted. No discovery or mathematical checker imports.'],limitations=['Author155 helper controls are inspected as saved finite records;14 own helper vetoes plus dependency and AST controls provide additional finite engineering checks.','Three copied end-to-end projections preserve the live356claim ledger. The ordinary Checkpoint-verifier report is explicitly a synthetic engineering copy.','No mathematical reapproval or target proof follows from this metadata gate.']))
  print('INDEPENDENT_REGISTRAR_V16_TWO_EXACT_BINDINGS_ENGINEERING_PASS',flush=True)
 except BaseException as error:
  save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,controls=controls,ledger_unchanged=(ROOT/'CLAIMS.yaml').read_bytes()==before,index_unchanged=sha(ROOT/'.git/index')==INDEX,deadline=deadline.status()));raise

if __name__=='__main__':main()
