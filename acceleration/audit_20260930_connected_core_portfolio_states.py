"""Independent saved-state audit; no producer import or transition-replay claim."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import random
import subprocess
import sys
from audit_20260930_factor_permutation_trace import read_input, bind_core, factor, exact_score, need
from audit_20260930_factor_annealing_objective import evaluate
from audit_20260930_factor_cooling_v3 import carry

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT/'acceleration/results/20260930_connected_core_portfolio_pilot'
RUN_SHA = '7ad597591aa3f52120d2d1c4cb2646378007a2e11875296666f832f4b6c303a6'
GATE = ROOT/'acceleration/results/20260930_independent_review/factor_portfolio_v4/summary.json'
GATE_SHA = 'df3d3a9ef20c622ce9b529a1aabbba2df18e95ac3e17b1210a866d46657e3ae2'
DOMAIN = ROOT/'acceleration/results/20260930_independent_review/connected_identity_cores/summary.json'
DOMAIN_SHA = 'efdcacb9130bf29a28ece4c07022bdab11ab953a862f117fc55f44bd5244d2b4'
VERSION = 'TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1'

def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def key(p): return Path(p).resolve().relative_to(ROOT).as_posix()

def save(p, x):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(x, f, indent=2); f.write('\n')

def initial(seed):
    rng = random.Random(seed); result = []
    for _ in range(16):
        perms = [list(range(60)), list(range(60))]
        for row in perms: rng.shuffle(row)
        result.append(dict(rng=str(rng.randrange(1, 2**64)), proposals=0,
                           permutations=perms, best_permutations=deepcopy(perms)))
    return result

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    inputs = {}
    def pin(p, h=None):
        value = digest(p); need(h is None or value == h, 'artifact hash '+key(p))
        inputs[key(p)] = value; return value
    def read(p, h=None): pin(p, h); return json.loads(p.read_bytes())
    try:
        gate = read(GATE, GATE_SHA); domain = read(DOMAIN, DOMAIN_SHA)
        need(gate['status'] == 'INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS', 'wrapper gate')
        need(domain['status'] == 'INDEPENDENT_CONNECTED_IDENTITY_CORE_PORTFOLIO_PASS', 'domain gate')
        for audit in (gate, domain):
            for path, h in audit['inputs_sha256'].items(): pin(ROOT/path, h)
        selection = read(ROOT/'acceleration/results/20260930_connected_identity_cores/summary.json',
                         '3ab78be8b7a7582c730e4cfe4c95533a2bc68cecccdfca45fa7d3f8cd58190b5')
        cores = {f'connected_{i:02d}': read(ROOT/r['path'], r['sha256'])['core_adjacency']
                 for i, r in enumerate(selection['selected'])}
        run = read(RUN/'summary.json', RUN_SHA); manifest = read(RUN/'manifest.json', run['manifest_sha256'])
        for path, h in manifest['inputs_sha256'].items(): pin(ROOT/path, h)
        expected = [dict(core=f'connected_{i:02d}', core_index=i, temperature=t,
                         label=f'connected_{i:02d}_T'+str(t).replace('.', '_'), seed=20260930+i,
                         chains=16, chunks=8, steps=1024, seconds=120, supervisor_seconds=120,
                         maximum_new_proposals=131072) for i in range(4) for t in (1, .25, 0)]
        need(manifest['planned_cases'] == expected and [r['case'] for r in run['cases']] == expected,
             'frozen 12-phase population')
        need([run[k] for k in ('attempted_phases','completed_phases','errors','resource_stops','skipped_phases')]
             == [12,12,0,0,0], 'phase accounting')
        need(run['distinct_initialized_chains_with_saved_checkpoints'] == 64 and
             run['stage_chain_endpoints_with_saved_checkpoints'] == 192, 'chain populations')
        fixture = read(ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json')
        positive = evaluate(fixture['cubic_core60'], fixture['factor60x180'])
        need(positive['score'] == 0 and not positive['mixed_cap_violations'] and
             not positive['column_overlap_violations'], 'nonempty SRG243 positive')
        f = deepcopy(fixture['factor60x180'])
        for row in f[20:40]: row[0], row[1] = row[1], row[0]
        need(evaluate(fixture['cubic_core60'], f)['score'] == 24, 'positive-domain score24 control')
        controls = []
        for label in ('nonbinary','wrong_C0','broken_permutation','wrong_core'):
            c = deepcopy(fixture['cubic_core60']); f = deepcopy(fixture['factor60x180'])
            if label == 'nonbinary': f[20][0] = True
            elif label == 'wrong_C0': f[0][0] ^= 1
            elif label == 'broken_permutation': f[20][0] ^= 1
            else: c[0][1] ^= 1
            try: evaluate(c, f)
            except ValueError as e: controls.append(dict(control=label,outcome='REJECTED',reason=str(e)))
            else: raise AssertionError(label)
        records=[]; raw_checks=[]; final_checks=[]; previous_phase={}; proposals=0; score_count=0
        for record, case in zip(run['cases'], expected):
            directory=RUN/case['label']; core=cores[case['core']]
            need(record['actual_exit_code']==0 and record['stage']=='COMPLETED' and
                 record['supervisor_expired'] is False, 'actual phase completion')
            need(read(RUN/(case['label']+'.receipt.json')) == record, 'saved outer receipt')
            summary=read(ROOT/record['summary'], record['summary_sha256'])
            need(summary['completed_chunks']==8 and summary['objective_version']==VERSION, 'phase summary')
            for path,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items(): pin(ROOT/path,h)
            config=summary['configuration']
            need(config['independent_gate_sha256']==GATE_SHA and Path(config['independent_gate']).resolve()==GATE,
                 'source gate binding')
            need(config['portfolio_domain_gate_sha256']==DOMAIN_SHA and
                 Path(config['portfolio_domain_gate']).resolve()==DOMAIN, 'raw domain gate binding')
            need(config['core']==case['core'] and config['temperature']==case['temperature'] and
                 config['seed']==case['seed'], 'phase configuration')
            if case['temperature']==1:
                need(record['resume_path'] is None and record['resume_sha256'] is None and config['resume'] is None,
                     'only initial phase has no resume')
                previous=initial(case['seed']); old_problem=None; resume=None
                need(record['initial_best_reported_score'] is None, 'unscored initial driver field')
            else:
                resume=ROOT/record['resume_path']; oldcp=read(resume,record['resume_sha256'])
                need(resume==previous_phase[case['core']] and Path(config['resume']).resolve()==resume,
                     'exact preceding phase resume')
                need(oldcp['problem']['core_adjacency']==core and oldcp['objective_version']==VERSION,
                     'resumed core and objective')
                previous=oldcp['chains']; old_problem=oldcp['problem']
            starting_total=sum(x['proposals'] for x in previous)
            need(len(previous)==16 and starting_total==record['initial_proposal_total'], 'initial counters')
            minima=[]; final_raw=[]; starting_min=None
            for chunk in range(8):
                prefix=f'{chunk:05d}'; problem=read_input(directory/f'chunk_{prefix}.txt'); bind_core(problem,core)
                need((problem['n'],problem['chains'],problem['steps'],problem['mode'],problem['temperature'])==
                     (12,16,1024,1,case['temperature']), 'native domain/configuration')
                native=read(directory/f'chunk_{prefix}.json'); cp=read(directory/f'checkpoint_{prefix}.json')
                receipt=read(directory/f'chunk_{prefix}.receipt.json')
                need(receipt['returncode']==0 and receipt['input_sha256']==digest(directory/f'chunk_{prefix}.txt') and
                     receipt['output_sha256']==digest(directory/f'chunk_{prefix}.json'), 'native receipt bytes')
                need(cp['chains']==native['chains'] and cp['chunk']==chunk and cp['problem']['core_adjacency']==core,
                     'checkpoint/native/domain identity')
                if old_problem is None: old_problem=cp['problem']
                need(cp['problem']==old_problem and cp['objective_version']==VERSION, 'unchanged problem')
                need(cp['source_sha256']==gate['inputs_sha256']['acceleration/factor_permutation_anneal_20260930_v2.cu'] and
                     cp['binary_sha256']==gate['inputs_sha256']['acceleration/build/factor_permutation_anneal_20260930_v2.exe'],
                     'unchanged native source/binary')
                need(len(native['chains'])==16, 'complete native chain population')
                scores=[]; start_scores=[]
                for chain,(state,saved,old) in enumerate(zip(problem['states'],native['chains'],previous)):
                    carry(state,old); example=(deepcopy(state),deepcopy(old))
                    need(saved['proposals']==old['proposals']+1024 and len(saved['trace'])==1024, 'proposal increment')
                    proposals+=len(saved['trace']); initial_best,_=exact_score(problem,state['best']); start_scores.append(initial_best)
                    current=[list(range(60))]+saved['permutations']; best=[list(range(60))]+saved['best_permutations']
                    score,_=exact_score(problem,current); bestscore,_=exact_score(problem,best); score_count+=1
                    need(score==saved['score'] and bestscore==saved['best_score'] and bestscore<=score and
                         bestscore<=initial_best, 'exact saved current/best score and monotonic best')
                    scores.append(bestscore)
                    if chunk==7:
                        for kind,perms,claimed in [('current',current,score),('best',best,bestscore)]:
                            f=factor(problem,perms); checked=evaluate(core,f)
                            need(checked['score']==claimed, 'independent literal factor score')
                            final_raw.append(dict(chain=chain,kind=kind,core_adjacency=core,factor=f,
                                                  claimed_score=claimed,objective_version=VERSION,target_graph=False))
                            final_checks.append(dict(phase=case['label'],chain=chain,kind=kind,**checked))
                if chunk==0:
                    starting_min=min(start_scores)
                    if case['temperature']!=1: need(starting_min==record['initial_best_reported_score'], 'starting minimum')
                raw=read(directory/f'best_{prefix}.json')
                need(raw['core_adjacency']==core and raw['objective_version']==VERSION, 'raw best domain/objective')
                checked=evaluate(core,raw['factor'])
                need(raw['claimed_score']==checked['score']==min(scores), 'raw best score')
                need(any(raw['factor']==factor(problem,[list(range(60))]+ch['best_permutations'])
                         for ch in native['chains'] if ch['best_score']==min(scores)), 'raw best belongs to saved chain')
                minima.append(checked['score']); raw_checks.append(dict(phase=case['label'],chunk=chunk,
                            raw_path=key(directory/f'best_{prefix}.json'),**checked)); previous=native['chains']
            last=directory/'checkpoint_00007.json'
            need(key(last)==record['last_checkpoint'] and digest(last)==record['last_checkpoint_sha256'], 'last checkpoint')
            need(sum(x['proposals'] for x in previous)-starting_total==record['observed_new_proposals']==131072,
                 'phase proposal count')
            need(minima[-1]==min(minima)==summary['best_score']==record['final_best_reported_score'], 'phase minimum')
            need(summary['best_raw_object']==key(directory/'best_00007.json'), 'last best pointer')
            previous_phase[case['core']]=last; save(out/(case['label']+'_final_states.json'),final_raw)
            records.append(dict(case=case,initial_best_score=starting_min,chunk_best_scores=minima,
                                final_best_score=minima[-1],resume_path=None if resume is None else key(resume),
                                phase_new_proposal_records=131072))
            print(case['label'],minima[-1],flush=True)
        need(proposals==run['completed_new_proposals']==1572864 and run['completed_chunks']==len(raw_checks)==96 and
             len(final_checks)==384 and score_count==1536, 'complete saved populations')
        need(all(r['final_best_score']>0 for r in records) and run['zero_reported'] is False, 'no saved E0')
        for label in ('current','best','rng','proposals'):
            state,old=deepcopy(example)
            if label in ('current','best'): state[label][1][0],state[label][1][1]=state[label][1][1],state[label][1][0]
            else: state[label]+=1
            try: carry(state,old)
            except ValueError as e: controls.append(dict(control='altered_carry_'+label,outcome='REJECTED',reason=str(e)))
            else: raise AssertionError(label)
        try: need(evaluate(final_raw[0]['core_adjacency'],final_raw[0]['factor'])['score']==final_raw[0]['claimed_score']+1,'score')
        except ValueError as e: controls.append(dict(control='altered_claimed_score',outcome='REJECTED',reason=str(e)))
        else: raise AssertionError('false score')
        save(out/'controls.json',dict(positive243_score=0,valid_domain_corruption_score=24,corruptions=controls))
        save(out/'saved_states.json',dict(chunk_best=raw_checks,phase_final_states=final_checks))
        for p in [Path(__file__),ROOT/'acceleration/audit_20260930_factor_permutation_trace.py',
                  ROOT/'acceleration/audit_20260930_factor_annealing_objective.py',
                  ROOT/'acceleration/audit_20260930_factor_cooling_v3.py',ROOT/'uv.lock',ROOT/'pyproject.toml']: pin(p)
        now=datetime.now(timezone.utc).isoformat()
        statement=('The frozen four-core portfolio has 96 saved chunk-best, 192 phase-final-current and 192 phase-final-best factors '
                   'in their declared permutation domains with exact recorded scores; its 64 initialized chains continue across '
                   'three phases with checked checkpoint carry, and final minima per core are 168→154→140, 170→134→132, '
                   '172→146→128 and 166→144→134; no saved state has score zero.')
        dependencies=[dict(id=i,revision=1,relation=r) for i,r in [
            ('C-FOUR-CONNECTED-IDENTITY-CORE-PORTFOLIO','uses_result'),
            ('C-FOUR-CONNECTED-CORE-ANNEALER-CALIBRATION','verification_dependency'),
            ('C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL','verification_dependency')]]
        report=dict(status='INDEPENDENT_CONNECTED_CORE_PORTFOLIO_SAVED_STATES_PASS',timestamp=now,
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,
            outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},
            claim_id='C-CONNECTED-CORE-PORTFOLIO-ANNEALER-SAVED-STATES',claim_revision=1,statement=statement,
            kind='empirical/engineering result',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
            scope='Exact saved scores, domain membership and checkpoint carry for this finite four-core portfolio only.',
            dependencies=dependencies,assumptions=['No nontrivial target automorphism is assumed.'],
            verifier='/root/state_literature_audit',method='independent_artifact_check',
            shared_components=['Frozen independent columnwise objective and separately authored bitset factor checker.',
                               'Frozen independently checked carry helper; standard-library seeded initialization.',
                               'No producer imports.'],cases=records,chunk_best_states=96,phase_final_current_states=192,
            phase_final_best_states=192,distinct_initialized_chains=64,phase_chain_endpoints=192,
            new_saved_proposal_records=proposals,checkpoint_current_scores_checked=score_count,
            checkpoint_best_scores_checked=score_count,positive_controls=2,corrupt_controls=len(controls),
            artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False,
            limitations=['Saved proposal records were counted, but individual campaign transitions and RNG progression were not replayed.',
                         'Phase populations overlap; 192 endpoints represent 64 continuing chains.',
                         'Scores are exact values of the heuristic objective, not mathematical bounds or exclusions.',
                         'Cap violations are recorded as diagnostics; no residual adjacency was constructed.',
                         'No performance guarantee, target-wide coverage, full factor or target graph is claimed.'],
            overall_search_coverage='UNKNOWN; no validated denominator.',created_at=now,updated_at=now)
        save(out/'summary.json',report)
        save(out/'claim_binding.json',{k:report[k] for k in ['claim_id','claim_revision','statement','kind','basis',
            'recommendation','review_state','scope','dependencies','assumptions','verifier','method','shared_components',
            'limitations','artifact_availability','created_at','updated_at']} | dict(evidence=[dict(path=key(out/'summary.json'),
                sha256=digest(out/'summary.json'),availability='LOCAL_ONLY')],ledger_changed=False))
        print(json.dumps(dict(status=report['status'],summary_sha256=digest(out/'summary.json'),
                              binding_sha256=digest(out/'claim_binding.json'))))
    except BaseException as e: save(out/'failure.json',dict(error=repr(e))); raise

if __name__=='__main__': main()
