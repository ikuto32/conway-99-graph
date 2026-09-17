"""Integrate the independent matching/pair propagation and comparison review."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]


def main():
    ledger=yaml.safe_load((ROOT/'CLAIMS.yaml').read_text(encoding='utf-8'))
    path='acceleration/results/20260917_independent_review/matching_pair.json'
    review=json.loads((ROOT/path).read_bytes())
    assert review['status']=='INDEPENDENT_MATCHING_FILTERED_PAIR_PROPAGATION_AND_COMPARISON_PASS'
    for p,h in review['inputs_sha256'].items():
        assert sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    evidence={
        'matching-pair-independent':path,
        'matching-pair-proof':'acceleration/results/20260917_independent_review/MATCHING_PAIR_AUDIT.md',
        'matching-pair-manifest':'acceleration/results/20260917_theory/matching_pair_baseline18481/manifest.json',
        'matching-pair-native':'acceleration/results/20260917_theory/matching_pair_baseline18481/native.json',
        'matching-pair-original-ids':'acceleration/results/20260917_theory/matching_pair_baseline18481/translated_pairs.json'}
    for id,p in evidence.items():
        ledger['artifacts'].append(dict(id=id,path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest(),availability='LOCAL_ONLY',
            retrieval='Workspace relative path; awaiting the next artifact publication commit on draft PR1.',unavailable_reason='New local artifact, not yet published.'))
    hashes={a['id']:a['sha256'] for a in ledger['artifacts']}
    now=datetime.now(timezone.utc).isoformat()
    for binding in review['claim_bindings']:
        assert all(c['id']!=binding['id'] for c in ledger['claims'])
        ledger['claims'].append(dict(id=binding['id'],revision=binding['revision'],statement=binding['statement'],
            kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=binding['scope'],unrestricted_target=False,target_resolution='NONE'),
            assumptions=['The same fixed baseline18481 present/absent overlap edges and disjoint-edge universe as in the matching-filter claim.',
                'A global completion must select a surviving matching-admissible local star at every vertex; pair relations enforce reciprocity and exact common-neighbor counts.',
                'No nontrivial automorphism is assumed.'],
            dependencies=[dict(id='C-STAR-TRIANGLE-FILTER-18481',revision=1,relation='uses_result')],
            evidence=list(evidence),verification=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check',
                command_or_audit=path+' and acceleration/results/20260917_independent_review/MATCHING_PAIR_AUDIT.md',
                timestamp=review['timestamp'],outcome='PASS',scope=binding['scope'],artifact_hashes={id:hashes[id] for id in evidence},
                shared_components=review['shared_trusted_components'],controls=['Calibrated positive and corrupted raw propagation/translation controls',
                    'All806 pair-deletion events and all84*83 directed final arcs checked independently','Exact original-ID mapping and compact isolated-vertex witness checked'],
                limitations=['No matching enumeration rerun; its already independently checked, immutable partition is reused.','Nonempty arc consistency is not a simultaneous graph witness.'])],
            limitations=['No new fixed-K exclusion or unrestricted target result.','The named local-choice populations overlap and must not be added as coverage.'],
            created_at=now,updated_at=now,unknowns={'external_source':'New current-project claim, not a historical import.'},external_source=None,
            reproducibility={'manifest':'matching-pair-manifest'}))
    ledger['updated_at']=now
    (ROOT/'CLAIMS.yaml').write_text(yaml.safe_dump(ledger,sort_keys=False,width=110),encoding='utf-8')


if __name__=='__main__':main()
