"""Compact complete-assignment/raw25 checker; calibration uses derived SAT."""
import argparse
from datetime import datetime,timezone
import gzip
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_triangle_one_c2_row_object as prior

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_one_c2_compact'
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_one_c2_compact/summary.json'
GATE_SHA='ea7d2ab3ea41118c6047261fc0dc7e6e7b23f667785cfec8d902c0fadc635a60'
ACTUAL=ROOT/'acceleration/results/20260930_independent_review/triangle_one_c2_row_sat_object/summary.json'
ACTUAL_SHA='e4693a9bb52831e26ecdeb350565123df4cac58917a66db4762ea31e161809b1'
ORIGINAL_ASSIGNMENT=ROOT/'acceleration/results/20260930_triangle_one_c2_row_native_pilot/main/parsed_model.json'
need,digest,key,read,save=prior.need,prior.digest,prior.key,prior.read,prior.save

def inputs():
    _,scope,derived,bindings=prior.inputs()
    need(digest(GATE)==GATE_SHA,'compact encoding gate hash');gate=read(GATE)
    need(gate['status']=='INDEPENDENT_TRIANGLE_ONE_C2_COMPACT_EQUIVALENCE_PASS','independent compact equivalence gate')
    bindings.update(gate['inputs_sha256']);bindings.update({key(GATE):GATE_SHA,key(__file__):digest(__file__)})
    for p,v in bindings.items():need(digest(ROOT/p)==v,'bound source/artifact '+p)
    model=read(D/'model.json');g,columns,known,entries,refs,components=derived
    need(model['variables']==22379 and model['clauses']==81366 and model['known_incidence_rows']==known and model['entry_variables']==entries and model['target_gram_rows']==g,'same independently checked primaryscope')
    return model,derived,bindings

def decode(values,derived):
    g,columns,known,entries,refs,components=derived;c=[r[:] for r in known]
    for e in entries:c[e['row']][e['column']]=int(values[e['id']])
    result=prior.raw.validate(c,g,known,components,columns)
    return c,result

def clauses(values):
    with (D/'instance.cnf').open('rb') as stream:return prior.common.check_cnf_stream(stream,values,22379,81366)

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit compact native/completeclause/raw25 checker',producer_imports=False,shared_components=['Frozen independent original raw25 scope/validator and native/assignment/CNF helpers reused.','Independent compact equivalence gate authenticates every changed clause/model field.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',limitations=['A checked compact SAT object is the same25rowprojection, not a larger factor or graph.'])

def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,derived,bindings=inputs()
    need(digest(ACTUAL)==ACTUAL_SHA,'verified originalSAT report');actual=read(ACTUAL)
    need(actual['status']=='INDEPENDENT_TRIANGLE_ONE_C2_ROW_SAT_OBJECT_PASS','complete original positiveSAT checker')
    for p,v in actual['inputs_sha256'].items():need(digest(ROOT/p)==v,'originalSAT input unchanged');bindings[p]=v
    bindings[key(ACTUAL)]=ACTUAL_SHA
    full=prior.common.assignment_values(read(ORIGINAL_ASSIGNMENT)['assignment'],74814)
    signed=[i if full[i] else -i for i in range(1,22380)];values=prior.common.assignment_values(signed,22379)
    checked=clauses(values);c,result=decode(values,derived)
    save(args.out/'restricted_verified_assignment.json',dict(assignment=signed,derivation='Restriction to IDs1..22379 of independently verified original25 SAT assignment; no new solve.'))
    stdout=b'c codec from restricted verified original assignment; NOT a new solver call\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,signed[i:i+100]))+(' 0' if i+100>=len(signed) else '')+'\n').encode() for i in range(0,len(signed),100))
    got,native=prior.native.native_values(io.BytesIO(stdout),22379);need(got==values,'complete compact native/JSON codec')
    with gzip.open(args.out/'derived_assignment_native_codec.stdout.txt.gz','wb') as stream:stream.write(stdout)
    save(args.out/'derived_independent_factor.json',dict(incidence_matrix=c,Q1=result['Q1'],selected_C2_row=c[24],exact_checks=result,is_complete36row_factor=False,is_full99_graph=False))
    rejected=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):rejected.append(label)
        else:raise ValueError('corrupt compact control accepted '+label)
    for label,i in [('C1_primary_flip',1),('C2_primary_flip',601),('first_auxiliary_flip',651)]:
        bad=values[:];bad[i]^=1;reject(label,lambda:clauses(bad))
    for label,bad in [('missing_status',stdout.replace(b's SATISFIABLE\n',b'')),('missing_terminator',stdout.replace(b' 0\n',b'\n')),('wrong_UNSAT_status',stdout.replace(b's SATISFIABLE',b's UNSATISFIABLE'))]:reject(label,lambda:prior.native.native_values(io.BytesIO(bad),22379))
    reject('partial_assignment',lambda:prior.common.assignment_values(signed[:-1],22379))
    reject('old_74814_assignment_wrong_scope',lambda:prior.common.assignment_values(read(ORIGINAL_ASSIGNMENT)['assignment'],22379))
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable inputs')
    report={**provenance(bindings),'status':'INDEPENDENT_TRIANGLE_ONE_C2_COMPACT_OBJECT_CHECKER_CALIBRATION_PASS','variables':22379,'clauses':81366,'positive_control':'Actual complete compact assignment derived by restriction of a previously verified originalSAT model; independently passes every compact clause.','source_original_SAT_audit':key(ACTUAL),'source_original_SAT_audit_sha256':ACTUAL_SHA,'derived_assignment_path':key(args.out/'restricted_verified_assignment.json'),'derived_assignment_sha256':digest(args.out/'restricted_verified_assignment.json'),'all_compact_clauses':checked,'raw25':result,'native_codec':native,'corrupt_controls_rejected':rejected,'new_solver_calls':0,'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,derived,bindings=inputs()
    values=prior.common.assignment_values(read(args.assignment)['assignment'],22379)
    with args.native_output.open('rb') as stream:got,native=prior.native.native_values(stream,22379)
    need(got==values,'full compact native/JSON equality');checked=clauses(values);c,result=decode(values,derived)
    if args.decoded:
        raw=read(args.decoded);need(raw['incidence_matrix']==c and raw['Q1']==result['Q1'] and raw['selected_C2_row']==c[24],'optionaldecoded agreement')
    save(args.out/'independent_factor.json',dict(incidence_matrix=c,Q1=result['Q1'],selected_C2_row=c[24],exact_checks=result,is_complete36row_factor=False,is_full99_graph=False))
    for path in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(path)]=digest(path)
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable inputs')
    report={**provenance(bindings),'status':'INDEPENDENT_TRIANGLE_ONE_C2_COMPACT_SAT_OBJECT_PASS','native_assignment':native,'all_raw_clauses':checked,'exact_raw25':result,'independent_factor_sha256':digest(args.out/'independent_factor.json'),'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('calibrate');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('sat');p.add_argument('--out',type=Path,required=True);p.add_argument('--assignment',type=Path,required=True);p.add_argument('--native-output',type=Path,required=True);p.add_argument('--decoded',type=Path)
    args=ap.parse_args()
    try:(calibrate if args.mode=='calibrate' else sat)(args)
    except BaseException as e:
        if args.out.exists() and not (args.out/'failure.json').exists():save(args.out/'failure.json',dict(status='CHECK_FAILED',error=repr(e)))
        raise
if __name__=='__main__':main()
