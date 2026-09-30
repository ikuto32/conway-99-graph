"""One-shot append of four independently approved count-relaxation records."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
COHORTS=[('count_master_claim_binding','claim_binding.json','71d5e80e7b8ac1358fc857fc6b502dd54a2fc099bf7fc8643d0beb45a66ad976','bb7d6e4ae74b7510f9647719529f2574a79949322742a026455e50d3ef7c06f8',1),('count_master_sat_outcome','claim_binding.json','61e7eb9643902c866617a270d856a521f71f5b2723c0e731edae3896baba484d','c85e37976da76539541d6a96e30a58c9df9245ae536bc12c5e3a3a6e6a700e6c',1),('count_interval_claim_bindings','claim_bindings.json','ac0816933527d8f2bfe96c208fb265f741eae3df4da31ca9e6646b7d460652e2','d6426ac132d214b488219fc0e96eb2a750cdf1a62cae955981c530ea242c5e3d',2)]
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(old['claims'])==233
    checked={};newids=[];added={}
    def bind(p,h):
        assert p not in checked or checked[p]==h
        if p not in checked:assert sha(p)==h,p;checked[p]=h
    def bindings(obj):
        if isinstance(obj,list):
            for x in obj:bindings(x)
        elif isinstance(obj,dict):
            for k,v in obj.items():
                if k in ('inputs_sha256','outputs_sha256','evidence_sha256','artifact_hashes'):
                    for p,h in v.items():bind(p,h)
                else:bindings(v)
    def artifact(p):
        if p in added:return added[p]
        aid='twentyfourth-count-evidence-'+str(len(added));assert aid not in {a['id']for a in data['artifacts']};h=sha(p);bind(p,h);added[p]=aid
        data['artifacts'].append(dict(id=aid,path=p,sha256=h,availability='LOCAL_ONLY',retrieval='Exact workspace path. Bound independent reports retain commands, inputs, outputs, controls and original verification records.',unavailable_reason='Twenty-fourth immutable evidence publication not yet confirmed.'))
        return aid
    for directory,filename,sp,bp,count in COHORTS:
        summary=I+directory+'/summary.json';binding=I+directory+'/'+filename;bind(summary,sp);bind(binding,bp);summary_record=read(summary);rows=read(binding);rows=rows if isinstance(rows,list)else[rows];assert len(rows)==count
        assert summary_record['status'].startswith('INDEPENDENT_')and summary_record['status'].endswith('_PASS');bindings(summary_record);bindings(rows)
        for row in rows:
            assert row['status']=='VERIFIED'and row['review_state']=='CLEAR'and row['revision']==1 and row['verifier']=='/root/eight_domain_audit'
            assert row['id']not in{c['id']for c in data['claims']}
            paths=[summary,binding]
            for ev in row.get('evidence',[]):bind(ev['path'],ev['sha256']);paths.append(ev['path'])
            for v in row['verification_records']:
                assert v['claim_id']==row['id']and v['claim_revision']==1 and v['verifier']==row['verifier']and v['outcome']=='PASS'
                if 'report_path'in v:bind(v['report_path'],v['report_sha256']);paths.append(v['report_path'])
            paths=list(dict.fromkeys(paths));evidence=[artifact(p)for p in paths];hashes={artifact(p):sha(p)for p in paths};verifications=[]
            for v in row['verification_records']:
                audit=v.get('report_path',summary)
                verifications.append(dict(claim_revision=1,verifier=v['verifier'],method='independent_artifact_check',command_or_audit=audit,timestamp=v['timestamp'],outcome='PASS',scope=v.get('scope',row['scope']),artifact_hashes=hashes,shared_components=row['trusted_components'],controls=[v.get('method',row.get('checking_method','Exact derivation and artifact checks are recorded in the bound independent reports.')),'Original verifier records, calibrated controls and exact command arrays preserved without rewriting in the bound claim-binding artifact.'],limitations=row['limitations']))
            claim={k:row[k]for k in ['id','revision','statement','kind','basis','status','review_state','assumptions','dependencies','limitations','created_at','updated_at']}
            claim.update(scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),evidence=evidence,verification=verifications,external_source=None,unknowns={'external_source':row['external_review_null_reason']},reproducibility=dict(manifest=artifact(summary)))
            data['claims'].append(claim);newids.append(claim['id'])
    assert len(newids)==4 and data['claims'][:-4]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentyfourth_count_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=newids,checked_input_bindings=checked,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=4,checked_input_bindings=len(checked))))
if __name__=='__main__':main()
