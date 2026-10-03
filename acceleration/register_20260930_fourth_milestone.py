"""Register fourteen completed independent claim reviews; no discovery is run."""
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
        ('box-rule','target_gram_boolean_box_lemma.json','mathematical result',True,'docs/DERIVATION_20260930_TARGET_GRAM_BOX_NOGOODS.md'),
        ('box-initial','initial_gram_box_nogood_claim_binding.json','exclusion',False,B+'rook_gram_box_cut_initial/manifest.json'),
        ('box-nine','rook_box_collection01.json','exclusion',False,B+'rook_box_batch01/accepted_checkpoint.json'),
        ('box-ten','rook_box_collection02.json','exclusion',False,B+'rook_box_lazy_wave02/final_checkpoint.json'),
        ('box-wave2','rook_box_wave02_binding.json','empirical/engineering result',False,B+'rook_box_lazy_wave02/manifest.json'),
        ('transport','scaffold_cut_transport_lemma.json','mathematical result',True,'docs/DERIVATION_20260930_SCAFFOLD_CUT_TRANSPORT.md'),
        ('maps32','rook_scaffold_relabelings32.json','encoding',False,B+'rook_scaffold_relabeling/accepted_relabelings.json'),
        ('degree-rule','degree_block_gram/lemma_claim_binding.json','mathematical result',False,B+'degree_block_gram_bounds/run01/manifest.json'),
        ('degree-cut12','degree_block_gram/cut_claim_binding.json','exclusion',False,B+'degree_block_gram_bounds/run01/final_cut_certificate.json'),
        ('orbits352','rook_cut_orbits/summary.json','exclusion',False,B+'rook_cut_orbits01/manifest.json'),
        ('matching-cap','local_redundancy_v2/matching_cap_lemma.json','mathematical result',True,'acceleration/theory_20260930_matching_cap_composition.md'),
        ('closed-upper','local_redundancy_v2/closed_gram_lemma.json','mathematical result',True,'acceleration/theory_20260930_closed28_gram_redundancy.md'),
        ('closed-lower','closed28_lower_lemma/summary.json','mathematical result',True,'acceleration/theory_20260930_closed28_lower_gram_redundancy.md'),
        ('closed29-two','closed29_specific_gram_v2/summary.json','exclusion',False,B+'closed29_extension_screen/run01/negative_candidates.json')]
    now=datetime.now(timezone.utc).isoformat();added=[]
    for label,filename,kind,general,manifest in specs:
        audit=B+'independent_review/'+filename;r=read(audit)
        if label=='box-wave2':
            assert r['status']=='INDEPENDENT_ROOK_BOX_WAVE_ARTIFACT_BINDING_PASS'
            assert r['counts']['solver_rounds']==2 and r['counts']['independent_local_sat_passes']==1 and r['counts']['unknown_solver_results']==1
            r.update(claim_id='C-ROOK-GRAM-BOX-WAVE02',claim_revision=1,recommendation='VERIFIED',basis=['COMPUTED'],
                statement='The exact recorded second boxed-Gram SAT wave on the frozen 780-edge family made two solver attempts: one produced a complete independently checked local59 assignment with a checked negative Gram direction and one new valid23literal box clause; the other returned UNKNOWN. The final ordered collection has ten clauses, and no UNSAT proof or whole-family exclusion was produced.',
                dependencies=[dep('C-ROOK-FOUR-FACTOR-BOX-CUT-COLLECTION01'),dep('C-ROOK-FOUR-FACTOR-BOX-CUT-COLLECTION02'),dep('C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING','encoding_equivalence')])
        if label=='orbits352':r['dependencies'].append(dep('C-ROOK-FOUR-FACTOR-BOX-CUT-COLLECTION02'))
        assert r['recommendation']=='VERIFIED'
        for p,h in r['inputs_sha256'].items():assert digest(p)==h,p
        paths={label+'-audit':audit,label+'-manifest':manifest}
        artifacts=[dict(id=i,path=p,sha256=digest(p),availability='LOCAL_ONLY',retrieval='Workspace-relative audit and hash-bound evidence. Public retrieval will be recorded after immutable publication is confirmed.',unavailable_reason='Public commit for these bytes is not yet confirmed.') for i,p in paths.items()]
        limits=r['limitations'];scope=r['scope'];revision=r['claim_revision']
        c=dict(id=r['claim_id'],revision=revision,statement=r['statement'],kind=kind,basis=r.get('basis',['DERIVED','COMPUTED']),status='VERIFIED',review_state='CLEAR',
            scope=dict(description=scope,unrestricted_target=general,target_resolution='NONE'),
            assumptions=['Exactly the hypotheses and pinned fixed configurations in the statement and bound independent audit.','No automorphism of a hypothetical target and no universal rook-containment assumption.'],
            dependencies=r['dependencies'],evidence=list(paths),verification=[dict(claim_revision=revision,verifier=r['verifier'],method='independent_derivation' if kind=='mathematical result' else 'independent_artifact_check',command_or_audit=audit,timestamp=r['timestamp'],outcome='PASS',scope=scope,
                artifact_hashes={a['id']:a['sha256'] for a in artifacts},shared_components=r.get('shared_components',[]),controls=['See exact positive and corrupted controls and scope of replay in the bound independent audit.'],limitations=limits)],
            limitations=limits,created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Independent internal checking only; no external peer review.'},reproducibility=dict(manifest=label+'-manifest'))
        assert c['id'] not in {x['id'] for x in data['claims']}
        data['claims'].append(c);data['artifacts'].extend(artifacts);added.append(c['id'])
    data['updated_at']=now
    result=validator.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'resume')
    with(out/'claims_before_fourth_milestone.yaml').open('xb')as f:f.write(before)
    assert ledger.read_bytes()==before
    ledger.write_text(yaml.safe_dump(data,sort_keys=False,width=110),encoding='utf-8')
    with(out/'fourth_milestone_registration.json').open('x',encoding='utf-8')as f:json.dump(dict(timestamp=now,new_claim_ids=added,previous_ledger_sha256=sha256(before).hexdigest(),ledger_sha256=digest('CLAIMS.yaml'),validation=result,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN'),f,indent=2)
    print(json.dumps(dict(claims_added=added,target_resolution='UNKNOWN')))

if __name__=='__main__':main()
