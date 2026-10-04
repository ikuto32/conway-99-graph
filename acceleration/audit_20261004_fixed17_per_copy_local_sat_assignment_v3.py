"""SOURCE ONLY: distinct complete local-SAT assignment checker.
No discovery encoder import/AST/backend is used to validate a saved assignment.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
SELF='acceleration/audit_20261004_fixed17_per_copy_local_sat_assignment_v3.py'
SPEC='acceleration/audit_20261004_fixed17_per_copy_local_sat_assignment_v3_spec.md'
MODEL_SCHEMA='FIXED17_COPY_ADJACENCY_MODEL_V1'
CAL_STATUS='INDEPENDENT_FIXED17_PER_COPY_LOCAL_SAT_ASSIGNMENT_V1_CALIBRATION_PASS'
FULL_STATUS='INDEPENDENT_FIXED17_PER_COPY_LOCAL_SAT_ASSIGNMENT_V1_COMPLETE_PASS'
ENCODING_STATUS='INDEPENDENT_FIXED17_PER_COPY_LOCAL_SAT_V1_COMPLETE_PASS'
SUP_SHA='46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17'
JSON_LIMIT=64*1024*1024
BODY_LIMIT=256*1024*1024
PINS={
 'acceleration/audit_20261004_fixed17_per_copy_adjacency_v1.py':'777838556a4b74e86e329220440fe146c167d097b3228b49277fb39faeaa43f8',
 'acceleration/audit_20261004_fixed17_per_copy_adjacency_v1_spec.md':'5cffa344f73694333d66202f0362cb352576d1821eae5d484c04cc22791b852f',
 'acceleration/audit_20261004_fixed17_per_copy_local_sat_v6.py':'53d2fc562d50d847a33b05b065013b534c4e1ceba9a0772451db73eccc00bf1c',
 'acceleration/audit_20261004_fixed17_per_copy_local_sat_v6_spec.md':'4d1aadd130ce1924fa9eb338577eace210460e36cb3e07faeda9bfcb956625ae',
 'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command_v2.py':SUP_SHA,
 'acceleration/run_20261004_fixed17_per_copy_local_sat_native_v1.sh':'5d4b351e91997fda5fdc9d0767a08fa6a47d5b7d6def35ad288c581cf3d6ffb1',
 'acceleration/run_20261004_fixed17_per_copy_local_sat_native_v1_spec.md':'dbc7335c17902b524cf86e8b3674bdb6df560bfdf63673367fd9cdef8a5cab8d',
 'build/research-cadical195/source/build/cadical':'021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}

class Veto(ValueError):
    pass

def need(ok,stage):
    if not ok:raise Veto(stage)

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



class Budget:
    def __init__(self,seconds):
        self.deadline=CommandDeadline(seconds,allocation_reason='Distinct complete SAT assignment/all clauses/local rows/graph diagnosis; all hashes and closing share this invocation.')
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

def parse_assignment(stream,variables,budget):
    need(type(variables) is int and 0<variables<=150000,'ASSIGNMENT_DOMAIN')
    values=[None]*(variables+1);seen=0;status_seen=False;terminated=False;total_bytes=0
    for line in stream:
        budget.tick();total_bytes+=len(line)
        need(type(line) is bytes and len(line)<=1024*1024 and total_bytes<=JSON_LIMIT,'SAT_LOG_SIZE')
        need(line.endswith(b'\n') and b'\r' not in line,'SAT_LOG_FORMAT')
        if line==b'\n' or line.startswith(b'c '):continue
        if line.startswith(b's '):
            need(line==b's SATISFIABLE\n' and not status_seen and seen==0 and not terminated,'SAT_STATUS')
            status_seen=True;continue
        if not status_seen and not line.startswith(b'v '):
            # The pinned Bash caller prints versions/checksum results before CaDiCaL.
            # Such lines are never accepted as a status or assignment coordinate.
            continue
        need(line.startswith(b'v ') and status_seen and not terminated,'SAT_MODEL_LINE')
        tokens=line[2:-1].split(b' ')
        need(tokens and all(tokens),'SAT_MODEL_TOKEN')
        for position,token in enumerate(tokens):
            if token==b'0':
                need(position==len(tokens)-1,'SAT_MODEL_TERMINATOR')
                terminated=True;continue
            need(re.fullmatch(rb'-?[1-9][0-9]*',token) is not None,'SAT_MODEL_TOKEN')
            literal=int(token);variable=abs(literal)
            need(variable<=variables,'SAT_MODEL_ID')
            need(values[variable] is None,'SAT_MODEL_DUPLICATE')
            values[variable]=int(literal>0);seen+=1
    need(status_seen,'SAT_STATUS')
    need(terminated,'SAT_MODEL_TERMINATOR')
    need(seen==variables and all(type(value) is int and value in (0,1) for value in values[1:]),'SAT_MODEL_COMPLETE')
    return values[1:]


def check_formula(stream,values,variables,clauses,budget):
    need(type(variables) is int and type(clauses) is int and 0<variables<=150000 and 0<=clauses<=600000,'FORMULA_COUNTS')
    need(type(values) is list and len(values)==variables and all(type(v) is int and v in (0,1) for v in values),'ASSIGNMENT_VALUES')
    header=stream.readline(1025)
    need(header==f'p cnf {variables} {clauses}\n'.encode('ascii'),'DIMACS_HEADER')
    total_bytes=len(header);digest=hashlib.sha256();digest.update(header)
    for ordinal in range(clauses):
        budget.tick();line=stream.readline(1024*1024+1);total_bytes+=len(line)
        need(len(line)<=1024*1024 and total_bytes<=BODY_LIMIT,'FORMULA_SIZE')
        need(re.fullmatch(rb'(?:-?[1-9][0-9]* )*0\n',line) is not None,'CLAUSE_FORMAT')
        literals=[int(token) for token in line[:-2].split()];digest.update(line)
        need(all(0<abs(lit)<=variables for lit in literals),'CLAUSE_VARIABLE')
        need(any(values[abs(lit)-1]==int(lit>0) for lit in literals),'CLAUSE_FALSE')
    need(not stream.read(1),'FORMULA_EOF')
    return {'variables':variables,'complete_clauses_checked':clauses,'formula_bytes':total_bytes,
            'formula_sha256':digest.hexdigest(),'every_clause_satisfied':True,'exact_eof':True}


def assignment_model(raw,submitted,budget):
    geometry,abstract=abstract_model(raw,budget);expected=wire_model(raw,budget)
    need(typed_equal(submitted,expected),'MODEL_RECONSTRUCTION')
    return geometry,abstract


def expected_encoding_map(model,variables,clauses):
    need(type(variables) is int and type(clauses) is int and variables>=model['variables'] and clauses>=0,'ENCODING_COUNTS')
    cursor=1;mapping=[]
    for v,pair in enumerate(model['variable_pairs']):
        fixed=model['lower'][v]==model['upper'][v]
        mapping.append({'variable_index':v,'sat_id':v+1,'copy_pair':list(pair),
          'lower':model['lower'][v],'upper':model['upper'][v],'first_clause':cursor,'clause_count':int(fixed)})
        cursor+=int(fixed)
    degree_rows=[i for i,row in enumerate(model['rows']) if row['kind']=='degree']
    support_rows=[i for i,row in enumerate(model['rows']) if row['kind']=='support_incidence']
    return {'schema':'FIXED17_PER_COPY_LOCAL_SAT_ENCODING_MODEL_V1','source_model':model,
      'variable_map':mapping,'group_order_model_rows':degree_rows+support_rows,
      'groups_file':'groups.jsonl','clauses_file':'clauses.body','dimacs_file':'local.cnf',
      'total_groups':len(model['rows']),'degree_groups':model['outside_copies'],
      'support_groups':model['outside_copies']*model['support_order'],'base_variables':model['variables'],
      'variables':variables,'clauses':clauses,'fixed_units':cursor-1,
      'impossible_rows_possible_and_retained':True,'outside_pair_CN_equations_included':False,
      'no_equitable_profile_assumed':True}


def encoding_map(model,submitted,variables,clauses):
    need(typed_equal(submitted,expected_encoding_map(model,variables,clauses)),'ENCODING_MAP')


def local_assignment(raw,submitted,values,budget):
    geometry,model=assignment_model(raw,submitted,budget)
    need(type(values) is list and len(values)>=len(model['variable_pairs']) and
         all(type(value) is int and value in (0,1) for value in values),'ASSIGNMENT_VALUES')
    base=values[:len(model['variable_pairs'])]
    need(all(a<=v<=b for a,v,b in zip(model['lower'],base,model['upper'])),'LOCAL_BOUND')
    row_checks=[]
    for index,row in enumerate(model['rows']):
        budget.tick();lhs=sum(base[v] for v,coefficient in row['terms'])
        need(lhs==row['rhs'],'LOCAL_ROW')
        row_checks.append({'index':index,'copy':row['copy'],'coordinate':row['coordinate'],
                           'lhs':lhs,'rhs':row['rhs'],'holds':True})
    n,support=geometry['n'],geometry['support'];matrix=[[0]*n for _ in range(n)]
    for u in range(support):
        for v in range(support):matrix[u][v]=geometry['h'][u][v]
    for x,members in enumerate(geometry['types']):
        for u in members:matrix[u][support+x]=matrix[support+x][u]=1
    for (x,y),value in zip(model['variable_pairs'],base):
        matrix[support+x][support+y]=matrix[support+y][support+x]=value
    diagnostic=whole_srg_diagnostic(matrix,geometry['k'],budget)
    return {'copy_labels':geometry['labels'],'variable_pairs':model['variable_pairs'],'edge_values':base,
      'complete_local_rows_checked':len(row_checks),'row_checks':row_checks,
      'adjacency':matrix,'full_graph_diagnostic':diagnostic,
      'local_witness_validated':True,'graph_object_approved':False}


def native_runtime(plan,manifest,terminal,formula_path):
    need(type(plan) is dict and type(plan.get('command')) is list and
         typed_equal(plan.get('supervisor_argv'),plan['command']) and type(plan.get('child_argv')) is list,'NATIVE_PLAN')
    command,child=plan['command'],plan['child_argv']
    need(all(type(word) is str for word in command+child) and len(child)==6 and
         child[:2]==['/usr/bin/bash','acceleration/run_20261004_fixed17_per_copy_local_sat_native_v1.sh'] and
         child[2]==formula_path and re.fullmatch('[0-9]+',child[5]) is not None and
         child[5] in ('10','1800') and command[-6:]==child,'NATIVE_PLAN')
    prefix=command[:-6]
    need(prefix[:3]==['/usr/bin/python3','-B','acceleration/run_compute_command_v2.py'] and
         prefix[-1]=='--','NATIVE_PLAN')
    flags={};words=prefix[3:-1]
    need(len(words)%2==0,'NATIVE_PLAN')
    for name,value in zip(words[::2],words[1::2]):
        need(name.startswith('--') and name not in flags,'NATIVE_PLAN');flags[name]=value
    common={'--seconds','--shutdown-reserve-seconds','--allocation-reason','--success-criterion',
         '--verification-criterion','--out'}
    if child[5]=='1800':
        need(len(command)==24 and flags.keys()==common|{'--review-json'} and flags['--review-json'],'NATIVE_PLAN')
    else:need(len(command)==22 and flags.keys()==common,'NATIVE_PLAN')
    try:outer=float(flags['--seconds']);shutdown=float(flags['--shutdown-reserve-seconds'])
    except ValueError:raise Veto('NATIVE_PLAN')
    need(math.isfinite(outer) and math.isfinite(shutdown) and 0<shutdown<outer<=21600,'NATIVE_PLAN')
    need(type(manifest) is dict and manifest.get('source_sha256')==SUP_SHA and
         manifest.get('runtime_scope')=='LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2' and
         typed_equal(manifest.get('command'),child) and
         manifest.get('cwd')=='/mnt/c/Users/ikuto/projects/conway-99-graph' and
         typed_equal(manifest.get('seconds'),outer) and typed_equal(manifest.get('shutdown_reserve_seconds'),shutdown) and
         manifest.get('automatic_retry') is False and manifest.get('cumulative_across_commands') is False,'NATIVE_MANIFEST')
    need(type(terminal) is dict and type(terminal.get('invocation_id')) is str and terminal['invocation_id'] and
         terminal['invocation_id']==manifest.get('invocation_id') and terminal.get('stop_reason')=='COMMAND_EXITED' and
         type(terminal.get('command_exit_code')) is int and terminal['command_exit_code']==10 and
         terminal.get('error') is None and terminal.get('deadline_reached') is False and
         terminal.get('hard_limit_observed') is True,'NATIVE_TERMINAL')
    cleanup=terminal.get('cleanup')
    need(type(cleanup) is dict and cleanup.get('reaped') is True and cleanup.get('job_active_zero_observed') is True and
         type(cleanup.get('actual_exit_code')) is int and cleanup['actual_exit_code']==10 and
         cleanup.get('cleanup_errors')==[] and cleanup.get('process_group_live_pids')==[],'NATIVE_CLEANUP')
    observations=cleanup.get('cleanup_observations')
    need(type(observations) is list and observations and all(type(row) is dict and
         type(row.get('original_group')) is int and row['original_group']>0 and
         type(row.get('live_pids')) is list and type(row.get('unreadable_pids')) is list for row in observations) and
         len({row['original_group'] for row in observations})==1 and
         observations[-1]['live_pids']==[] and observations[-1]['unreadable_pids']==[],'NATIVE_GROUP')
    elapsed=terminal.get('elapsed_seconds')
    need(type(elapsed) in (int,float) and math.isfinite(elapsed) and 0<=elapsed<=outer,'NATIVE_ELAPSED')
    return {'native_exit':10,'literal_supervisor_status':terminal.get('status'),
      'original_group':observations[-1]['original_group'],'clean_group_observed':True,
      'elapsed_seconds':elapsed,'formula_path':formula_path,'native_seconds':int(child[5]),
      'out':flags['--out'],'review_path':flags.get('--review-json'),
      'timely_review_policy_inherited_from_root_runtime_acceptance':True}


def repo_key(name):
    need(type(name) is str and name,'RECEIPT_PATH')
    text=name.replace('\\','/');linux='/mnt/c/Users/ikuto/projects/conway-99-graph/'
    if text.startswith(linux):text=text[len(linux):]
    elif text.startswith(ROOT.as_posix()+'/'):text=text[len(ROOT.as_posix())+1:]
    need(not Path(text).is_absolute() and all(part not in ('','.', '..') for part in text.split('/')),'RECEIPT_PATH')
    return key(safe(text,False))


def packet(reader,ref):
    raw=reader.ref(ref);need(type(raw) is dict and type(raw.get('outputs_sha256')) is dict,'PACKET_HEADER')
    base=safe(ref['path']).parent;outputs=raw['outputs_sha256']
    need(all(safe(name).is_relative_to(base) and safe(name)!=base/'summary.json' for name in outputs),'PACKET_NAME')
    need(set(inventory(base,reader.budget,('summary.json',)))==set(outputs),'PACKET_POPULATION')
    reader.map(outputs)
    return raw,base


def encoding_gate(raw,model,profile_ref,model_ref,formula_ref,map_ref,scientific=True):
    need(type(raw) is dict and raw.get('status')==ENCODING_STATUS and
         type(raw.get('implementation_version')) is int and raw['implementation_version']==1 and
         type(raw.get('code_version')) is int and raw['code_version']==6 and
         raw.get('producer')=='/root/structural' and raw.get('verifier')=='/root/native_driver' and
         raw.get('method')=='independent_artifact_check' and raw.get('target_resolution')=='NONE','ENCODING_GATE_HEADER')
    checker='acceleration/audit_20261004_fixed17_per_copy_local_sat_v6.py'
    spec='acceleration/audit_20261004_fixed17_per_copy_local_sat_v6_spec.md'
    pins=raw.get('inputs_sha256');outputs=raw.get('outputs_sha256')
    need(type(pins) is dict and pins.get(checker)==PINS[checker] and pins.get(spec)==PINS[spec] and
         raw.get('source_sha256')==PINS[checker] and raw.get('specification_sha256')==PINS[spec],'ENCODING_GATE_SOURCE')
    need(type(outputs) is dict and all(pins.get(ref['path'])==ref['sha256'] for ref in
         (profile_ref,model_ref,formula_ref)) and outputs.get(map_ref['path'])==map_ref['sha256'],'ENCODING_GATE_DIRECT_PINS')
    scope=raw.get('outcome');rows=model['rows'];size=model['outside_copies'];support=model['support_order']
    need(type(scope) is dict and all(type(scope.get(name)) is int and scope[name]==value for name,value in
         (('base_variables',model['variables']),('complete_groups',len(rows)),('complete_degree_groups',size),
          ('complete_support_groups',size*support),('complete_checkpoints',len(range(100,len(rows),100))+1))) and
         type(scope.get('variables')) is int and model['variables']<=scope['variables']<=150000 and
         type(scope.get('clauses')) is int and 0<=scope['clauses']<=600000 and
         scope.get('exact_formula_sha256')==formula_ref['sha256'] and scope.get('exact_eof') is True and
         scope.get('all_auxiliary_clauses_checked') is True and scope.get('outside_pair_CN_equations_included') is False and
         scope.get('all_checkpoint_prefixes_checked') is True and scope.get('graph_object_approved') is False,'ENCODING_GATE_SCOPE')
    if scientific:
        need(model['target_order']==99 and model['target_degree']==14 and size==82 and support==17 and
             model['variables']==3321 and len(rows)==1476 and scope['variables']==110371 and
             scope['clauses']==409777,'SCIENTIFIC_ENCODING_SCOPE')
    return {'variables':scope['variables'],'clauses':scope['clauses'],'base_variables':model['variables'],
      'complete_groups':len(rows),'complete_formula_correspondence_inherited':True,
      'encoding_ancestor_actions_or_bulk_replayed':False}


def encoding_acceptance(raw,ref):
    need(type(raw) is dict and raw.get('result')=='PASS' and
         (typed_equal(raw.get('summary'),ref) or
          raw.get('full_report_path')==ref['path'] and raw.get('full_report_sha256')==ref['sha256']),
         'ENCODING_ROOT_ACCEPTANCE')


def native_acceptance(raw,refs,review_absent=False):
    need(type(raw) is dict and raw.get('result') in ('PASS','PASS_RUNTIME_IDENTITY_ONLY'),'NATIVE_ROOT_ACCEPTANCE')
    pins=raw.get('fresh_inputs_sha256',raw.get('inputs_sha256'))
    need(type(pins) is dict and all(pins.get(ref['path'])==ref['sha256'] for ref in refs),'NATIVE_ROOT_DIRECT_PINS')
    if review_absent:
        need(raw.get('native_review_required') is False and type(raw.get('native_review_not_needed_reason')) is str and
             raw['native_review_not_needed_reason'].strip(),'NATIVE_ROOT_REVIEW_ABSENCE')


def native_material(plan,formula_ref,stdout_ref,checksum_ref,review_ref,manifest_path,terminal_path):
    need(typed_equal(plan.get('formula'),formula_ref) or plan.get('formula_path')==formula_ref['path'] and
         plan.get('formula_sha256')==formula_ref['sha256'],'NATIVE_PLAN_MATERIAL')
    declared=plan.get('stdout')
    need(type(declared) is dict and declared.keys()=={'path','sha256'} and declared['path']==stdout_ref['path'] and
         declared['sha256'] in (None,stdout_ref['sha256']) or
         plan.get('stdout_path')==stdout_ref['path'] and 'stdout_sha256' in plan and
         plan['stdout_sha256'] in (None,stdout_ref['sha256']),'NATIVE_PLAN_MATERIAL')
    child=plan['child_argv'];prefix=plan['command'][:-6];words=prefix[3:-1]
    flags=dict(zip(words[::2],words[1::2]));out=repo_key(flags['--out'])
    review_path=repo_key(flags['--review-json'])
    need(repo_key(child[4])==checksum_ref['path'] and (review_ref is None or review_path==review_ref['path']) and
         stdout_ref['path']==out+'/stdout.log' and repo_key(manifest_path)==out+'/manifest.json' and
         repo_key(terminal_path)==out+'/summary.json','NATIVE_RECEIPT_LOCATION')


def checksum_bytes(formula_ref):
    caller='acceleration/run_20261004_fixed17_per_copy_local_sat_native_v1.sh'
    solver='build/research-cadical195/source/build/cadical'
    return ''.join(digest+'  '+name+'\n' for name,digest in
      ((formula_ref['path'],formula_ref['sha256']),(caller,PINS[caller]),(solver,PINS[solver]))).encode('ascii')


def checksum_list(data,formula_ref):
    need(type(data) is bytes and data==checksum_bytes(formula_ref),'NATIVE_CHECKSUM_LIST')
    return {'formula':formula_ref,'caller_sha256':PINS['acceleration/run_20261004_fixed17_per_copy_local_sat_native_v1.sh'],
      'solver_sha256':PINS['build/research-cadical195/source/build/cadical'],'exact_three_checksum_lines':True}


def synthetic_runtime(scientific=False):
    child=['/usr/bin/bash','acceleration/run_20261004_fixed17_per_copy_local_sat_native_v1.sh',
      'fixture/local.cnf','fixture/proof.drat','fixture/sha256.txt','1800' if scientific else '10']
    prefix=['/usr/bin/python3','-B','acceleration/run_compute_command_v2.py',
      '--seconds','1900' if scientific else '60','--shutdown-reserve-seconds','20',
      '--allocation-reason','Finite actual-shaped runtime control','--success-criterion','native10',
      '--verification-criterion','complete assignment','--out','fixture/native']
    if scientific:prefix+=['--review-json','fixture/review.json']
    command=prefix+['--']+child
    plan={'command':command,'supervisor_argv':list(command),'child_argv':child,
      'formula':{'path':'fixture/local.cnf','sha256':'1'*64},
      'stdout':{'path':'fixture/native/stdout.log','sha256':None if scientific else '2'*64}}
    manifest={'schema_version':1,'source_sha256':SUP_SHA,'runtime_scope':'LOCAL_LINUX_GROUP_BOUNDED_CLEANUP_V2',
      'invocation_id':'synthetic-only','command':child,'cwd':'/mnt/c/Users/ikuto/projects/conway-99-graph',
      'seconds':1900.0 if scientific else 60.0,'shutdown_reserve_seconds':20.0,
      'automatic_retry':False,'cumulative_across_commands':False}
    terminal={'invocation_id':'synthetic-only','status':'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET',
      'stop_reason':'COMMAND_EXITED','command_exit_code':10,'error':None,'deadline_reached':False,
      'hard_limit_observed':True,'elapsed_seconds':0.1,'cleanup':{'reaped':True,'job_active_zero_observed':True,
      'actual_exit_code':10,'cleanup_errors':[],'process_group_live_pids':[],
      'cleanup_observations':[{'original_group':123,'live_pids':[],'unreadable_pids':[]}]}}
    return {'plan':plan,'manifest':manifest,'terminal':terminal}


def synthetic_encoding(model):
    refs={name:{'path':'fixture/'+file,'sha256':digest*64} for name,file,digest in
      (('profile','profile.json','1'),('model','model.json','2'),('formula','local.cnf','3'),
       ('map','independent_encoding_model.json','4'))}
    checker='acceleration/audit_20261004_fixed17_per_copy_local_sat_v6.py'
    spec='acceleration/audit_20261004_fixed17_per_copy_local_sat_v6_spec.md'
    gate={'status':ENCODING_STATUS,'implementation_version':1,'code_version':6,
      'producer':'/root/structural','verifier':'/root/native_driver','method':'independent_artifact_check',
      'target_resolution':'NONE','source_sha256':PINS[checker],'specification_sha256':PINS[spec],
      'inputs_sha256':{checker:PINS[checker],spec:PINS[spec],
         **{refs[name]['path']:refs[name]['sha256'] for name in ('profile','model','formula')}},
      'outputs_sha256':{refs['map']['path']:refs['map']['sha256']},
      'outcome':{'base_variables':model['variables'],'variables':model['variables'],'clauses':2,
         'complete_groups':len(model['rows']),'complete_degree_groups':model['outside_copies'],
         'complete_support_groups':model['outside_copies']*model['support_order'],
         'complete_checkpoints':len(range(100,len(model['rows']),100))+1,'all_checkpoint_prefixes_checked':True,
         'exact_formula_sha256':refs['formula']['sha256'],'exact_eof':True,
         'all_auxiliary_clauses_checked':True,'outside_pair_CN_equations_included':False,'graph_object_approved':False}}
    return gate,refs


def own_routes(out,budget):
    rows=[]
    def run(name,expected,payload,action):
        budget.tick();result=None
        try:result=action();actual='PASS'
        except Veto as exc:actual=str(exc)
        if expected!='PASS':result=None
        row={'index':len(rows),'name':name,'expected_stage':expected,'actual_stage':actual,'matches':actual==expected}
        write(out/f"control_{len(rows):03d}.json",{**row,'payload':payload,'result':result},budget)
        rows.append(row)
    def sat(name,expected,data,variables=2):
        run(name,expected,{'text':data.decode('ascii'),'variables':variables},
            lambda:parse_assignment(io.BytesIO(data),variables,budget))
    def cnf(name,expected,data,values=None,variables=2,clauses=2):
        values=[1,1] if values is None else values
        run(name,expected,{'text':data.decode('ascii'),'values':values,'variables':variables,'clauses':clauses},
            lambda:check_formula(io.BytesIO(data),values,variables,clauses,budget))
    good=b's SATISFIABLE\nv 1 2 0\n';formula=b'p cnf 2 2\n1 2 0\n-1 2 0\n'
    sat('positive_complete_model','PASS',good)
    sat('positive_wrapped_model','PASS',b'c synthetic fixture\ns SATISFIABLE\nv 1\nc between model lines\nv 2 0\n')
    sat('positive_native_bash_preamble','PASS',b'bash 5.2\nsha256sum (GNU coreutils) 9.1\nfixture/local.cnf: OK\nc solver\n'+good)
    sat('positive_signed_model','PASS',b's SATISFIABLE\nv -1 2 0\n')
    cnf('positive_all_clauses','PASS',formula)
    cnf('positive_zero_clauses','PASS',b'p cnf 2 0\n',clauses=0)
    rook=rook_fixture();raw=rook['profile'];model=wire_model(raw,budget);bits=rook['candidate']['edge_values']
    run('positive_rook_complete_local_and_graph','PASS',rook,
        lambda:local_assignment(raw,model,bits,budget))
    switched=switched_rook_fixture()
    def switched_check():
        result=local_assignment(switched['profile'],model,switched['candidate']['edge_values'],budget)
        need(result['local_witness_validated'] is True and result['full_graph_diagnostic']['srg_valid'] is False and
             result['graph_object_approved'] is False,'SWITCHED_ROOK_BOUNDARY')
        return result
    run('positive_local_SAT_does_not_approve_graph','PASS',switched,switched_check)
    mapped=expected_encoding_map(model,21,2)
    run('positive_reconstructed_base_map','PASS',mapped,lambda:encoding_map(model,mapped,21,2))
    legacy=synthetic_runtime();current=synthetic_runtime(True)
    def rt(value):return native_runtime(value['plan'],value['manifest'],value['terminal'],'fixture/local.cnf')
    run('positive_native_legacy_22_6','PASS',legacy,lambda:rt(legacy))
    def current_rt():
        result=rt(current)
        native_material(current['plan'],current['plan']['formula'],{'path':'fixture/native/stdout.log','sha256':'2'*64},
          {'path':'fixture/sha256.txt','sha256':'3'*64},None,
          'fixture/native/manifest.json','fixture/native/summary.json')
        result['review']=review_scope(None,current['terminal'])
        return result
    run('positive_native_current_24_6_with_material','PASS',current,current_rt)
    gate,refs=synthetic_encoding(model)
    def eg(value):return encoding_gate(value,model,refs['profile'],refs['model'],refs['formula'],refs['map'],False)
    run('positive_encoding_actual_header_source','PASS',gate,lambda:eg(gate))
    checks=checksum_bytes(refs['formula'])
    run('positive_exact_native_three_checksums','PASS',checks.decode('ascii'),lambda:checksum_list(checks,refs['formula']))
    proof_ref={'path':'fixture/full/summary.json','sha256':'5'*64};root={'result':'PASS','summary':proof_ref}
    run('positive_encoding_root_summary_ref','PASS',root,lambda:encoding_acceptance(root,proof_ref))
    native_root={'result':'PASS_RUNTIME_IDENTITY_ONLY','fresh_inputs_sha256':{r['path']:r['sha256'] for r in refs.values()},
      'native_review_required':False,'native_review_not_needed_reason':'Synthetic native10 closed before1700s'}
    run('positive_native_root_identity_only','PASS',native_root,lambda:native_acceptance(native_root,list(refs.values()),True))
    nested=out/'fixture_packet';nested.mkdir();write(nested/'leaf.json',{'fixture':True},budget)
    leaf=key(nested/'leaf.json');leaf_hash=Reader(budget).digest(nested/'leaf.json')
    write(nested/'summary.json',{'outputs_sha256':{leaf:leaf_hash}},budget)
    packet_ref={'path':key(nested/'summary.json'),'sha256':Reader(budget).digest(nested/'summary.json')}
    run('positive_exact_packet_inventory','PASS',packet_ref,lambda:packet(Reader(budget),packet_ref)[0])
    for name,expected,data in (
      ('missing_status','SAT_MODEL_LINE',b'v 1 2 0\n'),
      ('UNSAT_status','SAT_STATUS',b's UNSATISFIABLE\n'),
      ('duplicate_coordinate','SAT_MODEL_DUPLICATE',b's SATISFIABLE\nv 1 1 2 0\n'),
      ('duplicate_status','SAT_STATUS',b's SATISFIABLE\ns SATISFIABLE\nv 1 2 0\n'),
      ('missing_coordinate','SAT_MODEL_COMPLETE',b's SATISFIABLE\nv 1 0\n'),
      ('missing_terminator','SAT_MODEL_TERMINATOR',b's SATISFIABLE\nv 1 2\n'),
      ('internal_terminator','SAT_MODEL_TERMINATOR',b's SATISFIABLE\nv 1 0 2\n'),
      ('model_after_terminator','SAT_MODEL_LINE',b's SATISFIABLE\nv 1 2 0\nv 1\n'),
      ('coordinate_outside_domain','SAT_MODEL_ID',b's SATISFIABLE\nv 1 3 0\n'),
      ('leading_zero','SAT_MODEL_TOKEN',b's SATISFIABLE\nv 01 2 0\n'),
      ('plus_token','SAT_MODEL_TOKEN',b's SATISFIABLE\nv +1 2 0\n'),
      ('float_coordinate','SAT_MODEL_TOKEN',b's SATISFIABLE\nv 1.0 2 0\n'),
      ('negative_zero','SAT_MODEL_TOKEN',b's SATISFIABLE\nv 1 2 -0\n'),
      ('model_before_status','SAT_MODEL_LINE',b'v 1\ns SATISFIABLE\nv 2 0\n'),
      ('unexpected_after_status','SAT_MODEL_LINE',b's SATISFIABLE\nnot model\nv 1 2 0\n'),
      ('CRLF_model','SAT_LOG_FORMAT',b's SATISFIABLE\r\nv 1 2 0\r\n'),
      ('double_space','SAT_MODEL_TOKEN',b's SATISFIABLE\nv 1  2 0\n')):
        sat(name,expected,data)
    cnf('wrong_DIMACS_header','DIMACS_HEADER',b'p cnf 3 2\n1 2 0\n-1 2 0\n')
    cnf('false_clause','CLAUSE_FALSE',b'p cnf 2 2\n-1 -2 0\n-1 2 0\n')
    cnf('empty_clause','CLAUSE_FALSE',b'p cnf 2 2\n0\n-1 2 0\n')
    cnf('clause_variable_range','CLAUSE_VARIABLE',b'p cnf 2 2\n1 3 0\n-1 2 0\n')
    cnf('float_clause','CLAUSE_FORMAT',b'p cnf 2 2\n1.0 2 0\n-1 2 0\n')
    cnf('clause_missing_zero','CLAUSE_FORMAT',b'p cnf 2 2\n1 2\n-1 2 0\n')
    cnf('extra_clause_after_EOF','FORMULA_EOF',formula+b'1 0\n')
    cnf('Boolean_assignment_value','ASSIGNMENT_VALUES',formula,[True,1])
    changed=copy.deepcopy(model);changed['rows'][0]['lower']=True
    run('model_Boolean_row','MODEL_RECONSTRUCTION',changed,lambda:assignment_model(raw,changed,budget))
    changed_row=copy.deepcopy(model);changed_row['rows'][-1]['upper']+=1
    run('late_model_rhs','MODEL_RECONSTRUCTION',changed_row,lambda:assignment_model(raw,changed_row,budget))
    changed_pair=copy.deepcopy(model);changed_pair['variable_pairs'][-1].reverse()
    run('late_model_pair_order','MODEL_RECONSTRUCTION',changed_pair,lambda:assignment_model(raw,changed_pair,budget))
    forced=copy.deepcopy(raw);forced['pair_bits'][0]['bits']=[1];forced_model=wire_model(forced,budget)
    lower_bad=list(bits);lower_bad[0]=0
    run('fixed_true_bound','LOCAL_BOUND',{'profile':forced,'values':lower_bad},
        lambda:local_assignment(forced,forced_model,lower_bad,budget))
    degree_bad=list(bits);degree_bad[0]=0
    run('local_degree_row','LOCAL_ROW',degree_bad,lambda:local_assignment(raw,model,degree_bad,budget))
    bool_bad=list(bits);bool_bad[-1]=False
    run('local_Boolean_coordinate','ASSIGNMENT_VALUES',bool_bad,lambda:local_assignment(raw,model,bool_bad,budget))
    invalid_graph=[[0]*3 for _ in range(3)];invalid_graph[0][0]=False
    run('graph_Boolean_entry','SRG_BINARY',invalid_graph,lambda:whole_srg_diagnostic(invalid_graph,1,budget))
    bad_map=copy.deepcopy(mapped);bad_map['variable_map'][-1]['sat_id']-=1
    run('late_map_wrong_SAT_id','ENCODING_MAP',bad_map,lambda:encoding_map(model,bad_map,21,2))
    bad_unit=copy.deepcopy(mapped);bad_unit['variable_map'][0]['clause_count']=1
    run('map_fixed_unit_claim','ENCODING_MAP',bad_unit,lambda:encoding_map(model,bad_unit,21,2))
    def damaged_runtime(name,stage,edit):
        value=copy.deepcopy(current);edit(value);run(name,stage,value,lambda:rt(value))
    damaged_runtime('native_UNSAT20','NATIVE_TERMINAL',lambda p:p['terminal'].__setitem__('command_exit_code',20))
    damaged_runtime('native_Boolean_exit','NATIVE_TERMINAL',lambda p:p['terminal'].__setitem__('command_exit_code',True))
    damaged_runtime('native_deadline','NATIVE_TERMINAL',lambda p:p['terminal'].__setitem__('deadline_reached',True))
    damaged_runtime('native_error','NATIVE_TERMINAL',lambda p:p['terminal'].__setitem__('error','error'))
    damaged_runtime('native_unreaped','NATIVE_CLEANUP',lambda p:p['terminal']['cleanup'].__setitem__('reaped',False))
    damaged_runtime('native_unreadable_original_group','NATIVE_GROUP',
        lambda p:p['terminal']['cleanup']['cleanup_observations'][-1].__setitem__('unreadable_pids',[123]))
    damaged_runtime('native_live_original_group','NATIVE_CLEANUP',
        lambda p:p['terminal']['cleanup'].__setitem__('process_group_live_pids',[123]))
    damaged_runtime('native_wrong_scope','NATIVE_MANIFEST',lambda p:p['manifest'].__setitem__('runtime_scope','invented'))
    damaged_runtime('native_elapsed_string','NATIVE_ELAPSED',lambda p:p['terminal'].__setitem__('elapsed_seconds','inf'))
    damaged_runtime('native_science_without_review','NATIVE_PLAN',
        lambda p:(p['plan']['command'].__delitem__(slice(15,17)),p['plan']['supervisor_argv'].__delitem__(slice(15,17))))
    wrong_material=copy.deepcopy(current);wrong_material['plan']['stdout']['path']='fixture/elsewhere.log'
    run('native_wrong_stdout_identity','NATIVE_PLAN_MATERIAL',wrong_material,
        lambda:native_material(wrong_material['plan'],current['plan']['formula'],current['plan']['stdout'],
          {'path':'fixture/sha256.txt','sha256':'3'*64},{'path':'fixture/review.json','sha256':'4'*64},
          'fixture/native/manifest.json','fixture/native/summary.json'))
    def damaged_gate(name,stage,edit):
        value=copy.deepcopy(gate);edit(value);run(name,stage,value,lambda:eg(value))
    damaged_gate('encoding_old_source_code3','ENCODING_GATE_HEADER',lambda p:p.__setitem__('code_version',3))
    damaged_gate('encoding_Boolean_wire_version','ENCODING_GATE_HEADER',lambda p:p.__setitem__('implementation_version',True))
    damaged_gate('encoding_wrong_software','ENCODING_GATE_SOURCE',
        lambda p:p['inputs_sha256'].__setitem__('acceleration/audit_20261004_fixed17_per_copy_local_sat_v6.py','0'*64))
    damaged_gate('encoding_missing_formula_pin','ENCODING_GATE_DIRECT_PINS',lambda p:p['inputs_sha256'].pop(refs['formula']['path']))
    damaged_gate('encoding_Boolean_group_count','ENCODING_GATE_SCOPE',lambda p:p['outcome'].__setitem__('complete_groups',True))
    damaged_gate('encoding_swapped_method_key','ENCODING_GATE_HEADER',lambda p:p.__setitem__('verification_method',p.pop('method')))
    run('checksum_formula_hash_changed','NATIVE_CHECKSUM_LIST',checks.decode('ascii').replace('3'*64,'0'*64),
        lambda:checksum_list(checks.replace(b'3'*64,b'0'*64),refs['formula']))
    run('checksum_extra_line','NATIVE_CHECKSUM_LIST',(checks+b'0  extra\n').decode('ascii'),
        lambda:checksum_list(checks+b'0  extra\n',refs['formula']))
    wrong_root={'result':'PASS','summary':{**proof_ref,'sha256':'0'*64}}
    run('encoding_root_wrong_summary','ENCODING_ROOT_ACCEPTANCE',wrong_root,lambda:encoding_acceptance(wrong_root,proof_ref))
    wrong_native={'result':'PASS_RUNTIME_IDENTITY_ONLY','fresh_inputs_sha256':{}}
    run('native_root_missing_direct_pin','NATIVE_ROOT_DIRECT_PINS',wrong_native,
        lambda:native_acceptance(wrong_native,list(refs.values())))
    run('duplicate_JSON_key','JSON_DUPLICATE','{"a":0,"a":1}',lambda:decode(b'{"a":0,"a":1}'))
    run('nonfinite_JSON_number','JSON_NONFINITE','{"a":NaN}',lambda:decode(b'{"a":NaN}'))
    run('save_reserve_boundary','SAVE_RESERVE',{'stop_required':False,'remaining_seconds':20},
        lambda:reserve({'stop_required':False,'remaining_seconds':20}))
    (nested/'extra').mkdir();write(nested/'extra/summary.json',{'unlisted':True},budget)
    run('unlisted_nested_summary','PACKET_POPULATION',{'ref':packet_ref,'extra':'extra/summary.json'},
        lambda:packet(Reader(budget),packet_ref))
    review={'invocation_id':'synthetic-only','observed_at_elapsed_seconds':0.05,'observations':'Finite fixture only',
      'remaining_cost':'No scientific computation','benefit_and_alternatives':'Parser control',
      'uncertainty':'Synthetic receipt','decision':'continue','success_probability':None}
    run('positive_genuine_shaped_policy_review','PASS',review,lambda:review_scope(review,current['terminal']))
    bool_review=copy.deepcopy(review);bool_review['observed_at_elapsed_seconds']=False
    run('review_Boolean_elapsed','NATIVE_REVIEW_IDENTITY',bool_review,lambda:review_scope(bool_review,current['terminal']))
    late=copy.deepcopy(current['terminal']);late['elapsed_seconds']=1700.0
    run('missing_due_policy_review','NATIVE_REVIEW_REQUIRED',late,lambda:review_scope(None,late))
    absence_bad=copy.deepcopy(native_root);absence_bad.pop('native_review_not_needed_reason')
    run('native_root_review_absence_reason_missing','NATIVE_ROOT_REVIEW_ABSENCE',absence_bad,
        lambda:native_acceptance(absence_bad,list(refs.values()),True))
    bool_stdout=copy.deepcopy(current);bool_stdout['plan']['stdout']['sha256']=True
    run('native_planned_stdout_Boolean_hash','NATIVE_PLAN_MATERIAL',bool_stdout,
        lambda:native_material(bool_stdout['plan'],current['plan']['formula'],
          {'path':'fixture/native/stdout.log','sha256':'2'*64},
          {'path':'fixture/sha256.txt','sha256':'3'*64},None,
          'fixture/native/manifest.json','fixture/native/summary.json'))
    damaged_gate('encoding_old_source_code4','ENCODING_GATE_HEADER',lambda p:p.__setitem__('code_version',4))
    damaged_gate('encoding_old_source_code5','ENCODING_GATE_HEADER',lambda p:p.__setitem__('code_version',5))
    return rows


def calibrate(out,budget):
    rows=own_routes(out,budget);positive=sum(row['expected_stage']=='PASS' for row in rows)
    need(len(rows)==82 and positive==17,'OWN_POPULATION');write(out/'controls.json',rows,budget)
    need(all(row['matches'] for row in rows),'OWN_STAGE_MISMATCH')
    return {'positive':17,'negative':65,'total':82,'all_precise_stages_match':True,
      'actual_scientific_formula_read':False,'actual_native_assignment_read':False,
      'known_rook_full_graph_checks':1,'switched_rook_local_pass_graph_failure_retained':True,
      'complete_tiny_rook_local_rows':21,'solver_calls':0,'graph_object_approved':False}


def qualification(reader,ref,software):
    raw,base=packet(reader,ref)
    need(raw.get('status')==CAL_STATUS and raw.get('mode')=='calibrate' and
         type(raw.get('implementation_version')) is int and raw['implementation_version']==1 and
         type(raw.get('code_version')) is int and raw['code_version']==3 and
         raw.get('producer')=='/root' and raw.get('verifier')=='/root/native_driver' and
         raw.get('method')=='independent_artifact_check' and raw.get('target_resolution')=='NONE' and
         typed_equal(raw.get('source_software'),software),'OWN_HEADER')
    scope=raw.get('outcome')
    need(type(scope) is dict and all(type(scope.get(name)) is int and scope[name]==value for name,value in
         (('positive',17),('negative',65),('total',82))) and scope.get('all_precise_stages_match') is True and
         scope.get('actual_scientific_formula_read') is False and scope.get('actual_native_assignment_read') is False,
         'OWN_SCOPE')
    need(type(raw.get('inputs_sha256')) is dict and all(raw['inputs_sha256'].get(name)==digest for name,digest in software.items()),
         'OWN_SOFTWARE')
    outputs=raw['outputs_sha256'];need(len(outputs)==86,'OWN_OUTPUT_POPULATION')
    for name,digest in outputs.items():reader.read(name,digest)
    table=reader.read(base/'controls.json',outputs[key(base/'controls.json')])
    need(type(table) is list and len(table)==82 and all(type(row) is dict and type(row.get('index')) is int and
         row['index']==i and row.get('matches') is True and row.get('actual_stage')==row.get('expected_stage')
         for i,row in enumerate(table)),'OWN_STAGES')
    for i,row in enumerate(table):
        record=reader.read(base/f'control_{i:03d}.json',outputs[key(base/f'control_{i:03d}.json')])
        need(type(record) is dict and all(typed_equal(record.get(name),value) for name,value in row.items()),'OWN_RECORD_IDENTITY')
    return {'qualified_positive':17,'qualified_negative':65,'qualified_total':82,
      'all_saved_stage_records_authenticated':True,'own82_actions_rerun':False}


def review_identity(raw,terminal):
    need(type(raw) is dict and raw.get('invocation_id')==terminal['invocation_id'] and
         all(type(raw.get(name)) is str and raw[name].strip() for name in
             ('observations','remaining_cost','benefit_and_alternatives','uncertainty')) and
         type(raw.get('observed_at_elapsed_seconds')) in (int,float) and math.isfinite(raw['observed_at_elapsed_seconds']) and
         0<=raw['observed_at_elapsed_seconds']<=terminal['elapsed_seconds'] and
         raw.get('success_probability') is None and raw.get('decision') in ('continue','stop','change_method'),
         'NATIVE_REVIEW_IDENTITY')
    return {'invocation_id':raw['invocation_id'],'declared_observation_elapsed_seconds':raw['observed_at_elapsed_seconds'],
      'decision':raw['decision'],'timely_submission_and_acceptance_inherited_from_root_receipt':True,
      'freshness_not_recomputed_from_later_terminal_elapsed':True}


def review_scope(raw,terminal):
    if raw is None:
        need(type(terminal.get('elapsed_seconds')) in (int,float) and math.isfinite(terminal['elapsed_seconds']) and
             0<=terminal['elapsed_seconds']<1700,'NATIVE_REVIEW_REQUIRED')
        return {'required':False,'native_closed_before_declared_1700_second_review_point':True,
          'absence_authenticated_by_root_runtime_acceptance':True}
    return review_identity(raw,terminal)


def full(reader,config,out,software):
    names={'independent_calibration','root_calibration_acceptance','encoding_report','encoding_root_acceptance',
      'profile','copy_model','copy_gate','copy_root_acceptance','encoding_map','formula','native_plan','native_manifest',
      'native_terminal','native_stdout','native_checksum_list','native_review','native_root_acceptance'}
    need(type(config) is dict and config.keys()==names|{'schema','target_resolution','inputs_sha256'} and
         config['schema']=='FIXED17_PER_COPY_LOCAL_SAT_ASSIGNMENT_CONFIGURATION_V1' and
         config['target_resolution']=='NONE','CONFIGURATION')
    refs={}
    for name in names:
        if name=='native_review' and config[name] is None:refs[name]=None;continue
        ref=config[name];need(type(ref) is dict and ref.keys()=={'path','sha256'} and
          type(ref['path']) is str and key(safe(ref['path']))==ref['path'] and
          type(ref['sha256']) is str and re.fullmatch('[0-9a-f]{64}',ref['sha256']) is not None,'CONFIGURATION_REFERENCE')
        refs[name]=ref
    declared=dict(software)
    for ref in refs.values():
        if ref is None:continue
        need(ref['path'] not in declared or declared[ref['path']]==ref['sha256'],'INPUT_ALIAS')
        declared[ref['path']]=ref['sha256']
    need(typed_equal(config['inputs_sha256'],declared),'CONFIGURATION_INPUT_UNION');reader.map(declared)
    fixed={'profile':{'path':'acceleration/results/20261004_fixed17_count_neighbor_capacity01/parsed_screen_input.json',
        'sha256':'468f281bfc13a34a5c23ca2a6af9f8564954c826e0b9f7bddfad36a76832690e'},
      'copy_model':{'path':'acceleration/results/20261004_fixed17_copy_adjacency01/copy_model.json',
        'sha256':'dc8590c9484cb8c0555b1cb00e3f6058daab6bbe1462673035611a69a4b046c3'},
      'copy_gate':{'path':'acceleration/results/20261004_independent_review/fixed17_per_copy_adjacency_full01/summary.json',
        'sha256':'47d107e7b2981018a51f4274e9fcfb97889abf2e6b353ed30efade74078bb625'},
      'copy_root_acceptance':{'path':'acceleration/results/20261004_per_copy_adjacency_checker_full_root_actual_acceptance01.json',
        'sha256':'08a0219e5feec68c2bfa748d99c9730cac6a78bd40931d4f639d430bfe0648ed'}}
    need(all(typed_equal(refs[name],ref) for name,ref in fixed.items()),'FIXED_PREMISE_IDENTITIES')
    own=qualification(reader,refs['independent_calibration'],software)
    # These admin/model receipts are direct authenticated inherited premises, not a new closure walk.
    reader.ref(refs['root_calibration_acceptance']);reader.ref(refs['copy_gate']);reader.ref(refs['copy_root_acceptance'])
    raw=reader.ref(refs['profile']);model=reader.ref(refs['copy_model'])
    geometry,abstract=assignment_model(raw,model,reader.budget)
    need(geometry['n']==99 and geometry['k']==14 and geometry['support']==17 and len(geometry['labels'])==82 and
         len(raw['ordered_masks'])==472 and len(abstract['variable_pairs'])==3321 and len(abstract['rows'])==1476,
         'SCIENTIFIC_MODEL_SCOPE')
    gate=reader.ref(refs['encoding_report']);mapping=reader.ref(refs['encoding_map'])
    gate_base=safe(refs['encoding_report']['path']).parent
    need(safe(refs['encoding_map']['path'])==gate_base/'independent_encoding_model.json','ENCODING_MAP_LOCATION')
    scope=encoding_gate(gate,model,refs['profile'],refs['copy_model'],refs['formula'],refs['encoding_map'])
    encoding_acceptance(reader.ref(refs['encoding_root_acceptance']),refs['encoding_report'])
    encoding_map(model,mapping,scope['variables'],scope['clauses'])
    plan=reader.ref(refs['native_plan']);manifest=reader.ref(refs['native_manifest']);terminal=reader.ref(refs['native_terminal'])
    runtime=native_runtime(plan,manifest,terminal,refs['formula']['path'])
    need(runtime['native_seconds']==1800,'SCIENTIFIC_NATIVE_DURATION')
    native_material(plan,refs['formula'],refs['native_stdout'],refs['native_checksum_list'],refs['native_review'],
      refs['native_manifest']['path'],refs['native_terminal']['path'])
    need(type(terminal.get('preserved_outputs')) is str and repo_key(terminal['preserved_outputs'])==repo_key(runtime['out']),
      'NATIVE_PRESERVED_OUTPUTS')
    native_refs=[refs[name] for name in ('native_plan','native_manifest','native_terminal','native_stdout',
      'native_checksum_list','native_review') if refs[name] is not None]
    native_acceptance(reader.ref(refs['native_root_acceptance']),native_refs,refs['native_review'] is None)
    review=review_scope(None if refs['native_review'] is None else reader.ref(refs['native_review']),terminal)
    checksum_path=safe(refs['native_checksum_list']['path']);reader.budget.tick()
    checksum=checksum_list(checksum_path.read_bytes(),refs['formula']);reader.budget.tick()
    with safe(refs['native_stdout']['path']).open('rb') as stream:
        values=parse_assignment(stream,scope['variables'],reader.budget)
    with safe(refs['formula']['path']).open('rb') as stream:
        clauses=check_formula(stream,values,scope['variables'],scope['clauses'],reader.budget)
    need(clauses['formula_sha256']==refs['formula']['sha256'],'FORMULA_STREAM_HASH')
    witness=local_assignment(raw,model,values,reader.budget)
    write(out/'independent_assignment.json',{'schema':'INDEPENDENT_LOCAL_SAT_COMPLETE_ASSIGNMENT_V1',
      'variables':scope['variables'],'values':values,'base_variables':3321,'every_variable_assigned_once':True},reader.budget)
    write(out/'complete_clause_receipt.json',clauses,reader.budget)
    write(out/'complete_mapping_receipt.json',scope,reader.budget)
    write(out/'native_runtime_receipt.json',{**runtime,'review':review},reader.budget)
    write(out/'native_checksum_receipt.json',checksum,reader.budget)
    write(out/'independent_local_rows.json',witness['row_checks'],reader.budget)
    write(out/'decoded_adjacency.json',witness['adjacency'],reader.budget)
    write(out/'full_graph_diagnostic.json',witness['full_graph_diagnostic'],reader.budget)
    write(out/'qualification_authentication_receipt.json',own,reader.budget)
    return {'complete_variables_assigned':scope['variables'],'complete_clauses_satisfied':scope['clauses'],
      'complete_base_variables_checked':3321,'complete_local_rows_checked':1476,'exact_formula_eof':True,
      'native_exit_code':10,'local_SAT_witness_validated':True,'complete_graph_CN_entries':9801,
      'decoded_graph_srg_valid':witness['full_graph_diagnostic']['srg_valid'],
      'first_graph_failure':witness['full_graph_diagnostic']['first_failure'],
      'graph_object_approved':False,'count_profile_excluded':False,'target_resolution':'NONE',
      'encoding_correspondence_inherited':True,'copy_model_prerequisite_inherited':True,
      'own82_actions_rerun':False,'ancestor_bulk_or_actions_replayed':False,'solver_calls':0,
      'discovery_encoder_imports':0,'discovery_solver_imports':0,'discovery_AST_executed':False,
      'native_review_policy_inherited':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('calibrate','check'))
    parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',required=True)
    parser.add_argument('--self-sha256',required=True);parser.add_argument('--spec-sha256',required=True)
    parser.add_argument('--configuration');parser.add_argument('--configuration-sha256')
    args=parser.parse_args();budget=Budget(args.seconds);reader=Reader(budget)
    out=safe(args.out,False);need(out.is_relative_to(ROOT/'acceleration/results') and not out.exists(),'OUTPUT_ROOT')
    out.mkdir(parents=True)
    try:
        software={**PINS,SELF:args.self_sha256,SPEC:args.spec_sha256};reader.map(software)
        if args.mode=='calibrate':
            need(args.configuration is None and args.configuration_sha256 is None,'CALIBRATION_ARGUMENTS')
            outcome=calibrate(out,budget);status=CAL_STATUS
        else:
            need(args.configuration is not None and args.configuration_sha256 is not None,'CONFIGURATION_ARGUMENTS')
            config=reader.read(args.configuration,args.configuration_sha256)
            outcome=full(reader,config,out,software);status=FULL_STATUS
        reader.close();outputs={name:reader.digest(safe(name),BODY_LIMIT if name.endswith('.cnf') else JSON_LIMIT)
          for name in inventory(out,budget)}
        need(len(outputs)==(86 if args.mode=='calibrate' else 9),'CHECKER_OUTPUT_POPULATION')
        report={'status':status,'implementation_version':1,'code_version':3,'mode':args.mode,
          'producer':'/root','verifier':'/root/native_driver','checking_implementation_author':'/root/native_driver',
          'actual_executor':'See separate genuine supported supervisor receipt','encoding_producer':'/root/structural',
          'method':'independent_artifact_check','timestamp':datetime.now(timezone.utc).isoformat(),
          'source_sha256':args.self_sha256,'specification_sha256':args.spec_sha256,'source_software':software,
          'inputs_sha256':dict(reader.inputs),'outputs_sha256':outputs,'outcome':outcome,
          'elapsed_seconds':budget.deadline.status()['elapsed_seconds'],'target_resolution':'NONE',
          'own_actions_rerun':82 if args.mode=='calibrate' else 0,'automatic_retry':False,
          'shared_components':['Exact pinned Native777838 profile/model/set-CN/rook functions are copied unchanged; no module/AST import.',
            'Pinned Native local-SAT V6 unchanged IO conventions are reused with a new budget rationale; assignment/clause/runtime decoders are newly authored.',
            'Accepted exact profile/copy-model and future code6 full encoding correspondence are declared inherited premises.',
            'Root actual native receipt supplies timely policy review; no hard-real-time or proof theorem inferred.'],
          'limitations':['Local SAT plus all1476 equations is insufficient for a target graph; all9801 decoded CN entries are checked separately.',
            'A complete local witness whose decoded graph fails CN remains a local witness, not an exclusion or graph approval.',
            'Native10, clean observed original Linux group and complete saved assignment/clauses are required; no native launch or UNSAT proof check.',
            'No old full99 or local encoding gate approves this changed decoder without its own fresh applicable controls.',
            '20save is allocated guard intent; actual clean external containment is independently observed.']}
        write(out/'summary.json',report,budget);reader.close();budget.tick()
        print(json.dumps({'status':status,'outcome':outcome},allow_nan=False),flush=True);return 0
    except BaseException as exc:
        try:write(out/'failure.json',{'status':'FAILED_OR_NOT_COMPLETED','stage':str(exc) if isinstance(exc,Veto) else None,
          'error':repr(exc),'inputs_sha256':dict(reader.inputs),'elapsed_seconds':budget.deadline.status()['elapsed_seconds'],
          'target_resolution':'NONE','automatic_retry':False},budget,True)
        except BaseException:pass
        raise


if __name__=='__main__':sys.exit(main())
