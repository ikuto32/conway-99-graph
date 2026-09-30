"""Prepare observed-byte recovery classification; preserve both unexecuted predecessors."""
from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=ROOT/'acceleration/register_20261001_thirtieth_batches03_05_v2.py'
    assert h(old)=='f91210a340ab4b84f37a9aa88483007e8101f87b9e400e5e47a1872ca82d7d57'
    source=old.read_text(encoding='utf8')
    before="        save(out/'failure.json',dict(error=repr(ex),checked_input_bindings=bindings,ledger_replaced=ledger_replaced,observed_ledger_sha256=sha('CLAIMS.yaml'),recovery_required=ledger_replaced)); raise"
    after='''        observed=None; observed_reason=None
        try: observed=sha('CLAIMS.yaml')
        except BaseException as observation_error: observed_reason=repr(observation_error)
        before_hash=hashlib.sha256(before).hexdigest()
        after_hash=hashlib.sha256(after).hexdigest() if 'after' in locals() else None
        commit_state=('UNCHANGED_BEFORE' if observed==before_hash else
                      'REPLACED_WITH_EXPECTED_AFTER' if after_hash is not None and observed==after_hash else
                      'UNKNOWN_OR_UNEXPECTED_BYTES')
        save(out/'failure.json',dict(error=repr(ex),checked_input_bindings=bindings,
            replacement_flag_diagnostic_only=ledger_replaced,commit_state=commit_state,
            observed_ledger_sha256=observed,observation_unavailable_reason=observed_reason,
            before_sha256=before_hash,prepared_after_sha256=after_hash,
            prepared_after_unavailable_reason=None if after_hash is not None else 'Failure before final ledger serialization.',
            recovery_required=commit_state!='UNCHANGED_BEFORE')); raise'''
    assert source.count(before)==1;source=source.replace(before,after);ast.parse(source)
    new=ROOT/'acceleration/register_20261001_thirtieth_batches03_05_v3.py'
    with new.open('x',encoding='utf8',newline='\n')as f:f.write(source)
    oldspec=old.with_name(old.stem+'_spec.md');spec=new.with_name(new.stem+'_spec.md')
    with spec.open('x',encoding='utf8',newline='\n')as f:
        f.write(oldspec.read_text(encoding='utf8'))
        f.write('''
V3 changes only failure classification. The replacement Boolean is diagnostic:
actual observed live SHA256 determines UNCHANGED_BEFORE, REPLACED_WITH_EXPECTED_AFTER,
or UNKNOWN_OR_UNEXPECTED_BYTES. Any state except exact BEFORE requires a separate
recovery audit. Unavailable observations and unavailable prepared-after bytes
are explicit nulls with reasons. This closes the interrupt interval between
atomic replacement and assigning its diagnostic flag. No exception injection
or registrar execution has occurred during this preparation.
''')
    out=ROOT/'acceleration/results/20261001_thirtieth_registrar_v3_preparation';out.mkdir(exist_ok=False)
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        inputs_sha256={old.relative_to(ROOT).as_posix():h(old),oldspec.relative_to(ROOT).as_posix():h(oldspec),Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__))},
        outputs_sha256={new.relative_to(ROOT).as_posix():h(new),spec.relative_to(ROOT).as_posix():h(spec)},
        registrar_executed=False,ledger_mutations=0,mathematical_verification=False,validation='AST parse only.')
    with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result['outputs_sha256']))
if __name__=='__main__':main()
