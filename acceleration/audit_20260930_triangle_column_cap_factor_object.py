"""Independent complete SAT codec and raw36 factor with target column caps."""
import argparse
from datetime import datetime,timezone
import gzip
import io
from itertools import combinations
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
import audit_20260930_triangle_component_factor_object as old
import audit_20260930_triangle_factor_column_caps as encoding

ROOT=Path(__file__).resolve().parents[1]
need,digest,key,read,save=old.need,old.digest,old.key,old.read,old.save
D=encoding.D
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_factor_column_caps/summary.json'
GATE_SHA='675dae8635175088bff026c59e171c1d2b2b66a4a880cd6a10500ae66bb74331'
OLD_CAL=ROOT/'acceleration/results/20260930_independent_review/triangle_component_factor_object_calibration/summary.json'
OLD_CAL_SHA='5c6250b7282f8c513355e523c15c106f4a13f4cc78bc2c1b621a1394b5a351db'

def bind_inputs():
    _,derived,comp,bindings=old.bind_inputs()
    need(digest(GATE)==GATE_SHA and digest(OLD_CAL)==OLD_CAL_SHA,'exact semantic/calibration gates')
    gate=read(GATE);cal=read(OLD_CAL)
    need(gate['status']=='INDEPENDENT_TRIANGLE_COLUMN_CAP_FACTOR_CNF_ENCODING_PASS','new complete encoding gate')
    need(cal['status']=='INDEPENDENT_TRIANGLE_COMPONENT_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS','prior exact raw-factor calibration')
    bindings.update(gate['inputs_sha256']);bindings.update(cal['inputs_sha256'])
    bindings.update({key(GATE):GATE_SHA,key(OLD_CAL):OLD_CAL_SHA,key(__file__):digest(__file__),key(encoding.__file__):digest(encoding.__file__)})
    for p,value in bindings.items():need(digest(ROOT/p)==value,'exact input/source '+p)
    model=read(D/'model.json');scope=read(D/'scope.json');h,g,columns,known,zeros,entries,refs=derived
    encoding.scope_check(scope,read(encoding.premise.base.D/'scope.json'),comp)
    need(model['known_incidence_rows']==known and model['target_gram_rows']==g and model['entry_variables']==entries,'unchanged complete primary scope')
    need(model['variables']==61296 and model['clauses']==256320,'new exact dimensions')
    return model,derived,comp,bindings

def column_check(c):
    need(len(c)==36 and all(len(row)==60 and all(type(x) is int and x in (0,1) for x in row) for row in c),'literal binary36x60 column-cap input')
    counts=[]
    for d,e in combinations(range(60),2):
        q=sum(c[r][d]*c[r][e] for r in range(36))
        need(q<=2,'raw column cap '+str((d,e,q)));counts.append(q)
    return dict(column_pairs_checked=1770,overlap_histogram={str(i):counts.count(i) for i in range(3)},maximum_overlap=max(counts))

def raw_check(c,derived,comp):
    h,g,columns,known,zeros,entries,refs=derived
    return dict(exact_Gram=old.old.independent.factor_check(c,g,known),exact_components=old.component_check(c,comp),exact_column_caps=column_check(c))

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
      verifier='/root/eight_domain_audit independent raw full-factor checker',producer_imports=False,
      shared_components=['Pinned independent factor/Gram, component-equation, native-output, JSON assignment and complete CNF parsers reused.','New literal full36 column-pair implementation, scope binding and fresh controls.'],
      target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',limitations=['SAT supplies a36x60 incidence factor with necessary column caps, not a99vertex graph.','Residual outside adjacency D and mixed core/outside pair equations are absent.'])

def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    model,derived,comp,bindings=bind_inputs();h,g,columns,known,zeros,entries,refs=derived
    positives=[]
    for dirname,record in [('wave151-triangle-root-factor','exact_partial_factor'),('wave154-triangle-factor-portfolio','second_exact_Q1_representative')]:
        q=read(ROOT/'external_conway99_research/attempts'/dirname/'exact-results.json')[record]['Q1']
        c=[r[:] for r in known[:12]]+[[int(a in columns[q[d]]) for d in range(60)] for a in range(12)]
        positives.append(old.old.independent.factor_check(c,[row[:24] for row in g[:24]],known[:24]))
    # A separately labelled literal column-cap positive. It is not a research Gram factor.
    rng=random.Random(9001);supports=[];attempts=0
    while len(supports)<60:
        candidate=set(rng.sample(range(36),6));attempts+=1
        need(attempts<=100000,'bounded synthetic column control generation')
        if all(len(candidate&prior)<=2 for prior in supports):supports.append(candidate)
    positive=[[int(r in support) for support in supports] for r in range(36)]
    cap_positive=column_check(positive)
    save(args.out/'synthetic_column_cap_positive.json',dict(incidence_matrix=positive,label='Only a literal full-shape column-cap control; no Gram, margin, component or research-SAT claim',seed=9001,attempts=attempts))
    negative=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):negative.append(label)
        else:raise ValueError('corrupt control accepted '+label)
    repeated=[row[:] for row in positive]
    for r in range(36):repeated[r][1]=repeated[r][0]
    reject('duplicate_column_overlap6',lambda:column_check(repeated))
    isolated=[[0]*60 for _ in range(36)]
    for r in range(3):isolated[r][0]=isolated[r][1]=1
    reject('isolated_column_overlap3',lambda:column_check(isolated))
    boolean=[row[:] for row in positive];boolean[0][0]=bool(boolean[0][0])
    reject('Boolean_entry_not_literal_integer',lambda:column_check(boolean))
    reject('partial25_not_full36',lambda:column_check(positive[:25]))
    # Existing exact Gram conditions alone need not imply the new cap.
    repeated_fibres=[row[:] for _ in range(3) for row in known[:12]]
    own_g=[[sum(x*y for x,y in zip(a,b)) for b in repeated_fibres] for a in repeated_fibres]
    separate_factor=old.old.independent.factor_check(repeated_fibres,own_g)
    reject('synthetic_Gram_factor_fails_new_column_cap',lambda:column_check(repeated_fibres))
    variables,clauses=61296,256320;signed=list(range(1,variables+1));values=old.old.common.assignment_values(signed,variables)
    raw=b'c synthetic full-size codec, not research SAT\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,signed[i:i+100]))+(' 0' if i+100>=variables else '')+'\n').encode() for i in range(0,variables,100))
    native,native_result=old.old.native.native_values(io.BytesIO(raw),variables);need(native==values,'complete native/JSON codec')
    cnf=b'p cnf 61296 256320\n'+b''.join((str(i%variables+1)+' 0\n').encode() for i in range(clauses))
    cnf_result=old.old.common.check_cnf_stream(io.BytesIO(cnf),values,variables,clauses)
    with gzip.open(args.out/'synthetic_fullsize_native.txt.gz','wb') as stream:stream.write(raw)
    with gzip.open(args.out/'synthetic_fullsize.cnf.gz','wb') as stream:stream.write(cnf)
    for label,bad in [('missing_native_status',raw.replace(b's SATISFIABLE\n',b'')),('missing_native_terminator',raw.replace(b'61296 0\n',b'61296\n')),('duplicate_native_id',raw.replace(b'v 1 2 ',b'v 1 1 ',1)),('missing_native_id',raw.replace(b'v 1 2 ',b'v 2 ',1))]:reject(label,lambda:old.old.native.native_values(io.BytesIO(bad),variables))
    for label,bad in [('old_clause_count',cnf.replace(b'61296 256320',b'61296 212580',1)),('missing_last_clause',cnf[:cnf.rfind(b'\n',0,-1)+1]),('false_clause_sign',cnf.replace(b'1 0\n',b'-1 0\n',1))]:reject(label,lambda:old.old.common.check_cnf_stream(io.BytesIO(bad),values,variables,clauses))
    broken=values[:];broken[-1]=0;reject('false_auxiliary_value',lambda:old.old.common.check_cnf_stream(io.BytesIO(cnf),broken,variables,clauses))
    reject('partial_assignment',lambda:old.old.common.assignment_values(signed[:-1],variables))
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable artifacts')
    report={**provenance(bindings),'status':'INDEPENDENT_TRIANGLE_COLUMN_CAP_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS','variables':variables,'clauses':clauses,
      'positive24row_Gram_fixtures':positives,'positive_column_cap_fixture':cap_positive,'separate_synthetic36_Gram_positive':separate_factor,
      'combined_positive_research_factor':None,'combined_positive_research_factor_null_reason':'No verified complete36row factor of this research Gram is presently available; Gram, component, cap and complete-codec paths have separately labelled positive controls.',
      'synthetic_codec':dict(native=native_result,cnf=cnf_result,research_SAT_witness=False),'fresh_corrupt_controls_rejected':negative,'prior_component_calibration':dict(path=key(OLD_CAL),sha256=OLD_CAL_SHA),'encoding_gate_sha256':GATE_SHA,'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,derived,comp,bindings=bind_inputs()
    h,g,columns,known,zeros,entries,refs=derived
    values=old.old.common.assignment_values(read(args.assignment)['assignment'],61296)
    with args.native_output.open('rb') as stream:native,native_result=old.old.native.native_values(stream,61296)
    need(values==native,'complete native and parsed assignment agreement')
    with (D/'instance.cnf').open('rb') as stream:cnf_result=old.old.common.check_cnf_stream(stream,values,61296,256320)
    c=[row[:] for row in known]
    for e in entries:c[e['row']][e['column']]=int(values[e['id']])
    exact=raw_check(c,derived,comp)
    if args.decoded:need(read(args.decoded)['incidence_matrix']==c,'producer decode agrees with independently reconstructed incidence')
    save(args.out/'independent_factor.json',dict(incidence_matrix=c,target_gram=g,components=comp,exact_checks=exact,encoding_model_sha256=digest(D/'model.json'),scope_sha256=digest(D/'scope.json'),is_full99_graph=False))
    for p in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(p)]=digest(p)
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable artifacts')
    report={**provenance(bindings),'status':'INDEPENDENT_TRIANGLE_COLUMN_CAP_FACTOR_SAT_OBJECT_PASS','native_assignment':native_result,'all_raw_clauses':cnf_result,**exact,'independent_factor_sha256':digest(args.out/'independent_factor.json'),'elapsed_seconds':time.monotonic()-start}
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
