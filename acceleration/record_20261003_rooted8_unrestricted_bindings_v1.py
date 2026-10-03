"""Bind independently checked rooted8 revisions; metadata only, no ledger writes."""
import argparse,hashlib,json,platform,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261003_independent_review/'
CAT=BASE+'rooted8_unrestricted_catalogue01/'
MODEL=BASE+'rooted8_unrestricted_model01/'
RAW='acceleration/results/20261003_rooted8_unrestricted_extension01/'
PROOF='acceleration/audit_20261003_rooted8_unrestricted_model_proof_v1.md'
CID='C-UNRESTRICTED-ROOTED8-NONEDGE-LOCAL-CATALOGUE-COVERAGE'
MID='C-UNRESTRICTED-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING'
def need(ok,why):
    if not ok:raise ValueError(why)
def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Exact two-rooted8 schema2 independent bindings, raw/source/calibration/receipt hashes; metadata only100seconds20reserve')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'bounded metadata output');out.mkdir(parents=True,exist_ok=False);pins={}
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'not completed within the allocated budget')
    def pin(name,identity=None):
        tick();actual=digest(ROOT/name);need(identity is None or actual==identity,'exact immutable input '+name);need(name not in pins or pins[name]==actual,'consistent repeated identity');pins[name]=actual
    def read(name):return json.loads((ROOT/name).read_bytes())
    reports=[]
    for name,identity,status in [(CAT+'summary.json','1cf70d9caed5235bcce437fbc57280a0778c1f9a6cd9d628766de586516f9a6a','INDEPENDENT_COMPLETE_UNRESTRICTED_ROOTED8_CATALOGUE_PASS'),(MODEL+'summary.json','ec5073a22027c512e29dac1d49048a507f272cb8ce1a0a79d2ca1f663f1be974','INDEPENDENT_UNRESTRICTED_ROOTED8_MARKED_UNIVERSAL5_PRODUCT_MODEL_PASS')]:
        pin(name,identity);report=read(name);need(report['status']==status and report['producer']=='/root/structural' and report['verifier']=='/root/checkpoint_audit','exact independent checking role/status');reports.append(report)
        for path,value in report['inputs_sha256'].items():pin(path,value)
    cat,model=reports
    need((cat['parent_classes'],cat['labelled_augmentation_attempts'],cat['locally_admissible_extensions'],cat['complete_unrestricted_rooted_classes'],cat['exact_labelled_image_checks'])==(2770,354560,134594,20524,14777280),'exact complete coverage population')
    need(cat['prism_filter_applied'] is False and cat['new_exclusions']==0 and cat['target_resolution'] is False,'unrestricted nonresolution scope')
    need((model['variables'],model['rows'],model['nonzeros'],model['inherited_rows'],model['marked_extension_rows'],model['upper_pair_product_rows'])==(23334,86434,985893,11769,70837,3828),'exact complete operator dimensions')
    need((model['free_deletions_checked'],model['every_lower_isomorphism_checks'])==(123144,4838942) and model['target_resolution'] is False and model['graph_realizability_asserted'] is False,'exact full independent transport scope')
    pin(MODEL+'reconstructed_rows.json','033778d196dcf7d21f76b2460018944b291c1b34b38602ce9f66c24e198dbd70')
    pin(PROOF,'f14c53a486bf6db35664e381937911d770939cc436e86618af0ab61beefb9dc7')
    frozen='acceleration/results/20261003_wave36_milestone01/CLAIMS.yaml';pin(frozen,'8f8d39f5e4fcaf8cb8ec2681e0a9ec795439c80e2c8bd1d8a5903ef1087d342d')
    ledger=yaml.safe_load((ROOT/frozen).read_text());claims={c['id']:c for c in ledger['claims']}
    dependencies=[('C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE','coverage'),('C-UNRESTRICTED-ROOTED7-MARKED-REROOT-MEAN-NECESSARY-ENCODING','uses_result'),('C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY','uses_result')]
    for cid,relation in dependencies:need(claims[cid]['revision']==1 and claims[cid]['status']=='VERIFIED' and claims[cid]['review_state']=='CLEAR','actual pinned dependency revision '+cid)
    # Direct producing/checking closure only, not a wholesale transitive archive
    # migration. Raw hashing authenticates already checked bytes, not mathematics.
    manifest=read(RAW+'manifest.json')
    for name,identity in manifest['inputs_sha256'].items():pin(name,identity)
    roots=[RAW.rstrip('/'),BASE+'rooted8_unrestricted_calibration01',BASE+'rooted8_unrestricted_calibration02',BASE+'rooted8_unrestricted_calibration_supervision01',BASE+'rooted8_unrestricted_calibration_supervision02',BASE+'rooted8_unrestricted_catalogue_calibration01',BASE+'rooted8_unrestricted_catalogue_calibration_supervision01',BASE+'rooted8_unrestricted_catalogue_supervision01',BASE+'rooted8_unrestricted_model_supervision01','acceleration/results/20261003_rooted8_unrestricted_precontrols01','acceleration/results/20261003_rooted8_unrestricted_precontrols02','acceleration/results/20261003_rooted8_unrestricted_precontrols_supervisor01','acceleration/results/20261003_rooted8_unrestricted_precontrols_supervisor02','acceleration/results/20261003_rooted8_unrestricted_build_supervisor01']
    for directory in roots:
        need((ROOT/directory).is_dir(),'actual completed/failure closure '+directory)
        for file in sorted((ROOT/directory).rglob('*')):
            if file.is_file():pin(file.relative_to(ROOT).as_posix())
    for directory in ('rooted8_unrestricted_catalogue01','rooted8_unrestricted_model01'):
        for file in sorted((ROOT/BASE/directory).iterdir()):
            if file.is_file():pin(file.relative_to(ROOT).as_posix())
    for name in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),'acceleration/theory_20261003_rooted8_unrestricted_extension_v1.py','docs/PROTOCOL_20261003_UNRESTRICTED_ROOTED8_V1.md','acceleration/audit_20261003_rooted8_unrestricted_model_v1.py','acceleration/audit_20261003_rooted8_unrestricted_model_v1_spec.md',PROOF]:pin(name)
    terminal=[]
    for name in (BASE+'rooted8_unrestricted_catalogue_supervision01/summary.json',BASE+'rooted8_unrestricted_model_supervision01/summary.json','acceleration/results/20261003_rooted8_unrestricted_build_supervisor01/summary.json'):
        receipt=read(name);need(receipt['command_exit_code']==0 and receipt['cleanup']['reaped'] is True and receipt['cleanup']['job_active_zero_observed'] is True,'actual complete contained invocation '+name);terminal.append({'path':name,'sha256':pins[name],'elapsed_seconds':receipt['elapsed_seconds'],'exit_code':0,'reaped':True,'job_empty':True})
    now=datetime.now(timezone.utc).isoformat();common={'binding_schema_version':2,'revision':1,'claim_revision':1,'kind':'encoding','basis':['DERIVED','COMPUTED'],'status':'VERIFIED','review_state':'CLEAR','producer':'/root/structural','verifier':'/root/checkpoint_audit','created_at':now,'updated_at':now,'inputs_sha256':dict(sorted(pins.items())),'shared_components':model['shared_components'],'artifact_availability':'LOCAL_ONLY for new evidence; older pinned inputs retain their separately recorded availability.','retrieval':'Exact workspace paths and commands in hash-bound run/audit records. Raw new model/reconstruction need lossless packaging and independent recovery before PUBLIC promotion.','external_review':None,'external_review_null_reason':'No external review of these newly bound revisions is recorded.','limitations':['Necessary finite count encoding/catalogue only; no target graph, general nonexistence proof, profile exclusion, optimizer outcome or graph realization.','Pinned independent rooted5/rooted6/rooted7 results are reused; full historical transitive archive is not freshly replayed.','Positive fixture calibration does not replace complete catalogue/operator checking; both exact full reports are separately bound.','New raw model59358049bytes and independently reconstructed rows65506677bytes remain LOCAL_ONLY pending separate lossless package/recovery/publication checking.','Failed producerV1 precontrols and independent checkerV1 support-count failure are preserved as original bytes and receipts; neither is a mathematical refutation.']}
    bindings=[]
    coverage={**common,'id':CID,'statement':cat['statement'],'scope':{'description':'Exact complete finite ordered-nonedge rooted8 local-cap catalogue:20524classes from every2770root7 parent and128neighborhoods, retaining all qualifying prisms; free-label coordinates assume no target automorphism.','unrestricted_target':True,'target_resolution':'NONE'},'assumptions':['Finite simple rooted8 graphs have fixed ordered nonadjacent roots and adjacent/nonadjacent common-neighbor caps1/2.','The pinned prior rooted7 catalogue covers every qualifying seven-vertex deletion.','Only permutations of the six free labels define coordinates; no target graph automorphism or prism absence is assumed.'],'dependencies':[{'id':dependencies[0][0],'revision':1,'relation':'coverage'}],'method':'independent_artifact_check','verification_timestamp':cat['timestamp'],'report':CAT+'summary.json','report_sha256':pins[CAT+'summary.json'],'source_commit':cat['source_commit'],'command':cat['command'],'cwd':cat['cwd'],'python':cat['python'],'controls':{'finite':cat['controls'],'actual_complete_artifact':cat['actual_omission_controls']},'written_coverage_context':{'path':PROOF,'sha256':pins[PROOF],'role':'Coverage induction is explained as checking context; recorded method remains independent complete artifact checking.'}}
    encoding={**common,'id':MID,'statement':model['statement'],'scope':{'description':model['scope'],'unrestricted_target':True,'target_resolution':'NONE'},'assumptions':['A hypothetical complete SRG(99,14,1,2) supplies nonnegative integer flag counts at every actual ordered nonedge.','The separately verified unrestricted rooted7 prefix, rooted6 three-parameter affine count profile and universal rooted5 counts are necessary; these results are reused by exact pins.','Primary(c,a,b) and inherited secondary edge/nonedge profiles vary by their actual pairs; no prism-free premise, uniformity, fixed witness or target automorphism is used.'],'dependencies':[{'id':dependencies[1][0],'revision':1,'relation':'uses_result'},{'id':dependencies[2][0],'revision':1,'relation':'uses_result'},{'id':CID,'revision':1,'relation':'coverage'}],'method':'independent_derivation','verification_timestamp':model['timestamp'],'report':MODEL+'summary.json','report_sha256':pins[MODEL+'summary.json'],'source_commit':model['source_commit'],'command':model['command'],'cwd':model['cwd'],'python':model['python'],'controls':{'finite':model['controls'],'actual_complete_artifact':model['raw_corruption_controls']},'written_proof':{'path':PROOF,'sha256':pins[PROOF],'role':'Independent marked double count/orbit transport and ordered-union product necessity derivation; report bytes unchanged.'}}
    for directory,binding in ((CAT,coverage),(MODEL,encoding)):
        path=directory+'claim_binding_schema2.json';save(ROOT/path,binding);bindings.append({'id':binding['id'],'revision':1,'path':path,'sha256':digest(ROOT/path),'status':'VERIFIED','scope':binding['scope'],'method':binding['method'],'report_sha256':binding['report_sha256']})
    save(out/'summary.json',{'status':'EXACT_UNRESTRICTED_ROOTED8_TWO_SCHEMA2_BINDINGS_RECORDED','timestamp':now,'source_sha256':pins[Path(__file__).relative_to(ROOT).as_posix()],'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'inputs_sha256':pins,'bindings':bindings,'terminal_records':terminal,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'ledger_mutated':False,'index_mutated':False,'mathematical_replay':False,'new_exclusions':0,'target_resolution':'UNKNOWN','elapsed_seconds':time.monotonic()-start,'deadline':deadline.status()})
    print(json.dumps({'status':'EXACT_UNRESTRICTED_ROOTED8_TWO_SCHEMA2_BINDINGS_RECORDED','summary_sha256':digest(out/'summary.json'),'bindings':bindings,'elapsed_seconds':time.monotonic()-start}))

if __name__=='__main__':main()
