"""Bind a conditional family exclusion to separate exact verification."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry

AUDIT='acceleration/results/20260917_independent_review/moment_positive600.json'
BINDING='acceleration/results/20260917_independent_review/moment_positive600_claim_binding.json'


def main():
    assert shared.digest(AUDIT)=='d435c7789bd2f181e3a870b2019ae309cdbf2d9530bc21b2d987d40671444bc8'
    assert shared.digest(BINDING)=='4a46735b46fe9465f836b978359b09f2f822815809543854e0c2725fe71ed21c'
    audit,binding=shared.load(AUDIT),shared.load(BINDING)
    assert audit['status']=='INDEPENDENT_PARTIAL_K_POSITIVE_MOMENT_EXCLUSION_PASS'
    assert binding['status']=='INDEPENDENT_PARTIAL_K_POSITIVE_MOMENT_CLAIM_BINDING_PASS'
    assert binding['recommendation']=='VERIFIED' and audit['producer_imported'] is False
    assert audit['checked_original_choices']==54478 and audit['checked_centers']==84
    assert audit['exact_bound']['numerator']==590533056 and audit['exact_bound']['denominator']==1048576
    for report in (audit,binding):
        for p,h in report['inputs_sha256'].items():assert shared.digest(p)==h,p
    root=shared.ROOT;lp=root/'CLAIMS.yaml';old=lp.read_bytes();ledger=registry.read_ledger(lp)
    resume=root/'acceleration/results/20260917_resume'
    snapshot=resume/'claims_before_partial_coordinate_exclusion.yaml'
    receipt=resume/'partial_coordinate_exclusion_registration.json'
    assert not snapshot.exists() and not receipt.exists()
    folder='acceleration/results/20260917_partial_matching_moment_replay600/'
    evidence={'partial-exclusion-audit':AUDIT,'partial-exclusion-binding':BINDING,
        'partial-exclusion-manifest':folder+'manifest.json','partial-exclusion-certificate':folder+'exact_support_bound.json',
        'partial-exclusion-derivation':folder+'CANDIDATE_EXCLUSION.md',
        'partial-exclusion-independent-source':'acceleration/audit_20260917_moment_positive600.py'}
    artifacts=[dict(id=i,path=p,sha256=shared.digest(p),availability='LOCAL_ONLY',
        retrieval='Workspace relative path; prerequisite complete domains and moment model are recorded in pinned claim dependencies.',
        unavailable_reason='Awaiting confirmed publication of this new exact certificate.') for i,p in evidence.items()]
    now=datetime.now(timezone.utc).isoformat()
    claim=dict(id=binding['claim_id'],revision=1,statement=binding['statement'],kind='exclusion',
        basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description='Only the labeled partial-coordinate family specified by manifest dcc0118cc35993743e94bf7b548e6870526e33f3d4fe4015a48cdacb0c1fc05c: 162 fixed outer K edges, 60 freed matching-coordinate and 1680 disjoint-support unknown edges, and all prescribed absences.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['The fixed root scaffold, 162 K edges and prescribed absent edges in the named scope manifest.',
            'No nontrivial graph automorphism is assumed. No numerical solver declaration is a premise.'],
        dependencies=binding['dependencies'],evidence=list(evidence),
        verification=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check',
            command_or_audit=BINDING,timestamp=binding['timestamp'],outcome='PASS',scope=binding['statement'],
            artifact_hashes={a['id']:a['sha256'] for a in artifacts},shared_components=audit['shared_components'],
            controls=['All 54478 original neighborhood columns and all 84 maxima independently reconstructed using Python integers.',
                'Nine valid rooted rook9 cases with separate RHS and column corruptions; altered bound and out-of-box weight rejected; zero weights give zero.'],
            limitations=audit['limitations'])],limitations=audit['limitations'],created_at=now,updated_at=now,
        external_source=None,unknowns={'external_source':'Current-project conditional exclusion; no external peer review claimed.'},
        reproducibility=dict(manifest='partial-exclusion-manifest'))
    merged=shared.merge(ledger,artifacts,[claim],now)
    validation=registry.validate(merged,root,shared.load('docs/claims.schema.json'),'available',ledger)
    assert validation['valid'],validation['errors']
    assert lp.read_bytes()==old
    snapshot.write_bytes(old);lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf-8')
    shared.save(receipt,dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
        registrar_sha256=shared.digest(__file__),before_ledger_sha256=shared.sha256(old).hexdigest(),ledger_sha256=shared.digest(lp),
        status='INDEPENDENT_PARTIAL_COORDINATE_EXCLUSION_REGISTERED',claim_id=claim['id'],claim_revision=1,
        exact_bound='9227079/16384',validation=validation,registrar_performs_mathematical_verification=False,
        target_resolution='UNKNOWN'))
    print(json.dumps(dict(claim=claim['id'],exact_bound='9227079/16384',ledger_sha256=shared.digest(lp))))


if __name__=='__main__':main()
