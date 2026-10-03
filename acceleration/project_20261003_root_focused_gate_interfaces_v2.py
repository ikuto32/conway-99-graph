"""Exact two-key root-focused gate metadata projection; no mathematical replay."""
import argparse
import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
SELF='acceleration/project_20261003_root_focused_gate_interfaces_v2.py'
SPEC='acceleration/project_20261003_root_focused_gate_interfaces_v2_spec.md'
ORIGINS={
 'controls':('acceleration/results/20261003_independent_review/root_focused_engine_full01/summary.json','fa4fa8756360b3f510575caeac4c5b9d19826b1463faaecf094c5c77a96951bc','INDEPENDENT_ROOT_FOCUSED_ENGINE_V1_CONTROLS_PASS'),
 'saved_objects':('acceleration/results/20261003_independent_review/root_focused_saved_calibration02/summary.json','009129501a0b20ab81b823626d04d1ee76983fc6c228a88408568321f1d054f5','INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_CALIBRATION_PASS')}
PROTECTED={'CLAIMS.yaml','.git/index'}
PROTECTED_HASHES={'CLAIMS.yaml':'b2796504a736ef16872ee36812d3b8ddb6446d0ea28d4883525f9ab9a3dd5679','.git/index':'68b695ba680915be542d08a9522a2a3acd329f8fd05e471b35ae27a9e0523152'}
EXTRA={'acceleration/results/20261003_independent_review/root_focused_complete_preflight01/summary.json':'b94f418b8824f3b8791819ef711a6f5cec4a5588488001ee0e58334005070fa0'}
class ProjectionError(ValueError):pass
def need(ok,message):
 if not ok:raise ProjectionError(message)
def digest(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,value):
 with p.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,indent=2);f.write('\n')
def transform(kind,raw,path,h,sourcepins):
 need(kind in ORIGINS and (path,h)==ORIGINS[kind][:2],'exact immutable origin identity')
 need(type(raw)is dict and raw['status']==ORIGINS[kind][2]and raw['verifier']=='/root/checkpoint_audit'and raw['producer']=='/root/native_driver'and raw['method']=='independent_artifact_check','exact original report role/status/method')
 need(type(raw['inputs_sha256'])is dict and PROTECTED<=set(raw['inputs_sha256']),'both original protected observations present')
 for name,hvalue in raw['inputs_sha256'].items():need(type(name)is str and type(hvalue)is str and len(hvalue)==64 and all(c in '0123456789abcdef'for c in hvalue),'literal original input identities')
 need({k:raw['inputs_sha256'][k]for k in sorted(PROTECTED)}==PROTECTED_HASHES,'exact pinned historical protected observations')
 if kind=='controls':
  need(all(type(raw[k])is int for k in ['positive_native_calls','strict_native_vetoes','complete_finite_proposals','complete_probe_proposals','pair_cost_records_checked','whole_split_families','scientific_results_approved'])and all(type(v)is int for v in raw['actual_immediate_retention_events'].values()),'literal integer finite scope fields')
  need((raw['positive_native_calls'],raw['strict_native_vetoes'],raw['complete_finite_proposals'],raw['complete_probe_proposals'],raw['pair_cost_records_checked'],raw['whole_split_families'])==(26,36,13582,270,4472,4),'exact complete original finite scope')
  need(raw['actual_immediate_retention_events']=={'initial':6,'first_localzero':2,'accepted_mu_improvement':0}and raw['unexercised_retention_branches']==['accepted_mu_improvement']and raw['target_resolution']=='NONE'and raw['scientific_results_approved']==0,'original unexercised branch/no-science scope')
 else:
  need(type(raw['positive_controls'])is int and type(raw['strict_negative_controls'])is int,'literal integer calibration scope fields')
  need(raw['positive_controls']==4 and raw['strict_negative_controls']==21 and raw['scientific_outputs_checked']is False,'exact original pre-output calibration scope')
 result=copy.deepcopy(raw);observations={k:result['inputs_sha256'].pop(k)for k in sorted(PROTECTED)}
 for k,v in {path:h,**sourcepins,**(EXTRA if kind=='controls'else{})}.items():need(k not in result['inputs_sha256']or result['inputs_sha256'][k]==v,'consistent immutable projection dependency');result['inputs_sha256'][k]=v
 need(set(raw['inputs_sha256'])-set(result['inputs_sha256'])==PROTECTED and all(result['inputs_sha256'][k]==v for k,v in raw['inputs_sha256'].items()if k not in PROTECTED),'only two mutable observations removed')
 result['historical_protected_execution_state']=dict(observations_sha256=observations,role='Observed protected state at original checking invocation; not an immutable native execution dependency.',reason='Original independent command checked these bytes before/after and left them unchanged. Later authorized ledger availability/registration or Git publication may change them without changing checked native/helper artifacts.',original_report=dict(path=path,sha256=h),current_state_checked=False,current_state_checked_reason='This conversion does not reread or assert current ledger/index values.')
 result['interface_projection']=dict(schema='ROOT_FOCUSED_TWO_PROTECTED_OBSERVATIONS_PROJECTION_V1',original_report_path=path,original_report_sha256=h,removed_dependency_keys=sorted(PROTECTED),mathematical_replay=False,new_native_calls=0,new_mathematical_approval=False,scope='Identity-preserving metadata conversion of exact unchanged independent statement/control outcomes; pending ROOT interface review.')
 need(all(result[k]==v for k,v in raw.items()if k!='inputs_sha256'),'every original report field preserved')
 return result
def controls():
 records=[]
 def reject(name,expected,fn):
  try:fn()
  except ProjectionError as e:need(str(e)==expected,'wrong rejection diagnostic '+name);records.append(dict(case=name,outcome='REJECTED',diagnostic=str(e)));return
  raise ProjectionError('false acceptance '+name)
 for kind,(path,h,status)in ORIGINS.items():
  raw=json.loads((ROOT/path).read_bytes());sourcepins={SELF:digest(ROOT/SELF),SPEC:digest(ROOT/SPEC)};good=transform(kind,raw,path,h,sourcepins);need(PROTECTED.isdisjoint(good['inputs_sha256']),'valid immutable projection');records.append(dict(case=kind+' exact original positive',outcome='PASS'))
  for label,message,change in [('status','exact original report role/status/method',lambda x:x.update(status='UNKNOWN')),('verifier','exact original report role/status/method',lambda x:x.update(verifier='/root/native_driver')),('method','exact original report role/status/method',lambda x:x.update(method='repeated_execution')),('producer','exact original report role/status/method',lambda x:x.update(producer='/root/checkpoint_audit')),('missingledger','both original protected observations present',lambda x:x['inputs_sha256'].pop('CLAIMS.yaml')),('missingindex','both original protected observations present',lambda x:x['inputs_sha256'].pop('.git/index')),('inputhash','literal original input identities',lambda x:x['inputs_sha256'].__setitem__('CLAIMS.yaml','bad')),('validwrongledgerhash','exact pinned historical protected observations',lambda x:x['inputs_sha256'].__setitem__('CLAIMS.yaml','0'*64)),('validwrongindexhash','exact pinned historical protected observations',lambda x:x['inputs_sha256'].__setitem__('.git/index','0'*64))]:
   bad=copy.deepcopy(raw);change(bad);reject(kind+' '+label,message,lambda:transform(kind,bad,path,h,sourcepins))
  reject(kind+' wrong origin hash','exact immutable origin identity',lambda:transform(kind,raw,path,'0'*64,sourcepins));reject(kind+' wrong origin path','exact immutable origin identity',lambda:transform(kind,raw,'acceleration/other.json',h,sourcepins))
  changed=copy.deepcopy(raw)
  if kind=='controls':changed['complete_finite_proposals']+=1
  else:changed['strict_negative_controls']+=1
  reject(kind+' wrong exact scope','exact complete original finite scope'if kind=='controls'else'exact original pre-output calibration scope',lambda:transform(kind,changed,path,h,sourcepins))
  field='complete_finite_proposals'if kind=='controls'else'positive_controls';message='literal integer finite scope fields'if kind=='controls'else'literal integer calibration scope fields'
  for value in [float(raw[field]),True]:
   changed=copy.deepcopy(raw);changed[field]=value;reject(kind+' wrong literal scope '+repr(value),message,lambda:transform(kind,changed,path,h,sourcepins))
 # The harness must reject a wrong-stage exception instead of crediting it.
 def wrong():raise ProjectionError('other stage')
 reject('wrong-stage harness rejection','wrong rejection diagnostic inner',lambda:reject('inner','expected stage',wrong))
 return records
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['controls','project']);p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',required=True);a=p.parse_args();d=CommandDeadline(a.seconds,allocation_reason='Narrow exact metadata interface conversion/calibration only,20save reserve; no native or mathematical replay');out=(ROOT/a.out).resolve();need(out.is_relative_to(ROOT),'workspace output');out.mkdir(parents=True,exist_ok=False);pins={}
 try:
  for name in [SELF,SPEC,'acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']:pins[name]=digest(ROOT/name)
  sourcepins=dict(pins)
  for kind,(path,h,status)in ORIGINS.items():
   need(d.status()['remaining_seconds']>20,'not completed within allocated budget');need(digest(ROOT/path)==h,'exact original report bytes');pins[path]=h;raw=json.loads((ROOT/path).read_bytes())
   for name,wanted in raw['inputs_sha256'].items():
    if name in PROTECTED:continue
    need(d.status()['remaining_seconds']>20,'source identity reserve');need(digest(ROOT/name)==wanted,'unchanged immutable source/raw dependency '+name);pins[name]=wanted
  for name,h in EXTRA.items():need(digest(ROOT/name)==h,'required complete source preflight bytes');pins[name]=h
  records=controls();save(out/'controls.json',records)
  if a.mode=='project':
   for kind,(path,h,status)in ORIGINS.items():save(out/(kind+'_gate.json'),transform(kind,json.loads((ROOT/path).read_bytes()),path,h,sourcepins))
  save(out/'summary.json',dict(status='ROOT_FOCUSED_INTERFACE_PROJECTION_HELPER_CONTROLS_PASS'if a.mode=='controls'else'ROOT_FOCUSED_INTERFACE_METADATA_PROJECTIONS_PENDING_ROOT_REVIEW',timestamp=datetime.now(timezone.utc).isoformat(),author='/root/checkpoint_audit',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,positive_controls=sum(r['outcome']=='PASS'for r in records),strict_negative_controls=sum(r['outcome']=='REJECTED'for r in records),controls_sha256=digest(out/'controls.json'),deadline=d.status(),mathematical_replay=False,native_calls=0,ledger_or_index_written=False,limitations=['Author controls are not independent ROOT review.','Exactly two historical protected observations moved; every immutable dependency and original report field preserved.','No current protected-state assertion and no new mathematical approval.']));print(a.mode,'EXACT_TWO_KEY_PROJECTION',len(records))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),inputs_sha256=pins,deadline=d.status(),no_approval=True));raise
if __name__=='__main__':main()
