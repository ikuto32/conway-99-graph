"""Editorial schema correction of completed finite engineering r1 binding."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261002_independent_review/weight60_controls01'
ORIGINAL=BASE+'/claim_binding.json'
ORIGINAL_SHA='3218c24c1ec41da1495b33585ad87ccbf658f4ce923c57d744b26473a84574be'


def sha(name):
    with(ROOT/name).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    assert sha(ORIGINAL)==ORIGINAL_SHA
    binding=json.loads((ROOT/ORIGINAL).read_bytes());old=binding['shared_components'];assert type(old)is dict and len(old)==2
    binding['shared_component_hashes']=old
    binding['shared_components']=[f'Pinned prior independently authored helper {name}; SHA256 {digest}; code reuse disclosed, no old execution approval transfer.'for name,digest in sorted(old.items())]
    binding['updated_at']=datetime.now(timezone.utc).isoformat()
    binding['editorial_schema_correction']=dict(original=ORIGINAL,original_sha256=ORIGINAL_SHA,statement_changed=False,claim_revision_changed=False,scope_changed=False,reason='Registrar requires shared_components array; original dict retained under shared_component_hashes and unchanged inputs_sha256. Failed registration left authoritative ledger unchanged.')
    for name in[ORIGINAL,Path(__file__).relative_to(ROOT).as_posix(),'acceleration/results/20261003_wave36_registration_supervision01/manifest.json','acceleration/results/20261003_wave36_registration_supervision01/summary.json']:binding['inputs_sha256'][name]=sha(name)
    for name,digest in binding['inputs_sha256'].items():assert sha(name)==digest,name
    assert binding['revision']==binding['claim_revision']==1 and set(binding['scope'])=={'description','unrestricted_target','target_resolution'}
    path=ROOT/BASE/'claim_binding_schema2.json'
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path.relative_to(ROOT).as_posix()),id=binding['id'],revision=1)))


if __name__=='__main__':main()
