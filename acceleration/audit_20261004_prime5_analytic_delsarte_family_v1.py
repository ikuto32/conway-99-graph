"""SOURCE ONLY: distinct complete V2 analytic-family applicability and arithmetic."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261004_prime5_analytic_delsarte_family_v1.py'
SPEC = 'acceleration/audit_20261004_prime5_analytic_delsarte_family_v1_spec.md'
CORE = 'acceleration/audit_20261004_prime5_code_delsarte_v1.py'
CORE_SPEC = 'acceleration/audit_20261004_prime5_code_delsarte_v1_spec.md'
PRODUCER = 'acceleration/construct_20261004_prime5_analytic_delsarte_v2.py'
PRODUCER_SPEC = 'acceleration/construct_20261004_prime5_analytic_delsarte_v2_spec.md'
PINS = {
 CORE:'0333acd3790a7d9dee631a7c27fd1346e24f67e923d74bc54c824f099acc187f',
 CORE_SPEC:'a3b39fceb90fd8595bc34dd50c5579fa6b205c7141e5a416f600537c0bfe4b87',
 PRODUCER:'a4294996414f86337e1726628d337319a0f3c3b85b9afd6f37713a09cb91b624',
 PRODUCER_SPEC:'cae1a819d0b603f1243393cab0a4f86401a943d6b19fa1c7527aeea114d3b4f4',
 'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command_v2.py':'46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'acceleration/results/20261004_independent_review/prime5_code_delsarte_calibration01/summary.json':'098fc604985244c42cfea8b8d9e40a1c98f21c8bfb7947a7f9a3b4543359dee0',
 'acceleration/results/20261004_prime5_code_delsarte_checker_calibration_root_acceptance01.json':'c0c157a581f43e36b681f292bd4064db2584652b6e4f81bbc33284239e902c52',
 'acceleration/audit_20261004_prime5_analytic_delsarte_v1.py':'3d43158c8e564fb6b645a17dfaf3cdac84d7f8f16c6ac51c95f2b1e00dddee84',
 'acceleration/audit_20261004_prime5_analytic_delsarte_v1_spec.md':'f46453b25f4cb7971b9c8cb7ac413013284a2dc465ede836c1dad5add21a132e',
 'acceleration/results/20261004_independent_review/prime5_analytic_delsarte_calibration01/summary.json':'0fa8a74edfe31a1979a464d05034b37760097626c3762abd4784daba72a1087d',
 'acceleration/results/20261004_prime5_analytic_delsarte_adapter_root_acceptance01.json':'06000964ef34c1b704d43f79f90658d50911663baeb4ccf062346ec11141207a',
}
PYTHON = 'C:/Users/ikuto/projects/conway-99-graph/build/research-venv/Scripts/python.exe'
UV = 'C:/Users/ikuto/.local/bin/uv.exe'
LOWER = {'3':924,'4':8316,'5':24948,'6':391776}
RENORM_REFS = {
 'renorm_binding':{'path':'acceleration/results/20261004_independent_review/code_delsarte_image_lower_count_renormalization_native01/claim_binding_schema2.json','sha256':'a11104e4e9a3f4e3a511a563b949e5689b06bf94b22ca5bb6776b110ef3a241c'},
 'renorm_report':{'path':'acceleration/results/20261004_independent_review/code_delsarte_image_lower_count_renormalization_native01/summary.json','sha256':'da90958c41bdc88e69c53f12f04663888f571888fe31536d74022b383c6b8b61'},
 'renorm_acceptance':{'path':'acceleration/results/20261004_code_delsarte_image_count_renormalization_root_written_acceptance01.json','sha256':'ae4bb06d688e722d555003e849631f7a4dec32daaf4323b84450836639293389'},
}
CAL_STATUS = 'INDEPENDENT_PRIME5_ANALYTIC_FAMILY_V1_CALIBRATION_PASS'
FULL_STATUS = 'INDEPENDENT_PRIME5_ANALYTIC_FAMILY_V1_COMPLETE_PASS'
OBJECTIVE = 'Lowest exact rational size upper; equal objectives retain first frozen case index.'

class Veto(ValueError):
    pass

def need(ok, stage):
    if not ok:
        raise Veto(stage)

# Literal checking reader from qualified Native3d431; producer code is not loaded.
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
    definition = importlib.util.spec_from_file_location('qualified_native_q5_family_math', ROOT/CORE)
    core = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(core)
    own = reader.ref({'path':list(PINS)[8],'sha256':PINS[list(PINS)[8]]})
    root = reader.ref({'path':list(PINS)[9],'sha256':PINS[list(PINS)[9]]})
    need(own.get('status') == core.CAL_STATUS and own.get('control_rows') == 68
         and own.get('source') == {'path':CORE,'sha256':PINS[CORE]}
         and root.get('reviewer') == '/root' and root.get('result') == 'PASS_FINITE_CHECKER_ENGINEERING_ONLY'
         and root.get('own_calibration') == {'path':list(PINS)[8],'sha256':PINS[list(PINS)[8]]}, 'CORE_QUALIFICATION')
    reader.tick()
    return core

def header(raw, mode, core):
    status = 'PRIME5_ANALYTIC_DELSARTE_V2_AUTHOR_CONTROLS_PASS' if mode == 'calibrate' else 'CANDIDATE_PRIME5_ANALYTIC_DELSARTE_V2_FAMILY_COMPLETE'
    need(type(raw) is dict and raw.get('schema') == 'PRIME5_ANALYTIC_DELSARTE_RUN_V2'
         and type(raw.get('implementation_version')) is int and raw['implementation_version'] == 2
         and raw.get('mode') == mode and raw.get('status') == status and raw.get('producer') == '/root/structural', 'FAMILY_HEADER')
    need(core.equal(raw.get('source'),{'path':PRODUCER,'sha256':PINS[PRODUCER]})
         and core.equal(raw.get('specification'),{'path':PRODUCER_SPEC,'sha256':PINS[PRODUCER_SPEC]}), 'FAMILY_SOURCE')
    software = {p:PINS[p] for p in (PRODUCER,PRODUCER_SPEC,'acceleration/command_deadline.py','acceleration/run_compute_command_v2.py','pyproject.toml','uv.lock')}
    need(core.equal(raw.get('inputs_sha256'),software), 'FAMILY_INPUTS')
    need(raw.get('nonzero_code_forced') is False and raw.get('target_graph_read') is False
         and raw.get('target_resolution') == 'NONE' and type(raw.get('LP_calls')) is int and raw['LP_calls'] == 0
         and raw.get('support_assumption_authenticated_inside_worker') is False, 'FAMILY_SCOPE')

def runtime(plan, manifest, terminal, summary, mode, core):
    outer, worker_seconds = (180,150) if mode == 'calibrate' else (600,550)
    schema = 'PRIME5_ANALYTIC_DELSARTE_SOURCE_ONLY_AUTHOR_PLAN_V2' if mode == 'calibrate' else 'ROOT_PRIME5_ANALYTIC_DELSARTE_CONCRETE_FAMILY_PLAN_V2'
    need(type(plan) is dict and plan.get('schema') == schema, 'RUNTIME_PLAN')
    command, child, worker = (plan.get(k) for k in ('command','child_argv','worker_argv'))
    need(all(type(x) is list and all(type(w) is str and w for w in x) for x in (command,child,worker))
         and [len(command),len(child),len(worker)] == [36,20,12]
         and core.equal(command,plan.get('supervisor_argv')) and core.equal(command[16:],child)
         and core.equal(child[8:],worker), 'RUNTIME_PLAN')
    need(command[:8] == [PYTHON,'-B',(ROOT/'acceleration/run_compute_command_v2.py').as_posix(),
         '--seconds',str(outer),'--shutdown-reserve-seconds','20','--allocation-reason']
         and command[9] == '--success-criterion' and command[11] == '--verification-criterion'
         and command[13] == '--out' and command[15] == '--', 'RUNTIME_PREFIX')
    need(child[:8] == [UV,'run','--locked','--offline','--cache-dir',(ROOT/'build/uv-cache').as_posix(),'--python',PYTHON]
         and worker[:4] == [PYTHON,'-B',(ROOT/PRODUCER).as_posix(),mode], 'RUNTIME_SUFFIX')
    flags = core.options(worker[4:])
    need(flags.keys() == {'--seconds','--out','--self-sha256','--spec-sha256'}
         and flags['--seconds'] == str(worker_seconds) and flags['--self-sha256'] == PINS[PRODUCER]
         and flags['--spec-sha256'] == PINS[PRODUCER_SPEC], 'RUNTIME_SUFFIX')
    need(type(manifest) is dict and manifest.get('source_sha256') == PINS['acceleration/run_compute_command_v2.py']
         and manifest.get('runtime_scope') == 'LOCAL_WINDOWS_SUSPENDED_JOB_V1'
         and core.equal(manifest.get('command'),child) and manifest.get('seconds') == outer
         and manifest.get('shutdown_reserve_seconds') == 20, 'RUNTIME_MANIFEST')
    need(type(terminal) is dict and type(terminal.get('command_exit_code')) is int and terminal['command_exit_code'] == 0
         and terminal.get('stop_reason') == 'COMMAND_EXITED' and terminal.get('error') is None
         and terminal.get('deadline_reached') is False and terminal.get('invocation_id') == manifest.get('invocation_id'), 'RUNTIME_EXIT')
    cleanup = terminal.get('cleanup')
    need(type(cleanup) is dict and all(cleanup.get(k) is True for k in ('created_suspended','resumed','reaped','job_active_zero_observed'))
         and cleanup.get('cleanup_errors') == [] and type(cleanup.get('actual_exit_code')) is int
         and cleanup['actual_exit_code'] == 0, 'RUNTIME_CLEANUP')
    need(core.finite(terminal.get('elapsed_seconds')) and 0 <= terminal['elapsed_seconds'] <= outer
         and type(summary.get('deadline')) is dict and core.finite(summary['deadline'].get('elapsed_seconds'))
         and 0 <= summary['deadline']['elapsed_seconds'] <= worker_seconds, 'RUNTIME_ELAPSED')
    return flags

def packet(refs, mode, reader, core):
    need(type(refs) is dict and refs.keys() == {'summary','plan','manifest','terminal'}, 'PACKET_REFS')
    raw, plan, manifest, terminal = (reader.ref(refs[k]) for k in ('summary','plan','manifest','terminal'))
    header(raw,mode,core)
    flags = runtime(plan,manifest,terminal,raw,mode,core)
    base = ROOT/Path(refs['summary']['path']).parent
    need(Path(flags['--out']).resolve() == base.resolve() and Path(plan['command'][14]).resolve() ==
         (ROOT/Path(refs['manifest']['path']).parent).resolve() and Path(refs['manifest']['path']).parent == Path(refs['terminal']['path']).parent, 'RUNTIME_OUTPUT')
    names = core.inventory(base,raw.get('outputs_sha256'))
    expected = (['controls.json']+['fixture_'+str(i)+'.json' for i in range(4)]+['checkpoint_'+str(i)+'.json' for i in range(4)]) if mode == 'calibrate' else [
        'case_'+str(i).zfill(4)+suffix+'.json' for i in range(384) for suffix in ('','_checkpoint')]
    need(set(names) == set(expected) and type(raw.get('output_payload_count')) is int and raw['output_payload_count'] == len(expected)
         and type(raw.get('physical_file_count')) is int and raw['physical_file_count'] == len(expected)+1, 'FAMILY_POPULATION')
    return raw, {name:reader.ref({'path':(base/name).relative_to(ROOT).as_posix(),'sha256':raw['outputs_sha256'][name]}) for name in names}

def prefix(raw, n, t, s, reader, core):
    need(type(raw.get('p_coefficients')) is list and 2 <= len(raw['p_coefficients']) <= t+1, 'TRACE_P_SHAPE')
    p = [core.canonical(x) for x in raw['p_coefficients']]
    need(p[0] == 1, 'TRACE_P_ZERO')
    for j in range(1,len(p)):
        reader.tick()
        previous = 0 if j == 1 else p[j-2]
        need(4*(n-j+1)*p[j] == (s-3*(j-1))*p[j-1]-(j-1)*previous, 'TRACE_RECURRENCE')
    if raw['status'] == 'REJECTED_CONSTRUCTION' and raw['first_veto'] == 'RECURRENCE_SIGN':
        need(all(x > 0 for x in p[:-1]) and p[-1] <= 0, 'TRACE_SIGN')
        need(type(raw['failed_p_index']) is int and raw['failed_p_index'] == len(p)-1
             and raw['g_coefficients'] is None and core.canonical(raw['failed_value']) == p[-1], 'TRACE_FAILED_VALUE')
        return p, None
    need(len(p) == t+1 and all(x > 0 for x in p), 'TRACE_SIGN')
    need(type(raw.get('g_coefficients')) is list and len(raw['g_coefficients']) == t+2, 'TRACE_G_SHAPE')
    given_g = [core.canonical(x) for x in raw['g_coefficients']]
    g = [Fraction(0)]*(t+2)
    # Accumulate each column of the multiplication-by-K1 operator, rather than
    # invoke Structural's g builder or product coefficient formula.
    for j, value in enumerate(p):
        reader.tick()
        g[j] += (3*j-s)*value
        g[j+1] += (j+1)*value
        if j:
            g[j-1] += 4*(n+1-j)*value
    need(given_g == g and all(x == 0 for x in g[:t]) and g[t+1] == (t+1)*p[t], 'TRACE_G')
    if raw['status'] == 'REJECTED_CONSTRUCTION':
        need(raw['first_veto'] == 'TRUNCATED_SIGN' and g[t] <= 0, 'TRACE_SIGN')
        need(type(raw['failed_g_index']) is int and raw['failed_g_index'] == t
             and core.canonical(raw['failed_value']) == g[t], 'TRACE_FAILED_VALUE')
    else:
        need(raw['status'] == 'CANDIDATE_CERTIFICATES' and raw['first_veto'] is None and g[t] > 0, 'TRACE_SIGN')
    return p, g

def rescaling(base_raw, low_raw, denominator_text, n, d, h, lower, reader, core):
    base = core.certificate(base_raw,[5,n,d,h,{}],reader)
    ys = [core.canonical(x) for x in base['multipliers']]
    denominator = 1+sum(y*lower.get(str(j),0) for j,y in enumerate(ys,1))
    need(core.canonical(denominator_text) == denominator and denominator >= 1, 'RESCALING_DENOMINATOR')
    need(type(low_raw) is dict and core.equal(low_raw.get('multipliers'),[str(y/denominator) for y in ys]), 'RESCALING_MULTIPLIERS')
    low = core.certificate(low_raw,[5,n,d,h,lower],reader)
    need(core.equal(low['polynomial_values'],[{'weight':r['weight'],'value':str(core.canonical(r['value'])/denominator)}
         for r in base['polynomial_values']]) and core.canonical(low['code_size_upper']) == core.canonical(base['code_size_upper'])/denominator, 'RESCALING_VALUES')
    return base, low

def validate_case(raw, index, t, s_text, reader, core, n=99, d=55, h=32, lower=None):
    lower = LOWER if lower is None else lower
    need(type(raw) is dict and core.equal([raw.get(k) for k in ('case_index','q','n','minimum_distance','t','s')],
         [index,5,n,d,t,s_text]), 'FAMILY_LABEL')
    common = {'case_index','q','n','minimum_distance','s','t','status','first_veto','p_coefficients','g_coefficients'}
    if raw.get('status') == 'REJECTED_CONSTRUCTION':
        extra = {'failed_p_index','failed_value'} if raw.get('first_veto') == 'RECURRENCE_SIGN' else {'failed_g_index','failed_value'}
    else:
        extra = {'f_coefficients','constant_coefficient','baseline','low_image_counts','renormalization_denominator'}
    need(raw.keys() == common|extra, 'FAMILY_FIELDS')
    s = core.canonical(s_text)
    p, g = prefix(raw,n,t,s,reader,core)
    if raw['status'] == 'REJECTED_CONSTRUCTION':
        return {'index':index,'t':t,'s':s_text,'status':raw['status'],'first_veto':raw['first_veto']}, None
    need(2*t+1 <= min(h,n) and type(raw['f_coefficients']) is list and len(raw['f_coefficients']) == 2*t+2, 'F_COEFFICIENT_SHAPE')
    f = [core.canonical(x) for x in raw['f_coefficients']]
    need(all(x >= 0 for x in f) and f[-1] > 0, 'F_COEFFICIENT_SIGN')
    constant = core.canonical(raw['constant_coefficient'])
    need(constant > 0 and f[0] == constant == g[t]*p[t]*4**t*math.comb(n,t), 'CONSTANT_COEFFICIENT')
    # The exact product identity is checked at degree+1 distinct weights. Since
    # both polynomials have degree <=2t+1, this determines the full polynomial.
    for weight in range(2*t+2):
        reader.tick()
        k = core.coefficients(5,n,2*t+1,weight,reader)
        pv = sum(value*k[j] for j,value in enumerate(p))
        need(sum(value*k[j] for j,value in enumerate(f)) == (4*n-5*weight-s)*pv*pv, 'FACTORIZATION')
    base, low = rescaling(raw['baseline'],raw['low_image_counts'],raw['renormalization_denominator'],n,d,h,lower,reader,core)
    expected_ys = [str(f[j]/constant) if j < len(f) else '0' for j in range(1,h+1)]
    need(core.equal(base['multipliers'],expected_ys), 'NORMALIZED_COEFFICIENTS')
    return {'index':index,'t':t,'s':s_text,'status':raw['status'],'first_veto':None,
        'baseline_size':base['code_size_upper'],'baseline_dimension':base['integer_dimension_upper'],
        'low_size':low['code_size_upper'],'low_dimension':low['integer_dimension_upper']}, {'baseline':base,'low_image_counts':low}

def universe():
    texts = [str(s) for s in range(121,161)]+['243/2','485/4','969/8','1937/16','3873/32','7745/64','15489/128','30977/256']
    return [(t,s) for t in range(8,16) for s in texts]

def update_best(best, index, t, s, certificates, core):
    need(type(index) is int and index >= 0, 'BEST_INDEX')
    for branch in ('baseline','low_image_counts'):
        cert = certificates[branch]
        if best[branch] is None or core.canonical(cert['code_size_upper']) < core.canonical(best[branch]['code_size_upper']):
            best[branch] = {'case_index':index,'t':t,'s':s,'code_size_upper':cert['code_size_upper'],
                'integer_dimension_upper':cert['integer_dimension_upper'],'dimension_lower_power':cert['dimension_lower_power'],
                'dimension_next_power':cert['dimension_next_power'],'stronger_than_historical27':cert['integer_dimension_upper'] < 27}

def checkpoint(raw, completed, valid, rejected, counts, best, core):
    need(core.equal(raw,{'completed_cases':completed,'valid_cases':valid,'rejected_cases':rejected,
         'first_veto_counts':counts,'best':best}), 'FAMILY_CHECKPOINT')

def family_summary(raw, valid, rejected, counts, best, core):
    expected = {'selected_cases':384,'completed_cases':384,'valid_cases':valid,'rejected_cases':rejected,
        'first_veto_counts':counts,'best':best,'objective':OBJECTIVE,'target_polynomial_constructed':valid > 0,
        'separate_exact_checker_required':True,'image_counts_authenticated_inside_worker':False,
        'progress':{'completed_cases':384,'active_case':None}}
    need(core.equal({k:raw.get(k) for k in expected},expected), 'FAMILY_SUMMARY')

def author_actions(outputs, reader, core):
    names = ['product_n2','full_space_n2','wrong_product_constant','negative_multiplier']
    expected = ['PASS','PASS','PRODUCT_COEFFICIENT','MULTIPLIER_SIGN']
    stages = ['PASS','PASS','PRODUCT_COEFFICIENT','COEFFICIENT_SIGN']
    rows, comparisons = outputs['controls.json'], []
    need(type(rows) is list and len(rows) == 4, 'AUTHOR_CONTROLS')
    for i in range(4):
        reader.tick()
        row, raw = rows[i], outputs['fixture_'+str(i)+'.json']
        need(core.equal(row,{'index':i,'name':names[i],'expected':expected[i],'actual':expected[i],'passed':True})
             and core.equal(outputs['checkpoint_'+str(i)+'.json'],{'completed_controls':i+1,'row':row}), 'AUTHOR_CONTROLS')
        need(type(raw) is dict and raw.keys() == {'fixture','result'}, 'AUTHOR_FIXTURE')
        try:
            if i in (0,2):
                need(core.equal(raw['fixture'],{'coefficients':[8,3,2]}), 'PRODUCT_COEFFICIENT')
                result = {'coefficients':[8,3,2],'values':[sum(a*k for a,k in zip([8,3,2],core.coefficients(5,2,2,w))) for w in range(3)]}
            elif i == 1:
                need(core.equal(raw['fixture'],{'n':2,'distance':1,'multipliers':['1','1'],'lower_counts':{'1':8,'2':16}}), 'AUTHOR_FIXTURE')
                base = core.derive(5,2,1,2,{},['1','1'],reader)
                low = core.derive(5,2,1,2,{'1':8,'2':16},['1/25','1/25'],reader)
                rescaling(base,low,'25',2,1,2,{'1':8,'2':16},reader,core)
                result = {'baseline':base,'renormalized':{'denominator':'25','certificate':low}}
            else:
                need(core.equal(raw['fixture'],{'n':2,'distance':1,'multipliers':['-1','1']}), 'AUTHOR_FIXTURE')
                result = core.derive(5,2,1,2,{},['-1','1'],reader)
            actual = 'PASS'
        except (Veto,core.Veto) as exc:
            actual, result = str(exc), None
        need(actual == stages[i] and core.equal(result,raw['result']), 'AUTHOR_INDEPENDENT_STAGE')
        comparisons.append({'index':i,'producer_stage':expected[i],'independent_stage':actual})
    return comparisons

def fixture_header():
    return {'schema':'PRIME5_ANALYTIC_DELSARTE_RUN_V2','implementation_version':2,'mode':'science',
        'status':'CANDIDATE_PRIME5_ANALYTIC_DELSARTE_V2_FAMILY_COMPLETE','producer':'/root/structural',
        'source':{'path':PRODUCER,'sha256':PINS[PRODUCER]},'specification':{'path':PRODUCER_SPEC,'sha256':PINS[PRODUCER_SPEC]},
        'inputs_sha256':{p:PINS[p] for p in (PRODUCER,PRODUCER_SPEC,'acceleration/command_deadline.py','acceleration/run_compute_command_v2.py','pyproject.toml','uv.lock')},
        'nonzero_code_forced':False,'target_graph_read':False,'target_resolution':'NONE','LP_calls':0,
        'support_assumption_authenticated_inside_worker':False}

def fixture_runtime():
    base = (ROOT/'acceleration/results/family_fixture').as_posix()
    worker = [PYTHON,'-B',(ROOT/PRODUCER).as_posix(),'science','--seconds','550','--out',base,'--self-sha256',PINS[PRODUCER],'--spec-sha256',PINS[PRODUCER_SPEC]]
    child = [UV,'run','--locked','--offline','--cache-dir',(ROOT/'build/uv-cache').as_posix(),'--python',PYTHON]+worker
    command = [PYTHON,'-B',(ROOT/'acceleration/run_compute_command_v2.py').as_posix(),'--seconds','600','--shutdown-reserve-seconds','20',
        '--allocation-reason','fixture','--success-criterion','fixture','--verification-criterion','fixture','--out',base+'_supervision','--']+child
    plan = {'schema':'ROOT_PRIME5_ANALYTIC_DELSARTE_CONCRETE_FAMILY_PLAN_V2','command':command,'supervisor_argv':copy.deepcopy(command),'child_argv':child,'worker_argv':worker}
    manifest = {'source_sha256':PINS['acceleration/run_compute_command_v2.py'],'runtime_scope':'LOCAL_WINDOWS_SUSPENDED_JOB_V1',
        'command':copy.deepcopy(child),'seconds':600,'shutdown_reserve_seconds':20,'invocation_id':'fixture'}
    terminal = {'command_exit_code':0,'stop_reason':'COMMAND_EXITED','error':None,'deadline_reached':False,'invocation_id':'fixture','elapsed_seconds':1.0,
        'cleanup':{'created_suspended':True,'resumed':True,'reaped':True,'job_active_zero_observed':True,'cleanup_errors':[],'actual_exit_code':0}}
    return plan,manifest,terminal,{'deadline':{'elapsed_seconds':1.0}}

def changed(raw, key, value):
    result = copy.deepcopy(raw)
    result[key] = value
    return result

def calibration(reader, core):
    toy = {'case_index':0,'q':5,'n':6,'minimum_distance':5,'t':1,'s':'3','status':'CANDIDATE_CERTIFICATES','first_veto':None,
        'p_coefficients':['1','1/8'],'g_coefficients':['0','1','1/4'],'f_coefficients':['3','2','11/16','3/32'],
        'constant_coefficient':'3','renormalization_denominator':'1'}
    toy['baseline'] = core.derive(5,6,5,3,{},['2/3','11/48','1/32'],reader)
    toy['low_image_counts'] = copy.deepcopy(toy['baseline'])
    rec = {'status':'REJECTED_CONSTRUCTION','first_veto':'RECURRENCE_SIGN','p_coefficients':['1','0'],
        'failed_p_index':1,'failed_value':'0','g_coefficients':None}
    trunc = {'status':'REJECTED_CONSTRUCTION','first_veto':'TRUNCATED_SIGN','p_coefficients':['1','5/6'],
        'g_coefficients':['0','-79/6','5/3'],'failed_g_index':1,'failed_value':'-79/6'}
    base = core.derive(5,2,1,2,{},['1','1'],reader)
    low = core.derive(5,2,1,2,{'1':8,'2':16},['1/25','1/25'],reader)
    def tiny():
        return validate_case(toy,0,1,'3',reader,core,6,5,3,{})[0]
    def tie():
        best = {'baseline':None,'low_image_counts':None}
        certs = {'baseline':base,'low_image_counts':base}
        update_best(best,0,1,'3',certs,core);update_best(best,1,2,'4',certs,core)
        need(best['baseline']['case_index'] == best['low_image_counts']['case_index'] == 0,'FIRST_TIE')
        return best
    def prefix_change(key,value):
        return prefix(changed(toy,key,value),6,1,Fraction(3),reader,core)
    def factor_change():
        raw = copy.deepcopy(toy);raw['f_coefficients'][1]='65/32'
        return validate_case(raw,0,1,'3',reader,core,6,5,3,{})
    def low_change():
        raw = copy.deepcopy(low);raw['multipliers'][1]='2/25'
        return rescaling(base,raw,'25',2,1,2,{'1':8,'2':16},reader,core)
    def value_change():
        raw = copy.deepcopy(toy);raw['baseline']['polynomial_values'][-1]['value']='0'
        return validate_case(raw,0,1,'3',reader,core,6,5,3,{})
    def runtime_change(kind):
        plan,manifest,terminal,summary = fixture_runtime()
        if kind == 'bool':
            terminal['command_exit_code']=False
        if kind == 'old':
            old=(ROOT/'acceleration/construct_20261004_prime5_analytic_delsarte_v1.py').as_posix()
            plan['worker_argv'][2]=old;plan['child_argv'][10]=old;plan['command'][26]=old;plan['supervisor_argv'][26]=old
        return runtime(plan,manifest,terminal,summary,'science',core)
    def bad_checkpoint():
        best=tie();raw={'completed_cases':1,'valid_cases':1,'rejected_cases':0,'first_veto_counts':{},'best':copy.deepcopy(best)}
        raw['best']['baseline']['case_index']=1
        return checkpoint(raw,1,1,0,{},best,core)
    def bad_summary():
        best=tie();raw={'selected_cases':384,'completed_cases':384,'valid_cases':True,'rejected_cases':383,'first_veto_counts':{},'best':best,
            'objective':OBJECTIVE,'target_polynomial_constructed':True,'separate_exact_checker_required':True,
            'image_counts_authenticated_inside_worker':False,'progress':{'completed_cases':384,'active_case':None}}
        return family_summary(raw,1,383,{},best,core)
    actions = [
      ('actual_v2_header','PASS',lambda: header(fixture_header(),'science',core)),
      ('positive_recurrence_g','PASS',lambda: prefix(toy,6,1,Fraction(3),reader,core) and None),
      ('legitimate_first_p_rejection','PASS',lambda: prefix(rec,6,1,Fraction(0),reader,core) and None),
      ('legitimate_g_rejection','PASS',lambda: prefix(trunc,6,1,Fraction(20),reader,core) and None),
      ('tiny_complete_polynomial','PASS',tiny),
      ('n2_exact_rescaling','PASS',lambda: {'denominator':'25','bound':rescaling(base,low,'25',2,1,2,{'1':8,'2':16},reader,core)[1]['code_size_upper']}),
      ('first_equal_bound_tie','PASS',tie),
      ('old_implementation','FAMILY_HEADER',lambda: header(changed(fixture_header(),'implementation_version',1),'science',core)),
      ('boolean_implementation','FAMILY_HEADER',lambda: header(changed(fixture_header(),'implementation_version',True),'science',core)),
      ('old_source','FAMILY_SOURCE',lambda: header(changed(fixture_header(),'source',{'path':PRODUCER,'sha256':'0'*64}),'science',core)),
      ('missing_software','FAMILY_INPUTS',lambda: header(changed(fixture_header(),'inputs_sha256',{}),'science',core)),
      ('wrong_p_value','TRACE_RECURRENCE',lambda: prefix_change('p_coefficients',['1','1/9'])),
      ('missed_first_nonpositive_p','TRACE_SIGN',lambda: prefix({'status':'REJECTED_CONSTRUCTION','first_veto':'RECURRENCE_SIGN',
        'p_coefficients':['1','0','-1/20'],'failed_p_index':2,'failed_value':'-1/20','g_coefficients':None},6,2,Fraction(0),reader,core)),
      ('wrong_g_value','TRACE_G',lambda: prefix_change('g_coefficients',['0','2','1/4'])),
      ('false_p_rejection','TRACE_SIGN',lambda: prefix({'status':'REJECTED_CONSTRUCTION','first_veto':'RECURRENCE_SIGN',
        'p_coefficients':['1','1/8'],'failed_p_index':1,'failed_value':'1/8','g_coefficients':None},6,1,Fraction(3),reader,core)),
      ('wrong_failed_g_value','TRACE_FAILED_VALUE',lambda: prefix(changed(trunc,'failed_value','0'),6,1,Fraction(20),reader,core)),
      ('wrong_full_product_coefficient','FACTORIZATION',factor_change),
      ('wrong_constant','CONSTANT_COEFFICIENT',lambda: validate_case(changed(toy,'constant_coefficient','4'),0,1,'3',reader,core,6,5,3,{})),
      ('wrong_rescaling_denominator','RESCALING_DENOMINATOR',lambda: rescaling(base,low,'24',2,1,2,{'1':8,'2':16},reader,core)),
      ('wrong_rescaled_multiplier','RESCALING_MULTIPLIERS',low_change),
      ('wrong_last_certificate_value','VALUE_TABLE',value_change),
      ('actual_flat_runtime','PASS',lambda: runtime_change('valid')),
      ('boolean_native_exit','RUNTIME_EXIT',lambda: runtime_change('bool')),
      ('old_caller_runtime','RUNTIME_SUFFIX',lambda: runtime_change('old')),
      ('checkpoint_wrong_tie','FAMILY_CHECKPOINT',bad_checkpoint),
      ('reordered_case','FAMILY_LABEL',lambda: validate_case(changed(toy,'case_index',1),0,1,'3',reader,core,6,5,3,{})),
      ('boolean_summary_count','FAMILY_SUMMARY',bad_summary),
    ]
    rows=[]
    for i,(name,expected,action) in enumerate(actions):
        reader.tick()
        try:
            result,actual=action(),'PASS'
        except (Veto,core.Veto) as exc:
            actual,result=str(exc),None
        row={'index':i,'name':name,'expected':expected,'actual':actual,'result':result}
        reader.save('control_'+str(i)+'.json',row);rows.append(row)
        need(actual == expected,'CONTROL_STAGE')
    reader.save('controls.json',rows)
    return {'status':CAL_STATUS,'control_rows':27,'positive':8,'negative':19,'own68_actions_rerun':0,'old_adapter15_actions_rerun':0}

def full(ref, reader, core):
    config=reader.ref(ref)
    need(type(config) is dict and config.keys() == {'schema','family_own','family_root','author','science','premises'}
         and config['schema'] == 'INDEPENDENT_PRIME5_ANALYTIC_FAMILY_PACKET_V1', 'CONFIGURATION')
    own,root=reader.ref(config['family_own']),reader.ref(config['family_root'])
    need(own.get('status') == CAL_STATUS and own.get('source') == {'path':SELF,'sha256':reader.inputs[SELF]}
         and own.get('specification') == {'path':SPEC,'sha256':reader.inputs[SPEC]}
         and own.get('control_rows') == 27 and own.get('positive') == 8 and own.get('negative') == 19, 'FAMILY_QUALIFICATION')
    need(root.get('reviewer') == '/root' and root.get('result') == 'PASS_FINITE_ANALYTIC_FAMILY_CHECKER_ENGINEERING_ONLY'
         and root.get('source') == own['source'] and root.get('specification') == own['specification']
         and core.equal(root.get('own_calibration'),config['family_own']), 'FAMILY_ROOT_QUALIFICATION')
    need(type(config['premises']) is dict and config['premises'].keys() == set(core.PREMISES)|{'renorm_binding','renorm_report','renorm_acceptance'}, 'PREMISE_REFS')
    for key,ref in config['premises'].items():
        need(core.equal(ref,core.PREMISES[key] if key in core.PREMISES else RENORM_REFS[key]),'PREMISE_REF')
        raw=reader.ref(ref)
        if key == 'renorm_binding':
            need(raw.get('id') == 'C-CODE-DELSARTE-IMAGE-LOWER-COUNT-RENORMALIZATION' and raw.get('revision') == 1
                 and raw.get('status') == 'VERIFIED' and raw.get('review_state') == 'CLEAR','RENORM_PREMISE')
        elif key == 'renorm_report':
            need(raw.get('claim_id') == 'C-CODE-DELSARTE-IMAGE-LOWER-COUNT-RENORMALIZATION' and raw.get('revision') == 1
                 and raw.get('result') == 'PASS' and raw.get('verifier') == '/root/native_driver','RENORM_PREMISE')
        elif key == 'renorm_acceptance':
            need(raw.get('claim_id') == 'C-CODE-DELSARTE-IMAGE-LOWER-COUNT-RENORMALIZATION' and raw.get('claim_revision') == 1
                 and raw.get('reviewer') == '/root' and raw.get('result') == 'PASS_INDEPENDENT_WRITTEN_SCOPE','RENORM_PREMISE')
    author,outputs=packet(config['author'],'calibrate',reader,core)
    need(author.get('control_count') == 4 and author.get('positive_controls') == 2 and author.get('negative_controls') == 2
         and author.get('target_polynomial_constructed') is False,'AUTHOR_POPULATION')
    stages=author_actions(outputs,reader,core)
    raw,outputs=packet(config['science'],'science',reader,core)
    selected=universe();need(len(selected) == 384 and len(set(selected)) == 384,'FAMILY_UNIVERSE')
    valid,rejected,counts,best,checks,best_objects=0,0,{}, {'baseline':None,'low_image_counts':None},[],{'baseline':None,'low_image_counts':None}
    for index,(t,s) in enumerate(selected):
        reader.tick();stem='case_'+str(index).zfill(4)
        row,certs=validate_case(outputs[stem+'.json'],index,t,s,reader,core)
        checks.append(row)
        if certs is None:
            rejected+=1;counts[row['first_veto']]=counts.get(row['first_veto'],0)+1
        else:
            valid+=1
            old=copy.deepcopy(best)
            update_best(best,index,t,s,certs,core)
            for branch in best:
                if not core.equal(old[branch],best[branch]):
                    best_objects[branch]=certs[branch]
        checkpoint(outputs[stem+'_checkpoint.json'],index+1,valid,rejected,counts,best,core)
    family_summary(raw,valid,rejected,counts,best,core)
    reader.save('independent_case_checks.json',checks)
    reader.save('independent_author_stages.json',stages)
    reader.save('independent_best_baseline.json',best_objects['baseline'])
    reader.save('independent_best_low_image_counts.json',best_objects['low_image_counts'])
    return {'status':FULL_STATUS,'outcome':{'complete_cases':384,'valid_cases':valid,'rejected_cases':rejected,'first_veto_counts':counts,
        'complete_candidate_certificates':2*valid,'multipliers_per_certificate':32,'tail_weights_per_certificate':45,
        'values_per_certificate':46,'best':best,'objective':OBJECTIVE},'producer_actions_replayed':4,'own68_actions_rerun':0,
        'old_adapter15_actions_rerun':0,'family_own_actions_rerun':0,'all_prefixes_and_product_polynomials_checked':True}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('calibrate','full'))
    for flag in ('seconds','out','self-sha256','spec-sha256'):
        parser.add_argument('--'+flag,required=True,type=float if flag == 'seconds' else str)
    parser.add_argument('--configuration');parser.add_argument('--configuration-sha256');args=parser.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='One fresh analytic family checker qualification or complete384-case rational replay; all reads, folds, writes and closing guards share the deadline.')
    out=Path(args.out);reader=Reader(deadline,out)
    try:
        reader.tick();need(not out.exists() and out.resolve().is_relative_to(ROOT/'acceleration/results')
            and all(not p.is_symlink() for p in out.parents),'OUTPUT_PATH');out.mkdir(parents=True)
        reader.raw(SELF,args.self_sha256);reader.raw(SPEC,args.spec_sha256);core=load_core(reader)
        result=calibration(reader,core) if args.mode == 'calibrate' else full({'path':args.configuration,'sha256':args.configuration_sha256},reader,core)
        reader.close();reader.tick()
        outputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
        need(len(outputs) == (28 if args.mode == 'calibrate' else 4),'OUTPUT_POPULATION')
        summary={'schema':'INDEPENDENT_PRIME5_ANALYTIC_FAMILY_RUN_V1','implementation_version':1,'mode':args.mode,
            'timestamp':datetime.now(timezone.utc).isoformat(),'producer':'/root/structural','verifier':'/root/native_driver','method':'independent_artifact_check',
            'source':{'path':SELF,'sha256':args.self_sha256},'specification':{'path':SPEC,'sha256':args.spec_sha256},**result,
            'inputs_sha256':reader.inputs,'outputs_sha256':outputs,'output_payload_count':len(outputs),'physical_file_count':len(outputs)+1,
            'deadline':deadline.status(),'LP_calls':0,'target_resolution':'NONE','nonzero_code_forced':False,
            'shared_core':{'path':CORE,'sha256':PINS[CORE]},'limitations':['Qualified Native math and literal Reader are shared; no Structural module/functions/AST/backend imported.',
            'Finite384 selected cases only; every rejection concerns this construction and does not prove code infeasibility.',
            'Exact lower-count bound requires accepted support55/image-count/rescaling applicability, no nonzero code or target resolution.']}
        reader.save('summary.json',summary);reader.close();reader.tick()
        print(json.dumps({'status':summary['status'],'summary':str(out/'summary.json')}));return 0
    except Exception as exc:
        if out.is_dir() and not (out/'failure.json').exists():
            with (out/'failure.json').open('x',encoding='utf8',newline='\n') as stream:
                json.dump({'status':'FAILED_OR_NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET','error_type':type(exc).__name__,'error':str(exc),
                    'deadline':deadline.status(),'provisional_summary_is_not_gate':(out/'summary.json').exists()},stream,indent=2,allow_nan=False);stream.write('\n')
        print(json.dumps({'error_type':type(exc).__name__,'error':str(exc)}),file=sys.stderr);return 1

if __name__ == '__main__':
    raise SystemExit(main())
