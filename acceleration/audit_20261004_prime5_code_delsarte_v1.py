"""SOURCE ONLY: independent exact Delsarte certificates by integer coefficient folds.
No producer import, AST extraction, numerical backend or code enumeration.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261004_prime5_code_delsarte_v1.py'
SPEC = 'acceleration/audit_20261004_prime5_code_delsarte_v1_spec.md'
PRODUCER = 'acceleration/solve_20261004_prime5_code_delsarte_v2.py'
PRODUCER_SPEC = 'acceleration/solve_20261004_prime5_code_delsarte_v2_spec.md'
PRODUCER_SHA = 'ac47adedb67794ed029c72b920fcfd039ef0210f1e45daf257dcd361223776d7'
PRODUCER_SPEC_SHA = 'd21bb894ba67f4b5e6f4582963ae8c70dd7f66ab7d05810f8226eb80bcbc45b4'
SUP_SHA = '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17'
PINS = {
 PRODUCER: PRODUCER_SHA, PRODUCER_SPEC: PRODUCER_SPEC_SHA,
 'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command_v2.py': SUP_SHA,
 'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}
PREMISES = {
 'support_binding': {'path':'acceleration/results/20261004_independent_review/target_prime5_left_code_support55_native01/claim_binding_schema2.json','sha256':'277f203d4aadec95182ed8a6195128a7978710be8b79922d6984566cbd7229eb'},
 'support_report': {'path':'acceleration/results/20261004_independent_review/target_prime5_left_code_support55_native01/summary.json','sha256':'448cb1b9b4925cac3a51bba2fd05c26d1a394aa1dccb1de78f5389db931f3d1f'},
 'support_acceptance': {'path':'acceleration/results/20261004_target_prime5_left_code_support55_root_written_acceptance01.json','sha256':'2e01da9ae94d42ff931074f91e6cb973e8ba8165110bfa9598187deaa8b4aa38'},
 'counts_binding': {'path':'acceleration/results/20261004_independent_review/prime5_triangle_image_weight_counts_native01/claim_binding_schema2.json','sha256':'a2c8c707e79e985c9959f576dd0f5690267967a16586c852a6ada8228261129c'},
 'counts_report': {'path':'acceleration/results/20261004_independent_review/prime5_triangle_image_weight_counts_native01/summary.json','sha256':'f43cb87b3de159e6d6e65a56f8943a63d2609afadc9869519b95649e9d0e8e19'},
 'counts_acceptance': {'path':'acceleration/results/20261004_prime5_triangle_image_weight_counts_root_written_acceptance01.json','sha256':'0ca9cd13d1ce1877bfced1325677c83c9c283c31b3a872688d4423c09a3da081'},
}
LOWER = {'3':924,'4':8316,'5':24948,'6':391776}
CAL_STATUS = 'INDEPENDENT_PRIME5_CODE_DELSARTE_V1_CALIBRATION_PASS'
CONTROL_STATUS = 'INDEPENDENT_PRIME5_CODE_DELSARTE_V1_PRODUCER_CONTROLS_PASS'
FULL_STATUS = 'INDEPENDENT_PRIME5_CODE_DELSARTE_V1_COMPLETE_PASS'


class Veto(ValueError):
    def __init__(self, stage, detail=None):
        super().__init__(stage)
        self.stage, self.detail = stage, detail


def need(ok, stage, detail=None):
    if not ok:
        raise Veto(stage, detail)


def equal(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def unique(items):
    result = {}
    for key, value in items:
        need(type(key) is str and key not in result, 'DUPLICATE_KEY')
        result[key] = value
    return result


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def canonical(text):
    need(type(text) is str and len(text) <= 2048, 'FRACTION_TEXT')
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError):
        raise Veto('FRACTION_CANONICAL') from None
    need(str(value) == text and value.denominator <= 10**512, 'FRACTION_CANONICAL')
    return value


def parameters(q, n, distance, degree, lower):
    need(type(q) is int and q in (2, 5) and type(n) is int and 1 <= n <= 99
         and type(distance) is int and 1 <= distance <= n
         and type(degree) is int and 1 <= degree <= min(32, n), 'PARAMETERS')
    need(type(lower) is dict, 'LOWER_SHAPE')
    for key, value in lower.items():
        need(type(key) is str and re.fullmatch('[1-9][0-9]*', key) is not None
             and 1 <= int(key) <= degree, 'LOWER_KEY')
        need(type(value) is int, 'LOWER_INTEGER')
        j, shell = int(key), 1
        for position in range(1, j+1):
            shell = shell*(n-position+1)//position
        shell *= (q-1)**j
        need(0 <= value <= shell, 'LOWER_RANGE')


def coefficients(q, n, degree, weight, budget=None):
    need(all(type(x) is int for x in (q, n, degree, weight))
         and q in (2, 5) and 0 <= degree <= n <= 99 and 0 <= weight <= n, 'KRAW_PARAMETERS')
    # Fresh generating-function fold; no binomial/signed-sum producer algorithm.
    values = [1] + [0]*degree
    for coordinate in range(n):
        if budget is not None:
            budget.tick()
        slope = -1 if coordinate < weight else q-1
        for j in range(min(degree, coordinate+1), 0, -1):
            values[j] += slope*values[j-1]
    return values


def derive(q, n, distance, degree, lower, texts, budget=None):
    parameters(q, n, distance, degree, lower)
    need(type(texts) is list and len(texts) == degree, 'COEFFICIENT_SHAPE')
    multipliers = [canonical(text) for text in texts]
    need(all(y >= 0 for y in multipliers), 'COEFFICIENT_SIGN')
    rows = []
    for weight in [0, *range(distance, n+1)]:
        krow = coefficients(q, n, degree, weight, budget)
        total = Fraction(1)
        for j, multiplier in enumerate(multipliers, 1):
            total += multiplier*(krow[j]-lower.get(str(j), 0))
        need(weight == 0 or total <= 0, 'POLYNOMIAL_SIGN',
             {'weight':weight,'value':str(total)})
        rows.append({'weight':weight,'value':str(total)})
    bound = canonical(rows[0]['value'])
    need(bound >= 1, 'ZERO_CODE_BOUND')
    power, dimension = 1, 0
    while power*q <= bound:
        if budget is not None:
            budget.tick()
        power *= q
        dimension += 1
    return {'schema':'EXACT_CODE_DELSARTE_DUAL_CANDIDATE_V1','q':q,'n':n,
        'minimum_distance':distance,'degree':degree,'dual_lower_counts':copy.deepcopy(lower),
        'multipliers':list(texts),'polynomial_values':rows,'code_size_upper':str(bound),
        'integer_dimension_upper':dimension,'dimension_lower_power':power,
        'dimension_next_power':power*q,'nonzero_code_forced':False,
        'is_optimality_certificate':False,'target_resolution':'NONE'}


def certificate(raw, expected=None, budget=None):
    fields = {'schema','q','n','minimum_distance','degree','dual_lower_counts','multipliers',
        'polynomial_values','code_size_upper','integer_dimension_upper',
        'dimension_lower_power','dimension_next_power','nonzero_code_forced',
        'is_optimality_certificate','target_resolution'}
    need(type(raw) is dict and raw.keys() == fields
         and raw.get('schema') == 'EXACT_CODE_DELSARTE_DUAL_CANDIDATE_V1', 'CERTIFICATE_HEADER')
    need(raw['nonzero_code_forced'] is False and raw['is_optimality_certificate'] is False
         and raw['target_resolution'] == 'NONE', 'CERTIFICATE_SCOPE')
    q, n, d, h, lower = (raw[k] for k in ('q','n','minimum_distance','degree','dual_lower_counts'))
    parameters(q, n, d, h, lower)
    if expected is not None:
        need(equal([q,n,d,h,lower], expected), 'FIXED_PARAMETERS')
    computed = derive(q, n, d, h, lower, raw['multipliers'], budget)
    need(equal(raw['polynomial_values'], computed['polynomial_values']), 'VALUE_TABLE')
    canonical(raw['code_size_upper'])
    need(raw['code_size_upper'] == computed['code_size_upper'], 'BOUND_VALUE')
    for name in ('integer_dimension_upper','dimension_lower_power','dimension_next_power'):
        need(type(raw[name]) is int and raw[name] == computed[name], 'DIMENSION_POWERS')
    return computed


def candidate_wrapper(raw, expected, budget=None):
    need(type(raw) is dict and raw.keys() == {'candidate','unknown_reason'}, 'CANDIDATE_WRAPPER')
    if raw['candidate'] is None:
        need(type(raw['unknown_reason']) is str and bool(raw['unknown_reason']), 'UNKNOWN_REASON')
        return {'candidate_available':False,'unknown_reason':raw['unknown_reason'],
                'code_size_upper':None,'integer_dimension_upper':None,
                'candidate_stronger_than_historical27':False,'conclusion':'UNKNOWN'}
    need(raw['unknown_reason'] is None, 'CANDIDATE_REASON')
    checked = certificate(raw['candidate'], expected, budget)
    return {'candidate_available':True,'unknown_reason':None,
        'code_size_upper':checked['code_size_upper'],
        'integer_dimension_upper':checked['integer_dimension_upper'],
        'candidate_stronger_than_historical27':checked['integer_dimension_upper'] < 27,
        'verified_certificate':checked,'conclusion':'CONDITIONAL_EXACT_UPPER_BOUND'}


def safe(path, exists=True):
    need(type(path) is str and bool(path), 'INPUT_PATH')
    p = Path(path)
    if not p.is_absolute():
        need('\\' not in path and ':' not in path and
             all(piece not in ('','.','..') for piece in path.split('/')), 'INPUT_PATH')
        p = ROOT/p
    need(p.resolve().is_relative_to(ROOT) and not p.is_symlink()
         and all(not parent.is_symlink() for parent in p.parents), 'INPUT_PATH')
    if exists:
        need(p.is_file(), 'INPUT_FILE')
    return p


def digest_text(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None, 'INPUT_SHA')
    return value


def reserve(value):
    need(type(value) is dict and value.get('stop_required') is False and
         finite(value.get('remaining_seconds')) and value['remaining_seconds'] > 20, 'SAVE_GUARD')
    return value


class Reader:
    def __init__(self, seconds, out):
        self.deadline = CommandDeadline(seconds, allocation_reason=
            'One independent rational checker; pins, integer coefficient folds, receipts and saves share the deadline.')
        self.out, self.inputs = out, {}

    def tick(self):
        reserve(self.deadline.status())

    def raw(self, path, sha):
        self.tick()
        actual = safe(path)
        digest_text(sha)
        need(actual.stat().st_size <= 2*1024*1024, 'INPUT_SIZE')
        data = actual.read_bytes()
        need(hashlib.sha256(data).hexdigest() == sha, 'INPUT_SHA')
        key = actual.relative_to(ROOT).as_posix()
        need(key not in self.inputs or self.inputs[key] == sha, 'INPUT_CHANGED')
        self.inputs[key] = sha
        self.tick()
        return data

    def ref(self, ref):
        need(type(ref) is dict and ref.keys() == {'path','sha256'}, 'REFERENCE')
        try:
            return json.loads(self.raw(ref['path'],ref['sha256']), object_pairs_hook=unique,
                parse_constant=lambda text: (_ for _ in ()).throw(Veto('JSON_NONFINITE')))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise Veto('JSON_FILE') from None

    def save(self, name, value):
        self.tick()
        p = self.out/name
        need(p.parent == self.out, 'OUTPUT_NAME')
        with p.open('x', encoding='utf8', newline='\n') as stream:
            json.dump(value, stream, allow_nan=False, ensure_ascii=False, indent=2)
            stream.write('\n')
        self.tick()

    def close_inputs(self):
        for name, sha in list(self.inputs.items()):
            self.raw(name,sha)


def inventory(base, output_map):
    need(type(output_map) is dict and all(type(k) is str and '\\' not in k and ':' not in k
         and k != 'summary.json' and all(piece not in ('','.','..') for piece in k.split('/'))
         for k in output_map), 'OUTPUT_MAP')
    for sha in output_map.values():
        digest_text(sha)
    actual = []
    for p in base.rglob('*'):
        need(not p.is_symlink(), 'OUTPUT_INVENTORY')
        if p.is_file() and p != base/'summary.json':
            actual.append(p.relative_to(base).as_posix())
    need(set(actual) == set(output_map), 'OUTPUT_INVENTORY')
    return sorted(actual)


def options(words):
    need(type(words) is list and len(words)%2 == 0, 'RUNTIME_FLAGS')
    result = {}
    for name, value in zip(words[::2], words[1::2]):
        need(type(name) is str and name.startswith('--') and name not in result
             and type(value) is str and bool(value), 'RUNTIME_FLAGS')
        result[name] = value
    return result


def runtime(plan, manifest, terminal, summary, mode):
    need(type(plan) is dict, 'RUNTIME_PLAN')
    schemas = ({'PRIME5_CODE_DELSARTE_V2_SOURCE_ONLY_AUTHOR_CALIBRATION_PLAN'} if mode == 'calibrate'
        else {'PRIME5_CODE_DELSARTE_CONCRETE_SCIENCE_PLAN_V2',
              'ROOT_PRIME5_CODE_DELSARTE_CONCRETE_SCIENCE_PLAN_V2'})
    need(plan.get('schema') in schemas, 'RUNTIME_PLAN')
    root_flat = plan['schema'] == 'ROOT_PRIME5_CODE_DELSARTE_CONCRETE_SCIENCE_PLAN_V2'
    command, child, worker = (plan.get(k) for k in ('command','child_argv','worker_argv'))
    need(all(type(x) is list and all(type(w) is str and w for w in x)
             for x in (command,child,worker)), 'RUNTIME_PLAN')
    need(equal(plan.get('supervisor_argv'),command), 'RUNTIME_ALIAS')
    if mode == 'science' and not root_flat:
        nested = plan.get('solve')
        need(type(nested) is dict and all(equal(nested.get(k),plan.get(k)) for k in
             ('command','supervisor_argv','child_argv','worker_argv','allocation')), 'RUNTIME_ALIAS')
    need(len(worker) == (12 if mode == 'calibrate' else 16) and len(child) == len(worker)+8
         and len(command) == len(child)+16 and command[16:] == child and child[8:] == worker,
         'RUNTIME_SUFFIX')
    need(command[:2] == [worker[0],'-B'] and safe(command[2]) == ROOT/'acceleration/run_compute_command_v2.py'
         and worker[1] == '-B' and safe(worker[2]) == ROOT/PRODUCER and worker[3] == mode,
         'RUNTIME_SOURCE')
    need(child[1:5] == ['run','--locked','--offline','--cache-dir']
         and safe(child[5],False) == ROOT/'build/uv-cache' and child[6:8] == ['--python',worker[0]],
         'RUNTIME_ENVIRONMENT')
    outer, flags = options(command[3:15]), options(worker[4:])
    need(command[15] == '--' and outer.keys() == {'--seconds','--shutdown-reserve-seconds',
         '--allocation-reason','--success-criterion','--verification-criterion','--out'}, 'RUNTIME_FLAGS')
    wanted_flags = {'--seconds','--out','--self-sha256','--spec-sha256'}
    if mode == 'science':
        wanted_flags |= {'--configuration','--configuration-sha256'}
    need(flags.keys() == wanted_flags and flags['--self-sha256'] == PRODUCER_SHA
         and flags['--spec-sha256'] == PRODUCER_SPEC_SHA, 'RUNTIME_SOURCE')
    need(type(manifest) is dict and manifest.get('schema_version') == 1
         and type(manifest.get('schema_version')) is int and equal(manifest.get('command'),child)
         and manifest.get('source_sha256') == SUP_SHA
         and manifest.get('runtime_scope') == 'LOCAL_WINDOWS_SUSPENDED_JOB_V1'
         and manifest.get('process_scope') == 'Local non-escaping process tree only; remote/daemonized compute is unsupported'
         and manifest.get('automatic_retry') is False and manifest.get('cumulative_across_commands') is False
         and safe(manifest.get('cwd'),False) == ROOT, 'RUNTIME_MANIFEST')
    for field, flag in (('seconds','--seconds'),('shutdown_reserve_seconds','--shutdown-reserve-seconds')):
        need(finite(manifest.get(field)) and manifest[field] == float(outer[flag]), 'RUNTIME_ALLOCATION')
    allocation = plan.get('allocation')
    if root_flat:
        need(equal(plan.get('source'),{'path':PRODUCER,'sha256':PRODUCER_SHA})
             and equal(plan.get('specification'),{'path':PRODUCER_SPEC,'sha256':PRODUCER_SPEC_SHA})
             and equal(plan.get('word_counts'),{'supervisor':40,'child':24,'worker':16})
             and equal(plan.get('configuration'),{'path':flags['--configuration'],
                 'sha256':flags['--configuration-sha256']})
             and outer['--seconds'] == '180' and flags['--seconds'] == '150'
             and outer['--shutdown-reserve-seconds'] == '20', 'RUNTIME_ROOT_PROFILE')
        # These are this profile's literal command allocations, not invented plan fields.
        allocation = {'outer_seconds':180,'worker_seconds':150,
                      'save_reserve_seconds':20,'shutdown_reserve_seconds':20}
    need(type(allocation) is dict and all(finite(allocation.get(k)) for k in
         ('outer_seconds','worker_seconds','save_reserve_seconds','shutdown_reserve_seconds'))
         and allocation['outer_seconds'] == manifest['seconds']
         and allocation['worker_seconds'] == float(flags['--seconds'])
         and allocation['save_reserve_seconds'] == allocation['shutdown_reserve_seconds'] == 20
         and allocation['shutdown_reserve_seconds'] == manifest['shutdown_reserve_seconds'], 'RUNTIME_ALLOCATION')
    need(type(terminal) is dict and type(terminal.get('command_exit_code')) is int
         and terminal['command_exit_code'] == 0 and terminal.get('stop_reason') == 'COMMAND_EXITED'
         and terminal.get('status') == 'COMMAND_COMPLETED_VERIFICATION_PENDING'
         and terminal.get('error') is None and terminal.get('deadline_reached') is False, 'RUNTIME_EXIT')
    cleanup = terminal.get('cleanup')
    need(type(cleanup) is dict and type(cleanup.get('actual_exit_code')) is int
         and cleanup['actual_exit_code'] == 0 and all(cleanup.get(k) is True for k in
         ('created_suspended','resumed','reaped','job_active_zero_observed'))
         and cleanup.get('cleanup_errors') == [], 'RUNTIME_CLEANUP')
    need(type(manifest.get('invocation_id')) is str and bool(manifest['invocation_id'])
         and terminal.get('invocation_id') == manifest['invocation_id'], 'RUNTIME_INVOCATION')
    need(finite(terminal.get('elapsed_seconds')) and 0 <= terminal['elapsed_seconds'] <= manifest['seconds'],
         'RUNTIME_ELAPSED')
    reserve(summary.get('deadline'))
    return flags, outer


def guidance(raw, degree, rows):
    keys = {'schema','status','message','scipy_version','variable_count','constraint_count',
        'time_limit_seconds','solver_success','fun','scaled_variables','is_exact_certificate'}
    need(type(raw) is dict and raw.keys() == keys and raw['schema'] == 'NUMERICAL_CODE_LP_GUIDANCE_V1'
         and type(raw['status']) is int and type(raw['message']) is str
         and raw['scipy_version'] == '1.18.1'
         and type(raw['variable_count']) is int and raw['variable_count'] == degree
         and type(raw['constraint_count']) is int and raw['constraint_count'] == rows
         and finite(raw['time_limit_seconds']) and 0 < raw['time_limit_seconds'] <= 20
         and type(raw['solver_success']) is bool and raw['is_exact_certificate'] is False, 'GUIDANCE_HEADER')
    need(raw['fun'] is None or finite(raw['fun']), 'GUIDANCE_FINITE')
    values = raw['scaled_variables']
    need(values is None or (type(values) is list and len(values) == degree and
         all(type(x) is float and math.isfinite(x) for x in values)), 'GUIDANCE_FINITE')
    return {'numerical_status_is_proof':False,'numerical_infeasibility_is_proof':False}


def character_fixture():
    # Direct 8-character enumeration on the written even binary code, no backend.
    words = [[0,0,0],[1,1,0],[1,0,1],[0,1,1]]
    sums, dual = [], [0]*4
    for bits in range(8):
        u = [(bits >> i) & 1 for i in range(3)]
        value = sum(1 if sum(x*y for x,y in zip(u,word))%2 == 0 else -1 for word in words)
        need(value in (0,4), 'HAND_EXPECTATION')
        sums.append(value)
        if value == 4:
            dual[sum(u)] += 1
    transformed = [coefficients(2,3,3,0)[j]+3*coefficients(2,3,3,2)[j] for j in range(4)]
    zero = [coefficients(2,3,0,i)[0] for i in range(4)]
    need(equal(sums,[4,0,0,0,0,0,0,4]) and equal(dual,[1,0,0,1])
         and equal(transformed,[4,0,0,4]) and equal(zero,[1,1,1,1]), 'HAND_EXPECTATION')
    return {'eight_character_sums':sums,'dual_weight_counts':dual,
            'transformed_weight_counts':transformed,'K0':zero}


def synthetic_guidance():
    return {'schema':'NUMERICAL_CODE_LP_GUIDANCE_V1','status':0,'message':'synthetic no backend call',
        'scipy_version':'1.18.1','variable_count':1,'constraint_count':2,
        'time_limit_seconds':1.0,'solver_success':True,'fun':3.0,
        'scaled_variables':[3.0],'is_exact_certificate':False}


def synthetic_runtime():
    worker = [(ROOT/'build/research-venv/Scripts/python.exe').as_posix(),'-B',(ROOT/PRODUCER).as_posix(),
        'calibrate','--seconds','100','--out',(ROOT/'acceleration/results/synthetic_q5_controls').as_posix(),
        '--self-sha256',PRODUCER_SHA,'--spec-sha256',PRODUCER_SPEC_SHA]
    child = ['uv','run','--locked','--offline','--cache-dir',(ROOT/'build/uv-cache').as_posix(),
             '--python',worker[0],*worker]
    command = [worker[0],'-B',(ROOT/'acceleration/run_compute_command_v2.py').as_posix(),
        '--seconds','120','--shutdown-reserve-seconds','20','--allocation-reason','synthetic',
        '--success-criterion','synthetic','--verification-criterion','synthetic',
        '--out',(ROOT/'acceleration/results/synthetic_q5_SUP').as_posix(),'--',*child]
    allocation = {'outer_seconds':120,'worker_seconds':100,
                  'save_reserve_seconds':20,'shutdown_reserve_seconds':20}
    manifest = {'schema_version':1,'command':child,'source_sha256':SUP_SHA,
        'runtime_scope':'LOCAL_WINDOWS_SUSPENDED_JOB_V1',
        'process_scope':'Local non-escaping process tree only; remote/daemonized compute is unsupported',
        'automatic_retry':False,'cumulative_across_commands':False,'cwd':ROOT.as_posix(),
        'seconds':120,'shutdown_reserve_seconds':20,'invocation_id':'synthetic_q5'}
    terminal = {'invocation_id':'synthetic_q5','status':'COMMAND_COMPLETED_VERIFICATION_PENDING',
        'stop_reason':'COMMAND_EXITED','command_exit_code':0,'error':None,'deadline_reached':False,
        'elapsed_seconds':1.0,'cleanup':{'actual_exit_code':0,'created_suspended':True,
            'resumed':True,'reaped':True,'job_active_zero_observed':True,'cleanup_errors':[]}}
    return {'plan':{'schema':'PRIME5_CODE_DELSARTE_V2_SOURCE_ONLY_AUTHOR_CALIBRATION_PLAN',
        'command':command,'supervisor_argv':command,'child_argv':child,'worker_argv':worker,'allocation':allocation},
        'manifest':manifest,'terminal':terminal,'summary':{'deadline':{'stop_required':False,'remaining_seconds':80}}}


AUTHOR_NAMES = [
 'character_normalization_and_kraw_zero','kraw_first','kraw_second','binary_even_three',
 'binary_repetition','quinary_length_one','quinary_length_two','rational_rescale','tiny_numerical_guide',
 'boolean_q','zero_length','zero_distance','boolean_degree','noncanonical_lower_key','late_lower_key',
 'boolean_lower','negative_lower','ambient_lower_exceeded','short_coefficients','boolean_fraction',
 'float_fraction','unreduced_fraction','zero_denominator','negative_coefficient','insufficient_coefficient',
 'last_weight_sign','boolean_sha','wrong_source_sha','occupied_output',
 'high_degree_full_space','degree_cap_33',
]
AUTHOR_EXPECTED = ['PASS']*9 + ['PARAMETERS']*4 + ['LOWER_KEY']*2 + [
 'LOWER_INTEGER','LOWER_RANGE','LOWER_RANGE','COEFFICIENT_SHAPE','FRACTION_TEXT','FRACTION_TEXT',
 'FRACTION_CANONICAL','FRACTION_CANONICAL','COEFFICIENT_SIGN','POLYNOMIAL_SIGN','POLYNOMIAL_SIGN',
 'INPUT_SHA','INPUT_SHA','OUTPUT_EXISTS','PASS','PARAMETERS']


def literal_author_actions(reader):
    # Each pure positive is reconstructed with the independent coefficient fold.
    return [
      lambda:character_fixture(),
      lambda:[coefficients(5,3,1,i)[1] for i in range(4)],
      lambda:[coefficients(2,3,2,i)[2] for i in range(4)],
      lambda:derive(2,3,2,1,{},['1']),
      lambda:derive(2,3,3,1,{},['1/3']),
      lambda:derive(5,1,1,1,{},['1']),
      lambda:derive(5,2,2,1,{},['1/2']),
      lambda:{'unscaled':derive(2,3,2,1,{},['1']),'scaled':derive(2,3,2,1,{},['1'])},
      lambda:{'guidance':synthetic_guidance(),'candidate':derive(2,3,2,1,{},['1']),'unknown_reason':None},
      lambda:parameters(True,3,2,1,{}),
      lambda:parameters(5,0,1,1,{}),
      lambda:parameters(5,3,0,1,{}),
      lambda:parameters(5,3,2,True,{}),
      lambda:parameters(5,3,2,1,{'01':0}),
      lambda:parameters(5,3,2,1,{'2':0}),
      lambda:parameters(5,3,2,1,{'1':True}),
      lambda:parameters(5,3,2,1,{'1':-1}),
      lambda:parameters(5,1,1,1,{'1':5}),
      lambda:derive(2,3,2,1,{},[]),
      lambda:derive(2,3,2,1,{},[True]),
      lambda:derive(2,3,2,1,{},[1.0]),
      lambda:derive(2,3,2,1,{},['2/2']),
      lambda:derive(2,3,2,1,{},['1/0']),
      lambda:derive(2,3,2,1,{},['-1']),
      lambda:derive(2,3,2,1,{},['1/2']),
      lambda:derive(2,2,1,2,{},['0','1']),
      lambda:reader.raw(SELF,True),
      lambda:reader.raw(SELF,'0'*64),
      lambda:need(not reader.out.exists(),'OUTPUT_EXISTS'),
      lambda:derive(5,32,1,32,{},['1']*32),
      lambda:parameters(5,33,1,33,{}),
    ]


def replay_author(reader, summary, base):
    need(summary.get('status') == 'PRIME5_CODE_DELSARTE_V2_AUTHOR_CONTROLS_PASS'
         and type(summary.get('positive')) is int and summary['positive'] == 10
         and type(summary.get('negative')) is int and summary['negative'] == 21
         and type(summary.get('LP_calls')) is int and summary['LP_calls'] == 1
         and summary.get('scientific_LP_calls') == 0 and type(summary.get('scientific_LP_calls')) is int
         and summary.get('target_parameters_read') is False, 'AUTHOR_HEADER')
    expected_files = {f'control_{i:02d}.json' for i in range(31)} | {'controls.json'}
    need(summary['outputs_sha256'].keys() == expected_files, 'AUTHOR_POPULATION')
    controls = reader.ref({'path':(base/'controls.json').relative_to(ROOT).as_posix(),
                          'sha256':summary['outputs_sha256']['controls.json']})
    need(type(controls) is dict and controls.keys() == {'schema','rows'}
         and controls['schema'] == 'PRIME5_CODE_DELSARTE_CONTROLS_V2'
         and type(controls['rows']) is list and len(controls['rows']) == 31, 'AUTHOR_TABLE')
    actions, stages = literal_author_actions(reader), []
    for i, (name, expected, action) in enumerate(zip(AUTHOR_NAMES,AUTHOR_EXPECTED,actions)):
        reader.tick()
        ref = {'path':(base/f'control_{i:02d}.json').relative_to(ROOT).as_posix(),
               'sha256':summary['outputs_sha256'][f'control_{i:02d}.json']}
        raw = reader.ref(ref)
        need(type(raw) is dict and raw.keys() == {'index','name','expected','actual','detail','value'}
             and type(raw['index']) is int and raw['index'] == i and raw['name'] == name
             and raw['expected'] == raw['actual'] == expected, 'AUTHOR_ROW')
        actual, detail, result = 'PASS', None, None
        try:
            result = action()
        except Veto as exc:
            actual, detail = exc.stage, exc.detail
        need(actual == expected and equal(detail,raw['detail']), 'AUTHOR_REJECTION', {'index':i})
        if i < 8 or i == 29:
            need(equal(result,raw['value']), 'AUTHOR_VALUE', {'index':i})
        elif i == 8:
            value = raw['value']
            need(type(value) is dict and value.keys() == {'guidance','candidate','unknown_reason'}
                 and value['unknown_reason'] is None, 'AUTHOR_VALUE')
            guidance(value['guidance'],1,2)
            checked = certificate(value['candidate'],[2,3,2,1,{}],reader)
            need(checked['code_size_upper'] == '4' and value['guidance']['solver_success'] is True,
                 'AUTHOR_VALUE')
        else:
            need(raw['value'] is None, 'AUTHOR_VALUE')
        projection = {k:v for k,v in raw.items() if k != 'value'}
        need(equal(projection,controls['rows'][i]), 'AUTHOR_TABLE')
        stages.append({'index':i,'name':name,'expected':expected,'producer':raw['actual'],'independent':actual})
    return stages


def source_packet(reader, packet, mode):
    fields = {'schema','mode','own_calibration','own_acceptance','producer_summary',
        'producer_plan','producer_manifest','producer_terminal','producer_acceptance'}
    if mode == 'full':
        fields |= {'producer_controls','producer_controls_acceptance'}
    need(type(packet) is dict and packet.keys() == fields
         and packet['schema'] == 'INDEPENDENT_PRIME5_CODE_DELSARTE_CHECK_PACKET_V1'
         and packet['mode'] == mode, 'PACKET_HEADER')
    own = reader.ref(packet['own_calibration'])
    need(type(own) is dict and own.get('status') == CAL_STATUS
         and type(own.get('implementation_version')) is int and own['implementation_version'] == 1
         and own.get('producer') == '/root/structural' and own.get('verifier') == '/root/native_driver'
         and own.get('method') == 'independent_artifact_check' and own.get('target_resolution') == 'NONE'
         and own.get('positive') == 16 and type(own.get('positive')) is int
         and own.get('negative') == 52 and type(own.get('negative')) is int, 'OWN_GATE')
    need(type(own.get('inputs_sha256')) is dict and
         all(own['inputs_sha256'].get(k) == v for k,v in reader.software.items()), 'OWN_GATE_SOURCE')
    need(type(own.get('outputs_sha256')) is dict, 'OWN_GATE')
    own_base = safe(packet['own_calibration']['path']).parent
    inventory(own_base,own['outputs_sha256'])
    for name, sha in own['inputs_sha256'].items():
        reader.raw(name,sha)
    for name, sha in own['outputs_sha256'].items():
        reader.raw((own_base/name).relative_to(ROOT).as_posix(),sha)
    # Root receipts are exact pinned administrative dependencies, not mathematical algorithms.
    need(type(reader.ref(packet['own_acceptance'])) is dict, 'ROOT_RECEIPT')
    need(type(reader.ref(packet['producer_acceptance'])) is dict, 'ROOT_RECEIPT')
    summary = reader.ref(packet['producer_summary'])
    producer_mode = 'calibrate' if mode == 'controls' else 'science'
    need(type(summary) is dict and summary.get('schema') == 'PRIME5_CODE_DELSARTE_RUN_V2'
         and type(summary.get('implementation_version')) is int and summary['implementation_version'] == 2
         and summary.get('mode') == producer_mode and summary.get('producer') == '/root/structural'
         and equal(summary.get('source'),{'path':PRODUCER,'sha256':PRODUCER_SHA})
         and equal(summary.get('specification'),{'path':PRODUCER_SPEC,'sha256':PRODUCER_SPEC_SHA})
         and summary.get('target_resolution') == 'NONE', 'PRODUCER_HEADER')
    inputs, outputs = summary.get('inputs_sha256'), summary.get('outputs_sha256')
    need(type(inputs) is dict and all(inputs.get(k) == v for k,v in PINS.items()), 'PRODUCER_SOFTWARE')
    need(type(outputs) is dict and type(summary.get('output_payload_count')) is int
         and summary['output_payload_count'] == len(outputs)
         and type(summary.get('physical_file_count')) is int
         and summary['physical_file_count'] == len(outputs)+1, 'PRODUCER_POPULATION')
    base = safe(packet['producer_summary']['path']).parent
    inventory(base,outputs)
    for name, sha in inputs.items():
        reader.raw(name,sha)
    for name, sha in outputs.items():
        reader.raw((base/name).relative_to(ROOT).as_posix(),sha)
    plan, manifest, terminal = (reader.ref(packet[k]) for k in
                                ('producer_plan','producer_manifest','producer_terminal'))
    flags, outer = runtime(plan,manifest,terminal,summary,producer_mode)
    need(safe(flags['--out'],False) == base and base.is_dir()
         and safe(packet['producer_manifest']['path']).parent == safe(outer['--out'],False)
         and safe(packet['producer_terminal']['path']).parent == safe(outer['--out'],False)
         and safe(packet['producer_manifest']['path']).name == 'manifest.json'
         and safe(packet['producer_terminal']['path']).name == 'summary.json', 'RUNTIME_LOCATION')
    return summary, base, flags


def accepted_author(reader, ref):
    raw = reader.ref(ref)
    need(type(raw) is dict and raw.get('schema') == 'PRIME5_CODE_DELSARTE_RUN_V2'
         and type(raw.get('implementation_version')) is int and raw['implementation_version'] == 2
         and raw.get('mode') == 'calibrate' and raw.get('producer') == '/root/structural'
         and equal(raw.get('source'),{'path':PRODUCER,'sha256':PRODUCER_SHA})
         and equal(raw.get('specification'),{'path':PRODUCER_SPEC,'sha256':PRODUCER_SPEC_SHA})
         and raw.get('target_resolution') == 'NONE', 'AUTHOR_HEADER')
    need(equal(raw.get('inputs_sha256'),PINS) and type(raw.get('outputs_sha256')) is dict
         and type(raw.get('output_payload_count')) is int and raw['output_payload_count'] == 32
         and type(raw.get('physical_file_count')) is int and raw['physical_file_count'] == 33,
         'AUTHOR_POPULATION')
    base = safe(ref['path']).parent
    inventory(base,raw['outputs_sha256'])
    for name, sha in raw['inputs_sha256'].items():
        reader.raw(name,sha)
    for name, sha in raw['outputs_sha256'].items():
        reader.raw((base/name).relative_to(ROOT).as_posix(),sha)
    return raw, base


def full(reader, packet, summary, base, flags):
    need(summary.get('status') == 'CANDIDATE_PRIME5_CODE_DELSARTE_V2_COMPLETE'
         and type(summary.get('outcome')) is list and len(summary['outcome']) == 4
         and type(summary.get('LP_calls')) is int and summary['LP_calls'] == 4
         and type(summary.get('scientific_LP_calls')) is int and summary['scientific_LP_calls'] == 4
         and summary.get('target_parameters_read') is True and summary.get('nonzero_code_forced') is False
         and summary.get('separate_exact_rational_checker_required') is True
         and summary.get('optimality_or_code_realization_claimed') is False, 'SCIENCE_HEADER')
    config_ref = {'path':flags['--configuration'],'sha256':flags['--configuration-sha256']}
    config = reader.ref(config_ref)
    keys = {'schema','parameters',*PREMISES,'author_controls','author_controls_acceptance','root_authority'}
    parameters_expected = {'q':5,'n':99,'minimum_distance':55,'degrees':[20,32],'image_lower_counts':LOWER}
    need(type(config) is dict and config.keys() == keys
         and config['schema'] == 'PRIME5_CODE_DELSARTE_CONFIGURATION_V2'
         and equal(config['parameters'],parameters_expected), 'SCIENCE_CONFIGURATION')
    need(all(equal(config[name],ref) for name,ref in PREMISES.items()), 'SCIENCE_PREMISES')
    expected_inputs = dict(PINS)
    expected_inputs[config_ref['path']] = config_ref['sha256']
    premise_objects = {}
    for name in keys-{'schema','parameters'}:
        ref = config[name]
        premise_objects[name] = reader.ref(ref)
        expected_inputs[ref['path']] = ref['sha256']
    need(equal(summary['inputs_sha256'],expected_inputs), 'SCIENCE_INPUT_CLOSURE')
    for label, claim_id in [('support','C-UNRESTRICTED-TARGET-PRIME5-LEFT-CODE-SUPPORT-LOWER55'),
                            ('counts','C-PRIME5-LINEAR-TRIPLE-IMAGE-WEIGHT-COUNTS')]:
        bound = premise_objects[label+'_binding']
        need(type(bound) is dict and bound.get('schema') == 'CLAIM_BINDING_SCHEMA2'
             and bound.get('id') == claim_id and type(bound.get('revision')) is int and bound['revision'] == 1
             and bound.get('status') == 'VERIFIED' and bound.get('review_state') == 'CLEAR'
             and bound.get('producer') == '/root/structural' and bound.get('verifier') == '/root/native_driver'
             and bound.get('method') == 'independent_derivation'
             and type(bound.get('scope')) is dict and bound['scope'].get('unrestricted_target') is True
             and bound['scope'].get('target_resolution') == 'NONE'
             and bound.get('report') == config[label+'_report']['path']
             and bound.get('report_sha256') == config[label+'_report']['sha256'], 'PREMISE_HEADER')
        receipt = premise_objects[label+'_acceptance']
        need(type(receipt) is dict and receipt.get('reviewer') == '/root'
             and receipt.get('claim_id') == claim_id and type(receipt.get('claim_revision')) is int
             and receipt['claim_revision'] == 1 and receipt.get('result') in
             ('PASS_WRITTEN_SCOPE_AND_BOUND_ARTIFACTS','PASS_WRITTEN_SCOPE_AND_EXACT_BINDING'), 'PREMISE_ACCEPTANCE')
    author_receipt = premise_objects['author_controls_acceptance']
    need(type(author_receipt) is dict
         and author_receipt.get('schema') == 'ROOT_PRIME5_CODE_DELSARTE_AUTHOR_CONTROLS_ACCEPTANCE_V2'
         and author_receipt.get('result') == 'PASS_ENGINEERING_ONLY'
         and equal(author_receipt.get('author_controls'),config['author_controls']), 'AUTHOR_ACCEPTANCE')
    authority = premise_objects['root_authority']
    need(type(authority) is dict and authority.get('schema') == 'ROOT_PRIME5_CODE_DELSARTE_ONE_AUTHORITY_V2'
         and authority.get('permitted_mode') == 'science'
         and equal(authority.get('source'),{'path':PRODUCER,'sha256':PRODUCER_SHA})
         and equal(authority.get('specification'),{'path':PRODUCER_SPEC,'sha256':PRODUCER_SPEC_SHA}), 'ROOT_AUTHORITY')
    control_gate = reader.ref(packet['producer_controls'])
    need(type(control_gate) is dict and control_gate.get('status') == CONTROL_STATUS
         and type(control_gate.get('implementation_version')) is int and control_gate['implementation_version'] == 1
         and control_gate.get('producer') == '/root/structural' and control_gate.get('verifier') == '/root/native_driver'
         and control_gate.get('method') == 'independent_artifact_check' and control_gate.get('target_resolution') == 'NONE'
         and equal(control_gate.get('producer_summary'),config['author_controls'])
         and type(control_gate.get('inputs_sha256')) is dict
         and all(control_gate['inputs_sha256'].get(k) == v for k,v in reader.software.items()), 'PRODUCER_CONTROL_GATE')
    control_base = safe(packet['producer_controls']['path']).parent
    need(type(control_gate.get('outputs_sha256')) is dict, 'PRODUCER_CONTROL_GATE')
    inventory(control_base,control_gate['outputs_sha256'])
    for name, sha in control_gate['inputs_sha256'].items():
        reader.raw(name,sha)
    for name, sha in control_gate['outputs_sha256'].items():
        reader.raw((control_base/name).relative_to(ROOT).as_posix(),sha)
    need(type(reader.ref(packet['producer_controls_acceptance'])) is dict, 'ROOT_RECEIPT')
    author, author_base = accepted_author(reader,config['author_controls'])
    stages = replay_author(reader,author,author_base)
    parsed = reader.ref({'path':(base/'parsed_input.json').relative_to(ROOT).as_posix(),
                        'sha256':summary['outputs_sha256'].get('parsed_input.json')})
    expected_parsed = {'parameters':parameters_expected,
        'accepted_premise_refs':{k:v for k,v in config.items() if k not in ('schema','parameters')},
        'not_used_at_degree20_or32':{'96':924,'99':2776},
        'historical_dimension27_comparison_is_not_a_new_gate':True}
    need(equal(parsed,expected_parsed), 'PARSED_INPUT')
    files, outcomes, certificates, prefix = {'parsed_input.json'}, [], [], []
    for index, (degree,label,lower) in enumerate([(20,'baseline',{}),(20,'low_image_counts',LOWER),
                                                (32,'baseline',{}),(32,'low_image_counts',LOWER)]):
        reader.tick()
        case = f'degree{degree}_{label}'
        values = {}
        for tail in ('guidance','candidate','checkpoint'):
            name = case+'_'+tail+'.json'
            files.add(name)
            need(name in summary['outputs_sha256'], 'SCIENCE_OUTPUT_POPULATION')
            values[tail] = reader.ref({'path':(base/name).relative_to(ROOT).as_posix(),
                                     'sha256':summary['outputs_sha256'][name]})
        guidance(values['guidance'],degree,45)
        checked = candidate_wrapper(values['candidate'],[5,99,55,degree,lower],reader)
        row = {'case':case,'degree':degree,'image_lower_counts_used':copy.deepcopy(lower),
            **{k:checked[k] for k in ('candidate_available','unknown_reason','code_size_upper',
                                     'integer_dimension_upper','candidate_stronger_than_historical27')}}
        need(equal(row,summary['outcome'][index]), 'SCIENCE_OUTCOME')
        outcomes.append({**row,'conclusion':checked['conclusion']})
        if checked['candidate_available']:
            name = case+'_polynomial.json'
            files.add(name)
            need(name in summary['outputs_sha256'], 'SCIENCE_OUTPUT_POPULATION')
            polynomial = reader.ref({'path':(base/name).relative_to(ROOT).as_posix(),
                                    'sha256':summary['outputs_sha256'][name]})
            value = checked['verified_certificate']
            need(equal(polynomial,{'multipliers':value['multipliers'],'values':value['polynomial_values']}),
                 'POLYNOMIAL_FILE')
            certificates.append({'case':case,'exact_certificate':value})
        prefix.append(case)
        cp = values['checkpoint']
        need(type(cp) is dict and cp.keys() == {'progress','LP_calls','deadline'}
             and equal(cp['progress'],{'completed_cases':prefix,'active_case':None,'phase':'checkpoint'})
             and type(cp['LP_calls']) is int and cp['LP_calls'] == index+1, 'SCIENCE_CHECKPOINT')
        reserve(cp['deadline'])
    need(summary['outputs_sha256'].keys() == files, 'SCIENCE_OUTPUT_POPULATION')
    reader.save('independent_certificates.json',{'schema':'INDEPENDENT_PRIME5_EXACT_CERTIFICATES_V1',
        'certificates':certificates,'complete_case_outcomes':outcomes,
        'absent_candidate_has_no_bound_or_infeasibility_conclusion':True})
    reader.save('producer_stage_pairs.json',{'schema':'INDEPENDENT_PRIME5_PRODUCER_STAGE_PAIRS_V1','rows':stages})
    return {'complete_cases':4,'exact_certificates':len(certificates),'unknown_cases':4-len(certificates),
        'support_signs_per_certificate':45,'polynomial_values_per_certificate':46,
        'all_multipliers_and_powers_exact':True,'producer_actions_rerun':31,'own_actions_rerun':0,
        'improved_bounds':sum(row['candidate_stronger_than_historical27'] for row in outcomes),
        'numerical_infeasibility_is_proof':False,'nonzero_code_forced':False,'target_matrix_or_code_enumerated':False}


def changed(raw, path, value):
    result = copy.deepcopy(raw)
    node = result
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = copy.deepcopy(value)
    return result


def root_runtime_fixture():
    raw = synthetic_runtime()
    worker = list(raw['plan']['worker_argv'])
    worker[3], worker[5] = 'science','150'
    ref = {'path':'acceleration/synthetic_q5_configuration.json','sha256':'0'*64}
    worker.extend(['--configuration',ref['path'],'--configuration-sha256',ref['sha256']])
    child = [*raw['plan']['child_argv'][:8],*worker]
    command = [*raw['plan']['command'][:16],*child]
    command[4] = '180'
    raw['plan'] = {'schema':'ROOT_PRIME5_CODE_DELSARTE_CONCRETE_SCIENCE_PLAN_V2',
        'source':{'path':PRODUCER,'sha256':PRODUCER_SHA},
        'specification':{'path':PRODUCER_SPEC,'sha256':PRODUCER_SPEC_SHA},
        'configuration':ref,'word_counts':{'supervisor':40,'child':24,'worker':16},
        'command':command,'supervisor_argv':command,'child_argv':child,'worker_argv':worker}
    raw['manifest']['command'], raw['manifest']['seconds'] = child,180
    return raw


def check_runtime_fixture(raw, mode='calibrate'):
    flags, outer = runtime(raw['plan'],raw['manifest'],raw['terminal'],raw['summary'],mode)
    return {'worker_seconds':flags['--seconds'],'outer_seconds':outer['--seconds'],
            'strict_runtime_header_checked':True}


def calibration(reader):
    cert = derive(2,3,2,1,{},['1'])
    original = list(zip(AUTHOR_NAMES,AUTHOR_EXPECTED,literal_author_actions(reader)))
    probe = reader.out/'inventory_probe'
    probe.mkdir()
    for name in ('summary.json','data.json'):
        with (probe/name).open('x',encoding='utf8',newline='\n') as stream:
            stream.write('{"fixture":"inventory"}\n')
    probe_map = {'data.json':hashlib.sha256((probe/'data.json').read_bytes()).hexdigest()}

    def nested_summary_bad():
        extra = probe/'extra'
        extra.mkdir()
        with (extra/'summary.json').open('x',encoding='utf8',newline='\n') as stream:
            stream.write('{"unlisted":true}\n')
        return inventory(probe,probe_map)

    def cert_action(path, value):
        return lambda:certificate(changed(cert,path,value))

    def runtime_action(path, value):
        return lambda:check_runtime_fixture(changed(synthetic_runtime(),path,value))

    actions = original + [
      ('zero_left_code_allowed','PASS',lambda:certificate(derive(2,3,3,3,{'3':1},['0','0','1/2']))),
      ('absent_candidate_is_unknown','PASS',lambda:candidate_wrapper(
          {'candidate':None,'unknown_reason':'NUMERICAL_GUIDE_UNKNOWN'},[5,99,55,20,{}])),
      ('actual_windows_receipt_shape','PASS',lambda:check_runtime_fixture(synthetic_runtime())),
      ('output_directory_is_string','PASS',lambda:str(safe(reader.out.as_posix(),False))),
      ('exact_base_summary_exemption','PASS',lambda:inventory(probe,probe_map)),
      ('actual_root_flat_science_shape','PASS',lambda:check_runtime_fixture(root_runtime_fixture(),'science')),
      ('extra_certificate_key','CERTIFICATE_HEADER',lambda:certificate({**cert,'extra':True})),
      ('old_certificate_schema','CERTIFICATE_HEADER',cert_action(['schema'],'OLD_CODE_CERTIFICATE')),
      ('nonzero_code_forced','CERTIFICATE_SCOPE',cert_action(['nonzero_code_forced'],True)),
      ('optimality_overclaim','CERTIFICATE_SCOPE',cert_action(['is_optimality_certificate'],True)),
      ('target_resolution_overclaim','CERTIFICATE_SCOPE',cert_action(['target_resolution'],'EXCLUDED')),
      ('first_value_changed','VALUE_TABLE',cert_action(['polynomial_values',0,'value'],'5')),
      ('last_value_changed','VALUE_TABLE',cert_action(['polynomial_values',2,'value'],'-1')),
      ('value_order_changed','VALUE_TABLE',cert_action(['polynomial_values'],list(reversed(cert['polynomial_values'])))),
      ('boolean_weight','VALUE_TABLE',cert_action(['polynomial_values',0,'weight'],False)),
      ('unreduced_value','VALUE_TABLE',cert_action(['polynomial_values',0,'value'],'8/2')),
      ('floating_value','VALUE_TABLE',cert_action(['polynomial_values',0,'value'],4.0)),
      ('bound_disagrees','BOUND_VALUE',cert_action(['code_size_upper'],'5')),
      ('bound_unreduced','FRACTION_CANONICAL',cert_action(['code_size_upper'],'8/2')),
      ('bound_boolean','FRACTION_TEXT',cert_action(['code_size_upper'],True)),
      ('boolean_dimension','DIMENSION_POWERS',cert_action(['integer_dimension_upper'],True)),
      ('boolean_lower_power','DIMENSION_POWERS',cert_action(['dimension_lower_power'],True)),
      ('float_next_power','DIMENSION_POWERS',cert_action(['dimension_next_power'],8.0)),
      ('wrong_next_power','DIMENSION_POWERS',cert_action(['dimension_next_power'],16)),
      ('negative_dimension','DIMENSION_POWERS',cert_action(['integer_dimension_upper'],-1)),
      ('absent_missing_reason','UNKNOWN_REASON',lambda:candidate_wrapper({'candidate':None,'unknown_reason':None},None)),
      ('absent_boolean_reason','UNKNOWN_REASON',lambda:candidate_wrapper({'candidate':None,'unknown_reason':True},None)),
      ('certificate_with_unknown_reason','CANDIDATE_REASON',lambda:candidate_wrapper({'candidate':cert,'unknown_reason':'unknown'},None)),
      ('wrapper_extra_field','CANDIDATE_WRAPPER',lambda:candidate_wrapper({'candidate':None,'unknown_reason':'unknown','extra':0},None)),
      ('manifest_source_changed','RUNTIME_MANIFEST',runtime_action(['manifest','source_sha256'],'0'*64)),
      ('manifest_scope_changed','RUNTIME_MANIFEST',runtime_action(['manifest','runtime_scope'],'OLD_SCOPE')),
      ('boolean_child_exit','RUNTIME_EXIT',runtime_action(['terminal','command_exit_code'],False)),
      ('unsuspended_child','RUNTIME_CLEANUP',runtime_action(['terminal','cleanup','created_suspended'],False)),
      ('nonfinite_elapsed_text','RUNTIME_ELAPSED',runtime_action(['terminal','elapsed_seconds'],'inf')),
      ('worker_source_changed','RUNTIME_SUFFIX',runtime_action(['plan','worker_argv',2],(ROOT/SELF).as_posix())),
      ('unlisted_nested_summary','OUTPUT_INVENTORY',nested_summary_bad),
      ('duplicate_json_key','DUPLICATE_KEY',lambda:json.loads('{"x":1,"x":2}',object_pairs_hook=unique)),
    ]
    need(len(actions) == 68 and sum(stage == 'PASS' for _,stage,_ in actions) == 16,
         'OWN_CONTROL_POPULATION')
    stages = []
    for index, (name, expected, action) in enumerate(actions):
        reader.tick()
        result, detail, actual = None, None, 'PASS'
        try:
            result = action()
        except Veto as exc:
            actual, detail = exc.stage, exc.detail
        row = {'index':index,'name':name,'expected':expected,'actual':actual,'detail':detail,'value':result}
        reader.save(f'control_{index:02d}.json',row)
        need(actual == expected,'CONTROL_STAGE',{'index':index,'expected':expected,'actual':actual})
        if expected == 'PASS':
            if index == 1:
                need(equal(result,[12,7,2,-3]),'HAND_EXPECTATION')
            elif index == 2:
                need(equal(result,[3,-1,-1,3]),'HAND_EXPECTATION')
            elif name == 'zero_left_code_allowed':
                need(result['code_size_upper'] == '1' and result['integer_dimension_upper'] == 0
                     and result['dimension_next_power'] == 2,'HAND_EXPECTATION')
            elif name == 'absent_candidate_is_unknown':
                need(result['conclusion'] == 'UNKNOWN' and result['code_size_upper'] is None,
                     'HAND_EXPECTATION')
            elif name == 'high_degree_full_space':
                need(result['code_size_upper'] == '23283064365386962890625'
                     and result['integer_dimension_upper'] == 32 and len(result['polynomial_values']) == 33
                     and all(row['value'] == '0' for row in result['polynomial_values'][1:]),'HAND_EXPECTATION')
        stages.append({k:v for k,v in row.items() if k != 'value'})
    reader.save('controls.json',{'schema':'INDEPENDENT_PRIME5_CODE_DELSARTE_CONTROLS_V1','rows':stages})
    return {'positive':16,'negative':52,'control_rows':68,'LP_calls':0,
        'target_parameters_read':False,'producer_literal_actions_checked':31,'own_actions_rerun':68}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',choices=('calibrate','controls','full'))
    parser.add_argument('--seconds',type=float,required=True)
    parser.add_argument('--out',required=True)
    parser.add_argument('--self-sha256',required=True)
    parser.add_argument('--spec-sha256',required=True)
    parser.add_argument('--packet')
    parser.add_argument('--packet-sha256')
    args = parser.parse_args()
    reader = Reader(args.seconds,safe(args.out,False))
    try:
        need(not reader.out.exists(),'OUTPUT_EXISTS')
        need(reader.out.resolve().is_relative_to(ROOT/'acceleration/results'),'OUTPUT_PATH')
        reader.out.mkdir(parents=True)
        for path, sha in {SELF:args.self_sha256,SPEC:args.spec_sha256,**PINS}.items():
            reader.raw(path,sha)
        reader.software = dict(reader.inputs)
        producer_ref = None
        if args.mode == 'calibrate':
            need(args.packet is None and args.packet_sha256 is None,'CALIBRATION_SCOPE')
            outcome = calibration(reader)
            status = CAL_STATUS
        else:
            need(args.packet is not None and args.packet_sha256 is not None,'PACKET_REQUIRED')
            packet = reader.ref({'path':args.packet,'sha256':args.packet_sha256})
            raw, base, flags = source_packet(reader,packet,args.mode)
            producer_ref = packet['producer_summary']
            if args.mode == 'controls':
                need(equal(raw['inputs_sha256'],PINS),'AUTHOR_SOFTWARE_CLOSURE')
                stages = replay_author(reader,raw,base)
                reader.save('producer_stage_pairs.json',{'schema':'INDEPENDENT_PRIME5_PRODUCER_STAGE_PAIRS_V1','rows':stages})
                outcome = {'positive':10,'negative':21,'producer_actions_rerun':31,
                    'own_actions_rerun':0,'tiny_numerical_guidance_objects_checked':1,'LP_calls':0,
                    'numeric_infeasibility_is_proof':False}
                status = CONTROL_STATUS
            else:
                outcome = full(reader,packet,raw,base,flags)
                status = FULL_STATUS
        reader.close_inputs()
        reader.tick()
        outputs = {p.relative_to(reader.out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(reader.out.rglob('*')) if p.is_file()}
        expected_count = 72 if args.mode == 'calibrate' else (1 if args.mode == 'controls' else 2)
        need(len(outputs) == expected_count,'CHECKER_OUTPUT_POPULATION')
        inventory(reader.out,outputs)
        reader.tick()
        summary = {'schema':'INDEPENDENT_PRIME5_CODE_DELSARTE_RUN_V1','implementation_version':1,
            'timestamp':datetime.now(timezone.utc).isoformat(),'status':status,'mode':args.mode,
            'producer':'/root/structural','verifier':'/root/native_driver','method':'independent_artifact_check',
            'source':{'path':SELF,'sha256':args.self_sha256},
            'specification':{'path':SPEC,'sha256':args.spec_sha256},'source_software':reader.software,
            'producer_summary':producer_ref,**outcome,'inputs_sha256':dict(reader.inputs),
            'outputs_sha256':outputs,'output_payload_count':len(outputs),'physical_file_count':len(outputs)+1,
            'deadline':reader.deadline.status(),'target_resolution':'NONE',
            'limitations':['Accepted mathematical premises are declared direct dependencies, not rederived here.',
                'Numerical infeasibility and absent certificates yield UNKNOWN, never exclusion.',
                'No nonzero left code, optimum, code realization or target graph is inferred.',
                'Qualified own controls are authenticated in later modes; their actions are not rerun.',
                'Producer numerical guidance is inspected without any backend call.']}
        reader.save('summary.json',summary)
        reader.tick()
        print(json.dumps({'status':status,'summary':str(reader.out/'summary.json')}))
        return 0
    except Exception as exc:
        if reader.out.is_dir() and not (reader.out/'failure.json').exists():
            with (reader.out/'failure.json').open('x',encoding='utf8',newline='\n') as stream:
                json.dump({'status':'FAILED_OR_NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET',
                    'stage':getattr(exc,'stage',None),'error':str(exc),'error_type':type(exc).__name__,
                    'detail':getattr(exc,'detail',None),'inputs_sha256':reader.inputs,
                    'deadline':reader.deadline.status(),
                    'provisional_summary_is_not_a_gate':(reader.out/'summary.json').exists()},
                    stream,allow_nan=False,ensure_ascii=False,indent=2)
                stream.write('\n')
        print(json.dumps({'error':str(exc),'error_type':type(exc).__name__}),file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())


