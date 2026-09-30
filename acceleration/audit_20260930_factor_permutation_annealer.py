"""Independent frozen CPU/GPU trajectories, exact objective and restart calibration."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import platform
import subprocess
import sys
import time
import audit_20260930_factor_permutation_trace as trace
import audit_20260930_factor_annealing_objective as raw

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_factor_permutation_annealer_calibration_v2'
OLD=ROOT/'acceleration/results/20260930_factor_permutation_annealer_calibration'
SUMMARY_SHA='bc20553c5da3713f66f239d6a4e5bd761455c61d363902db2a1aaddc720d9993'
SOURCE=ROOT/'acceleration/factor_permutation_anneal_20260930_v2.cu'
EXE=ROOT/'acceleration/build/factor_permutation_anneal_20260930_v2.exe'
RAW_GATE=ROOT/'acceleration/results/20260930_independent_review/factor_annealing_objective_calibration/summary.json'
RAW_GATE_SHA='3e18e7a9684f8d04db65f5ce8e0af45705cf35da1ce05c3c62494a42c58ceb08'
need=trace.need
def digest(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,value):
    with p.open('x',encoding='utf-8')as f:json.dump(value,f,indent=2);f.write('\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(p,expected=None):
        value=digest(p);need(expected is None or value==expected,'hash '+str(p));bindings[key(p)]=value;return p
    def read(p,expected=None):return json.loads(bind(p,expected).read_bytes())
    try:
        summary=read(D/'summary.json',SUMMARY_SHA);manifest=read(D/'manifest.json')
        for source in[summary,manifest]:
            for p,sha in source['inputs_sha256'].items():bind(ROOT/p,sha)
        for p,sha in summary['outputs_sha256'].items():bind(ROOT/p,sha)
        bind(EXE,summary['binary_sha256'])
        gate=read(RAW_GATE,RAW_GATE_SHA);need(gate['status']=='INDEPENDENT_FACTOR_OBJECTIVE_RAW_CHECKER_CALIBRATION_PASS','separate exact raw-object reference gate')
        for p,sha in gate['inputs_sha256'].items():bind(ROOT/p,sha)
        oldmanifest=read(OLD/'manifest.json');oldfailure=read(OLD/'failure.json');oldbuild=read(OLD/'build_receipt.json')
        for p,sha in oldmanifest['inputs_sha256'].items():bind(ROOT/p,sha)
        oldsource=(ROOT/'acceleration/factor_permutation_anneal_20260930.cu').read_text();newsource=SOURCE.read_text()
        wrong='int((s.rows[r][b/64]>>(b%64))&1ULL;'
        right='int((s.rows[r][b/64]>>(b%64))&1ULL);'
        need(oldsource.count(wrong)==1 and oldsource.replace(wrong,right)==newsource,'only missing-parenthesis native correction')
        need(oldbuild['returncode']!=0 and oldbuild['binary_sha256']is None and oldfailure['error']=='build','preserved compile failure before execution')
        build=read(D/'build_receipt.json')
        need(build['returncode']==0 and build['binary_sha256']==digest(EXE),'successful exact binary receipt')
        need('V13.2.78'in build['nvcc_version']and'19.51.36243.0'in build['stdout'],'recorded actual compiler versions')
        builder=(ROOT/'acceleration/build_factor_permutation_anneal_20260930_v2.ps1').read_text()
        need(all(flag in builder for flag in['sm_89','-O3','-std=c++17','--fmad=false','/O2']),'bound build configuration')
        problems={};cores={};records=[];raw_records=[];normal_moves=0;checkpoint_moves=0;boundary_checks=[]
        def inspect_raw(path,expected_factor=None,expected_score=None):
            obj=read(path);result=raw.evaluate(obj['core_adjacency'],obj['factor'])
            need(obj['objective_version']=='TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1'and obj['target_graph']is False,'raw objective/version/scope')
            need(type(obj['claimed_score'])is int and obj['claimed_score']==result['score'],'raw claimed exact score')
            if expected_factor is not None:need(obj['factor']==expected_factor,'exported raw factor from actual permutations')
            if expected_score is not None:need(result['score']==expected_score,'raw score from independent trace')
            raw_records.append(dict(path=key(path),sha256=digest(path),score=result['score'],block_scores=result['block_scores_01_02_12'],mixed_violations=len(result['mixed_cap_violations']),column_violations=len(result['column_overlap_violations'])))
            return obj,result
        def receipt(stem,backend):
            r=read(D/f'{stem}_{backend}.receipt.json');need(r['returncode']==0 and r['input_sha256']==digest(D/f'{stem}.txt')and r['output_sha256']==digest(D/f'{stem}_{backend}.json'),'native receipt and full byte identities')
            need(Path(r['command'][0]).resolve()==EXE.resolve()and r['command'][1]==backend,'authenticated backend command')
        def replay(stem,label,both=True):
            p=trace.read_input(bind(D/f'{stem}.txt'));trace.bind_core(p,cores[label]);expected=problems[label]
            need(p['target']==expected['target']and p['edges']==expected['edges'],'input binds raw problem')
            output=read(D/f'{stem}_gpu.json')if both else read(D/f'{stem}.json')
            need(output['backend']=='gpu'and len(output['chains'])==p['chains'],'GPU backend/count')
            if both:
                cpu=read(D/f'{stem}_cpu.json');need(cpu['backend']=='cpu'and cpu['chains']==output['chains'],'complete CPU/GPU trajectory and checkpoint state parity');receipt(stem,'cpu');receipt(stem,'gpu')
            else:
                r=read(D/f'{stem}.receipt.json');need(r['returncode']==0 and r['input_sha256']==digest(D/f'{stem}.txt')and r['output_sha256']==digest(D/f'{stem}.json'),'split receipt identity')
            checks=[trace.audit_chain(p,state,result)for state,result in zip(p['states'],output['chains'])]
            return p,output,checks
        for label in['shift6','six_prism','fixture243']:
            record=read(D/f'{label}_problem.json');cores[label]=record['core_adjacency'];problems[label]=record
            initial=read(D/f'{label}_initial.json')
            for k,state in enumerate(initial):
                p=trace.read_input(D/f'{label}_forced.txt');trace.bind_core(p,cores[label])
                need(p['states'][k]['current'][1:]==state['permutations']and p['states'][k]['best'][1:]==state['best_permutations']and p['states'][k]['rng']==int(state['rng']),'raw initial input/state identity')
                exact,_=trace.exact_score(p,p['states'][k]['current']);inspect_raw(D/f'{label}_initial_chain{k}_raw.json',trace.factor(p,p['states'][k]['current']),exact)
            for name,mode,temperature in[('forced',0,0.0),('greedy',1,0.0),('anneal',1,3.25)]:
                stem=f'{label}_{name}';p,output,checks=replay(stem,label);need(p['steps']==64 and p['mode']==mode and p['temperature']==temperature,'declared calibration mode')
                for k,check in enumerate(checks):
                    normal_moves+=check['proposals'];inspect_raw(D/f'{stem}_chain{k}_raw_final.json',check.pop('final_factor'),check['final_score']);inspect_raw(D/f'{stem}_chain{k}_raw_best.json',check.pop('best_factor'),check['best_score'])
                records.append(dict(case=stem,chains=len(checks),checks=checks,device=output['device'],cuda_runtime=output['cuda_runtime'],cuda_driver=output['cuda_driver']))
            p1,o1,c1=replay(label+'_split_first',label,False);p2,o2,c2=replay(label+'_split_second',label,False)
            need(p1['steps']==23 and p2['steps']==41 and p1['mode']==p2['mode']==1 and p1['temperature']==p2['temperature']==3.25,'declared split protocol')
            whole=read(D/f'{label}_anneal_gpu.json')
            for k,(first,second,full)in enumerate(zip(o1['chains'],o2['chains'],whole['chains'])):
                need(first['trace']==full['trace'][:23]and second['trace']==full['trace'][23:],'complete split trace concatenation')
                need({k:v for k,v in second.items()if k!='trace'}=={k:v for k,v in full.items()if k!='trace'},'complete resume final state')
                need(p2['states'][k]['current'][1:]==first['permutations']and p2['states'][k]['best'][1:]==first['best_permutations']and p2['states'][k]['rng']==int(first['rng'])and p2['states'][k]['proposals']==first['proposals'],'exact persisted checkpoint inputs')
            checkpoint_moves+=sum(x['proposals']for x in c1+c2)
        for a,b in[(63,64),(127,128)]:
            stem=f'boundary_{a}_{b}';p,out,checks=replay(stem,'fixture243');need(p['steps']==1 and p['mode']==0 and out['chains'][0]['trace'][0][1:3]==[a,b],'explicit word boundary control')
            normal_moves+=1;check=checks[0];inspect_raw(D/f'{stem}_raw_final.json',check.pop('final_factor'),check['final_score']);check.pop('best_factor');boundary_checks.append(dict(columns=[a,b],check=check))
        need(normal_moves==962 and checkpoint_moves==320 and len(raw_records)==37,'actual bounded calibration populations')
        rejected=[]
        expected_errors={'zero_rng':'rng state','duplicate_permutation':'duplicate permutation','duplicate_catalog':'catalog duplicate','asymmetric_target':'target symmetry','trailing_input':'trailing input'}
        for label,error in expected_errors.items():
            r=read(D/f'bad_{label}.receipt.json');need(r['returncode']==2 and error in r['stderr']and r['output_sha256']is None,'actual malformed native rejection')
            need(r['input_sha256']==digest(D/f'bad_{label}.txt')and not(D/f'bad_{label}.json').exists(),'malformed bytes preserved and no output');rejected.append(label)
        p=trace.read_input(D/'shift6_forced.txt');positive=read(D/'shift6_forced_gpu.json')['chains'][0]
        for label in['delta','acceptance','final_rng','best_permutation','final_score']:
            bad=deepcopy(positive)
            if label=='delta':bad['trace'][0][3]+=1
            elif label=='acceptance':bad['trace'][0][4]^=1
            elif label=='final_rng':bad['rng']=str(int(bad['rng'])^1)
            elif label=='best_permutation':bad['best_permutations'][0][0]=bad['best_permutations'][0][1]
            else:bad['score']+=1
            try:trace.audit_chain(p,p['states'][0],bad)
            except ValueError:rejected.append('independent_'+label)
            else:raise ValueError('independent corruption accepted '+label)
        for label in['target','catalog','core']:
            bad=deepcopy(p);core=deepcopy(cores['shift6'])
            if label=='target':bad['target'][0][12]+=1
            elif label=='catalog':bad['edges'][0][0]=bad['edges'][0][1]
            else:core[0][1]=0
            try:trace.bind_core(bad,core)
            except ValueError:rejected.append('independent_'+label)
            else:raise ValueError('binding corruption accepted '+label)
        save(args.out/'trace_checks.json',dict(cases=records,boundary_checks=boundary_checks,main_and_boundary_proposals=normal_moves,replayed_checkpoint_proposals=checkpoint_moves,raw_objects=raw_records))
        save(args.out/'controls.json',dict(actual_native_malformed_rejections=5,fresh_independent_corruption_rejections=8,rejected=rejected,known243_initial_score=next(r['score']for r in raw_records if'fixture243_initial'in r['path']),positive_reference_gate_sha256=RAW_GATE_SHA))
        for p in[Path(__file__),Path(trace.__file__),Path(raw.__file__),ROOT/'docs/AUDIT_20260930_FACTOR_PERMUTATION_ANNEALER.md']:bind(p)
        need(all(digest(ROOT/p)==sha for p,sha in bindings.items()),'stable exact input bytes')
        report=dict(status='INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/state_literature_audit independent input/column-accumulation trace and raw-object checker',kind='empirical/engineering result',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
          statement='The frozen v2 annealer passes the saved finite CPU/GPU calibration: all962 main/boundary proposal deltas, decisions and current/best states agree with independent exact full-objective recomputation; all320 additional checkpoint-replayed proposals and37 raw initial/final/best objects check, with the specified controls.',
          scope='Finite saved calibration on two n12 fixed cores and the known n20 positive fixture, including forced/T0/T3.25 modes. Algebraic delta reasoning applies to the stated permutation domain; no universal floating trajectory claim.',
          objective_version='TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1',proposals_main_and_boundary=962,checkpoint_replayed_proposals=320,raw_objects_checked=37,actual_native_bad_controls=5,fresh_independent_corruptions=8,solver_calls=0,campaign_calls=0,
          source_correction='Exactly one missing close-parenthesis corrected from preserved v1; earlier compile failure launched no executable.',build=dict(binary_sha256=digest(EXE),nvcc_version=build['nvcc_version'],host_compiler_version='19.51.36243.0',architecture='sm_89',flags=['-O3','-std=c++17','--fmad=false','/O2']),
          independent_energy_path='Accumulate cross-cell row-pair counts by columns, then square all errors from scratch; no producer imports or popcount-delta reuse.',
          shared_components=['Python raw-object reference separately calibrated by root on independently checked SRG243 fixture.','Native CPU/GPU implementations share RNG/proposal/acceptance helpers; the independent checker separately replays the integer RNG and saved decisions.','Floating exponential comparisons checked only for saved cases away from threshold.'],
          artifacts=dict(trace_checks_sha256=digest(args.out/'trace_checks.json'),controls_sha256=digest(args.out/'controls.json')),
          limitations=['No campaign outcome, speedup or performance guarantee.','No universal host/device exp or trajectory equivalence.','Score zero is only an abstract factor; caps and residual D remain separate.','The243positive is not a Conway99candidate.','Compiler versions/build receipt are authenticated provenance, not a fresh diverse rebuild.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as error:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(error),inputs_sha256=bindings));raise
if __name__=='__main__':main()
