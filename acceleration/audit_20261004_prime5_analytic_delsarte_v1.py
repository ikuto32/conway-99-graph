"""SOURCE ONLY: analytic caller applicability around pinned Native certificate()."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261004_prime5_analytic_delsarte_v1.py'
SPEC = 'acceleration/audit_20261004_prime5_analytic_delsarte_v1_spec.md'
CORE = 'acceleration/audit_20261004_prime5_code_delsarte_v1.py'
CORE_SPEC = 'acceleration/audit_20261004_prime5_code_delsarte_v1_spec.md'
PRODUCER = 'acceleration/construct_20261004_prime5_analytic_delsarte_v1.py'
PRODUCER_SPEC = 'acceleration/construct_20261004_prime5_analytic_delsarte_v1_spec.md'
PINS = {
 CORE: '0333acd3790a7d9dee631a7c27fd1346e24f67e923d74bc54c824f099acc187f',
 CORE_SPEC: 'a3b39fceb90fd8595bc34dd50c5579fa6b205c7141e5a416f600537c0bfe4b87',
 PRODUCER: '42944723499b6016608d27c33e89e4e8784e542847010f066b1ec4397ca4e755',
 PRODUCER_SPEC: 'b3ddb4830d68c2d9f57cbebe1c9046a664d049fa1428c40d6d330bd06e354dd1',
 'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command_v2.py': '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17',
 'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'acceleration/results/20261004_independent_review/prime5_code_delsarte_calibration01/summary.json': '098fc604985244c42cfea8b8d9e40a1c98f21c8bfb7947a7f9a3b4543359dee0',
 'acceleration/results/20261004_prime5_code_delsarte_checker_calibration_root_acceptance01.json': 'c0c157a581f43e36b681f292bd4064db2584652b6e4f81bbc33284239e902c52',
}
PYTHON = 'C:/Users/ikuto/projects/conway-99-graph/build/research-venv/Scripts/python.exe'
UV = 'C:/Users/ikuto/.local/bin/uv.exe'
CAL_STATUS = 'INDEPENDENT_PRIME5_ANALYTIC_DELSARTE_V1_CALIBRATION_PASS'
FULL_STATUS = 'INDEPENDENT_PRIME5_ANALYTIC_DELSARTE_V1_COMPLETE_PASS'

class Veto(ValueError):
    pass

def need(ok, stage):
    if not ok:
        raise Veto(stage)

class Reader:
    def __init__(self, deadline, out):
        self.deadline, self.out, self.inputs = deadline, out, {}
    def tick(self):
        state = self.deadline.status()
        need(state['stop_required'] is False and state['remaining_seconds'] > 20, 'SAVE_GUARD')
    def raw(self, path, sha):
        self.tick()
        need(type(path) is str and type(sha) is str and re.fullmatch('[0-9a-f]{64}', sha), 'INPUT_REF')
        need('\\' not in path and ':' not in path and all(x not in ('','.','..') for x in path.split('/')), 'INPUT_PATH')
        actual = ROOT/path
        need(actual.resolve().is_relative_to(ROOT) and actual.is_file() and not actual.is_symlink()
             and all(not p.is_symlink() for p in actual.parents), 'INPUT_PATH')
        need(actual.stat().st_size <= 2*1024*1024, 'INPUT_SIZE')
        data = actual.read_bytes()
        need(hashlib.sha256(data).hexdigest() == sha, 'INPUT_SHA')
        need(path not in self.inputs or self.inputs[path] == sha, 'INPUT_CHANGED')
        self.inputs[path] = sha
        self.tick()
        return data
    def ref(self, ref):
        need(type(ref) is dict and ref.keys() == {'path','sha256'}, 'INPUT_REF')
        def unique(items):
            value = {}
            for k, v in items:
                need(k not in value, 'DUPLICATE_KEY')
                value[k] = v
            return value
        return json.loads(self.raw(ref['path'],ref['sha256']), object_pairs_hook=unique,
            parse_constant=lambda x: (_ for _ in ()).throw(Veto('JSON_NONFINITE')))
    def save(self, name, value):
        self.tick()
        need(type(name) is str and '/' not in name and '\\' not in name, 'OUTPUT_NAME')
        with (self.out/name).open('x',encoding='utf8',newline='\n') as stream:
            json.dump(value,stream,indent=2,allow_nan=False)
            stream.write('\n')
        self.tick()
    def close(self):
        for path, sha in list(self.inputs.items()):
            self.raw(path,sha)

def load_core(reader):
    for path, sha in PINS.items():
        reader.raw(path,sha)
    definition = importlib.util.spec_from_file_location('qualified_native_q5_certificate', ROOT/CORE)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    # Only this already-qualified Native checking module is loaded; its main guard
    # is false. No Structural producer, numerical backend or source AST is used.
    own = reader.ref({'path':list(PINS)[8],'sha256':PINS[list(PINS)[8]]})
    root = reader.ref({'path':list(PINS)[9],'sha256':PINS[list(PINS)[9]]})
    need(own.get('status') == module.CAL_STATUS and own.get('control_rows') == 68
         and own.get('positive') == 16 and own.get('negative') == 52
         and own.get('source') == {'path':CORE,'sha256':PINS[CORE]}, 'CORE_QUALIFICATION')
    need(root.get('result') == 'PASS_FINITE_CHECKER_ENGINEERING_ONLY'
         and root.get('reviewer') == '/root' and root.get('source') == own['source']
         and root.get('own_calibration') == {'path':list(PINS)[8],'sha256':PINS[list(PINS)[8]]}, 'CORE_ROOT_QUALIFICATION')
    reader.tick()
    return module

def header(summary, mode, core):
    status = 'PRIME5_ANALYTIC_DELSARTE_V1_AUTHOR_CONTROLS_PASS' if mode == 'calibrate' else 'CANDIDATE_PRIME5_ANALYTIC_DELSARTE_V1_COMPLETE'
    need(type(summary) is dict and summary.get('schema') == 'PRIME5_ANALYTIC_DELSARTE_RUN_V1'
         and type(summary.get('implementation_version')) is int and summary['implementation_version'] == 1
         and summary.get('mode') == mode and summary.get('status') == status
         and summary.get('producer') == '/root/structural', 'ANALYTIC_HEADER')
    need(core.equal(summary.get('source'), {'path':PRODUCER,'sha256':PINS[PRODUCER]})
         and core.equal(summary.get('specification'), {'path':PRODUCER_SPEC,'sha256':PINS[PRODUCER_SPEC]}), 'ANALYTIC_SOURCE')
    expected = {p:PINS[p] for p in (PRODUCER,PRODUCER_SPEC,'acceleration/command_deadline.py','acceleration/run_compute_command_v2.py','pyproject.toml','uv.lock')}
    need(core.equal(summary.get('inputs_sha256'),expected), 'ANALYTIC_INPUTS')
    need(summary.get('nonzero_code_forced') is False and summary.get('target_graph_read') is False
         and summary.get('target_resolution') == 'NONE' and type(summary.get('LP_calls')) is int
         and summary['LP_calls'] == 0 and summary.get('support_assumption_authenticated_inside_worker') is False, 'ANALYTIC_SCOPE')

def runtime(plan, manifest, terminal, summary, mode, core):
    schema = 'PRIME5_ANALYTIC_DELSARTE_SOURCE_ONLY_AUTHOR_PLAN_V1' if mode == 'calibrate' else 'ROOT_PRIME5_ANALYTIC_DELSARTE_CONCRETE_SCIENCE_PLAN_V1'
    need(type(plan) is dict and plan.get('schema') == schema, 'RUNTIME_PLAN')
    command, child, worker = (plan.get(k) for k in ('command','child_argv','worker_argv'))
    need(all(type(x) is list and all(type(w) is str and w for w in x) for x in (command,child,worker))
         and [len(command),len(child),len(worker)] == [36,20,12]
         and core.equal(command,plan.get('supervisor_argv')) and core.equal(command[16:],child)
         and core.equal(child[8:],worker), 'RUNTIME_PLAN')
    need(command[:8] == [PYTHON,'-B',str(ROOT/'acceleration/run_compute_command_v2.py').replace('\\','/'),
         '--seconds','180','--shutdown-reserve-seconds','20','--allocation-reason']
         and command[9] == '--success-criterion' and command[11] == '--verification-criterion'
         and command[13] == '--out' and command[15] == '--', 'RUNTIME_PREFIX')
    need(child[:8] == [UV,'run','--locked','--offline','--cache-dir',str(ROOT/'build/uv-cache').replace('\\','/'),
         '--python',PYTHON] and worker[:4] == [PYTHON,'-B',str(ROOT/PRODUCER).replace('\\','/'),mode], 'RUNTIME_SUFFIX')
    flags = core.options(worker[4:])
    need(flags.keys() == {'--seconds','--out','--self-sha256','--spec-sha256'}
         and flags['--seconds'] == '150' and flags['--self-sha256'] == PINS[PRODUCER]
         and flags['--spec-sha256'] == PINS[PRODUCER_SPEC], 'RUNTIME_SUFFIX')
    need(type(manifest) is dict and manifest.get('source_sha256') == PINS['acceleration/run_compute_command_v2.py']
         and manifest.get('runtime_scope') == 'LOCAL_WINDOWS_SUSPENDED_JOB_V1'
         and core.equal(manifest.get('command'),child) and manifest.get('seconds') == 180
         and manifest.get('shutdown_reserve_seconds') == 20, 'RUNTIME_MANIFEST')
    need(type(terminal) is dict and type(terminal.get('command_exit_code')) is int
         and terminal['command_exit_code'] == 0 and terminal.get('stop_reason') == 'COMMAND_EXITED'
         and terminal.get('error') is None and terminal.get('deadline_reached') is False
         and terminal.get('invocation_id') == manifest.get('invocation_id'), 'RUNTIME_EXIT')
    cleanup = terminal.get('cleanup')
    need(type(cleanup) is dict and all(cleanup.get(k) is True for k in ('created_suspended','resumed','reaped','job_active_zero_observed'))
         and cleanup.get('cleanup_errors') == [] and type(cleanup.get('actual_exit_code')) is int
         and cleanup['actual_exit_code'] == 0, 'RUNTIME_CLEANUP')
    need(core.finite(terminal.get('elapsed_seconds')) and 0 <= terminal['elapsed_seconds'] <= 180
         and type(summary.get('deadline')) is dict and core.finite(summary['deadline'].get('elapsed_seconds'))
         and 0 <= summary['deadline']['elapsed_seconds'] <= 150, 'RUNTIME_ELAPSED')
    return flags

def packet(raw, mode, reader, core):
    need(type(raw) is dict and raw.keys() == {'summary','plan','manifest','terminal'}, 'PACKET_REFS')
    summary, plan, manifest, terminal = (reader.ref(raw[k]) for k in ('summary','plan','manifest','terminal'))
    header(summary,mode,core)
    flags = runtime(plan,manifest,terminal,summary,mode,core)
    base = ROOT/Path(raw['summary']['path']).parent
    need(Path(flags['--out']).resolve() == base.resolve()
         and Path(plan['command'][14]).resolve() == (ROOT/Path(raw['manifest']['path']).parent).resolve()
         and Path(raw['terminal']['path']).parent == Path(raw['manifest']['path']).parent, 'RUNTIME_OUTPUT')
    names = core.inventory(base,summary.get('outputs_sha256'))
    expected = (['controls.json']+['fixture_'+str(i)+'.json' for i in range(4)]+['checkpoint_'+str(i)+'.json' for i in range(4)]) if mode == 'calibrate' else (
        ['certificate.json','construction.json','polynomial_values.json','construction_checkpoint.json']+['recurrence_checkpoint_'+str(i)+'.json' for i in range(10)])
    need(set(names) == set(expected) and type(summary.get('output_payload_count')) is int
         and summary['output_payload_count'] == len(expected) and type(summary.get('physical_file_count')) is int
         and summary['physical_file_count'] == len(expected)+1, 'ANALYTIC_POPULATION')
    outputs = {}
    for name in names:
        outputs[name] = reader.ref({'path':(base/name).relative_to(ROOT).as_posix(),'sha256':summary['outputs_sha256'][name]})
    return summary, outputs

def tiny_product(payload, core):
    need(type(payload) is dict and core.equal(payload,{'coefficients':[8,3,2]}), 'PRODUCT_COEFFICIENT')
    values = [sum(a*k for a,k in zip([8,3,2],core.coefficients(5,2,2,i))) for i in range(3)]
    need(values == [64,9,4], 'PRODUCT_VALUES')
    return {'coefficients':[8,3,2],'values':values}

def author_actions(outputs, reader, core):
    expected_names = ['product_n2','full_space_n2','wrong_product_constant','negative_multiplier']
    producer_stages = ['PASS','PASS','PRODUCT_COEFFICIENT','MULTIPLIER_SIGN']
    independent_stages = ['PASS','PASS','PRODUCT_COEFFICIENT','COEFFICIENT_SIGN']
    rows = outputs['controls.json']
    need(type(rows) is list and len(rows) == 4, 'AUTHOR_CONTROLS')
    comparisons = []
    for i in range(4):
        reader.tick()
        row, raw = rows[i], outputs['fixture_'+str(i)+'.json']
        need(core.equal(row,{'index':i,'name':expected_names[i],'expected':producer_stages[i],
             'actual':producer_stages[i],'passed':True}) and core.equal(outputs['checkpoint_'+str(i)+'.json'],
             {'completed_controls':i+1,'row':row}), 'AUTHOR_CONTROLS')
        need(type(raw) is dict and raw.keys() == {'fixture','result'}, 'AUTHOR_FIXTURE')
        try:
            if i in (0,2):
                result = tiny_product(raw['fixture'],core)
            else:
                need(core.equal(raw['fixture'],{'n':2,'distance':1,'multipliers':['1','1'] if i == 1 else ['-1','1']}), 'AUTHOR_FIXTURE')
                result = core.derive(5,2,1,2,{},raw['fixture']['multipliers'],reader)
            actual = 'PASS'
        except (Veto,core.Veto) as exc:
            actual, result = str(exc), None
        need(actual == independent_stages[i] and core.equal(result,raw['result']), 'AUTHOR_INDEPENDENT_STAGE')
        comparisons.append({'index':i,'producer_stage':producer_stages[i],'independent_stage':actual})
    return comparisons

def fixture_header():
    return {'schema':'PRIME5_ANALYTIC_DELSARTE_RUN_V1','implementation_version':1,'mode':'science',
        'status':'CANDIDATE_PRIME5_ANALYTIC_DELSARTE_V1_COMPLETE','producer':'/root/structural',
        'source':{'path':PRODUCER,'sha256':PINS[PRODUCER]},'specification':{'path':PRODUCER_SPEC,'sha256':PINS[PRODUCER_SPEC]},
        'inputs_sha256':{p:PINS[p] for p in (PRODUCER,PRODUCER_SPEC,'acceleration/command_deadline.py','acceleration/run_compute_command_v2.py','pyproject.toml','uv.lock')},
        'nonzero_code_forced':False,'target_graph_read':False,'target_resolution':'NONE','LP_calls':0,
        'support_assumption_authenticated_inside_worker':False}

def fixture_runtime():
    base = str(ROOT/'acceleration/results/analytic_fixture').replace('\\','/')
    worker = [PYTHON,'-B',str(ROOT/PRODUCER).replace('\\','/'),'science','--seconds','150',
        '--out',base,'--self-sha256',PINS[PRODUCER],'--spec-sha256',PINS[PRODUCER_SPEC]]
    child = [UV,'run','--locked','--offline','--cache-dir',str(ROOT/'build/uv-cache').replace('\\','/'),'--python',PYTHON]+worker
    command = [PYTHON,'-B',str(ROOT/'acceleration/run_compute_command_v2.py').replace('\\','/'),
        '--seconds','180','--shutdown-reserve-seconds','20','--allocation-reason','finite fixture',
        '--success-criterion','finite fixture','--verification-criterion','finite fixture','--out',base+'_supervision','--']+child
    plan = {'schema':'ROOT_PRIME5_ANALYTIC_DELSARTE_CONCRETE_SCIENCE_PLAN_V1',
        'command':command,'supervisor_argv':copy.deepcopy(command),'child_argv':child,'worker_argv':worker}
    manifest = {'source_sha256':PINS['acceleration/run_compute_command_v2.py'],
        'runtime_scope':'LOCAL_WINDOWS_SUSPENDED_JOB_V1','command':copy.deepcopy(child),
        'seconds':180.0,'shutdown_reserve_seconds':20.0,'invocation_id':'fixture'}
    terminal = {'command_exit_code':0,'stop_reason':'COMMAND_EXITED','error':None,'deadline_reached':False,
        'invocation_id':'fixture','elapsed_seconds':1.0,'cleanup':{'created_suspended':True,'resumed':True,
        'reaped':True,'job_active_zero_observed':True,'cleanup_errors':[],'actual_exit_code':0}}
    summary = fixture_header();summary['deadline'] = {'elapsed_seconds':0.5}
    return plan,manifest,terminal,summary

def calibration(reader, core):
    raw = fixture_header()
    tiny = core.derive(5,2,1,2,{},['1','1'],reader)
    def changed(field, value):
        result = copy.deepcopy(raw);result[field] = value;return result
    wrong_value = copy.deepcopy(tiny);wrong_value['polynomial_values'][-1]['value'] = '1'
    wrong_fraction = copy.deepcopy(tiny);wrong_fraction['multipliers'][0] = True
    runtime_fixture = fixture_runtime()
    bad_exit = copy.deepcopy(runtime_fixture);bad_exit[2]['command_exit_code'] = False
    bad_source = copy.deepcopy(runtime_fixture)
    bad_source[0]['worker_argv'][2] = str(ROOT/'acceleration/old_numeric.py').replace('\\','/')
    bad_source[0]['child_argv'][10] = bad_source[0]['worker_argv'][2]
    bad_source[0]['command'][26] = bad_source[0]['worker_argv'][2]
    bad_source[0]['supervisor_argv'][26] = bad_source[0]['worker_argv'][2]
    actions = [
      ('actual_analytic_header','PASS',lambda: header(raw,'science',core)),
      ('shared_tiny_certificate','PASS',lambda: core.certificate(tiny,[5,2,1,2,{}],reader)),
      ('tiny_product_coordinate_values','PASS',lambda: tiny_product({'coefficients':[8,3,2]},core)),
      ('boolean_implementation','ANALYTIC_HEADER',lambda: header(changed('implementation_version',True),'science',core)),
      ('old_numeric_schema','ANALYTIC_HEADER',lambda: header(changed('schema','PRIME5_CODE_DELSARTE_RUN_V2'),'science',core)),
      ('wrong_analytic_source','ANALYTIC_SOURCE',lambda: header(changed('source',{'path':PRODUCER,'sha256':'0'*64}),'science',core)),
      ('missing_input_pin','ANALYTIC_INPUTS',lambda: header(changed('inputs_sha256',{}),'science',core)),
      ('nonzero_overclaim','ANALYTIC_SCOPE',lambda: header(changed('nonzero_code_forced',True),'science',core)),
      ('bool_multiplier','FRACTION_TEXT',lambda: core.certificate(wrong_fraction,[5,2,1,2,{}],reader)),
      ('wrong_last_value','VALUE_TABLE',lambda: core.certificate(wrong_value,[5,2,1,2,{}],reader)),
      ('wrong_product_constant','PRODUCT_COEFFICIENT',lambda: tiny_product({'coefficients':[9,3,2]},core)),
      ('old_analytic_status','ANALYTIC_HEADER',lambda: header(changed('status','PRIME5_ANALYTIC_DELSARTE_V1_AUTHOR_CONTROLS_PASS'),'science',core)),
      ('actual_analytic_runtime_shape','PASS',lambda: runtime(*runtime_fixture,'science',core)),
      ('boolean_runtime_child_exit','RUNTIME_EXIT',lambda: runtime(*bad_exit,'science',core)),
      ('old_caller_runtime_source','RUNTIME_SUFFIX',lambda: runtime(*bad_source,'science',core)),
    ]
    rows = []
    for i,(name,expected,action) in enumerate(actions):
        reader.tick()
        try:
            result, actual = action(), 'PASS'
        except (Veto,core.Veto) as exc:
            result, actual = None, str(exc)
        row = {'index':i,'name':name,'expected':expected,'actual':actual,'result':result}
        reader.save('control_'+str(i)+'.json',row)
        rows.append(row)
        need(actual == expected,'CONTROL_STAGE')
    reader.save('controls.json',rows)
    return {'status':CAL_STATUS,'positive':4,'negative':11,'control_rows':15,'own68_actions_rerun':0}

def full(ref, reader, core):
    config = reader.ref(ref)
    need(type(config) is dict and config.keys() == {'schema','adapter_own','adapter_root','author','science','support'}
         and config['schema'] == 'INDEPENDENT_PRIME5_ANALYTIC_DELSARTE_PACKET_V1', 'CONFIGURATION')
    own, root = reader.ref(config['adapter_own']), reader.ref(config['adapter_root'])
    need(own.get('status') == CAL_STATUS and own.get('source') == {'path':SELF,'sha256':reader.inputs[SELF]}
         and own.get('specification') == {'path':SPEC,'sha256':reader.inputs[SPEC]}
         and own.get('control_rows') == 15 and own.get('positive') == 4 and own.get('negative') == 11, 'ADAPTER_QUALIFICATION')
    need(root.get('reviewer') == '/root' and root.get('result') == 'PASS_FINITE_ANALYTIC_ADAPTER_ENGINEERING_ONLY'
         and root.get('source') == own['source'] and root.get('specification') == own['specification']
         and core.equal(root.get('own_calibration'),config['adapter_own']), 'ADAPTER_ROOT_QUALIFICATION')
    author, author_outputs = packet(config['author'],'calibrate',reader,core)
    need(author.get('control_count') == 4 and author.get('positive_controls') == 2
         and author.get('negative_controls') == 2 and author.get('target_polynomial_constructed') is False, 'AUTHOR_POPULATION')
    stages = author_actions(author_outputs,reader,core)
    summary, outputs = packet(config['science'],'science',reader,core)
    checked = core.certificate(outputs['certificate.json'],[5,99,55,32,{}],reader)
    need(core.equal(outputs['polynomial_values.json'],checked['polynomial_values']), 'VALUE_FILE')
    need(core.equal(summary.get('outcome'),{'code_size_upper':checked['code_size_upper'],
         'integer_dimension_upper':checked['integer_dimension_upper'],
         'stronger_than_historical27':checked['integer_dimension_upper'] < 27})
         and summary.get('target_polynomial_constructed') is True, 'SCIENCE_OUTCOME')
    need(type(config['support']) is dict and config['support'].keys() == {'support_binding','support_report','support_acceptance'}, 'SUPPORT_REFS')
    for key, given in config['support'].items():
        need(core.equal(given,core.PREMISES[key]),'SUPPORT_REF')
        reader.ref(given)
    reader.save('independent_certificate.json',checked)
    reader.save('independent_polynomial_values.json',checked['polynomial_values'])
    reader.save('independent_author_stages.json',stages)
    return {'status':FULL_STATUS,'outcome':{'checked_multipliers':32,'checked_tail_weights':45,
        'checked_values':46,'code_size_upper':checked['code_size_upper'],
        'integer_dimension_upper':checked['integer_dimension_upper'],
        'stronger_than_historical27':checked['integer_dimension_upper'] < 27},
        'own68_actions_rerun':0,'adapter_own_actions_rerun':0,'producer_actions_replayed':4,
        'construction_trace_authenticated_only':True,'construction_trace_arithmetic_replayed':False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',choices=('calibrate','full'))
    for flag in ('seconds','out','self-sha256','spec-sha256'):
        parser.add_argument('--'+flag,required=True,type=float if flag == 'seconds' else str)
    parser.add_argument('--configuration');parser.add_argument('--configuration-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds,allocation_reason='One new analytic-source packet adapter; shared qualified coefficient folds, all reads/actions and seals share this deadline.')
    out = Path(args.out)
    reader = Reader(deadline,out)
    try:
        reader.tick()
        need(not out.exists() and out.resolve().is_relative_to(ROOT/'acceleration/results')
             and all(not p.is_symlink() for p in out.parents), 'OUTPUT_PATH')
        out.mkdir(parents=True)
        reader.raw(SELF,args.self_sha256);reader.raw(SPEC,args.spec_sha256)
        core = load_core(reader)
        result = calibration(reader,core) if args.mode == 'calibrate' else full(
            {'path':args.configuration,'sha256':args.configuration_sha256},reader,core)
        reader.close()
        outputs = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
        need(len(outputs) == (16 if args.mode == 'calibrate' else 3), 'OUTPUT_POPULATION')
        reader.tick()
        summary = {'schema':'INDEPENDENT_PRIME5_ANALYTIC_DELSARTE_RUN_V1','implementation_version':1,
            'mode':args.mode,'timestamp':datetime.now(timezone.utc).isoformat(),'producer':'/root/structural',
            'verifier':'/root/native_driver','method':'independent_artifact_check',
            'source':{'path':SELF,'sha256':args.self_sha256},'specification':{'path':SPEC,'sha256':args.spec_sha256},
            **result,'inputs_sha256':reader.inputs,'outputs_sha256':outputs,'output_payload_count':len(outputs),
            'physical_file_count':len(outputs)+1,'deadline':deadline.status(),'target_resolution':'NONE',
            'LP_calls':0,'qualified_shared_core':{'path':CORE,'sha256':PINS[CORE]},
            'limitations':['No producer functions/AST/backend used; Native qualified module declarations are shared explicitly.',
             'Actual adapter/runtime/population require a new applicable own qualification and clean supported terminal.',
             'Construction trace bytes are authenticated; its p/g/product arithmetic is covered only by separate written proof.',
             'No nonzero code, optimum, graph, target resolution or improvement beyond the exact reported bound inferred.']}
        reader.save('summary.json',summary)
        reader.close();reader.tick()
        print(json.dumps({'status':summary['status'],'summary':str(out/'summary.json')}))
        return 0
    except Exception as exc:
        if out.is_dir() and not (out/'failure.json').exists():
            with (out/'failure.json').open('x',encoding='utf8',newline='\n') as stream:
                json.dump({'status':'FAILED_OR_NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET','error_type':type(exc).__name__,
                    'error':str(exc),'deadline':deadline.status(),'provisional_summary_is_not_gate':(out/'summary.json').exists()},stream,indent=2,allow_nan=False)
                stream.write('\n')
        print(json.dumps({'error_type':type(exc).__name__,'error':str(exc)}),file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
