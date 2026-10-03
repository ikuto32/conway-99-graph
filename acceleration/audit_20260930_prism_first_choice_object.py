"""Independent augmented SAT assignment, sole-unit and raw six-prism object check."""
from datetime import datetime,timezone
import argparse
import gzip
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_prism_all_columns_object as base
import audit_20260930_prism_first_choice_normalization as normalization

ROOT=base.ROOT;D=normalization.D
GATE=ROOT/'acceleration/results/20260930_independent_review/prism_first_choice_normalization/summary.json'
GATE_SHA='c5963305cff69ef0242db04d373fdf7cba1339e547191554b64b319165bf8223'
CAL=ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_object_calibration/summary.json'
CAL_SHA='433816d402860b3f1a0cda328a9930952077c113ef1b4c50af097529ed5a9078'
BASE_SOURCE_SHA='5cf39e8b8b2de2aa0439d478db19d242dacf6c9ffcbc4e2a957ab974ad19f0e2'
need,digest,key,read,save=base.need,base.digest,base.key,base.read,base.save

def bind_inputs():
    need(digest(base.__file__)==BASE_SOURCE_SHA,'frozen independent object source')
    model,derived,bindings=base.bind_inputs()
    for p,sha,status in[(GATE,GATE_SHA,'INDEPENDENT_SIX_PRISM_FIRST_CHOICE_NORMALIZATION_PASS'),(CAL,CAL_SHA,'INDEPENDENT_SIX_PRISM_ALL_COLUMNS_OBJECT_CHECKER_CALIBRATION_PASS')]:
        need(digest(p)==sha,'frozen gate hash');gate=read(p);need(gate['status']==status,'gate status')
        bindings.update(gate['inputs_sha256']);bindings[key(p)]=sha
    bindings[key(__file__)]=digest(__file__);bindings[key(normalization.__file__)]=digest(normalization.__file__)
    for p,sha in bindings.items():need(digest(ROOT/p)==sha,'exact input '+p)
    normalization.recipe_check(read(D/'model.json'))
    normalization.byte_check((base.D/'instance.cnf').read_bytes(),(D/'instance.cnf').read_bytes())
    return model,derived,bindings

def decode(values,grouped):
    need(values[1]==1,'positive normalized literal1')
    factor=[[0]*60 for _ in range(36)];selected=[]
    for d,choices in enumerate(grouped):
        yes=[c for c in choices if values[c['id']]];need(len(yes)==1,'exact one choice in every column')
        selected.append(yes[0]['id'])
        for r in yes[0]['rows']:factor[r][d]=1
    need(selected[0]==1,'raw chosen first support')
    return factor,selected

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
      verifier='/root/state_literature_audit independent augmented-object wrapper',shared_components=['Frozen independent base raw36factor, native/JSON and complete-CNF checkers.','New exact normalization gate/augmented-byte/positive-unit scope and controls.'],producer_imports=False,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',limitations=['A valid abstract six-prism factor is not a target graph.','Distinct-column caps are diagnostic, not encoded; residual D remains absent.','No positive complete research factor is available as a calibration fixture.'])

def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,derived,bindings=bind_inputs();core,g,columns,c0,components,grouped=derived
    f=base.balanced_control(columns);own_g=[[sum(x*y for x,y in zip(a,b))for b in f]for a in f]
    own=base.raw_check(f,own_g,c0,components)
    chosen=[next(c['id']for c in choices if c['rows']==[r for r in range(36)if f[r][d]])for d,choices in enumerate(grouped)]
    synthetic_signed=[i if i in set(chosen)else-i for i in range(1,245881)]
    primary_values=base.common.assignment_values(synthetic_signed,245880)
    decoded,selection=decode(primary_values,grouped);need(decoded==f and selection==chosen,'positive normalized synthetic raw primary codec')
    need(own_g!=g,'synthetic own Gram is not research Gram')
    positive=list(range(1,245881));values=base.common.assignment_values(positive,245880)
    stdout=b'c SYNTHETIC full-size codec; not research SAT\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,positive[i:i+100]))+(' 0'if i+100>=245880 else'')+'\n').encode()for i in range(0,245880,100))
    parsed,nativeres=base.native.native_values(io.BytesIO(stdout),245880);need(parsed==values,'complete native codec')
    cnf=b'p cnf 245880 874801\n'+b''.join((str(2+i%245879)+' 0\n').encode()for i in range(874800))+b'1 0\n'
    cnfres=base.common.check_cnf_stream(io.BytesIO(cnf),values,245880,874801)
    for name,data in [('synthetic_native.stdout.gz',stdout),('synthetic_augmented.cnf.gz',cnf)]:
        with gzip.open(args.out/name,'wb')as stream:stream.write(data)
    save(args.out/'synthetic_normalized_raw_control.json',dict(factor=f,own_gram=own_g,selected_choice_ids=chosen,label='Generic normalized positive with its own Gram; not a research SAT assignment or prescribed factor.'))
    rejected=[]
    def reject(label,fn):
        try:fn()
        except(ValueError,KeyError,IndexError):rejected.append(label)
        else:raise ValueError('corrupted control accepted '+label)
    bad=values[:];bad[1]=0
    reject('sole_final_unit_false',lambda:base.common.check_cnf_stream(io.BytesIO(cnf),bad,245880,874801))
    reject('raw_first_choice_false',lambda:decode(bad,grouped))
    reject('missing_assignment',lambda:base.common.assignment_values(positive[:-1],245880))
    reject('duplicate_assignment',lambda:base.common.assignment_values([1]+positive[:-1],245880))
    for label,data in [('missing_final_unit',cnf[:-4]),('negative_final_unit',cnf[:-4]+b'-1 0\n'),('old_header',cnf.replace(b'874801',b'874800',1))]:reject(label,lambda:base.common.check_cnf_stream(io.BytesIO(data),values,245880,874801))
    for label,data in [('missing_native_terminator',stdout.replace(b'245880 0\n',b'245880\n')),('duplicate_native_id',stdout.replace(b'v 1 2 ',b'v 1 1 ',1)),('wrong_native_status',stdout.replace(b's SATISFIABLE',b's UNSATISFIABLE'))]:reject(label,lambda:base.native.native_values(io.BytesIO(data),245880))
    reject('generic_own_Gram_not_research',lambda:base.raw_check(f,g,c0,components))
    duplicate=primary_values[:];duplicate[grouped[0][1]['id']]=1;reject('two_choices_in_first_column',lambda:decode(duplicate,grouped))
    need(all(digest(ROOT/p)==sha for p,sha in bindings.items()),'stable inputs')
    report={**provenance(bindings),'status':'INDEPENDENT_SIX_PRISM_FIRST_CHOICE_OBJECT_CALIBRATION_PASS','variables':245880,'clauses':874801,'normalization_gate_sha256':GATE_SHA,'base_calibration_sha256':CAL_SHA,
      'synthetic_own_Gram_positive':own,'synthetic_fullsize_codec':dict(native=nativeres,cnf=cnfres,research_SAT_witness=False),'normalized_primary_codec':dict(selected_first_choice=chosen[0],columns=len(chosen),research_CNF_assignment=False),
      'fresh_corruptions_rejected':rejected,'positive_research_factor':None,'positive_research_factor_null_reason':'Unknown; calibrated generic fixtures are separately labelled.','elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,derived,bindings=bind_inputs();core,g,columns,c0,components,grouped=derived
    values=base.common.assignment_values(read(args.assignment)['assignment'],245880)
    with args.native_output.open('rb')as stream:parsed,native=base.native.native_values(stream,245880)
    need(values==parsed,'all native and parsed values agree')
    with(D/'instance.cnf').open('rb')as stream:clauses=base.common.check_cnf_stream(stream,values,245880,874801)
    f,selected=decode(values,grouped);exact=base.raw_check(f,g,c0,components)
    if args.decoded:
        obj=read(args.decoded);need(obj['factor']==f and obj['selected_choice_ids']==selected and obj['target_graph']is False,'independent raw decode agrees')
    save(args.out/'independent_factor.json',dict(factor=f,selected_choice_ids=selected,core_adjacency=core,target_gram=g,components=components,exact_checks=exact,target_graph=False))
    for p in[args.assignment,args.native_output]+([args.decoded]if args.decoded else[]):bindings[key(p)]=digest(p)
    need(all(digest(ROOT/p)==sha for p,sha in bindings.items()),'stable inputs')
    report={**provenance(bindings),'status':'INDEPENDENT_SIX_PRISM_FIRST_CHOICE_FACTOR_OBJECT_PASS','native_assignment':native,'all_raw_augmented_clauses':clauses,'positive_unit1_checked':True,**exact,'independent_factor_sha256':digest(args.out/'independent_factor.json'),'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('calibrate');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('sat');p.add_argument('--out',type=Path,required=True);p.add_argument('--assignment',type=Path,required=True);p.add_argument('--native-output',type=Path,required=True);p.add_argument('--decoded',type=Path)
    args=ap.parse_args()
    try:(calibrate if args.mode=='calibrate'else sat)(args)
    except BaseException as error:
        if args.out.exists()and not(args.out/'failure.json').exists():save(args.out/'failure.json',dict(status='CHECK_FAILED',error=repr(error)))
        raise
if __name__=='__main__':main()
