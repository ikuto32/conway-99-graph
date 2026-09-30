"""Fresh native54 object wrapper over frozen independent reconstruction; no producer imports."""
from collections import defaultdict, Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse, ast, gzip, json, platform, subprocess, sys, time, traceback
import audit_20260930_hadamard_fiftyfour_profiles as checked

ROOT=checked.ROOT;B=checked.B;codec=checked.codec;shared=checked.shared
need=codec.need;sha=codec.sha;key=codec.key;read=codec.read;save=codec.save;same=codec.same
GATE=B/'20260930_independent_review/hadamard_fiftyfour_profile_cnfs/summary.json'
GATE_SHA='4fa50584776c9862e4e4c0286567b212b9a436c13a6cf0ebf0cd0b0ad751a6e5'
PREP=B/'20260930_hadamard_six_profile_batch_preparation/summary.json'
RUNNER=ROOT/'acceleration/native_20260930_hadamard_six_profile_batch.py'
SPEC=ROOT/'acceleration/native_20260930_hadamard_six_profile_batch_spec.md'
PINS={GATE:GATE_SHA,PREP:'2922e9d7929f1b3630a225ef18ad907870791f07f989aceb1fa338a79e325ad1',
 Path(checked.__file__):'522364d9bc3948dc9661099cd9a09dbd48df4f3f6f442135eca9f24e3761af6a',
 RUNNER:'cf1ca91b527a7422668085fc1acf75dae259f7b460a2f6eea95ee5bd5e2bbd0b',
 SPEC:'5959da4066ae15acdd2820029bce740f3e7287616f505b3c7e5f2d76bbfb7d13',
 ROOT/'acceleration/native_20260930_unrestricted_full99.py':'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',
 ROOT/'acceleration/native_20260930_proof_location.py':'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
 ROOT/'acceleration/theory_20260930_hadamard_six_profile_cnf.py':'cac3d732f9045b32b77648acfb246f3a6c842724ec232bd10321806bb079ca0a',
 ROOT/'acceleration/theory_20260930_hadamard_six_profile_cnf_spec.md':'0a55b28ed0e4869764aafedecb48471c60e8ad19b7eb79bceeca5838b915b520',
 ROOT/'acceleration/theory_20260930_hadamard_four_profile_cnf.py':'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',
 ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py':'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016'}


def static_local_closure(path):
    """Resolve local plain imports without executing a native/producer module."""
    seen=set();pending=[path]
    while pending:
        p=pending.pop().resolve()
        if p in seen:continue
        seen.add(p);tree=ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
        for node in ast.walk(tree):
            names=[x.name for x in node.names]if isinstance(node,ast.Import)else [node.module]if isinstance(node,ast.ImportFrom)and node.module else []
            for name in names:
                q=ROOT/'acceleration'/((name.split('.')[0])+'.py')
                if q.is_file():pending.append(q)
    return seen


def selected_local_control(model,scope,last=False):
    """Positive decode of every local domain; deliberately no full-Gram claim."""
    F=[[0]*60 for _ in range(36)];ids=[]
    for domain in model['domains']:
        option=domain['choices'][-1 if last else 0];ids.append(option['selector'])
        for d,word in zip(domain['columns'],option['colour_words']):
            for a,f in zip(domain['support'],word):F[12*f+a][d]=1
        actual=[[sum(F[12*f+a][d]for d in domain['columns'])for f in range(3)]for a in domain['support']]
        need(actual==domain['fixed_counts'],'positive local decoded profile counts')
        need(all(sum(F[r][d]*F[r][e]for r in range(36))<=2 for d in domain['columns']for e in domain['columns']if d<e),'positive local caps')
    need(all(sum(F[12*f+a][d]for f in range(3))==scope['L12x60'][a][d]for a in range(12)for d in range(60)),'all720 aggregate entries')
    need(all(sum(F[r])==10 for r in range(36)),'all36 literal profile-implied row margins')
    return dict(selected=ids,factor=F,positive_scope='Local domain decode, counts, aggregate and margins only; not full Gram or research SAT.')


def extended_controls(out):
    common=checked.calibrate();rejected=[];sizes=[]
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):rejected.append(name);return
        raise ValueError('accepted corruption '+name)
    for n,m in((10048,174766),(10156,177412)):
        literals=[i if i%2 else -i for i in range(1,n+1)];values=codec.assignment(literals,n)
        native='c SYNTHETIC CODEC ONLY; NOT RESEARCH SAT\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,literals[i:i+113]))for i in range(0,n,113))+' 0\n'
        need(codec.native(native,n)==values,'full native/JSON positive for each dimension')
        clauses=[[literals[i%n]]for i in range(m)];codec.all_clauses(clauses,values)
        (out/f'synthetic_{n}.stdout.log').write_text(native,encoding='ascii',newline='\n')
        save(out/f'synthetic_{n}.assignment.json',dict(assignment=literals,research_SAT=False))
        (out/f'synthetic_{n}.cnf').write_bytes(codec.cnf_bytes(clauses,n))
        for label,bad in [('missing_status',native.replace('s SATISFIABLE\n','')),('wrong_status',native.replace('SATISFIABLE','UNSATISFIABLE')),('duplicate_status',native+'s SATISFIABLE\n'),('unterminated',native.replace(' 0\n','\n')),('duplicate_ID',native.replace('v 1 -2','v 1 1')),('postzero',native+'v 1\n'),('out_of_range',native.replace('v 1 -2',f'v {n+1} -2'))]:
            reject(f'{label}_{n}',lambda bad=bad,n=n:codec.native(bad,n))
        reject(f'Boolean_JSON_{n}',lambda literals=literals,n=n:codec.assignment([True,*literals[1:]],n))
        reject(f'wrong_false_clause_{n}',lambda clauses=clauses,values=values:codec.all_clauses([*clauses[:-1],[-clauses[-1][0]]],values))
        altered=codec.assignment([-literals[0],*literals[1:]],n)
        reject(f'native_JSON_disagreement_{n}',lambda altered=altered,values=values:need(altered==values,'native/JSON literal identity'))
        sizes.append(dict(variables=n,clauses=m,scope='synthetic parser and clause fixture, not a research model'))
    return dict(shared_fresh_controls=common,additional_rejected_corruptions=rejected,fullsize_synthetic_positives=sizes)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['calibrate','sat']);ap.add_argument('--profile-id');ap.add_argument('--encoding-gate',type=Path,required=True);ap.add_argument('--encoding-gate-sha256',required=True);ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();actual=pins.get(key(p))
        if actual is None:actual=sha(p);pins[key(p)]=actual
        need(h is None or h==actual,'exact input hash '+key(p))
    try:
        need(args.encoding_gate.resolve()==GATE.resolve()and args.encoding_gate_sha256==GATE_SHA,'exact approved aggregate encoding gate')
        for p,h in PINS.items():pin(p,h)
        gate=read(GATE);need(gate['status']=='INDEPENDENT_HADAMARD_FIFTYFOUR_PROFILE_ENCODING_PASS'and gate['checked_formulas']==54,'approved complete54 scope')
        for p,h in gate['inputs_sha256'].items():pin(ROOT/p,h)
        for p,h in gate['outputs_sha256'].items():pin(ROOT/p,h)
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_FIFTYFOUR_PROFILE_OBJECT.md')
        prep=read(PREP)
        for p,h in prep['inputs_sha256'].items():pin(ROOT/p,h)
        native_closure=static_local_closure(RUNNER)|{SPEC,ROOT/'acceleration/theory_20260930_hadamard_six_profile_cnf_spec.md',ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py'}
        checker_closure=static_local_closure(Path(__file__))
        for p in native_closure|checker_closure:pin(p)
        need(set(prep['static_local_import_closure'])<=set(map(key,native_closure)),'preparation closure plus explicit producer spec')
        need(all(not p.name.startswith(('theory_','native_'))for p in checker_closure),'no discovery/native checker imports')
        batch=read(checked.BATCH);selection=read(checked.SELECTION);ids=selection['remaining_profile_ids'];need(ids==batch['selection']==[r['profile_id']for r in batch['records']]and len(set(ids))==54,'literal selected54 IDs')
        for rec in batch['records']:
            for field in('cnf','model','scope'):need(gate['inputs_sha256'][rec[field+'_path']]==rec[field+'_sha256']==pins[rec[field+'_path']],'exact bound formula identity')
            profile_path=(ROOT/rec['scope_path']).parent/'selected_profile.json';profile=read(profile_path);need(gate['inputs_sha256'][key(profile_path)]==sha(profile_path),'direct selected profile pin')
            for ref in profile['local_domains']:need(gate['inputs_sha256'][ref['path']]==ref['sha256']==pins[ref['path']],'full initial domain direct pin')
        if args.mode=='sat':need(args.profile_id in ids and args.assignment and args.native_output,'explicit allowed profile and complete native files')
        else:need(args.profile_id is None and not args.assignment and not args.native_output and not args.decoded,'aggregate calibration has no research object')
        words,triples,balanced=checked.prior.catalogue();index=defaultdict(list)
        for i,t in enumerate(triples):index[tuple(sum(words[w][p]==f for w in t)for p in range(6)for f in range(3))].append(i)
        catalog=(words,triples,balanced,index);raw=read(checked.RAW);records=[];local_positives=[];rejections=[]
        common=extended_controls(out)if args.mode=='calibrate'else None
        selected=[r for r in batch['records']if args.mode=='calibrate'or r['profile_id']==args.profile_id]
        for rec in selected:
            d=(ROOT/rec['scope_path']).parent;profile=read(d/'selected_profile.json')
            scope,model,clauses=checked.derive(raw,profile,catalog,rec['scope_sha256'],sha(d/'selected_profile.json'))
            need(same(scope,read(d/'scope.json'))and same(model,read(d/'model.json')),'complete independent selected model/scope')
            need(codec.cnf_bytes(clauses,model['variables'])==(d/'instance.cnf').read_bytes(),'all actual clause bytes, exact per-profile dimensions')
            if args.mode=='calibrate':
                positive_first=selected_local_control(model,scope);positive_last=selected_local_control(model,scope,True)
                local_positives.append(dict(profile_id=rec['profile_id'],first=positive_first,last=positive_last))
                # Real per-profile prefix/threshold auxiliary values are set from
                # one concrete local selection. This is only a negative whole-CNF
                # fixture; the complete prescribed Gram has not been satisfied.
                chosen=set(positive_first['selected']);values={i:False for i in range(1,model['variables']+1)}
                for i in chosen:values[i]=True
                for row in model['exact_one_prefix_rows']:
                    for i,v in enumerate(row['prefixes']):values[v]=any(values[x]for x in row['selectors'][:i+1])
                for cell in model['pair_cell_counts']:
                    for group in cell['group_contributions']:
                        for channel in group['channels']:values[channel['variable']]=any(values[x]for x in channel['selectors'])
                need(len(values)==model['variables'],'complete per-profile auxiliary fixture')
                try:checked.object_check(values,model,scope,clauses,rec['model_sha256'],rec['scope_sha256'])
                except ValueError as error:rejections.append(dict(profile_id=rec['profile_id'],reason=str(error),scope='Concrete first-option local assignment rejected as full factor.'))
                else:raise ValueError('unexpected genuine research factor in calibration; stop for independent review')
            else:
                pin(args.assignment);pin(args.native_output);values=codec.assignment(read(args.assignment)['assignment'],model['variables'])
                need(values==codec.native(args.native_output.read_text(encoding='utf-8'),model['variables']),'every native and JSON signed literal')
                decoded=None
                if args.decoded:pin(args.decoded);decoded=read(args.decoded)
                obj=checked.object_check(values,model,scope,clauses,rec['model_sha256'],rec['scope_sha256'],decoded)
                save(out/'independent_Gram_factor.json',obj)
            records.append(dict(profile_id=rec['profile_id'],variables=model['variables'],clauses=model['clauses'],model_sha256=rec['model_sha256'],scope_sha256=rec['scope_sha256'],cnf_sha256=rec['cnf_sha256'],complete_raw_reconstruction=True))
            print(json.dumps(dict(checked=len(records),total=len(selected),profile_id=rec['profile_id'])),flush=True)
        save(out/'records.json',records)
        if args.mode=='calibrate':
            save(out/'local_decode_controls.json',local_positives);save(out/'actual_CNF_negative_controls.json',rejections);save(out/'controls.json',common)
            # Exercise the actual frozen argparse interface without executing a solver.
            help_result=subprocess.run([sys.executable,'-B',str(Path(__file__)),'sat','--help'],cwd=ROOT,capture_output=True,text=True)
            need(help_result.returncode==0 and '--profile-id' in help_result.stdout and '--native-output' in help_result.stdout and '--decoded' in help_result.stdout,'actual SAT CLI ABI')
            (out/'sat_help.stdout.log').write_text(help_result.stdout,encoding='utf-8');(out/'sat_help.stderr.log').write_text(help_result.stderr,encoding='utf-8')
        timestamp=datetime.now(timezone.utc).isoformat();status='INDEPENDENT_HADAMARD_FIFTYFOUR_PROFILE_OBJECT_CALIBRATION_PASS'if args.mode=='calibrate'else 'INDEPENDENT_HADAMARD_SIX_PROFILE_SAT_OBJECT_PASS'
        report=dict(status=status,timestamp=timestamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},selected_profiles=ids,checked_profiles=[r['profile_id']for r in records],checked_formulas=len(records),clauses_checked=sum(r['clauses']for r in records),native_source_closure=sorted(map(key,native_closure)),checker_source_closure=sorted(map(key,checker_closure)),controls=common,local_decode_positive_controls=len(local_positives)*2,actual_CNF_negative_controls=len(rejections),source_sharing=['Frozen independently authored fiftyfour-profile reconstruction/object checker and its explicitly pinned independent catalogue/core/Gram/codec helpers.','Native and producer source bytes are authenticated and statically inspected; never imported.'],sat_cli='sat --profile-id ID --encoding-gate PATH --encoding-gate-sha256 SHA --assignment JSON --native-output LOG [--decoded JSON] --out NEWDIR',scope='Exact selected literal-profile full Gram and within-triplicate caps. Cross-group column caps/mixed caps are independently computed diagnostics; residual D absent.',limitations=['No genuine54-profile SAT object used for calibration; genuine243 and synthetic/local-only positives are explicitly distinct.','This calibration does not establish a research factor or approve a native outcome.'],native_calls=0,solver_calls=0,target_resolution=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',report);print(json.dumps(dict(status=status,summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))))
    except Exception as e:
        save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise


if __name__=='__main__':main()
