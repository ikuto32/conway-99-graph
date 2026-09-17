"""Freeze ledger-derived foundation and certificate-simplification progress."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import yaml


def digest(p): return sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_bytes())
def save(p, value):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2); f.write('\n')


def main():
    base = 'acceleration/results/20260917_'
    resume = base + 'resume/'
    snapshot = resume + 'claims_at_seventh_milestone.yaml'
    assert not Path(snapshot).exists()
    ledger = yaml.safe_load(Path('CLAIMS.yaml').read_bytes())
    previous = yaml.safe_load(Path(resume + 'claims_at_sixth_milestone.yaml').read_bytes())
    before = {c['id']:c for c in previous['claims']}
    changes = [{k:c[k] for k in ('id','revision','status','review_state','statement','scope')} for c in ledger['claims'] if c['id'] not in before or c['revision'] != before[c['id']]['revision']]
    assert len(changes) == 5 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in changes)
    paths = dict(domains=base+'independent_review/four_matchings/summary.json',
        full_model=base+'independent_review/four_matching_moments.json',
        filter=base+'independent_review/four_coordinate_matching_filter/summary.json',
        filtered_model=base+'independent_review/four_matching_filtered_moments.json',
        small_certificate=base+'independent_review/two_coordinate_small_certificate.json',
        recovery=base+'independent_review/recovery_tools.json',
        parent=base+'two_coordinate_checkpoint.json', remote=resume+'sixth_remote_review_observation.json')
    reports = {k:load(p) for k,p in paths.items()}
    refs = {p:digest(p) for p in paths.values()}
    for key in ('domains','full_model','filter','filtered_model','small_certificate','recovery'):
        for p,h in reports[key]['inputs_sha256'].items():
            assert digest(p)==h, p
            assert p not in refs or refs[p]==h
            refs[p]=h
    assert reports['filter']['counts']['original_count']==290460
    assert reports['filter']['counts']['surviving_count']==230879
    assert reports['small_certificate']['D1']['lower_bound']==204
    now = datetime.now(timezone.utc).isoformat()
    commit = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    Path(snapshot).write_bytes(Path('CLAIMS.yaml').read_bytes())
    refs[snapshot]=digest(snapshot)
    checkpoint=base+'four_coordinate_foundations_checkpoint.json'
    data=dict(created_utc=now, source_commit=commit, target_resolution='UNKNOWN',
        status='VERIFIED_FOUNDATIONS_AND_SIMPLIFIED_CONDITIONAL_CERTIFICATE',
        previous_checkpoint_preserved=dict(path=paths['parent'],sha256=refs[paths['parent']]),
        current_best=reports['parent']['current_best'],current_star_marginal_best=reports['parent']['current_star_marginal_best'],
        claim_changes=changes, four_coordinate_exclusion_established=False,
        counts=dict(four_original_choices=290460,four_matching_rejected=59581,four_matching_survivors=230879,empty_domains=0,
            two_coordinate_weight_sets_checked=9,two_coordinate_positive_weight_sets=9),
        simplified_two_coordinate_bound=reports['small_certificate']['D1'],
        referenced_files_sha256=refs,directly_hash_checked_reference_count=len(refs),
        process_state='UNKNOWN; this report generator does not observe processes',
        next_experiment='Complete separately capped four-coordinate filtered moment solve and independently check any exact support bound; bounded six-coordinate domain pilot is separate.',
        overall_search_coverage='UNKNOWN; no validated denominator',draft_pr='https://github.com/ikuto32/conway-99-graph/pull/2',builder_sha256=digest(__file__))
    save(checkpoint,data)
    save(resume+'seventh_milestone.json',dict(as_of=now,source_commit=commit,previous_report='docs/RESEARCH_20260917_SIXTH_WAVE.md',checkpoint=checkpoint,checkpoint_sha256=digest(checkpoint),claim_changes=changes,counts=data['counts'],target=ledger['target'],input_paths=paths,referenced_files_sha256=refs,draft_pr=data['draft_pr']))
    print(json.dumps(dict(checkpoint=checkpoint,sha256=digest(checkpoint),claims_changed=len(changes),references=len(refs))))


if __name__=='__main__': main()
