"""SOURCE ONLY: binary copy selectors and a literal local-neighborhood matching."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import sys
import time
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
MAX_BYTES = 64 * 1024**2
TOLERANCE = 1e-7
COUNTS = {'positive':13, 'negative':29, 'total':42}
CAL_STATUS = 'FIXED17_FOCAL_SELECTOR_MATCHING_V1_AUTHOR_CONTROLS_PASS'
SOFTWARE = {
    'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py':'593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
    'build/research-venv/Lib/site-packages/highspy/_core/__init__.pyi':'53c07e5eafff940daa32458b20262b07d39420b062e0875c2f56e9ac92f4d699',
    'build/research-venv/Lib/site-packages/highspy/_core.cp312-win_amd64.pyd':'f733d7369f647f8afe481bbaf569164f7cd7c127e41ca53cd7c205c2fb9038e2',
    'build/research-venv/Lib/site-packages/highspy/highs.py':'00ce58ef248062125309ccdaf7af6374caf1a29f6a04e0d637b7507ead34d51a',
    'build/research-venv/Lib/site-packages/highspy/__init__.py':'01df06ec93388a45de66adb43d4b243cd7e11c54f24106064a221facf6aa7eb9',
    'build/research-venv/Lib/site-packages/highspy-1.15.1.dist-info/METADATA':'cc09b9d5bf93d8cd79be21bede4e72b686d79cdc75f6524e0e0a1af3e9487a8d',
    'build/research-venv/Lib/site-packages/numpy/__init__.py':'a6958cb364663b7acce81ccfd58eeb65a2b34d5376157f924777b97211a73be4',
    'build/research-venv/Lib/site-packages/numpy-2.5.3.dist-info/METADATA':'451a9b8028000588e66b0b415587b6aef0bbc51a96d8e8a0cba0dc23acf64f99',
}
PROFILE = 'acceleration/results/20261004_fixed17_count_neighbor_capacity01/parsed_screen_input.json'
PROFILE_SHA = '468f281bfc13a34a5c23ca2a6af9f8564954c826e0b9f7bddfad36a76832690e'
PREMISES = {
    PROFILE:PROFILE_SHA,
    'acceleration/results/20261004_independent_review/fixed17_count_neighbor_capacity_full01/summary.json':'4f6711cba2450262709ba0724bbd9bdbba3c95934c85265479985be7a38decb3',
    'acceleration/results/20261004_fixed17_count_neighbor_capacity_full_root_actual_acceptance01.json':'d8eaf7c2cb41a0bd8f1287b652edcbcc498b97f3475575b6e3b0d77e5d655017',
    'acceleration/results/20261004_independent_review/external_moment_integer_counts_full01/summary.json':'37bcf42a3b5e358c4306c642e152e3e605a07dc305de71b2272e455e377bd6b8',
    'acceleration/results/20261004_independent_review/fixed17_dual_gram_pairs_full02/summary.json':'ee9fa8961415df0e5f0ca429c33fc95a1d6223b77ec68e2c9ec71cc1dec0e218',
    'acceleration/results/20261004_independent_review/target_exterior_type_edge_moments01/summary.json':'910a740aff6ecd90515af7de0a2743abab47eabe902274237b3b70e1d0fdc6d6',
    'docs/CANDIDATE_20261004_FOCAL_NEIGHBOR_MATCHING_NECESSITY_V1.md':'30be5b396aadf848e73ad24ae3c49a9a2734d9b62944f756d057a95843b57858',
    'acceleration/audit_20261004_focal_neighbor_matching_structural_v1.md':'ee5641a7be52bce09de0e9f00078d252f8107b6461c5ddec7a2b22afc69799a5',
    'acceleration/results/20261004_independent_review/focal_neighbor_matching_necessity01/summary.json':'848d35933fe2b2876ac20631a3370a73d6696cd053a7e07004b113703220a7d3',
}

class Veto(ValueError):
    pass

class SaveStop(RuntimeError):
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
        return len(a) == len(b) and all(same(x,y) for x,y in zip(a,b))
    return a == b

def reserve(raw):
    need(type(raw) is dict and raw.get('stop_required') is False and
         type(raw.get('remaining_seconds')) in (int,float) and
         math.isfinite(raw['remaining_seconds']) and raw['remaining_seconds'] > 20, 'SAVE_RESERVE')
    return raw

def tick(deadline):
    return reserve(deadline.status())

def safe(name):
    need(type(name) is str and name and '\x00' not in name, 'PATH_STRING')
    p = Path(name)
    p = p if p.is_absolute() else ROOT/p
    need(p.resolve().is_relative_to(ROOT), 'PATH_SCOPE')
    for current in (p,*p.parents):
        if current == ROOT.parent:
            break
        if current.exists():
            need(not current.is_symlink() and not current.is_junction(), 'PATH_LINK')
    return p.resolve()

def decode(raw):
    def pairs(items):
        out = {}
        for key,value in items:
            need(key not in out, 'JSON_DUPLICATE')
            out[key] = value
        return out
    def bad(_):
        raise Veto('JSON_NONFINITE')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)

class Reader:
    def __init__(self,deadline):
        self.deadline,self.pins = deadline,{}
    def read(self,name,digest,parse=True):
        tick(self.deadline)
        need(type(digest) is str and re.fullmatch('[0-9a-f]{64}',digest), 'SHA256_STRING')
        p = safe(name)
        need(p.is_file() and p.stat().st_size <= MAX_BYTES, 'FILE_BOUND')
        key = p.relative_to(ROOT).as_posix()
        need(key not in self.pins or self.pins[key] == digest, 'PIN_CONFLICT')
        h,blocks,size = hashlib.sha256(),[],0
        with p.open('rb') as f:
            while True:
                tick(self.deadline)
                block = f.read(1024*1024)
                if not block:
                    break
                size += len(block)
                need(size <= MAX_BYTES, 'FILE_BOUND')
                h.update(block)
                if parse:
                    blocks.append(block)
        need(h.hexdigest() == digest, 'INPUT_HASH')
        self.pins[key] = digest
        tick(self.deadline)
        return decode(b''.join(blocks)) if parse else None
    def mapping(self,pins):
        need(type(pins) is dict and pins, 'INPUT_MAP')
        for p,h in pins.items():
            self.read(p,h,False)
    def closing(self):
        self.mapping(dict(self.pins))

def save(path,value,deadline):
    tick(deadline)
    raw = (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode('utf8')
    need(len(raw) <= MAX_BYTES and not path.exists(), 'OUTPUT_FRESH_BOUND')
    temporary = path.with_suffix(path.suffix+'.tmp')
    with temporary.open('xb') as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    tick(deadline)
    os.replace(temporary,path)
    tick(deadline)

def profile(raw):
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
    table,n = raw['pair_bits'],len(masks)
    need(type(table) is list and len(table) == n*(n+1)//2, 'PAIR_POPULATION')
    bits = {}
    for at,(i,j) in enumerate(itertools.combinations_with_replacement(range(n),2)):
        item = table[at]
        need(type(item) is dict and set(item) == {'i','j','bits'}, 'PAIR_KEYS')
        need(type(item['i']) is int and type(item['j']) is int and (item['i'],item['j']) == (i,j), 'PAIR_COORDINATES')
        value = item['bits']
        need(type(value) is list and all(type(a) is int and a in (0,1) for a in value)
             and value == sorted(set(value)), 'PAIR_BITS')
        bits[i,j] = value
    # Empty masks are retained for explicit copy-level joint-selection cuts.
    # Actual science separately authenticates the accepted full468f profile.
    sets = [{u for u in range(m) if mask&(1<<u)} for mask in masks]
    return h,sets,counts,bits

def model(raw,focal,deadline,parsed=None):
    h,sets,counts,bits = profile(raw) if parsed is None else parsed
    need(type(focal) is int and 0 <= focal < len(counts), 'FOCAL_INDEX')
    need(counts[focal] > 0, 'FOCAL_POSITIVE')
    t = sets[focal]
    need(all(not h[u][v] for u in t for v in t), 'FOCAL_SUPPORT_INDEPENDENT')
    slots = [[i,c] for i,n in enumerate(counts) for c in range(n) if [i,c] != [focal,0]]
    intersections = [len(t&sets[i]) for i,c in slots]
    lower,upper,reasons = [],[],[]
    for (i,c),overlap in zip(slots,intersections):
        tick(deadline)
        allowed = bits[min(i,focal),max(i,focal)]
        lower.append(int(allowed == [1]))
        upper.append(int(1 in allowed and overlap <= 1))
        reasons.append({'focal_bits':allowed,'focal_support_overlap':overlap,
                        'suppressed_by_overlap':overlap >= 2})
    edges = []
    for a,b in itertools.combinations(range(len(slots)),2):
        tick(deadline)
        i,j = slots[a][0],slots[b][0]
        if intersections[a] == intersections[b] == 0 and not sets[i]&sets[j] and 1 in bits[min(i,j),max(i,j)]:
            edges.append([a,b])
    nq = len(slots)
    edge_index = {tuple(pair):nq+i for i,pair in enumerate(edges)}
    incident = [[] for _ in slots]
    for at,(a,b) in enumerate(edges,nq):
        incident[a].append([at,1]);incident[b].append([at,1])
    rows = []
    def row(kind,terms,lo,hi,detail):
        rows.append({'index':len(rows),'kind':kind,'terms':terms,'lower':lo,'upper':hi,'detail':detail})
    row('SELECTOR_DEGREE',[[a,1] for a in range(nq)],raw['target_degree']-len(t),raw['target_degree']-len(t),None)
    for u in range(len(h)):
        rhs = 2-int(u in t)-sum(h[u][v] for v in t)
        row('SELECTOR_INCIDENCE',[[a,1] for a,(i,c) in enumerate(slots) if u in sets[i]],rhs,rhs,u)
    for a,overlap in enumerate(intersections):
        if overlap == 0:
            row('MATCHING_DEGREE',[[a,-1],*incident[a]],0,0,slots[a])
    for at,(a,b) in enumerate(edges,nq):
        row('MATCHING_SELECTED_COUPLING',[[at,1],[a,-1]],None,0,[a,b])
        row('MATCHING_SELECTED_COUPLING',[[at,1],[b,-1]],None,0,[a,b])
    for a,b in itertools.combinations(range(nq),2):
        tick(deadline)
        i,j = slots[a][0],slots[b][0]
        allowed,overlap = bits[min(i,j),max(i,j)],len(sets[i]&sets[j])
        pair = (a,b)
        if not allowed or overlap >= 2 or (allowed == [1] and pair not in edge_index):
            row('PAIR_JOINT_BAN',[[a,1],[b,1]],None,1,
                {'slots':[a,b],'allowed_bits':allowed,'support_overlap':overlap})
        elif allowed == [1]:
            row('SELECTED_FORCED_EDGE',[[a,1],[b,1],[edge_index[pair],-1]],None,1,{'slots':[a,b]})
    variables = nq+len(edges)
    need(nq <= 81 and len(edges) <= 3240 and variables <= 3321 and len(rows) <= 9819, 'MODEL_SIZE_BOUND')
    return {'schema':'FIXED17_FOCAL_SELECTOR_MATCHING_MODEL_V1','focal_type':focal,'focal_label':[focal,0],
        'support_size':len(h),'target_degree':raw['target_degree'],'focal_mask':raw['ordered_masks'][focal],
        'ordered_masks':raw['ordered_masks'],'counts':counts,'selector_slots':slots,
        'selector_reasons':reasons,'matching_slot_pairs':edges,'selector_variables':nq,
        'matching_variables':len(edges),'variables':variables,'lower':lower+[0]*len(edges),
        'upper':upper+[1]*len(edges),'rows':rows,'incidence_equalities':len(h)+1,
        'same_type_uniform_profiles':False,'all_pair_masks_enforced':True,'graph_completion':False}

def first_bound(m):
    for j,(lo,hi) in enumerate(zip(m['lower'],m['upper'])):
        if lo > hi:
            return {'kind':'STRUCTURAL_SELECTOR_BOUND','variable':j,'lower':lo,'upper':hi}
    for row in m['rows']:
        lo = sum(c*(m['lower'][j] if c >= 0 else m['upper'][j]) for j,c in row['terms'])
        hi = sum(c*(m['upper'][j] if c >= 0 else m['lower'][j]) for j,c in row['terms'])
        if (row['lower'] is not None and hi < row['lower']) or (row['upper'] is not None and lo > row['upper']):
            return {'kind':'EXACT_ROW_INTERVAL_BOUND','row':row['index'],'row_kind':row['kind'],
                    'attainable_minimum':lo,'attainable_maximum':hi,'lower':row['lower'],'upper':row['upper']}
    return None

def binary_checked(m,values,deadline):
    need(type(values) is list and len(values) == m['variables'], 'BINARY_SHAPE')
    need(all(type(x) is int for x in values), 'BINARY_INTEGER')
    need(all(x in (0,1) for x in values), 'BINARY_BOUND')
    need(all(lo <= x <= hi for lo,x,hi in zip(m['lower'],values,m['upper'])), 'SELECTOR_BOUND')
    checked = []
    for row in m['rows']:
        tick(deadline)
        lhs = sum(c*values[j] for j,c in row['terms'])
        need((row['lower'] is None or lhs >= row['lower']) and
             (row['upper'] is None or lhs <= row['upper']),row['kind'])
        checked.append({'index':row['index'],'kind':row['kind'],'lhs':lhs,'lower':row['lower'],
                        'upper':row['upper'],'exact':True})
    return checked

def from_labels(m,selected,matched,deadline):
    need(type(selected) is list and all(type(p) is list and len(p) == 2 for p in selected), 'SELECTED_SHAPE')
    need(all(type(x) is int for p in selected for x in p), 'LABEL_INTEGER')
    need(m['focal_label'] not in selected, 'SELECTED_SELF')
    need(selected == sorted(selected) and len({tuple(p) for p in selected}) == len(selected), 'SELECTED_ORDER')
    slot_index = {tuple(p):i for i,p in enumerate(m['selector_slots'])}
    need(all(tuple(p) in slot_index for p in selected), 'SELECTED_CAPACITY')
    need(type(matched) is list and all(type(p) is list and len(p) == 2 and all(type(v) is list and len(v) == 2 for v in p)
                                     for p in matched), 'MATCHING_SHAPE')
    need(all(type(x) is int for p in matched for v in p for x in v), 'MATCHING_INTEGER')
    need(matched == sorted(matched) and len({tuple(tuple(v) for v in p) for p in matched}) == len(matched)
         and all(p[0] < p[1] for p in matched), 'MATCHING_ORDER')
    edge_index = {tuple(pair):m['selector_variables']+i for i,pair in enumerate(m['matching_slot_pairs'])}
    values = [0]*m['variables']
    for p in selected:
        values[slot_index[tuple(p)]] = 1
    for left,right in matched:
        need(tuple(left) in slot_index and tuple(right) in slot_index, 'MATCHING_EDGE_NOT_ELIGIBLE')
        pair = tuple(sorted((slot_index[tuple(left)],slot_index[tuple(right)])))
        need(pair in edge_index, 'MATCHING_EDGE_NOT_ELIGIBLE')
        values[edge_index[pair]] = 1
    return values,binary_checked(m,values,deadline)

def witness(m,values,deadline):
    checked = binary_checked(m,values,deadline)
    nq = m['selector_variables']
    selected = [p for p,q in zip(m['selector_slots'],values[:nq]) if q]
    matched = [[m['selector_slots'][a],m['selector_slots'][b]] for (a,b),q in zip(m['matching_slot_pairs'],values[nq:]) if q]
    # Matching pair order comes from ordered selector-slot combinations.
    return {'schema':'FIXED17_EXACT_FOCAL_SELECTOR_MATCHING_WITNESS_V1','focal_type':m['focal_type'],
        'focal_label':m['focal_label'],'selected_labels':selected,'matching_pairs':matched,
        'binary_values':values,'all_sparse_rows':checked,'incidence_equalities':m['incidence_equalities'],
        'self_excluded':True,'all_bit0_and_overlap_cuts_checked':True,'matching_exact':True,
        'independent_approval':False,'graph_completion':False,'uniform_profiles':False}

def extraction(m,guidance,deadline):
    xs = guidance.get('col_value')
    need(type(xs) is list and all(type(x) is float and math.isfinite(x) for x in xs), 'NUMERIC_VECTOR')
    need(type(guidance.get('solution_value_valid')) is bool, 'NUMERIC_VALID_FLAG')
    if not guidance['solution_value_valid'] or len(xs) != m['variables']:
        return {'candidate':None,'reason':'No complete value-valid incumbent','numeric_infeasibility_is_proof':False}
    rounded = [round(x) for x in xs]
    distance = max((abs(x-y) for x,y in zip(xs,rounded)),default=0)
    if distance > TOLERANCE:
        return {'candidate':None,'reason':'Nonintegral coordinate','maximum_distance':distance,'numeric_infeasibility_is_proof':False}
    try:
        w = witness(m,rounded,deadline)
    except Veto as exc:
        if str(exc) == 'SAVE_RESERVE':
            raise
        return {'candidate':None,'reason':'Exact extraction rejected: '+str(exc),'rounded_values':rounded,
                'maximum_distance':distance,'numeric_infeasibility_is_proof':False}
    return {'candidate':w,'maximum_distance':distance,'independent_approval':False,'graph_completion':False}

def native(m,out,prefix,deadline,maximum,reserve_seconds):
    tick(deadline)
    import highspy
    import numpy as np
    need(Path(highspy.__file__).resolve() == ROOT/'build/research-venv/Lib/site-packages/highspy/__init__.py' and
         Path(np.__file__).resolve() == ROOT/'build/research-venv/Lib/site-packages/numpy/__init__.py', 'BACKEND_PATH')
    need(type(maximum) in (int,float) and math.isfinite(maximum) and 0 < maximum <= 10, 'SOLVER_MAXIMUM')
    remaining = tick(deadline)['remaining_seconds']
    if remaining <= reserve_seconds:
        raise SaveStop('No remaining solver allowance after declared closing reserve')
    solver = highspy.Highs()
    need(solver.version() == '1.15.1' and np.__version__ == '2.5.3', 'BACKEND_VERSION')
    lp = highspy.HighsLp()
    lp.num_col_,lp.num_row_ = m['variables'],len(m['rows'])
    lp.col_cost_ = np.zeros(lp.num_col_,dtype=np.float64)
    lp.col_lower_,lp.col_upper_ = np.asarray(m['lower'],dtype=np.float64),np.asarray(m['upper'],dtype=np.float64)
    lp.integrality_ = [highspy.HighsVarType.kInteger]*lp.num_col_
    lp.row_lower_ = np.asarray([-highspy.kHighsInf if r['lower'] is None else r['lower'] for r in m['rows']],dtype=np.float64)
    lp.row_upper_ = np.asarray([highspy.kHighsInf if r['upper'] is None else r['upper'] for r in m['rows']],dtype=np.float64)
    starts,indices,coefficients = [0],[],[]
    for row in m['rows']:
        tick(deadline)
        for j,c in row['terms']:
            indices.append(j);coefficients.append(c)
        starts.append(len(indices))
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_ = np.asarray(starts,dtype=np.int32)
    lp.a_matrix_.index_,lp.a_matrix_.value_ = np.asarray(indices,dtype=np.int32),np.asarray(coefficients,dtype=np.float64)
    log = out/(prefix+'_solver.log')
    with log.open('xb'):
        pass
    options = {'presolve':'on','solver':'choose','threads':1,'parallel':'off','random_seed':0,
        'mip_rel_gap':0.0,'mip_abs_gap':0.0,'primal_feasibility_tolerance':TOLERANCE,
        'mip_feasibility_tolerance':TOLERANCE,'output_flag':True,'log_to_console':False,'log_file':str(log)}
    for key,value in options.items():
        need(solver.setOptionValue(key,value) == highspy.HighsStatus.kOk, 'HIGHS_OPTION:'+key)
    need(solver.passModel(lp) == highspy.HighsStatus.kOk, 'HIGHS_MODEL')
    remaining = tick(deadline)['remaining_seconds']
    if remaining <= reserve_seconds:
        raise SaveStop('Model preprocessing consumed the remaining solver allowance')
    allowance = min(float(maximum),remaining-reserve_seconds)
    need(solver.setOptionValue('time_limit',allowance) == highspy.HighsStatus.kOk, 'HIGHS_OPTION:time_limit')
    options['time_limit'] = allowance
    started = time.monotonic()
    status = solver.run()
    elapsed = time.monotonic()-started
    tick(deadline)
    solution = solver.getSolution()
    xs = [float(x) for x in solution.col_value]
    need(all(math.isfinite(x) for x in xs), 'NUMERIC_VECTOR')
    guidance = {'schema':'FIXED17_SELECTOR_MATCHING_NUMERIC_GUIDANCE_V1','native_version':solver.version(),
        'numpy_version':np.__version__,'run_status':str(status),'model_status':str(solver.getModelStatus()),
        'solution_value_valid':bool(solution.value_valid),'col_value':xs,'col_value_float_hex':[x.hex() for x in xs],
        'options':options,'wall_seconds':elapsed,'solver_calls':1,'objective_all_zero':True,
        'floating_status_is_proof':False,'numeric_infeasibility_is_proof':False}
    save(out/(prefix+'_guidance.json'),guidance,deadline)
    return guidance

def rook_fixture(support,forced=False):
    points = list(itertools.product(range(3),repeat=2))
    support = [tuple(p) for p in support]
    def adjacent(a,b):
        return a != b and (a[0] == b[0] or a[1] == b[1])
    outside = [p for p in points if p not in support]
    point_masks = {p:sum(1<<u for u,q in enumerate(support) if adjacent(p,q)) for p in outside}
    masks = sorted(set(point_masks.values()))
    groups = [[p for p in outside if point_masks[p] == t] for t in masks]
    for group in groups:
        group.sort(key=lambda p:(p != (0,0),p))
    labels = {p:[i,c] for i,group in enumerate(groups) for c,p in enumerate(group)}
    table = []
    for i,j in itertools.combinations_with_replacement(range(len(masks)),2):
        actual = {int(adjacent(a,b)) for a in groups[i] for b in groups[j] if a != b}
        table.append({'i':i,'j':j,'bits':sorted(actual) if forced and actual else [0,1]})
    raw = {'target_order':9,'target_degree':4,'support_adjacency':[[int(adjacent(a,b)) for b in support] for a in support],
           'ordered_masks':masks,'counts':[len(group) for group in groups],'pair_bits':table}
    w = [p for p in outside if adjacent(p,(0,0))]
    selected = sorted(labels[p] for p in w)
    matched = sorted(sorted([labels[a],labels[b]]) for a,b in itertools.combinations(w,2) if adjacent(a,b))
    return {'profile':raw,'focal':labels[(0,0)][0],'selected_labels':selected,'matching_pairs':matched}

def fixture_checked(p,deadline):
    m = model(p['profile'],p['focal'],deadline)
    values,rows = from_labels(m,p['selected_labels'],p['matching_pairs'],deadline)
    return {'model':m,'witness':witness(m,values,deadline),'checked_rows':rows}

def controls(out,deadline):
    corners = [[1,1],[1,2],[2,1],[2,2]]
    base = rook_fixture(corners)
    repeated = rook_fixture([[1,1]])
    independent2 = rook_fixture([[0,1],[1,0]])
    path = rook_fixture([[0,1],[1,1],[1,2],[2,2]])
    m = model(base['profile'],base['focal'],deadline)
    values,_ = from_labels(m,base['selected_labels'],base['matching_pairs'],deadline)
    routes = []
    def add(name,stage,p,action):
        routes.append((name,stage,copy.deepcopy(p),action))
    def mutate(name,stage,p,change,action=None):
        q = copy.deepcopy(p);change(q)
        add(name,stage,q,action or (lambda p:fixture_checked(p,deadline)))
    for name,p in [('rook_empty_T_free',base),('rook_empty_T_forced',rook_fixture(corners,True)),
                   ('rook_singleton_T',path),('rook_independent_two_T',independent2),
                   ('rook_repeated_empty_and_singleton_selected_types',repeated)]:
        add(name,'PASS',p,lambda p:fixture_checked(p,deadline))
    def unknown(p):
        result = extraction(m,p,deadline)
        need(result['candidate'] is None and result.get('numeric_infeasibility_is_proof') is False, 'UNKNOWN_CONTROL')
        return result
    add('absent_incumbent_unknown','PASS',{'solution_value_valid':False,'col_value':[]},unknown)
    badfloat = [float(x) for x in values];badfloat[0] = 0.5
    add('nonintegral_incumbent_unknown','PASS',{'solution_value_valid':True,'col_value':badfloat},unknown)
    add('binary_but_row_invalid_unknown','PASS',{'solution_value_valid':True,'col_value':[0.0]*m['variables']},unknown)
    add('budget_above_reserve','PASS',{'stop_required':False,'remaining_seconds':20.000001},reserve)
    fixed = {'variables':1,'lower':[1],'upper':[1],
             'rows':[{'index':0,'kind':'TINY_FIXED','terms':[[0,1]],'lower':1,'upper':1,'detail':None}]}
    parity = {'variables':1,'lower':[0],'upper':[1],
              'rows':[{'index':0,'kind':'TINY_PARITY','terms':[[0,2]],'lower':1,'upper':1,'detail':None}]}
    def tiny(p,case):
        g = native(p,out,'tiny_'+case,deadline,5,30)
        xs = g['col_value']
        if case == 'fixed':
            need(g['solution_value_valid'] and xs == [1.0], 'TINY_FIXED_WITNESS')
            binary_checked(p,[1],deadline)
        else:
            need(not g['solution_value_valid'] or len(xs) != 1 or abs(xs[0]-round(xs[0])) > TOLERANCE
                 or 2*round(xs[0]) != 1, 'TINY_PARITY_NO_EXACT_INTEGER')
        return {'guidance':g,'mathematical_infeasibility_proven':False}
    add('native_tiny_fixed_binary','PASS',fixed,lambda p:tiny(p,'fixed'))
    add('native_tiny_parity_unknown','PASS',parity,lambda p:tiny(p,'parity'))
    def native_rook(p):
        mm = model(p['profile'],p['focal'],deadline)
        g = native(mm,out,'tiny_rook',deadline,5,30)
        result = extraction(mm,g,deadline)
        need(result['candidate'] is not None, 'TINY_ROOK_EXACT_WITNESS')
        return {'guidance':g,'extraction':result}
    add('native_rook_forced_matching','PASS',rook_fixture(corners,True),native_rook)
    conflict = copy.deepcopy(independent2)
    focal = conflict['focal']
    for item in conflict['profile']['pair_bits']:
        if item['i'] == item['j'] == focal:
            item['bits'] = [1]
    def conflict_check(p):
        mm = model(p['profile'],p['focal'],deadline)
        b = first_bound(mm)
        need(type(b) is dict and b['kind'] == 'STRUCTURAL_SELECTOR_BOUND', 'BOUND_CONTROL')
        return {'model':mm,'exact_bound':b,'fixture_is_not_a_target_graph':True}
    add('explicit_forced_focal_overlap_conflict','PASS',conflict,conflict_check)
    for name,value,stage in [('count_bool',True,'COUNT_INTEGER'),('count_sum',0,'COUNT_SUM')]:
        mutate(name,stage,base,lambda p,v=value:p['profile']['counts'].__setitem__(0,v))
    mutate('mask_bool','TYPE_MASK',base,lambda p:p['profile']['ordered_masks'].__setitem__(0,False))
    mutate('graph_bool','GRAPH_DOMAIN',base,lambda p:p['profile']['support_adjacency'][0].__setitem__(0,False))
    mutate('pair_coordinate_bool','PAIR_COORDINATES',base,lambda p:p['profile']['pair_bits'][0].__setitem__('i',False))
    mutate('pair_bits_bool','PAIR_BITS',base,lambda p:p['profile']['pair_bits'][0].__setitem__('bits',[False,1]))
    mutate('pair_missing','PAIR_POPULATION',base,lambda p:p['profile']['pair_bits'].pop())
    mutate('focal_bool','FOCAL_INDEX',base,lambda p:p.__setitem__('focal',False))
    mutate('nonindependent_focal_T','FOCAL_SUPPORT_INDEPENDENT',base,lambda p:p.__setitem__('focal',1))
    for name,value,stage in [('binary_bool',True,'BINARY_INTEGER'),('binary_float',1.0,'BINARY_INTEGER'),('binary_two',2,'BINARY_BOUND')]:
        q = copy.deepcopy(values);q[0] = value
        add(name,stage,q,lambda p:binary_checked(m,p,deadline))
    mutate('selected_focal_self','SELECTED_SELF',base,lambda p:p['selected_labels'].__setitem__(0,[0,0]))
    mutate('selected_duplicate','SELECTED_ORDER',base,lambda p:p['selected_labels'].__setitem__(1,p['selected_labels'][0]))
    mutate('selected_copy_outside_count','SELECTED_CAPACITY',base,lambda p:p['selected_labels'][0].__setitem__(1,99))
    mutate('selected_wrong_degree','SELECTOR_DEGREE',base,lambda p:p['selected_labels'].pop())
    mutate('edge_support_overlap_one','MATCHING_EDGE_NOT_ELIGIBLE',base,
           lambda p:p.__setitem__('matching_pairs',[[[1,0],[2,0]],[[3,0],[4,0]]]))
    mutate('matching_edge_missing','MATCHING_DEGREE',base,lambda p:p['matching_pairs'].pop())
    mutate('matching_edge_duplicate','MATCHING_ORDER',base,lambda p:p['matching_pairs'].append(p['matching_pairs'][0]))
    def p_edge(p):
        p['matching_pairs'] = sorted([*p['matching_pairs'],sorted([p['selected_labels'][0],p['selected_labels'][-1]])])
    mutate('T_singleton_selected_vertex_has_W_edge','MATCHING_EDGE_NOT_ELIGIBLE',path,p_edge)
    def change_bits(p,i,j,value):
        for item in p['profile']['pair_bits']:
            if (item['i'],item['j']) == (min(i,j),max(i,j)):
                item['bits'] = value;return
        raise Veto('CONTROL_PAIR_NOT_FOUND')
    mutate('Gram_only_bit0_overlap_one','PAIR_JOINT_BAN',base,lambda p:change_bits(p,1,2,[]))
    # Abstract simultaneous-row fixture: two empty R copies each match a disjoint
    # singleton R copy. Its empty-pair bit0 is not incident with the focal type.
    zero_overlap = {'profile':{'target_order':8,'target_degree':6,'support_adjacency':[[0,0],[0,0]],
        'ordered_masks':[0,1,2],'counts':[2,2,2],'pair_bits':[{'i':i,'j':j,'bits':[0,1]}
            for i,j in itertools.combinations_with_replacement(range(3),2)]},'focal':1,
        'selected_labels':[[0,0],[0,1],[1,1],[2,0],[2,1]],
        'matching_pairs':[[[0,0],[2,0]],[[0,1],[2,1]]]}
    mutate('Gram_only_bit0_overlap_zero','PAIR_JOINT_BAN',zero_overlap,lambda p:change_bits(p,0,0,[]))
    def overlap_two(p):
        p['selected_labels'] = [[0,0],[p['focal'],1]];p['matching_pairs'] = []
    mutate('focal_overlap_two_plain_rows_insufficient','SELECTOR_BOUND',independent2,overlap_two)
    # Path fixture focal0 selects R copies1,2 and P copy4; a forced1 P-R pair cannot be matched.
    mutate('sole_bit1_ineligible_selected_pair','PAIR_JOINT_BAN',path,lambda p:change_bits(p,1,4,[1]))
    force = {'profile':{'target_order':7,'target_degree':6,'support_adjacency':[[0]],'ordered_masks':[0,1],
                       'counts':[4,2],'pair_bits':[{'i':0,'j':0,'bits':[1]},
                           {'i':0,'j':1,'bits':[0,1]},{'i':1,'j':1,'bits':[0,1]}]},
             'focal':1,'selected_labels':[[0,0],[0,1],[0,2],[0,3],[1,1]],
             'matching_pairs':[[[0,0],[0,1]],[[0,2],[0,3]]]}
    add('sole_bit1_selected_R_pair_not_matched','SELECTED_FORCED_EDGE',force,lambda p:fixture_checked(p,deadline))
    add('json_duplicate','JSON_DUPLICATE','{"x":1,"x":2}',decode)
    add('json_nonfinite','JSON_NONFINITE','{"x":NaN}',decode)
    add('budget_at_reserve','SAVE_RESERVE',{'stop_required':False,'remaining_seconds':20},reserve)
    add('budget_stop','SAVE_RESERVE',{'stop_required':True,'remaining_seconds':100},reserve)
    need(len(routes) == COUNTS['total'] and sum(stage == 'PASS' for name,stage,p,a in routes) == COUNTS['positive'], 'CONTROL_POPULATION')
    table = []
    for i,(name,expected,payload,action) in enumerate(routes):
        save(out/('control_%02d_%s.json'%(i,name)),payload,deadline)
        result = None
        try:
            result,actual = action(payload),'PASS'
        except Veto as exc:
            actual = str(exc)
        table.append({'index':i,'name':name,'expected_stage':expected,'actual_stage':actual,'matches':actual == expected})
        if result is not None:
            save(out/('result_%02d.json'%i),result,deadline)
    save(out/'controls.json',table,deadline)
    need(all(r['matches'] for r in table), 'AUTHOR_CONTROL_STAGE_MISMATCH')
    return {'counts':COUNTS,'all_precise_stages_match':True,'native_solver_calls':3,
        'actual_profile_read':False,'graph_completion':False,'abstract_bit_corruptions_are_not_rook_necessity_claims':True}

def prerequisite(reader,config,software):
    need(type(config) is dict and config.get('schema') == 'FIXED17_FOCAL_SELECTOR_MATCHING_CONFIGURATION_V1'
         and config.get('target_resolution') == 'NONE', 'CONFIG_HEADER')
    required = {**PREMISES,**software}
    pins = config.get('inputs_sha256')
    need(type(pins) is dict and all(pins.get(p) == h for p,h in required.items()), 'CONFIG_DIRECT_PINS')
    reader.mapping(pins)
    profile_raw = reader.read(PROFILE,PROFILE_SHA)
    capacity = reader.read('acceleration/results/20261004_independent_review/fixed17_count_neighbor_capacity_full01/summary.json',
                           PREMISES['acceleration/results/20261004_independent_review/fixed17_count_neighbor_capacity_full01/summary.json'])
    need(capacity.get('status') == 'INDEPENDENT_FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_COMPLETE_PASS' and
         capacity.get('inputs_sha256',{}).get(PROFILE) == PROFILE_SHA, 'TRUSTED_PROFILE_GATE')
    for kind in ('calibration','producer_controls'):
        reference = config.get('independent_'+kind)
        need(type(reference) is dict and set(reference) == {'path','sha256','implementation_version'}, 'QUALIFICATION_REFERENCE')
        path = safe(reference['path']).relative_to(ROOT).as_posix()
        need(pins.get(path) == reference['sha256'] and type(reference['implementation_version']) is int and
             reference['implementation_version'] > 0, 'QUALIFICATION_PIN')
        gate = reader.read(path,reference['sha256'])
        expected = 'INDEPENDENT_FIXED17_FOCAL_SELECTOR_MATCHING_V1_'+('CALIBRATION_PASS' if kind == 'calibration' else 'PRODUCER_CONTROLS_PASS')
        need(gate.get('status') == expected and type(gate.get('implementation_version')) is int and
             gate['implementation_version'] == reference['implementation_version'] and
             gate.get('producer') == '/root/structural' and gate.get('verifier') != '/root/structural' and
             type(gate.get('verifier')) is str and gate.get('method') == 'independent_artifact_check' and
             gate.get('target_resolution') == 'NONE' and
             all(gate.get('inputs_sha256',{}).get(p) == h for p,h in software.items()), 'QUALIFICATION_HEADER')
    return profile_raw

def scientific(reader,config,out,software):
    raw = prerequisite(reader,config,software)
    parsed = profile(raw)
    positive = [i for i,n in enumerate(raw['counts']) if n]
    need(raw['target_order'] == 99 and raw['target_degree'] == 14 and len(raw['support_adjacency']) == 17
         and len(raw['ordered_masks']) == 472 and sum(raw['counts']) == 82 and len(positive) == 68, 'FIXED_SCOPE')
    maximum = config.get('per_focal_solver_seconds')
    need(type(maximum) in (int,float) and math.isfinite(maximum) and 0 < maximum <= 10, 'SOLVER_MAXIMUM')
    save(out/'parsed_matching_input.json',raw,reader.deadline)
    decisions,calls,elapsed,unmet = [],0,0.0,[]
    for i in positive:
        tick(reader.deadline)
        prefix = 'type_%03d'%i
        m = model(raw,i,reader.deadline,parsed)
        save(out/(prefix+'_model.json'),m,reader.deadline)
        bound = first_bound(m)
        gp = wp = None
        if bound is not None:
            decision = {'status':'CANDIDATE_EXACT_LOCAL_BOUND_FAILURE','exact_bound':bound,
                        'candidate':None,'numeric_infeasibility_is_proof':False}
        else:
            try:
                g = native(m,out,prefix,reader.deadline,maximum,120)
            except SaveStop as exc:
                unmet = ['Remaining focal models/decisions/checkpoints not completed',str(exc)]
                break
            calls += 1;elapsed += g['wall_seconds'];gp = prefix+'_guidance.json'
            result = extraction(m,g,reader.deadline)
            if result['candidate'] is None:
                decision = {**result,'status':'UNKNOWN_NO_EXACT_LOCAL_MATCHING'}
            else:
                wp = prefix+'_witness.json';save(out/wp,result['candidate'],reader.deadline)
                decision = {'status':'CANDIDATE_EXACT_LOCAL_SELECTOR_MATCHING','candidate_saved':True,
                            'maximum_distance':result['maximum_distance'],'numeric_infeasibility_is_proof':False}
        decision.update(focal_type=i,guidance_path=gp,witness_path=wp,graph_completion=False,
                        count_witness_excluded=False,uniform_profiles=False)
        save(out/(prefix+'_decision.json'),decision,reader.deadline)
        decisions.append(decision)
        save(out/('checkpoint_%03d.json'%i),{'schema':'FIXED17_FOCAL_SELECTOR_MATCHING_CHECKPOINT_V1',
            'completed_focal_types':len(decisions),'positive_type_prefix':positive[:len(decisions)],
            'decisions':list(decisions),'scientific_solver_calls':calls,'solver_wall_seconds':elapsed,
            'target_resolution':'NONE','automatic_retry':False},reader.deadline)
        print(json.dumps({'completed':len(decisions),'focal_type':i,'status':decision['status']}),flush=True)
    complete = len(decisions) == len(positive)
    outcome = {'completed':complete,'completed_focal_types':len(decisions),'required_focal_types':68,
        'outside_copies':82,'selector_slots_per_focal':81,'equalities_per_focal':18,'all_type_masks':472,
        'decisions':decisions,'scientific_solver_calls':calls,'solver_wall_seconds':elapsed,'unmet_requirements':unmet,
        'exact_local_matchings':sum(d['witness_path'] is not None for d in decisions),
        'unknown_focals':sum(d['status'] == 'UNKNOWN_NO_EXACT_LOCAL_MATCHING' for d in decisions),
        'candidate_exact_bounds':sum(d['status'] == 'CANDIDATE_EXACT_LOCAL_BOUND_FAILURE' for d in decisions),
        'graph_completion':False,'count_witness_excluded':False,'numerical_infeasibility_is_proof':False}
    save(out/'matching_outcome.json',outcome,reader.deadline)
    return outcome

def output_hashes(out,deadline):
    result = {}
    for path in sorted(out.iterdir()):
        tick(deadline)
        need(path.is_file() and not path.is_symlink() and path.suffix != '.tmp', 'OUTPUT_POPULATION')
        h = hashlib.sha256()
        with path.open('rb') as f:
            while True:
                tick(deadline);block = f.read(1024*1024)
                if not block:
                    break
                h.update(block)
        result[path.name] = h.hexdigest()
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',choices=('calibrate','solve'))
    for name in ('seconds','out','self-sha256','spec-sha256','executor'):
        parser.add_argument('--'+name,required=True,type=float if name == 'seconds' else str)
    parser.add_argument('--configuration');parser.add_argument('--configuration-sha256')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds,allocation_reason='New selector/matching model, controls, native guidance and exact witness checks share one invocation')
    reader = Reader(deadline)
    out = safe(args.out)
    need(out.is_relative_to(ROOT/'acceleration/results') and not out.exists(), 'OUTPUT_FRESH')
    out.mkdir(parents=True)
    software = {**SOFTWARE,SELF.relative_to(ROOT).as_posix():args.self_sha256,SPEC.relative_to(ROOT).as_posix():args.spec_sha256}
    try:
        reader.mapping(software)
        author = controls(out,deadline)
        if args.mode == 'calibrate':
            outcome,status = author,CAL_STATUS
        else:
            need(args.configuration is not None and args.configuration_sha256 is not None, 'CONFIG_ARGUMENTS')
            config = reader.read(args.configuration,args.configuration_sha256)
            outcome = scientific(reader,config,out,software)
            status = 'CANDIDATE_FIXED17_FOCAL_SELECTOR_MATCHING_V1' if outcome['completed'] else 'NOT_COMPLETED_WITH_ALLOCATED_BUDGET'
        reader.closing()
        outputs = output_hashes(out,deadline)
        if args.mode == 'calibrate':
            need(len(outputs) == 62, 'AUTHOR_OUTPUT_POPULATION')
        report = {'schema':'FIXED17_FOCAL_SELECTOR_MATCHING_PRODUCER_REPORT_V1','implementation_version':1,
            'status':status,'timestamp':datetime.now(timezone.utc).isoformat(),'mode':args.mode,
            'producer':'/root/structural','source_author':'/root/structural','executor_declaration':args.executor,
            'executor_identity_requires_external_runtime_receipt':True,'independent_approval':False,
            'independent_verifier':None,'independent_verifier_null_reason':'Distinct fresh model/witness/closure/runtime replay required',
            'source_software':software,'inputs_sha256':reader.pins,'outputs_sha256':outputs,
            'output_root':out.relative_to(ROOT).as_posix(),'author_controls':author,'outcome':outcome,
            'command':sys.argv,'cwd':str(ROOT),'deadline':deadline.status(),
            'native_solver_calls':3+outcome.get('scientific_solver_calls',0),'actual_profile_read':args.mode == 'solve',
            'target_resolution':'NONE','graph_completion':False,'count_witness_excluded':False,
            'automatic_retry':False,'ledger_index_git_mutations':0,
            'shared_components':['Root matching discovery and separately written Structural theorem proof are explicit prerequisites, no new proof approval',
                'Reader/deadline/save/HiGHS array patterns from frozen9c0c plain focal source, no imports of that source or its AST functions',
                'Qualified468f whole profile inherited through4f671/d8eaf, not ancestor Gram/count arithmetic rerun',
                'Public rook geometry and explicitly mock corrupted bit sets; not an actual target construction'],
            'limitations':['Each local selector/matching witness concerns one designated focal copy, not a symmetric graph',
                'UNKNOWN numeric status or absent incumbent cannot exclude a count witness or target',
                'Exact bound records are candidates requiring complete separate verification before any exclusion',
                'No uniform same-type profiles, equitable partition or automorphism assumed',
                '20-second save guards are engineering intent; supported clean outer runtime and independent verification required',
                'Cooperative SaveStop saves prior prefixes/current model; unexpected exception/hard kill may lose pending suffix',
                'All scientific endpoint hashes/gates are future objects, never transferred from the plain focal lane']}
        save(out/'summary.json',report,deadline)
        reader.closing();tick(deadline)
        print(json.dumps({'status':status,'mode':args.mode}),flush=True)
    except Exception as exc:
        try:
            (out/'failure.json').write_text(json.dumps({'status':'FAILED_PRESERVED','stage':str(exc),
                'exception':type(exc).__name__,'inputs_sha256':reader.pins,'target_resolution':'NONE','automatic_retry':False,
                'timestamp':datetime.now(timezone.utc).isoformat()},indent=2,allow_nan=False)+'\n',encoding='utf8')
        except Exception:
            pass
        raise

if __name__ == '__main__':
    main()
