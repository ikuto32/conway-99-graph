"""Independent native count-profile object checker; no solver/producer imports."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,platform,subprocess,sys,time,traceback
import audit_20260930_hadamard_count_master_cnf_v2 as independent
ROOT=independent.ROOT;D=independent.D;B=independent.B
need=independent.need;read=independent.read;sha=independent.sha;save=independent.save
NATIVE_PINS={'acceleration/native_20260930_hadamard_count_master.py':'4e9f82faf455da04954bfd8812ff066e72bcf7e0e863cba656fb352ad293dcc3','acceleration/native_20260930_hadamard_count_master_spec.md':'bdc7698981fa42d9b4f0adfc9088f1e57d4e2b65c6f9c0a27cbe973b1c3a460d','acceleration/native_20260930_unrestricted_full99.py':'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22','acceleration/native_20260930_proof_location.py':'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854','acceleration/theory_20260930_hadamard_count_master_cnf.py':'470cbec724f891264593dc5b438648dc2995b3f860f89decf4b6ac8bc1c4f28b','acceleration/theory_20260930_hadamard_count_master_cnf_spec.md':'67b5e379c1b5e6d1dcb6e6aff0c022821a56169a55e1656abf3d353aac5b5d19'}
GATE=B+'independent_review/hadamard_count_master_cnf_v2/summary.json'
GATE_SHA='80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888'
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def native_model(path,n):
    status=[];literals=[];v_seen=False;terminated=False
    with Path(path).open('r',encoding='ascii')as stream:
        for line in stream:
            words=line.split()
            if not words or words[0]=='c':continue
            if words[0]=='s':need(words==['s','SATISFIABLE'],'native SAT status only');status.append(words[1]);continue
            need(words[0]=='v'and len(words)>1,'native output grammar');v_seen=True
            for s in words[1:]:
                need(not terminated,'no native literals after final zero')
                if s=='0':terminated=True;continue
                need(s not in ['+0','-0']and s.lstrip('-').isdigit(),'strict native integer token');literals.append(int(s))
    need(status==['SATISFIABLE']and v_seen and terminated,'one native SAT status and terminated model')
    return independent.signed_values(literals,n)
def cnf_object(path,values,expected_clauses):
    n=len(values)-1;count=0
    with Path(path).open('r',encoding='ascii',newline='')as stream:
        head=stream.readline();need(head==f'p cnf {n} {expected_clauses}\n','strict actual CNF header')
        for line in stream:
            tokens=line.split();need(tokens and tokens[-1]=='0','terminated actual clause');clause=[int(x)for x in tokens[:-1]]
            need(all(x and abs(x)<=n for x in clause),'actual clause ID range');need(independent.clause_pass(clause,values),f'unsatisfied actual clause {count+1}');count+=1
    need(count==expected_clauses,'complete actual clause population');return count
def compare_decoded(actual,expected,model_hash,clauses):
    for k,v in {**expected,'model_sha256':model_hash,'actual_cnf_clauses_checked':clauses}.items():
        need(k in actual and json.dumps(actual[k],sort_keys=True,separators=(',',':'))==json.dumps(v,sort_keys=True,separators=(',',':')),'decoded field '+k)
def authenticate(args):
    gatepath=args.encoding_gate.resolve();need(key(gatepath)==GATE and args.encoding_gate_sha256==GATE_SHA and sha(gatepath)==GATE_SHA,'exact independent encoding gate')
    gate=json.loads(gatepath.read_bytes());need(gate['status']=='INDEPENDENT_HADAMARD_COUNT_MASTER_ENCODING_PASS','encoding gate status');pins={key(gatepath):GATE_SHA}
    for p,h in gate['inputs_sha256'].items():need(sha(ROOT/p)==h,'encoding premise bytes '+p);pins[p]=h
    for p,h in NATIVE_PINS.items():need(sha(ROOT/p)==h,'native source closure '+p);pins[p]=h
    for p in [Path(__file__),Path(independent.__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_COUNT_MASTER_OBJECT.md']:
        pins[key(p)]=sha(p)
    return pins
def evaluate(model,variant,assignment,native,decoded=None):
    need(variant in ('baseline','at_least_seven'),'literal variant');v=model['variants'][variant]
    values=independent.signed_values(json.loads(Path(assignment).read_bytes())['assignment'],v['variables']);raw=native_model(native,v['variables']);need(values==raw,'complete native/JSON assignment equality')
    checked=cnf_object(ROOT/v['cnf_path'],values,v['clauses']);result=independent.literal_decode(model,values,variant)
    if decoded is not None:compare_decoded(json.loads(Path(decoded).read_bytes()),result,sha(ROOT/(D+'model.json')),checked)
    return result,checked
def write_native(path,assignment):
    with Path(path).open('x',encoding='ascii',newline='\n')as f:
        f.write('c Independent synthetic native codec fixture, not a solver execution.\ns SATISFIABLE\n')
        for start in range(0,len(assignment),100):f.write('v '+' '.join(map(str,assignment[start:start+100]))+(' 0'if start+100>=len(assignment)else'')+'\n')
def calibration(args,out,pins):
    model=read(D+'model.json');rejected=[];positives=[]
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):rejected.append(name);return
        raise ValueError('corruption unexpectedly accepted '+name)
    for path in sorted((ROOT/D).glob('*_assignment.json')):
        a=json.loads(path.read_bytes())['assignment'];native=out/(path.stem+'_synthetic_native.log');write_native(native,a)
        decoded=path.with_name(path.name.replace('_assignment.json','_counts.json'));result,n=evaluate(model,'baseline',path,native,decoded);positives.append(dict(assignment=key(path),assignment_sha256=sha(path),native_codec_fixture=key(native),native_sha256=sha(native),clauses_checked=n,exception_count=result['exception_count'],full_factor=False));pins[key(path)]=sha(path);pins[key(decoded)]=sha(decoded)
        values=independent.signed_values(a,155750);aug=values+[False]*189
        for row in model['extension']['states']:aug[row['id']]=sum(aug[x]for x in model['extension']['input_variables'][:row['i']])>=row['j']
        reject(path.stem+'_augmented_final_bound',lambda:cnf_object(ROOT/(D+'at_least_seven.cnf'),aug,705833))
        for label,variable in [('coordinate',model['coordinate_domains'][0]['selectors'][0]),('group',model['group_domains'][0]['selectors'][0]),('channel',model['count_channels'][0]['variables'][0]),('prefix',model['one_hot_domains'][0]['prefix_variables'][0])]:
            bad=values.copy();bad[variable]=not bad[variable];reject(path.stem+'_flipped_'+label,lambda:cnf_object(ROOT/(D+'baseline.cnf'),bad,704454))
        changed={**result,'exception_count':result['exception_count']+1};reject(path.stem+'_decoded_exception_count',lambda:compare_decoded(changed,result,sha(ROOT/(D+'model.json')),n))
        wrong=json.loads(decoded.read_bytes());wrong['coordinate_group_fibre_counts'][0][0][0]=4;reject(path.stem+'_decoded_counts',lambda:compare_decoded(wrong,result,sha(ROOT/(D+'model.json')),n))
    need(len(positives)==2,'two authentic baseline count positives')
    # Full augmented-size native codec/JSON positive does not claim CNF satisfaction.
    synthetic=[i if i%2 else-i for i in range(1,155940)];path=out/'fullsize_augmented_codec.log';write_native(path,synthetic);need(native_model(path,155939)==independent.signed_values(synthetic,155939),'full augmented native codec');save(out/'fullsize_augmented_codec.json',dict(assignment=synthetic,synthetic_codec_only=True,is_research_SAT=False))
    for name,a in [('missing',synthetic[:-1]),('duplicate',synthetic[:-1]+[synthetic[0]]),('range',synthetic[:-1]+[155940]),('boolean',synthetic[:-1]+[True]),('zero',synthetic[:-1]+[0])]:reject('assignment_'+name,lambda:independent.signed_values(a,155939))
    small=out/'tiny_native_positive.log';write_native(small,[1,-2]);need(native_model(small,2)==[None,True,False],'tiny native positive')
    for label,text in [('status','s UNSATISFIABLE\nv 1 -2 0\n'),('duplicate','s SATISFIABLE\nv 1 -1 0\n'),('missing','s SATISFIABLE\nv 1 0\n'),('unterminated','s SATISFIABLE\nv 1 -2\n'),('internalzero','s SATISFIABLE\nv 1 0 -2 0\n'),('doublestatus','s SATISFIABLE\ns SATISFIABLE\nv 1 -2 0\n'),('badtoken','s SATISFIABLE\nv 1 false 0\n')]:
        q=out/('corrupt_native_'+label+'.log');q.write_text(text,encoding='ascii',newline='\n');reject('native_'+label,lambda:native_model(q,2))
    smallcnf=out/'tiny_cnf_positive.cnf';smallcnf.write_bytes(b'p cnf 2 2\n1 0\n-2 0\n');need(cnf_object(smallcnf,[None,True,False],2)==2,'tiny actual clauses positive')
    for label,text in [('header',b'p cnf 3 2\n1 0\n-2 0\n'),('unit',b'p cnf 2 2\n-1 0\n-2 0\n'),('missing',b'p cnf 2 2\n1 0\n'),('range',b'p cnf 2 2\n1 0\n3 0\n')]:
        q=out/('corrupt_cnf_'+label+'.cnf');q.write_bytes(text);reject('cnf_'+label,lambda:cnf_object(q,[None,True,False],2))
    save(out/'controls.json',dict(positive_baseline_assignments=positives,rejected_corruptions=rejected,fullsize_codec_variables=155939,synthetic_fullsize_CNF_satisfaction_claim=False,actual_augmented_research_SAT_fixture=None,actual_augmented_research_SAT_fixture_null_reason='No research solver has been run. The two authentic baseline positives correctly fail the necessary extension.',source_reuse='Frozen independent complete-encoding checker provides strict signed values, clause truth and literal count-table decoder. No producer or native-runner imports.'))
    return dict(status='INDEPENDENT_HADAMARD_COUNT_MASTER_OBJECT_CALIBRATION_PASS',positive_baseline_count_objects=2,baseline_clauses_per_object=704454,augmented_native_codec_variables=155939,rejected_corruptions=len(rejected),scope='Complete native assignment and actual CNF plus literal count-object validation; this calibration supplies no augmented research SAT result or full factor.')
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    for mode in ('calibrate','sat'):
        s=sub.add_parser(mode);s.add_argument('--encoding-gate',type=Path,required=True);s.add_argument('--encoding-gate-sha256',required=True);s.add_argument('--out',type=Path,required=True)
        if mode=='sat':
            s.add_argument('--variant',choices=['baseline','at_least_seven'],required=True);s.add_argument('--assignment',type=Path,required=True);s.add_argument('--native-output',type=Path,required=True);s.add_argument('--decoded',type=Path)
    args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    try:
        pins=authenticate(args)
        if args.mode=='calibrate':result=calibration(args,out,pins)
        else:
            for f in (args.assignment,args.native_output,args.decoded):
                if f is not None:pins[key(f)]=sha(f)
            decoded,count=evaluate(read(D+'model.json'),args.variant,args.assignment,args.native_output,args.decoded);save(out/'independent_count_profile.json',decoded)
            result=dict(status='INDEPENDENT_HADAMARD_COUNT_MASTER_SAT_OBJECT_PASS',variant=args.variant,actual_clauses_checked=count,exception_count=decoded['exception_count'],independent_count_profile=key(out/'independent_count_profile.json'),independent_count_profile_sha256=sha(out/'independent_count_profile.json'),scope='One exact count-CSP witness only; no unsummed Gram, cross-group caps, full factor or target graph.')
        result.update(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},solver_calls=0,target_resolution=False,shared_code='Frozen independently authored encoding checker only; standard-library exact arithmetic. Producer/native sources are authenticated but never imported.',elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),elapsed_seconds=result['elapsed_seconds'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=pins,source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
