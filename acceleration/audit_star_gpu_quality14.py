"""Compare scalar CUDA500 results with the saved14 cold CPU/strong-LP study.

This does not launch CUDA, replay iterations, solve LPs, or enumerate domains.
Rank statistics describe the same selected14 sample, not new general evidence.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
SCALAR_TOLERANCE=2e-6

def path(p):return (ROOT/str(p).replace('\\','/')).resolve()
def key(p):return path(p).relative_to(ROOT).as_posix()
def digest(p):return sha256(path(p).read_bytes()).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)
def rational(q):return Fraction(int(q['numerator']),int(q['denominator']))
def ranks(values):return [(sum(x<v for x in values)+1+sum(x<=v for x in values))/2 for v in values]
def corr(x,y):
    xx=[v-math.fsum(x)/len(x) for v in x];yy=[v-math.fsum(y)/len(y) for v in y]
    den=math.sqrt(math.fsum(v*v for v in xx)*math.fsum(v*v for v in yy))
    return math.fsum(a*b for a,b in zip(xx,yy))/den if den else None

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ('manifest','gpu-output','gpu-source','gpu-binary','cpu-study','real-parity','tiny-parity','cli-controls','out'):p.add_argument('--'+arg,required=True)
    a=p.parse_args();out=path(a.out);require(not out.exists(),'Preserve quality report')
    bindings={}
    def bind(p,expected=None):
        h=digest(p);name=key(p);require(expected is None or expected==h,'Changed binding '+name)
        require(name not in bindings or bindings[name]==h,'Conflicting hash');bindings[name]=h;return h
    def load(p):
        bind(p);d=json.loads(path(p).read_bytes())
        for field in ('inputs_sha256','outputs_sha256'):
            for name,h in d.get(field,{}).items():bind(name,h)
        return d
    bind(__file__);bind(a.gpu_source);bind(a.gpu_binary)
    for name in (a.real_parity,a.tiny_parity):
        proof=load(name)
        require(proof['status']=='COLD_STAR_CUDA_CANONICAL_CPU_COMPONENTWISE_PARITY_PASS','Missing recurrence parity')
        pb={key(p):h for p,h in proof['inputs_sha256'].items()}
        require(pb.get(key(a.gpu_source))==digest(a.gpu_source) and pb.get(key(a.gpu_binary))==digest(a.gpu_binary),'Parity/source/binary mismatch')
    controls=load(a.cli_controls)
    require(controls['status']=='INDEPENDENT_COLD_STAR_CUDA_PROJECTION_AND_CLI_CONTROLS_PASS' and controls['all_negative_controls_rejected'],'Missing parser/projection controls')
    cb={key(p):h for p,h in controls['inputs_sha256'].items()}
    require(cb.get(key(a.gpu_source))==digest(a.gpu_source) and cb.get(key(a.gpu_binary))==digest(a.gpu_binary),'CLI control binary mismatch')
    manifest=load(a.manifest);gpu=load(a.gpu_output);cpu=load(a.cpu_study)
    require(manifest['status']=='AUDITED_COLD_STAR_PDHG_BINARY_EXPORTED' and manifest['candidate_count']==14 and manifest['checkpoints']==[500],'Wrong exported cohort')
    require(gpu['status']=='NUMERICAL_COLD_STAR_PDHG_BATCH_FINISHED' and gpu['candidate_count']==14 and len(gpu['results'])==14 and gpu['eta']==.9 and gpu['theta']==1,'Wrong GPU output')
    require(gpu['initialization']=='uniform_per_simplex_probability_zero_dual' and gpu['best_scope']=='initial_and_requested_checkpoint_last_and_average' and gpu['numerical_scores_are_proofs'] is False,'Wrong GPU semantics')
    require(cpu['status']=='BOUNDED_STAR_PDHG_QUALITY_STUDY_FINISHED' and cpu['complete2000_runs']==28 and len(cpu['records'])==14,'Missing saved14 CPU study')
    bind(manifest['binary_path'],manifest['binary_sha256'])
    binary=path(manifest['binary_path']).read_bytes();view=memoryview(binary)
    require(binary[:8]==b'C99SCP01' and struct.unpack_from('<3I',binary,8)==(14,1,500),'Binary header differs')
    require(len(binary)==manifest['binary_bytes'],'Binary length differs')
    sources={r['candidate_sha256']:r for r in [load(row['path']) for row in cpu['records']]}
    require(len(sources)==14,'Repeated saved study candidates')
    records=[];scalar_errors=[];cursor=20
    for i,(case,result) in enumerate(zip(manifest['cases'],gpu['results'])):
        require(case['index']==i==result['candidate_index'],'Wrong candidate position')
        require(case['record_byte_offset']==cursor,'Missing/reordered binary record')
        record=view[cursor:cursor+case['byte_length']]
        require(sha256(record).hexdigest()==case['record_sha256'],'Wrong binary record hash')
        require(struct.unpack_from('<5I',record,0)==tuple(case[k] for k in ('N','M','Q','blocks','nnz')),'Wrong binary dimensions')
        for part in case['arrays'].values():
            fragment=record[part['relative_byte_offset']:part['relative_byte_offset']+part['byte_length']]
            require(sha256(fragment).hexdigest()==part['sha256'],'Wrong binary array hash')
        cursor+=case['byte_length']
        require(case['M']==5166 and case['Q']==1680 and case['blocks']==84,'Wrong star row/block convention')
        require((result['n_variables'],result['n_rows'],result['n_equalities'])==(case['N'],5166,1680),'Wrong GPU shape')
        require(result['domain_counts']==[b-a for a,b in zip(case['offsets'][:-1],case['offsets'][1:])],'GPU domain geometry differs')
        source=sources[case['candidate_sha256']]
        require(key(case['candidate_path'])==key(source['candidate_path']) and key(case['audit_path'])==key(source['reference_audit_path']) and case['audit_sha256']==source['reference_audit_sha256'],'CPU/export candidate+audit association')
        audit=load(case['audit_path']);phase=load(case['phase_path'])
        ab={key(p):h for p,h in audit['inputs_sha256'].items()}
        require(audit['status']=='INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS' and ab.get(key(case['phase_path']))==case['phase_sha256'] and ab.get(key(case['candidate_path']))==case['candidate_sha256'],'Strong exact reference association')
        require(phase['candidate_sha256']==case['candidate_sha256'] and phase['domains_sha256']==case['domains_sha256'],'Wrong original domain table')
        lower,upper=rational(audit['exact_dual_lower']),rational(audit['exact_primal_upper'])
        require(source['exact_star_interval']==[float(lower),float(upper)],'Wrong saved exact interval')
        cold=next(r for r in source['runs'] if r['start']=='cold_uniform_zero_dual')
        expected=next(r for r in cold['checkpoints'] if r['iterations']==500)
        require(len(result['checkpoints'])==1 and result['checkpoints'][0]['iterations']==500,'Wrong GPU checkpoint')
        actual=result['checkpoints'][0];errs={}
        for kind in ('initial','last','average'):
            truth=cold['initial'] if kind=='initial' else expected[kind]
            got=result['initial'] if kind=='initial' else actual[kind]
            for label,value in truth.items():
                require(math.isfinite(got[label]),'Nonfinite GPU score')
                error=abs(got[label]-value);errs[kind+'.'+label]=error;require(error<=SCALAR_TOLERANCE,'GPU/saved CPU scalar mismatch')
        for label in ('best_upper_numeric','best_lower_numeric'):
            error=abs(actual[label]-expected[label]);errs[label]=error;require(error<=SCALAR_TOLERANCE,'Best-point convention differs')
        scalar_errors.extend(errs.values())
        records.append(dict(index=source['index'],candidate_position=i,candidate_sha256=case['candidate_sha256'],exact_star_interval=[float(lower),float(upper)],
                            actual=actual,scalar_errors=errs,cpu500_iteration_seconds=cold['checkpoints'][0]['elapsed_seconds']))
    require(cursor==len(binary),'Unbound tail in binary')
    truth=[sum(r['exact_star_interval'])/2 for r in records];indices=[r['index'] for r in records]
    true_top=set(sorted(indices,key=lambda i:truth[indices.index(i)])[:4]);metrics=[]
    for field in ('last_upper','average_upper','last_lower','average_lower','best_upper_numeric','best_lower_numeric'):
        def value(record):
            cp=record['actual']
            if field in ('best_upper_numeric','best_lower_numeric'):return cp[field]
            kind,bound=field.split('_');return cp[kind]['primal_upper_numeric' if bound=='upper' else 'dual_lower_numeric']
        vals=[value(r) for r in records];selected=[r['index'] for r in sorted(records,key=lambda r:(value(r),r['index']))[:4]]
        rho=corr(ranks(vals),ranks(truth));recall=len(set(selected)&true_top)/4
        prior=next(m for m in cpu['metrics'] if m['start']=='cold_uniform_zero_dual' and m['iterations']==500 and m['score']==field)
        require(abs(rho-prior['spearman'])<=1e-12 and recall==prior['top_k_recall'] and selected==prior['predicted_top'],'GPU ranking differs from saved coldCPU')
        metrics.append(dict(score=field,spearman=rho,top4_recall=recall,predicted_top=selected,actual_top=sorted(true_top)))
    report=dict(status='COLD_STAR_CUDA_SAVED14_SCALAR_AND_RANK_PARITY_PASS',inputs_sha256=bindings,records=records,metrics=metrics,
                scalar_checks=len(scalar_errors),scalar_absolute_tolerance=SCALAR_TOLERANCE,max_scalar_error=max(scalar_errors),
                gpu_timings={k:gpu[k] for k in ('parse_seconds','gpu_iteration_seconds','checkpoint_transfer_and_metrics_seconds','elapsed_seconds')},
                saved_cpu500_iteration_seconds_sum=sum(r['cpu500_iteration_seconds'] for r in records),
                timing_scope='GPU elapsed includes parse/upload/iterations/checkpoint host evaluation up to JSON serialization; saved CPU timings are iteration/checkpoint-only, not paired end-to-end speedup measurements.',
                LP_runs=0,domain_enumerations=0,new_GPU_runs=0,exclusion_claims=0,
                scope='Scalar and ranking agreement on these14 previously CP-selected local-gate-passing candidates. The GPU approximations are numerical hints, not exact bounds/certificates or universal ranking-performance evidence.')
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=report['status'],max_scalar_error=report['max_scalar_error'],metrics=metrics,gpu_timings=report['gpu_timings'],sha256=digest(out))))

if __name__=='__main__':main()
