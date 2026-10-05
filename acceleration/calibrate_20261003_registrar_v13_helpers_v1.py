"""Same-author finite metadata controls; not independent registrar approval."""
import argparse,ast,copy,hashlib,importlib.util,json,platform,sys,time
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/register_20261003_bound_claims_v12.py'
OLD_SHA='70d4082b2f73fd23e4d8fb295e36eeb0092976c01f78e99fcd342f3a96598044'
NEW='acceleration/register_20261003_bound_claims_v13.py'
BASE='acceleration/results/20261003_independent_review/'
RANK='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER85'
CENSUS='C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS'
BINDINGS={RANK:('acceleration/results/20261003_incidence_low_weight_bindings02/rank85_claim_binding_schema2_v2.json','2080894a078a0fa04b77e155be06e1ca67d41568e4a1a284cbf5b0da30331189'),CENSUS:('acceleration/results/20261003_fixed_two_line_census_binding03/claim_binding_schema2_draft.json','b01fc9a8faa71e22187128bc2b0affc1c4e8cb74fce83a8dad2b427208b0e0f1')}

def need(ok,msg):
    if not ok:raise ValueError(msg)
def save(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Same-author tiny AST/role/report metadata controls only; no registrar main/mathematics/ledger/index;60worker20reserve')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'bounded output');out.mkdir(parents=True,exist_ok=False);pins={};controls=[]
    def pin(name,identity=None):
        need(deadline.status()['remaining_seconds']>20,'not completed within allocated metadata budget')
        with (ROOT/name).open('rb')as stream:h=hashlib.file_digest(stream,'sha256').hexdigest()
        need(identity is None or h==identity,'exact input '+name);pins[name]=h;return h
    def read(name,identity=None):pin(name,identity);return json.loads((ROOT/name).read_bytes())
    def reject(label,expected,fn):
        try:fn()
        except ValueError as error:need(str(error)==expected,'exact negative diagnostic '+label+': '+str(error));controls.append(dict(case=label,outcome='REJECTED',diagnostic=str(error)));return
        raise ValueError('false acceptance '+label)
    try:
        live=pin('CLAIMS.yaml');index=pin('.git/index')
        pin(OLD,OLD_SHA);pin(NEW)
        for path in [NEW.replace('.py','_spec.md'),'acceleration/register_20261003_bound_claims_v13_additions.txt',Path(__file__).relative_to(ROOT).as_posix(),'acceleration/calibrate_20261003_registrar_v13_helpers_v1_spec.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml']:pin(path)
        old_ast=ast.parse((ROOT/OLD).read_text(encoding='utf8-sig'));new_ast=ast.parse((ROOT/NEW).read_text(encoding='utf8-sig'))
        olddefs={n.name for n in old_ast.body if isinstance(n,ast.FunctionDef)};newdefs={n.name for n in new_ast.body if isinstance(n,ast.FunctionDef)}
        need(newdefs-olddefs=={'v13_root_role','v13_root_report'} and olddefs<=newdefs,'only two new definitions')
        restored=copy.deepcopy(new_ast);restored.body=[n for n in restored.body if not(isinstance(n,ast.FunctionDef)and n.name in {'v13_root_role','v13_root_report'})]
        class Restore(ast.NodeTransformer):
            def visit_Assign(self,node):
                if any(isinstance(n,ast.Name)and n.id=='exact_v13'for n in node.targets):return None
                return self.generic_visit(node)
            def visit_Expr(self,node):
                if isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Name)and node.value.func.id=='v13_root_report':return None
                return self.generic_visit(node)
            def visit_BoolOp(self,node):
                self.generic_visit(node);node.values=[v for v in node.values if not(isinstance(v,ast.Name)and v.id=='exact_v13')];return node
        need(ast.dump(Restore().visit(restored),include_attributes=False)==ast.dump(old_ast,include_attributes=False),'complete V12 AST preserved outside declared additions')
        controls.append(dict(case='complete_V12_AST_restoration',outcome='PASS'))
        spec=importlib.util.spec_from_file_location('author_v13_helpers',ROOT/NEW);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        bs={cid:read(p,h)for cid,(p,h)in BINDINGS.items()};rs={cid:read(b['report'],b['report_sha256'])for cid,b in bs.items()}
        for cid,b in bs.items():
            need(m.v13_root_role(cid,BINDINGS[cid][1],b)is True,'exact positive adapter');controls.append(dict(case=cid+'_role',outcome='PASS'))
            m.v13_root_report(cid,b['report_sha256'],b,rs[cid]);controls.append(dict(case=cid+'_report',outcome='PASS'))
            reject(cid+'_wrong_binding','v13 exact binding identity',lambda:m.v13_root_role(cid,'0'*64,b))
            mutations=[('wrong_revision','v13 exact revision status method and separate roles',lambda x:x.update(revision=2)),
              ('boolean_revision','v13 exact revision status method and separate roles',lambda x:x.update(revision=True)),
              ('boolean_claim_revision','v13 exact revision status method and separate roles',lambda x:x.update(claim_revision=True)),
              ('wrong_status','v13 exact revision status method and separate roles',lambda x:x.update(status='CANDIDATE')),
              ('wrong_review','v13 exact revision status method and separate roles',lambda x:x.update(review_state='QUARANTINED')),
              ('self_approval','v13 exact revision status method and separate roles',lambda x:x.update(producer='/root')),
              ('wrong_verifier','v13 exact revision status method and separate roles',lambda x:x.update(verifier='/root/structural')),
              ('wrong_method','v13 exact revision status method and separate roles',lambda x:x.update(method='independent_derivation')),
              ('wrong_kind','v13 exact revision status method and separate roles',lambda x:x.update(kind='encoding')),
              ('wrong_basis','v13 exact revision status method and separate roles',lambda x:x.update(basis=['CITED'])),
              ('target_promotion','v13 exact scope',lambda x:x['scope'].update(target_resolution='EXISTS')),
              ('broader_scope','v13 exact scope',lambda x:x['scope'].update(description='All graphs')),
              ('wrong_target_scope','v13 exact scope',lambda x:x['scope'].update(unrestricted_target=not x['scope']['unrestricted_target'])),
              ('nonliteral_scope_bool','v13 exact scope',lambda x:x['scope'].update(unrestricted_target=int(x['scope']['unrestricted_target']))),
              ('wrong_statement','v13 exact statement',lambda x:x.update(statement='Target nonexistence')),
              ('wrong_report_path','v13 exact report reference',lambda x:x.update(report='other.json')),
              ('wrong_report_hash','v13 exact report reference',lambda x:x.update(report_sha256='0'*64)),
              ('wrong_dependency','v13 exact dependencies',lambda x:x.update(dependencies=[dict(id='not-approved',revision=1,relation='premise')]))]
            for label,diag,change in mutations:
                bad=copy.deepcopy(b);change(bad);reject(cid+'_'+label,diag,lambda:m.v13_root_role(cid,BINDINGS[cid][1],bad))
            bad=copy.deepcopy(b);bad['verification_records']=[];reject(cid+'_legacy_record_collision','v13 legacy record namespace absent',lambda:m.v13_root_role(cid,BINDINGS[cid][1],bad))
            reject(cid+'_wrong_report_identity','v13 exact independent report',lambda:m.v13_root_report(cid,'0'*64,b,rs[cid]))
            for label,change in [('wrong_report_role',lambda x:x.update(verifier='/root/structural')),('wrong_report_target',lambda x:x.update(target_resolution=False))]:
                bad=copy.deepcopy(rs[cid]);change(bad);reject(cid+'_'+label,'v13 report roles and target scope',lambda:m.v13_root_report(cid,b['report_sha256'],b,bad))
        tests=[('rank85_false_optimum',RANK,'v13 exact conditional rank85 scope',lambda x:x.update(optimum_asserted=True)),
          ('rank85_truncated_rows',RANK,'v13 exact conditional rank85 scope',lambda x:x.update(complete_exact_coefficients_checked=1286)),
          ('rank85_wrong_bound',RANK,'v13 exact conditional rank85 scope',lambda x:x.update(exact_size_upper=[1,1])),
          ('rank85_wrong_image_counts',RANK,'v13 exact conditional rank85 scope',lambda x:x['lower_word_counts'].update({'6':24487})),
          ('census_missing_proposal',CENSUS,'v13 exact fixed census outcome',lambda x:x.update(complete_proposals_checked=239084)),
          ('census_bool_population',CENSUS,'v13 exact fixed census outcome',lambda x:x.update(frozen_labelled_proposals=True)),
          ('census_incomplete',CENSUS,'v13 exact fixed census outcome',lambda x:x.update(complete_universe=False)),
          ('census_no_absence',CENSUS,'v13 exact fixed census outcome',lambda x:x.update(absence_of_descent_asserted=False)),
          ('census_false_descent',CENSUS,'v13 exact fixed census outcome',lambda x:x['aggregate'].update(best_mu=3478)),
          ('census_overlap_summed',CENSUS,'v13 exact fixed census outcome',lambda x:x['aggregate'].update(unique_valid_neighbor_graphs=140694)),
          ('census_missing_tie',CENSUS,'v13 exact fixed census outcome',lambda x:x['aggregate'].update(best_proposal_ids=[68908])),
          ('census_false_SRG',CENSUS,'v13 exact fixed census outcome',lambda x:x['independently_checked_chosen_neighbor'].update(ordered_srg_identity_mismatches=0))]
        for label,cid,diag,change in tests:
            bad=copy.deepcopy(rs[cid]);change(bad);reject(label,diag,lambda:m.v13_root_report(cid,bs[cid]['report_sha256'],bs[cid],bad))
        bindingtests=[('rank85_known_target',RANK,'v13 exact conditional rank85 scope',lambda x:x.update(premise_state='VERIFIED')),
          ('rank85_upper_rank',RANK,'v13 exact conditional rank85 scope',lambda x:x.update(rank_upper_assumed=True)),
          ('rank85_bad_cal_reference',RANK,'v13 exact rank85 calibration reference',lambda x:x.update(pre_output_calibration_sha256='0'*64)),
          ('rank85_bad_source',RANK,'v13 exact rank85 source proof calibration pins',lambda x:x['inputs_sha256'].update({'acceleration/theory_20261003_incidence_low_weight_lp_v1.py':'0'*64})),
          ('rank85_numerics_accepted',RANK,'v13 exact rank85 recorded controls',lambda x:x['recorded_validation'].update(numerical_status_used_as_certificate=True)),
          ('census_false_target',CENSUS,'v13 exact fixed census outcome',lambda x:x.update(target_resolution=True)),
          ('census_bad_raw_graph',CENSUS,'v13 exact census source input calibration pins',lambda x:x['inputs_sha256'].update({'acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj':'0'*64})),
          ('census_lost_corrupt_control',CENSUS,'v13 exact census finite calibration',lambda x:x['pre_output_calibration']['strict_saved_stream_and_metadata_corruptions'].pop()),
          ('census_bad_overlap',CENSUS,'v13 exact census finite calibration',lambda x:x['pre_output_calibration'].update(known_overlap_checked=False)),
          ('census_wrong_frozen_start',CENSUS,'v13 exact finite census evidence',lambda x:x['computational_evidence'].update(labelled_triples=230)),
          ('census_missing_explicit_control',CENSUS,'v13 exact explicit census controls',lambda x:x['controls']['pre_output_independent'].update(strict_corruption_count=0)),
          ('census_false_trajectory',CENSUS,'v13 exact explicit census controls',lambda x:x['controls']['full_independent'].update(complete_trajectory_checked=True)),
          ('census_missing_supplement',CENSUS,'v13 exact supplemental record preservation',lambda x:x['supplemental_verification_records'].pop()),
          ('census_wrong_record_revision',CENSUS,'v13 exact supplemental record preservation',lambda x:x['supplemental_verification_records'][1].update(claim_revision=2)),
          ('census_wrong_record_artifact',CENSUS,'v13 exact supplemental record preservation',lambda x:x['supplemental_verification_records'][1]['artifact_hashes'].update({'acceleration/audit_20261003_two_line_records_v2.py':'0'*64})),
          ('census_invented_hardware',CENSUS,'v13 explicit unavailable information',lambda x:x['unavailable_information'][1].update(value='imagined CPU')),
          ('census_lost_unknown_reason',CENSUS,'v13 explicit unavailable information',lambda x:x['unavailable_information'][0].update(reason=''))]
        for label,cid,diag,change in bindingtests:
            bad=copy.deepcopy(bs[cid]);change(bad);reject(label,diag,lambda:m.v13_root_report(cid,bad['report_sha256'],bad,rs[cid]))
        need(m.v13_root_role('C-UNAPPROVED-ROOT',BINDINGS[RANK][1],bs[RANK])is False,'unapproved ID not admitted');m.v13_root_report('C-UNAPPROVED-ROOT','0'*64,{},{});controls.append(dict(case='unapproved_ROOT_ID_no_exception',outcome='PASS'))
        for cid,q in m.V12_ROOT_EXACT.items():
            path=BASE+('incidence_griesmer01/claim_binding.json'if cid.endswith('LOWER67')else 'weight60_warm_roots_dense01/summary.json')
            if cid.endswith('LOWER67'):oldb=read(path,q['binding'])
            else:oldb=read('acceleration/results/20261003_weight60_warm_root_census_binding01/claim_binding_schema2_draft.json',q['binding'])
            need(m.v12_root_role(cid,q['binding'],oldb)is True,'old exact V12 adapter preserved');controls.append(dict(case=cid+'_old_role',outcome='PASS'))
        need(pin('CLAIMS.yaml')==live and pin('.git/index')==index,'live ledger/index unchanged')
        report=dict(status='AUTHOR_REGISTRAR_V13_HELPER_CONTROLS_PASS_PENDING_INDEPENDENT_GATE',timestamp=datetime.now(timezone.utc).isoformat(),author='/root/checkpoint_audit',independent_approval=False,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,positive_controls=sum(c['outcome']=='PASS'for c in controls),strict_negative_controls=sum(c['outcome']=='REJECTED'for c in controls),controls=controls,full_V12_AST_preserved=True,registrar_main_called=False,mathematical_replays=0,ledger_mutations=0,index_mutations=0,scientific_invocations=0,target_resolution='NONE',limitations=['Same-author controls only; ROOT separate engineering gate required before use.','Hash/role/report metadata checks do not replay or independently approve mathematical/scientific evidence.','No registration, PUBLIC promotion or broad ROOT-verifier exception.'],elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],controls=len(controls),path=str(out/'summary.json'))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,completed_controls=controls,outputs_preserved=True,elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
