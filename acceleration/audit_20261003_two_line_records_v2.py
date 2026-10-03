"""Independent complete canonical-record census checker using exact dense deltas.

Imports only ROOT's byte-preserved independent dense checker, never producer.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import audit_20261003_two_line_dense_delta_v1 as F
from command_deadline import CommandDeadline

ROOT = F.ROOT
PRODUCER = 'acceleration/census_20261003_weight60_two_line_v1.py'
PRODUCER_SHA = 'f1384de1b0aa2c53c951abadf821f211637c33090422a9fcfe7619deefa1a710'
STATE = 'acceleration/results/20261003_hypergraph_weight60_warm01/native/final.state'
STATE_SHA = 'c15b421468af173b6c2ee11e9bcb31d5abca586fcb47a7c7ee312f527b31979b'
MATRIX = 'acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj'
MATRIX_SHA = '9d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d'


DENSE_CAL = 'acceleration/results/20261003_independent_review/two_line_dense_calibration01/summary.json'
DENSE_CAL_SHA = '6053c8685c9eafb7b06c01bc8a97476559e5c2aa3494f97335a26bf2ed0ff386'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, obj):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(obj, stream, indent=2); stream.write('\n')


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(',', ':'))+'\n').encode()


def load(path):
    def pairs(values):
        result = {}
        for key, value in values:
            F.need(key not in result, 'duplicate JSON metadata key')
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=pairs)


def identical(actual, expected, stage):
    F.need(canonical(actual) == canonical(expected), stage)


def record(a, cn, triples, pair, pid, root, baseline):
    i, j = pair
    ix, jy = (pid % 9)//3, pid % 3
    computed = F.classify(a, cn, triples, i, j, ix, jy, root, baseline)
    result = dict(schema='EXACT_V2_TWO_LINE_LABELLED_PROPOSAL_V1', proposal_id=pid,
                  i=i, j=j, ix=ix, jy=jy, old_triples=computed['old_triples'],
                  new_triples=None, valid=False, invalid_reason=None, conflict_pair=None,
                  toggles=None, delta_lambda=None, delta_mu=None, new_lambda=None, new_mu=None,
                  new_root_residual=None, root_residual_delta=None, classification=None)
    if not computed['valid']:
        if computed['invalid_reason'] == 'exclusive-selection':
            result.update(invalid_reason='selected_point_not_exclusive', classification='invalid_selection')
        else:
            result.update(new_triples=computed['new_triples'], invalid_reason='new_pair_already_present',
                          classification='invalid_linearity')
            left, right = triples[i], triples[j]
            p, q = left[ix], right[jy]
            other_left = [x for k,x in enumerate(left) if k != ix]
            other_right = [x for k,x in enumerate(right) if k != jy]
            matrix = a.copy()
            for u,v in [(p,x) for x in other_left]+[(q,x) for x in other_right]:
                matrix[u,v] = matrix[v,u] = 0
            for u,v in [(q,x) for x in other_left]+[(p,x) for x in other_right]:
                if matrix[u,v]:
                    result['conflict_pair'] = sorted([u,v]); break
                matrix[u,v] = matrix[v,u] = 1
            F.need(result['conflict_pair'] is not None, 'independent literal conflict witness')
        return result
    dl, dm = computed['delta_lambda'], computed['delta_mu']
    classification = ('valid_lambda_changed' if dl else 'valid_lambda_preserving_mu_'+
                      ('down' if dm < 0 else 'up' if dm > 0 else 'equal'))
    result.update(valid=True, new_triples=computed['new_triples'],
                  toggles=[t[:2] for t in computed['net_adjacency_toggles']],
                  delta_lambda=dl, delta_mu=dm, new_lambda=computed['new_lambda'],
                  new_mu=computed['new_mu'], new_root_residual=baseline[2]+computed['root_row_residual_delta'],
                  root_residual_delta=computed['root_row_residual_delta'], classification=classification)
    return result


def aggregate(records):
    counts, graphs, best = Counter(), set(), []
    best_mu = None
    for r in records:
        counts[r['classification']] += 1
        if r['valid']:
            graphs.add(tuple(tuple(t) for t in r['toggles']))
            if r['delta_lambda'] == 0:
                if best_mu is None or r['new_mu'] < best_mu:
                    best_mu, best = r['new_mu'], [r['proposal_id']]
                elif r['new_mu'] == best_mu:
                    best.append(r['proposal_id'])
    return dict(counts=dict(sorted(counts.items())), unique_valid_neighbor_graphs=len(graphs),
                best_mu=best_mu, best_proposal_ids=best)


def checked_stream(manifest, a, cn, triples, root, baseline, deadline, progress=None):
    pairs = list(itertools.combinations(range(len(triples)), 2))
    expected_id, records, pins = 0, [], {}
    F.need(type(manifest['population']) is int and type(manifest['completed_proposals']) is int
           and 0 <= manifest['completed_proposals'] <= manifest['population'] == len(pairs)*9,
           'literal complete population')
    for part in manifest['parts']:
        F.need(all(type(part[k]) is int for k in ('start','end','record_count','raw_bytes','gzip_bytes'))
               and part['record_count'] > 0 and part['start'] == expected_id and
               part['end'] == part['start']+part['record_count'] <= manifest['completed_proposals'], 'exact contiguous part universe')
        path = (ROOT/part['path']).resolve()
        F.need(path.is_relative_to(ROOT) and path.stat().st_size == part['gzip_bytes'] and sha(path) == part['gzip_sha256'], 'exact compressed part')
        digest, size, count = hashlib.sha256(), 0, 0
        with gzip.open(path, 'rb') as stream:
            while True:
                line = stream.readline(4097)
                if not line: break
                F.need(len(line) <= 4096 and line.endswith(b'\n'), 'bounded complete canonical line')
                F.need(expected_id < manifest['population'] and expected_id < part['end'], 'bounded exact proposal population')
                expected = record(a, cn, triples, pairs[expected_id//9], expected_id, root, baseline)
                F.need(line == canonical(expected), 'exact complete canonical proposal record')
                records.append(expected); digest.update(line); size += len(line); count += 1; expected_id += 1
                if expected_id % 1000 == 0:
                    F.need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds'] > 20, 'not completed within allocated budget')
        F.need((count,size,digest.hexdigest()) == (part['record_count'],part['raw_bytes'],part['raw_sha256']), 'exact decompressed part population/hash')
        F.need(expected_id == part['end'], 'exact complete part endpoint')
        pins[path.relative_to(ROOT).as_posix()] = part['gzip_sha256']
        if progress:
            with progress.open('a', encoding='utf8', newline='\n') as writer:
                writer.write(json.dumps(dict(timestamp=datetime.now(timezone.utc).isoformat(), complete_proposals=expected_id,
                             population=manifest['population'], deadline=deadline.status()))+'\n')
    F.need(expected_id == manifest['completed_proposals'], 'exact complete claimed prefix')
    return records, pins


def check_saved(manifest, directory, records, a, triples, root, baseline):
    """Check every prefix, all ties, and the chosen raw neighbor separately."""
    pins = {}
    identical(manifest['aggregate'], aggregate(records), 'exact typed complete aggregate')
    endpoints = [part['end'] for part in manifest['parts']]
    observed = []
    for cp in manifest['checkpoints']:
        path = (ROOT/cp['path']).resolve()
        F.need(path.is_relative_to(ROOT) and sha(path) == cp['sha256'], 'exact checkpoint')
        obj = load(path); endpoint = obj['next_proposal_id']
        F.need(obj['schema'] == 'EXACT_V2_TWO_LINE_CENSUS_CHECKPOINT_V1' and type(endpoint) is int
               and endpoint in endpoints and endpoint not in observed, 'exact checkpoint endpoint')
        index = endpoints.index(endpoint)+1
        identical(obj['identity'], manifest['identity'], 'exact typed checkpoint identity')
        identical(obj['parts'], manifest['parts'][:index], 'exact checkpoint part prefix')
        identical(obj['aggregate'], aggregate(records[:endpoint]), 'exact checkpoint aggregate prefix')
        observed.append(endpoint); pins[path.relative_to(ROOT).as_posix()] = cp['sha256']
    # Resumed manifests retain old parts but list only newly written checkpoints.
    start = manifest['starting_proposal_id']
    F.need(type(start) is int and start in [0,*endpoints] and start <= len(records), 'exact invocation prefix start')
    identical(observed, [q for q in endpoints if q > start], 'every new checkpoint endpoint')
    F.need(type(manifest['proposals_evaluated_this_invocation']) is int and
           manifest['proposals_evaluated_this_invocation'] == len(records)-start, 'exact invocation proposal count')
    F.need(manifest['status'] == ('CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK' if len(records) == manifest['population'] else 'UNKNOWN_PREFIX_ONLY')
           and type(manifest['budget_stop']) is bool and manifest['independent_approval'] is False
           and manifest['target_resolution'] is False, 'precise original completion scope')
    expected_baseline = dict(lambda_energy=baseline[0],mu_energy=baseline[1],root=root,root_residual=baseline[2])
    identical(manifest['baseline'], expected_baseline, 'exact typed scalar baseline')
    best_ids = aggregate(records)['best_proposal_ids']; best = [records[i] for i in best_ids]
    path = directory/'best_ties.json'
    identical(load(path), dict(records=best, scope='All lambda-preserving minimum-mu labelled proposals among saved prefix; complete only if all proposal IDs covered.'), 'every minimum-mu tie')
    pins[path.resolve().relative_to(ROOT).as_posix()] = sha(path)
    identical(manifest['selected_proposal_id'], best_ids[0] if best_ids else None, 'lexicographic selected minimum-mu tie')
    if not best_ids:
        F.need(not (directory/'best_neighbor.adj').exists() and not (directory/'best_neighbor_triples.json').exists(), 'no invented selected neighbor')
        return pins, None
    selected = records[best_ids[0]]; new_triples = copy.deepcopy(triples)
    new_triples[selected['i']],new_triples[selected['j']] = selected['new_triples']
    neighbor = F.adjacency(len(a), 7 if len(a)==99 else 2, new_triples)
    path = directory/'best_neighbor_triples.json'
    identical(load(path), dict(n=len(a),degree=7 if len(a)==99 else 2,triples=new_triples,proposal_id=selected['proposal_id']), 'complete chosen neighbor triples')
    pins[path.resolve().relative_to(ROOT).as_posix()] = sha(path)
    path = directory/'best_neighbor.adj'
    raw=(str(len(a))+'\n'+''.join(''.join(str(int(v)) for v in row)+'\n' for row in neighbor)).encode()
    F.need(path.read_bytes()==raw, 'complete chosen raw neighbor adjacency')
    pins[path.resolve().relative_to(ROOT).as_posix()] = sha(path)
    cn=neighbor@neighbor; el,em,er=F.energy(neighbor,cn,root)
    F.need((el,em,er)==(selected['new_lambda'],selected['new_mu'],selected['new_root_residual']), 'complete chosen neighbor full product')
    expected=((2 if len(a)==9 else 12)*F.np.eye(len(a),dtype=F.np.int64)-neighbor+2*F.np.ones_like(neighbor))
    return pins, dict(proposal_id=selected['proposal_id'],lambda_energy=el,mu_energy=em,root_residual=er,
                      ordered_srg_identity_mismatches=int(F.np.count_nonzero(cn-expected)))


def root_minimum(records):
    eligible=[r for r in records if r['valid'] and r['delta_lambda']==0]
    minimum=min((r['new_root_residual'] for r in eligible),default=None)
    return dict(population='All saved valid lambda-preserving labelled proposals, including worsening global-mu moves',
                population_count=len(eligible),minimum_root_residual=minimum,
                minimum_records=[dict(proposal_id=r['proposal_id'],new_root_residual=r['new_root_residual'],new_mu=r['new_mu'])
                                 for r in eligible if r['new_root_residual']==minimum])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=['calibrate','check'])
    ap.add_argument('--seconds', type=float, required=True); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--controls', type=Path); ap.add_argument('--controls-sha256')
    ap.add_argument('--manifest', type=Path); ap.add_argument('--manifest-sha256')
    ap.add_argument('--calibration', type=Path); ap.add_argument('--calibration-sha256')
    args = ap.parse_args(); original_command = [sys.executable,*sys.argv]
    d = CommandDeadline(args.seconds, allocation_reason='Complete exact dense record/stream check; finite270 controls before full239085; explicit percommand deadline and20save reserve')
    out = args.out.resolve(); F.need(out.is_relative_to(ROOT), 'workspace output'); out.mkdir(parents=True, exist_ok=False)
    F.need(sha(ROOT/PRODUCER) == PRODUCER_SHA, 'exact unchanged scientific producer')
    pins = {p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),Path(F.__file__),
            Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/PRODUCER,
            ROOT/'acceleration/census_20261003_weight60_two_line_v1_spec.md',ROOT/'uv.lock',ROOT/'pyproject.toml']}
    F.need(sha(ROOT/DENSE_CAL)==DENSE_CAL_SHA, 'exact separate dense preoutput calibration')
    dense=load(ROOT/DENSE_CAL); pins[DENSE_CAL]=DENSE_CAL_SHA
    for name,identity in dense['inputs_outputs_sha256'].items():
        F.need(sha(ROOT/name)==identity, 'unchanged separately calibrated dense component');pins[name]=identity
    if args.mode == 'calibrate':
        F.need(args.controls and sha(args.controls/'summary.json') == args.controls_sha256, 'exact author controls')
        saved = load(args.controls/'summary.json'); pins[(args.controls/'summary.json').resolve().relative_to(ROOT).as_posix()] = args.controls_sha256
        calibrated = []; populations = 0; fullmatrix_checks = 0; fixture_data = {}
        for name in ('rook9','prism9'):
            fixture = saved['fixtures'][name]
            a = F.adjacency(fixture['n'],fixture['degree'],fixture['triples']); cn = a@a
            root = fixture['root']; baseline = F.energy(a,cn,root)
            whole = None
            for suffix in ('whole','resumed'):
                p = args.controls/(name+'_'+suffix)/'manifest.json'; m = load(p)
                records, identities = checked_stream(m,a,cn,fixture['triples'],root,baseline,d)
                F.need(m['population'] == m['completed_proposals'] == 135 and aggregate(records) == m['aggregate'], 'complete tiny aggregate')
                extra, selected_neighbor = check_saved(m,p.parent,records,a,fixture['triples'],root,baseline);pins.update(extra)
                F.need(whole is None or records == whole, 'independent complete split identity')
                whole = records; pins.update(identities); pins[p.resolve().relative_to(ROOT).as_posix()] = sha(p)
            calibrated.extend(whole); populations += len(whole)
            fixture_data[name] = (m,whole,a,cn,fixture['triples'],root,baseline,p.parent)
            for r in whole:
                if not r['valid']:continue
                ordered=copy.deepcopy(fixture['triples']);ordered[r['i']],ordered[r['j']]=r['new_triples']
                rebuilt=F.adjacency(9,2,ordered);full=rebuilt@rebuilt
                scalar=F.np.asarray([[sum(int(rebuilt[u,k])*int(rebuilt[k,v]) for k in range(9))for v in range(9)]for u in range(9)],dtype=F.np.int64)
                computed=F.classify(a,cn,fixture['triples'],r['i'],r['j'],r['ix'],r['jy'],root,baseline)
                F.need(F.np.array_equal(rebuilt,computed['new_matrix']) and F.np.array_equal(full,computed['new_cn'])
                       and F.np.array_equal(full,scalar), 'all valid rook/prism full scalar products')
                fullmatrix_checks+=1
            if name == 'prism9': F.need(whole[18]['valid'] and whole[18]['new_lambda'] == whole[18]['new_mu'] == 0, 'known overlapping prism-to-rook')
        negatives = []
        m,whole,a,cn,triples,root,baseline,directory=fixture_data['rook9']
        good = next(r for r in whole if r['valid'])
        def reject(label,stage,fn):
            try:fn()
            except ValueError as exc:
                F.need(str(exc)==stage, 'precise corrupted control diagnostic')
                negatives.append(dict(case=label,outcome='REJECTED',diagnostic=stage));return
            raise ValueError('corrupted saved control accepted: '+label)
        for label, field, value in [('proposal_id','proposal_id',-1),('lambda_delta','delta_lambda',good['delta_lambda']+1),
                                    ('root_delta','root_residual_delta',good['root_residual_delta']+1),
                                    ('bool_integer','new_lambda',True),('missing_toggle','toggles',[]),
                                    ('classification','classification','valid_lambda_preserving_mu_down')]:
            damaged = copy.deepcopy(good); damaged[field] = value
            raw=b''.join(canonical(damaged if r['proposal_id']==good['proposal_id'] else r) for r in whole)
            path=out/('corrupt_'+label+'.jsonl.gz'); path.write_bytes(gzip.compress(raw,compresslevel=1,mtime=0))
            corrupt=dict(population=135,completed_proposals=135,parts=[dict(path=path.relative_to(ROOT).as_posix(),start=0,end=135,
                         record_count=135,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest(),gzip_bytes=path.stat().st_size,gzip_sha256=sha(path))])
            # Fresh correct hashes force the damaged raw record through the actual checking path.
            reject(label,'exact complete canonical proposal record',lambda corrupt=corrupt:checked_stream(corrupt,a,cn,triples,root,baseline,d))
            pins[path.relative_to(ROOT).as_posix()]=sha(path)
        for label,mutation,stage in [
            ('part_gap',lambda x:x['parts'][0].__setitem__('start',1),'exact contiguous part universe'),
            ('raw_hash',lambda x:x['parts'][0].__setitem__('raw_sha256','0'*64),'exact decompressed part population/hash'),
            ('gzip_hash',lambda x:x['parts'][0].__setitem__('gzip_sha256','0'*64),'exact compressed part'),
            ('bool_population',lambda x:x.__setitem__('population',True),'literal complete population')]:
            corrupt=copy.deepcopy(m);mutation(corrupt)
            reject(label,stage,lambda corrupt=corrupt:checked_stream(corrupt,a,cn,triples,root,baseline,d))
        for label,mutation,stage in [
            ('selected_id',lambda x:x.__setitem__('selected_proposal_id',1),'lexicographic selected minimum-mu tie'),
            ('missing_checkpoint',lambda x:x['checkpoints'].pop(),'every new checkpoint endpoint')]:
            corrupt=copy.deepcopy(m);mutation(corrupt)
            reject(label,stage,lambda corrupt=corrupt:check_saved(corrupt,directory,whole,a,triples,root,baseline))
        original=load(ROOT/m['checkpoints'][0]['path'])
        for label,mutation,stage in [('checkpoint_endpoint',lambda x:x.__setitem__('next_proposal_id',136),'exact checkpoint endpoint'),
                                    ('checkpoint_parts',lambda x:x.__setitem__('parts',[]),'exact checkpoint part prefix'),
                                    ('checkpoint_aggregate',lambda x:x['aggregate'].__setitem__('best_mu',99),'exact checkpoint aggregate prefix')]:
            obj=copy.deepcopy(original);mutation(obj);path=out/(label+'.json');write(path,obj)
            corrupt=copy.deepcopy(m);corrupt['checkpoints'][0]=dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path))
            reject(label,stage,lambda corrupt=corrupt:check_saved(corrupt,directory,whole,a,triples,root,baseline))
            pins[path.relative_to(ROOT).as_posix()]=sha(path)
        result = dict(status='INDEPENDENT_TWO_LINE_RECORDS_V2_PREOUTPUT_CALIBRATION_PASS', complete_unique_tiny_records=populations,
                      complete_records_including_split_replay=populations*2, known_overlap_checked=True, strict_record_corruptions=negatives,
                      complete_new_fullmatrix_and_scalar_comparisons=fullmatrix_checks,
                      pre_full_scientific_output=True, scientific_census_outputs_inspected=False)
    else:
        F.need(args.calibration and sha(args.calibration)==args.calibration_sha256, 'exact applicable record checker preoutput gate')
        cal=load(args.calibration)
        F.need(cal['status']=='INDEPENDENT_TWO_LINE_RECORDS_V2_PREOUTPUT_CALIBRATION_PASS', 'applicable record gate status')
        for name,identity in cal['inputs_sha256'].items():F.need(sha(ROOT/name)==identity,'exact current preoutput gate component');pins[name]=identity
        pins[args.calibration.resolve().relative_to(ROOT).as_posix()]=args.calibration_sha256
        F.need(args.manifest and sha(args.manifest) == args.manifest_sha256, 'exact scientific manifest')
        for name,identity in [(STATE,STATE_SHA),(MATRIX,MATRIX_SHA)]: F.need(sha(ROOT/name)==identity,'exact frozen warm raw input'); pins[name]=identity
        lines = (ROOT/STATE).read_text(encoding='ascii').splitlines()
        F.need(lines[0]=='HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2' and lines.count('current 231')==1,'exact current block boundary')
        start = lines.index('current 231')+1; triples=[[int(v) for v in line.split()] for line in lines[start:start+231]]
        a=F.adjacency(99,7,triples); raw=('99\n'+''.join(''.join(str(int(v)) for v in row)+'\n' for row in a)).encode()
        F.need(raw==(ROOT/MATRIX).read_bytes(),'complete matrix reconstruction from ordered triples')
        cn=a@a; baseline=F.energy(a,cn,11); F.need(baseline==(0,3480,52),'exact scalar baseline')
        m=load(args.manifest); F.need(m['schema']=='EXACT_V2_TWO_LINE_CENSUS_MANIFEST_V1' and m['population']==239085 and m['identity']['software'][PRODUCER]==PRODUCER_SHA,'complete fixed scientific universe/source')
        identical([m['identity'][k]for k in ('n','degree','root','total')],[99,7,11,239085],'exact literal target identity')
        F.need(m['identity']['proposal_order']=='unordered triplepairs i<j lex; selected positions ix,jy lex;9*pair_index+3*ix+jy', 'exact canonical proposal order')
        for name,identity in {**m['identity']['software'],**m['identity']['inputs_sha256']}.items():F.need(sha(ROOT/name)==identity,'exact frozen scientific input/software');pins[name]=identity
        records,identities=checked_stream(m,a,cn,triples,11,baseline,d,out/'progress.jsonl'); pins.update(identities)
        extra,selected_neighbor=check_saved(m,args.manifest.parent,records,a,triples,11,baseline);pins.update(extra)
        root_result=root_minimum(records);write(out/'all_lambda_preserving_minimum_root_ties.json',root_result)
        pins[(out/'all_lambda_preserving_minimum_root_ties.json').relative_to(ROOT).as_posix()]=sha(out/'all_lambda_preserving_minimum_root_ties.json')
        pins[args.manifest.resolve().relative_to(ROOT).as_posix()]=args.manifest_sha256
        result=dict(status='INDEPENDENT_TWO_LINE_COMPLETE_FIXED_GRAPH_CENSUS_V2_PASS' if len(records)==239085 else 'INDEPENDENT_TWO_LINE_PREFIX_ONLY_V2_PASS',
                    complete_proposals_checked=len(records), frozen_labelled_proposals=239085, aggregate=m['aggregate'],
                    independently_checked_chosen_neighbor=selected_neighbor,minimum_root_residual=root_result['minimum_root_residual'],
                    minimum_root_tie_count=len(root_result['minimum_records']),
                    complete_universe=len(records)==239085, absence_of_descent_asserted=len(records)==239085 and m['aggregate']['counts'].get('valid_lambda_preserving_mu_down',0)==0)
    write(out/'summary.json',dict(**result,timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root',producer='/root/native_driver',
          method='independent_artifact_check',command=original_command,cwd=str(ROOT),python=platform.python_version(),numpy=F.np.__version__,
          inputs_sha256=pins,shared_components=['ROOT byte-preserved independent dense V1 reused; no scientific producer/parser/bitset scorer imported.',
          'Known fixture/input definitions, Python JSON/gzip, fixed-width NumPy integer operations with explicit n99 overflow bounds.'],
          limitations=['One fixed graph and exact labelled two-line universe only; no graph-space/global minimum/ergodicity or target conclusion.',
          'The finite calibration challenges parser/record/delta behavior; full scientific approval requires every actual record.'],target_resolution='NONE',deadline=d.status()))
    print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'))))


if __name__ == '__main__':
    try: main()
    except BaseException as error:
        # Retain raw producer files and last complete checked-prefix progress.
        if '--out' in sys.argv:
            path=Path(sys.argv[sys.argv.index('--out')+1]).resolve()
            if path.is_relative_to(ROOT) and path.is_dir() and not (path/'failure.json').exists():
                write(path/'failure.json',dict(error=repr(error),timestamp=datetime.now(timezone.utc).isoformat(),
                       status='AUDIT_NOT_COMPLETED',approval=False,raw_artifacts_preserved=True,
                       unmet_requirements='Complete canonical raw record/checkpoint/selected neighbor audit; inspect saved progress; no absence of descent or target conclusion.'))
        raise
