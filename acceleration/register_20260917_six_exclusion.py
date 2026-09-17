"""Register the independently checked six-coordinate conditional exclusion."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry


def main():
    base='acceleration/results/20260917_'
    binding_path=base+'independent_review/six_exclusion_claim_binding.json'
    audit_path=base+'independent_review/six_gpu_support.json'
    assert shared.digest(binding_path)=='3221d8c86c6bee1aadf801316541de992ba96650c777466bc32cd1fff010c7f0'
    assert shared.digest(audit_path)=='0814b6d5e660b876247cf83dc4e37cfaa0e86ec1d1b05b59ab8b6fd63ebbcf80'
    binding=shared.load(binding_path);audit=shared.load(audit_path)
    for report in (binding,audit):
        for p,h in report['inputs_sha256'].items():assert shared.digest(p)==h,p
    assert binding['recommendation']=='VERIFIED' and binding['artifact_review_outcome']=='PASS'
    assert binding['exact_positive_bound']==dict(numerator=906048,denominator=1048576,reduced='14157/16384')
    evidence={'six-exclusion-binding':binding_path,'six-exclusion-bound-audit':audit_path,
        'six-exclusion-manifest':base+'six_moment_pdhg/run01/manifest.json',
        'six-exclusion-certificate':base+'six_moment_pdhg/run01/certificates/10000_last.json',
        'six-exclusion-chunks':base+'six_moment_pdhg/run01/chunk_manifest.json'}
    artifacts=[dict(id=i,path=p,sha256=shared.digest(p),availability='LOCAL_ONLY',
        retrieval='Workspace relative path; exact raw inputs and chunk recovery manifest retained.',
        unavailable_reason='Not yet assigned a confirmed public commit.') for i,p in evidence.items()]
    now=datetime.now(timezone.utc).isoformat();scope=audit['scope']
    claim=dict(id=binding['claim_id'],revision=1,statement=binding['statement'],kind='exclusion',basis=['DERIVED','COMPUTED'],
        status='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Only the pinned 189-edge root scaffold, 132 fixed K edges and prescribed absences.','No nontrivial automorphism or solver convergence assumption.'],
        dependencies=binding['dependencies'],evidence=list(evidence),verification=[dict(claim_revision=1,
            verifier='independent_verifier agent',method='independent_artifact_check',command_or_audit=binding_path,
            timestamp=binding['timestamp'],outcome='PASS',scope=scope,artifact_hashes={a['id']:a['sha256'] for a in artifacts},
            shared_components=audit['shared_components'],controls=['Independent raw-neighborhood integer sums for every retained star and 84 maxima; rook positive and corrupted controls detailed in audit.'],
            limitations=binding['limitations'])],limitations=binding['limitations'],created_at=now,updated_at=now,
        external_source=None,unknowns={'external_source':'Current-project independent review; no external peer review claimed.'},
        reproducibility=dict(manifest='six-exclusion-manifest'))
    lp=shared.ROOT/'CLAIMS.yaml';old=lp.read_bytes();ledger=registry.read_ledger(lp)
    resume=shared.ROOT/(base+'resume');snapshot=resume/'claims_before_six_exclusion.yaml';receipt=resume/'six_exclusion_registration.json'
    assert not snapshot.exists() and not receipt.exists()
    merged=shared.merge(ledger,artifacts,[claim],now)
    validation=registry.validate(merged,shared.ROOT,shared.load('docs/claims.schema.json'),'available',ledger)
    assert validation['valid'],validation['errors']
    assert lp.read_bytes()==old
    with snapshot.open('xb') as f:f.write(old)
    lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf-8')
    shared.save(receipt,dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),registrar_sha256=shared.digest(__file__),
        previous_ledger_sha256=shared.sha256(old).hexdigest(),ledger_sha256=shared.digest(lp),registered_claims=[claim['id']],
        validation=validation,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN'))
    print(json.dumps(dict(claim=claim['id'],revision=1,status='VERIFIED',scope=scope,ledger_sha256=shared.digest(lp))))


if __name__=='__main__':main()
