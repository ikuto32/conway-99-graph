"""Register completed independent audits; registration is not verification."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml
import validate_claims as validator

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
def digest(p):
    x=Path(p);x=x if x.is_absolute() else ROOT/x
    h=sha256()
    with x.open('rb') as f:
        while block:=f.read(1<<20):h.update(block)
    return h.hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def dep(i,relation='uses_result'):return dict(id=i,revision=1,relation=relation)

def main():
    ledger=ROOT/'CLAIMS.yaml';before=ledger.read_bytes();old=validator.read_ledger(ledger);data=validator.read_ledger(ledger)
    specs=[
      ('eight-filter',B+'independent_review/eight_matching_filter_claim_binding.json','encoding',B+'eight_matching_filter/run01/manifest.json',None,
       dict(summary=B+'eight_matching_filter/run01/summary.json',fullaudit=B+'independent_review/eight_coordinate_matching_filter/summary.json',derivation=B+'independent_review/eight_coordinate_matching_filter/DERIVATION.md')),
      ('eight-moments',B+'independent_review/eight_filtered_moments/summary.json','encoding',B+'eight_filtered_moments/run01/build_manifest.json',None,
       dict(summary=B+'eight_filtered_moments/run01/build_summary.json',matrix=B+'eight_filtered_moments/run01/integer_augmented_csr.npz',model=B+'eight_filtered_moments/run01/model.json',chunks=B+'eight_filtered_moments/run01/chunk_manifest.json',derivation='docs/AUDIT_20260930_EIGHT_MOMENT_NECESSITY.md')),
      ('rook-free-cnf',B+'rook_free_internal_sat/independent_cnf_encoding.json','encoding',B+'rook_free_internal_sat/manifest.json',[dep('C-ROOK-NINE-REGULAR-SET-ENCODING')],
       dict(model=B+'rook_free_internal_sat/model.json',cnf=B+'rook_free_internal_sat/instance.cnf',gzip=B+'rook_free_internal_sat/instance.cnf.gz',summary=B+'rook_free_internal_sat/summary.json')),
      ('rook-local-sat',B+'rook_free_internal_independent_certificate/summary.json','construction',B+'rook_free_internal_pilot/manifest.json',None,
       dict(graph=B+'rook_free_internal_independent_certificate/independent_full59.json',assignment=B+'rook_free_internal_pilot/main/model.json',receipt=B+'rook_free_internal_pilot/main/receipt.json')),
      ('rook-original-gram',B+'independent_review/rook_original_gram.json','exclusion',B+'rook_free_internal_gram/manifest.json',[dep('C-ROOK-FOUR-FACTOR-WINDOW-LOCAL-CONSTRUCTION','verification_dependency')],
       dict(graph=B+'rook_free_internal_independent_certificate/independent_full59.json',certificate=B+'rook_free_internal_gram/result.json'))]
    now=datetime.now(timezone.utc).isoformat();added=[]
    for label,audit,kind,manifest,deps,extra in specs:
        r=read(audit);assert r['recommendation']=='VERIFIED'
        for p,v in r['inputs_sha256'].items():assert digest(p)==v,p
        paths={label+'-audit':audit,label+'-manifest':manifest,**{label+'-'+k:v for k,v in extra.items()}}
        artifacts=[dict(id=i,path=p,sha256=digest(p),availability='LOCAL_ONLY',retrieval='Workspace-relative evidence; gzip or chunk manifests recover large exact artifacts where recorded.',unavailable_reason='Publication to an immutable public commit has not yet been confirmed for this evidence set.') for i,p in paths.items()]
        deps=r.get('dependencies',[]) if deps is None else deps
        scope=r['scope'];limits=r['limitations']
        timestamp=r.get('timestamp',r.get('completed_at'))
        c=dict(id=r['claim_id'],revision=r['claim_revision'],statement=r['statement'],kind=kind,basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
            scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
            assumptions=['Only the exact labelled input artifacts and fixed-family restrictions stated in the audit.','No nontrivial graph automorphism or universal rook containment is assumed.'],
            dependencies=deps,evidence=list(paths),verification=[dict(claim_revision=r['claim_revision'],verifier=r['verifier'],method='independent_artifact_check',command_or_audit=audit,timestamp=timestamp,outcome='PASS',scope=scope,
              artifact_hashes={a['id']:a['sha256'] for a in artifacts},shared_components=r.get('shared_components',[]),
              controls=['Calibrated positive and deliberately corrupted controls are enumerated in the bound audit report.'],limitations=limits)],
            limitations=limits,created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Internal independent review; no external peer review claimed.'},reproducibility=dict(manifest=label+'-manifest'))
        assert c['id'] not in {x['id'] for x in data['claims']}
        data['claims'].append(c);data['artifacts'].extend(artifacts);added.append(c['id'])
    data['updated_at']=now
    result=validator.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'resume')
    with(out/'claims_before_second_milestone.yaml').open('xb')as f:f.write(before)
    assert ledger.read_bytes()==before
    ledger.write_text(yaml.safe_dump(data,sort_keys=False,width=110),encoding='utf-8')
    with(out/'second_milestone_registration.json').open('x',encoding='utf-8')as f:json.dump(dict(timestamp=now,new_claim_ids=added,previous_ledger_sha256=sha256(before).hexdigest(),ledger_sha256=digest('CLAIMS.yaml'),validation=result,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN'),f,indent=2)
    print(json.dumps(dict(claims_added=added,target_resolution='UNKNOWN')))

if __name__=='__main__':main()
