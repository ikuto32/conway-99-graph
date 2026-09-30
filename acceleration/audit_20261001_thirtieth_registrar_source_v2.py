"""Static v2 registrar transaction review, with no registrar imports or execution."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/register_20261001_thirtieth_batches03_05.py'
NEW='acceleration/register_20261001_thirtieth_batches03_05_v2.py'
PINS={OLD:'121d2646bc47c2112f71059dce6bc6e9ea86d428cf36d8d9d373032a61493852',NEW:'f91210a340ab4b84f37a9aa88483007e8101f87b9e400e5e47a1872ca82d7d57','acceleration/register_20261001_thirtieth_batches03_05_v2_spec.md':'b97b19c7a278ac1417a65b8e82ca2d7333ebf2060385e3996330f83314d42103','acceleration/results/20261001_independent_review/thirtieth_registrar_source_review/summary.json':'356086a119f686c2e15757b2f7c82ca83ac8fa764b2c1a1d3a47ae57606a704b'}
OUT='acceleration/results/20261001_independent_review/thirtieth_registrar_source_review_v2'

def need(v,m):
 if not v:raise ValueError(m)
def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 out=ROOT/OUT;out.mkdir(parents=True,exist_ok=False)
 for p,d in PINS.items():need(h(p)==d,'frozen identity '+p)
 old,new=[(ROOT/p).read_text(encoding='utf8')for p in [OLD,NEW]]
 trees=[ast.parse(x)for x in [old,new]]
 funcs=[{n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}for t in trees]
 unchanged=[]
 for name in ['need','safe','sha','read','save','admissible','compare_batch']:
  need(ast.dump(funcs[0][name],include_attributes=False)==ast.dump(funcs[1][name],include_attributes=False),'unchanged function '+name);unchanged.append(name)
 a=old[old.index('    def pin('):old.index('        need((ROOT/')]
 b=new[new.index('    def pin('):new.index('        # Prepare every byte')]
 need(a==b,'entire precommit claim-binding/validation construction unchanged')
 need("os.replace(pending,ROOT/'CLAIMS.yaml'); ledger_replaced=True"in new,'replace then Python flag')
 need("recovery_required=ledger_replaced"in new and "except BaseException"in new,'flag-only classification and broad catch')
 phases=[dict(phase='before replacement',live='BEFORE',flag=False,reported_recovery=False),dict(phase='replacement completed before flag assignment',live='AFTER',flag=False,reported_recovery=False),dict(phase='flag assigned before final receipt publication',live='AFTER',flag=True,reported_recovery=True)]
 need(any(r['live']=='AFTER'and not r['reported_recovery']for r in phases),'literal interruption-window countermodel')
 for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]:PINS[p.relative_to(ROOT).as_posix()]=h(p.relative_to(ROOT))
 result=dict(status='INDEPENDENT_THIRTIETH_REGISTRAR_V2_SOURCE_REVIEW_CHANGES_REQUESTED',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],inputs_sha256=PINS,registrar_imported=False,registrar_executed=False,ledger_writes=0,mathematical_verification=False,unchanged_functions=unchanged,precommit_binding_logic_unchanged=True,original_partial_write_gap_closed=True,
  finding=dict(id='POST_RENAME_FLAG_WINDOW',severity='receipt classification',statement='An interruption after atomic replacement but before the Python flag assignment can leave live AFTER bytes while recovery_required remains false. The separately observed hash exposes this state but does not govern the current classification.',source_model=phases,execution_observed=False,not_mathematical_refutation=True,recommendation='Classify observed live bytes as BEFORE, AFTER, OTHER or UNREADABLE; derive recovery requirement from that state. Keep the in-memory flag diagnostic only.'),
  trusted_components=['Atomic os.replace on the actual local filesystem; single-root-writer operational assumption.'],limitations=['Static source and instruction-boundary model only; no OS fault injection or registrar execution.','No mathematical binding reapproval; all actual future report pairs remain required.','No power-loss durability or external-writer exclusion assertion.'])
 with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(dict(status=result['status'],sha256=h(OUT+'/summary.json'))))
if __name__=='__main__':main()
