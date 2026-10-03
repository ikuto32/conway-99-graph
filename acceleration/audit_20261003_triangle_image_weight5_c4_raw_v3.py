"""Independent complete C4 raw audit, calibrated before discovery-output reads."""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import platform
import sys
from command_deadline import CommandDeadline
import audit_20261003_triangle_image_weight5_core_v1 as P
import audit_20261003_triangle_image_weight5_c4_controls_v3 as C

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/audit_20261003_triangle_image_weight5_c4_raw_v3.py'
SPEC = 'acceleration/audit_20261003_triangle_image_weight5_c4_raw_v3_spec.md'
INPUT = 'acceleration/results/20261003_triangle_image_weight5_controls01/actual_graph_fixtures.json'
PRODUCER = 'acceleration/theory_20261003_triangle_image_weight5_c4_v2.py'
PINS = {
    INPUT: 'c2c1fe1c6c861b7e85ee8b56a5f999651b243af4600efd69149410f0943aa2fd',
    PRODUCER: 'f10cc3f06d0178ff73ea9db547fb01662e3f65ae8f3664e1abf637667dc4fd87',
    'acceleration/theory_20261003_triangle_image_weight5_c4_v2_spec.md': 'd84d894f7f69f26d236ae0020ea9ee8cb069a8373c47135bed4076853fddd843',
    'acceleration/theory_20261003_triangle_image_weight5_c4_v1.py': 'f9203c6c1aeab51849a7511c918cfbd97e2c9348883ddaf3450e058562fde2d0',
    'acceleration/theory_20261003_triangle_image_weight5_c4_v1_spec.md': '4832b3c40f8e5f9d9cb34fa4f9da808064df86d5b5a0b5d5a803217b415dd7ee',
    'acceleration/results/20261003_triangle_image_weight5_c4_controls01/failure.json': 'c6ce45e1872d3058feaae794fe210bded6e13ce231d4d639110200b5d9d33074',
    'acceleration/audit_20261003_triangle_image_weight5_c4_raw_v2.py': 'a0e0b0d269bfa7140f7d084b7c4b901fffa90a4a057ba95bb3cc095d0d99892b',
    'acceleration/audit_20261003_triangle_image_weight5_c4_raw_v2_spec.md': '6d8969282394d9271c5a64da298dc40e0722206d9553b77fd5ea8e84c709bc06',
    'acceleration/results/20261003_independent_review/weight5_c4_raw_calibration02/summary.json': '55f3d18dd6dc5de2c9d194db2cf943a43c8d104edf0a2493fb935781017919f4',
    'acceleration/audit_20261003_triangle_image_weight5_core_v1.py': '7e9813b687afd83551d1beecce01a00b525f51b6ba25c769c76fc5efb7385848',
    'acceleration/audit_20261003_triangle_image_weight5_c4_controls_v3.py': '45e0e95a35f48acd7e569db4b049ae2b3453ac7905e7961a6f8cd5ac0ad7a6aa',
    'acceleration/audit_20261003_triangle_image_weight5_c4_v1.md': 'bdc99b2f6a2bf92f9e322616227c4be26db7d57b08ccbcfd9353fbf76260ce12',
    'acceleration/audit_20261003_triangle_image_weight5_c4_v1_proof.md': '7099b2780b3fe1b8abdbbdb9bff30b2993df6599cb39b3959655eb673ac4a90a',
    'acceleration/audit_20261003_triangle_image_weight5_v1_proof.md': '8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee',
    'acceleration/results/20261003_independent_review/weight5_full02/summary.json': 'dedb5c3affcfd0edb98a1d97ebdc973290b53b67ecbb76f3d78135b2bea688f2',
    'acceleration/results/20261003_independent_review/weight5_c4_calibration01/summary.json': 'de1cde6369b81961c7c658a4ce1ffa41413fdc7d66d3fcccea6c4c57b24881c9',
}


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def adjacency(n, edges):
    need(type(n) is int and n >= 0 and type(edges) is list, 'RAW_DOMAIN')
    rows = [set() for _ in range(n)]
    need(all(type(e) is list and len(e) == 2 and all(type(v) is int and 0 <= v < n for v in e)
             and e[0] < e[1] for e in edges) and edges == sorted(edges)
             and len(set(map(tuple, edges))) == len(edges), 'RAW_DOMAIN')
    for u, v in edges:
        rows[u].add(v)
        rows[v].add(u)
    need(all(len(rows[u] & rows[v]) == 1 for u, v in edges), 'EDGE_CN1_PREMISE')
    return rows


def expected(label, n, edges):
    rows = adjacency(n, edges)
    checked = C.complete(rows)
    triangles = checked['actual_triangles']
    path_ids = {tuple(row['path']) for row in checked['paths']}
    trios = []
    for ids in combinations(range(len(triangles)), 3):
        chosen = [triangles[i] for i in ids]
        word = P.points(P.mask(chosen[0]) ^ P.mask(chosen[1]) ^ P.mask(chosen[2]))
        trios.append(dict(triangle_indices=list(ids),
            intersection_sizes=[len(set(chosen[a]) & set(chosen[b])) for a, b in [(0,1),(0,2),(1,2)]],
            support=word, is_path=ids in path_ids))
    fibers = {}
    for path in checked['paths']:
        fibers.setdefault(tuple(path['support']), []).append(sorted(triangles[i] for i in path['path']))
    raw_fibers = [dict(support=list(word), path_triangle_sets=sorted(preimages), multiplicity=len(preimages))
                  for word, preimages in sorted(fibers.items())]
    cycles = []
    for q in checked['induced_cycles']:
        a, *rest = q
        matches = []
        for b in rest:
            other = [v for v in rest if v != b]
            if b in rows[a] and other[1] in rows[other[0]]:
                matches.append([[a,b],other])
        cycles.append(dict(vertices=q, induced_edges=[list(e) for e in combinations(q,2) if e[1] in rows[e[0]]],
                           perfect_matchings=sorted(matches)))
    doubles = []
    for item in checked['double_fibers']:
        p, t = item['canonical_hidden_points']
        r = item['isolated']
        matching = item['canonical_matching']
        recovered = sorted([sorted([*matching[0],p]),sorted([*matching[1],t]),sorted([p,t,r])])
        preimages = sorted(sorted(triangles[i] for i in ids) for ids in item['path_preimages'])
        need(recovered in preimages, 'INDEPENDENT_CANONICAL_RECOVERY')
        doubles.append(dict(support=item['support'],isolated_vertex=r,cycle_vertices=item['cycle'],
            canonical_matching=matching,canonical_edge_completions=[p,t],central_edge=sorted([p,t]),
            central_completion=r,canonical_path_triangles=recovered,two_path_triangle_sets=preimages))
    # Enumerate coefficient vectors by independent column doubling in mask order.
    image = [0]
    for triangle in triangles:
        column = P.mask(triangle)
        image += [value ^ column for value in image]
    image_records = [dict(coefficient_mask=i,support=P.points(word)) for i,word in enumerate(image)]
    image5 = sorted({tuple(P.points(word)) for word in image if word.bit_count() == 5})
    need(len(image5) == checked['complete_weight5_words'], 'INDEPENDENT_COMPLETE_IMAGE')
    paths, c4 = checked['path_count'], checked['cycle_count']
    return dict(schema='TRIANGLE_IMAGE_WEIGHT5_C4_COLLISION_FIXTURE_V1',label=label,vertices=n,edges=edges,
        actual_triangles=triangles,vertex_triangle_counts=[sum(v in row for row in triangles) for v in range(n)],
        all_triangle_triples=trios,path_records=[row for row in trios if row['is_path']],support_fibers=raw_fibers,
        induced_c4_records=cycles,double_fiber_cycle_map=doubles,path_count=paths,
        irregular_path_formula=P.formula(triangles,n),cycle_count=c4,double_fiber_count=checked['double_fiber_count'],
        distinct_path_words=checked['distinct_path_words'],old_half_path_lower=(paths+1)//2,
        subtracted_cycle_lower=paths-c4,strengthened_lower=max((paths+1)//2,paths-c4),
        complete_small_image_records=image_records,complete_small_image_weight5_words=[list(word) for word in image5])


def check_fixture(raw, wanted):
    need(type(raw) is dict and raw.keys() == wanted.keys(), 'RAW_SCHEMA')
    for key, stage in [('actual_triangles','RAW_ACTUAL_TRIANGLES'),('all_triangle_triples','RAW_COMPLETE_TRIPLES'),
                       ('path_records','RAW_COMPLETE_PATHS'),('support_fibers','RAW_COMPLETE_FIBERS'),
                       ('induced_c4_records','RAW_COMPLETE_C4S')]:
        need(same(raw[key],wanted[key]),stage)
    maps = raw['double_fiber_cycle_map']
    need(type(maps) is list and all(type(m) is dict and type(m.get('support')) is list
             and all(type(v) is int for v in m['support']) for m in maps),'RAW_MAP_INTEGER_SUPPORT')
    need(len({tuple(m['cycle_vertices']) for m in maps}) == len(maps),'RAW_MAP_INJECTION')
    need(same(maps,wanted['double_fiber_cycle_map']),'RAW_EXACT_COLLISION_MAP')
    for key in ['path_count','cycle_count','double_fiber_count','distinct_path_words','strengthened_lower']:
        need(same(raw[key],wanted[key]),'RAW_EXACT_COUNTS')
    for key in ['complete_small_image_records','complete_small_image_weight5_words']:
        need(same(raw[key],wanted[key]),'RAW_COMPLETE_IMAGE')
    need(same(raw,wanted),'RAW_COMPLETE_RECORD')


def target():
    coefficients = [C.poly5(99,w) for w in range(100)]
    need(coefficients == [P.krawtchouk(99,5,w) for w in range(100)],'INDEPENDENT_CHARACTER_PATHS')
    paths = (99*14//6)*3*6*6
    nonedges = 99*84//2
    lower = paths-nonedges//2
    rhs = comb(99,5)-lower
    fractions = [Fraction(lower-coefficients[w],rhs) for w in range(1,100)]
    return dict(schema='TRIANGLE_IMAGE_WEIGHT5_C4_TARGET_CHARACTER_V1',length=99,triangle_incidence_degree=7,
        actual_triangle_count_conditional=231,unordered_paths=paths,unordered_nonedges=nonedges,
        induced_c4_count=nonedges//2,image_weight5_lower=lower,degree=5,krawtchouk_by_weight0to99=coefficients,
        shifted_rhs=rhs,normalized_coefficient_pairs_by_weight1to99=[[f.numerator,f.denominator] for f in fractions],
        target_resolution='NONE')


def check_target(raw,wanted):
    need(type(raw) is dict and raw.keys() == wanted.keys(),'TARGET_SCHEMA')
    for key,stage in [('induced_c4_count','TARGET_C4_DOUBLECOUNT'),('image_weight5_lower','TARGET_COLLISION_SUBTRACTION'),
                       ('shifted_rhs','TARGET_CHARACTER_ZERO_WORD')]:
        need(same(raw[key],wanted[key]),stage)
    need(same(raw['krawtchouk_by_weight0to99'],wanted['krawtchouk_by_weight0to99'])
         and same(raw['normalized_coefficient_pairs_by_weight1to99'],wanted['normalized_coefficient_pairs_by_weight1to99']),
         'TARGET_ALL_EXACT_COEFFICIENTS')
    need(same(raw,wanted),'TARGET_COMPLETE_RECORD')


def check_relabel(raw,rook):
    permutation = [1,0,2,3,4,5,6,7,8]
    need(type(raw) is dict and set(raw)=={'schema','vertex_permutation','relabelled_fixture','support_cycle_map_equivariance_checked','original_label'}
         and raw['schema']=='WEIGHT5_C4_RELABEL_CONTROL_V1' and same(raw['vertex_permutation'],permutation)
         and raw['support_cycle_map_equivariance_checked'] is True and raw['original_label']=='rook9','RELABEL_SCHEMA')
    edges = sorted([sorted([permutation[u],permutation[v]]) for u,v in rook['edges']])
    wanted = expected('rook9_transposition01',9,edges)
    check_fixture(raw['relabelled_fixture'],wanted)
    transport = lambda values:tuple(sorted(permutation[v] for v in values))
    original_pairs = sorted((transport(m['support']),transport(m['cycle_vertices'])) for m in rook['double_fiber_cycle_map'])
    new_pairs = sorted((tuple(m['support']),tuple(m['cycle_vertices'])) for m in wanted['double_fiber_cycle_map'])
    need(original_pairs == new_pairs,'PAIRED_RELABEL_EQUIVARIANCE')
    return wanted


def mutation_cases(rook,character):
    result = []
    def add(name,stage,change):
        raw = copy.deepcopy(rook);change(raw);result.append((name,stage,raw,'fixture'))
    add('missing_cycle','RAW_COMPLETE_C4S',lambda x:x['induced_c4_records'].pop())
    add('missing_collision_map','RAW_EXACT_COLLISION_MAP',lambda x:x['double_fiber_cycle_map'].pop())
    add('wrong_isolated','RAW_EXACT_COLLISION_MAP',lambda x:x['double_fiber_cycle_map'][0].update(isolated_vertex=x['double_fiber_cycle_map'][0]['cycle_vertices'][0]))
    add('wrong_completion','RAW_EXACT_COLLISION_MAP',lambda x:x['double_fiber_cycle_map'][0]['canonical_edge_completions'].__setitem__(0,99))
    add('boolean_support','RAW_MAP_INTEGER_SUPPORT',lambda x:x['double_fiber_cycle_map'][0]['support'].__setitem__(0,True))
    add('count_preserving_duplicate_cycle_map','RAW_MAP_INJECTION',lambda x:x['double_fiber_cycle_map'].__setitem__(1,copy.deepcopy(x['double_fiber_cycle_map'][0])))
    add('count_preserving_matching_permutation','RAW_EXACT_COLLISION_MAP',lambda x:x['double_fiber_cycle_map'][0].update(canonical_matching=copy.deepcopy(x['double_fiber_cycle_map'][1]['canonical_matching'])))
    for name,key,value in [('wrong_double_count','double_fiber_count',8),('false_path_injection','distinct_path_words',18),('overstated_word_lower','strengthened_lower',10)]:
        add(name,'RAW_EXACT_COUNTS',lambda x,key=key,value=value:x.update({key:value}))
    add('missing_path','RAW_COMPLETE_PATHS',lambda x:x['path_records'].pop())
    add('changed_image','RAW_COMPLETE_IMAGE',lambda x:x['complete_small_image_weight5_words'].pop())
    for name,key,value,stage in [('wrong_target_c4','induced_c4_count',2078,'TARGET_C4_DOUBLECOUNT'),
        ('wrong_target_lower','image_weight5_lower',22870,'TARGET_COLLISION_SUBTRACTION'),
        ('omitted_zero_word_constant','shifted_rhs',71500274,'TARGET_CHARACTER_ZERO_WORD')]:
        raw=copy.deepcopy(character);raw[key]=value;result.append((name,stage,raw,'target'))
    raw=copy.deepcopy(character);raw['krawtchouk_by_weight0to99'][36]+=1
    result.append(('changed_exact_coefficient','TARGET_ALL_EXACT_COEFFICIENTS',raw,'target'))
    return result


def reject(name,stage,callback,controls):
    try:
        callback()
    except ValueError as error:
        need(type(error) is ValueError and str(error)==stage,'PRECISE_NEGATIVE_STAGE:'+name)
        controls.append(dict(case=name,stage=stage,outcome='REJECTED'))
        return
    raise ValueError('CORRUPTION_ACCEPTED:'+name)


def pending_metadata(report):
    need(report['status']=='AUTHOR_WEIGHT5_C4_COLLISION_CONTROLS_PASS_PENDING_INDEPENDENT_RAW_AUDIT'
         and report['producer']=='/root/structural' and report['independent_approval'] is False
         and report['target_resolution']=='NONE' and report['rank_bound_claimed'] is False
         and all(type(report[key]) is int and report[key]==0 for key in ['numerical_solver_invocations','graph_exclusions']),
         'ACTUAL_PENDING_SCOPE')


def raw_calibration_metadata(cal,source_sha):
    need(cal['status']=='INDEPENDENT_WEIGHT5_C4_RAW_V1_CALIBRATION_PASS' and cal['producer_outputs_checked'] is False
         and cal['inputs_sha256'][SOURCE]==source_sha and type(cal['strict_interface_corruptions']) is int
         and cal['strict_interface_corruptions']==27,'NEW_RAW_CALIBRATION')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['calibration','full'])
    parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',required=True)
    parser.add_argument('--calibration');parser.add_argument('--calibration-sha256')
    parser.add_argument('--producer-summary');parser.add_argument('--producer-summary-sha256')
    parser.add_argument('--supervisor');parser.add_argument('--supervisor-sha256')
    args=parser.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='Complete seven finite raw C4 fixtures, paired relabel, saved negative artifacts and100/99exact target coefficients;10seconds preserve reserve')
    out=(ROOT/args.out).resolve();need(out.is_relative_to(ROOT),'WORKSPACE_OUTPUT');out.mkdir(parents=True,exist_ok=False)
    pins={};controls=[];protected={name:sha(ROOT/name) for name in ['CLAIMS.yaml','.git/index']}
    def pin(name,wanted=None):
        need(deadline.status()['remaining_seconds']>10,'PRESERVATION_RESERVE')
        path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'WORKSPACE_INPUT')
        identity=sha(path);need(wanted is None or identity==wanted,'INPUT_HASH:'+name)
        need(name not in pins or pins[name]==identity,'CONSISTENT_IDENTITY:'+name);pins[name]=identity
        return load(path) if path.suffix=='.json' else None
    def closure(report):
        for name,identity in report['inputs_sha256'].items():pin(name,identity)
    try:
        for name,identity in PINS.items():pin(name,identity)
        for name in [SOURCE,SPEC,'acceleration/audit_20261003_triangle_image_weight5_c4_raw_v1.py',
                     'acceleration/audit_20261003_triangle_image_weight5_c4_raw_v1_spec.md',
                     'acceleration/results/20261003_independent_review/weight5_c4_raw_calibration01/summary.json',
                     'pyproject.toml','uv.lock','acceleration/command_deadline.py','acceleration/run_compute_command.py']:pin(name)
        old=load(ROOT/'acceleration/results/20261003_independent_review/weight5_full02/summary.json');closure(old)
        prior_cal=load(ROOT/'acceleration/results/20261003_independent_review/weight5_c4_calibration01/summary.json');closure(prior_cal)
        need(prior_cal['status']=='INDEPENDENT_WEIGHT5_C4_COLLISION_CHECKER_V3_CALIBRATION_PASS'
             and prior_cal['producer_outputs_checked'] is False,'PRIOR_INDEPENDENT_CALIBRATION')
        fixtures=load(ROOT/INPUT)
        labels=['single_triangle','friendship7','one_intersection_plus_disjoint','loose_chain3','three_disjoint','loose_cycle4','rook9']
        need([row['label'] for row in fixtures]==labels,'FROZEN_SELECTION')
        expected_rows=[expected(row['label'],row['vertices'],row['edges']) for row in fixtures]
        need([expected_rows[1]['vertices'],len(expected_rows[1]['actual_triangles'])]==[15,7],'ACTUAL_FRIENDSHIP_FIFTEEN')
        for row in expected_rows:check_fixture(copy.deepcopy(row),row)
        character=target();check_target(copy.deepcopy(character),character)
        rook=expected_rows[-1]
        tiny_rows=adjacency(9,rook['edges']);need(C.srg_cycles(tiny_rows,4)==9,'KNOWN_EXACT_CYCLE_FORMULA')
        known_cases=mutation_cases(rook,character)
        for name,stage,raw,kind in known_cases:
            reject(name,stage,lambda raw=raw,kind=kind:check_fixture(raw,rook) if kind=='fixture' else check_target(raw,character),controls)
        def missing_mu(rows):
            need(all(len(rows[u]&rows[v])==2 for u,v in combinations(range(len(rows)),2) if v not in rows[u]),'NONEDGE_CN2_PREMISE')
        k7=[list(pair) for pair in combinations(range(7),2)]
        two=rook['edges']+[[u+9,v+9] for u,v in rook['edges']]
        reject('k7_missing_lambda','EDGE_CN1_PREMISE',lambda:adjacency(7,k7),controls)
        reject('two_rooks_missing_mu2','NONEDGE_CN2_PREMISE',lambda:missing_mu(adjacency(18,two)),controls)
        edges=sorted([sorted([1 if u==0 else 0 if u==1 else u,1 if v==0 else 0 if v==1 else v]) for u,v in rook['edges']])
        relabel=dict(schema='WEIGHT5_C4_RELABEL_CONTROL_V1',vertex_permutation=[1,0,2,3,4,5,6,7,8],
                     relabelled_fixture=expected('rook9_transposition01',9,edges),support_cycle_map_equivariance_checked=True,original_label='rook9')
        check_relabel(relabel,rook)
        # Independent interface controls additionally cover omitted schema,
        # count booleans, ignored formula and normalized rational corruption.
        for name,stage,key,value in [('bool_path_count','RAW_EXACT_COUNTS','path_count',True),
                ('wrong_irregular_formula','RAW_COMPLETE_RECORD','irregular_path_formula',19),
                ('wrong_vertex_counts','RAW_COMPLETE_RECORD','vertex_triangle_counts',[0]*9)]:
            bad=copy.deepcopy(rook);bad[key]=value
            reject(name,stage,lambda bad=bad:check_fixture(bad,rook),controls)
        bad=copy.deepcopy(rook);bad.pop('schema')
        reject('missing_schema','RAW_SCHEMA',lambda:check_fixture(bad,rook),controls)
        bad=copy.deepcopy(character);bad['normalized_coefficient_pairs_by_weight1to99'][0][0]+=1
        reject('changed_normalized_fraction','TARGET_ALL_EXACT_COEFFICIENTS',lambda:check_target(bad,character),controls)
        bad=copy.deepcopy(relabel);bad['vertex_permutation'][0]=True
        reject('bool_permutation','RELABEL_SCHEMA',lambda:check_relabel(bad,rook),controls)
        minimal=dict(status='AUTHOR_WEIGHT5_C4_COLLISION_CONTROLS_PASS_PENDING_INDEPENDENT_RAW_AUDIT',
                     producer='/root/structural',independent_approval=False,target_resolution='NONE',
                     rank_bound_claimed=False,numerical_solver_invocations=0,graph_exclusions=0)
        pending_metadata(minimal)
        for key,value in [('numerical_solver_invocations',False),('graph_exclusions',0.0)]:
            bad=copy.deepcopy(minimal);bad[key]=value
            reject('literal_'+key,'ACTUAL_PENDING_SCOPE',lambda bad=bad:pending_metadata(bad),controls)
        simulated_cal=dict(status='INDEPENDENT_WEIGHT5_C4_RAW_V1_CALIBRATION_PASS',producer_outputs_checked=False,
                           inputs_sha256={SOURCE:pins[SOURCE]},strict_interface_corruptions=27)
        raw_calibration_metadata(simulated_cal,pins[SOURCE])
        bad=copy.deepcopy(simulated_cal);bad['strict_interface_corruptions']=27.0
        reject('float_calibration_population','NEW_RAW_CALIBRATION',lambda:raw_calibration_metadata(bad,pins[SOURCE]),controls)
        save(out/'independent_fixture_records.json',expected_rows);save(out/'independent_target_row.json',character)
        save(out/'independent_interface_controls.json',controls)
        scope='INDEPENDENT_WEIGHT5_C4_RAW_V1_CALIBRATION_PASS'
        actual_negative_count=0
        if args.mode=='full':
            need(all([args.calibration,args.calibration_sha256,args.producer_summary,args.producer_summary_sha256,args.supervisor,args.supervisor_sha256]),'EXPLICIT_ACTUAL_IDENTITIES')
            cal=pin(args.calibration,args.calibration_sha256)
            raw_calibration_metadata(cal,pins[SOURCE])
            closure(cal)
            terminal=pin(args.supervisor,args.supervisor_sha256);cleanup=terminal['cleanup']
            need(terminal['command_exit_code']==0 and terminal['stop_reason']=='COMMAND_EXITED' and terminal['error'] is None
                 and terminal['deadline_reached'] is False and cleanup['reaped'] is True and cleanup['job_active_zero_observed'] is True
                 and cleanup['cleanup_errors']==[],'ACTUAL_CONTAINED_EXIT')
            report=pin(args.producer_summary,args.producer_summary_sha256)
            pending_metadata(report)
            need(type(report.get('implementation_version')) is int and report['implementation_version']==2
                 and report['inputs_outputs_sha256'].get(PRODUCER)==PINS[PRODUCER], 'EXACT_CHANGED_PRODUCER_V2')
            for name,identity in report['inputs_outputs_sha256'].items():pin(name,identity)
            folder=(ROOT/args.producer_summary).parent
            def raw(name):
                member=(folder/name).relative_to(ROOT).as_posix()
                need(member in report['inputs_outputs_sha256'],'RECORDED_RAW_MEMBER:'+name)
                return pin(member,report['inputs_outputs_sha256'][member])
            actual=raw('actual_graph_fixtures.json');need(type(actual) is list and len(actual)==7,'ACTUAL_SEVEN')
            for i,(row,wanted) in enumerate(zip(actual,expected_rows)):
                check_fixture(row,wanted);need(same(raw('fixture_'+str(i).zfill(2)+'.json'),row),'ACTUAL_DUPLICATE_FIXTURE')
            check_target(raw('target_character_row.json'),character)
            check_relabel(raw('permutation_control.json'),rook)
            negatives=raw('strict_controls.json');need(type(negatives) is list and len(negatives)==18,'ALL_SAVED_NEGATIVES')
            need([r['case'] for r in negatives]==[r[0] for r in known_cases]+['k7_missing_lambda','two_rooks_missing_mu2'],'EXACT_NEGATIVE_SELECTION')
            actual_checks=[]
            for record,(name,stage,wanted,kind) in zip(negatives,known_cases):
                need(record['expected_stage']==record['observed_stage']==stage and record['raw_path']==name+'.json','AUTHOR_PRECISE_STAGE')
                observed=raw(record['raw_path']);need(same(observed,wanted),'EXACT_SAVED_MUTATION:'+name)
                reject(name,stage,lambda observed=observed,kind=kind:check_fixture(observed,rook) if kind=='fixture' else check_target(observed,character),actual_checks)
            premises=raw('missing_premises.json')
            need(same(premises,dict(k7=dict(vertices=7,edges=k7),two_rooks=dict(vertices=18,edges=two))),'ACTUAL_MISSING_PREMISES')
            for r in negatives[-2:]:need(r['expected_stage']==r['observed_stage'] and 'raw_path' not in r,'AUTHOR_PREMISE_STAGE')
            need(negatives[-2]['expected_stage']=='EDGE_CN1_PREMISE' and negatives[-1]['expected_stage']=='NONEDGE_CN2_PREMISE','AUTHOR_PREMISE_STAGES')
            reject('k7_missing_lambda','EDGE_CN1_PREMISE',lambda:adjacency(premises['k7']['vertices'],premises['k7']['edges']),actual_checks)
            reject('two_rooks_missing_mu2','NONEDGE_CN2_PREMISE',lambda:missing_mu(adjacency(premises['two_rooks']['vertices'],premises['two_rooks']['edges'])),actual_checks)
            save(out/'actual_strict_controls.json',actual_checks);actual_negative_count=len(actual_checks)
            scope='INDEPENDENT_WEIGHT5_C4_COLLISION_COMPLETE_RAW_V1_PASS'
        counts=[len(expected_rows),sum(len(r['all_triangle_triples']) for r in expected_rows),sum(r['path_count'] for r in expected_rows),
            sum(r['distinct_path_words'] for r in expected_rows),sum(r['cycle_count'] for r in expected_rows),
            sum(r['double_fiber_count'] for r in expected_rows),sum(len(r['complete_small_image_records']) for r in expected_rows)]
        need(counts==[7,62,23,14,10,9,234],'COMPLETE_FROZEN_POPULATION')
        need(all(sha(ROOT/name)==identity for name,identity in protected.items()),'PROTECTED_STATE_CHANGED')
        save(out/'summary.json',dict(status=scope,checker_implementation_version=3,timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/structural',verifier='/root',
            method='independent_derivation_and_complete_artifact_checking',claim_revision=1,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=pins,complete_original_fixtures=7,complete_three_triangle_combinations=62,unordered_paths=23,separate_fixture_supports=14,
            complete_induced_c4s=10,complete_double_fibers=9,complete_small_image_coefficient_masks=234,positive_relabelled_fixtures=1,
            paired_relabel_map_checked=True,strict_interface_corruptions=len(controls),actual_saved_strict_corruptions=actual_negative_count,
            producer_outputs_checked=args.mode=='full',complete_character_coefficients=100,complete_normalized_weights=99,
            target_unordered_paths=24948,target_induced_c4_count=2079,target_weight5_lower_count=22869,target_character_rhs=71500275,
            universal_derivation_checked=True,written_audit=C.PROOF,written_audit_sha256=C.PROOF_SHA,
            universal_statement='For every finite simple graph with exactly one common neighbor for each adjacent pair, the binary triangle-incidence image contains at least max(ceil(P/2), P-c4(G)) weight-five words, where P is the unordered three-triangle path count and c4(G) the induced four-cycle count. Consequently any srg(99,14,1,2) has N5>=22869 and its exact degree-five kernel-character shifted right-hand side is71500275.',
            target_resolution='NONE',graph_exclusions=0,rank_asserted=False,numerical_solver_invocations=0,ledger_mutations=0,index_mutations=0,
            historical_protected_execution_state=protected,deadline=deadline.status(),
            shared_components=['Own prior calibrated independent inverse core7e981 and collision core45e reused; discovery producer never imported.',
                'Complete coefficient vectors independently rebuilt by column doubling; target polynomial convolution and binomial paths both checked.',
                'Declared JSON serialization/canonical matching format shared; raw types, full fibers, paired relabel and every record independently rebuilt.',
                'Python exact arithmetic/sets/Fraction, JSON, SHA256, locked runtime and command deadline trusted.'],
            limitations=['Universal conclusion relies on written independent inverse and C4 injection proofs, not finite agreement.',
                'Original friendship7 artifact has15vertices/7triangles; prior collision calibration friendship7 has7vertices/3triangles, separately scoped.',
                'Calibration mode approves its raw interface only; full mode additionally checks all new actual discovery raw artifacts.',
                'No nonzero kernel, rank bound, optimum, unrestricted exclusion, target resolution, novelty or external review.']))
        print(scope)
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,completed_interface_controls=controls,deadline=deadline.status(),outputs_preserved=True))
        raise


if __name__=='__main__':main()
