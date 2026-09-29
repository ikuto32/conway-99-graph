"""Independent complete native SAT and raw Q1 projection object checker."""
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
import audit_20260930_triangle_q1_capacity_cnf as independent
import audit_20260930_full99_sat_object as common
import audit_20260930_unrestricted_full99_sat_object as native

ROOT=Path(__file__).resolve().parents[1]
D=independent.D
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_q1_capacity_cnf/summary.json'
GATE_SHA='78db3e5afd4a1a3a0cedc451ac3e36f14ccd3615e15babcd060a1bc1f7a81a22'
need,digest,key,read,save=common.need,common.digest,common.key,common.read,common.save

def inputs():
    need(digest(GATE)==GATE_SHA,'exact encoding gate')
    gate=read(GATE);need(gate['status']=='INDEPENDENT_TRIANGLE_Q1_CAPACITY_CNF_ENCODING_PASS','scope/encoding independent gate')
    bindings={**gate['inputs_sha256'],key(GATE):GATE_SHA,key(__file__):digest(__file__),
      'acceleration/audit_20260930_full99_sat_object.py':'65d90a85be5fe67c510e561839901e9b8b7c3b9fc1ab7439af0e6bd3746a380c',
      'acceleration/audit_20260930_unrestricted_full99_sat_object.py':'6b78545d53041382e9b134718637998e4d0083175640b70044f60f480bcbc200'}
    for path,value in bindings.items():need(digest(ROOT/path)==value,'bound artifact '+path)
    model=read(D/'model.json');scope=read(D/'scope.json');derived=independent.scope_check(model,scope)
    return model,scope,derived,bindings

def validate(c,g,known,components,columns):
    literal=independent.base.factor_check(c,g,known)
    totals=independent.capacity_check(c,components)
    q=independent.extract_q1(c,columns)
    return dict(exact_integer_factor=literal,capacity_totals=totals,Q1=q)

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit independent raw24 projection checking path',producer_imports=False,
      shared_components=['Frozen independent projection rawscope and capacity/Q1 extraction helpers.','Frozen independent literal binary-factor/Gram/margins checker.','Frozen independent complete assignment, native SAT output and raw CNF parser.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',
      limitations=['A SAT24row object need not extend to C2, a36rowfactor or a99vertex target.','Synthetic positive controls have their own explicitly different Gram; no positive research projection is assumed.'])

def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,scope,derived,bindings=inputs();g,columns,known,entries,refs,components=derived
    rejected=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,IndexError,KeyError):rejected.append(label)
        else:raise ValueError('corrupt control accepted '+label)
    archived=[]
    for directory,field in [('wave151-triangle-root-factor','exact_partial_factor'),('wave154-triangle-factor-portfolio','second_exact_Q1_representative')]:
        path=ROOT/'external_conway99_research/attempts'/directory/'exact-results.json';need(key(path) in bindings,'pinned archive fixture')
        q=read(path)[field]['Q1'];c=[r[:] for r in known[:12]]+[[int(a in columns[q[d]]) for d in range(60)] for a in range(12)]
        gram=independent.base.factor_check(c,g,known);need(independent.extract_q1(c,columns)==q,'archived raw Q1 roundtrip')
        reject('archived_capacity_'+directory,lambda:independent.capacity_check(c,components));archived.append(dict(source=key(path),exact_Gram=gram,expected_projection_rejection=True))
    groups=[[r for r in group if r<12] for group in components];pi={}
    for f in range(3):
        for position,a in enumerate(groups[f]):pi[a]=groups[(f+1)%3][position]
    synthetic=[r[:] for r in known[:12]]+[[int(a in (pi[e[0]],pi[e[1]])) for e in columns] for a in range(12)]
    synthetic_g=[[sum(synthetic[a][d]*synthetic[b][d] for d in range(60)) for b in range(24)] for a in range(24)]
    positive=validate(synthetic,synthetic_g,None,components,columns)
    save(args.out/'synthetic_positive_factor.json',dict(incidence_matrix=synthetic,target_gram=synthetic_g,components=components,Q1=positive['Q1'],label='Complete synthetic24row object against its own Gram; not the research Gram'))
    reject('synthetic_wrong_research_Gram',lambda:validate(synthetic,g,known,components,columns))
    for label in ['nonbinary','boolean','short_row','bit_flip','duplicate_C1_column']:
        bad=[r[:] for r in synthetic]
        if label=='nonbinary':bad[12][0]=2
        elif label=='boolean':bad[12][0]=bool(bad[12][0])
        elif label=='short_row':bad[12].pop()
        elif label=='bit_flip':bad[12][0]^=1
        else:
            for r in range(12,24):bad[r][1]=bad[r][0]
        reject(label,lambda:validate(bad,synthetic_g,None,components,columns))
    bad=[r[:] for r in synthetic]
    for r in [r for r in components[0] if r<24][:3]:bad[r][0]=1
    reject('three_in_component',lambda:independent.capacity_check(bad,components))
    variables,clauses=19686,68328;signed=list(range(1,variables+1));values=common.assignment_values(signed,variables)
    raw=b'c synthetic codec; not a research SAT witness\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,signed[i:i+100]))+(' 0' if i+100>=variables else '')+'\n').encode() for i in range(0,variables,100))
    parsed,native_result=native.native_values(io.BytesIO(raw),variables);need(parsed==values,'complete19686native/JSON agreement')
    cnf=b'p cnf 19686 68328\n'+b''.join((str(i%variables+1)+' 0\n').encode() for i in range(clauses));cnf_result=common.check_cnf_stream(io.BytesIO(cnf),values,variables,clauses)
    with gzip.open(args.out/'synthetic_native.stdout.txt.gz','wb') as f:f.write(raw)
    with gzip.open(args.out/'synthetic_fullsize.cnf.gz','wb') as f:f.write(cnf)
    for label,bad in [('missing_status',raw.replace(b's SATISFIABLE\n',b'')),('missing_final0',raw.replace(b'19686 0\n',b'19686\n')),('duplicate_id',raw.replace(b'v 1 2 ',b'v 1 1 ',1)),('missing_id',raw.replace(b'v 1 2 ',b'v 2 ',1))]:reject(label,lambda:native.native_values(io.BytesIO(bad),variables))
    for label,bad in [('wrong_header',cnf.replace(b'19686 68328',b'19686 68327',1)),('missing_clause',cnf[:cnf.rfind(b'\n',0,-1)+1]),('false_clause',cnf.replace(b'1 0\n',b'-1 0\n',1))]:reject(label,lambda:common.check_cnf_stream(io.BytesIO(bad),values,variables,clauses))
    reject('partial_assignment',lambda:common.assignment_values(signed[:-1],variables))
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable artifacts')
    report={**provenance(bindings),'status':'INDEPENDENT_TRIANGLE_Q1_CAPACITY_OBJECT_CHECKER_CALIBRATION_PASS','variables':variables,'clauses':clauses,'archived_positive_Gram_negative_capacity_controls':archived,'synthetic_positive':positive,'synthetic_codec':dict(native=native_result,cnf=cnf_result,research_SAT_witness=False),'corrupted_controls_rejected':rejected,'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,scope,derived,bindings=inputs();g,columns,known,entries,refs,components=derived
    values=common.assignment_values(read(args.assignment)['assignment'],19686)
    with args.native_output.open('rb') as stream:raw,native_result=native.native_values(stream,19686)
    need(values==raw,'all native/JSON values agree')
    with (D/'instance.cnf').open('rb') as stream:clause_result=common.check_cnf_stream(stream,values,19686,68328)
    c=[r[:] for r in known]
    for e in entries:c[e['row']][e['column']]=int(values[e['id']])
    result=validate(c,g,known,components,columns)
    if args.decoded:
        decoded=read(args.decoded);need(decoded['incidence_matrix']==c and decoded['Q1']==result['Q1'],'optional producer matrix/Q1 raw equality')
    save(args.out/'independent_factor.json',dict(incidence_matrix=c,target_gram=g,Q1=result['Q1'],components=components,exact_checks=result,encoding_model_sha256=digest(D/'model.json'),scope_sha256=digest(D/'scope.json'),is_complete36row_factor=False,is_full99_graph=False))
    for path in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(path)]=digest(path)
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable bound artifacts')
    report={**provenance(bindings),'status':'INDEPENDENT_TRIANGLE_Q1_CAPACITY_SAT_OBJECT_PASS','native_assignment':native_result,'all_raw_clauses':clause_result,'exact_object':result,'independent_factor_sha256':digest(args.out/'independent_factor.json'),'elapsed_seconds':time.monotonic()-start}
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
