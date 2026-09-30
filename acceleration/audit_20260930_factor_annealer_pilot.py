"""Independent saved-state pilot audit; never imports an annealer producer."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys

from audit_20260930_factor_permutation_trace import read_input, bind_core, factor, exact_score, need
from audit_20260930_factor_annealing_objective import evaluate

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT/'acceleration/results/20260930_factor_annealer_pilot'
GATE = ROOT/'acceleration/results/20260930_independent_review/factor_permutation_annealer_bound/summary.json'
GATE_SHA = '70c54735a3331f4bc9dff3ace2f5d1dd4bae49ec051f415a262538f9385b20b9'
RUN_SHA = 'f238c8d42da208323c35a9424bf4f4b66b1db6421dac89144c494210e6869de9'
OBJECTIVE = 'TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1'

def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def key(p): return p.resolve().relative_to(ROOT).as_posix()

def save(p, x):
    with p.open('x', encoding='utf-8', newline='\n') as f: json.dump(x, f, indent=2); f.write('\n')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    out=a.out.resolve(); out.mkdir(parents=True,exist_ok=False); inputs={}
    def pin(p, expected=None):
        sha=digest(p); need(expected is None or sha==expected, 'artifact hash: '+key(p)); inputs[key(p)]=sha; return sha
    def read(p, expected=None): pin(p,expected); return json.loads(p.read_bytes())
    gate=read(GATE,GATE_SHA); need(gate['status']=='INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS','calibration gate')
    for path,sha in gate['inputs_sha256'].items(): pin(ROOT/path,sha)
    for p in [Path(__file__),ROOT/'acceleration/audit_20260930_factor_permutation_trace.py',ROOT/'acceleration/audit_20260930_factor_annealing_objective.py',ROOT/'uv.lock',ROOT/'pyproject.toml']: pin(p)
    run=read(RUN/'summary.json',RUN_SHA); manifest=read(RUN/'manifest.json',run['manifest_sha256'])
    for path,sha in manifest['inputs_sha256'].items(): pin(ROOT/path,sha)
    expected=[dict(core=core,seed=seed,temperature=t,chains=16,chunks=8,steps=1024,seconds=120,label=core+'_T'+str(t).replace('.','_')) for core,seed in [('shift6',20260930),('six_prism',20260931)] for t in (1,3.25,8)]
    need(manifest['cases']==expected and len(run['cases'])==6,'frozen six-case population')
    need([run[k] for k in ('attempted_cases','completed_cases','error_cases','skipped_cases')]==[6,6,0,0],'case accounting')
    raw_shift=read(ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf/scope.json')['core']
    shift=[[0]*36 for _ in range(36)]
    for g in range(3):
        for i,j in enumerate(raw_shift['internal_matchings'][g]): shift[12*g+i][12*g+j]=1
    for g,h,p in [(0,1,raw_shift['F01']),(0,2,raw_shift['F02']),(1,2,raw_shift['P12'])]:
        for i,j in enumerate(p): shift[12*g+i][12*h+j]=shift[12*h+j][12*g+i]=1
    prism=read(ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/derived_geometry.json')['core_adjacency']
    cores={'shift6':shift,'six_prism':prism}
    fixture=read(ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json')
    positive=evaluate(fixture['cubic_core60'],fixture['factor60x180'])
    need(positive['score']==0 and not positive['mixed_cap_violations'] and not positive['column_overlap_violations'],'positive nonempty243')
    controls=[]
    for label in ('nonbinary','wrong_C0','broken_permutation','wrong_core'):
        c=deepcopy(fixture['cubic_core60']); f=deepcopy(fixture['factor60x180'])
        if label=='nonbinary': f[20][0]=True
        elif label=='wrong_C0': f[0][0]^=1
        elif label=='broken_permutation': f[20][0]^=1
        else: c[0][1]^=1
        try: evaluate(c,f)
        except ValueError as e: controls.append(dict(label=label,outcome='REJECTED',reason=str(e)))
        else: raise AssertionError(label)
    altered=deepcopy(fixture['factor60x180'])
    for row in altered[20:40]: row[0],row[1]=row[1],row[0]
    need(evaluate(fixture['cubic_core60'],altered)['score']==24,'domain-preserving score24 calibration')
    cases=[]; raw_records=[]; final_records=[]; proposals=0
    for record,case in zip(run['cases'],expected):
        need(record['case']==case and record['exit_code']==0 and record['stage']=='COMPLETED','case recipe and exit')
        directory=RUN/case['label']; summary=read(ROOT/record['summary'],record['summary_sha256'])
        need(summary['completed_chunks']==8 and summary['objective_version']==OBJECTIVE,'eight chunks/objective')
        need(read(RUN/(case['label']+'.receipt.json'))==record,'outer receipt identity')
        for path,sha in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items(): pin(ROOT/path,sha)
        need(summary['binary_sha256']==gate['inputs_sha256']['acceleration/build/factor_permutation_anneal_20260930_v2.exe'],'native binary identity')
        core=cores[case['core']]; previous=None; chunk_best=[]; final_raw=[]
        for chunk in range(8):
            prefix=f'{chunk:05d}'; problem=read_input(directory/f'chunk_{prefix}.txt'); bind_core(problem,core)
            need((problem['n'],problem['chains'],problem['steps'],problem['mode'],problem['temperature'])==(12,16,1024,1,case['temperature']),'native recipe')
            native=read(directory/f'chunk_{prefix}.json'); checkpoint=read(directory/f'checkpoint_{prefix}.json'); receipt=read(directory/f'chunk_{prefix}.receipt.json')
            need(receipt['returncode']==0 and receipt['input_sha256']==digest(directory/f'chunk_{prefix}.txt') and receipt['output_sha256']==digest(directory/f'chunk_{prefix}.json'),'native receipts')
            need(checkpoint['chains']==native['chains'] and checkpoint['chunk']==chunk,'checkpoint raw native state equality')
            need(checkpoint['problem']['core_adjacency']==core and checkpoint['problem']['target']==problem['target'] and checkpoint['problem']['edges']==problem['edges'],'checkpoint problem binding')
            need(checkpoint['source_sha256']==gate['inputs_sha256']['acceleration/factor_permutation_anneal_20260930_v2.cu'] and checkpoint['binary_sha256']==summary['binary_sha256'],'checkpoint engine binding')
            need(len(native['chains'])==16,'all chains saved')
            scores=[]
            for chain,(state,saved) in enumerate(zip(problem['states'],native['chains'])):
                need(saved['proposals']==(chunk+1)*1024 and len(saved['trace'])==1024,'saved proposal accounting')
                proposals+=len(saved['trace'])
                if previous is not None:
                    old=previous[chain]
                    need(state['current'][1:]==old['permutations'] and state['best'][1:]==old['best_permutations'] and state['rng']==int(old['rng']) and state['proposals']==old['proposals'],'resumption preserves saved state')
                current=[list(range(60))]+saved['permutations']; best=[list(range(60))]+saved['best_permutations']
                score,_=exact_score(problem,current); best_score,_=exact_score(problem,best)
                need(score==saved['score'] and best_score==saved['best_score'] and best_score<=score,'saved current/best exact scores')
                scores.append(best_score)
                if chunk==7:
                    for label,perms,claimed in [('current',current,score),('best',best,best_score)]:
                        f=factor(problem,perms); checked=evaluate(core,f); need(checked['score']==claimed,'second raw-object score path')
                        final_raw.append(dict(chain=chain,kind=label,core_adjacency=core,factor=f,claimed_score=claimed,objective_version=OBJECTIVE,target_graph=False))
                        final_records.append(dict(case=case['label'],chain=chain,kind=label,**checked))
            raw=read(directory/f'best_{prefix}.json'); need(raw['core_adjacency']==core,'chunk best exact core')
            result=evaluate(core,raw['factor']); need(raw['objective_version']==OBJECTIVE and raw['claimed_score']==result['score']==min(scores),'chunk best exact score/minimum')
            candidates=[factor(problem,[list(range(60))]+ch['best_permutations']) for ch in native['chains'] if ch['best_score']==min(scores)]
            need(raw['factor'] in candidates,'chunk raw best is an actual saved chain best')
            chunk_best.append(result['score']); raw_records.append(dict(case=case['label'],chunk=chunk,raw_path=key(directory/f'best_{prefix}.json'),**result)); previous=native['chains']
        need(summary['best_score']==record['reported_best_score']==chunk_best[-1]==min(chunk_best),'reported case minimum')
        need(summary['best_raw_object']==key(directory/'best_00007.json'),'reported final raw pointer')
        save(out/(case['label']+'_final_states.json'),final_raw)
        cases.append(dict(case=case,chunk_best_scores=chunk_best,minimum_saved_score=min(chunk_best),final_current_states=16,final_best_states=16,chunk_best_states=8))
    need(proposals==786432 and len(raw_records)==48 and len(final_records)==192,'exact saved populations')
    for label in ('wrong_saved_score','wrong_saved_core'):
        raw=deepcopy(final_raw[0])
        if label=='wrong_saved_score': raw['claimed_score']+=1
        else: raw['core_adjacency'][0][1]^=1
        try:
            need(raw['core_adjacency']==cores[case['core']],'intended fixed core'); result=evaluate(raw['core_adjacency'],raw['factor']); need(result['score']==raw['claimed_score'],'claimed score identity')
        except ValueError as e: controls.append(dict(label=label,outcome='REJECTED',reason=str(e)))
        else: raise AssertionError(label)
    save(out/'controls.json',dict(positive243=positive,valid_domain_swapped_score=24,corruptions=controls))
    save(out/'saved_states.json',dict(chunk_best=raw_records,final_states=final_records))
    outputs={key(p):digest(p) for p in out.iterdir() if p.is_file()}
    report=dict(status='INDEPENDENT_FACTOR_ANNEALER_PILOT_SAVED_STATES_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,outputs_sha256=outputs,
      claim_id='C-FACTOR-PERMUTATION-ANNEALER-PILOT-SAVED-STATES',claim_revision=1,verifier='Independent state_literature_audit checking path',checking_method='Independent raw column-count reconstruction plus separate bitset full-object evaluator; no producer imports.',
      statement='For the six frozen two-core pilot cases, all 48 saved chunk-best objects and all 96 final-current and 96 final-best objects satisfy their declared permutation-factor domains and have the exact recorded integer objective scores; none has objective zero.',
      cases=cases,completed_cases=6,error_cases=0,skipped_cases=0,final_current_states=96,final_best_states=96,chunk_best_states=48,all_checkpoint_chain_current_scores_checked=768,all_checkpoint_chain_best_scores_checked=768,saved_proposal_records=proposals,
      objective_version=OBJECTIVE,scope='These are saved-state correctness checks in the two fixed core domains, not target existence or nonexistence and not search coverage.',
      independent_controls=6,target_resolution=False,overall_search_coverage='UNKNOWN; no validated denominator.',
      limitations=['No campaign transition deltas, acceptance decisions or RNG trajectories replayed; native calibration covers only its saved finite controls.','The 786432 figure counts saved proposal records, not distinct factors or independently replayed transitions.','Caps are measured diagnostics and may fail; no constraint exclusion follows from a positive score.','No timing or speedup conclusion.','Independent helpers are shared with previous audits and Python standard library; no producer scorer imported.'],artifact_availability='PUBLIC')
    save(out/'summary.json',report); print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'),minima=[c['minimum_saved_score'] for c in cases])))

if __name__=='__main__': main()
