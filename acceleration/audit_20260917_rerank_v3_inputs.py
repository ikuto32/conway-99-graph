"""Independent input-only review of128 unchanged models at5000 iterations."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import platform
import struct
import sys
import time

ROOT=Path(__file__).resolve().parents[1]

def require(ok,msg):
    if not ok:raise ValueError(msg)
def path(p):
    p=Path(p);return p.resolve()if p.is_absolute()else(ROOT/p).resolve()
def key(p):return path(p).relative_to(ROOT).as_posix()
def digest(p):
    h=sha256()
    with path(p).open('rb')as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def q(x):return Fraction(int(x['numerator']),int(x['denominator']))

def compare_streams(old,new):
    left,right=old.read(20),new.read(20)
    require(left==b'C99SCP01'+struct.pack('<III',32,1,500),'old header')
    require(right==b'C99SCP01'+struct.pack('<III',32,1,5000),'new header')
    total=0;h=sha256()
    while True:
        a,b=old.read(1<<20),new.read(1<<20)
        require(a==b,'payload byte mismatch')
        if not a:break
        total+=len(a);h.update(a)
    return total,h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prepared',required=True);ap.add_argument('--preflight',required=True)
    ap.add_argument('--controls',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    require(not path(a.out).exists(),'preserve audit');tick=time.perf_counter();bindings={}
    def bind(p,h=None):
        k=key(p)
        if k not in bindings:bindings[k]=digest(p)
        require(h is None or h==bindings[k],'artifact identity '+k);return bindings[k]
    def read(p):
        bind(p);d=json.loads(path(p).read_bytes())
        for f,h in d.get('inputs_sha256',{}).items():bind(f,h)
        return d
    for p in (__file__,'acceleration/refine_whole_star_rank_v3.py','uv.lock',a.protocol):bind(p)
    prep=path(a.prepared)/'manifest.json';m=read(prep);preflight=read(a.preflight);producer_controls=read(a.controls)
    require(producer_controls['status']=='WHOLE_STAR_RERANK_V3_PRODUCER_CONTROLS_PASS' and
            producer_controls['positive_controls']==3 and producer_controls['negative_controls']==24 and
            len(producer_controls['controls'])==27 and
            sum(r['outcome']=='ACCEPT'for r in producer_controls['controls'])==3 and
            sum(r['outcome']=='REJECT'for r in producer_controls['controls'])==24 and
            producer_controls['independent_verification']is False and producer_controls['GPU_processes']==producer_controls['LP_runs']==0,'producer control record')
    for f,h in producer_controls['outputs_sha256'].items():bind(f,h)
    require(m['status']=='WHOLE_STAR_RERANK_V3_PREPARED_NO_COMPUTE'and m['objective_id']=='ORIGINAL_STAR_SIMPLEX_PDHG_V1','prepared objective/status')
    old=read(m['source_ranking_path']);old_audit=read(m['source_audit_path']);scope=read(m['calibration_review_path']);evaluated=read(m['evaluated_path'])
    bind(m['source_audit_path'],'34f72e00cf1b6e734b6be706c12ce414d8978a6f24803e648eefbc0d19bb8788')
    bind(m['calibration_review_path'],'f023c28c8f82388c69ea56af5b91785853bb7519c51044371a957743fc6072d1')
    require(old_audit['ranking_summary_sha256']==bind(m['source_ranking_path']) and scope['evaluation_sha256']==bind(m['evaluated_path']),'existing independent associations')
    ids=old_audit['input_selected_indices'];excluded=scope['selected_indices']
    require(len(ids)==len(set(ids))==128 and m['input_selected_indices']==ids and m['records']==old['records'],'unchanged128 records')
    require(len(excluded)==len(set(excluded))==16 and set(excluded)<=set(ids) and m['excluded_LP_tested_indices']==excluded==[r['proposal_index']for r in evaluated['records']],'excluded16 exact scope')
    require(m['calibration']==scope['records'],'all16 calibration raw records')
    for produced,checked in zip(evaluated['records'],scope['records']):
        require(produced['proposal_index']==checked['proposal_index'] and all(q(produced[k])==q(checked[k])for k in ('exact_lower','exact_upper')),'exact calibration interval')
    require(m['iterations']==5000 and m['source_iterations']==500 and m['checkpoint_list']==[5000] and
            m['initialization']=='uniform_per_simplex_probability_zero_dual' and m['eta']==.9 and m['theta']==1 and m['float_type']=='float64','cold numeric settings')
    require(m['reranked_candidates']==128 and m['new_candidates']==0 and m['eligible_for_next_LP']==112 and
            m['chunk_process_seconds']==600 and m['maximum_GPU_processes']==4 and m['maximum_GPU_process_wall_budget_seconds']==2400,'resource population')
    require(m['domain_enumeration_processes']==m['model_exporter_invocations']==m['LP_runs']==m['GPU_processes']==0 and
            m['original_complete_domains_used']is True and m['pair_pruned_domains_used']is False and m['independently_audited_original_domains']is False,'scope flags')
    policy=m['policy'];require(policy['upper_count']==policy['lower_count']==8 and policy['selection_requires_new_independent_ranking_audit']is True and
            policy['scores']=='Initial and sole requested5000 checkpoint last/average only; no500 results merged' and
            policy['unavailable_policy']=='No shortlist unless all128 reranking outputs pass sanity checks','future ranking policy')
    require(len(m['chunks'])==len(old['chunks'])==4,'four chunk inventory');records=[];all_ids=[]
    for j,(c,oc)in enumerate(zip(m['chunks'],old['chunks'])):
        require(c['chunk_index']==oc['chunk_index']==j and key(c['source_input_path'])==key(oc['input_path'])and c['source_input_sha256']==oc['input_sha256'],'source chunk mapping')
        old_manifest=read(c['source_manifest_path']);bind(c['source_manifest_path'],c['source_manifest_sha256'])
        require(c['cases']==old_manifest['cases'] and len(c['cases'])==32,'unchanged record table')
        for f,h in ((c['source_input_path'],c['source_input_sha256']),(c['input_path'],c['input_sha256'])):bind(f,h)
        require(old_audit['inputs_sha256'][key(c['source_input_path'])]==bind(c['source_input_path']),'prior audit sourcebinary binding')
        with path(c['source_input_path']).open('rb')as f,path(c['input_path']).open('rb')as g:count,payloadhash=compare_streams(f,g)
        require(count==c['identity']['payload_bytes'] and payloadhash==c['identity']['payload_sha256'],'reported payload identity')
        cursor=20
        with path(c['input_path']).open('rb')as g:
            g.seek(cursor)
            for k,case in enumerate(c['cases']):
                require(case['index']==k and case['record_byte_offset']==cursor,'serialized record layout')
                h=sha256();remaining=case['byte_length'];require(type(remaining)is int and remaining>0,'record size')
                while remaining:
                    b=g.read(min(1<<20,remaining));require(b,'truncated record');h.update(b);remaining-=len(b)
                require(h.hexdigest()==case['record_sha256'],'record payload hash')
                cursor+=case['byte_length'];all_ids.append(case['proposal_index'])
            require(g.read(1)==b'' and cursor==20+count,'complete record payload coverage')
        records.append(dict(chunk_index=j,unchanged_payload_bytes=count,unchanged_payload_sha256=payloadhash,exact_record_hashes_checked=32))
    require(all_ids==ids,'all128 original binary index identity')
    require(preflight['status']=='WHOLE_STAR_RERANK_V3_PREFLIGHT_PASS'and preflight['selected_indices']==ids and
            preflight['excluded_LP_tested_indices']==excluded and preflight['preparation_sha256']==bind(prep)and preflight['GPU_processes']==0,'producer preflight')
    h0=b'C99SCP01'+struct.pack('<III',32,1,500);h1=b'C99SCP01'+struct.pack('<III',32,1,5000);payload=b'known-exact-matrix-payload'
    compare_streams(BytesIO(h0+payload),BytesIO(h1+payload));controls=[dict(name='valid_header_only_copy',outcome='PASS')]
    for name,bad in [('changed_payload',h1+payload[:-1]+b'X'),('truncated_payload',h1+payload[:-1]),('wrong_iterations',h0+payload),('wrong_count',h1[:8]+struct.pack('<I',31)+h1[12:]+payload)]:
        try:compare_streams(BytesIO(h0+payload),BytesIO(bad))
        except ValueError as e:controls.append(dict(name=name,outcome='REJECT',reason=str(e)))
        else:raise ValueError('corruption accepted')
    require(all(digest(f)==h for f,h in bindings.items()),'input changed')
    report=dict(status='INDEPENDENT_WHOLE_STAR_RERANK_V3_INPUT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=m['source_commit'],
        inputs_sha256=bindings,command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),
        selected_indices=ids,excluded_LP_tested_indices=excluded,producer_imported=False,records=records,controls=controls,
        source_iteration=500,new_iteration=5000,unchanged_models=128,new_models=0,eligible_original_ids=112,
        shared_trusted_components=['Python standard library','hash-bound independently reconstructed128 models','hash-bound independent16 exact intervals'],
        producer_controls_observed_status=producer_controls['status'],producer_controls_reexecuted=False,
        numerical_execution_reviewed_here=False,domain_completeness_rechecked_here=False,scope='Exact preparation/payload identity and finite selection/calibration input mapping only; new5000 numerical results require separate review',
        GPU_processes=0,LP_runs=0,target_resolution='UNKNOWN',elapsed_seconds=time.perf_counter()-tick)
    path(a.out).open('x',encoding='utf8').write(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],payload_bytes=sum(r['unchanged_payload_bytes']for r in records),sha256=digest(a.out))))

if __name__=='__main__':main()
