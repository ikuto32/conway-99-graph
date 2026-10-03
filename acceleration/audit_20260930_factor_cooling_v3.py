"""Independent cooling saved-state/domain/score and checkpoint-carry audit."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
from audit_20260930_factor_permutation_trace import read_input,bind_core,factor,exact_score,need
from audit_20260930_factor_annealing_objective import evaluate

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'acceleration/results/20260930_factor_annealer_cooling_v3'
GATE=ROOT/'acceleration/results/20260930_independent_review/factor_resume_v3/summary.json'
GATE_SHA='2c08fb8e4fb2c67179a9ad130cfe4109f43d4dd51719f3abd1e8694070d78ab6'
RUN_SHA='7c454cbd3e61f7700e588d3f58cd6598032652948904caf1424a7f43787d6895'
VERSION='TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1'

def digest(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()

def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')

def carry(state,old):
    need(state['current'][1:]==old['permutations'],'current permutations carried')
    need(state['best'][1:]==old['best_permutations'],'best permutations carried')
    need(state['rng']==int(old['rng']),'RNG state carried')
    need(state['proposals']==old['proposals'],'cumulative proposal counter carried')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);inputs={}
    def pin(p,h=None):
        value=digest(p);need(h is None or value==h,'artifact hash '+key(p));inputs[key(p)]=value;return value
    def read(p,h=None):pin(p,h);return json.loads(p.read_bytes())
    try:
        gate=read(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS','v3 public resume gate')
        for path,h in gate['inputs_sha256'].items():pin(ROOT/path,h)
        pilot=read(ROOT/'acceleration/results/20260930_independent_review/factor_annealer_pilot/summary.json','97858230f5e777d601554e51184f0cb3b57ce6d39ed022a3850005b49c27fdd5')
        correction=read(ROOT/'acceleration/results/20260930_independent_review/factor_annealer_pilot_availability_correction/summary.json','7e70341364942f018684633a8ec4a032429e9c94ea2d7d1af4a2041f1896a634');need(correction['corrected_value']=='LOCAL_ONLY','availability correction retained')
        for path,h in pilot['inputs_sha256'].items():pin(ROOT/path,h)
        run=read(RUN/'summary.json',RUN_SHA);manifest=read(RUN/'manifest.json',run['manifest_sha256'])
        for path,h in manifest['inputs_sha256'].items():pin(ROOT/path,h)
        expected=[dict(core=core,temperature=temp,label=core+'_T'+str(temp).replace('.','_'),seed=seed,chains=16,chunks=16,steps=1024,seconds=120,supervisor_seconds=120,maximum_new_proposals=262144)for core,seed in [('shift6',20260930),('six_prism',20260931)]for temp in(.25,0)]
        need(manifest['planned_cases']==expected and [r['case']for r in run['cases']]==expected,'frozen four-stage population')
        need([run[k]for k in('attempted_stages','completed_stages','errors','resource_stops','skipped_stages')]==[4,4,0,0,0],'actual stage accounting')
        need(run['distinct_resumed_chains']==32 and run['new_chain_initializations']==0,'population labels')
        rawshift=read(ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf/scope.json')['core'];shift=[[0]*36 for _ in range(36)]
        for g in range(3):
            for i,j in enumerate(rawshift['internal_matchings'][g]):shift[12*g+i][12*g+j]=1
        for g,h,p in[(0,1,rawshift['F01']),(0,2,rawshift['F02']),(1,2,rawshift['P12'])]:
            for i,j in enumerate(p):shift[12*g+i][12*h+j]=shift[12*h+j][12*g+i]=1
        cores={'shift6':shift,'six_prism':read(ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/derived_geometry.json')['core_adjacency']}
        fixture=read(ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json');positive=evaluate(fixture['cubic_core60'],fixture['factor60x180']);need(positive['score']==0 and not positive['mixed_cap_violations'] and not positive['column_overlap_violations'],'nonempty positive243')
        altered=deepcopy(fixture['factor60x180'])
        for row in altered[20:40]:row[0],row[1]=row[1],row[0]
        need(evaluate(fixture['cubic_core60'],altered)['score']==24,'valid-domain corrupted Gram score24')
        controls=[]
        for label in('nonbinary','wrong_C0','broken_permutation','wrong_core'):
            c=deepcopy(fixture['cubic_core60']);f=deepcopy(fixture['factor60x180'])
            if label=='nonbinary':f[20][0]=True
            elif label=='wrong_C0':f[0][0]^=1
            elif label=='broken_permutation':f[20][0]^=1
            else:c[0][1]^=1
            try:evaluate(c,f)
            except ValueError as e:controls.append(dict(control=label,outcome='REJECTED',reason=str(e)))
            else:raise AssertionError(label)
        records=[];raw_checks=[];final_checks=[];new_proposals=0;previous_stage={};latest_example=None
        for record,case in zip(run['cases'],expected):
            directory=RUN/case['label'];core=cores[case['core']]
            need(record['actual_exit_code']==0 and record['stage']=='COMPLETED' and record['supervisor_expired']is False,'completed subprocess')
            need(read(RUN/(case['label']+'.receipt.json'))==record,'outer saved receipt')
            summary=read(ROOT/record['summary'],record['summary_sha256']);need(summary['completed_chunks']==16 and summary['objective_version']==VERSION,'sixteen completed chunks')
            for path,h in{**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/path,h)
            config=summary['configuration'];need(config['independent_gate_sha256']==GATE_SHA and Path(config['independent_gate']).resolve()==GATE and config['temperature']==case['temperature'],'v3 configured gate/temperature')
            resume=ROOT/record['resume_path'];oldcp=read(resume,record['resume_sha256'])
            want=(ROOT/f"acceleration/results/20260930_factor_annealer_pilot/{case['core']}_T1/checkpoint_00007.json")if case['temperature']==.25 else previous_stage[case['core']]
            need(resume==want and Path(config['resume']).resolve()==resume,'declared original/stage resume chain')
            need(oldcp['problem']['core_adjacency']==core and oldcp['objective_version']==VERSION,'resumed raw core/objective')
            previous=oldcp['chains'];need(len(previous)==16 and sum(x['proposals']for x in previous)==record['initial_proposal_total'],'initial chain population/counters')
            starting_total=record['initial_proposal_total'];starting_min=None;chunk_minima=[];final_raw=[]
            for chunk in range(16):
                prefix=f'{chunk:05d}';problem=read_input(directory/f'chunk_{prefix}.txt');bind_core(problem,core)
                need((problem['n'],problem['chains'],problem['steps'],problem['mode'],problem['temperature'])==(12,16,1024,1,case['temperature']),'native input domain/configuration')
                native=read(directory/f'chunk_{prefix}.json');cp=read(directory/f'checkpoint_{prefix}.json');receipt=read(directory/f'chunk_{prefix}.receipt.json')
                need(receipt['returncode']==0 and receipt['input_sha256']==digest(directory/f'chunk_{prefix}.txt') and receipt['output_sha256']==digest(directory/f'chunk_{prefix}.json'),'native receipt exact bytes')
                need(cp['chains']==native['chains'] and cp['chunk']==chunk and cp['problem']==oldcp['problem'],'checkpoint/native/raw domain equality')
                need(cp['source_sha256']==gate['inputs_sha256']['acceleration/factor_permutation_anneal_20260930_v2.cu'] and cp['binary_sha256']==gate['inputs_sha256']['acceleration/build/factor_permutation_anneal_20260930_v2.exe'],'unchanged native source/binary')
                need(len(native['chains'])==16,'complete saved chains');scores=[];start_scores=[]
                for chain,(state,saved,old)in enumerate(zip(problem['states'],native['chains'],previous)):
                    carry(state,old);latest_example=(deepcopy(state),deepcopy(old))
                    need(saved['proposals']==old['proposals']+1024 and len(saved['trace'])==1024,'incremental proposal counters');new_proposals+=len(saved['trace'])
                    initial_best,_=exact_score(problem,state['best']);start_scores.append(initial_best)
                    current=[list(range(60))]+saved['permutations'];best=[list(range(60))]+saved['best_permutations'];score,_=exact_score(problem,current);bestscore,_=exact_score(problem,best)
                    need(score==saved['score'] and bestscore==saved['best_score'] and bestscore<=score and bestscore<=initial_best,'saved exact current/best objective and monotone best')
                    scores.append(bestscore)
                    if chunk==15:
                        for kind,perms,claimed in[('current',current,score),('best',best,bestscore)]:
                            f=factor(problem,perms);checked=evaluate(core,f);need(checked['score']==claimed,'independent raw bitset objective')
                            final_raw.append(dict(chain=chain,kind=kind,core_adjacency=core,factor=f,claimed_score=claimed,objective_version=VERSION,target_graph=False));final_checks.append(dict(stage=case['label'],chain=chain,kind=kind,**checked))
                if chunk==0:starting_min=min(start_scores);need(starting_min==record['initial_best_reported_score'],'independent starting minimum')
                raw=read(directory/f'best_{prefix}.json');need(raw['core_adjacency']==core and raw['objective_version']==VERSION,'raw chunk-best core/objective');checked=evaluate(core,raw['factor']);need(raw['claimed_score']==checked['score']==min(scores),'exact chunk best score')
                need(any(raw['factor']==factor(problem,[list(range(60))]+ch['best_permutations'])for ch in native['chains']if ch['best_score']==min(scores)),'raw object belongs to actual saved best chain')
                chunk_minima.append(checked['score']);raw_checks.append(dict(stage=case['label'],chunk=chunk,raw_path=key(directory/f'best_{prefix}.json'),**checked));previous=native['chains']
            last=directory/'checkpoint_00015.json';need(key(last)==record['last_checkpoint'] and digest(last)==record['last_checkpoint_sha256'],'last checkpoint pointer/hash')
            need(sum(x['proposals']for x in previous)-starting_total==record['observed_new_proposals']==262144,'stage proposal total difference')
            need(chunk_minima[-1]==min(chunk_minima)==summary['best_score']==record['final_best_reported_score'],'exact stage final minimum')
            need(summary['best_raw_object']==key(directory/'best_00015.json'),'saved final best pointer')
            previous_stage[case['core']]=last;save(out/(case['label']+'_final_states.json'),final_raw)
            records.append(dict(case=case,resume_path=key(resume),resume_sha256=digest(resume),initial_best_score=starting_min,chunk_best_scores=chunk_minima,final_best_score=chunk_minima[-1],stage_new_proposal_records=262144,final_current_states=16,final_best_states=16))
        need(new_proposals==run['completed_new_proposals']==1048576 and len(raw_checks)==64 and len(final_checks)==128,'exact saved populations')
        for label in('current','best','rng','proposals'):
            state,old=deepcopy(latest_example)
            if label in('current','best'):state[label][1][0],state[label][1][1]=state[label][1][1],state[label][1][0]
            else:state[label]+=1
            try:carry(state,old)
            except ValueError as e:controls.append(dict(control='altered_carry_'+label,outcome='REJECTED',reason=str(e)))
            else:raise AssertionError(label)
        raw=deepcopy(final_raw[0]);raw['claimed_score']+=1
        try:need(evaluate(raw['core_adjacency'],raw['factor'])['score']==raw['claimed_score'],'saved score identity')
        except ValueError as e:controls.append(dict(control='altered_claimed_score',outcome='REJECTED',reason=str(e)))
        else:raise AssertionError('false score')
        save(out/'controls.json',dict(positive243_score=positive['score'],positive243_no_cap_violations=True,valid_domain_corruption_score=24,corruptions=controls));save(out/'saved_states.json',dict(chunk_best=raw_checks,final_states=final_checks))
        for p in[Path(__file__),ROOT/'acceleration/audit_20260930_factor_permutation_trace.py',ROOT/'acceleration/audit_20260930_factor_annealing_objective.py',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();claim_id='C-FACTOR-PERMUTATION-ANNEALER-COOLING-SAVED-STATES'
        statement='All64 saved chunk-best and64 stage-final-current plus64 stage-final-best factors from the frozen four-stage cooling run satisfy their two declared permutation domains and exact recorded integer scores, with verified checkpoint continuation of32 prior chains and minima164 to134 to124 for shift6 and184 to146 to142 for six-prism; none of these saved states has score zero.'
        dependencies=[dict(id=name,revision=1,relation=relation)for name,relation in [('C-FACTOR-PERMUTATION-PUBLIC-JSON-RESUME-CALIBRATION','verification_dependency'),('C-FACTOR-PERMUTATION-ANNEALER-PILOT-SAVED-STATES','uses_result'),('C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL','verification_dependency'),('C-FIXED-TRIANGLE-JOINT-BINARY-FACTOR-CNF-ENCODING','uses_result'),('C-SIX-PRISM-COMPLETE-COLUMN-FACTOR-CNF','uses_result')]]
        report=dict(status='INDEPENDENT_FACTOR_ANNEALER_COOLING_SAVED_STATES_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},claim_id=claim_id,claim_revision=1,statement=statement,kind='empirical/engineering result',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='Saved-state scores/domain and actual checkpoint carry across four cooling stages in two fixed cores, not a factor construction or target exclusion.',dependencies=dependencies,assumptions=['No nontrivial target automorphism is assumed.','Exact frozen artifacts and stated integer objective.'],verifier='/root/state_literature_audit independent raw-state and checkpoint checker',method='independent_artifact_check',shared_components=['Frozen independent full columnwise objective and separately authored bitset raw-factor validator.','Python standard library; no producer imports.'],cases=records,stage_counts=dict(attempted=4,completed=4,errors=0,skipped=0),chunk_best_states=64,stage_final_current_states=64,stage_final_best_states=64,continued_chain_population=32,used_chain_reinitializations=0,new_saved_proposal_records=1048576,checkpoint_current_scores_checked=1024,checkpoint_best_scores_checked=1024,positive_controls=2,malformed_controls=len(controls),objective_version=VERSION,artifact_availability='LOCAL_ONLY',retrieval='Existing local paths pinned by this report; public immutable publication has not been confirmed.',target_resolution=False,external_review=False,created_at=now,updated_at=now,
          limitations=['All 1048576 records were counted; individual campaign transition deltas, acceptance and RNG progression were not replayed.','Checkpoint input RNG/current/best/counters match the preceding saved state exactly; this does not claim the wrapper never computes an unused seeded temporary before loading its checkpoint.','Stage-chain populations overlap:64 per-stage endpoints represent32 continuing chain identities.','Positive scores and observed improvements are not mathematical bounds or exclusions; caps are checked only as diagnostics.','No performance or target-wide coverage conclusion.'],overall_search_coverage='UNKNOWN; no validated denominator.')
        save(out/'summary.json',report)
        binding=dict(status='INDEPENDENT_COOLING_CLAIM_BINDING_PASS',claim_id=claim_id,claim_revision=1,statement=statement,kind=report['kind'],basis=report['basis'],recommendation='VERIFIED',review_state='CLEAR',scope=report['scope'],dependencies=dependencies,assumptions=report['assumptions'],evidence=[dict(path=key(out/'summary.json'),sha256=digest(out/'summary.json'),availability='LOCAL_ONLY')],verification=[dict(claim_revision=1,verifier=report['verifier'],method='independent_artifact_check',command_or_audit=key(out/'summary.json'),timestamp=now,outcome='PASS',scope=report['scope'],artifact_hashes={key(out/'summary.json'):digest(out/'summary.json')},shared_components=report['shared_components'])],limitations=report['limitations'],created_at=now,updated_at=now,artifact_availability='LOCAL_ONLY',ledger_changed=False)
        save(out/'claim_binding.json',binding);print(json.dumps(dict(status=report['status'],summary_sha256=digest(out/'summary.json'),binding_sha256=digest(out/'claim_binding.json'),minima=[r['final_best_score']for r in records])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise

if __name__=='__main__':main()
