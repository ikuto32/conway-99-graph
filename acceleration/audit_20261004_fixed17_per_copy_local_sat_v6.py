"""SOURCE ONLY: independent complete local per-copy SAT clause/model checker.
No discovery producer import, AST helper execution, solver or graph search.
Explicit unchanged Native set/rank and prefix-array components are copied below.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import io
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261004_fixed17_per_copy_local_sat_v6.py'
SPEC = 'acceleration/audit_20261004_fixed17_per_copy_local_sat_v6_spec.md'
PRODUCER = 'acceleration/build_20261004_fixed17_per_copy_local_sat_v1.py'
PRODUCER_SPEC = 'acceleration/build_20261004_fixed17_per_copy_local_sat_v1_spec.md'
MODEL_SCHEMA = 'FIXED17_COPY_ADJACENCY_MODEL_V1'
CAL_STATUS = 'INDEPENDENT_FIXED17_PER_COPY_LOCAL_SAT_V1_CALIBRATION_PASS'
CONTROLS_STATUS = 'INDEPENDENT_FIXED17_PER_COPY_LOCAL_SAT_V1_AUTHOR_CONTROLS_PASS'
FULL_STATUS = 'INDEPENDENT_FIXED17_PER_COPY_LOCAL_SAT_V1_COMPLETE_PASS'
AUTHOR_STATUS = 'FIXED17_PER_COPY_LOCAL_SAT_V1_AUTHOR_CONTROLS_PASS'
BUILD_STATUS = 'CANDIDATE_FIXED17_PER_COPY_LOCAL_SAT_V1_COMPLETE_ENCODING'
COPY_STATUS = 'INDEPENDENT_FIXED17_PER_COPY_ADJACENCY_V1_COMPLETE_PASS'
SUP = 'acceleration/run_compute_command_v2.py'
SUP_SHA = '46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17'
BODY_LIMIT = 256*1024*1024
JSON_LIMIT = 64*1024*1024
PINS = {
 PRODUCER:'04fa6cf7889d786719fcd1c71ced52af83ec98d9459820fd5bd9422bcde72af3',
 PRODUCER_SPEC:'2d1774a019254ffd96c06a975ae4d8a34b14817f668830150c2c9173f8cea610',
 'acceleration/theory_20260930_eight_full99_cnf.py':'21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c',
 'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 SUP:SUP_SHA,
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'acceleration/audit_20261004_fixed17_per_copy_adjacency_v1.py':'777838556a4b74e86e329220440fe146c167d097b3228b49277fb39faeaa43f8',
 'acceleration/audit_20261004_fixed17_per_copy_adjacency_v1_spec.md':'5cffa344f73694333d66202f0362cb352576d1821eae5d484c04cc22791b852f',
 'acceleration/audit_20261004_fixed17_count_full99_cnf_v3.py':'dfb9cd49f44c39c93bfd73e4c73fe3b1d36709e2e10fe5fabaa49b9bab8bef0e',
 'acceleration/audit_20261004_fixed17_count_full99_cnf_v3_spec.md':'c9359a16990ce8f81fbc7d36a5861263fc6954499b01672c48f5cdba9c55b8b8',
}
AUTHOR_SOFTWARE_KEYS = {PRODUCER,PRODUCER_SPEC,'acceleration/theory_20260930_eight_full99_cnf.py',
 'acceleration/command_deadline.py',SUP,'pyproject.toml','uv.lock'}
AUTHOR_COUNTS = {'positive':7,'negative':22,'total':29}
OWN_COUNTS = {'positive':19,'negative':76,'total':95}
CODE_VERSION = 6  # Wire implementation_version remains 1; fresh source pins govern applicability.

class Veto(ValueError):
    pass

def need(ok,stage):
    if not ok: raise Veto(stage)

def tick(budget):
    if budget is not None:
        budget.tick()



def typed_equal(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(typed_equal(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(typed_equal(a, b) for a, b in zip(left, right))
    return left == right



def profile_geometry(raw, budget=None):
    required = {'target_order', 'target_degree', 'support_adjacency', 'ordered_masks', 'counts', 'pair_bits'}
    need(type(raw) is dict and raw.keys() == required, 'PROFILE_FIELDS')
    n, k, h, masks, counts, table = (raw[name] for name in (
        'target_order', 'target_degree', 'support_adjacency', 'ordered_masks', 'counts', 'pair_bits'))
    need(type(n) is int and type(k) is int and 0 < k < n - 1, 'PROFILE_TARGET')
    need(type(h) is list and 0 < len(h) < n, 'PROFILE_GRAPH')
    support = len(h)
    need(all(type(row) is list and len(row) == support for row in h), 'PROFILE_GRAPH')
    need(all(type(value) is int and value in (0, 1) for row in h for value in row), 'PROFILE_GRAPH')
    for u in range(support):
        tick(budget)
        need(h[u][u] == 0 and all(h[u][v] == h[v][u] for v in range(support)), 'PROFILE_GRAPH')
    need(type(masks) is list and masks and all(type(mask) is int and 0 <= mask < 2**support for mask in masks)
         and all(a < b for a, b in zip(masks, masks[1:])), 'PROFILE_MASKS')
    need(type(counts) is list and len(counts) == len(masks)
         and all(type(value) is int and value >= 0 for value in counts), 'PROFILE_COUNTS')
    need(sum(counts) == n - support, 'PROFILE_COUNTS')
    q = len(masks)
    need(type(table) is list and len(table) == q*(q+1)//2, 'PROFILE_PAIR_POPULATION')
    pair_bits = {}
    ordinal = 0
    for i in range(q):
        tick(budget)
        for j in range(i, q):
            row = table[ordinal]
            need(type(row) is dict and row.keys() == {'i', 'j', 'bits'}
                 and type(row['i']) is int and type(row['j']) is int
                 and row['i'] == i and row['j'] == j, 'PROFILE_PAIR_ORDER')
            bits = row['bits']
            need(type(bits) is list and all(type(bit) is int and bit in (0, 1) for bit in bits)
                 and bits in ([], [0], [1], [0, 1]), 'PROFILE_PAIR_BITS')
            pair_bits[i, j] = set(bits)
            ordinal += 1
    labels, types = [], []
    for i, multiplicity in enumerate(counts):
        members = {u for u in range(support) if (masks[i] >> u) & 1}
        for copy_number in range(multiplicity):
            labels.append([i, copy_number])
            types.append(set(members))
    return {'n': n, 'k': k, 'h': h, 'support': support, 'labels': labels,
            'types': types, 'pair_bits': pair_bits}



def unordered_rank(x, y, size):
    need(type(x) is int and type(y) is int and 0 <= x < y < size, 'VARIABLE_PAIR_DOMAIN')
    return x*(2*size-x-1)//2 + y-x-1



def abstract_model(raw, budget=None):
    geometry = profile_geometry(raw, budget)
    labels, types = geometry['labels'], geometry['types']
    size, support, k = len(labels), geometry['support'], geometry['k']
    pairs = [None]*(size*(size-1)//2)
    lower, upper = [None]*len(pairs), [None]*len(pairs)
    incident = [set() for _ in labels]
    for x in range(size):
        tick(budget)
        for y in range(x+1, size):
            ordinal = unordered_rank(x, y, size)
            pairs[ordinal] = [x, y]
            i, j = sorted((labels[x][0], labels[y][0]))
            allowed = geometry['pair_bits'][i, j]
            need(allowed, 'PROFILE_INCOMPATIBLE_PAIR')
            lower[ordinal] = 1 if allowed == {1} else 0
            upper[ordinal] = 1 if 1 in allowed else 0
            incident[x].add(ordinal)
            incident[y].add(ordinal)
    rows = []
    for x in range(size):
        tick(budget)
        degree_rhs = k - len(types[x])
        rows.append({'copy': x, 'coordinate': None, 'rhs': degree_rhs,
                     'terms': [[ordinal, 1] for ordinal in sorted(incident[x])]})
        for u in range(support):
            required = 2 - int(u in types[x]) - sum(geometry['h'][u][v] for v in types[x])
            coordinates = []
            for y in range(size):
                if y != x and u in types[y]:
                    a, b = sorted((x, y))
                    coordinates.append(unordered_rank(a, b, size))
            rows.append({'copy': x, 'coordinate': u, 'rhs': required,
                         'terms': [[ordinal, 1] for ordinal in sorted(coordinates)]})
    return geometry, {'labels': labels, 'variable_pairs': pairs, 'lower': lower, 'upper': upper, 'rows': rows}



def wire_model(raw, budget=None):
    geometry, abstract = abstract_model(raw, budget)
    rows = []
    for row in abstract['rows']:
        tick(budget)
        x, u, rhs = row['copy'], row['coordinate'], row['rhs']
        rows.append({'kind':'degree' if u is None else 'support_incidence', 'copy_x':x,
            'type_i':geometry['labels'][x][0], 'support_u':u, 'lower':rhs, 'upper':rhs,
            'terms':row['terms']})
    return {'schema':MODEL_SCHEMA, 'target_order':raw['target_order'], 'target_degree':raw['target_degree'],
        'support_order':geometry['support'], 'ordered_masks':copy.deepcopy(raw['ordered_masks']),
        'counts':list(raw['counts']), 'copy_labels':copy.deepcopy(geometry['labels']),
        'variable_pairs':abstract['variable_pairs'], 'variables':len(abstract['variable_pairs']),
        'outside_copies':len(geometry['labels']), 'lower':abstract['lower'], 'upper':abstract['upper'],
        'rows':rows, 'no_equitable_profile_assumed':True, 'outside_pair_CN_equations_included':False}



def whole_srg_diagnostic(matrix, degree, budget=None):
    need(type(matrix) is list and matrix and type(degree) is int, 'SRG_MATRIX_SHAPE')
    n = len(matrix)
    need(0 < degree < n-1 and all(type(row) is list and len(row) == n for row in matrix), 'SRG_PARAMETERS')
    need(all(type(value) is int and value in (0, 1) for row in matrix for value in row), 'SRG_BINARY')
    neighbors = []
    for u in range(n):
        tick(budget)
        need(matrix[u][u] == 0 and all(matrix[u][v] == matrix[v][u] for v in range(n)), 'SRG_SYMMETRY')
        neighbors.append({v for v, value in enumerate(matrix[u]) if value})
    degrees = [len(row) for row in neighbors]
    common, first_failure = [], None
    for u, actual in enumerate(degrees):
        if actual != degree and first_failure is None:
            first_failure = {'u': u, 'actual': actual, 'expected': degree, 'stage': 'SRG_DEGREE'}
    for u in range(n):
        tick(budget)
        row = []
        for v in range(n):
            actual = len(neighbors[u] & neighbors[v])
            expected = degree if u == v else 1 if v in neighbors[u] else 2
            row.append(actual)
            if actual != expected and first_failure is None:
                first_failure = {'u': u, 'v': v, 'actual': actual, 'expected': expected,
                                 'stage': 'SRG_DIAGONAL_CN' if u == v else 'SRG_EDGE_CN' if v in neighbors[u] else 'SRG_NONEDGE_CN'}
        common.append(row)
    return {'srg_valid': first_failure is None, 'complete_ordered_cn_entries': n*n,
            'degrees': degrees, 'common_neighbor_matrix': common, 'first_failure': first_failure}



def rook_fixture():
    # The support is (0,0),(0,1); exterior order is canonical type/copy order.
    raw = {'target_order': 9, 'target_degree': 4,
           'support_adjacency': [[0, 1], [1, 0]],
           'ordered_masks': [0, 1, 2, 3], 'counts': [2, 2, 2, 1],
           'pair_bits': [{'i': i, 'j': j, 'bits': [0, 1]}
                         for i in range(4) for j in range(i, 4)]}
    labels = [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1], [3, 0]]
    edges = {(0, 1), (0, 2), (0, 4), (0, 6), (1, 3), (1, 5),
             (1, 6), (2, 3), (2, 4), (3, 5), (4, 5)}
    pairs = [[x, y] for x in range(7) for y in range(x+1, 7)]
    matrix = [[int((min(x, y), max(x, y)) in edges) for y in range(7)] for x in range(7)]
    candidate = {'schema': 'FIXED17_COPY_ADJACENCY_INTEGER_CANDIDATE_V1',
                 'copy_labels': [list(label) for label in labels], 'variable_pairs': pairs,
                 'edge_values': [matrix[x][y] for x, y in pairs], 'exterior_adjacency': matrix,
                 'graph_object_validated': False}
    return {'profile': raw, 'candidate': candidate}



def switched_rook_fixture():
    fixture = rook_fixture()
    matrix = fixture['candidate']['exterior_adjacency']
    for x, y, value in ((2, 4, 0), (3, 5, 0), (2, 5, 1), (3, 4, 1)):
        matrix[x][y] = matrix[y][x] = value
    fixture['candidate']['edge_values'] = [matrix[x][y] for x, y in fixture['candidate']['variable_pairs']]
    return fixture



def neg(a):
    return not a if type(a) is bool else -a



class Logic:
    """Fresh independently written logic; no AST, encoder import or decoder reuse."""
    def __init__(self, base, budget, receiver=None, memory=True):
        self.top,self.base,self.count = base,base,0
        self.budget,self.receiver = budget,receiver
        self.rows,self.trace = ([] if memory else None),([] if memory else None)
    def emit(self, *refs):
        row = []
        for a in refs:
            if type(a) is bool:
                if a:return
                continue
            need(type(a) is int and a != 0 and abs(a) <= self.top, 'CLAUSE_REFERENCE')
            if -a in row:return
            if a not in row:row.append(a)
        self.count += 1
        if self.rows is not None:self.rows.append(row)
        if self.receiver is not None:self.receiver(row)
        if self.count % 1000 == 0:self.budget.tick()
    def gate(self, op, args, clauses):
        self.top += 1; z = self.top
        if self.trace is not None:self.trace.append([z,op,list(args)])
        for row in clauses(z):self.emit(*row)
        return z
    def and_ref(self,a,b):
        if type(a) is bool:return b if a else False
        if type(b) is bool:return a if b else False
        return self.gate('and',(a,b),lambda z:((a,-z),(b,-z),(-a,-b,z)))
    def or_ref(self,a,b):
        if type(a) is bool:return True if a else b
        if type(b) is bool:return True if b else a
        return self.gate('or',(a,b),lambda z:((-a,z),(-b,z),(a,b,-z)))
    def threshold_ref(self,a,b,c):
        if type(a) is bool:return True if a else self.and_ref(b,c)
        if type(b) is bool:return self.or_ref(a,c) if b else a
        if type(c) is bool:return self.or_ref(a,b) if c else a
        return self.gate('threshold',(a,b,c),lambda z:((-a,z),(-b,-c,z),(a,b,-z),(a,c,-z)))
    def counter(self,inputs,bound,equality,annotation):
        need(type(bound) is int and type(equality) is bool and 0 <= bound <= len(inputs) and
             all(type(a) is int and a > 0 for a in inputs) and len(set(inputs)) == len(inputs), 'COUNTER_DOMAIN')
        first,oldtop = self.count+1,self.top
        # Fixed-size prefix arrays independently express S(i,j)=[first i inputs have at least j ones].
        previous = [True]+[False]*(bound+1); states = []
        for i,x in enumerate(inputs,1):
            self.budget.tick()
            current = [True]+[False]*(bound+1)
            for j in range(1,min(i,bound+1)+1):
                current[j] = self.threshold_ref(previous[j],x,previous[j-1])
                states.append([i,j,current[j]])
            previous = current
        if equality:self.emit(previous[bound])
        self.emit(neg(previous[bound+1]))
        return {**annotation,'inputs':inputs,'bound':bound,'equality':equality,'states':states,
                'first_auxiliary_variable':oldtop+1 if self.top>oldtop else None,
                'last_auxiliary_variable':self.top if self.top>oldtop else None,
                'auxiliary_null_reason':'All states folded to constants or inputs.' if self.top==oldtop else None,
                'first_clause':first,'clause_count':self.count-first+1}


class Budget:
    def __init__(self,seconds):
        self.deadline=CommandDeadline(seconds,allocation_reason='Distinct complete local SAT clause/model checking; all hashes, arithmetic and closing share this invocation.')
    def tick(self):
        reserve(self.deadline.status())
    def emergency(self):
        need(self.deadline.status()['remaining_seconds']>0,'SAVE_RESERVE')


def reserve(status):
    need(type(status) is dict and status.get('stop_required') is False and
         type(status.get('remaining_seconds')) in (int,float) and
         math.isfinite(status['remaining_seconds']) and status['remaining_seconds']>20,'SAVE_RESERVE')


def safe(name,exists=True):
    need(type(name) is str and name,'INPUT_PATH')
    path=Path(name)
    if not path.is_absolute():path=ROOT/path
    path=path.absolute()
    need(path.is_relative_to(ROOT) and '..' not in path.parts,'INPUT_PATH')
    cursor=ROOT
    for part in path.relative_to(ROOT).parts:
        cursor=cursor/part
        need(not cursor.is_symlink() and not (hasattr(cursor,'is_junction') and cursor.is_junction()),'INPUT_PATH')
        if cursor.exists():need(not (cursor.stat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT) if hasattr(cursor.stat(),'st_file_attributes') else True,'INPUT_PATH')
    if exists:need(path.is_file(),'INPUT_FILE')
    return path


def output_directory(name,base):
    need(type(name) is str,'OUTPUT_DIRECTORY')
    path=safe(name,False)
    need(path.is_dir() and path==base,'OUTPUT_DIRECTORY')
    return path


def key(path):return path.relative_to(ROOT).as_posix()


def decode(data):
    def pairs(items):
        answer={}
        for name,value in items:
            need(name not in answer,'JSON_DUPLICATE');answer[name]=value
        return answer
    def constant(value):raise Veto('JSON_NONFINITE')
    try:return json.loads(data.decode('utf-8'),object_pairs_hook=pairs,parse_constant=constant)
    except (UnicodeDecodeError,json.JSONDecodeError):raise Veto('JSON_SYNTAX')


def json_bytes(value,compact=False):
    return (json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':') if compact else None,
                       indent=None if compact else 2,ensure_ascii=False)+'\n').encode('utf-8')


class Reader:
    def __init__(self,budget):self.budget,self.inputs=budget,{}
    def digest(self,path,limit=JSON_LIMIT):
        path=safe(str(path));self.budget.tick()
        need(path.stat().st_size<=limit,'INPUT_SIZE');hashed=hashlib.sha256();total=0
        with path.open('rb') as stream:
            while chunk:=stream.read(1024*1024):
                self.budget.tick();total+=len(chunk);need(total<=limit,'INPUT_SIZE');hashed.update(chunk)
        self.budget.tick();return hashed.hexdigest()
    def pin(self,path,expected,limit=JSON_LIMIT):
        need(type(expected) is str and re.fullmatch('[0-9a-f]{64}',expected) is not None,'INPUT_HASH_DOMAIN')
        path=safe(str(path));actual=self.digest(path,limit);need(actual==expected,'INPUT_HASH')
        name=key(path);need(name not in self.inputs or self.inputs[name]==expected,'INPUT_ALIAS');self.inputs[name]=expected
        return path
    def read(self,path,expected):
        path=self.pin(path,expected);self.budget.tick();data=path.read_bytes();need(len(data)<=JSON_LIMIT,'INPUT_SIZE')
        need(hashlib.sha256(data).hexdigest()==expected,'INPUT_HASH');self.budget.tick();return decode(data)
    def ref(self,ref):
        need(type(ref) is dict and ref.keys()=={'path','sha256'},'REFERENCE')
        return self.read(ref['path'],ref['sha256'])
    def map(self,pins):
        need(type(pins) is dict,'INPUT_MAP')
        for name,digest in pins.items():self.pin(name,digest,BODY_LIMIT+1024 if name.endswith(('.cnf','.body','.jsonl')) else JSON_LIMIT)
    def close(self):
        for name,digest in self.inputs.items():
            need(self.digest(safe(name),BODY_LIMIT+1024 if name.endswith(('.cnf','.body','.jsonl')) else JSON_LIMIT)==digest,'CLOSING_HASH')


def write(path,value,budget,emergency=False):
    guard=budget.emergency if emergency else budget.tick;guard()
    need(not path.exists(),'OUTPUT_EXISTS');data=json_bytes(value);need(len(data)<=JSON_LIMIT,'OUTPUT_SIZE')
    temporary=path.with_name(path.name+'.writing')
    with temporary.open('xb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
    guard();os.replace(temporary,path);guard()


def inventory(base,budget,excluding=()):
    result=[]
    for path in sorted(base.rglob('*')):
        budget.tick();safe(str(path),False)
        if path.is_file() and path.relative_to(base).as_posix() not in excluding:result.append(key(path))
    return result


def packet(reader,path,digest):
    summary=reader.read(path,digest);base=safe(str(path)).parent
    need(type(summary) is dict and type(summary.get('inputs_sha256')) is dict and
         type(summary.get('outputs_sha256')) is dict,'PACKET_MAPS')
    reader.map(summary['inputs_sha256']);reader.map(summary['outputs_sha256'])
    names=inventory(base,reader.budget,('summary.json',))
    need(names==sorted(summary['outputs_sha256']),'PACKET_POPULATION')
    return summary,base


def bounded_profile(raw,budget=None):
    geometry=profile_geometry(raw,budget)
    need(geometry['n']<=99 and geometry['support']<=17 and len(raw['ordered_masks'])<=472,'PROFILE_TARGET')
    for (i,j),bits in geometry['pair_bits'].items():
        tick(budget)
        if raw['counts'][i]*raw['counts'][j]>0 and (i!=j or raw['counts'][i]>=2):
            need(bool(bits),'PROFILE_INCOMPATIBLE_PAIR')
    return geometry


def validate_model(raw,submitted,budget=None):
    bounded_profile(raw,budget);expected=wire_model(raw,budget)
    need(type(submitted) is dict and submitted.keys()==expected.keys(),'MODEL_FIELDS')
    need(type(submitted['schema']) is str and submitted['schema']==MODEL_SCHEMA,'MODEL_HEADER')
    need(all(type(submitted[name]) is int and submitted[name]==expected[name]
             for name in ('target_order','target_degree','support_order','variables','outside_copies')),'MODEL_DIMENSIONS')
    need(submitted['no_equitable_profile_assumed'] is True and submitted['outside_pair_CN_equations_included'] is False,'MODEL_FLAGS')
    need(typed_equal(submitted['variable_pairs'],expected['variable_pairs']),'MODEL_VARIABLE_PAIRS')
    lo,hi=submitted['lower'],submitted['upper'];need(type(lo) is list and type(hi) is list and len(lo)==len(hi)==expected['variables'] and
        all(type(a) is int and type(b) is int and 0<=a<=b<=1 for a,b in zip(lo,hi)),'MODEL_BOUNDS')
    need(type(submitted['rows']) is list and len(submitted['rows'])==len(expected['rows']),'MODEL_ROWS')
    for row in submitted['rows']:
        tick(budget);need(type(row) is dict and row.keys()=={'kind','copy_x','type_i','support_u','lower','upper','terms'},'MODEL_ROW_DOMAIN')
        need(type(row['kind']) is str and row['kind'] in ('degree','support_incidence') and
             type(row['copy_x']) is int and type(row['type_i']) is int and
             (row['support_u'] is None or type(row['support_u']) is int) and
             type(row['lower']) is int and type(row['upper']) is int and row['lower']==row['upper'],'MODEL_ROW_DOMAIN')
        terms=row['terms'];need(type(terms) is list and all(type(t) is list and len(t)==2 and type(t[0]) is int and
             0<=t[0]<expected['variables'] and type(t[1]) is int and t[1]==1 for t in terms) and
             all(a[0]<b[0] for a,b in zip(terms,terms[1:])),'MODEL_ROW_DOMAIN')
    need(typed_equal(submitted,expected),'MODEL_RECONSTRUCTION');return expected


def scientific_scope(raw,model,budget=None):
    g=bounded_profile(raw,budget)
    need((g['n'],g['k'],g['support'],len(raw['ordered_masks']),sum(c>0 for c in raw['counts']),
          model['outside_copies'],model['variables'],len(model['rows']))==(99,14,17,472,68,82,3321,1476) and
          sum(c*t.bit_count() for c,t in zip(raw['counts'],raw['ordered_masks']))==166,'SCIENTIFIC_SCOPE')


def copy_gate(raw,model,refs):
    need(type(raw) is dict and raw.get('status')==COPY_STATUS and type(raw.get('implementation_version')) is int and
         raw['implementation_version']==1 and raw.get('producer')=='/root/checkpoint_audit' and
         raw.get('verifier')=='/root/native_driver' and raw.get('method')=='independent_artifact_check' and
         raw.get('target_resolution')=='NONE','GATE_HEADER')
    pins=raw.get('inputs_sha256');need(type(pins) is dict and all(type(p) is str and type(s) is str and
         re.fullmatch('[0-9a-f]{64}',s) for p,s in pins.items()) and
         all(pins.get(ref['path'])==ref['sha256'] for ref in refs),'GATE_PINS')
    expected={'complete_input_type_count':len(model['ordered_masks']),'positive_types':sum(c>0 for c in model['counts']),
         'outside_copies':model['outside_copies'],'binary_edge_variables':model['variables'],
         'complete_degree_rows':model['outside_copies'],'complete_support_incidence_rows':model['outside_copies']*model['support_order'],
         'complete_equations':len(model['rows']),'no_equitable_profile_assumed':True,
         'outside_pair_CN_model_equations_included':False,'count_witness_excluded':False,'numeric_status_is_proof':False}
    need(type(raw.get('outcome')) is dict and all(typed_equal(raw['outcome'].get(k),v) for k,v in expected.items()),'GATE_SCOPE')


def row_order(model):
    return [i for i,row in enumerate(model['rows']) if row['kind']=='degree']+[
        i for i,row in enumerate(model['rows']) if row['kind']=='support_incidence']


def fixed_units(logic,model):
    result=[]
    for v,pair in enumerate(model['variable_pairs']):
        logic.budget.tick();lo,hi=model['lower'][v],model['upper'][v];first=logic.count+1
        if lo==hi:logic.emit(v+1 if lo else -(v+1))
        result.append({'variable_index':v,'sat_id':v+1,'copy_pair':list(pair),'lower':lo,'upper':hi,
                       'first_clause':first,'clause_count':logic.count-first+1})
    return result


def local_row(logic,model,index,ordinal):
    row=model['rows'][index];true_ids=[];false_ids=[];inputs=[]
    for v,coefficient in row['terms']:
        need(type(v) is int and type(coefficient) is int and coefficient==1,'COUNTER_DOMAIN')
        if model['lower'][v]==model['upper'][v]:(true_ids if model['lower'][v] else false_ids).append(v+1)
        else:inputs.append(v+1)
    residual=row['lower']-len(true_ids)
    annotation={'group_ordinal':ordinal,'original_model_row':index,'original_row':copy.deepcopy(row),
                'fixed_true_inputs':true_ids,'fixed_false_inputs':false_ids,'residual':residual}
    if residual<0 or residual>len(inputs):
        first=logic.count+1;logic.emit()
        return {**annotation,'inputs':inputs,'bound':residual,'equality':True,'states':[],
                'first_auxiliary_variable':None,'last_auxiliary_variable':None,'auxiliary_null_reason':'IMPOSSIBLE_RESIDUAL',
                'first_clause':first,'clause_count':1}
    return logic.counter(inputs,residual,True,annotation)


def memory_encoding(model,budget):
    logic=Logic(model['variables'],budget);mapping=fixed_units(logic,model)
    groups=[local_row(logic,model,index,ordinal) for ordinal,index in enumerate(row_order(model))]
    return logic,mapping,groups


def canonical_clause(row):return (' '.join(map(str,row))+(' ' if row else '')+'0\n').encode('ascii')


class ClauseCompare:
    def __init__(self,body,cnf,budget):
        self.body,self.cnf,self.budget=body,cnf,budget;self.count,self.bytes=0,0;self.digest=hashlib.sha256()
        header=cnf.readline(1025);need(re.fullmatch(rb'p cnf ([0-9]+) ([0-9]+)\n',header) is not None,'DIMACS_HEADER')
        parts=header.split();self.declared_top,self.declared_clauses=int(parts[2]),int(parts[3])
        need(header==f'p cnf {self.declared_top} {self.declared_clauses}\n'.encode('ascii'),'DIMACS_HEADER')
    def consume(self,row):
        self.budget.tick();need(type(row) is list and all(type(v) is int and v!=0 for v in row),'CLAUSE_IDENTITY')
        expected=canonical_clause(row);need(len(expected)<=1024*1024,'CLAUSE_SIZE')
        body=self.body.readline(1024*1024+1);cnf=self.cnf.readline(1024*1024+1)
        need(body==expected and cnf==expected,'CLAUSE_IDENTITY')
        self.digest.update(body);self.bytes+=len(body);self.count+=1;need(self.bytes<=BODY_LIMIT,'CLAUSE_SIZE')
    def finish(self,logic):
        self.budget.tick();need((self.declared_top,self.declared_clauses)==(logic.top,logic.count),'DIMACS_HEADER')
        need(not self.body.read(1) and not self.cnf.read(1),'CLAUSE_EOF')


def encoding_model(model,mapping,logic):
    return {'schema':'FIXED17_PER_COPY_LOCAL_SAT_ENCODING_MODEL_V1','source_model':model,'variable_map':mapping,
      'group_order_model_rows':row_order(model),'groups_file':'groups.jsonl','clauses_file':'clauses.body','dimacs_file':'local.cnf',
      'total_groups':len(model['rows']),'degree_groups':model['outside_copies'],
      'support_groups':model['outside_copies']*model['support_order'],'base_variables':model['variables'],
      'variables':logic.top,'clauses':logic.count,'fixed_units':sum(a==b for a,b in zip(model['lower'],model['upper'])),
      'impossible_rows_possible_and_retained':True,'outside_pair_CN_equations_included':False,'no_equitable_profile_assumed':True}


def verify_pipeline(model,budget,load,open_binary,save_journal=None):
    total=len(model['rows']);journal_digest=hashlib.sha256();journal_bytes=0;checkpoints=[]
    with open_binary('clauses.body') as body,open_binary('local.cnf') as cnf,open_binary('groups.jsonl') as journal:
        compared=ClauseCompare(body,cnf,budget);logic=Logic(model['variables'],budget,compared.consume,False)
        mapping=fixed_units(logic,model)
        for ordinal,index in enumerate(row_order(model)):
            budget.tick();group=local_row(logic,model,index,ordinal);expected=json_bytes(group,True)
            actual=journal.readline(JSON_LIMIT+1);need(actual,'GROUP_EOF');need(actual==expected,'GROUP_IDENTITY')
            journal_digest.update(actual);journal_bytes+=len(actual);need(journal_bytes<=BODY_LIMIT,'GROUP_SIZE')
            if save_journal is not None:save_journal.write(expected);budget.tick()
            completed=ordinal+1
            if completed%100==0 or completed==total:
                expected_cp={'schema':'FIXED17_PER_COPY_LOCAL_SAT_CHECKPOINT_V1','completed_groups':completed,
                  'total_groups':total,'clauses':logic.count,'variables':logic.top,'body_bytes':compared.bytes,
                  'body_prefix_sha256':compared.digest.hexdigest(),'group_journal_bytes':journal_bytes,
                  'group_journal_prefix_sha256':journal_digest.hexdigest()}
                need(typed_equal(load('checkpoint_%04d.json'%completed),expected_cp),'CHECKPOINT_IDENTITY');checkpoints.append(expected_cp)
        need(not journal.read(1),'GROUP_EOF');compared.finish(logic)
    expected_model=encoding_model(model,mapping,logic)
    need(typed_equal(load('encoding_model.json'),expected_model),'ENCODING_MODEL_IDENTITY')
    return expected_model,{'complete_groups':total,'degree_groups':model['outside_copies'],
      'support_groups':model['outside_copies']*model['support_order'],'complete_checkpoints':len(checkpoints),
      'base_variables':model['variables'],'variables':logic.top,'clauses':logic.count,
      'body_bytes':compared.bytes,'body_sha256':compared.digest.hexdigest(),'group_journal_bytes':journal_bytes,
      'group_journal_sha256':journal_digest.hexdigest(),'exact_clause_order':True,'exact_group_order':True,
      'exact_dimacs_header':True,'exact_eof':True,'all_auxiliary_clauses_checked':True,'all_checkpoint_prefixes_checked':True}


def flags(words):
    need(type(words) is list and all(type(w) is str for w in words) and len(words)%2==0,'RUNTIME_WORDS')
    answer={}
    for i in range(0,len(words),2):
        need(words[i].startswith('--') and words[i] not in answer,'RUNTIME_WORDS');answer[words[i]]=words[i+1]
    return answer


def runtime_profile(plan,mode):
    need(type(plan) is dict,'RUNTIME_PLAN')
    if mode=='calibrate':
        need(plan.get('schema')=='FIXED17_PER_COPY_LOCAL_SAT_V1_SOURCE_ONLY_AUTHOR_CALIBRATION_PLAN','RUNTIME_PLAN_SCHEMA');selected=plan
    else:
        need(plan.get('schema')=='FIXED17_PER_COPY_LOCAL_SAT_V1_CONCRETE_BUILD_PLAN' and type(plan.get('build')) is dict,'RUNTIME_PLAN_SCHEMA')
        selected=plan['build']
        need(all(typed_equal(plan.get(k),selected.get(k)) for k in ('command','supervisor_argv','child_argv','worker_argv','allocation')),'RUNTIME_PLAN_ALIASES')
    need(all(k in selected for k in ('command','supervisor_argv','child_argv','worker_argv','allocation')),'RUNTIME_PLAN')
    need(typed_equal(selected['command'],selected['supervisor_argv']),'RUNTIME_PLAN_ALIASES')
    worker,child,command=selected['worker_argv'],selected['child_argv'],selected['command']
    need(type(worker) is list and len(worker)==(12 if mode=='calibrate' else 16) and
         Path(worker[0])==ROOT/'build/research-venv/Scripts/python.exe' and worker[1]=='-B' and
         Path(worker[2])==ROOT/PRODUCER and worker[3]==mode,'RUNTIME_WORKER')
    options=flags(worker[4:]);base_flags={'--seconds','--out','--self-sha256','--spec-sha256'}
    need(options.keys()==base_flags|({'--configuration','--configuration-sha256'} if mode=='build' else set()),'RUNTIME_FLAGS')
    need(type(child) is list and len(child)==len(worker)+8 and child[1:4]==['run','--locked','--offline'] and
         Path(child[0])==Path('C:/Users/ikuto/.local/bin/uv.exe') and child[4]=='--cache-dir' and
         Path(child[5])==ROOT/'build/uv-cache' and child[6]=='--python' and
         child[7]==worker[0] and typed_equal(child[8:],worker),'RUNTIME_CHILD')
    need(type(command) is list and len(command)==len(child)+16 and command[:3]==[worker[0],'-B',str(ROOT/SUP).replace('\\','/')]
         and command[15]=='--' and typed_equal(command[16:],child),'RUNTIME_SUPERVISOR')
    sup=flags(command[3:15]);need(sup.keys()=={'--seconds','--shutdown-reserve-seconds','--allocation-reason',
         '--success-criterion','--verification-criterion','--out'},'RUNTIME_SUPERVISOR')
    allocation=selected['allocation'];need(type(allocation) is dict,'RUNTIME_ALLOCATION')
    expected=(allocation.get('outer_seconds'),allocation.get('worker_seconds'),allocation.get('save_reserve_seconds'),allocation.get('shutdown_reserve_seconds'))
    need(all(type(x) in (int,float) and math.isfinite(x) for x in expected) and expected[0]>expected[1]>20 and expected[2:]==(20,20)
         and float(sup['--seconds'])==expected[0] and float(options['--seconds'])==expected[1] and
         float(sup['--shutdown-reserve-seconds'])==expected[3],'RUNTIME_ALLOCATION')
    return selected,options,expected


def runtime(plan,manifest,terminal,summary,mode):
    selected,options,allocation=runtime_profile(plan,mode)
    need(type(manifest) is dict and type(manifest.get('schema_version')) is int and manifest['schema_version']==1 and
         manifest.get('source_sha256')==SUP_SHA and manifest.get('runtime_scope')=='LOCAL_WINDOWS_SUSPENDED_JOB_V1' and
         manifest.get('process_scope')=='Local non-escaping process tree only; remote/daemonized compute is unsupported' and
         typed_equal(manifest.get('command'),selected['child_argv']) and type(manifest.get('cwd')) is str and
         Path(manifest['cwd'])==ROOT and manifest.get('automatic_retry') is False and
         manifest.get('cumulative_across_commands') is False and typed_equal(manifest.get('seconds'),float(allocation[0])) and
         typed_equal(manifest.get('shutdown_reserve_seconds'),float(allocation[3])),'RUNTIME_MANIFEST')
    need(type(manifest.get('invocation_id')) is str and manifest['invocation_id'] and type(terminal) is dict and
         terminal.get('invocation_id')==manifest['invocation_id'] and terminal.get('stop_reason')=='COMMAND_EXITED' and
         type(terminal.get('command_exit_code')) is int and terminal['command_exit_code']==0 and terminal.get('error') is None and
         terminal.get('deadline_reached') is False and terminal.get('hard_limit_observed') is True,'RUNTIME_TERMINAL')
    cleanup=terminal.get('cleanup');need(type(cleanup) is dict and all(cleanup.get(k) is True for k in
         ('created_suspended','resumed','reaped','job_active_zero_observed')) and cleanup.get('cleanup_errors')==[] and
         type(cleanup.get('actual_exit_code')) is int and cleanup['actual_exit_code']==0,'RUNTIME_CLEANUP')
    elapsed=terminal.get('elapsed_seconds');need(type(elapsed) in (int,float) and math.isfinite(elapsed) and
         0<=elapsed<=allocation[0],'RUNTIME_ELAPSED')
    raw_elapsed=summary.get('elapsed_seconds');need(type(raw_elapsed) in (int,float) and math.isfinite(raw_elapsed) and
         0<=raw_elapsed<allocation[1]-20,'RUNTIME_WORKER_ELAPSED')
    need(summary.get('mode')==mode and summary.get('source_sha256')==options['--self-sha256'] and
         summary.get('specification_sha256')==options['--spec-sha256'] and summary.get('producer')=='/root/structural' and
         summary.get('source_author')=='/root/structural' and summary.get('target_resolution')=='NONE','RUNTIME_SUMMARY')
    return options


def own_header(raw,software):
    need(type(raw) is dict and raw.get('status')==CAL_STATUS and type(raw.get('implementation_version')) is int and
         raw['implementation_version']==1 and type(raw.get('code_version')) is int and raw['code_version']==CODE_VERSION and
         raw.get('producer')=='/root/structural' and raw.get('verifier')=='/root/native_driver' and
         raw.get('method')=='independent_artifact_check' and raw.get('target_resolution')=='NONE','CALIBRATION_HEADER')
    need(typed_equal(raw.get('inputs_sha256'),software),'CALIBRATION_SOURCE')
    need(type(raw.get('outcome')) is dict and typed_equal(raw['outcome'].get('counts'),OWN_COUNTS) and
         raw['outcome'].get('all_precise_stages_match') is True and raw['outcome'].get('actual_profile_read') is False and
         raw['outcome'].get('actual_model_read') is False and typed_equal(raw['outcome'].get('solver_calls'),0),'CALIBRATION_SCOPE')


def qualification(reader,args,software):
    need(args.calibration is not None and args.calibration_sha256 is not None,'CALIBRATION_ARGUMENTS')
    raw,base=packet(reader,args.calibration,args.calibration_sha256);own_header(raw,software)
    stages=reader.read(base/'controls.json',raw['outputs_sha256'][key(base/'controls.json')])
    need(type(stages) is list and len(stages)==OWN_COUNTS['total'] and all(type(row) is dict and row.get('matches') is True and
         row.get('expected_stage')==row.get('actual_stage') for row in stages),'CALIBRATION_STAGES')


def source_packet(reader,args,mode):
    required=('producer_plan','producer_summary','producer_manifest','producer_terminal')
    need(all(getattr(args,k) is not None and getattr(args,k+'_sha256') is not None for k in required),'PRODUCER_ARGUMENTS')
    plan=reader.read(args.producer_plan,args.producer_plan_sha256)
    summary,base=packet(reader,args.producer_summary,args.producer_summary_sha256)
    manifest=reader.read(args.producer_manifest,args.producer_manifest_sha256)
    terminal=reader.read(args.producer_terminal,args.producer_terminal_sha256)
    options=runtime(plan,manifest,terminal,summary,mode);output_directory(options['--out'],base)
    need(options['--self-sha256']==PINS[PRODUCER] and options['--spec-sha256']==PINS[PRODUCER_SPEC] and
         type(summary.get('implementation_version')) is int and summary['implementation_version']==1,'PRODUCER_SOURCE')
    for name in AUTHOR_SOFTWARE_KEYS:need(summary['inputs_sha256'].get(name)==PINS[name],'PRODUCER_SOURCE')
    if mode=='calibrate':need(typed_equal(summary['inputs_sha256'],{k:PINS[k] for k in AUTHOR_SOFTWARE_KEYS}),'PRODUCER_CALIBRATION_SOURCE')
    return summary,base,options


def satisfies(rows,assignment):
    return all(any(assignment[abs(lit)]==(lit>0) for lit in row) for row in rows)


def extensions(logic,bits,budget):
    accepted=[]
    for extras in itertools.product((False,True),repeat=logic.top-len(bits)):
        budget.tick();assignment={i+1:v for i,v in enumerate((*bits,*extras))}
        if satisfies(logic.rows,assignment):accepted.append(list(extras))
    return accepted


def recurrence_tables(budget):
    observations=[]
    for a_kind,c_kind in itertools.product((False,True,'input'),repeat=2):
        logic=Logic(3,budget);a=1 if a_kind=='input' else a_kind;c=3 if c_kind=='input' else c_kind
        reference=logic.threshold_ref(a,2,c)
        for bits in itertools.product((False,True),repeat=3):
            extras=extensions(logic,bits,budget);need(len(extras)==1,'RECURRENCE_TRUTH')
            expected=(bits[0] if a_kind=='input' else a_kind) or (bits[1] and (bits[2] if c_kind=='input' else c_kind))
            values={i+1:v for i,v in enumerate((*bits,*extras[0]))};observed=reference if type(reference) is bool else values[reference]
            need(observed==expected,'RECURRENCE_TRUTH')
            observations.append({'a':a_kind,'c':c_kind,'base':list(bits),'result_ref':reference,'expected':expected,
                                 'auxiliary':extras[0],'clauses':copy.deepcopy(logic.rows)})
    need(len(observations)==72,'RECURRENCE_TRUTH');return observations


def counter_tables(budget):
    observations=[]
    for n in range(4):
        for bound in range(n+1):
            logic=Logic(n,budget);record=logic.counter(list(range(1,n+1)),bound,True,{'n':n})
            for bits in itertools.product((False,True),repeat=n):
                extras=extensions(logic,bits,budget);expected=sum(bits)==bound;need(len(extras)==int(expected),'COUNTER_TRUTH')
                observations.append({'n':n,'bound':bound,'base':list(bits),'expected':expected,
                     'satisfying_auxiliaries':extras,'record':copy.deepcopy(record),'clauses':copy.deepcopy(logic.rows)})
    need(len(observations)==49,'COUNTER_TRUTH');return observations


def residual_tables(budget):
    cases=[([],[],0),([],[],-1),([],[],1),([1,0],[1,0],1),([1,0],[1,0],0),
           ([1,0],[1,0],2),([1,0,0],[1,1,1],2),([0,0],[1,1],1)]
    observations=[]
    for index,(lo,hi,rhs) in enumerate(cases):
        n=len(lo);logic=Logic(n,budget)
        for v in range(n):
            if lo[v]==hi[v]:logic.emit(v+1 if lo[v] else -(v+1))
        row={'kind':'degree','copy_x':0,'type_i':0,'support_u':None,'lower':rhs,'upper':rhs,'terms':[[v,1] for v in range(n)]}
        model={'rows':[row],'lower':lo,'upper':hi};record=local_row(logic,model,0,index)
        record['original_model_row']=index
        for bits in itertools.product((False,True),repeat=n):
            extras=extensions(logic,bits,budget);expected=all(lo[v]<=int(bits[v])<=hi[v] for v in range(n)) and sum(bits)==rhs
            need(len(extras)==int(expected),'RESIDUAL_TRUTH')
            observations.append({'case':index,'lower':lo,'upper':hi,'rhs':rhs,'base':list(bits),'expected':expected,
                 'satisfying_auxiliaries':extras,'record':copy.deepcopy(record),'clauses':copy.deepcopy(logic.rows)})
    return observations


def graph_from_edges(raw,model,values,budget):
    g=profile_geometry(raw,budget);n,m=g['n'],g['support'];neighbors=[set() for _ in range(n)]
    for u in range(m):neighbors[u].update(v for v,bit in enumerate(g['h'][u]) if bit)
    for x,vertices in enumerate(g['types']):
        for u in vertices:neighbors[u].add(m+x);neighbors[m+x].add(u)
    for (x,y),bit in zip(model['variable_pairs'],values):
        if bit:neighbors[m+x].add(m+y);neighbors[m+y].add(m+x)
    return [[int(v in neighbors[u]) for v in range(n)] for u in range(n)]


def rook_check(payload,budget,switched):
    raw,submitted,values=payload['profile'],payload['model'],payload['edges'];model=validate_model(raw,submitted,budget)
    need(type(values) is list and len(values)==model['variables'] and all(type(v) is int and v in (0,1) for v in values),'ROOK_LOCAL')
    need(all(a<=v<=b for a,v,b in zip(model['lower'],values,model['upper'])) and
         all(sum(values[v] for v,c in row['terms'])==row['lower'] for row in model['rows']),'ROOK_LOCAL')
    logic,mapping,groups=memory_encoding(model,budget);assignment={v+1:bool(bit) for v,bit in enumerate(values)}
    for group in groups:
        for prefix,threshold,ref in group['states']:
            truth=sum(assignment[v] for v in group['inputs'][:prefix])>=threshold
            if type(ref) is bool:need(ref==truth,'ROOK_EXTENSION')
            elif ref in assignment:need(assignment[ref]==truth,'ROOK_EXTENSION')
            else:assignment[ref]=truth
    need(set(assignment)==set(range(1,logic.top+1)) and satisfies(logic.rows,assignment),'ROOK_EXTENSION')
    graph=graph_from_edges(raw,model,values,budget);diagnostic=whole_srg_diagnostic(graph,4,budget)
    failure=diagnostic['first_failure'];first=None if failure is None else {'u':failure['u'],'v':failure['v'],'observed':failure['actual'],'expected':failure['expected']}
    need(typed_equal(first,{'u':2,'v':4,'observed':0,'expected':1} if switched else None),'ROOK_GRAPH_BOUNDARY')
    return {'profile':raw,'model':model,'edge_assignment':values,'sat_assignment':[[v,int(assignment[v])] for v in sorted(assignment)],
      'variable_map':mapping,'groups':groups,'clauses':logic.rows,'adjacency':graph,
      'ordered_common_neighbors':diagnostic['common_neighbor_matrix'],'first_full_graph_failure':first,
      'local_encoding_pass':True,'full_graph_pass':first is None}


AUTHOR_ROUTES=[('recurrence_complete_truth_table','PASS'),('counter_complete_truth_tables','PASS'),
 ('residual_complete_truth_tables','PASS'),('rook_local_witness','PASS'),('switched_rook_local_only','PASS'),
 ('forced_rook_bounds','PASS'),('input_gate_header_and_scope','PASS'),('target_bool','PROFILE_TARGET'),
 ('degree_float','PROFILE_TARGET'),('graph_asymmetric','PROFILE_GRAPH'),('mask_bool','PROFILE_MASKS'),
 ('count_bool','PROFILE_COUNTS'),('pair_bit_bool','PROFILE_PAIR_BITS'),('pair_order','PROFILE_PAIR_ORDER'),
 ('occupied_empty_pair','PROFILE_INCOMPATIBLE_PAIR'),('variable_pair_changed','MODEL_VARIABLE_PAIRS'),
 ('row_missing','MODEL_ROWS'),('rhs_changed','MODEL_RECONSTRUCTION'),('coefficient_bool','MODEL_ROW_DOMAIN'),
 ('bound_bool','MODEL_BOUNDS'),('term_duplicate','MODEL_ROW_DOMAIN'),('diagonal_variable','MODEL_VARIABLE_PAIRS'),
 ('scope_flag_changed','MODEL_FLAGS'),('gate_implementation_bool','GATE_HEADER'),('gate_pin_changed','GATE_PINS'),
 ('gate_equations_bool','GATE_SCOPE'),('json_duplicate','JSON_DUPLICATE'),('json_nonfinite','JSON_NONFINITE'),
 ('tiny_fixture_is_not_science','SCIENTIFIC_SCOPE')]


def hand_rook_payload(switched=False,forced=False):
    fixture=switched_rook_fixture() if switched else rook_fixture();raw=fixture['profile']
    if forced:
        fixed={(0,0):[1],(1,1):[1],(2,2):[1],(0,3):[1],(1,3):[0],(2,3):[0],(3,3):[0]}
        for row in raw['pair_bits']:row['bits']=list(fixed.get((row['i'],row['j']),[0,1]))
    return {'profile':raw,'model':wire_model(raw),'edges':list(fixture['candidate']['edge_values'])}


def synthetic_gate(model):
    refs=[{'path':'synthetic/profile.json','sha256':'1'*64},{'path':'synthetic/model.json','sha256':'2'*64}]
    raw={'status':COPY_STATUS,'implementation_version':1,'producer':'/root/checkpoint_audit','verifier':'/root/native_driver',
         'method':'independent_artifact_check','target_resolution':'NONE','inputs_sha256':{r['path']:r['sha256'] for r in refs},
         'outcome':{'complete_input_type_count':len(model['ordered_masks']),'positive_types':sum(c>0 for c in model['counts']),
          'outside_copies':model['outside_copies'],'binary_edge_variables':model['variables'],
          'complete_degree_rows':model['outside_copies'],'complete_support_incidence_rows':model['outside_copies']*model['support_order'],
          'complete_equations':len(model['rows']),'no_equitable_profile_assumed':True,
          'outside_pair_CN_model_equations_included':False,'count_witness_excluded':False,'numeric_status_is_proof':False}}
    return raw,refs


def author_action(name,payload,budget):
    if name=='recurrence_complete_truth_table':return recurrence_tables(budget)
    if name=='counter_complete_truth_tables':return counter_tables(budget)
    if name=='residual_complete_truth_tables':return residual_tables(budget)
    if name in ('rook_local_witness','switched_rook_local_only','forced_rook_bounds'):
        return rook_check(payload,budget,name=='switched_rook_local_only')
    fixture=hand_rook_payload();raw,model=fixture['profile'],fixture['model']
    if name.startswith('gate_') or name=='input_gate_header_and_scope':
        return copy_gate(payload,model,synthetic_gate(model)[1])
    if name in {'target_bool','degree_float','graph_asymmetric','mask_bool','count_bool','pair_bit_bool','pair_order','occupied_empty_pair'}:
        return bounded_profile(payload,budget)
    if name in {'variable_pair_changed','row_missing','rhs_changed','coefficient_bool','bound_bool','term_duplicate','diagonal_variable','scope_flag_changed'}:
        return validate_model(raw,payload,budget)
    if name in ('json_duplicate','json_nonfinite'):return decode(payload['raw_utf8'].encode('ascii'))
    if name=='tiny_fixture_is_not_science':return scientific_scope(payload['profile'],payload['model'],budget)
    raise Veto('AUTHOR_ACTION')


def replay_controls(reader,summary,base,out):
    expected={'positive_controls':7,'negative_controls':22,'total_controls':29,'recurrence_observations':72,
      'counter_observations':49,'residual_hand_cases':8,'full_rook_common_neighbor_entries':243,
      'synthetic_gate_controls':True,'actual_per_copy_gate_read':False,'actual_profile_read':False,'actual_model_read':False,
      'solver_calls':0,'inherited_helper_definitions_only':True,'truth_table_controls_are_complete':True}
    need(summary.get('status')==AUTHOR_STATUS and typed_equal(summary.get('outcome'),expected),'AUTHOR_SCOPE')
    names={'controls.json'};table=reader.read(base/'controls.json',summary['outputs_sha256'][key(base/'controls.json')]);pairs=[]
    need(type(table) is list and len(table)==29,'AUTHOR_STAGE_POPULATION')
    for index,(name,stage) in enumerate(AUTHOR_ROUTES):
        reader.budget.tick();filename='case_%02d.json'%index;names.add(filename)
        saved=reader.read(base/filename,summary['outputs_sha256'][key(base/filename)])
        expected_row={'index':index,'name':name,'expected_stage':stage,'actual_stage':stage,'matched':True}
        need(typed_equal(table[index],expected_row) and type(saved) is dict and
             all(typed_equal(saved.get(k),v) for k,v in expected_row.items()),'AUTHOR_STAGE_ROW')
        actual,result='PASS',None
        try:result=author_action(name,saved['payload'],reader.budget)
        except Veto as exc:
            if str(exc)=='SAVE_RESERVE':raise
            actual=str(exc)
        need(actual==stage,'AUTHOR_INDEPENDENT_STAGE:'+name+':'+actual)
        if stage=='PASS':
            need(typed_equal(saved.get('result'),result),'AUTHOR_RETURNED_RESULT')
            write(out/('independent_author_result_%02d.json'%index),result,reader.budget)
        pairs.append({'index':index,'name':name,'expected_stage':stage,'producer_stage':table[index]['actual_stage'],
                      'independent_stage':actual,'matches':True})
    need({key(base/name) for name in names}==set(summary['outputs_sha256']) and len(names)==30,'AUTHOR_OUTPUT_POPULATION')
    write(out/'independent_stage_pairs.json',pairs,reader.budget)
    return {'counts':AUTHOR_COUNTS,'all_precise_stages_match':True,'author_physical_files':31,'author_output_hashes':30,
      'all_recurrence_base_cases':72,'all_counter_base_cases':49,'residual_hand_cases':8,'complete_fixture_cn_entries':243,
      'actual_target_input_read':False,'solver_calls':0}


def author_payloads():
    normal=hand_rook_payload();raw,model=normal['profile'],normal['model'];g,refs=synthetic_gate(model)
    positives=[{'base_bits':3,'a_c_choices':9},{'n_range':[0,3],'all_bounds':True},{'hand_cases':8},
               normal,hand_rook_payload(True),hand_rook_payload(False,True),g]
    result=[copy.deepcopy(p) for p in positives]
    edits=[('target_order',True),('target_degree',4.0)]
    for name,value in edits:p=copy.deepcopy(raw);p[name]=value;result.append(p)
    p=copy.deepcopy(raw);p['support_adjacency'][0][1]=0;result.append(p)
    p=copy.deepcopy(raw);p['ordered_masks'][0]=False;result.append(p)
    p=copy.deepcopy(raw);p['counts'][0]=True;result.append(p)
    p=copy.deepcopy(raw);p['pair_bits'][0]['bits']=[False,1];result.append(p)
    p=copy.deepcopy(raw);p['pair_bits'][0]['j']=1;result.append(p)
    p=copy.deepcopy(raw);p['pair_bits'][0]['bits']=[];result.append(p)
    p=copy.deepcopy(model);p['variable_pairs'][0][1]=2;result.append(p)
    p=copy.deepcopy(model);p['rows'].pop();result.append(p)
    p=copy.deepcopy(model);p['rows'][0]['lower']=p['rows'][0]['upper']=3;result.append(p)
    p=copy.deepcopy(model);p['rows'][0]['terms'][0][1]=True;result.append(p)
    p=copy.deepcopy(model);p['lower'][0]=False;result.append(p)
    p=copy.deepcopy(model);p['rows'][0]['terms'][1]=list(p['rows'][0]['terms'][0]);result.append(p)
    p=copy.deepcopy(model);p['variable_pairs'][0][1]=0;result.append(p)
    p=copy.deepcopy(model);p['no_equitable_profile_assumed']=False;result.append(p)
    p=copy.deepcopy(g);p['implementation_version']=True;result.append(p)
    p=copy.deepcopy(g);p['inputs_sha256'][refs[0]['path']]='3'*64;result.append(p)
    p=copy.deepcopy(g);p['outcome']['complete_equations']=True;result.append(p)
    result.extend([{'raw_utf8':'{"x":1,"x":2}'},{'raw_utf8':'{"x":NaN}'},{'profile':raw,'model':model}])
    need(len(result)==29,'AUTHOR_PAYLOAD_DEFINITIONS');return result


def synthetic_runtime():
    python=str(ROOT/'build/research-venv/Scripts/python.exe').replace('\\','/')
    worker=[python,'-B',str(ROOT/PRODUCER).replace('\\','/'),'calibrate','--seconds','100','--out',
            str(ROOT/'acceleration/results/synthetic_local_sat').replace('\\','/'),'--self-sha256',PINS[PRODUCER],
            '--spec-sha256',PINS[PRODUCER_SPEC]]
    child=[str(Path('C:/Users/ikuto/.local/bin/uv.exe')),'run','--locked','--offline','--cache-dir',
           str(ROOT/'build/uv-cache').replace('\\','/'),'--python',python,*worker]
    command=[python,'-B',str(ROOT/SUP).replace('\\','/'),'--seconds','120','--shutdown-reserve-seconds','20',
             '--allocation-reason','finite fixture','--success-criterion','finite fixture',
             '--verification-criterion','finite fixture','--out','synthetic_supervision','--',*child]
    plan={'schema':'FIXED17_PER_COPY_LOCAL_SAT_V1_SOURCE_ONLY_AUTHOR_CALIBRATION_PLAN','command':command,
          'supervisor_argv':command,'child_argv':child,'worker_argv':worker,
          'allocation':{'outer_seconds':120,'worker_seconds':100,'save_reserve_seconds':20,'shutdown_reserve_seconds':20}}
    manifest={'schema_version':1,'invocation_id':'synthetic','source_sha256':SUP_SHA,
       'runtime_scope':'LOCAL_WINDOWS_SUSPENDED_JOB_V1',
       'process_scope':'Local non-escaping process tree only; remote/daemonized compute is unsupported',
       'command':child,'cwd':str(ROOT),'seconds':120.0,'shutdown_reserve_seconds':20.0,
       'automatic_retry':False,'cumulative_across_commands':False}
    terminal={'invocation_id':'synthetic','stop_reason':'COMMAND_EXITED','command_exit_code':0,'error':None,
       'deadline_reached':False,'hard_limit_observed':True,'elapsed_seconds':1.0,'cleanup':{
       'created_suspended':True,'resumed':True,'reaped':True,'job_active_zero_observed':True,
       'cleanup_errors':[],'actual_exit_code':0}}
    summary={'mode':'calibrate','source_sha256':PINS[PRODUCER],'specification_sha256':PINS[PRODUCER_SPEC],
       'producer':'/root/structural','source_author':'/root/structural','target_resolution':'NONE','elapsed_seconds':0.5}
    return {'plan':plan,'manifest':manifest,'terminal':terminal,'summary':summary}


def write_fixture(folder,model,budget):
    need(not folder.exists(),'OUTPUT_EXISTS');folder.mkdir();logic,mapping,groups=memory_encoding(model,budget)
    body=b''.join(canonical_clause(row) for row in logic.rows);lines=[json_bytes(g,True) for g in groups]
    blobs={'clauses.body':body,'local.cnf':f'p cnf {logic.top} {logic.count}\n'.encode('ascii')+body,
           'groups.jsonl':b''.join(lines),'encoding_model.json':json_bytes(encoding_model(model,mapping,logic))}
    for completed in range(1,len(groups)+1):
        if completed%100 and completed!=len(groups):continue
        last=groups[completed-1];clause_count=last['first_clause']+last['clause_count']-1
        top=max([model['variables']]+[g['last_auxiliary_variable'] for g in groups[:completed] if g['last_auxiliary_variable'] is not None])
        prefix=b''.join(canonical_clause(row) for row in logic.rows[:clause_count]);journal=b''.join(lines[:completed])
        blobs['checkpoint_%04d.json'%completed]=json_bytes({'schema':'FIXED17_PER_COPY_LOCAL_SAT_CHECKPOINT_V1',
          'completed_groups':completed,'total_groups':len(groups),'clauses':clause_count,'variables':top,
          'body_bytes':len(prefix),'body_prefix_sha256':hashlib.sha256(prefix).hexdigest(),
          'group_journal_bytes':len(journal),'group_journal_prefix_sha256':hashlib.sha256(journal).hexdigest()})
    for name,data in blobs.items():
        budget.tick()
        with (folder/name).open('xb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
        budget.tick()
    return blobs


def pipeline_blobs(model,blobs,budget):
    return verify_pipeline(model,budget,lambda name:decode(blobs[name]),lambda name:io.BytesIO(blobs[name]))


def normalization_control(budget):
    logic=Logic(2,budget);logic.emit(False,1,1,False);logic.emit(1,-1);logic.emit(True,-1);logic.emit(False,False)
    need(typed_equal(logic.rows,[[1],[]]),'NORMALIZATION');return {'clauses':logic.rows,'count':logic.count}


def output_population(mode,outputs):
    need(type(mode) is str and mode in ('calibrate','controls','full') and
         type(outputs) is dict,'CHECKER_OUTPUT_POPULATION')
    # Calibration: one leaf per action + controls.json + eleven stream leaves + two inventory leaves.
    expected=OWN_COUNTS['total']+14 if mode=='calibrate' else 8 if mode=='controls' else 11
    need(len(outputs)==expected,'CHECKER_OUTPUT_POPULATION')
    return {'mode':mode,'non_summary_outputs':expected,'physical_files_including_summary':expected+1}


def own_routes(out,budget,software):
    rows=[]
    def run(name,stage,payload,action):
        budget.tick();observed,result,error='PASS',None,None
        try:result=action()
        except Veto as exc:
            if str(exc)=='SAVE_RESERVE' and stage!='SAVE_RESERVE':raise
            observed,error=str(exc),str(exc)
        except Exception as exc:observed,error='UNEXPECTED_EXCEPTION',repr(exc)
        row={'index':len(rows),'name':name,'expected_stage':stage,'actual_stage':observed,'matches':stage==observed}
        write(out/('control_%03d.json'%len(rows)),{**row,'payload':payload,'result':result,'error':error},budget);rows.append(row)
    for (name,stage),payload in zip(AUTHOR_ROUTES,author_payloads()):
        run(name,stage,payload,lambda name=name,payload=payload:author_action(name,payload,budget))
    rook=hand_rook_payload(False,True);rook_model=rook['model']
    rook_blobs=write_fixture(out/'fixture_rook',rook_model,budget)
    late_raw={'target_order':53,'target_degree':2,'support_adjacency':[[0]],'ordered_masks':[0],'counts':[52],
              'pair_bits':[{'i':0,'j':0,'bits':[0]}]}
    late_model=wire_model(late_raw,budget);late_blobs=write_fixture(out/'fixture_late',late_model,budget)
    runtime_payload=synthetic_runtime()
    rt_action=lambda p:runtime(p['plan'],p['manifest'],p['terminal'],p['summary'],'calibrate')
    header={'status':CAL_STATUS,'implementation_version':1,'code_version':CODE_VERSION,'producer':'/root/structural','verifier':'/root/native_driver',
      'method':'independent_artifact_check','target_resolution':'NONE','inputs_sha256':software,
      'outcome':{'counts':OWN_COUNTS,'all_precise_stages_match':True,'actual_profile_read':False,'actual_model_read':False,'solver_calls':0}}
    run('positive_disk_rook_pipeline','PASS',{'fixture':'fixture_rook'},lambda:verify_pipeline(rook_model,budget,
        lambda name:decode((out/'fixture_rook'/name).read_bytes()),lambda name:(out/'fixture_rook'/name).open('rb')))
    run('positive_late_constant_pipeline','PASS',{'fixture':'fixture_late','groups':104,'checkpoints':[100,104]},
        lambda:pipeline_blobs(late_model,late_blobs,budget))
    run('positive_normalization','PASS',{},lambda:normalization_control(budget))
    run('positive_fixed_only_constant','PASS',{'fixture':'fixture_late','all104impossible':True},
        lambda:need(sum(row==[] for row in memory_encoding(late_model,budget)[0].rows)==104,'IMPOSSIBLE_RESIDUAL'))
    run('positive_actual_sup2_runtime','PASS',runtime_payload,lambda:rt_action(runtime_payload))
    run('positive_output_directory','PASS',str(out),lambda:str(output_directory(str(out),out)))
    run('positive_source_snapshot','PASS',header,lambda:own_header(header,software))
    def corrupt(name,stage,base_model,base_blobs,edit):
        changed=dict(base_blobs);edit(changed)
        payload={'changed_files':{k:v.decode('utf-8') for k,v in changed.items() if v!=base_blobs[k]}}
        run(name,stage,payload,lambda:pipeline_blobs(base_model,changed,budget))
    def json_edit(blobs,name,edit):
        value=decode(blobs[name]);edit(value);blobs[name]=json_bytes(value)
    def group_edit(blobs,ordinal,edit):
        lines=blobs['groups.jsonl'].splitlines(keepends=True);value=decode(lines[ordinal]);edit(value)
        lines[ordinal]=json_bytes(value,True);blobs['groups.jsonl']=b''.join(lines)
    corrupt('fixed_unit_wrong','CLAUSE_IDENTITY',rook_model,rook_blobs,
        lambda p:p.__setitem__('clauses.body',b'999 0\n'+p['clauses.body'].split(b'\n',1)[1]))
    corrupt('group_residual_changed','GROUP_IDENTITY',rook_model,rook_blobs,
        lambda p:group_edit(p,0,lambda g:g.__setitem__('residual',g['residual']+1)))
    corrupt('late_group_missing','GROUP_EOF',late_model,late_blobs,
        lambda p:p.__setitem__('groups.jsonl',b''.join(p['groups.jsonl'].splitlines(keepends=True)[:-1])))
    corrupt('dimacs_top_changed','DIMACS_HEADER',rook_model,rook_blobs,
        lambda p:p.__setitem__('local.cnf',b'p cnf 999999 '+p['local.cnf'].split(b'\n',1)[0].split()[3]+b'\n'+p['local.cnf'].split(b'\n',1)[1]))
    corrupt('dimacs_clause_count_changed','DIMACS_HEADER',rook_model,rook_blobs,
        lambda p:p.__setitem__('local.cnf',p['local.cnf'].replace(p['local.cnf'].split(b'\n',1)[0],
          b'p cnf '+p['local.cnf'].split()[2]+b' 999999',1)))
    corrupt('dimacs_spacing','DIMACS_HEADER',rook_model,rook_blobs,
        lambda p:p.__setitem__('local.cnf',p['local.cnf'].replace(b'p cnf ',b'p  cnf ',1)))
    corrupt('clause_missing','CLAUSE_IDENTITY',rook_model,rook_blobs,
        lambda p:p.__setitem__('clauses.body',p['clauses.body'].split(b'\n',1)[1]))
    run('clause_boolean_alias','CLAUSE_IDENTITY',{'clause':[True]},
        lambda:ClauseCompare(io.BytesIO(),io.BytesIO(b'p cnf 1 1\n'),budget).consume([True]))
    corrupt('clause_spacing','CLAUSE_IDENTITY',rook_model,rook_blobs,
        lambda p:p.__setitem__('clauses.body',b' '+p['clauses.body']))
    corrupt('trailing_clause','CLAUSE_EOF',rook_model,rook_blobs,
        lambda p:p.__setitem__('local.cnf',p['local.cnf']+b'1 0\n'))
    corrupt('checkpoint_body_hash','CHECKPOINT_IDENTITY',late_model,late_blobs,
        lambda p:json_edit(p,'checkpoint_0100.json',lambda c:c.__setitem__('body_prefix_sha256','0'*64)))
    corrupt('checkpoint_journal_bytes','CHECKPOINT_IDENTITY',late_model,late_blobs,
        lambda p:json_edit(p,'checkpoint_0100.json',lambda c:c.__setitem__('group_journal_bytes',0)))
    corrupt('late_checkpoint_bool','CHECKPOINT_IDENTITY',late_model,late_blobs,
        lambda p:json_edit(p,'checkpoint_0104.json',lambda c:c.__setitem__('completed_groups',True)))
    corrupt('map_id_bool','ENCODING_MODEL_IDENTITY',rook_model,rook_blobs,
        lambda p:json_edit(p,'encoding_model.json',lambda c:c['variable_map'][0].__setitem__('sat_id',True)))
    corrupt('encoding_scope_changed','ENCODING_MODEL_IDENTITY',rook_model,rook_blobs,
        lambda p:json_edit(p,'encoding_model.json',lambda c:c.__setitem__('no_equitable_profile_assumed',False)))
    corrupt('group_aux_missing','GROUP_IDENTITY',rook_model,rook_blobs,
        lambda p:group_edit(p,0,lambda g:g.__setitem__('first_auxiliary_variable',999999)))
    damaged=copy.deepcopy(rook_model);damaged['lower'][0]=damaged['upper'][0]=0
    run('mandatory_bound_changed','MODEL_RECONSTRUCTION',damaged,lambda:validate_model(rook['profile'],damaged,budget))
    corrupt('impossible_residual_annotation','GROUP_IDENTITY',late_model,late_blobs,
        lambda p:group_edit(p,103,lambda g:g.__setitem__('auxiliary_null_reason',None)))
    corrupt('map_unit_range_changed','ENCODING_MODEL_IDENTITY',rook_model,rook_blobs,
        lambda p:json_edit(p,'encoding_model.json',lambda c:c['variable_map'][0].__setitem__('clause_count',0)))
    damaged_header=copy.deepcopy(header);damaged_header['implementation_version']=True
    run('own_version_bool','CALIBRATION_HEADER',damaged_header,lambda:own_header(damaged_header,software))
    damaged_pins=copy.deepcopy(header);damaged_pins['inputs_sha256'][SELF]='0'*64
    run('own_source_snapshot_changed','CALIBRATION_SOURCE',damaged_pins,lambda:own_header(damaged_pins,software))
    unreaped=copy.deepcopy(runtime_payload);unreaped['terminal']['cleanup']['resumed']=False
    run('runtime_unresumed','RUNTIME_CLEANUP',unreaped,lambda:rt_action(unreaped))
    wrong_scope=copy.deepcopy(runtime_payload);wrong_scope['manifest']['runtime_scope']='invented'
    run('runtime_wrong_scope','RUNTIME_MANIFEST',wrong_scope,lambda:rt_action(wrong_scope))
    wrong_elapsed=copy.deepcopy(runtime_payload);wrong_elapsed['terminal']['elapsed_seconds']='inf'
    run('runtime_elapsed_string','RUNTIME_ELAPSED',wrong_elapsed,lambda:rt_action(wrong_elapsed))
    run('file_as_directory','OUTPUT_DIRECTORY',str(out/'control_000.json'),lambda:output_directory(str(out/'control_000.json'),out))
    run('reserve_boundary','SAVE_RESERVE',{'stop_required':False,'remaining_seconds':20},
        lambda:reserve({'stop_required':False,'remaining_seconds':20}))
    hidden=out/'fixture_inventory';hidden.mkdir();(hidden/'extra').mkdir()
    write(hidden/'summary.json',{'inputs_sha256':{},'outputs_sha256':{}},budget)
    write(hidden/'extra/summary.json',{'unlisted_extra':True},budget)
    hidden_summary=hidden/'summary.json';hidden_digest=Reader(budget).digest(hidden_summary)
    run('unlisted_nested_summary','PACKET_POPULATION',{'fixture':'fixture_inventory','unlisted':'extra/summary.json'},
        lambda:packet(Reader(budget),str(hidden_summary),hidden_digest))
    native_source='acceleration/audit_20261004_fixed17_per_copy_adjacency_v1.py'
    native_spec='acceleration/audit_20261004_fixed17_per_copy_adjacency_v1_spec.md'
    exact_native={name:PINS[name] for name in (native_source,native_spec)}
    actual_gate_header={'status':COPY_STATUS,'implementation_version':1,
      'producer':'/root/checkpoint_audit','verifier':'/root/native_driver',
      'method':'independent_artifact_check','target_resolution':'NONE',
      'source_software':dict(exact_native),'inputs_sha256':dict(exact_native)}
    run('positive_copy_gate_actual_source_maps','PASS',actual_gate_header,
        lambda:copy_gate_source(actual_gate_header))
    def damaged_copy_source(name,edit):
        changed=copy.deepcopy(actual_gate_header);edit(changed)
        run(name,'COPY_GATE_SOURCE',changed,lambda:copy_gate_source(changed))
    damaged_copy_source('copy_source_map_missing',lambda p:p.pop('source_software'))
    damaged_copy_source('copy_source_map_bool',lambda p:p.__setitem__('source_software',True))
    damaged_copy_source('copy_source_key_missing',lambda p:p['source_software'].pop(native_source))
    damaged_copy_source('copy_source_hash_bool',lambda p:p['source_software'].__setitem__(native_source,True))
    damaged_copy_source('copy_source_hash_mismatch',lambda p:p['source_software'].__setitem__(native_source,'0'*64))
    damaged_copy_source('copy_spec_key_missing',lambda p:p['source_software'].pop(native_spec))
    damaged_copy_source('copy_spec_hash_mismatch',lambda p:p['source_software'].__setitem__(native_spec,'0'*64))
    damaged_copy_source('copy_input_map_missing',lambda p:p.pop('inputs_sha256'))
    damaged_copy_source('copy_input_map_bool',lambda p:p.__setitem__('inputs_sha256',True))
    damaged_copy_source('copy_input_source_missing',lambda p:p['inputs_sha256'].pop(native_source))
    damaged_copy_source('copy_input_source_bool',lambda p:p['inputs_sha256'].__setitem__(native_source,True))
    damaged_copy_source('copy_input_spec_mismatch',lambda p:p['inputs_sha256'].__setitem__(native_spec,'0'*64))
    model_gate_base=out/'fixture_copy_gate'
    model_gate_ref={'path':key(model_gate_base/'summary.json'),'sha256':'1'*64}
    accepted_model={'variables':3321,'rows':1476,'copies':82,'checkpoints':9,
      'path':key(model_gate_base/'independent_copy_model.json'),'sha256':'2'*64}
    basename_model_gate={'outputs_sha256':{'independent_copy_model.json':'2'*64,'independent_stage_pairs.json':'3'*64}}
    model_acceptance_fixture={'prior':basename_model_gate,'checked':accepted_model,'summary_ref':model_gate_ref}
    model_ref_action=lambda p:accepted_copy_model_ref(p['prior'],p['checked'],p['summary_ref'])
    run('positive_copy_model_basename_output_map','PASS',model_acceptance_fixture,
        lambda:model_ref_action(model_acceptance_fixture))
    canonical_model_gate=copy.deepcopy(model_acceptance_fixture)
    canonical_model_gate['prior']['outputs_sha256']={key(model_gate_base/name):digest for name,digest in basename_model_gate['outputs_sha256'].items()}
    run('positive_copy_model_canonical_output_map','PASS',canonical_model_gate,
        lambda:model_ref_action(canonical_model_gate))
    def damaged_model_acceptance(name,edit):
        changed=copy.deepcopy(model_acceptance_fixture);edit(changed)
        run(name,'ROOT_MODEL_ACCEPTANCE',changed,lambda:model_ref_action(changed))
    damaged_model_acceptance('copy_model_outputs_missing',lambda p:p['prior'].pop('outputs_sha256'))
    damaged_model_acceptance('copy_model_outputs_bool',lambda p:p['prior'].__setitem__('outputs_sha256',True))
    damaged_model_acceptance('copy_model_output_hash_bool',lambda p:p['prior']['outputs_sha256'].__setitem__('independent_copy_model.json',True))
    damaged_model_acceptance('copy_model_output_hash_nonhex',lambda p:p['prior']['outputs_sha256'].__setitem__('independent_copy_model.json','Z'*64))
    damaged_model_acceptance('copy_model_output_hash_mismatch',lambda p:p['prior']['outputs_sha256'].__setitem__('independent_copy_model.json','4'*64))
    damaged_model_acceptance('copy_model_output_missing',lambda p:p['prior']['outputs_sha256'].pop('independent_copy_model.json'))
    def replace_model_key(payload,new_key):
        outputs=payload['prior']['outputs_sha256'];digest=outputs.pop('independent_copy_model.json');outputs[new_key]=digest
    damaged_model_acceptance('copy_model_output_absolute',lambda p:replace_model_key(p,str(model_gate_base/'independent_copy_model.json')))
    damaged_model_acceptance('copy_model_output_traversal',lambda p:replace_model_key(p,'../independent_copy_model.json'))
    damaged_model_acceptance('copy_model_output_outside_base',lambda p:replace_model_key(p,'acceleration/independent_copy_model.json'))
    damaged_model_acceptance('copy_model_output_alias',lambda p:p['prior']['outputs_sha256'].__setitem__(accepted_model['path'],'2'*64))
    damaged_model_acceptance('copy_model_checked_path_bool',lambda p:p['checked'].__setitem__('path',True))
    damaged_model_acceptance('copy_model_checked_outside_base',lambda p:p['checked'].__setitem__('path','acceleration/independent_copy_model.json'))
    damaged_model_acceptance('copy_model_checked_hash_bool',lambda p:p['checked'].__setitem__('sha256',True))
    damaged_model_acceptance('copy_model_summary_reference_shape',lambda p:p['summary_ref'].__setitem__('unexpected',0))
    calibration_outputs={'fixture_%03d.json'%i:'1'*64 for i in range(OWN_COUNTS['total']+14)}
    run('positive_current_calibration_output_population','PASS',calibration_outputs,
        lambda:output_population('calibrate',calibration_outputs))
    full_outputs={'fixture_%03d.json'%i:'1'*64 for i in range(11)}
    run('positive_current_full_output_population','PASS',full_outputs,
        lambda:output_population('full',full_outputs))
    stale_outputs={'fixture_%03d.json'%i:'1'*64 for i in range(90)}
    run('stale_v4_calibration_output_population','CHECKER_OUTPUT_POPULATION',stale_outputs,
        lambda:output_population('calibrate',stale_outputs))
    return rows


def calibrate(out,budget,software):
    rows=own_routes(out,budget,software);positive=sum(row['expected_stage']=='PASS' for row in rows)
    need(len(rows)==OWN_COUNTS['total'] and positive==OWN_COUNTS['positive'],'OWN_POPULATION');write(out/'controls.json',rows,budget)
    need(all(row['matches'] for row in rows),'OWN_STAGE_MISMATCH')
    return {'counts':OWN_COUNTS,'all_precise_stages_match':True,'original_author_counterparts':29,
      'new_positive_controls':OWN_COUNTS['positive']-AUTHOR_COUNTS['positive'],
      'new_negative_controls':OWN_COUNTS['negative']-AUTHOR_COUNTS['negative'],'disk_pipeline_fixtures':2,
      'late_fixture_groups':104,'late_fixture_checkpoints':[100,104],
      'actual_profile_read':False,'actual_model_read':False,'actual_encoding_read':False,'solver_calls':0}


def controls_header(raw,software):
    need(type(raw) is dict and raw.get('status')==CONTROLS_STATUS and type(raw.get('implementation_version')) is int and
         raw['implementation_version']==1 and type(raw.get('code_version')) is int and raw['code_version']==CODE_VERSION and
         raw.get('producer')=='/root/structural' and raw.get('verifier')=='/root/native_driver' and
         raw.get('method')=='independent_artifact_check' and raw.get('target_resolution')=='NONE','CONTROLS_HEADER')
    pins=raw.get('inputs_sha256');need(type(pins) is dict and all(pins.get(k)==v for k,v in software.items()),'CONTROLS_SOURCE')
    need(type(raw.get('outcome')) is dict and typed_equal(raw['outcome'].get('counts'),AUTHOR_COUNTS) and
         raw['outcome'].get('all_precise_stages_match') is True,'CONTROLS_SCOPE')


def copy_gate_source(raw):
    native_source='acceleration/audit_20261004_fixed17_per_copy_adjacency_v1.py'
    native_spec='acceleration/audit_20261004_fixed17_per_copy_adjacency_v1_spec.md'
    need(type(raw) is dict,'COPY_GATE_SOURCE')
    sources=raw.get('source_software');inputs=raw.get('inputs_sha256')
    need(type(sources) is dict and type(inputs) is dict,'COPY_GATE_SOURCE')
    expected={name:PINS[name] for name in (native_source,native_spec)}
    for name,digest in expected.items():
        need(type(sources.get(name)) is str and sources[name]==digest and
             type(inputs.get(name)) is str and inputs[name]==digest,'COPY_GATE_SOURCE')
    return {'source_software':dict(expected),'inputs_sha256':dict(expected)}


def accepted_copy_model_ref(prior,checked,summary_ref):
    stage='ROOT_MODEL_ACCEPTANCE'
    need(type(summary_ref) is dict and summary_ref.keys()=={'path','sha256'} and
         type(summary_ref['path']) is str and type(summary_ref['sha256']) is str and
         re.fullmatch('[0-9a-f]{64}',summary_ref['sha256']) is not None,stage)
    summary_name=summary_ref['path'];summary_path=Path(summary_name)
    need(not summary_path.is_absolute() and '\\' not in summary_name and
         '..' not in summary_path.parts and summary_name==summary_path.as_posix(),stage)
    summary_path=safe(summary_name,False);base=summary_path.parent
    need(summary_path.name=='summary.json' and summary_name==key(summary_path),stage)
    need(type(checked) is dict and type(checked.get('path')) is str and
         type(checked.get('sha256')) is str and re.fullmatch('[0-9a-f]{64}',checked['sha256']) is not None,stage)
    checked_name=checked['path'];checked_path=Path(checked_name)
    need(not checked_path.is_absolute() and '\\' not in checked_name and
         '..' not in checked_path.parts and checked_name==checked_path.as_posix(),stage)
    checked_path=safe(checked_name,False)
    need(checked_name==key(checked_path) and checked_path.parent==base and
         checked_path.name=='independent_copy_model.json',stage)
    outputs=prior.get('outputs_sha256') if type(prior) is dict else None
    need(type(outputs) is dict,stage);normalized={}
    for name,digest in outputs.items():
        need(type(name) is str and name and type(digest) is str and
             re.fullmatch('[0-9a-f]{64}',digest) is not None,stage)
        path=Path(name)
        need(not path.is_absolute() and '\\' not in name and '..' not in path.parts and
             name==path.as_posix(),stage)
        if len(path.parts)==1:
            path=safe(str(base/path),False)
        else:
            path=safe(name,False);need(name==key(path),stage)
        need(path.parent==base and path.name!='summary.json',stage)
        canonical=key(path);need(canonical not in normalized,stage);normalized[canonical]=digest
    need(normalized.get(checked_name)==checked['sha256'],stage)
    return {'path':checked_name,'sha256':checked['sha256']}


def configuration(reader,args,options,software):
    config_path=options['--configuration'];config_hash=options['--configuration-sha256']
    config=reader.read(config_path,config_hash)
    fields={'schema','source','specification','input_profile','copy_model','per_copy_gate','root_acceptance',
            'author_calibration','independent_encoding_controls','root_authority','scope'}
    need(type(config) is dict and config.keys()==fields and config['schema']=='FIXED17_PER_COPY_LOCAL_SAT_CONFIGURATION_V1' and
         config['scope']=='FIXED17_82_COPY_LOCAL_ROWS_ONLY','CONFIGURATION')
    need(typed_equal(config['source'],{'path':PRODUCER,'sha256':PINS[PRODUCER]}) and
         typed_equal(config['specification'],{'path':PRODUCER_SPEC,'sha256':PINS[PRODUCER_SPEC]}),'CONFIGURATION_SOURCE')
    need(typed_equal(config['independent_encoding_controls'],{'path':key(safe(args.producer_controls)),
         'sha256':args.producer_controls_sha256}),'CONFIGURATION_CONTROLS')
    declared={k:PINS[k] for k in AUTHOR_SOFTWARE_KEYS};declared[key(safe(config_path))]=config_hash
    for name in fields-{'schema','scope','source','specification'}:
        ref=config[name];need(type(ref) is dict and ref.keys()=={'path','sha256'},'CONFIGURATION_REFERENCES')
        need(ref['path'] not in declared or declared[ref['path']]==ref['sha256'],'INPUT_ALIAS');declared[ref['path']]=ref['sha256']
    raw=reader.ref(config['input_profile']);submitted=reader.ref(config['copy_model']);model=validate_model(raw,submitted,reader.budget)
    scientific_scope(raw,model,reader.budget)
    prior=reader.ref(config['per_copy_gate']);copy_gate(prior,model,[config['input_profile'],config['copy_model']])
    copy_gate_source(prior)
    root=reader.ref(config['root_acceptance'])
    need(type(root) is dict and root.get('schema')=='ROOT_PER_COPY_ADJACENCY_INDEPENDENT_FULL_ACTUAL_ACCEPTANCE_V1' and
         root.get('result')=='PASS' and typed_equal(root.get('summary'),config['per_copy_gate']) and
         root.get('count_witness_excluded') is False and root.get('graph_object_approved') is False,'ROOT_MODEL_ACCEPTANCE')
    checked=root.get('exact_checked_model');need(type(checked) is dict and checked.get('variables')==3321 and
         checked.get('rows')==1476 and checked.get('copies')==82 and checked.get('checkpoints')==9,'ROOT_MODEL_ACCEPTANCE')
    checked_ref=accepted_copy_model_ref(prior,checked,config['per_copy_gate'])
    need(typed_equal(reader.ref(checked_ref),model),'ACCEPTED_NATIVE_MODEL_IDENTITY')
    controls,cbase=packet(reader,args.producer_controls,args.producer_controls_sha256);controls_header(controls,software)
    need(controls['inputs_sha256'].get(key(safe(args.calibration)))==args.calibration_sha256,'CONTROLS_CALIBRATION_IDENTITY')
    author,abase=packet(reader,config['author_calibration']['path'],config['author_calibration']['sha256'])
    need(controls['inputs_sha256'].get(config['author_calibration']['path'])==config['author_calibration']['sha256'],'CONTROLS_AUTHOR_IDENTITY')
    reader.ref(config['root_authority'])
    return raw,model,author,abase,declared


def full(reader,args,summary,base,options,out,software):
    need(args.producer_controls is not None and args.producer_controls_sha256 is not None,'CONTROLS_ARGUMENTS')
    raw,model,author,abase,declared=configuration(reader,args,options,software)
    need(typed_equal(summary['inputs_sha256'],declared),'SCIENTIFIC_INPUT_MAP')
    author_scope=replay_controls(reader,author,abase,out)
    names={'parsed_profile.json','encoding_model.json','groups.jsonl','clauses.body','local.cnf'}
    names.update('checkpoint_%04d.json'%n for n in (*range(100,1401,100),1476))
    need({key(base/name) for name in names}==set(summary['outputs_sha256']) and len(names)==20,'BUILD_OUTPUT_POPULATION')
    parsed=reader.read(base/'parsed_profile.json',summary['outputs_sha256'][key(base/'parsed_profile.json')])
    need(typed_equal(parsed,raw),'PROFILE_IDENTITY')
    def load(name):return reader.read(base/name,summary['outputs_sha256'][key(base/name)])
    journal=out/'independent_groups.jsonl';need(not journal.exists(),'OUTPUT_EXISTS')
    with journal.open('xb') as saved:
        encoded,receipt=verify_pipeline(model,reader.budget,load,lambda name:(base/name).open('rb'),saved)
        reader.budget.tick();saved.flush();os.fsync(saved.fileno());reader.budget.tick()
    expected={'base_variables':3321,'variables':encoded['variables'],'clauses':encoded['clauses'],
      'total_groups':1476,'degree_groups':82,'support_groups':1394,'checkpoints':15,'fixed_units':encoded['fixed_units'],
      'solver_calls':0,'independent_encoding_complete_check_performed':False,'graph_object_approved':False,
      'count_witness_excluded':False,'target_resolution':'NONE','prerequisite_complete_model_scope_inherited':True,
      'prerequisite_bulk_closure_rehashed':False}
    need(summary.get('status')==BUILD_STATUS and typed_equal(summary.get('outcome'),expected),'BUILD_OUTCOME')
    formula=base/'local.cnf';receipt['exact_formula_sha256']=summary['outputs_sha256'][key(formula)]
    receipt['exact_formula_bytes']=formula.stat().st_size
    write(out/'independent_encoding_model.json',encoded,reader.budget)
    write(out/'independent_stream_receipt.json',receipt,reader.budget)
    return {'author_control_scope':author_scope,'counts':AUTHOR_COUNTS,'all_precise_stages_match':True,
       'base_variables':3321,'variables':encoded['variables'],'clauses':encoded['clauses'],'complete_groups':1476,
       'complete_degree_groups':82,'complete_support_groups':1394,'complete_checkpoints':15,
       'fixed_units':encoded['fixed_units'],'exact_formula_sha256':receipt['exact_formula_sha256'],
       'exact_eof':True,'all_auxiliary_clauses_checked':True,'all_checkpoint_prefixes_checked':True,
       'shared_native_model_component':'777838556a4b74e86e329220440fe146c167d097b3228b49277fb39faeaa43f8',
       'shared_native_prefix_component':'dfb9cd49f44c39c93bfd73e4c73fe3b1d36709e2e10fe5fabaa49b9bab8bef0e',
       'discovery_encoder_imported':False,'discovery_AST_executed':False,'prerequisite_model_scope_inherited':True,
       'prerequisite_ancestor_bulk_replayed':False,'own95_actions_rerun':False,'author29_actions_rerun':True,
       'outside_pair_CN_equations_included':False,'equitable_profile_assumed':False,'graph_object_approved':False,
       'count_witness_excluded':False,'SAT_or_UNSAT_result':None,'solver_calls':0}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('calibrate','controls','full'))
    parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',required=True)
    parser.add_argument('--self-sha256',required=True);parser.add_argument('--spec-sha256',required=True)
    for name in ('calibration','producer-plan','producer-summary','producer-manifest','producer-terminal','producer-controls'):
        parser.add_argument('--'+name);parser.add_argument('--'+name+'-sha256')
    args=parser.parse_args();budget=Budget(args.seconds);reader=Reader(budget)
    out=safe(args.out,False);need(out.is_relative_to(ROOT/'acceleration/results') and not out.exists(),'OUTPUT_ROOT');out.mkdir(parents=True)
    try:
        software={**PINS,SELF:args.self_sha256,SPEC:args.spec_sha256};reader.map(software)
        if args.mode=='calibrate':
            need(all(getattr(args,name) is None and getattr(args,name+'_sha256') is None for name in
                ('calibration','producer_plan','producer_summary','producer_manifest','producer_terminal','producer_controls')),'CALIBRATION_ARGUMENTS')
            outcome=calibrate(out,budget,software);status=CAL_STATUS
        else:
            qualification(reader,args,software)
            summary,base,options=source_packet(reader,args,'calibrate' if args.mode=='controls' else 'build')
            if args.mode=='controls':outcome=replay_controls(reader,summary,base,out);status=CONTROLS_STATUS
            else:outcome=full(reader,args,summary,base,options,out,software);status=FULL_STATUS
        reader.close();outputs={name:reader.digest(safe(name),BODY_LIMIT+1024 if name.endswith(('.cnf','.body','.jsonl')) else JSON_LIMIT)
                               for name in inventory(out,budget)}
        output_population(args.mode,outputs)
        report={'status':status,'implementation_version':1,'code_version':CODE_VERSION,'producer':'/root/structural','verifier':'/root/native_driver',
          'checking_implementation_author':'/root/native_driver','actual_executor':'See genuine external supported supervisor receipt',
          'method':'independent_artifact_check','timestamp':datetime.now(timezone.utc).isoformat(),'mode':args.mode,
          'source_sha256':args.self_sha256,'specification_sha256':args.spec_sha256,'inputs_sha256':reader.inputs,
          'outputs_sha256':outputs,'outcome':outcome,'elapsed_seconds':budget.deadline.status()['elapsed_seconds'],
          'target_resolution':'NONE','own_actions_rerun':OWN_COUNTS['total'] if args.mode=='calibrate' else 0,
          'limitations':['Applicable mathematical premises are inherited directly; no old Gram or solver closure is regenerated.',
           'Only exact local1476 equations and pair bounds are encoded. No outside CN or graph/SAT/UNSAT outcome follows.',
           '20save is allocated guard intent; clean genuine supported containment governs actual completion.']}
        write(out/'summary.json',report,budget);reader.close();budget.tick();return 0
    except BaseException as exc:
        try:write(out/'failure.json',{'status':'FAILED_OR_NOT_COMPLETED','stage':str(exc) if isinstance(exc,Veto) else None,
          'error':repr(exc),'inputs_sha256':reader.inputs,'elapsed_seconds':budget.deadline.status()['elapsed_seconds'],
          'target_resolution':'NONE','automatic_retry':False},budget,True)
        except BaseException:pass
        raise


if __name__=='__main__':sys.exit(main())
