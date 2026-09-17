"""Cold 5000-iteration reranking of exactly the previously audited128 models.

No domain enumeration/model exporter. Only the single header u32 at offset16
changes. The existing GPU-result sanity checker is reused and hash pinned.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time

from rank_fresh_star_pdhg import check_gpu

ROOT=Path(__file__).resolve().parents[1]
OBJECTIVE='ORIGINAL_STAR_SIMPLEX_PDHG_V1'
GPU='acceleration/build/star_pdhg_gpu.exe'
SOURCE_AUDIT_SHA='34f72e00cf1b6e734b6be706c12ce414d8978a6f24803e648eefbc0d19bb8788'
PINS={
    GPU:'9dc3ea92ca53a6ebc8dd3715f5a0586ef00b18d5c8c8b7bd4e61cb6c2ae11075',
    'acceleration/star_pdhg_gpu.cu':'79593e296a4fba29882fb04b7e7dd88091dbc7f218135b6db2ba79c0b49002e8',
    'acceleration/rank_fresh_star_pdhg.py':'0feedea50f90a852d62a659e2e9e3979edf83756c9bd07af1e24db5ae50b8eea',
}
POLICY=dict(eligible_population='The same128 original row IDs minus the16 already LP-evaluated IDs',
    numerical_order='Ascending score then original proposal_index',upper_count=8,lower_count=8,
    union_fill='Append unused eligible rows by ascending upper score until16',
    unavailable_policy='No shortlist unless all128 reranking outputs pass sanity checks',
    scores='Initial and sole requested5000 checkpoint last/average only; no500 results merged',
    selection_requires_new_independent_ranking_audit=True)


def require(ok,message):
    if not ok:raise ValueError(message)


def path(p):
    p=Path(str(p).replace('\\','/'))
    return (p if p.is_absolute() else ROOT/p).resolve()


def key(p):
    p=path(p);return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()


def digest(p):
    h=sha256()
    with path(p).open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()


def load(p):return json.loads(path(p).read_bytes())


def save(p,d):
    with path(p).open('x',encoding='utf8') as f:f.write(json.dumps(d,indent=2,allow_nan=False)+'\n')


def now():return datetime.now(timezone.utc).isoformat()


def header(h,iteration):
    require(len(h)==20 and h[:8]==b'C99SCP01','Wrong20-byte binary header')
    count,ncheck,cp=struct.unpack('<3I',h[8:20])
    require(count==32 and ncheck==1 and cp==iteration,'Frozen32-case single-checkpoint header differs')
    return count


def copy_header_only(source,target):
    """Streamcopy existing exact payload; never import/export a model."""
    require(path(source)!=path(target) and not path(target).exists(),'Preserve source/fresh copy')
    with path(source).open('rb') as src,path(target).open('xb') as dst:
        h=src.read(20);header(h,500)
        dst.write(h[:16]+struct.pack('<I',5000))
        for block in iter(lambda:src.read(1<<20),b''):dst.write(block)


def payload_identity(source,target,cases):
    """Complete byte equality outside the single modified header field."""
    require(path(source).stat().st_size==path(target).stat().st_size,'Binary size changed')
    h=sha256();total=20
    with path(source).open('rb') as src,path(target).open('rb') as dst:
        old,new=src.read(20),dst.read(20);header(old,500);header(new,5000)
        require(old[:16]==new[:16],'A different header field changed')
        for block in iter(lambda:src.read(1<<20),b''):
            require(dst.read(len(block))==block,'Model payload changed');h.update(block);total+=len(block)
        require(dst.read(1)==b'','Trailing output')
    cursor=20
    with path(target).open('rb') as f:
        for i,c in enumerate(cases):
            require(c['index']==i and c['record_byte_offset']==cursor and type(c['byte_length']) is int and c['byte_length']>0,
                'Model record layout mismatch')
            f.seek(cursor);left=c['byte_length'];rh=sha256()
            while left:
                block=f.read(min(left,1<<20));require(block,'Truncated record');rh.update(block);left-=len(block)
            require(rh.hexdigest()==c['record_sha256'],'Serialized model record changed')
            cursor+=c['byte_length']
    require(len(cases)==32 and cursor==total,'Incomplete model payload coverage')
    return dict(payload_offset=20,payload_bytes=total-20,payload_sha256=h.hexdigest(),
        identical_outside_range=[16,20],changed_u32_offset=16,old_u32=500,new_u32=5000,
        independently_verified=False,all_record_hashes_preserved=True)


class Bindings:
    def __init__(self):self.values={}
    def bind(self,p,h=None):
        k=key(p)
        if k not in self.values:self.values[k]=digest(p)
        require(h is None or self.values[k]==h,'Changed input: '+k)
        return self.values[k]
    def read(self,p):
        self.bind(p);d=load(p)
        for f,h in d.get('inputs_sha256',{}).items():self.bind(f,h)
        return d
    def recheck(self):
        for p,h in self.values.items():require(digest(p)==h,'Input changed during operation: '+p)


def selection(rows,excluded):
    ids=[r['proposal_index'] for r in rows]
    require(len(ids)==128 and len(set(ids))==128 and all(type(i) is int for i in ids),'Exactly128distinct reranked IDs required')
    require(len(excluded)==len(set(excluded))==16 and set(excluded)<=set(ids),'Exactly16already-evaluated IDs required')
    require(all(type(r[k]) in (int,float) and isfinite(r[k]) for r in rows for k in ('best_lower_numeric','best_upper_numeric')),
        'Finite reranking values required')
    require(all(r['best_lower_numeric']<=r['best_upper_numeric']+1e-7 and r['best_upper_numeric']>=-1e-10 for r in rows),
        'Inconsistent numerical bracket')
    eligible=[r for r in rows if r['proposal_index'] not in excluded]
    require(len(eligible)==112,'Wrong eligible denominator')
    upper=[r['proposal_index'] for r in sorted(eligible,key=lambda r:(r['best_upper_numeric'],r['proposal_index']))]
    lower=[r['proposal_index'] for r in sorted(eligible,key=lambda r:(r['best_lower_numeric'],r['proposal_index']))]
    order=[];roles={}
    for seq,role in ((upper[:8],'upper'),(lower[:8],'lower')):
        for i in seq:
            if i not in roles:order.append(i);roles[i]=[]
            roles[i].append(role)
    for i in upper:
        if len(order)==16:break
        if i not in roles:order.append(i);roles[i]=['upper_fill']
    return [dict(proposal_index=i,selection_roles=roles[i]) for i in order],upper,lower


def prepare(args):
    out=path(args.prepared);require(out.is_relative_to(ROOT) and not out.exists(),'Fresh workspace preparation directory required')
    b=Bindings()
    for p,h in PINS.items():b.bind(p,h)
    b.bind(__file__);b.bind('uv.lock');b.bind('pyproject.toml')
    original=b.read(args.source_ranking);b.bind(args.source_audit,SOURCE_AUDIT_SHA);audit=b.read(args.source_audit)
    require(audit['status']=='INDEPENDENT_WHOLE_FRESH_STAR_PDHG_RANKING_AUDIT_PASS' and
        audit['all_serialized_models_reconstructed'] is True and audit['producer_or_native_imported'] is False,
        'Original independent full-model audit required')
    require(audit['ranking_summary_sha256']==b.bind(args.source_ranking) and key(audit['ranking_summary_path'])==key(args.source_ranking),
        'Original ranking audit association')
    require(original['status']=='NUMERICAL_WHOLE_FRESH_STAR_PDHG_RANKING_FINISHED' and original['producer_version']=='whole_fresh_v2_balanced' and
        original['objective_id']==OBJECTIVE and original['iterations']==500 and original['scored_count']==128 and original['unavailable_count']==0 and
        original['original_complete_domains_used'] is True and original['pair_pruned_domains_used'] is False,'Frozen source ranking scope')
    ids=original['input_selected_indices']
    require(len(ids)==len(set(ids))==128 and ids==[r['proposal_index'] for r in original['records']]==audit['input_selected_indices'],
        'Frozen128 inventory differs')
    evaluated=b.read(args.evaluated);review=b.read(args.calibration_review)
    require(review['status']=='INDEPENDENT_WHOLE_FRESH_STAR_SHORTLIST_AUDIT_PASS' and review['producer_imported'] is False and
        key(review['evaluation_path'])==key(args.evaluated) and review['evaluation_sha256']==b.bind(args.evaluated),
        'Actual independent16 LP review required')
    excluded=[r['proposal_index'] for r in evaluated['records']]
    require(excluded==review['selected_indices'] and len(excluded)==len(set(excluded))==16 and set(excluded)<=set(ids),'Independent excluded16 identity')
    calibration=[]
    for produced,checked in zip(evaluated['records'],review['records']):
        require(produced['proposal_index']==checked['proposal_index'] and checked['result']=='INDEPENDENT_RAW_CHECK_PASS','Calibration identity')
        for field in ('exact_lower','exact_upper'):
            require(Fraction(int(produced[field]['numerator']),int(produced[field]['denominator']))==
                Fraction(int(checked[field]['numerator']),int(checked[field]['denominator'])),'Calibration interval differs')
        calibration.append(deepcopy(checked))
    require(len(calibration)==16,'Missing calibration cases')
    chunks=original['chunks'];require(len(chunks)==4 and [c['chunk_index'] for c in chunks]==list(range(4)),'Frozen four chunks required')
    all_cases=[];old_manifests=[]
    for c in chunks:
        b.bind(c['input_path'],c['input_sha256']);b.bind(c['manifest_path'],c['manifest_sha256']);m=b.read(c['manifest_path'])
        require(audit['inputs_sha256'].get(key(c['input_path']))==c['input_sha256'],'Original binary is not independently bound')
        require(m['candidate_count']==32 and m['checkpoints']==[500] and m['binary_sha256']==c['input_sha256'] and
            m['original_complete_domains_used'] is True and m['pair_pruned_domains_used'] is False,'Old chunk scope')
        require([x['proposal_index'] for x in m['cases']]==c['proposal_indices'],'Old chunk index mapping')
        old_manifests.append(m);all_cases+=m['cases']
    require([c['proposal_index'] for c in all_cases]==ids,'Original payload ordering differs')
    for i,(c,r) in enumerate(zip(all_cases,original['records'])):
        require(c['native_result_index']==i and c['original_native_index']==r['original_native_index']==r['proposal_index'],'Original native mapping')
        for f in ('candidate','domains'):
            require(key(c[f+'_path'])==key(r[f+'_path']) and c[f+'_sha256']==r[f+'_sha256'],'Original graph/domain identity')
            b.bind(c[f+'_path'],c[f+'_sha256'])
    out.mkdir();copied=[]
    for c,m in zip(chunks,old_manifests):
        target=out/f"chunk_{c['chunk_index']:03d}.bin";copy_header_only(c['input_path'],target)
        identity=payload_identity(c['input_path'],target,m['cases'])
        copied.append(dict(chunk_index=c['chunk_index'],source_input_path=c['input_path'],source_input_sha256=c['input_sha256'],
            source_manifest_path=c['manifest_path'],source_manifest_sha256=c['manifest_sha256'],input_path=key(target),input_sha256=b.bind(target),
            cases=m['cases'],identity=identity))
    b.recheck()
    manifest=dict(status='WHOLE_STAR_RERANK_V3_PREPARED_NO_COMPUTE',created_at=now(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable]+sys.argv,working_directory=str(ROOT),python_version=platform.python_version(),inputs_sha256=b.values,
        source_ranking_path=key(args.source_ranking),source_ranking_sha256=b.bind(args.source_ranking),source_audit_path=key(args.source_audit),source_audit_sha256=SOURCE_AUDIT_SHA,
        evaluated_path=key(args.evaluated),evaluated_sha256=b.bind(args.evaluated),calibration_review_path=key(args.calibration_review),calibration_review_sha256=b.bind(args.calibration_review),
        chunks=copied,records=deepcopy(original['records']),input_selected_indices=ids,excluded_LP_tested_indices=excluded,calibration=calibration,
        objective_id=OBJECTIVE,original_complete_domains_used=True,pair_pruned_domains_used=False,independently_audited_original_domains=False,
        iterations=5000,source_iterations=500,initialization='uniform_per_simplex_probability_zero_dual',eta=.9,theta=1,float_type='float64',
        checkpoint_list=[5000],policy=POLICY,reranked_candidates=128,new_candidates=0,eligible_for_next_LP=112,
        chunk_process_seconds=600,maximum_GPU_processes=4,maximum_GPU_process_wall_budget_seconds=2400,
        domain_enumeration_processes=0,model_exporter_invocations=0,LP_runs=0,GPU_processes=0,
        numerical_acceptance='All finite sane GPU metrics; no mathematical numerical threshold. Interval/order calibration is descriptive, failures retained.',
        calibration_policy='Compare all16 saved exact intervals with both500 and5000 numerical brackets; no certification or retrospective case exclusion.',
        scope='Exactly the same128 fixed models; numerical reranking only, no target exclusion or coverage claim')
    save(out/'manifest.json',manifest)
    return manifest


def preflight(args):
    b=Bindings();manifest=path(args.prepared)/'manifest.json';m=b.read(manifest)
    require(m['status']=='WHOLE_STAR_RERANK_V3_PREPARED_NO_COMPUTE' and m['objective_id']==OBJECTIVE and m['iterations']==5000 and
        m['source_iterations']==500 and m['policy']==POLICY and m['reranked_candidates']==128 and m['new_candidates']==0 and
        m['eligible_for_next_LP']==112 and m['chunk_process_seconds']==600 and m['maximum_GPU_processes']==4,
        'Preregistered configuration changed')
    require(m['original_complete_domains_used'] is True and m['pair_pruned_domains_used'] is False and
        m['independently_audited_original_domains'] is False and len(m['chunks'])==4,'Wrong original-domain scope')
    require(m['initialization']=='uniform_per_simplex_probability_zero_dual' and m['eta']==.9 and m['theta']==1 and
        m['float_type']=='float64' and m['checkpoint_list']==[5000] and m['maximum_GPU_process_wall_budget_seconds']==2400 and
        m['domain_enumeration_processes']==m['model_exporter_invocations']==m['LP_runs']==m['GPU_processes']==0,
        'Frozen numerical settings/process budget differs')
    require(m['inputs_sha256'].get(key(__file__))==digest(__file__),'Preparation producer source changed')
    for p,h in PINS.items():b.bind(p,h)
    ids=[]
    for c in m['chunks']:
        b.bind(c['input_path'],c['input_sha256']);b.bind(c['source_input_path'],c['source_input_sha256'])
        require(payload_identity(c['source_input_path'],c['input_path'],c['cases'])==c['identity'],'Header-only copy evidence changed')
        ids.extend(x['proposal_index'] for x in c['cases'])
    require(ids==m['input_selected_indices']==[r['proposal_index'] for r in m['records']] and len(set(ids))==128,'Rerank128 mapping')
    require(len(m['excluded_LP_tested_indices'])==len(set(m['excluded_LP_tested_indices']))==16 and
        set(m['excluded_LP_tested_indices'])<=set(ids),'Excluded16 mapping')
    b.recheck();return m,b


def execution_gate(args,m,b):
    require(args.input_audit and args.input_auditor and args.input_auditor_sha256,'Independent input review required beforeGPU')
    b.bind(args.input_auditor,args.input_auditor_sha256);r=b.read(args.input_audit)
    require(r['status']=='INDEPENDENT_WHOLE_STAR_RERANK_V3_INPUT_PASS' and r['producer_imported'] is False and
        r['selected_indices']==m['input_selected_indices'] and r['excluded_LP_tested_indices']==m['excluded_LP_tested_indices'],
        'Independent rerank input scope differs')
    for p in [__file__,path(args.prepared)/'manifest.json',args.input_auditor]+[c['input_path'] for c in m['chunks']]:
        require(r['inputs_sha256'].get(key(p))==b.bind(p),'Independent input report does not bind '+key(p))


def calibration_rows(m,rows):
    old={r['proposal_index']:r for r in m['records']};new={r['proposal_index']:r for r in rows};result=[]
    old_upper=sorted(old,key=lambda i:(old[i]['best_upper_numeric'],i));old_lower=sorted(old,key=lambda i:(old[i]['best_lower_numeric'],i))
    new_upper=sorted(new,key=lambda i:(new[i]['best_upper_numeric'],i));new_lower=sorted(new,key=lambda i:(new[i]['best_lower_numeric'],i))
    for exact in m['calibration']:
        i=exact['proposal_index'];lo=Fraction(int(exact['exact_lower']['numerator']),int(exact['exact_lower']['denominator']));hi=Fraction(int(exact['exact_upper']['numerator']),int(exact['exact_upper']['denominator']))
        r=dict(proposal_index=i,exact_lower=exact['exact_lower'],exact_upper=exact['exact_upper'],numerical_scores_are_certificates=False)
        for label,source,ur,lr in [('iterations500',old,old_upper,old_lower),('iterations5000',new,new_upper,new_lower)]:
            a=source[i]['best_lower_numeric'];z=source[i]['best_upper_numeric']
            # Calibration booleans compare exact binary floats to exact rationals; they do not certify GPU arithmetic.
            r[label]=dict(lower_numeric=a,upper_numeric=z,gap_numeric=z-a,upper_rank_among128=ur.index(i)+1,lower_rank_among128=lr.index(i)+1,
                numerical_lower_le_exact_lower=Fraction.from_float(float(a))<=lo,
                numerical_upper_ge_exact_upper=Fraction.from_float(float(z))>=hi,
                upper_minus_exact_upper_display=z-float(hi),exact_lower_minus_lower_display=float(lo)-a)
        result.append(r)
    return result


def execute(args,m,b):
    out=path(args.out);require(out.is_relative_to(ROOT) and not out.exists(),'Fresh execution directory required');out.mkdir()
    save(out/'manifest.json',dict(status='WHOLE_STAR_RERANK_V3_EXECUTION_BOUND',created_at=now(),inputs_sha256=b.values,
        preparation_path=key(path(args.prepared)/'manifest.json'),preparation_sha256=digest(path(args.prepared)/'manifest.json'),
        input_review_path=key(args.input_audit),input_review_sha256=digest(args.input_audit),command=[sys.executable]+sys.argv,
        working_directory=str(ROOT),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        iterations=5000,chunk_process_seconds=600,maximum_GPU_processes=4,policy=POLICY))
    records=deepcopy(m['records']);by_id={r['proposal_index']:r for r in records};done=[];outputs={};started=time.perf_counter();active=None
    for r in records:r.update(status='RERANK_PENDING',best_lower_numeric=None,best_upper_numeric=None)
    try:
        for c in m['chunks']:
            active=c['chunk_index'];gpuout=out/f'chunk_{active:03d}.json';log=out/f'chunk_{active:03d}.log'
            require(digest(c['input_path'])==c['input_sha256'] and digest(GPU)==PINS[GPU],'Input changed beforeGPU')
            cmd=[str(path(GPU)),str(path(c['input_path'])),str(gpuout)];tick=time.perf_counter()
            with log.open('x',encoding='utf8') as f:
                run=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=600,check=False)
            outputs[key(log)]=digest(log);require(run.returncode==0,'GPU failed: '+key(log))
            result=load(gpuout);scores=check_gpu(result,c['cases'],5000)
            for case,(lower,upper) in zip(c['cases'],scores):
                by_id[case['proposal_index']].update(status='NUMERICALLY_RERANKED',best_lower_numeric=lower,best_upper_numeric=upper)
            outputs[key(gpuout)]=digest(gpuout)
            done.append(dict(chunk_index=active,command=cmd,return_code=run.returncode,gpu_output_path=key(gpuout),gpu_output_sha256=digest(gpuout),
                wall_seconds=time.perf_counter()-tick,device=result['device'],GPU_iteration_seconds=result['gpu_iteration_seconds']))
            save(out/f'progress_{active:03d}.json',dict(status='WHOLE_STAR_RERANK_V3_CHUNK_COMPLETE',completed_chunks=done,
                completed_reranked_candidates=sum(r['status']=='NUMERICALLY_RERANKED' for r in records),records=records,outputs_sha256=outputs))
            print(json.dumps(dict(completed_chunk=active,reranked=sum(r['status']=='NUMERICALLY_RERANKED' for r in records))),flush=True)
        chosen,upper,lower=selection(records,m['excluded_LP_tested_indices']);b.recheck()
        save(out/'summary.json',dict(status='NUMERICAL_WHOLE_STAR_RERANK_V3_FINISHED',created_at=now(),objective_id=OBJECTIVE,
            inputs_sha256=b.values,outputs_sha256=outputs,manifest_path=key(out/'manifest.json'),manifest_sha256=digest(out/'manifest.json'),
            preparation_path=key(path(args.prepared)/'manifest.json'),preparation_sha256=digest(path(args.prepared)/'manifest.json'),
            iterations=5000,source_iterations=500,records=records,chunks=done,input_selected_indices=m['input_selected_indices'],
            reranked_candidates=128,new_candidates=0,unavailable_count=0,excluded_LP_tested_indices=m['excluded_LP_tested_indices'],
            eligible_for_next_LP=112,eligible_ranked_by_upper=upper,eligible_ranked_by_lower=lower,proposed_union16=chosen,
            shortlist_independent_audit_pending=True,calibration=calibration_rows(m,records),elapsed_seconds=time.perf_counter()-started,
            original_complete_domains_used=True,pair_pruned_domains_used=False,independently_audited_original_domains=False,
            domain_enumeration_processes=0,model_exporter_invocations=0,LP_runs=0,GPU_processes=len(done),
            numerical_scores_are_proofs=False,exclusions_claimed=0,graph_constructed=False,general_nonexistence_proved=False))
    except BaseException as e:
        save(out/'failure.json',dict(status='WHOLE_STAR_RERANK_V3_STOPPED',created_at=now(),active_chunk=active,error_type=type(e).__name__,message=str(e),
            completed_chunks=done,records=records,outputs_sha256=outputs,shortlist_created=False,no_mathematical_conclusion=True,
            restart='Preserve this directory. A separately recorded new attempt may reuse validated prepared binaries; do not overwrite or silently rerun completed chunks.'))
        raise


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-ranking',default='acceleration/results/20260917_whole_fresh_v2_balanced/ranking/summary.json')
    p.add_argument('--source-audit',default='acceleration/results/20260917_independent_review/whole_fresh_ranking.json')
    p.add_argument('--evaluated',default='acceleration/results/20260917_whole_fresh_v2_balanced/shortlist/summary.json')
    p.add_argument('--calibration-review');p.add_argument('--prepared',required=True);p.add_argument('--out');p.add_argument('--report')
    p.add_argument('--input-audit');p.add_argument('--input-auditor');p.add_argument('--input-auditor-sha256')
    modes=p.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare',action='store_true');modes.add_argument('--validate-only',action='store_true');modes.add_argument('--execute',action='store_true')
    return p


def main():
    args=parser().parse_args()
    if args.prepare:
        require(args.calibration_review,'Actual independent calibration review required');m=prepare(args)
        print(json.dumps(dict(status=m['status'],prepared=key(args.prepared),reranked_candidates=128,new_candidates=0,GPU_processes=0)));return
    m,b=preflight(args)
    if args.validate_only:
        r=dict(status='WHOLE_STAR_RERANK_V3_PREFLIGHT_PASS',created_at=now(),inputs_sha256=b.values,
            preparation_path=key(path(args.prepared)/'manifest.json'),preparation_sha256=digest(path(args.prepared)/'manifest.json'),
            selected_indices=m['input_selected_indices'],excluded_LP_tested_indices=m['excluded_LP_tested_indices'],
            reranked_candidates=128,new_candidates=0,eligible_for_next_LP=112,GPU_processes=0,independent_verification=False)
        if args.report:save(args.report,r)
        print(json.dumps({k:v for k,v in r.items() if k!='inputs_sha256'}));return
    execution_gate(args,m,b);require(args.out,'Fresh output required');execute(args,m,b)


if __name__=='__main__':main()
