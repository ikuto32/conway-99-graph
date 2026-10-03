"""Preserve v1 and prepare a recoverable atomic ledger commit for the unrun registrar."""
from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=ROOT/'acceleration/register_20261001_thirtieth_batches03_05.py'
    assert h(old)=='121d2646bc47c2112f71059dce6bc6e9ea86d428cf36d8d9d373032a61493852'
    text=old.read_text(encoding='utf8')
    def replace(a,b):
        nonlocal text
        assert text.count(a)==1,repr(a)
        text=text.replace(a,b)
    replace('import argparse, copy, hashlib, json, re, subprocess, sys, yaml',
            'import argparse, copy, hashlib, json, os, re, subprocess, sys, yaml')
    replace("bindings={}; before=(ROOT/'CLAIMS.yaml').read_bytes()", "bindings={}; before=(ROOT/'CLAIMS.yaml').read_bytes(); ledger_replaced=False")
    replace("        need((ROOT/'CLAIMS.yaml').read_bytes()==before,'unchanged live ledger before write'); (ROOT/'CLAIMS.yaml').write_bytes(after); save(out/'summary.json',result)", '''        # Prepare every byte and an immutable journal before touching the live ledger.
        pending=out/'CLAIMS.pending.yaml'
        with pending.open('xb') as stream:
            stream.write(after); stream.flush(); os.fsync(stream.fileno())
        prepared=dict(result)
        prepared['status']='THIRTIETH_BATCHES03_05_REGISTRATION_PREPARED'
        prepared['intended_final_status']=result['status']
        prepared['scope_note']='Preparation is not evidence that the live ledger was replaced.'
        save(out/'registration.prepared.json',prepared)
        result['ledger_write_protocol']='Prepared same-volume temporary file then atomic os.replace; final receipt is published only after ledger replacement.'
        result['recovery_journal']=(out/'transaction.json').relative_to(ROOT).as_posix()
        pending_summary=out/'summary.pending.json'
        with pending_summary.open('x',encoding='utf8',newline='\\n') as stream:
            json.dump(result,stream,indent=2); stream.write('\\n'); stream.flush(); os.fsync(stream.fileno())
        save(out/'transaction.json',dict(status='PREPARED_NOT_COMMITTED',
            before_sha256=result['previous_ledger_sha256'],after_sha256=result['ledger_sha256'],
            pending_ledger=pending.relative_to(ROOT).as_posix(),
            prepared_receipt=pending_summary.relative_to(ROOT).as_posix(),
            prepared_receipt_sha256=hashlib.sha256(pending_summary.read_bytes()).hexdigest(),
            recovery='If final summary is absent, compare the live ledger against immutable before/after snapshots. Do not rerun or overwrite this transaction. Record a separate recovery audit before any further registration.',
            trusted_components=['Python os.replace and the local filesystem atomic rename semantics; no universal power-loss durability guarantee.']))
        need(pending.read_bytes()==after,'prepared ledger exact bytes')
        need((ROOT/'CLAIMS.yaml').read_bytes()==before,'unchanged live ledger before atomic replacement')
        os.replace(pending,ROOT/'CLAIMS.yaml'); ledger_replaced=True
        os.replace(pending_summary,out/'summary.json')''')
    replace("save(out/'failure.json',dict(error=repr(ex),checked_input_bindings=bindings)); raise",
            "save(out/'failure.json',dict(error=repr(ex),checked_input_bindings=bindings,ledger_replaced=ledger_replaced,observed_ledger_sha256=sha('CLAIMS.yaml'),recovery_required=ledger_replaced)); raise")
    ast.parse(text)
    new=ROOT/'acceleration/register_20261001_thirtieth_batches03_05_v2.py'
    with new.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    spec=new.with_name(new.stem+'_spec.md')
    oldspec=old.with_name(old.stem+'_spec.md')
    with spec.open('x',encoding='utf8',newline='\n')as f:
        f.write(oldspec.read_text(encoding='utf8'))
        f.write('''
V2 changes only ledger commit/recovery. Preserve v1 unexecuted source and its
independent source-review finding. Prepare and fsync a same-volume ledger temp
and final-receipt temp, write an immutable PREPARED journal and preparatory report,
then authenticate the live before bytes immediately before atomic os.replace.
Publish summary.json only after replacement. An exception records whether the
ledger replacement occurred and the observed live hash. If replacement succeeds
but final receipt publication fails, treat registration as requiring a separate
recovery audit using immutable before/after snapshots, journal and prepared receipt.
Do not rerun or silently roll back. Atomic filesystem rename semantics are a
trusted component; power-loss durability and concurrent external edits are not
universally guaranteed. The single root writer remains the operational assumption.
''')
    out=ROOT/'acceleration/results/20261001_thirtieth_registrar_v2_preparation';out.mkdir(exist_ok=False)
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        inputs_sha256={old.relative_to(ROOT).as_posix():h(old),oldspec.relative_to(ROOT).as_posix():h(oldspec),Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__))},
        outputs_sha256={new.relative_to(ROOT).as_posix():h(new),spec.relative_to(ROOT).as_posix():h(spec)},
        registrar_executed=False,ledger_mutations=0,mathematical_verification=False,validation='AST parse only; independent source review and actual six report pairs still required.')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result['outputs_sha256']))
if __name__=='__main__':main()
