"""Independently check complete strengthened-factor SAT and exact raw factor."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import gzip
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_triangle_joint_factor_object_v2 as old
import audit_20260930_triangle_factor_components as components_audit

ROOT=Path(__file__).resolve().parents[1]
need,digest,key,read,save=old.need,old.digest,old.key,old.read,old.save
D=ROOT/'acceleration/results/20260930_triangle_factor_components'
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_factor_components/summary.json'
GATE_SHA='03d84677f34e0a209f9331c32efcd0b843dae60b97dbf9e9102b85171a5fef5b'
OLD_CAL=ROOT/'acceleration/results/20260930_independent_review/triangle_joint_factor_object_calibration_v2/summary.json'
OLD_CAL_SHA='f0a23a0d4f0d81a6a789cb46f8f11d757e1ee753dbfea692c3eb47834999a464'

def bind_inputs():
    model0,scope,derived,bindings=old.bind_inputs()
    need(digest(GATE)==GATE_SHA and digest(OLD_CAL)==OLD_CAL_SHA,'component and base-object calibration gate hashes')
    gate=read(GATE);cal=read(OLD_CAL)
    need(gate['status']=='INDEPENDENT_TRIANGLE_COMPONENT_FACTOR_CNF_ENCODING_PASS','component encoding semantic gate')
    need(cal['status']=='INDEPENDENT_TRIANGLE_JOINT_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS','frozen base raw-object calibration')
    bindings.update(gate['inputs_sha256']);bindings.update(cal['inputs_sha256'])
    bindings.update({key(GATE):GATE_SHA,key(OLD_CAL):OLD_CAL_SHA,key(__file__):digest(__file__)})
    for path,value in bindings.items():need(digest(ROOT/path)==value,'input/source hash '+path)
    model=read(D/'model.json');h,g,columns,known,zeros,entries,refs=derived
    comp,contrasts=components_audit.kernel_check(read(D/'kernel_certificate.json'),h,g)
    need(model['known_incidence_rows']==known and model['target_gram_rows']==g and model['entry_variables']==entries,'same complete primary factor scope')
    need(model['variables']==61296 and model['clauses']==212580,'augmented scope dimensions')
    return model,derived,comp,bindings

def component_check(c,comp):
    need(len(c)==36 and all(len(r)==60 and all(type(x) is int and x in (0,1) for x in r) for r in c),'raw36x60 binary component input')
    need(sorted(x for group in comp for x in group)==list(range(36)) and len(comp)==3,'complete component partition')
    totals=[[sum(c[r][d] for r in group) for d in range(60)] for group in comp]
    need(all(x==2 for row in totals for x in row),'all180 exact component totals')
    return dict(equations_checked=180,component_column_totals=totals)

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit independent augmented-factor object checker',producer_imports=False,
      shared_components=['Frozen independent base factor/Gram checker, original scope reconstruction, complete assignment/native-output/CNF parsing reused with pins.','Frozen independently audited exact component-kernel implication and augmented byte gate.'],
      target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',limitations=['An accepted SAT object is only a36x60factor, not a full99graph.','No positive full36factor of the research Gram is known; partial24row fixtures and separately labelled synthetic codecs calibrate the checker.'])

def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    model,derived,comp,bindings=bind_inputs();h,g,columns,known,zeros,entries,refs=derived
    positives=[]
    for dirname,record in [('wave151-triangle-root-factor','exact_partial_factor'),('wave154-triangle-factor-portfolio','second_exact_Q1_representative')]:
        path=ROOT/'external_conway99_research/attempts'/dirname/'exact-results.json';q=read(path)[record]['Q1']
        c=[r[:] for r in known[:12]]+[[int(a in columns[q[d]]) for d in range(60)] for a in range(12)]
        positives.append(old.independent.factor_check(c,[row[:24] for row in g[:24]],known[:24]))
    synthetic=[[0]*60 for _ in range(36)]
    for column in range(60):
        for group in comp:
            for position in [2*column%12,(2*column+1)%12]:synthetic[group[position]][column]=1
    linear_result=component_check(synthetic,comp)
    save(args.out/'synthetic_component_positive.json',dict(incidence_matrix=synthetic,components=comp,label='Only a synthetic positive component-equation control; not a Gram factor or research SAT witness'))
    negative=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):negative.append(label)
        else:raise ValueError('corrupt control accepted '+label)
    bad=[r[:] for r in synthetic];bad[comp[0][0]][0]^=1
    reject('wrong_component_total',lambda:component_check(bad,comp))
    reject('wrong_component_partition',lambda:component_check(synthetic,[comp[0],comp[0],comp[2]]))
    variables,clauses=61296,212580;signed=list(range(1,variables+1));values=old.common.assignment_values(signed,variables)
    raw=b'c explicitly synthetic augmented codec, not a research SAT witness\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,signed[i:i+100]))+(' 0' if i+100>=variables else '')+'\n').encode() for i in range(0,variables,100))
    got,native_result=old.native.native_values(io.BytesIO(raw),variables);need(values==got,'all61296native/JSON assignment values')
    cnf=b'p cnf 61296 212580\n'+b''.join((str(i%variables+1)+' 0\n').encode() for i in range(clauses))
    cnf_result=old.common.check_cnf_stream(io.BytesIO(cnf),values,variables,clauses)
    with gzip.open(args.out/'synthetic_native.stdout.txt.gz','wb') as stream:stream.write(raw)
    with gzip.open(args.out/'synthetic_fullsize.cnf.gz','wb') as stream:stream.write(cnf)
    for label,bad in [('missing_status',raw.replace(b's SATISFIABLE\n',b'')),('missing_terminator',raw.replace(b'61296 0\n',b'61296\n')),('duplicate_variable',raw.replace(b'v 1 2 ',b'v 1 1 ',1)),('missing_variable',raw.replace(b'v 1 2 ',b'v 2 ',1))]:
        reject(label,lambda:old.native.native_values(io.BytesIO(bad),variables))
    for label,bad in [('old_dimensions',cnf.replace(b'61296 212580',b'58860 203748',1)),('missing_clause',cnf[:cnf.rfind(b'\n',0,-1)+1]),('wrong_sign',cnf.replace(b'1 0\n',b'-1 0\n',1))]:
        reject(label,lambda:old.common.check_cnf_stream(io.BytesIO(bad),values,variables,clauses))
    broken=values[:];broken[-1]=0
    reject('false_last_auxiliary',lambda:old.common.check_cnf_stream(io.BytesIO(cnf),broken,variables,clauses))
    reject('partial_old_size_assignment',lambda:old.common.assignment_values(signed[:58860],variables))
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable inputs')
    report={**provenance(bindings),'status':'INDEPENDENT_TRIANGLE_COMPONENT_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS','variables':variables,'clauses':clauses,'positive24row_Gram_fixtures':positives,'component_equation_positive':linear_result,'synthetic_codec':dict(native=native_result,cnf=cnf_result,research_SAT_witness=False),'fresh_corrupt_controls_rejected':negative,'base_calibration_reused':dict(path=key(OLD_CAL),sha256=OLD_CAL_SHA,corrupt_controls=22),'encoding_gate_sha256':GATE_SHA,'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    model,derived,comp,bindings=bind_inputs();h,g,columns,known,zeros,entries,refs=derived
    values=old.common.assignment_values(read(args.assignment)['assignment'],61296)
    with args.native_output.open('rb') as stream:raw,native_result=old.native.native_values(stream,61296)
    need(values==raw,'all61296native/JSON values agree')
    with (D/'instance.cnf').open('rb') as stream:clause_result=old.common.check_cnf_stream(stream,values,61296,212580)
    c=[row[:] for row in known]
    for e in entries:c[e['row']][e['column']]=int(values[e['id']])
    exact=old.independent.factor_check(c,g,known);linear=component_check(c,comp)
    if args.decoded:need(read(args.decoded)['incidence_matrix']==c,'optional producer matrix equals independent decode')
    save(args.out/'independent_factor.json',dict(incidence_matrix=c,target_gram=g,components=comp,encoding_model_sha256=digest(D/'model.json'),scope_sha256=digest(old.D/'scope.json'),exact_Gram=exact,component_column_totals=linear))
    for path in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(path)]=digest(path)
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable inputs')
    report={**provenance(bindings),'status':'INDEPENDENT_TRIANGLE_COMPONENT_FACTOR_SAT_OBJECT_PASS','native_assignment':native_result,'all_raw_clauses':clause_result,'exact_factor':exact,'exact_components':linear,'independent_factor_sha256':digest(args.out/'independent_factor.json'),'elapsed_seconds':time.monotonic()-start}
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
