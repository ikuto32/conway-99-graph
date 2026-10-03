"""Register independently reviewed encodings and one completed UNKNOWN run."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
ROWS=[('hadamard_oriented_triples','35d301643712de203946bb2dc2ce1908e5dc988a783dafff965015cde14a7f93','87dddbcffc7e7059d964bfe7b7130d11de15d6de3111f2b742ad68b4a5aff8a7','INDEPENDENT_HADAMARD_ORIENTED_TRIPLE_ENCODING_PASS'),
('hadamard_oriented_unknown','1210de7c30e3c8d6ce9bcd14b0e8e1aa7bd3ee16f82e5768c7d1b5e30843cc3a','4c9152971d0629c8387544b4e4257bde56ffdaae61207a17de011fe96f3bb872','INDEPENDENT_HADAMARD_ORIENTED_TRIPLE_UNKNOWN_RUN_AUDIT_PASS'),
('hadamard_balanced_gram_cnf_v2','b63a4de43c1bcf4de56c52e4b4cc3ae8c697a3198654eb3f44d97bce7549ea7c','890fe8bf2ae0c259b1ca298a9350809dccc65133ad8e6cde9dc10cbecf0dffbd','INDEPENDENT_HADAMARD_BALANCED_GRAM_ENCODING_PASS')]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==188
    ids=[];bindings={};new_artifacts={}
    def artifact(p):
        if p in new_artifacts:return new_artifacts[p]
        aid=f'twentieth-encodings-evidence{len(new_artifacts)}';assert aid not in{a['id'] for a in data['artifacts']}
        limitation='Raw partial trace retained locally; it is not a complete contradiction certificate.' if p.endswith('.drat') else 'Twentieth immutable evidence publication not yet confirmed.'
        data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; saved independent reports bind inputs, commands, versions and controls.',unavailable_reason=limitation));new_artifacts[p]=aid;return aid
    for directory,report_sha,binding_sha,status in ROWS:
        report_path=I+directory+'/summary.json';binding_path=I+directory+'/claim_binding.json'
        assert h(report_path)==report_sha and h(binding_path)==binding_sha
        audit=read(report_path);row=read(binding_path);assert audit['status']==status
        assert row['status']=='VERIFIED' and row['review_state']=='CLEAR' and row['revision']==1 and row['verifier']=='/root/structural_attack'
        assert row['id']not in{c['id'] for c in data['claims']}
        bindings[report_path]=report_sha;bindings[binding_path]=binding_sha
        for field in ['inputs_sha256','outputs_sha256']:
            for p,sha in audit.get(field,{}).items():assert h(p)==sha,p;assert p not in bindings or bindings[p]==sha;bindings[p]=sha
        paths=[report_path,binding_path]
        if directory=='hadamard_oriented_unknown':paths.append('acceleration/results/20260930_hadamard_oriented_triples_native_pilot/main/proof.drat')
        evidence=[artifact(p) for p in paths];hashes={artifact(p):h(p) for p in paths}
        dependencies=copy.deepcopy(row['dependencies'])
        dependencies.extend({k:v for k,v in dep.items() if k in ['id','revision','relation']} for dep in row.get('verification_dependencies',[]))
        verification=dict(claim_revision=1,verifier=row['verifier'],method='independent_artifact_check',command_or_audit=report_path,timestamp=audit['timestamp'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=row['shared_components'],controls=[row['method'],'The saved exact positive/corrupted controls and full artifact comparisons are bound in the audit; no target-wide completeness is implied.'],limitations=row['limitations'])
        data['claims'].append(dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=row['assumptions'],dependencies=dependencies,evidence=evidence,verification=[verification],limitations=row['limitations'],created_at=row['created_at'],updated_at=row['updated_at'],external_source=None,unknowns={'external_source':'Internal independent review only; no external acceptance or novelty assertion.'},reproducibility=dict(manifest=evidence[0])));ids.append(row['id'])
    assert data['claims'][:-3]==old['claims'] and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentieth_encoding_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=3)))
if __name__=='__main__':main()
