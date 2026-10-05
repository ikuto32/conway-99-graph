"""Prepare a narrow wave30 inventory; no inventory execution or ledger mutation."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
N='acceleration/results/20261001_';J=N+'independent_review/'
I='acceleration/results/20260930_independent_review/'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    failed=Path(__file__).with_name('prepare_20261001_thirtieth_inventory_source.py')
    correction=ROOT/(N+'thirtieth_inventory_preparation_correction');correction.mkdir(exist_ok=False)
    receipt=dict(recorded_at=datetime.now(timezone.utc).isoformat(),failed_source=dict(path=failed.relative_to(ROOT).as_posix(),sha256=h(failed)),failed_command=['uv','run','--locked','--offline','--cache-dir','.uv-cache-20260917','python','-B','acceleration/prepare_20261001_thirtieth_inventory_source.py'],cwd=str(ROOT),actual_exit_code=1,tool_chunk='dcc4f5',observed_exception="NameError: name 'I' is not defined at source line40",executed_at=None,executed_at_null_reason='The original tool result did not record an exact UTC start timestamp.',failure_before_output_source_write=True,ledger_mutations=0,correction='Define the intended archived independent-review path in a new source version; preserve original executed source.',new_source=dict(path=Path(__file__).relative_to(ROOT).as_posix(),sha256=h(Path(__file__))))
    with(correction/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(receipt,f,indent=2);f.write('\n')
    old=ROOT/'acceleration/inventory_20261001_twentyninth_candidates.py'
    # This preparation records the exact predecessor bytes; the new source is not executed.
    source=old.read_text(encoding='utf8');tail=source[source.index('def reason(p):'):]
    dirs=[]
    for b in (3,4,5):
        pre=f'exact_eight_prefix64_batch{b:02d}'
        dirs += [N+pre+'_'+s for s in ('request','selection','execution','build_launcher','native_preflight','native_pilot')]
        dirs += [N+pre+f'_cnfs_part{i:02d}'for i in range(4)]
        if b!=4:dirs.append(N+pre+'_consolidated')
        dirs += [J+pre+'_'+s for s in ('selection','object_calibration','proofs')]
        dirs.append(J+pre+('_cnfs_v4' if b==4 else '_cnfs_v3'))
    dirs += [N+'exact_eight_prefix64_batch04_continuation_'+s for s in ('authorization','preparation','selection','build_launcher','consolidated')]
    dirs += [N+f'exact_eight_prefix64_batch04_continuation_cnfs_part{i:02d}'for i in range(4)]
    dirs += [J+'exact_eight_prefix64_batch04_continuation_preflight']
    dirs += [N+s for s in ('exact_eight_case0_core','exact_eight_case0_core_v2','reimbayev_seven_access','reimbayev_z82_overlap','reimbayev_z82_overlap_v2','thirtieth_registrar_preparation','thirtieth_registrar_v2_preparation','thirtieth_registrar_v3_preparation','thirtieth_initial_registrar_preparation','thirtieth_followup_registrar_preparation')]
    dirs += [J+s for s in ('exact_eight_case0_core','reimbayev_z82','thirtieth_registrar_source_review','thirtieth_registrar_source_review_v2','thirtieth_registrar_source_review_v3','thirtieth_followup_registrar_source_review')]
    regs=[N+'thirtieth_initial_registration',N+'thirtieth_followup_registration'];dirs+=regs
    stems=['freeze_20261001_exact_eight_prefix64_batch03_request','freeze_20261001_exact_eight_prefix64_request','continue_20261001_exact_eight_batch04','check_20261001_exact_eight_batch04_continuation_preparation','audit_20261001_exact_eight_checkpoint_continuation','audit_20261001_exact_eight_checkpoint_records','audit_20261001_exact_eight_explicit_batch_v4','theory_20261001_exact_eight_case0_core','theory_20261001_exact_eight_case0_core_v2','audit_20261001_exact_eight_case0_core','bind_20261001_exact_eight_case0_core','theory_20261001_reimbayev_z82_overlap','theory_20261001_reimbayev_z82_overlap_v2','audit_20261001_reimbayev_z82','bind_20261001_reimbayev_z82','prepare_20261001_thirtieth_registrar','prepare_20261001_thirtieth_registrar_v2','prepare_20261001_thirtieth_registrar_v3','register_20261001_thirtieth_batches03_05','register_20261001_thirtieth_batches03_05_v2','register_20261001_thirtieth_batches03_05_v3','audit_20261001_thirtieth_registrar_source','audit_20261001_thirtieth_registrar_source_v2','audit_20261001_thirtieth_registrar_source_v3','prepare_20261001_thirtieth_initial_registrar','register_20261001_thirtieth_initial_claims','prepare_20261001_thirtieth_followup_registrar','register_20261001_thirtieth_followup_claims','record_20261001_thirtieth_initial_checkpoint','record_20261001_thirtieth_checkpoint','prepare_20261001_thirtieth_inventory_source','inventory_20261001_thirtieth_candidates']
    files=['acceleration/'+s+'.py'for s in stems]
    files += ['acceleration/theory_20261001_exact_eight_prefix64_batch03_plan.md','acceleration/theory_20261001_exact_eight_prefix64_batch04_plan.md','acceleration/theory_20261001_exact_eight_prefix64_batch04_continuation_plan.md','acceleration/theory_20261001_exact_eight_prefix64_batch05_plan.md','docs/REVIEW_PLAN_20261001_EXACT_EIGHT_CHECKPOINT_CONTINUATION.md','docs/RESULT_20261001_EXACT_EIGHT_CASE0_CORE.md','docs/LITERATURE_20261001_REIMBAYEV_SEVEN_Z82.md','docs/AUDIT_20261001_REIMBAYEV_Z82.md','docs/RESEARCH_20261001_THIRTIETH_WAVE.md',N+'resume/thirtieth_initial_checkpoint.json',N+'resume/thirtieth_milestone_checkpoint.json',N+'resume/claims_at_thirtieth_milestone.yaml']
    stems.append('prepare_20261001_thirtieth_inventory_source_v2')
    files.append('acceleration/prepare_20261001_thirtieth_inventory_source_v2.py')
    dirs.append(N+'thirtieth_inventory_preparation_correction')
    header='''"""Explicit wave30 candidate inventory, never mathematical approval."""
from pathlib import Path
from collections import defaultdict
import argparse,ast,hashlib,json,re,time
import yaml
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
N='acceleration/results/20261001_'
I=B+'independent_review/'
J=N+'independent_review/'
'''
    values=dict(DIRECTORIES=sorted(set(dirs)),FILES=sorted(set(files)),SOURCE_STEMS=sorted(set(stems)),REGISTRATIONS=regs,CHECKPOINT=N+'resume/thirtieth_milestone_checkpoint.json',SNAPSHOT=N+'resume/claims_at_thirtieth_milestone.yaml',CHECKPOINT_SHA=None,SNAPSHOT_SHA=None,PRIOR=N+'twentyninth_artifact_packaging/catalog.json',PRIOR_SHA='22a5e3b558a7b2104ae48d939d4bd116d03371333247c736e06a4e279b8fa0a5',ORIGIN_PINS={old.relative_to(ROOT).as_posix():h(old),Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__))},LIMIT=10*1024**2,MAX_FILES=20000,MAX_BYTES=4*1024**3,MAX_SECONDS=120,PROTECTED={'PROMPT.md','CLAIMS.yaml',I+'hadamard_oriented_unknown/process.stdout.log'},FUTURE_TOKENS=('batch06','batch07','batch08','batch09','batch10','batch11','n3_hamming','three_center','thirtyfirst','thirtieth_raw_recovery','thirtieth_recovery','reproducing_20261001_thirtieth'),ACTIVE_OUTPUT=None)
    for k,v in values.items():header+=k+'='+repr(v)+'\n'
    repl={'twentyninth_candidate_inventory':'thirtieth_candidate_inventory','len(records) < 29':'len(records) < 31',"len(ledger['claims']) == 300":"len(ledger['claims']) == 308","{'VERIFIED':293, 'CANDIDATE':3, 'REFUTED':4}":"{'VERIFIED':301, 'CANDIDATE':3, 'REFUTED':4}","cp['claim_population']==300":"cp['claim_population']==308",'len(newids) == len(set(newids)) == 6':'len(newids) == len(set(newids)) == 8',"sum(c['status']=='VERIFIED' for c in newclaims) == 6":"sum(c['status']=='VERIFIED' for c in newclaims) == 8","len(newclaims)==6":"len(newclaims)==8",'WAVE29':'WAVE30','claims=300':'claims=308','Batch03 and later allocations are excluded;':'Batch06 and later allocations and unrelated structural probes are excluded;'}
    for a,b in repl.items():assert a in tail,a;tail=tail.replace(a,b)
    new=ROOT/'acceleration/inventory_20261001_thirtieth_candidates.py';spec=new.with_name(new.stem+'_spec.md');text=header+'\n'+tail;ast.parse(text)
    with new.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    with spec.open('x',encoding='utf8',newline='\n')as f:f.write('''# Exact wave30 candidate inventory

After the308-claim milestone is frozen, authenticate its checkpoint/ledger SHA
and both registration transactions. Inventory only the declared batch03/04/05,
batch04original-partial and continuation, core v1/v2, selected Z82 producer/audit,
and registrar preparation/review/correction records. All eight new claim IDs
must match the checkpoint. No batch06+, Hamming or three-center probe is selected.
No broad untracked-file staging, Git command, solver, or proof replay occurs.

Bound selection to20,000 files/4GiB/120cooperative seconds. Hash all selected
bytes, scan explicit metadata references and static local imports, and report
every absent file, conflicting binding and outside-allowlist dependency. Do not
open protected sources, credentials-shaped paths, tools, or later cohorts.
Large raw files need a separately checked retrieval package. Model/domain JSON
is hashed but not recursively parsed in this inventory; the final catalog must
check the full closure. Downloaded primary literature and its extracted figure
will remain LOCAL_ONLY with versioned external retrieval instructions rather
than being silently republished or described as Git-available.

This initial inventory may report missing supplements; such a report is not
publication approval. Preserve its exact source and output before preparing
any revised allowlist. No current claim or process state is inferred here.
''')
    out=ROOT/(N+'thirtieth_inventory_source_preparation');out.mkdir(exist_ok=False)
    r=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs_sha256=values['ORIGIN_PINS'],outputs_sha256={new.relative_to(ROOT).as_posix():h(new),spec.relative_to(ROOT).as_posix():h(spec)},inventory_executed=False,ledger_mutations=0,validation='AST parse only')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r['outputs_sha256']))
if __name__=='__main__':main()
