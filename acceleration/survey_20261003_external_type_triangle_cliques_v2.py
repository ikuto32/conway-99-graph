"""Source-only complete weighted-triangle diagnostic; no LP or graph search."""
import argparse, copy, hashlib, itertools, json, math, re, sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
MODEL = 'acceleration/results/20261003_external_moment_triple_lp01/triple_system.json'
PRIMAL = 'acceleration/results/20261003_external_moment_triple_lp01/triple_primal.json'
TYPES = 'acceleration/results/20261003_external_moment_outside_cn_filter01/types.json'
LEMMA = 'acceleration/results/20261003_independent_review/exterior_type_pair_triple_caps01/summary.json'
FIXED = {
 MODEL: '6226df2a75d8bf296b77f8e636a8e3fc5d1764d378dd7779cd08bad2d9a4c792',
 PRIMAL: 'e311192634b43b00e5c0b2e4d34cff62bcb38aaa59de1aae91450b5e004218da',
 TYPES: '87d0272e244f60f1eefa06d3a0b2d0179a275791f7bb586992b16f648595bad2',
 LEMMA: 'd3e2f27aca979839edb3e612cd825d2cce18346d81ca2bfa868e86b6b1baffee'}
SOFTWARE = {
 'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db'}
FULL = 'INDEPENDENT_TRIPLE_CAPPED_EXTERNAL_MOMENT_CERTIFICATE_V1_COMPLETE_PASS'
CAL = 'EXTERNAL_TYPE_TRIANGLE_CLIQUES_V1_AUTHOR_CALIBRATION_PASS'


def need(ok, stage):
    if not ok: raise ValueError(stage)


def strict_json(raw):
    need(type(raw) is bytes and len(raw) <= 64 * 1024**2, 'JSON_BYTES')
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'JSON_DUPLICATE')
            result[key] = value
        return result
    def nonfinite(_): raise ValueError('JSON_NONFINITE')
    return json.loads(raw.decode('utf8'), object_pairs_hook=pairs, parse_constant=nonfinite)


def rational_vector(raw, count):
    need(type(raw) is list and len(raw) == count, 'WEIGHT_SHAPE')
    result = []
    for value in raw:
        need(type(value) is str, 'WEIGHT_STRING')
        try: number = Fraction(value)
        except (ValueError, ZeroDivisionError): raise ValueError('WEIGHT_CANONICAL') from None
        need(str(number) == value, 'WEIGHT_CANONICAL')
        need(number >= 0, 'WEIGHT_NONNEGATIVE')
        result.append(number)
    return result


def mask_list(raw, m):
    need(type(m) is int and m >= 3, 'DOMAIN_INTEGER')
    need(type(raw) is list and all(type(v) is int and 0 <= v < 1 << m for v in raw), 'MASK_INTEGER')
    need(raw == sorted(set(raw)), 'MASK_ORDER')
    return raw


def population(masks, weights, m):
    mask_list(masks, m)
    values = rational_vector(weights, len(masks))
    # Strictly positive canonical rationals; no floating/tolerance selection.
    return [dict(column=i, mask=mask, cardinality=mask.bit_count(), weight=str(value))
            for i, (mask, value) in enumerate(zip(masks, values)) if mask.bit_count() >= 3 and value > 0]


def triangle_scan(selected, pair_save, triangle_save, violation_save, guard):
    n = len(selected); neighbors = [set() for _ in selected]
    edges = 0; pairs = 0; pair_violations = 0
    for i in range(n):
        for j in range(i + 1, n):
            guard(); intersection = (selected[i]['mask'] & selected[j]['mask']).bit_count()
            incompatible = intersection >= 3
            pair_sum = Fraction(selected[i]['weight']) + Fraction(selected[j]['weight'])
            pair_save(dict(positions=[i, j], columns=[selected[i]['column'], selected[j]['column']],
                           intersection_cardinality=intersection, incompatible=incompatible,
                           weights=[selected[i]['weight'], selected[j]['weight']], exact_sum=str(pair_sum),
                           pair_inequality_violated=incompatible and pair_sum > 1))
            pairs += 1
            if incompatible:
                neighbors[i].add(j); neighbors[j].add(i); edges += 1
                if pair_sum > 1: pair_violations += 1
    triangles = violations = 0; max_sum = None
    for i in range(n):
        guard()
        for j in sorted(k for k in neighbors[i] if k > i):
            guard()
            for k in sorted(q for q in neighbors[i] & neighbors[j] if q > j):
                guard(); total = sum((Fraction(selected[q]['weight']) for q in [i, j, k]), Fraction(0))
                item = dict(positions=[i, j, k], columns=[selected[q]['column'] for q in [i, j, k]],
                    masks=[selected[q]['mask'] for q in [i, j, k]], weights=[selected[q]['weight'] for q in [i, j, k]],
                    exact_sum=str(total), threshold='1', violated=total > 1)
                triangle_save(item); triangles += 1
                if max_sum is None or total > max_sum: max_sum = total
                if total > 1: violation_save(item); violations += 1
    need(pairs == math.comb(n, 2), 'COMPLETE_PAIR_POPULATION')
    return dict(positive_types=n, unordered_pairs=pairs, incompatible_pairs=edges, violated_incompatible_pairs=pair_violations,
                all_three_subsets=math.comb(n, 3), triangle_cliques=triangles,
                violated_triangle_cliques=violations, maximum_triangle_sum=None if max_sum is None else str(max_sum))


def gate_header(raw):
    need(type(raw) is dict and raw.get('status') == FULL and raw.get('producer') == '/root/checkpoint_audit'
         and raw.get('verifier') == '/root/structural' and raw.get('method') == 'independent_artifact_check'
         and raw.get('target_resolution') == 'NONE' and type(raw.get('implementation_version')) is int
         and raw['implementation_version'] == 2, 'EXACT_PRIMAL_GATE_HEADER')
    outcome = raw.get('outcome')
    need(type(outcome) is dict and outcome.get('certificate_kind') == 'primal'
         and all(type(outcome.get(key)) is int and outcome[key] == value for key, value in
                 [('rows', 834), ('variables', 1152), ('original_variables', 472), ('original_equations', 154), ('triple_caps', 680)]),
         'EXACT_PRIMAL_GATE_SCOPE')


def own_controls(save, guard):
    rows = []
    def scan(ms, ws, m=9):
        p = population(ms, ws, m); pairs=[]; triangles=[]; bad=[]
        result = triangle_scan(p, pairs.append, triangles.append, bad.append, guard)
        return dict(population=p, pairs=pairs, triangles=triangles, violations=bad, counts=result)
    def positive(label, ms, ws, expected):
        result = scan(ms, ws)
        need(result['counts']['triangle_cliques'] == expected[0]
             and result['counts']['violated_triangle_cliques'] == expected[1], 'CONTROL_TRIANGLE_RESULT')
        save('control_' + label + '.json', dict(masks=ms, weights=ws, result=result, synthetic=True))
        rows.append(dict(case=label, expected_stage='PASS', actual_stage='PASS'))
    # Pair intersections are different disjoint triples; no common three-point Q.
    positive('pairwise_without_common_Q', [63,455,504], ['1/2']*3, [1,1])
    base=scan([63,455,504], ['1/2']*3)
    need(base['triangles'][0]['exact_sum']=='3/2' and base['counts']['violated_incompatible_pairs']==0,
         'CONTROL_EXACT_THRESHOLD')
    Q_sums=[sum((Fraction('1/2') for T in [63,455,504] if T & sum(1<<i for i in Q)==sum(1<<i for i in Q)),Fraction(0))
            for Q in itertools.combinations(range(9),3)]
    need(max(Q_sums)==1 and (63 & 455 & 504).bit_count()==0, 'CONTROL_NO_COMMON_Q')
    save('control_pairwise_without_common_Q_cuts.json',dict(all84_Q_sums=list(map(str,Q_sums)),maximum='1',common_intersection_size=0))
    positive('exact_one_not_violated', [63,455,504], ['1/3']*3, [1,0])
    positive('below_one', [63,455,504], ['1/4']*3, [1,0])
    positive('one_edge_not_triangle', [7,15,28], ['1/2']*3, [0,0])
    positive('small_and_zero_excluded', [1,7,63,455,504], ['99','0','1/2','1/2','1/2'], [1,1])
    header=dict(status=FULL, producer='/root/checkpoint_audit', verifier='/root/structural', method='independent_artifact_check',
        target_resolution='NONE', implementation_version=2, outcome=dict(certificate_kind='primal', rows=834, variables=1152,
        original_variables=472, original_equations=154, triple_caps=680))
    gate_header(header); save('control_genuine_primal_header.json', header)
    rows.append(dict(case='genuine_primal_header', expected_stage='PASS', actual_stage='PASS'))
    def negative(label, stage, payload, action):
        try: action()
        except ValueError as error: need(str(error) == stage, 'CONTROL_WRONG_STAGE:' + label)
        else: raise ValueError('CONTROL_FALSE_ACCEPT:' + label)
        save('control_' + label + '.json', dict(payload=payload, expected_stage=stage, actual_stage=stage, synthetic=True))
        rows.append(dict(case=label, expected_stage=stage, actual_stage=stage))
    for label, ms, stage in [('bool_mask',[True],'MASK_INTEGER'), ('float_mask',[7.0],'MASK_INTEGER'),
        ('duplicate_mask',[7,7],'MASK_ORDER'), ('reverse_masks',[15,7],'MASK_ORDER'), ('out_of_domain',[512],'MASK_INTEGER')]:
        negative(label, stage, ms, lambda ms=ms: population(ms, ['1']*len(ms), 9))
    for label, ws, stage in [('float_weight',[1.0],'WEIGHT_STRING'), ('bool_weight',[True],'WEIGHT_STRING'),
        ('unreduced_weight',['2/4'],'WEIGHT_CANONICAL'), ('negative_weight',['-1'],'WEIGHT_NONNEGATIVE'),
        ('wrong_weight_count',[],'WEIGHT_SHAPE')]:
        negative(label, stage, ws, lambda ws=ws: population([7], ws, 9))
    for label, mutate, stage in [('legacy_method', lambda q: q.update(method='independent_derivation'),'EXACT_PRIMAL_GATE_HEADER'),
        ('dual_not_primal', lambda q: q['outcome'].update(certificate_kind='farkas'),'EXACT_PRIMAL_GATE_SCOPE'),
        ('bool_dimension', lambda q: q['outcome'].update(rows=True),'EXACT_PRIMAL_GATE_SCOPE')]:
        q=copy.deepcopy(header); mutate(q); negative(label, stage, q, lambda q=q: gate_header(q))
    need(len(rows)==19 and sum(x['actual_stage']=='PASS' for x in rows)==6, 'EXACT_6_13_CONTROLS')
    save('controls.json', dict(positive=6, precise_negative=13, total=19, records=rows, actual_primal_read=False))
    return rows


def main():
    p=argparse.ArgumentParser(); p.add_argument('mode', choices=['calibrate','survey'])
    p.add_argument('--seconds',type=float,required=True); p.add_argument('--out',required=True)
    p.add_argument('--source-sha256',required=True); p.add_argument('--spec-sha256',required=True)
    for name in ['calibration','full-gate','root-full-acceptance']:
        p.add_argument('--'+name); p.add_argument('--'+name+'-sha256')
    a=p.parse_args(); d=CommandDeadline(a.seconds, allocation_reason='Exact positive population/all weighted triangle cliques; authentication,controls,680 cut diagnostics and outputs inside invocation/20save')
    def guard():
        s=d.status(); need(not s['stop_required'] and s['remaining_seconds']>20,'SAVE_RESERVE')
    out=Path(a.out).resolve(); need(out.is_relative_to(ROOT) and not out.exists(),'FRESH_OUTPUT'); out.mkdir(parents=True)
    inputs={}; outputs={}
    def path(name):
        q=ROOT/name; need(q.resolve().is_relative_to(ROOT) and q.is_file() and not q.is_symlink(),'INPUT_PATH'); return q
    def digest(q):
        h=hashlib.sha256()
        with q.open('rb') as f:
            while block:=f.read(1024**2): guard(); h.update(block)
        guard(); return h.hexdigest()
    def pin(q, expected):
        need(type(expected) is str and re.fullmatch('[0-9a-f]{64}',expected) is not None,'HASH_FORMAT')
        need(digest(q)==expected,'INPUT_IDENTITY'); inputs[q.resolve().relative_to(ROOT).as_posix()]=expected
    def read(q): guard(); result=strict_json(q.read_bytes()); guard(); return result
    def save(name, value):
        guard(); q=out/name; q.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n'); guard()
        outputs[name]=digest(q)
    def mapped(mapping):
        need(type(mapping) is dict and mapping,'INPUT_MAP')
        for name, expected in mapping.items(): pin(path(name),expected)
    try:
        pin(SELF,a.source_sha256); pin(SPEC,a.spec_sha256); mapped(SOFTWARE)
        tested=own_controls(save,guard); outcome=None
        if a.mode=='calibrate':
            need(all(getattr(a,name.replace('-','_')) is None and getattr(a,name.replace('-','_')+'_sha256') is None
                     for name in ['calibration','full-gate','root-full-acceptance']), 'CALIBRATION_NO_ACTUAL')
        else:
            for name in ['calibration','full-gate','root-full-acceptance']:
                value=getattr(a,name.replace('-','_')); identity=getattr(a,name.replace('-','_')+'_sha256')
                need(value and identity,'PREREQUISITE_REQUIRED'); pin(path(value),identity)
            cal=read(path(a.calibration))
            need(cal.get('status')==CAL and cal.get('source_sha256')==a.source_sha256 and cal.get('spec_sha256')==a.spec_sha256
                 and cal.get('controls')==tested,'APPLICABLE_CALIBRATION')
            mapped(cal['inputs_sha256'])
            for name,expected in cal['outputs_sha256'].items(): pin(path(a.calibration).parent/name,expected)
            gate=read(path(a.full_gate)); gate_header(gate); mapped(gate['inputs_sha256'])
            mapped(gate['outputs_sha256'])
            for name,expected in FIXED.items():
                need(gate['inputs_sha256'].get(name)==expected,'GATE_DIRECT_PINS'); pin(path(name),expected)
            review=read(path(a.root_full_acceptance))
            need(review.get('full_report_sha256')==a.full_gate_sha256 and review.get('target_resolution')=='NONE', 'ROOT_FULL_ACCEPTANCE_BINDING')
            model=read(path(MODEL)); primal=read(path(PRIMAL)); types=read(path(TYPES))
            need(model.get('schema')=='TRIPLE_CAPPED_EXTERNAL_MOMENT_SYSTEM_V1' and type(model.get('original_variables')) is int
                 and model['original_variables']==472 and model.get('support_vertices')==list(range(17)),'FIXED_MODEL_SCOPE')
            need(type(types) is list and len(types)==472 and all(type(x) is dict and set(x)=={'mask','coefficient'} for x in types),'TYPE_POPULATION')
            masks=mask_list([x['mask'] for x in types],17); need(masks==model.get('ordered_masks'),'MODEL_MASK_ORDER')
            need(primal.get('schema')=='TRIPLE_CAPPED_EXTERNAL_MOMENT_EXACT_PRIMAL_V1','PRIMAL_SCHEMA')
            values=rational_vector(primal.get('values'),1152); selected=population(masks,list(map(str,values[:472])),17)
            save('positive_types.json',dict(source_first_columns=472,positive_exact_threshold='0',minimum_type_size=3,records=selected))
            cuts=[]
            for row,Q in enumerate(itertools.combinations(range(17),3)):
                guard(); mask=sum(1<<i for i in Q); total=sum((values[i] for i,T in enumerate(masks) if T&mask==mask),Fraction(0))
                need(total<=1 and total+values[472+row]==1,'ORIGINAL_TRIPLE_SLACK')
                cuts.append(dict(row=row,Q=list(Q),sum=str(total),slack=str(values[472+row]),holds=True))
            save('all680_common_Q_caps.json',cuts)
            handles={name:(out/name).open('x',encoding='utf8',newline='\n') for name in ['all_pairs.jsonl','all_triangle_cliques.jsonl','all_violations.jsonl']}
            written={name:0 for name in handles}
            def emit(name,item):
                guard(); handles[name].write(json.dumps(item,sort_keys=True,separators=(',',':'))+'\n'); written[name]+=1
                if written[name]%1000==0: handles[name].flush(); guard()
            try: counts=triangle_scan(selected,lambda x:emit('all_pairs.jsonl',x),lambda x:emit('all_triangle_cliques.jsonl',x),lambda x:emit('all_violations.jsonl',x),guard)
            finally:
                for f in handles.values(): f.flush(); f.close()
            for name in handles: outputs[name]=digest(out/name)
            need(written['all_pairs.jsonl']==counts['unordered_pairs'] and written['all_triangle_cliques.jsonl']==counts['triangle_cliques']
                 and written['all_violations.jsonl']==counts['violated_triangle_cliques'],'ALL_SAVED_POPULATIONS')
            outcome=dict(**counts,original_common_Q_cuts_checked=680,triangle_threshold='strictly greater than1',
                all_matches_retained=True,maximum_cliques_enumerated=False,original_primal_gate_sha256=a.full_gate_sha256,
                meaning='Violations separate this exact rational point from necessary realizable-type clique inequalities; no whole-system infeasibility or target exclusion')
        for name,expected in list(inputs.items()): pin(path(name),expected)
        save('summary.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),status=CAL if a.mode=='calibrate' else 'CANDIDATE_EXTERNAL_TYPE_TRIANGLE_CLIQUES_V1_COMPLETE',
            producer='/root/checkpoint_audit',independent_verifier_required='/root/native_driver',target_resolution='NONE',
            source_sha256=a.source_sha256,spec_sha256=a.spec_sha256,command=[sys.executable,*sys.argv],
            inputs_sha256=inputs,outputs_sha256=outputs.copy(),controls=tested,outcome=outcome,LP_calls=0,RREF_calls=0,
            actual_primal_read=a.mode=='survey',full_trajectory_or_graph_claim=False,deadline=d.status()))
        guard()
    except Exception as error:
        (out/'failure.json').write_text(json.dumps(dict(stage=str(error),exception=type(error).__name__,inputs_sha256=inputs,
            outputs_sha256=outputs,no_automatic_retry=True,no_infeasibility_inference=True,deadline=d.status()),indent=2)+'\n',encoding='utf8')
        raise


if __name__=='__main__': main()
