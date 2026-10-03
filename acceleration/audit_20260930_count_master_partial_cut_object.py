"""Independent full signed/native/CNF and raw count checks for705845 clauses."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json,platform,subprocess,sys,time
import audit_20260930_count_master_eight_orbit_cut_object as old
ROOT=old.ROOT;B=old.B;I=B+'independent_review/';D=B+'count_master_scalar_cuts/';MASTER=old.D
base=old.base;independent=old.independent;need=old.need;read=old.read;sha=old.sha;save=old.save;key=old.key
GATE=I+'count_master_partial_cut_cnf/summary.json';GATE_SHA='dc1ada9d87d41b5cc6597cd0ff7ce2ed0a06981d8b487dbb797505240f435460'
CNF=ROOT/D/'instance.cnf';N=155939;M=705845
DOC='docs/AUDIT_20260930_COUNT_MASTER_PARTIAL_CUT_CNF.md'
NATIVE='acceleration/native_20260930_count_master_partial_cuts.py'

def authenticate(args):
    need(key(args.encoding_gate)==GATE and args.encoding_gate_sha256==GATE_SHA and sha(ROOT/GATE)==GATE_SHA,'exact independent composition gate')
    gate=read(GATE);need(gate['status']=='INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_CNF_PASS','gate status');pins={GATE:GATE_SHA}
    for p,h in gate['inputs_sha256'].items():need(sha(ROOT/p)==h,'unchanged gate input '+p);pins[p]=h
    # Source identities are bound to their earlier immutable independent records.
    previous=read(I+'count_master_eight_orbit_cut_object_calibration/summary.json')
    need(previous['status']=='INDEPENDENT_COUNT_MASTER_EIGHT_ORBIT_CUT_OBJECT_CALIBRATION_PASS','old calibrated checking path')
    previous_path=I+'count_master_eight_orbit_cut_object_calibration/summary.json';pins[previous_path]=sha(ROOT/previous_path)
    for p in [key(old.__file__),key(base.__file__),key(independent.__file__)]:
        need(previous['inputs_sha256'][p]==sha(ROOT/p),'independent reused source identity '+p);pins[p]=sha(ROOT/p)
    for p in [key(__file__),DOC,NATIVE,NATIVE.replace('.py','_spec.md'),'acceleration/native_20260930_unrestricted_full99.py','acceleration/native_20260930_unrestricted_full99_spec.md','acceleration/native_20260930_proof_location.py','acceleration/native_20260930_proof_location_spec.md','uv.lock','pyproject.toml']:
        pins[p]=sha(ROOT/p)
    # All imports of the native wrapper are restricted to the two pinned helpers.
    native_tools={'build/research-cadical195/source/build/cadical':'021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7','build/rook-drat-checker/drat-trim.exe':'23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac'}
    for p,h in native_tools.items():need(sha(ROOT/p)==h,'native tool identity');pins[p]=h
    return pins

def scalar_truth(result,values,records):
    table=result['coordinate_group_fibre_counts'];truths=[]
    for rec in records:
        raw=any(table[t['coordinate']][t['group']][t['fibre']]>t['upper_bound'] for t in rec['partial_restrictions'])
        actual=independent.clause_pass(rec['clause'],values);need(raw==actual,'new scalar raw/channel equality');truths.append(raw)
    return truths

def evaluate(args):
    assignment=json.loads(args.assignment.read_bytes())['assignment'];values=independent.signed_values(assignment,N)
    need(values==base.native_model(args.native_output,N),'all native/JSON variables identical')
    count=base.cnf_object(CNF,values,M);result=independent.literal_decode(read(MASTER+'model.json'),values,'at_least_seven')
    prior=old.cut_truth(result,values,old.cut_records());fresh=scalar_truth(result,values,read(D+'model.json')['scalar_clause_records'])
    need(all(prior)and all(fresh),'all old and scalar cuts')
    if args.decoded is not None:base.compare_decoded(json.loads(args.decoded.read_bytes()),result,sha(ROOT/MASTER/'model.json'),M)
    return result,count,prior,fresh

def envelope_diagnostic(result):
    raw=read(B+'hadamard20_support/six_prism.json');groups=read(MASTER+'model.json')['groups'];counts=result['coordinate_group_fibre_counts'];G=raw['prescribed_Gram36'];rows=[]
    for a in range(12):
        for b in range(a+1,12):
            common=[g for g,s in enumerate(groups)if a in s and b in s]
            if not common:continue
            need(len(common)==5,'five group scalar universe')
            for f in range(3):
                for h in range(3):
                    upper=sum(min(counts[a][g][f],counts[b][g][h])for g in common);target=G[12*f+a][12*h+b]
                    rows.append(dict(coordinates=[a,b],fibres=[f,h],upper=upper,target=target,passes=upper>=target))
    need(len(rows)==540,'full540 envelope diagnostics')
    return dict(records=rows,failed=[r for r in rows if not r['passes']],scope='Necessary universal overlap upper bounds only; not all are encoded by the six added clauses. Diagnostic failures do not invalidate a count-CSP witness.')

def calibrate(out,pins):
    rejected=[]
    def reject(name,fn):
        try:fn()
        except(ValueError,KeyError,TypeError,IndexError):rejected.append(name)
        else:raise ValueError('bad control accepted '+name)
    path=B+'count_master_eight_orbit_cut_native_pilot/main/parsed_model.json';need(sha(ROOT/path)=='40174793158d22cb17a0fff711102e9f3053ab04c9b23ba632d94c2976727189','authentic old SAT assignment');pins[path]=sha(ROOT/path)
    assignment=read(path)['assignment'];values=independent.signed_values(assignment,N);native=out/'old_count_synthetic_native.log';base.write_native(native,assignment);need(base.native_model(native,N)==values,'full155939 codec positive')
    base.cnf_object(ROOT/old.CNF,values,705839);result=independent.literal_decode(read(MASTER+'model.json'),values,'at_least_seven');need(all(old.cut_truth(result,values,old.cut_records())),'prior six cuts positive')
    records=read(D+'model.json')['scalar_clause_records'];truth=scalar_truth(result,values,records);need(truth==[True]*5+[False],'actual old witness fails only last scalar clause');reject('old_real_count_excluded',lambda:base.cnf_object(CNF,values,M))
    altered=copy.deepcopy(records);altered[-1]['clause'][0]*=-1;reject('new_clause_wrong_sign',lambda:scalar_truth(result,values,altered))
    badresult=copy.deepcopy(result);badresult['coordinate_group_fibre_counts'][11][1][1]=1;reject('raw_count_channel_mismatch',lambda:scalar_truth(badresult,values,records))
    for name,a in [('missing',assignment[:-1]),('duplicate',assignment[:-1]+[assignment[0]]),('zero',assignment[:-1]+[0]),('range',assignment[:-1]+[N+1]),('boolean',assignment[:-1]+[True])]:reject(name,lambda a=a:independent.signed_values(a,N))
    toy=out/'tiny_positive.cnf';toy.write_bytes(b'p cnf 3 3\n1 0\n-2 0\n2 3 0\n');need(base.cnf_object(toy,[None,True,False,True],3)==3,'complete strengthened tiny positive')
    for label,data in [('header',b'p cnf 4 3\n1 0\n-2 0\n2 3 0\n'),('false',b'p cnf 3 3\n1 0\n-2 0\n-1 0\n'),('missing',b'p cnf 3 3\n1 0\n-2 0\n'),('range',b'p cnf 3 3\n1 0\n-2 0\n4 0\n')]:
        p=out/('corrupt_'+label+'.cnf');p.write_bytes(data);reject('cnf_'+label,lambda p=p:base.cnf_object(p,[None,True,False,True],3))
    for label,text in [('status','s UNSATISFIABLE\nv 1 -2 0\n'),('duplicate','s SATISFIABLE\nv 1 1 0\n'),('missing','s SATISFIABLE\nv 1 0\n'),('unterminated','s SATISFIABLE\nv 1 -2\n'),('internal_zero','s SATISFIABLE\nv 1 0 -2 0\n')]:
        p=out/('bad_native_'+label+'.log');p.write_text(text,encoding='ascii');reject('native_'+label,lambda p=p:base.native_model(p,2))
    diagnostic=envelope_diagnostic(result);need(len(diagnostic['failed'])==1 and diagnostic['failed'][0]==dict(coordinates=[9,11],fibres=[2,1],upper=1,target=2,passes=False),'known540-envelope negative control')
    save(out/'controls.json',dict(old_real_count_positive_clauses=705839,new_formula_correctly_rejects_old_witness=True,scalar_truth=truth,fullsize_codec=N,tiny_complete_positive=True,rejected=rejected,new_formula_positive=None,new_formula_positive_reason='No research SAT assignment for the strengthened instance supplied.',full_factor=False));save(out/'old_count_envelope_diagnostic.json',diagnostic)
    return dict(status='INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_OBJECT_CALIBRATION_PASS',rejected_corruptions=len(rejected),actual_clause_count=M,fullsize_native_codec_variables=N)

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    for mode in ['calibrate','sat']:
        p=sub.add_parser(mode);p.add_argument('--variant',choices=['at_least_seven'],default='at_least_seven');p.add_argument('--encoding-gate',type=Path,required=True);p.add_argument('--encoding-gate-sha256',required=True);p.add_argument('--out',type=Path,required=True)
        if mode=='sat':p.add_argument('--assignment',type=Path,required=True);p.add_argument('--native-output',type=Path,required=True);p.add_argument('--decoded',type=Path)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        pins=authenticate(args)
        if args.mode=='calibrate':report=calibrate(out,pins)
        else:
            for p in [args.assignment,args.native_output,args.decoded]:
                if p is not None:pins[key(p)]=sha(p)
            result,count,prior,fresh=evaluate(args);save(out/'independent_count_profile.json',result);save(out/'independent_cut_avoidance.json',dict(old_profile_cuts=prior,scalar_cuts=fresh));diagnostic=envelope_diagnostic(result);save(out/'universal_upper_envelopes.json',diagnostic)
            report=dict(status='INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_SAT_OBJECT_PASS',actual_clauses_checked=count,exception_count=result['exception_count'],profile_sha256=result['profile_sha256'],independent_count_profile=key(out/'independent_count_profile.json'),independent_count_profile_sha256=sha(out/'independent_count_profile.json'),upper_envelope_diagnostic_failures=len(diagnostic['failed']))
        need(time.monotonic()-started<180,'object bound180s')
        report.update(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},solver_calls=0,full_factor=False,target_resolution=False,shared_components=['Reuses only frozen independent native/CNF codecs and literal count decoder; no producer/native imports.','Prior encoding composition and count-channel meaning are pinned premises.'],elapsed_seconds=time.monotonic()-started,scope='Exact strengthened count-CSP object only; not a factor, residual D or target graph.');save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
