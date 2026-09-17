"""Record the independently checked finite coordinate-assignment population."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry


def main():
    audit_path='acceleration/results/20260917_independent_review/coordinate_universe.json'
    assert shared.digest(audit_path)=='d7284d73e75f3fe49160c1a2f8ba97eb0263424e727661db25ac1cf631ba8c57'
    audit=shared.load(audit_path)
    assert audit['status']=='INDEPENDENT_PARTIAL_COORDINATE_MATCHING_UNIVERSE_PASS'
    assert audit['matching_count']==6040 and audit['accepted_partial_cap_assignments']==6040
    for p,h in audit['inputs_sha256'].items():assert shared.digest(p)==h
    root=shared.ROOT;lp=root/'CLAIMS.yaml';old=lp.read_bytes();ledger=registry.read_ledger(lp)
    resume=root/'acceleration/results/20260917_resume';snapshot=resume/'claims_before_coordinate_universe.yaml'
    receipt=resume/'coordinate_universe_registration.json';assert not snapshot.exists() and not receipt.exists()
    folder='acceleration/results/20260917_partial_coordinate_matchings/'
    evidence={'coordinate-universe-audit':audit_path,'coordinate-universe-manifest':folder+'manifest.json',
        'coordinate-universe-list':folder+'matchings.json','coordinate-universe-outcomes':folder+'outcomes.json',
        'coordinate-universe-independent-source':'acceleration/audit_20260917_coordinate_universe.py'}
    artifacts=[dict(id=i,path=p,sha256=shared.digest(p),availability='LOCAL_ONLY',
        retrieval='Workspace relative path; all6040 labeled assignments explicitly retained.',
        unavailable_reason='No confirmed public commit yet.') for i,p in evidence.items()]
    now=datetime.now(timezone.utc).isoformat()
    claim=dict(id=audit['claim_id'],revision=1,statement=audit['statement'],kind='mathematical result',
        basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description=audit['mathematical_scope'],unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Only the frozen coordinate vertices, allowed edges and partial scaffold are considered.',
            'Partial upper caps have their declared degree/common-neighbor meaning; no completion is asserted.'],
        dependencies=[],evidence=list(evidence),verification=[dict(claim_revision=1,
            verifier='root agent using separate count derivation and dense matrix checker; producer was structural_continuation agent',
            method='independent_artifact_check',command_or_audit=audit_path,timestamp=audit['timestamp'],outcome='PASS',
            scope=audit['mathematical_scope'],artifact_hashes={a['id']:a['sha256'] for a in artifacts},
            shared_components=audit['shared_components'],controls=[str(x) for x in audit['controls']],limitations=audit['limitations'])],
        limitations=audit['limitations'],created_at=now,updated_at=now,external_source=None,
        unknowns={'external_source':'Current-project finite count, not historical import or literature claim.'},
        reproducibility=dict(manifest='coordinate-universe-manifest'))
    merged=shared.merge(ledger,artifacts,[claim],now)
    validation=registry.validate(merged,root,shared.load('docs/claims.schema.json'),'available',ledger)
    assert validation['valid'],validation['errors'];assert lp.read_bytes()==old
    snapshot.write_bytes(old);lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf-8')
    shared.save(receipt,dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
        registrar_sha256=shared.digest(__file__),previous_ledger_sha256=shared.sha256(old).hexdigest(),ledger_sha256=shared.digest(lp),
        validation=validation,status='INDEPENDENT_COORDINATE_UNIVERSE_REGISTERED',claim_id=claim['id'],
        target_resolution='UNKNOWN',registrar_performs_mathematical_verification=False))
    print(json.dumps(dict(claim=claim['id'],ledger_sha256=shared.digest(lp))))


if __name__=='__main__':main()
