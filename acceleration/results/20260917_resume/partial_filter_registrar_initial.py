"""Register the independently checked partial-domain matching partition."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry

AUDIT='acceleration/results/20260917_independent_review/partial_matching_filter/summary.json'
AUDIT_SHA='5559bd5aa51a8e72047a31a4e6050bf337d81860f6c6540d89ca27bb7c9676cf'


def main():
    root=shared.ROOT
    assert shared.digest(AUDIT)==AUDIT_SHA
    review=shared.load(AUDIT)
    assert review['status']=='INDEPENDENT_PARTIAL_K_NEIGHBORHOOD_MATCHING_FILTER_PASS'
    assert review['producer_imported'] is False and review['empty_domains']==0
    assert review['counts']['original_count']==54478 and review['counts']['rejected_count']==13105
    assert review['counts']['surviving_count']==41373
    for p,h in review['inputs_sha256'].items():assert shared.digest(p)==h,p
    lp=root/'CLAIMS.yaml';old=lp.read_bytes();ledger=registry.read_ledger(lp)
    resume=root/'acceleration/results/20260917_resume'
    snapshot=resume/'claims_before_partial_matching_filter.yaml'
    receipt=resume/'partial_matching_filter_registration.json'
    assert not snapshot.exists() and not receipt.exists()
    now=datetime.now(timezone.utc).isoformat()
    folder='acceleration/results/20260917_partial_matching_filter/'
    evidence={'partial-filter-audit':AUDIT,'partial-filter-manifest':folder+'manifest.json',
        'partial-filter-summary':folder+'summary.json',
        'partial-filter-independent-source':'acceleration/audit_20260917_partial_matching_filter.py'}
    artifacts=[dict(id=i,path=p,sha256=shared.digest(p),availability='LOCAL_ONLY',
        retrieval='Workspace relative path; per-center raw records are hash-indexed in the summary and independent audit.',
        unavailable_reason='Not yet assigned a confirmed public commit.') for i,p in evidence.items()]
    claim=dict(id=review['claim_id'],revision=1,
        statement='For the 54,478 original center/domain-ID choices in the exact one-coordinate partial-K family, the necessary neighborhood perfect-matching test rejects exactly 13,105 and retains exactly 41,373. All 84 domains remain nonempty. Each rejected choice has no perfect matching among individually cap-permissible remaining neighborhood edges; every retained choice has a checked matching witness. Positive matching multiplicities are not claimed.',
        kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description=review['scope'],unrestricted_target=False,target_resolution='NONE'),
        assumptions=['The specified 162 fixed K edges and all prescribed absent edges of the frozen partial-coordinate family.',
            'Any target completion has a seven-edge matching in every 14-vertex neighborhood, since lambda=1. No automorphism assumption.'],
        dependencies=[dict(claim_id='C-PARTIAL-K-ONE-COORDINATE-DOMAINS',revision=1,relation='coverage')],
        evidence=list(evidence),verification=[dict(claim_revision=1,verifier='independent_verifier agent',
            method='independent_artifact_check',command_or_audit=AUDIT,timestamp=review['completed_at'],outcome='PASS',
            scope=review['scope'],artifact_hashes={a['id']:a['sha256'] for a in artifacts},
            shared_components=review['shared_components'],controls=[
                'Five edge-processing DP fixtures; independent prior graph-mutation and deliberate corrupted windmill controls.',
                'All 701,455 prospective neighborhood edges checked; all retained witnesses and every rejected star checked through a separate path.'],
            limitations=review['limitations'])],limitations=review['limitations'],created_at=now,updated_at=now,
        unknowns={'external_source':'Current-project result, not a historical import.'},external_source=None,
        reproducibility=dict(manifest='partial-filter-manifest'))
    merged=shared.merge(ledger,artifacts,[claim],now)
    validation=registry.validate(merged,root,shared.load('docs/claims.schema.json'),'available',ledger)
    assert validation['valid'],validation['errors']
    assert lp.read_bytes()==old
    snapshot.write_bytes(old)
    lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf-8')
    shared.save(receipt,dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
        source_sha256=shared.digest(__file__),independent_audit_sha256=AUDIT_SHA,
        previous_ledger_sha256=shared.sha256(old).hexdigest(),ledger_sha256=shared.digest(lp),validation=validation,
        status='INDEPENDENT_PARTIAL_MATCHING_FILTER_REGISTERED',registrar_performs_mathematical_verification=False))
    print(json.dumps(dict(claim=claim['id'],ledger_sha256=shared.digest(lp))))


if __name__=='__main__':main()
