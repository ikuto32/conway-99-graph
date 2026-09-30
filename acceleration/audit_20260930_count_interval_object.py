"""Independent constructed/native exact interval-count object verification."""
from pathlib import Path
from datetime import datetime,timezone
from itertools import combinations,product
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
import audit_20260930_hadamard_count_master_object as baseobj
ROOT=baseobj.ROOT;B=baseobj.B;BASE=baseobj.D;D=B+'count_interval_cnf/';W=B+'count_interval_witness/';G=B+'independent_review/count_interval_cnf/summary.json';GH='03bc6b052a831eb0e5d3dacce7647ec88a81410e5f63ec81c88246575cd6baa6'
need=baseobj.need;read=baseobj.read;sha=baseobj.sha;save=baseobj.save;key=baseobj.key
PINS={'acceleration/native_20260930_count_interval.py':'60e378aaae9b250dc4eba3287e473e17a8417e52508d6d024d51681627008abc','acceleration/native_20260930_count_interval_spec.md':'6769423d47ed8fe9fcf2f7f8fc7a1315f79cbb35d6f77c3c673e0c5dfc471e60','build/research-cadical195/source/build/cadical':'021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7','build/rook-drat-checker/drat-trim.exe':'23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac'}
def authenticate(args):
    need(key(args.encoding_gate)==G and args.encoding_gate_sha256==GH and sha(args.encoding_gate)==GH,'exact interval encoding gate');gate=read(G);need(gate['status']=='INDEPENDENT_COUNT_INTERVAL_ENCODING_PASS','encoding status');pins={G:GH}
    for p,h in {**gate['inputs_sha256'],**PINS}.items():need(sha(ROOT/p)==h,'authenticated input '+p);pins[p]=h
    for stem in ['native_20260930_unrestricted_full99','native_20260930_proof_location']:
        p='acceleration/'+stem+'.py';need(sha(ROOT/p)==baseobj.NATIVE_PINS[p],'frozen engineering helper');pins[p]=sha(ROOT/p)
        spec='acceleration/'+stem+'_spec.md';need((ROOT/spec).exists(),'runtime spec present');pins[spec]=sha(ROOT/spec)
    for p in [Path(__file__),Path(baseobj.__file__),Path(baseobj.independent.__file__),ROOT/'docs/AUDIT_20260930_COUNT_INTERVAL_OBJECT.md']:pins[key(p)]=sha(p)
    return pins
def interval_rows(base,decoded,config,table,values):
    selected=decoded['selected_global_signature_indices'];groups=base['groups'];raw=read(baseobj.independent.RAW);C=raw['core_adjacency'];localindex={tuple(c):i for i,c in enumerate(table['local_cells'])};rows=[]
    for a,b in combinations(range(12),2):
        if a//2==b//2:continue
        for f,h in product(range(3),repeat=2):
            low=high=0
            for g,s in enumerate(groups):
                if a in s and b in s:
                    j=localindex[s.index(a),s.index(b),f,h];r=table['records'][selected[g]];low+=r['minimum'][j];high+=r['maximum'][j]
            i=12*f+a;j=12*h+b;target=12*int(i==j)-C[i][j]+2-sum(C[i][k]*C[k][j]for k in range(36))-int(f==h)
            need(low<=target<=high,'literal exact scalar interval');rows.append(dict(cell=len(rows),coordinates=[a,b],fibres=[f,h],lower=low,target=target,upper=high))
    need(len(rows)==540,'all literal540 intervals')
    # Independently recompute every auxiliary by direct truth/count, not the producer recurrence.
    for channel in config['channels']:
        mask=int(channel['selector_index_mask_hex'],16);ids=base['group_domains'][channel['group']]['selectors'];expected=any(values[x]for k,x in enumerate(ids)if mask>>k&1);need(values[channel['variable']]==expected,'exact OR auxiliary')
    ev=lambda t:t if type(t)is bool else values[t]
    for cell in config['cells']:
        for kind in ['lower','upper']:
            counter=cell[kind+'_counter']
            for state in counter['states']:need(values[state['id']]==(sum(ev(x)for x in counter['inputs'][:state['i']])>=state['j']),'exact direct-prefix auxiliary')
    return rows
def actual_clauses(values,corrupted_variables=()):
    faults={x:None for x in corrupted_variables};n=0
    with (ROOT/(D+'instance.cnf')).open('r',encoding='ascii',newline='')as f:
        need(f.readline()=='p cnf 185963 7659287\n','actual literal header')
        for line in f:
            tokens=line.split();need(tokens and tokens[-1]=='0','actual terminator');clause=[int(x)for x in tokens[:-1]];need(all(x and abs(x)<=185963 for x in clause),'actual ID range');n+=1
            truth=[values[abs(x)]==(x>0)for x in clause];need(any(truth),f'actual false clause {n}')
            for variable in corrupted_variables:
                if faults[variable]is None and any(abs(x)==variable for x in clause)and not any(v^(abs(x)==variable)for x,v in zip(clause,truth)):faults[variable]=dict(clause_index=n,clause=clause)
    need(n==7659287,'complete clause count');need(all(r is not None for r in faults.values()),'all requested corruptions have actual falsified-clause witnesses');return n,faults
def check(args,calibrate=False):
    model=read(D+'model.json');base=read(BASE+'model.json');assignment=json.loads(args.assignment.read_bytes())['assignment'];values=baseobj.independent.signed_values(assignment,185963)
    if args.native_output is not None:need(baseobj.native_model(args.native_output,185963)==values,'native complete assignment equality')
    with gzip.open(ROOT/model['inventory_configuration_path'],'rt',encoding='utf-8')as f:config=json.load(f)
    with gzip.open(ROOT/(B+'hadamard_count_gram_intervals/signature_intervals.json.gz'),'rt',encoding='utf-8')as f:table=json.load(f)
    decoded=baseobj.independent.literal_decode(base,values[:155940],'at_least_seven');rows=interval_rows(base,decoded,config,table,values)
    flip=[config['channels'][0]['variable'],config['cells'][0]['lower_counter']['states'][0]['id'],config['cells'][-1]['upper_counter']['states'][-1]['id'],base['coordinate_domains'][0]['selectors'][0],base['group_domains'][0]['selectors'][0]]if calibrate else[]
    clauses,faults=actual_clauses(values,flip)
    return decoded,rows,clauses,faults,values
def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    for mode in ['calibrate','constructed','sat']:
        p=sub.add_parser(mode);p.add_argument('--encoding-gate',type=Path,required=True);p.add_argument('--encoding-gate-sha256',required=True);p.add_argument('--out',type=Path,required=True)
        p.add_argument('--assignment',type=Path,required=mode!='calibrate',default=ROOT/(W+'assignment.json'));p.add_argument('--native-output',type=Path,required=mode=='sat')
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    try:
        pins=authenticate(args);pins[key(args.assignment)]=sha(args.assignment)
        if args.native_output is not None:pins[key(args.native_output)]=sha(args.native_output)
        if args.mode in ('calibrate','constructed'):
            need(sha(ROOT/(W+'summary.json'))=='91e72adcf4c1052b0348318cdb0d25ae6bf90f02b11901d8175e69525a5a712b','frozen constructed producer');summary=read(W+'summary.json');need(summary['native_calls']==summary['solver_calls']==0,'constructed witness no native')
            for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():need(sha(ROOT/p)==h,'constructed raw input/output '+p);pins[p]=h
            pins[W+'summary.json']=sha(ROOT/(W+'summary.json'));need(sha(args.assignment)=='242c6349604955f45fb103dc2221e62d70d3ccb417d8a31a8bc6e9e19724d0cc','specific constructed assignment')
        decoded,rows,clauses,faults,values=check(args,args.mode=='calibrate')
        if args.mode in ('calibrate','constructed'):
            old=baseobj.independent.signed_values(read(B+'hadamard_count_master_native_pilot_v2/main/parsed_model.json')['assignment'],155939);need(values[:155940]==old,'unchanged authentic native base values');need(decoded==read(W+'count_profile.json')and rows==read(W+'all540_intervals.json')['records'],'literal independent count/interval reproduction')
        save(out/'independent_count_profile.json',decoded);save(out/'all540_intervals.json',dict(records=rows,profile_sha256=decoded['profile_sha256']))
        if args.mode=='calibrate':
            rejected=[]
            def reject(name,fn):
                try:fn()
                except(ValueError,KeyError,IndexError,TypeError):rejected.append(name);return
                raise ValueError('accepted corruption '+name)
            assignment=json.loads(args.assignment.read_bytes())['assignment']
            for name,bad in [('missing',assignment[:-1]),('duplicate',assignment[:-1]+[assignment[0]]),('boolean',assignment[:-1]+[True]),('range',assignment[:-1]+[185964]),('zero',assignment[:-1]+[0])]:reject(name,lambda:baseobj.independent.signed_values(bad,185963))
            # Actual false-clause witnesses, each checked against independently altered values.
            for x,witness in faults.items():
                bad=values.copy();bad[x]=not bad[x];need(not baseobj.independent.clause_pass(witness['clause'],bad),'literal altered assignment falsifies actual clause');rejected.append('actual_variable_'+str(x))
            codec=out/'codec_only.log';baseobj.write_native(codec,assignment);need(baseobj.native_model(codec,185963)==values,'complete native codec positive; no native execution')
            for name,text in [('UNSAT','s UNSATISFIABLE\nv 1 -2 0\n'),('duplicate','s SATISFIABLE\nv 1 -1 0\n'),('unterminated','s SATISFIABLE\nv 1 -2\n')]:
                path=out/('corrupt_native_'+name+'.log');path.write_text(text,encoding='ascii',newline='\n');reject(name,lambda:baseobj.native_model(path,2))
            save(out/'controls.json',dict(actual_constructed_positive_clauses=clauses,altered_assignment_false_clause_witnesses=faults,rejected_corruptions=rejected,native_codec_only=True,native_execution=False,full_factor_positive=False))
            status='INDEPENDENT_COUNT_INTERVAL_OBJECT_CALIBRATION_PASS'
        else:status='INDEPENDENT_COUNT_INTERVAL_CONSTRUCTED_OBJECT_PASS'if args.mode=='constructed'else'INDEPENDENT_COUNT_INTERVAL_SAT_OBJECT_PASS'
        result=dict(status=status,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},assignment_variables=185963,actual_clauses_checked=clauses,literal_interval_cells=540,exception_count=decoded['exception_count'],profile_sha256=decoded['profile_sha256'],constructed_assignment=args.mode!='sat',solver_calls=0,target_resolution=False,scope='One exact necessary interval count-CSP witness only, no full Gram factor or residual graph.',shared_components='Frozen independently authored base strict assignment/native parser and literal count decoder; no producer imports. New all-clause scanner, direct-prefix auxiliaries and raw-core-derived scalar interval checks.',elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',result);print(json.dumps(dict(status=status,summary_sha256=sha(out/'summary.json'),seconds=result['elapsed_seconds'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
