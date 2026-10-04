"""SOURCE ONLY: distinct complete binary focal selector and matching verifier."""
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
SELF = 'acceleration/audit_20261004_fixed17_focal_selector_matching_v1.py'
SPEC = 'acceleration/audit_20261004_fixed17_focal_selector_matching_v1_spec.md'
PRODUCER = 'acceleration/solve_20261004_fixed17_focal_selector_matching_v1.py'
PRODUCER_SPEC = 'acceleration/solve_20261004_fixed17_focal_selector_matching_v1_spec.md'
CAL_STATUS = 'INDEPENDENT_FIXED17_FOCAL_SELECTOR_MATCHING_V1_CALIBRATION_PASS'
CONTROLS_STATUS = 'INDEPENDENT_FIXED17_FOCAL_SELECTOR_MATCHING_V1_PRODUCER_CONTROLS_PASS'
FULL_STATUS = 'INDEPENDENT_FIXED17_FOCAL_SELECTOR_MATCHING_V1_COMPLETE_PASS'
AUTHOR_COUNTS = {'positive':13,'negative':29,'total':42}
OWN_COUNTS = {'positive':20,'negative':51,'total':71}
TRUSTED_PROFILE = 'acceleration/results/20261004_fixed17_count_neighbor_capacity01/parsed_screen_input.json'
TRUSTED_PROFILE_SHA = '468f281bfc13a34a5c23ca2a6af9f8564954c826e0b9f7bddfad36a76832690e'
SOFTWARE = {
  "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
  "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
  "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
  "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
  "acceleration/solve_20261004_fixed17_focal_selector_matching_v1.py": "d1be8cf63cb3205169db26a92708f76103597091b3058760ab83edd94b2c1428",
  "acceleration/solve_20261004_fixed17_focal_selector_matching_v1_spec.md": "0f0afa61109f4763567d0a24c687254a3be647cb2cf568fa254443c9eb50a87a",
  "acceleration/audit_20261004_fixed17_focal_neighbor_integer_v1.py": "218c0a282b17c0b37689dd27897422470308f6f0f9a0ced8320ae31aa5462c13",
  "acceleration/audit_20261004_fixed17_count_neighbor_capacity_v1.py": "ee985db1c2c54408b7eb18bdc997af6586d4d437ae0f9a9e8af5a56b1b91b24f"
}
AUTHOR_SOFTWARE = {
  "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
  "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
  "acceleration/solve_20261004_fixed17_focal_selector_matching_v1.py": "d1be8cf63cb3205169db26a92708f76103597091b3058760ab83edd94b2c1428",
  "acceleration/solve_20261004_fixed17_focal_selector_matching_v1_spec.md": "0f0afa61109f4763567d0a24c687254a3be647cb2cf568fa254443c9eb50a87a",
  "build/research-venv/Lib/site-packages/highspy-1.15.1.dist-info/METADATA": "cc09b9d5bf93d8cd79be21bede4e72b686d79cdc75f6524e0e0a1af3e9487a8d",
  "build/research-venv/Lib/site-packages/highspy/__init__.py": "01df06ec93388a45de66adb43d4b243cd7e11c54f24106064a221facf6aa7eb9",
  "build/research-venv/Lib/site-packages/highspy/_core.cp312-win_amd64.pyd": "f733d7369f647f8afe481bbaf569164f7cd7c127e41ca53cd7c205c2fb9038e2",
  "build/research-venv/Lib/site-packages/highspy/_core/__init__.pyi": "53c07e5eafff940daa32458b20262b07d39420b062e0875c2f56e9ac92f4d699",
  "build/research-venv/Lib/site-packages/highspy/highs.py": "00ce58ef248062125309ccdaf7af6374caf1a29f6a04e0d637b7507ead34d51a",
  "build/research-venv/Lib/site-packages/numpy-2.5.3.dist-info/METADATA": "451a9b8028000588e66b0b415587b6aef0bbc51a96d8e8a0cba0dc23acf64f99",
  "build/research-venv/Lib/site-packages/numpy/__init__.py": "a6958cb364663b7acce81ccfd58eeb65a2b34d5376157f924777b97211a73be4",
  "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
  "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db"
}
PREMISES = {
  "acceleration/results/20261004_fixed17_count_neighbor_capacity01/parsed_screen_input.json": "468f281bfc13a34a5c23ca2a6af9f8564954c826e0b9f7bddfad36a76832690e",
  "acceleration/results/20261004_independent_review/fixed17_count_neighbor_capacity_full01/summary.json": "4f6711cba2450262709ba0724bbd9bdbba3c95934c85265479985be7a38decb3",
  "acceleration/results/20261004_fixed17_count_neighbor_capacity_full_root_actual_acceptance01.json": "d8eaf7c2cb41a0bd8f1287b652edcbcc498b97f3475575b6e3b0d77e5d655017",
  "acceleration/results/20261004_independent_review/external_moment_integer_counts_full01/summary.json": "37bcf42a3b5e358c4306c642e152e3e605a07dc305de71b2272e455e377bd6b8",
  "acceleration/results/20261004_independent_review/fixed17_dual_gram_pairs_full02/summary.json": "ee9fa8961415df0e5f0ca429c33fc95a1d6223b77ec68e2c9ec71cc1dec0e218",
  "acceleration/results/20261004_independent_review/target_exterior_type_edge_moments01/summary.json": "910a740aff6ecd90515af7de0a2743abab47eabe902274237b3b70e1d0fdc6d6",
  "docs/CANDIDATE_20261004_FOCAL_NEIGHBOR_MATCHING_NECESSITY_V1.md": "30be5b396aadf848e73ad24ae3c49a9a2734d9b62944f756d057a95843b57858",
  "acceleration/audit_20261004_focal_neighbor_matching_structural_v1.md": "ee5641a7be52bce09de0e9f00078d252f8107b6461c5ddec7a2b22afc69799a5",
  "acceleration/results/20261004_independent_review/focal_neighbor_matching_necessity01/summary.json": "848d35933fe2b2876ac20631a3370a73d6696cd053a7e07004b113703220a7d3"
}
# The producer prerequisite requires its full thirteen software identities in
# checking gates; these backend bytes are authenticated, never executed here.
SOFTWARE.update(AUTHOR_SOFTWARE)

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
            'Independent selector matching model, binary labels and raw closure checking; all authentication and saves share the allocation')
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
         and flags.get('--executor') in ('/root','/root/structural'), 'RUNTIME_SOURCE')
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
    if schema == 'FIXED17_FOCAL_SELECTOR_MATCHING_SOURCE_ONLY_PLAN_V1':
        need(mode == 'calibrate', 'RUNTIME_PLAN_SCHEMA')
        value = plan.get('calibration')
    elif schema == 'ROOT_FIXED17_FOCAL_SELECTOR_MATCHING_AUTHOR_CONTROLS_CONCRETE_V1':
        need(mode == 'calibrate', 'RUNTIME_PLAN_SCHEMA')
        value = plan
    elif schema == 'FIXED17_FOCAL_SELECTOR_MATCHING_CONCRETE_PLAN_V1':
        need(mode == 'solve', 'RUNTIME_PLAN_SCHEMA')
        value = plan.get('solve')
        need(type(value) is dict and all(same(plan.get(k),value.get(k)) for k in
             ('command','supervisor_argv','child_argv','worker_argv','allocation')), 'RUNTIME_PLAN_ALIASES')
    else:
        raise Veto('RUNTIME_PLAN_SCHEMA')
    need(type(value) is dict, 'RUNTIME_PLAN_PROFILE')
    return value


def profile(raw, budget=None):
    need(type(raw) is dict and set(raw) == {'target_order','target_degree','support_adjacency',
         'ordered_masks','counts','pair_bits'}, 'PROFILE_FIELDS')
    v,k,h = raw['target_order'],raw['target_degree'],raw['support_adjacency']
    need(type(v) is int and type(k) is int and 0 <= k < v, 'TARGET_INTEGER')
    need(type(h) is list and 1 <= len(h) <= 17 and
         all(type(row) is list and len(row) == len(h) for row in h), 'GRAPH_SHAPE')
    m = len(h)
    need(v > m and v-m <= 82 and all(type(x) is int and x in (0,1) for row in h for x in row)
         and all(h[u][u] == 0 and h[u][w] == h[w][u] for u in range(m) for w in range(m)), 'GRAPH_DOMAIN')
    masks,counts = raw['ordered_masks'],raw['counts']
    need(type(masks) is list and masks and all(type(t) is int and 0 <= t < 1<<m for t in masks), 'TYPE_MASK')
    need(masks == sorted(set(masks)), 'TYPE_ORDER')
    need(type(counts) is list and len(counts) == len(masks), 'COUNT_SHAPE')
    need(all(type(n) is int for n in counts), 'COUNT_INTEGER')
    need(all(0 <= n <= v-m for n in counts), 'COUNT_BOUND')
    need(sum(counts) == v-m, 'COUNT_SUM')
    n = len(masks)
    need(type(raw['pair_bits']) is list and len(raw['pair_bits']) == n*(n+1)//2, 'PAIR_POPULATION')
    pairs = {}; cursor = 0
    for i in range(n):
        if budget is not None: budget.tick()
        for j in range(i,n):
            item = raw['pair_bits'][cursor]; cursor += 1
            need(type(item) is dict and set(item) == {'i','j','bits'}, 'PAIR_KEYS')
            need(type(item['i']) is int and type(item['j']) is int and (item['i'],item['j']) == (i,j), 'PAIR_COORDINATES')
            bs = item['bits']
            need(type(bs) is list and all(type(a) is int and a in (0,1) for a in bs)
                 and bs == sorted(set(bs)), 'PAIR_BITS')
            pairs[i,j] = bs
    sets = [set(u for u in range(m) if mask>>u & 1) for mask in masks]
    return h,sets,counts,pairs


def reconstruct(raw, focal, budget, parsed=None):
    """Build from copy-label sets, then independently serialize the required wire."""
    h,sets,counts,bits = profile(raw,budget) if parsed is None else parsed
    need(type(focal) is int and 0 <= focal < len(counts), 'FOCAL_INDEX')
    need(counts[focal] > 0, 'FOCAL_POSITIVE')
    t = sets[focal]
    need(not any(h[a][b] for a in t for b in t), 'FOCAL_SUPPORT_INDEPENDENT')
    pool = sorted((j,c) for j,number in enumerate(counts) for c in range(number)
                  if (j,c) != (focal,0))
    slots = [list(label) for label in pool]; nq = len(slots)
    touch = [len(sets[j] & t) for j,c in pool]
    lo = [int(bits[min(j,focal),max(j,focal)] == [1]) for j,c in pool]
    hi = [int(1 in bits[min(j,focal),max(j,focal)] and touch[a] <= 1)
          for a,(j,c) in enumerate(pool)]
    reasons = [{'focal_bits':bits[min(j,focal),max(j,focal)],'focal_support_overlap':touch[a],
                'suppressed_by_overlap':touch[a] >= 2} for a,(j,c) in enumerate(pool)]
    eligible = []
    for a in range(nq):
        budget.tick()
        for b in range(a+1,nq):
            j,k = pool[a][0],pool[b][0]
            if not touch[a] and not touch[b] and sets[j].isdisjoint(sets[k]) and 1 in bits[min(j,k),max(j,k)]:
                eligible.append([a,b])
    pair_variable = {tuple(pair):nq+i for i,pair in enumerate(eligible)}
    rows = []
    def add(kind,terms,lower,upper,detail):
        rows.append({'index':len(rows),'kind':kind,'terms':terms,'lower':lower,'upper':upper,'detail':detail})
    residual = raw['target_degree'] - len(t)
    add('SELECTOR_DEGREE',[[a,1] for a in range(nq)],residual,residual,None)
    for u in range(len(h)):
        rhs = 2 - int(u in t) - len(t & {w for w,value in enumerate(h[u]) if value})
        add('SELECTOR_INCIDENCE',[[a,1] for a,(j,c) in enumerate(pool) if u in sets[j]],rhs,rhs,u)
    for a in range(nq):
        if touch[a] == 0:
            incident = [[nq+e,1] for e,pair in enumerate(eligible) if a in pair]
            add('MATCHING_DEGREE',[[a,-1],*incident],0,0,slots[a])
    for e,(a,b) in enumerate(eligible):
        add('MATCHING_SELECTED_COUPLING',[[nq+e,1],[a,-1]],None,0,[a,b])
        add('MATCHING_SELECTED_COUPLING',[[nq+e,1],[b,-1]],None,0,[a,b])
    for a in range(nq):
        budget.tick()
        for b in range(a+1,nq):
            j,k = pool[a][0],pool[b][0]
            allowed = bits[min(j,k),max(j,k)]; overlap = len(sets[j] & sets[k])
            variable = pair_variable.get((a,b))
            if len(allowed) == 0 or overlap >= 2 or (allowed == [1] and variable is None):
                add('PAIR_JOINT_BAN',[[a,1],[b,1]],None,1,
                    {'slots':[a,b],'allowed_bits':allowed,'support_overlap':overlap})
            elif allowed == [1]:
                add('SELECTED_FORCED_EDGE',[[a,1],[b,1],[variable,-1]],None,1,{'slots':[a,b]})
    nv = nq + len(eligible)
    need(nq <= 81 and len(eligible) <= 3240 and nv <= 3321 and len(rows) <= 9819, 'MODEL_SIZE_BOUND')
    return {'schema':'FIXED17_FOCAL_SELECTOR_MATCHING_MODEL_V1','focal_type':focal,'focal_label':[focal,0],
        'support_size':len(h),'target_degree':raw['target_degree'],'focal_mask':raw['ordered_masks'][focal],
        'ordered_masks':raw['ordered_masks'],'counts':counts,'selector_slots':slots,'selector_reasons':reasons,
        'matching_slot_pairs':eligible,'selector_variables':nq,'matching_variables':len(eligible),'variables':nv,
        'lower':lo+[0]*len(eligible),'upper':hi+[1]*len(eligible),'rows':rows,'incidence_equalities':len(h)+1,
        'same_type_uniform_profiles':False,'all_pair_masks_enforced':True,'graph_completion':False}


def first_bound(model):
    for variable in range(model['variables']):
        lower,upper = model['lower'][variable],model['upper'][variable]
        if lower > upper:
            return {'kind':'STRUCTURAL_SELECTOR_BOUND','variable':variable,'lower':lower,'upper':upper}
    for row in model['rows']:
        minimum = maximum = 0
        for index,coefficient in row['terms']:
            a,b = coefficient*model['lower'][index],coefficient*model['upper'][index]
            minimum += min(a,b); maximum += max(a,b)
        if (row['lower'] is not None and maximum < row['lower']) or (row['upper'] is not None and minimum > row['upper']):
            return {'kind':'EXACT_ROW_INTERVAL_BOUND','row':row['index'],'row_kind':row['kind'],
                'attainable_minimum':minimum,'attainable_maximum':maximum,'lower':row['lower'],'upper':row['upper']}
    return None


def binary_rows(model, values, budget):
    need(type(values) is list and len(values) == model['variables'], 'BINARY_SHAPE')
    need(all(type(x) is int for x in values), 'BINARY_INTEGER')
    need(all(x == 0 or x == 1 for x in values), 'BINARY_BOUND')
    need(all(model['lower'][i] <= x <= model['upper'][i] for i,x in enumerate(values)), 'SELECTOR_BOUND')
    checked = []
    for row in model['rows']:
        budget.tick(); lhs = sum(values[index]*coefficient for index,coefficient in row['terms'])
        need((row['lower'] is None or row['lower'] <= lhs) and
             (row['upper'] is None or lhs <= row['upper']), row['kind'])
        checked.append({'index':row['index'],'kind':row['kind'],'lhs':lhs,
                        'lower':row['lower'],'upper':row['upper'],'exact':True})
    return checked


def labels_values(model, selected, matched, budget):
    need(type(selected) is list and all(type(label) is list and len(label) == 2 for label in selected), 'SELECTED_SHAPE')
    need(all(type(v) is int for label in selected for v in label), 'LABEL_INTEGER')
    need(model['focal_label'] not in selected, 'SELECTED_SELF')
    need(selected == sorted(selected) and len(set(tuple(p) for p in selected)) == len(selected), 'SELECTED_ORDER')
    slot = {tuple(label):i for i,label in enumerate(model['selector_slots'])}
    need(all(tuple(label) in slot for label in selected), 'SELECTED_CAPACITY')
    need(type(matched) is list and all(type(edge) is list and len(edge) == 2 and
         all(type(label) is list and len(label) == 2 for label in edge) for edge in matched), 'MATCHING_SHAPE')
    need(all(type(v) is int for edge in matched for label in edge for v in label), 'MATCHING_INTEGER')
    need(matched == sorted(matched) and len(set(tuple(tuple(p) for p in edge) for edge in matched)) == len(matched)
         and all(edge[0] < edge[1] for edge in matched), 'MATCHING_ORDER')
    variables = {tuple(edge):model['selector_variables']+i for i,edge in enumerate(model['matching_slot_pairs'])}
    result = [0]*model['variables']
    for label in selected: result[slot[tuple(label)]] = 1
    for left,right in matched:
        need(tuple(left) in slot and tuple(right) in slot, 'MATCHING_EDGE_NOT_ELIGIBLE')
        pair = tuple(sorted([slot[tuple(left)],slot[tuple(right)]]))
        need(pair in variables, 'MATCHING_EDGE_NOT_ELIGIBLE'); result[variables[pair]] = 1
    return result,binary_rows(model,result,budget)


def exact_witness(model, values, budget):
    checked = binary_rows(model,values,budget); nq = model['selector_variables']
    selected = [list(model['selector_slots'][i]) for i in range(nq) if values[i] == 1]
    matching = [[list(model['selector_slots'][a]),list(model['selector_slots'][b])]
                for e,(a,b) in enumerate(model['matching_slot_pairs']) if values[nq+e] == 1]
    # Reverse decoding is checked too; binary values never bypass label identity.
    decoded,again = labels_values(model,selected,matching,budget)
    need(same(decoded,values) and same(again,checked), 'BINARY_LABEL_IDENTITY')
    return {'schema':'FIXED17_EXACT_FOCAL_SELECTOR_MATCHING_WITNESS_V1','focal_type':model['focal_type'],
        'focal_label':model['focal_label'],'selected_labels':selected,'matching_pairs':matching,
        'binary_values':values,'all_sparse_rows':checked,'incidence_equalities':model['incidence_equalities'],
        'self_excluded':True,'all_bit0_and_overlap_cuts_checked':True,'matching_exact':True,
        'independent_approval':False,'graph_completion':False,'uniform_profiles':False}


def extraction(model, guidance, budget):
    need(type(guidance) is dict, 'NUMERIC_VECTOR')
    xs = guidance.get('col_value')
    need(type(xs) is list and all(type(x) is float and math.isfinite(x) for x in xs), 'NUMERIC_VECTOR')
    need(type(guidance.get('solution_value_valid')) is bool, 'NUMERIC_VALID_FLAG')
    if not guidance['solution_value_valid'] or len(xs) != model['variables']:
        return {'candidate':None,'reason':'No complete value-valid incumbent','numeric_infeasibility_is_proof':False}
    integral = [round(x) for x in xs]
    distance = max([abs(x-integral[i]) for i,x in enumerate(xs)],default=0)
    if distance > 1e-7:
        return {'candidate':None,'reason':'Nonintegral coordinate','maximum_distance':distance,'numeric_infeasibility_is_proof':False}
    try:
        w = exact_witness(model,integral,budget)
    except Veto as exc:
        if str(exc) == 'SAVE_RESERVE': raise
        return {'candidate':None,'reason':'Exact extraction rejected: '+str(exc),'rounded_values':integral,
                'maximum_distance':distance,'numeric_infeasibility_is_proof':False}
    return {'candidate':w,'maximum_distance':distance,'independent_approval':False,'graph_completion':False}


def guidance_checked(raw, model, budget, maximum):
    need(type(raw) is dict and raw.get('schema') == 'FIXED17_SELECTOR_MATCHING_NUMERIC_GUIDANCE_V1'
         and raw.get('native_version') == '1.15.1' and raw.get('numpy_version') == '2.5.3'
         and type(raw.get('solver_calls')) is int and raw['solver_calls'] == 1
         and raw.get('objective_all_zero') is True and raw.get('floating_status_is_proof') is False
         and raw.get('numeric_infeasibility_is_proof') is False, 'GUIDANCE_HEADER')
    xs = raw.get('col_value')
    need(type(xs) is list and all(type(x) is float and math.isfinite(x) for x in xs), 'NUMERIC_VECTOR')
    need(type(raw.get('solution_value_valid')) is bool, 'NUMERIC_VALID_FLAG')
    need(same(raw.get('col_value_float_hex'),[x.hex() for x in xs]), 'GUIDANCE_HEX')
    elapsed = raw.get('wall_seconds')
    need(type(elapsed) in (int,float) and math.isfinite(elapsed) and elapsed >= 0, 'GUIDANCE_ELAPSED')
    opts = raw.get('options'); need(type(opts) is dict, 'GUIDANCE_OPTIONS')
    expected = {'presolve':'on','solver':'choose','threads':1,'parallel':'off','random_seed':0,
        'mip_rel_gap':0.0,'mip_abs_gap':0.0,'primal_feasibility_tolerance':1e-7,'mip_feasibility_tolerance':1e-7,
        'output_flag':True,'log_to_console':False}
    need(all(same(opts.get(k),v) for k,v in expected.items()), 'GUIDANCE_OPTIONS')
    limit = opts.get('time_limit')
    need(type(limit) in (int,float) and math.isfinite(limit) and 0 < limit <= maximum, 'GUIDANCE_TIME_LIMIT')
    need(type(opts.get('log_file')) is str and opts['log_file'], 'GUIDANCE_OPTIONS')
    need(type(raw.get('run_status')) is str and type(raw.get('model_status')) is str, 'GUIDANCE_HEADER')
    return float(elapsed)


def fixture_checked(payload, budget):
    model = reconstruct(payload['profile'],payload['focal'],budget)
    values,rows = labels_values(model,payload['selected_labels'],payload['matching_pairs'],budget)
    return {'model':model,'witness':exact_witness(model,values,budget),'checked_rows':rows}


AUTHOR_ROUTES = [
    ('rook_empty_T_free','PASS'),('rook_empty_T_forced','PASS'),('rook_singleton_T','PASS'),
    ('rook_independent_two_T','PASS'),('rook_repeated_empty_and_singleton_selected_types','PASS'),
    ('absent_incumbent_unknown','PASS'),('nonintegral_incumbent_unknown','PASS'),
    ('binary_but_row_invalid_unknown','PASS'),('budget_above_reserve','PASS'),
    ('native_tiny_fixed_binary','PASS'),('native_tiny_parity_unknown','PASS'),('native_rook_forced_matching','PASS'),
    ('explicit_forced_focal_overlap_conflict','PASS'),('count_bool','COUNT_INTEGER'),('count_sum','COUNT_SUM'),
    ('mask_bool','TYPE_MASK'),('graph_bool','GRAPH_DOMAIN'),('pair_coordinate_bool','PAIR_COORDINATES'),
    ('pair_bits_bool','PAIR_BITS'),('pair_missing','PAIR_POPULATION'),('focal_bool','FOCAL_INDEX'),
    ('nonindependent_focal_T','FOCAL_SUPPORT_INDEPENDENT'),('binary_bool','BINARY_INTEGER'),
    ('binary_float','BINARY_INTEGER'),('binary_two','BINARY_BOUND'),('selected_focal_self','SELECTED_SELF'),
    ('selected_duplicate','SELECTED_ORDER'),('selected_copy_outside_count','SELECTED_CAPACITY'),
    ('selected_wrong_degree','SELECTOR_DEGREE'),('edge_support_overlap_one','MATCHING_EDGE_NOT_ELIGIBLE'),
    ('matching_edge_missing','MATCHING_DEGREE'),('matching_edge_duplicate','MATCHING_ORDER'),
    ('T_singleton_selected_vertex_has_W_edge','MATCHING_EDGE_NOT_ELIGIBLE'),
    ('Gram_only_bit0_overlap_one','PAIR_JOINT_BAN'),('Gram_only_bit0_overlap_zero','PAIR_JOINT_BAN'),
    ('focal_overlap_two_plain_rows_insufficient','SELECTOR_BOUND'),('sole_bit1_ineligible_selected_pair','PAIR_JOINT_BAN'),
    ('sole_bit1_selected_R_pair_not_matched','SELECTED_FORCED_EDGE'),('json_duplicate','JSON_DUPLICATE'),
    ('json_nonfinite','JSON_NONFINITE'),('budget_at_reserve','SAVE_RESERVE'),('budget_stop','SAVE_RESERVE')]


def rook_fixture(support, forced=False):
    """Public geometry recomputed here; no producer fixture/parser is selected."""
    board = [(r,c) for r in range(3) for c in range(3)]
    support = [tuple(x) for x in support]
    def linked(p,q): return p != q and (p[0] == q[0] or p[1] == q[1])
    exterior = [p for p in board if p not in support]
    masks_of = {p:sum(2**u for u,q in enumerate(support) if linked(p,q)) for p in exterior}
    masks = sorted(set(masks_of.values()))
    groups = [sorted([p for p in exterior if masks_of[p] == mask],key=lambda p:(p != (0,0),p)) for mask in masks]
    labels = {p:[i,j] for i,group in enumerate(groups) for j,p in enumerate(group)}
    pair_bits = []
    for i in range(len(masks)):
        for j in range(i,len(masks)):
            observed = sorted(set(int(linked(p,q)) for p in groups[i] for q in groups[j] if p != q))
            pair_bits.append({'i':i,'j':j,'bits':observed if forced and observed else [0,1]})
    selected = [p for p in exterior if linked(p,(0,0))]
    matched = [sorted([labels[p],labels[q]]) for a,p in enumerate(selected) for q in selected[a+1:] if linked(p,q)]
    return {'profile':{'target_order':9,'target_degree':4,
        'support_adjacency':[[int(linked(p,q)) for q in support] for p in support],
        'ordered_masks':masks,'counts':[len(group) for group in groups],'pair_bits':pair_bits},
        'focal':labels[(0,0)][0],'selected_labels':sorted(labels[p] for p in selected),
        'matching_pairs':sorted(matched)}


def corner_fixture(): return rook_fixture([[1,1],[1,2],[2,1],[2,2]])


def author_action(name, payload, budget):
    if name.startswith('json_'): return decode(payload)
    if name.startswith('budget_'): return reserve(payload)
    if name in ('absent_incumbent_unknown','nonintegral_incumbent_unknown','binary_but_row_invalid_unknown'):
        base = corner_fixture(); model = reconstruct(base['profile'],base['focal'],budget)
        observed = extraction(model,payload,budget)
        need(observed['candidate'] is None and observed.get('numeric_infeasibility_is_proof') is False, 'UNKNOWN_CONTROL')
        return observed
    if name in ('binary_bool','binary_float','binary_two'):
        base = corner_fixture(); return binary_rows(reconstruct(base['profile'],base['focal'],budget),payload,budget)
    if name == 'explicit_forced_focal_overlap_conflict':
        model = reconstruct(payload['profile'],payload['focal'],budget); bound = first_bound(model)
        need(type(bound) is dict and bound['kind'] == 'STRUCTURAL_SELECTOR_BOUND', 'BOUND_CONTROL')
        return {'model':model,'exact_bound':bound,'fixture_is_not_a_target_graph':True}
    if name.startswith('native_'):
        # Native receipts are decoded separately in replay_controls; no native call here.
        if name == 'native_rook_forced_matching': return fixture_checked(payload,budget)
        return {'native_fixture_only':True}
    return fixture_checked(payload,budget)


def own_routes(budget, out):
    base = corner_fixture(); path = rook_fixture([[0,1],[1,1],[1,2],[2,2]])
    two = rook_fixture([[0,1],[1,0]]); repeated = rook_fixture([[1,1]])
    bm = reconstruct(base['profile'],base['focal'],budget)
    values,_ = labels_values(bm,base['selected_labels'],base['matching_pairs'],budget)
    routes = []
    def add(name, expected, payload, action):
        routes.append((name,expected,copy.deepcopy(payload),action))
    def change(name, expected, payload, mutation, action=None):
        altered = copy.deepcopy(payload); mutation(altered)
        add(name,expected,altered,action or (lambda p,n=name:author_action(n,p,budget)))
    def bits_change(p,i,j,bits):
        target = (min(i,j),max(i,j))
        for row in p['profile']['pair_bits']:
            if (row['i'],row['j']) == target: row['bits'] = bits; return
        raise Veto('CONTROL_PAIR_NOT_FOUND')
    for name,payload in [('rook_empty_T_free',base),('rook_empty_T_forced',rook_fixture([[1,1],[1,2],[2,1],[2,2]],True)),
        ('rook_singleton_T',path),('rook_independent_two_T',two),('rook_repeated_empty_and_singleton_selected_types',repeated)]:
        add(name,'PASS',payload,lambda p:fixture_checked(p,budget))
    add('absent_incumbent_unknown','PASS',{'solution_value_valid':False,'col_value':[]},
        lambda p:author_action('absent_incumbent_unknown',p,budget))
    half = [float(v) for v in values]; half[0] = 0.5
    add('nonintegral_incumbent_unknown','PASS',{'solution_value_valid':True,'col_value':half},
        lambda p:author_action('nonintegral_incumbent_unknown',p,budget))
    add('binary_but_row_invalid_unknown','PASS',{'solution_value_valid':True,'col_value':[0.0]*bm['variables']},
        lambda p:author_action('binary_but_row_invalid_unknown',p,budget))
    add('budget_above_reserve','PASS',{'stop_required':False,'remaining_seconds':20.000001},reserve)
    fixed = {'variables':1,'lower':[1],'upper':[1],
        'rows':[{'index':0,'kind':'TINY_FIXED','terms':[[0,1]],'lower':1,'upper':1,'detail':None}]}
    parity = {'variables':1,'lower':[0],'upper':[1],
        'rows':[{'index':0,'kind':'TINY_PARITY','terms':[[0,2]],'lower':1,'upper':1,'detail':None}]}
    add('native_tiny_fixed_binary','PASS',fixed,lambda p:binary_rows(p,[1],budget))
    def impossible_tiny(p):
        # Explicit two possible binary values, exact arithmetic, no numerical inference.
        for value in (0,1):
            try: binary_rows(p,[value],budget)
            except Veto as exc: need(str(exc) == 'TINY_PARITY','TINY_PARITY_CONTROL')
            else: raise Veto('TINY_PARITY_CONTROL')
        return {'both_binary_values_rejected':True}
    add('native_tiny_parity_unknown','PASS',parity,impossible_tiny)
    add('native_rook_forced_matching','PASS',rook_fixture([[1,1],[1,2],[2,1],[2,2]],True),
        lambda p:fixture_checked(p,budget))
    conflict = copy.deepcopy(two); bits_change(conflict,conflict['focal'],conflict['focal'],[1])
    add('explicit_forced_focal_overlap_conflict','PASS',conflict,
        lambda p:author_action('explicit_forced_focal_overlap_conflict',p,budget))
    change('count_bool','COUNT_INTEGER',base,lambda p:p['profile']['counts'].__setitem__(0,True))
    change('count_sum','COUNT_SUM',base,lambda p:p['profile']['counts'].__setitem__(0,0))
    change('mask_bool','TYPE_MASK',base,lambda p:p['profile']['ordered_masks'].__setitem__(0,False))
    change('graph_bool','GRAPH_DOMAIN',base,lambda p:p['profile']['support_adjacency'][0].__setitem__(0,False))
    change('pair_coordinate_bool','PAIR_COORDINATES',base,lambda p:p['profile']['pair_bits'][0].__setitem__('i',False))
    change('pair_bits_bool','PAIR_BITS',base,lambda p:p['profile']['pair_bits'][0].__setitem__('bits',[False,1]))
    change('pair_missing','PAIR_POPULATION',base,lambda p:p['profile']['pair_bits'].pop())
    change('focal_bool','FOCAL_INDEX',base,lambda p:p.__setitem__('focal',False))
    change('nonindependent_focal_T','FOCAL_SUPPORT_INDEPENDENT',base,lambda p:p.__setitem__('focal',1))
    for name,value,stage in [('binary_bool',True,'BINARY_INTEGER'),('binary_float',1.0,'BINARY_INTEGER'),('binary_two',2,'BINARY_BOUND')]:
        change(name,stage,values,lambda p,v=value:p.__setitem__(0,v),lambda p:binary_rows(bm,p,budget))
    change('selected_focal_self','SELECTED_SELF',base,lambda p:p['selected_labels'].__setitem__(0,[0,0]))
    change('selected_duplicate','SELECTED_ORDER',base,lambda p:p['selected_labels'].__setitem__(1,p['selected_labels'][0]))
    change('selected_copy_outside_count','SELECTED_CAPACITY',base,lambda p:p['selected_labels'][0].__setitem__(1,99))
    change('selected_wrong_degree','SELECTOR_DEGREE',base,lambda p:p['selected_labels'].pop())
    change('edge_support_overlap_one','MATCHING_EDGE_NOT_ELIGIBLE',base,
        lambda p:p.__setitem__('matching_pairs',[[[1,0],[2,0]],[[3,0],[4,0]]]))
    change('matching_edge_missing','MATCHING_DEGREE',base,lambda p:p['matching_pairs'].pop())
    change('matching_edge_duplicate','MATCHING_ORDER',base,lambda p:p['matching_pairs'].append(p['matching_pairs'][0]))
    change('T_singleton_selected_vertex_has_W_edge','MATCHING_EDGE_NOT_ELIGIBLE',path,
        lambda p:p.__setitem__('matching_pairs',sorted(p['matching_pairs']+[sorted([p['selected_labels'][0],p['selected_labels'][-1]])])))
    change('Gram_only_bit0_overlap_one','PAIR_JOINT_BAN',base,lambda p:bits_change(p,1,2,[]))
    zero = {'profile':{'target_order':8,'target_degree':6,'support_adjacency':[[0,0],[0,0]],
        'ordered_masks':[0,1,2],'counts':[2,2,2],'pair_bits':[{'i':i,'j':j,'bits':[0,1]}
            for i in range(3) for j in range(i,3)]},'focal':1,
        'selected_labels':[[0,0],[0,1],[1,1],[2,0],[2,1]],
        'matching_pairs':[[[0,0],[2,0]],[[0,1],[2,1]]]}
    change('Gram_only_bit0_overlap_zero','PAIR_JOINT_BAN',zero,lambda p:bits_change(p,0,0,[]))
    change('focal_overlap_two_plain_rows_insufficient','SELECTOR_BOUND',two,
        lambda p:p.update(selected_labels=[[0,0],[p['focal'],1]],matching_pairs=[]))
    change('sole_bit1_ineligible_selected_pair','PAIR_JOINT_BAN',path,lambda p:bits_change(p,1,4,[1]))
    force = {'profile':{'target_order':7,'target_degree':6,'support_adjacency':[[0]],
        'ordered_masks':[0,1],'counts':[4,2],'pair_bits':[{'i':0,'j':0,'bits':[1]},
            {'i':0,'j':1,'bits':[0,1]},{'i':1,'j':1,'bits':[0,1]}]},'focal':1,
        'selected_labels':[[0,0],[0,1],[0,2],[0,3],[1,1]],
        'matching_pairs':[[[0,0],[0,1]],[[0,2],[0,3]]]}
    add('sole_bit1_selected_R_pair_not_matched','SELECTED_FORCED_EDGE',force,lambda p:fixture_checked(p,budget))
    add('json_duplicate','JSON_DUPLICATE','{"x":1,"x":2}',decode)
    add('json_nonfinite','JSON_NONFINITE','{"x":NaN}',decode)
    add('budget_at_reserve','SAVE_RESERVE',{'stop_required':False,'remaining_seconds':20},reserve)
    add('budget_stop','SAVE_RESERVE',{'stop_required':True,'remaining_seconds':100},reserve)
    need(len(routes) == 42 and [r[:2] for r in routes] == AUTHOR_ROUTES, 'OWN_AUTHOR_COUNTERPARTS')
    # Seven new positives and twenty-two negatives exercise actual checking helpers.
    add('complete_binary_roundtrip','PASS',values,lambda p:exact_witness(bm,p,budget))
    add('abstract_overlap_zero_before_cut','PASS',zero,lambda p:fixture_checked(p,budget))
    exact = {'solution_value_valid':True,'col_value':[float(v) for v in values]}
    add('exact_float_incumbent_candidate','PASS',exact,
        lambda p:need(extraction(bm,p,budget)['candidate'] is not None,'KNOWN_CANDIDATE'))
    add('typed_model_identity','PASS',bm,lambda p:model_identity(p,bm))
    add('output_directory_positive','PASS',str(out),lambda p:output_directory(p,out))
    rt_positive = synthetic_runtime()
    add('actual_shaped_593_runtime_positive','PASS',rt_positive,
        lambda p:runtime(p['plan'],p['manifest'],p['terminal'],p['summary'],'calibrate',{'source':'pin','spec':'pin'}))
    flat_profile = {'schema':'ROOT_FIXED17_FOCAL_SELECTOR_MATCHING_AUTHOR_CONTROLS_CONCRETE_V1',
                    **rt_positive['plan']}
    add('actual_flat_root_profile_positive','PASS',flat_profile,lambda p:runtime_profile(p,'calibrate'))
    change('count_float','COUNT_INTEGER',base,lambda p:p['profile']['counts'].__setitem__(0,1.0),lambda p:fixture_checked(p,budget))
    change('mask_float','TYPE_MASK',base,lambda p:p['profile']['ordered_masks'].__setitem__(0,0.0),lambda p:fixture_checked(p,budget))
    change('selected_bool','LABEL_INTEGER',base,lambda p:p['selected_labels'][0].__setitem__(0,True),lambda p:fixture_checked(p,budget))
    change('selected_float','LABEL_INTEGER',base,lambda p:p['selected_labels'][0].__setitem__(1,0.0),lambda p:fixture_checked(p,budget))
    change('matched_bool','MATCHING_INTEGER',base,lambda p:p['matching_pairs'][0][0].__setitem__(1,False),lambda p:fixture_checked(p,budget))
    change('matched_float','MATCHING_INTEGER',base,lambda p:p['matching_pairs'][0][0].__setitem__(1,0.0),lambda p:fixture_checked(p,budget))
    change('model_late_term','MODEL_RECONSTRUCTION',bm,lambda p:p['rows'][-1]['terms'][-1].__setitem__(1,2),lambda p:model_identity(p,bm))
    change('model_boolean_lower','MODEL_RECONSTRUCTION',bm,lambda p:p['lower'].__setitem__(0,False),lambda p:model_identity(p,bm))
    w = exact_witness(bm,values,budget)
    change('witness_binary_bool','EXACT_WITNESS',w,lambda p:p['binary_values'].__setitem__(0,False),lambda p:witness_identity(p,bm,values,budget))
    change('witness_label_wrong','EXACT_WITNESS',w,lambda p:p['selected_labels'][0].__setitem__(1,99),lambda p:witness_identity(p,bm,values,budget))
    change('numeric_bool','NUMERIC_VECTOR',exact,lambda p:p['col_value'].__setitem__(0,False),lambda p:extraction(bm,p,budget))
    change('numeric_flag_int','NUMERIC_VALID_FLAG',exact,lambda p:p.__setitem__('solution_value_valid',1),lambda p:extraction(bm,p,budget))
    add('numeric_nonfinite','NUMERIC_VECTOR',{'solution_value_valid':True,'col_value':['inf']},lambda p:extraction(bm,p,budget))
    g = synthetic_guidance(values)
    change('guidance_late_hex','GUIDANCE_HEX',g,lambda p:p['col_value_float_hex'].__setitem__(-1,'0x1.0p+0'),lambda p:guidance_checked(p,bm,budget,5))
    cp = {'completed_focal_types':1,'positive_type_prefix':[0],'decisions':[]}
    change('checkpoint_boolean','CHECKPOINT_PREFIX',cp,lambda p:p.__setitem__('completed_focal_types',True),lambda p:checkpoint_identity(p,cp))
    rt = synthetic_runtime()
    rtcheck = lambda p:runtime(p['plan'],p['manifest'],p['terminal'],p['summary'],'calibrate',{'source':'pin','spec':'pin'})
    change('runtime_missing_suspended','RUNTIME_CLEANUP',rt,lambda p:p['terminal']['cleanup'].pop('created_suspended'),rtcheck)
    change('runtime_boolean_exit','RUNTIME_EXIT',rt,lambda p:p['terminal'].__setitem__('command_exit_code',False),rtcheck)
    change('runtime_shifted_suffix','RUNTIME_SUFFIX',rt,lambda p:p['plan']['child_argv'].pop(0),rtcheck)
    fake = {'status':CAL_STATUS,'implementation_version':1,'mode':'calibrate','producer':'/root/structural',
        'verifier':'/root/native_driver','method':'independent_artifact_check','target_resolution':'NONE',
        'actual_target_input_read':False,'source_software':{'synthetic':'pin'},
        'outcome':{'counts':OWN_COUNTS,'all_precise_stages_match':True}}
    change('own_gate_boolean_impl','OWN_HEADER',fake,lambda p:p.__setitem__('implementation_version',True),lambda p:own_header(p,{'synthetic':'pin'},'calibrate'))
    add('output_directory_file','PRODUCER_OUTPUT_DIRECTORY',str(out/'control_000_rook_empty_T_free.json'),lambda p:output_directory(p,out))
    change('runtime_profile_old_family','RUNTIME_PLAN_SCHEMA',flat_profile,
        lambda p:p.__setitem__('schema','ROOT_CONCRETE_FOCAL_NEIGHBOR_AUTHOR_CALIBRATION_V1'),lambda p:runtime_profile(p,'calibrate'))
    nested = {'schema':'FIXED17_FOCAL_SELECTOR_MATCHING_CONCRETE_PLAN_V1','solve':copy.deepcopy(rt_positive['plan']),
              **copy.deepcopy(rt_positive['plan'])}
    nested['allocation'] = nested['solve']['allocation'] = {'outer':120,'worker':100,'save':20,'shutdown':20}
    nested['supervisor_argv'] = copy.deepcopy(nested['command']); nested['solve']['supervisor_argv'] = copy.deepcopy(nested['command'])
    change('science_alias_shifted_child','RUNTIME_PLAN_ALIASES',nested,
        lambda p:p['child_argv'].pop(0),lambda p:runtime_profile(p,'solve'))
    need(len(routes) == OWN_COUNTS['total'] and sum(r[1] == 'PASS' for r in routes) == OWN_COUNTS['positive'], 'OWN_ROUTE_COUNTS')
    return routes


def model_identity(raw, expected): need(same(raw,expected), 'MODEL_RECONSTRUCTION')
def witness_identity(raw, model, values, budget): need(same(raw,exact_witness(model,values,budget)), 'EXACT_WITNESS')
def checkpoint_identity(raw, expected): need(same(raw,expected), 'CHECKPOINT_PREFIX')


def synthetic_guidance(values):
    floats = [float(v) for v in values]
    return {'schema':'FIXED17_SELECTOR_MATCHING_NUMERIC_GUIDANCE_V1','native_version':'1.15.1','numpy_version':'2.5.3',
        'solver_calls':1,'objective_all_zero':True,'floating_status_is_proof':False,'numeric_infeasibility_is_proof':False,
        'col_value':floats,'col_value_float_hex':[v.hex() for v in floats],'solution_value_valid':True,
        'run_status':'synthetic','model_status':'synthetic','wall_seconds':0.0,
        'options':{'presolve':'on','solver':'choose','threads':1,'parallel':'off','random_seed':0,
            'mip_rel_gap':0.0,'mip_abs_gap':0.0,'primal_feasibility_tolerance':1e-7,'mip_feasibility_tolerance':1e-7,
            'output_flag':True,'log_to_console':False,'log_file':'synthetic','time_limit':5.0}}


def output_directory(name, base):
    need(type(name) is str,'PRODUCER_OUTPUT_DIRECTORY')
    path = safe(name,False); need(path.is_dir() and path == base,'PRODUCER_OUTPUT_DIRECTORY')


def own_header(raw, software, mode):
    need(type(raw) is dict and raw.get('status') == (CAL_STATUS if mode == 'calibrate' else CONTROLS_STATUS)
         and raw.get('mode') == mode and type(raw.get('implementation_version')) is int and raw['implementation_version'] == 1
         and raw.get('producer') == '/root/structural' and raw.get('verifier') == '/root/native_driver'
         and raw.get('method') == 'independent_artifact_check' and raw.get('target_resolution') == 'NONE'
         and raw.get('actual_target_input_read') is False and same(raw.get('source_software'),software), 'OWN_HEADER')
    need(same(raw.get('outcome',{}).get('counts'),OWN_COUNTS if mode == 'calibrate' else AUTHOR_COUNTS)
         and raw['outcome'].get('all_precise_stages_match') is True,'OWN_SCOPE')


def qualify(reader, args, software):
    cal,base = packet(reader,args.calibration,args.calibration_sha256)
    own_header(cal,software,'calibrate'); need(same(cal.get('inputs_sha256'),software),'OWN_SOFTWARE')
    table = reader.read(base/'controls.json',cal['outputs_sha256']['controls.json'])
    need(type(table) is list and len(table) == OWN_COUNTS['total'] and
         all(type(row) is dict and type(row.get('index')) is int and row['index'] == i and row.get('matches') is True
             and row.get('expected_stage') == row.get('actual_stage') for i,row in enumerate(table)), 'OWN_STAGE_TABLE')


def source_packet(reader, args, mode):
    plan = reader.read(args.producer_plan,args.producer_plan_sha256)
    summary,base = packet(reader,args.producer_summary,args.producer_summary_sha256)
    need(summary.get('schema') == 'FIXED17_FOCAL_SELECTOR_MATCHING_PRODUCER_REPORT_V1'
         and type(summary.get('implementation_version')) is int and summary['implementation_version'] == 1
         and summary.get('mode') == mode and summary.get('producer') == '/root/structural'
         and summary.get('source_author') == '/root/structural' and summary.get('independent_approval') is False
         and summary.get('target_resolution') == 'NONE' and summary.get('graph_completion') is False
         and summary.get('count_witness_excluded') is False and summary.get('actual_profile_read') is (mode == 'solve')
         and summary.get('automatic_retry') is False and type(summary.get('ledger_index_git_mutations')) is int
         and summary['ledger_index_git_mutations'] == 0, 'PRODUCER_HEADER')
    need(same(summary.get('source_software'),AUTHOR_SOFTWARE),'PRODUCER_SOFTWARE')
    declared = summary.get('inputs_sha256')
    need(type(declared) is dict and all(type(p) is str and type(h) is str and len(h) == 64 and
         all(c in '0123456789abcdef' for c in h) for p,h in declared.items()) and
         all(declared.get(p) == h for p,h in AUTHOR_SOFTWARE.items()),'PRODUCER_DECLARED_INPUTS')
    reader.map(AUTHOR_SOFTWARE)  # Explicit direct premises replace any huge ancestor closure walk.
    manifest = reader.read(args.producer_manifest,args.producer_manifest_sha256)
    terminal = reader.read(args.producer_terminal,args.producer_terminal_sha256)
    flags = runtime(runtime_profile(plan,mode),manifest,terminal,summary,mode,
        {'source':SOFTWARE[PRODUCER],'spec':SOFTWARE[PRODUCER_SPEC]})
    output_directory(flags['--out'],base)
    need(safe(summary.get('output_root'),False) == base,'PRODUCER_OUTPUT_DIRECTORY')
    expected = 'FIXED17_FOCAL_SELECTOR_MATCHING_V1_AUTHOR_CONTROLS_PASS' if mode == 'calibrate' else 'CANDIDATE_FIXED17_FOCAL_SELECTOR_MATCHING_V1'
    need(summary.get('status') == expected,'PRODUCER_STATUS')
    return summary,base,flags


def replay_controls(reader, summary, base, out):
    author = summary.get('author_controls')
    expected_author = {'counts':AUTHOR_COUNTS,'all_precise_stages_match':True,'native_solver_calls':3,
        'actual_profile_read':False,'graph_completion':False,'abstract_bit_corruptions_are_not_rook_necessity_claims':True}
    need(same(author,expected_author),'AUTHOR_SCOPE')
    table = reader.read(base/'controls.json',summary['outputs_sha256']['controls.json'])
    need(type(table) is list and len(table) == 42,'AUTHOR_STAGE_POPULATION')
    names = {'controls.json'}; pairs = []
    def load(name):
        names.add(name); need(name in summary['outputs_sha256'],'AUTHOR_PAYLOAD')
        return reader.read(base/name,summary['outputs_sha256'][name])
    for i,(name,expected) in enumerate(AUTHOR_ROUTES):
        payload = load('control_%02d_%s.json'%(i,name)); result = None
        try: result = author_action(name,payload,reader.budget); actual = 'PASS'
        except Veto as exc: actual = str(exc)
        row = table[i]
        need(type(row) is dict and type(row.get('index')) is int and row['index'] == i and row.get('name') == name
             and row.get('expected_stage') == expected and row.get('actual_stage') == expected and row.get('matches') is True,'AUTHOR_STAGE_ROW')
        need(actual == expected,'AUTHOR_INDEPENDENT_STAGE')
        if i < 13:
            returned = load('result_%02d.json'%i)
            if i in (9,10,11):
                case = {9:'fixed',10:'parity',11:'rook'}[i]
                guidance = load('tiny_'+case+'_guidance.json'); names.add('tiny_'+case+'_solver.log')
                model = payload if i != 11 else reconstruct(payload['profile'],payload['focal'],reader.budget)
                guidance_checked(guidance,model,reader.budget,5)
                if i == 9:
                    need(guidance['solution_value_valid'] is True and same(guidance['col_value'],[1.0]),'TINY_FIXED_WITNESS')
                    binary_rows(model,[1],reader.budget)
                    result = {'guidance':guidance,'mathematical_infeasibility_proven':False}
                elif i == 10:
                    xs = guidance['col_value']
                    need(not guidance['solution_value_valid'] or len(xs) != 1 or
                         abs(xs[0]-round(xs[0])) > 1e-7 or 2*round(xs[0]) != 1,'TINY_PARITY_NO_EXACT_INTEGER')
                    result = {'guidance':guidance,'mathematical_infeasibility_proven':False}
                else:
                    extracted = extraction(model,guidance,reader.budget)
                    need(extracted['candidate'] is not None,'TINY_ROOK_EXACT_WITNESS')
                    result = {'guidance':guidance,'extraction':extracted}
            need(same(returned,result),'AUTHOR_RETURNED_RESULT')
            write(out/('independent_result_%02d.json'%i),result,reader.budget)
        pairs.append({'index':i,'name':name,'expected_stage':expected,'producer_stage':row['actual_stage'],
                      'independent_stage':actual,'matches':True})
    need(len(names) == 62 and names <= set(summary['outputs_sha256']),'AUTHOR_INVENTORY')
    if summary['mode'] == 'calibrate':
        need(set(summary['outputs_sha256']) == names and same(summary.get('outcome'),author),'AUTHOR_OUTPUT_POPULATION')
    write(out/'independent_stage_pairs.json',pairs,reader.budget)
    return names,{'counts':AUTHOR_COUNTS,'all_precise_stages_match':True,'producer_physical_files':63,
        'producer_output_hashes':62,'complete_public_rook_fixtures':5,'complete_tiny_native_receipts':3,
        'solver_calls':0,'actual_target_input_read':False,'graph_completion':False}


def saved_matching(raw, focal, model, decision, guidance, witness, budget, expected_model=None):
    model_identity(model,reconstruct(raw,focal,budget) if expected_model is None else expected_model)
    bound = first_bound(model); gp = wp = None
    if bound is not None:
        need(guidance is None and witness is None,'BOUND_PAYLOAD_POPULATION')
        expected = {'status':'CANDIDATE_EXACT_LOCAL_BOUND_FAILURE','exact_bound':bound,
                    'candidate':None,'numeric_infeasibility_is_proof':False}
    else:
        need(type(guidance) is dict,'GUIDANCE_MISSING')
        extracted = extraction(model,guidance,budget); gp = 'type_%03d_guidance.json'%focal
        if extracted['candidate'] is None:
            need(witness is None,'UNKNOWN_WITNESS_POPULATION')
            expected = {**extracted,'status':'UNKNOWN_NO_EXACT_LOCAL_MATCHING'}
        else:
            need(same(witness,extracted['candidate']),'EXACT_WITNESS')
            # Strict raw witness binary values also get independently decoded.
            exact = exact_witness(model,witness.get('binary_values'),budget)
            need(same(exact,witness),'EXACT_WITNESS')
            wp = 'type_%03d_witness.json'%focal
            expected = {'status':'CANDIDATE_EXACT_LOCAL_SELECTOR_MATCHING','candidate_saved':True,
                        'maximum_distance':extracted['maximum_distance'],'numeric_infeasibility_is_proof':False}
    expected.update(focal_type=focal,guidance_path=gp,witness_path=wp,graph_completion=False,
                    count_witness_excluded=False,uniform_profiles=False)
    need(same(decision,expected),'SCIENTIFIC_DECISION')
    return expected


def configuration(reader,args,flags,software):
    gate,gbase = packet(reader,args.producer_controls,args.producer_controls_sha256)
    own_header(gate,software,'controls')
    need(gate.get('inputs_sha256',{}).get(safe(args.calibration).relative_to(ROOT).as_posix()) == args.calibration_sha256,
         'CONTROLS_CALIBRATION_PIN')
    config = reader.read(flags['--configuration'],flags['--configuration-sha256'])
    need(type(config) is dict and config.get('schema') == 'FIXED17_FOCAL_SELECTOR_MATCHING_CONFIGURATION_V1'
         and config.get('target_resolution') == 'NONE' and type(config.get('inputs_sha256')) is dict,'CONFIG_HEADER')
    pins = config['inputs_sha256']
    required = {**PREMISES,**AUTHOR_SOFTWARE,SELF:software[SELF],SPEC:software[SPEC]}
    for name,digest in required.items(): need(pins.get(name) == digest,'CONFIG_DIRECT_PINS')
    for key,mode,path,digest in [('independent_calibration','calibrate',args.calibration,args.calibration_sha256),
        ('independent_producer_controls','controls',args.producer_controls,args.producer_controls_sha256)]:
        ref = config.get(key)
        need(type(ref) is dict and set(ref) == {'path','sha256','implementation_version'} and
             type(ref['implementation_version']) is int and ref['implementation_version'] == 1
             and safe(ref['path']) == safe(path) and ref['sha256'] == digest and
             pins.get(safe(path).relative_to(ROOT).as_posix()) == digest,'CONFIG_QUALIFICATION_PIN')
    need(config.get('source') == PRODUCER and config.get('source_sha256') == AUTHOR_SOFTWARE[PRODUCER]
         and config.get('spec') == PRODUCER_SPEC and config.get('spec_sha256') == AUTHOR_SOFTWARE[PRODUCER_SPEC],
         'CONFIG_SOURCE')
    maximum = config.get('per_focal_solver_seconds')
    need(type(maximum) in (int,float) and math.isfinite(maximum) and 0 < maximum <= 10,'CONFIG_SOLVER_SECONDS')
    # Explicit submitted configuration identities are metadata; no transitive
    # Gram/pair/count closure is recomputed. Required direct premises are hashed.
    need(all(type(p) is str and type(h) is str and len(h) == 64 and all(c in '0123456789abcdef' for c in h)
             for p,h in pins.items()),'CONFIG_PIN_SCHEMA')
    reader.map(PREMISES)
    trusted = reader.read(TRUSTED_PROFILE,TRUSTED_PROFILE_SHA)
    cp = 'acceleration/results/20261004_independent_review/fixed17_count_neighbor_capacity_full01/summary.json'
    capacity = reader.read(cp,PREMISES[cp])
    need(capacity.get('status') == 'INDEPENDENT_FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_COMPLETE_PASS' and
         capacity.get('inputs_sha256',{}).get(TRUSTED_PROFILE) == TRUSTED_PROFILE_SHA,'TRUSTED_PROFILE_GATE')
    return trusted,float(maximum)


def full(reader,args,summary,base,flags,out,software):
    need(args.producer_controls is not None and args.producer_controls_sha256 is not None,'CONTROLS_ARGUMENTS')
    trusted,maximum = configuration(reader,args,flags,software)
    names,control_scope = replay_controls(reader,summary,base,out)
    def load(name):
        names.add(name); need(name in summary['outputs_sha256'],'SCIENTIFIC_PAYLOAD')
        return reader.read(base/name,summary['outputs_sha256'][name])
    raw = load('parsed_matching_input.json'); need(same(raw,trusted),'TRUSTED_PROFILE_IDENTITY')
    parsed = profile(raw,reader.budget)
    positive = [i for i,number in enumerate(raw['counts']) if number > 0]
    need(raw['target_order'] == 99 and raw['target_degree'] == 14 and len(raw['support_adjacency']) == 17
         and len(raw['ordered_masks']) == 472 and sum(raw['counts']) == 82 and len(positive) == 68,'FIXED_SCOPE')
    decisions = []; calls = 0; elapsed = 0.0; sparse_rows = 0; witness_rows = 0; matching_vars = 0
    for completed,focal in enumerate(positive,1):
        reader.budget.tick(); prefix = 'type_%03d'%focal
        model = load(prefix+'_model.json'); decision = load(prefix+'_decision.json')
        expected_model = reconstruct(raw,focal,reader.budget,parsed); model_identity(model,expected_model)
        guidance = witness = None
        if first_bound(expected_model) is None:
            guidance = load(prefix+'_guidance.json'); names.add(prefix+'_solver.log'); calls += 1
            elapsed += guidance_checked(guidance,expected_model,reader.budget,maximum)
            if extraction(expected_model,guidance,reader.budget)['candidate'] is not None:
                witness = load(prefix+'_witness.json')
        checked = saved_matching(raw,focal,model,decision,guidance,witness,reader.budget,expected_model)
        decisions.append(checked); sparse_rows += len(expected_model['rows']); matching_vars += expected_model['matching_variables']
        if witness is not None: witness_rows += len(expected_model['rows'])
        checkpoint = load('checkpoint_%03d.json'%focal)
        expected_checkpoint = {'schema':'FIXED17_FOCAL_SELECTOR_MATCHING_CHECKPOINT_V1',
            'completed_focal_types':completed,'positive_type_prefix':positive[:completed],
            'decisions':list(decisions),'scientific_solver_calls':calls,'solver_wall_seconds':elapsed,
            'target_resolution':'NONE','automatic_retry':False}
        checkpoint_identity(checkpoint,expected_checkpoint)
        write(out/('independent_matching_%03d.json'%focal),{'model':expected_model,'decision':decision,
            'exact_witness':witness,'complete_incidence_equalities':18,
            'complete_sparse_model_rows':len(expected_model['rows']),'checkpoint_checked':True},reader.budget)
    matches = sum(d['witness_path'] is not None for d in decisions)
    unknown = sum(d['status'] == 'UNKNOWN_NO_EXACT_LOCAL_MATCHING' for d in decisions)
    bounds = sum(d['status'] == 'CANDIDATE_EXACT_LOCAL_BOUND_FAILURE' for d in decisions)
    outcome = {'completed':True,'completed_focal_types':68,'required_focal_types':68,'outside_copies':82,
        'selector_slots_per_focal':81,'equalities_per_focal':18,'all_type_masks':472,'decisions':decisions,
        'scientific_solver_calls':calls,'solver_wall_seconds':elapsed,'unmet_requirements':[],
        'exact_local_matchings':matches,'unknown_focals':unknown,'candidate_exact_bounds':bounds,
        'graph_completion':False,'count_witness_excluded':False,'numerical_infeasibility_is_proof':False}
    need(same(load('matching_outcome.json'),outcome) and same(summary.get('outcome'),outcome),'FULL_OUTCOME')
    need(set(summary['outputs_sha256']) == names and len(names) == 268+2*calls+matches,'FULL_OUTPUT_POPULATION')
    need(type(summary.get('native_solver_calls')) is int and summary['native_solver_calls'] == 3+calls,'FULL_SOLVER_COUNT')
    write(out/'independent_outcome.json',outcome,reader.budget)
    return {**outcome,'counts':AUTHOR_COUNTS,'producer_controls':control_scope,'all_precise_stages_match':True,
        'complete_selector_variables':68*81,'complete_reconstructed_incidence_equalities':1224,
        'complete_matching_variables':matching_vars,'complete_sparse_model_rows':sparse_rows,
        'complete_verified_witness_rows':witness_rows,'complete_checkpoints':68,
        'all_pair_bit_and_overlap_cuts_checked':True,'all_binary_copy_labels_checked':True,
        'qualified_profile_inherited':True,'ancestor_Gram_recomputed':False,'ancestor_count_recomputed':False,
        'independent_solver_calls':0,'actual_target_input_read':True}


def calibrate(out,budget):
    rows = []
    for i,(name,expected,payload,action) in enumerate(own_routes(budget,out)):
        write(out/('control_%03d_%s.json'%(i,name)),payload,budget)
        try: action(payload); actual = 'PASS'
        except Veto as exc: actual = str(exc)
        rows.append({'index':i,'name':name,'expected_stage':expected,'actual_stage':actual,'matches':actual == expected})
    write(out/'controls.json',rows,budget)
    need(all(row['matches'] for row in rows),'OWN_STAGE_MISMATCH')
    return {'counts':OWN_COUNTS,'all_precise_stages_match':True,'solver_calls':0,'producer_imports':0,
        'actual_target_input_read':False,'graph_completion':False,'author_counterparts':42,
        'new_positive_helpers':7,'new_strict_negative_helpers':22,'complete_public_rook_fixtures':5,
        'abstract_bit_corruptions_are_not_rook_necessity_claims':True}


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
            if args.mode == 'controls': _,outcome = replay_controls(reader,summary,base,out); status = CONTROLS_STATUS
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
        report = {'status':status,'implementation_version':1,'mode':args.mode,'timestamp':datetime.now(timezone.utc).isoformat(),
            'producer':'/root/structural','verifier':'/root/native_driver','checking_source_author':'/root/native_driver',
            'method':'independent_artifact_check','target_resolution':'NONE','source_software':software,
            'inputs_sha256':dict(reader.pins),'outputs_sha256':outputs,'outcome':outcome,'command':[sys.executable,*sys.argv],
            'cwd':str(ROOT),'actual_target_input_read':args.mode == 'full','producer_imports':0,'solver_calls':0,
            'graph_completion':False,'automatic_retry':False,'deadline':budget.tick(),
            'shared_components':['Native218c/ee985 reader/runtime ancestry is explicitly copied; no whole module imported',
                'Immutable qualified468f/capacity/count/pair/block plus written matching theorem are inherited direct premises',
                'New copy-label-set incidence, unordered-pair eligibility and exact sparse-row/witness reconstruction',
                'Wire/stage taxonomy and public rook geometry shared; no producer functions, AST, HiGHS or NumPy execution'],
            'limitations':['Complete68 local systems are separate designated focal choices, not a simultaneous symmetric graph',
                'UNKNOWN numerical incumbent cannot exclude counts or target; exact first bounds concern only supplied local model',
                'All native guidance is authenticated metadata, no backend run or transitive Gram/count proof reconstruction',
                '20save guards are allocated intent; actual supported containment/elapsed terminal remains required',
                'No formal proof, external review, novelty, availability, ledger/index or Git action']}
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


