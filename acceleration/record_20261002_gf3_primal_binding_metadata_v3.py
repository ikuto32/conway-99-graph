"""Finalize unregistered r1 schema projection with immutable writer provenance."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261002_independent_review/gf3_full_artifact01'
SOURCE=BASE+'/claim_binding_schema3.json'
EXPECTED='12b37fc32578dbc6162c3b2a3978e88c9bf124731dfc0a723b73b040f29c224b'


def sha(path):
    with(ROOT/path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    assert sha(SOURCE)==EXPECTED
    binding=json.loads((ROOT/SOURCE).read_bytes());pins=binding['inputs_sha256']
    paths=[SOURCE,binding['editorial_correction']['preserved_original_binding'],
      'acceleration/record_20261002_gf3_primal_binding_v1.py',
      'acceleration/record_20261002_gf3_primal_binding_schema3_v2.py',
      Path(__file__).relative_to(ROOT).as_posix(),
      'acceleration/results/20261002_independent_review/gf3_primal_binding_supervision01/manifest.json',
      'acceleration/results/20261002_independent_review/gf3_primal_binding_supervision01/summary.json',
      'acceleration/results/20261002_independent_review/gf3_primal_binding_schema3_supervision01/manifest.json',
      'acceleration/results/20261002_independent_review/gf3_primal_binding_schema3_supervision01/summary.json']
    provenance=[]
    for path in paths:
        digest=sha(path);assert path not in pins or pins[path]==digest;pins[path]=digest;provenance.append(dict(path=path,sha256=digest))
    binding['binding_construction_provenance']=dict(editorial_only=True,prior_intermediate_binding=SOURCE,prior_intermediate_binding_sha256=EXPECTED,writer_sources_and_completed_receipts=provenance,statement_and_revision_unchanged=True)
    binding['artifacts']=[dict(path=path,sha256=digest,availability='LOCAL_ONLY',retrieval='Current shared checkout; separate publication/recovery closure determines public status.')for path,digest in pins.items()]
    assert set(binding['scope'])=={'description','unrestricted_target','target_resolution'}and binding['shared_components']
    path=ROOT/BASE/'claim_binding_v2.json'
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(id=binding['id'],revision=1,path=path.relative_to(ROOT).as_posix(),sha256=sha(path.relative_to(ROOT)),original_preserved_sha256=binding['editorial_correction']['preserved_original_binding_sha256'])))


if __name__=='__main__':main()
