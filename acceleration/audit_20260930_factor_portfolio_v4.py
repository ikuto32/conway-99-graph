"""Independent exact four-core admission, source delta and finite trajectory audit."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse
import ast
import difflib
import hashlib
import json
import platform
import subprocess
import sys
from audit_20260930_factor_permutation_trace import read_input,bind_core,audit_chain,factor,exact_score,need
from audit_20260930_factor_annealing_objective import evaluate

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v3.py'
NEW=ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v4.py'
DOMAIN=ROOT/'acceleration/results/20260930_independent_review/connected_identity_cores/summary.json'
DOMAIN_SHA='efdcacb9130bf29a28ece4c07022bdab11ab953a862f117fc55f44bd5244d2b4'
PRIOR=ROOT/'acceleration/results/20260930_independent_review/factor_resume_v3/summary.json'
PRODUCER=ROOT/'acceleration/results/20260930_factor_permutation_portfolio_calibration_v4'

def digest(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()

def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={}
    def bind(p,h=None):
        value=digest(p);need(h is None or h==value,'input hash '+key(p));bindings[key(p)]=value
    def read(p,h=None):bind(p,h);return json.loads(p.read_bytes())
    try:
        domain=read(DOMAIN,DOMAIN_SHA);need(domain['status']=='INDEPENDENT_CONNECTED_IDENTITY_CORE_PORTFOLIO_PASS','independent exact domain gate')
        prior=read(PRIOR,'2c08fb8e4fb2c67179a9ad130cfe4109f43d4dd51719f3abd1e8694070d78ab6')
        for gate in(domain,prior):
            for path,h in gate['inputs_sha256'].items():bind(ROOT/path,h)
        bind(NEW,'4e8151b67024a932b1b291957827b06cb8773e6966899ff295655648d1c97d3d');bind(NEW.with_name('theory_20260930_factor_permutation_annealer_v4_spec.md'),'6414fa3e36c85a79602f7026d4aea613ddbe9117d1ea3e363007fa7532889563')
        producer=read(PRODUCER/'summary.json','fca3a54193763ae0dd0dedec1dfda821588825b9b765184f2c2619851b4902c5')
        for path,h in{**producer['inputs_sha256'],**producer['outputs_sha256']}.items():bind(ROOT/path,h)
        cores={f'connected_{i:02d}':read(ROOT/selected['path'],selected['sha256'])for i,selected in enumerate(domain['selected'])}
        oldtree=ast.parse(OLD.read_text());newtree=ast.parse(NEW.read_text());oldf={node.name:node for node in oldtree.body if isinstance(node,ast.FunctionDef)};newf={node.name:node for node in newtree.body if isinstance(node,ast.FunctionDef)}
        need(set(newf)-set(oldf)=={'bind_portfolio'} and not(set(oldf)-set(newf)),'only portfolio gate helper added')
        changed=[name for name in oldf if ast.dump(oldf[name])!=ast.dump(newf[name])];need(set(changed)=={'core_data','run_chunks','resume_regression','main'},'only admission/orchestration functions changed')
        need(ast.dump(oldf['problem'])==ast.dump(newf['problem']),'unchanged canonical problem and JSON-list fix')
        diff=''.join(difflib.unified_diff(OLD.read_text().splitlines(True),NEW.read_text().splitlines(True),fromfile=key(OLD),tofile=key(NEW)));(out/'source_delta.patch').write_text(diff,encoding='utf-8',newline='\n')
        replay=out/'public_wrapper_replay';command=[sys.executable,'-B',str(NEW),'portfolio-calibrate','--portfolio-domain-gate',str(DOMAIN),'--portfolio-domain-gate-sha256',DOMAIN_SHA,'--out',str(replay)]
        completed=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=90);save(out/'replay_receipt.json',dict(command=command,cwd=str(ROOT),returncode=completed.returncode,stdout=completed.stdout,stderr=completed.stderr));need(completed.returncode==0,'fresh actual portfolio CLI calibration')
        fresh=read(replay/'summary.json');need(fresh['status']=='CANDIDATE_FOUR_CORE_WRAPPER_CALIBRATION_PASS','fresh producer telemetry awaiting separate checks')
        checked_proposals=0;raw_count=0;records=[];fresh_states=[]
        for directory,label in[(PRODUCER,'original_saved'),(replay,'fresh_actual_execution')]:
            for core_label,rawcore in cores.items():
                core=rawcore['core_adjacency'];checkpoints=[];whole_problem=None;whole_native=None
                for suffix,steps in [('first23',23),('resume41',41),('whole64',64)]:
                    path=directory/(core_label+'_'+suffix);summary=read(path/'summary.json')
                    for rel,h in{**summary['inputs_sha256'],**summary['outputs_sha256']}.items():bind(ROOT/rel,h)
                    problem=read_input(path/'chunk_00000.txt');bind_core(problem,core);need(problem['target']==rawcore['target_gram'] and problem['edges']==rawcore['nonmatching_edge_catalogs'],'new domain target/catalog identity')
                    cp=read(path/'checkpoint_00000.json');native=read(path/'chunk_00000.json');receipt=read(directory/(core_label+'_'+suffix+'.receipt.json'))
                    need(receipt['exit_code']==0 and 'calibration-chunk'in receipt['command'] and DOMAIN_SHA in receipt['command'],'actual separately domain-gated CLI call')
                    need((problem['steps'],problem['chains'],problem['mode'],problem['temperature'])==(steps,2,1,3.25),'frozen finite configuration')
                    need(cp['chains']==native['chains'] and cp['problem']['core_adjacency']==core and cp['problem']['target']==problem['target'] and cp['problem']['edges']==problem['edges'],'literal checkpoint domain/native state')
                    for chain,(initial,saved)in enumerate(zip(problem['states'],native['chains'])):
                        checked=audit_chain(problem,initial,saved);checked_proposals+=checked['proposals']
                        for kind in('final','best'):
                            f=checked[kind+'_factor'];score=checked['final_score'if kind=='final'else'best_score'];literal=evaluate(core,f);need(literal['score']==score,'separate raw-factor score')
                            if label=='fresh_actual_execution':fresh_states.append(dict(core=core_label,stage=suffix,chain=chain,kind=kind,core_adjacency=core,factor=f,claimed_score=score))
                    checkpoints.append(cp)
                    if suffix=='whole64':whole_problem=problem;whole_native=native
                a,b,z=checkpoints;need(a['problem']==b['problem']==z['problem'],'full JSON problem equality')
                for first,continued,whole in zip(a['chains'],b['chains'],z['chains']):
                    need(first['trace']+continued['trace']==whole['trace'],'complete split trace')
                    need({k:v for k,v in continued.items()if k!='trace'}=={k:v for k,v in whole.items()if k!='trace'},'all final chain fields')
                    need(first['proposals']==23 and continued['proposals']==64,'disk-resume cumulative counters')
                cpu=read(directory/(core_label+'_whole64_cpu.json'));read(directory/(core_label+'_whole64_cpu.receipt.json'));need(cpu['chains']==whole_native['chains'],'native CPU/GPU entire state equality')
                for chain,(initial,saved)in enumerate(zip(whole_problem['states'],whole_native['chains'])):
                    for kind,permutations,score in [('initial',initial['current'],exact_score(whole_problem,initial['current'])[0]),('final',[list(range(60))]+saved['permutations'],saved['score']),('best',[list(range(60))]+saved['best_permutations'],saved['best_score'])]:
                        raw=read(directory/f'{core_label}_chain{chain}_raw_{kind}.json');need(raw['core_adjacency']==core and raw['factor']==factor(whole_problem,permutations),'raw exported object identity');need(evaluate(core,raw['factor'])['score']==raw['claimed_score']==score,'exact exported score');raw_count+=1
                records.append(dict(population=label,core=core_label,whole_trajectory_proposals=128,split_repeated_proposals=128,CPU_GPU_equal=True,all_transition_scores_and_persisted_states_checked=True))
            for control in('wrong_target','changed_edge_pair','wrong_objective','wrong_source_hash','wrong_binary_hash'):
                bad=directory/('bad_'+control);read(directory/('bad_'+control+'_checkpoint.json'));receipt=read(directory/('bad_'+control+'.receipt.json'));failure=read(bad/'failure.json');read(bad/'manifest.json')
                need(receipt['exit_code']!=0 and not list(bad.glob('chunk_*')) and failure['error']in('resume domain/objective binding','resume exact engine binding'),'actual corrupted checkpoint rejection')
        need(checked_proposals==2048 and raw_count==48 and len(fresh_states)==48,'original/fresh finite populations')
        fixture=read(ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json');positive=evaluate(fixture['cubic_core60'],fixture['factor60x180']);need(positive['score']==0,'known243 raw score calibration')
        malformed=deepcopy(fixture['factor60x180']);malformed[20][0]=True
        try:evaluate(fixture['cubic_core60'],malformed)
        except ValueError:pass
        else:raise AssertionError('boolean factor accepted')
        badgates=[]
        for label in('wrong_status','missing_selected_core','wrong_selected_hash'):
            bad=deepcopy(domain)
            if label=='wrong_status':bad['status']='PENDING'
            elif label=='missing_selected_core':del bad['inputs_sha256'][domain['selected'][0]['path']]
            else:bad['inputs_sha256'][domain['selected'][0]['path']]='0'*64
            path=out/(label+'_corrupt_gate.json');save(path,bad);badgates.append((label,path,digest(path)))
        negative=[]
        configurations=[('missing_domain_gate',None,None,'calibration-chunk'),('wrong_domain_hash',DOMAIN,'0'*64,'calibration-chunk'),*[(label,path,h,'calibration-chunk')for label,path,h in badgates],('old_wrapper_research_gate',DOMAIN,DOMAIN_SHA,'run')]
        for label,path,h,mode in configurations:
            dest=out/('negative_'+label);cmd=[sys.executable,'-B',str(NEW),mode,'--out',str(dest),'--core','connected_00','--seed','20260930','--chains','2','--chunks','1','--steps','23','--seconds','30','--temperature','3.25']
            if path:cmd+=['--portfolio-domain-gate',str(path),'--portfolio-domain-gate-sha256',h]
            if mode=='run':cmd+=['--independent-gate',str(PRIOR),'--independent-gate-sha256','2c08fb8e4fb2c67179a9ad130cfe4109f43d4dd51719f3abd1e8694070d78ab6']
            result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=20);save(out/('negative_'+label+'.receipt.json'),dict(command=cmd,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr));need(result.returncode!=0 and not list(dest.glob('chunk_*')),'negative gate rejected before native input');negative.append(label)
        save(out/'raw_fresh_states.json',fresh_states)
        for p in[Path(__file__),ROOT/'acceleration/audit_20260930_factor_permutation_trace.py',ROOT/'acceleration/audit_20260930_factor_annealing_objective.py',ROOT/'docs/AUDIT_20260930_FACTOR_PORTFOLIO_V4.md']:bind(p)
        now=datetime.now(timezone.utc).isoformat();report=dict(status='INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,outputs_sha256={key(p):digest(p)for p in out.rglob('*')if p.is_file()},claim_id='C-FOUR-CONNECTED-CORE-ANNEALER-CALIBRATION',claim_revision=1,
          statement='For the four exact connected P=I portfolio cores, the frozen v4 wrapper admits only the hash-bound domains and passes the recorded original and fresh finite CPU/GPU/public-resume controls, with all2048 GPU proposal occurrences and48 exported raw objects matching independently computed exact scores and states.',kind='empirical/engineering result',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='Four frozen core IDs only; native algorithm unchanged, with independent exact domains and finite T3.25 two-chain23+41/64 controls.',dependencies=[dict(id=name,revision=1,relation='verification_dependency')for name in('C-FOUR-CONNECTED-IDENTITY-CORE-PORTFOLIO','C-FACTOR-PERMUTATION-PUBLIC-JSON-RESUME-CALIBRATION','C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL')],verifier='/root/state_literature_audit independent raw-domain, source and exact-trajectory review',method='independent_artifact_check',shared_components=['Unchanged independently checked native engine and own frozen independent trace/raw-object helpers.','Actual public CLI invoked as a black-box producer; independent expected values import no producer scorer.'],source_changed_functions=changed,unchanged_algorithm_helpers=len(oldf)-len(changed),records=records,original_GPU_control_proposals=1024,fresh_GPU_control_proposals=1024,CPU_repeats_each_execution=512,raw_exported_objects_checked=48,raw_fresh_stage_end_objects_preserved=48,corrupted_resume_controls_each_execution=5,independent_gate_controls=negative,positive243_raw_score=0,malformed_raw_control_rejected=True,
          assumptions=['No nontrivial target automorphism is assumed.','P=I and the four selected cores are deliberate domain restrictions.'],limitations=['No portfolio campaign launched by this reviewer.','2048 counts original and fresh proposal occurrences; it is not a count of distinct factors or independent random trajectories.','Finite floating acceptance parity only, no universal trajectory or performance guarantee.','Integer score zero would be an abstract Gram factor; outside caps and residual D need separate exact checking.','Raw243 is a non-target positive control.'],artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False,created_at=now,updated_at=now)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise

if __name__=='__main__':main()
