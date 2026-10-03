"""Independent source-diff and protected finite engineering controls for registrar V10."""
import argparse,ast,copy,hashlib,importlib.util,json,os,platform,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/register_20261002_bound_claims_v9.py'
NEW='acceleration/register_20261003_bound_claims_v10.py'
PINS={OLD:'d1dd5e3a6316b7ef77f7234f406cb405a52b9c9c81b224caf0d4392fa4bcef28',NEW:'cf6a12cee68ff206f6493953cd6ab8a07c1c8d04dbe1ad91d944694acb6d348d','acceleration/register_20261003_bound_claims_v10_spec.md':'fc75979786e26661afc2eb04c312713353e00cb59212346b0b9c073ae19c5911'}
BINDINGS=[
 ('acceleration/results/20261003_independent_review/root7_mod2_full02/claim_binding.json','59be79ef4fed77ee65ce500dcbaf22eb1f4788dd53d187f97166e909d2b881e3'),
 ('acceleration/results/20261003_weight60_root_census_binding01/claim_binding_schema2_draft.json','b3fd150fe6a36c0bac66984c4940fe48957c64dd323fbeb15ba7c91069feb2fb'),
 ('acceleration/results/20261003_independent_review/rejected_incidence_rank01/claim_binding.json','518ac2e90784fe6d14d0ac5a933f77ca4fd4255ad1ab58b48262b5c6b4a64d4b'),
 ('acceleration/results/20261003_independent_review/weight60_pilot01/claim_binding.json','f0c43192a25e9a99e428b181877b5d61890a152c8d5575a90d9fa2987547f063')]

class AuditError(ValueError):pass
class ProtectedLedgerWrite(RuntimeError):pass
def need(ok,why):
    if not ok:raise AuditError(why)
def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,data):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(data,stream,indent=2);stream.write('\n')
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def source_equivalence(old_source,new_source):
    old,new=ast.parse(old_source),ast.parse(new_source);removed=[]
    retained=[]
    for node in new.body:
        if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='WAVE37_EXACT' for target in node.targets):removed.append('WAVE37_EXACT');continue
        if isinstance(node,ast.FunctionDef) and node.name in ('wave37_role','wave37_report'):removed.append(node.name);continue
        retained.append(node)
    need(sorted(removed)==['WAVE37_EXACT','wave37_report','wave37_role'],'only three declared new top-level adapters')
    new.body=retained;old_main=next(node for node in old.body if isinstance(node,ast.FunctionDef) and node.name=='main');new_main=next(node for node in new.body if isinstance(node,ast.FunctionDef) and node.name=='main')
    old_by_message={node.value.args[1].value:node for node in ast.walk(old_main) if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='need' and len(node.value.args)>1 and isinstance(node.value.args[1],ast.Constant)}
    replacements=[]
    class Normalize(ast.NodeTransformer):
        def visit_Assign(self,node):
            if any(isinstance(target,ast.Name) and target.id=='exact_wave37' for target in node.targets):
                need(ast.unparse(node.value)=='wave37_role(cid, expected, binding)','exact role adapter insertion');replacements.append('exact_role_call');return None
            return self.generic_visit(node)
        def visit_Expr(self,node):
            call=node.value
            if isinstance(call,ast.Call) and isinstance(call.func,ast.Name):
                if call.func.id=='wave37_report':
                    need(ast.unparse(call)=='wave37_report(cid, report_sha, binding, report)','exact report adapter insertion');replacements.append('exact_report_call');return None
                if call.func.id=='need' and len(call.args)>1 and isinstance(call.args[1],ast.Constant) and call.args[1].value in ('independent exact-scope checking status','separate checking identity for the exact recorded discovery'):
                    message=call.args[1].value
                    need('exact_wave37' in ast.unparse(node),'only explicitly expected predicate relaxation');replacements.append(message);return copy.deepcopy(old_by_message[message])
            return self.generic_visit(node)
    Normalize().visit(new_main)
    need(sorted(replacements)==sorted(['exact_role_call','exact_report_call','independent exact-scope checking status','separate checking identity for the exact recorded discovery']),'exact four executable changes')
    need(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),'all prior executable AST behavior preserved outside exact adapters')
    return {'new_top_level':removed,'new_main_changes':replacements,'normalized_ast_identical':True}

def reject(records,label,expected,call):
    try:call()
    except ValueError as error:
        need(type(error) is ValueError and str(error)==expected,'precise control diagnostic: '+label+' got '+repr(error));records.append({'label':label,'diagnostic':str(error)})
    else:raise AuditError('negative control accepted: '+label)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Registrar V10 independent exact-source diff/protected dryrun/finite corruption controls; metadata only,150 worker seconds')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'bounded output');out.mkdir(parents=True,exist_ok=False);pins={};controls=[];guarded=[]
    before=(ROOT/'CLAIMS.yaml').read_bytes();before_sha=hashlib.sha256(before).hexdigest()
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'not completed within the allocated budget')
    def pin(name,expected=None):
        tick();name=Path(name).as_posix();actual=digest(ROOT/name);need(expected is None or actual==expected,'exact source/input '+name);pins[name]=actual
    for name,identity in PINS.items():pin(name,identity)
    for name in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),'acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/validate_claims.py','docs/claims.schema.json','uv.lock','pyproject.toml']:pin(name)
    equivalence=source_equivalence((ROOT/OLD).read_text(),(ROOT/NEW).read_text())
    old,new=load_module('subject_v9',ROOT/OLD),load_module('subject_v10',ROOT/NEW)
    bindings=[]
    for name,identity in BINDINGS:
        pin(name,identity);binding=json.loads((ROOT/name).read_bytes());pin(binding['report'],binding['report_sha256']);report=json.loads((ROOT/binding['report']).read_bytes());bindings.append((name,identity,binding,report))
    expected={binding['id']:(identity,binding['report_sha256'],binding['status'],binding['producer'],binding['verifier']) for name,identity,binding,report in bindings[:3]}
    need(new.WAVE37_EXACT==expected,'exact three-entry whitelist independently assembled from frozen bindings')
    need(len(json.loads((ROOT/BINDINGS[0][0]).read_bytes())['dependencies'])==1,'one exact model dependency')
    for name,identity,binding,report in bindings[:3]:
        cid=binding['id'];need(new.wave37_role(cid,identity,binding) is True,'positive exact adapter');new.wave37_report(cid,binding['report_sha256'],binding,report)
        reject(controls,cid+':bindinghash','exact wave37 binding identity',lambda:new.wave37_role(cid,'0'*64,binding))
        for field,value in [('status','CANDIDATE'),('review_state','QUARANTINED'),('producer',binding['verifier']),('verifier','/root/arbitrary'),('method','repeated_execution')]:
            damaged=copy.deepcopy(binding);damaged[field]=value
            reject(controls,cid+':'+field,'exact wave37 status and independent artifact roles',lambda:new.wave37_role(cid,identity,damaged))
        for field,value in [('unrestricted_target',True),('target_resolution','NONEXISTENCE')]:
            damaged=copy.deepcopy(binding);damaged['scope'][field]=value
            reject(controls,cid+':scope_'+field,'exact finite wave37 scope',lambda:new.wave37_role(cid,identity,damaged))
        reject(controls,cid+':reporthash','exact wave37 independent report',lambda:new.wave37_report(cid,'0'*64,binding,report))
        need(new.wave37_role(cid+'-ALIAS',identity,binding) is False,'aliases do not receive adapter role')
        damaged=copy.deepcopy(report)
        if cid==bindings[0][2]['id']:
            damaged['excluded_profiles']=1;diagnostic='complete literal mod2 scope only'
            dependency=copy.deepcopy(binding);dependency['dependencies'][0]['relation']='premise'
            reject(controls,cid+':dependency','exact reused necessary-model dependency',lambda:new.wave37_report(cid,binding['report_sha256'],dependency,report))
            for field,value in [('rank_asserted',True),('compatible_profiles',650),('complete_scalar_primal_row_checks',47075),('target_resolution','NONEXISTENCE')]:
                corrupt=copy.deepcopy(report);corrupt[field]=value
                reject(controls,cid+':report_'+field,diagnostic,lambda:new.wave37_report(cid,binding['report_sha256'],binding,corrupt))
        elif cid==bindings[1][2]['id']:
            damaged['complete_roots']=197;diagnostic='complete two-graph census only'
            corrupt=copy.deepcopy(report);corrupt['graph_records'][0]['fully_cn2_roots']=1
            reject(controls,cid+':false_warm_root','exact two literal graph minima and zero direct warm roots',lambda:new.wave37_report(cid,binding['report_sha256'],binding,corrupt))
            corrupt=copy.deepcopy(report);corrupt['graph_records'][0]['minimum_root_ties']=[80]
            reject(controls,cid+':wrong_minimum_label','exact two literal graph minima and zero direct warm roots',lambda:new.wave37_report(cid,binding['report_sha256'],binding,corrupt))
        else:
            damaged['ranks']['C']=27;diagnostic='exact generic counterexample, target bound remains unknown'
            corrupt=copy.deepcopy(report);corrupt['target_bound_status']='REFUTED'
            reject(controls,cid+':target_rank_refutation','exact generic counterexample, target bound remains unknown',lambda:new.wave37_report(cid,binding['report_sha256'],binding,corrupt))
        reject(controls,cid+':report_population_or_rank',diagnostic,lambda:new.wave37_report(cid,binding['report_sha256'],binding,damaged))
        tick()
    # Source controls themselves must not accept a changed old semantic guard.
    corrupted=(ROOT/NEW).read_text().replace("need(scope['target_resolution']=='NONE','no resolution promotion in this registrar')","need(True,'no resolution promotion in this registrar')")
    try:source_equivalence((ROOT/OLD).read_text(),corrupted)
    except AuditError as error:need(str(error)=='all prior executable AST behavior preserved outside exact adapters','exact AST mutation diagnostic');controls.append({'label':'changed_prior_target_guard','diagnostic':str(error)})
    else:raise AuditError('source control accepted changed prior target guard')
    def dry_run(subject,label,items):
        tick();destination=out/label;original_argv=sys.argv;original_replace=os.replace
        def block_replace(source,target):
            need(Path(target).resolve()==ROOT/'CLAIMS.yaml','only protected ledger write attempted')
            need((ROOT/'CLAIMS.yaml').read_bytes()==before,'live ledger unchanged at write barrier')
            guarded.append({'label':label,'pending':str(source),'target':str(target)});raise ProtectedLedgerWrite('Expected protected atomic write; no live ledger replacement executed.')
        try:
            os.replace=block_replace;sys.argv=[str(ROOT/NEW),'--out',str(destination),'--previous-sha256',before_sha]
            for path,identity in items:sys.argv.extend(['--binding',str(ROOT/path),'--binding-sha256',identity])
            try:subject.main()
            except ProtectedLedgerWrite:pass
            else:raise AuditError('positive dryrun did not reach protected write barrier')
        finally:os.replace=original_replace;sys.argv=original_argv
        need((ROOT/'CLAIMS.yaml').read_bytes()==before,'no liveledger mutation by protected dryrun')
        return yaml.safe_load((destination/'CLAIMS.after.yaml').read_text())
    pilot_v9=dry_run(old,'ordinary_pilot_v9',[BINDINGS[3]]);pilot_v10=dry_run(new,'ordinary_pilot_v10',[BINDINGS[3]])
    def editorial(data):
        data=copy.deepcopy(data);data.pop('updated_at')
        for claim in data['claims'][-1:]:claim['created_at']=claim['updated_at']=None
        return data
    need(editorial(pilot_v9)==editorial(pilot_v10),'ordinary pilot path exact unchanged projection')
    all_new=dry_run(new,'four_actual_bindings_v10',BINDINGS);original=yaml.safe_load(before)
    need(all_new['claims'][:len(original['claims'])]==original['claims'] and all_new['artifacts'][:len(original['artifacts'])]==original['artifacts'] and all_new['target']==original['target'],'protected actualprojection preserves all prior records/target')
    appended=all_new['claims'][len(original['claims']):]
    need([(c['id'],c['status'],c['review_state']) for c in appended]==[(b['id'],b['status'],b['review_state']) for name,identity,b,report in bindings],'actual four exact statuses and scopes')
    need(appended[2]['status']=='REFUTED' and appended[2]['verification'][0]['outcome']=='PASS','counterexample PASS retains exact REFUTED claim')
    # Wrong statements are rejected by the real main's immutable binding gate,
    # not by pretending that a mutation retains the authenticated SHA256.
    mutated=copy.deepcopy(bindings[0][2]);mutated['statement']='Unrestricted target nonexistence.';bad=out/'wrong_statement_binding.json';save(bad,mutated)
    original_argv=sys.argv
    try:
        sys.argv=[str(ROOT/NEW),'--out',str(out/'wrong_statement_main'),'--previous-sha256',before_sha,'--binding',str(bad),'--binding-sha256',BINDINGS[0][1]]
        reject(controls,'wrong_statement_real_main','immutable binding',new.main)
    finally:sys.argv=original_argv
    need((ROOT/'CLAIMS.yaml').read_bytes()==before,'ledger unchanged at completion')
    report={'status':'INDEPENDENT_REGISTRAR_V10_EXACT_ADAPTER_ENGINEERING_PASS','timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/checkpoint_audit','producer':'/root','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,'before_ledger_sha256':before_sha,'source_equivalence':equivalence,'positive_exact_adapters':3,'ordinary_pilot_projection_v9_v10_equal':True,'actual_protected_four_binding_projection':{'claims_before':len(original['claims']),'claims_after':len(all_new['claims']),'new_exact_ids':[c['id'] for c in appended],'prior_claims_artifacts_target_unchanged':True,'new_refutations':1,'new_exclusions':0},'controls':controls,'protected_write_barriers':guarded,'ledger_mutated':False,'index_mutated':False,'mathematical_replays':0,'target_resolution':'UNKNOWN','shared_components':['Registrar modules imported as engineering subjects under independently implemented source-AST comparison and protected atomic-write barriers; no mathematical producer or proof checking is invoked.','Existing schema validator/YAML serialization are trusted engineering components, not mathematical verification.'],'limitations':['Finite metadata/source controls only; no new mathematical discovery approval.','Protected dryrun snapshots are test artifacts, not actual ledger registrations. Root must execute the frozen registrar independently and a separate later impact audit must inspect its actual snapshots.','Role/REFUTED exceptions are identity-bound to three exact bindings/reports; no general ROOT-verifier or target conclusion approval.'],'elapsed_seconds':time.monotonic()-start,'deadline':deadline.status()}
    save(out/'summary.json',report);print(json.dumps({'status':report['status'],'sha256':digest(out/'summary.json'),'strict_controls':len(controls),'elapsed_seconds':report['elapsed_seconds']}))

if __name__=='__main__':main()
