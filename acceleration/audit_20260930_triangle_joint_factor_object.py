"""Scope-bound exact incidence-factor and raw SAT assignment checker.

Uses only independently authored scope, integer-factor, DIMACS and native
parsing helpers. No producer or solver imports. A factor is not a target.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_triangle_joint_factor_cnf as independent
import audit_20260930_full99_sat_object as common
import audit_20260930_unrestricted_full99_sat_object as native

ROOT=Path(__file__).resolve().parents[1]
D=independent.D
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_joint_factor_cnf/summary.json'
GATE_SHA='5a6ebade41cf1ab35796ca5d5ce3840c23b624ab06d0ed5a4ff327327ea2b97f'
need,digest,key,read,save=common.need,common.digest,common.key,common.read,common.save
HELPERS={
 'acceleration/audit_20260930_full99_sat_object.py':'65d90a85be5fe67c510e561839901e9b8b7c3b9fc1ab7439af0e6bd3746a380c',
 'acceleration/audit_20260930_unrestricted_full99_sat_object.py':'6b78545d53041382e9b134718637998e4d0083175640b70044f60f480bcbc200',
}

def bind_inputs():
    need(digest(GATE)==GATE_SHA,'frozen encoding audit identity')
    gate=read(GATE)
    need(gate['status']=='INDEPENDENT_TRIANGLE_JOINT_FACTOR_CNF_ENCODING_PASS','independent conditional factor encoding gate')
    bindings={**gate['inputs_sha256'],key(GATE):GATE_SHA,**HELPERS}
    for path,value in bindings.items():need(digest(ROOT/path)==value,'input hash '+path)
    bindings[key(__file__)]=digest(__file__)
    model=read(D/'model.json');scope=read(D/'scope.json')
    derived=independent.scope_check(model,scope)
    return model,scope,derived,bindings

def base_report(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
      verifier='/root/eight_domain_audit independent raw incidence-factor checking path',producer_imports=False,
      shared_components=['Frozen independent raw-core/Gram/scope and literal integer factor checker from joint encoding audit.','Frozen independent generic complete assignment and raw DIMACS checker.','Frozen independently authored native SAT v-line parser.'],
      limitations=['SAT is only a binary36x60 incidence factor, not an SRG or a full99 graph.','No known positive36row factor of the research Gram is available; positive research fixtures have24rows.'],
      target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')

def reject(call,label,records):
    try:call()
    except (ValueError,AssertionError,IndexError,KeyError) as e:records.append(dict(case=label,error=str(e)))
    else:raise ValueError('corrupted control accepted '+label)

def calibrate(args):
    out=args.out;out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    model,scope,derived,bindings=bind_inputs();h,g,edges,known,zeros,entries,refs=derived
    c0=[row[:] for row in known[:12]];g24=[row[:24] for row in g[:24]]
    positives=[];negative=[];samples=[]
    for directory,record in [('wave151-triangle-root-factor','exact_partial_factor'),('wave154-triangle-factor-portfolio','second_exact_Q1_representative')]:
        path=ROOT/'external_conway99_research/attempts'/directory/'exact-results.json'
        need(key(path) in bindings,'archive positive fixture pinned by encoding audit')
        q=read(path)[record]['Q1'];need(sorted(q)==list(range(60)),'raw archived Q1 permutation')
        c=c0+[[int(a in edges[q[d]]) for d in range(60)] for a in range(12)]
        result=independent.factor_check(c,g24,known[:24]);samples.append(c)
        positives.append(dict(path=key(path),Q1_key=record+'.Q1',scope='Exact two-fibre24x60 positive fixture only',result=result))
        bad=deepcopy(c);bad[12][0]^=1
        reject(lambda:independent.factor_check(bad,g24,known[:24]),'single_bit_'+directory,negative)
    synthetic=deepcopy(c0+c0+c0)
    synthetic_g=[[sum(synthetic[a][d]*synthetic[b][d] for d in range(60)) for b in range(36)] for a in range(36)]
    synthetic_result=independent.factor_check(synthetic,synthetic_g)
    save(out/'synthetic_full36_factor.json',dict(incidence_matrix=synthetic,target_gram=synthetic_g,label='Synthetic repeated C0; not a factor of the research Gram'))
    reject(lambda:independent.factor_check(synthetic,g,known),'synthetic_is_not_research_factor',negative)
    for name in ['nonbinary','boolean','short_row','short_matrix','wrong_gram','row_margin','column_margin','margin_preserving_switch']:
        bad=deepcopy(synthetic);badg=deepcopy(synthetic_g)
        if name=='nonbinary':bad[0][0]=2
        elif name=='boolean':bad[0][0]=bool(bad[0][0])
        elif name=='short_row':bad[0].pop()
        elif name=='short_matrix':bad.pop()
        elif name=='wrong_gram':badg[0][24]+=1
        elif name=='row_margin':bad[0][0]^=1
        elif name=='column_margin':
            a=next(d for d,x in enumerate(bad[0]) if x);b=next(d for d,x in enumerate(bad[0]) if not x);bad[0][a]=0;bad[0][b]=1
        else:
            a=next(d for d in range(60) if bad[0][d] and not bad[1][d]);b=next(d for d in range(60) if bad[1][d] and not bad[0][d])
            for row in [0,1]:
                for col in [a,b]:bad[row][col]^=1
            need(all(sum(row)==10 for row in bad) and all(sum(bad[r][d] for r in range(s,s+12))==2 for s in [0,12,24] for d in range(60)),'switch preserves margins')
        reject(lambda:independent.factor_check(bad,badg),name,negative)
    variables=58860;clauses=203748
    signed=list(range(1,variables+1));values=common.assignment_values(signed,variables)
    raw=b'c synthetic codec control; not a research SAT witness\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,signed[i:i+100]))+(' 0' if i+100>=variables else '')+'\n').encode() for i in range(0,variables,100))
    parsed,native_result=native.native_values(io.BytesIO(raw),variables)
    need(parsed==values,'complete fullsize native/JSON agreement')
    with gzip.open(out/'synthetic_58860_native.stdout.txt.gz','wb') as stream:stream.write(raw)
    cnf=b'p cnf 58860 203748\n'+b''.join((str(1+i%variables)+' 0\n').encode() for i in range(clauses))
    with gzip.open(out/'synthetic_203748.cnf.gz','wb') as stream:stream.write(cnf)
    cnf_result=common.check_cnf_stream(io.BytesIO(cnf),values,variables,clauses)
    corrupt=values[:];corrupt[1]=0
    reject(lambda:common.check_cnf_stream(io.BytesIO(cnf),corrupt,variables,clauses),'false_fullsize_clause',negative)
    for name,bad in [('native_missing_status',raw.replace(b's SATISFIABLE\n',b'')),('native_missing_terminator',raw.replace(b'58860 0\n',b'58860\n')),('native_duplicate_id',raw.replace(b'v 1 2 ',b'v 1 1 ',1)),('native_missing_id',raw.replace(b'v 1 2 ',b'v 2 ',1))]:
        reject(lambda:native.native_values(io.BytesIO(bad),variables),name,negative)
    for name,bad in [('missing_assignment',signed[:-1]),('duplicate_assignment',[1]+signed[:-1]),('zero_assignment',[0]+signed[1:])]:
        reject(lambda:common.assignment_values(bad,variables),name,negative)
    for name,bad in [('wrong_header',cnf.replace(b'58860 203748',b'58860 203747',1)),('missing_clause',cnf[:cnf.rfind(b'\n',0,-1)+1]),('wrong_literal',cnf.replace(b'1 0\n',b'-1 0\n',1))]:
        reject(lambda:common.check_cnf_stream(io.BytesIO(bad),values,variables,clauses),name,negative)
    need(all(digest(ROOT/path)==value for path,value in bindings.items()),'unchanged bound inputs')
    report={**base_report(bindings),'status':'INDEPENDENT_TRIANGLE_JOINT_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS','known_positive_research_full36_factor_available':False,
      'positive_research_24row_fixtures':positives,'synthetic_36row_fixture':synthetic_result,'synthetic_codec':dict(variables=variables,clauses=clauses,native=native_result,cnf=cnf_result,research_SAT_witness=False),
      'corrupt_controls_rejected':negative,'encoding_gate_sha256':GATE_SHA,'elapsed_seconds':time.monotonic()-start}
    save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))

def sat(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    model,scope,derived,bindings=bind_inputs();h,g,edges,known,zeros,entries,refs=derived
    need(args.assignment is not None and args.native_output is not None,'complete raw assignment and native output required')
    values=common.assignment_values(read(args.assignment)['assignment'],model['variables'])
    with args.native_output.open('rb') as stream:raw_values,native_result=native.native_values(stream,model['variables'])
    need(values==raw_values,'complete native/JSON assignment agreement')
    with (D/'instance.cnf').open('rb') as stream:clause_result=common.check_cnf_stream(stream,values,model['variables'],model['clauses'])
    c=[row[:] for row in known]
    for e in entries:c[e['row']][e['column']]=int(values[e['id']])
    exact=independent.factor_check(c,g,known)
    if args.decoded:
        decoded=read(args.decoded)
        need(decoded['incidence_matrix']==c,'producer decoded matrix equals independent raw assignment decode')
        need(decoded['encoding_model_sha256']==digest(D/'model.json') and decoded['scope_sha256']==digest(D/'scope.json'),'producer optional decoded artifact scope binding')
    save(args.out/'independent_factor.json',dict(incidence_matrix=c,target_gram=g,encoding_model_sha256=digest(D/'model.json'),scope_sha256=digest(D/'scope.json'),exact_integer_checks=exact))
    for path in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(path)]=digest(path)
    need(all(digest(ROOT/path)==value for path,value in bindings.items()),'unchanged bound artifacts')
    report={**base_report(bindings),'status':'INDEPENDENT_TRIANGLE_JOINT_FACTOR_SAT_OBJECT_PASS','encoding_gate_sha256':GATE_SHA,'all_raw_clauses':clause_result,'native_assignment':native_result,'exact_factor':exact,'independent_factor_sha256':digest(args.out/'independent_factor.json'),'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('calibrate');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('sat');p.add_argument('--out',type=Path,required=True);p.add_argument('--assignment',type=Path,required=True);p.add_argument('--native-output',type=Path,required=True);p.add_argument('--decoded',type=Path)
    args=ap.parse_args()
    try:(calibrate if args.mode=='calibrate' else sat)(args)
    except BaseException as e:
        if args.out.exists() and not (args.out/'failure.json').exists():save(args.out/'failure.json',dict(status='CHECK_FAILED',error=repr(e),timestamp=datetime.now(timezone.utc).isoformat()))
        raise

if __name__=='__main__':main()
