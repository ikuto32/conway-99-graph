"""Unexecuted finite controls for the new independent frozen-root scorer.

This is a kernel calibration only. It does not approve producer execution or
parse a producer census; the separately versioned caller must do that.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform
import sys
from command_deadline import CommandDeadline
import audit_20261003_root_focused_census_core_v1 as K
import audit_20261003_root_focused_core_v2 as S

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/audit_20261003_root_focused_census_controls_v1.py'
SPEC = 'acceleration/audit_20261003_root_focused_census_controls_v1_spec.md'


def need(ok, message):
    K.require(ok, 'CALIBRATION', message)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path, value):
    with path.open('x',encoding='utf8',newline='\n') as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False)
        stream.write('\n')


def full_set_candidate(base, indices):
    """Independent slow literal line construction, with a separate set domain."""
    i,j,pi,pj = indices
    rows = copy.deepcopy(base['triples'])
    x,y = rows[i][pi],rows[j][pj]
    if x in rows[j] or y in rows[i]:
        return False, None, None
    rows[i][pi],rows[j][pj] = y,x
    seen = set()
    for row in rows:
        for pair in combinations(row,2):
            pair = frozenset(pair)
            if pair in seen:
                return False, None, None
            seen.add(pair)
    graph = S.graph(rows,base['n'],base['degree'],base['root'])
    return True,rows,graph


def fixture_rows(name):
    if name == 'rook9':
        return [[3*r+c for c in range(3)] for r in range(3)] + [[3*r+c for r in range(3)] for c in range(3)],9,2
    if name == 'prism9':
        return [[0,2,6],[0,1,7],[1,2,8],[3,5,6],[3,4,7],[4,5,8]],9,2
    if name == 'cube12_defect':
        return [[1,2,7],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[0,10,11]],12,2
    need(name == 'target99','declared fixture')
    return [[v,v+33,v+66] for v in range(33)]+[[v,(v+1)%99,(v+4)%99] for v in range(99)]+[[v,(v+7)%99,(v+18)%99] for v in range(99)],99,7


def one_comparison(base, indices, scalar=True):
    checked = K.evaluate(base,indices)
    valid,rows,graph = full_set_candidate(base,indices)
    need(type(checked['admissible']) is bool and checked['admissible'] == valid,'literal/set admissibility agreement')
    if not valid:
        return dict(indices=list(indices),admissible=False),{}
    scalar_result = S.scalar_matrix(S.matrix_bytes(graph),base['n'],base['degree'],base['root']) if scalar else graph
    for key in ['lambda_energy','mu_energy','root_residual','root_energy']:
        need(type(checked[key]) is int and checked[key] == graph[key] == scalar_result[key], 'full set/scalar '+key)
    need(K.matrix_bytes(checked['candidate_bits']) == S.matrix_bytes(graph),'complete matrix bytes')
    need(all(rows[row[0]] == row[1:] for row in base['frozen']),'literal original frozen rows')
    need(checked['delta_lambda'] == graph['lambda_energy']-base['lambda_energy']
         and checked['delta_mu'] == graph['mu_energy']-base['mu_energy']
         and checked['delta_root'] == graph['root_residual']-base['root_residual']
         and checked['delta_F'] == graph['root_energy']-base['root_energy'], 'independent full component deltas')
    need(checked['lambda_preserving'] == (graph['lambda_energy'] == base['lambda_energy'])
         and checked['strict_root_descent'] == (graph['lambda_energy'] == base['lambda_energy'] and graph['root_residual'] < base['root_residual']),
         'exact root classification')
    touched = {u for u in range(base['n']) if checked['candidate_bits'][u] != base['bits'][u]}
    count = len(touched)*(base['n']-len(touched))+len(touched)*(len(touched)-1)//2
    need(checked['changed_row_count'] == len(touched) and checked['affected_pair_count'] == count,'complete affected pair census')
    shared = set(checked['old_triples'][0]) & set(checked['old_triples'][1])
    cancelled = bool(shared) and all(z not in touched for z in shared)
    outside = set(range(base['n']))-touched
    outside_with_changed_common = 0
    for u,v in combinations(sorted(outside),2):
        common = {z for z in touched if base['bits'][u] >> z & 1 and base['bits'][v] >> z & 1}
        if common:
            need((base['bits'][u]&base['bits'][v]).bit_count() == (checked['candidate_bits'][u]&checked['candidate_bits'][v]).bit_count(),
                 'untouched pair with changed common-neighbor row')
            outside_with_changed_common += 1
    removed_edges = sum(bool(base['bits'][u] >> v & 1) and not bool(checked['candidate_bits'][u] >> v & 1) for u,v in combinations(range(base['n']),2))
    added_edges = sum(not bool(base['bits'][u] >> v & 1) and bool(checked['candidate_bits'][u] >> v & 1) for u,v in combinations(range(base['n']),2))
    return dict(indices=list(indices),admissible=True,scores={k:graph[k] for k in ['lambda_energy','mu_energy','root_residual','root_energy']},
                scalar_matrix=scalar,affected_pairs=count),dict(shared_point_cancellation=int(cancelled),
                                                               untouched_pair_changed_common_neighbor=outside_with_changed_common,
                                                               changed_edge_categories=int(removed_edges > 0 and added_edges > 0))


def reject(records,label,callback,stage,message):
    try:
        callback()
    except K.CensusError as error:
        need(error.stage == stage and str(error) == stage+': '+message,'negative exact diagnostic '+label)
        records.append(dict(name=label,expected_stage=stage,expected_diagnostic=message,outcome='REJECTED'))
        return
    except BaseException as error:
        raise AssertionError('Wrong-stage negative '+label+': '+repr(error)) from error
    raise AssertionError('Accepted corruption '+label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seconds',type=float,required=True)
    parser.add_argument('--out',required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds,allocation_reason='New independent exact frozen-root census kernel calibration only; complete tiny universes plus16target samples,10s save reserve;no producer artifacts/native calls')
    out = (ROOT/args.out).resolve()
    need(out.is_relative_to(ROOT),'workspace output')
    out.mkdir(parents=True,exist_ok=False)
    protected = {name:digest(ROOT/name) for name in ['CLAIMS.yaml','.git/index']}
    pins = {}
    try:
        for name in [SOURCE,SPEC,'acceleration/audit_20261003_root_focused_census_core_v1.py',
                     'acceleration/audit_20261003_root_focused_census_core_v1_spec.md','acceleration/audit_20261003_root_focused_core_v2.py',
                     'acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']:
            pins[name] = digest(ROOT/name)
        records = []
        special = Counter()
        fixture_counts = {}
        for name,expected in [('rook9',54),('prism9',54),('cube12_defect',135)]:
            need(deadline.status()['remaining_seconds'] > 10,'calibration reserve')
            rows,n,degree = fixture_rows(name)
            base = K.from_triples(rows,n,degree,0)
            universe = K.labelled_universe(base)
            need(len(universe) == expected and len(set(universe)) == expected,'complete tiny labelled universe')
            fixture_counts[name] = dict(labelled_proposals=expected,complete_full_scalar_admissible=0)
            for indices in universe:
                record,coverage = one_comparison(base,indices)
                record['fixture'] = name
                records.append(record)
                special.update(coverage)
                fixture_counts[name]['complete_full_scalar_admissible'] += int(record['admissible'])
        rows,n,degree = fixture_rows('target99')
        base = K.from_triples(rows,n,degree,11)
        universe = K.labelled_universe(base)
        need(len(universe) == 224784,'exact target labelled population')
        # Fixed sample independent of scores:16 evenly spaced labels in the
        # lex mutable-label universe, including its two endpoints.
        sample_ids = [(len(universe)-1)*i//15 for i in range(16)]
        fixture_counts['target99'] = dict(labelled_universe=224784,fixed_sample_ids=sample_ids,attempted=16,full_scalar_admissible=0)
        for pid in sample_ids:
            need(deadline.status()['remaining_seconds'] > 10,'target calibration reserve')
            record,coverage = one_comparison(base,universe[pid])
            record.update(fixture='target99',pid=pid)
            records.append(record)
            special.update(coverage)
            fixture_counts['target99']['full_scalar_admissible'] += int(record['admissible'])
        need(all(special[key] > 0 for key in ['shared_point_cancellation','untouched_pair_changed_common_neighbor','changed_edge_categories']),
             'actual branch-aware algebraic controls')
        negatives = []
        rook,n,degree = fixture_rows('rook9')
        rb = K.from_triples(rook,n,degree,0)
        bad = copy.deepcopy(rook);bad[0][0]=True
        reject(negatives,'bool point',lambda:K.from_triples(bad,9,2,0),'DOMAIN','three literal distinct points')
        reject(negatives,'float n',lambda:K.from_triples(rook,9.0,2,0),'DOMAIN','literal graph domain')
        reject(negatives,'bool degree',lambda:K.from_triples(rook,9,True,0),'DOMAIN','literal graph domain')
        reject(negatives,'root outside',lambda:K.from_triples(rook,9,2,9),'DOMAIN','literal graph domain')
        reject(negatives,'missing line',lambda:K.from_triples(rook[:-1],9,2,0),'DOMAIN','complete ordered triangle population')
        bad = copy.deepcopy(rook);bad[1]=bad[0][:]
        reject(negatives,'duplicate pair',lambda:K.from_triples(bad,9,2,0),'DOMAIN','linear pair multiplicity')
        bad = copy.deepcopy(rook);bad[0][1]=bad[0][0]
        reject(negatives,'repeated point',lambda:K.from_triples(bad,9,2,0),'DOMAIN','three literal distinct points')
        reject(negatives,'bool label',lambda:K.evaluate(rb,[1,2,True,0]),'LABEL','four literal proposal indices')
        reject(negatives,'float label',lambda:K.evaluate(rb,[1,2,0,0.0]),'LABEL','four literal proposal indices')
        reject(negatives,'missing label',lambda:K.evaluate(rb,[1,2,0]),'LABEL','four literal proposal indices')
        reject(negatives,'reversed lines',lambda:K.evaluate(rb,[2,1,0,0]),'LABEL','unordered line labels and ordered point positions')
        reject(negatives,'equal lines',lambda:K.evaluate(rb,[1,1,0,0]),'LABEL','unordered line labels and ordered point positions')
        reject(negatives,'negative line',lambda:K.evaluate(rb,[-1,2,0,0]),'LABEL','unordered line labels and ordered point positions')
        reject(negatives,'position outside',lambda:K.evaluate(rb,[1,2,3,0]),'LABEL','unordered line labels and ordered point positions')
        reject(negatives,'frozen line',lambda:K.evaluate(rb,[0,1,0,0]),'FROZEN','proposal contains only mutable line labels')
        rejected_stage = False
        try:
            reject([], 'wrong-stage harness',lambda:K.require(False,'OTHER','wrong'),'LABEL','four literal proposal indices')
        except K.CensusError as error:
            rejected_stage = error.stage == 'CALIBRATION' and str(error) == 'CALIBRATION: negative exact diagnostic wrong-stage harness'
        need(rejected_stage,'wrong-stage harness must fail')
        negatives.append(dict(name='wrong-stage harness',outcome='WRONG_STAGE_REJECTED'))
        save(out/'positive_records.json',records)
        save(out/'strict_controls.json',negatives)
        need(all(digest(ROOT/name) == identity for name,identity in protected.items()),'protected ledger/index unchanged')
        now = datetime.now(timezone.utc).isoformat()
        save(out/'summary.json',dict(status='INDEPENDENT_FROZEN_ROOT_TWO_LINE_KERNEL_V1_CALIBRATION_PASS',
            timestamp=now,verifier='/root/checkpoint_audit',producer='/root/native_driver',method='independent_artifact_check',
            inputs_sha256=pins,positive_labelled_proposals=len(records),strict_negative_controls=len(negatives),
            fixture_populations=fixture_counts,actual_algebraic_case_observations=dict(special),producer_outputs_checked=False,
            native_calls=0,ledger_mutations=0,index_mutations=0,target_resolution='NONE',
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),deadline=deadline.status(),
            historical_protected_execution_state=dict(observations_sha256=protected,role='Before/after checking execution observations; not immutable scientific dependencies'),
            shared_components=['Independent earlier root-focused core raw-domain/adjacency-set scorer and scalar integer matrix path; no native producer imports.',
                               'Known fixture incidence lists; the new changed-row bitmask scorer does not use the earlier move replay/delta implementation.'],
            limitations=['Kernel calibration only; producer execution, file schemas and complete target census need separate new checking.',
                         '16target samples are not complete verification of224784target proposals.'],
            positive_records_sha256=digest(out/'positive_records.json'),strict_controls_sha256=digest(out/'strict_controls.json')))
        print('INDEPENDENT_FROZEN_ROOT_TWO_LINE_KERNEL_V1_CALIBRATION_PASS')
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,outputs_preserved=True,deadline=deadline.status(),native_calls=0))
        raise


if __name__ == '__main__':
    main()
