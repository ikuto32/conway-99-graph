"""Select one unproved literal case per exact selector-size class."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import gzip,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
MAN=B+'exact_eight_campaign_preparation/campaign_manifest.json';INV=I+'exact_eight_campaign_inventory/summary.json';RECORDS=I+'exact_eight_campaign_inventory/independent_inventory.json.gz';PLAN='acceleration/theory_20260930_exact_eight_sizeclass16_plan.md'
GATES=[(I+'exact_eight_first12_proofs/summary.json','a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9',12),(I+'exact_eight_next32_proofs/summary.json','21ee1b189c8b250eabcaedad43a79b9025978d540a1480f1c03eaeb446acee4c',32)]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    assert h(MAN)=='e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba'and h(INV)=='555ef430f8a84b8b995c98566decf2c6cb92f9e8de6db1645955c0e48dd0f9ea'
    inv=read(INV);assert inv['outputs_sha256'][RECORDS]==h(RECORDS)=='b2b847af97c907e90ddb928b60958425e7b84fc6793c7297275a3ba7b9ef611a'
    universe=read(MAN);rows=universe['records'];byid={r['case_id']:r for r in rows};assert len(rows)==len(byid)==792
    measured=json.loads(gzip.decompress((ROOT/RECORDS).read_bytes()))['records'];assert [r['case_id']for r in measured]==[r['case_id']for r in rows]
    sizes={r['case_id']:r['computed_formula_dimensions']['selectors']for r in measured}
    for r in measured:assert sum(r['initial_domain_sizes'])==sizes[r['case_id']] and r['full_count_profile_sha256']==byid[r['case_id']]['full_count_profile_sha256']
    checked={p:h(p)for p in[MAN,INV,RECORDS,PLAN,Path(__file__).relative_to(ROOT).as_posix()]};done=[]
    for path,pin,count in GATES:
        assert h(path)==pin;checked[path]=pin;g=read(path);assert g['status'].endswith('_LITERAL_PROOFS_PASS')and g['completed_proof_replays']==count and not g['pending_case_ids']and not g['SAT_pending']and not g['UNKNOWN']
        for field in['inputs_sha256','outputs_sha256']:
            for p,s in g[field].items():assert h(p)==s,p;checked[p]=s
        assert len(g['case_records'])==count
        for r in g['case_records']:
            assert r['outcome']=='UNSAT_VERIFIED'and r['replay']['actual_exit_code']==0 and r['replay']['accepted']and r['trace']['complete_proof']
            assert byid[r['case_id']]['full_count_profile_sha256']==r['full_count_profile_sha256']and byid[r['case_id']]['case_index']==r['case_index'];done.append(r['case_id'])
    assert len(done)==len(set(done))==44 and {sizes[c]for c in done}=={2184}
    population=Counter(sizes.values());assert len(population)==16;chosen=[]
    for size in sorted(population):chosen.append(next(r for r in rows if r['case_id']not in set(done)and sizes[r['case_id']]==size))
    assert len(chosen)==len({r['case_id']for r in chosen})==16
    out=ROOT/(B+'exact_eight_sizeclass16_selection');out.mkdir(exist_ok=False)
    selection=dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',selection_policy='FIRST_UNPROVED_PER_SELECTOR_SIZE_CLASS_V1',campaign_manifest_path=MAN,campaign_manifest_sha256=h(MAN),ordered_case_ids=[r['case_id']for r in chosen],selection_reason='First unproved manifest member in each independently inventoried selector-size class; classes ordered by increasing selector count. No class-wide exclusion is inferred.',authorization_record_path=PLAN,authorization_record_sha256=h(PLAN),completed_proof_gates=[dict(path=p,sha256=s,completed_cases=n)for p,s,n in GATES],inventory_gate=dict(path=INV,sha256=h(INV)),inventory_records=dict(path=RECORDS,sha256=h(RECORDS)),skipped_verified_case_ids=done,population=792,unresolved_before_batch=748,selected_instances=16,selected_selector_sizes=[sizes[r['case_id']]for r in chosen],class_populations=[dict(selectors=s,cases=population[s])for s in sorted(population)])
    save(out/'selection.json',selection);receipt=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=checked,selection_path=(out/'selection.json').relative_to(ROOT).as_posix(),selection_sha256=h((out/'selection.json').relative_to(ROOT)),selected_case_indices=[r['case_index']for r in chosen],native_calls=0,producer_calls=0,scope='Allocation only. No new formula approval or class-wide feasibility/exclusion claim.')
    save(out/'summary.json',receipt);print(json.dumps(dict(selection_sha256=receipt['selection_sha256'],indices=receipt['selected_case_indices'],selector_sizes=selection['selected_selector_sizes'])))
if __name__=='__main__':main()
