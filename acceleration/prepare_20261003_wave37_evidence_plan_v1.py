"""Explicit wave37 plan and narrow raw-byte attributes; no index operation."""
import argparse,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline
from audit_20261002_wave31_transition_v1 import UniqueLoader
ROOT=Path(__file__).resolve().parents[1]
LEDGER='af2af9811e0f701648095a31ebfeaad3cd956e2d332c09cc4344bdaa3f496a90'
BASE='acceleration/results/20261003_independent_review/'
EXTRAS=[
 'README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md','.gitattributes','.github/workflows/claims.yml',
 'docs/RESEARCH_20261003_THIRTYSEVENTH_WAVE.md','docs/REPLAY_20261003_WAVE37_UNRESTRICTED_ROOTED8.md','docs/AUDIT_20261003_WAVE36_PUBLICATION_CONFIRMED.md',
 'acceleration/freeze_20261003_wave37_evidence_v1.py','acceleration/freeze_20261003_wave37_evidence_v1_spec.md','acceleration/freeze_20261003_wave37_evidence_v2.py','acceleration/freeze_20261003_wave37_evidence_v2_spec.md',
 'acceleration/stage_20261003_wave37_index_v1.py','acceleration/stage_20261003_wave37_index_v1_spec.md',
 'acceleration/record_20261003_wave37_milestone_v1.py','acceleration/results/20261003_wave37_milestone01','acceleration/results/20261003_wave37_milestone_supervision01',
 'acceleration/results/20261003_wave37_registration01','acceleration/results/20261003_wave37_registration02','acceleration/results/20261003_wave37_registration_supervision01','acceleration/results/20261003_wave37_registration_supervision02',
 'acceleration/register_20261003_bound_claims_v10.py','acceleration/register_20261003_bound_claims_v10_spec.md','acceleration/audit_20261003_registrar_v10_engineering_v1.py','acceleration/audit_20261003_registrar_v10_engineering_v1_spec.md',BASE+'registrar_v10_engineering01',BASE+'registrar_v10_engineering_supervision01',
 'acceleration/audit_20261003_wave37_transition_v1.py','acceleration/audit_20261003_wave37_transition_v1_spec.md',BASE+'wave37_transition01',BASE+'wave37_transition_supervision01',
 'acceleration/confirm_20261003_wave36_publication_v1.py','acceleration/confirm_20261003_wave36_publication_v1_spec.md','acceleration/results/20261003_wave36_public_confirmation01','acceleration/results/20261003_wave36_public_confirmation_supervision01',
 'acceleration/audit_20261003_wave36_availability_v1.py','acceleration/audit_20261003_wave36_availability_v1_spec.md',BASE+'wave36_availability01',BASE+'wave36_availability_supervision01',BASE+'wave36_availability_calibration01',BASE+'wave36_availability_calibration_supervision01',
 'acceleration/results/20261003_rooted8_unrestricted_source_supervisor01','acceleration/results/20261003_rooted8_unrestricted_source_supervisor02',
 'acceleration/results/20261003_rooted8_unrestricted_metadata_supervisor01','acceleration/results/20261003_rooted8_unrestricted_launch_metadata01.json','acceleration/results/20261003_rooted8_unrestricted_launch_metadata_supervisor01','acceleration/results/20261003_rooted8_unrestricted_candidate_metadata_supervisor01',
 'acceleration/record_20261003_rooted8_unrestricted_bindings_v1.py','acceleration/record_20261003_rooted8_unrestricted_bindings_v1_spec.md',BASE+'rooted8_unrestricted_bindings01',BASE+'rooted8_unrestricted_bindings_supervision01',
 'acceleration/package_20261003_wave37_rooted8_v1.py','acceleration/package_20261003_wave37_rooted8_v1_spec.md','acceleration/results/20261003_wave37_rooted8_package01','acceleration/results/20261003_wave37_rooted8_package_supervision01',
 'acceleration/audit_20261003_wave37_lossless_recovery_v1.py','acceleration/audit_20261003_wave37_lossless_recovery_v1_spec.md',BASE+'wave37_recovery01/summary.json',BASE+'wave37_recovery01/controls',BASE+'wave37_recovery_supervision01',
 'acceleration/recover_20261003_wave37_public_inputs_v1.py','acceleration/recover_20261003_wave37_public_inputs_v1_spec.md','acceleration/results/20261003_wave37_recovery_clean01','acceleration/results/20261003_wave37_recovery_clean_supervision01'
]
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):
 with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def save(p,v):
 with p.open('x',encoding='utf8',newline='\n') as s:json.dump(v,s,indent=2);s.write('\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();d=CommandDeadline(a.seconds,allocation_reason='Narrow metadata plan and exact hash-bound attribute suffix;120outer100worker20reserve, no index/science')
 out=a.out.resolve();need(out.is_relative_to(ROOT),'bounded output');out.mkdir(parents=True,exist_ok=False);need(sha(ROOT/'CLAIMS.yaml')==LEDGER,'exact343 ledger')
 current=yaml.load((ROOT/'CLAIMS.yaml').read_text(),Loader=UniqueLoader);need(len(current['claims'])==343,'exact343 cutoff');docs={q['path'] for q in current['artifacts'] if q['id'] in {e for c in current['claims'][337:] for e in c['evidence']} and q['path'].startswith('docs/') and q['path'].endswith('.md')}
 docs.update(p for p in EXTRAS if p.startswith('docs/') and p.endswith('.md'));docs.update(['README.md','ACTIVE_RESEARCH.md','.github/workflows/claims.yml','.gitattributes']);attrs=ROOT/'.gitattributes';before=attrs.read_bytes();(out/'gitattributes.before').write_bytes(before)
 lines=before.decode('utf8').splitlines();added=[('/'+p+' -text') for p in sorted(docs) if ('/'+p+' -text') not in lines]
 suffix=('\n# Exact wave37 hash-bound docs and reviewed infrastructure byte identities.\n'+'\n'.join(added)+'\n').encode();attrs.write_bytes(before+suffix)
 need(attrs.read_bytes().startswith(before),'all prior attributes preserved')
 from freeze_20261003_wave37_evidence_v2 import PACKAGES,path
 extras=list(EXTRAS)+[Path(__file__).relative_to(ROOT).as_posix(),'acceleration/prepare_20261003_wave37_evidence_plan_v1_spec.md',out.relative_to(ROOT).as_posix()]
 for p in extras:need(path(p).exists(),'explicit extra exists '+p)
 plan={'schema':'WAVE37_EXPLICIT_CLOSURE_PLAN_V2','ledger_sha256':LEDGER,'before':'acceleration/results/20261003_wave36_public_confirmation01/CLAIMS.after.yaml','before_sha256':'5bd21f4126fea49e84e54b6d4bd63e4401b31d62727b72198d2c97c36c9e0ed3','packages':PACKAGES,'recovery':{'path':BASE+'wave37_recovery01/summary.json','sha256':'6dd37b0d65e16522a71ac8a07419907b281ea96f5638bbab170678122564392c'},'clean_restore':{'path':'acceleration/results/20261003_wave37_recovery_clean01/summary.json','sha256':'5091fc02647848d5330943a440387007f66cf905748a2c908af84c415eab5499'},'extras':extras,'exclusions':['All new warm scientific outputs/process observations, root8 GF2/reset bindings queuedwave38.','Restored raw duplicates under recovery01/recovered and all build destinations.','Historical untracked directories,494MBGF3checkpoint and platform binaries.'],'attributes_added':added}
 save(out/'plan.json',plan);save(out/'summary.json',{'status':'WAVE37_EXPLICIT_PLAN_AND_NARROW_ATTRIBUTES_PREPARED','timestamp':datetime.now(timezone.utc).isoformat(),'command':[sys.executable,*sys.argv],'source_sha256':sha(Path(__file__)),'plan_sha256':sha(out/'plan.json'),'before_attributes_sha256':hashlib.sha256(before).hexdigest(),'after_attributes_sha256':sha(attrs),'attributes_added':added,'historical_attribute_prefix_preserved':True,'ledger_mutated':False,'index_mutated':False,'mathematical_replay':False,'deadline':d.status()});print(json.dumps({'plan_sha256':sha(out/'plan.json'),'attributes_added':len(added),'after_attributes_sha256':sha(attrs)}))
if __name__=='__main__':main()
