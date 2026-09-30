"""Independent complete SAT assignment and fixed-core factor checker."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import gzip
import io
import json
import platform
import subprocess
import sys
import audit_20260930_variable_core_factor_object as base
import audit_20260930_connected_fixed_core_cnf as extension

ROOT=extension.ROOT
GATE=ROOT/'acceleration/results/20260930_independent_review/connected_fixed_core_cnf/summary.json'
GATE_SHA='3ab0a89b8ab4f7043b0bca8d3c66bdb6cbfc7b52a5f4e949de2602feabcf7d3b'
BASE_CALIBRATION=ROOT/'acceleration/results/20260930_independent_review/variable_core_factor_object_calibration/summary.json'
BASE_CALIBRATION_SHA='7577bbb79dfa5b334badc71cac820364d169edfe11f0eeaccd7eedbca9b1d40a'
BASE_SOURCE_SHA='8146a2d1c3eedd9d623ee5074b96b0657da5d2786f1f556898c720352165ee82'
FIXTURE=ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json'
need,read,save,digest,key=extension.need,extension.read,extension.save,extension.digest,extension.key
common,native=base.common,base.native

def bind():
    need(digest(GATE)==GATE_SHA and read(GATE)['status']=='INDEPENDENT_CONNECTED_FIXED_CORE_CNF_BATCH_PASS','fixed encoding gate')
    need(digest(BASE_CALIBRATION)==BASE_CALIBRATION_SHA and
         read(BASE_CALIBRATION)['status']=='INDEPENDENT_VARIABLE_CORE_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS','base calibration')
    need(digest(base.__file__)==BASE_SOURCE_SHA,'frozen independent base raw checker')
    model,scope,primary,bindings=base.bind_inputs()
    batch,_,extension_inputs=extension.bind_inputs()
    bindings.update(extension_inputs);bindings.update(read(GATE)['inputs_sha256'])
    for p in [Path(__file__),Path(base.__file__),Path(extension.__file__),GATE,BASE_CALIBRATION,
              ROOT/'docs/AUDIT_20260930_CONNECTED_FIXED_CORE_OBJECT.md',FIXTURE]:bindings[key(p)]=digest(p)
    for path,h in bindings.items():need(digest(ROOT/path)==h,'bound artifact '+path)
    return model,scope,primary,batch,bindings

def core_values(values,model,core):
    for r in model['matching_variables']:
        a,b=r['endpoints'];need(values[r['id']]==int(core['M'+str(r['fibre'])][a]==b),'every fixed matching variable')
    for r in model['permutation_variables']:
        need(values[r['id']]==int(core['P'][r['row']]==r['column']),'every fixed permutation variable')
    return dict(matching_entries=132,permutation_entries=144)

def raw_core_equal(raw,core):
    need(raw['core_adjacency']==core['core_adjacency'],'decoded exact selected core')
    for g in (1,2):need(raw[f'M{g}']==[[int(core[f'M{g}'][a]==b) for b in range(12)] for a in range(12)],'decoded matching equality')
    need(raw['P']==[[int(a==b) for b in range(12)] for a in range(12)],'decoded P equality')

def native_bytes(signed):
    return b'c SYNTHETIC full-size codec control; NOT research SAT\ns SATISFIABLE\n'+b''.join(
        ('v '+' '.join(map(str,signed[i:i+100]))+(' 0' if i+100>=len(signed) else '')+'\n').encode()
        for i in range(0,len(signed),100))

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
        verifier='/root/state_literature_audit',method='independent_artifact_check',producer_imports=False,
        artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False,
        shared_components=['Frozen independently authored native/JSON and complete CNF parsers.',
                           'Frozen independently authored variable-core decoder and literal integer Gram/margin/cap/partial99 checker.',
                           'Separate fixed-core raw-entry and complete positive-unit extension checks.'],
        limitations=['An accepted 36x60 factor and partial99 graph still require residual D; this is not a complete target graph.',
                     'The four selected connected cores are restrictions, not exhaustive target coverage.',
                     'No target automorphism or target asymmetry is assumed.'])

def calibrate(args):
    model,scope,primary,batch,bindings=bind();negative=[];positive=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):negative.append(name)
        else:raise ValueError('corrupt control accepted '+name)
    fixture=read(FIXTURE);qs=fixture['internal_matchings'];p=fixture['cross12'];n=len(p)
    m1=[[int(qs[1][a]==b) for b in range(n)] for a in range(n)]
    m2=[[int(qs[2][a]==b) for b in range(n)] for a in range(n)]
    pm=[[int(p[a]==b) for b in range(n)] for a in range(n)]
    checked=base.raw_factor(m1,m2,pm,fixture['factor60x180'],research=False)
    need(checked['core_adjacency']==fixture['cubic_core60'],'known nonempty243 raw core')
    save(args.out/'known243_positive.json',dict(exact_checks=checked['exact_checks'],label='Known SRG243 necessary-factor positive, not research99'))
    for label in ('Boolean_entry','changed_C0','changed_F1'):
        f=deepcopy(fixture['factor60x180'])
        if label=='Boolean_entry':f[20][0]=bool(f[20][0])
        elif label=='changed_C0':f[0][0]^=1
        else:f[20][0]^=1
        reject(label,lambda f=f:base.raw_factor(m1,m2,pm,f,research=False))
    f=deepcopy(fixture['factor60x180'])
    for row in f[20:40]:row[0],row[1]=row[1],row[0]
    reject('domain_valid_but_wrong_Gram',lambda:base.raw_factor(m1,m2,pm,f,research=False))
    reject('243_not_research99',lambda:base.raw_factor(m1,m2,pm,fixture['factor60x180']))
    m=[[0,1],[1,0]];identity=[[1,0],[0,1]]
    rook=base.raw_factor(m,m,identity,[[] for _ in range(6)],research=False)
    base.raw_math.srg_check(rook['partial_adjacency_full99'],4)
    for r in batch['records']:
        core=read(ROOT/r['core_path']);rows=extension.expected_rows(core);signed=list(range(1,110905))
        for item in model['matching_variables']:
            a,b=item['endpoints'];v=item['id'];signed[v-1]=v if core[f"M{item['fibre']}"][a]==b else -v
        for item in model['permutation_variables']:
            v=item['id'];signed[v-1]=v if item['row']==item['column'] else -v
        values=common.assignment_values(signed,110904);core_values(values,model,core)
        native_raw=native_bytes(signed);parsed,nativerec=native.native_values(io.BytesIO(native_raw),110904)
        need(parsed==values,'complete native assignment codec')
        cnf=(b'p cnf 110904 518184\n'+b''.join(f'{signed[i%110904]} 0\n'.encode() for i in range(518160))+
             b''.join(f"{row['literal']} 0\n".encode() for row in rows))
        cnfrec=common.check_cnf_stream(io.BytesIO(cnf),values,110904,518184)
        for label,blob in [('native',native_raw),('cnf',cnf)]:
            with gzip.open(args.out/f"synthetic_core_{r['core_index']:02d}.{label}.gz",'wb') as stream:stream.write(blob)
        positive.append(dict(core_index=r['core_index'],native=nativerec,cnf=cnfrec,research_SAT_witness=False,
                             exact_true_fixing_units=[row['literal'] for row in rows]))
        raw=dict(core_adjacency=core['core_adjacency'],M1=[[int(core['M1'][a]==b) for b in range(12)] for a in range(12)],
                 M2=[[int(core['M2'][a]==b) for b in range(12)] for a in range(12)],P=[[int(a==b) for b in range(12)] for a in range(12)])
        raw_core_equal(raw,core)
        bad=deepcopy(raw);bad['core_adjacency'][0][1]^=1
        reject(f"wrong_raw_core_{r['core_index']}",lambda:raw_core_equal(bad,core))
        wrong=values[:];wrong[rows[0]['literal']]=0
        reject(f"false_fixing_bit_{r['core_index']}",lambda:core_values(wrong,model,core))
        false_clause=cnf[:cnf.rfind(b'\n',0,-1)+1]+b'-1716 0\n'
        reject(f"false_actual_last_unit_{r['core_index']}",lambda:common.check_cnf_stream(io.BytesIO(false_clause),values,110904,518184))
    for name,bad in [('missing_status',native_raw.replace(b's SATISFIABLE\n',b'')),
                     ('missing_terminator',native_raw.replace(b'110904 0\n',b'110904\n')),
                     ('duplicate_ID',native_raw.replace(b'v 1 2 ',b'v 1 1 ',1)),
                     ('missing_ID',native_raw.replace(b'v 1 2 ',b'v 2 ',1)),
                     ('contradictory_status',native_raw+b's UNSATISFIABLE\n')]:
        reject(name,lambda bad=bad:native.native_values(io.BytesIO(bad),110904))
    reject('partial_JSON_assignment',lambda:common.assignment_values(signed[:-1],110904))
    reject('duplicate_JSON_assignment',lambda:common.assignment_values(signed+[signed[-1]],110904))
    reject('wrong_augmented_header',lambda:common.check_cnf_stream(io.BytesIO(cnf.replace(b'518184',b'518160',1)),values,110904,518184))
    reject('missing_actual_clause',lambda:common.check_cnf_stream(io.BytesIO(cnf[:-7]),values,110904,518184))
    report={**provenance(bindings), 'status':'INDEPENDENT_CONNECTED_FIXED_CORE_OBJECT_CHECKER_CALIBRATION_PASS',
        'variables':110904,'clauses':518184,'encoding_gate_sha256':GATE_SHA,
        'known243_positive':checked['exact_checks'],'known_rook9_positive':rook['exact_checks'],
        'synthetic_fullsize_per_core':positive,'corruptions_rejected':negative,
        'positive_research_factor':None,'positive_research_factor_null_reason':'No verified factor for any of these four research cores is available; known243 and rook9 are separately parameterized positives, synthetic CNFs exercise codecs only.',
        'outputs_sha256':{key(p):digest(p) for p in args.out.iterdir() if p.is_file()}}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    model,scope,primary,batch,bindings=bind();r=batch['records'][args.core_index];core=read(ROOT/r['core_path'])
    values=common.assignment_values(read(args.assignment)['assignment'],110904)
    with args.native_output.open('rb') as stream:nativevalues,nativerec=native.native_values(stream,110904)
    need(values==nativevalues,'every native and parsed signed assignment value')
    with (ROOT/r['cnf_path']).open('rb') as stream:cnfrec=common.check_cnf_stream(stream,values,110904,518184)
    fixed=core_values(values,model,core);raw=base.decode(values,primary);raw_core_equal(raw,core)
    if args.decoded:
        produced=read(args.decoded)
        for field in ['M1','M2','P','core_adjacency','incidence_matrix','prescribed_gram','partial_adjacency_full99']:
            need(produced[field]==raw[field],'independent raw decode equals supplied '+field)
        need(produced['full99_graph'] is False,'partial graph boundary')
    save(args.out/'independent_factor_and_partial99.json',{**raw,'full99_graph':False,'fixed_core_index':args.core_index})
    for p in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(p)]=digest(p)
    report={**provenance(bindings),'status':'INDEPENDENT_CONNECTED_FIXED_CORE_FACTOR_SAT_OBJECT_PASS',
        'core_index':args.core_index,'fixed_core_values':fixed,'native_assignment':nativerec,'all_raw_clauses':cnfrec,
        'raw_exact_checks':raw['exact_checks'],'independent_raw_sha256':digest(args.out/'independent_factor_and_partial99.json')}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('calibrate');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('sat');p.add_argument('--out',type=Path,required=True);p.add_argument('--core-index',type=int,choices=range(4),required=True)
    p.add_argument('--assignment',type=Path,required=True);p.add_argument('--native-output',type=Path,required=True);p.add_argument('--decoded',type=Path)
    args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    try:(calibrate if args.mode=='calibrate' else sat)(args)
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
