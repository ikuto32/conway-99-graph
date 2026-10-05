"""Independent raw integer exterior-count checking; no work occurs on import."""
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
SELF = 'acceleration/audit_20261004_external_moment_integer_counts_v1.py'
SPEC = 'acceleration/audit_20261004_external_moment_integer_counts_v1_spec.md'
MODEL = 'acceleration/results/20261003_external_moment_outside_cn_filter01/filtered_system.json'
TYPES = 'acceleration/results/20261003_external_moment_outside_cn_filter01/types.json'
FIXED = {
    MODEL: 'c628c76325d5b49106740bce7c6d3b72bc7728fdc78d85437ad484f3afbd7306',
    TYPES: '87d0272e244f60f1eefa06d3a0b2d0179a275791f7bb586992b16f648595bad2',
}
SOFTWARE = {
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'acceleration/run_compute_command_v2.py': '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}
ROWS = ((0,1,2),(0,3,4),(0,5,6),(1,7,9),(1,8,10),(15,11,14),
        (16,12,13),(2,15,16),(3,7,11),(4,8,12),(5,9,13),(6,10,14))
PAIR_FIELDS = ('proposal_id','i','j','left_mask','right_mask','intersection',
    'upper_left_diagonal','upper_right_diagonal','upper_cross_0','upper_cross_1',
    'lower_left_diagonal','lower_right_diagonal','lower_cross_0','lower_cross_1',
    'upper_bits','lower_bits','cn_bits','combined_bits','classification')
CLASSES = {(): 'incompatible', (0,): 'forced_nonadjacent',
           (1,): 'forced_adjacent', (0,1): 'either'}
CAL_STATUS = 'INDEPENDENT_EXTERNAL_MOMENT_INTEGER_COUNTS_V1_CALIBRATION_PASS'
CONTROLS_STATUS = 'INDEPENDENT_EXTERNAL_MOMENT_INTEGER_COUNTS_V1_PRODUCER_CONTROLS_PASS'
FULL_STATUS = 'INDEPENDENT_EXTERNAL_MOMENT_INTEGER_COUNTS_V1_COMPLETE_PASS'
PRODUCER = 'acceleration/solve_20261004_fixed17_integer_type_counts_v1.py'
PRODUCER_SPEC = 'acceleration/solve_20261004_fixed17_integer_type_counts_v1_spec.md'
PRODUCER_PINS = {
    PRODUCER:'77ef381e6a07b78203c07d5dad77c28c95b43a699ef6785002c90a672a58a1c4',
    PRODUCER_SPEC:'cf1ca26515b663db3bad3685b5b09d0c34e76a64fed291e0d776dad0ed9a3d8d',
}
AUTHOR_SOFTWARE = {k:v for k,v in SOFTWARE.items() if k != 'acceleration/run_compute_command_v2.py'}
AUTHOR_SOFTWARE.update({
    'build/research-venv/Lib/site-packages/highspy/_core/__init__.pyi':
        '53c07e5eafff940daa32458b20262b07d39420b062e0875c2f56e9ac92f4d699',
    'build/research-venv/Lib/site-packages/highspy/_core.cp312-win_amd64.pyd':
        'f733d7369f647f8afe481bbaf569164f7cd7c127e41ca53cd7c205c2fb9038e2',
    'build/research-venv/Lib/site-packages/highspy/highs.py':
        '00ce58ef248062125309ccdaf7af6374caf1a29f6a04e0d637b7507ead34d51a',
    'build/research-venv/Lib/site-packages/highspy/__init__.py':
        '01df06ec93388a45de66adb43d4b243cd7e11c54f24106064a221facf6aa7eb9',
    'build/research-venv/Lib/site-packages/highspy-1.15.1.dist-info/METADATA':
        'cc09b9d5bf93d8cd79be21bede4e72b686d79cdc75f6524e0e0a1af3e9487a8d',
})
OWN_COUNTS = {'positive':12,'negative':58,'total':70}
AUTHOR_COUNTS = {'positive':11,'negative':30,'total':41}

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
            'Independent exact integer count and complete certified-pair checks; all I/O shares the allocation')
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

def adjacency(rows, n):
    h = [[0] * n for _ in range(n)]
    for row in rows:
        for i, j in itertools.combinations(row, 2):
            need(h[i][j] == 0, 'LITERAL_EDGE_DUPLICATE')
            h[i][j] = h[j][i] = 1
    return h

def graph(raw):
    need(type(raw) is list and raw and all(type(row) is list and len(row) == len(raw) for row in raw),
         'GRAPH_SHAPE')
    n = len(raw)
    need(all(type(v) is int and v in (0,1) for row in raw for v in row), 'GRAPH_INTEGER')
    need(all(raw[i][i] == 0 and raw[i][j] == raw[j][i] for i in range(n) for j in range(n)), 'GRAPH_SIMPLE')
    return raw

def supports(ordered, n):
    need(type(ordered) is list and ordered, 'MASK_SHAPE')
    need(all(type(x) is int for x in ordered), 'MASK_INTEGER')
    need(all(0 <= x < 2 ** n for x in ordered), 'MASK_RANGE')
    need(ordered == sorted(set(ordered)), 'MASK_ORDER')
    return [frozenset(i for i in range(n) if mask & (1 << i)) for mask in ordered]

def moment_system(h, masks, order, degree, adjacent_cn=1, nonadjacent_cn=2):
    h = graph(h)
    n = len(h)
    need(all(type(x) is int for x in (order,degree,adjacent_cn,nonadjacent_cn)) and
         order >= n and degree >= 0 and adjacent_cn >= 0 and nonadjacent_cn >= 0, 'MODEL_PARAMETERS')
    sets = supports(masks, n)
    pairs = list(itertools.combinations(range(n), 2))
    labels = [{'kind':'total'}] + [{'kind':'vertex','vertex':i} for i in range(n)] + [
        {'kind':'pair','vertices':[i,j]} for i,j in pairs]
    rhs = [order-n] + [degree-sum(h[i]) for i in range(n)] + [
        (adjacent_cn if h[i][j] else nonadjacent_cn) - sum(h[i][k]*h[j][k] for k in range(n))
        for i,j in pairs]
    need(all(x >= 0 for x in rhs), 'MODEL_NEGATIVE_DEFICIT')
    columns = [[1] + [int(i in s) for i in range(n)] + [int(i in s and j in s) for i,j in pairs]
               for s in sets]
    return labels, rhs, columns, sets

def count_vector(raw, count, maximum):
    need(type(raw) is list and len(raw) == count, 'COUNT_SHAPE')
    need(all(type(v) is int for v in raw), 'COUNT_INTEGER')
    need(all(0 <= v <= maximum for v in raw), 'COUNT_RANGE')
    return raw

def presence_vector(raw, counts):
    need(type(raw) is list and len(raw) == len(counts), 'PRESENCE_SHAPE')
    need(all(type(v) is int and v in (0,1) for v in raw), 'PRESENCE_BINARY')
    need(all(v == int(c > 0) for c,v in zip(counts,raw)), 'PRESENCE_COUNT_EQUIVALENCE')
    return raw

def moments(counts, labels, rhs, columns, budget):
    need(len(columns) == len(counts) and len(rhs) == len(labels), 'MOMENT_SHAPE')
    result = []
    for r, (label, wanted) in enumerate(zip(labels,rhs)):
        budget.tick()
        actual = sum(counts[j] * columns[j][r] for j in range(len(counts)))
        need(actual == wanted, 'MOMENT_EQUATION')
        result.append({'row':r,'label':label,'lhs':actual,'rhs':wanted,'equal':True})
    return result

def triple_caps(counts, sets, n, budget):
    result = []
    for row, points in enumerate(itertools.combinations(range(n),3)):
        budget.tick()
        q = frozenset(points)
        value = sum(counts[j] for j,s in enumerate(sets) if q <= s)
        need(value <= 1, 'COMMON_Q_CAP')
        result.append({'row':row,'Q':list(points),'sum':value,'holds':True})
    return result

def pair_structure(raw, pid, i, j, ordered):
    need(type(raw) is dict and set(raw) == set(PAIR_FIELDS), 'PAIR_FIELDS')
    need(all(type(raw[k]) is int for k in PAIR_FIELDS[:14]), 'PAIR_INTEGER')
    for k in ('upper_bits','lower_bits','cn_bits','combined_bits'):
        value = raw[k]
        need(type(value) is list and all(type(v) is int and v in (0,1) for v in value) and
             value == sorted(set(value)), 'PAIR_BITS')
    need((raw['proposal_id'],raw['i'],raw['j'],raw['left_mask'],raw['right_mask']) ==
         (pid,i,j,ordered[i],ordered[j]), 'PAIR_ORDER')
    overlap = (ordered[i] & ordered[j]).bit_count()
    need(raw['intersection'] == overlap and raw['cn_bits'] == [a for a in (0,1) if overlap <= 2-a],
         'PAIR_CN')
    joint = [a for a in (0,1) if all(a in raw[k] for k in ('upper_bits','lower_bits','cn_bits'))]
    need(raw['combined_bits'] == joint and type(raw['classification']) is str and
         raw['classification'] == CLASSES[tuple(joint)], 'PAIR_CLASSIFICATION')
    # Schur arithmetic was checked by the exact source-bound pair COMPLETE gate.
    # This new checker inherits that fact, and never infers a different bit.
    return joint

def no_good(counts, presence, i, j, allowed):
    if allowed:
        return None
    if i == j:
        need(counts[i] <= 1, 'EQUAL_TYPE_MULTIPLICITY')
        return {'kind':'equal_multiplicity','i':i,'count':counts[i],'upper_bound':1,'holds':True}
    need(presence[i] + presence[j] <= 1 and counts[i] * counts[j] == 0, 'PAIR_NO_GOOD')
    return {'kind':'distinct_no_good','i':i,'j':j,'presence_sum':presence[i]+presence[j],
            'product':counts[i]*counts[j],'holds':True}

def integer_candidate(counts_raw, presence_raw, h, ordered, order, degree, pair_rows, budget):
    labels,rhs,columns,sets = moment_system(h,ordered,order,degree)
    counts = count_vector(counts_raw,len(ordered),order-len(h))
    presence = presence_vector(presence_raw,counts)
    equations = moments(counts,labels,rhs,columns,budget)
    caps = triple_caps(counts,sets,len(h),budget)
    restrictions = []
    need(type(pair_rows) is list and len(pair_rows) == len(ordered)*(len(ordered)+1)//2, 'PAIR_POPULATION')
    for pid,(i,j) in enumerate(itertools.combinations_with_replacement(range(len(ordered)),2)):
        budget.tick()
        allowed = pair_structure(pair_rows[pid],pid,i,j,ordered)
        witness = no_good(counts,presence,i,j,allowed)
        if witness is not None:
            restrictions.append(witness)
    return {'counts':counts,'presence':presence,'moment_rows':equations,'common_Q_caps':caps,
            'incompatibility_checks':restrictions,'all_pair_records_checked':len(pair_rows)}

def fixed_input(model, raw_types):
    need(type(model) is dict and model.get('schema') == 'OUTSIDE_VERTEX_CN_FILTERED_MOMENT_SYSTEM_V1',
         'FIXED_MODEL_SCHEMA')
    for key,value in {'target_order':99,'target_degree':14,'adjacent_cn':1,'nonadjacent_cn':2,
                      'original_eligible_type_count':534,'eligible_type_count':472}.items():
        need(type(model.get(key)) is int and model[key] == value, 'FIXED_MODEL_DOMAIN')
    h = adjacency(ROWS,17)
    need(same(model.get('ordered_support_vertices'),list(range(17))) and
         same(model.get('induced_adjacency'),h), 'FIXED_H_ALL289')
    need(type(raw_types) is list and len(raw_types) == 472, 'FIXED_TYPE_POPULATION')
    need(all(type(item) is dict and set(item) == {'mask','coefficient'} for item in raw_types),
         'FIXED_TYPE_FIELDS')
    ordered = [item['mask'] for item in raw_types]
    labels,rhs,columns,sets = moment_system(h,ordered,99,14)
    need(same(model.get('row_labels'),labels) and same(model.get('right_hand_side'),rhs), 'FIXED_154_RHS')
    need(all(same(item['coefficient'],column) for item,column in zip(raw_types,columns)), 'FIXED_TYPE_COEFFICIENT')
    need(model.get('retained_coefficients_are_literal_originals') is True and
         model.get('original_row_labels_rhs_unchanged') is True, 'FIXED_MODEL_PROVENANCE')
    return h,ordered,labels,rhs,columns,sets

def sparse_rows(h, ordered, order, degree, forbidden, equal_forbidden, budget):
    labels,rhs,columns,sets = moment_system(h,ordered,order,degree)
    count = len(ordered)
    need(type(forbidden) is list and all(type(p) is list and len(p) == 2 and
         all(type(i) is int for i in p) and 0 <= p[0] < p[1] < count for p in forbidden)
         and forbidden == sorted(forbidden) and len({tuple(p) for p in forbidden}) == len(forbidden),
         'FORBIDDEN_PAIR_ORDER')
    need(type(equal_forbidden) is list and all(type(i) is int and 0 <= i < count for i in equal_forbidden)
         and equal_forbidden == sorted(set(equal_forbidden)), 'EQUAL_FORBIDDEN_ORDER')
    upper = [1 if len(s) >= 3 or i in equal_forbidden else order-len(h) for i,s in enumerate(sets)]
    rows = []
    for r,wanted in enumerate(rhs):
        budget.tick()
        rows.append({'kind':'moment','origin':r,'lower':wanted,'upper':wanted,
                     'terms':[[j,column[r]] for j,column in enumerate(columns) if column[r]]})
    triples = list(itertools.combinations(range(len(h)),3))
    for points in triples:
        budget.tick()
        q = frozenset(points)
        rows.append({'kind':'triple','origin':list(points),'lower':None,'upper':1,
                     'terms':[[j,1] for j,s in enumerate(sets) if q <= s]})
    for j,u in enumerate(upper):
        budget.tick()
        rows.append({'kind':'presence_lower','origin':j,'lower':0,'upper':None,
                     'terms':[[j,1],[count+j,-1]]})
        rows.append({'kind':'presence_upper','origin':j,'lower':None,'upper':0,
                     'terms':[[j,1],[count+j,-u]]})
    for i,j in forbidden:
        budget.tick()
        rows.append({'kind':'forbidden_pair','origin':[i,j],'lower':None,'upper':1,
                     'terms':[[count+i,1],[count+j,1]]})
    return rows,upper,labels,rhs,columns,[list(p) for p in triples]

def checked_sparse_rows(raw, expected, variables):
    need(type(raw) is list and len(raw) == len(expected), 'SPARSE_ROW_POPULATION')
    for observed,wanted in zip(raw,expected):
        need(type(observed) is dict and set(observed) == {'kind','origin','lower','upper','terms'}, 'SPARSE_ROW_FIELDS')
        need(type(observed['kind']) is str, 'SPARSE_ROW_KIND')
        need(all(value is None or type(value) is int for value in (observed['lower'],observed['upper'])),
             'SPARSE_ROW_BOUND_INTEGER')
        terms = observed['terms']
        need(type(terms) is list and all(type(t) is list and len(t) == 2 and all(type(v) is int for v in t)
             and 0 <= t[0] < variables and t[1] != 0 for t in terms), 'SPARSE_TERM_INTEGER')
        need(same(observed,wanted), 'SPARSE_ROW_IDENTITY')

def count_type_upper(counts, upper):
    need(len(counts) == len(upper) and all(count <= bound for count,bound in zip(counts,upper)), 'COUNT_TYPE_UPPER')

def exact_sparse_evaluation(counts, presence, rows, budget):
    values = counts + presence
    result = []
    for index,row in enumerate(rows):
        budget.tick()
        value = sum(values[j]*coefficient for j,coefficient in row['terms'])
        need((row['lower'] is None or value >= row['lower']) and
             (row['upper'] is None or value <= row['upper']), 'SPARSE_CANDIDATE_CONSTRAINT')
        result.append({'row':index,'kind':row['kind'],'origin':row['origin'],'value':value,
                       'lower':row['lower'],'upper':row['upper'],'holds':True})
    return result

def expected_model(h, ordered, order, degree, forbidden, equal, budget):
    rows,upper,labels,rhs,columns,triples = sparse_rows(h,ordered,order,degree,forbidden,equal,budget)
    count = len(ordered)
    matrix = [[column[r] for column in columns] for r in range(len(rhs))]
    return {'schema':'FIXED17_INTEGER_TYPE_COUNT_MODEL_V1','ordered_masks':ordered,'count_variables':count,
        'presence_variables':count,'variables':2*count,'objective':[0]*(2*count),'lower':[0]*(2*count),
        'upper':upper+[1]*count,'all_columns_integer':True,'rows':rows,'moment_rhs':rhs,'moments':matrix,
        'triples':triples,'forbidden_distinct_pairs':forbidden,'equal_forbidden_indices':equal,'target_graph':False}

def model_identity(raw, expected):
    need(type(raw) is dict and set(raw) == set(expected), 'COUNT_MODEL_FIELDS')
    for name in ('count_variables','presence_variables','variables'):
        need(type(raw[name]) is int, 'COUNT_MODEL_INTEGER')
    for name in ('ordered_masks','objective','lower','upper','moment_rhs','equal_forbidden_indices'):
        need(type(raw[name]) is list and all(type(v) is int for v in raw[name]), 'COUNT_MODEL_INTEGER')
    need(type(raw['moments']) is list and all(type(row) is list and all(type(v) is int for v in row)
         for row in raw['moments']), 'COUNT_MODEL_INTEGER')
    checked_sparse_rows(raw['rows'],expected['rows'],expected['variables'])
    need(same(raw,expected), 'COUNT_MODEL_IDENTITY')

def guidance(raw, variables):
    need(type(raw) is dict and raw.get('floating_status_is_proof') is False and
         raw.get('numeric_infeasibility_is_proof') is False, 'GUIDANCE_SCOPE')
    values = raw.get('col_value')
    need(type(values) is list and len(values) == variables, 'GUIDANCE_SHAPE')
    need(all(type(x) is float and math.isfinite(x) for x in values), 'GUIDANCE_FINITE')
    need(raw.get('schema') == 'FIXED17_INTEGER_TYPE_COUNT_NUMERIC_GUIDANCE_V1' and
         type(raw.get('native_version')) is str and type(raw.get('numpy_version')) is str and
         type(raw.get('run_status')) is str and type(raw.get('model_status')) is str and
         type(raw.get('solution_value_valid')) is bool and raw.get('objective_all_zero') is True and
         type(raw.get('solver_calls')) is int and raw['solver_calls'] == 1, 'GUIDANCE_HEADER')
    need(same(raw.get('col_value_float_hex'),[x.hex() for x in values]), 'GUIDANCE_FLOAT_HEX')
    need(type(raw.get('wall_seconds')) in (int,float) and math.isfinite(raw['wall_seconds']) and
         raw['wall_seconds'] >= 0, 'GUIDANCE_WALL')
    return values

def candidate_wire(raw, ordered, maximum):
    need(type(raw) is dict and set(raw) == {'schema','ordered_masks','counts','presence','integer',
         'exact_constraints','independent_approval','graph_completion'} and
         raw['schema'] == 'FIXED17_EXACT_INTEGER_TYPE_COUNTS_V1', 'CANDIDATE_SCHEMA')
    need(same(raw['ordered_masks'],ordered), 'CANDIDATE_MASK_IDENTITY')
    need(raw['integer'] is True and raw['exact_constraints'] is True and
         raw['independent_approval'] is False and raw['graph_completion'] is False, 'CANDIDATE_FLAGS')
    counts = count_vector(raw['counts'],len(ordered),maximum)
    presence = presence_vector(raw['presence'],counts)
    return counts,presence

def pair_gate_header(raw, required=None, fixture=False):
    need(type(raw) is dict and raw.get('status') == 'INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS'
         and type(raw.get('implementation_version')) is int and raw['implementation_version'] == 2
         and raw.get('mode') == 'full' and raw.get('producer') == '/root/structural'
         and raw.get('verifier') == '/root/native_driver' and raw.get('method') == 'independent_artifact_check'
         and raw.get('target_resolution') == 'NONE', 'PAIR_GATE_HEADER')
    required = required if required is not None else {
        'acceleration/audit_20261004_fixed17_dual_gram_pairs_v2.py':
            '7f7b9f965d2d6051af7614c4a7ab2737504a455eeb086f9b96b9d9ead57fe3bf',
        'acceleration/audit_20261004_fixed17_dual_gram_pairs_v2_spec.md':
            'e3728e455da83f4291b361931c944902fb54e7384e54b3a49901ced92f04e032'}
    pins = raw.get('inputs_sha256')
    need(type(pins) is dict and all(pins.get(p) == h for p,h in required.items()), 'PAIR_GATE_SOURCE')
    outcome = raw.get('outcome')
    wanted = {
        'complete_pair_records':111628,'complete_record_fields':19,'complete_parts':23,
        'complete_checkpoints':23,'final_part_records':1628,'complete_scaled_type_vectors':472,
        'complete_induced_adjacency_entries':289}
    if not fixture:
        wanted['complete_submitted_inverse_product_entries'] = 1156
    need(type(outcome) is dict and all(type(outcome.get(k)) is int and outcome[k] == v for k,v in wanted.items()),
        'PAIR_GATE_COUNTS')
    need(outcome.get('equal_types_are_distinct_external_vertices') is True and
         outcome.get('same_adjacency_bit_required') is True, 'PAIR_GATE_SCOPE')

def candidate_state(summary, extraction, output_names):
    need(type(extraction) is dict and 'candidate' in extraction, 'EXTRACTION_SCHEMA')
    outcome = summary.get('outcome')
    need(type(outcome) is dict and type(outcome.get('exact_integer_candidate_produced')) is bool,
         'CANDIDATE_OUTCOME')
    present = extraction['candidate'] is not None
    expected_status = 'CANDIDATE_FIXED17_INTEGER_TYPE_COUNTS_V1' if present else 'NO_EXACT_INTEGER_COUNT_WITNESS_V1'
    need(summary.get('status') == expected_status and outcome['exact_integer_candidate_produced'] == present,
         'CANDIDATE_STATUS')
    need(('exact_integer_candidate.json' in output_names) == present and
         ('exact_constraint_rows.json' in output_names) == present, 'CANDIDATE_FILE_POPULATION')
    if not present:
        need(type(extraction.get('reason')) is str and extraction['reason'] and
             outcome.get('certificate_unavailable_reason') == extraction['reason'], 'CANDIDATE_ABSENT_REASON')
    return present

def fixture_pairs(ordered):
    records = []
    for pid,(i,j) in enumerate(itertools.combinations_with_replacement(range(len(ordered)),2)):
        overlap = (ordered[i] & ordered[j]).bit_count()
        bits = [a for a in (0,1) if overlap <= 2-a]
        record = {k:0 for k in PAIR_FIELDS[:14]}
        record.update(proposal_id=pid,i=i,j=j,left_mask=ordered[i],right_mask=ordered[j],intersection=overlap,
            upper_bits=[0,1],lower_bits=[0,1],cn_bits=bits,combined_bits=list(bits),classification=CLASSES[tuple(bits)])
        records.append(record)
    return records

def rook_fixture():
    # Literal valid rook(3,3) outside counts for S=(0,1,3). No optimizer or
    # producer control helper supplies these independently hand-derived values.
    h = [[0,1,1],[1,0,0],[1,0,0]]
    ordered = list(range(8))
    counts = [1,0,1,1,1,1,1,0]
    raw = {'schema':'FIXED17_EXACT_INTEGER_TYPE_COUNTS_V1','ordered_masks':ordered,'counts':counts,
           'presence':[1,0,1,1,1,1,1,0],'integer':True,'exact_constraints':True,
           'independent_approval':False,'graph_completion':False}
    return h,ordered,raw,fixture_pairs(ordered)

def own_header(raw, software):
    need(type(raw) is dict and raw.get('status') == CAL_STATUS and raw.get('mode') == 'calibrate'
         and type(raw.get('implementation_version')) is int and raw['implementation_version'] == 1
         and raw.get('producer') == '/root/checkpoint_audit' and raw.get('verifier') == '/root/native_driver'
         and raw.get('method') == 'independent_artifact_check' and raw.get('target_resolution') == 'NONE'
         and raw.get('actual_target_input_read') is False and same(raw.get('source_software'),software),
         'OWN_CALIBRATION_HEADER')

def own_routes(budget):
    h,ordered,baseline,pairs = rook_fixture()
    def run_candidate(p):
        counts,presence = candidate_wire(p,ordered,6)
        return integer_candidate(counts,presence,h,ordered,9,4,pairs,budget)
    labels,rhs,columns,sets = moment_system(h,ordered,9,4)
    exact = {'labels':labels,'rhs':rhs,'columns':columns}
    def check_model(p):
        need(type(p) is dict and set(p) == set(exact), 'MODEL_FIELDS')
        need(type(p['rhs']) is list and all(type(x) is int for x in p['rhs']), 'MODEL_RHS_INTEGER')
        need(same(p['rhs'],rhs), 'MODEL_RHS_IDENTITY')
        need(type(p['columns']) is list and all(type(r) is list and all(type(x) is int for x in r)
             for r in p['columns']), 'MODEL_COLUMN_INTEGER')
        need(same(p['columns'],columns), 'MODEL_COLUMN_IDENTITY')
        need(same(p['labels'],labels), 'MODEL_LABEL_IDENTITY')
    good_guidance = {'schema':'FIXED17_INTEGER_TYPE_COUNT_NUMERIC_GUIDANCE_V1',
        'col_value':[0.0,1.0],'col_value_float_hex':[0.0.hex(),1.0.hex()],
        'native_version':'synthetic','numpy_version':'synthetic','run_status':'synthetic','model_status':'synthetic',
        'solution_value_valid':True,'solver_calls':1,'wall_seconds':1.0,'objective_all_zero':True,
        'floating_status_is_proof':False,'numeric_infeasibility_is_proof':False}
    fake_gate = {'status':'INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS','implementation_version':2,
        'mode':'full','producer':'/root/structural','verifier':'/root/native_driver',
        'method':'independent_artifact_check','target_resolution':'NONE',
        'inputs_sha256':{'acceleration/audit_20261004_fixed17_dual_gram_pairs_v2.py':
            '7f7b9f965d2d6051af7614c4a7ab2737504a455eeb086f9b96b9d9ead57fe3bf',
            'acceleration/audit_20261004_fixed17_dual_gram_pairs_v2_spec.md':
            'e3728e455da83f4291b361931c944902fb54e7384e54b3a49901ced92f04e032'},
        'outcome':{'complete_pair_records':111628,'complete_record_fields':19,'complete_parts':23,
            'complete_checkpoints':23,'final_part_records':1628,'complete_scaled_type_vectors':472,
            'complete_induced_adjacency_entries':289,'complete_submitted_inverse_product_entries':1156,
            'equal_types_are_distinct_external_vertices':True,'same_adjacency_bit_required':True}}
    qualification = {'status':CAL_STATUS,'mode':'calibrate','implementation_version':1,
        'producer':'/root/checkpoint_audit','verifier':'/root/native_driver','method':'independent_artifact_check',
        'target_resolution':'NONE','actual_target_input_read':False,'source_software':{'synthetic':'pin'}}
    routes = [
        ('positive_rook_exact','PASS',baseline,run_candidate),
        ('positive_rook_model','PASS',exact,check_model),
        ('positive_low_type_multiplicity','PASS',{'counts':[2],'presence':[1]},
            lambda p:no_good(p['counts'],p['presence'],0,0,[0,1])),
        ('positive_equal_single','PASS',{'counts':[1],'presence':[1]},
            lambda p:no_good(p['counts'],p['presence'],0,0,[])),
        ('positive_distinct_zero','PASS',{'counts':[2,0],'presence':[1,0]},
            lambda p:no_good(p['counts'],p['presence'],0,1,[])),
        ('positive_guidance','PASS',good_guidance,lambda p:guidance(p,2)),
        ('positive_no_incumbent_guidance','PASS',{**good_guidance,'solution_value_valid':False},
            lambda p:guidance(p,2)),
        ('positive_pair_gate','PASS',fake_gate,pair_gate_header),
        ('positive_own_header','PASS',qualification,lambda p:own_header(p,{'synthetic':'pin'})),
        ('positive_candidate_absent','PASS',{
            'summary':{'status':'NO_EXACT_INTEGER_COUNT_WITNESS_V1',
                'outcome':{'exact_integer_candidate_produced':False,
                           'certificate_unavailable_reason':'No complete value-valid numerical incumbent'}},
            'extraction':{'candidate':None,'reason':'No complete value-valid numerical incumbent'},
            'output_names':['integer_model.json','scientific_guidance.json','extraction.json']},
            lambda p:candidate_state(p['summary'],p['extraction'],p['output_names'])),
    ]
    def mutation(name, stage, original, change, action):
        p = copy.deepcopy(original)
        change(p)
        routes.append((name,stage,p,action))
    mutation('candidate_schema','CANDIDATE_SCHEMA',baseline,lambda p:p.__setitem__('schema','wrong'),run_candidate)
    for name,value in [('mask_bool',True),('mask_float',0.0)]:
        mutation(name,'CANDIDATE_MASK_IDENTITY',baseline,lambda p,v=value:p['ordered_masks'].__setitem__(0,v),run_candidate)
    mutation('mask_order','CANDIDATE_MASK_IDENTITY',baseline,
        lambda p:p.__setitem__('ordered_masks',[1,0,2,3,4,5,6,7]),run_candidate)
    for name,value,stage in [('count_bool',True,'COUNT_INTEGER'),('count_float',1.0,'COUNT_INTEGER'),
        ('count_negative',-1,'COUNT_RANGE'),('count_large',7,'COUNT_RANGE')]:
        mutation(name,stage,baseline,lambda p,v=value:p['counts'].__setitem__(0,v),run_candidate)
    mutation('count_short','COUNT_SHAPE',baseline,lambda p:p['counts'].pop(),run_candidate)
    for name,value in [('presence_bool',True),('presence_float',1.0),('presence_two',2)]:
        mutation(name,'PRESENCE_BINARY',baseline,lambda p,v=value:p['presence'].__setitem__(0,v),run_candidate)
    mutation('presence_short','PRESENCE_SHAPE',baseline,lambda p:p['presence'].pop(),run_candidate)
    mutation('presence_wrong','PRESENCE_COUNT_EQUIVALENCE',baseline,lambda p:p['presence'].__setitem__(0,0),run_candidate)
    for name,key,value in [('integer_int','integer',1),('exact_int','exact_constraints',1),
        ('self_approval','independent_approval',True),('graph_completion','graph_completion',True)]:
        mutation(name,'CANDIDATE_FLAGS',baseline,lambda p,k=key,v=value:p.__setitem__(k,v),run_candidate)
    mutation('wrong_moment','MOMENT_EQUATION',baseline,lambda p:p['counts'].__setitem__(0,2),run_candidate)
    cap_counts = list(baseline['counts']); cap_counts[7] = 2
    routes.append(('common_Q_two','COMMON_Q_CAP',cap_counts,lambda p:triple_caps(p,sets,3,budget)))
    routes.extend([
        ('equal_two','EQUAL_TYPE_MULTIPLICITY',{'counts':[2],'presence':[1]},
            lambda p:no_good(p['counts'],p['presence'],0,0,[])),
        ('distinct_both','PAIR_NO_GOOD',{'counts':[1,2],'presence':[1,1]},
            lambda p:no_good(p['counts'],p['presence'],0,1,[]))])
    first = pairs[0]
    def first_pair(p):
        return pair_structure(p,0,0,0,ordered)
    for name,key,value,stage in [('pair_extra','extra',1,'PAIR_FIELDS'),('pair_bool','j',False,'PAIR_INTEGER'),
        ('pair_bits_bool','cn_bits',[False,1],'PAIR_BITS'),('pair_order','proposal_id',1,'PAIR_ORDER'),
        ('pair_mask','right_mask',1,'PAIR_ORDER'),('pair_cn','intersection',1,'PAIR_CN'),
        ('pair_class','classification','incompatible','PAIR_CLASSIFICATION')]:
        mutation(name,stage,first,lambda p,k=key,v=value:p.__setitem__(k,v),first_pair)
    mutation('rhs_bool','MODEL_RHS_INTEGER',exact,lambda p:p['rhs'].__setitem__(0,True),check_model)
    mutation('rhs_wrong','MODEL_RHS_IDENTITY',exact,lambda p:p['rhs'].__setitem__(0,5),check_model)
    mutation('column_bool','MODEL_COLUMN_INTEGER',exact,lambda p:p['columns'][0].__setitem__(0,True),check_model)
    mutation('column_late','MODEL_COLUMN_IDENTITY',exact,lambda p:p['columns'][-1].__setitem__(-1,0),check_model)
    mutation('label_order','MODEL_LABEL_IDENTITY',exact,lambda p:p['labels'].reverse(),check_model)
    for name,value,stage in [('guide_string','1','GUIDANCE_FINITE'),('guide_bool',True,'GUIDANCE_FINITE'),
        ('guide_nonfinite','inf','GUIDANCE_FINITE')]:
        mutation(name,stage,good_guidance,lambda p,v=value:p['col_value'].__setitem__(0,v),lambda p:guidance(p,2))
    mutation('guide_proof','GUIDANCE_SCOPE',good_guidance,
        lambda p:p.__setitem__('floating_status_is_proof',True),lambda p:guidance(p,2))
    mutation('guide_short','GUIDANCE_SHAPE',good_guidance,lambda p:p['col_value'].pop(),lambda p:guidance(p,2))
    routes.extend([('json_duplicate','JSON_DUPLICATE','{"n":0,"n":1}',decode),
                   ('json_nonfinite','JSON_NONFINITE','{"n":NaN}',decode)])
    mutation('pair_gate_bool_version','PAIR_GATE_HEADER',fake_gate,
        lambda p:p.__setitem__('implementation_version',True),pair_gate_header)
    mutation('pair_gate_source','PAIR_GATE_SOURCE',fake_gate,
        lambda p:p['inputs_sha256'].__setitem__('acceleration/audit_20261004_fixed17_dual_gram_pairs_v2.py','wrong'),pair_gate_header)
    mutation('pair_gate_bool_count','PAIR_GATE_COUNTS',fake_gate,
        lambda p:p['outcome'].__setitem__('complete_pair_records',True),pair_gate_header)
    for name,key,value in [('own_bool_version','implementation_version',True),
        ('own_wrong_method','method','independent_derivation'),('own_wrong_source','source_software',{})]:
        mutation(name,'OWN_CALIBRATION_HEADER',qualification,
            lambda p,k=key,v=value:p.__setitem__(k,v),lambda p:own_header(p,{'synthetic':'pin'}))
    sparse,_,_,_,_,_ = sparse_rows(h,ordered,9,4,[[0,2]],[7],budget)
    run_sparse = lambda p:checked_sparse_rows(p,sparse,16)
    routes.append(('positive_sparse_model','PASS',sparse,run_sparse))
    mutation('sparse_bound_bool','SPARSE_ROW_BOUND_INTEGER',sparse,
        lambda p:p[0].__setitem__('lower',True),run_sparse)
    mutation('sparse_term_bool','SPARSE_TERM_INTEGER',sparse,
        lambda p:p[0]['terms'][0].__setitem__(1,True),run_sparse)
    mutation('sparse_last_coefficient','SPARSE_ROW_IDENTITY',sparse,
        lambda p:p[-1]['terms'][-1].__setitem__(1,2),run_sparse)
    mutation('sparse_short','SPARSE_ROW_POPULATION',sparse,lambda p:p.pop(),run_sparse)
    mutation('sparse_origin_bool','SPARSE_ROW_IDENTITY',sparse,
        lambda p:p[0].__setitem__('origin',False),run_sparse)
    rt = synthetic_runtime()
    run_runtime = lambda p:runtime(p['plan'],p['manifest'],p['terminal'],p['summary'],'calibrate',{'source':'pin','spec':'pin'})
    routes.append(('positive_runtime','PASS',rt,run_runtime))
    for name,change,stage in [
        ('runtime_exit_bool',lambda p:p['terminal'].__setitem__('command_exit_code',False),'RUNTIME_EXIT'),
        ('runtime_live_job',lambda p:p['terminal']['cleanup'].__setitem__('job_active_zero_observed',False),'RUNTIME_CLEANUP'),
        ('runtime_source_wrong',lambda p:p['manifest'].__setitem__('source_sha256','wrong'),'RUNTIME_MANIFEST'),
        ('runtime_invocation_wrong',lambda p:p['terminal'].__setitem__('invocation_id','other'),'RUNTIME_INVOCATION'),
        ('runtime_command_wrong',lambda p:p['summary'].__setitem__('command',p['summary']['command'][1:]),'RUNTIME_SUMMARY_COMMAND'),
        ('runtime_elapsed_string',lambda p:p['terminal'].__setitem__('elapsed_seconds','inf'),'RUNTIME_ELAPSED')]:
        mutation(name,stage,rt,change,run_runtime)
    return routes

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

def pair_evidence(reader, gate_path, gate_digest, source_summary_path):
    gate = reader.read(gate_path,gate_digest)
    pair_gate_header(gate)
    need(all(gate['inputs_sha256'].get(p) == h for p,h in FIXED.items()), 'PAIR_FIXED_DIRECT_PINS')
    reader.map(gate['inputs_sha256'])
    key = safe(source_summary_path).relative_to(ROOT).as_posix()
    need(key in gate['inputs_sha256'], 'PAIR_RAW_SUMMARY_PIN')
    summary,base = packet(reader,source_summary_path,gate['inputs_sha256'][key])
    expected = {'scaled_input.json'}|{kind+'_%03d.json'%i for i in range(23) for kind in ('part','checkpoint')}
    need(summary.get('status') == 'CANDIDATE_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE' and
         set(summary['outputs_sha256']) == expected, 'PAIR_RAW_PACKET')
    for name,digest in summary['outputs_sha256'].items():
        raw_key = (base/name).relative_to(ROOT).as_posix()
        need(gate['inputs_sha256'].get(raw_key) == digest, 'PAIR_RAW_FILE_PIN')
    return gate,summary,base

def pair_rules(reader, summary, base, ordered):
    records,forbidden,equal,rules = [],[],[],[]
    positions = iter(itertools.combinations_with_replacement(range(len(ordered)),2))
    outputs = summary['outputs_sha256']
    prefix = []
    for index in range(23):
        reader.budget.tick()
        start,stop = index*5000,min((index+1)*5000,111628)
        name = 'part_%03d.json'%index
        part = reader.read(base/name,outputs[name])
        need(type(part) is dict and set(part) == {'schema','part_index','start','stop','count','records'}
             and part['schema'] == 'DUAL_GRAM_PAIR_PART_V1', 'PAIR_PART_FIELDS')
        need(all(type(part[k]) is int for k in ('part_index','start','stop','count')) and
             (part['part_index'],part['start'],part['stop'],part['count']) == (index,start,stop,stop-start),
             'PAIR_PART_BOUNDARY')
        need(type(part['records']) is list and len(part['records']) == stop-start, 'PAIR_PART_POPULATION')
        for raw in part['records']:
            reader.budget.tick()
            i,j = next(positions)
            pid = len(records)
            allowed = pair_structure(raw,pid,i,j,ordered)
            records.append(raw)
            if not allowed:
                if i == j:
                    equal.append(i)
                else:
                    forbidden.append([i,j])
                rules.append({'proposal_id':pid,'i':i,'j':j,'left_mask':ordered[i],'right_mask':ordered[j],
                    'rule':'multiplicity_at_most_one' if i == j else 'presence_sum_at_most_one'})
        prefix.append({'pair_records':stop,'total':111628,'forbidden_distinct_pairs':len(forbidden),
                       'equal_forbidden_types':len(equal)})
    need(len(records) == 111628 and next(positions,None) is None, 'PAIR_COMPLETE_POPULATION')
    return records,forbidden,equal,rules,prefix

def source_packet(reader, args, mode):
    plan = reader.read(args.producer_plan,args.producer_plan_sha256)
    summary,base = packet(reader,args.producer_summary,args.producer_summary_sha256)
    manifest = reader.read(args.producer_manifest,args.producer_manifest_sha256)
    terminal = reader.read(args.producer_terminal,args.producer_terminal_sha256)
    if mode == 'calibrate':
        need(plan.get('schema') == 'FIXED17_INTEGER_TYPE_COUNTS_SOURCE_ONLY_PLAN_V1' and
             plan.get('source_sha256') == PRODUCER_PINS[PRODUCER] and
             plan.get('spec_sha256') == PRODUCER_PINS[PRODUCER_SPEC] and
             type(plan.get('calibration')) is dict, 'PRODUCER_CALIBRATION_PLAN')
        profile = plan['calibration']
    else:
        need(plan.get('schema') == 'FIXED17_INTEGER_TYPE_COUNTS_CONCRETE_SCIENCE_PLAN_V1' and
             type(plan.get('solve')) is dict and all(same(plan.get(k),plan['solve'].get(k))
             for k in ('command','child_argv','worker_argv')), 'PRODUCER_SCIENCE_PLAN')
        profile = plan['solve']
    flags = runtime(profile,manifest,terminal,summary,mode,
                    {'source':PRODUCER_PINS[PRODUCER],'spec':PRODUCER_PINS[PRODUCER_SPEC]})
    need(safe(flags['--out'],False) == base, 'PRODUCER_OUTPUT_ROOT')
    need(summary.get('schema') == 'FIXED17_INTEGER_TYPE_COUNT_PRODUCER_REPORT_V1' and
         type(summary.get('implementation_version')) is int and summary['implementation_version'] == 1 and
         summary.get('mode') == mode and summary.get('producer') == '/root/checkpoint_audit' and
         summary.get('source_author') == '/root/checkpoint_audit' and summary.get('target_resolution') == 'NONE',
         'PRODUCER_HEADER')
    need(same(summary.get('source_software'),{**AUTHOR_SOFTWARE,**PRODUCER_PINS}) and
         summary.get('actual_target_input_read') == (mode == 'solve') and
         type(summary.get('actual_target_input_read')) is bool and summary.get('automatic_retry') is False and
         summary.get('independent_approval') is False and summary.get('old_primal_positive_support_filter_used') is False
         and type(summary.get('LP_search_calls')) is int and summary['LP_search_calls'] == 0 and
         type(summary.get('ledger_index_git_mutations')) is int and summary['ledger_index_git_mutations'] == 0 and
         summary.get('complete_ancestor_evidence_closure_rehashed') is False, 'PRODUCER_LIMITATIONS')
    reader.map(summary.get('inputs_sha256'))
    return summary,base,flags

def own_controls(out, budget):
    routes = own_routes(budget)
    need(len(routes) == OWN_COUNTS['total'] and sum(stage == 'PASS' for _,stage,_,_ in routes) == OWN_COUNTS['positive']
         and len({name for name,_,_,_ in routes}) == len(routes), 'OWN_ROUTE_POPULATION')
    rows = []
    for name,expected,payload,function in routes:
        budget.tick()
        write(out/('control_'+name+'.json'),payload,budget)
        actual = 'PASS'
        try:
            function(copy.deepcopy(payload))
        except Veto as exc:
            actual = str(exc)
        rows.append({'name':name,'expected_stage':expected,'actual_stage':actual})
        need(actual == expected, 'OWN_STAGE:'+name+':'+actual)
    write(out/'controls.json',rows,budget)
    return {'controls':OWN_COUNTS,'known_rook_exterior_vertices':6,'candidate_absent_exercised':True,
            'actual_target_input_read':False,'solver_calls':0}

def qualify_own(reader, path, digest, software):
    snapshot = dict(software)
    summary,base = packet(reader,path,digest)
    own_header(summary,snapshot)
    need(same(summary.get('inputs_sha256'),snapshot) and
         same(summary.get('outcome',{}).get('controls'),OWN_COUNTS), 'OWN_CALIBRATION_SCOPE')
    routes = own_routes(reader.budget)
    names = {'control_'+name+'.json' for name,_,_,_ in routes}|{'controls.json'}
    need(set(summary['outputs_sha256']) == names, 'OWN_OUTPUT_POPULATION')
    table = reader.read(base/'controls.json',summary['outputs_sha256']['controls.json'])
    expected = [{'name':name,'expected_stage':stage,'actual_stage':stage} for name,stage,_,_ in routes]
    need(same(table,expected), 'OWN_CONTROL_TABLE')
    reader.map(snapshot)
    return summary

def component_model(ordered, matrix, rhs, triples, forbidden, equal):
    """Expected public finite-fixture packet; never used to create a new science model."""
    n = len(ordered)
    upper = [1 if mask.bit_count() >= 3 or i in equal else 82 for i,mask in enumerate(ordered)]
    rows = [{'kind':'moment','origin':r,'lower':b,'upper':b,
             'terms':[[j,value] for j,value in enumerate(row) if value]} for r,(row,b) in enumerate(zip(matrix,rhs))]
    sets = [frozenset(i for i in range(max(1,max(ordered).bit_length())) if mask & (1 << i)) for mask in ordered]
    rows += [{'kind':'triple','origin':list(q),'lower':None,'upper':1,
              'terms':[[j,1] for j,s in enumerate(sets) if frozenset(q) <= s]} for q in triples]
    rows += [row for j,bound in enumerate(upper) for row in (
        {'kind':'presence_lower','origin':j,'lower':0,'upper':None,'terms':[[j,1],[n+j,-1]]},
        {'kind':'presence_upper','origin':j,'lower':None,'upper':0,'terms':[[j,1],[n+j,-bound]]})]
    rows += [{'kind':'forbidden_pair','origin':[i,j],'lower':None,'upper':1,
              'terms':[[n+i,1],[n+j,1]]} for i,j in forbidden]
    return {'schema':'FIXED17_INTEGER_TYPE_COUNT_MODEL_V1','ordered_masks':ordered,'count_variables':n,
        'presence_variables':n,'variables':2*n,'objective':[0]*(2*n),'lower':[0]*(2*n),'upper':upper+[1]*n,
        'all_columns_integer':True,'rows':rows,'moment_rhs':rhs,'moments':matrix,'triples':[list(q) for q in triples],
        'forbidden_distinct_pairs':[list(p) for p in forbidden],'equal_forbidden_indices':sorted(equal),'target_graph':False}

def declared_count_payload(payload, budget):
    model = payload['model']
    n = model['count_variables']
    counts = count_vector(payload['counts'],n,82)
    count_type_upper(counts,model['upper'][:n])
    presence = presence_vector(payload['presence'],counts)
    cols = [[row[j] for row in model['moments']] for j in range(n)]
    moments(counts,[{'synthetic_row':i} for i in range(len(model['moment_rhs']))],model['moment_rhs'],cols,budget)
    sets = [frozenset(i for i in range(max(1,max(model['ordered_masks']).bit_length())) if mask & (1 << i))
            for mask in model['ordered_masks']]
    for q in model['triples']:
        budget.tick()
        need(sum(counts[i] for i,s in enumerate(sets) if frozenset(q) <= s) <= 1, 'COMMON_Q_CAP')
    for i,j in model['forbidden_distinct_pairs']:
        no_good(counts,presence,i,j,[])
    exact_sparse_evaluation(counts,presence,model['rows'],budget)
    return counts,presence

def author_routes(budget):
    ordered = [0,1,2,3,7,15]
    matrix = [[1]*6]+[[int(i in {j for j in range(4) if mask & (1 << j)}) for mask in ordered] for i in range(4)]
    fixture = component_model(ordered,matrix,[3,1,1,1,0],list(itertools.combinations(range(4),3)),[[1,2]],[2])
    def payload(counts, rhs=None):
        model = copy.deepcopy(fixture)
        if rhs is not None:
            model['moment_rhs'] = rhs
            for i,b in enumerate(rhs):
                model['rows'][i]['lower'] = model['rows'][i]['upper'] = b
        return {'model':model,'counts':counts,'presence':[int(v > 0) for v in counts]}
    check = lambda p:declared_count_payload(p,budget)
    base = payload([2,0,0,0,1,0])
    routes = [
        ('low_type_multiplicity_two','PASS','PASS',base,check),
        ('allowed_low_type_pair_total_three','PASS','PASS',payload([0,2,0,1,0,0],[3,3,1,0,0]),check),
        ('high_type_one','PASS','PASS',payload([0,0,0,0,1,0],[1,1,1,1,0]),check),
        ('equal_forbidden_single_copy','PASS','PASS',payload([0,0,1,0,0,0],[1,0,1,0,0]),check),
        ('exact_presence_link','PASS','PASS',copy.deepcopy(base),check)]
    h = [[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]]
    rook_masks = [0,3,5,10,12]
    labels,rhs,cols,_ = moment_system(h,rook_masks,9,4)
    rook_matrix = [[column[r] for column in cols] for r in range(len(rhs))]
    raw_types = [{'mask':mask,'coefficient':column} for mask,column in zip(rook_masks,cols)]
    rook = {'matrix':rook_matrix,'rhs':rhs}
    def rook_check(p):
        need(type(p) is dict and set(p) == {'matrix','rhs'}, 'MODEL_FIELDS')
        need(type(p['matrix']) is list and all(type(row) is list and all(type(x) is int for x in row)
             for row in p['matrix']) and type(p['rhs']) is list and all(type(x) is int for x in p['rhs']),
             'MODEL_COLUMN_INTEGER')
        need(same(p['matrix'],rook_matrix), 'MODEL_COLUMN_IDENTITY')
        need(same(p['rhs'],rhs), 'MODEL_RHS_IDENTITY')
        moments([1]*5,labels,rhs,cols,budget)
    routes.append(('known_rook_exterior_five','PASS','PASS',rook,rook_check))
    gate = {'status':'INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS','mode':'full','implementation_version':2,
        'producer':'/root/structural','verifier':'/root/native_driver','method':'independent_artifact_check',
        'target_resolution':'NONE','inputs_sha256':{'synthetic':'pin'},'outcome':{
            'complete_pair_records':111628,'complete_record_fields':19,'complete_parts':23,'complete_checkpoints':23,
            'final_part_records':1628,'complete_scaled_type_vectors':472,'complete_induced_adjacency_entries':289,
            'complete_raw_physical_files':48,'equal_types_are_distinct_external_vertices':True,
            'same_adjacency_bit_required':True}}
    gate_check = lambda p:pair_gate_header(p,{'synthetic':'pin'},True)
    routes.append(('canonical_pair_gate','PASS','PASS',gate,gate_check))
    def solver_budget(p):
        need(p.get('stop_required') is False and type(p.get('remaining_seconds')) in (int,float)
             and math.isfinite(p['remaining_seconds']) and p['remaining_seconds'] > 20, 'SAVE_RESERVE')
        need(min(1500.0,p['remaining_seconds']-180) > 0, 'SOLVER_RESERVE')
    routes.append(('solver_budget_above_reserve','PASS','PASS',{'stop_required':False,'remaining_seconds':181},solver_budget))
    def mutation(name, producer_stage, native_stage, original, change, action):
        p = copy.deepcopy(original); change(p)
        routes.append((name,producer_stage,native_stage,p,action))
    for name,value,cp_stage,native_stage in [
        ('count_bool',[True,0,0,0,1,0],'COUNT_INTEGER','COUNT_INTEGER'),
        ('count_float',[2.0,0,0,0,1,0],'COUNT_INTEGER','COUNT_INTEGER'),
        ('count_missing',[2,0,0,0,1],'COUNT_POPULATION','COUNT_SHAPE'),
        ('count_negative',[-1,0,0,0,1,0],'COUNT_BOUND','COUNT_RANGE'),
        ('count_over82',[83,0,0,0,1,0],'COUNT_BOUND','COUNT_RANGE'),
        ('high_type_multiple',[2,0,0,0,2,0],'COUNT_BOUND','COUNT_TYPE_UPPER'),
        ('equal_forbidden_multiple',[2,0,2,0,1,0],'COUNT_BOUND','COUNT_TYPE_UPPER'),
        ('wrong_moment',[1,0,0,0,1,0],'MOMENT_EQUALITY','MOMENT_EQUATION')]:
        mutation(name,cp_stage,native_stage,base,lambda p,v=value:p.__setitem__('counts',v),check)
    for name,value,cp_stage,native_stage in [
        ('presence_bool',[True,0,0,0,1,0],'PRESENCE_INTEGER','PRESENCE_BINARY'),
        ('presence_missing',[1,0,0,0,1],'PRESENCE_POPULATION','PRESENCE_SHAPE'),
        ('wrong_presence_link',[0,0,0,0,1,0],'PRESENCE_EQUIVALENCE','PRESENCE_COUNT_EQUIVALENCE')]:
        mutation(name,cp_stage,native_stage,base,lambda p,v=value:p.__setitem__('presence',v),check)
    routes += [
        ('triple_violation','TRIPLE_CAP','COMMON_Q_CAP',payload([1,0,0,0,1,1],[3,2,2,2,1]),check),
        ('forbidden_low_type_pair','PAIR_PRESENCE_NOGOOD','PAIR_NO_GOOD',payload([1,1,1,0,0,0],[3,1,1,0,0]),check)]
    def type_check(p):
        need(type(p) is list and all(type(item) is dict and set(item) == {'mask','coefficient'} for item in p),
             'FIXED_TYPE_FIELDS')
        values = [item['mask'] for item in p]
        sets = supports(values,4)
        for item,s in zip(p,sets):
            expected = [1]+[int(i in s) for i in range(4)]+[int(i in s and j in s) for i,j in itertools.combinations(range(4),2)]
            need(same(item['coefficient'],expected), 'FIXED_TYPE_COEFFICIENT')
    for name,value,cp_stage,native_stage in [
        ('type_mask_bool',True,'TYPE_MASK_INTEGER','MASK_INTEGER'),
        ('type_mask_float',0.0,'TYPE_MASK_INTEGER','MASK_INTEGER')]:
        mutation(name,cp_stage,native_stage,raw_types,lambda p,v=value:p[0].__setitem__('mask',v),type_check)
    mutation('type_order','TYPE_MASK_ORDER','MASK_ORDER',raw_types,lambda p:p[2].__setitem__('mask',3),type_check)
    for name,value in [('coefficient_bool',True),('coefficient_float',1.0)]:
        mutation(name,'TYPE_COEFFICIENT','FIXED_TYPE_COEFFICIENT',raw_types,
                 lambda p,v=value:p[0]['coefficient'].__setitem__(0,v),type_check)
    for name,value in [('pair_gate_bool_version',True),('pair_gate_old_version',1)]:
        mutation(name,'PAIR_GATE_HEADER','PAIR_GATE_HEADER',gate,lambda p,v=value:p.__setitem__('implementation_version',v),gate_check)
    def method_alias(p):
        p['method'] = None; p['verification_method'] = 'independent_artifact_check'
    mutation('pair_gate_method_alias','PAIR_GATE_HEADER','PAIR_GATE_HEADER',gate,method_alias,gate_check)
    mutation('pair_gate_incomplete','PAIR_GATE_COUNTS','PAIR_GATE_COUNTS',gate,
             lambda p:p['outcome'].__setitem__('complete_pair_records',111627),gate_check)
    record = fixture_pairs([0])[0]
    for name,key,value,cp_stage,native_stage in [
        ('pair_record_bool','proposal_id',False,'PAIR_RECORD_INTEGER','PAIR_INTEGER'),
        ('pair_bits_bool','cn_bits',[False,1],'PAIR_BITS','PAIR_BITS'),
        ('pair_combined_mismatch','combined_bits',[],'PAIR_INTERSECTION','PAIR_CLASSIFICATION')]:
        mutation(name,cp_stage,native_stage,record,lambda p,k=key,v=value:p.__setitem__(k,v),
                 lambda p:pair_structure(p,0,0,0,[0]))
    for name,raw,stage in [('budget_at_reserve',{'stop_required':False,'remaining_seconds':180},'SOLVER_RESERVE'),
        ('budget_expired',{'stop_required':False,'remaining_seconds':0},'SAVE_RESERVE'),
        ('budget_review_due',{'stop_required':True,'remaining_seconds':500},'SAVE_RESERVE')]:
        routes.append((name,stage,stage,raw,solver_budget))
    mutation('wrong_rhs','MODEL_RHS_IDENTITY','MODEL_RHS_IDENTITY',rook,
             lambda p:p.__setitem__('rhs',[5,3,2,2,2,1,1,0,0,1,1]),rook_check)
    mutation('wrong_integer_coefficient','MODEL_COEFFICIENT_IDENTITY','MODEL_COLUMN_IDENTITY',rook,
             lambda p:p['matrix'][0].__setitem__(0,0),rook_check)
    need(len(routes) == 38 and sum(cp == 'PASS' for _,cp,_,_,_ in routes) == 8, 'AUTHOR_ROUTE_POPULATION')
    return routes

def producer_controls(reader, args, out):
    summary,base,_ = source_packet(reader,args,'calibrate')
    need(summary.get('status') == 'FIXED17_INTEGER_TYPE_COUNTS_V1_AUTHOR_CONTROLS_PASS' and
         same(summary.get('inputs_sha256'),{**AUTHOR_SOFTWARE,**PRODUCER_PINS}) and
         same(summary.get('outcome',{}).get('controls'),AUTHOR_COUNTS), 'AUTHOR_CALIBRATION_SCOPE')
    routes = author_routes(reader.budget)
    backend = ['native_low_multiplicity','native_rational_only','native_allowed_low_pair']
    names = ({name+'.json' for name,_,_,_,_ in routes}|{'controls.json'}|
        {name+suffix for name in backend for suffix in ('_model.json','_guidance.json','_extraction.json','_solver.log')})
    need(set(summary['outputs_sha256']) == names and len(names) == 51, 'AUTHOR_OUTPUT_POPULATION')
    outputs = summary['outputs_sha256']
    table = reader.read(base/'controls.json',outputs['controls.json'])
    expected = [{'name':name,'expected_stage':cp,'actual_stage':cp} for name,cp,_,_,_ in routes]+[
        {'name':name,'expected_stage':'PASS','actual_stage':'PASS'} for name in backend]
    need(same(table,expected), 'AUTHOR_CONTROL_TABLE')
    checked = []
    for name,cp,native,pristine,function in routes:
        payload = reader.read(base/(name+'.json'),outputs[name+'.json'])
        need(same(payload,pristine), 'AUTHOR_PAYLOAD:'+name)
        actual = 'PASS'
        try:
            function(copy.deepcopy(payload))
        except Veto as exc:
            actual = str(exc)
        need(actual == native, 'AUTHOR_NATIVE_STAGE:'+name+':'+actual)
        checked.append({'name':name,'producer_expected_stage':cp,'producer_actual_stage':cp,
                        'independent_expected_stage':native,'independent_actual_stage':actual})
    for name,ordered,a,rhs,witness in [
        ('native_low_multiplicity',[1],[[1]],[2],True),
        ('native_rational_only',[1],[[2]],[1],False),
        ('native_allowed_low_pair',[1,3],[[1,1]],[3],True)]:
        wanted = component_model(ordered,a,rhs,[],[],[])
        model = reader.read(base/(name+'_model.json'),outputs[name+'_model.json'])
        need(same(model,wanted), 'AUTHOR_BACKEND_MODEL')
        raw_guidance = reader.read(base/(name+'_guidance.json'),outputs[name+'_guidance.json'])
        guidance(raw_guidance,2*len(ordered))
        extraction = reader.read(base/(name+'_extraction.json'),outputs[name+'_extraction.json'])
        if witness:
            need(type(extraction.get('candidate')) is dict, 'AUTHOR_BACKEND_CANDIDATE')
            counts,presence = candidate_wire(extraction['candidate'],ordered,82)
            declared_count_payload({'model':model,'counts':counts,'presence':presence},reader.budget)
        else:
            need(extraction.get('candidate') is None and all(2*x != 1 for x in range(83)), 'AUTHOR_BACKEND_TINY_INTEGER_DOMAIN')
        checked.append({'name':name,'producer_expected_stage':'PASS','producer_actual_stage':'PASS',
                        'independent_expected_stage':'PASS','independent_actual_stage':'PASS'})
    write(out/'producer_control_stage_pairs.json',checked,reader.budget)
    return {'complete_author_controls':AUTHOR_COUNTS,'complete_stage_pairs':41,'complete_backend_fixtures':3,
            'tiny_exact_integer_domain_values':83,'complete_raw_physical_files':52,
            'actual_target_input_read':False,'solver_calls':0}

def full(reader, args, out, software):
    control,control_base = packet(reader,args.producer_controls,args.producer_controls_sha256)
    need(control.get('status') == CONTROLS_STATUS and control.get('mode') == 'controls' and
         type(control.get('implementation_version')) is int and control['implementation_version'] == 1 and
         control.get('producer') == '/root/checkpoint_audit' and control.get('verifier') == '/root/native_driver' and
         control.get('method') == 'independent_artifact_check' and control.get('target_resolution') == 'NONE' and
         same(control.get('source_software'),software) and control.get('actual_target_input_read') is False,
         'CONTROLS_GATE_HEADER')
    need(same(control.get('outcome'),{'complete_author_controls':AUTHOR_COUNTS,'complete_stage_pairs':41,
         'complete_backend_fixtures':3,'tiny_exact_integer_domain_values':83,'complete_raw_physical_files':52,
         'actual_target_input_read':False,'solver_calls':0}) and
         set(control['outputs_sha256']) == {'producer_control_stage_pairs.json'}, 'CONTROLS_GATE_SCOPE')
    reader.map(control['inputs_sha256'])
    summary,base,flags = source_packet(reader,args,'solve')
    config = reader.read(flags['--configuration'],flags['--configuration-sha256'])
    need(type(config) is dict and config.get('schema') == 'FIXED17_INTEGER_TYPE_COUNTS_CONFIGURATION_V1'
         and config.get('source_sha256') == PRODUCER_PINS[PRODUCER] and
         config.get('spec_sha256') == PRODUCER_PINS[PRODUCER_SPEC], 'CONFIGURATION_HEADER')
    reader.map(config.get('inputs_sha256'))
    cal_key = safe(config['author_calibration_path']).relative_to(ROOT).as_posix()
    need(control['inputs_sha256'].get(cal_key) == config['author_calibration_sha256'], 'AUTHOR_CALIBRATION_BINDING')
    gate,pair_summary,pair_base = pair_evidence(reader,config['pair_gate_path'],config['pair_gate_sha256'],
                                              config['pair_producer_summary_path'])
    h,ordered,labels,rhs,columns,sets = fixed_input(reader.read(MODEL,FIXED[MODEL]),reader.read(TYPES,FIXED[TYPES]))
    records,forbidden,equal,rules,prefixes = pair_rules(reader,pair_summary,pair_base,ordered)
    wanted = expected_model(h,ordered,99,14,forbidden,equal,reader.budget)
    outputs = summary['outputs_sha256']
    required = ({'parsed_fixed_input.json','pair_rules.json','integer_model.json','before_solver_checkpoint.json',
        'scientific_solver.log','scientific_guidance.json','after_solver_checkpoint.json','extraction.json'}|
        {'pair_read_checkpoint_%03d.json'%i for i in range(23)})
    extraction = reader.read(base/'extraction.json',outputs['extraction.json'])
    present = candidate_state(summary,extraction,outputs)
    need(set(outputs) == required|({'exact_integer_candidate.json','exact_constraint_rows.json'} if present else set()),
         'SCIENTIFIC_OUTPUT_POPULATION')
    parsed = {'ordered_masks':ordered,'induced_adjacency':h,'moment_labels':labels,
              'moments':wanted['moments'],'rhs':rhs,'triples':wanted['triples']}
    need(same(reader.read(base/'parsed_fixed_input.json',outputs['parsed_fixed_input.json']),parsed), 'PARSED_FIXED_INPUT')
    projected = {'complete_pair_records':111628,'rules':rules,'all_record_labels_scanned':True,
                 'equal_types_mean_distinct_vertices':True,'retained_count_types':472}
    need(same(reader.read(base/'pair_rules.json',outputs['pair_rules.json']),projected), 'PROJECTED_PAIR_RULES')
    model_identity(reader.read(base/'integer_model.json',outputs['integer_model.json']),wanted)
    for i,prefix in enumerate(prefixes):
        name = 'pair_read_checkpoint_%03d.json'%i
        need(same(reader.read(base/name,outputs[name]),prefix), 'PAIR_READ_CHECKPOINT')
    raw_guidance = reader.read(base/'scientific_guidance.json',outputs['scientific_guidance.json'])
    guidance(raw_guidance,944)
    before = reader.read(base/'before_solver_checkpoint.json',outputs['before_solver_checkpoint.json'])
    after = reader.read(base/'after_solver_checkpoint.json',outputs['after_solver_checkpoint.json'])
    need(before.get('stage') == 'full_model_saved' and type(before.get('rows')) is int and
         before['rows'] == len(wanted['rows']) and type(before.get('variables')) is int and before['variables'] == 944,
         'BEFORE_SOLVER_CHECKPOINT')
    need(after.get('stage') == 'native_returned' and after.get('model_status') == raw_guidance['model_status'] and
         type(after.get('value_valid')) is bool and after['value_valid'] == raw_guidance['solution_value_valid'],
         'AFTER_SOLVER_CHECKPOINT')
    checked = None
    if present:
        candidate = reader.read(base/'exact_integer_candidate.json',outputs['exact_integer_candidate.json'])
        need(same(candidate,extraction['candidate']), 'CANDIDATE_EXTRACTION_IDENTITY')
        counts,presence = candidate_wire(candidate,ordered,82)
        count_type_upper(counts,wanted['upper'][:472])
        checked = integer_candidate(counts,presence,h,ordered,99,14,records,reader.budget)
        sparse = exact_sparse_evaluation(counts,presence,wanted['rows'],reader.budget)
        expected_rows = ([{'kind':'moment','index':i,'lhs':row['lhs'],'rhs':row['rhs']}
                          for i,row in enumerate(checked['moment_rows'])] +
            [{'kind':'triple','vertices':row['Q'],'lhs':row['sum'],'upper':1} for row in checked['common_Q_caps']] +
            [{'kind':'forbidden_pair','i':i,'j':j,'lhs':presence[i]+presence[j],'upper':1} for i,j in forbidden])
        raw_rows = reader.read(base/'exact_constraint_rows.json',outputs['exact_constraint_rows.json'])
        need(same(raw_rows,expected_rows) and same(extraction.get('exact_rows'),expected_rows), 'EXACT_CONSTRAINT_ROWS')
        checked['all_sparse_rows'] = sparse
        checked['candidate_exact_checked'] = True
    else:
        checked = {'candidate_exact_checked':False,'reason':extraction['reason'],
                   'integer_feasibility_conclusion':None,'integer_infeasibility_conclusion':None}
    outcome = summary['outcome']
    expected_counts = {'count_types':472,'presence_variables':472,'original_moment_equalities':154,'triple_caps':680,
        'complete_pair_records':111628,'forbidden_distinct_pair_rules':len(forbidden),
        'equal_forbidden_multiplicity_bounds':len(equal),'scientific_solver_calls':1}
    need(all(type(outcome.get(k)) is int and outcome[k] == v for k,v in expected_counts.items()) and
         all(outcome.get(k) is True for k in ('all_type_variables_retained','high_cardinality_types_binary')) and
         all(outcome.get(k) is False for k in ('floating_status_is_proof','numeric_infeasibility_is_proof','graph_completion')),
         'SCIENTIFIC_OUTCOME')
    write(out/'independent_count_review.json',checked,reader.budget)
    return {'complete_count_variables':472,'complete_presence_variables':472,'complete_moment_rows':154,
        'complete_common_Q_caps':680,'complete_pair_records':111628,'complete_pair_record_fields':19,
        'complete_pair_read_checkpoints':23,'complete_sparse_model_rows':len(wanted['rows']),
        'forbidden_distinct_pairs':len(forbidden),'equal_multiplicity_bounds':len(equal),
        'complete_raw_physical_files':len(outputs)+1,'candidate_exact_checked':present,
        'candidate_absent_reason':None if present else extraction['reason'],
        'graph_completion':False,'solver_calls':0,'actual_target_input_read':True}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',choices=('calibrate','controls','full'))
    for name in ('seconds','out','self-sha256','spec-sha256'):
        parser.add_argument('--'+name,required=True,type=float if name == 'seconds' else str)
    for name in ('calibration','producer-plan','producer-summary','producer-manifest','producer-terminal','producer-controls'):
        parser.add_argument('--'+name)
        parser.add_argument('--'+name+'-sha256')
    args = parser.parse_args()
    budget = Budget(args.seconds)
    out = safe(args.out,False)
    need(out.is_relative_to(ROOT/'acceleration/results') and not out.exists(), 'OUTPUT_FRESH_SCOPE')
    out.mkdir(parents=True)
    reader = Reader(budget)
    software = {**SOFTWARE,**PRODUCER_PINS,SELF:args.self_sha256,SPEC:args.spec_sha256}
    try:
        reader.map(software)
        if args.mode == 'calibrate':
            outcome = own_controls(out,budget)
            status = CAL_STATUS
        else:
            need(all(getattr(args,name) is not None and getattr(args,name+'_sha256') is not None for name in
                 ('calibration','producer_plan','producer_summary','producer_manifest','producer_terminal')), 'REPLAY_ARGUMENTS')
            qualify_own(reader,args.calibration,args.calibration_sha256,software)
            if args.mode == 'controls':
                outcome = producer_controls(reader,args,out)
                status = CONTROLS_STATUS
            else:
                need(args.producer_controls is not None and args.producer_controls_sha256 is not None, 'CONTROLS_ARGUMENTS')
                outcome = full(reader,args,out,software)
                status = FULL_STATUS
        reader.closing()
        outputs = {}
        for path in sorted(out.iterdir()):
            budget.tick()
            need(path.is_file() and path.name != 'summary.json', 'CHECKER_OUTPUT_POPULATION')
            outputs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        report = {'status':status,'implementation_version':1,'mode':args.mode,
            'timestamp':datetime.now(timezone.utc).isoformat(),'producer':'/root/checkpoint_audit',
            'verifier':'/root/native_driver','checking_source_author':'/root/native_driver',
            'method':'independent_artifact_check','target_resolution':'NONE','source_software':software,
            'inputs_sha256':dict(reader.pins),'outputs_sha256':outputs,'outcome':outcome,
            'command':[sys.executable]+sys.argv,'cwd':str(ROOT),'actual_target_input_read':args.mode == 'full',
            'solver_calls':0,'producer_imports':0,'new_scientific_model_generation':False,
            'graph_completion':False,'integer_infeasibility_inferred':False,'automatic_retry':False,
            'deadline':budget.tick(),'shared_components':[
                'Frozen type universe and genuine Native implementation2 pair mathematics are explicitly trusted inputs',
                'Native independently reconstructs H degrees/CN, support-set coefficient/Q rows and integer/no-good arithmetic',
                'Public finite producer fixture data/wire taxonomy shared; no Checkpoint producer code is imported',
                'Native JSON/SHA/path/deadline/runtime reader ancestry disclosed; pinned command_deadline is the only local import'],
            'limitations':['One fixed induced H17 necessary exterior count system, not a graph completion or target certificate',
                'A candidate absent packet gives no integer feasibility or infeasibility conclusion',
                'All floating statuses/values/logs/bounds remain guidance; the verifier never rounds a float into a count',
                'Complete saved integer rows are checked; no native internal trajectory, branching proof or optimality is reconstructed',
                'Guarded twenty-second save reserve is intent, not an OS/filesystem hard real-time guarantee',
                'A clean actual contained terminal and absence of failure are required even after prospective summary emission']}
        write(out/'summary.json',report,budget)
        reader.closing()
        budget.tick()
    except Exception as exc:
        try:
            (out/'failure.json').write_text(json.dumps({'status':'FAILED_PRESERVED','stage':str(exc),
                'exception':type(exc).__name__,'timestamp':datetime.now(timezone.utc).isoformat(),
                'inputs_sha256':reader.pins,'target_resolution':'NONE','automatic_retry':False,
                'integer_infeasibility_inferred':False,'deadline':budget.deadline.status()},indent=2,allow_nan=False)+'\n',encoding='utf8')
        except Exception:
            pass
        raise

if __name__ == '__main__':
    main()

