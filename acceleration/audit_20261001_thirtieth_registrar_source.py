"""Source-only review of the unexecuted wave30 registrar; never import it."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
SRC='acceleration/register_20261001_thirtieth_batches03_05.py'
SPEC='acceleration/register_20261001_thirtieth_batches03_05_spec.md'
PINS={SRC:'121d2646bc47c2112f71059dce6bc6e9ea86d428cf36d8d9d373032a61493852',SPEC:'7ad8c4122efd9d2654162cf5092213a226d08ab6c18e86319e6a842408aa4a6d'}
OUT='acceleration/results/20261001_independent_review/thirtieth_registrar_source_review'

def need(v,m):
    if not v:raise ValueError(m)

def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def read(p):PINS[p]=h(p);return json.loads((ROOT/p).read_bytes())

def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')

def main():
    out=ROOT/OUT;out.mkdir(parents=True,exist_ok=False)
    for p,d in list(PINS.items()):need(h(p)==d,'frozen identity '+p)
    text=(ROOT/SRC).read_text(encoding='utf8');tree=ast.parse(text)
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    main=function_source=ast.get_source_segment(text,functions['main'])
    need("need((ROOT/'CLAIMS.yaml').read_bytes()==before,'unchanged live ledger before write'); (ROOT/'CLAIMS.yaml').write_bytes(after); save(out/'summary.json',result)"in main,'literal nontransactional write ordering')
    need(not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in ('replace','rename')for n in ast.walk(functions['main'])),'no atomic rename call')
    need("save(out/'failure.json',dict(error=repr(ex),checked_input_bindings=bindings))"in main,'failure receipt lacks observed ledger hash/commit state')
    patterns=["need(len(args.cohort)==6,'exact six bound additions')","need([r['id'] for r in rows]==list(EXPECTED),'exact identities in dependency order')","need(data['claims'][:-6]==old['claims'] and data['artifacts'][:-12]==old['artifacts'],'all previous records unchanged')","premise['revision']==dep['revision'] and premise['status']=='VERIFIED' and premise['review_state']=='CLEAR'","len(old['claims'])==300","len(data['claims'])==306"]
    need(all(x in main for x in patterns),'identity/dependency/old-object validation structure')
    source_compare=ast.get_source_segment(text,functions['compare_batch'])
    need("len(enc['skipped_verified_case_ids'])==60+64*(batch-1)"in source_compare and "len(allids)==len(set(allids))==192"in source_compare,'192 disjoint identities and preceding counts')
    records=[];rows=[]
    for suffix,folder,status in [('GRAM-ENCODINGS','cnfs_v3','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS'),('LITERAL-PROFILE-EXCLUSIONS','proofs','INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS')]:
        d='acceleration/results/20261001_independent_review/exact_eight_prefix64_batch03_'+folder
        report=read(d+'/summary.json');row=read(d+'/claim_binding.json')
        need(row['id']=='C-FIXED-HADAMARD-EXACT-EIGHT-PREFIX64-BATCH03-'+suffix and row['verifier']=='/root/structural_attack','actual03 binding identity')
        need(row['revision']==1 and row['status']=='VERIFIED' and row['review_state']=='CLEAR' and report['status']==status,'actual03 bound states')
        need(all(row[k]for k in ['statement','scope','assumptions','dependencies','method','shared_components','created_at','updated_at']),'bound original fields present')
        records.append(report);rows.append(row)
    enc,proof=records;er,pr=rows
    need(er['checked_cases']==enc['checked_cases']and pr['case_records']==proof['case_records'],'literal binding/report case populations')
    ids=[r['case_id']for r in enc['checked_cases']]
    need(len(ids)==len(set(ids))==64 and ids==enc['selected_case_ids']==proof['selected_case_ids']==[r['case_id']for r in proof['case_records']],'actual03 case identity order')
    for a,b in zip(enc['checked_cases'],proof['case_records'],strict=True):
        need(all(a[k]==b[k]for k in ['case_id','case_index','subset_index','full_count_profile_sha256','cnf_path','cnf_sha256','scope_path','scope_sha256']),'actual03 formula/count/scope alignment')
    need(len(enc['skipped_verified_case_ids'])==len(set(enc['skipped_verified_case_ids']))==188 and set(ids).isdisjoint(enc['skipped_verified_case_ids']),'actual03 complete distinct skip population')
    need(pr['dependencies']==[{'id':er['id'],'revision':1,'relation':'encoding_equivalence'}],'actual03 proof depends on exact encoding')
    prep=read('acceleration/results/20261001_thirtieth_registrar_preparation/summary.json');need(prep['registrar_executed']is False and prep['ledger_mutations']==0 and prep['outputs_sha256'][SRC]==PINS[SRC],'unexecuted preparation record')
    PINS[Path(__file__).relative_to(ROOT).as_posix()]=h(Path(__file__).relative_to(ROOT));sp=Path(__file__).with_name(Path(__file__).stem+'_spec.md');PINS[sp.relative_to(ROOT).as_posix()]=h(sp.relative_to(ROOT))
    result=dict(status='INDEPENDENT_THIRTIETH_REGISTRAR_SOURCE_REVIEW_CHANGES_REQUESTED',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=PINS,registrar_imported=False,registrar_executed=False,mathematical_verification=False,ledger_writes=0,git_writes=0,reviewed_source_only=True,
        finding=dict(id='NONATOMIC_LIVE_LEDGER_WRITE',severity='execution safety',statement='The live ledger is truncated and written with Path.write_bytes before summary.json is saved. A partial-write failure may leave a truncated ledger; a later receipt failure can leave a changed ledger without success receipt. Failure output does not classify the observed commit state.',location_lines=[n.lineno for n in ast.walk(functions['main'])if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='write_bytes'],not_observed_incident=True,not_mathematical_refutation=True,recommendation='Prepare complete before/after snapshots and a transaction journal before same-directory atomic replacement; final and failure receipts must record the observed live hash and recovery route.'),
        checked=['Exact ordered six report/binding paths and independent statuses','300-to306 population and six VERIFIED additions','Original statement/scope/assumptions/dependency/shared-component preservation','Dependencies require exact current VERIFIED/CLEAR revisions','All prior claim/artifact objects must remain equal before schema/impact validation','Actual batch03 binding/report alignment for64 literal cases and188 distinct skips','Missing/unpinned batch04 or05 artifacts fail before the live-write section','Protected path guard precedes hashing via safe()'],
        limitations=['No registrar helper imported or executed. No simulated disk or OS fault injected. Finding follows literal source operation order.','Only batch03 current reports were inspected; batch04/05 approval and raw artifacts remain required at actual registration.','No mathematical reapproval or claim refutation; no ledger/index/Git changes.','Source hardening must receive its own review; this result does not approve a future replacement.'])
    save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],sha256=h(OUT+'/summary.json'))))
if __name__=='__main__':main()
