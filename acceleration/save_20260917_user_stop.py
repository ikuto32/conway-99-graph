"""Save the user-requested stop without launching any research process."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import yaml


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def main():
    base = Path('acceleration/results')
    resume = base / '20260917_resume'
    snapshot = resume / 'claims_at_user_stop.yaml'
    assert not snapshot.exists()
    snapshot.write_bytes(Path('CLAIMS.yaml').read_bytes())
    ledger = yaml.safe_load(snapshot.read_bytes())
    prior = yaml.safe_load((resume / 'claims_at_seventh_milestone.yaml').read_bytes())
    previous = {c['id']: c for c in prior['claims']}
    changes = [{k: c[k] for k in ('id', 'revision', 'status', 'review_state', 'scope')}
               for c in ledger['claims']
               if c['id'] not in previous or c['revision'] != previous[c['id']]['revision']]
    paths = [str(snapshot), 'docs/STOP_20260917_SIX_COORDINATE.md',
             str(resume / 'user_stop_process_observation.json'),
             str(resume / 'six_exclusion_validation.json'),
             str(base / '20260917_four_coordinate_exclusion_checkpoint.json'),
             str(base / '20260917_partial_eight_matchings/STOP_RECORD.json'),
             str(base / '20260917_independent_review/six_gpu_support.json'),
             str(base / '20260917_independent_review/six_exclusion_claim_binding.json'),
             str(base / '20260917_independent_review/six_cpu_failure.json'),
             str(base / '20260917_six_moment_pdhg/run01/summary.json')]
    refs = {p.replace('\\', '/'): digest(p) for p in paths}
    for path in paths:
        if path.endswith('.json'):
            data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
            for field in ('inputs_sha256', 'artifact_sha256'):
                for p, h in data.get(field, {}).items():
                    assert digest(p) == h, p
                    refs[p.replace('\\', '/')] = h
    stop = json.loads((base / '20260917_partial_eight_matchings/STOP_RECORD.json').read_bytes())
    process = json.loads((resume / 'user_stop_process_observation.json').read_text(encoding='utf-8-sig'))
    assert process['research_process_count'] == 0
    status = Counter((c['status'], c['review_state']) for c in ledger['claims'])
    report = dict(
        schema_version=1, timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        branch=subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip(),
        status='STOPPED_BY_USER', stop_reason='User requested preservation because token resources are running low.',
        research_restart_authorized=False, target_resolution='UNKNOWN', external_target_review='NOT_APPLICABLE',
        overall_search_coverage='UNKNOWN; no validated denominator',
        claim_counts=[dict(status=s, review_state=r, count=n) for (s, r), n in sorted(status.items())],
        claim_changes_since_seventh_milestone=changes,
        latest_mathematical_claim=dict(id='C-PARTIAL-K-SIX-COORDINATE-EXCLUSION', revision=1,
            exact_bound='14157/16384', fixed_K_edges=132, unrestricted_target=False),
        six_gpu_attempts=dict(completed=6, independently_checked=6, positive=4, nonpositive=2),
        six_CPU_outcome='SolveError; zero returned weights yield no exclusion or feasibility certificate.',
        eight_coordinate_partial=dict(completed_centers=stop['completed_centers'], center_population=84,
            saved_choices=stop['complete_domain_choices'], independently_checked=False,
            all_domains_complete=False, next_center=stop['next_center'], in_progress_masks_saved=False),
        process_observation=process, next_action='Await explicit user resume; then read stop/restart instructions.',
        previous_report='docs/RESEARCH_20260917_EIGHTH_WAVE.md',
        restart_document='docs/STOP_20260917_SIX_COORDINATE.md',
        draft_pr='https://github.com/ikuto32/conway-99-graph/pull/2',
        referenced_files_sha256=refs, builder_sha256=digest(__file__),
        limitations=['Registry validation is not mathematical verification.',
                    'Large local artifacts require their recorded recovery paths; preserve the workspace.',
                    'No exact recursive-stack checkpoint for the interrupted center.'])
    out = base / '20260917_user_requested_stop.json'
    with out.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print(json.dumps(dict(path=str(out), sha256=digest(out), claim_counts=report['claim_counts'], references=len(refs))))


if __name__ == '__main__':
    main()
