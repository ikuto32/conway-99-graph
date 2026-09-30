"""Register six independently checked wave23 claims without broadening their scope."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
COHORTS=[
 ('hadamard_six_profile_cnf','09997159af6339561bd76aa05e0fed1118f8dfe629413ccbef4c8f05e7947e29','claim_binding.json','2d5f18e37c025f805ebea529c27c9049006bcb1f37c39cbabd37f403b4e99bb4',1,'/root/eight_domain_audit'),
 ('hadamard_six_profile_unsat','6d790eea59e2e0924f2c41df36c86ae899a41b03d1d4dddb623431a3f4e7b6b2','claim_binding.json','d5bdba1f0b6694ac52660d3568964b60a534004b2d8c666280bfe3e035792154',1,'/root/structural_attack'),
 ('hadamard_fiftyfour_profile_cnfs','4fa50584776c9862e4e4c0286567b212b9a436c13a6cf0ebf0cd0b0ad751a6e5','claim_binding.json','5241b84a5fa355755d5df3b98aa96154104586e6f5bb436f27b2dc716a0263f4',1,'eight_domain_audit'),
 ('hadamard_all_triple_descent','d16968f418a7fac753d20941e33571378054d3493a2f845b65019bf41107d36d','claim_binding.json','c3461e70bdf2c26cd8637d33844460d7b322f6e5c992fc908c1d2d4765ba84e3',1,'eight_domain_audit'),
 ('hadamard_eight_exception_census','95176ae42241c3745fe1e017fbeca3798b04bc49f1113455605c3ed928e204f6','claim_binding.json','9c5133f710dd9628e7dad6031a18f1031f5bc01b259811dcdb542ee1786a8705',1,'/root/eight_domain_audit'),
 ('hadamard_seven_profile_local_domains','764918cdb953f10f378304db4448000a8eee9b8e721e750fc62870df98fdbe2d','claim_binding.json','1a81a4ab44f8c13ff7e11d384ad35cab4d37303d8329e636f49b34128999d406',1,'/root/structural_attack')]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old);assert len(data['claims'])==216
    publication=read('acceleration/results/20260930_resume/twentysecond_publication_pointer_receipt.json')
    assert publication['published_commit']=='7d5e43c5529400d4ac6dc5aae53f904becaa597b'
    assert publication['ledger_sha256']==hashlib.sha256(before).hexdigest()
    bindings={};ids=[]
    for index,(directory,pin,filename,bpin,count,verifier)in enumerate(COHORTS):
        folder=I+directory+'/';sp=folder+'summary.json';bp=folder+filename
        assert h(sp)==pin and h(bp)==bpin
        audit=read(sp);rows=read(bp);rows=rows if isinstance(rows,list)else[rows];assert len(rows)==count and audit['status'].startswith('INDEPENDENT_')and audit['status'].endswith('_PASS')
        paths=[sp,bp]
        for p in paths:
            bindings[p]=h(p)
            obj=read(p)
            for record in(obj if isinstance(obj,list)else[obj]):
                for field in['inputs_sha256','outputs_sha256','evidence_sha256','artifact_hashes']:
                    for ref,sha in record.get(field,{}).items():
                        assert h(ref)==sha,ref;assert ref not in bindings or bindings[ref]==sha;bindings[ref]=sha
        evidence=[];hashes={}
        for j,p in enumerate(paths):
            aid=f'twentythird-base-{index}-evidence{j}';assert aid not in{a['id']for a in data['artifacts']};evidence.append(aid);hashes[aid]=h(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; independent reports bind raw evidence, source, commands and controls.',unavailable_reason='Twenty-third immutable evidence publication not yet confirmed.'))
        for row in rows:
            assert row.get('status',row.get('recommendation'))=='VERIFIED'and row['verifier']==verifier and row['revision']==1
            assert row['id']not in{c['id']for c in data['claims']}
            shared=row.get('shared_components',row.get('trusted_components',audit.get('shared_components',audit.get('source_sharing'))))
            assert shared
            assumptions=row.get('assumptions')
            if assumptions is None:
                assert directory in ('hadamard_fiftyfour_profile_cnfs','hadamard_all_triple_descent')
                assumptions=['The exact pinned support, profiles and within-triplicate caps stated in the bound encoding claim.'] if directory=='hadamard_fiftyfour_profile_cnfs' else ['The pinned finite saved artifacts, complete local catalog and exact objective version stated in the independent report.']
            v=dict(claim_revision=1,verifier=verifier,method='independent_artifact_check',command_or_audit=sp,timestamp=audit['timestamp'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=shared,controls=[row.get('method',row.get('checking_method')),'Exact controls and corruption outcomes are preserved in the bound independent report; no solver or proof replay repeated by registrar.'],limitations=row['limitations'])
            claim=dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',
                scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=assumptions,
                dependencies=[dict(id=dep.get('id',dep.get('claim_id')),revision=dep['revision'],relation=dep['relation']) for dep in row['dependencies']+row.get('verification_dependencies',[])],evidence=list(evidence),verification=[v],limitations=row['limitations'],
                created_at=row.get('created_at',row.get('created')),updated_at=row.get('updated_at',row.get('updated')),external_source=None,unknowns={'external_source':'Internal independent checking; no external peer review asserted.','verifier_name':'Recorded exactly as in each frozen binding; eight_domain_audit is the existing /root/eight_domain_audit agent alias.'},reproducibility=dict(manifest=evidence[0]))
            data['claims'].append(claim);ids.append(claim['id'])
    assert len(ids)==6 and data['claims'][:-6]==old['claims']and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentythird_base_results_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=6)))
if __name__=='__main__':main()

