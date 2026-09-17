"""Register fresh independent exclusion, wider domains, and failed weight transfer."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry

BASE='acceleration/results/20260917_'
REV=BASE+'independent_review/'


def reviewed(path, pin):
    assert shared.digest(path)==pin
    r=shared.load(path)
    for p,h in r['inputs_sha256'].items():assert shared.digest(p)==h,p
    return r


def main():
    da=REV+'six_matchings/summary.json'
    domains=reviewed(da,'051a57b2fc1b5353a6100b949f86674483cff686c4f797f4f1ad8b037d7f3768')
    ba=REV+'four_matching_exclusion_claim_binding.json'
    binding=reviewed(ba,'454921726c32220620c1548e29ce823dc2633ff40e186c9d5adfc0db5707500c')
    ra=REV+'four_matching_filtered_run01_bound.json'
    bound=reviewed(ra,'6d8bba20e6d71c5538ed46008ce2676f8c573740adc5512d86bea6b7c93c835a')
    ta=REV+'filtered_four_weight_transfer/summary.json'
    transfer=reviewed(ta,'a641c841f713e0c9831fbeb22a3f1cd6dfff773afc0920af12334340bb857e45')
    assert domains['domain_choices']==879449 and domains['old_embedded_choices']==290460
    assert binding['recommendation']=='VERIFIED' and binding['artifact_review_outcome']=='PASS'
    assert bound['conditional_family_exclusion'] and bound['filter_complement_identity_checked']
    assert transfer['weight_sets_checked']==10 and transfer['positive_bounds']==0 and transfer['nonpositive_bounds']==10
    lp=shared.ROOT/'CLAIMS.yaml';old=lp.read_bytes();ledger=registry.read_ledger(lp)
    resume=shared.ROOT/(BASE+'resume');snapshot=resume/'claims_before_four_exclusion_six_domains.yaml';receipt=resume/'four_exclusion_six_domains_registration.json'
    assert not snapshot.exists() and not receipt.exists()
    now=datetime.now(timezone.utc).isoformat();artifacts=[];claims=[]
    configs=[dict(id=domains['claim_id'],review=domains,scope=domains['scope'],statement=domains['statement'],kind='encoding',deps=[],
        evidence={'six-domains-audit':da,'six-domains-manifest':BASE+'partial_six_matchings/manifest.json','six-domains-summary':BASE+'partial_six_matchings/summary.json'},manifest='six-domains-manifest',limitations=domains['limitations']),
        dict(id=binding['claim_id'],review=binding,scope=bound['scope'],statement=binding['statement'],kind='exclusion',deps=binding['dependencies'],
        evidence={'four-exclusion-binding':ba,'four-exclusion-bound-audit':ra,'four-exclusion-manifest':BASE+'four_matching_filtered_solve2400/run01/manifest.json','four-exclusion-certificate':BASE+'four_matching_filtered_solve2400/run01/exact_support_bound.json','four-exclusion-derivation':BASE+'four_matching_filtered_solve2400/run01/CANDIDATE_FOUR_COORDINATE_EXCLUSION.md'},manifest='four-exclusion-manifest',limitations=binding['limitations']),
        dict(id='C-FOUR-COORDINATE-FIXED-WEIGHT-TRANSFER-SCREEN',review=transfer,scope=transfer['scope'],
        statement='All ten fixed transferred weight sets selected in the frozen filtered-four transfer manifest have nonpositive exact support bounds on its 230,879 surviving original local stars; none of these ten weights certifies exclusion. This establishes neither feasibility nor impossibility for the family.',
        kind='empirical/engineering result',deps=[dict(id='C-PARTIAL-K-FOUR-COORDINATE-MATCHING-FILTERED-MOMENT-ENCODING',revision=1,relation='uses_result')],
        evidence={'four-transfer-audit':ta,'four-transfer-manifest':BASE+'filtered_four_weight_transfer/manifest.json','four-transfer-summary':BASE+'filtered_four_weight_transfer/summary.json'},manifest='four-transfer-manifest',
        limitations=['Only these ten fixed weights; no optimality or exhaustive weight search.',transfer['timing_deviation'],transfer['disclosure']])]
    for spec in configs:
        r=spec['review'];evidence=spec['evidence'];scope=spec['scope'];limitations=spec['limitations']
        aa=[dict(id=i,path=p,sha256=shared.digest(p),availability='LOCAL_ONLY',retrieval='Workspace relative path; exact raw inputs and audit manifests retained, recovery companions separately indexed.',unavailable_reason='Not yet assigned a confirmed public commit.') for i,p in evidence.items()]
        artifacts.extend(aa)
        scientific=bound if spec['kind']=='exclusion' else r
        claims.append(dict(id=spec['id'],revision=1,statement=spec['statement'],kind=spec['kind'],basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
            assumptions=['Only the fixed scaffold, prescribed absences and unknown edge family in the hash-bound manifest.','No automorphism assumption; floating-point solver flags are not proof premises.'],
            dependencies=spec['deps'],evidence=list(evidence),verification=[dict(claim_revision=1,
                verifier='structural_continuation agent' if r is transfer else 'independent_verifier agent',method='independent_artifact_check',command_or_audit=next(iter(evidence.values())),
                timestamp=r.get('timestamp',r.get('completed_at')),outcome='PASS',scope=scope,artifact_hashes={a['id']:a['sha256'] for a in aa},
                shared_components=scientific['shared_components'],controls=['Complete independent checking and calibrated positive/corrupted controls are specified in the bound audit.'],limitations=limitations)],
            limitations=limitations,created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Current-project independent result; not external peer review.'},reproducibility=dict(manifest=spec['manifest'])) )
    merged=shared.merge(ledger,artifacts,claims,now)
    validation=registry.validate(merged,shared.ROOT,shared.load('docs/claims.schema.json'),'available',ledger)
    assert validation['valid'],validation['errors']
    assert lp.read_bytes()==old;snapshot.write_bytes(old);lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf-8')
    shared.save(receipt,dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),registrar_sha256=shared.digest(__file__),previous_ledger_sha256=shared.sha256(old).hexdigest(),ledger_sha256=shared.digest(lp),registered_claims=[c['id'] for c in claims],validation=validation,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN'))
    print(json.dumps(dict(claims=[c['id'] for c in claims],ledger_sha256=shared.digest(lp))))


if __name__=='__main__':main()
