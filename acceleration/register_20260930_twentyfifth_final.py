"""Five independently approved scoped claims and one unreviewed design estimate."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
COHORTS=[
('count_master_partial_cut_cnf','dc1ada9d87d41b5cc6597cd0ff7ce2ed0a06981d8b487dbb797505240f435460','claim_binding.json','86bfdf8a9a1855d08bb059cdc3021a8ed95516467d458287a35f09ab9852b7a4'),
('lex_unknown_trace_transport','56b004dc3c72cb818610575febea7ef1a648e7c22d79bd0b28f6a0cd697c425c','claim_binding.json','a299be28ec97c813bc592c04f46bd9551d1614ad62c732a5e66b817ed023cd19'),
('gf2_alternating_completion_scope_addendum','c7e030dc5021fd018ab90371e8c9f82c72c116f40bf6f2a1e9b900f67b85e44a','claim_bindings.json','2bdf5ffb56e40b19535e8f9a35898c918a781aa7d64c2f0067b37752458dc4e3'),
('count_master_partial_cut_sat_outcome','736ccbcda81ee34c21ede2a80253d5b224fabb96a2e83d0a2c1c76dba435d071','claim_binding.json','3d23547288c66dc2f7e5c38e529d64746172044446e8fe15ec227c975a1eb3ee')]
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();assert hashlib.sha256(before).hexdigest()=='4241ad1f845aeccfcfeb01238e6df0f566ee0528f2ee9cc0e5662a4a9ecd7881'
    old=registry.read_ledger(path);assert len(old['claims'])==261;data=copy.deepcopy(old);now=datetime.now(timezone.utc).isoformat();pins={};ids=[];adaptations=[]
    def authenticate(p,h=None):
        digest=sha(p);assert h is None or digest==h,p;assert p not in pins or pins[p]==digest;pins[p]=digest
    def objects(obj):
        if isinstance(obj,list):return obj
        return obj['claims']if 'claims'in obj else[obj]
    def bind_records(p):
        authenticate(p)
        for row in objects(read(p)):
            for field in ['inputs_sha256','outputs_sha256','artifact_hashes','evidence_sha256']:
                for ref,h in row.get(field,{}).items():authenticate(ref,h)
    def evidence(paths,label):
        aids=[];hashes={}
        for j,p in enumerate(paths):
            bind_records(p);aid=f'twentyfifth-final-{label}-evidence{j}';assert aid not in{a['id']for a in data['artifacts']};aids.append(aid);hashes[aid]=sha(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=sha(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; frozen report binds source, artifacts, commands, versions, limits and verification controls.',unavailable_reason='Twenty-fifth immutable evidence publication not yet confirmed.'))
        return aids,hashes
    for index,(directory,sh,filename,bh)in enumerate(COHORTS):
        sp=I+directory+'/summary.json';bp=I+directory+'/'+filename;authenticate(sp,sh);authenticate(bp,bh);audit=read(sp)
        assert audit['status'].startswith('INDEPENDENT_') and audit['status'].endswith('_PASS'),audit['status']
        paths=[sp,bp]
        if index==2:
            original=I+'gf2_alternating_completion_v2/summary.json';authenticate(original,'a18dbc2aff1e98a881226e04432e3db08a0b827741dc615eaf00c1c06ca0d093');paths.append(original)
        aids,hashes=evidence(paths,str(index))
        for row in objects(read(bp)):
            assert row['status']=='VERIFIED' and row['revision']==1
            cid=row.get('id',row.get('claim_id'));assert cid not in{c['id']for c in data['claims']}
            limitations=row['limitations'];dependencies=copy.deepcopy(row['dependencies']);unknowns={'external_source':'Internal independent review; no external peer review claimed.'}
            if index==3:
                verifier='/root/'+row['independent_verification']['verifier'];assert verifier=='/root/structural_attack'
                method=row['independent_verification']['method'];kind='construction';basis=['COMPUTED'];scope=audit['scope'];created=updated=now
                assumptions=['Exact saved native assignment and authenticated fixed count-CSP encoding.','Complete local catalogue and model meanings are pinned independent premises; this outcome check reconstructs the actual counts.']
                dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PROFILE-SIX-SCALAR-CUT-COUNT-ENCODING',revision=1,relation='encoding_equivalence'),dict(id='C-FIXED-HADAMARD-SIX-PARTIAL-SCALAR-COUNT-CUTS',revision=1,relation='uses_result')]
                unknowns['historical_binding_creation_timestamp']='Original binding omitted claim creation/update times; actual ledger registration time used.'
                adaptations.append(dict(id=cid,changes=['Canonicalize recorded verifier structural_attack to /root/structural_attack.','Use construction/COMPUTED for the exact count witness; statement unchanged.','Bind new complete encoding claim revision and keep original dependency records in evidence.','Use actual registration timestamp; original binding omitted claim timestamps.']))
            else:
                verifier=row['verifier'];assert verifier!=row['producer'];method=row.get('method',row.get('checking_method'));kind=row['kind'];basis=row['basis'];scope=row['scope'];created=row['created_at'];updated=row['updated_at'];assumptions=row['assumptions']
            assert method and assumptions
            v=dict(claim_revision=1,verifier=verifier,method='independent_artifact_check'if index!=2 else'independent_derivation',command_or_audit=sp,timestamp=audit['timestamp'],outcome='PASS',scope=scope,artifact_hashes=hashes,shared_components=row['shared_components'],controls=[method,'Detailed complete/sampled distinctions and corruption controls remain in the bound reports; this registrar performs no new mathematical verification.'],limitations=limitations)
            data['claims'].append(dict(id=cid,revision=1,statement=row['statement'],kind=kind,basis=basis,status='VERIFIED',review_state='CLEAR',scope=dict(description=scope,unrestricted_target=index==2,target_resolution='NONE'),assumptions=assumptions,dependencies=dependencies,evidence=aids,verification=[v],limitations=limitations,created_at=created,updated_at=updated,external_source=None,unknowns=unknowns,reproducibility=dict(manifest=aids[0])));ids.append(cid)
    candidate=B+'all_triple_count_preflight_v3/summary.json';authenticate(candidate,'7ed9bc4170703472057ba9549d2959d5533e480fbc109f4792defbcaab071518');aids,_=evidence([candidate,B+'all_triple_count_preflight_v3/manifest.json'],'inventory')
    row=read(candidate);assert row['research_CNF_built']is False and row['independent_approval']is False and row['native_calls']==0
    cid='C-FIXED-HADAMARD-ALL-TRIPLE-COUNT-DESIGN-INVENTORY';assert cid not in{c['id']for c in data['claims']}
    data['claims'].append(dict(id=cid,revision=1,statement='The frozen all-triple/count design inventory estimates its at-least-seven variant at1405719 variables,31254053 clauses and760094578 DIMACS ASCII bytes. The formula was not built or searched. These design counts have not received independent checking.',kind='empirical/engineering result',basis=['COMPUTED'],status='CANDIDATE',review_state='CLEAR',scope=dict(description='Only the frozen proposed all31110 local triples per20groups count/Gram recipe, with within-group caps and no cross-group caps. Inventory numbers are unverified estimates for that recipe.',unrestricted_target=False,target_resolution='NONE'),assumptions=['Literal raw support, retained local catalogue and proposed unshared threshold-channel construction.'],dependencies=[dict(id='C-FIXED-HADAMARD-ARBITRARY-EXCEPTION-COUNT-MASTER-ENCODING',revision=1,relation='uses_result')],evidence=aids,verification=[],limitations=['No encoding equivalence, successful CNF build, solver performance, memory sufficiency or target conclusion established.','Prior group-order failure and corrected Windows memory-probe records are preserved as evidence.'],created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Internal proposed engineering design.','independent_review':'No independent inventory review was performed; producer self-checks do not promote status.'},reproducibility=dict(manifest=aids[1])));ids.append(cid)
    assert len(ids)==6 and len(data['claims'])==267 and data['claims'][:-6]==old['claims'] and data['artifacts'][:len(old['artifacts'])]==old['artifacts'];data['updated_at']=now
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/(B+'twentyfifth_final_registration');out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before);after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),registrar_sha256=sha(Path(__file__).relative_to(ROOT)),new_claim_ids=ids,new_verified=5,new_candidate=1,checked_input_bindings=pins,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,binding_editorial_adaptations=adaptations,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=267,new_verified=5,new_candidate=1,ledger_sha256=result['ledger_sha256'])))
if __name__=='__main__':main()
