"""Append-only v2 status-label correction; never imports the native wrapper."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'acceleration'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def put(p,text):
    with p.open('x',encoding='utf8',newline='\n')as f:f.write(text)
def main():
    old=A/'native_20260930_exact_eight_campaign.py';new=A/'native_20260930_exact_eight_campaign_v2.py'
    oldspec=A/'native_20260930_exact_eight_campaign_spec.md';newspec=A/'native_20260930_exact_eight_campaign_v2_spec.md'
    helper=A/'prepare_20260930_exact_eight_campaign_native.py';helper2=A/'prepare_20260930_exact_eight_campaign_native_v2.py'
    out=A/'results/20260930_exact_eight_campaign_native_preparation'
    assert out.is_dir() and not any(out.iterdir())
    failed=dict(status='SOURCE_ONLY_PREPARATION_CONTROL_FAILED',recorded_at=datetime.now(timezone.utc).isoformat(),retrospective_record=True,error='AssertionError at isolated outcome-parser expectation in prepare_20260930_exact_eight_campaign_native.py line16',failed_cases=[dict(actual_exit_code=20,stdout='s SATISFIABLE\n',trace_bytes=1),dict(actual_exit_code=20,stdout='s UNSATISFIABLE\ns UNSATISFIABLE\n',trace_bytes=1)],actual_label='UNSAT_TRACE_UNAVAILABLE_UNKNOWN',expected_label='UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME',safety_scope='Both original classifications were UNKNOWN and stop expansion; only the reason label was inaccurate.',original_inputs_sha256={key(p):sha(p)for p in[old,oldspec,helper]},runtime_repository_imports=0,preflight_calls=0,native_calls=0)
    put(out/'failure.json',json.dumps(failed,indent=2)+'\n')
    text=old.read_text();before="    elif code==20:reason='UNSAT_TRACE_UNAVAILABLE_UNKNOWN'";after="    elif valid_unsat:reason='UNSAT_TRACE_UNAVAILABLE_UNKNOWN'"
    assert text.count(before)==1
    put(new,text.replace(before,after))
    put(newspec,oldspec.read_text()+'''\n## Append-only v2 correction\n\nThe original source-only preparation failed two isolated outcome-label controls.\nBoth old branches conservatively stopped as UNKNOWN, but exit20 with a conflicting\nor duplicate status line was mislabeled as unavailable trace. V2 changes only the\ntrace-unavailable branch condition from exit20 to the exact valid-UNSAT predicate.\nContradictory native status now reaches the generic UNKNOWN status/resource branch.\nOriginal source/spec/helper/failure are retained unchanged. No native wrapper\nimport, preflight or native call occurred during that preparation.\n''')
    h=helper.read_text().replace("native_20260930_exact_eight_campaign.py'","native_20260930_exact_eight_campaign_v2.py'").replace("20260930_exact_eight_campaign_native_preparation'","20260930_exact_eight_campaign_native_preparation_v2'")
    h=h.replace("if __name__=='__main__':main()", "if __name__=='__main__':\n    try:main()\n    except BaseException as ex:\n        if OUT.is_dir() and not(OUT/'failure.json').exists():(OUT/'failure.json').write_text(json.dumps(dict(error=repr(ex),source_sha256=sha(Path(__file__)),native_calls=0,runtime_repository_imports=0),indent=2)+'\\n',encoding='utf8')\n        raise")
    put(helper2,h)
    delta=dict(status='SOURCE_ONLY_V2_CORRECTION_RECORDED',source_sha256=sha(Path(__file__)),original_inputs_sha256=failed['original_inputs_sha256'],outputs_sha256={key(p):sha(p)for p in[new,newspec,helper2]},literal_source_change=dict(before=before,after=after),original_failure_sha256=sha(out/'failure.json'),native_calls=0,preflight_calls=0)
    put(out/'correction.json',json.dumps(delta,indent=2)+'\n');print(json.dumps(delta))
if __name__=='__main__':main()
