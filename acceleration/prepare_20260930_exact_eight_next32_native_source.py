"""Create a new next32 native source from frozen first12 v2; no wrapper import."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';OLD=A/'native_20260930_exact_eight_campaign_v2.py';NEW=A/'native_20260930_exact_eight_next32.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,t):
    with p.open('x',encoding='utf8',newline='\n')as f:f.write(t)
assert sha(OLD)=='e4a406a8b6f77db93257bc9a6265ffa0c7944af26d4a77e2b7017c67ef3dce2f'
t=OLD.read_text(encoding='utf8')
t=t.replace('first12 sequential','next32 sequential').replace("20260930_exact_eight_first12_cnfs/summary.json","20260930_exact_eight_next32_cnfs/summary.json").replace("20260930_independent_review/exact_eight_campaign/summary.json","20260930_independent_review/exact_eight_next32_cnfs/summary.json")
t=t.replace('INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS','INDEPENDENT_EXACT_EIGHT_NEXT32_ENCODING_PASS').replace('INDEPENDENT_EXACT_EIGHT_CAMPAIGN_OBJECT_CALIBRATION_PASS','INDEPENDENT_EXACT_EIGHT_NEXT32_OBJECT_CALIBRATION_PASS')
t=t.replace('first_batch_allocated_native_wall_seconds=720,maximum_cases=12','first_batch_allocated_native_wall_seconds=1920,maximum_cases=32')
t=t.replace("PINS={BATCH:'3f7abda7d7e12a6babaf48c6c690f85bf1db69e6401098f2ece9a881b1772136',UNIVERSE:","PINS={UNIVERSE:")
mark='PINS.update(producer.PINS)'
addition="""
SELECTION=B/'20260930_exact_eight_next32_selection/selection.json'
NEXT_PLAN=ROOT/'acceleration/theory_20260930_exact_eight_next32_plan.md'
PRIOR_PROOFS=B/'20260930_independent_review/exact_eight_first12_proofs/summary.json'
PINS.update({SELECTION:'b906256dcf706c7d03360cc2cb7e31e5dd09b52cec3ba994ae9600954aeb88cd',NEXT_PLAN:'b91ff543c53b223b8db55d03d04a9266ffaca71b43bdbca10d85ddfa607bbd42',PRIOR_PROOFS:'a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9'})

def validate_next32(u,selection,prior):
    ids=[r['case_id']for r in u['records']];h.require(len(ids)==len(set(ids))==792 and u['universe_size']==792,'all792 distinct cases')
    h.require(not u['historical_profiles_subtracted']and not u['prior_exclusions_used'],'original population unchanged')
    h.require(prior['status']=='INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS'and prior['completed_proof_replays']==12 and prior['completed_attempts']==12 and prior['SAT_pending']==prior['UNKNOWN']==0 and not prior['pending_case_ids'],'complete independent first12 proof premise')
    old=prior['case_records'];oldids=[r['case_id']for r in old];h.require(oldids==prior['selected_case_ids']==u['first_batch_case_ids']and len(oldids)==len(set(oldids))==12,'exact previously verified12, no other subtraction')
    byid={r['case_id']:r for r in u['records']}
    for r in old:
        w=byid[r['case_id']];h.require(r['case_index']==w['case_index']and r['subset_index']==w['subset_index']and r['full_count_profile_sha256']==w['full_count_profile_sha256'],'prior proof literal membership')
        h.require(r['outcome']=='UNSAT_VERIFIED'and r['trace']['complete_proof']and r['replay']['accepted']and r['replay']['actual_exit_code']==0,'prior proof actually verified')
    expected=[cid for cid in ids if cid not in set(oldids)][:32]
    h.require(selection['schema']=='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1'and selection['campaign_manifest_path']==h.key(UNIVERSE)and selection['campaign_manifest_sha256']==PINS[UNIVERSE],'exact selection manifest')
    h.require(selection['authorization_record_path']==h.key(NEXT_PLAN)and selection['authorization_record_sha256']==PINS[NEXT_PLAN]and selection['completed_proof_gate_path']==h.key(PRIOR_PROOFS)and selection['completed_proof_gate_sha256']==PINS[PRIOR_PROOFS],'selection authorization and proof gate')
    h.require(selection['skipped_verified_case_ids']==oldids and selection['ordered_case_ids']==expected and len(set(expected))==32,'exact next32 order')
    h.require((selection['population'],selection['unresolved_before_batch'],selection['selected_instances'])==(792,780,32),'selection cardinalities')
    return expected
"""
t=t.replace(mark,mark+addition)
start=t.index("    h.require(args.encoding_gate.resolve()==ENCODING_GATE.resolve(),")
end=t.index('    for r in records:',start)
oldblock=t[start:end]
newblock="""    h.require(args.encoding_gate.resolve()==ENCODING_GATE.resolve(),'exact next32 independent encoding report')
    h.require(digest(BATCH)==args.batch_summary_sha256,'explicit exact32 build summary');bindings[h.key(BATCH)]=args.batch_summary_sha256
    h.require(e.AS_LIMIT==LIMITS['address_space_bytes'],'unchanged4GiB address-space helper')
    h.require('--seed=0..2e9              random seed [0]'in SEED_HELP.read_text(),'authenticated actual default seed0')
    u=h.read(UNIVERSE);selection=h.read(SELECTION);prior=h.checked_gate(PRIOR_PROOFS,PINS[PRIOR_PROOFS],'INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS');ids=validate_next32(u,selection,prior);batch=h.read(BATCH);records=batch['records'];byid={r['case_id']:r for r in u['records']}
    for r in prior['case_records']:
        for field in['cnf','scope','run_summary','native_receipt']:
            p=ROOT/r[field+'_path'];v=r[field+'_sha256'];h.require(digest(p)==v and prior['inputs_sha256'].get(h.key(p))==v,'prior verified literal input/receipt');bindings[h.key(p)]=v
        p=ROOT/r['trace']['path'];v=r['trace']['sha256'];h.require(digest(p)==v and p.stat().st_size==r['trace']['bytes']and prior['inputs_sha256'].get(h.key(p))==v,'prior complete checked proof identity');bindings[h.key(p)]=v
        oldscope=h.read(ROOT/r['scope_path']);h.require(oldscope['campaign_case_id']==r['case_id']and oldscope['coordinate_group_fibre_counts']==byid[r['case_id']]['raw_representative']['counts'],'prior exact raw-count scope')
    h.require(batch['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'and batch['completed_formulas']==32 and not batch['pending_case_ids']and batch['native_calls']==0,'all32 literal formulas built')
    h.require(batch['selected_case_ids']==ids==[r['case_id']for r in records]and len(ids)==len(set(ids))==32,'exact selected32 build order')
    h.require(batch['inputs_sha256'].get(h.key(SELECTION))==PINS[SELECTION],'build exact selection pin')
    direct={BATCH,UNIVERSE,SELECTION,NEXT_PLAN,PRIOR_PROOFS,producer.RAW,producer.LOCAL,producer.PLAN,Path(producer.__file__),producer.SPEC,producer.BLOCK_GATE,producer.BLOCK_SUMMARY}
"""
t=t.replace(oldblock,newblock)
t=t.replace("reports[0]['complete_formulas']==12","reports[0]['complete_formulas']==32")
t=t.replace("desc='Native first12 exact-eight cases'","desc='Native next32 exact-eight cases'").replace("stop='ALL_FIRST12_ATTEMPTED'","stop='ALL_NEXT32_ATTEMPTED'")
t=t.replace('Allocated720s covers12x60','Allocated1920s covers32x60')
t=t.replace("for n in ['encoding-gate-sha256','object-gate-sha256','attempt-id']:","for n in ['encoding-gate-sha256','object-gate-sha256','batch-summary-sha256','attempt-id']:")
t=t.replace("EXACT_EIGHT_CAMPAIGN_", "EXACT_EIGHT_NEXT32_")
# The blanket label replacement affects statuses only; no inherited first12 gate survives.
put(NEW,t)
print(json.dumps(dict(source_path=NEW.relative_to(ROOT).as_posix(),source_sha256=sha(NEW),preserved_source_sha256=sha(OLD),native_calls=0,preflight_calls=0)))
