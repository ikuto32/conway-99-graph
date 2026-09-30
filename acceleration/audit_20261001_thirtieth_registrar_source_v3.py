"""Independent narrow source review of registrar v3, without importing it."""
from pathlib import Path
from datetime import datetime,timezone
import ast,copy,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
V2='acceleration/register_20261001_thirtieth_batches03_05_v2.py'
V3='acceleration/register_20261001_thirtieth_batches03_05_v3.py'
PINS={V2:'f91210a340ab4b84f37a9aa88483007e8101f87b9e400e5e47a1872ca82d7d57',V3:'8ff7c5791c54c72f2c9c16a4237dd162480d63927e87f4d338ca032c79cc7b92','acceleration/register_20261001_thirtieth_batches03_05_v3_spec.md':'648c8e5732705adffb6cfa5f1df3fd0861ba2b8a24b6842b904679edeb304137','acceleration/results/20261001_independent_review/thirtieth_registrar_source_review/summary.json':'356086a119f686c2e15757b2f7c82ca83ac8fa764b2c1a1d3a47ae57606a704b','acceleration/results/20261001_independent_review/thirtieth_registrar_source_review_v2/summary.json':'e67eb689ec0b6c60bcc09b2fb865f180e7838f7694039341a3fe94f7a7ce5a39'}
OUT='acceleration/results/20261001_independent_review/thirtieth_registrar_source_review_v3'

def need(v,m):
 if not v:raise ValueError(m)
def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def norm(n):return ast.dump(n,include_attributes=False)
def main():
 out=ROOT/OUT;out.mkdir(parents=True,exist_ok=False)
 for p,d in PINS.items():need(h(p)==d,'frozen identity '+p)
 trees=[ast.parse((ROOT/p).read_text(encoding='utf8'))for p in [V2,V3]]
 handlers=[]
 for t in trees:
  m=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='main')
  outer=next(n for n in m.body if isinstance(n,ast.Try))
  need(len(outer.handlers)==1 and isinstance(outer.handlers[0].type,ast.Name)and outer.handlers[0].type.id=='BaseException','outer failure handler')
  handlers.append(copy.deepcopy(outer.handlers[0]));outer.handlers[0].body=[ast.Pass()]
 need(norm(trees[0])==norm(trees[1]),'entire module unchanged except failure handler')
 handler=handlers[1]
 commit=next(n.value for n in handler.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='commit_state'for x in n.targets))
 expected=ast.parse("'UNCHANGED_BEFORE' if observed==before_hash else 'REPLACED_WITH_EXPECTED_AFTER' if after_hash is not None and observed==after_hash else 'UNKNOWN_OR_UNEXPECTED_BYTES'",mode='eval').body
 need(norm(commit)==norm(expected),'observed hash controls exact state expression')
 writes=[n for n in ast.walk(handler)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='save']
 need(len(writes)==1,'one failure receipt')
 record=writes[0].args[1];need(isinstance(record,ast.Call)and isinstance(record.func,ast.Name)and record.func.id=='dict','explicit failure mapping')
 keys={k.arg:k.value for k in record.keywords}
 need(norm(keys['recovery_required'])==norm(ast.parse("commit_state!='UNCHANGED_BEFORE'",mode='eval').body),'safe recovery classification')
 need(isinstance(keys['replacement_flag_diagnostic_only'],ast.Name)and keys['replacement_flag_diagnostic_only'].id=='ledger_replaced','flag is diagnostic')
 need(all(k in keys for k in ['observed_ledger_sha256','observation_unavailable_reason','before_sha256','prepared_after_sha256','prepared_after_unavailable_reason']),'observations and unavailable reasons')
 need(not any(isinstance(n,ast.Name)and n.id=='ledger_replaced'for n in ast.walk(commit)),'flag-independent authoritative state')
 # A separate decision table checks the finite classification; no extracted code executes.
 rows=[]
 for after in ['b'*64,None]:
  for observed in ['a'*64,'b'*64,'c'*64,None]:
   for flag in [False,True]:
    if observed=='a'*64:state='UNCHANGED_BEFORE'
    elif after is not None and observed==after:state='REPLACED_WITH_EXPECTED_AFTER'
    else:state='UNKNOWN_OR_UNEXPECTED_BYTES'
    recovery=state!='UNCHANGED_BEFORE'
    need(recovery==(observed!='a'*64),'recover except exact before')
    rows.append(dict(prepared_after=after,observed=observed,diagnostic_flag=flag,expected_state=state,recovery_required=recovery))
 bad=[]
 def reject(name,condition):
  need(not condition,'accepted malformed classifier '+name);bad.append(name)
 reject('old flag-only recovery',all(r['diagnostic_flag']==r['recovery_required']for r in rows))
 reject('unknown state accepted without recovery',all(not r['recovery_required']for r in rows if r['observed']is None))
 reject('AFTER requires diagnostic flag',all(r['diagnostic_flag']for r in rows if r['expected_state']=='REPLACED_WITH_EXPECTED_AFTER'))
 prep='acceleration/results/20261001_thirtieth_registrar_v3_preparation/summary.json';PINS[prep]=h(prep);p=json.loads((ROOT/prep).read_bytes());need(not p['registrar_executed']and p['ledger_mutations']==0 and p['outputs_sha256'][V3]==PINS[V3],'actual unexecuted preparation')
 for f in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]:PINS[f.relative_to(ROOT).as_posix()]=h(f.relative_to(ROOT))
 result=dict(status='INDEPENDENT_THIRTIETH_REGISTRAR_V3_SOURCE_REVIEW_PASS',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],inputs_sha256=PINS,registrar_imported=False,registrar_executed=False,ledger_writes=0,git_writes=0,mathematical_verification=False,whole_module_other_than_failure_handler_unchanged=True,decision_table=rows,malformed_classifiers_rejected=bad,previous_findings_closed=['NONATOMIC_LIVE_LEDGER_WRITE by the unchanged v2 pending/fsync/journal/atomic-replace protocol','POST_RENAME_FLAG_WINDOW by v3 observed-hash classification'],
  scope='Source-only review of the exact v3 registrar. Binding checks retain previous reviewed behavior; no execution approval or mathematical reapproval.',
  prerequisites=['All six actual independent report/binding pairs for batches03,04,05 must exist and pass exact hash/status/identity/dependency checks.','Root must explicitly supply the current300 ledger SHA after publication-pointer updates and own the single-writer transaction.','Any failure with observed bytes other than exact BEFORE requires separate recovery audit; do not rerun blindly.'],
  limitations=['No registrar import, live transaction, OS failure injection or native solver execution.','Source reasoning and16 finite classifier states only; no universal OS, power-loss, concurrent-writer or exception-delivery guarantee.','Atomic local filesystem replacement and successful receipt storage remain trusted engineering components. If storage itself prevents a failure receipt, the prepared transaction journal and snapshots supply the recovery route.'])
 with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(dict(status=result['status'],sha256=h(OUT+'/summary.json'))))
if __name__=='__main__':main()
