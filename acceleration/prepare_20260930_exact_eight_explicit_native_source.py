"""Freeze reusable explicit-batch wrapper from immutable next32 native source."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';OLD=A/'native_20260930_exact_eight_next32_v2.py';NEW=A/'native_20260930_exact_eight_explicit_batch.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD)=='54da0724f5350a8eb77590943b373c26ded5b55d568f92664334b8a5dd4754c3'
t=OLD.read_text(encoding='utf8').replace('Gated next32 sequential native attempts','Gated explicit1..64 sequential native attempts')
t=t.replace("ENCODING_GATE=B/'20260930_independent_review/exact_eight_next32_cnfs/summary.json'\n",'')
t=t.replace('INDEPENDENT_EXACT_EIGHT_NEXT32_','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_').replace('first_batch_allocated_native_wall_seconds=1920,maximum_cases=32','maximum_cases=64,allocation_rule=\'60 times selected case count\'')
start=t.index("SELECTION=B/'20260930_exact_eight_next32_selection/selection.json'");end=t.index('\ndef source_closure():',start)
t=t[:start]+'''SELECTION=None

def allocation_seconds(n):
    h.require(type(n)is int and 1<=n<=LIMITS['maximum_cases'],'selected-case count1..64')
    return LIMITS['native_wall_seconds_per_attempt']*n

def validate_selection(u,selection):
    allids=[r['case_id']for r in u['records']];h.require(len(allids)==len(set(allids))==792 and u['universe_size']==792,'complete792 universe')
    h.require(not u['historical_profiles_subtracted']and not u['prior_exclusions_used'],'original population remains unchanged')
    h.require(selection['schema']=='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1'and selection['campaign_manifest_path']==h.key(UNIVERSE)and selection['campaign_manifest_sha256']==PINS[UNIVERSE],'exact explicit selection manifest')
    ids=selection['ordered_case_ids'];h.require(type(ids)is list and all(type(cid)is str for cid in ids),'literal ordered case list');allocation_seconds(len(ids))
    h.require(len(ids)==len(set(ids))and all(cid in set(allids)for cid in ids),'distinct literal universe members')
    h.require(type(selection['selection_reason'])is str and bool(selection['selection_reason'].strip()),'explicit scientific selection provenance')
    if 'selected_instances'in selection:h.require(selection['selected_instances']==len(ids),'declared selection count')
    return list(ids)

def selection_authorization(selection):
    name=selection['authorization_record_path'];expected=selection['authorization_record_sha256']
    h.require(type(name)is str and name and not Path(name).is_absolute()and '..'not in Path(name).parts,'relative authorization record')
    p=(ROOT/name).resolve();h.require(p.is_relative_to(ROOT)and h.key(p)==name and p.is_file(),'exact repository authorization record')
    h.require(type(expected)is str and re.fullmatch('[0-9a-f]{64}',expected),'explicit authorization SHA')
    return p,expected

''' +t[end:]
start=t.index("    h.require(args.encoding_gate.resolve()==ENCODING_GATE.resolve(),");end=t.index('    for r in records:',start)
t=t[:start]+'''    h.require(digest(BATCH)==args.batch_summary_sha256,'explicit complete build consolidation');bindings[h.key(BATCH)]=args.batch_summary_sha256
    h.require(digest(SELECTION)==args.selection_sha256,'explicit frozen selection');bindings[h.key(SELECTION)]=args.selection_sha256
    h.require(e.AS_LIMIT==LIMITS['address_space_bytes'],'unchanged4GiB address-space helper')
    h.require('--seed=0..2e9              random seed [0]'in SEED_HELP.read_text(),'authenticated actual default seed0')
    u=h.read(UNIVERSE);selection=h.read(SELECTION);ids=validate_selection(u,selection);authorization,authorization_sha=selection_authorization(selection)
    h.require(digest(authorization)==authorization_sha,'exact selection authorization');bindings[h.key(authorization)]=authorization_sha
    batch=h.read(BATCH);records=batch['records'];byid={r['case_id']:r for r in u['records']}
    h.require(batch['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'and batch['completed_formulas']==len(ids)and not batch['pending_case_ids']and batch['native_calls']==0,'all explicitly selected literal formulas built')
    h.require(batch['selected_case_ids']==ids==[r['case_id']for r in records]and len(ids)==len(set(ids)),'exact explicit build order without skipping')
    h.require(batch['inputs_sha256'].get(h.key(SELECTION))==args.selection_sha256,'build exact selection pin')
    direct={BATCH,UNIVERSE,SELECTION,authorization,producer.RAW,producer.LOCAL,producer.PLAN,Path(producer.__file__),producer.SPEC,producer.BLOCK_GATE,producer.BLOCK_SUMMARY}
''' +t[end:]
t=t.replace("reports[0]['complete_formulas']==32","reports[0]['complete_formulas']==len(ids)")
needle="    h.require(reports[1]['inputs_sha256'].get(h.key(args.encoding_gate))==args.encoding_gate_sha256,'same exact encoding gate')"
t=t.replace(needle,needle+"\n    h.require(reports[0]['selection_path']==h.key(SELECTION)and reports[0]['selection_sha256']==args.selection_sha256 and reports[0]['batch_summary_path']==h.key(BATCH)and reports[0]['batch_summary_sha256']==args.batch_summary_sha256,'same independently approved explicit selection and consolidation')")
t=t.replace('    global BATCH\n','    global BATCH,SELECTION\n').replace("BATCH=args.batch_summary.resolve();h.require(BATCH.is_relative_to(ROOT)and BATCH.is_file(),'explicit repository-contained complete32 consolidation')","BATCH=args.batch_summary.resolve();SELECTION=args.selection.resolve()\n    h.require(all(p.is_relative_to(ROOT)and p.is_file()for p in[BATCH,SELECTION]),'explicit repository-contained selection/consolidation')")
t=t.replace("bindings,records=preflight(args);selection=[r['case_id']for r in records];initial=", "bindings,records=preflight(args);selection=[r['case_id']for r in records];allocated_limit=allocation_seconds(len(selection));initial=")
t=t.replace("manifest=dict(build_consolidation_path=", "manifest=dict(explicit_selection_path=h.key(SELECTION),explicit_selection_sha256=args.selection_sha256,selected_case_count=len(selection),allocated_native_wall_limit_seconds=allocated_limit,build_consolidation_path=")
t=t.replace("selected_case_ids=selection,limits=LIMITS,seed=SEED,native_calls=0","selected_case_ids=selection,selected_case_count=len(selection),allocated_native_wall_limit_seconds=allocated_limit,limits=LIMITS,seed=SEED,native_calls=0")
t=t.replace("base=dict(inputs_sha256=bindings,selected_case_ids=selection,", "base=dict(inputs_sha256=bindings,selected_case_ids=selection,selected_case_count=len(selection),allocated_native_wall_limit_seconds=allocated_limit,explicit_selection_path=h.key(SELECTION),explicit_selection_sha256=args.selection_sha256,")
t=t.replace("LIMITS['first_batch_allocated_native_wall_seconds']","allocated_limit")
t=t.replace('ALL_NEXT32_ATTEMPTED','ALL_EXPLICITLY_SELECTED_CASES_ATTEMPTED').replace("desc='Native next32 exact-eight cases'","desc='Native explicit exact-eight cases'").replace('EXACT_EIGHT_NEXT32_','EXACT_EIGHT_EXPLICIT_BATCH_')
t=t.replace('Allocated1920s covers32x60 native limits; actual wrapped, transfer and verification overhead are recorded separately.','The explicit selectedN allocates60*N native seconds, N1..64; actual wrapped, transfer and verification overhead are recorded separately. No universe completion is inferred.')
t=t.replace("['out','batch-summary','encoding-gate','object-gate','object-checker']","['out','selection','batch-summary','encoding-gate','object-gate','object-checker']").replace("['encoding-gate-sha256','object-gate-sha256','batch-summary-sha256','attempt-id']","['selection-sha256','encoding-gate-sha256','object-gate-sha256','batch-summary-sha256','attempt-id']")
ast.parse(t)
with NEW.open('x',encoding='utf8',newline='\n')as f:f.write(t)
print(json.dumps(dict(source=NEW.relative_to(ROOT).as_posix(),sha256=sha(NEW),prior_source_sha256=sha(OLD),native_calls=0,preflight_calls=0)))
