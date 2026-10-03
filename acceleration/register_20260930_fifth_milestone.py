"""Register completed exact encoding and artifact audits, without running discovery."""
from datetime import datetime,timezone
from hashlib import sha256
import json,yaml
import validate_claims as validator
from register_20260930_second_milestone import digest,read,dep,ROOT,B

def main():
    ledger=ROOT/'CLAIMS.yaml';before=ledger.read_bytes();old=validator.read_ledger(ledger);data=validator.read_ledger(ledger)
    specs=[
        ('eight-sat','independent_review/eight_full99_cnf/summary.json','encoding',False,'eight_full99_cnf/manifest.json','eight_full99_cnf/artifact_packages.json'),
        ('eight-cut44','independent_review/eight_full99_w81_gram_cut/summary.json','exclusion',False,'eight_raw29_gram_cut/manifest.json','eight_raw29_gram_cut/certificate.json'),
        ('orbit-witness','independent_review/rook_orbit_sat_replay_v2/summary.json','construction',False,'rook_orbit_solver_pilot/manifest.json','independent_review/rook_orbit_sat_replay_v2/independent_full59.json'),
        ('orbit-dual','independent_review/rook_orbit_gram/summary.json','exclusion',False,'rook_orbit_gram01/manifest.json','rook_orbit_gram01/result.json'),
        ('orbit-cut43','rook_orbit_gram_box01/independent_box_nogood.json','exclusion',False,'rook_orbit_gram_box01/manifest.json','rook_orbit_gram_box01/certificate.json'),
        ('unrestricted-sat','independent_review/unrestricted_full99_cnf/summary.json','encoding',True,'unrestricted_full99_cnf/manifest.json','unrestricted_full99_cnf/artifact_packages.json')]
    now=datetime.now(timezone.utc).isoformat();added=[]
    for label,suffix,kind,unrestricted,manifest,extra in specs:
        audit=B+suffix;r=read(audit)
        if label=='orbit-witness':
            assert r['status']=='INDEPENDENT_ORBIT_AUGMENTED_ROOK_WINDOW_SAT_PASS'
            assert r['variables']==30420 and r['checked_clauses']==3690172 and r['appended_clauses']==352
            r.update(claim_id='C-ROOK-ORBIT-AUGMENTED-LOCAL59-WITNESS',claim_revision=1,recommendation='VERIFIED',basis=['COMPUTED'],
                dependencies=[dep('C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING','encoding_equivalence'),dep('C-ROOK-GRAM-CUT-ORBITS-352','uses_result')])
        if label=='orbit-cut43':
            assert r['status']=='INDEPENDENT_TARGET_GRAM_BOX_NOGOOD_PASS' and r['clause_length']==43
            assert r['global_boolean_box_upper_bound']==-647025452510426640
            r.update(claim_id='C-ROOK-ORBIT-LOCAL59-GRAM-BOX-CUT43',claim_revision=1,
                scope='One explicit43literal forbidden Boolean edge pattern in the pinned780edge central-factor family; not a full-family exclusion.',basis=['DERIVED','COMPUTED'])
            r['dependencies'].append(dep('C-ROOK-ORBIT-LOCAL59-DUAL-GRAM-EXCLUSION','derived_from'))
        if label=='orbit-dual':r['dependencies'].append(dep('C-ROOK-ORBIT-AUGMENTED-LOCAL59-WITNESS','derived_from'))
        assert r['recommendation']=='VERIFIED'
        for p,h in r['inputs_sha256'].items():assert digest(p)==h,p
        paths={label+'-audit':audit,label+'-manifest':B+manifest,label+'-artifact':B+extra}
        artifacts=[dict(id=i,path=p,sha256=digest(p),availability='LOCAL_ONLY',retrieval='Workspace-relative audited evidence; exact gzip companions or ordered package parts recover oversized original bytes.',unavailable_reason='Public commit for this evidence has not yet been confirmed.') for i,p in paths.items()]
        limits=r['limitations'];scope=r['scope'];revision=r['claim_revision']
        c=dict(id=r['claim_id'],revision=revision,statement=r['statement'],kind=kind,basis=r.get('basis',['DERIVED','COMPUTED']),status='VERIFIED',review_state='CLEAR',
            scope=dict(description=scope,unrestricted_target=unrestricted,target_resolution='NONE'),
            assumptions=r.get('assumptions',['Exactly the frozen model or graph and the declared hypotheses in the statement and independent report.','No nontrivial target automorphism.']),
            dependencies=r['dependencies'],evidence=list(paths),verification=[dict(claim_revision=revision,verifier=r['verifier'],method='independent_artifact_check',command_or_audit=audit,timestamp=r['timestamp'],outcome='PASS',scope=scope,
                artifact_hashes={a['id']:a['sha256'] for a in artifacts},shared_components=r.get('shared_components',[]),controls=['Full positive and adversarial controls and shared trusted components are enumerated in the bound audit.'],limitations=limits)],
            limitations=limits,created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Independent internal checking only; no external review.'},reproducibility=dict(manifest=label+'-manifest'))
        assert c['id'] not in {x['id'] for x in data['claims']}
        data['claims'].append(c);data['artifacts'].extend(artifacts);added.append(c['id'])
    data['updated_at']=now
    result=validator.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert result['valid'],result['errors']
    out=ROOT/(B+'resume')
    with(out/'claims_before_fifth_milestone.yaml').open('xb')as f:f.write(before)
    assert ledger.read_bytes()==before;ledger.write_text(yaml.safe_dump(data,sort_keys=False,width=110),encoding='utf-8')
    with(out/'fifth_milestone_registration.json').open('x',encoding='utf-8')as f:json.dump(dict(timestamp=now,new_claim_ids=added,previous_ledger_sha256=sha256(before).hexdigest(),ledger_sha256=digest('CLAIMS.yaml'),validation=result,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN'),f,indent=2)
    print(json.dumps({'new_verified_claims':added,'target_resolution':'UNKNOWN'}))
if __name__=='__main__':main()
