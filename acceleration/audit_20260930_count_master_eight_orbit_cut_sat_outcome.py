"""Independent native outcome/raw count witness audit after six profile cuts."""
from datetime import datetime, timezone
from itertools import permutations
from pathlib import Path
from types import SimpleNamespace
import argparse, copy, hashlib, json, platform, re, subprocess, sys, time, traceback
import audit_20260930_count_master_eight_orbit_cut_object as obj

ROOT, B, D = obj.ROOT, obj.B, obj.D
need, read, sha, save, key = obj.need, obj.read, obj.sha, obj.save, obj.key
R = B + 'count_master_eight_orbit_cut_native_pilot/'
EG = obj.ENCODING_PATH
EH = '4c919b9b48d4c9d6bf085480f9ae166172f33b457e85713c50c109c29bc57493'
CG = B + 'independent_review/count_master_eight_orbit_cut_object_calibration/summary.json'
CH = 'fc449db2cc7813c567bfb458f225c6f0ca93e5b39f400fd08d3697f876ece113'
REL = B + 'independent_review/hadamard_input_relabeling/'
REL_HASH = '9f188fd497b622b8e87611c220ddf931365089905cbd7b9f1fdbf9deb8ad4dd5'
EXPECTED_DIGEST = '086fc4155012236d30b13756b01e48ed2050db7cf028274b4aea533333ef0f17'
EXPECTED_PROFILE_HASH = '7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0'
LIMITS = dict(native_wall_seconds=60, conflicts=1000000, address_space_bytes=4294967296,
              trace_file_bytes=10737418240, kill_grace_seconds=5, outer_guard_seconds=70,
              maximum_research_calls=1, automatic_retry=False)
CID = 'C-FIXED-HADAMARD-SIX-CUT-COUNT-CSP-WITNESS'
SPEC = 'acceleration/audit_20260930_count_master_eight_orbit_cut_sat_outcome_spec.md'


def linux(relative):
    path = str((ROOT / relative).resolve()).replace('\\', '/')
    return '/mnt/' + path[0].lower() + path[2:]


def receipt_check(summary, text, workspace):
    rec = summary['receipt']
    need(rec['actual_exit_code'] == 10 and rec['outer_windows_guard_expired'] is False
         and rec['outer_windows_guard_seconds'] == 70, 'native SAT without guard expiry')
    need([line for line in text.splitlines() if line.startswith('s ')] == ['s SATISFIABLE'],
         'exact single native SAT status')
    expected = ['wsl.exe', '--distribution', 'Ubuntu-24.04', '--exec', '/usr/bin/timeout',
        '--signal=TERM', '--kill-after=5s', '60s', '/usr/bin/prlimit',
        '--as=4294967296:4294967296', '--fsize=10737418240:10737418240', '--core=0:0',
        linux('build/research-cadical195/source/build/cadical'), '--no-binary', '-c', '1000000',
        linux(obj.CNF), workspace + '/proof.drat']
    need(rec['command'] == expected, 'exact binary, CNF, output and resource command')
    need(summary['research_calls'] == 1 and summary['automatic_retry'] is False, 'single research call')
    need(summary['interpreted_result'] == 'COUNT_MASTER_EIGHT_ORBIT_CUT_SAT_RAW_UNCHECKED',
         'honest producer outcome status')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in text, 'saved native version')


def profile_identity(actual, expected):
    need(actual == expected, 'raw count profile exactly matches fresh complete decode')
    need(actual['full_factor'] is False and actual['target_graph'] is False
         and actual['residual_D'] is None, 'necessary count object, no factor assertion')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pins, started = {}, time.perf_counter()

    def pin(path, digest=None):
        path = key(path)
        if path not in pins: pins[path] = sha(ROOT / path)
        need(digest is None or pins[path] == digest, 'artifact identity ' + path)
        return path

    def authenticate_receipt(record):
        for stream in ['stdout', 'stderr']:
            pin(record[stream], record[stream + '_sha256'])

    try:
        pin(R + 'summary.json', '9bca784d427493d236a53202e8bfecd5b473769996d5a153ed13369c46c3834f')
        pin(R + 'independent_object/summary.json', '743d8296a01945d9c969eb9d41823be021e899936afe0f099da65a4bc3e14b94')
        for path in [R + 'manifest.json', R + 'workspace.json', R + 'main/launch.json',
                     R + 'main/solver.receipt.json', R + 'independent_object_command.receipt.json']:
            pin(path)
        run, child = read(R + 'summary.json'), read(R + 'independent_object/summary.json')
        for report in [run, child]:
            for path, digest in {**report['inputs_sha256'], **report['outputs_sha256']}.items(): pin(path, digest)
        pin(EG, EH)
        pin(CG, CH)
        need(read(EG)['status'] == obj.ENCODING_STATUS
             and read(CG)['status'] == 'INDEPENDENT_COUNT_MASTER_EIGHT_ORBIT_CUT_OBJECT_CALIBRATION_PASS',
             'frozen encoding and calibration approvals')
        need(child['status'] == 'INDEPENDENT_COUNT_MASTER_EIGHT_ORBIT_CUT_SAT_OBJECT_PASS'
             and child['actual_clauses_checked'] == 705839 and child['all_six_excluded_profiles_avoided'] is True,
             'saved independent child exact scope')
        need(read(R + 'manifest.json')['limits'] == LIMITS, 'configured bounded native protocol')
        workspace = read(R + 'workspace.json')['path']
        need(workspace.startswith('/tmp/conway99-count-master-orbit-cut-') and '\n' not in workspace,
             'recorded unique native proof workspace')
        text = (ROOT / (R + 'main/solver.stdout.log')).read_text()
        receipt_check(run, text, workspace)
        need(read(R + 'main/solver.receipt.json') == run['receipt'], 'raw native receipt identity')
        need(read(R + 'main/launch.json')['command'] == run['receipt']['command']
             and read(R + 'main/launch.json')['cnf_sha256'] == obj.DATA_PINS[obj.CNF], 'saved launch identity')
        authenticate_receipt(run['receipt'])
        need(read(R + 'independent_object_command.receipt.json') == run['independent_object_receipt'],
             'actual child receipt identity')
        need(run['independent_object_receipt']['actual_exit_code'] == 0
             and run['independent_object_receipt']['outer_windows_guard_expired'] is False,
             'saved child completed successfully')
        authenticate_receipt(run['independent_object_receipt'])
        transfer = run['proof_copy']
        pin(R + 'main/proof.drat', transfer['sha256'])
        need((ROOT / (R + 'main/proof.drat')).stat().st_size == transfer['bytes'] == 609634,
             'fresh complete saved SAT trace bytes')
        need(transfer['linux_source'] == workspace + '/proof.drat', 'trace from actual solver output path')
        for field in ['native_hash_receipt', 'copy_receipt']:
            rec = transfer[field]
            need(rec['actual_exit_code'] == 0 and rec['outer_windows_guard_expired'] is False, 'successful saved trace transfer')
            authenticate_receipt(rec)
        hashtext = (ROOT / transfer['native_hash_receipt']['stdout']).read_text().split()
        need(hashtext == [transfer['sha256'], transfer['linux_source']], 'historical native hash equals current host bytes')
        obs = run['fresh_process_observation']
        authenticate_receipt(obs)
        need(obs['actual_exit_code'] == 1 and obs['outer_windows_guard_expired'] is False
             and len((ROOT / obs['stdout']).read_text().strip().splitlines()) <= 1,
             'saved post-run named-process observation, not a current process assertion')

        evaluate_args = SimpleNamespace(variant='at_least_seven',
            assignment=ROOT / (R + 'main/parsed_model.json'), native_output=ROOT / (R + 'main/solver.stdout.log'),
            decoded=ROOT / (R + 'main/decoded_count_profile.json'))
        decoded, clause_count, truth = obj.evaluate(evaluate_args)
        profile_identity(read(R + 'independent_object/independent_count_profile.json'), decoded)
        pin(R + 'independent_object/independent_count_profile.json', EXPECTED_PROFILE_HASH)
        need(decoded['profile_sha256'] == EXPECTED_DIGEST and decoded['exception_count'] == 8
             and decoded['exceptional_groups'] == [1, 3, 5, 11, 13, 15, 18, 19]
             and truth == [True] * 6, 'exact new eight-exception count object and six avoided cuts')

        controls = []
        def reject(label, function):
            try: function()
            except (ValueError, KeyError, TypeError, IndexError):
                controls.append(label)
                return
            raise ValueError('corruption accepted ' + label)
        for label in ['exit', 'guard', 'wall', 'conflicts', 'input', 'binary', 'research_count', 'status']:
            bad, altered_text = copy.deepcopy(run), text
            if label == 'exit': bad['receipt']['actual_exit_code'] = 20
            elif label == 'guard': bad['receipt']['outer_windows_guard_expired'] = True
            elif label == 'wall': bad['receipt']['command'][7] = '600s'
            elif label == 'conflicts': bad['receipt']['command'][15] = '100'
            elif label == 'input': bad['receipt']['command'][16] = 'wrong.cnf'
            elif label == 'binary': bad['receipt']['command'][12] = 'different_solver'
            elif label == 'research_count': bad['research_calls'] = 2
            else: altered_text = text.replace('s SATISFIABLE', 's UNSATISFIABLE')
            reject('receipt_' + label, lambda q=bad, s=altered_text: receipt_check(q, s, workspace))
        for label in ['count', 'deviation', 'exception_groups', 'digest', 'false_factor']:
            bad = copy.deepcopy(decoded)
            if label == 'count': bad['coordinate_group_fibre_counts'][0][0][0] += 1
            elif label == 'deviation': bad['coordinate_fibre_deviations'][0][0][0] += 1
            elif label == 'exception_groups': bad['exceptional_groups'] = bad['exceptional_groups'][:-1]
            elif label == 'digest': bad['profile_sha256'] = '0' * 64
            else: bad['full_factor'] = True
            save(out / ('corrupt_profile_' + label + '.json'), bad)
            reject('raw_profile_' + label, lambda q=bad: profile_identity(q, decoded))
        model = read(D + 'model.json')
        values = obj.independent.signed_values(read(R + 'main/parsed_model.json')['assignment'], obj.N)
        for label, var in [('coordinate', decoded['selected_coordinate_selector_ids'][0]),
                           ('group', decoded['selected_group_selector_ids'][0]),
                           ('channel', model['count_channels'][0]['variables'][0]),
                           ('prefix', model['one_hot_domains'][0]['prefix_variables'][0])]:
            bad = values.copy()
            bad[var] = not bad[var]
            reject('assignment_flip_' + label, lambda v=bad: obj.base.cnf_object(ROOT / obj.CNF, v, obj.M))

        # Reuse the independently verified complete coordinate-action census as a
        # premise, never promote it to a census of all36-row/factor symmetries.
        pin(REL + 'summary.json', REL_HASH)
        rel = read(REL + 'summary.json')
        need(rel['status'] == 'INDEPENDENT_FIXED_INPUT_COORDINATE_RELABELING_CENSUS_PASS', 'reviewed coordinate-action family')
        for path in [REL + 'accepted_coordinate_maps.json', REL + 'claim_binding.json']:
            pin(path, rel['outputs_sha256'][path])
        need(read(REL + 'accepted_coordinate_maps.json') == [list(range(12))],
             'only identity coordinate map preserves this support in the specified family')
        old_path = B + 'independent_review/count_master_sat_outcome/independent_count_profile.json'
        pin(old_path, '0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152')
        old = read(old_path)['coordinate_group_fibre_counts']
        current = decoded['coordinate_group_fibre_counts']
        raw_path = B + 'hadamard20_support/six_prism.json'
        pin(raw_path, 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d')
        raw = read(raw_path)
        comparisons = []
        for tau in permutations(range(3)):
            moved = [[[0] * 3 for _ in range(20)] for _ in range(12)]
            for a in range(12):
                for g in range(20):
                    for f in range(3): moved[a][g][tau[f]] = old[a][g][f]
            differing = [(a, g, f) for a in range(12) for g in range(20) for f in range(3)
                         if moved[a][g][f] != current[a][g][f]]
            need(differing, 'new count table outside every old global-fibre image')
            rows = [12 * tau[f] + a for f in range(3) for a in range(12)]
            need(all(matrix[rows[i]][rows[j]] == matrix[i][j]
                     for matrix in [raw['core_adjacency'], raw['prescribed_Gram36']]
                     for i in range(36) for j in range(36)), 'literal fixed C/Gram fibre covariance')
            a, g, f = differing[0]
            comparisons.append(dict(fibre_image=list(tau), unequal_count_entries=len(differing),
                first_difference=dict(coordinate=a, group=g, fibre=f,
                    transformed_old=moved[a][g][f], new=current[a][g][f])))
        save(out / 'restricted_relabeling_assessment.json', dict(
            status='DIFFERENT_UNDER_SPECIFIED_VERIFIED_ACTION_FAMILY',
            coordinate_action_family='All46080 permutations preserving the six fixed matching pairs, restricted to those preserving the literal support; only identity survives.',
            coordinate_census_gate=REL + 'summary.json', coordinate_census_sha256=REL_HASH,
            complete_global_fibre_comparisons=comparisons,
            identical_support_column_permutations='Count tables are unchanged by these column reorderings.',
            arbitrary_factor_or_target_symmetry_distinctness='UNKNOWN',
            limitation='No claim of novelty modulo all36-row actions, arbitrary core embeddings, supports or target graph automorphisms.'))
        save(out / 'controls.json', dict(actual_native_SAT_receipt_positive=True,
            actual_complete_count_object_positive=True, actual_clauses_checked=clause_count,
            rejected_corruptions=controls, shared_frozen_checker=True,
            raw_profile_corruptions_saved=True, new_solver_calls=0))
        save(out / 'independent_count_profile.json', decoded)
        save(out / 'independent_cut_avoidance.json', dict(cut_satisfaction=truth, profile_sha256=EXPECTED_DIGEST))
        for path in [key(__file__), SPEC, key(obj.__file__), key(obj.base.__file__),
                     key(obj.independent.__file__), 'uv.lock', 'pyproject.toml']: pin(path)
        binding_path = str(Path(EG).parent / 'claim_bindings.json').replace('\\', '/')
        pin(binding_path, read(EG)['outputs_sha256'][binding_path])
        premise = next(c for c in read(binding_path) if c['id'] == 'C-FIXED-HADAMARD-COUNT-MASTER-SIX-PROFILE-CUT-ENCODING')
        need(premise['revision'] == 1 and premise['status'] == 'VERIFIED' and premise['review_state'] == 'CLEAR',
             'exact reviewed cut encoding premise')
        now = datetime.now(timezone.utc).isoformat()
        claim = dict(id=CID, revision=1, kind='construction', basis=['COMPUTED'], status='VERIFIED',
            review_state='CLEAR', statement='The pinned155939-variable705839-clause count-master formula with at least seven exceptional groups and all six excluded-profile nogoods has the complete saved satisfying assignment, independently decoding to count profile086fc4155012236d30b13756b01e48ed2050db7cf028274b4aea533333ef0f17 with exactly eight exceptional groups.',
            scope='One exact count-CSP witness avoiding the six literal forbidden tables; no full factor, unsummed Gram, scalar interval test, cross-group caps or residual graph asserted.',
            assumptions=['Exact immutable count model, six-cut encoding and literal fixed support authenticated by the independent encoding gate.'],
            dependencies=[dict(id=premise['id'], revision=1, relation='encoding_equivalence')],
            premise_binding=dict(path=binding_path, sha256=pins[binding_path], claim_id=premise['id'], revision=1),
            verifier='/root/eight_domain_audit',
            checking_method='Fresh complete native/JSON and705839-clause replay, raw720-count/marginal/local-signature decode, six explicit cut avoidances, native receipt/input/trace authentication and adversarial controls. Reuses the frozen independent object checker; not a new independent implementation of its parser.',
            trusted_components=['Frozen independent cut-object checker and original count decoder, pinned independent encoding/calibration gates, Python exact arithmetic. No producer imports.'],
            verification_records=[dict(claim_id=CID, claim_revision=1, verifier='/root/eight_domain_audit',
                kind='independent_artifact_checking', timestamp=now, outcome='PASS', inputs_sha256=pins,
                command=[sys.executable, *sys.argv], cwd=str(ROOT),
                scope='Complete actual assignment, native output, clause set, raw count table and saved execution evidence.')],
            limitations=['A count-table witness is not a factor, graph or target resolution.',
                         'The saved SAT trace is execution evidence, not an UNSAT proof.',
                         'Distinctness beyond the explicitly checked coordinate/global-fibre action family is UNKNOWN.',
                         'The saved post-run process observation is historical; no currently running process is asserted.'],
            artifact_availability='LOCAL_ONLY', availability_reason='Awaiting parent wave25 publication.',
            created_at=now, updated_at=now, external_review=None,
            external_review_null_reason='Internal independent artifact review only.')
        save(out / 'claim_binding.json', claim)
        conflicts = re.findall(r'^c conflicts:\s+(\d+)\b', text, re.M)
        need(conflicts == ['241'], 'observed exact native conflict statistic')
        result = dict(status='INDEPENDENT_COUNT_MASTER_EIGHT_ORBIT_CUT_NATIVE_SAT_OUTCOME_PASS',
            timestamp=now, source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
            inputs_sha256=pins, outputs_sha256={key(p): sha(p) for p in out.iterdir()},
            native_calls_completed=1, actual_native_exit=10, actual_clauses_checked=clause_count,
            observed_conflicts=241, configured_limits=LIMITS, exception_count=8,
            exceptional_groups=decoded['exceptional_groups'], profile_sha256=EXPECTED_DIGEST,
            all_six_excluded_profiles_avoided=True, restricted_relabeling_comparisons=6,
            arbitrary_symmetry_distinctness='UNKNOWN', rejected_corruptions=len(controls),
            partial_SAT_trace=dict(path=R + 'main/proof.drat', sha256=transfer['sha256'], bytes=transfer['bytes'],
                                   proof_of_UNSAT=False, availability='LOCAL_ONLY'),
            approved_claim_ids=[CID], new_solver_calls=0, target_resolution=False,
            elapsed_seconds=time.perf_counter() - started)
        save(out / 'summary.json', result)
        print(json.dumps(dict(status=result['status'], summary_sha256=sha(out / 'summary.json'),
                              binding_sha256=sha(out / 'claim_binding.json'))))
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), traceback=traceback.format_exc(),
            source_sha256=sha(Path(__file__)), inputs_sha256=pins))
        raise


if __name__ == '__main__': main()
