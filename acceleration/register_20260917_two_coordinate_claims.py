"""Register three two-coordinate claims from independent domain/model/proof audits."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry

REV='acceleration/results/20260917_independent_review/'
PINS={REV+'two_matchings/summary.json':'f3d2ba90be5e8c27bc64c2e4941174d36fc3ddfcbc29ce25da872df652383acb',
    REV+'two_matching_moments.json':'5af1f353a70a16fc5f915195b911d782e360ffc0690463936b7a9dea983197ed',
    REV+'two_matching_solve_bound.json':'adf254892686dab05f0317b9ecec963b1b98eee8f9f8ccee129b05ebf6145065',
    REV+'two_matching_exclusion_claim_binding.json':'ed7d79951b796371776cec874f64816aba9e316324e07398da70b920b9a00ffd'}


def main():
    reports=[]
    for p,h in PINS.items():
        assert shared.digest(p)==h
        r=shared.load(p)
        for q,k in r['inputs_sha256'].items():assert shared.digest(q)==k,q
        reports.append(r)
    domains,model,raw,binding=reports
    assert domains['domain_choices']==89308 and domains['old_embedded_choices']==54478 and domains['fixed_K_edges']==156
    assert model['shape']==[5370,96280] and model['nonzeros']==7315157 and model['complete_augmented_matrix_and_bounds_checked']
    assert binding['recommendation']=='VERIFIED' and binding['artifact_review_outcome']=='PASS'
    root=shared.ROOT;lp=root/'CLAIMS.yaml';old=lp.read_bytes();ledger=registry.read_ledger(lp)
    resume=root/'acceleration/results/20260917_resume';snapshot=resume/'claims_before_two_coordinate_results.yaml'
    receipt=resume/'two_coordinate_registration.json';assert not snapshot.exists() and not receipt.exists()
    now=datetime.now(timezone.utc).isoformat();artifacts=[];claims=[]
    dd='acceleration/results/20260917_partial_two_matchings/'
    mm='acceleration/results/20260917_two_matching_moments/'
    specs=[(domains,'encoding',[],{'two-domains-audit':REV+'two_matchings/summary.json','two-domains-manifest':dd+'manifest.json','two-domains-summary':dd+'summary.json'},'two-domains-manifest'),
        (model,'encoding',[model['dependency']],{'two-moment-model-audit':REV+'two_matching_moments.json','two-moment-build-manifest':mm+'build_manifest.json','two-moment-model':mm+'model.json','two-moment-matrix':mm+'integer_augmented_csr.npz','two-moment-derivation':mm+'TWO_COORDINATE_MOMENT_MODEL.md'},'two-moment-build-manifest'),
        (binding,'exclusion',binding['dependencies'],{'two-exclusion-binding':REV+'two_matching_exclusion_claim_binding.json','two-exclusion-raw-audit':REV+'two_matching_solve_bound.json','two-exclusion-manifest':mm+'solve_manifest.json','two-exclusion-certificate':mm+'exact_support_bound.json','two-exclusion-derivation':mm+'CANDIDATE_TWO_COORDINATE_EXCLUSION.md'},'two-exclusion-manifest')]
    for review,kind,deps,evidence,manifest in specs:
        assert review['recommendation']=='VERIFIED' and review['claim_revision']==1
        aa=[dict(id=i,path=p,sha256=shared.digest(p),availability='LOCAL_ONLY',retrieval='Workspace relative path; complete source/domains/matrix and independent reviews retained.',unavailable_reason='Not yet assigned a confirmed public commit.') for i,p in evidence.items()]
        artifacts.extend(aa)
        scientific=raw if kind=='exclusion' else review
        scope=review.get('scope',domains['scope'])
        limitations=review.get('limitations',[])+([] if kind!='exclusion' else ['Exclusion only for156fixedK edges and recorded prescribed absent edges; not unrestricted Conway-99.'])
        claims.append(dict(id=review['claim_id'],revision=1,statement=review['statement'],kind=kind,basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
            assumptions=['Exact two-sign-coordinate partial family and original domain IDs; all other prescribed absences retained.','No nontrivial automorphism assumption. Floating-point solver declarations are not proof premises.'],
            dependencies=deps,evidence=list(evidence),verification=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check',
                command_or_audit=next(iter(evidence.values())),timestamp=review.get('timestamp',review.get('completed_at')),outcome='PASS',scope=scope,
                artifact_hashes={a['id']:a['sha256'] for a in aa},shared_components=scientific.get('shared_components',['Python standard library','prior independent raw-neighborhood helper']),
                controls=['Exact complete domain/model or raw-bound checking as specified in the bound independent audit.','Positive and deliberately corrupted controls are recorded in the referenced audit.'],limitations=limitations)],
            limitations=limitations,created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Current-project independent result, not historical import or external peer review.'},reproducibility=dict(manifest=manifest)))
    merged=shared.merge(ledger,artifacts,claims,now)
    v=registry.validate(merged,root,shared.load('docs/claims.schema.json'),'available',ledger);assert v['valid'],v['errors']
    assert lp.read_bytes()==old;snapshot.write_bytes(old);lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf-8')
    shared.save(receipt,dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),registrar_sha256=shared.digest(__file__),
        previous_ledger_sha256=shared.sha256(old).hexdigest(),ledger_sha256=shared.digest(lp),validation=v,
        registered_claims=[c['id'] for c in claims],registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN'))
    print(json.dumps(dict(claims=[c['id'] for c in claims],ledger_sha256=shared.digest(lp))))


if __name__=='__main__':main()
