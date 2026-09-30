"""Freeze the next32 literal cases, skipping only authenticated completed proofs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
MAN=B+'exact_eight_campaign_preparation/campaign_manifest.json'
GATE=B+'independent_review/exact_eight_first12_proofs/summary.json'
PLAN='acceleration/theory_20260930_exact_eight_next32_plan.md'
def h(p):
    with (ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
    assert h(MAN)=='e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba'
    assert h(GATE)=='a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9'
    u=read(MAN);g=read(GATE);assert g['status']=='INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS'
    assert g['completed_proof_replays']==12 and not g['pending_case_ids'] and not g['SAT_pending'] and not g['UNKNOWN']
    byid={r['case_id']:r for r in u['records']};assert len(byid)==792
    checked={MAN:h(MAN),GATE:h(GATE),PLAN:h(PLAN),Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__).relative_to(ROOT))}
    for field in ['inputs_sha256','outputs_sha256']:
        for p,s in g[field].items():assert h(p)==s,p;checked[p]=s
    done=[]
    for r in g['case_records']:
        assert r['outcome']=='UNSAT_VERIFIED' and r['replay']['actual_exit_code']==0
        assert byid[r['case_id']]['full_count_profile_sha256']==r['full_count_profile_sha256']
        assert byid[r['case_id']]['case_index']==r['case_index'];done.append(r['case_id'])
    assert len(done)==len(set(done))==12 and set(done)==set(g['selected_case_ids'])
    remaining=[r for r in u['records']if r['case_id']not in set(done)];assert len(remaining)==780
    chosen=remaining[:32];out=ROOT/(B+'exact_eight_next32_selection');out.mkdir(exist_ok=False)
    selection=dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',campaign_manifest_path=MAN,campaign_manifest_sha256=h(MAN),ordered_case_ids=[r['case_id']for r in chosen],selection_reason='First32 manifest-ordered instances after removing only the12 independently proved campaign literal cases.',authorization_record_path=PLAN,authorization_record_sha256=h(PLAN),completed_proof_gate_path=GATE,completed_proof_gate_sha256=h(GATE),skipped_verified_case_ids=done,population=792,unresolved_before_batch=780,selected_instances=32)
    (out/'selection.json').write_text(json.dumps(selection,indent=2)+'\n',encoding='utf8')
    receipt=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=checked,selection_path=(out/'selection.json').relative_to(ROOT).as_posix(),selection_sha256=h((out/'selection.json').relative_to(ROOT)),selected_case_indices=[r['case_index']for r in chosen],native_calls=0,producer_calls=0,scope='Selection only; no new formula approval, proof replay or mathematical exclusion.')
    (out/'summary.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(selection_sha256=receipt['selection_sha256'],indices=receipt['selected_case_indices'])))
if __name__=='__main__':main()
