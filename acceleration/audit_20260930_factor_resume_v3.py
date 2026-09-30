"""Independent v3 source/actual Python disk-resume regression audit."""
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
from audit_20260930_factor_permutation_trace import read_input,bind_core,audit_chain,need
from audit_20260930_factor_annealing_objective import evaluate

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v2.py'
NEW=ROOT/'acceleration/theory_20260930_factor_permutation_annealer_v3.py'
PRIOR=ROOT/'acceleration/results/20260930_independent_review/factor_permutation_annealer_bound/summary.json'
PRODUCER=ROOT/'acceleration/results/20260930_factor_permutation_resume_calibration_v3'
FAILED=ROOT/'acceleration/results/20260930_factor_annealer_cooling'

def digest(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()

def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={}
    def bind(p,sha=None):
        h=digest(p);need(sha is None or sha==h,'input hash '+key(p));bindings[key(p)]=h;return p
    def read(p,sha=None):return json.loads(bind(p,sha).read_bytes())
    try:
        prior=read(PRIOR,'70c54735a3331f4bc9dff3ace2f5d1dd4bae49ec051f415a262538f9385b20b9')
        for path,h in prior['inputs_sha256'].items():bind(ROOT/path,h)
        pilot=read(ROOT/'acceleration/results/20260930_independent_review/factor_annealer_pilot/summary.json','97858230f5e777d601554e51184f0cb3b57ce6d39ed022a3850005b49c27fdd5')
        for path,h in pilot['inputs_sha256'].items():bind(ROOT/path,h)
        bind(NEW,'8f2a85f5a87d1c6a3a37fdb104628c126c67c4ba6ace846b7c9f3b3aba0525b3')
        bind(NEW.with_name('theory_20260930_factor_permutation_annealer_v3_spec.md'),'2e342b7be1650385407c2c9811ee51eb16ac6bcc84fcb1a0657386bdb1704c04')
        producer=read(PRODUCER/'summary.json','29a54c2698d1c9de55ef0e970c7a6def19c3a2b20eb769d4d6dc84cf1743da4c')
        for path,h in {**producer['inputs_sha256'],**producer['outputs_sha256']}.items():bind(ROOT/path,h)
        oldtree=ast.parse(OLD.read_text());newtree=ast.parse(NEW.read_text());oldf={n.name:n for n in oldtree.body if isinstance(n,ast.FunctionDef)};newf={n.name:n for n in newtree.body if isinstance(n,ast.FunctionDef)}
        need(set(newf)-set(oldf)=={'resume_regression'} and not(set(oldf)-set(newf)),'only regression helper added')
        changed=[n for n in oldf if ast.dump(oldf[n])!=ast.dump(newf[n])]
        need(set(changed)=={'problem','run_chunks','main'},'unchanged algorithm/helper functions')
        normalized=deepcopy(newf['problem'])
        class UndoList(ast.NodeTransformer):
            def visit_Call(self,node):
                if isinstance(node.func,ast.Name) and node.func.id=='list' and len(node.args)==1 and isinstance(node.args[0],ast.Name) and node.args[0].id=='pair':return node.args[0]
                return self.generic_visit(node)
        normalized=UndoList().visit(normalized);need(ast.dump(normalized)==ast.dump(oldf['problem']),'sole domain representation delta list(pair)')
        diff=''.join(difflib.unified_diff(OLD.read_text().splitlines(True),NEW.read_text().splitlines(True),fromfile=key(OLD),tofile=key(NEW)))
        (out/'source_delta.patch').write_text(diff,encoding='utf-8',newline='\n')
        failure=read(FAILED/'summary.json','0a82e3c77809f7001afc37a701d2a479fe015fe365ebcbf8ec143f53342fb13a')
        need((failure['attempted_stages'],failure['completed_stages'],failure['errors'],failure['skipped_stages'],failure['completed_new_proposals'])==(2,0,2,2,0),'failed campaign stage accounting')
        applicability=[]
        for core in('shift6','six_prism'):
            fd=FAILED/(core+'_T0_25');err=read(fd/'failure.json');need(err['error']=='resume domain/objective binding' and sorted(p.name for p in fd.iterdir())==['failure.json','manifest.json'],'v2 failed before native input')
            cp=read(ROOT/f'acceleration/results/20260930_factor_annealer_pilot/{core}_T1/checkpoint_00007.json');saved=cp['problem'];live=deepcopy(saved);live['edges']=[[tuple(pair)for pair in cell]for cell in saved['edges']]
            need(live!=saved and json.loads(json.dumps(live))==saved,'exact tuple/list boundary defect')
            applicability.append(dict(core=core,type_mismatches=sum(len(cell)for cell in live['edges']),domain_values_unchanged=True,observed_new_native_inputs=0))
        # Execute the actual wrapper; expected scores and transitions are checked below by separate code.
        replay=out/'public_wrapper_replay';command=[sys.executable,'-B',str(NEW),'resume-calibrate','--out',str(replay)]
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=60)
        save(out/'replay_receipt.json',dict(command=command,cwd=str(ROOT),returncode=result.returncode,stdout=result.stdout,stderr=result.stderr));need(result.returncode==0,'actual public wrapper calibration execution')
        fresh=read(replay/'summary.json');need(fresh['status']=='CANDIDATE_PUBLIC_JSON_RESUME_REGRESSION_PASS','fresh producer result pending separate checks')
        records=[];proposals=0;raws=[]
        for directory,label in[(PRODUCER,'producer_saved'),(replay,'independent_fresh_execution')]:
            for core in('shift6','six_prism'):
                checkpoints=[]
                for suffix,steps in [('first23',23),('resume41',41),('whole64',64)]:
                    path=directory/(core+'_'+suffix);summary=read(path/'summary.json')
                    for rel,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():bind(ROOT/rel,h)
                    problem=read_input(path/'chunk_00000.txt');cp=read(path/'checkpoint_00000.json');native=read(path/'chunk_00000.json');receipt=read(directory/(core+'_'+suffix+'.receipt.json'))
                    need(receipt['exit_code']==0 and 'calibration-chunk'in receipt['command'],'actual public CLI process')
                    bind_core(problem,cp['problem']['core_adjacency']);need(problem['steps']==steps and problem['chains']==2 and problem['temperature']==3.25,'fixed finite configuration')
                    need(cp['chains']==native['chains'] and cp['problem']['edges']==problem['edges'] and cp['objective_version']=='TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1','checkpoint/native/domain binding')
                    if label=='independent_fresh_execution':
                        for chain,(state,saved)in enumerate(zip(problem['states'],native['chains'])):
                            checked=audit_chain(problem,state,saved);proposals+=checked['proposals']
                            for kind in('final','best'):
                                f=checked[kind+'_factor'];score=checked['final_score'if kind=='final'else'best_score'];check=evaluate(cp['problem']['core_adjacency'],f);need(check['score']==score,'independent literal raw-object score')
                                raws.append(dict(core=core,stage=suffix,chain=chain,kind=kind,core_adjacency=cp['problem']['core_adjacency'],factor=f,claimed_score=score))
                    checkpoints.append(cp)
                a,b,z=checkpoints
                need(a['problem']==b['problem']==z['problem'],'saved JSON domain exact equality')
                for first,continued,whole in zip(a['chains'],b['chains'],z['chains']):
                    need(first['trace']+continued['trace']==whole['trace'],'all split/whole trace rows')
                    need({k:v for k,v in continued.items()if k!='trace'}=={k:v for k,v in whole.items()if k!='trace'},'all final persisted fields')
                    need(first['proposals']==23 and continued['proposals']==64,'proposal counter continuation')
                oldcp=read(ROOT/f'acceleration/results/20260930_factor_annealer_pilot/{core}_T1/checkpoint_00007.json')
                need(oldcp['problem']==a['problem'] and oldcp['objective_version']==a['objective_version'] and oldcp['source_sha256']==a['source_sha256'] and oldcp['binary_sha256']==a['binary_sha256'],'old16-chain checkpoint shares corrected exact domain and engine')
                records.append(dict(population=label,core=core,chains=2,split=[23,41],whole=64,all_persisted_fields_and_traces_equal=True))
            for control in('wrong_target','changed_edge_pair','wrong_objective','wrong_source_hash','wrong_binary_hash'):
                path=directory/('bad_'+control);read(directory/('bad_'+control+'_checkpoint.json'));receipt=read(directory/('bad_'+control+'.receipt.json'));read(path/'manifest.json');bad=read(path/'failure.json')
                need(receipt['exit_code']!=0 and not list(path.glob('chunk_*')) and bad['error']in('resume domain/objective binding','resume exact engine binding'),'corrupted actual resume rejected')
        need(proposals==512,'fresh independently replayed control proposal count')
        # Independent negative tests hit the public calibration resource boundary.
        rejected=[]
        for label,extra in [('too_many_steps',['--steps','65']),('missing_resume',['--steps','41']),('research_without_gate',[])]:
            dest=out/('guard_'+label);cmd=[sys.executable,'-B',str(NEW),'run'if label=='research_without_gate'else'calibration-chunk','--out',str(dest),'--core','shift6','--seed','20260930','--chains','2','--chunks','1','--steps','23','--seconds','30','--temperature','3.25',*extra]
            r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=20);save(out/('guard_'+label+'.receipt.json'),dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));need(r.returncode!=0 and not list(dest.glob('chunk_*')),'public gate/resource negative control');rejected.append(label)
        save(out/'raw_control_states.json',raws)
        save(out/'v2_applicability_addendum.json',dict(status='INDEPENDENT_V2_PUBLIC_RESUME_LIMITATION_CHECKED',prior_gate=key(PRIOR),prior_gate_sha256=digest(PRIOR),failed_batch=key(FAILED/'summary.json'),failed_batch_sha256=digest(FAILED/'summary.json'),cases=applicability,exact_effect='V2 actual public run --resume rejects its JSON edge lists against newly constructed tuple catalogs before any native call. Prior native finite delta/acceptance/calibration and saved-state checks remain valid within their recorded scope. Public Python disk-resume usability was not covered and must not be inferred from that gate.',original_evidence_changed=False,target_resolution=False))
        bind(Path(__file__));bind(ROOT/'acceleration/audit_20260930_factor_permutation_trace.py');bind(ROOT/'acceleration/audit_20260930_factor_annealing_objective.py');bind(ROOT/'docs/AUDIT_20260930_FACTOR_RESUME_V3.md')
        report=dict(status='INDEPENDENT_FACTOR_PERMUTATION_ANNEALER_CALIBRATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,outputs_sha256={key(p):digest(p)for p in out.rglob('*')if p.is_file()},
          claim_id='C-FACTOR-PERMUTATION-PUBLIC-JSON-RESUME-CALIBRATION',claim_revision=1,verifier='/root/state_literature_audit independent source and trace review',scope='V3 Python JSON domain representation fix plus actual bounded public disk-resume calibration; unchanged v2 native kernel retains its existing finite calibration scope.',
          actual_fresh_wrapper_native_calls=6,actual_fresh_control_proposals=512,independently_recomputed_raw_final_best_objects=len(raws),saved_and_fresh_regressions=records,corrupted_resume_controls_fresh=5,additional_public_gate_controls=rejected,unchanged_function_count=len(oldf)-len(changed),changed_functions=changed,prior_calibration_gate=dict(path=key(PRIOR),sha256=digest(PRIOR)),
          limitations=['No cooling research retry launched by this audit.','Fresh actual CLI execution is repeated producer orchestration; expected transition scores, state continuation and literal objects are checked independently without producer imports.','The public calibration mode exercises the same run_chunks body after its separate strict calibration authorization branch. This is not a fabricated research gate.','Only the two finite two-chain23+41/64 controls establish full floating acceptance parity here; no universal trajectory guarantee.','The old16-chain checkpoints were checked for exact domain/objective/engine identity; their resumed research outcomes require subsequent saved-state review.'],target_resolution=False)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise

if __name__=='__main__':main()
