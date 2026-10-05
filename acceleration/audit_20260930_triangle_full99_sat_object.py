"""Independent fixed-triangle full99 SAT object checker and calibration.

Shared frozen helpers are disclosed and hash-pinned. No producer is imported.
Conditional scope is reconstructed from its independently checked raw99
propagation artifact; no unrestricted root-label convention is applied.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import io
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import audit_20260930_full99_sat_object as common
import audit_20260930_unrestricted_full99_sat_object as native

ROOT,need,digest,key,read,save = common.ROOT,common.need,common.digest,common.key,common.read,common.save
BASE = ROOT/'acceleration/results/20260930_triangle_full99_cnf'
MODEL,CNF,SCOPE = BASE/'model.json',BASE/'instance.cnf',BASE/'scope.json'
MODEL_SHA='983723dbb211fe02e805046fe2c7a6f5fbb9032eab8afe51edee21dc7b2efb79'
CNF_SHA='4b9c05bb01ac76340c6f72e314c4ee84317facb687e9a32a79094f6fce85d8ea'
SCOPE_SHA='f4096676d89e0df4c356cdd9e4afa26d1465c829dee93c6e33b2cd74f547ea41'
PROP=ROOT/'acceleration/results/20260930_triangle_partial99/wave154.json'
PROP_SHA='e8581587313cf8207799dcf781d8469eb66a699687e023faf0a435000ab9f69b'
PROP_GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_q1_partial99/summary.json'
PROP_GATE_SHA='bad7ddc51101377b8eaa284c650db8adcee5c261a0717073b90fc9e2347d7594'
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_full99_cnf/summary.json'
GATE_SHA='9b47af959088ef3a0eaf9f4e8d00181a5d86ff745f5efade002052cff51302c4'
VARIABLES,CLAUSES,EDGES = 429476,1486729,1927
HELPERS={Path(common.__file__):'65d90a85be5fe67c510e561839901e9b8b7c3b9fc1ab7439af0e6bd3746a380c',
         Path(native.__file__):'6b78545d53041382e9b134718637998e4d0083175640b70044f60f480bcbc200'}


def triangle_scope(model,scope,prop):
    initial,a = prop['initial_adjacency'],prop['final_adjacency']
    for matrix in (initial,a):
        need(len(matrix)==99 and all(len(row)==99 for row in matrix),'99 partial shape')
        need(all(type(matrix[i][j]) is int and matrix[i][j] in (-1,0,1) and matrix[i][j]==matrix[j][i]
                 and (i!=j or matrix[i][j]==0) for i in range(99) for j in range(99)),'partial exact matrix')
    need(scope['initial_adjacency_full99']==initial,'every initial scope entry equals audited propagation input')
    edges=[(u,v) for u,v in combinations(range(99),2) if a[u][v]==-1]
    need(len(edges)==EDGES,'exact1927 residual edges')
    mapping=[dict(u=u,v=v,id=i+1) for i,(u,v) in enumerate(edges)]
    for obj in (model,scope):
        need(obj['known_adjacency_full99']==a,'all9801 final fixed/free entries')
        need(obj['edge_variables']==mapping,'lexicographic residual edge bijection')
        need(obj['propagation_artifact']==key(PROP) and obj['propagation_sha256']==PROP_SHA,'exact propagation identity')
        need(obj['target_automorphism_assumed'] is False and obj['unrestricted_coverage_claim'] is False,'conditional scope without automorphism premise')
    labels=dict(triangle=[0,1,2],A_groups=[list(range(3+12*i,15+12*i)) for i in range(3)],B=list(range(39,99)))
    need(scope['vertex_labels']==labels,'all vertex block labels')
    need(scope['archive_commit']=='85e705cc6c2a14d123120c93a847e30aaab1789e'
         and scope['archive_Q1_path']=='attempts/wave154-triangle-factor-portfolio/exact-results.json'
         and scope['archive_Q1_key']=='second_exact_Q1_representative.Q1','conditional archive factor identity')
    need(scope['forced_steps_count']==len(prop['steps'])==563,'forced-entry count')
    need(model['scope_path']==key(SCOPE) and model['scope_sha256']==SCOPE_SHA,'model scope binding')
    need(model['variables']==VARIABLES and model['clauses']==CLAUSES and model['branch_units']==[],'exact model size/no added branch units')
    return a,edges,dict(partial_matrix_entries_checked=9801,initial_matrix_entries_checked=9801,
        free_edges=EDGES,fixed_present_edges=sum(a[u][v]==1 for u,v in combinations(range(99),2)),
        fixed_absent_edges=sum(a[u][v]==0 for u,v in combinations(range(99),2)),forced_entries=563,
        scope='Only the exact fixed Wave154 triangle/Q1 family',unrestricted_coverage=False)


def authenticated(args):
    bindings={}
    def pin(path,expected=None):
        p=Path(path).resolve();actual=digest(p)
        need(expected is None or actual==expected,'artifact hash '+key(p))
        bindings[key(p)]=actual;return p
    need(args.encoding_audit_sha256==GATE_SHA,'frozen independently approved encoding gate')
    gate=read(pin(args.encoding_audit,GATE_SHA))
    need(gate['status']=='INDEPENDENT_CONDITIONAL_TRIANGLE_FULL99_CNF_ENCODING_PASS','conditional encoding gate status')
    for path,sha in {args.model:MODEL_SHA,args.cnf:CNF_SHA,SCOPE:SCOPE_SHA,PROP:PROP_SHA,PROP_GATE:PROP_GATE_SHA,**HELPERS}.items():pin(path,sha)
    for path in (args.model,args.cnf,SCOPE,PROP,PROP_GATE):
        need(gate['inputs_sha256'][key(path)]==bindings[key(path)],'encoding gate exact input binding')
    propagation=read(PROP_GATE)
    need(propagation['status']=='INDEPENDENT_TRIANGLE_Q1_PARTIAL99_PROPAGATION_PASS'
         and propagation['inputs_sha256'][key(PROP)]==PROP_SHA,'independent propagation gate')
    model,scope,prop=read(args.model),read(SCOPE),read(PROP)
    a,edges,scope_record=triangle_scope(model,scope,prop)
    return model,scope,prop,a,edges,scope_record,bindings,pin


def provenance():
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='/root/state_literature_audit independent fixed-triangle SAT-object checking path',producer_imported=False,
        shared_components=['Frozen independent generic full99 checker: exact integer SRG identity, JSON/assignment/CNF parsing, decoding and six known-SRG fixtures',
                           'Frozen independent unrestricted checker: only strict native DIMACS v-line parsing is reused; its root-label scope and encoding are not applied',
                           'Separately audited immutable triangle propagation and conditional encoding gates'],
        external_review=False,artifact_availability='LOCAL_ONLY')


def codec_controls(out):
    good=b'c SYNTHETIC tiny codec control\ns SATISFIABLE\nv 1 -2\nv 3 0\n'
    vals,tiny=native.native_values(io.BytesIO(good),3)
    need(vals==common.assignment_values([1,-2,3],3),'known native/JSON agreement')
    cases={
        'no_status':good.replace(b's SATISFIABLE\n',b''),'two_statuses':good+b's SATISFIABLE\n',
        'UNSAT':good.replace(b'SATISFIABLE',b'UNSATISFIABLE'),'UNKNOWN':good.replace(b'SATISFIABLE',b'UNKNOWN'),
        'missing_zero':good.replace(b'3 0',b'3'),'data_after_zero':good+b'v 1\n',
        'token_after_zero':good.replace(b'3 0',b'3 0 2'),'duplicate_id':good.replace(b'3 0',b'2 0'),
        'missing_id':good.replace(b'3 0',b'0'),'outside_range':good.replace(b'3 0',b'4 0'),
        'nonnumeric':good.replace(b'3 0',b'x 0'),'bad_protocol':good+b'done\n'}
    rejected=[]
    for name,data in cases.items():
        try:native.native_values(io.BytesIO(data),3)
        except ValueError as exc:rejected.append(dict(case=name,error=str(exc)))
        else:raise ValueError('native corruption accepted: '+name)
    fixture=out/'synthetic_fullsize_native.stdout.gz';raw_hash=hashlib.sha256();raw_bytes=0
    with gzip.open(fixture,'wb',compresslevel=6) as stream:
        def write(data):
            nonlocal raw_bytes
            stream.write(data);raw_hash.update(data);raw_bytes+=len(data)
        write(b'c SYNTHETIC CODEC CONTROL; NOT RESEARCH SOLVER OUTPUT\ns SATISFIABLE\n')
        for first in range(1,VARIABLES+1,512):
            write(('v '+' '.join(str(-i) for i in range(first,min(first+512,VARIABLES+1)))+'\n').encode('ascii'))
        write(b'v 0\n')
    with gzip.open(fixture,'rb') as stream:full_values,full_native=native.native_values(stream,VARIABLES)
    synthetic_json=out/'synthetic_fullsize_assignment.json.gz'
    with gzip.open(synthetic_json,'wt',encoding='ascii') as stream:json.dump(dict(assignment=list(range(-1,-VARIABLES-1,-1))),stream,separators=(',',':'))
    with gzip.open(synthetic_json,'rt',encoding='ascii') as stream:parsed=json.load(stream,object_pairs_hook=common.unique_keys)
    need(common.assignment_values(parsed['assignment'],VARIABLES)==full_values,'all fullsize JSON/native assignments agree')
    class SyntheticCNF:
        def readline(self):return ('p cnf %d %d\n'%(VARIABLES,CLAUSES)).encode('ascii')
        def __iter__(self):
            for i in range(CLAUSES):yield ('-%d 0\n'%(1+i%VARIABLES)).encode('ascii')
    cnf=common.check_cnf_stream(SyntheticCNF(),full_values,VARIABLES,CLAUSES)
    return dict(tiny_native=tiny,corrupt_native_outputs_rejected=rejected,fullsize_native=full_native,fullsize_cnf=cnf,
        complete_json_native_values_compared=VARIABLES,synthetic_native_fixture=key(fixture),synthetic_native_sha256=digest(fixture),
        synthetic_json_fixture=key(synthetic_json),synthetic_json_sha256=digest(synthetic_json),
        native_uncompressed_bytes=raw_bytes,native_uncompressed_sha256=raw_hash.hexdigest(),
        scope='Synthetic codec control only:429476negative IDs and1486729 repeated negative unit clauses. This is not the research CNF, a research SAT assignment, or a target graph.',
        retrieval='Decompress both saved gzip fixtures. Generate the synthetic CNF header and clauses -(1+i mod429476) 0 for i=0..1486728 using this frozen source.')


def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False)
    model,scope,prop,a,edges,scope_record,bindings,pin=authenticated(args)
    generic=common.controls(args.out);codec=codec_controls(args.out)
    graph=common.decode_model(a,edges,bytearray(VARIABLES+1))
    try:common.validate_srg(graph,99,14,1,2)
    except ValueError as exc:zero_rejection=str(exc)
    else:raise ValueError('all-free-zero partial completion accepted as target')
    save(args.out/'scope_valid_free_zero_invalid_target.json',dict(adjacency_full99=graph,scope_valid=True,target_valid=False))
    fields=('known_adjacency_full99','edge_variables','propagation_artifact','propagation_sha256',
            'target_automorphism_assumed','unrestricted_coverage_claim','scope_path','scope_sha256','variables','clauses','branch_units')
    small={k:model[k] for k in fields};rejected=[]
    for name in ('changed_fixed_entry','changed_free_entry','missing_variable','wrong_endpoint','wrong_id','automorphism',
                 'unrestricted_coverage','branch_unit','initial_entry','vertex_label','archive_key','forced_count','propagation_hash'):
        m,s=deepcopy(small),deepcopy(scope)
        if name=='changed_fixed_entry':m['known_adjacency_full99'][0][1]=m['known_adjacency_full99'][1][0]=0
        elif name=='changed_free_entry':u,v=edges[0];m['known_adjacency_full99'][u][v]=m['known_adjacency_full99'][v][u]=0
        elif name=='missing_variable':m['edge_variables'].pop()
        elif name=='wrong_endpoint':m['edge_variables'][0]['v']=98
        elif name=='wrong_id':m['edge_variables'][0]['id']=2
        elif name=='automorphism':m['target_automorphism_assumed']=True
        elif name=='unrestricted_coverage':s['unrestricted_coverage_claim']=True
        elif name=='branch_unit':m['branch_units']=[1]
        elif name=='initial_entry':s['initial_adjacency_full99'][0][1]=0
        elif name=='vertex_label':s['vertex_labels']['triangle']=[0,1,3]
        elif name=='archive_key':s['archive_Q1_key']='another_factor.Q1'
        elif name=='forced_count':s['forced_steps_count']=562
        else:m['propagation_sha256']='0'*64
        try:triangle_scope(m,s,prop)
        except ValueError as exc:rejected.append(dict(case=name,error=str(exc)))
        else:raise ValueError('scope corruption accepted: '+name)
    pin(__file__);pin(ROOT/'uv.lock')
    report=provenance();report.update(status='INDEPENDENT_TRIANGLE_FULL99_SAT_OBJECT_CHECKER_CALIBRATION_PASS',
        inputs_sha256=bindings,generic_controls=generic,codec_controls=codec,scope_check=scope_record,
        scope_corruptions_rejected=rejected,scope_valid_zero_completion_rejected_as_target=zero_rejection,
        solver_launched=False,target_resolution=False,
        statement='The separate fixed-triangle SAT-object checker is calibrated on six known SRGs, exact corrupted objects, complete429476variable synthetic native/JSON assignments,1486729synthetic raw clauses, and the independently gated1927edge partial99 scope.',
        limitations=['No known-valid99target is available as a positive calibration fixture.','Synthetic codec controls are not research SAT evidence.',
                     'Prior independent propagation and encoding proofs are authenticated, not rerun by this object checker.','A positive research result requires a later full decoded99graph to pass every exact check.'])
    need(all(digest(ROOT/p)==sha for p,sha in bindings.items()),'inputs stable')
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))


def check(args):
    started=time.monotonic();args.out.mkdir(parents=True,exist_ok=False)
    model,scope,prop,a,edges,scope_record,bindings,pin=authenticated(args)
    signed=read(pin(args.assignment))['assignment']
    values=common.assignment_values(signed,VARIABLES)
    with pin(args.native_output).open('rb') as stream:native_values,native_record=native.native_values(stream,VARIABLES)
    need(values==native_values,'every native value equals complete JSON assignment')
    with args.cnf.open('rb') as stream:cnf_record=common.check_cnf_stream(stream,values,VARIABLES,CLAUSES)
    graph=common.decode_model(a,edges,values)
    if args.decoded is not None:need(read(pin(args.decoded))['adjacency_full99']==graph,'producer adjacency equals independent decode')
    exact=common.validate_srg(graph,99,14,1,2)
    path=args.out/'independent_adjacency_full99.json'
    save(path,dict(adjacency_full99=graph,exact_identity='A^2=12I-A+2J',independent_result=exact,external_review=False))
    pin(__file__);pin(ROOT/'uv.lock')
    need(all(digest(ROOT/p)==sha for p,sha in bindings.items()),'inputs stable')
    report=provenance();report.update(status='INDEPENDENT_TRIANGLE_TARGET_GRAPH_PASS_PENDING_EXTERNAL_REVIEW',inputs_sha256=bindings,
        native_check=native_record,cnf_check=cnf_record,scope_check=scope_record,graph_check=exact,graph_path=key(path),graph_sha256=digest(path),
        target_resolution=True,elapsed_seconds=time.monotonic()-started,
        statement='The explicit99vertex adjacency satisfies the full target identity exactly and all fixed triangle-family entries. The complete native/JSON assignments agree and satisfy every1486729raw clause of the pinned conditional encoding.',
        limitations=['Internally independently checked candidate positive resolution pending external review. No unrestricted family-coverage claim is required for a concrete validated99vertex target.'])
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],graph_sha256=digest(path),summary_sha256=digest(args.out/'summary.json'))))


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    for name in ('calibrate','sat'):
        p=sub.add_parser(name)
        p.add_argument('--cnf',type=Path,default=CNF);p.add_argument('--model',type=Path,default=MODEL)
        p.add_argument('--encoding-audit',type=Path,default=GATE);p.add_argument('--encoding-audit-sha256',default=GATE_SHA)
        p.add_argument('--out',type=Path,required=True)
        if name=='sat':
            p.add_argument('--assignment',type=Path,required=True);p.add_argument('--native-output',type=Path,required=True)
            p.add_argument('--decoded',type=Path)
    args=parser.parse_args();(calibrate if args.command=='calibrate' else check)(args)


if __name__=='__main__':main()
