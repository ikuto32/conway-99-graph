"""Stop bookkeeping only: aggregate saved gates; never launch research."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = 'acceleration/results/'
OUT = ROOT / (BASE + '20261001_user_stop')


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def save(name, value):
    with (OUT / name).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def main():
    OUT.mkdir(exist_ok=False)
    raw = (ROOT / 'CLAIMS.yaml').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '9e76cdb8efa4ee9fca25243b461002720b9d387acf00381f0893c01bb5655719'
    ledger = yaml.safe_load(raw)
    claims = ledger['claims']
    assert len(claims) == 308 and all(c['review_state'] == 'CLEAR' for c in claims)
    assert ledger['target']['status'] == 'UNKNOWN' and not ledger['target']['supporting_claims']
    registrations = []
    new_ids = []
    previous = None
    for folder in ['20261001_thirtieth_initial_registration', '20261001_stop_registration']:
        path = BASE + folder + '/summary.json'
        record = read(path)
        before = (ROOT / BASE / folder / 'CLAIMS.before.yaml').read_bytes()
        after = (ROOT / BASE / folder / 'CLAIMS.after.yaml').read_bytes()
        assert hashlib.sha256(before).hexdigest() == record['previous_ledger_sha256']
        assert hashlib.sha256(after).hexdigest() == record['ledger_sha256']
        assert previous is None or before == previous
        previous = after
        new_ids.extend(record['new_claim_ids'])
        registrations.append(dict(path=path, sha256=digest(path), new_claim_ids=record['new_claim_ids']))
    assert previous == raw and len(set(new_ids)) == 8
    gates = [('20260930', 'exact_eight_first12_proofs'), ('20260930', 'exact_eight_next32_proofs'),
             ('20260930', 'exact_eight_sizeclass16_proofs'), ('20260930', 'exact_eight_next64_proofs')]
    gates += [('20261001', f'exact_eight_prefix64_batch{b:02d}_proofs') for b in range(2, 5)]
    batches, union = [], set()
    for day, folder in gates:
        path = BASE + day + '_independent_review/' + folder + '/summary.json'
        sha = digest(path)
        artifact_ids = {a['id'] for a in ledger['artifacts'] if a['path'] == path and a['sha256'] == sha}
        owners = [c['id'] for c in claims if artifact_ids.intersection(c['evidence']) and c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR']
        assert owners
        report = read(path)
        ids = [c['case_id'] for c in report['case_records']]
        assert len(ids) == len(set(ids)) == report['completed_proof_replays'] and not union.intersection(ids)
        assert all(c['outcome'] == 'UNSAT_VERIFIED' and c['trace']['complete_proof'] and c['replay']['accepted'] and c['replay']['actual_exit_code'] == 0 for c in report['case_records'])
        union.update(ids)
        batches.append(dict(path=path, sha256=sha, claim_ids=owners, cases=len(ids), proof_bytes=sum(c['trace']['bytes'] for c in report['case_records'])))
    assert len(union) == 316
    stop_path = BASE + '20261001_exact_eight_prefix64_batch05_execution/user_stop_checkpoint.json'
    assert digest(stop_path) == 'aabe73c99f961d7aeb9db1d8e771b6653e9cb681ca6e94ea736d7ef26508f085'
    stop = read(stop_path)
    for path, sha in stop['inputs_sha256'].items():
        assert digest(path) == sha
    assert stop['batch05']['native_research_calls'] == stop['batch05']['native_preflight_calls'] == stop['batch05']['proof_audits'] == 0
    assert all(not (ROOT / path).exists() for path in stop['unstarted_paths_confirmed_absent'])
    common = ['uv', 'run', '--locked', '--offline', '--cache-dir', '.uv-cache-20260917', 'python', '-B', 'acceleration/native_20260930_exact_eight_explicit_batch.py']
    inputs = [('selection', BASE + '20261001_exact_eight_prefix64_batch05_selection/selection.json'),
              ('batch-summary', BASE + '20261001_exact_eight_prefix64_batch05_consolidated/summary.json'),
              ('encoding-gate', BASE + '20261001_independent_review/exact_eight_prefix64_batch05_cnfs_v3/summary.json'),
              ('object-gate', BASE + '20261001_independent_review/exact_eight_prefix64_batch05_object_calibration/summary.json')]
    arguments = []
    for flag, path in inputs:
        arguments += ['--' + flag, path, '--' + flag + '-sha256', digest(path)]
    arguments += ['--object-checker', 'acceleration/audit_20260930_exact_eight_explicit_batch_v3.py', '--attempt-id', 'prefix64-batch05-after-user-resume01']
    resume = dict(status='SAVED_ONLY_NOT_EXECUTED', explicit_new_user_resume_required=True, cwd=str(ROOT), environment={'UV_PROJECT_ENVIRONMENT': 'build/research-venv'},
                  prerequisites=['Reauthenticate all saved input and source hashes.', 'Check live processes and reserves afresh.', 'Require explicit preflight PASS before research.', 'Use fresh output paths; do not overwrite prior evidence.'],
                  preflight_argv=common + ['--preflight', '--out', BASE + '20261001_exact_eight_prefix64_batch05_native_preflight_after_resume01'] + arguments,
                  research_argv=common + ['--research', '--out', BASE + '20261001_exact_eight_prefix64_batch05_native_after_resume01'] + arguments,
                  next_verification='Only after an actual result: independently decode any SAT object or replay each complete UNSAT proof with the pinned proof-v2 checker. These commands do not themselves establish an exclusion.',
                  source_hashes={p: digest(p) for p in ['uv.lock', 'pyproject.toml', 'acceleration/native_20260930_exact_eight_explicit_batch.py', 'acceleration/native_20260930_exact_eight_explicit_batch_spec.md', 'acceleration/audit_20260930_exact_eight_explicit_batch_v3.py', 'acceleration/audit_20260930_exact_eight_explicit_batch_proofs_v2.py']})
    save('resume_plan.json', resume)
    (OUT / 'CLAIMS.snapshot.yaml').write_bytes(raw)
    record = dict(schema='USER_STOP_V1', timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  command=[sys.executable, *sys.argv], cwd=str(ROOT), source_sha256=digest(Path(__file__).relative_to(ROOT)),
                  status='STOPPED_AT_EXPLICIT_USER_REQUEST', reason='今回の実行をきりが良いところで正常に終了してください。', automatic_resume=False,
                  previous_report='docs/RESEARCH_20261001_TWENTYNINTH_WAVE.md', target_resolution='UNKNOWN', external_review='No target resolution artifact; no external mathematical review asserted.',
                  claim_population=len(claims), status_counts=dict(Counter(c['status'] for c in claims)), review_counts=dict(Counter(c['review_state'] for c in claims)),
                  ledger_sha256=digest('CLAIMS.yaml'), registrations=registrations, new_verified_ids=new_ids, completed_literal_batches=batches,
                  frozen_literal_population=792, distinct_literal_exclusions=len(union), unresolved_literal_cases=792-len(union), new_literal_exclusions=sum(b['cases'] for b in batches[-2:]),
                  complete_proof_bytes=sum(b['proof_bytes'] for b in batches), new_proof_bytes=sum(b['proof_bytes'] for b in batches[-2:]),
                  batch05=stop['batch05'], stop_process_record=dict(path=stop_path, sha256=digest(stop_path), observation=stop['targeted_process_observation']),
                  fresh_mathematical_runs=0, artifact_availability='New evidence closure remains LOCAL_ONLY. This stop package does not establish complete public replay.',
                  overall_search_coverage='UNKNOWN; no validated denominator.', best_result='Previously verified fixed-support lower bound of eight unbalanced groups unchanged; literal exclusions are restricted cases, not a target-wide bound.',
                  deferred=['Batch05 native preflight, native search and proof replay.', 'Batch06 allocation.', 't6 integer-lift inventory.', 'Full wave30 public evidence packaging.'],
                  superseded_unexecuted=['register_20261001_thirtieth_followup_claims.py', 'record_20261001_thirtieth_checkpoint.py', 'inventory_20261001_thirtieth_candidates.py'],
                  limitations=['316 exclusions concern one fixed six-prism Hadamard support; no unrestricted normalization or target automorphism is assumed.', 'The third-star exclusion requires the literal t6_h1 induced graph, prism-freeness and the stated rank-11 premise; it adds zero cases to the 792-case campaign.', 'No whole-family or unrestricted nonexistence conclusion.', 'Counts aggregate saved independently checked records; this bookkeeping does not rerun or approve mathematics.'],
                  resume_plan=dict(path=(OUT / 'resume_plan.json').relative_to(ROOT).as_posix(), sha256=digest((OUT / 'resume_plan.json').relative_to(ROOT))))
    save('checkpoint.json', record)
    assert (ROOT / 'CLAIMS.yaml').read_bytes() == raw
    print(json.dumps({k: record[k] for k in ['status', 'claim_population', 'distinct_literal_exclusions', 'unresolved_literal_cases', 'new_literal_exclusions', 'complete_proof_bytes']}))


if __name__ == '__main__':
    main()
