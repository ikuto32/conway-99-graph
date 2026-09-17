"""Register independently checked local matching partition; no target claim."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]


def main():
    ledger=yaml.safe_load((ROOT/'CLAIMS.yaml').read_text(encoding='utf-8'))
    report_path='acceleration/results/20260917_independent_review/triangle_matching/summary.json'
    review=json.loads((ROOT/report_path).read_bytes())
    assert review['status']=='INDEPENDENT_EXACT_TRIANGLE_MATCHING_FILTER_PASS'
    binding=review['claim_binding']
    assert binding['id']=='C-STAR-TRIANGLE-FILTER-18481' and binding['revision']==1
    for field in ('inputs_sha256','vertex_reports_sha256'):
        for path,h in review[field].items():
            assert sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    entries={
        'triangle-manifest':'acceleration/results/20260917_theory/matching_baseline18481/manifest.json',
        'triangle-producer-summary':'acceleration/results/20260917_theory/matching_baseline18481/summary.json',
        'triangle-independent-review':report_path,
        'triangle-independent-derivation':'acceleration/results/20260917_independent_review/TRIANGLE_MATCHING_AUDIT.md',
        'triangle-independent-source':'acceleration/audit_20260917_triangle_matching.py'}
    for id,path in entries.items():
        ledger['artifacts'].append(dict(id=id,path=path,sha256=sha256((ROOT/path).read_bytes()).hexdigest(),availability='LOCAL_ONLY',
            retrieval='Workspace relative path; publication pending on codex/fresh-star-audit-20260917.',unavailable_reason='New local artifact, not yet published.'))
    hashes={a['id']:a['sha256'] for a in ledger['artifacts']}
    now=datetime.now(timezone.utc).isoformat()
    ledger['claims'].append(dict(id=binding['id'],revision=1,statement=binding['statement'],kind='mathematical result',
        basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description='Exact local choice partition for the named fixed overlap assignment and its original84 star domains. A rejected choice cannot occur in a target completion; the surviving set is only a necessary local relaxation.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Fixed baseline18481 overlap assignment, all unlisted overlapping-support and same-fiber edges absent; unknown edges only on disjoint support pairs.',
            'For each chosen complete14-neighbor set, forced internal edges stay present and each added internal edge must individually respect all partial common-neighbor caps.',
            'In a target completion lambda=1 forces each completed neighborhood to be a matching; no nontrivial automorphism assumption.'],
        dependencies=[],evidence=list(entries),
        verification=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check',
            command_or_audit=report_path+' and acceleration/results/20260917_independent_review/TRIANGLE_MATCHING_AUDIT.md',
            timestamp=review['timestamp'],outcome='PASS',scope=binding['scope'],artifact_hashes={id:hashes[id] for id in entries},
            shared_components=['Python standard library','Raw candidate and original domain artifacts; no producer/project module imports'],
            controls=['Positive matching and graph fixtures plus four corrupted raw records','All325963 prospective-edge tests checked by explicit adjacency mutation','All73814586 fixed-size edge subsets enumerated, rather than producer recurrence'],
            limitations=['Individually admissible matching edges may conflict when combined.','No empty vertex domain, no new fixed-K exclusion, no unrestricted coverage.'])],
        limitations=['The incumbent K was already excluded by another exact certificate.','No optimization objective is compared across changed feasible domains.','The separate pair-AC overlap comparison is not promoted by this claim.'],
        created_at=now,updated_at=now,unknowns={'external_source':'New current-project claim, not imported from historical ledger.'},
        external_source=None,reproducibility={'manifest':'triangle-manifest'}))
    ledger['updated_at']=now
    (ROOT/'CLAIMS.yaml').write_text(yaml.safe_dump(ledger,sort_keys=False,width=110),encoding='utf-8')


if __name__=='__main__':main()
