"""SOURCE ONLY: independent exact individual exterior-neighbor rows and copy labels."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
from pathlib import Path
import stat
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261004_fixed17_focal_neighbor_integer_v1.py'
SPEC = 'acceleration/audit_20261004_fixed17_focal_neighbor_integer_v1_spec.md'
PRODUCER = 'acceleration/solve_20261004_fixed17_focal_neighbor_integer_v1.py'
PRODUCER_SPEC = 'acceleration/solve_20261004_fixed17_focal_neighbor_integer_v1_spec.md'
CAL_STATUS = 'INDEPENDENT_FIXED17_FOCAL_NEIGHBOR_INTEGER_V1_CALIBRATION_PASS'
CONTROLS_STATUS = 'INDEPENDENT_FIXED17_FOCAL_NEIGHBOR_INTEGER_V1_PRODUCER_CONTROLS_PASS'
FULL_STATUS = 'INDEPENDENT_FIXED17_FOCAL_NEIGHBOR_INTEGER_V1_COMPLETE_PASS'
AUTHOR_COUNTS = {'positive':9,'negative':25,'total':34}
OWN_COUNTS = {'positive':17,'negative':52,'total':69}
SOFTWARE = {
    'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py':'593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
    PRODUCER:'9c0c5f607ef27134674ffff709185b8da0d83ab3502fd18a3c76cd968a1e2a6e',
    PRODUCER_SPEC:'6fa4b2a7b88de50e06d2fb40c4bb3821e79add2fa322adaf76198dc117354225',
    'acceleration/screen_20261004_fixed17_count_neighbor_capacity_v1.py':'4d737ba3b8ea90df487a1b71cbc6fe4f8baf38234533fdc9115bb76034556371',
    'acceleration/audit_20261004_fixed17_count_neighbor_capacity_v1.py':'ee985db1c2c54408b7eb18bdc997af6586d4d437ae0f9a9e8af5a56b1b91b24f',
}
AUTHOR_SOFTWARE = {k:v for k,v in SOFTWARE.items() if k != 'acceleration/audit_20261004_fixed17_count_neighbor_capacity_v1.py'}
AUTHOR_SOFTWARE.update({
    'build/research-venv/Lib/site-packages/highspy/_core/__init__.pyi':'53c07e5eafff940daa32458b20262b07d39420b062e0875c2f56e9ac92f4d699',
    'build/research-venv/Lib/site-packages/highspy/_core.cp312-win_amd64.pyd':'f733d7369f647f8afe481bbaf569164f7cd7c127e41ca53cd7c205c2fb9038e2',
    'build/research-venv/Lib/site-packages/highspy/highs.py':'00ce58ef248062125309ccdaf7af6374caf1a29f6a04e0d637b7507ead34d51a',
    'build/research-venv/Lib/site-packages/highspy/__init__.py':'01df06ec93388a45de66adb43d4b243cd7e11c54f24106064a221facf6aa7eb9',
    'build/research-venv/Lib/site-packages/highspy-1.15.1.dist-info/METADATA':'cc09b9d5bf93d8cd79be21bede4e72b686d79cdc75f6524e0e0a1af3e9487a8d',
})
TRUSTED_PROFILE = 'acceleration/results/20261004_fixed17_count_neighbor_capacity01/parsed_screen_input.json'
TRUSTED_PROFILE_SHA = '468f281bfc13a34a5c23ca2a6af9f8564954c826e0b9f7bddfad36a76832690e'
PREMISES = {
    'acceleration/results/20261004_independent_review/fixed17_count_neighbor_capacity_full01/summary.json':'4f6711cba2450262709ba0724bbd9bdbba3c95934c85265479985be7a38decb3',
    'acceleration/results/20261004_fixed17_count_neighbor_capacity_full_root_actual_acceptance01.json':'d8eaf7c2cb41a0bd8f1287b652edcbcc498b97f3475575b6e3b0d77e5d655017',
    'acceleration/results/20261004_independent_review/external_moment_integer_counts_full01/summary.json':'37bcf42a3b5e358c4306c642e152e3e605a07dc305de71b2272e455e377bd6b8',
    'acceleration/results/20261004_integer_counts_independent_full_root_actual_acceptance01.json':'3823dec446f661d87a27d2cad80b4c2f91883c786f30def4f43a25eb913bb10d',
    'acceleration/results/20261004_independent_review/fixed17_dual_gram_pairs_full02/summary.json':'ee9fa8961415df0e5f0ca429c33fc95a1d6223b77ec68e2c9ec71cc1dec0e218',
    'acceleration/results/20261004_fixed17_dual_gram_pairs_checker_root_actual_full_acceptance02.json':'39a904ee2ec0bdb4b1a28678c1842794d2abe7d05150879517265a6e7f797586',
    'acceleration/results/20261004_independent_review/target_exterior_type_edge_moments01/summary.json':'910a740aff6ecd90515af7de0a2743abab47eabe902274237b3b70e1d0fdc6d6',
    'acceleration/results/20261004_fixed17_integer_type_counts01/exact_integer_candidate.json':'133097b6174aa1a4b1d327b5c72a727f8ad1ac6daeef0654b117a5f8b88de5b5',
    'acceleration/results/20261004_fixed17_integer_type_counts01/parsed_fixed_input.json':'cfe5003a2bd0ad4b2b979264c6e6d1648dc3cd67d1ebc03226d44998371b1248',
}
# Engineering reader/runtime ancestry is copied explicitly, never imported.
class Veto(ValueError):
    pass

def need(ok, stage):
    if not ok:
        raise Veto(stage)

def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b

def decode(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'JSON_DUPLICATE')
            result[k] = v
        return result
    def constant(_):
        raise Veto('JSON_NONFINITE')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise Veto('JSON_SYNTAX') from None

class Budget:
    def __init__(self, seconds):
        self.deadline = CommandDeadline(seconds, allocation_reason=
            'Independent exact focal row/vector checking; all authentication and saves share the allocation')
    def tick(self):
        s = self.deadline.status()
        need(not s['stop_required'] and s['remaining_seconds'] > 20, 'SAVE_RESERVE')
        return s

def safe(name, exists=True):
    p = Path(name)
    p = p if p.is_absolute() else ROOT / p
    need(p.resolve().is_relative_to(ROOT), 'PATH_SCOPE')
    for component in (p, *p.parents):
        if component == ROOT.parent:
            break
        if component.exists():
            flags = getattr(component.lstat(), 'st_file_attributes', 0)
            need(not component.is_symlink() and not (flags & stat.FILE_ATTRIBUTE_REPARSE_POINT), 'PATH_REPARSE')
    if exists:
        need(p.is_file(), 'INPUT_FILE')
    return p

class Reader:
    def __init__(self, budget):
        self.budget = budget
        self.pins = {}
    def read(self, name, digest, parse=True):
        self.budget.tick()
        p = safe(name)
        need(type(digest) is str and len(digest) == 64 and
             all(c in '0123456789abcdef' for c in digest), 'HASH_SCHEMA')
        limit = 64 * 1024**2
        need(p.stat().st_size <= limit, 'INPUT_SIZE')
        h, chunks, size = hashlib.sha256(), [], 0
        with p.open('rb') as f:
            while True:
                self.budget.tick()
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                need(size <= limit, 'INPUT_SIZE')
                h.update(chunk)
                if parse:
                    chunks.append(chunk)
        need(h.hexdigest() == digest, 'INPUT_HASH')
        key = p.relative_to(ROOT).as_posix()
        need(key not in self.pins or self.pins[key] == digest, 'PIN_CONFLICT')
        self.pins[key] = digest
        self.budget.tick()
        return decode(b''.join(chunks)) if parse else None
    def map(self, identities):
        need(type(identities) is dict and identities, 'INPUT_MAP')
        for name, digest in sorted(identities.items()):
            self.read(name, digest, False)
    def closing(self):
        self.map(dict(self.pins))

def write(path, obj, budget):
    budget.tick()
    with path.open('x', encoding='utf8', newline='\n') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')
    budget.tick()

def inventory(base, budget):
    result = set()
    for p in base.rglob('*'):
        budget.tick()
        if p.is_dir():
            safe(p,False)
        else:
            safe(p)
            result.add(p.relative_to(base).as_posix())
    return result

def packet(reader, path, digest):
    summary = reader.read(path,digest)
    need(type(summary) is dict, 'REPORT_SCHEMA')
    base = safe(path).parent
    outputs = summary.get('outputs_sha256')
    need(type(outputs) is dict and outputs and all(type(k) is str and type(v) is str for k,v in outputs.items()),
         'OUTPUT_MAP')
    need('summary.json' not in outputs and inventory(base,reader.budget) == set(outputs)|{'summary.json'},
         'OUTPUT_POPULATION')
    for name,digest in outputs.items():
        destination = base/name
        need(destination.resolve().is_relative_to(base) and destination != base, 'OUTPUT_PATH')
        reader.read(destination,digest,False)
    return summary,base


def options(words):
    need(type(words) is list and len(words)%2 == 0, 'ARGV_PAIRS')
    result = {}
    for key,value in zip(words[::2],words[1::2]):
        need(type(key) is str and key.startswith('--') and key not in result and type(value) is str,
             'ARGV_OPTION')
        result[key] = value
    return result

def runtime(plan, manifest, terminal, summary, mode, source):
    command,child,worker = (plan.get(k) for k in ('command','child_argv','worker_argv'))
    need(type(command) is list and type(child) is list and type(worker) is list and '--' in command, 'RUNTIME_PLAN')
    split = command.index('--')
    need(same(command[split+1:],child) and same(child[8:],worker), 'RUNTIME_SUFFIX')
    need(len(worker) == (14 if mode == 'calibrate' else 18) and worker[1] == '-B'
         and safe(worker[2]) == ROOT/PRODUCER and worker[3] == mode, 'RUNTIME_WORKER')
    need(safe(command[2]) == ROOT/'acceleration/run_compute_command.py', 'RUNTIME_SUPERVISOR')
    outer,flags = options(command[3:split]),options(worker[4:])
    need(flags.get('--self-sha256') == source['source'] and flags.get('--spec-sha256') == source['spec']
         and flags.get('--executor') in ('/root','/root/checkpoint_audit'), 'RUNTIME_SOURCE')
    need(same(manifest.get('command'),child) and manifest.get('source_sha256') ==
         SOFTWARE['acceleration/run_compute_command.py'] and type(manifest.get('schema_version')) is int and
         manifest['schema_version'] == 1 and manifest.get('process_scope') ==
         'Local non-escaping process tree only; remote/daemonized compute is unsupported' and
         manifest.get('cumulative_across_commands') is False and manifest.get('automatic_retry') is False and
         Path(manifest.get('cwd','')).resolve() == ROOT, 'RUNTIME_MANIFEST')
    for key in ('seconds','shutdown_reserve_seconds'):
        name = '--seconds' if key == 'seconds' else '--shutdown-reserve-seconds'
        need(type(manifest.get(key)) in (int,float) and math.isfinite(manifest[key]) and
             manifest[key] == float(outer[name]), 'RUNTIME_ALLOCATION')
    need(type(terminal.get('command_exit_code')) is int and terminal['command_exit_code'] == 0 and
         terminal.get('error') is None and terminal.get('deadline_reached') is False, 'RUNTIME_EXIT')
    cleanup = terminal.get('cleanup')
    need(type(cleanup) is dict and type(cleanup.get('actual_exit_code')) is int and cleanup['actual_exit_code'] == 0
         and all(cleanup.get(k) is True for k in ('created_suspended','resumed','reaped','job_active_zero_observed'))
         and cleanup.get('cleanup_errors') == [], 'RUNTIME_CLEANUP')
    need(type(manifest.get('invocation_id')) is str and manifest['invocation_id'] and
         terminal.get('invocation_id') == manifest['invocation_id'], 'RUNTIME_INVOCATION')
    elapsed = terminal.get('elapsed_seconds')
    need(type(elapsed) in (int,float) and math.isfinite(elapsed) and 0 <= elapsed <= manifest['seconds'], 'RUNTIME_ELAPSED')
    need(same(summary.get('command'),worker[2:]) and Path(summary.get('cwd','')).resolve() == ROOT,
         'RUNTIME_SUMMARY_COMMAND')
    need(summary.get('executor_declaration') == flags['--executor'] and
         summary.get('executor_identity_requires_external_runtime_receipt') is True, 'RUNTIME_EXECUTOR')
    status = summary.get('deadline')
    need(type(status) is dict and status.get('stop_required') is False and
         type(status.get('remaining_seconds')) in (int,float) and math.isfinite(status['remaining_seconds']) and
         status['remaining_seconds'] > 20, 'RUNTIME_WORKER_DEADLINE')
    return flags

def synthetic_runtime():
    worker = [str(ROOT/'build/research-venv/Scripts/python.exe'),'-B',str(ROOT/PRODUCER),'calibrate',
        '--seconds','100','--out',str(ROOT/'acceleration/results/synthetic_integer_controls'),
        '--self-sha256','pin','--spec-sha256','pin','--executor','/root']
    child = ['uv','run','--locked','--offline','--no-sync','--python',worker[0],'--',*worker]
    command = [worker[0],'-B',str(ROOT/'acceleration/run_compute_command.py'),'--seconds','120',
        '--shutdown-reserve-seconds','20','--out','synthetic_supervision','--allocation-reason','synthetic',
        '--success-criterion','synthetic','--verification-requirement','synthetic','--',*child]
    manifest = {'command':child,'source_sha256':SOFTWARE['acceleration/run_compute_command.py'],
        'schema_version':1,'process_scope':'Local non-escaping process tree only; remote/daemonized compute is unsupported',
        'cumulative_across_commands':False,'automatic_retry':False,'cwd':str(ROOT),'seconds':120,
        'shutdown_reserve_seconds':20,'invocation_id':'synthetic_integer'}
    terminal = {'command_exit_code':0,'error':None,'deadline_reached':False,'elapsed_seconds':1,
        'invocation_id':'synthetic_integer','cleanup':{'actual_exit_code':0,'created_suspended':True,
            'resumed':True,'reaped':True,'job_active_zero_observed':True,'cleanup_errors':[]}}
    summary = {'command':worker[2:],'cwd':str(ROOT),'executor_declaration':'/root',
        'executor_identity_requires_external_runtime_receipt':True,
        'deadline':{'stop_required':False,'remaining_seconds':90}}
    return {'plan':{'command':command,'child_argv':child,'worker_argv':worker},
            'manifest':manifest,'terminal':terminal,'summary':summary}


def reserve(raw):
    need(type(raw) is dict and raw.get('stop_required') is False and
         type(raw.get('remaining_seconds')) in (int,float) and math.isfinite(raw['remaining_seconds'])
         and raw['remaining_seconds'] > 20, 'SAVE_RESERVE')
    return raw


def runtime_profile(plan, mode):
    need(type(plan) is dict, 'RUNTIME_PLAN_SCHEMA')
    schema = plan.get('schema')
    if schema == 'FIXED17_FOCAL_NEIGHBOR_INTEGER_SOURCE_ONLY_PLAN_V1':
        need(mode == 'calibrate', 'RUNTIME_PLAN_SCHEMA')
        value = plan.get('calibration')
    elif schema == 'ROOT_CONCRETE_FOCAL_NEIGHBOR_AUTHOR_CALIBRATION_V1':
        need(mode == 'calibrate', 'RUNTIME_PLAN_SCHEMA')
        value = plan
    elif schema == 'FIXED17_FOCAL_NEIGHBOR_INTEGER_CONCRETE_PLAN_V1':
        need(mode == 'solve', 'RUNTIME_PLAN_SCHEMA')
        value = plan.get('solve')
        need(type(value) is dict and all(same(plan.get(k),value.get(k)) for k in
             ('command','supervisor_argv','child_argv','worker_argv','allocation')), 'RUNTIME_PLAN_ALIASES')
    else:
        raise Veto('RUNTIME_PLAN_SCHEMA')
    need(type(value) is dict, 'RUNTIME_PLAN_PROFILE')
    return value


def profile(raw,budget=None):
    need(type(raw) is dict and set(raw)=={'target_order','target_degree','support_adjacency',
         'ordered_masks','counts','pair_bits'},'PROFILE_FIELDS')
    v,k,h=raw['target_order'],raw['target_degree'],raw['support_adjacency']
    need(type(v) is int and type(k) is int and 0<=k<v,'TARGET_INTEGER')
    need(type(h) is list and 4<=len(h)<=17 and
         all(type(row) is list and len(row)==len(h) for row in h),'GRAPH_SHAPE')
    m=len(h)
    need(v>m and all(type(x) is int and x in (0,1) for row in h for x in row) and
         all(h[u][u]==0 and h[u][w]==h[w][u] for u in range(m) for w in range(m)),'GRAPH_DOMAIN')
    masks,counts=raw['ordered_masks'],raw['counts']
    need(type(masks) is list and masks and all(type(t) is int and 0<=t<1<<m for t in masks),'TYPE_MASK_INTEGER')
    need(masks==sorted(set(masks)),'TYPE_MASK_ORDER')
    need(type(counts) is list and len(counts)==len(masks),'COUNT_SHAPE')
    need(all(type(x) is int for x in counts),'COUNT_INTEGER')
    need(all(0<=x<=v-m for x in counts),'COUNT_BOUND')
    need(sum(counts)==v-m,'COUNT_SUM')
    table=raw['pair_bits'];n=len(masks)
    need(type(table) is list and len(table)==n*(n+1)//2,'PAIR_POPULATION')
    bits={};at=0
    for i in range(n):
        if budget is not None:budget.tick()
        for j in range(i,n):
            item=table[at];at+=1
            need(type(item) is dict and set(item)=={'i','j','bits'},'PAIR_KEYS')
            need(type(item['i']) is int and type(item['j']) is int and item['i']==i and item['j']==j,'PAIR_COORDINATES')
            value=item['bits']
            need(type(value) is list and all(type(a) is int and a in (0,1) for a in value) and
                 value==sorted(set(value)),'PAIR_BITS')
            bits[i,j]=value
    for (i,j),value in bits.items():
        if not value and counts[i] and counts[j]:
            need(i==j,'INCOMPATIBLE_COEXISTENCE');need(counts[i]<=1,'EQUAL_MULTIPLICITY')
    return h,[{u for u in range(m) if t&(1<<u)} for t in masks],counts,bits


def reconstruct(raw,focal,budget,parsed=None):
    h,sets,counts,bits=profile(raw,budget) if parsed is None else parsed;n=len(counts);m=len(h)
    need(type(focal) is int and 0<=focal<n,'FOCAL_INDEX');need(counts[focal]>0,'FOCAL_POSITIVE')
    neighbors=[{w for w in range(m) if h[u][w]} for u in range(m)]
    selected=sets[focal];capacities=[];lower=[];upper=[]
    for j,number in enumerate(counts):
        budget.tick();capacity=number-(1 if j==focal else 0);allowed=bits[min(j,focal),max(j,focal)]
        capacities.append(capacity);lower.append(capacity if allowed==[1] else 0)
        upper.append(capacity if 1 in allowed else 0)
    degree=raw['target_degree']-len(selected)
    b=[2-(1 if u in selected else 0)-len(neighbors[u]&selected) for u in range(m)]
    rows=[{'kind':'degree','coordinate':None,'rhs':degree,'coefficients':[1]*n}]
    for u in range(m):
        rows.append({'kind':'support_coordinate','coordinate':u,'rhs':b[u],
                     'coefficients':[1 if u in s else 0 for s in sets]})
    return {'schema':'FIXED17_FOCAL_NEIGHBOR_INTEGER_MODEL_V1','focal_type':focal,'focal_label':[focal,0],
            'ordered_masks':raw['ordered_masks'],'count_vector':counts,'copy_capacities':capacities,
            'variables':n,'support_size':m,'lower':lower,'upper':upper,'rows':rows,
            'required_outside_degree':degree,'required_support_incidences':b,
            'same_type_neighbor_profiles_not_assumed':True,'uniform_profiles':False}


def bounds(model):
    low,high=model['lower'],model['upper'];r=model['required_outside_degree']
    if r<sum(low):return {'stage':'MANDATORY_BOUND','rhs':r,'minimum':sum(low),'maximum':sum(high),'row':0}
    if not 0<=r<=sum(high):return {'stage':'CAPACITY_BOUND','rhs':r,'minimum':sum(low),'maximum':sum(high),'row':0}
    for i,row in enumerate(model['rows'][1:],1):
        lo=sum(low[j] for j,c in enumerate(row['coefficients']) if c)
        hi=sum(high[j] for j,c in enumerate(row['coefficients']) if c)
        if not lo<=row['rhs']<=hi:
            return {'stage':'COORDINATE_BOUND','rhs':row['rhs'],'minimum':lo,'maximum':hi,'row':i}
    return None


def values_checked(model,values,budget):
    need(type(values) is list and len(values)==model['variables'],'NEIGHBOR_SHAPE')
    need(all(type(x) is int for x in values),'NEIGHBOR_INTEGER')
    need(all(x>=0 for x in values),'NEIGHBOR_NONNEGATIVE')
    need(all(model['lower'][j]<=x<=model['upper'][j] for j,x in enumerate(values)),'NEIGHBOR_BOUND')
    rows=[]
    for i,row in enumerate(model['rows']):
        budget.tick();lhs=0
        for j,c in enumerate(row['coefficients']):lhs+=c*values[j]
        need(lhs==row['rhs'],'NEIGHBOR_DEGREE' if i==0 else 'NEIGHBOR_COORDINATE')
        rows.append({'index':i,'kind':row['kind'],'coordinate':row['coordinate'],'lhs':lhs,'rhs':row['rhs'],'exact':True})
    return rows


def labels_checked(model,values,labels,budget):
    need(type(labels) is list and all(type(p) is list and len(p)==2 for p in labels),'LABEL_SHAPE')
    need(all(type(x) is int for p in labels for x in p),'LABEL_INTEGER')
    need(model['focal_label'] not in labels,'LABEL_SELF')
    need(labels==sorted(labels) and len({tuple(p) for p in labels})==len(labels),'LABEL_ORDER')
    need(all(0<=j<model['variables'] and 0<=c<model['count_vector'][j] for j,c in labels),'LABEL_CAPACITY')
    need(len(labels)==model['required_outside_degree'],'LABEL_DEGREE')
    aggregate=[0]*model['variables']
    for j,c in labels:budget.tick();aggregate[j]+=1
    need(same(aggregate,values),'LABEL_AGGREGATION');values_checked(model,aggregate,budget)
    return {'chosen_labels':labels,'binary_labeled_neighbor_choice':True,'selected_count':len(labels),'self_excluded':True}


def selected_labels(model,values):
    return [[j,c] for j,x in enumerate(values) for c in range(1 if j==model['focal_type'] else 0,
             x+(1 if j==model['focal_type'] else 0))]


def extraction(model,guidance,budget):
    xs=guidance.get('col_value')
    need(type(xs) is list and all(type(x) is float and math.isfinite(x) for x in xs),'NUMERIC_VECTOR')
    need(type(guidance.get('solution_value_valid')) is bool,'NUMERIC_VALID_FLAG')
    if not guidance['solution_value_valid'] or len(xs)!=model['variables']:
        return {'candidate':None,'reason':'No complete value-valid numerical incumbent','numeric_infeasibility_is_proof':False}
    rounded=[round(x) for x in xs];distance=max((abs(x-y) for x,y in zip(xs,rounded)),default=0)
    if distance>1e-7:return {'candidate':None,'reason':'Coordinate exceeds declared extraction tolerance',
                           'maximum_distance':distance,'numeric_infeasibility_is_proof':False}
    try:rows=values_checked(model,rounded,budget)
    except Veto as exc:
        if str(exc)=='SAVE_RESERVE':raise
        return {'candidate':None,'reason':'Exact extraction rejected: '+str(exc),'rounded_values':rounded,
                'maximum_distance':distance,'numeric_infeasibility_is_proof':False}
    return {'candidate':rounded,'rows':rows,'maximum_distance':distance,'exact_constraints':True,
            'independent_approval':False,'graph_completion':False}


def guidance_checked(raw,model,budget,maximum):
    need(type(raw) is dict and raw.get('schema')=='FIXED17_FOCAL_NEIGHBOR_NUMERIC_GUIDANCE_V1' and
         raw.get('native_version')=='1.15.1' and type(raw.get('solver_calls')) is int and raw['solver_calls']==1 and
         raw.get('objective_all_zero') is True and raw.get('floating_status_is_proof') is False and
         raw.get('numeric_infeasibility_is_proof') is False,'GUIDANCE_HEADER')
    extraction(model,raw,budget)
    need(same(raw.get('col_value_float_hex'),[x.hex() for x in raw['col_value']]),'GUIDANCE_HEX')
    elapsed=raw.get('wall_seconds')
    need(type(elapsed) in (int,float) and math.isfinite(elapsed) and elapsed>=0,'GUIDANCE_ELAPSED')
    options=raw.get('options');need(type(options) is dict,'GUIDANCE_OPTIONS')
    expected={'threads':1,'parallel':'off','random_seed':0,'mip_rel_gap':0.0,
              'mip_abs_gap':0.0,'primal_feasibility_tolerance':1e-7,'mip_feasibility_tolerance':1e-7}
    need(all(same(options.get(k),v) for k,v in expected.items()),'GUIDANCE_OPTIONS')
    limit=options.get('time_limit')
    need(type(limit) in (int,float) and math.isfinite(limit) and 0<limit<=maximum,'GUIDANCE_TIME_LIMIT')
    return float(elapsed)


def saved_focal(raw,focal,model,decision,guidance,witness,budget,expected_model=None):
    need(type(model) is dict and same(model,reconstruct(raw,focal,budget) if expected_model is None else expected_model),
         'MODEL_RECONSTRUCTION')
    bound=bounds(model)
    if bound is not None:
        expected={'candidate':None,'exact_simple_bound':bound,
                  'reason':'A directly reconstructed necessary bound fails; independent replay required',
                  'numeric_infeasibility_is_proof':False}
        status='CANDIDATE_EXACT_SIMPLE_BOUND_FAILURE';gp=wp=None
        need(guidance is None and witness is None,'BOUND_PAYLOAD_POPULATION')
    else:
        need(type(guidance) is dict,'GUIDANCE_MISSING');expected=extraction(model,guidance,budget)
        gp='type_%03d_guidance.json'%focal;wp=None
        status='UNKNOWN_NO_EXACT_LOCAL_NEIGHBOR_VECTOR'
        if expected['candidate'] is not None:
            values=expected['candidate'];labels=selected_labels(model,values)
            rebuilt={'schema':'FIXED17_EXACT_FOCAL_NEIGHBOR_VECTOR_V1','focal_type':focal,'focal_label':[focal,0],
                     'ordered_masks':raw['ordered_masks'],'neighbor_counts':values,
                     **labels_checked(model,values,labels,budget),'exact_rows':expected['rows'],
                     'exact_constraints':True,'independent_approval':False,'graph_completion':False,
                     'same_type_uniform_profile_claimed':False}
            need(same(witness,rebuilt),'EXACT_WITNESS');status='CANDIDATE_EXACT_LOCAL_NEIGHBOR_CHOICE'
            wp='type_%03d_witness.json'%focal
        else:need(witness is None,'UNKNOWN_WITNESS_POPULATION')
    expected.update(focal_type=focal,status=status,guidance_path=gp,witness_path=wp,
                    graph_completion=False,infeasibility_from_numeric_status=False)
    need(same(decision,expected),'DECISION_RECORD')
    return {'focal_type':focal,'status':status,'witness_path':wp,'guidance_path':gp}


def allowance(raw,maximum=10,reserve_seconds=180):
    remaining=reserve(raw)['remaining_seconds']
    need(type(maximum) in (int,float) and math.isfinite(maximum) and 0<maximum<=10,'SOLVER_MAXIMUM')
    need(type(reserve_seconds) is int and reserve_seconds in (30,180),'SOLVER_RESERVE_POLICY')
    value=min(float(maximum),remaining-reserve_seconds);need(value>0,'SOLVER_RESERVE');return value


AUTHOR_ROUTES=(
 ('known_rook_all_five_free_choices','PASS'),('known_rook_all_five_forced_choices','PASS'),
 ('two_same_type_copies_exclude_self_zero_degree','PASS'),('aggregate_lifts_to_distinct_binary_copy_slots','PASS'),
 ('numeric_absent_is_not_an_infeasibility_proof','PASS'),('budget_above_reserve','PASS'),
 ('tiny_integer_0','PASS'),('tiny_integer_1','PASS'),('tiny_integer_2','PASS'),
 ('count_bool','COUNT_INTEGER'),('count_float','COUNT_INTEGER'),('count_sum','COUNT_SUM'),
 ('mask_bool','TYPE_MASK_INTEGER'),('mask_order','TYPE_MASK_ORDER'),('graph_bool','GRAPH_DOMAIN'),
 ('pair_label_bool','PAIR_COORDINATES'),('pair_bits_bool','PAIR_BITS'),('pair_missing','PAIR_POPULATION'),
 ('pair_incompatible_coexistence','INCOMPATIBLE_COEXISTENCE'),('focal_bool','FOCAL_INDEX'),
 ('focal_absent','FOCAL_POSITIVE'),('neighbor_bool','NEIGHBOR_INTEGER'),('neighbor_float','NEIGHBOR_INTEGER'),
 ('neighbor_negative','NEIGHBOR_NONNEGATIVE'),('neighbor_above_capacity','NEIGHBOR_BOUND'),
 ('mandatory_pair_one_not_selected','NEIGHBOR_BOUND'),('neighbor_wrong_degree','NEIGHBOR_DEGREE'),
 ('neighbor_wrong_coordinate','NEIGHBOR_COORDINATE'),('chosen_label_bool','LABEL_INTEGER'),
 ('chosen_label_self','LABEL_SELF'),('chosen_label_missing','LABEL_DEGREE'),
 ('budget_at_reserve','SAVE_RESERVE'),('budget_stop','SAVE_RESERVE'),('solver_closing_reserve','SOLVER_RESERVE'))


def rook_fixture(forced=False):
    outside_edges={(0,1),(0,2),(0,3),(0,4),(1,4),(2,3)}
    return {'target_order':9,'target_degree':4,
            'support_adjacency':[[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]],
            'ordered_masks':[0,3,5,10,12],'counts':[1]*5,
            'pair_bits':[{'i':i,'j':j,'bits':[int((i,j) in outside_edges)] if forced and i!=j else [0,1]}
                         for i in range(5) for j in range(i,5)]}


def witness_action(payload,budget):
    model=reconstruct(payload['packet'],payload['focal'],budget);values=payload['values']
    return {'model':model,'values':values,'rows':values_checked(model,values,budget),
            'labels':labels_checked(model,values,selected_labels(model,values),budget)}


def tiny_model(case):
    rows=[{'kind':'degree','coordinate':None,'rhs':1,'coefficients':[1,1]},
          {'kind':'support_coordinate','coordinate':0,'rhs':1,'coefficients':[1,0]}]
    if case==0:return {'variables':2,'lower':[0,0],'upper':[1,1],'rows':rows}
    return {'variables':1,'lower':[1 if case==2 else 0],'upper':[1],
            'rows':[{'kind':'degree','coordinate':None,'rhs':1,'coefficients':[1 if case==2 else 2]}]}


def tiny_exhaustive(payload,case,budget):
    need(same(payload,tiny_model(case)),'TINY_MODEL');accepted=[]
    for values in itertools.product((0,1),repeat=payload['variables']):
        try:values_checked(payload,list(values),budget);accepted.append(list(values))
        except Veto as exc:
            if str(exc)=='SAVE_RESERVE':raise
    need(accepted==([[1,0]] if case==0 else [[1]] if case==2 else []),'TINY_INTEGER_ENUMERATION')
    return {'complete_binary_candidates':2**payload['variables'],'accepted':accepted,'solver_calls':0}


def author_action(name,payload,budget):
    if name.startswith('known_rook_all_five'):
        edges={(0,1),(0,2),(0,3),(0,4),(1,4),(2,3)};results=[]
        for i in range(5):
            values=[int(i!=j and tuple(sorted((i,j))) in edges) for j in range(5)]
            results.append(witness_action({'packet':payload,'focal':i,'values':values},budget))
        return {'results':results,'complete_actual_rook_exterior_choices':5}
    if name.startswith('tiny_integer_'):return tiny_exhaustive(payload,int(name[-1]),budget)
    if name=='numeric_absent_is_not_an_infeasibility_proof':
        return extraction(reconstruct(rook_fixture(),1,budget),payload,budget)
    if name=='solver_closing_reserve':return allowance(payload)
    if name.startswith('budget_'):return reserve(payload)
    if name=='aggregate_lifts_to_distinct_binary_copy_slots' or name.startswith('chosen_label_'):
        model=reconstruct(payload['packet'],payload['focal'],budget)
        return labels_checked(model,payload['values'],payload['labels'],budget)
    result=witness_action(payload,budget)
    if name=='two_same_type_copies_exclude_self_zero_degree':
        need(result['model']['copy_capacities']==[1] and result['labels']['chosen_labels']==[],'SELF_CAPACITY_CONTROL')
    return result


def own_routes(budget,out):
    free,forced=rook_fixture(),rook_fixture(True)
    repeated={'target_order':6,'target_degree':4,'support_adjacency':[[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]],
              'ordered_masks':[15],'counts':[2],'pair_bits':[{'i':0,'j':0,'bits':[0]}]}
    base={'packet':free,'focal':1,'values':[1,0,0,0,1]}
    payloads=[free,forced,{'packet':repeated,'focal':0,'values':[0]},
              {**base,'labels':[[0,0],[4,0]]},{'solution_value_valid':False,'col_value':[]},
              {'stop_required':False,'remaining_seconds':20.000001},*[tiny_model(i) for i in range(3)]]
    routes=[(name,stage,p,lambda p,n=name:author_action(n,p,budget))
            for (name,stage),p in zip(AUTHOR_ROUTES[:9],payloads)]
    def mutation(name,stage,original,change,action=None):
        p=copy.deepcopy(original);change(p)
        routes.append((name,stage,p,action or (lambda p,n=name:author_action(n,p,budget))))
    for name,key,value in [('count_bool','counts',True),('count_float','counts',1.0),('count_sum','counts',0),
                            ('mask_bool','ordered_masks',False)]:
        mutation(name,dict(AUTHOR_ROUTES)[name],base,lambda p,k=key,v=value:p['packet'][k].__setitem__(0,v))
    mutation('mask_order','TYPE_MASK_ORDER',base,lambda p:p['packet']['ordered_masks'].reverse())
    mutation('graph_bool','GRAPH_DOMAIN',base,lambda p:p['packet']['support_adjacency'][0].__setitem__(0,False))
    mutation('pair_label_bool','PAIR_COORDINATES',base,lambda p:p['packet']['pair_bits'][0].__setitem__('i',False))
    mutation('pair_bits_bool','PAIR_BITS',base,lambda p:p['packet']['pair_bits'][0].__setitem__('bits',[False,1]))
    mutation('pair_missing','PAIR_POPULATION',base,lambda p:p['packet']['pair_bits'].pop())
    mutation('pair_incompatible_coexistence','INCOMPATIBLE_COEXISTENCE',base,
             lambda p:p['packet']['pair_bits'][1].__setitem__('bits',[]))
    mutation('focal_bool','FOCAL_INDEX',base,lambda p:p.__setitem__('focal',True))
    def absent(p):p['focal']=0;p['packet']['counts']=[0,2,1,1,1]
    mutation('focal_absent','FOCAL_POSITIVE',base,absent)
    for name,value,stage in [('neighbor_bool',True,'NEIGHBOR_INTEGER'),('neighbor_float',1.0,'NEIGHBOR_INTEGER'),
                             ('neighbor_negative',-1,'NEIGHBOR_NONNEGATIVE'),('neighbor_above_capacity',2,'NEIGHBOR_BOUND')]:
        mutation(name,stage,base,lambda p,v=value:p['values'].__setitem__(0,v))
    mutation('mandatory_pair_one_not_selected','NEIGHBOR_BOUND',{**base,'packet':forced},lambda p:p['values'].__setitem__(4,0))
    mutation('neighbor_wrong_degree','NEIGHBOR_DEGREE',base,lambda p:p['values'].__setitem__(4,0))
    mutation('neighbor_wrong_coordinate','NEIGHBOR_COORDINATE',base,lambda p:p.__setitem__('values',[1,0,1,0,0]))
    labelbase={**base,'labels':[[0,0],[4,0]]}
    mutation('chosen_label_bool','LABEL_INTEGER',labelbase,lambda p:p['labels'][0].__setitem__(0,False))
    mutation('chosen_label_self','LABEL_SELF',labelbase,lambda p:p.__setitem__('labels',[[1,0],[4,0]]))
    mutation('chosen_label_missing','LABEL_DEGREE',labelbase,lambda p:p['labels'].pop())
    for name,stage,p in [('budget_at_reserve','SAVE_RESERVE',{'stop_required':False,'remaining_seconds':20}),
                         ('budget_stop','SAVE_RESERVE',{'stop_required':True,'remaining_seconds':100}),
                         ('solver_closing_reserve','SOLVER_RESERVE',{'stop_required':False,'remaining_seconds':180})]:
        routes.append((name,stage,p,lambda p,n=name:author_action(n,p,budget)))
    need([(n,s) for n,s,p,a in routes]==list(AUTHOR_ROUTES),'OWN_AUTHOR_ROUTES')
    model=reconstruct(free,1,budget);values=base['values']
    guidance={'schema':'FIXED17_FOCAL_NEIGHBOR_NUMERIC_GUIDANCE_V1','native_version':'1.15.1',
              'solver_calls':1,'objective_all_zero':True,'floating_status_is_proof':False,
              'numeric_infeasibility_is_proof':False,'solution_value_valid':True,'col_value':[float(x) for x in values],
              'col_value_float_hex':[float(x).hex() for x in values],'wall_seconds':0.0,
              'options':{'threads':1,'parallel':'off','random_seed':0,'mip_rel_gap':0.0,'mip_abs_gap':0.0,
                         'primal_feasibility_tolerance':1e-7,'mip_feasibility_tolerance':1e-7,'time_limit':5.0}}
    extracted=extraction(model,guidance,budget);labels=selected_labels(model,values)
    witness={'schema':'FIXED17_EXACT_FOCAL_NEIGHBOR_VECTOR_V1','focal_type':1,'focal_label':[1,0],
             'ordered_masks':free['ordered_masks'],'neighbor_counts':values,**labels_checked(model,values,labels,budget),
             'exact_rows':extracted['rows'],'exact_constraints':True,'independent_approval':False,
             'graph_completion':False,'same_type_uniform_profile_claimed':False}
    decision={**extracted,'focal_type':1,'status':'CANDIDATE_EXACT_LOCAL_NEIGHBOR_CHOICE',
              'guidance_path':'type_001_guidance.json','witness_path':'type_001_witness.json',
              'graph_completion':False,'infeasibility_from_numeric_status':False}
    case={'packet':free,'focal':1,'model':model,'decision':decision,'guidance':guidance,'witness':witness}
    def casecheck(p):
        guidance_checked(p['guidance'],p['model'],budget,5)
        return saved_focal(p['packet'],p['focal'],p['model'],p['decision'],p['guidance'],p['witness'],budget)
    boundcase={'lower':[1],'upper':[1],'required_outside_degree':0,
               'rows':[{'kind':'degree','coordinate':None,'rhs':0,'coefficients':[1]}]}
    def boundcheck(p):
        need(same(bounds(p['model']),p['expected']),'BOUND_CONTROL')
        if 'saved_case' in p:
            q=p['saved_case'];saved_focal(q['packet'],q['focal'],q['model'],q['decision'],None,None,budget)
    boundfixtures=[{'model':boundcase,'expected':{'stage':'MANDATORY_BOUND','rhs':0,'minimum':1,'maximum':1,'row':0}},
        {'model':{'lower':[0],'upper':[0],'required_outside_degree':1,
                  'rows':[{'kind':'degree','coordinate':None,'rhs':1,'coefficients':[1]}]},
         'expected':{'stage':'CAPACITY_BOUND','rhs':1,'minimum':0,'maximum':0,'row':0}},
        {'model':{'lower':[0],'upper':[1],'required_outside_degree':1,
                  'rows':[{'kind':'degree','coordinate':None,'rhs':1,'coefficients':[1]},
                          {'kind':'support_coordinate','coordinate':0,'rhs':2,'coefficients':[1]}]},
         'expected':{'stage':'COORDINATE_BOUND','rhs':2,'minimum':0,'maximum':1,'row':1}}]
    badprofile=rook_fixture()
    for pair in badprofile['pair_bits']:
        if 1 in (pair['i'],pair['j']):pair['bits']=[1]
    badmodel=reconstruct(badprofile,1,budget)
    baddecision={'candidate':None,'exact_simple_bound':{'stage':'MANDATORY_BOUND','rhs':2,'minimum':4,'maximum':4,'row':0},
                 'reason':'A directly reconstructed necessary bound fails; independent replay required',
                 'numeric_infeasibility_is_proof':False,'focal_type':1,'status':'CANDIDATE_EXACT_SIMPLE_BOUND_FAILURE',
                 'guidance_path':None,'witness_path':None,'graph_completion':False,'infeasibility_from_numeric_status':False}
    boundfixtures[0]['saved_case']={'packet':badprofile,'focal':1,'model':badmodel,'decision':baddecision}
    for name,p in zip(('positive_exact_mandatory_bound','positive_exact_capacity_bound','positive_exact_coordinate_bound'),boundfixtures):
        routes.append((name,'PASS',p,boundcheck))
    lowcopy={'packet':{'target_order':6,'target_degree':5,'support_adjacency':[[0]*4 for _ in range(4)],
             'ordered_masks':[15],'counts':[2],'pair_bits':[{'i':0,'j':0,'bits':[0,1]}]},'focal':0,'values':[1]}
    routes.append(('positive_low_copy_distinct_self_excluded','PASS',lowcopy,lambda p:witness_action(p,budget)))
    routes.append(('positive_saved_exact_model_vector_labels_decision','PASS',case,casecheck))
    unknown=copy.deepcopy(case);unknown['guidance'].update(solution_value_valid=False,col_value=[],col_value_float_hex=[])
    unknown['witness']=None
    unknown['decision']={'candidate':None,'reason':'No complete value-valid numerical incumbent',
        'numeric_infeasibility_is_proof':False,'focal_type':1,'status':'UNKNOWN_NO_EXACT_LOCAL_NEIGHBOR_VECTOR',
        'guidance_path':'type_001_guidance.json','witness_path':None,'graph_completion':False,
        'infeasibility_from_numeric_status':False}
    routes.append(('positive_saved_absent_vector_remains_unknown','PASS',unknown,casecheck))
    rt=synthetic_runtime();rt['plan']['schema']='ROOT_CONCRETE_FOCAL_NEIGHBOR_AUTHOR_CALIBRATION_V1'
    rtcheck=lambda p:runtime(runtime_profile(p['plan'],'calibrate'),p['manifest'],p['terminal'],p['summary'],
                             'calibrate',{'source':'pin','spec':'pin'})
    routes.append(('positive_actual593_runtime_profile','PASS',rt,rtcheck))
    directory={'path':str(out),'expected_base':str(out)}
    dircheck=lambda p:output_directory(p['path'],Path(p['expected_base']))
    routes.append(('positive_actual_output_directory','PASS',directory,dircheck))
    mutation('profile_extra_field','PROFILE_FIELDS',base,lambda p:p['packet'].__setitem__('extra',0),lambda p:witness_action(p,budget))
    mutation('neighbor_vector_missing','NEIGHBOR_SHAPE',base,lambda p:p['values'].pop(),lambda p:witness_action(p,budget))
    mutation('mask_float','TYPE_MASK_INTEGER',base,lambda p:p['packet']['ordered_masks'].__setitem__(0,0.0),lambda p:witness_action(p,budget))
    mutation('pair_float','PAIR_BITS',base,lambda p:p['packet']['pair_bits'][0].__setitem__('bits',[0.0,1]),lambda p:witness_action(p,budget))
    def equalbad(p):p['packet']['counts']=[1,2,1,1,0];p['packet']['pair_bits'][5]['bits']=[]
    mutation('forbidden_equal_type_multiplicity','EQUAL_MULTIPLICITY',base,equalbad,lambda p:witness_action(p,budget))
    mutation('labels_duplicate','LABEL_ORDER',labelbase,lambda p:p.__setitem__('labels',[[0,0],[0,0]]),
             lambda p:labels_checked(reconstruct(p['packet'],p['focal'],budget),p['values'],p['labels'],budget))
    mutation('label_outside_copy_range','LABEL_CAPACITY',labelbase,lambda p:p['labels'][1].__setitem__(1,1),
             lambda p:labels_checked(reconstruct(p['packet'],p['focal'],budget),p['values'],p['labels'],budget))
    mutation('labels_disagree_with_vector','LABEL_AGGREGATION',labelbase,lambda p:p.__setitem__('labels',[[0,0],[2,0]]),
             lambda p:labels_checked(reconstruct(p['packet'],p['focal'],budget),p['values'],p['labels'],budget))
    mutation('model_boolean_capacity','MODEL_RECONSTRUCTION',case,lambda p:p['model']['copy_capacities'].__setitem__(0,True),casecheck)
    mutation('model_last_coordinate_changed','MODEL_RECONSTRUCTION',case,lambda p:p['model']['rows'][-1]['coefficients'].__setitem__(0,1),casecheck)
    mutation('numeric_status_promoted_to_exclusion','DECISION_RECORD',case,
             lambda p:p['decision'].__setitem__('infeasibility_from_numeric_status',True),casecheck)
    mutation('witness_boolean_coordinate','EXACT_WITNESS',case,lambda p:p['witness']['neighbor_counts'].__setitem__(0,True),casecheck)
    mutation('witness_contains_focal_copy','EXACT_WITNESS',case,lambda p:p['witness']['chosen_labels'][0].__setitem__(0,1),casecheck)
    mutation('numeric_boolean_coordinate','NUMERIC_VECTOR',case,lambda p:p['guidance']['col_value'].__setitem__(0,True),casecheck)
    mutation('numeric_hex_corruption','GUIDANCE_HEX',case,lambda p:p['guidance']['col_value_float_hex'].__setitem__(0,0),casecheck)
    mutation('numeric_feasibility_promoted_to_proof','GUIDANCE_HEADER',case,
             lambda p:p['guidance'].__setitem__('floating_status_is_proof',True),casecheck)
    mutation('numeric_boolean_solver_calls','GUIDANCE_HEADER',case,lambda p:p['guidance'].__setitem__('solver_calls',True),casecheck)
    mutation('runtime_boolean_exit','RUNTIME_EXIT',rt,lambda p:p['terminal'].__setitem__('command_exit_code',False),rtcheck)
    mutation('runtime_unreaped','RUNTIME_CLEANUP',rt,lambda p:p['terminal']['cleanup'].__setitem__('reaped',False),rtcheck)
    mutation('runtime_unknown_schema','RUNTIME_PLAN_SCHEMA',rt,lambda p:p['plan'].__setitem__('schema','unknown'),rtcheck)
    mutation('output_path_is_regular_file','PRODUCER_OUTPUT_DIRECTORY',directory,
             lambda p:p.__setitem__('path',str(out/'control_000_known_rook_all_five_free_choices.json')),dircheck)
    routes.extend([('json_duplicate','JSON_DUPLICATE','{"x":1,"x":2}',decode),
                   ('json_nonfinite','JSON_NONFINITE','{"x":NaN}',decode)])
    prefix={'schema':'FIXED17_FOCAL_NEIGHBOR_CHECKPOINT_V1','completed_types':1,'positive_type_prefix':[1],
            'decisions':[{'focal_type':1,'status':decision['status'],'witness_path':decision['witness_path'],
                          'guidance_path':decision['guidance_path']}],'scientific_solver_calls':1,
            'solver_wall_seconds':0.0,'target_resolution':'NONE','automatic_retry':False}
    cpcheck=lambda p:need(same(p,prefix),'CHECKPOINT_PREFIX')
    mutation('checkpoint_boolean_count','CHECKPOINT_PREFIX',prefix,lambda p:p.__setitem__('completed_types',True),cpcheck)
    mutation('checkpoint_late_prefix_changed','CHECKPOINT_PREFIX',prefix,
             lambda p:p['positive_type_prefix'].__setitem__(0,2),cpcheck)
    fakecal={'status':CAL_STATUS,'mode':'calibrate','implementation_version':1,'producer':'/root/checkpoint_audit',
             'verifier':'/root/native_driver','method':'independent_artifact_check','target_resolution':'NONE',
             'actual_target_input_read':False,'source_software':{'synthetic':'pin'},
             'outcome':{'counts':OWN_COUNTS,'all_precise_stages_match':True}}
    mutation('own_gate_boolean_implementation','OWN_HEADER',fakecal,lambda p:p.__setitem__('implementation_version',True),
             lambda p:own_header(p,{'synthetic':'pin'},'calibrate'))
    mutation('own_gate_unqualified_scope','OWN_SCOPE',fakecal,
             lambda p:p['outcome'].__setitem__('all_precise_stages_match',False),
             lambda p:own_header(p,{'synthetic':'pin'},'calibrate'))
    need(len(routes)==OWN_COUNTS['total'] and sum(s=='PASS' for n,s,p,a in routes)==OWN_COUNTS['positive'],'OWN_ROUTE_COUNTS')
    return routes


def output_directory(name,base):
    need(type(name) is str,'PRODUCER_OUTPUT_DIRECTORY')
    path=safe(name,False);need(path.is_dir() and path==base,'PRODUCER_OUTPUT_DIRECTORY')


def own_header(raw,software,mode):
    need(type(raw) is dict and raw.get('status')==(CAL_STATUS if mode=='calibrate' else CONTROLS_STATUS) and
         raw.get('mode')==mode and type(raw.get('implementation_version')) is int and raw['implementation_version']==1 and
         raw.get('producer')=='/root/checkpoint_audit' and raw.get('verifier')=='/root/native_driver' and
         raw.get('method')=='independent_artifact_check' and raw.get('target_resolution')=='NONE' and
         raw.get('actual_target_input_read') is False and same(raw.get('source_software'),software),'OWN_HEADER')
    need(same(raw.get('outcome',{}).get('counts'),OWN_COUNTS if mode=='calibrate' else AUTHOR_COUNTS) and
         raw['outcome'].get('all_precise_stages_match') is True,'OWN_SCOPE')


def qualify(reader,args,software):
    snapshot=dict(software);cal,base=packet(reader,args.calibration,args.calibration_sha256)
    own_header(cal,snapshot,'calibrate');need(same(cal.get('inputs_sha256'),snapshot),'OWN_SOFTWARE')
    rows=reader.read(base/'controls.json',cal['outputs_sha256']['controls.json'])
    need(type(rows) is list and len(rows)==OWN_COUNTS['total'] and
         all(type(r) is dict and type(r.get('index')) is int and r['index']==i and r.get('matches') is True and
             r.get('expected_stage')==r.get('actual_stage') for i,r in enumerate(rows)),'OWN_STAGE_TABLE')


def source_packet(reader,args,mode):
    plan=reader.read(args.producer_plan,args.producer_plan_sha256)
    summary,base=packet(reader,args.producer_summary,args.producer_summary_sha256)
    need(summary.get('schema')=='FIXED17_FOCAL_NEIGHBOR_INTEGER_PRODUCER_REPORT_V1' and
         type(summary.get('implementation_version')) is int and summary['implementation_version']==1 and
         summary.get('mode')==mode and summary.get('producer')=='/root/checkpoint_audit' and
         summary.get('source_author')=='/root/checkpoint_audit' and summary.get('independent_approval') is False and
         summary.get('target_resolution')=='NONE' and summary.get('actual_count_witness_read') is (mode=='solve') and
         summary.get('automatic_retry') is False and type(summary.get('ledger_index_git_mutations')) is int and
         summary['ledger_index_git_mutations']==0,'PRODUCER_HEADER')
    need(same(summary.get('source_software'),AUTHOR_SOFTWARE),'PRODUCER_SOFTWARE')
    identities=summary.get('inputs_sha256')
    need(type(identities) is dict and all(type(p) is str and type(h) is str and len(h)==64 and
         all(c in '0123456789abcdef' for c in h) for p,h in identities.items()) and
         all(identities.get(p)==h for p,h in AUTHOR_SOFTWARE.items()),'PRODUCER_DECLARED_INPUTS')
    reader.map(AUTHOR_SOFTWARE)  # Ancestor proof/maps are declared trusted premises, not recursively rehashed.
    manifest=reader.read(args.producer_manifest,args.producer_manifest_sha256)
    terminal=reader.read(args.producer_terminal,args.producer_terminal_sha256)
    flags=runtime(runtime_profile(plan,mode),manifest,terminal,summary,mode,
                  {'source':SOFTWARE[PRODUCER],'spec':SOFTWARE[PRODUCER_SPEC]})
    output_directory(flags['--out'],base)
    need(safe(summary.get('output_root'),False)==base,'PRODUCER_OUTPUT_DIRECTORY')
    expected='FIXED17_FOCAL_NEIGHBOR_INTEGER_V1_AUTHOR_CONTROLS_PASS' if mode=='calibrate' else 'CANDIDATE_FIXED17_FOCAL_NEIGHBOR_INTEGER_SYSTEMS_V1'
    need(summary.get('status')==expected,'PRODUCER_STATUS');return summary,base,flags


def replay_controls(reader,summary,base,out):
    author=summary.get('author_controls')
    need(type(author) is dict and same(author.get('counts'),AUTHOR_COUNTS) and author.get('stage_mismatches')==[] and
         type(author.get('native_solver_calls')) is int and author['native_solver_calls']==3 and
         author.get('actual_count_witness_read') is False and author.get('duplicate_copy_fixture_is_row_kernel_only') is True,
         'AUTHOR_SCOPE')
    table=reader.read(base/'controls.json',summary['outputs_sha256']['controls.json'])
    need(type(table) is list and len(table)==34 and same(author.get('table'),table),'AUTHOR_STAGE_POPULATION')
    names={'controls.json'};pairs=[]
    def load(name):
        names.add(name);need(name in summary['outputs_sha256'],'AUTHOR_PAYLOAD')
        return reader.read(base/name,summary['outputs_sha256'][name])
    for i,(name,expected) in enumerate(AUTHOR_ROUTES):
        payload=load('control_%02d_%s.json'%(i,name));result=None
        try:result=author_action(name,payload,reader.budget);actual='PASS'
        except Veto as exc:actual=str(exc)
        row=table[i]
        need(type(row) is dict and type(row.get('index')) is int and row['index']==i and row.get('name')==name and
             row.get('expected_stage')==expected and row.get('actual_stage')==expected and row.get('matches') is True,
             'AUTHOR_STAGE_ROW')
        need(actual==expected,'AUTHOR_INDEPENDENT_STAGE')
        if i<9:
            returned=load('result_%02d.json'%i)
            if 6<=i<=8:
                case=i-6;guidance=load('tiny_%d_guidance.json'%case)
                names.add('tiny_%d_solver.log'%case)
                guidance_checked(guidance,payload,reader.budget,5)
                observed=extraction(payload,guidance,reader.budget)
                need(observed['candidate']==([1,0] if case==0 else [1] if case==2 else None),'AUTHOR_TINY_CANDIDATE')
                need(same(returned,{'guidance':guidance,'extraction':observed,'mathematical_infeasibility_proven':False}),
                     'AUTHOR_RETURNED_RESULT')
                result={**result,'extraction':observed,'numerical_infeasibility_is_proof':False}
            else:need(same(returned,result),'AUTHOR_RETURNED_RESULT')
            write(out/('independent_result_%02d.json'%i),result,reader.budget)
        pairs.append({'index':i,'name':name,'expected_stage':expected,'producer_stage':row['actual_stage'],
                      'independent_stage':actual,'matches':True})
    need(len(names)==50 and names<=set(summary['outputs_sha256']),'AUTHOR_INVENTORY')
    if summary['mode']=='calibrate':need(set(summary['outputs_sha256'])==names and same(summary.get('outcome'),author),'AUTHOR_OUTPUT_POPULATION')
    write(out/'independent_stage_pairs.json',pairs,reader.budget)
    return names,{'counts':AUTHOR_COUNTS,'all_precise_stages_match':True,'producer_physical_files':51,
                  'producer_output_hashes':50,'complete_known_rook_focal_rows':10,'complete_tiny_binary_cases':3,
                  'solver_calls':0,'actual_target_input_read':False,'graph_completion':False}


def full(reader,args,summary,base,flags,out,software):
    need(args.producer_controls is not None and args.producer_controls_sha256 is not None,'CONTROLS_ARGUMENTS')
    gate,gbase=packet(reader,args.producer_controls,args.producer_controls_sha256);own_header(gate,software,'controls')
    config=reader.read(flags['--configuration'],flags['--configuration-sha256'])
    need(type(config) is dict and config.get('schema')=='FIXED17_FOCAL_NEIGHBOR_INTEGER_CONFIGURATION_V1' and
         config.get('target_resolution')=='NONE' and type(config.get('inputs_sha256')) is dict,'CONFIG_HEADER')
    cpins=config['inputs_sha256'];expected={**PREMISES,SELF:software[SELF],SPEC:software[SPEC],
                                         args.calibration:args.calibration_sha256,args.producer_controls:args.producer_controls_sha256}
    # Arguments may be absolute; maps use immutable workspace-relative names.
    for name,digest in expected.items():
        relative=safe(name).relative_to(ROOT).as_posix();need(cpins.get(relative)==digest,'CONFIG_QUALIFICATION_PIN')
    need(same(config.get('independent_checker_source'),SELF) and config.get('independent_checker_source_sha256')==software[SELF] and
         safe(config.get('independent_checker_calibration_path'))==safe(args.calibration) and
         config.get('independent_checker_calibration_sha256')==args.calibration_sha256 and
         safe(config.get('independent_producer_controls_path'))==safe(args.producer_controls) and
         config.get('independent_producer_controls_sha256')==args.producer_controls_sha256,'CONFIG_CHECKER')
    author_path=safe(config.get('author_calibration_path')).relative_to(ROOT).as_posix()
    author_hash=config.get('author_calibration_sha256')
    need(type(author_hash) is str and len(author_hash)==64 and cpins.get(author_path)==author_hash and
         gate.get('inputs_sha256',{}).get(author_path)==author_hash and
         summary.get('inputs_sha256',{}).get(author_path)==author_hash,'CONFIG_AUTHOR_CALIBRATION')
    need(all(gate.get('inputs_sha256',{}).get(p)==h for p,h in software.items()),'CONTROLS_SOFTWARE_PINS')
    maximum=config.get('per_focal_solver_seconds')
    need(type(maximum) in (int,float) and math.isfinite(maximum) and 0<maximum<=10,'CONFIG_SOLVER_SECONDS')
    reader.map(PREMISES);trusted=reader.read(TRUSTED_PROFILE,TRUSTED_PROFILE_SHA)
    capacity=reader.read(next(iter(PREMISES)),next(iter(PREMISES.values())))
    need(capacity.get('status')=='INDEPENDENT_FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_COMPLETE_PASS' and
         capacity.get('inputs_sha256',{}).get(TRUSTED_PROFILE)==TRUSTED_PROFILE_SHA,'TRUSTED_PROFILE_GATE')
    names,control_scope=replay_controls(reader,summary,base,out)
    def load(name):
        names.add(name);need(name in summary['outputs_sha256'],'SCIENTIFIC_PAYLOAD')
        return reader.read(base/name,summary['outputs_sha256'][name])
    raw=load('parsed_focal_input.json');need(same(raw,trusted),'TRUSTED_PROFILE_IDENTITY');parsed=profile(raw,reader.budget)
    positive=[i for i,x in enumerate(raw['counts']) if x]
    need(len(raw['ordered_masks'])==472 and len(raw['support_adjacency'])==17 and
         sum(raw['counts'])==82 and len(positive)==68,'FIXED_SCOPE')
    decisions=[];calls=0;elapsed=0.0
    for completed,i in enumerate(positive,1):
        reader.budget.tick();prefix='type_%03d'%i;model=load(prefix+'_model.json');decision=load(prefix+'_decision.json')
        expected_model=reconstruct(raw,i,reader.budget,parsed);bound=bounds(expected_model)
        guidance=witness=None
        if bound is None:
            guidance=load(prefix+'_guidance.json');names.add(prefix+'_solver.log');calls+=1
            elapsed+=guidance_checked(guidance,expected_model,reader.budget,maximum)
            if extraction(expected_model,guidance,reader.budget)['candidate'] is not None:witness=load(prefix+'_witness.json')
        item=saved_focal(raw,i,model,decision,guidance,witness,reader.budget,expected_model);decisions.append(item)
        checkpoint=load('checkpoint_%03d.json'%i)
        expected_cp={'schema':'FIXED17_FOCAL_NEIGHBOR_CHECKPOINT_V1','completed_types':completed,
                     'positive_type_prefix':positive[:completed],'decisions':list(decisions),
                     'scientific_solver_calls':calls,'solver_wall_seconds':elapsed,'target_resolution':'NONE','automatic_retry':False}
        need(same(checkpoint,expected_cp),'CHECKPOINT_PREFIX')
        write(out/('independent_focal_%03d.json'%i),{'model':expected_model,'decision':decision,
              'exact_witness':witness,'complete_rows_reconstructed':18,'checkpoint_checked':True},reader.budget)
    witnesses=sum(d['witness_path'] is not None for d in decisions)
    failures=sum(d['status']=='CANDIDATE_EXACT_SIMPLE_BOUND_FAILURE' for d in decisions)
    unknown=sum(d['status']=='UNKNOWN_NO_EXACT_LOCAL_NEIGHBOR_VECTOR' for d in decisions)
    outcome={'outside_copies':82,'positive_types':68,'all_type_variables':472,'equalities_per_focal':18,
             'complete_equalities_checked_for_witnesses':True,'completed_focal_types':68,'decisions':decisions,
             'exact_neighbor_witnesses':witnesses,'exact_simple_bound_failures':failures,'unknown_focal_types':unknown,
             'scientific_solver_calls':calls,'solver_wall_seconds':elapsed,'every_focal_has_exact_choice':witnesses==68,
             'graph_completion':False,'numerical_infeasibility_proves_nothing':True,'uniform_profiles':False}
    need(same(load('focal_neighbor_outcome.json'),outcome) and same(summary.get('outcome'),outcome),'FULL_OUTCOME')
    need(set(summary['outputs_sha256'])==names and len(names)==256+2*calls+witnesses,'FULL_OUTPUT_POPULATION')
    need(type(summary.get('native_solver_calls')) is int and summary['native_solver_calls']==3+calls,'FULL_SOLVER_COUNT')
    write(out/'independent_outcome.json',outcome,reader.budget)
    return {**outcome,'producer_controls':control_scope,'complete_reconstructed_model_rows':1224,
            'complete_verified_integer_witness_rows':18*witnesses,'complete_checkpoints':68,
            'all_precise_stages_match':True,'qualified_profile_inherited':True,'ancestor_Gram_recomputed':False,
            'ancestor_count_system_recomputed':False,'independent_solver_calls':0,'actual_target_input_read':True}


def calibrate(out,budget):
    table=[]
    for i,(name,expected,payload,action) in enumerate(own_routes(budget,out)):
        write(out/('control_%03d_%s.json'%(i,name)),payload,budget)
        try:action(payload);actual='PASS'
        except Veto as exc:actual=str(exc)
        table.append({'index':i,'name':name,'expected_stage':expected,'actual_stage':actual,'matches':actual==expected})
    write(out/'controls.json',table,budget)
    need(all(r['matches'] for r in table),'OWN_STAGE_MISMATCH')
    return {'counts':OWN_COUNTS,'all_precise_stages_match':True,'solver_calls':0,'producer_imports':0,
            'actual_target_input_read':False,'graph_completion':False,
            'complete_known_rook_focal_rows':10,'complete_tiny_binary_cases':3,
            'distinct_same_type_copy_label_checked':True,'all_three_exact_bound_branches_checked':True}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=('calibrate','controls','full'))
    for name in ('seconds','out','self-sha256','spec-sha256'):
        parser.add_argument('--'+name,required=True,type=float if name=='seconds' else str)
    for name in ('calibration','producer-plan','producer-summary','producer-manifest','producer-terminal','producer-controls'):
        parser.add_argument('--'+name);parser.add_argument('--'+name+'-sha256')
    args=parser.parse_args();budget=Budget(args.seconds);out=safe(args.out,False)
    need(out.is_relative_to(ROOT/'acceleration/results') and not out.exists(),'OUTPUT_FRESH');out.mkdir(parents=True)
    reader=Reader(budget);software={**SOFTWARE,SELF:args.self_sha256,SPEC:args.spec_sha256}
    try:
        reader.map(software)
        if args.mode=='calibrate':outcome=calibrate(out,budget);status=CAL_STATUS
        else:
            for name in ('calibration','producer_plan','producer_summary','producer_manifest','producer_terminal'):
                need(getattr(args,name) is not None and getattr(args,name+'_sha256') is not None,'SOURCE_ARGUMENTS')
            qualify(reader,args,software)
            summary,base,flags=source_packet(reader,args,'calibrate' if args.mode=='controls' else 'solve')
            if args.mode=='controls':_,outcome=replay_controls(reader,summary,base,out);status=CONTROLS_STATUS
            else:outcome=full(reader,args,summary,base,flags,out,software);status=FULL_STATUS
        reader.closing();outputs={}
        for name in sorted(inventory(out,budget)):
            digest=hashlib.sha256()
            with (out/name).open('rb') as handle:
                while True:
                    budget.tick();block=handle.read(1024*1024)
                    if not block:break
                    digest.update(block)
            outputs[name]=digest.hexdigest()
        report={'status':status,'implementation_version':1,'mode':args.mode,'timestamp':datetime.now(timezone.utc).isoformat(),
                'producer':'/root/checkpoint_audit','verifier':'/root/native_driver','checking_source_author':'/root/native_driver',
                'method':'independent_artifact_check','target_resolution':'NONE','source_software':software,
                'inputs_sha256':dict(reader.pins),'outputs_sha256':outputs,'outcome':outcome,'command':[sys.executable,*sys.argv],
                'cwd':str(ROOT),'actual_target_input_read':args.mode=='full','producer_imports':0,'solver_calls':0,
                'graph_completion':False,'automatic_retry':False,'deadline':budget.tick(),
                'shared_components':['Native ee985/c457 reader/runtime engineering ancestry copied explicitly, not imported',
                    'Immutable qualified468f profile and4f671/d8eaf/count/pair/block dependencies inherited, not Gram/count rederived',
                    'New set-incidence rows, integer vectors, distinct labels and prefix checks; no CP AST/parser/model imports',
                    'Public rook geometry and declared wire/stage names shared; no HiGHS/NumPy imports or calls'],
                'limitations':['Every checked exact choice is one focal row only; no symmetric simultaneous graph or uniform profile inference',
                    'Absent or rejected numerical incumbent remains UNKNOWN, never count witness/target exclusion',
                    'Floating guidance is separately authenticated metadata; native optimization is not rerun',
                    'Source producer declared ancestor maps are not bulk replayed; explicit qualified direct premises are inherited',
                    'No matching, clique, full99 CNF or later model cuts are included',
                    '20save is guarded allocation intent and actual terminal requirement, not a hard-real-time guarantee',
                    'No formal/external/novelty claim or ledger/index/Git mutation']}
        write(out/'summary.json',report,budget);reader.closing();budget.tick()
        print(json.dumps({'status':status,'mode':args.mode}),flush=True)
    except Exception as exc:
        try:
            (out/'failure.json').write_text(json.dumps({'status':'FAILED_PRESERVED','stage':str(exc),
                'exception':type(exc).__name__,'inputs_sha256':reader.pins,'target_resolution':'NONE','automatic_retry':False,
                'timestamp':datetime.now(timezone.utc).isoformat()},indent=2,allow_nan=False)+'\n',encoding='utf8')
        except Exception:pass
        raise


if __name__=='__main__':
    main()
