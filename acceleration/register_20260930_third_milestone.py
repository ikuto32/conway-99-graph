"""Bind exact completed independent reports; no discovery code is executed."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml
import validate_claims as validator
from register_20260930_second_milestone import digest,read,dep,ROOT,B

def main():
    ledger=ROOT/'CLAIMS.yaml';before=ledger.read_bytes();old=validator.read_ledger(ledger);data=validator.read_ledger(ledger)
    specs=[
      ('gram-lemma','target_gram_support_lemma.json','mathematical result',True,B+'independent_review/target_gram_support_lemma.json',{'derivation':'docs/DERIVATION_20260930_TARGET_GRAM_NOGOODS.md'}),
      ('gram-cut45','minimized_gram_nogood_claim_binding.json','exclusion',False,B+'rook_gram_minimized/manifest.json',{'raw-audit':B+'rook_gram_minimized/independent_nogood.json','certificate':B+'rook_gram_minimized/certificate.json','clause':B+'rook_gram_minimized/nogood.clause'}),
      ('large-gpu-gate','large_gpu_calibration_claim_binding.json','empirical/engineering result',False,B+'large_gpu_build/preregistration.json',{'full-audit':B+'independent_review/large_gpu_cpu_parity/summary.json','pilot':B+'large_gpu_reader/pilot/summary.json','source':'acceleration/moment_pdhg_gpu_large.cu','build':'acceleration/build_moment_pdhg_gpu_large.ps1','build-receipt':B+'large_gpu_build/receipt.json'}),
      ('eight-gpu-six','eight_gpu_support_run02_claim_binding.json','empirical/engineering result',False,B+'eight_moment_pdhg/run02/manifest.json',{'full-audit':B+'independent_review/eight_gpu_support_run02.json','attempts':B+'eight_moment_pdhg/run02/certificates/summary.json','execution':B+'eight_moment_pdhg/run02/receipt.json','chunks':B+'eight_moment_pdhg/run02/chunk_manifest.json'}),
      ('rook-lazy01','rook_lazy_wave01_binding.json','empirical/engineering result',False,B+'rook_lazy_wave01/manifest.json',{'summary':B+'rook_lazy_wave01/summary.json','checkpoint':B+'rook_lazy_wave01/final_checkpoint.json'})]
    now=datetime.now(timezone.utc).isoformat();added=[]
    for label,filename,kind,unrestricted,manifest,extra in specs:
        audit=B+'independent_review/'+filename;r=read(audit)
        if label=='rook-lazy01':
            assert r['status']=='INDEPENDENT_ROOK_LAZY_WAVE_ARTIFACT_BINDING_PASS'
            r.update(claim_id='C-ROOK-GRAM-NOGOOD-WAVE01',claim_revision=1,recommendation='VERIFIED',
                statement='In the exact recorded first lazy SAT wave on the frozen 780-edge central-factor family, nine solver attempts produced eight distinct independently checked local 59-vertex graphs and one UNKNOWN attempt. Each of the eight graphs has a checked negative integer Gram quadratic and a valid support nogood for target extensions; the accepted ordered cut list has nine clauses including the separately checked initial clause. No UNSAT proof or whole-family exclusion was produced.',
                dependencies=[dep('C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS'),dep('C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING','encoding_equivalence'),dep('C-ROOK-FOUR-FACTOR-MINIMIZED-GRAM-NOGOOD')],basis=['DERIVED','COMPUTED'])
        assert r['recommendation']=='VERIFIED'
        for p,v in r['inputs_sha256'].items():assert digest(p)==v,p
        paths={label+'-audit':audit,label+'-manifest':manifest,**{label+'-'+k:v for k,v in extra.items()}}
        if label=='eight-gpu-six':
            for row in read(extra['attempts'])['attempts']:paths[label+'-'+str(row['iterations'])+'-'+row['iterate']]=row['path']
        artifacts=[dict(id=i,path=p,sha256=digest(p),availability='LOCAL_ONLY',retrieval='Workspace-relative report/raw evidence; referenced gzip/chunk manifests or native build sources provide reconstruction where stated.',unavailable_reason='Immutable public commit for these bytes has not yet been confirmed.') for i,p in paths.items()]
        scope=r['scope'];limits=r['limitations'];revision=r.get('claim_revision',1)
        c=dict(id=r['claim_id'],revision=revision,statement=r['statement'],kind=kind,basis=r.get('basis',['COMPUTED']),status='VERIFIED',review_state='CLEAR',
            scope=dict(description=scope,unrestricted_target=unrestricted,target_resolution='NONE'),
            assumptions=['All assumptions and quantifiers are exactly those in the stated target identity or frozen artifacts and bound audit.','No graph automorphism or universal rook-containment premise.'],
            dependencies=r['dependencies'],evidence=list(paths),verification=[dict(claim_revision=revision,verifier=r['verifier'],method='independent_derivation' if label=='gram-lemma' else 'independent_artifact_check',command_or_audit=audit,timestamp=r['timestamp'],outcome='PASS',scope=scope,
              artifact_hashes={a['id']:a['sha256'] for a in artifacts},shared_components=r.get('shared_components',[]),controls=['The bound audit enumerates exact positive and corrupted controls and discloses complete versus reused checking paths.'],limitations=limits)],
            limitations=limits,created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Internal independent checking only; no external peer review.'},reproducibility=dict(manifest=label+'-manifest'))
        assert c['id'] not in {x['id'] for x in data['claims']}
        data['claims'].append(c);data['artifacts'].extend(artifacts);added.append(c['id'])
    data['updated_at']=now
    result=validator.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'resume')
    with(out/'claims_before_third_milestone.yaml').open('xb')as f:f.write(before)
    assert ledger.read_bytes()==before;ledger.write_text(yaml.safe_dump(data,sort_keys=False,width=110),encoding='utf-8')
    with(out/'third_milestone_registration.json').open('x',encoding='utf-8')as f:json.dump(dict(timestamp=now,new_claim_ids=added,previous_ledger_sha256=sha256(before).hexdigest(),ledger_sha256=digest('CLAIMS.yaml'),validation=result,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN'),f,indent=2)
    print(json.dumps(dict(claims_added=added,target_resolution='UNKNOWN')))

if __name__=='__main__':main()
