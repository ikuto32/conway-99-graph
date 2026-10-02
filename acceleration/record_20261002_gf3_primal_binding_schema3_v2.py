"""Editorial schema3 correction of an unregistered GF3 r1 binding; preserve v1."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261002_independent_review/gf3_full_artifact01'
OLD=BASE+'/claim_binding.json'
OLD_SHA='2325194ff1ea911d060a2b0c2a62a4786bc72e2b2ecf3670815adaf671adb7c0'
PACKAGE='acceleration/results/20261002_wave33_model_package01/manifest.json'
PACKAGE_SHA='c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145'
RECOVERY='acceleration/results/20261002_independent_review/wave33_model_recovery01/summary.json'
RECOVERY_SHA='b9352a5e5810f20ff9187c06f5e00636f2f3abad2810ed3d7c23df655b76f583'


def sha(path):
    with(ROOT/path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    assert sha(OLD)==OLD_SHA
    binding=json.loads((ROOT/OLD).read_bytes());original_statement=binding['statement']
    scope=binding['scope'];binding['profile_population']=scope['profile_population'];binding['prism_free_target_interpretation']=scope['prism_free_target_interpretation']
    binding['scope']={k:scope[k]for k in ['description','unrestricted_target','target_resolution']}
    binding['shared_components']=binding['verification']['shared_components']
    pins=binding['inputs_sha256'];calibration=binding['pre_output_calibration']['path'];cal=json.loads((ROOT/calibration).read_bytes())
    assert sha(calibration)==binding['pre_output_calibration']['sha256']
    for path,wanted in cal['inputs_sha256'].items():
        assert sha(path)==wanted,path
        assert path not in pins or pins[path]==wanted
        pins[path]=wanted
    assert sha(PACKAGE)==PACKAGE_SHA and sha(RECOVERY)==RECOVERY_SHA
    package=json.loads((ROOT/PACKAGE).read_bytes());recovery=json.loads((ROOT/RECOVERY).read_bytes())
    assert recovery['status']=='INDEPENDENT_WAVE33_FOUR_LITERAL_MODELS_RAW_RECOVERY_PASS'
    pins[PACKAGE]=PACKAGE_SHA;pins[RECOVERY]=RECOVERY_SHA
    for path,wanted in recovery['inputs_sha256'].items():
        assert sha(path)==wanted,path
        assert path not in pins or pins[path]==wanted
        pins[path]=wanted
    binding['raw_model_recovery']=dict(raw_path=binding['normalization']['raw_model'],raw_sha256=binding['normalization']['raw_model_sha256'],raw_bytes=57414699,committed_raw=False,package_manifest=PACKAGE,package_manifest_sha256=PACKAGE_SHA,independent_recovery_report=RECOVERY,independent_recovery_report_sha256=RECOVERY_SHA,availability='PUBLIC',retrieval='Use the unchanged recovery CLI and exact argv in the pinned independent report, with package/parts at repositorycommit cfef855d7cec5b42a2508e664ff8308270814756. Authenticate every compressed/raw part; no new public network replay is asserted by this metadata correction.')
    binding['artifacts']=[dict(path=path,sha256=digest,availability='LOCAL_ONLY',retrieval='Current shared checkout; separate publication/recovery closure determines public status.')for path,digest in pins.items()]
    binding['editorial_correction']=dict(preserved_original_binding=OLD,preserved_original_binding_sha256=OLD_SHA,reason='Before registration, match schema3 exactly: three scope keys, top-level shared_components, complete pre-output-calibration input closure, and existing public lossless raw-model recovery metadata. Statement/revision and verification report unchanged.',previous_binding_promoted=False,statement_unchanged=True)
    binding['updated_at']=datetime.now(timezone.utc).isoformat();assert binding['statement']==original_statement
    path=ROOT/BASE/'claim_binding_schema3.json'
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(binding,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(id=binding['id'],revision=1,path=path.relative_to(ROOT).as_posix(),sha256=sha(path.relative_to(ROOT)),original_preserved_sha256=OLD_SHA)))


if __name__=='__main__':main()
