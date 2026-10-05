"""Promote unchanged PSD statement r1 to r2 only on the separate complete audit."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
def h(p):
    with (ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==284
    sp=B+'independent_review/exact_eight_psd_screen/summary.json';bp=B+'independent_review/exact_eight_psd_screen/claim_binding.json'
    assert h(sp)=='94f6313cbd0bdc6ddef5930a53bb09f22742abe6a3cfe42fccf0cd9416bf259a'
    assert h(bp)=='0b7a8c808badd90812291f835cdafb5991bec8d3d4ca845f853c8a96c032572e'
    audit=read(sp);row=read(bp);assert audit['status']=='INDEPENDENT_EXACT_EIGHT_PSD_SCREEN_PASS'
    assert row['revision']==2 and row['previous_revision']==1 and row['status']=='VERIFIED' and row['verifier']=='/root/state_literature_audit'
    checked={sp:h(sp),bp:h(bp)}
    for record in [audit,row]:
        for field in ['inputs_sha256','outputs_sha256','artifact_hashes','evidence_sha256']:
            for p,s in record.get(field,{}).items():assert h(p)==s,p;checked[p]=s
    impact=row['revision_impact'];snap=impact['candidate_snapshot'];assert h(snap)==impact['candidate_snapshot_sha256']
    historical=registry.read_ledger(ROOT/snap);prior=next(c for c in historical['claims']if c['id']==row['id']);claim=next(c for c in data['claims']if c['id']==row['id'])
    assert claim==prior and claim['revision']==1 and claim['status']=='CANDIDATE' and not claim['verification']
    for field in ['statement','kind','basis','assumptions','dependencies','created_at']:assert row[field]==claim[field],field
    assert row['scope']==claim['scope']['description']
    dependents=[c['id']for c in data['claims']for d in c['dependencies']if d['id']==claim['id']];assert not dependents,'Explicit dependent impact review required'
    now=datetime.now(timezone.utc).isoformat();hashes={}
    for i,p in enumerate([sp,bp]):
        aid=f'twentyseventh-psd-review-evidence{i}';assert aid not in{a['id']for a in data['artifacts']};hashes[aid]=h(p)
        data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; complete independent integer matrix/certificate audit and r2 binding.',unavailable_reason='Wave27 immutable publication not yet confirmed.'));claim['evidence'].append(aid)
    claim.update(revision=2,status='VERIFIED',review_state='CLEAR',updated_at=now,limitations=row['limitations'])
    claim['unknowns'].pop('independent_verification')
    claim['verification'].append(dict(claim_revision=2,verifier=row['verifier'],method='independent_artifact_check',command_or_audit=sp,timestamp=row['updated_at'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=row['shared_components'],controls=[row['method'],'All792 matrix certificates and the exact positive/corruption controls are recorded in the bound independent audit.'],limitations=row['limitations']))
    for a in data['artifacts']:
        if a['id'].startswith('twentyseventh-psd-candidate-evidence'):a['unavailable_reason']='Wave27 immutable publication not yet confirmed; original producer-only evidence retained.'
    data['updated_at']=now
    assert all(a==b for a,b in zip(data['claims'],old['claims'])if a['id']!=row['id'])
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/(B+'twentyseventh_psd_promotion');out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),registrar_sha256=h(Path(__file__).relative_to(ROOT)),previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),promoted_claim_ids=[row['id']],from_revision=1,to_revision=2,statement_scope_assumptions_dependencies_unchanged=True,dependent_claims=dependents,checked_artifact_hashes=checked,revision_impact=impact,validation=validation,producer_approves_own_claim=False,target_resolution='UNKNOWN')
    with (out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=284,promoted_to_verified=1,new_statements=0)))
if __name__=='__main__':main()
