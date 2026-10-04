"""SOURCE ONLY: distinct cumulative-histogram checking of complete saved screens."""
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
SELF = 'acceleration/audit_20261004_fixed17_count_neighbor_capacity_v1.py'
SPEC = 'acceleration/audit_20261004_fixed17_count_neighbor_capacity_v1_spec.md'
PRODUCER = 'acceleration/screen_20261004_fixed17_count_neighbor_capacity_v1.py'
PRODUCER_SPEC = 'acceleration/screen_20261004_fixed17_count_neighbor_capacity_v1_spec.md'
SOFTWARE = {
    'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py':'593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
    PRODUCER:'4d737ba3b8ea90df487a1b71cbc6fe4f8baf38234533fdc9115bb76034556371',
    PRODUCER_SPEC:'35281d5f41ca2a49d872152d9d286c6f2b56f6b510bf7e1ea5fbd91d154b82d6',
    'acceleration/audit_20261004_external_moment_integer_counts_v1.py':
        'fb6511f9b78c426bf558001c0f69fb9a1972a90716fa6aaef089e7ba27b0dcff',
}
AUTHOR_SOFTWARE = {k:v for k,v in SOFTWARE.items() if not k.endswith('audit_20261004_external_moment_integer_counts_v1.py')}
COUNT_BASE = 'acceleration/results/20261004_fixed17_integer_type_counts01/'
COUNT_PINS = {
    COUNT_BASE+'exact_integer_candidate.json':'133097b6174aa1a4b1d327b5c72a727f8ad1ac6daeef0654b117a5f8b88de5b5',
    COUNT_BASE+'parsed_fixed_input.json':'cfe5003a2bd0ad4b2b979264c6e6d1648dc3cd67d1ebc03226d44998371b1248',
}
COUNT_GATE = 'acceleration/results/20261004_independent_review/external_moment_integer_counts_full01/summary.json'
COUNT_GATE_SHA = '37bcf42a3b5e358c4306c642e152e3e605a07dc305de71b2272e455e377bd6b8'
PAIR_GATE = 'acceleration/results/20261004_independent_review/fixed17_dual_gram_pairs_full02/summary.json'
PAIR_GATE_SHA = 'ee9fa8961415df0e5f0ca429c33fc95a1d6223b77ec68e2c9ec71cc1dec0e218'
PROOF = 'acceleration/results/20261004_independent_review/target_exterior_type_edge_moments01/summary.json'
PROOF_SHA = '910a740aff6ecd90515af7de0a2743abab47eabe902274237b3b70e1d0fdc6d6'
PAIR_BASE = 'acceleration/results/20261004_fixed17_dual_gram_pairs01/'
PAIR_FIELDS = ('proposal_id','i','j','left_mask','right_mask','intersection',
    'upper_left_diagonal','upper_right_diagonal','upper_cross_0','upper_cross_1',
    'lower_left_diagonal','lower_right_diagonal','lower_cross_0','lower_cross_1',
    'upper_bits','lower_bits','cn_bits','combined_bits','classification')
CLASSES = {():'incompatible',(0,):'forced_nonadjacent',(1,):'forced_adjacent',(0,1):'either'}
CAL_STATUS = 'INDEPENDENT_FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_CALIBRATION_PASS'
CONTROLS_STATUS = 'INDEPENDENT_FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_PRODUCER_CONTROLS_PASS'
FULL_STATUS = 'INDEPENDENT_FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_COMPLETE_PASS'
AUTHOR_COUNTS = {'positive':8,'negative':23,'total':31}
OWN_COUNTS = {'positive':12,'negative':40,'total':52}
AUTHOR_ROUTES = (
    ('known_rook_rectangle_free','PASS'),('known_rook_rectangle_forced','PASS'),
    ('self_is_excluded_from_five_copy_pool','PASS'),('forced_one_slots_exactly_meet_every_Q','PASS'),
    ('budget_above_save_reserve','PASS'),('genuine_shaped_count_gate','PASS'),
    ('full_Q_is_separate_after_size_three','PASS'),('same_type_two_copies_zero_exterior_degree','PASS'),
    ('count_bool','COUNT_INTEGER'),('count_float','COUNT_INTEGER'),('count_negative','COUNT_BOUND'),
    ('count_missing','COUNT_SHAPE'),('count_sum_changed','COUNT_SUM'),('mask_bool','TYPE_MASK_INTEGER'),
    ('mask_float','TYPE_MASK_INTEGER'),('mask_order','TYPE_MASK_ORDER'),('graph_bool','GRAPH_DOMAIN'),
    ('pair_label_bool','PAIR_COORDINATES'),('pair_bits_bool','PAIR_BITS'),('pair_bits_reordered','PAIR_BITS'),
    ('pair_missing','PAIR_POPULATION'),('incompatible_positive_types','INCOMPATIBLE_COEXISTENCE'),
    ('self_copy_cannot_supply_its_own_degree','NEIGHBOR_CAPACITY'),('eligible_pool_short','NEIGHBOR_CAPACITY'),
    ('forced_one_exceeds_degree','MANDATORY_CAPACITY'),('deliberately_bad_empty_type_vector','ROW_BOUND'),
    ('forbidden_equal_type_has_two_distinct_copies','EQUAL_MULTIPLICITY'),
    ('gate_unchecked_candidate','COUNT_GATE_SCOPE'),('gate_bool_count','COUNT_GATE_SCOPE'),
    ('budget_at_save_reserve','SAVE_RESERVE'),('budget_review_stop','SAVE_RESERVE'),
)

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
            'Independent cumulative-histogram row screens; all authentication and saves share the allocation')
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
        need(p.stat().st_size <= 64 * 1024 * 1024, 'INPUT_SIZE')
        h, chunks, size = hashlib.sha256(), [], 0
        with p.open('rb') as f:
            while True:
                self.budget.tick()
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                need(size <= 64 * 1024 * 1024, 'INPUT_SIZE')
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

def count_header(raw, required):
    need(type(raw) is dict and raw.get('status') == 'INDEPENDENT_EXTERNAL_MOMENT_INTEGER_COUNTS_V1_COMPLETE_PASS'
         and raw.get('mode') == 'full' and type(raw.get('implementation_version')) is int
         and raw['implementation_version'] == 1 and raw.get('producer') == '/root/checkpoint_audit'
         and raw.get('verifier') == '/root/native_driver' and raw.get('method') == 'independent_artifact_check'
         and raw.get('target_resolution') == 'NONE','COUNT_GATE_HEADER')
    need(type(raw.get('inputs_sha256')) is dict and all(raw['inputs_sha256'].get(p)==h for p,h in required.items()),
         'COUNT_GATE_DIRECT_PINS')
    fields = {'complete_count_variables':472,'complete_presence_variables':472,'complete_moment_rows':154,
        'complete_common_Q_caps':680,'complete_pair_records':111628,'complete_pair_record_fields':19,
        'complete_pair_read_checkpoints':23}
    outcome = raw.get('outcome')
    need(type(outcome) is dict and all(type(outcome.get(k)) is int and outcome[k]==v for k,v in fields.items())
         and outcome.get('candidate_exact_checked') is True and outcome.get('graph_completion') is False,
         'COUNT_GATE_SCOPE')

def decode_input(raw, budget):
    need(type(raw) is dict and set(raw)=={'target_order','target_degree','support_adjacency','ordered_masks','counts','pair_bits'},
         'PACKET_FIELDS')
    order,degree,h = (raw[k] for k in ('target_order','target_degree','support_adjacency'))
    need(type(order) is int and type(degree) is int and 0<=degree<order,'TARGET_INTEGER')
    need(type(h) is list and 4<=len(h)<=17 and all(type(row) is list and len(row)==len(h) for row in h),'GRAPH_SHAPE')
    m=len(h)
    need(order>m and all(type(x) is int and x in (0,1) for row in h for x in row)
         and all(h[u][u]==0 and h[u][v]==h[v][u] for u in range(m) for v in range(m)), 'GRAPH_DOMAIN')
    masks=raw['ordered_masks']
    need(type(masks) is list and masks and all(type(x) is int and 0<=x<2**m for x in masks),'TYPE_MASK_INTEGER')
    need(masks==sorted(set(masks)),'TYPE_MASK_ORDER')
    numbers=raw['counts']
    need(type(numbers) is list and len(numbers)==len(masks),'COUNT_SHAPE')
    need(all(type(x) is int for x in numbers),'COUNT_INTEGER')
    need(all(0<=x<=order-m for x in numbers),'COUNT_BOUND')
    need(sum(numbers)==order-m,'COUNT_SUM')
    rawbits=raw['pair_bits']; n=len(masks)
    need(type(rawbits) is list and len(rawbits)==n*(n+1)//2,'PAIR_POPULATION')
    bits=[[None]*n for _ in range(n)]
    ordinal=0
    for i in range(n):
        for j in range(i,n):
            budget.tick()
            item=rawbits[ordinal]; ordinal+=1
            need(type(item) is dict and set(item)=={'i','j','bits'},'PAIR_KEYS')
            need(type(item['i']) is int and type(item['j']) is int and item['i']==i and item['j']==j,'PAIR_COORDINATES')
            value=item['bits']
            need(type(value) is list and all(type(x) is int and x in (0,1) for x in value)
                 and value==sorted(set(value)),'PAIR_BITS')
            bits[i][j]=bits[j][i]=tuple(value)
    for i in range(n):
        for j in range(i,n):
            budget.tick()
            if not bits[i][j] and numbers[i] and numbers[j]:
                need(i==j,'INCOMPATIBLE_COEXISTENCE')
                need(numbers[i]<=1,'EQUAL_MULTIPLICITY')
    sets=[frozenset(u for u in range(m) if mask & 2**u) for mask in masks]
    neighbors=[frozenset(v for v in range(m) if h[u][v]) for u in range(m)]
    return h,sets,numbers,bits,neighbors

def subsets(m):
    need(type(m) is int and 4<=m<=17,'SUPPORT_SIZE')
    result=[]
    for k in (1,2,3):
        result.extend([list(q) for q in itertools.combinations(range(m),k)])
    result.append(list(range(m)))
    return result

def cumulative(histogram, count, descending, budget):
    need(type(count) is int and 0<=count<=sum(len(x) for x in histogram),'HISTOGRAM_COUNT')
    amount=0; labels=[]; remaining=count
    for weight in (range(len(histogram)-1,-1,-1) if descending else range(len(histogram))):
        budget.tick()
        bucket=histogram[weight]
        take=min(remaining,len(bucket))
        # Producer ties are ascending(type,copy), with a high selection using the tail at the boundary.
        picked=bucket[len(bucket)-take:] if descending and take else bucket[:take]
        amount+=take*weight
        labels.extend(picked)
        remaining-=take
    need(remaining==0,'HISTOGRAM_SELECTION')
    # The selected high tail is serialized in ascending score/label order, not reverse rank order.
    if descending:
        rank={tuple(label):weight for weight,bucket in enumerate(histogram) for label in bucket}
        labels.sort(key=lambda label:(rank[tuple(label)],label[0],label[1]))
    return amount,labels

def reconstruct(raw,budget,consumer=None):
    h,types,numbers,bits,neighbors=decode_input(raw,budget)
    m=len(h); qs=subsets(m)
    pool=[[i,c] for i in range(len(types)) for c in range(numbers[i])]
    positive=[i for i in range(len(types)) if numbers[i]>0]
    first=None; failed=0; types_out=[]
    for completed,i in enumerate(positive,1):
        budget.tick()
        focal=[i,0]; required=raw['target_degree']-len(types[i])
        b=[2-int(u in types[i])-len(neighbors[u]&types[i]) for u in range(m)]
        mandatory=[]; optional=[]; eligible=[]
        for j in range(len(types)):
            for c in range(numbers[j]):
                if i==j and c==0:
                    continue
                allowed=bits[i][j]
                label=[j,c]
                if 1 in allowed:
                    eligible.append(label)
                    (mandatory if allowed==(1,) else optional).append(label)
        residual=required-len(mandatory)
        capacity='MANDATORY_CAPACITY' if residual<0 else 'NEIGHBOR_CAPACITY' if residual>len(optional) else None
        rows=[]
        for qi,q in enumerate(qs):
            budget.tick()
            qset=frozenset(q); demand=sum(b[u] for u in q)
            fixed=sum(len(types[j]&qset) for j,c in mandatory)
            if capacity is None:
                histogram=[[] for _ in range(len(q)+1)]
                for j,c in optional:
                    histogram[len(types[j]&qset)].append([j,c])
                low,lo=cumulative(histogram,residual,False,budget)
                high,hi=cumulative(histogram,residual,True,budget)
                minimum=fixed+low; maximum=fixed+high
                holds=minimum<=demand<=maximum
                stage=None if holds else 'ROW_BOUND'
            else:
                minimum=maximum=lo=hi=None; holds=False; stage=capacity
            row={'q_index':qi,'Q':q,'required_sum':demand,'mandatory_sum':fixed,'minimum_sum':minimum,
                'maximum_sum':maximum,'lower_optional_labels':lo,'upper_optional_labels':hi,
                'bounds_defined':capacity is None,'necessary_bound_holds':holds,'violation_stage':stage}
            rows.append(row)
            if first is None and stage:
                first={'type_index':i,'mask':raw['ordered_masks'][i],'focal_label':focal,'q_index':qi,'Q':q,
                    'required_outside_degree':required,'eligible_count':len(eligible),'mandatory_count':len(mandatory),
                    'optional_count':len(optional),'residual_degree':residual,'required_sum':demand,
                    'mandatory_sum':fixed,'minimum_sum':minimum,'maximum_sum':maximum,'violation_stage':stage}
        is_failed=any(not row['necessary_bound_holds'] for row in rows)
        failed+=int(is_failed)
        tr={'schema':'FIXED_COUNT_NEIGHBOR_CAPACITY_TYPE_ROWS_V1','type_index':i,'mask':raw['ordered_masks'][i],
            'count':numbers[i],'focal_label':focal,'all_same_type_copies_have_identical_screen_inputs':True,
            'required_outside_degree':required,'b':b,'eligible_labels':eligible,'mandatory_labels':mandatory,
            'optional_labels':optional,'residual_degree':residual,'capacity_stage':capacity,'q_count':len(qs),
            'failed':is_failed,'rows':rows}
        if consumer:
            consumer(i,tr,positive[:completed],first,completed*len(qs))
        else:
            types_out.append(tr)
    result={'schema':'FIXED_COUNT_NEIGHBOR_CAPACITY_SCREEN_OUTCOME_V1','positive_type_indices':positive,
        'positive_types':len(positive),'labelled_outside_pool':pool,'outside_copies':len(pool),'q_universe':qs,
        'q_per_positive_type':len(qs),'complete_q_rows':len(positive)*len(qs),'failed_positive_types':failed,
        'first_violation':first,'all_screens_pass':first is None,'self_exclusion':True,
        'mandatory_bit_one_enforced':True,'no_uniform_profile_assumed':True,'graph_completion':False,
        'integer_witness_rejected_by_necessary_screen':first is not None,'target_exclusion':False,
        'rows':types_out if consumer is None else None}
    return result

def type_rows(actual,expected):
    need(type(actual) is dict and set(actual)==set(expected),'TYPE_RECORD_FIELDS')
    need(type(actual.get('rows')) is list and len(actual['rows'])==len(expected['rows']),'Q_POPULATION')
    for key,value in expected.items():
        if key!='rows':
            need(same(actual[key],value),'TYPE_RECORD_VALUE')
    for got,want in zip(actual['rows'],expected['rows']):
        need(type(got) is dict and set(got)==set(want),'Q_RECORD_FIELDS')
        need(same(got,want),'Q_RECORD_VALUE')

def checkpoint(actual,positive,first,rows):
    need(type(actual) is dict and set(actual)=={'completed_positive_type_indices','first_violation','screened_rows','deadline'},
         'CHECKPOINT_FIELDS')
    need(same(actual['completed_positive_type_indices'],positive) and same(actual['first_violation'],first)
         and type(actual['screened_rows']) is int and actual['screened_rows']==rows,'CHECKPOINT_PREFIX')
    reserve(actual['deadline'])

def result_wire(actual,expected):
    need(type(actual) is dict and set(actual)==set(expected),'OUTCOME_FIELDS')
    need(same(actual,expected),'OUTCOME_VALUE')

class RejectedScreen(Veto):
    def __init__(self,stage,result):
        super().__init__(stage)
        self.result=result

def checked_screen(raw,budget):
    result=reconstruct(raw,budget)
    if not result['all_screens_pass']:
        raise RejectedScreen(result['first_violation']['violation_stage'],result)
    return result

def author_action(name,payload,budget):
    if name.startswith('budget_'):
        return reserve(payload)
    if name in ('genuine_shaped_count_gate','gate_unchecked_candidate','gate_bool_count'):
        return count_header(payload,{'synthetic.json':'0'*64})
    if name=='full_Q_is_separate_after_size_three':
        need(type(payload) is dict and set(payload)=={'size'} and type(payload['size']) is int
             and payload['size']==17 and len(subsets(payload['size']))==834,'Q_UNIVERSE')
        return None
    if name=='self_is_excluded_from_five_copy_pool':
        result=reconstruct(payload,budget); tr=result['rows'][0]
        need(tr['focal_label'] not in tr['eligible_labels'] and len(tr['eligible_labels'])==4,'SELF_EXCLUSION_CONTROL')
        need(result['all_screens_pass'],'KNOWN_ROOK_SCREEN')
        return result
    if name=='forced_one_slots_exactly_meet_every_Q':
        result=reconstruct(payload,budget)
        need(result['all_screens_pass'] and all(r['residual_degree']==0 and
             len(r['mandatory_labels'])==r['required_outside_degree'] and
             all(q['minimum_sum']==q['required_sum']==q['maximum_sum'] for q in r['rows']) for r in result['rows']),
             'FORCED_CONTROL')
        return result
    need(name in dict(AUTHOR_ROUTES),'AUTHOR_ROUTE_UNKNOWN')
    return checked_screen(payload,budget)

def own_header(raw,software):
    need(type(raw) is dict and raw.get('status')==CAL_STATUS and raw.get('mode')=='calibrate'
         and type(raw.get('implementation_version')) is int and raw['implementation_version']==1
         and raw.get('producer')=='/root/checkpoint_audit' and raw.get('verifier')=='/root/native_driver'
         and raw.get('method')=='independent_artifact_check' and raw.get('target_resolution')=='NONE'
         and raw.get('actual_target_input_read') is False and same(raw.get('source_software'),software),'OWN_CALIBRATION_HEADER')

def qualification(reader,args,software):
    cal,base=packet(reader,args.calibration,args.calibration_sha256)
    own_header(cal,software)
    need(same(cal.get('outcome',{}).get('counts'),OWN_COUNTS),'OWN_CALIBRATION_COUNTS')
    reader.map(cal['inputs_sha256'])
    return cal

def runtime_profile(plan,mode):
    need(type(plan) is dict,'PRODUCER_PLAN_SCHEMA')
    if mode=='calibrate':
        if plan.get('schema')=='ROOT_CONCRETE_COUNT_NEIGHBOR_CAPACITY_AUTHOR_CONTROL_PLAN_V1':
            profile=plan
        else:
            need(plan.get('schema')=='FIXED17_COUNT_NEIGHBOR_CAPACITY_SOURCE_ONLY_PLAN_V1','PRODUCER_PLAN_SCHEMA')
            profile=plan.get('calibration')
    else:
        if plan.get('schema')=='ROOT_CONCRETE_COUNT_NEIGHBOR_CAPACITY_CANDIDATE_SCIENCE_PLAN_V1':
            profile=plan
        else:
            need(plan.get('schema')=='FIXED17_COUNT_NEIGHBOR_CAPACITY_CONCRETE_SCIENCE_PLAN_V1','PRODUCER_PLAN_SCHEMA')
            profile=plan.get('screen')
            need(type(profile) is dict and all(same(plan.get(k),profile.get(k)) for k in
                 ('command','child_argv','worker_argv')),'SCIENCE_PLAN_ALIASES')
    need(type(profile) is dict,'RUNTIME_PLAN')
    return profile

def source_packet(reader,args,mode):
    plan=reader.read(args.producer_plan,args.producer_plan_sha256)
    profile=runtime_profile(plan,mode)
    summary,base=packet(reader,args.producer_summary,args.producer_summary_sha256)
    manifest=reader.read(args.producer_manifest,args.producer_manifest_sha256)
    terminal=reader.read(args.producer_terminal,args.producer_terminal_sha256)
    flags=runtime(profile,manifest,terminal,summary,mode,
        {'source':SOFTWARE[PRODUCER],'spec':SOFTWARE[PRODUCER_SPEC]})
    need(safe(flags['--out'],False)==base,'RUNTIME_OUTPUT')
    need(type(summary) is dict and summary.get('schema')=='FIXED17_COUNT_NEIGHBOR_CAPACITY_PRODUCER_REPORT_V1'
         and type(summary.get('implementation_version')) is int and summary['implementation_version']==1
         and summary.get('mode')==mode and summary.get('producer')=='/root/checkpoint_audit'
         and summary.get('source_author')=='/root/checkpoint_audit' and summary.get('independent_approval') is False
         and summary.get('target_resolution')=='NONE' and same(summary.get('source_software'),AUTHOR_SOFTWARE),
         'PRODUCER_HEADER')
    reader.map(summary['inputs_sha256'])
    return summary,base

def replay_controls(reader,summary,base,out):
    need(summary['status']=='FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_AUTHOR_CONTROLS_PASS'
         and same(summary.get('outcome',{}).get('counts'),AUTHOR_COUNTS)
         and summary.get('actual_count_witness_read') is False,'AUTHOR_CONTROL_HEADER')
    table=reader.read(base/'controls.json',summary['outputs_sha256']['controls.json'])
    need(type(table) is list and len(table)==31,'AUTHOR_CONTROL_POPULATION')
    stagepairs=[]; expected_names={'controls.json'}
    for index,(name,stage) in enumerate(AUTHOR_ROUTES):
        reader.budget.tick()
        row=table[index]
        expected={'index':index,'name':name,'expected_stage':stage,'actual_stage':stage,'matches':True}
        need(same(row,expected),'AUTHOR_STAGE_RECORD')
        filename='control_%02d_%s.json'%(index,name);expected_names.add(filename)
        payload=reader.read(base/filename,summary['outputs_sha256'][filename])
        value=None
        try:
            value=author_action(name,payload,reader.budget);actual='PASS'
        except Veto as exc:
            actual=str(exc)
            if isinstance(exc,RejectedScreen):
                value=exc.result
        need(actual==stage,'AUTHOR_INDEPENDENT_STAGE')
        if value is not None:
            filename='result_%02d.json'%index;expected_names.add(filename)
            saved=reader.read(base/filename,summary['outputs_sha256'][filename])
            need(same(saved,value),'AUTHOR_RESULT_VALUE')
        stagepairs.append({'index':index,'name':name,'expected_stage':stage,'producer_stage':row['actual_stage'],
                           'independent_stage':actual,'matches':True})
    need(set(summary['outputs_sha256'])==expected_names and len(expected_names)==42,'AUTHOR_OUTPUT_POPULATION')
    write(out/'independent_stage_pairs.json',stagepairs,reader.budget)
    return {'producer_controls':AUTHOR_COUNTS,'complete_stage_pairs':31,'complete_returned_results':10,
            'actual_target_input_read':False,'graph_completion':False}

def pair_payload(reader,ordered):
    gate=reader.read(PAIR_GATE,PAIR_GATE_SHA)
    need(gate.get('status')=='INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS'
         and type(gate.get('implementation_version')) is int and gate['implementation_version']==2
         and gate.get('producer')=='/root/structural' and gate.get('verifier')=='/root/native_driver'
         and gate.get('method')=='independent_artifact_check' and gate.get('target_resolution')=='NONE','PAIR_GATE_HEADER')
    pins=gate.get('inputs_sha256');need(type(pins) is dict and PAIR_BASE+'summary.json' in pins,'PAIR_RAW_PIN')
    source,base=packet(reader,PAIR_BASE+'summary.json',pins[PAIR_BASE+'summary.json'])
    expected={'scaled_input.json'}|{kind+'_%03d.json'%i for kind in ('part','checkpoint') for i in range(23)}
    need(set(source['outputs_sha256'])==expected,'PAIR_RAW_POPULATION')
    for name,digest in source['outputs_sha256'].items():
        need(pins.get(PAIR_BASE+name)==digest,'PAIR_RAW_DIRECT_PIN')
    labels=[]; table=[]; ordinal=0
    for i in range(472):
        for j in range(i,472):
            labels.append((i,j))
    for p in range(23):
        start=p*5000;stop=min(start+5000,111628)
        part=reader.read(base/('part_%03d.json'%p),source['outputs_sha256']['part_%03d.json'%p])
        need(type(part) is dict and set(part)=={'schema','part_index','start','stop','count','records'}
             and part['schema']=='DUAL_GRAM_PAIR_PART_V1','PAIR_PART_FIELDS')
        need(all(type(part[k]) is int for k in ('part_index','start','stop','count')) and
             [part[k] for k in ('part_index','start','stop','count')]==[p,start,stop,stop-start]
             and type(part['records']) is list and len(part['records'])==stop-start,'PAIR_PART_BOUNDARY')
        for record in part['records']:
            reader.budget.tick();i,j=labels[ordinal]
            need(type(record) is dict and set(record)==set(PAIR_FIELDS)
                 and all(type(record[k]) is int for k in PAIR_FIELDS[:14]),'PAIR_RECORD_FIELDS')
            need(same([record[k] for k in ('proposal_id','i','j','left_mask','right_mask')],
                      [ordinal,i,j,ordered[i],ordered[j]]),'PAIR_RECORD_LABEL')
            for key in PAIR_FIELDS[14:18]:
                bits=record[key]
                need(type(bits) is list and all(type(x) is int and x in (0,1) for x in bits)
                     and bits==sorted(set(bits)),'PAIR_RECORD_BITS')
            allowed=[a for a in (0,1) if all(a in record[k] for k in ('upper_bits','lower_bits','cn_bits'))]
            need(same(record['combined_bits'],allowed) and record['classification']==CLASSES[tuple(allowed)],'PAIR_INTERSECTION')
            table.append({'i':i,'j':j,'bits':allowed});ordinal+=1
        reader.read(base/('checkpoint_%03d.json'%p),source['outputs_sha256']['checkpoint_%03d.json'%p],False)
    need(ordinal==111628,'PAIR_COMPLETE')
    return table

def full(reader,args,summary,base,out):
    need(summary['status']=='CANDIDATE_FIXED17_COUNT_NEIGHBOR_CAPACITY_SCREEN_V1'
         and summary.get('actual_count_witness_read') is True,'SCIENCE_HEADER')
    need(args.producer_controls is not None and args.producer_controls_sha256 is not None,'PRODUCER_CONTROLS_ARGUMENTS')
    controls,cbase=packet(reader,args.producer_controls,args.producer_controls_sha256)
    need(controls.get('status')==CONTROLS_STATUS and controls.get('mode')=='controls'
         and type(controls.get('implementation_version')) is int and controls['implementation_version']==1
         and controls.get('producer')=='/root/checkpoint_audit' and controls.get('verifier')=='/root/native_driver'
         and controls.get('method')=='independent_artifact_check' and controls.get('target_resolution')=='NONE'
         and same(controls.get('source_software'),CURRENT_SOFTWARE),'CONTROLS_GATE_HEADER')
    need(same(controls.get('outcome',{}).get('producer_controls'),AUTHOR_COUNTS)
         and type(controls['outcome'].get('complete_stage_pairs')) is int
         and controls['outcome']['complete_stage_pairs']==31,'CONTROLS_GATE_SCOPE')
    reader.map(controls['inputs_sha256'])
    need(summary.get('inputs_sha256',{}).get(PROOF)==PROOF_SHA,'WRITTEN_PROOF_DIRECT_PIN')
    proof=reader.read(PROOF,PROOF_SHA)
    need(proof.get('status')=='INDEPENDENT_TARGET_EXTERIOR_TYPE_NEIGHBOR_PROFILES_AND_EDGE_MOMENTS_V1_WRITTEN_PASS'
         and proof.get('claim_id')=='C-TARGET-EXTERIOR-TYPE-NEIGHBOR-PROFILES-AND-EDGE-MOMENTS'
         and type(proof.get('claim_revision')) is int and proof['claim_revision']==1
         and proof.get('producer')=='/root/structural' and proof.get('verifier')=='/root/native_driver'
         and proof.get('method')=='independent_derivation' and proof.get('target_resolution')=='NONE','WRITTEN_PROOF_HEADER')
    gate=reader.read(COUNT_GATE,COUNT_GATE_SHA);count_header(gate,COUNT_PINS)
    parsed=reader.read(COUNT_BASE+'parsed_fixed_input.json',COUNT_PINS[COUNT_BASE+'parsed_fixed_input.json'])
    candidate=reader.read(COUNT_BASE+'exact_integer_candidate.json',COUNT_PINS[COUNT_BASE+'exact_integer_candidate.json'])
    need(type(candidate) is dict and candidate.get('schema')=='FIXED17_EXACT_INTEGER_TYPE_COUNTS_V1'
         and candidate.get('integer') is True and candidate.get('exact_constraints') is True
         and candidate.get('independent_approval') is False and candidate.get('graph_completion') is False,'COUNT_CANDIDATE_FLAGS')
    ordered=candidate.get('ordered_masks')
    need(type(ordered) is list and len(ordered)==472 and same(parsed.get('ordered_masks'),ordered),'COUNT_MASK_IDENTITY')
    count=candidate.get('counts');presence=candidate.get('presence')
    need(type(count) is list and len(count)==472 and all(type(x) is int for x in count)
         and type(presence) is list and len(presence)==472 and all(type(x) is int and x in (0,1) for x in presence)
         and presence==[int(x>0) for x in count],'COUNT_PRESENCE')
    literal=((0,1,2),(0,3,4),(0,5,6),(1,7,9),(1,8,10),(15,11,14),
             (16,12,13),(2,15,16),(3,7,11),(4,8,12),(5,9,13),(6,10,14))
    h=[[0]*17 for _ in range(17)]
    for triangle in literal:
        for u,v in itertools.combinations(triangle,2):
            need(h[u][v]==0,'LITERAL_EDGE_REPEAT')
            h[u][v]=h[v][u]=1
    need(same(parsed.get('induced_adjacency'),h),'LITERAL_H_IDENTITY')
    payload={'target_order':99,'target_degree':14,'support_adjacency':parsed['induced_adjacency'],
        'ordered_masks':ordered,'counts':count,'pair_bits':pair_payload(reader,ordered)}
    saved=reader.read(base/'parsed_screen_input.json',summary['outputs_sha256']['parsed_screen_input.json'])
    need(same(saved,payload),'SCREEN_PARSED_INPUT')
    expected_outputs={'parsed_screen_input.json','screen_outcome.json'}
    checked=[]
    def consume(i,tr,prefix,first,rowcount):
        name='type_%03d.json'%i;cp='checkpoint_%03d.json'%i
        expected_outputs.update((name,cp))
        type_rows(reader.read(base/name,summary['outputs_sha256'][name]),tr)
        checkpoint(reader.read(base/cp,summary['outputs_sha256'][cp]),prefix,first,rowcount)
        write(out/('independent_type_%03d.json'%i),tr,reader.budget)
        checked.append(i)
    expected=reconstruct(payload,reader.budget,consume)
    result_wire(reader.read(base/'screen_outcome.json',summary['outputs_sha256']['screen_outcome.json']),expected)
    need(same(summary.get('outcome'),expected),'SCIENCE_OUTCOME')
    need(set(summary['outputs_sha256'])==expected_outputs,'SCIENCE_OUTPUT_POPULATION')
    need(expected['outside_copies']==82 and expected['positive_types']==68 and expected['q_per_positive_type']==834
         and expected['complete_q_rows']==56712 and checked==expected['positive_type_indices'],'COMPLETE_FIXED_SCOPE')
    write(out/'independent_screen_outcome.json',expected,reader.budget)
    return {k:v for k,v in expected.items() if k not in ('rows','q_universe','labelled_outside_pool')}

def fixture(forced=False):
    h=[[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]]
    actual={(0,1),(0,2),(0,3),(0,4),(1,4),(2,3)}
    return {'target_order':9,'target_degree':4,'support_adjacency':h,
            'ordered_masks':[0,3,5,10,12],'counts':[1]*5,
            'pair_bits':[{'i':i,'j':j,'bits':[int((i,j) in actual)] if forced and i!=j else [0,1]}
                         for i in range(5) for j in range(i,5)]}

def own_routes(budget):
    free,forced=fixture(),fixture(True)
    fakegate={'status':'INDEPENDENT_EXTERNAL_MOMENT_INTEGER_COUNTS_V1_COMPLETE_PASS','mode':'full',
        'implementation_version':1,'producer':'/root/checkpoint_audit','verifier':'/root/native_driver',
        'method':'independent_artifact_check','target_resolution':'NONE','inputs_sha256':{'synthetic.json':'0'*64},
        'outcome':{'complete_count_variables':472,'complete_presence_variables':472,'complete_moment_rows':154,
            'complete_common_Q_caps':680,'complete_pair_records':111628,'complete_pair_record_fields':19,
            'complete_pair_read_checkpoints':23,'candidate_exact_checked':True,'graph_completion':False}}
    repeat={'target_order':6,'target_degree':4,'support_adjacency':[[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]],
            'ordered_masks':[15],'counts':[2],'pair_bits':[{'i':0,'j':0,'bits':[0]}]}
    bad=copy.deepcopy(free);bad['ordered_masks']=[0];bad['counts']=[5];bad['pair_bits']=[{'i':0,'j':0,'bits':[0,1]}]
    equal=copy.deepcopy(bad);equal['pair_bits'][0]['bits']=[]
    isolated={'target_order':5,'target_degree':1,'support_adjacency':[[0]*4 for _ in range(4)],
              'ordered_masks':[0],'counts':[1],'pair_bits':[{'i':0,'j':0,'bits':[0,1]}]}
    routes=[]
    initial=[free,forced,copy.deepcopy(free),copy.deepcopy(forced),
             {'stop_required':False,'remaining_seconds':20.000001},fakegate,{'size':17},repeat]
    for (name,stage),payload in zip(AUTHOR_ROUTES[:8],initial):
        routes.append((name,stage,payload,lambda p,n=name:author_action(n,p,budget)))
    def mutate(name,stage,original,change,action):
        payload=copy.deepcopy(original);change(payload);routes.append((name,stage,payload,action))
    checked=lambda p:checked_screen(p,budget)
    for name,value in [('count_bool',True),('count_float',1.0)]:
        mutate(name,'COUNT_INTEGER',free,lambda p,v=value:p['counts'].__setitem__(0,v),checked)
    mutate('count_negative','COUNT_BOUND',free,lambda p:p['counts'].__setitem__(0,-1),checked)
    mutate('count_missing','COUNT_SHAPE',free,lambda p:p['counts'].pop(),checked)
    mutate('count_sum_changed','COUNT_SUM',free,lambda p:p['counts'].__setitem__(0,0),checked)
    for name,value in [('mask_bool',False),('mask_float',0.0)]:
        mutate(name,'TYPE_MASK_INTEGER',free,lambda p,v=value:p['ordered_masks'].__setitem__(0,v),checked)
    mutate('mask_order','TYPE_MASK_ORDER',free,lambda p:p['ordered_masks'].reverse(),checked)
    mutate('graph_bool','GRAPH_DOMAIN',free,lambda p:p['support_adjacency'][0].__setitem__(0,False),checked)
    mutate('pair_label_bool','PAIR_COORDINATES',free,lambda p:p['pair_bits'][0].__setitem__('i',False),checked)
    mutate('pair_bits_bool','PAIR_BITS',free,lambda p:p['pair_bits'][0].__setitem__('bits',[False,1]),checked)
    mutate('pair_bits_reordered','PAIR_BITS',free,lambda p:p['pair_bits'][0].__setitem__('bits',[1,0]),checked)
    mutate('pair_missing','PAIR_POPULATION',free,lambda p:p['pair_bits'].pop(),checked)
    mutate('incompatible_positive_types','INCOMPATIBLE_COEXISTENCE',free,
           lambda p:p['pair_bits'][1].__setitem__('bits',[]),checked)
    routes.append(('self_copy_cannot_supply_its_own_degree','NEIGHBOR_CAPACITY',isolated,checked))
    mutate('eligible_pool_short','NEIGHBOR_CAPACITY',free,lambda p:p.__setitem__('target_degree',6),checked)
    mutate('forced_one_exceeds_degree','MANDATORY_CAPACITY',forced,lambda p:p.__setitem__('target_degree',3),checked)
    routes.append(('deliberately_bad_empty_type_vector','ROW_BOUND',bad,checked))
    routes.append(('forbidden_equal_type_has_two_distinct_copies','EQUAL_MULTIPLICITY',equal,checked))
    gatecheck=lambda p:count_header(p,{'synthetic.json':'0'*64})
    mutate('gate_unchecked_candidate','COUNT_GATE_SCOPE',fakegate,
           lambda p:p['outcome'].__setitem__('candidate_exact_checked',False),gatecheck)
    mutate('gate_bool_count','COUNT_GATE_SCOPE',fakegate,
           lambda p:p['outcome'].__setitem__('complete_count_variables',True),gatecheck)
    routes.append(('budget_at_save_reserve','SAVE_RESERVE',{'stop_required':False,'remaining_seconds':20},reserve))
    routes.append(('budget_review_stop','SAVE_RESERVE',{'stop_required':True,'remaining_seconds':100},reserve))
    need([(n,s) for n,s,p,a in routes]==list(AUTHOR_ROUTES),'OWN_AUTHOR_ROUTE_DECLARATION')
    # Four independently shaped positive paths beyond the shared public31 fixture taxonomy.
    hist=[[[0,0],[1,0]],[[2,0],[3,0]],[[4,0]]]
    def histogram_test(p):
        lo,ll=cumulative(p,3,False,budget);hi,hl=cumulative(p,3,True,budget)
        need((lo,hi)==(1,4) and same(ll,[[0,0],[1,0],[2,0]])
             and same(hl,[[2,0],[3,0],[4,0]]),'HISTOGRAM_CONTROL')
        return {'minimum':lo,'maximum':hi,'low_labels':ll,'high_labels':hl}
    def failure_result(p):
        value=reconstruct(p,budget)
        need(value['all_screens_pass'] is False and value['first_violation']['violation_stage']=='ROW_BOUND',
             'FAILURE_RESULT_CONTROL')
        return value
    runtime_fixture=synthetic_runtime()
    runtime_fixture['plan']['schema']='ROOT_CONCRETE_COUNT_NEIGHBOR_CAPACITY_AUTHOR_CONTROL_PLAN_V1'
    rt=lambda p:runtime(runtime_profile(p['plan'],'calibrate'),p['manifest'],p['terminal'],p['summary'],
                        'calibrate',{'source':'pin','spec':'pin'})
    header={'status':CAL_STATUS,'implementation_version':1,'mode':'calibrate','producer':'/root/checkpoint_audit',
        'verifier':'/root/native_driver','method':'independent_artifact_check','target_resolution':'NONE',
        'actual_target_input_read':False,'source_software':{'synthetic':'pin'}}
    routes.extend([('positive_histogram_tied_boundary','PASS',hist,histogram_test),
                   ('positive_exact_failed_bound_is_data','PASS',copy.deepcopy(bad),failure_result),
                   ('positive_actual_shaped593_runtime','PASS',runtime_fixture,rt),
                   ('positive_source_snapshot_qualification','PASS',header,lambda p:own_header(p,{'synthetic':'pin'}))])
    baseline=reconstruct(free,budget);tr=baseline['rows'][0]
    tc=lambda p:type_rows(p,tr)
    for name,key,value in [('q_bool','necessary_bound_holds',1),('minimum_wrong','minimum_sum',-1),
                           ('maximum_wrong','maximum_sum',99),('required_wrong','required_sum',99),
                           ('copy_wrong','lower_optional_labels',[[0,0]])]:
        mutate(name,'Q_RECORD_VALUE',tr,lambda p,k=key,v=value:p['rows'][0].__setitem__(k,v),tc)
    mutate('type_b_wrong','TYPE_RECORD_VALUE',tr,lambda p:p['b'].__setitem__(0,99),tc)
    mutate('type_self_in_pool','TYPE_RECORD_VALUE',tr,lambda p:p['eligible_labels'].append([0,0]),tc)
    mutate('type_failed_wrong','TYPE_RECORD_VALUE',tr,lambda p:p.__setitem__('failed',True),tc)
    mutate('q_last_missing','Q_POPULATION',tr,lambda p:p['rows'].pop(),tc)
    cp={'completed_positive_type_indices':[0],'first_violation':None,'screened_rows':15,
        'deadline':{'stop_required':False,'remaining_seconds':50}}
    cc=lambda p:checkpoint(p,[0],None,15)
    mutate('checkpoint_missing_index','CHECKPOINT_PREFIX',cp,lambda p:p['completed_positive_type_indices'].clear(),cc)
    mutate('checkpoint_bool_rows','CHECKPOINT_PREFIX',cp,lambda p:p.__setitem__('screened_rows',True),cc)
    mutate('checkpoint_wrong_culprit','CHECKPOINT_PREFIX',cp,lambda p:p.__setitem__('first_violation',{}),cc)
    mutate('checkpoint_no_reserve','SAVE_RESERVE',cp,lambda p:p['deadline'].__setitem__('remaining_seconds',20),cc)
    mutate('outcome_false_pass','OUTCOME_VALUE',baseline,lambda p:p.__setitem__('all_screens_pass',False),
           lambda p:result_wire(p,baseline))
    mutate('runtime_bool_exit','RUNTIME_EXIT',runtime_fixture,lambda p:p['terminal'].__setitem__('command_exit_code',False),rt)
    mutate('runtime_not_reaped','RUNTIME_CLEANUP',runtime_fixture,lambda p:p['terminal']['cleanup'].__setitem__('reaped',False),rt)
    mutate('runtime_inf_string','RUNTIME_WORKER_DEADLINE',runtime_fixture,
           lambda p:p['summary']['deadline'].__setitem__('remaining_seconds','inf'),rt)
    need(len(routes)==52 and sum(stage=='PASS' for name,stage,p,a in routes)==12,'OWN_ROUTE_POPULATION')
    return routes

def calibrate(out,budget):
    table=[]
    for i,(name,expected,payload,action) in enumerate(own_routes(budget)):
        budget.tick();write(out/('control_%03d_%s.json'%(i,name)),payload,budget)
        try:
            action(payload);actual='PASS'
        except Veto as exc:
            actual=str(exc)
        row={'index':i,'name':name,'expected_stage':expected,'actual_stage':actual,'matches':expected==actual}
        table.append(row)
    write(out/'controls.json',table,budget)
    need(all(row['matches'] for row in table),'OWN_CONTROL_STAGE_MISMATCH')
    return {'counts':OWN_COUNTS,'all_precise_stages_match':True,'actual_target_input_read':False,
            'graph_completion':False,'mathematical_scope':'finite synthetic/public fixture implementation qualification only'}

def main():
    global CURRENT_SOFTWARE
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=('calibrate','controls','full'))
    for name in ('seconds','out','self-sha256','spec-sha256'):
        parser.add_argument('--'+name,required=True,type=float if name=='seconds' else str)
    for name in ('calibration','producer-plan','producer-summary','producer-manifest','producer-terminal','producer-controls'):
        parser.add_argument('--'+name);parser.add_argument('--'+name+'-sha256')
    args=parser.parse_args();budget=Budget(args.seconds)
    out=safe(args.out,False)
    need(out.is_relative_to(ROOT/'acceleration/results') and not out.exists(),'OUTPUT_FRESH')
    out.mkdir(parents=True)
    reader=Reader(budget)
    software={**SOFTWARE,SELF:args.self_sha256,SPEC:args.spec_sha256};CURRENT_SOFTWARE=software
    try:
        reader.map(software)
        if args.mode=='calibrate':
            outcome=calibrate(out,budget);status=CAL_STATUS
        else:
            for key in ('calibration','producer_plan','producer_summary','producer_manifest','producer_terminal'):
                need(getattr(args,key) is not None and getattr(args,key+'_sha256') is not None,'SOURCE_ARGUMENTS')
            qualification(reader,args,software)
            summary,base=source_packet(reader,args,'calibrate' if args.mode=='controls' else 'screen')
            if args.mode=='controls':
                outcome=replay_controls(reader,summary,base,out);status=CONTROLS_STATUS
            else:
                outcome=full(reader,args,summary,base,out);status=FULL_STATUS
        reader.closing();outputs={}
        for name in sorted(inventory(out,budget)):
            path=out/name;h=hashlib.sha256()
            with path.open('rb') as handle:
                while True:
                    budget.tick();block=handle.read(1024*1024)
                    if not block:break
                    h.update(block)
            outputs[name]=h.hexdigest()
        report={'status':status,'implementation_version':1,'mode':args.mode,'timestamp':datetime.now(timezone.utc).isoformat(),
            'producer':'/root/checkpoint_audit','verifier':'/root/native_driver','checking_source_author':'/root/native_driver',
            'method':'independent_artifact_check','target_resolution':'NONE','source_software':software,
            'inputs_sha256':dict(reader.pins),'outputs_sha256':outputs,'outcome':outcome,'command':[sys.executable,*sys.argv],
            'cwd':str(ROOT),'actual_target_input_read':args.mode=='full','producer_imports':0,'solver_calls':0,
            'graph_completion':False,'automatic_retry':False,'deadline':budget.tick(),
            'shared_components':['Qualified immutable Native count/pair artifacts and written block theorem are trusted mathematical premises',
                'Distinct cumulative histogram arithmetic/set intersections; producer code is never imported',
                'Public analytic fixtures and field/stage taxonomy shared; Native fb651 reader/runtime ancestry copied openly'],
            'limitations':['Exact saved count-vector selected834-Q necessary bounds only, no simultaneous selection or graph completion',
                'Correctly verified failed screen is not target exclusion; a future caller must separately require all_screens_pass true',
                'Raw pair Gram arithmetic inherited from genuine pair gate, no inverse regeneration or whole ancestral closure claim',
                'Guarded20-save allocation intent and actual supported terminal, no hard real-time guarantee']}
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
