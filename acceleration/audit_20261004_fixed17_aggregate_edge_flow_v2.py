"""SOURCE ONLY: distinct exact aggregate symmetric exterior edge-flow checker."""
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
SELF = 'acceleration/audit_20261004_fixed17_aggregate_edge_flow_v2.py'
SPEC = 'acceleration/audit_20261004_fixed17_aggregate_edge_flow_v2_spec.md'
PRODUCER = 'acceleration/solve_20261004_fixed17_aggregate_edge_flow_v1.py'
PRODUCER_SPEC = 'acceleration/solve_20261004_fixed17_aggregate_edge_flow_v1_spec.md'
CAL_STATUS = 'INDEPENDENT_FIXED17_AGGREGATE_EDGE_FLOW_V1_CALIBRATION_PASS'
CONTROLS_STATUS = 'INDEPENDENT_FIXED17_AGGREGATE_EDGE_FLOW_V1_PRODUCER_CONTROLS_PASS'
FULL_STATUS = 'INDEPENDENT_FIXED17_AGGREGATE_EDGE_FLOW_V1_COMPLETE_PASS'
AUTHOR_COUNTS = {'positive':7,'negative':25,'total':32}
OWN_COUNTS = {'positive':19,'negative':55,'total':74}
MODEL_SCHEMA = 'FIXED17_AGGREGATE_EXTERIOR_EDGE_FLOW_MODEL_V1'
CANDIDATE_SCHEMA = 'FIXED17_AGGREGATE_EXTERIOR_EDGE_FLOW_INTEGER_CANDIDATE_V1'
TRUSTED_PROFILE = 'acceleration/results/20261004_fixed17_count_neighbor_capacity01/parsed_screen_input.json'
TRUSTED_PROFILE_SHA = '468f281bfc13a34a5c23ca2a6af9f8564954c826e0b9f7bddfad36a76832690e'
AUTHOR_SOFTWARE = {
  "acceleration/solve_20261004_fixed17_aggregate_edge_flow_v1.py": "ec556ba097babc3595c4f07ab1b44b7b3e4615b91d3d5546940ae6c9c22970bf",
  "acceleration/solve_20261004_fixed17_aggregate_edge_flow_v1_spec.md": "c7e2accfa60147566064c756bad225dfe926e05755ceb123f45b093cfbbbbac2",
  "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
  "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
  "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
  "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
  "build/research-venv/Lib/site-packages/highspy/_core/__init__.pyi": "53c07e5eafff940daa32458b20262b07d39420b062e0875c2f56e9ac92f4d699",
  "build/research-venv/Lib/site-packages/highspy/_core.cp312-win_amd64.pyd": "f733d7369f647f8afe481bbaf569164f7cd7c127e41ca53cd7c205c2fb9038e2",
  "build/research-venv/Lib/site-packages/highspy/highs.py": "00ce58ef248062125309ccdaf7af6374caf1a29f6a04e0d637b7507ead34d51a",
  "build/research-venv/Lib/site-packages/highspy/__init__.py": "01df06ec93388a45de66adb43d4b243cd7e11c54f24106064a221facf6aa7eb9",
  "build/research-venv/Lib/site-packages/highspy-1.15.1.dist-info/METADATA": "cc09b9d5bf93d8cd79be21bede4e72b686d79cdc75f6524e0e0a1af3e9487a8d"
}
PREMISES = {
  "acceleration/results/20261004_fixed17_count_neighbor_capacity01/parsed_screen_input.json": "468f281bfc13a34a5c23ca2a6af9f8564954c826e0b9f7bddfad36a76832690e",
  "acceleration/results/20261004_fixed17_integer_type_counts01/exact_integer_candidate.json": "133097b6174aa1a4b1d327b5c72a727f8ad1ac6daeef0654b117a5f8b88de5b5",
  "acceleration/results/20261004_independent_review/external_moment_integer_counts_full01/summary.json": "37bcf42a3b5e358c4306c642e152e3e605a07dc305de71b2272e455e377bd6b8",
  "acceleration/results/20261004_independent_review/fixed17_count_neighbor_capacity_full01/summary.json": "4f6711cba2450262709ba0724bbd9bdbba3c95934c85265479985be7a38decb3",
  "acceleration/results/20261004_independent_review/fixed17_dual_gram_pairs_full02/summary.json": "ee9fa8961415df0e5f0ca429c33fc95a1d6223b77ec68e2c9ec71cc1dec0e218",
  "acceleration/results/20261004_independent_review/target_exterior_type_edge_moments01/summary.json": "910a740aff6ecd90515af7de0a2743abab47eabe902274237b3b70e1d0fdc6d6",
  "acceleration/results/20261004_integer_counts_independent_full_root_actual_acceptance01.json": "3823dec446f661d87a27d2cad80b4c2f91883c786f30def4f43a25eb913bb10d",
  "acceleration/results/20261004_fixed17_count_neighbor_capacity_full_root_actual_acceptance01.json": "d8eaf7c2cb41a0bd8f1287b652edcbcc498b97f3475575b6e3b0d77e5d655017",
  "acceleration/results/20261004_fixed17_dual_gram_pairs_checker_root_actual_full_acceptance02.json": "39a904ee2ec0bdb4b1a28678c1842794d2abe7d05150879517265a6e7f797586",
  "acceleration/results/20261004_target_exterior_type_edge_moments_root_written_acceptance01.json": "0e09566986883576c0f421cb1e47391eaadb49db72183d4e90c3ce55f9356728"
}
SOFTWARE = dict(AUTHOR_SOFTWARE)
SOFTWARE.update({
    'acceleration/audit_20261004_fixed17_focal_neighbor_integer_v1.py':'218c0a282b17c0b37689dd27897422470308f6f0f9a0ced8320ae31aa5462c13',
    'acceleration/audit_20261004_fixed17_focal_selector_matching_v1.py':'49f2c88d2e844b5ff04034ce3265fdaa78af54c3be61e93b0aef90abcad0930d'})
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
            'Independent aggregate integer flow/model and raw closure checking; all authentication and saves share the allocation')
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
         summary.get('actual_executor_requires_external_receipt') is True, 'RUNTIME_EXECUTOR')
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
        'actual_executor_requires_external_receipt':True,
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
    if schema == 'FIXED17_AGGREGATE_EDGE_FLOW_SOURCE_ONLY_PLAN_V1':
        need(mode == 'calibrate', 'RUNTIME_PLAN_SCHEMA'); result = plan.get('calibration')
    elif schema == 'ROOT_CONCRETE_FIXED17_AGGREGATE_EDGE_FLOW_AUTHOR_CALIBRATION_V1':
        need(mode == 'calibrate', 'RUNTIME_PLAN_SCHEMA'); result = plan
    elif schema == 'FIXED17_AGGREGATE_EDGE_FLOW_CONCRETE_PLAN_V1':
        need(mode == 'solve', 'RUNTIME_PLAN_SCHEMA'); result = plan.get('solve')
        need(type(result) is dict and all(same(plan.get(k),result.get(k)) for k in
             ('command','supervisor_argv','child_argv','worker_argv','allocation')), 'RUNTIME_PLAN_ALIASES')
    else: raise Veto('RUNTIME_PLAN_SCHEMA')
    need(type(result) is dict, 'RUNTIME_PLAN_PROFILE')
    return result


def profile(raw, budget):
    need(type(raw) is dict and set(raw) == {'target_order','target_degree','support_adjacency',
        'ordered_masks','counts','pair_bits'}, 'PROFILE_FIELDS')
    v,k,h = raw['target_order'],raw['target_degree'],raw['support_adjacency']
    need(type(v) is int and type(k) is int and 0 < k < v-1, 'PROFILE_TARGET')
    need(type(h) is list and 0 < len(h) < v and all(type(row) is list and len(row) == len(h) for row in h), 'PROFILE_GRAPH')
    m = len(h)
    need(all(type(x) is int and x in (0,1) for row in h for x in row) and
         all(h[u][u] == 0 and h[u][w] == h[w][u] for u in range(m) for w in range(m)), 'PROFILE_GRAPH')
    masks,counts = raw['ordered_masks'],raw['counts']
    need(type(masks) is list and masks and all(type(t) is int and 0 <= t < 1<<m for t in masks)
         and masks == sorted(set(masks)), 'PROFILE_MASKS')
    need(type(counts) is list and len(counts) == len(masks) and
         all(type(n) is int and 0 <= n <= v-m for n in counts) and sum(counts) == v-m, 'PROFILE_COUNTS')
    n = len(masks); supplied = raw['pair_bits']
    need(type(supplied) is list and len(supplied) == n*(n+1)//2, 'PROFILE_PAIR_POPULATION')
    bits = {}; ordinal = 0
    for i in range(n):
        budget.tick()
        for j in range(i,n):
            row = supplied[ordinal]; ordinal += 1
            need(type(row) is dict and set(row) == {'i','j','bits'} and type(row['i']) is int and
                 type(row['j']) is int and (row['i'],row['j']) == (i,j), 'PROFILE_PAIR_ORDER')
            bs = row['bits']
            need(type(bs) is list and all(type(a) is int for a in bs) and bs in ([],[0],[1],[0,1]), 'PROFILE_PAIR_BITS')
            bits[i,j] = bs
    sets = [{u for u in range(m) if mask & (1<<u)} for mask in masks]
    return h,sets,counts,bits


def reconstruct(raw, budget):
    h,sets,counts,bits = profile(raw,budget); m = len(h)
    ids = [i for i,n in enumerate(counts) if n]
    pairs = []
    # Nested original-index loops, not the producer's combinations decoder.
    for i in ids:
        for j in ids:
            if i <= j: pairs.append([i,j])
    capacities,lower,upper = [],[],[]
    for i,j in pairs:
        budget.tick()
        cap = counts[i]*counts[j] if i != j else sum(range(counts[i]))
        bs = bits[i,j]; need(bs or cap == 0,'PROFILE_INCOMPATIBLE_COEXISTENCE')
        capacities.append(cap); lower.append(cap if bs == [1] else 0); upper.append(cap if 1 in bs else 0)
    rows = []; checkpoints = []
    for completed,i in enumerate(ids,1):
        budget.tick()
        requests = [(None,counts[i]*(raw['target_degree']-len(sets[i])))]
        requests += [(u,counts[i]*(2-int(u in sets[i])-len({w for w in sets[i] if h[u][w]}))) for u in range(m)]
        for u,rhs in requests:
            terms = []
            for column,(a,b) in enumerate(pairs):
                # Count both endpoints independently. Same-class edges hit twice.
                coefficient = int(a == i and (u is None or u in sets[b]))
                coefficient += int(b == i and (u is None or u in sets[a]))
                if coefficient: terms.append([column,coefficient])
            rows.append({'kind':'degree' if u is None else 'support_incidence','type_i':i,'support_u':u,
                         'lower':rhs,'upper':rhs,'terms':terms})
        if completed%8 == 0 or completed == len(ids):
            checkpoints.append({'positive_classes_completed':completed,'exact_rows_completed':len(rows),
                                'total_positive_classes':len(ids),'total_expected_rows':len(ids)*(m+1)})
    built = {'schema':MODEL_SCHEMA,'target_order':raw['target_order'],'target_degree':raw['target_degree'],
        'support_order':m,'positive_type_ids':ids,'variable_pairs':pairs,'variables':len(pairs),
        'lower':lower,'upper':upper,'capacities':capacities,'rows':rows,'ordered_masks':raw['ordered_masks'],
        'counts':counts,'support_adjacency':h,'zero_count_classes_omitted_canonically':True,
        'diagonal_is_unordered_edge_count':True,'diagonal_row_coefficient':2,
        'no_equitable_profile_assumed':True,'graph_completion':False}
    return built,checkpoints


def from_edges(built, values):
    ids = built['positive_type_ids']; by_pair = {tuple(pair):x for pair,x in zip(built['variable_pairs'],values)}
    dense = [[(2 if i == j else 1)*by_pair[min(i,j),max(i,j)] for j in ids] for i in ids]
    return {'schema':CANDIDATE_SCHEMA,'variable_pairs':copy.deepcopy(built['variable_pairs']),
            'edge_counts':list(values),'ordered_flow_matrix':dense}


def check_candidate(built, raw, budget):
    need(type(raw) is dict and set(raw) == {'schema','variable_pairs','edge_counts','ordered_flow_matrix'} and
         raw['schema'] == CANDIDATE_SCHEMA, 'CANDIDATE_HEADER')
    need(same(raw['variable_pairs'],built['variable_pairs']), 'CANDIDATE_VARIABLE_ORDER')
    xs,flow = raw['edge_counts'],raw['ordered_flow_matrix']; ids = built['positive_type_ids']; p = len(ids)
    need(type(xs) is list and len(xs) == built['variables'] and all(type(x) is int and x >= 0 for x in xs), 'CANDIDATE_INTEGER')
    need(all(lo <= x <= hi for lo,x,hi in zip(built['lower'],xs,built['upper'])), 'CANDIDATE_BOUND')
    need(type(flow) is list and len(flow) == p and all(type(row) is list and len(row) == p for row in flow)
         and all(type(x) is int and x >= 0 for row in flow for x in row), 'CANDIDATE_ORDERED_DOMAIN')
    need(all(flow[a][b] == flow[b][a] for a in range(p) for b in range(p)), 'CANDIDATE_SYMMETRY')
    need(all(flow[a][a]%2 == 0 for a in range(p)), 'CANDIDATE_DIAGONAL_PARITY')
    need(same(flow,from_edges(built,xs)['ordered_flow_matrix']), 'CANDIDATE_ORDERED_IDENTITY')
    m,h,counts,masks = (built[k] for k in ('support_order','support_adjacency','counts','ordered_masks'))
    sets = [{u for u in range(m) if t & (1<<u)} for t in masks]; observations = []
    # Independent dense row sums rather than evaluating the submitted sparse model.
    for a,i in enumerate(ids):
        budget.tick(); rhs = counts[i]*(built['target_degree']-len(sets[i])); lhs = sum(flow[a])
        need(lhs == rhs, 'DEGREE_EQUATION')
        observations.append({'row':len(observations),'kind':'degree','type_i':i,'support_u':None,'lhs':lhs,'rhs':rhs})
        for u in range(m):
            lhs = sum(flow[a][b] for b,j in enumerate(ids) if u in sets[j])
            rhs = counts[i]*(2-int(u in sets[i])-sum(h[u][w] for w in sets[i]))
            need(lhs == rhs, 'INCIDENCE_EQUATION')
            observations.append({'row':len(observations),'kind':'support_incidence','type_i':i,'support_u':u,'lhs':lhs,'rhs':rhs})
    return {'exact_integer_edge_variables':len(xs),'exact_rows':len(observations),'ordered_flow_symmetric':True,
            'all_diagonal_flows_even':True,'capacities_and_allowed_bits_checked':True,'observations':observations,
            'integer_aggregate_feasible':True,'graph_completion':False}


def guidance_checked(raw, built, budget, maximum):
    need(type(raw) is dict and set(raw) == {'schema','native_version','numpy_version','run_status','model_status',
        'solution_value_valid','col_value','col_value_float_hex','options','wall_seconds','objective_all_zero',
        'solver_calls','floating_status_is_proof','numeric_infeasibility_is_proof'} and
        raw['schema'] == 'FIXED17_AGGREGATE_EDGE_FLOW_NUMERIC_GUIDANCE_V1' and raw['native_version'] == '1.15.1'
        and type(raw['numpy_version']) is str and type(raw['run_status']) is str and type(raw['model_status']) is str,
        'GUIDANCE_HEADER')
    xs = raw['col_value']
    need(type(xs) is list and len(xs) in (0,built['variables']) and all(type(x) is float and math.isfinite(x) for x in xs), 'GUIDANCE_VALUES')
    need(type(raw['solution_value_valid']) is bool and (not raw['solution_value_valid'] or len(xs) == built['variables']), 'GUIDANCE_VALIDITY')
    need(same(raw['col_value_float_hex'],[x.hex() for x in xs]), 'GUIDANCE_HEX')
    need(type(raw['solver_calls']) is int and raw['solver_calls'] == 1 and raw['objective_all_zero'] is True and
         raw['floating_status_is_proof'] is False and raw['numeric_infeasibility_is_proof'] is False,'GUIDANCE_SCOPE')
    need(type(raw['wall_seconds']) in (int,float) and math.isfinite(raw['wall_seconds']) and raw['wall_seconds'] >= 0, 'GUIDANCE_ELAPSED')
    opts = raw['options']; expected = {'presolve':'on','solver':'choose','threads':1,'parallel':'off','random_seed':0,
        'mip_rel_gap':0.0,'mip_abs_gap':0.0,'mip_feasibility_tolerance':1e-7,'primal_feasibility_tolerance':1e-7,
        'output_flag':True,'log_to_console':False}
    need(type(opts) is dict and set(opts) == set(expected)|{'log_file','time_limit'} and
         all(same(opts.get(k),v) for k,v in expected.items()) and type(opts['log_file']) is str and
         type(opts['time_limit']) in (int,float) and math.isfinite(opts['time_limit']) and 0 < opts['time_limit'] <= maximum,
         'GUIDANCE_OPTIONS')
    budget.tick(); return raw['wall_seconds']


def extraction(built, guidance, budget):
    xs = guidance['col_value']
    if not guidance['solution_value_valid'] or len(xs) != built['variables']:
        return {'candidate':None,'reason':'No complete value-valid numeric incumbent','infeasibility_proved':False}
    values = [int(round(x)) for x in xs]; distances = [abs(x-y) for x,y in zip(xs,values)]
    if any(x > 1e-7 for x in distances):
        return {'candidate':None,'reason':'Numerical coordinates exceed the declared extraction distance',
                'max_rounding_distance':max(distances),'infeasibility_proved':False}
    candidate = from_edges(built,values)
    try: receipt = check_candidate(built,candidate,budget)
    except Veto as exc:
        if str(exc) == 'SAVE_RESERVE': raise
        return {'candidate':None,'reason':'Extracted integers fail exact check: '+str(exc),'infeasibility_proved':False}
    return {'candidate':candidate,'exact_check':receipt,'rounding_tolerance':1e-7,
            'max_rounding_distance':max(distances,default=0.0),'infeasibility_proved':False}


def model_identity(raw, expected): need(same(raw,expected), 'MODEL_RECONSTRUCTION')
def checkpoint_identity(raw, expected): need(same(raw,expected), 'CHECKPOINT_PREFIX')
def absent_identity(raw, expected): need(same(raw,expected), 'EXTRACTION_IDENTITY')
def output_directory(name, base):
    need(type(name) is str,'PRODUCER_OUTPUT_DIRECTORY')
    path = safe(name,False); need(path.is_dir() and path == base,'PRODUCER_OUTPUT_DIRECTORY')

AUTHOR_ROUTES = [
 ('known_rook_aggregate_multiplicities','PASS'),('known_rook_sole1_full_capacities','PASS'),
 ('known_rook_zero_classes_omitted','PASS'),('strict_json_integer_positive','PASS'),
 ('tiny_rook_integer_model','PASS'),('tiny_odd_diagonal_fixture','PASS'),('tiny_capacity_fixture','PASS'),
 ('profile_count_bool','PROFILE_COUNTS'),('profile_count_float','PROFILE_COUNTS'),
 ('profile_count_negative','PROFILE_COUNTS'),('profile_graph_bool','PROFILE_GRAPH'),
 ('profile_graph_float','PROFILE_GRAPH'),('profile_graph_asymmetric','PROFILE_GRAPH'),
 ('profile_mask_bool','PROFILE_MASKS'),('profile_mask_unsorted','PROFILE_MASKS'),
 ('profile_pair_bit_bool','PROFILE_PAIR_BITS'),('profile_pair_duplicate','PROFILE_PAIR_ORDER'),
 ('candidate_wrong_schema','CANDIDATE_HEADER'),('candidate_pair_order','CANDIDATE_VARIABLE_ORDER'),
 ('candidate_edge_bool','CANDIDATE_INTEGER'),('candidate_edge_negative','CANDIDATE_INTEGER'),
 ('candidate_edge_overcapacity','CANDIDATE_BOUND'),('candidate_forced_zero','CANDIDATE_BOUND'),
 ('candidate_forced_one','CANDIDATE_BOUND'),('candidate_matrix_bool','CANDIDATE_ORDERED_DOMAIN'),
 ('candidate_asymmetric','CANDIDATE_SYMMETRY'),('candidate_odd_diagonal','CANDIDATE_DIAGONAL_PARITY'),
 ('candidate_wrong_even_diagonal','CANDIDATE_ORDERED_IDENTITY'),('candidate_degree_failure','DEGREE_EQUATION'),
 ('candidate_incidence_failure_with_correct_degrees','INCIDENCE_EQUATION'),
 ('json_duplicate','JSON_DUPLICATE'),('json_nonfinite','JSON_NONFINITE')]


def rook_fixture(corners=False, forced=False):
    vertices = [(r,c) for r in range(3) for c in range(3)]
    support = [(0,0),(0,1),(1,0),(1,1)] if corners else [(0,0),(0,1)]
    adjacent = lambda a,b: a != b and (a[0] == b[0] or a[1] == b[1])
    h = [[int(adjacent(a,b)) for b in support] for a in support]
    outside = [a for a in vertices if a not in support]
    types = {a:sum(1<<u for u,b in enumerate(support) if adjacent(a,b)) for a in outside}
    masks = sorted(set(types.values())|({1,2} if corners else set()))
    counts = [sum(t == mask for t in types.values()) for mask in masks]
    by_mask = {t:i for i,t in enumerate(masks)}
    bits = {(i,j):[0,1] for i in range(len(masks)) for j in range(i,len(masks))}
    if forced:
        bits.update({(0,0):[1],(1,1):[1],(2,2):[1],(0,3):[1],(1,3):[0],(2,3):[0],(3,3):[0]})
    raw = {'target_order':9,'target_degree':4,'support_adjacency':h,'ordered_masks':masks,'counts':counts,
        'pair_bits':[{'i':i,'j':j,'bits':bits[i,j]} for i in range(len(masks)) for j in range(i,len(masks))]}
    edge_counts = {}
    for a_index,a in enumerate(outside):
        for b in outside[a_index+1:]:
            if adjacent(a,b):
                i,j = sorted((by_mask[types[a]],by_mask[types[b]]))
                edge_counts[i,j] = edge_counts.get((i,j),0)+1
    return raw,edge_counts


def rook_objects(budget,corners=False,forced=False):
    raw,edges = rook_fixture(corners,forced); built,cps = reconstruct(raw,budget)
    candidate = from_edges(built,[edges.get(tuple(pair),0) for pair in built['variable_pairs']])
    return raw,built,candidate,cps


def tiny_fixture(payload, budget):
    need(type(payload) is dict and type(payload.get('model')) is dict,'TINY_FIXTURE')
    model = payload['model']
    if payload.get('expected') == 'FEASIBLE':
        _,expected,_,_ = rook_objects(budget); model_identity(model,expected)
    elif payload.get('expected') == 'INFEASIBLE':
        parity = {'variables':1,'lower':[0],'upper':[1],'rows':[{'lower':1,'upper':1,'terms':[[0,2]]}]}
        cap = {'variables':1,'lower':[0],'upper':[1],'rows':[{'lower':2,'upper':2,'terms':[[0,1]]}]}
        need((same(model,parity) and payload.get('contradiction') == '2e=1 for integer e') or
             (same(model,cap) and payload.get('contradiction') == 'e=2 but 0<=e<=1'),'TINY_FIXTURE')
    else: raise Veto('TINY_FIXTURE')
    return {'hand_checked_fixture':True,'no_native_solver_call':True}


def author_action(name, payload, budget):
    if name.startswith('profile_'): return reconstruct(payload,budget)[0]
    if name in ('strict_json_integer_positive','json_duplicate','json_nonfinite'): return decode(payload['text'])
    if name.startswith('tiny_'): return tiny_fixture(payload,budget)
    corners = name == 'known_rook_zero_classes_omitted'
    forced = name in ('known_rook_sole1_full_capacities','candidate_forced_zero','candidate_forced_one')
    _,built,_,_ = rook_objects(budget,corners,forced)
    return check_candidate(built,payload,budget)


def synthetic_guidance(values, valid=True):
    xs = [float(x) for x in values]
    return {'schema':'FIXED17_AGGREGATE_EDGE_FLOW_NUMERIC_GUIDANCE_V1','native_version':'1.15.1',
        'numpy_version':'synthetic','run_status':'synthetic','model_status':'synthetic',
        'solution_value_valid':valid,'col_value':xs,'col_value_float_hex':[x.hex() for x in xs],
        'options':{'presolve':'on','solver':'choose','threads':1,'parallel':'off','random_seed':0,
            'mip_rel_gap':0.0,'mip_abs_gap':0.0,'mip_feasibility_tolerance':1e-7,'primal_feasibility_tolerance':1e-7,
            'output_flag':True,'log_to_console':False,'log_file':'synthetic','time_limit':5.0},
        'wall_seconds':0.0,'objective_all_zero':True,'solver_calls':1,
        'floating_status_is_proof':False,'numeric_infeasibility_is_proof':False}


def own_routes(budget,out):
    free,built,witness,cps = rook_objects(budget)
    forced,fixed,fixed_witness,_ = rook_objects(budget,forced=True)
    _,zero,zero_witness,_ = rook_objects(budget,corners=True)
    payloads = [witness,fixed_witness,zero_witness,{'text':'{"count":2,"zero":0}'},
        {'model':built,'expected':'FEASIBLE'},
        {'model':{'variables':1,'lower':[0],'upper':[1],'rows':[{'lower':1,'upper':1,'terms':[[0,2]]}]},
         'expected':'INFEASIBLE','contradiction':'2e=1 for integer e'},
        {'model':{'variables':1,'lower':[0],'upper':[1],'rows':[{'lower':2,'upper':2,'terms':[[0,1]]}]},
         'expected':'INFEASIBLE','contradiction':'e=2 but 0<=e<=1'}]
    edits = [
      (free,lambda x:x['counts'].__setitem__(0,True)),(free,lambda x:x['counts'].__setitem__(0,2.0)),
      (free,lambda x:x['counts'].__setitem__(0,-1)),(free,lambda x:x['support_adjacency'][0].__setitem__(1,True)),
      (free,lambda x:x['support_adjacency'][0].__setitem__(1,1.0)),(free,lambda x:x['support_adjacency'][0].__setitem__(1,0)),
      (free,lambda x:x['ordered_masks'].__setitem__(0,False)),(free,lambda x:x['ordered_masks'].__setitem__(0,1)),
      (free,lambda x:x['pair_bits'][0].__setitem__('bits',[False,1])),(free,lambda x:x['pair_bits'][1].__setitem__('j',0)),
      (witness,lambda x:x.__setitem__('schema','wrong')),(witness,lambda x:x['variable_pairs'].reverse()),
      (witness,lambda x:x['edge_counts'].__setitem__(0,True)),(witness,lambda x:x['edge_counts'].__setitem__(0,-1)),
      (witness,lambda x:x['edge_counts'].__setitem__(0,2)),(fixed_witness,lambda x:x['edge_counts'].__setitem__(6,1)),
      (fixed_witness,lambda x:x['edge_counts'].__setitem__(3,1)),(witness,lambda x:x['ordered_flow_matrix'][0].__setitem__(0,True)),
      (witness,lambda x:x['ordered_flow_matrix'][0].__setitem__(1,1)),(witness,lambda x:x['ordered_flow_matrix'][0].__setitem__(0,1)),
      (witness,lambda x:x['ordered_flow_matrix'][0].__setitem__(0,0))]
    for original,edit in edits:
        changed = copy.deepcopy(original); edit(changed); payloads.append(changed)
    payloads += [from_edges(built,[0,2,2,2,1,2,0,1,0,0]),from_edges(built,[1,3,2,1,1,1,0,1,1,0]),
                 {'text':'{"x":1,"x":2}'},{'text':'{"x":NaN}'}]
    records = []
    def run(name,expected,payload,action):
        budget.tick(); ordinal = len(records)
        write(out/('control_%03d_%s.json'%(ordinal,name)),payload,budget)
        try: result = action(payload); stage = 'PASS'
        except Veto as exc: result,stage = None,str(exc)
        row = {'index':ordinal,'name':name,'expected_stage':expected,'actual_stage':stage,'matches':stage == expected}
        write(out/('stage_%03d.json'%ordinal),row,budget); records.append(row)
        need(stage == expected,'CONTROL_STAGE:'+name+':'+stage)
    for (name,stage),payload in zip(AUTHOR_ROUTES,payloads):
        run(name,stage,payload,lambda p,name=name:author_action(name,p,budget))
    need(len(payloads) == 32 and len(records) == 32,'AUTHOR_COUNTERPART_POPULATION')
    def altered(name,stage,original,edit,action):
        changed = copy.deepcopy(original); edit(changed); run(name,stage,changed,action)
    good = synthetic_guidance(witness['edge_counts']); missing = synthetic_guidance([],False)
    fractional = synthetic_guidance([0.5]+witness['edge_counts'][1:])
    absent = extraction(built,missing,budget)
    # Eleven independent positives beyond the seven author counterparts.
    run('positive_full_model','PASS',built,lambda x:model_identity(x,built))
    run('positive_zero_class_model','PASS',zero,lambda x:model_identity(x,zero))
    singleton = copy.deepcopy(free); singleton['pair_bits'][-1]['bits'] = []
    run('positive_empty_singleton_diagonal','PASS',singleton,lambda x:reconstruct(x,budget))
    run('positive_dense_integer_flow','PASS',witness,lambda x:check_candidate(built,x,budget))
    run('positive_checkpoint','PASS',cps[0],lambda x:checkpoint_identity(x,cps[0]))
    run('positive_guidance_hex','PASS',good,lambda x:guidance_checked(x,built,budget,5))
    run('positive_absent_incumbent','PASS',absent,lambda x:absent_identity(x,absent))
    run('positive_fractional_no_integer_claim','PASS',fractional,lambda x:extraction(built,x,budget))
    rt = synthetic_runtime()
    run('positive_actual_shaped_593_runtime','PASS',rt,lambda x:runtime(x['plan'],x['manifest'],x['terminal'],x['summary'],
        'calibrate',{'source':'pin','spec':'pin'}))
    run('positive_save_reserve','PASS',{'stop_required':False,'remaining_seconds':21.0},reserve)
    run('positive_json_array','PASS',{'text':'[0,1,2]'},lambda x:decode(x['text']))
    # Twenty-three precise independent negative routes.
    altered('candidate_edge_float','CANDIDATE_INTEGER',witness,lambda x:x['edge_counts'].__setitem__(0,1.0),
        lambda x:check_candidate(built,x,budget))
    altered('candidate_matrix_float','CANDIDATE_ORDERED_DOMAIN',witness,lambda x:x['ordered_flow_matrix'][0].__setitem__(0,2.0),
        lambda x:check_candidate(built,x,budget))
    altered('candidate_matrix_missing','CANDIDATE_ORDERED_DOMAIN',witness,lambda x:x['ordered_flow_matrix'].pop(),
        lambda x:check_candidate(built,x,budget))
    altered('model_sparse_coefficient','MODEL_RECONSTRUCTION',built,lambda x:x['rows'][0]['terms'][0].__setitem__(1,1),lambda x:model_identity(x,built))
    altered('model_capacity','MODEL_RECONSTRUCTION',built,lambda x:x['capacities'].__setitem__(0,2),lambda x:model_identity(x,built))
    altered('model_diagonal_flag','MODEL_RECONSTRUCTION',built,lambda x:x.__setitem__('diagonal_row_coefficient',1),lambda x:model_identity(x,built))
    altered('checkpoint_late_count','CHECKPOINT_PREFIX',cps[0],lambda x:x.__setitem__('positive_classes_completed',5),lambda x:checkpoint_identity(x,cps[0]))
    altered('guidance_bool','GUIDANCE_VALUES',good,lambda x:x['col_value'].__setitem__(0,True),lambda x:guidance_checked(x,built,budget,5))
    altered('guidance_hex','GUIDANCE_HEX',good,lambda x:x['col_value_float_hex'].__setitem__(0,'wrong'),lambda x:guidance_checked(x,built,budget,5))
    def nonfinite_action(payload):
        changed = copy.deepcopy(payload['guidance']); changed['col_value'][0] = float(payload['value'])
        return guidance_checked(changed,built,budget,5)
    run('guidance_float_nonfinite','GUIDANCE_VALUES',{'guidance':good,'value':'inf'},nonfinite_action)
    altered('absent_infeasibility_claim','EXTRACTION_IDENTITY',absent,lambda x:x.__setitem__('infeasibility_proved',True),lambda x:absent_identity(x,absent))
    rt_action = lambda x:runtime(x['plan'],x['manifest'],x['terminal'],x['summary'],'calibrate',{'source':'pin','spec':'pin'})
    altered('runtime_wrong_source','RUNTIME_MANIFEST',rt,lambda x:x['manifest'].__setitem__('source_sha256','wrong'),rt_action)
    altered('runtime_bool_exit','RUNTIME_CLEANUP',rt,lambda x:x['terminal']['cleanup'].__setitem__('actual_exit_code',False),rt_action)
    altered('runtime_elapsed_type','RUNTIME_ELAPSED',rt,lambda x:x['terminal'].__setitem__('elapsed_seconds',True),rt_action)
    run('directory_file','PRODUCER_OUTPUT_DIRECTORY',str(out/'control_000_known_rook_aggregate_multiplicities.json'),lambda x:output_directory(x,out))
    run('reserve_boundary','SAVE_RESERVE',{'stop_required':False,'remaining_seconds':20.0},reserve)
    run('reserve_stop','SAVE_RESERVE',{'stop_required':True,'remaining_seconds':21.0},reserve)
    run('nested_plan_wrong_schema','RUNTIME_PLAN_SCHEMA',{'schema':'invented','calibration':rt['plan']},lambda x:runtime_profile(x,'calibrate'))
    nested = {'schema':'FIXED17_AGGREGATE_EDGE_FLOW_CONCRETE_PLAN_V1','solve':rt['plan'],**rt['plan']}
    altered('science_alias_mismatch','RUNTIME_PLAN_ALIASES',nested,lambda x:x.__setitem__('worker_argv',[]),lambda x:runtime_profile(x,'solve'))
    altered('profile_empty_positive_pair','PROFILE_INCOMPATIBLE_COEXISTENCE',free,
        lambda x:x['pair_bits'][0].__setitem__('bits',[]),lambda x:reconstruct(x,budget))
    altered('guidance_validity_bool','GUIDANCE_VALIDITY',good,lambda x:x.__setitem__('solution_value_valid',1),lambda x:guidance_checked(x,built,budget,5))
    altered('guidance_scope_proof','GUIDANCE_SCOPE',good,lambda x:x.__setitem__('floating_status_is_proof',True),lambda x:guidance_checked(x,built,budget,5))
    altered('candidate_pair_bool','CANDIDATE_VARIABLE_ORDER',witness,lambda x:x['variable_pairs'][0].__setitem__(0,False),
        lambda x:check_candidate(built,x,budget))
    # The original66 actions remain; new actual-shaped native checkpoint helper controls.
    checkpoints = synthetic_native_checkpoints(built,good)
    check_cp = lambda p:native_checkpoints(p['before'],p['after'],p['guidance'],built,5)
    run('positive_actual_status_native_checkpoints','PASS',checkpoints,check_cp)
    altered('native_before_legacy_scalar','NATIVE_BEFORE_DEADLINE',checkpoints,
        lambda p:p['before'].__setitem__('remaining',100.0),check_cp)
    altered('native_before_remaining_bool','NATIVE_BEFORE_DEADLINE',checkpoints,
        lambda p:p['before']['remaining'].__setitem__('remaining_seconds',True),check_cp)
    altered('native_before_stop_integer','NATIVE_BEFORE_DEADLINE',checkpoints,
        lambda p:p['before']['remaining'].__setitem__('stop_required',0),check_cp)
    altered('native_after_legacy_scalar','NATIVE_AFTER_DEADLINE',checkpoints,
        lambda p:p['after'].__setitem__('remaining',99.0),check_cp)
    altered('native_after_stop_true','NATIVE_AFTER_DEADLINE',checkpoints,
        lambda p:p['after']['remaining'].__setitem__('stop_required',True),check_cp)
    altered('native_before_missing_status_key','NATIVE_BEFORE_DEADLINE',checkpoints,
        lambda p:p['before']['remaining'].pop('review_due'),check_cp)
    altered('native_reversed_elapsed','NATIVE_DEADLINE_ORDER',checkpoints,
        lambda p:p['after']['remaining'].__setitem__('elapsed_seconds',0.0),check_cp)
    return records


def own_header(raw,software,mode):
    need(type(raw) is dict and raw.get('status') == (CAL_STATUS if mode == 'calibrate' else CONTROLS_STATUS)
         and raw.get('mode') == mode and type(raw.get('implementation_version')) is int and raw['implementation_version'] == 2
         and raw.get('producer') == '/root/checkpoint_audit' and raw.get('verifier') == '/root/native_driver'
         and raw.get('method') == 'independent_artifact_check' and raw.get('target_resolution') == 'NONE'
         and raw.get('actual_target_input_read') is False and same(raw.get('source_software'),software),'OWN_HEADER')
    need(same(raw.get('outcome',{}).get('counts'),OWN_COUNTS if mode == 'calibrate' else AUTHOR_COUNTS)
         and raw['outcome'].get('all_precise_stages_match') is True,'OWN_SCOPE')


def qualify(reader,args,software):
    summary,base = packet(reader,args.calibration,args.calibration_sha256)
    own_header(summary,software,'calibrate'); need(same(summary.get('inputs_sha256'),software),'OWN_SOFTWARE')
    rows = reader.read(base/'controls.json',summary['outputs_sha256']['controls.json'])
    need(type(rows) is list and len(rows) == OWN_COUNTS['total'] and all(type(row) is dict and
         type(row.get('index')) is int and row['index'] == i and row.get('matches') is True and
         row.get('expected_stage') == row.get('actual_stage') for i,row in enumerate(rows)), 'OWN_STAGE_TABLE')


def source_packet(reader,args,mode):
    plan = reader.read(args.producer_plan,args.producer_plan_sha256)
    summary,base = packet(reader,args.producer_summary,args.producer_summary_sha256)
    need(summary.get('schema') == 'FIXED17_AGGREGATE_EDGE_FLOW_PRODUCER_REPORT_V1'
         and type(summary.get('implementation_version')) is int and summary['implementation_version'] == 1
         and summary.get('mode') == mode and summary.get('producer') == '/root/checkpoint_audit'
         and summary.get('source_author') == '/root/checkpoint_audit' and summary.get('independent_approval') is False
         and summary.get('target_resolution') == 'NONE' and summary.get('automatic_retry') is False
         and summary.get('actual_count_input_read') is (mode == 'solve'),'PRODUCER_HEADER')
    need(same(summary.get('source_software'),AUTHOR_SOFTWARE),'PRODUCER_SOFTWARE')
    declared = summary.get('inputs_sha256')
    need(type(declared) is dict and all(type(p) is str and type(h) is str and len(h) == 64 and
         all(c in '0123456789abcdef' for c in h) for p,h in declared.items()) and
         all(declared.get(p) == h for p,h in AUTHOR_SOFTWARE.items()),'PRODUCER_DECLARED_INPUTS')
    reader.map(AUTHOR_SOFTWARE)
    manifest = reader.read(args.producer_manifest,args.producer_manifest_sha256)
    terminal = reader.read(args.producer_terminal,args.producer_terminal_sha256)
    flags = runtime(runtime_profile(plan,mode),manifest,terminal,summary,mode,
        {'source':AUTHOR_SOFTWARE[PRODUCER],'spec':AUTHOR_SOFTWARE[PRODUCER_SPEC]})
    output_directory(flags['--out'],base)
    if mode == 'calibrate':
        need(summary.get('status') == 'FIXED17_AGGREGATE_EXTERIOR_EDGE_FLOW_V1_AUTHOR_CONTROLS_PASS'
             and same(declared,AUTHOR_SOFTWARE),'PRODUCER_STATUS')
    else:
        need(summary.get('status') in ('CANDIDATE_FIXED17_AGGREGATE_INTEGER_EDGE_FLOW_V1','NO_EXACT_AGGREGATE_FLOW_WITNESS_V1'), 'PRODUCER_STATUS')
    return summary,base,flags


def checkpoint_status(raw, stage):
    keys = {'elapsed_seconds','remaining_seconds','review_remaining_seconds','review_due','review_overdue_seconds',
            'deadline_reached','stop_required','deadline_at','review_deadline_at','completed_reviews'}
    numbers = keys-{'review_due','deadline_reached','stop_required','completed_reviews'}
    need(type(raw) is dict and set(raw) == keys and all(type(raw[k]) in (int,float) and
         math.isfinite(raw[k]) and raw[k] >= 0 for k in numbers) and
         all(raw[k] is False for k in ('review_due','deadline_reached','stop_required')) and
         type(raw['completed_reviews']) is int and raw['completed_reviews'] >= 0 and
         raw['remaining_seconds'] > 20 and raw['review_remaining_seconds'] > 0 and raw['review_overdue_seconds'] == 0,
         stage)


def synthetic_native_checkpoints(built, guidance):
    def status(elapsed,remaining):
        return {'elapsed_seconds':elapsed,'remaining_seconds':remaining,'review_remaining_seconds':1800.0-elapsed,
                'review_due':False,'review_overdue_seconds':0.0,'deadline_reached':False,'stop_required':False,
                'deadline_at':101.0,'review_deadline_at':1800.0,'completed_reviews':0}
    return {'before':{'variables':built['variables'],'rows':len(built['rows']),
        'nnz':sum(len(row['terms']) for row in built['rows']),'proposed_options':copy.deepcopy(guidance['options']),
        'remaining':status(1.0,100.0),'native_limit_finalized_after_checkpoint':True},
        'after':{'native_status':guidance['run_status'],'model_status':guidance['model_status'],
            'wall_seconds':guidance['wall_seconds'],'remaining':status(2.0,99.0),'is_proof':False},
        'guidance':guidance}

def native_checkpoints(before,after,guidance,built,maximum):
    need(type(before) is dict and set(before) == {'variables','rows','nnz','proposed_options','remaining',
        'native_limit_finalized_after_checkpoint'} and type(before['variables']) is int and
        before['variables'] == built['variables'] and type(before['rows']) is int and before['rows'] == len(built['rows'])
        and type(before['nnz']) is int and before['nnz'] == sum(len(row['terms']) for row in built['rows'])
        and before['native_limit_finalized_after_checkpoint'] is True, 'NATIVE_BEFORE_CHECKPOINT')
    checkpoint_status(before['remaining'],'NATIVE_BEFORE_DEADLINE')
    expected_options = dict(guidance['options']); expected_options['time_limit'] = float(maximum)
    need(same(before['proposed_options'],expected_options),'NATIVE_OPTIONS_CHECKPOINT')
    need(type(after) is dict and set(after) == {'native_status','model_status','wall_seconds','remaining','is_proof'}
         and after['native_status'] == guidance['run_status'] and after['model_status'] == guidance['model_status']
         and same(after['wall_seconds'],guidance['wall_seconds']) and after['is_proof'] is False, 'NATIVE_AFTER_CHECKPOINT')
    checkpoint_status(after['remaining'],'NATIVE_AFTER_DEADLINE')
    a,b = before['remaining'],after['remaining']
    need(b['elapsed_seconds'] >= a['elapsed_seconds'] and b['remaining_seconds'] <= a['remaining_seconds']
         and same(a['deadline_at'],b['deadline_at']) and same(a['review_deadline_at'],b['review_deadline_at'])
         and a['completed_reviews'] == b['completed_reviews'], 'NATIVE_DEADLINE_ORDER')


def replay_controls(reader,summary,base,out):
    expected_scope = {**AUTHOR_COUNTS,'all_precise_stages_match':True,'tiny_native_calls':3,
        'actual_count_input_read':False,'actual_model_generated':False,'known_rook_positive_classes':4,
        'known_rook_unordered_variables':10,'known_rook_rows':12,'graph_completion':False}
    need(same(summary.get('outcome'),expected_scope),'AUTHOR_SCOPE')
    outputs = summary['outputs_sha256']; names = {'controls.json'}; pairs = []
    def load(name):
        names.add(name); need(name in outputs,'AUTHOR_PAYLOAD'); return reader.read(base/name,outputs[name])
    rows = load('controls.json'); need(type(rows) is list and len(rows) == 32,'AUTHOR_STAGE_POPULATION')
    for index,(name,expected) in enumerate(AUTHOR_ROUTES):
        payload = load('control_%03d_%s.json'%(index,name))
        result = None
        try: result = author_action(name,payload,reader.budget); stage = 'PASS'
        except Veto as exc: stage = str(exc)
        row = rows[index]
        desired = {'index':index,'name':name,'expected_stage':expected,'actual_stage':expected,'matches':True}
        need(same(row,desired) and same(load('stage_%03d.json'%index),desired),'AUTHOR_STAGE_ROW')
        need(stage == expected,'AUTHOR_INDEPENDENT_STAGE')
        if index < 7:
            returned = load('result_%03d.json'%index)
            if index in (4,5,6):
                prefix = {4:'tiny_rook',5:'tiny_parity',6:'tiny_capacity'}[index]
                guidance = load(prefix+'_guidance.json'); before = load(prefix+'_before_solver.json')
                after = load(prefix+'_after_solver.json'); names.add(prefix+'_solver.log')
                built = payload['model']; guidance_checked(guidance,built,reader.budget,5)
                native_checkpoints(before,after,guidance,built,5)
                if index == 4:
                    exact = extraction(built,guidance,reader.budget)
                    need(exact['candidate'] is not None,'TINY_NATIVE_FIXTURE')
                    result = {'guidance':guidance,'exact':exact,'synthetic_only':True}
                else:
                    need(guidance['model_status'] == 'HighsModelStatus.kInfeasible','TINY_NATIVE_FIXTURE')
                    # Known integer contradictions are independently established by literal coefficients.
                    result = {'guidance':guidance,'numeric_status_is_not_a_scientific_proof':True,
                              'known_fixture_contradiction':payload['contradiction']}
            need(same(returned,result),'AUTHOR_RETURNED_RESULT')
            write(out/('independent_result_%03d.json'%index),result,reader.budget)
        pairs.append({'index':index,'name':name,'expected_stage':expected,'producer_stage':row['actual_stage'],
                      'independent_stage':stage,'matches':True})
    need(len(names) == 84 and set(outputs) == names,'AUTHOR_OUTPUT_POPULATION')
    write(out/'independent_stage_pairs.json',pairs,reader.budget)
    return {'counts':AUTHOR_COUNTS,'all_precise_stages_match':True,'producer_physical_files':85,
        'producer_output_hashes':84,'complete_rook_flows':3,'complete_tiny_native_receipts':3,
        'solver_calls':0,'actual_target_input_read':False,'graph_completion':False}


def direct_premises(reader):
    reader.map(PREMISES)
    trusted = reader.read(TRUSTED_PROFILE,TRUSTED_PROFILE_SHA)
    prefix = 'acceleration/results/20261004_independent_review/'
    for name,status,implementation,producer in (
        ('external_moment_integer_counts_full01','INDEPENDENT_EXTERNAL_MOMENT_INTEGER_COUNTS_V1_COMPLETE_PASS',1,'/root/checkpoint_audit'),
        ('fixed17_dual_gram_pairs_full02','INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS',2,'/root/structural'),
        ('fixed17_count_neighbor_capacity_full01','INDEPENDENT_FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_COMPLETE_PASS',1,'/root/checkpoint_audit')):
        path = prefix+name+'/summary.json'; raw = reader.read(path,PREMISES[path])
        need(raw.get('status') == status and raw.get('mode') == 'full' and type(raw.get('implementation_version')) is int
             and raw['implementation_version'] == implementation and raw.get('producer') == producer
             and raw.get('verifier') == '/root/native_driver' and raw.get('method') == 'independent_artifact_check'
             and raw.get('target_resolution') == 'NONE','PREMISE_GATE')
        if name.startswith('fixed17_count_neighbor'):
            need(raw.get('inputs_sha256',{}).get(TRUSTED_PROFILE) == TRUSTED_PROFILE_SHA and
                 raw.get('outcome',{}).get('all_screens_pass') is True,'PROFILE_PREMISE')
        if name.startswith('external_moment'):
            cp = 'acceleration/results/20261004_fixed17_integer_type_counts01/exact_integer_candidate.json'
            need(raw.get('inputs_sha256',{}).get(cp) == PREMISES[cp] and raw.get('outcome',{}).get('candidate_exact_checked') is True,'COUNT_PREMISE')
    cp = 'acceleration/results/20261004_fixed17_integer_type_counts01/exact_integer_candidate.json'
    count = reader.read(cp,PREMISES[cp])
    need(same(count.get('ordered_masks'),trusted.get('ordered_masks')) and same(count.get('counts'),trusted.get('counts')),'COUNT_PROFILE_IDENTITY')
    theorem_path = prefix+'target_exterior_type_edge_moments01/summary.json'
    theorem = reader.read(theorem_path,PREMISES[theorem_path])
    need(theorem.get('status') == 'INDEPENDENT_TARGET_EXTERIOR_TYPE_NEIGHBOR_PROFILES_AND_EDGE_MOMENTS_V1_WRITTEN_PASS'
         and theorem.get('claim_id') == 'C-TARGET-EXTERIOR-TYPE-NEIGHBOR-PROFILES-AND-EDGE-MOMENTS'
         and type(theorem.get('claim_revision')) is int and theorem['claim_revision'] == 1
         and theorem.get('producer') == '/root/structural' and theorem.get('verifier') == '/root/native_driver'
         and theorem.get('method') == 'independent_derivation' and theorem.get('outcome') == 'PASS'
         and theorem.get('target_resolution') == 'NONE','BLOCK_PREMISE')
    return trusted


def configuration(reader,args,flags,software):
    controls,cbase = packet(reader,args.producer_controls,args.producer_controls_sha256)
    own_header(controls,software,'controls')
    need(controls.get('inputs_sha256',{}).get(safe(args.calibration).relative_to(ROOT).as_posix()) == args.calibration_sha256,
         'CONTROLS_CALIBRATION_PIN')
    config = reader.read(flags['--configuration'],flags['--configuration-sha256'])
    need(type(config) is dict and config.get('schema') == 'FIXED17_AGGREGATE_EDGE_FLOW_CONFIGURATION_V1'
         and config.get('target_resolution') == 'NONE' and type(config.get('inputs_sha256')) is dict,'CONFIG_HEADER')
    pins = config['inputs_sha256']
    for path,digest in {**PREMISES,**AUTHOR_SOFTWARE}.items(): need(pins.get(path) == digest,'CONFIG_DIRECT_PIN')
    for key,path,digest in (
        ('independent_checker_source',SELF,software[SELF]),('independent_checker_spec',SPEC,software[SPEC]),
        ('independent_calibration',args.calibration,args.calibration_sha256),
        ('independent_producer_controls',args.producer_controls,args.producer_controls_sha256)):
        name = config.get(key+'_path'); sha = config.get(key+'_sha256')
        need(type(name) is str and safe(name) == safe(path) and sha == digest and
             pins.get(safe(path).relative_to(ROOT).as_posix()) == digest,'CONFIG_QUALIFICATION_PIN')
    maximum = config.get('maximum_solver_seconds')
    need(type(maximum) is int and 0 < maximum <= 1500,'CONFIG_SOLVER_RANGE')
    author_path = config.get('author_calibration_path'); author_sha = config.get('author_calibration_sha256')
    need(type(author_path) is str and type(author_sha) is str and pins.get(safe(author_path).relative_to(ROOT).as_posix()) == author_sha
         and controls.get('inputs_sha256',{}).get(safe(author_path).relative_to(ROOT).as_posix()) == author_sha,'CONFIG_AUTHOR_PIN')
    author,abase = packet(reader,author_path,author_sha)
    need(author.get('status') == 'FIXED17_AGGREGATE_EXTERIOR_EDGE_FLOW_V1_AUTHOR_CONTROLS_PASS' and
         author.get('mode') == 'calibrate' and same(author.get('source_software'),AUTHOR_SOFTWARE),'AUTHOR_HEADER')
    need(all(type(p) is str and type(h) is str and len(h) == 64 and all(c in '0123456789abcdef' for c in h)
         for p,h in pins.items()),'CONFIG_PIN_SCHEMA')
    return direct_premises(reader),maximum,author,abase


def full(reader,args,summary,base,flags,out,software):
    need(args.producer_controls is not None and args.producer_controls_sha256 is not None,'CONTROLS_ARGUMENTS')
    trusted,maximum,author,abase = configuration(reader,args,flags,software)
    author_scope = replay_controls(reader,author,abase,out)
    names = set(); outputs = summary['outputs_sha256']
    def load(name):
        names.add(name); need(name in outputs,'SCIENTIFIC_PAYLOAD'); return reader.read(base/name,outputs[name])
    raw = load('parsed_aggregate_input.json'); need(same(raw,trusted),'TRUSTED_PROFILE_IDENTITY')
    built,cps = reconstruct(raw,reader.budget); model_identity(load('aggregate_model.json'),built)
    need(raw['target_order'] == 99 and raw['target_degree'] == 14 and len(raw['support_adjacency']) == 17
         and len(raw['ordered_masks']) == 472 and sum(raw['counts']) == 82 and len(built['positive_type_ids']) == 68
         and built['variables'] == 2346 and len(built['rows']) == 1224 and len(cps) == 9,'FIXED_SCOPE')
    for ordinal,expected in enumerate(cps): checkpoint_identity(load('model_checkpoint_%03d.json'%ordinal),expected)
    guidance = load('scientific_guidance.json'); guidance_checked(guidance,built,reader.budget,maximum)
    native_checkpoints(load('scientific_before_solver.json'),load('scientific_after_solver.json'),guidance,built,maximum)
    names.add('scientific_solver.log')
    extracted = extraction(built,guidance,reader.budget); absent_identity(load('extraction.json'),extracted)
    present = extracted['candidate'] is not None
    if present:
        candidate = load('exact_integer_edge_flow.json'); need(same(candidate,extracted['candidate']),'EXACT_CANDIDATE_IDENTITY')
        receipt = check_candidate(built,candidate,reader.budget)
        need(same(load('exact_flow_rows.json'),receipt['observations']),'EXACT_ROW_TABLE')
        write(out/'independent_exact_flow_rows.json',receipt,reader.budget)
    need(names == set(outputs) and len(names) == (18 if present else 16),'SCIENTIFIC_OUTPUT_POPULATION')
    expected = {'complete_input_type_count':472,'outside_copies':82,'positive_classes':68,
        'unordered_edge_variables':2346,'exact_equations':1224,'model_checkpoints':9,'scientific_solver_calls':1,
        'exact_integer_candidate_produced':present,'candidate_absent_reason':extracted.get('reason'),
        'numeric_model_status':guidance['model_status'],'coupled_integer_feasibility':'CANDIDATE' if present else 'UNKNOWN',
        'infeasibility_proved':False,'graph_completion':False,'no_equitable_profile_assumed':True}
    need(same(summary.get('outcome'),expected),'SCIENTIFIC_OUTCOME')
    need(summary['status'] == ('CANDIDATE_FIXED17_AGGREGATE_INTEGER_EDGE_FLOW_V1' if present else 'NO_EXACT_AGGREGATE_FLOW_WITNESS_V1'),'SCIENTIFIC_STATUS')
    write(out/'independent_aggregate_model.json',built,reader.budget)
    write(out/'independent_model_checkpoints.json',cps,reader.budget)
    return {'counts':AUTHOR_COUNTS,'all_precise_stages_match':True,'author_control_scope':author_scope,
        'complete_input_type_count':472,'outside_copies':82,'positive_classes':68,'unordered_edge_variables':2346,
        'complete_equations':1224,'model_checkpoints':9,'candidate_exact_checked':present,
        'integer_aggregate_feasible':True if present else None,
        'unknown_reason':None if present else 'No exact saved integer aggregate witness; no infeasibility conclusion',
        'all_capacities_and_pair_bits_checked':True,'diagonal_count_factor':2,'no_equitable_profile_assumed':True,
        'graph_completion':False,'count_witness_excluded':False,'numeric_status_is_proof':False,'solver_calls':0}


def calibrate(out,budget):
    rows = own_routes(budget,out)
    positives = sum(row['expected_stage'] == 'PASS' for row in rows)
    need(len(rows) == OWN_COUNTS['total'] and positives == OWN_COUNTS['positive'] and
         all(row['matches'] for row in rows),'OWN_POPULATION')
    write(out/'controls.json',rows,budget)
    return {'counts':OWN_COUNTS,'all_precise_stages_match':True,'actual_target_input_read':False,
            'solver_calls':0,'producer_imports':0,'graph_completion':False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',choices=('calibrate','controls','full'))
    for name in ('seconds','out','self-sha256','spec-sha256'):
        parser.add_argument('--'+name,required=True,type=float if name == 'seconds' else str)
    for name in ('calibration','producer-plan','producer-summary','producer-manifest','producer-terminal','producer-controls'):
        parser.add_argument('--'+name); parser.add_argument('--'+name+'-sha256')
    args = parser.parse_args(); budget = Budget(args.seconds); out = safe(args.out,False)
    need(out.is_relative_to(ROOT/'acceleration/results') and not out.exists(),'OUTPUT_FRESH'); out.mkdir(parents=True)
    reader = Reader(budget); software = {**SOFTWARE,SELF:args.self_sha256,SPEC:args.spec_sha256}
    try:
        reader.map(software)
        if args.mode == 'calibrate': outcome = calibrate(out,budget); status = CAL_STATUS
        else:
            for name in ('calibration','producer_plan','producer_summary','producer_manifest','producer_terminal'):
                need(getattr(args,name) is not None and getattr(args,name+'_sha256') is not None,'SOURCE_ARGUMENTS')
            qualify(reader,args,software)
            summary,base,flags = source_packet(reader,args,'calibrate' if args.mode == 'controls' else 'solve')
            if args.mode == 'controls': outcome = replay_controls(reader,summary,base,out); status = CONTROLS_STATUS
            else: outcome = full(reader,args,summary,base,flags,out,software); status = FULL_STATUS
        reader.closing(); outputs = {}
        for name in sorted(inventory(out,budget)):
            digest = hashlib.sha256()
            with (out/name).open('rb') as handle:
                while True:
                    budget.tick(); block = handle.read(1024*1024)
                    if not block: break
                    digest.update(block)
            outputs[name] = digest.hexdigest()
        report = {'status':status,'implementation_version':2,'mode':args.mode,'timestamp':datetime.now(timezone.utc).isoformat(),
            'producer':'/root/checkpoint_audit','verifier':'/root/native_driver','checking_source_author':'/root/native_driver',
            'method':'independent_artifact_check','target_resolution':'NONE','source_software':software,
            'inputs_sha256':dict(reader.pins),'outputs_sha256':outputs,'outcome':outcome,'command':[sys.executable,*sys.argv],
            'cwd':str(ROOT),'actual_target_input_read':args.mode == 'full','producer_imports':0,'solver_calls':0,
            'graph_completion':False,'automatic_retry':False,'deadline':budget.tick(),
            'shared_components':['Native218c/49f2 engineering reader/runtime source is copied explicitly, never imported',
                'Qualified468f/count37bc/pair ee9fa/capacity4f671/block910a are exact direct inherited premises',
                'Fresh endpoint-count sparse coefficients and independent dense class-flow equation evaluation',
                'Public rook geometry/wire/stage taxonomy shared; no producer functions/AST/HiGHS/NumPy execution'],
            'limitations':['Integer aggregate flow is only necessary; it is not per-copy symmetric adjacency or a99SRG',
                'Absent incumbent remains UNKNOWN; no numerical infeasibility/status or failure refutes counts or target',
                'Full authenticates own74 packet and independently replays32 author actions; own actions are not rerun by full',
                '20save guard is allocated intent; supported actual process/elapsed/cleanup receipt required',
                'Direct declared immutable premises inherited, no transitive Gram/count/pair crawler or fresh proof',
                'No formal/external/novelty/ledger/index/Git approval']}
        write(out/'summary.json',report,budget); reader.closing(); budget.tick()
        print(json.dumps({'status':status,'mode':args.mode}),flush=True)
    except Exception as exc:
        try:
            (out/'failure.json').write_text(json.dumps({'status':'FAILED_PRESERVED','stage':str(exc),
                'exception':type(exc).__name__,'inputs_sha256':reader.pins,'target_resolution':'NONE','automatic_retry':False,
                'timestamp':datetime.now(timezone.utc).isoformat()},indent=2,allow_nan=False)+'\n',encoding='utf8')
        except Exception: pass
        raise


if __name__ == '__main__': main()