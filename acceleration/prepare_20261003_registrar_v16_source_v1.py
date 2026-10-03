"""Source editing only: add two frozen V16 adapters without invoking any registrar."""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'acceleration/register_20261003_bound_claims_v15.py'
NEW = ROOT / 'acceleration/register_20261003_bound_claims_v16.py'
PARENT_SHA = '0ab32f92cc61a4c5438a9a9a04ae8f22f99743632f5c0261cad3b1118b66ede9'
BINDINGS = [
 ('acceleration/results/20261003_weight5_c4_binding01/claim_binding_schema2.json',
  '6525dae3734dc6c2f7eabcbd12db994f8c283019176388bb0f540690859225ee'),
 ('acceleration/results/20261003_triangle_rank87_binding01/claim_binding_schema2.json',
  'dc079188f50e43ac31c9b9707e94a5f6db1fe9644c9b3dbccca4c9e02591a39d')]

ADAPTERS = r'''
# V16 admits only two frozen ROOT-verifier results. It does not derive mathematics,
# overwrite raw headlines, waive literal equality for unrelated IDs, or add any
# fixed-graph/GF3/profile binding. V15 and earlier adapters remain unchanged.
V16_EXACT = json.loads(r\'''__CONFIG__\''')


def v16_role(cid, expected, binding):
    if cid not in V16_EXACT:return False
    exact=V16_EXACT[cid]
    need(expected==exact['binding_sha256'],'v16 exact frozen binding identity')
    keys=['id','revision','claim_revision','status','review_state','producer','verifier','method','kind','basis']
    need(all(key in binding and v15_same(binding[key],exact['binding_metadata'][key]) for key in keys),
         'v16 exact typed revision status roles method kind basis')
    keys=['scope','assumptions','dependencies','target_resolution','premise_state']
    need(all(key in binding and v15_same(binding[key],exact['binding_metadata'][key]) for key in keys),
         'v16 exact scope assumptions dependencies and unresolved premise')
    need('verification_records' not in binding and binding['statement']==exact['statement']
         and binding['report']==exact['report'] and binding['report_sha256']==exact['report_sha256'],
         'v16 exact literal statement primary report and no legacy fallback')
    keys=['controls','written_audit','written_audit_sha256','exact_certificate',
          'original_independent_report_method','original_independent_report_statement_field']
    need(all(v15_same(binding.get(key),exact['binding_metadata'][key]) for key in keys),
         'v16 exact proof controls certificate and original method metadata')
    need(digest(ROOT/exact['binding_path'])==exact['binding_sha256'],
         'v16 original immutable binding bytes')
    original=json.loads((ROOT/exact['binding_path']).read_bytes())
    need(v15_same(binding,original),'v16 complete literal binding metadata')
    return True


def v16_dependency_order(cid, existing_ids):
    if cid=='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER87':
        need('C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT'
             in existing_ids,'v16 C4 dependency must precede rank87')


def v16_report(cid, report_sha, binding, report):
    if cid not in V16_EXACT:return None
    exact=V16_EXACT[cid]
    need(v16_role(cid,exact['binding_sha256'],binding),'v16 exact bound report routing')
    need(report_sha==exact['report_sha256'],'v16 exact primary report identity')
    keys=['status','producer','verifier','method','claim_revision','checker_implementation_version',
          'target_resolution','producer_outputs_checked']
    need(all(key in report and v15_same(report[key],exact['report_fields'][key]) for key in keys),
         'v16 exact typed independent report identity and method')
    field=exact['statement_field']
    need(report.get(field)==binding['statement']
         and (field=='statement' or 'statement' not in report),
         'v16 exact existing raw headline field')
    need(all(key in report and v15_same(report[key],value)
             for key,value in exact['report_fields'].items()),
         'v16 exact checked results and nonresolution limitations')
    for name,identity in exact['explicit_pins'].items():
        need(binding['inputs_sha256'].get(name)==identity and digest(ROOT/name)==identity,
             'v16 exact proof calibration certificate or prior binding pin')
    calibration=json.loads((ROOT/exact['calibration_path']).read_bytes())
    need(all(key in calibration and v15_same(calibration[key],value)
             for key,value in exact['calibration_fields'].items()),
         'v16 exact preoutput calibration scope')
    need(digest(ROOT/exact['report'])==exact['report_sha256'],
         'v16 original immutable report bytes')
    original=json.loads((ROOT/exact['report']).read_bytes())
    need(v15_same(report,original),'v16 complete literal report metadata')
    return dict(claim_id=cid,claim_revision=1,
        original_report=exact['report'],original_report_sha256=report_sha,
        original_report_statement_field=field,original_report_statement=report[field],
        recorded_binding=exact['binding_path'],recorded_binding_sha256=exact['binding_sha256'],
        recorded_binding_statement=binding['statement'],
        recorded_binding_statement_sha256=exact['statement_sha256'],
        original_independent_report_method=report['method'],schema_method=binding['method'],
        original_written_audit=binding['written_audit'],original_written_audit_sha256=binding['written_audit_sha256'],
        original_calibration=exact['calibration_path'],original_calibration_sha256=exact['calibration_sha256'],
        reason='Exact two-ID metadata projection preserves the existing literal raw headline and combined independent derivation/artifact method. The schema records independent_derivation and retains the original method here. Universal mathematics and exact certificates were already checked by ROOT; this registrar does not replay them or infer any wider result.',
        raw_statement_changed=False,mathematical_replays=0,target_resolution='NONE')

'''


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sha(OLD)!=PARENT_SHA:raise ValueError('exact unchanged V15 source')
    if NEW.exists():raise ValueError('fresh V16 path only')
    configs={}
    common_report=['status','producer','verifier','method','claim_revision','checker_implementation_version',
      'target_resolution','producer_outputs_checked','numerical_solver_invocations','graph_exclusions']
    c4_report=['actual_saved_strict_corruptions','complete_character_coefficients','complete_double_fibers',
      'complete_induced_c4s','complete_normalized_weights','complete_original_fixtures',
      'complete_small_image_coefficient_masks','complete_three_triangle_combinations',
      'paired_relabel_map_checked','positive_relabelled_fixtures','rank_asserted','separate_fixture_supports',
      'strict_interface_corruptions','target_character_rhs','target_induced_c4_count','target_unordered_paths',
      'target_weight5_lower_count','universal_derivation_checked','unordered_paths','written_audit','written_audit_sha256']
    rank_report=['complete_exact_coefficients_checked','complete_nonnegative_dual_coordinates_checked',
      'complete_exact_weight_inequalities_checked','exact_size_upper','maximum_linear_dimension',
      'conditional_incidence_rank_lower','exact_lhs_pairs','exact_endpoint_system','strict_corruptions',
      'complete_literal_characters','lower_word_counts','weight_domain','universal_conditional_derivation_checked',
      'optimum_asserted','rank_upper_asserted','nonzero_kernel_asserted']
    metadata=['id','revision','claim_revision','status','review_state','producer','verifier','method','kind','basis',
      'scope','assumptions','dependencies','target_resolution','premise_state','controls','written_audit',
      'written_audit_sha256','exact_certificate','original_independent_report_method','original_independent_report_statement_field']
    for index,(name,identity) in enumerate(BINDINGS):
        path=ROOT/name
        if sha(path)!=identity:raise ValueError('exact new binding identity '+name)
        binding=json.loads(path.read_bytes()); report_path=binding['report']; report=json.loads((ROOT/report_path).read_bytes())
        if sha(ROOT/report_path)!=binding['report_sha256']:raise ValueError('exact original report identity')
        calibration=binding['controls']['independent_preoutput']; calpath=calibration['path']; cal=json.loads((ROOT/calpath).read_bytes())
        if sha(ROOT/calpath)!=calibration['sha256']:raise ValueError('exact original calibration identity')
        explicit={binding['written_audit']:binding['written_audit_sha256'],calpath:calibration['sha256']}
        if index==0:
            proof='acceleration/audit_20261003_triangle_image_weight5_c4_v1_proof.md'
            explicit[proof]='7099b2780b3fe1b8abdbbdb9bff30b2993df6599cb39b3959655eb673ac4a90a'
            proof='acceleration/audit_20261003_triangle_image_weight5_v1_proof.md'
            explicit[proof]='8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee'
            calfields=['status','producer','verifier','method','checker_implementation_version','producer_outputs_checked',
                'complete_original_fixtures','complete_three_triangle_combinations','complete_small_image_coefficient_masks',
                'complete_character_coefficients','complete_normalized_weights','strict_interface_corruptions',
                'universal_derivation_checked','target_resolution']
        else:
            certificate=binding['exact_certificate']; explicit[certificate['path']]=certificate['sha256']
            explicit[BINDINGS[0][0]]=BINDINGS[0][1]
            calfields=['status','producer','verifier','method','checker_implementation_version','producer_outputs_checked',
                'complete_literal_characters','strict_corruptions','target_resolution']
        for pin,expected in explicit.items():
            if binding['inputs_sha256'].get(pin)!=expected or sha(ROOT/pin)!=expected:raise ValueError('exact existing proof pin '+pin)
        configs[binding['id']]=dict(binding_path=name,binding_sha256=identity,statement=binding['statement'],
            statement_sha256=hashlib.sha256(binding['statement'].encode('utf8')).hexdigest(),
            binding_metadata={key:binding.get(key) for key in metadata},
            report=report_path,report_sha256=binding['report_sha256'],
            statement_field='universal_statement' if index==0 else 'statement',
            report_fields={key:report[key] for key in common_report+(c4_report if index==0 else rank_report)},
            calibration_path=calpath,calibration_sha256=calibration['sha256'],
            calibration_fields={key:cal[key] for key in calfields},explicit_pins=explicit)
    addition=ADAPTERS.replace("r\\'''", "r'''").replace("\\''')", "''')").replace('__CONFIG__',json.dumps(configs,indent=2,ensure_ascii=True))
    source=OLD.read_text(encoding='utf8'); source=source.replace('\ndef main():',addition+'\ndef main():',1)
    anchor='        exact_v15 = v15_role(cid, expected, binding)\n'
    if source.count(anchor)!=1:raise ValueError('exact role insertion anchor')
    source=source.replace(anchor,anchor+'        exact_v16 = v16_role(cid, expected, binding)\n        v16_dependency_order(cid, {c[\'id\'] for c in data[\'claims\']})\n',1)
    anchor=' or exact_v13 or exact_v15),'
    if source.count(anchor)!=1:raise ValueError('exact role alternative anchor')
    source=source.replace(anchor,' or exact_v13 or exact_v15 or exact_v16),',1)
    anchor='            editorial_statement_mapping = wave40_statement_mapping\n'
    if source.count(anchor)!=1:raise ValueError('exact report dispatcher anchor')
    source=source.replace(anchor,anchor+"        wave41_statement_mapping = v16_report(cid, report_sha, binding, report)\n        if wave41_statement_mapping is not None:\n            need(editorial_statement_mapping is None, 'v16 disjoint exact metadata adapter')\n            editorial_statement_mapping = wave41_statement_mapping\n",1)
    with NEW.open('x',encoding='utf8',newline='\n') as stream:stream.write(source)
    print(json.dumps(dict(source_editing_only=True,registrar_main_called=False,old_sha256=PARENT_SHA,new_path=NEW.relative_to(ROOT).as_posix(),new_sha256=sha(NEW),exact_ids=list(configs))))


if __name__=='__main__':main()
