"""Freeze next64 and four disjoint build selections; aggregate only exact receipts."""
import argparse,hashlib,json,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
MAN=B+'exact_eight_campaign_preparation/campaign_manifest.json'
PLAN='acceleration/theory_20260930_exact_eight_next64_plan.md'
OUT=B+'exact_eight_next64_selection'
GATES=[('exact_eight_first12_proofs','a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9',12,'SAT_pending'),('exact_eight_next32_proofs','21ee1b189c8b250eabcaedad43a79b9025978d540a1480f1c03eaeb446acee4c',32,'SAT_verified'),('exact_eight_sizeclass16_proofs','04d47a627081f42def048826f08bdf2574eff67479275d46112033bf994e4494',16,'SAT_verified')]
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with(ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def ref(p):return dict(path=p,sha256=h(p))
def provenance():return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_sha256=h(Path(__file__).relative_to(ROOT)),native_calls=0,independent_approval=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['select','consolidate']);ap.add_argument('--build-summary',nargs=2,action='append',metavar=('PATH','SHA256'));args=ap.parse_args()
    if args.mode=='select':
        assert not args.build_summary
        assert h(MAN)=='e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba'
        records=read(MAN)['records'];byid={r['case_id']:r for r in records};assert len(records)==len(byid)==792
        checked={p:h(p)for p in[MAN,PLAN,'uv.lock','pyproject.toml']};done=[];grefs=[]
        for name,pin,n,satkey in GATES:
            p=B+'independent_review/'+name+'/summary.json';assert h(p)==pin;g=read(p)
            assert g['status'].startswith('INDEPENDENT_')and g['status'].endswith('LITERAL_PROOFS_PASS')
            assert g['completed_proof_replays']==n and not g['pending_case_ids']and not g[satkey]and not g['UNKNOWN']
            checked[p]=pin
            for field in ['inputs_sha256','outputs_sha256']:
                for q,v in g[field].items():assert h(q)==v,q;assert q not in checked or checked[q]==v;checked[q]=v
            ids=[]
            for r in g['case_records']:
                assert r['outcome']=='UNSAT_VERIFIED'and r['replay']['actual_exit_code']==0
                assert byid[r['case_id']]['full_count_profile_sha256']==r['full_count_profile_sha256']
                assert byid[r['case_id']]['case_index']==r['case_index'];ids.append(r['case_id'])
            assert len(ids)==len(set(ids))==n and set(ids)==set(g['selected_case_ids'])and not set(ids)&set(done)
            done+=ids;grefs.append(dict(path=p,sha256=pin,completed_cases=n))
        assert len(done)==60
        remaining=[r for r in records if r['case_id']not in set(done)];assert len(remaining)==732;chosen=remaining[:64]
        selection=dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',selection_policy='FIRST_UNPROVED_MANIFEST_PREFIX_V1',campaign_manifest_path=MAN,campaign_manifest_sha256=h(MAN),ordered_case_ids=[r['case_id']for r in chosen],selection_reason='First64 manifest-ordered instances after removing only the60 independently proved first12, next32 and sizeclass16 literal cases.',authorization_record_path=PLAN,authorization_record_sha256=h(PLAN),completed_proof_gates=grefs,skipped_verified_case_ids=done,population=792,unresolved_before_batch=732,selected_instances=64)
        (ROOT/OUT).mkdir(exist_ok=False);parent=OUT+'/selection.json';save(parent,selection);parts=[]
        for i in range(4):
            child=dict(selection);child.update(selection_policy='AUTHORIZED_DISJOINT_BUILD_PARTITION_V1',ordered_case_ids=selection['ordered_case_ids'][16*i:16*(i+1)],selection_reason=f'Authorized ordered16-case build partition{i} of the parent64 selection; no new proof or skip inference.',parent_selection_path=parent,parent_selection_sha256=h(parent),partition_index=i,partition_offset=16*i,selected_instances=16)
            p=OUT+f'/partition_{i:02d}.json';save(p,child);parts.append(ref(p))
        save(OUT+'/summary.json',dict(provenance(),inputs_sha256=checked,outputs_sha256={p:h(p)for p in[parent,*[x['path']for x in parts]]},selection=ref(parent),build_selections=parts,selected_case_indices=[r['case_index']for r in chosen],producer_calls=0,scope='Selection and partition identities only; no new mathematical approval.'))
        print(json.dumps(dict(selection=ref(parent),build_selections=parts,indices=[r['case_index']for r in chosen])));return
    assert args.build_summary and len(args.build_summary)==4
    parent=OUT+'/selection.json';original=read(parent);parts=[OUT+f'/partition_{i:02d}.json'for i in range(4)]
    allrecords=[];checks={p:h(p)for p in[parent,*parts]};summaries=[];calls=0
    for i,((p,pin),part)in enumerate(zip(args.build_summary,parts,strict=True)):
        assert h(p)==pin;checks[p]=pin;s=read(part);b=read(p)
        assert s['parent_selection_path']==parent and s['parent_selection_sha256']==h(parent)
        assert s['partition_index']==i and s['partition_offset']==16*i and s['ordered_case_ids']==original['ordered_case_ids'][16*i:16*(i+1)]
        assert b['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'and b['completed_formulas']==16 and not b['pending_case_ids']and b['native_calls']==0
        assert b['selected_case_ids']==s['ordered_case_ids']==[r['case_id']for r in b['records']]
        for field in ['inputs_sha256','outputs_sha256']:
            for q,v in b[field].items():assert h(q)==v,q;assert q not in checks or checks[q]==v;checks[q]=v
        for r in b['records']:
            for f in r['files'].values():assert h(f['path'])==f['sha256']and(ROOT/f['path']).stat().st_size==f['bytes']
        allrecords+=b['records'];summaries.append(ref(p));calls+=b['producer_calls']
    assert [r['case_id']for r in allrecords]==original['ordered_case_ids']and len({r['case_id']for r in allrecords})==64
    out=B+'exact_eight_next64_consolidated';(ROOT/out).mkdir(exist_ok=False)
    save(out+'/summary.json',dict(provenance(),status='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE',schema='EXACT_EIGHT_EXPLICIT_BUILD_CONSOLIDATION_V1',inputs_sha256=checks,records=allrecords,selected_case_ids=original['ordered_case_ids'],completed_formulas=64,pending_case_ids=[],producer_calls=calls,build_summaries=summaries,build_selections=[ref(p)for p in parts],original_selection=ref(parent),automatic_resume=False,automatic_skip=False,limitations=['Artifact identity aggregation only; no new encoding or mathematical verification.','Four distinct16-case allocations of120 seconds each; no global120-second deadline claim.']))
    print(json.dumps(dict(completed=64,summary=ref(out+'/summary.json'))))
if __name__=='__main__':main()
