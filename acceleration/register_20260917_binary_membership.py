"""Record exact modular membership, without a rank or feasibility claim."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry


def main():
    prefix='acceleration/results/20260917_independent_review/'
    bp=prefix+'two_coordinate_binary_span_claim_binding.json';ap=prefix+'two_coordinate_binary_span.json'
    assert shared.digest(bp)=='ba7a5c4cb3e1fdbf5444718eb7756af9f684d2e4e689b1b98a87962a192f3cdf'
    assert shared.digest(ap)=='e503c548a9ba75799b7e94fe25bc6c5ab839fdd78c416676525daab5587b8a04'
    b,a=shared.load(bp),shared.load(ap)
    assert b['recommendation']=='VERIFIED' and a['all_witness_entries_checked'] and not a['full_rank_claimed']
    for r in (a,b):
        for p,h in r['inputs_sha256'].items():assert shared.digest(p)==h
    root=shared.ROOT;lp=root/'CLAIMS.yaml';old=lp.read_bytes();ledger=registry.read_ledger(lp)
    resume=root/'acceleration/results/20260917_resume';snapshot=resume/'claims_before_binary_membership.yaml';receipt=resume/'binary_membership_registration.json'
    assert not snapshot.exists() and not receipt.exists()
    folder='acceleration/results/20260917_two_coordinate_binary_span/'
    evidence={'binary-membership-binding':bp,'binary-membership-audit':ap,'binary-membership-manifest':folder+'manifest.json','binary-membership-witness':folder+'certificate.json'}
    aa=[dict(id=i,path=p,sha256=shared.digest(p),availability='LOCAL_ONLY',retrieval='Workspace relative path; complete XOR witness retained.',unavailable_reason='Not assigned a confirmed public commit yet.') for i,p in evidence.items()]
    now=datetime.now(timezone.utc).isoformat()
    claim=dict(id=b['claim_id'],revision=1,statement=b['statement'],kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description='Binary affine relaxation of the exact5370-row two-coordinate moment model; 1837 witness differences and84reference columns only. No full population rank assertion.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Frozen156-fixed-K two-coordinate domain/model, reduction of its probability columns and equality RHS modulo2.'],
        dependencies=b['dependencies'],evidence=list(evidence),verification=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check',command_or_audit=bp,timestamp=b['timestamp'],outcome='PASS',scope=b['statement'],
            artifact_hashes={x['id']:x['sha256'] for x in aa},shared_components=a['shared_components'],controls=[str(a['controls'])],limitations=b['limitations'])],
        limitations=b['limitations'],created_at=now,updated_at=now,external_source=None,
        unknowns={'external_source':'Current-project modular diagnostic; no external peer review.'},reproducibility=dict(manifest='binary-membership-manifest'))
    merged=shared.merge(ledger,aa,[claim],now);v=registry.validate(merged,root,shared.load('docs/claims.schema.json'),'available',ledger);assert v['valid'],v['errors']
    assert lp.read_bytes()==old;snapshot.write_bytes(old);lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf-8')
    shared.save(receipt,dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),registrar_sha256=shared.digest(__file__),previous_ledger_sha256=shared.sha256(old).hexdigest(),ledger_sha256=shared.digest(lp),validation=v,claim_id=claim['id'],registrar_performs_mathematical_verification=False))
    print(json.dumps(dict(claim=claim['id'],ledger_sha256=shared.digest(lp))))


if __name__=='__main__':main()
