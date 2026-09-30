"""Complete append-only v2 preparation after a Windows text-codec setup error."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';OUT=A/'results/20260930_exact_eight_campaign_native_preparation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def put(p,text):
    with p.open('x',encoding='utf8',newline='\n')as f:f.write(text)
def main():
    old=A/'native_20260930_exact_eight_campaign.py';new=A/'native_20260930_exact_eight_campaign_v2.py'
    oldspec=A/'native_20260930_exact_eight_campaign_spec.md';newspec=A/'native_20260930_exact_eight_campaign_v2_spec.md'
    helper=A/'prepare_20260930_exact_eight_campaign_native.py';helper2=A/'prepare_20260930_exact_eight_campaign_native_v2.py'
    before="    elif code==20:reason='UNSAT_TRACE_UNAVAILABLE_UNKNOWN'";after="    elif valid_unsat:reason='UNSAT_TRACE_UNAVAILABLE_UNKNOWN'"
    assert new.read_text(encoding='utf8')==old.read_text(encoding='utf8').replace(before,after)
    put(OUT/'correction_setup_failure.json',json.dumps(dict(status='CORRECTION_SETUP_TEXT_CODEC_FAILURE',source_path='acceleration/correct_20260930_exact_eight_campaign_native_preparation.py',source_sha256=sha(A/'correct_20260930_exact_eight_campaign_native_preparation.py'),error="UnicodeDecodeError: cp932 cannot decode UTF-8 spec at position40",partial_outputs=[key(OUT/'failure.json'),key(new)],recovery='Read unchanged original spec explicitly as UTF-8; preserve all prior files.',native_calls=0,preflight_calls=0),indent=2)+'\n')
    put(newspec,oldspec.read_text(encoding='utf8')+'''\n## Append-only v2 correction\n\nThe original source-only preparation failed two isolated outcome-label controls.\nBoth old branches conservatively stopped as UNKNOWN, but exit20 with a conflicting\nor duplicate status line was mislabeled as unavailable trace. V2 changes only the\ntrace-unavailable branch condition from exit20 to the exact valid-UNSAT predicate.\nContradictory native status now reaches the generic UNKNOWN status/resource branch.\nOriginal source/spec/helper/failure are retained unchanged. A subsequent text-codec\nsetup error reading the UTF-8 spec with Windows cp932 is also preserved. No native\nwrapper import, preflight or native call occurred during either preparation.\n''')
    h=helper.read_text(encoding='utf8').replace("native_20260930_exact_eight_campaign.py'","native_20260930_exact_eight_campaign_v2.py'").replace("20260930_exact_eight_campaign_native_preparation'","20260930_exact_eight_campaign_native_preparation_v2'")
    h=h.replace("if __name__=='__main__':main()", "if __name__=='__main__':\n    try:main()\n    except BaseException as ex:\n        if OUT.is_dir() and not(OUT/'failure.json').exists():(OUT/'failure.json').write_text(json.dumps(dict(error=repr(ex),source_sha256=sha(Path(__file__)),native_calls=0,runtime_repository_imports=0),indent=2)+'\\n',encoding='utf8')\n        raise")
    put(helper2,h)
    delta=dict(status='SOURCE_ONLY_V2_CORRECTION_COMPLETED',source_sha256=sha(Path(__file__)),original_inputs_sha256={key(p):sha(p)for p in[old,oldspec,helper]},outputs_sha256={key(p):sha(p)for p in[new,newspec,helper2]},literal_source_change=dict(before=before,after=after),failure_records={key(p):sha(p)for p in[OUT/'failure.json',OUT/'correction_setup_failure.json']},native_calls=0,preflight_calls=0)
    put(OUT/'correction.json',json.dumps(delta,indent=2)+'\n');print(json.dumps(delta))
if __name__=='__main__':main()
