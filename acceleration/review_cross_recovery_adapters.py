"""Restricted cross-recovery derivation and pure semantic controls; no science."""
import argparse
import ast
from copy import deepcopy
import difflib
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import build_recovered_cross_checkpoint as b
import evaluate_recovered_cross_star as e

EXPECTED={
    'audit_cp_cross_recovery.py':'3a3e0c93d540982248254d87a3de753d8171be0081b6a7c82a4a7b89187721c8',
    'evaluate_recovered_cross_star.py':'771b0c4b9f9486c788fac3748cc2c6f602fd5dbfc03a78ef3687b8123b299b77',
    'build_recovered_cross_checkpoint.py':'08a52b9fc7900d86ab3ed0f861eee8f6a7fa27c31eb18bf1fb216c6c555b4574',
}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();b.require(not args.out.exists(),'Fresh QA output required')
    book=b.Index();sources={};controls=[]
    def source(name):
        path=b.ROOT/'acceleration'/name;book.bind(path,EXPECTED.get(name));sources[name]=path.read_text();return sources[name]
    audit_matching=source('audit_cp_matching_recovery.py')
    normal_matching=source('audit_cp_matching_search_v2.py').splitlines(True)
    normal_cross=source('audit_cp_cross_search.py').splitlines(True)
    expected=audit_matching;reused_changes=0
    for tag,a,z,c,d in difflib.SequenceMatcher(None,normal_matching,normal_cross,autojunk=False).get_opcodes():
        if tag=='equal':continue
        old,new=''.join(normal_matching[a:z]),''.join(normal_cross[c:d])
        if expected.count(old)==1:
            expected=expected.replace(old,new);reused_changes+=1
        else:
            b.require(old.startswith('"""Independent reusable') or old.startswith('    report = dict(status='),
                'Unexpected nontransferable normal cross diff')
    expected=expected.replace('"""Independently recover a CP audit','"""Independently recover a cross3/4 CP audit')
    expected=expected.replace('    report = dict(status="INDEPENDENT_CP_MATCHING_REPAIRED_LP_AUDIT_PASS", audited_producer_version=2, inputs_sha256=hashes,',
        '    report = dict(status="INDEPENDENT_CP_CROSS_REPAIRED_LP_AUDIT_PASS", audited_producer_version="cross1", inputs_sha256=hashes,\n'
        '                  cross_single_cycle_sizes=[3, 4], cross_family_count_by_cycle_size=dict(sorted(cross_size_counts.items())),\n'
        '                  complete_cross_perfect_matching_family_claimed=False,')
    cross_audit=source('audit_cp_cross_recovery.py')
    b.require(expected==cross_audit,'Cross recovery is not exactly the frozen cross diff plus explicit recovery header/report metadata')
    replacement={
        'audit_cp_matching_recovery.py':'audit_cp_cross_recovery.py',
        '73f9652fdaeb419a0d532effb3c82b94a56184db062864a72dbcbbc02f7e1f19':EXPECTED['audit_cp_cross_recovery.py'],
        'INDEPENDENT_CP_MATCHING_REPAIRED_LP_AUDIT_PASS':'INDEPENDENT_CP_CROSS_REPAIRED_LP_AUDIT_PASS',
    }
    evaluator_old=source('evaluate_recovered_cp_star.py');expected=evaluator_old
    for old,new in replacement.items():expected=expected.replace(old,new)
    evaluator_new=source('evaluate_recovered_cross_star.py')
    b.require(expected==evaluator_new,'Evaluator has changes beyond explicit recovery source/status replacements')
    builder_old=source('build_recovered_star_checkpoint.py');expected=builder_old
    replacements={**replacement,
        'Index an explicitly repaired CP LP view':'Index an explicitly repaired cross3/4 CP LP view',
        'evaluate_recovered_cp_star.py':'evaluate_recovered_cross_star.py',
        '229fad86005b0c59d7bc51e92ec90f1b4002453f8c58fc395fd549d957a5965c':EXPECTED['evaluate_recovered_cross_star.py'],
        'logs/03_search_audit.log':'logs/05_search_audit.log',
        'INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS':'INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS',
    }
    for old,new in replacements.items():expected=expected.replace(old,new)
    builder_new=source('build_recovered_cross_checkpoint.py')
    b.require(expected==builder_new,'Builder has changes beyond explicit source/status/family/log replacements')
    def functions(text):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    oldfunc,newfunc=functions(evaluator_old),functions(evaluator_new)
    identical_science=[n for n in oldfunc if oldfunc[n]==newfunc.get(n)]
    b.require(all(n in identical_science for n in ('main','complete_pair_evidence','checked_star_interval')),
        'Evaluator scientific workflow changed')
    directory=b.resolve(args.round)
    original,view,audit,repairs=b.inspect_recovery(book,directory,directory/'recovery')
    b.check_stopped_round(book.read(directory/'manifest.json'),book.read(directory/'failure.json'))
    selected=e.select_records(view,audit)
    b.require(len(original['records'])==64 and len(selected)==30,'Actual cross recovery inventory/selection differs')
    baseline=book.read(directory/'manifest.json')['baseline_star_audit_path']
    preflight=e.preflight(SimpleNamespace(run=directory/'recovery',baseline_star_audit=b.resolve(baseline),
        out=b.ROOT/'acceleration/results/__cross_recovery_QA_no_output__',max_candidates=32,seconds=30.,audit_seconds=60.))
    b.require(preflight['selected_candidates']==selected,'Pure selection/preflight differs')
    for p,h in preflight['inputs_sha256'].items():book.bind(p,h)
    def reject(name,call):
        try:call()
        except (ValueError,KeyError,TypeError) as error:controls.append(dict(name=name,rejected=True,error=str(error)))
        else:raise ValueError('Accepted invalid control: '+name)
    for name,change in (
        ('matching_recovery_status',lambda o,v,a,r:a.update(status='INDEPENDENT_CP_MATCHING_REPAIRED_LP_AUDIT_PASS')),
        ('nonrepaired_view_status',lambda o,v,a,r:v.update(status='BOUNDED_CP_MATCHING_SEARCH_FINISHED')),
        ('relaxed_tolerance',lambda o,v,a,r:a.update(independent_LP_audit_tolerance=1e-6)),
        ('original_overwritten',lambda o,v,a,r:r.update(original_files_overwritten=True)),
        ('missing_failed_history',lambda o,v,a,r:v.update(original_audit_failure_preserved=False)),
        ('missing_record',lambda o,v,a,r:v['records'].pop()),
        ('duplicate_record',lambda o,v,a,r:v['records'][1].update(proposal_index=v['records'][0]['proposal_index'])),
        ('candidate_hash_changed',lambda o,v,a,r:v['records'][0].update(candidate_sha256='0'*64)),
        ('nonLP_role_changed',lambda o,v,a,r:v['records'][0].update(selection_roles=['false'])),
        ('unlisted_result_changed',lambda o,v,a,r:v['records'][0].update(result_sha256='0'*64)),
        ('wrong_repair_set',lambda o,v,a,r:v['repaired_proposal_indices'].append(-1)),
        ('wrong_original_error',lambda o,v,a,r:r['records'][0].update(original_strict_audit_error='other')),
        ('wrong_solver_count',lambda o,v,a,r:r.update(solver_runs=2)),
        ('wrong_numeric_best',lambda o,v,a,r:v.update(best=None)),
        ('one_LP_relaxed',lambda o,v,a,r:a['probe_reports'][0]['phase1_audit'].update(numerical_tolerance=1e-6)),
    ):
        objects=deepcopy([original,view,audit,repairs]);change(*objects)
        reject(name,lambda d=objects:b.check_recovery_semantics(*d))
    for wrong in ('INDEPENDENT_CP_MATCHING_REPAIRED_LP_AUDIT_PASS','INDEPENDENT_CP_CROSS_SEARCH_AUDIT_PASS'):
        changed=deepcopy(audit);changed['status']=wrong
        reject('evaluator_rejects_'+wrong,lambda a=changed:e.select_records(view,a))
    # Execute only the exact family guard expressions extracted from the frozen
    # source, not its science or audit function. Thus wrong-family controls
    # exercise the real checks while avoiding expensive replay.
    def guard(message,namespace,text=cross_audit):
        nodes=[n.value for n in ast.walk(ast.parse(text)) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and
            isinstance(n.value.func,ast.Name) and n.value.func.id=='require' and len(n.value.args)>1 and
            isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==message]
        b.require(len(nodes)==1,'Unique family guard absent')
        return eval(compile(ast.Expression(nodes[0]),'<frozen family guard>','eval'),{'require':b.require},namespace)
    family=book.read(view['paths']['family_audit'])
    guard('Wrong or incomplete cross extraction proof',dict(family=family))
    for name,change in (
        ('matching_family_proof',lambda f:f.update(status='INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS')),
        ('unchecked_original_final',lambda f:f.update(all_original_native_indices_and_final_graphs_checked=False)),
        ('unchecked_cycle_canonicality',lambda f:f.update(all_cycles_min_vertex_removed_first_checked=False)),
        ('family_imported_producer',lambda f:f.update(producer_imported=True)),
    ):
        changed=deepcopy(family);change(changed)
        reject(name,lambda f=changed:guard('Wrong or incomplete cross extraction proof',dict(family=f)))
    native=book.read(view['paths']['native'])
    guard('Wrong native family scope',dict(native=native))
    for name,change in (
        ('whole_matching_native_scope',lambda n:n.update(status='COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION')),
        ('wrong_cycle_scope',lambda n:n.update(cycle_sizes=[3,4,5])),
    ):
        changed=deepcopy(native);change(changed)
        reject(name,lambda n=changed:guard('Wrong native family scope',dict(native=n)))
    book.bind(Path(__file__))
    report=dict(status='CROSS_RECOVERY_RESTRICTED_ADAPTATION_AND_SEMANTIC_CONTROLS_PASS',inputs_sha256=book.verified,
        restricted_source_derivations_verified=True,transferred_frozen_cross_diff_segments=reused_changes,
        unchanged_evaluator_functions=identical_science,original_records=64,selected_nearzero=30,
        selected_indices=[r['proposal_index'] for r in selected],repaired_indices=view['repaired_proposal_indices'],
        negative_controls=len(controls),controls=controls,semantic_controls_bypass_hash_guards=True,
        scientific_reruns=0,LP_runs=0,domain_enumerations=0,subprocess_invocations=0,output_created=True)
    with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=report['status'],negative_controls=len(controls),selected=len(selected))))


if __name__=='__main__':main()
