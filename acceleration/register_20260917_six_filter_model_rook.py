"""Register independently checked six-coordinate prerequisites and fresh rook reduction."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry

BASE='acceleration/results/20260917_'
REV=BASE+'independent_review/'


def read_checked(path,pin):
    assert shared.digest(path)==pin
    r=shared.load(path)
    for p,h in r['inputs_sha256'].items():assert shared.digest(p)==h,p
    return r


def main():
    fa=REV+'six_coordinate_matching_filter/summary.json';ma=REV+'six_filtered_moments.json';ra=REV+'rook_regular_set_recheck.json'
    f=read_checked(fa,'05d4284f04fb5c84491394695c6f56a3e5517302ae95c1885b27592cfed78a7f')
    m=read_checked(ma,'f27467b03a34fe3ea3adec4e537585e71d5697f4e63562cdd43d7e6822c8f3e7')
    r=read_checked(ra,'203f8f314cb4d1b6452eec04955c71a05d48bf76088abd0145c0d07f15b5c6f3')
    assert f['counts']['original_count']==879449 and f['counts']['surviving_count']==712721 and f['empty_domains']==0
    assert m['shape']==[5610,719693] and m['nonzeros']==59380799 and m['all_raw_neighborhood_columns_checked']
    assert r['does_not_depend_on_missing_previous_auditor'] and r['fresh_review_after_source_collision']
    specs=[dict(id=f['claim_id'],review=f,scope=f['scope'],kind='exclusion',statement='For all 879,449 original center/domain-ID choices in the frozen six-coordinate partial-K family, the necessary neighborhood perfect-matching test rejects exactly 166,728 and retains exactly 712,721, leaving all 84 domains nonempty. Every rejection was independently checked and every survivor has a checked matching witness; positive matching multiplicities are not claimed.',deps=[dict(id='C-PARTIAL-K-SIX-COORDINATE-DOMAINS',revision=1,relation='coverage')],
        evidence={'six-filter-audit':fa,'six-filter-manifest':BASE+'six_coordinate_matching_filter/run01/manifest.json','six-filter-summary':BASE+'six_coordinate_matching_filter/run01/summary.json','six-filter-recovery-manifest':BASE+'six_coordinate_matching_filter/run01/compressed_artifacts.json'},manifest='six-filter-manifest',limitations=f['limitations']),
        dict(id=m['claim_id'],review=m,scope=m['scope'],kind='encoding',statement=m['statement'],deps=m['dependencies'],
        evidence={'six-filtered-model-audit':ma,'six-filtered-model-manifest':BASE+'six_filtered_moments/build_manifest.json','six-filtered-model-chunks':BASE+'six_filtered_moments/chunk_manifest.json'},manifest='six-filtered-model-manifest',limitations=m['limitations']),
        dict(id='C-ROOK-NINE-REGULAR-SET-ENCODING',review=r,scope='Exact conditional representation of a target containing an induced nine-vertex rook graph; no assumption that every target contains one.',kind='encoding',statement=r['statement'],deps=[],
        evidence={'rook-encoding-recheck':ra,'rook-encoding-manifest':BASE+'rook_regular_set/manifest.json','rook-encoding-matrices':BASE+'rook_regular_set/exact_matrices.json','rook-encoding-derivation':'docs/THEORY_20260917_ROOK_REGULAR_SET.md','rook-source-impact':BASE+'resume/rook_source_collision_impact.json','rook-original-source-unavailable':BASE+'resume/rook_original_source_unavailable.json'},manifest='rook-encoding-manifest',
        limitations=['Conditional on an induced rook9; no universal containment, target construction or exclusion is established.','The compatible quotient spectrum is not a contradiction; no novelty or external peer review claimed.','Historical checker source pinned by rook_regular_set.json was overwritten and is unavailable. Current verification uses the fresh uniquely named checker and does not depend on that historical source.','Finite calibration fixtures do not prove the universal statement; the independent written derivation does.'])]
    lp=shared.ROOT/'CLAIMS.yaml';old=lp.read_bytes();ledger=registry.read_ledger(lp)
    resume=shared.ROOT/(BASE+'resume');snapshot=resume/'claims_before_six_filter_model_rook.yaml';receipt=resume/'six_filter_model_rook_registration.json'
    assert not snapshot.exists() and not receipt.exists()
    now=datetime.now(timezone.utc).isoformat();aa=[];cc=[]
    for s in specs:
        review=s['review'];evidence=s['evidence'];scope=s['scope'];limitations=s['limitations']
        artifacts=[dict(id=i,path=p,sha256=shared.digest(p),availability='LOCAL_ONLY',retrieval='Workspace relative path; exact inputs and recovery manifests retained.',unavailable_reason='Not yet assigned a confirmed public commit.') for i,p in evidence.items()];aa.extend(artifacts)
        assumptions=['Only the exact scope and declared fixed data in the referenced derivation and manifest.','No nontrivial automorphism assumption.']
        if review is r:assumptions.append('Induced rook9 containment is a premise of the representation, not a universal target theorem.')
        cc.append(dict(id=s['id'],revision=1,statement=s['statement'],kind=s['kind'],basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),assumptions=assumptions,dependencies=s['deps'],evidence=list(evidence),
            verification=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check' if review is not r else 'independent_derivation',command_or_audit=next(iter(evidence.values())),timestamp=review.get('timestamp',review.get('completed_at')),outcome='PASS',scope=scope,artifact_hashes={a['id']:a['sha256'] for a in artifacts},shared_components=review['shared_components'],controls=['Exact positive and corrupted controls and independent full-scope checking are detailed in the referenced audit.'],limitations=limitations)],
            limitations=limitations,created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Current-project independent review; literature and historical labels are not promoted.'},reproducibility=dict(manifest=s['manifest'])) )
    merged=shared.merge(ledger,aa,cc,now);validation=registry.validate(merged,shared.ROOT,shared.load('docs/claims.schema.json'),'available',ledger);assert validation['valid'],validation['errors']
    assert lp.read_bytes()==old;snapshot.write_bytes(old);lp.write_text(yaml.safe_dump(merged,sort_keys=False,width=110),encoding='utf-8')
    shared.save(receipt,dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),source_sha256=shared.digest(__file__),previous_ledger_sha256=shared.sha256(old).hexdigest(),ledger_sha256=shared.digest(lp),registered_claims=[c['id'] for c in cc],validation=validation,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN'))
    print(json.dumps(dict(claims=[c['id'] for c in cc],ledger_sha256=shared.digest(lp))))


if __name__=='__main__':main()
