"""Source-only same-author synthetic BEST-extractor/interface controls.

No actual saved target, prerequisite report, projection or native process is read.
Synthetic fragments test selected fields only, not complete native state parsing.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/project_20261003_ternary_mixed_saved_best_v2.py'
SOURCE_SHA = '0395227419dfb9140480cf58f7c6410940f345c69f2bdf8c54fc96f8a5112307'
SPEC = SOURCE.replace('.py', '_spec.md')
SPEC_SHA = 'cecda6b65b24e1cbba7bb73078cbd4d3266aa82b47925d813a991c43c3e3ca9f'


def scalar(n, degree, rows):
    a = [[0]*n for _ in range(n)]
    for row in rows:
        for i, j in [(row[0], row[1]), (row[0], row[2]), (row[1], row[2])]:
            a[i][j] = a[j][i] = 1
    hist = [0, 0, 0]
    lam = mu = 0
    for i in range(n):
        for j in range(i+1, n):
            rho = sum(a[i][k]*a[j][k] for k in range(n))+a[i][j]-2
            hist[rho % 3] += 1
            if a[i][j]:
                lam += rho*rho
            else:
                mu += rho*rho
    f3 = hist[1]+hist[2]
    weight = {(9, 2): 577, (12, 2): 1057, (99, 7): 819820}[(n, degree)]
    raw = (str(n)+'\n'+''.join(''.join(map(str, row))+'\n' for row in a)).encode('ascii')
    return raw, dict(F3=f3, E_lambda=lam, E_mu=mu, E=lam+mu, scalar_weight=weight,
                    scalar=weight*f3+lam+mu, residue_population=hist)


def fragment(header, n, degree, rows, metric):
    values = [metric['F3'], metric['E_lambda'], metric['E_mu'], *metric['residue_population'], metric['scalar']]
    lines = header+[f'n {n}', f'degree {degree}', 'seed 3', 'step 7', 'rng opaque-not-parsed',
                    'best_metrics '+' '.join(map(str, values)), 'best '+str(len(rows))]
    lines += [' '.join(map(str, row)) for row in rows]
    lines += ['zero_archive opaque-not-parsed', 'END']
    return ('\n'.join(lines)+'\n').encode('ascii')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seconds', type=float, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Same-author synthetic best extractor and typed saved-report interface controls only; no actual saved target/raw report/native/trajectory')
    out = args.out.resolve()
    assert out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT'
    out.mkdir(parents=True)
    positives = []
    negatives = []
    budget_positives = []
    pins = {SOURCE: SOURCE_SHA, SPEC: SPEC_SHA}

    def tick():
        assert deadline.status()['remaining_seconds'] > 20 and not deadline.status()['stop_required'], 'SAVE_RESERVE'

    def save(name, value):
        with (out/name).open('x', encoding='utf8', newline='\n') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')

    try:
        for name, expected in pins.items():
            tick()
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, 'SOURCE_IDENTITY'
            tick()
        loader = importlib.util.spec_from_file_location('new_best_projector_controls', ROOT/SOURCE)
        module = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        rook = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]]
        cube = [[0,1,2],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[7,10,11]]
        cyclic = [[x,x+33,x+66] for x in range(33)]
        cyclic += [[x,(x+1)%99,(x+4)%99] for x in range(99)]
        cyclic += [[x,(x+7)%99,(x+18)%99] for x in range(99)]
        for label, n, d, rows in [('rook9',9,2,rook),('cube12',12,2,cube),('cyclic99_initializer',99,7,cyclic)]:
            tick()
            matrix, metric = scalar(n,d,rows)
            raw = fragment(module.HEADER,n,d,rows,metric)
            got_n, got_d, got_rows, got_matrix, got_metric = module.extract_best(raw)
            assert [got_n,got_d,got_rows] == [n,d,rows] and got_matrix == matrix and got_metric == metric, 'EXACT_SCALAR_FIXTURE'
            identity = hashlib.sha256(matrix).hexdigest()
            expected = (f'TERNARY_LINEAR_GRAPH_INPUT_V1\nn {n}\ndegree {d}\nsource_graph_sha256 {identity}\ntriples {len(rows)}\n'
                        + ''.join(' '.join(map(str,row))+'\n' for row in rows)+'END\n').encode('ascii')
            assert module.wire(got_rows,n,d,identity) == expected, 'EXACT_GEOMETRY_WIRE'
            changed = raw.replace(b'seed 3\nstep 7\nrng opaque-not-parsed', b'seed 88\nstep 12345\nrng different-opaque')
            assert module.extract_best(changed) == module.extract_best(raw), 'OPAQUE_HISTORY_EXCLUDED'
            (out/(label+'.synthetic_fragment')).write_bytes(raw)
            (out/(label+'.adj')).write_bytes(matrix)
            (out/(label+'.wire')).write_bytes(expected)
            save(label+'.rows.json',dict(n=n,point_degree=d,ordered_triples=rows,metrics=metric))
            positives.append(dict(case=label,binary_matrix_entries=n*n,unordered_pair_dot_products=n*(n-1)//2,metrics=metric,
                exact_best_order=True,exact_wire=True,opaque_seed_step_rng_excluded=True,full_native_state_fixture=False))
        assert positives[0]['metrics']['F3'] == 0 and positives[0]['metrics']['E'] == 0, 'KNOWN_ROOK'
        matrix, metric = scalar(9,2,rook)
        raw = fragment(module.HEADER,9,2,rook,metric)
        state_name = 'synthetic/native/final.state'
        matrix_name = 'synthetic/native/best.adj'
        state_sha = hashlib.sha256(raw).hexdigest()
        matrix_sha = hashlib.sha256(matrix).hexdigest()
        report = dict(status='INDEPENDENT_TERNARY_MIXED_SAVED_OBJECTS_V1_COMPLETE_PASS',
            producer='/root/native_driver',verifier='/root/checkpoint_audit',method='independent_artifact_check',target_resolution='NONE',
            checker_implementation_version=4,source_sha256=module.SAVED_SHA,spec_sha256=module.SAVED_SPEC_SHA,
            inputs_sha256={state_name:state_sha,matrix_name:matrix_sha,module.SAVED:module.SAVED_SHA,
                module.SAVED.replace('.py','_spec.md'):module.SAVED_SPEC_SHA,module.HISTORICAL_SCI:module.HISTORICAL_SCI_SHA,
                module.HISTORICAL_SCI.replace('.py','_spec.md'):module.HISTORICAL_SPEC_SHA},
            saved_raw_scope=dict(best=metric,saved_state_files=1,complete_current_best_matrix_observations=2,
                complete_scalar_matrix_products=162,authenticated_native_reported_proposals=7))
        assert module.saved_relation(report,state_name,state_sha,matrix_name,matrix_sha,metric) == report['inputs_sha256'], 'SYNTHETIC_REPORT_RELATION'
        save('synthetic_report.json',report)

        def reject(label, stage, callback, artifact=None):
            tick()
            observed = None
            try:
                callback()
            except ValueError as error:
                observed = str(error)
            assert observed == stage, (label,stage,observed)
            if artifact is not None:
                save(label+'.json',artifact)
            negatives.append(dict(case=label,expected_stage=stage,actual_stage=observed))

        for label, bad, stage in [('nonbytes','x','STATE_BYTES'),('oversize',b'x'*(1024*1024+1),'STATE_BYTES'),
            ('nonascii',raw+b'\xff','STATE_ASCII'),('crlf',raw.replace(b'\n',b'\r\n'),'STATE_NEWLINE'),
            ('no_newline',raw[:-1],'STATE_NEWLINE'),('wrong_header',raw.replace(b'HYPERGRAPH_',b'WRONG_',1),'STATE_HEADER'),
            ('wrong_end',raw.replace(b'END\n',b'OTHER\n'),'STATE_HEADER')]:
            reject(label,stage,lambda bad=bad:module.extract_best(bad))
        for name in ['n','degree','best','best_metrics']:
            line = next(x for x in raw.splitlines() if x.startswith(name.encode()+b' '))
            bad = raw.replace(line+b'\n',line+b'\n'+line+b'\n',1)
            reject('duplicate_'+name,'BEST_FIELD_UNIQUE:'+name,lambda bad=bad:module.extract_best(bad))
        for label,old,new,stage in [('bool_n',b'n 9\n',b'n True\n','BEST_DOMAIN_INTEGER'),
            ('float_degree',b'degree 2\n',b'degree 2.0\n','BEST_DOMAIN_INTEGER'),
            ('bad_domain',b'n 9\n',b'n 10\n','BEST_DOMAIN'),
            ('float_count',b'best 6\n',b'best 6.0\n','BEST_COUNT_INTEGER'),
            ('wrong_count',b'best 6\n',b'best 5\n','BEST_COUNT'),
            ('bool_row',b'0 1 2\n',b'False 1 2\n','BEST_ROW_INTEGER'),
            ('float_row',b'0 1 2\n',b'0.0 1 2\n','BEST_ROW_INTEGER'),
            ('repeated_point',b'0 1 2\n',b'0 0 2\n','TRIPLE_DISTINCT'),
            ('negative_row',b'0 1 2\n',b'-1 1 2\n','BEST_ROW_INTEGER'),
            ('bad_metric',b'best_metrics 0 0 0 36 0 0 0\n',b'best_metrics 1 0 0 36 0 0 0\n','BEST_METRICS'),
            ('float_metric',b'best_metrics 0 0 0 36 0 0 0\n',b'best_metrics 0.0 0 0 36 0 0 0\n','BEST_METRIC_INTEGER')]:
            bad = raw.replace(old,new,1)
            assert bad != raw, 'CONTROL_MUTATION'
            reject(label,stage,lambda bad=bad:module.extract_best(bad))
        for key,value,stage in [('status','OTHER','SAVED_HEADER'),('producer','/root','SAVED_HEADER'),
            ('verifier','/root/structural','SAVED_HEADER'),('method','independent_derivation','SAVED_HEADER'),
            ('target_resolution',True,'SAVED_HEADER'),('checker_implementation_version',4.0,'SAVED_IMPLEMENTATION'),
            ('source_sha256','0'*64,'SAVED_IMPLEMENTATION'),('spec_sha256','0'*64,'SAVED_IMPLEMENTATION'),
            ('inputs_sha256',{},'SAVED_INPUTS')]:
            changed = copy.deepcopy(report);changed[key] = value
            reject('report_'+key,stage,lambda changed=changed:module.saved_relation(changed,state_name,state_sha,matrix_name,matrix_sha,metric),changed)
        for key in [state_name,matrix_name,module.SAVED,module.SAVED.replace('.py','_spec.md'),
                    module.HISTORICAL_SCI,module.HISTORICAL_SCI.replace('.py','_spec.md')]:
            changed = copy.deepcopy(report);changed['inputs_sha256'][key] = '0'*64
            stage = 'SAVED_BEST_IDENTITIES' if key in [state_name,matrix_name] else 'SAVED_ANCESTRY'
            reject('closure_'+str(len(negatives)),stage,lambda changed=changed:module.saved_relation(changed,state_name,state_sha,matrix_name,matrix_sha,metric),changed)
        for key,value,stage in [('best',dict(metric,F3=False),'SAVED_BEST_METRICS'),
            ('saved_state_files',True,'SAVED_COMPLETE_SCOPE:saved_state_files'),
            ('complete_current_best_matrix_observations',0,'SAVED_COMPLETE_SCOPE:complete_current_best_matrix_observations'),
            ('complete_scalar_matrix_products',162.0,'SAVED_COMPLETE_SCOPE:complete_scalar_matrix_products'),
            ('authenticated_native_reported_proposals',False,'SAVED_COMPLETE_SCOPE:proposals')]:
            changed = copy.deepcopy(report);changed['saved_raw_scope'][key] = value
            reject('scope_'+key,stage,lambda changed=changed:module.saved_relation(changed,state_name,state_sha,matrix_name,matrix_sha,metric),changed)

        class SyntheticDeadline:
            def __init__(self, remaining, stopped):
                self.snapshot = dict(remaining_seconds=remaining, stop_required=stopped)
                self.calls = 0

            def status(self):
                self.calls += 1
                return dict(self.snapshot)

        for label, remaining in [('budget_above_reserve',20.000001),('budget_full_worker',100.0)]:
            tick()
            synthetic = SyntheticDeadline(remaining, False)
            module.check_budget(synthetic)
            assert synthetic.calls == 1, 'ONE_BUDGET_SNAPSHOT'
            budget_positives.append(dict(case=label,snapshot=synthetic.snapshot,status_reads=synthetic.calls,accepted=True))
        for label, remaining, stopped in [('budget_at_reserve',20.0,False),
                ('budget_below_reserve',19.0,False),('budget_expired',0.0,False),('budget_stop_required',100.0,True)]:
            synthetic = SyntheticDeadline(remaining, stopped)
            reject(label,'SAVE_RESERVE',lambda synthetic=synthetic:module.check_budget(synthetic),synthetic.snapshot)
            assert synthetic.calls == 1, 'ONE_BUDGET_SNAPSHOT'
        assert len(negatives) == 46 and len(budget_positives) == 2, 'DECLARED_CONTROL_POPULATION'
        save('controls.json',dict(positive=positives,synthetic_report_relation_positive=True,
            budget_predicate_positive=budget_positives,strict_negative=negatives))
        tick()
        save('summary.json',dict(status='AUTHOR_TERNARY_MIXED_SAVED_BEST_V2_SYNTHETIC_CONTROLS_PASS',
            producer='/root/native_driver',timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],
            inputs_sha256=pins,geometry_fixture_positives=len(positives),synthetic_report_positives=1,
            strict_negative_cases=len(negatives),opaque_history_exclusion_equalities=len(positives),
            preserved_extractor_report_strict_negative_cases=42,budget_predicate_positives=len(budget_positives),
            budget_predicate_strict_negative_cases=4,binary_matrix_entries=sum(x['binary_matrix_entries'] for x in positives),
            unordered_pair_dot_products=sum(x['unordered_pair_dot_products'] for x in positives),
            actual_saved_target_input_read=False,actual_saved_report_read=False,native_calls=0,
            same_author_controls_only=True,independent_approval=False,target_resolution='NONE',deadline=deadline.status()))
        tick()
    except BaseException as error:
        save('failure.json',dict(error=repr(error),inputs_sha256=pins,completed_positive=len(positives),
            completed_negative=len(negatives),deadline=deadline.status(),outputs_preserved=True,automatic_retry=False))
        raise


if __name__ == '__main__':
    main()
