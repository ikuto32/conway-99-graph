"""Freeze an explicit authenticated Wave36 evidence allowlist; no Git mutation.

No broad worktree search or source/result mutation. Exact new ledger artifacts,
frozen native allowlist and named completed roots only. Not mathematical review.
"""
import argparse, copy, hashlib, json, platform, subprocess, sys, time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import yaml
from command_deadline import CommandDeadline
from audit_20261002_wave31_transition_v1 import UniqueLoader
ROOT=Path(__file__).resolve().parents[1]
START='4b7470f6e2bd183d355a2247e28a354159681f0b12c10fcb90181bff94e91ea5'
ENGINE_ALLOW='acceleration/results/20261002_hypergraph_weight60_allowlist01/manifest.json'
ENGINE_ALLOW_SHA='646221ca457727c33938df90585ebf9ae1c80d858bdb12a9108085bd80c15372'
MODEL_BIND='acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/claim_binding.json'
LP_BIND='acceleration/results/20261003_independent_review/rooted7_unrestricted_lp01/claim_binding.json'
ANCHORS={ENGINE_ALLOW:ENGINE_ALLOW_SHA,MODEL_BIND:'107ac82be6212129f8d98056a4c640ee64e2557238b11465edb91535076cb727',LP_BIND:'e8d9f598e3d9dad746ec890cabf0ad5ce07a6a048fd1929c5bdeecad1ed438f6',
 'acceleration/results/20261002_independent_review/weight60_controls01/summary.json':'05a8c1e5b0d2df3d937cd1ab47961b17ff37ec2f3d9952a5db0feaf5178ac9f3',
 'acceleration/results/20261003_independent_review/weight60_saved_calibration03/summary.json':'660e4c420fa7f3f35f8c7291a4100931a7881237f0112c42428d6df9fa1baa07',
 'acceleration/freeze_20261002_hypergraph_weight60_pilot_plan_v1.py':'7fb5d9a6f7f2ada79626f3c60c96d88ef52e3ec547e7ce81b6173dfb67c03f0c',
 'acceleration/freeze_20261002_hypergraph_weight60_pilot_plan_v1_spec.md':'e78deb4d7fd753148b1f338e3eddc8acc78fea7d57f04a47b7c5ccd17445e9a0',
 'acceleration/plan_20261003_weight60_launch_protocol_v1.json':'39792fce219170be2484244c48eae298b0dd0ed03f47173f10e365ee88084337',
 'acceleration/results/20261003_wave35_public_confirmation01/receipt.json':'0137ee22ef26c4a8b21c54910187168dfe7fed5177b947737c80b96425a86246',
 'acceleration/results/20261003_independent_review/wave35_availability01/summary.json':'9abecafe6d14018cac5f70d5046ff11667defc387dab8c3a1709896fdf50bedd'}
PACKAGE='acceleration/results/20261002_wave33_model_package01/manifest.json'
PACKAGE_SHA='c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145'
CHECKPOINT='acceleration/results/20261002_rooted8_gf3_solve01/solve/checkpoint.bin'
CHECKPOINT_SHA='c2c13e6e83079264344f9610ba31ebe254544b501d9b95e9cafea9ff2d66b0b8'
CENSUS='acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/srg243_all_primary_coupling_records.json'
CENSUS_SHA='447d922b1a0ad28b3b7d459f84b8c02e55da7b9cc8da8615a5e882b6482d4919'
COMPLETED_ROOTS=[
 'acceleration/results/20261002_hypergraph_weight60_allowlist01',
 'acceleration/results/20261002_hypergraph_weight60_allowlist_supervision01',
 *['acceleration/results/20261002_independent_review/'+x for x in ('weight60_controls01','weight60_controls_supervisor01','weight60_scalar_calibration01','weight60_scalar_calibration_supervisor01')],
 *['acceleration/results/20261003_independent_review/'+x for x in ('weight60_binding_supervisor01','weight60_binding_schema_supervisor01','weight60_saved_calibration01','weight60_saved_calibration02','weight60_saved_calibration03','weight60_saved_calibration_supervisor01','weight60_saved_calibration_supervisor02','weight60_saved_calibration_supervisor03')],
 *['acceleration/results/'+x for x in ('20261002_rooted7_unrestricted_corner_calibration_supervisor01','20261002_rooted7_unrestricted_corner_calibration01','20261002_rooted7_unrestricted_corner_source_supervisor01','20261002_rooted7_unrestricted_corner_source_supervisor02','20261002_rooted7_unrestricted_corners_supervisor01','20261002_rooted7_unrestricted_corners01','20261002_rooted7_unrestricted_extension_supervisor01','20261002_rooted7_unrestricted_extension01','20261002_rooted7_unrestricted_source_preflight01')],
 *['acceleration/results/20261002_independent_review/'+x for x in ('rooted7_unrestricted_binding_supervision01','rooted7_unrestricted_model_supervision01','rooted7_unrestricted_model01')],
 *['acceleration/results/20261003_independent_review/'+x for x in ('rooted7_unrestricted_lp_binding_supervision01','rooted7_unrestricted_lp_calibration_supervision01','rooted7_unrestricted_lp_calibration_supervision02','rooted7_unrestricted_lp_calibration01','rooted7_unrestricted_lp_calibration02','rooted7_unrestricted_lp_supervision01','rooted7_unrestricted_lp01','wave35_availability_supervision01','wave35_availability01')],
 'acceleration/results/20261003_wave35_public_confirmation01',
 'acceleration/results/20261003_wave35_public_confirmation_supervision01',
 'acceleration/results/20261003_wave36_registration01',
 'acceleration/results/20261003_wave36_registration_supervision01',
 'acceleration/results/20261003_wave36_allowlist01',
 'acceleration/results/20261003_wave36_allowlist_supervision01']
SOURCES=[
 'acceleration/audit_20261003_weight60_saved_objects_v1.py','acceleration/audit_20261003_weight60_saved_objects_v1_spec.md',
 'acceleration/audit_20261003_weight60_saved_objects_v2.py','acceleration/audit_20261003_weight60_saved_objects_v2_spec.md',
 'acceleration/audit_20261003_weight60_saved_objects_v3.py','acceleration/audit_20261003_weight60_saved_objects_v3_spec.md',
 'acceleration/audit_20261003_wave35_availability_v1.py','acceleration/audit_20261003_wave35_availability_v1_spec.md',
 'acceleration/confirm_20261003_wave35_publication_v1.py','acceleration/confirm_20261003_wave35_publication_v1_spec.md',
 'acceleration/record_20261003_weight60_engineering_binding_v1.py',
 'acceleration/record_20261003_weight60_binding_schema2_v2.py',
 'acceleration/register_20261002_bound_claims_v9.py',
 'acceleration/record_20261003_rooted7_unrestricted_lp_binding_v1.py',
 'acceleration/audit_20261003_rooted7_unrestricted_lp_v1.py','acceleration/audit_20261003_rooted7_unrestricted_lp_v1_spec.md','acceleration/audit_20261003_rooted7_unrestricted_lp_v1_proof.md',
 'acceleration/audit_20261003_rooted7_unrestricted_lp_v2.py','acceleration/audit_20261003_rooted7_unrestricted_lp_v2_spec.md','acceleration/audit_20261003_rooted7_unrestricted_lp_v2_proof.md',
 'acceleration/record_20261002_rooted7_unrestricted_binding_v1.py',
 'acceleration/theory_20261002_rooted7_unrestricted_extension_v1.py','docs/PROTOCOL_20261002_UNRESTRICTED_ROOTED7_EXTENSION_V1.md',
 'acceleration/theory_20261002_rooted7_unrestricted_corners_v1.py','docs/PROTOCOL_20261002_UNRESTRICTED_ROOTED7_CORNERS_V1.md',
 'acceleration/theory_20261002_rooted7_unrestricted_corners_v3.py','docs/PROTOCOL_20261002_UNRESTRICTED_ROOTED7_CORNERS_V3.md','docs/PROTOCOL_20261002_UNRESTRICTED_ROOTED7_CORNERS_V2.md',
 'acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/compute_policy.json','docs/COMPUTE_POLICY.md','pyproject.toml','uv.lock',
 'acceleration/audit_20261002_wave31_transition_v1.py']
SOURCES+=['acceleration/freeze_20261003_wave36_evidence_v1.py','acceleration/freeze_20261003_wave36_evidence_v1_spec.md']
class FreezeError(ValueError):
    def __init__(self,stage):self.stage=stage;super().__init__(stage)
def need(ok,stage):
    if not ok:raise FreezeError(stage)
def path(name):
    need(type(name) is str and bool(name) and '\\' not in name and '\n' not in name and '\r' not in name and '\0' not in name,'LITERAL_RELATIVE_PATH')
    pp=PurePosixPath(name);need(not pp.is_absolute() and '..' not in pp.parts and not(name.startswith('.git/')),'BOUNDED_REPOSITORY_PATH')
    need(name.startswith(('acceleration/','docs/')) or name in ('CLAIMS.yaml','README.md','ACTIVE_RESEARCH.md','pyproject.toml','uv.lock','.gitattributes','.github/workflows/claims.yml'),'RESEARCH_NAMESPACE')
    p=(ROOT/name).resolve();need(p.is_relative_to(ROOT),'RESOLVED_WORKSPACE_PATH');return p
def sha(p):
    with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as s:json.dump(x,s,indent=2,sort_keys=True);s.write('\n')
def controls():
    result=[]
    for bad,stage in [('../outside','BOUNDED_REPOSITORY_PATH'),('/absolute','BOUNDED_REPOSITORY_PATH'),('acceleration/../../outside','BOUNDED_REPOSITORY_PATH'),('acceleration/line\nname','LITERAL_RELATIVE_PATH'),('acceleration\\mixed','LITERAL_RELATIVE_PATH'),('private.txt','RESEARCH_NAMESPACE'),('.git/config','BOUNDED_REPOSITORY_PATH')]:
        try:path(bad)
        except FreezeError as e:need(e.stage==stage,'CONTROL_WRONG_STAGE');result.append(dict(path=bad,expected=stage,outcome=e.stage))
        else:raise FreezeError('CONTROL_FALSE_ACCEPT')
    need(path('acceleration/command_deadline.py').is_file(),'POSITIVE_PATH_CONTROL');return result
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--ledger-sha256',required=True);ap.add_argument('--registration-summary',required=True);ap.add_argument('--registration-summary-sha256',required=True)
    ap.add_argument('--engine-binding',required=True);ap.add_argument('--engine-binding-sha256',required=True);ap.add_argument('--extra',action='append',default=[])
    ap.add_argument('--census-package',required=True);ap.add_argument('--census-package-sha256',required=True);ap.add_argument('--census-recovery',required=True);ap.add_argument('--census-recovery-sha256',required=True)
    args=ap.parse_args();start=time.monotonic();d=CommandDeadline(args.seconds,allocation_reason='Exact incremental337ledger/weight60finite+saved/model+LP/publication closures only;~100MiB/direct~2000paths vs51MiB frozen1460 engineeringrecords;240outer200worker20reserve,no science or index mutation')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'BOUNDED_OUTPUT');out.mkdir(parents=True,exist_ok=False);expected={};origins=defaultdict(set);pins={}
    tick=lambda:need(d.status()['remaining_seconds']>20 and not d.status()['stop_required'],'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET')
    def add(name,why,wanted=None):
        path(name);origins[name].add(why)
        if wanted is not None:need(name not in expected or expected[name]==wanted,'CONFLICTING_PINNED_IDENTITY');expected[name]=wanted
    def pin(name,wanted=None):
        tick();p=path(name);need(p.is_file(),'EXACT_INPUT_EXISTS');identity=sha(p);need(wanted is None or identity==wanted,'EXACT_INPUT_HASH');pins[name]=identity;add(name,'authenticated_anchor',identity);return identity
    def read(name,wanted=None):pin(name,wanted);return json.loads(path(name).read_bytes())
    def ledger(name,wanted):pin(name,wanted);return yaml.load(path(name).read_text(encoding='utf8'),Loader=UniqueLoader)
    def named_root(name,why):
        p=path(name);need(p.is_dir(),'EXPLICIT_COMPLETED_ROOT_EXISTS');found=[]
        for member in p.rglob('*'):
            if member.is_file():
                item=member.relative_to(ROOT).as_posix();add(item,why);found.append(item)
        return {'path':name,'files':len(found),'paths':sorted(found)}
    try:
        controls_record=controls();source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        git_index=Path(subprocess.check_output(['git','rev-parse','--git-path','index'],cwd=ROOT,text=True).strip());git_index=git_index if git_index.is_absolute() else ROOT/git_index;index_before=sha(git_index)
        summary=read(args.registration_summary,args.registration_summary_sha256);need(summary['before_ledger_sha256']==START and summary['ledger_sha256']==args.ledger_sha256 and summary['mathematical_replays']==0,'FROZEN_REGISTRATION_CHAIN')
        regparent=path(args.registration_summary).parent;reg_before=(regparent/'CLAIMS.before.yaml').relative_to(ROOT).as_posix();reg_after=(regparent/'CLAIMS.after.yaml').relative_to(ROOT).as_posix()
        before=ledger(reg_before,START);current=ledger(reg_after,args.ledger_sha256);live=ledger('CLAIMS.yaml',args.ledger_sha256)
        need(current==live and len(before['claims'])==334 and len(current['claims'])==337,'EXACT_INCREMENTAL_CLAIM_POPULATION')
        old_claims={c['id']:c for c in before['claims']};new_claims={c['id']:c for c in current['claims']};need(all(new_claims[k]==v for k,v in old_claims.items()),'BASELINE_CLAIMS_UNCHANGED')
        old={a['id']:a for a in before['artifacts']};new={a['id']:a for a in current['artifacts']};need(all(new[k]==v for k,v in old.items()),'BASELINE_ARTIFACTS_UNCHANGED')
        for aid,a in new.items():
            if aid not in old and a['path']:add(a['path'],'new_registered_artifact',a['sha256'])
        for name,wanted in ANCHORS.items():pin(name,wanted)
        bind=read(args.engine_binding,args.engine_binding_sha256);need(bind['id']=='C-HYPERGRAPH-WEIGHT60-EXCLUSIVE-SWAP-V2-FINITE-ENGINEERING-CONTROLS' and bind['revision']==1,'FROZEN_ENGINE_BINDING')
        for name in [MODEL_BIND,LP_BIND,args.engine_binding,ENGINE_ALLOW]:
            raw=json.loads(path(name).read_bytes())
            for key in ('inputs_sha256','outputs_sha256'):
                for p,wanted in raw.get(key,{}).items():
                    normalized=p if p.startswith(('acceleration/','docs/')) or p in ('pyproject.toml','uv.lock') else str(PurePosixPath(name).parent/p)
                    add(normalized,'binding_or_manifest_direct_closure',wanted)
            for record in raw.get('artifacts',[]):
                if type(record) is dict and 'path' in record:add(record['path'],'binding_direct_artifact',record['sha256'])
        for gate in ['acceleration/results/20261002_independent_review/weight60_controls01/summary.json','acceleration/results/20261003_independent_review/weight60_saved_calibration03/summary.json']:
            raw=read(gate,ANCHORS[gate])
            for p,wanted in raw['inputs_sha256'].items():add(p,'independent_finite_or_saved_gate_closure',wanted)
            for p,wanted in raw.get('outputs_sha256',{}).items():add(p if p.startswith('acceleration/') else str(PurePosixPath(gate).parent/p),'independent_gate_output',wanted)
        native=json.loads(path(ENGINE_ALLOW).read_bytes());need(native['schema']=='WEIGHT60_ENGINEERING_EXACT_STAGING_ALLOWLIST_V1' and native['hashed_records']==1460 and native['stage_paths_count']==1462 and len(native['records'])==1460,'EXACT_NATIVE_ALLOWLIST_POPULATION')
        native_names=[r['path'] for r in native['records']]
        need(len(set(native_names))==1460,'UNIQUE_NATIVE_RECORDS')
        for r in native['records']:add(r['path'],'frozen_native_engineering_allowlist',r['sha256'])
        stage_nul=str(PurePosixPath(ENGINE_ALLOW).parent/'stage_paths.nul');pin(stage_nul,native['stage_paths_sha256'])
        need(path(stage_nul).read_bytes().split(b'\0')[:-1]==[p.encode('utf8') for p in sorted(native_names+native['self_metadata_paths'])],'EXACT_NATIVE_PATH_LIST')
        need(path(stage_nul).read_bytes().endswith(b'\0'),'NUL_TERMINATED_NATIVE_PATH_LIST')
        package=read(PACKAGE,PACKAGE_SHA);public_raw={r['raw_path']:r for r in package['records']}
        census_package=read(args.census_package,args.census_package_sha256);need(len(census_package['records'])==1,'EXACT_CENSUS_PACKAGE_POPULATION')
        census_row=census_package['records'][0];need(census_row['raw_path']==CENSUS and census_row['raw_sha256']==CENSUS_SHA and census_row['raw_bytes']==57902243,'EXACT_CENSUS_PACKAGE_IDENTITY')
        census_recovery=read(args.census_recovery,args.census_recovery_sha256)
        need(census_recovery['status']=='INDEPENDENT_WAVE36_SRG243_COUPLING_CENSUS_RECOVERY_V1_PASS' and census_recovery['manifest_sha256']==args.census_package_sha256 and census_recovery['originals']==1 and census_recovery['raw_bytes']==57902243 and census_recovery['records'][0]['path']==CENSUS and census_recovery['records'][0]['sha256']==CENSUS_SHA and census_recovery['records'][0]['restored_every_byte_matches'] is True,'EXACT_CENSUS_INDEPENDENT_RECOVERY')
        for part in census_row['parts']:add(part['path'],'new_lossless_census_package_payload',part['gzip_sha256'])
        for p,wanted in census_recovery['inputs_sha256'].items():
            if p!=CENSUS:add(p,'new_census_recovery_direct_closure',wanted)
        roots=[named_root(p,'explicit_completed_result_root') for p in COMPLETED_ROOTS]
        roots.append(named_root(regparent.relative_to(ROOT).as_posix(),'successful_registration_root'))
        successful_supervision=regparent.relative_to(ROOT).as_posix().replace('_registration02','_registration_supervision02')
        if successful_supervision!=regparent.relative_to(ROOT).as_posix():roots.append(named_root(successful_supervision,'successful_registration_supervision'))
        for name in SOURCES:add(name,'explicit_preserved_source')
        for name in args.extra:
            p=path(name);need(p.exists(),'EXPLICIT_EXTRA_EXISTS')
            if p.is_dir():roots.append(named_root(name,'explicit_parent_extra_root'))
            else:add(name,'explicit_parent_extra')
        for name in [Path(__file__).resolve().relative_to(ROOT).as_posix(),'acceleration/freeze_20261003_wave36_evidence_v2_spec.md']:add(name,'new_metadata_allowlist_source')
        records=[];omitted=[]
        for name in sorted(origins):
            tick();p=path(name);need(p.is_file(),'ALL_REQUESTED_MEMBERS_EXIST');size=p.stat().st_size
            if name==CHECKPOINT:
                need(size==494930751 and expected.get(name)==CHECKPOINT_SHA,'EXACT_CHECKPOINT_RECORDED_PIN_AND_SIZE')
                omitted.append(dict(path=name,sha256=CHECKPOINT_SHA,bytes=size,availability='LOCAL_ONLY',fresh_hash_checked=False,reason='Previously independently authenticated native resume checkpoint; explicitly excluded before costly read. Its recorded identity is not a new fresh byte check.'));continue
            if name==CENSUS:
                need(size==57902243 and expected.get(name)==CENSUS_SHA,'EXACT_CENSUS_RECORDED_PIN_AND_SIZE')
                omitted.append(dict(path=name,sha256=CENSUS_SHA,bytes=size,availability='LOCAL_ONLY',fresh_hash_checked=False,manifest=args.census_package,manifest_sha256=args.census_package_sha256,independent_recovery=args.census_recovery,independent_recovery_sha256=args.census_recovery_sha256,publication_ready_lossless=True,reason='New complete raw census independently restored and checked into a fresh destination; package ready for later immutable publication. Remains LOCAL_ONLY until separate public-byte confirmation; no direct raw Git blob.'));continue
            if name in public_raw:
                r=public_raw[name];need(size==r['raw_bytes'] and (name not in expected or expected[name]==r['raw_sha256']),'EXACT_PREVIOUS_PUBLIC_RAW_PIN_AND_SIZE')
                omitted.append(dict(path=name,sha256=r['raw_sha256'],bytes=size,availability='PUBLIC',fresh_hash_checked=False,manifest=PACKAGE,manifest_sha256=PACKAGE_SHA,reason='Already independently losslessly recovered public raw model; skip raw Git duplication and fresh raw read.'));continue
            need(size<50*1024**2,'BOUNDED_DIRECT_MEMBER');identity=pins.get(name) or sha(p);need(name not in expected or identity==expected[name],'EXACT_DECLARED_MEMBER_HASH');records.append(dict(path=name,sha256=identity,bytes=size,origins=sorted(origins[name])))
        need(sha(git_index)==index_before,'GIT_INDEX_UNCHANGED');need(sha(ROOT/'CLAIMS.yaml')==args.ledger_sha256,'LIVE_LEDGER_UNCHANGED')
        list_path=out/'stage_paths.nul';self_metadata=[(out/'manifest.json').relative_to(ROOT).as_posix(),list_path.relative_to(ROOT).as_posix()];stage_names=sorted({r['path'] for r in records}|set(self_metadata));list_path.write_bytes(b''.join(p.encode('utf8')+b'\0' for p in stage_names))
        save(out/'manifest.json',dict(schema='WAVE36_INCREMENTAL_EXACT_EVIDENCE_ALLOWLIST_V2',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source_commit,source_sha256=sha(Path(__file__)),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,before_ledger_sha256=START,ledger_sha256=args.ledger_sha256,previous_claims=334,current_claims=337,records=records,direct_record_count=len(records),direct_bytes=sum(r['bytes'] for r in records),omitted=omitted,explicit_completed_roots=roots,native_allowlist_records=1460,native_self_metadata_paths=2,stage_paths_sha256=sha(list_path),stage_paths_count=len(stage_names),self_metadata_paths=self_metadata,controls=controls_record,index_sha256_before=index_before,index_sha256_after=sha(git_index),index_mutated=False,ledger_mutated=False,scientific_launched=False,mathematical_replay=False,availability_changed=False,independent_mathematical_approval=False,resource_policy='Per invocation;240outer200worker20internal reserve; no large native checkpoints/rawmodels read.',elapsed_seconds=time.monotonic()-start,deadline=d.status(),limitations=['Only declared exact new artifact closures, frozen native allowlist and named completed roots; no broad historical/untracked inclusion.','This is metadata allowlisting only; root owns Git index/commit/publication.','Omitted checkpoint/public raw model identities are inherited pinned identities and exact sizes, not fresh full hash checks.','All original failures and source versions retained in named closed roots.','V1 stopped at its declared50MiB direct member bound; the new57,902,243-byte census is independently losslessly packaged in V2, with no threshold relaxation.','New census package has complete independent byte recovery, but no PUBLIC availability assertion before separate immutable publication confirmation.','Claims require separate read-only impact audit; publication requires independent immutable public-byte confirmation.']))
        print(json.dumps(dict(manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),sha256=sha(out/'manifest.json'),direct_records=len(records),direct_bytes=sum(r['bytes'] for r in records),omitted=len(omitted),index_mutated=False)),flush=True)
    except BaseException as e:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),error=repr(e),stage=getattr(e,'stage',None),inputs_sha256=pins,elapsed_seconds=time.monotonic()-start,outputs_preserved=True,index_mutated=False,ledger_mutated=False));raise
if __name__=='__main__':main()
