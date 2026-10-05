"""Register five independently checked records without altering past claims."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];I='acceleration/results/20260930_independent_review/'
ROWS=[
('direct_cell_lex_encoding/summary.json','f78c588dc981c27f644bb1d2f31bd5e22e5562a4274a53d9d7c062e6dc44c3ed','direct_cell_lex_claim_binding.json','364da2b485a13baeb6467d596f729461e896bfdb60be25330469d3754b543a00','/root/structural_attack'),
('direct_cell_unknown_trace_transport/summary.json','58905474aeed1bac31b58f30645b95019607cd10af7bab6542fb4712870503e5','direct_cell_unknown_trace_transport/claim_binding.json','ed63a0d06c2b19e47d77740892d0e44c927295a8ffaacc433482b46d4ef0da2d','/root/structural_attack'),
('direct_cell_lex_standalone_unknown/summary.json','f56257086586c6cad43bcab89da071551ca6d67e30196749827bb10dda280233','direct_cell_lex_standalone_unknown/claim_binding.json','ed4fa7ef98c532333d01438e2c618433f490ec4ea35b1321667b97c746339936','/root/structural_attack'),
('direct_cell_lex_coupled_unknown/summary.json','dde2093be28b749c4bd27e9be06158cce19d84d65aadb1123bc4cfa4d4191e8a','direct_cell_lex_coupled_unknown/claim_binding.json','18df03bb1b6f4fd455a6b68f87c31c308db71564b6eeb625b29448435cd9bea7','/root/structural_attack'),
('second_count_partial_cut/summary.json','727f9aa9aec1b3fe3f0f422e440dd0fb6fb5bfc63602c3aeee28ba3082bccfc8','second_count_partial_cut/claim_binding.json','6462eb2b89843de3dd6d87666c841b3cbbfed6e34089edbf7f94df8ef128aecb','/root')]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    assert len(old['claims'])==256 and hashlib.sha256(before).hexdigest()=='03fb3d56774f53e5b82e455aefcfd15b4f542ba09a90864e0101a8e951b3c471'
    now=datetime.now(timezone.utc).isoformat();bindings={};ids=[];adaptations=[]
    for index,(sp,sh,bp,bh,verifier)in enumerate(ROWS):
        sp=I+sp;bp=I+bp;assert h(sp)==sh and h(bp)==bh
        audit,row=read(sp),read(bp);assert audit['status'].startswith('INDEPENDENT_') and audit['status'].endswith('_PASS')
        assert row['status']=='VERIFIED' and row['revision']==1 and row['verifier']==verifier and row['producer']!=verifier
        assert row['id']not in{c['id']for c in data['claims']}
        for p in [sp,bp]:
            bindings[p]=h(p)
            for field in ['inputs_sha256','outputs_sha256','artifact_hashes','evidence_sha256']:
                for ref,digest in read(p).get(field,{}).items():
                    assert h(ref)==digest,ref;assert ref not in bindings or bindings[ref]==digest;bindings[ref]=digest
        evidence=[];hashes={}
        for j,p in enumerate([sp,bp]):
            aid=f'twentyfifth-lex-cuts-{index}-evidence{j}';assert aid not in{a['id']for a in data['artifacts']}
            evidence.append(aid);hashes[aid]=h(p)
            data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path; report binds complete source, raw artifacts, commands, checking path and controls.',unavailable_reason='Twenty-fifth immutable publication not yet confirmed.'))
        deps=copy.deepcopy(row['dependencies']);assumptions=row.get('assumptions')
        if index==1:
            assumptions=['Only the exact two saved host streams and138 gzip parts in the pinned manifest.','Independent UNKNOWN outcome reports bind the original streams and recorded availability; no complete proof interpretation.']
        elif index in(2,3):
            for dep in deps: assert dep['relation']=='verification_dependency' and h(dep['artifact'])==dep['sha256']
            deps=[dict(id='C-FIXED-HADAMARD-DIRECT-CELL-EQUAL-SUPPORT-LEX-NORMALIZATION',revision=1,relation='verification_dependency')]
            assumptions=['Exact saved native attempt and frozen guards only.','The pinned independent lex object-calibration gate remains an explicit checking premise.','Current ext4 originals are missing; complete retained host bytes and historical transfer are checked separately.']
            adaptations.append(dict(id=row['id'],change='Map original encoding artifact dependency to registered exact lex encoding revision; preserve object gate as pinned checking premise and original dependency records as evidence.'))
        assert assumptions
        unknowns={'external_source':'Internal verification; external review is not asserted.'}
        created=row.get('created_at');updated=row.get('updated_at')
        if created is None or updated is None:
            assert index==0;created=updated=now
            unknowns['historical_binding_creation_timestamp']='Original immutable lex binding omitted creation/update timestamps; ledger uses actual registration timestamp, not an invented historical date.'
            adaptations.append(dict(id=row['id'],change=unknowns['historical_binding_creation_timestamp']))
        verification=dict(claim_revision=1,verifier=verifier,method='independent_artifact_check',command_or_audit=sp,timestamp=audit['timestamp'],outcome='PASS',scope=row['scope'],artifact_hashes=hashes,shared_components=row['shared_components'],controls=[row['method'],'Complete calibrated controls and outcomes are in the bound independent report; registrar adds no mathematical check.'],limitations=row['limitations'])
        claim=dict(id=row['id'],revision=1,statement=row['statement'],kind=row['kind'],basis=row['basis'],status='VERIFIED',review_state='CLEAR',scope=dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),assumptions=assumptions,dependencies=deps,evidence=evidence,verification=[verification],limitations=row['limitations'],created_at=created,updated_at=updated,external_source=None,unknowns=unknowns,reproducibility=dict(manifest=evidence[0]))
        data['claims'].append(claim);ids.append(row['id'])
    assert len(ids)==5 and data['claims'][:-5]==old['claims'] and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    data['updated_at']=now;validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/'acceleration/results/20260930_twentyfifth_lex_cuts_registration';out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),registrar_sha256=h(Path(__file__).relative_to(ROOT)),command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=ids,checked_input_bindings=bindings,previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=validation,existing_claim_records_unchanged=True,existing_artifact_records_unchanged=True,binding_editorial_adaptations=adaptations,registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=len(data['claims']),new_verified=5,ledger_sha256=result['ledger_sha256'])))
if __name__=='__main__':main()
