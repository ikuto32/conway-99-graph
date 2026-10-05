"""Independent checkpoint/report coherence; mathematical gates are premises."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import file_digest
from pathlib import Path
import argparse
import json
import re
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B+'independent_review/'


def need(ok, why):
    if not ok: raise ValueError(why)


def sha(path):
    with Path(path).open('rb') as stream: return file_digest(stream, 'sha256').hexdigest()


class UniqueLoader(yaml.SafeLoader): pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        need(key not in result, 'duplicate YAML key')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True); args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False); pins = {}
    def bind(path):
        p = ROOT/path; pins[path] = sha(p); return p
    def read(path): return json.loads(bind(path).read_bytes())
    ledger_path = B+'resume/claims_at_fourteenth_milestone.yaml'
    ledger = yaml.load(bind(ledger_path).read_text(encoding='utf-8'), Loader=UniqueLoader)
    checkpoint = read(B+'resume/fourteenth_milestone_checkpoint.json')
    report_path = 'docs/RESEARCH_20260930_FOURTEENTH_WAVE.md'; report = bind(report_path).read_text(encoding='utf-8')
    bind('acceleration/record_20260930_fourteenth_checkpoint.py')
    ids = []; previous_after = None
    for directory in ['fourteenth_gpu_registration', 'fourteenth_pair_modular_registration', 'fourteenth_factor_results_registration']:
        receipt = read(B+directory+'/summary.json')
        before = bind(B+directory+'/CLAIMS.before.yaml'); after = bind(B+directory+'/CLAIMS.after.yaml')
        need(sha(before) == receipt['previous_ledger_sha256'] and sha(after) == receipt['ledger_sha256'], 'exact registration snapshot hashes')
        if previous_after is not None: need(previous_after == before.read_bytes(), 'registration chain continuity')
        previous_after = after.read_bytes(); ids.extend(receipt['new_claim_ids'])
    need(previous_after == (ROOT/ledger_path).read_bytes(), 'checkpoint ledger is final registered snapshot')
    claims = ledger['claims']; by_id = {c['id']:c for c in claims}
    need(len(by_id) == len(claims) == checkpoint['claim_population'] == 138, 'exact claim population and unique IDs')
    need(dict(Counter(c['status'] for c in claims)) == checkpoint['claim_status_counts'] == {'VERIFIED':136, 'CANDIDATE':2}, 'status counts')
    need(dict(Counter(c['review_state'] for c in claims)) == checkpoint['claim_review_counts'] == {'CLEAR':138}, 'review counts')
    need(len(ids) == len(set(ids)) == 8 and checkpoint['new_verified_ids'] == ids, 'exact eight new claims')
    need(all(by_id[c]['revision'] == 1 and by_id[c]['status'] == 'VERIFIED' and by_id[c]['review_state'] == 'CLEAR' for c in ids), 'all eight exact revisions verified and clear')
    for cid in ids: need(report.count('| `'+cid+'` |') == 1, 'each new claim exactly once in report table')
    for path, expected in checkpoint['evidence_sha256'].items(): need(sha(bind(path)) == expected, 'checkpoint evidence hash '+path)
    prior = B+'resume/thirteenth_milestone_checkpoint.json'; need(sha(bind(prior)) == checkpoint['previous_checkpoint_sha256'], 'previous checkpoint pin')
    need(checkpoint['target_resolution'] == 'UNKNOWN' and checkpoint['external_review'] is None and checkpoint['external_review_null_reason'], 'target and external-review distinction')
    for field in ['complete99_graphs', 'independently_validated_new_target_factors', 'new_complete_unsat_traces', 'newly_closed_unrestricted_branches']:
        need(checkpoint[field] == 0, 'no construction/exclusion promotion')
    need(checkpoint['completed_native_attempts'] == checkpoint['native_UNKNOWN_results'] == 2 and checkpoint['native_SAT_results'] == checkpoint['native_UNSAT_results'] == 0, 'exact native stage counts')
    run_checks = []
    for row, name, exit_code, conflicts, reason in zip(checkpoint['native_runs'],
            ['variable_core_pair_orbits', 'prism_column_caps'], [0,124], [5000002,2374985], ['UNKNOWN_CONFLICT_LIMIT','UNKNOWN_TIMEOUT'], strict=True):
        need(row['name'] == name and row['result'] == reason and row['attempts'] == 1 and row['exit_code'] == exit_code, 'exact attempt label/result')
        run = read(row['summary']); audit = read(row['audit'])
        need(sha(ROOT/row['summary']) == row['summary_sha256'] and sha(ROOT/row['audit']) == row['audit_sha256'], 'exact completed run and independent audit')
        need(run['actual_exit_code'] == exit_code and run['research_calls'] == 1 and not run['receipt']['outer_windows_guard_expired'], 'native receipt outcome')
        stdout_path = run['receipt']['stdout']; stdout = bind(stdout_path).read_text(encoding='utf-8')
        got = re.findall(r'^c conflicts:\s+(\d+)\s', stdout, re.M)
        need(got == [str(conflicts)] and not re.search(r'^[sv] ', stdout, re.M), 'raw log conflicts and no SAT/UNSAT/model')
        need(row['observed_conflicts'] == conflicts == audit['outcome']['observed_final_conflicts'], 'observed conflicts agree independently')
        need(row['configured_conflicts'] == 5000000 and row['configured_seconds'] == 900, 'configured vs observed limits')
        need(row['wrapper_wall_seconds'] == run['receipt']['wall_seconds'] == audit['outcome']['wrapper_wall_seconds'], 'exact wrapper timing')
        trace = audit['partial_trace']
        need(row['incomplete_trace_bytes'] == trace['bytes'] == run['proof_copy']['bytes'] and row['incomplete_trace_sha256'] == trace['sha256'] == run['proof_copy']['sha256'], 'trace identity joins')
        need(row['incomplete_trace_availability'] == trace['availability'] == 'LOCAL_ONLY' and not trace['proof_checked'] and not trace['unsat_certificate'], 'partial trace is not proof or public artifact')
        run_checks.append(dict(name=name, observed_conflicts=conflicts, independent_audit_sha256=sha(ROOT/row['audit']), scope='Receipt/log/outcome coherence; prior complete trace hashing is a pinned premise, not repeated here.'))
    pilot = read(I+'factor_annealer_pilot/summary.json'); cooling = read(I+'factor_annealer_cooling_v3/summary.json')
    failed = read(B+'factor_annealer_cooling/summary.json'); correction = read(I+'factor_annealer_pilot_availability_correction/summary.json')
    gpu = checkpoint['gpu']; p, c = gpu['pilot'], gpu['corrected_cooling']
    for key, expected in [('completed_cases',6), ('chunk_best_states',48), ('final_current_states',96), ('final_best_states',96)]:
        need(p[key] == pilot[key] == expected, 'pilot '+key)
    need(p['proposal_records'] == pilot['saved_proposal_records'] == 6*16*8*1024, 'pilot saved proposal population')
    need(p['minima'] == [dict(label=r['case']['label'], value=r['minimum_saved_score']) for r in pilot['cases']], 'all six pilot minima')
    for key, expected in [('chunk_best_states',64), ('stage_final_current_states',64), ('stage_final_best_states',64)]:
        need(c[key] == cooling[key] == expected, 'cooling '+key)
    need(c['continuing_chains'] == cooling['continued_chain_population'] == 32, 'continuing chain identities')
    need(c['proposal_records'] == cooling['new_saved_proposal_records'] == 4*16*16*1024 and c['completed_stages'] == cooling['stage_counts']['completed'] == 4, 'cooling stage/proposal populations')
    need(c['minima'] == [dict(label=r['case']['label'], initial=r['initial_best_score'], final=r['final_best_score']) for r in cooling['cases']], 'four cooling continuation minima')
    need([(r['initial'],r['final']) for r in c['minima']] == [(164,134),(134,124),(184,146),(146,142)], 'precise comparable minima')
    need(gpu['failed_cooling'] == dict(attempted_stages=2, completed_stages=0, errors=2, skipped_stages=2, new_proposal_records=0), 'failed pilot state counts')
    need(failed['completed_new_proposals'] == 0 and failed['errors'] == 2 and failed['skipped_stages'] == 2, 'failed run pins')
    need(gpu['objective_version'] == pilot['objective_version'] == cooling['objective_version'] == 'TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1', 'comparable objective version')
    need(gpu['individual_campaign_transitions_replayed'] is False and gpu['exact_zero_saved_factors'] == 0, 'saved-state scope without transition or zero claim')
    need(pilot['all_checkpoint_chain_current_scores_checked'] == pilot['all_checkpoint_chain_best_scores_checked'] == 768, 'pilot checkpoint score populations')
    need(cooling['checkpoint_current_scores_checked'] == cooling['checkpoint_best_scores_checked'] == 1024, 'cooling checkpoint score populations')
    need(correction['original_value'] == 'PUBLIC' and correction['corrected_value'] == 'LOCAL_ONLY' and not correction['public_publication_confirmed'], 'public availability correction retained')
    need(correction['corrected_report']['sha256'] == sha(ROOT/(I+'factor_annealer_pilot/summary.json')), 'correction binds unchanged original report')
    execution = checkpoint['execution']
    stdout_path = B+'resume/fourteenth_process_snapshot.stdout.log'; stderr_path = B+'resume/fourteenth_process_snapshot.stderr.log'
    text = bind(stdout_path).read_text(encoding='utf-8'); bind(stderr_path)
    need(sha(ROOT/stdout_path) == execution['stdout_sha256'] and sha(ROOT/stderr_path) == execution['stderr_sha256'], 'fresh checkpoint process observation identities')
    need(execution['exit_code'] == 0 and execution['state'] == 'CADICAL_PROCESS_OBSERVED', 'actual saved process state')
    need('20260930_connected_fixed_core_cnf/core_00/instance.cnf' in text and 'prism_column_caps_v3/instance.cnf' not in text and 'variable_core_pair_orbits/instance.cnf' not in text, 'observed later cohort identified, completed cohort not implied running')
    need(datetime.fromisoformat(execution['observed_at']).tzinfo is not None, 'timestamped historical observation')
    for phrase in ['not a worldwide literature verdict', 'No unrestricted branch or fixed core was excluded',
            'individual campaign transitions were not replayed', 'incomplete traces remain LOCAL_ONLY', 'after publication',
            'Original successful perturbation matrices were not saved', 'different' if False else 'Different formulas and stops']:
        need(phrase in report, 'report scoped qualification '+phrase)
    need('Overall search coverage: UNKNOWN; no validated denominator.' in report and checkpoint['coverage'] == 'Overall search coverage: UNKNOWN; no validated denominator.', 'no invented coverage denominator')
    workflow = bind('.github/workflows/claims.yml').read_text(encoding='utf-8')
    for phrase in ['uv sync --locked', 'test_validate_claims.py', "'--hashes', 'public'", "'--previous'", 'SKIPPED previous-ledger impact review']:
        need(phrase in workflow, 'CI semantic validation component '+phrase)
    bind('acceleration/validate_claims.py'); bind('acceleration/test_validate_claims.py'); bind('docs/claims.schema.json')
    pins[Path(__file__).resolve().relative_to(ROOT).as_posix()] = sha(__file__)
    result = dict(status='INDEPENDENT_FOURTEENTH_CHECKPOINT_COHERENCE_PASS', timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(), command=[sys.executable,*sys.argv],
        inputs_sha256=pins, claim_population=138, verified_clear=136, candidate_clear=2, new_claim_ids=ids, native_run_checks=run_checks,
        GPU_counts_checked=True, report_scope_reading='No target result, global exclusion, public trace availability or campaign-transition verification is claimed.',
        material_corrections_required=[], editorial_observations=['The checkpoint/report are internally consistent; compact word-number spacing is stylistic only.',
            'ACTIVE_RESEARCH.md still points to thirteenth at review time; root-owned publication indexes are pending, outside this frozen checkpoint.'],
        verifier='/root/structural_attack independent checkpoint/source-record comparison', producer_checkpoint_imported=False,
        shared_components=['Pinned prior mathematical/engineering audits are premises; no discovery is reverified by this count/hash audit.',
            'Reviewer authored the separate publication catalog/replay guide, which are not claimed independently reapproved by this checkpoint audit.'],
        validation_plan=['uv run --locked --offline --cache-dir .uv-cache-20260917 python -B -m unittest discover -s acceleration -p test_validate_claims.py -v',
            'uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/validate_claims.py --hashes available --previous acceleration/results/20260930_resume/claims_at_thirteenth_milestone.yaml --out build/fourteenth-local-validation.json',
            'After immutable publication, repeat --hashes public and preserve explicit skipped/unavailable checks; green CI is not mathematical verification.'],
        limitations=['No fresh proof replay or GPU transition replay.', 'This records the checkpoint timestamp, not current process liveness.',
            'Draft PR unmerged/public hosting status is inherited narrative context, not freshly checked remotely by this local coherence audit.'],
        mathematical_reverification=False, target_resolution='UNKNOWN', external_review=False, artifact_availability='LOCAL_ONLY')
    for path,h in pins.items(): need(sha(ROOT/path) == h, 'no concurrent edit to reviewed input')
    with (args.out/'summary.json').open('x',encoding='utf-8',newline='\n') as stream: json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=result['status'], sha256=sha(args.out/'summary.json'))))


if __name__ == '__main__': main()
