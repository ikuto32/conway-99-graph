"""Complete native SAT and raw25 object checker for the exact frozen model."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import gzip
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_triangle_one_c2_row_cnf as independent
import audit_20260930_one_c2_raw25 as raw
import audit_20260930_full99_sat_object as common
import audit_20260930_unrestricted_full99_sat_object as native

ROOT=Path(__file__).resolve().parents[1]
D=independent.D
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_one_c2_row_cnf/summary.json'
GATE_SHA='661062b1fbdf0d9e076082867b44353509fb892d9946dc142d1c70b91f59558d'
CAL=ROOT/'acceleration/results/20260930_independent_review/one_c2_raw25_calibration/summary.json'
CAL_SHA='4035e326162dff623b84fe1b41b010164ee5abd06e4d678f000f7e4eaaa7806c'
need,digest,key,read,save=common.need,common.digest,common.key,common.read,common.save

def inputs():
    need(digest(GATE)==GATE_SHA and digest(CAL)==CAL_SHA,'exact encoding and raw25calibration gates')
    gate=read(GATE);cal=read(CAL)
    need(gate['status']=='INDEPENDENT_TRIANGLE_ONE_C2_ROW_CNF_ENCODING_PASS' and cal['status']=='INDEPENDENT_ONE_C2_RAW25_CHECKER_CALIBRATION_PASS','independent frozen gate statuses')
    bindings={**gate['inputs_sha256'],**cal['inputs_sha256'],key(GATE):GATE_SHA,key(CAL):CAL_SHA,key(__file__):digest(__file__),
      'acceleration/audit_20260930_full99_sat_object.py':'65d90a85be5fe67c510e561839901e9b8b7c3b9fc1ab7439af0e6bd3746a380c',
      'acceleration/audit_20260930_unrestricted_full99_sat_object.py':'6b78545d53041382e9b134718637998e4d0083175640b70044f60f480bcbc200'}
    for path,value in bindings.items():need(digest(ROOT/path)==value,'bound scope/source hash '+path)
    model=read(D/'model.json');scope=read(D/'scope.json');derived=independent.scope_check(model,scope)
    return model,scope,derived,bindings

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit independent native/completeclause/raw25 checking path',producer_imports=False,
      shared_components=['Frozen independent raw25 integer checker and scope constructor, with prior calibration pinned.','Frozen independent native SAT parser, complete assignment and rawCNF parser.'],
      limitations=['SAT constructs only25rows, not36rows or99vertices.','The positive calibration fixture uses its own Gram, which differs in26entries from the researchGram.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')

def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,scope,derived,bindings=inputs();g,columns,known,entries,refs,components=derived
    fixture=read(raw.FIXTURE);c=fixture['incidence_matrix'];own=fixture['own_target_gram'];positive=raw.validate(c,own,None,components,columns)
    rejected=[]
    def reject(label,fn,expected_error=None):
        try:fn()
        except (ValueError,KeyError,IndexError) as e:
            if expected_error is not None:need(expected_error in str(e),'control reached the intended validator: '+str(e))
            rejected.append(dict(case=label,error=str(e)))
        else:raise ValueError('corruption accepted '+label)
    selected_group=next(group for group in components if 24 in group)
    allowed=[d for d in range(60) if sum(c[r][d] for r in selected_group if r<24)<2]
    pair=next((d,e) for d in allowed for e in allowed if d<e and sum(c[r][d]*c[r][e] for r in range(24))==2)
    bad=deepcopy(c)
    for d in pair:
        if bad[24][d]==0:
            remove=next(e for e in range(60) if bad[24][e] and e not in pair);bad[24][remove]=0;bad[24][d]=1
    bg=[[sum(bad[a][d]*bad[b][d] for d in range(60)) for b in range(25)] for a in range(25)]
    need(all(sum(row)==10 for row in bad),'isolated pair-cap control preserves row margins')
    need(all(sum(bad[r][d] for r in group if r<25)<=2 for group in components for d in range(60)),'isolated pair-cap control preserves component caps')
    reject('isolated_column_overlap3_with_valid_own_Gram_and_all_other_margins',lambda:raw.validate(bad,bg,None,components,columns),'outside-column overlap cap')
    save(args.out/'isolated_column_overlap_corruption.json',dict(incidence_matrix=bad,own_Gram=bg,column_pair=pair,expected_failure='outside-column overlap cap; all preceding checks pass'))
    variables,clauses=74814,256151;signed=list(range(1,variables+1));values=common.assignment_values(signed,variables)
    stdout=b'c synthetic codec; NOT research SAT\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,signed[i:i+100]))+(' 0' if i+100>=variables else '')+'\n').encode() for i in range(0,variables,100))
    parsed,native_result=native.native_values(io.BytesIO(stdout),variables);need(parsed==values,'all74814native/JSON values')
    cnf=b'p cnf 74814 256151\n'+b''.join((str(i%variables+1)+' 0\n').encode() for i in range(clauses));cnf_result=common.check_cnf_stream(io.BytesIO(cnf),values,variables,clauses)
    with gzip.open(args.out/'synthetic_native.stdout.txt.gz','wb') as stream:stream.write(stdout)
    with gzip.open(args.out/'synthetic_fullsize.cnf.gz','wb') as stream:stream.write(cnf)
    for label,badtext in [('missing_status',stdout.replace(b's SATISFIABLE\n',b'')),('missing_final0',stdout.replace(b'74814 0\n',b'74814\n')),('duplicate_id',stdout.replace(b'v 1 2 ',b'v 1 1 ',1)),('missing_id',stdout.replace(b'v 1 2 ',b'v 2 ',1))]:reject(label,lambda:native.native_values(io.BytesIO(badtext),variables))
    for label,badcnf in [('wrong_header',cnf.replace(b'74814 256151',b'74814 256150',1)),('missing_clause',cnf[:cnf.rfind(b'\n',0,-1)+1]),('false_clause',cnf.replace(b'1 0\n',b'-1 0\n',1))]:reject(label,lambda:common.check_cnf_stream(io.BytesIO(badcnf),values,variables,clauses))
    reject('missing_last_assignment',lambda:common.assignment_values(signed[:-1],variables))
    reject('boolean_assignment',lambda:common.assignment_values([True]+signed[1:],variables))
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable frozen inputs')
    report={**provenance(bindings),'status':'INDEPENDENT_TRIANGLE_ONE_C2_ROW_OBJECT_CHECKER_CALIBRATION_PASS','variables':variables,'clauses':clauses,'positive_raw25':positive,'reused_raw25_calibration':dict(path=key(CAL),sha256=CAL_SHA,negative_controls=9),'fresh_corrupt_controls':rejected,'synthetic_codec':dict(native=native_result,cnf=cnf_result,research_SAT_witness=False),'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,scope,derived,bindings=inputs();g,columns,known,entries,refs,components=derived
    values=common.assignment_values(read(args.assignment)['assignment'],74814)
    with args.native_output.open('rb') as stream:parsed,native_result=native.native_values(stream,74814)
    need(values==parsed,'complete native/JSON agreement')
    with (D/'instance.cnf').open('rb') as stream:clause_result=common.check_cnf_stream(stream,values,74814,256151)
    c=[row[:] for row in known]
    for e in entries:c[e['row']][e['column']]=int(values[e['id']])
    result=raw.validate(c,g,known,components,columns)
    if args.decoded:
        decoded=read(args.decoded);need(decoded['incidence_matrix']==c and decoded['Q1']==result['Q1'] and decoded['selected_C2_row']==c[24],'independent raw25/Q1/selectedrow versus optional producer artifact')
    save(args.out/'independent_factor.json',dict(incidence_matrix=c,target_gram=g,Q1=result['Q1'],selected_C2_row=c[24],selected_C2_coordinate=0,components=components,exact_checks=result,encoding_model_sha256=digest(D/'model.json'),scope_sha256=digest(D/'scope.json'),is_complete36row_factor=False,is_full99_graph=False))
    for path in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(path)]=digest(path)
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable artifacts')
    report={**provenance(bindings),'status':'INDEPENDENT_TRIANGLE_ONE_C2_ROW_SAT_OBJECT_PASS','native_assignment':native_result,'all_raw_clauses':clause_result,'exact_object':result,'independent_factor_sha256':digest(args.out/'independent_factor.json'),'elapsed_seconds':time.monotonic()-start}
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
