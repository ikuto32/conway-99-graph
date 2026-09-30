"""Register two exact engineering counterexamples; no research claim is invalidated."""
from datetime import datetime,timezone
from pathlib import Path
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
BINDINGS=[('parallel_build_deadline_binding','2218dc272bd1738693b8bbdbf6f3086cf543c19cc2a43e682fab992f3273936a'),('windows_job_assignment_race_binding','ff51ff68c79f75e530d4f4c31ee7a8ee347cd4ff4e29bc662bdda905cdca2a53')]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    assert len(old['claims'])==292 and hashlib.sha256(before).hexdigest()=='8163e0459c3ead042574ca06fa531160f720ba102fa0c9828993c69256d45193'
    checked={};ids=[]
    for index,(folder,pin)in enumerate(BINDINGS):
        bp=I+folder+'/claim_binding.json';assert h(bp)==pin;row=read(bp)
        assert row['status']=='REFUTED'and row['revision']==1 and row['verifier']=='/root/state_literature_audit'
        assert row['id']not in{c['id']for c in data['claims']}and row['kind']=='empirical/engineering result'
        sp=row['independent_verification']['report'];assert h(sp)==row['independent_verification']['sha256'];audit=read(sp)
        assert audit['status']==row['independent_verification']['status']
        for p,obj in[(bp,row),(sp,audit)]:
            checked[p]=h(p)
            for field in ['inputs_sha256','outputs_sha256']:
                for q,v in obj.get(field,{}).items():assert h(q)==v,q;assert q not in checked or checked[q]==v;checked[q]=v
        evidence=[];eh={}
        for j,p in enumerate([bp,sp]):
            aid=f'twentyeighth-launcher-refutation-{index}-evidence{j}';assert aid not in{a['id']for a in data['artifacts']};evidence.append(aid);eh[aid]=h(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; independent source-bound counterexample and raw observations.',unavailable_reason='Twenty-eighth immutable evidence publication not yet confirmed.'))
        verification=dict(claim_revision=1,verifier=row['verifier'],method='independent_artifact_check',command_or_audit=bp,timestamp=row['updated_at'],outcome='FAIL',scope=row['scope']['description'],artifact_hashes=eh,shared_components=row['shared_components'],controls=row.get('controls',[row['method'],'Paired zero-delay positive and permitted delayed-cleanup counterexample, as recorded in the exact bound report.']),limitations=row['limitations'])
        data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='REFUTED',review_state='CLEAR',scope=row['scope'],assumptions=row['assumptions'],dependencies=row['dependencies'],evidence=evidence,verification=[verification],limitations=row['limitations'],created_at=row['created_at'],updated_at=row['updated_at'],external_source=None,unknowns={'external_source':'Internal independent counterexample, not external review.'},reproducibility={'manifest':evidence[0]}));ids.append(row['id'])
    assert data['claims'][:-2]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentyeighth_launcher_refutation_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),registrar_sha256=h(Path(__file__).relative_to(ROOT)),new_claim_ids=ids,checked_input_bindings=checked,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,binding_editorial_adaptations=['Use timestamp of the independent written claim-binding audit; original execution timestamps/commands are preserved in its evidence.','Copy each exact scope object and its description into the corresponding schema fields. No changes to prior mathematical claims.'],registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=0,new_refuted=2)))
if __name__=='__main__':main()
