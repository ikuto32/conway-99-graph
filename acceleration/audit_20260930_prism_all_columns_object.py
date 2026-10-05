"""Independent raw abstract six-prism factor and complete SAT certificate checker."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import gzip
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
import audit_20260930_unrestricted_triangle_factor as raw_math
import audit_20260930_triangle_joint_factor_cnf as factor_helper

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_prism_all_columns'
GATE=ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json'
GATE_SHA='07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3'
PINS={
 'acceleration/audit_20260930_full99_sat_object.py':'65d90a85be5fe67c510e561839901e9b8b7c3b9fc1ab7439af0e6bd3746a380c',
 'acceleration/audit_20260930_unrestricted_full99_sat_object.py':'6b78545d53041382e9b134718637998e4d0083175640b70044f60f480bcbc200',
 'acceleration/audit_20260930_unrestricted_triangle_factor.py':'040a4a297142fbfb5137cd5ac4d6aa5be786397971af875da7a0717dc8ca61bf',
 'acceleration/audit_20260930_triangle_joint_factor_cnf.py':'dd3ca89127560e808731adf51b0b39406dfbb28cc2decc72c07b40dec813e8fb',
 'acceleration/results/20260930_prism_all_columns/model.json':'a801e721a4c03d18e2fa9711a60f053895a4bfb8898b264f5174bcc36265f038',
 'acceleration/results/20260930_prism_all_columns/instance.cnf':'d45b7e9837ed02b669f3681aaa8a63af78ff46487e968c59cf47cd7a49e53d6f',
}
need,digest,key,save=common.need,common.digest,common.key,common.save
def read(p):return common.read(p)

def geometry():
    qs=[[a^1 for a in range(12)] for _ in range(3)];h=raw_math.raw_graph(qs,list(range(12)))
    core=[row[3:] for row in h[3:]];g=raw_math.literal_gram(h,12)
    columns=[list(pair) for pair in combinations(range(12),2) if pair[1]!=(pair[0]^1)]
    c0=[[int(a in pair) for pair in columns] for a in range(12)]
    components=[[12*f+2*a+b for f in range(3) for b in range(2)] for a in range(6)]
    return core,g,columns,c0,components

def scope_check(model):
    core,g,columns,c0,components=geometry()
    need(model['schema']=='SIX_PRISM_COMPLETE_COLUMN_DOMAINS_V1' and model['core_adjacency']==core and model['target_gram']==g and model['canonical_C0_columns']==columns and model['components']==components,'exact literal six-prism geometry')
    need(model['variables']==245880 and model['clauses']==874800,'exact dimensions')
    for name in ['outside_column_caps_encoded','residual_D_encoded','target_graph_encoded','symmetry_or_orbit_pruning','complement_pairing']:need(model[name] is False,'exact abstract scope '+name)
    choices=model['choices'];need(len(choices)==5760 and [r['id'] for r in choices]==list(range(1,5761)),'complete choice mapping identifiers')
    grouped=[[] for _ in range(60)]
    for item in choices:
        need(type(item['column']) is int and 0<=item['column']<60,'column index')
        d=item['column'];rows=item['rows'];need(rows==sorted(set(rows)) and len(rows)==6 and all(type(x) is int and 0<=x<36 for x in rows),'literal distinct six-row support')
        need([r for r in rows if r<12]==columns[d] and all(sum(r//12==f for r in rows)==2 for f in range(3)),'canonical C0 and three fibre counts')
        need(all(sum(r in rows for r in component)==1 for component in components),'one selected row in each component')
        grouped[d].append(item)
    need(all(len(group)==96 and len({tuple(item['rows']) for item in group})==96 for group in grouped),'distinct complete authenticated local choice populations')
    return core,g,columns,c0,components,grouped

def bind_inputs():
    need(digest(GATE)==GATE_SHA,'exact independent encoding gate');gate=read(GATE)
    need(gate['status']=='INDEPENDENT_SIX_PRISM_ALL_COLUMNS_CNF_ENCODING_PASS','complete finite-domain encoding audit')
    bindings={**gate['inputs_sha256'],**PINS,key(GATE):GATE_SHA,key(__file__):digest(__file__)}
    for p,h in bindings.items():need(digest(ROOT/p)==h,'exact input/source '+p)
    model=read(D/'model.json');derived=scope_check(model);return model,derived,bindings

def component_check(f,components):
    need(len(f)==36 and all(len(row)==60 and all(type(x) is int and x in (0,1) for x in row) for row in f),'raw literal36x60 component input')
    need(len(components)==6 and sorted(x for group in components for x in group)==list(range(36)),'six-component partition')
    totals=[[sum(f[r][d] for r in group) for d in range(60)] for group in components]
    need(all(x==1 for row in totals for x in row),'every component column total exactly one')
    return dict(equations=360,totals=totals)

def column_diagnostic(f):
    values=[];violations=[]
    for d,e in combinations(range(60),2):
        support=[r for r in range(36) if f[r][d] and f[r][e]];values.append(len(support))
        if len(support)>2:violations.append(dict(column_pair=[d,e],common_rows=support,overlap=len(support)))
    return dict(column_pairs=1770,overlap_histogram={str(k):values.count(k) for k in range(7)},violations=violations,violation_count=len(violations),encoded_constraint=False,independent_target_extension_exclusion_claimed=False)

def raw_check(f,g,c0,components):
    exact=factor_helper.factor_check(f,g,[row[:] for row in c0]+[[-1]*60 for _ in range(24)])
    return dict(exact_Gram_and_margins=exact,exact_components=component_check(f,components),column_caps_diagnostic=column_diagnostic(f))

def balanced_control(columns):
    f=[[0]*60 for _ in range(36)]
    for d,(i,j) in enumerate(columns):
        f[i][d]=f[j][d]=1;remaining=sorted(set(range(6))-{i//2,j//2})
        first=set(remaining[:2] if i%2==j%2 else remaining[2:])
        for component in remaining:f[(12 if component in first else 24)+2*component+i%2][d]=1
    return f

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit independent six-prism raw-object checker',producer_imports=False,
      shared_components=['Pinned independent raw39 graph/Gram and generic factor validators reused.','Pinned native/JSON/complete CNF parsers reused.','New choice decoding, component totals and non-encoded column diagnostics.'],limitations=['This is the abstract factor problem for one fixed six-prism core, with no arbitrary-core coverage.','Column-overlap caps and residual D are not encoded; a valid SAT factor is not a target.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')

def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,derived,bindings=bind_inputs();core,g,columns,c0,components,grouped=derived
    f=balanced_control(columns);own_g=[[sum(x*y for x,y in zip(a,b)) for b in f] for a in f];positive=raw_check(f,own_g,c0,components)
    need(own_g!=g,'synthetic positive is explicitly not the research Gram')
    save(args.out/'synthetic_balanced_factor_control.json',dict(factor=f,own_gram=own_g,components=components,label='Synthetic positive for own-Gram/margins/canonicalC0/component routines; not the prescribed six-prism Gram or a research SAT object'))
    negative=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):negative.append(label)
        else:raise ValueError('corrupt control accepted '+label)
    reject('synthetic_own_Gram_not_research_Gram',lambda:raw_check(f,g,c0,components))
    bad=deepcopy(f);bad[12][0]^=1;reject('factor_bit',lambda:raw_check(bad,own_g,c0,components))
    bad=deepcopy(f);bad[0][0]=bool(bad[0][0]);reject('Boolean_entry',lambda:raw_check(bad,own_g,c0,components))
    reject('partial24_not_full36',lambda:raw_check(f[:24],own_g,c0,components))
    reject('duplicate_component',lambda:component_check(f,[components[0]]+components[:-1]))
    bad=deepcopy(f);r=next(r for r in components[0] if bad[r][0]);bad[r][0]=0;reject('missing_component_entry',lambda:component_check(bad,components))
    wrongg=deepcopy(own_g);wrongg[0][0]+=1;reject('changed_Gram_entry',lambda:raw_check(f,wrongg,c0,components))
    # Diagnostic violations do not invalidate the abstract encoded factor scope.
    isolated=[[0]*60 for _ in range(36)]
    for r in range(3):isolated[r][0]=isolated[r][1]=1
    diagnostic=column_diagnostic(isolated);need(diagnostic['violation_count']==1 and diagnostic['violations'][0]['overlap']==3,'literal non-encoded cap diagnostic control')
    variables,clauses=245880,874800;signed=list(range(1,variables+1));values=common.assignment_values(signed,variables)
    raw=b'c synthetic full-size six-prism codec, not research SAT\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,signed[i:i+100]))+(' 0' if i+100>=variables else '')+'\n').encode() for i in range(0,variables,100))
    parsed,nativeres=native.native_values(io.BytesIO(raw),variables);need(parsed==values,'complete native and JSON codec')
    cnf=b'p cnf 245880 874800\n'+b''.join((str(i%variables+1)+' 0\n').encode() for i in range(clauses));cnfres=common.check_cnf_stream(io.BytesIO(cnf),values,variables,clauses)
    with gzip.open(args.out/'synthetic_native.stdout.gz','wb') as stream:stream.write(raw)
    with gzip.open(args.out/'synthetic_fullsize.cnf.gz','wb') as stream:stream.write(cnf)
    for name,bad in [('missing_status',raw.replace(b's SATISFIABLE\n',b'')),('missing_terminator',raw.replace(b'245880 0\n',b'245880\n')),('duplicate_native_id',raw.replace(b'v 1 2 ',b'v 1 1 ',1)),('missing_native_id',raw.replace(b'v 1 2 ',b'v 2 ',1))]:reject(name,lambda:native.native_values(io.BytesIO(bad),variables))
    for name,bad in [('wrong_header',cnf.replace(b'245880 874800',b'110904 518160',1)),('missing_clause',cnf[:cnf.rfind(b'\n',0,-1)+1]),('false_clause_sign',cnf.replace(b'1 0\n',b'-1 0\n',1))]:reject(name,lambda:common.check_cnf_stream(io.BytesIO(bad),values,variables,clauses))
    broken=values[:];broken[-1]=0;reject('false_auxiliary',lambda:common.check_cnf_stream(io.BytesIO(cnf),broken,variables,clauses))
    reject('partial_assignment',lambda:common.assignment_values(signed[:-1],variables))
    need(all(digest(ROOT/p)==h for p,h in bindings.items()),'stable frozen inputs')
    report={**provenance(bindings),'status':'INDEPENDENT_SIX_PRISM_ALL_COLUMNS_OBJECT_CHECKER_CALIBRATION_PASS','variables':variables,'clauses':clauses,'synthetic_own_Gram_positive':positive,'separate_column_diagnostic_control':diagnostic,'fullsize_codec':dict(native=nativeres,cnf=cnfres,research_SAT_witness=False),'fresh_corruptions_rejected':negative,
      'positive_research_factor':None,'positive_research_factor_null_reason':'No full factor of the prescribed research Gram is known. Synthetic fullshape positive uses its explicitly saved own Gram and is rejected against the actual research Gram.',
      'encoding_gate_sha256':GATE_SHA,'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,derived,bindings=bind_inputs();core,g,columns,c0,components,grouped=derived
    values=common.assignment_values(read(args.assignment)['assignment'],245880)
    with args.native_output.open('rb') as stream:nativevalues,nativeres=native.native_values(stream,245880)
    need(values==nativevalues,'every native and parsed assignment value agrees')
    with (D/'instance.cnf').open('rb') as stream:cnfres=common.check_cnf_stream(stream,values,245880,874800)
    f=[[0]*60 for _ in range(36)];selected=[]
    for d,choices in enumerate(grouped):
        chosen=[item for item in choices if values[item['id']]];need(len(chosen)==1,'one actual choice per column');selected.append(chosen[0]['id'])
        for r in chosen[0]['rows']:f[r][d]=1
    exact=raw_check(f,g,c0,components)
    if args.decoded:
        produced=read(args.decoded);need(produced['factor']==f and produced['selected_choice_ids']==selected and produced['target_graph'] is False,'independent complete raw decode equality')
    save(args.out/'independent_factor.json',dict(factor=f,selected_choice_ids=selected,core_adjacency=core,target_gram=g,components=components,exact_checks=exact,target_graph=False,encoding_model_sha256=digest(D/'model.json')))
    for p in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(p)]=digest(p)
    need(all(digest(ROOT/p)==h for p,h in bindings.items()),'stable frozen artifacts')
    report={**provenance(bindings),'status':'INDEPENDENT_SIX_PRISM_ALL_COLUMNS_FACTOR_OBJECT_PASS','native_assignment':nativeres,'all_raw_clauses':cnfres,**exact,'independent_factor_sha256':digest(args.out/'independent_factor.json'),'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('calibrate');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('sat');p.add_argument('--out',type=Path,required=True);p.add_argument('--assignment',type=Path,required=True);p.add_argument('--native-output',type=Path,required=True);p.add_argument('--decoded',type=Path)
    args=ap.parse_args()
    try:(calibrate if args.mode=='calibrate' else sat)(args)
    except BaseException as error:
        if args.out.exists() and not (args.out/'failure.json').exists():save(args.out/'failure.json',dict(status='CHECK_FAILED',error=repr(error)))
        raise

if __name__=='__main__':main()
