"""Three alternating scalar-only native/CPU subprocesses on one fixed input."""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]

def path(p):return (ROOT/str(p).replace('\\','/')).resolve()
def key(p):return path(p).relative_to(ROOT).as_posix()
def digest(p):return sha256(path(p).read_bytes()).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)
def dump(p,d):
    with path(p).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,allow_nan=False);f.write('\n')

def compare(cpu,gpu):
    require(cpu['candidate_count']==gpu['candidate_count']==2 and len(cpu['results'])==len(gpu['results'])==2,'Expected fixed real2 batch')
    maximum=0.;checks=0
    for a,b in zip(cpu['results'],gpu['results']):
        for name in ('candidate_index','n_variables','n_rows','n_equalities','domain_counts'):require(a[name]==b[name],'Candidate shape mismatch')
        for name,v in a['initial'].items():
            error=abs(v-b['initial'][name]);require(math.isfinite(error) and error<=2e-8,'Initial mismatch');maximum=max(maximum,error);checks+=1
        require([p['iterations'] for p in a['checkpoints']]==[p['iterations'] for p in b['checkpoints']]==[1,2,10,500,2000],'Checkpoint mismatch')
        for x,y in zip(a['checkpoints'],b['checkpoints']):
            tolerance=2e-8 if x['iterations']<=10 else 2e-6
            for point in ('last','average'):
                for name,v in x[point].items():
                    error=abs(v-y[point][name]);require(math.isfinite(error) and error<=tolerance,'Scalar mismatch');maximum=max(maximum,error);checks+=1
            for name in ('best_upper_numeric','best_lower_numeric'):
                error=abs(x[name]-y[name]);require(math.isfinite(error) and error<=tolerance,'Best scalar mismatch');maximum=max(maximum,error);checks+=1
    return dict(scalar_checks=checks,maximum_absolute_error=maximum,tolerances_unchanged_from_prior_parity=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qa-summary',required=True);p.add_argument('--manifest',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();out=path(a.out);require(not out.exists(),'Fresh benchmark directory')
    inputs={}
    def bind(p,expected=None):
        h=digest(p);require(expected is None or h==expected,'Changed bound file '+key(p));inputs[key(p)]=h;return h
    def load(p):
        bind(p);d=json.loads(path(p).read_bytes())
        for name,h in d.get('inputs_sha256',{}).items():bind(name,h)
        return d
    qa=load(a.qa_summary);manifest=load(a.manifest)
    require(qa['status']=='COLD_STAR_CUDA_BOUNDED_PROTOTYPE_QA_PASS','Prototype QA required')
    require(manifest['status']=='AUDITED_COLD_STAR_PDHG_BINARY_EXPORTED' and manifest['candidate_count']==2 and manifest['checkpoints']==[1,2,10,500,2000],'Use validated real2 only')
    binary=path(qa['native_binary_path']);bind(binary,qa['native_binary_sha256']);bind(qa['native_source_path'],qa['native_source_sha256'])
    input_file=path(manifest['binary_path']);bind(input_file,manifest['binary_sha256'])
    cpu_source=ROOT/'acceleration/star_pdhg_cpu_benchmark.py'
    for source in (__file__,cpu_source,ROOT/'acceleration/review_star_pdhg_gpu.py',ROOT/'acceleration/star_marginal_cp_cpu_v2.py'):bind(source)
    out.mkdir(parents=True);dump(out/'manifest.json',dict(status='PAIRED_COLD_STAR_TIMING_INPUTS_BOUND',inputs_sha256=inputs,orders=[['cpu','gpu'],['gpu','cpu'],['cpu','gpu']],trials=3,scalar_only=True))
    trials=[];outputs={};start=time.perf_counter()
    for trial,order in enumerate((('cpu','gpu'),('gpu','cpu'),('cpu','gpu'))):
        record=dict(trial=trial,order=list(order),runs={})
        for backend in order:
            result_path=out/f'trial_{trial}_{backend}.json';log_path=out/f'trial_{trial}_{backend}.log'
            command=([sys.executable,'-B',str(cpu_source)] if backend=='cpu' else [str(binary)])+[str(input_file),str(result_path)]
            require(all(digest(p)==h for p,h in inputs.items() if p.endswith(('.py','.cu','.exe','.bin'))),'Pinned execution input changed')
            tick=time.perf_counter();done=subprocess.run(command,capture_output=True,text=True,timeout=60,cwd=ROOT);wall=time.perf_counter()-tick
            log_path.write_text(done.stdout+done.stderr,encoding='utf-8');require(done.returncode==0,'Benchmark subprocess failed')
            result=json.loads(result_path.read_bytes())
            outputs[key(result_path)]=digest(result_path);outputs[key(log_path)]=digest(log_path)
            record['runs'][backend]=dict(command=command,process_wall_seconds=wall,result_path=key(result_path),result_sha256=digest(result_path),reported_elapsed_seconds=result['elapsed_seconds'],reported_iteration_seconds=result['cpu_iteration_seconds' if backend=='cpu' else 'gpu_iteration_seconds'])
        cpu=json.loads(path(record['runs']['cpu']['result_path']).read_bytes());gpu=json.loads(path(record['runs']['gpu']['result_path']).read_bytes())
        record['parity']=compare(cpu,gpu);record['paired_CPU_over_GPU_process_ratio']=record['runs']['cpu']['process_wall_seconds']/record['runs']['gpu']['process_wall_seconds'];trials.append(record)
        print(json.dumps(dict(trial=trial,cpu=record['runs']['cpu']['process_wall_seconds'],gpu=record['runs']['gpu']['process_wall_seconds'],ratio=record['paired_CPU_over_GPU_process_ratio'],scalar_error=record['parity']['maximum_absolute_error'])),flush=True)
    result=dict(status='THREE_PAIRED_COLD_STAR_PROCESS_BENCHMARKS_PASS',inputs_sha256=inputs,outputs_sha256=outputs,trials=trials,
                median_paired_process_ratio=statistics.median(r['paired_CPU_over_GPU_process_ratio'] for r in trials),
                median_cpu_process_seconds=statistics.median(r['runs']['cpu']['process_wall_seconds'] for r in trials),
                median_gpu_process_seconds=statistics.median(r['runs']['gpu']['process_wall_seconds'] for r in trials),
                elapsed_seconds=time.perf_counter()-start,
                timing_scope='Both process wall times include startup/imports, same binary read/parse/validation, cold iterations, all requested host scalar checkpoints and final scalar JSON write. Wrapper hash checks are outside each timed interval. No vector outputs.',
                workload='Same saved candidates25496+26025 and checkpoints1,2,10,500,2000, scalar output only, cold probabilities/dual each process.',
                environment_scope='Warm OS/file cache after prior controls; one thread requested for CPU numerical libraries; concurrent unrelated CPU stronger-LP research. Three trials do not establish general hardware throughput.',
                new_LP_runs=0,new_domain_enumerations=0,exclusions_claimed=0)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],median_ratio=result['median_paired_process_ratio'],sha256=digest(out/'summary.json'))),flush=True)

if __name__=='__main__':main()
