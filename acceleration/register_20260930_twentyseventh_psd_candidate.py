"""Record a producer-only PSD census as CANDIDATE, pending separate review."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
def h(p):
    with (ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=copy.deepcopy(old)
    assert len(old['claims'])==281
    sp=B+'exact_eight_psd_screen/summary_001.json'
    assert h(sp)=='7f60e486053bfe4b824b277691445e73ed3c468ab3ccdc4676db622b7d674207'
    run=read(sp);assert run['completed']==run['population']==792 and run['result_counts']=={'EXACT_RATIONAL_PSD':792} and run['rank_counts']=={'22':792}
    checked=dict(run['inputs_sha256'])
    for r in run['results']:checked[r['certificate_path']]=r['certificate_sha256']
    for p,s in checked.items():assert h(p)==s,p
    now=datetime.now(timezone.utc).isoformat();evidence=[]
    for i,p in enumerate([sp,B+'exact_eight_psd_screen/manifest.json',B+'exact_eight_psd_screen/attempt_001.json']):
        aid=f'twentyseventh-psd-candidate-evidence{i}';assert aid not in{a['id']for a in data['artifacts']};evidence.append(aid)
        data['artifacts'].append(dict(id=aid,path=p,sha256=h(p),availability='LOCAL_ONLY',retrieval='Exact workspace path. Summary binds all792 raw matrices and rational certificates.',unavailable_reason='Wave27 evidence not yet published; independent review pending.'))
    cid='C-FIXED-HADAMARD-EXACT-EIGHT-SURVIVOR-PSD-SCREEN';assert cid not in{c['id']for c in data['claims']}
    statement='For every one of the792 canonical count tables in authenticated scalar/block survivor population, N[f*12+a,g]=counts[a][g][f] and fixedintegerG give R=3G-NN^T positive semidefinite overQ, with rank22.'
    claim=dict(id=cid,revision=1,statement=statement,kind='mathematical result',basis=['COMPUTED'],status='CANDIDATE',review_state='CLEAR',
        scope=dict(description='Complete finite PSD diagnostic on792 canonical exactly-eight count tables of the literal six-prism support; no simultaneous factor feasibility or exclusion.',unrestricted_target=False,target_resolution='NONE'),
        assumptions=['Pinned literal core, prescribed integer Gram matrix and the authenticated complete scalar/block survivor population.'],
        dependencies=[dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-SEPARATE-GRAM-BLOCK-SCREEN',revision=1,relation='coverage')],evidence=evidence,verification=[],
        limitations=['Producer-only certificates have not yet received independent checking.','A necessary PSD pass establishes neither factor feasibility nor a target graph.','Only792 surviving canonical count profiles are tested; no other count population is included.'],
        created_at=now,updated_at=now,external_source=None,unknowns={'external_source':'Internal computational candidate, not a literature claim.','independent_verification':'Pending a separately implemented raw-matrix/certificate check by a nondiscovery verifier.'},reproducibility=dict(manifest=evidence[2]))
    data['claims'].append(claim);data['updated_at']=now
    assert data['claims'][:-1]==old['claims'] and data['artifacts'][:len(old['artifacts'])]==old['artifacts']
    validation=registry.validate(data,ROOT,read('docs/claims.schema.json'),'available',old);assert validation['valid'],validation['errors']
    out=ROOT/(B+'twentyseventh_psd_candidate_registration');out.mkdir(exist_ok=False);(out/'CLAIMS.before.yaml').write_bytes(before)
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode();assert path.read_bytes()==before;path.write_bytes(after);(out/'CLAIMS.after.yaml').write_bytes(after)
    result=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),registrar_sha256=h(Path(__file__).relative_to(ROOT)),
                previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),new_claim_ids=[cid],candidate_revision=1,checked_artifact_hashes=checked,validation=validation,independent_mathematical_verification=False,target_resolution='UNKNOWN')
    with (out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(claim_population=282,new_candidate=1,new_verified=0)))
if __name__=='__main__':main()
