"""Finite author controls only; imports helpers without invoking registrar main."""
import argparse
import ast
import copy
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/register_20261003_bound_claims_v11_2.py'
OLD_SHA='c8ae676ac9785b99f7be10dd8569088e0aa084ab4137a1bcdf37fa9c3098c67d'
NEW='acceleration/register_20261003_bound_claims_v12.py'
BINDINGS=[
 ('acceleration/results/20261003_independent_review/incidence_griesmer01/claim_binding.json','4e018e2be2705f4684b31266797571d0eaab1eeb5ce15603d4765a77265e4848'),
 ('acceleration/results/20261003_weight60_warm_root_census_binding01/claim_binding_schema2_draft.json','e49ba355e4ca8cf99e883d69594d6a972480b55aade5c6f60ecf9fe7d4566bff'),
]
LEGACY=[
 ('acceleration/results/20261003_independent_review/root8_mod2_full01/claim_binding.json','49f8bf5af0f9c634ff751b41a572bc6219e91b07bb75126ad9575c03b5f76bc1','v11'),
 ('acceleration/results/20261003_weight60_reset_binding01/claim_binding_schema2_draft.json','24bda9181cef4d872db8d1bb5e309b4c101cf9ce0b5489fc77faf730ddcab501','v11'),
 ('acceleration/results/20261003_independent_review/root7_mod2_full02/claim_binding.json','59be79ef4fed77ee65ce500dcbaf22eb1f4788dd53d187f97166e909d2b881e3','wave37'),
 ('acceleration/results/20261003_weight60_root_census_binding01/claim_binding_schema2_draft.json','b3fd150fe6a36c0bac66984c4940fe48957c64dd323fbeb15ba7c91069feb2fb','wave37'),
 ('acceleration/results/20261003_independent_review/rejected_incidence_rank01/claim_binding.json','518ac2e90784fe6d14d0ac5a933f77ca4fd4255ad1ab58b48262b5c6b4a64d4b','wave37'),
]
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def save(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def changed(value,path,replacement):
    value=copy.deepcopy(value);target=value
    for key in path[:-1]:target=target[key]
    target[path[-1]]=replacement;return value
def restore(old_text,new_text):
    old=ast.parse(old_text);new=ast.parse(new_text);removed=[];body=[]
    for node in new.body:
        if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='V12_ROOT_EXACT'for t in node.targets):removed.append('V12_ROOT_EXACT');continue
        if isinstance(node,ast.FunctionDef)and node.name in['v12_root_role','v12_root_controls','v12_root_report']:removed.append(node.name);continue
        body.append(node)
    need(sorted(removed)==['V12_ROOT_EXACT','v12_root_controls','v12_root_report','v12_root_role'],'Only declared V12 top-level additions')
    new.body=body;old_main=next(n for n in old.body if isinstance(n,ast.FunctionDef)and n.name=='main');new_main=next(n for n in new.body if isinstance(n,ast.FunctionDef)and n.name=='main');edits=[]
    original=next(n for n in ast.walk(old_main)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='need'and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant)and n.value.args[1].value=='separate checking identity for the exact recorded discovery')
    class Restore(ast.NodeTransformer):
        def visit_Assign(self,node):
            if any(isinstance(t,ast.Name)and t.id=='exact_v12'for t in node.targets):need(ast.unparse(node.value)=='v12_root_role(cid, expected, binding)','Exact V12 role call');edits.append('role_call');return None
            return self.generic_visit(node)
        def visit_Expr(self,node):
            call=node.value
            if isinstance(call,ast.Call)and isinstance(call.func,ast.Name):
                if call.func.id=='v12_root_report':need(ast.unparse(call)=='v12_root_report(cid, report_sha, binding, report)','Exact V12 report call');edits.append('report_call');return None
                if call.func.id=='need'and len(call.args)>1 and isinstance(call.args[1],ast.Constant)and call.args[1].value=='separate checking identity for the exact recorded discovery':need('exact_v12'in ast.unparse(node),'Exact V12 role alternative');edits.append('role_alternative');return copy.deepcopy(original)
            return self.generic_visit(node)
    Restore().visit(new_main)
    need(sorted(edits)==['report_call','role_alternative','role_call'],'Exactly three V12 main edits')
    need(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),'All prior executable AST preserved')
    return dict(removed_top_level=removed,main_edits=edits,normalized_restored_ast_identical=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--registrar-sha256',required=True);args=ap.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='Tiny author registrarV12 helper/AST tests only;90outer60worker20internalreserve; no main/index/ledger/science.');out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);before=(ROOT/'CLAIMS.yaml').read_bytes();pins={};negative=[]
    def pin(name,expected=None):
        need(not deadline.status()['stop_required']and deadline.status()['remaining_seconds']>20,'Not completed within allocated engineering budget')
        identity=sha(ROOT/name);need(expected is None or identity==expected,'Exact engineering input '+name);pins[name]=identity
        return json.loads((ROOT/name).read_bytes())if name.endswith('.json')else None
    def reject(label,stage,call):
        try:call()
        except ValueError as error:need(type(error)is ValueError and str(error)==stage,'Precise rejection '+label+' '+repr(error));negative.append(dict(case=label,diagnostic=stage))
        else:raise ValueError('Corruption accepted '+label)
    pin(OLD,OLD_SHA);pin(NEW,args.registrar_sha256)
    for name in['acceleration/register_20261003_bound_claims_v12_spec.md','acceleration/register_20261003_bound_claims_v12_adapter_block.txt',Path(__file__).relative_to(ROOT).as_posix(),'acceleration/calibrate_20261003_registrar_v12_helpers_v1_spec.md','acceleration/validate_claims.py','docs/claims.schema.json','pyproject.toml','uv.lock','acceleration/command_deadline.py','acceleration/run_compute_command.py']:pin(name)
    restoration=restore((ROOT/OLD).read_text(),(ROOT/NEW).read_text());old=load('old_registrar_v11_2',ROOT/OLD);new=load('new_registrar_v12',ROOT/NEW)
    positives=[]
    for name,expected in BINDINGS:
        binding=pin(name,expected);cid=binding['id'];exact=new.V12_ROOT_EXACT[cid];report=pin(binding['report'],binding['report_sha256']);control=pin(exact['controls'],exact['controls_sha256'])
        if 'proof'in exact:pin(exact['proof'],exact['proof_sha256'])
        need(new.v12_root_role(cid,expected,binding)is True,'New exact positive role');new.v12_root_report(cid,binding['report_sha256'],binding,report);new.v12_root_controls(cid,binding,report,control);positives.append(cid)
        reject(cid+':binding_hash','v12 exact binding identity',lambda:new.v12_root_role(cid,'0'*64,binding))
        for path,value in[(['id'],'OTHER'),(['revision'],2),(['claim_revision'],2),(['status'],'CANDIDATE'),(['review_state'],'QUARANTINED'),(['producer'],'/root'),(['verifier'],'/root/native_driver'),(['method'],'repeated_execution'),(['kind'],'encoding'),(['basis'],['CITED'])]:
            bad=changed(binding,path,value);reject(cid+':'+'.'.join(path),'v12 exact revision status method and separate roles',lambda bad=bad:new.v12_root_role(cid,expected,bad))
        for path,value in[(['scope','description'],'Broader target conclusion'),(['scope','unrestricted_target'],not exact['unrestricted']),(['scope','target_resolution'],'NEGATIVE')]:
            bad=changed(binding,path,value);reject(cid+':'+'.'.join(path),'v12 exact scope',lambda bad=bad:new.v12_root_role(cid,expected,bad))
        bad=changed(binding,['statement'],'Broader mathematical claim');reject(cid+':statement','v12 exact statement',lambda:new.v12_root_role(cid,expected,bad))
        bad=changed(binding,['report_sha256'],'0'*64);reject(cid+':report_reference','v12 exact report reference',lambda:new.v12_root_role(cid,expected,bad))
        bad=changed(binding,['dependencies'],[dict(id='UNKNOWN-PREMISE',revision=1,relation='premise')]);reject(cid+':dependencies','v12 exact dependencies',lambda:new.v12_root_role(cid,expected,bad))
        reject(cid+':report_hash','v12 exact independent report',lambda:new.v12_root_report(cid,'0'*64,binding,report))
        for path,value in[(['producer'],'/root'),(['verifier'],'/root/structural'),(['method'],'repeated_execution')]:
            bad=changed(report,path,value);reject(cid+':report_'+path[0],'v12 report roles and method',lambda bad=bad:new.v12_root_report(cid,binding['report_sha256'],binding,bad))
        if cid.startswith('C-UNRESTRICTED'):
            for path,value in[(['status'],'INDEPENDENT_CODE_DUAL_PASS'),(['minimum_rank'],68),(['maximum_kernel_dimension'],33),(['nonzero_kernel_weights'],[36,38]),(['target_resolution'],'NEGATIVE'),(['graph_constructed'],True),(['target_nonexistence'],True),(['rank_upper72_status'],'VERIFIED')]:
                bad=changed(report,path,value);reject(cid+':scope_'+path[0],'v12 exact conditional Griesmer scope',lambda bad=bad:new.v12_root_report(cid,binding['report_sha256'],binding,bad))
            bad=changed(binding,['premise_state'],'VERIFIED');reject(cid+':premise','v12 exact conditional Griesmer scope',lambda:new.v12_root_report(cid,binding['report_sha256'],bad,report))
            bad=changed(report,['inputs_sha256',exact['proof']],'0'*64);reject(cid+':proof_hash','v12 exact independently written proof',lambda:new.v12_root_report(cid,binding['report_sha256'],binding,bad))
            for path,value in[(['complete_kernel_population'],15),(['total_subspaces'],3289),(['minimum_word_residual_checks'],5854),(['target_dimension33_sum'],99),(['target_dimension33_griesmer_terms'],[36,18,9]),(['strict_corrupt_controls'],[])]:
                bad=changed(control,path,value);reject(cid+':controls_'+path[0],'v12 Griesmer complete finite controls',lambda bad=bad:new.v12_root_controls(cid,binding,report,bad))
            bad=changed(binding,['recorded_validation','finite_controls_are_general_proof'],True);reject(cid+':finite_proof_promotion','v12 Griesmer recorded controls',lambda:new.v12_root_controls(cid,bad,report,control))
        else:
            for path,value in[(['complete_roots'],197),(['raw_graphs'],3),(['literal_triangle_population'],313697),(['complete_scalar_matrix_entries'],19601),(['target_resolution'],'NEGATIVE')]:
                bad=changed(report,path,value);reject(cid+':population_'+path[0],'v12 exact finite warm census population',lambda bad=bad:new.v12_root_report(cid,binding['report_sha256'],binding,bad))
            for path,value in[(['graph_records',0,'fully_cn2_roots'],1),(['graph_records',0,'minimum_mu_row_residual'],50),(['graph_records',0,'minimum_root_ties'],[11]),(['graph_records',1,'global_mu_energy'],3480),(['graph_records',1,'selected_root'],11)]:
                bad=changed(report,path,value);reject(cid+':graph_'+path[-1],'v12 exact warm census graph records',lambda bad=bad:new.v12_root_report(cid,binding['report_sha256'],binding,bad))
            bad=changed(report,['inputs_sha256','acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj'],'0'*64);reject(cid+':raw_hash','v12 exact two warm raw graph identities',lambda:new.v12_root_report(cid,binding['report_sha256'],binding,bad))
            for path,value in[(['strict_negative_controls'],4),(['positive_roots'],8),(['control_timing'],'After artifact inspection')]:
                bad=changed(control,path,value);reject(cid+':controls_'+path[0],'v12 warm census complete finite controls',lambda bad=bad:new.v12_root_controls(cid,binding,report,bad))
            bad=changed(binding,['pre_output_calibration','corrupted_controls'],[]);reject(cid+':corrupt_controls_list','v12 warm census complete finite controls',lambda:new.v12_root_controls(cid,bad,report,control))
        bad=changed(binding,['inputs_sha256',exact['controls']],'0'*64);reject(cid+':control_hash','v12 exact control bytes',lambda:new.v12_root_report(cid,binding['report_sha256'],bad,report))
    need(new.v12_root_role('UNRELATED-ROOT-CLAIM','0'*64,{})is False,'Unknown ROOT ID not admitted');new.v12_root_report('UNRELATED-ROOT-CLAIM','0'*64,{},{});legacy=[]
    for name,expected,kind in LEGACY:
        binding=pin(name,expected);report=pin(binding['report'],binding['report_sha256']);cid=binding['id']
        if kind=='v11':
            need(old.v11_root_role(cid,expected,binding)==new.v11_root_role(cid,expected,binding)is True,'V11.2 role unchanged');old.v11_root_report(cid,binding['report_sha256'],binding,report);new.v11_root_report(cid,binding['report_sha256'],binding,report)
        else:
            need(old.wave37_role(cid,expected,binding)==new.wave37_role(cid,expected,binding)is True,'Wave37 role unchanged');old.wave37_report(cid,binding['report_sha256'],binding,report);new.wave37_report(cid,binding['report_sha256'],binding,report)
        legacy.append(cid)
    need((ROOT/'CLAIMS.yaml').read_bytes()==before,'Live ledger bytes unchanged')
    save(out/'summary.json',dict(status='AUTHOR_REGISTRAR_V12_HELPER_CALIBRATION_PASS_PENDING_INDEPENDENT_REVIEW',timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/structural',command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,source_restoration=restoration,new_positive_adapters=positives,legacy_positive_adapters=legacy,strict_negative_count=len(negative),strict_negative_controls=negative,unknown_ROOT_id_not_admitted=True,live_ledger_sha256_before=hashlib.sha256(before).hexdigest(),live_ledger_sha256_after=sha(ROOT/'CLAIMS.yaml'),registrar_main_called=False,ledger_mutations=0,index_mutations=0,mathematical_replays=0,scientific_invocations=0,independent_approval=False,target_resolution='NONE',deadline=deadline.status(),limitations=['Same author as V12; finite engineering controls only, not independent approval.','No registrar main, live ledger/index mutation or mathematical claim verification.','ROOT must independently gate the exact new adapter/source before live use.']))

if __name__=='__main__':main()
