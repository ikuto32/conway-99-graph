"""Explicit ten-case continuation and separately authenticated32-case aggregation."""
import argparse,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
ORIGINAL=B/'20260930_exact_eight_next32_selection/selection.json';FIRST=B/'20260930_exact_eight_next32_cnfs/summary.json'
SELECT=B/'20260930_exact_eight_next32_continuation_selection';SECOND=B/'20260930_exact_eight_next32_continuation_cnfs/summary.json';OUT=B/'20260930_exact_eight_next32_consolidated'
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def first():
    assert sha(ORIGINAL)=='b906256dcf706c7d03360cc2cb7e31e5dd09b52cec3ba994ae9600954aeb88cd'and sha(FIRST)=='ce844c0ef6d0fce544ff707fff86740e4957223c7d3fb064bcbe9369f0234cf7'
    s=read(ORIGINAL);r=read(FIRST);assert r['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_PARTIAL'and r['completed_formulas']==22 and len(r['pending_case_ids'])==10
    assert [x['case_id']for x in r['records']]+r['pending_case_ids']==s['ordered_case_ids']and r['native_calls']==0
    return s,r
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['select','consolidate']);args=ap.parse_args();original,a=first();stamp=datetime.now(timezone.utc).isoformat()
    provenance=dict(timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=sha(Path(__file__)),inputs_sha256={key(ORIGINAL):sha(ORIGINAL),key(FIRST):sha(FIRST)})
    if args.mode=='select':
        SELECT.mkdir(exist_ok=False)
        plan=SELECT/'continuation_plan.md'
        with plan.open('x',encoding='utf8',newline='\n')as f:f.write('# Explicit next32 build continuation\n\nThe original120-second invocation completed22 of32 formulas and preserved ten pending IDs. This fresh invocation selects exactly those pending IDs in original order, with a fresh120-second budget and output directory. It does not extend the earlier deadline or change any mathematical acceptance criterion. All32 require a new complete independent encoding audit before native execution. Preserve original partial records and any unfinished files. No automatic retry or skip; any subsequent failure needs another explicit decision. The original native allocation and limits remain unchanged.\n')
        s=dict(original);s['ordered_case_ids']=a['pending_case_ids'];s['selection_reason']='Explicit root continuation of the ten pending build IDs after the preserved120-second partial invocation; no mathematical result inferred.';s['authorization_record_path']=key(plan);s['authorization_record_sha256']=sha(plan);s['parent_selection_path']=key(ORIGINAL);s['parent_selection_sha256']=sha(ORIGINAL);s['partial_build_path']=key(FIRST);s['partial_build_sha256']=sha(FIRST);s['counts']=dict(parent_selected=32,previously_completed_builds=22,selected_pending_builds=10)
        save(SELECT/'selection.json',s);save(SELECT/'summary.json',dict(provenance,outputs_sha256={key(p):sha(p)for p in SELECT.iterdir()},native_calls=0,producer_calls=0));print(json.dumps(dict(selection_sha256=sha(SELECT/'selection.json'),pending=len(s['ordered_case_ids']))));return
    selection=SELECT/'selection.json';s=read(selection);assert s['ordered_case_ids']==a['pending_case_ids'];b=read(SECOND)
    assert b['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'and b['completed_formulas']==10 and b['pending_case_ids']==[]and b['native_calls']==0 and b['selected_case_ids']==s['ordered_case_ids']
    records=a['records']+b['records'];assert [x['case_id']for x in records]==original['ordered_case_ids']and len({x['case_id']for x in records})==32
    for summary in [a,b]:
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():assert sha(ROOT/p)==h,p
    for r in records:
        for f in r['files'].values():assert sha(ROOT/f['path'])==f['sha256']and(ROOT/f['path']).stat().st_size==f['bytes']
    OUT.mkdir(exist_ok=False);provenance['inputs_sha256'].update({key(SECOND):sha(SECOND),key(selection):sha(selection),key(SELECT/'continuation_plan.md'):sha(SELECT/'continuation_plan.md')})
    save(OUT/'summary.json',dict(provenance,status='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE',schema='EXACT_EIGHT_EXPLICIT_BUILD_CONSOLIDATION_V1',records=records,selected_case_ids=original['ordered_case_ids'],completed_formulas=32,pending_case_ids=[],native_calls=0,producer_calls=sum(x['producer_calls']for x in[a,b]),build_summaries=[dict(path=key(p),sha256=sha(p))for p in[FIRST,SECOND]],continuation_selections=[dict(path=key(selection),sha256=sha(selection))],original_selection=dict(path=key(ORIGINAL),sha256=sha(ORIGINAL)),automatic_resume=False,automatic_skip=False,independent_approval=False,limitations=['Artifact identity aggregation only; no new encoding, native outcome, or mathematical approval.','The partial first invocation remains partial and is not rewritten.']))
    print(json.dumps(dict(completed=32,summary_sha256=sha(OUT/'summary.json'))))
if __name__=='__main__':main()
