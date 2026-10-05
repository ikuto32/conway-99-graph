"""Independently decode arbitrary core/factor SAT and inspect the raw partial graph."""
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
import audit_20260930_variable_core_factor_cnf_v2 as encoding
import audit_20260930_unrestricted_triangle_factor as raw_math
import audit_20260930_full99_sat_object as common
import audit_20260930_unrestricted_full99_sat_object as native

ROOT=Path(__file__).resolve().parents[1]
D=encoding.D
GATE=ROOT/'acceleration/results/20260930_independent_review/variable_core_factor_cnf_v2/summary.json'
GATE_SHA='ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0'
PINS={
 'acceleration/audit_20260930_unrestricted_triangle_factor.py':'040a4a297142fbfb5137cd5ac4d6aa5be786397971af875da7a0717dc8ca61bf',
 'acceleration/audit_20260930_full99_sat_object.py':'65d90a85be5fe67c510e561839901e9b8b7c3b9fc1ab7439af0e6bd3746a380c',
 'acceleration/audit_20260930_unrestricted_full99_sat_object.py':'6b78545d53041382e9b134718637998e4d0083175640b70044f60f480bcbc200',
}
need,digest,key,save=encoding.need,encoding.digest,encoding.key,encoding.save
def read(p):return json.loads(Path(p).read_bytes())

def bind_inputs():
    need(digest(GATE)==GATE_SHA,'frozen all-clause semantic gate');gate=read(GATE)
    need(gate['status']=='INDEPENDENT_VARIABLE_CORE_FACTOR_CNF_ENCODING_PASS','arbitrary-core encoding approved')
    bindings={**gate['inputs_sha256'],**PINS,key(GATE):GATE_SHA,key(__file__):digest(__file__)}
    for p,value in bindings.items():need(digest(ROOT/p)==value,'input and source hash '+p)
    model=read(D/'model.json');scope=read(D/'scope.json');primary=encoding.scope_check(model,scope)
    need((model['variables'],model['clauses'])==(110904,518160),'frozen dimensions')
    return model,scope,primary,bindings

def matrices_to_coordinates(m1,m2,p):
    n=len(p)
    for matrix in [m1,m2,p]:need(len(matrix)==n and all(len(row)==n and all(type(x) is int and x in (0,1) for x in row) for row in matrix),'binary core matrix dimensions/types')
    for matrix in [m1,m2]:need(all(matrix[a][a]==0 and sum(matrix[a])==1 for a in range(n)) and all(matrix[a][b]==matrix[b][a] for a,b in combinations(range(n),2)),'symmetric perfect matching matrix')
    need(all(sum(row)==1 for row in p) and all(sum(p[a][b] for a in range(n))==1 for b in range(n)),'permutation row/column margins')
    q=[[a^1 for a in range(n)],*[ [row.index(1) for row in matrix] for matrix in [m1,m2]]]
    perm=[row.index(1) for row in p];raw_math.validate_types(q,perm);return q,perm

def column_caps(f):
    n=len(f);width=len(f[0]) if f else 0
    need(all(len(row)==width and all(type(x) is int and x in (0,1) for x in row) for row in f),'binary rectangular column input')
    counts=[]
    for d,e in combinations(range(width),2):
        value=sum(f[r][d]*f[r][e] for r in range(n));need(value<=2,'distinct-column cap '+str((d,e,value)));counts.append(value)
    return dict(pairs=len(counts),overlap_histogram={str(v):counts.count(v) for v in range(3)})

def mixed_caps(core,f):
    n=len(core);need(len(f)==n and all(len(row)==n for row in core),'mixed core dimensions');width=len(f[0]) if f else 0
    need(all(len(row)==width and all(type(x) is int and x in (0,1) for x in row) for row in f),'mixed incidence shape/types')
    counts=[]
    for a in range(n):
        for d in range(width):
            value=f[a][d]+sum(core[a][b]*f[b][d] for b in range(n));need(value<=2,'mixed cap '+str((a,d,value)));counts.append(value)
    return dict(pairs=len(counts),cap_histogram={str(v):counts.count(v) for v in range(3)})

def raw_factor(m1,m2,p,f,research=True):
    qs,perm=matrices_to_coordinates(m1,m2,p);n=len(perm);width=n*(n-2)//2
    need(not research or n==12,'research dimensions exactly12')
    need(len(f)==3*n and all(len(row)==width and all(type(x) is int and x in (0,1) for x in row) for row in f),'exact literal binary factor shape')
    columns=[pair for pair in combinations(range(n),2) if pair[1]!=(pair[0]^1)]
    c0=[[int(a in pair) for pair in columns] for a in range(n)]
    need(f[:n]==c0,'canonical complete C0 incidence')
    need(all(sum(row)==n-2 for row in f),'every exact incidence row margin')
    need(all(sum(f[n*g+a][d] for a in range(n))==2 for g in range(3) for d in range(width)),'every fibre column margin')
    h=raw_math.raw_graph(qs,perm);core=[row[3:] for row in h[3:]];g=raw_math.literal_gram(h,n)
    need(all(sum(f[a][d]*f[b][d] for d in range(width))==g[a][b] for a in range(3*n) for b in range(3*n)),'every literal exact variable-core Gram entry')
    mixed=mixed_caps(core,f);caps=column_caps(f);size=3+3*n+width
    partial=[[0]*size for _ in range(size)]
    for a in range(3+3*n):partial[a][:3+3*n]=h[a][:]
    for r in range(3*n):
        for d in range(width):partial[3+r][3+3*n+d]=partial[3+3*n+d][3+r]=f[r][d]
    for d,e in combinations(range(width),2):partial[3+3*n+d][3+3*n+e]=partial[3+3*n+e][3+3*n+d]=-1
    nb=[{j for j,x in enumerate(row) if x==1} for row in partial];exactpairs=0;cappairs=0
    for a,b in combinations(range(size),2):
        actual=len(nb[a]&nb[b]);adj=partial[a][b]
        if b<3+3*n or a<3:
            need(actual==2-adj,'literal partial graph exact core or T-Y common count');exactpairs+=1
        else:
            need(actual+max(adj,0)<=2,'literal partial graph remaining known-common cap');cappairs+=1
    need(all(len(nb[a])==n+2 for a in range(3+3*n)) and all(len(nb[a])==6 for a in range(3+3*n,size)),'raw partial known degrees')
    checks=dict(factor_rows=3*n,factor_columns=width,Gram_entries_checked=9*n*n,row_margins=3*n,fibre_column_margins=3*width,matching_rows=2*n,permutation_rows_and_columns=2*n,mixed_caps=mixed,column_caps=caps,partial_vertices=size,exact_known_common_pairs=exactpairs,other_known_pair_caps=cappairs,residual_unknown_pairs=width*(width-1)//2,is_complete_target=False)
    return dict(M1=m1,M2=m2,P=p,core_adjacency=core,incidence_matrix=f,prescribed_gram=g,partial_adjacency_full99=partial,exact_checks=checks)

def decode(values,primary):
    columns,known,entries,f,ms,matches,p,perms=primary;c=[row[:] for row in known]
    for item in entries:c[item['row']][item['column']]=int(values[item['id']])
    matrices=[[[0]*12 for _ in range(12)] for _ in range(2)];pm=[[0]*12 for _ in range(12)]
    for item in matches:
        a,b=item['endpoints'];matrices[item['fibre']-1][a][b]=matrices[item['fibre']-1][b][a]=int(values[item['id']])
    for item in perms:pm[item['row']][item['column']]=int(values[item['id']])
    return raw_factor(*matrices,pm,c)

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit independent raw arbitrary-core factor checker',producer_imports=False,
      shared_components=['Pinned independent native/JSON assignment and complete CNF parsers reused.','Pinned independently authored raw graph/common-neighbour builder reused from normalization audit.','New arbitrary-core primary decode, integer factor conditions and complete partial-graph checking.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',limitations=['A passed object is a universally necessary factor and partial99 graph, not a complete99 graph.','Residual D existence is not asserted.'])

def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,scope,primary,bindings=bind_inputs();negative=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):negative.append(name)
        else:raise ValueError('corrupt control accepted '+name)
    m=[[0,1],[1,0]];p=[[1,0],[0,1]];empty=[[] for _ in range(6)]
    positive=raw_factor(m,m,p,empty,research=False);raw_math.srg_check(positive['partial_adjacency_full99'],4)
    save(args.out/'rook9_complete_raw_control.json',{**positive,'label':'Known-valid9vertex SRG generic raw-factor control; empty Y, not99vertex research SAT'})
    reject('wrong_core_matching_fixedpoint',lambda:raw_factor([[1,0],[0,1]],m,p,empty,research=False))
    reject('wrong_permutation_column',lambda:raw_factor(m,m,[[1,0],[1,0]],empty,research=False))
    reject('Boolean_matching_entry',lambda:raw_factor([[False,1],[1,0]],m,p,empty,research=False))
    reject('incorrect_permutation_Gram',lambda:raw_factor(m,m,[[0,1],[1,0]],empty,research=False))
    reject('generic9_not_research99',lambda:raw_factor(m,m,p,empty))
    fixture_path=ROOT/'acceleration/results/20260930_independent_review/triangle_column_cap_factor_object_calibration/synthetic_column_cap_positive.json'
    bindings[key(fixture_path)]=digest(fixture_path);column_positive=column_caps(read(fixture_path)['incidence_matrix'])
    h=raw_math.raw_graph([[a^1 for a in range(12)]]*3,list(range(12)));core=[row[3:] for row in h[3:]]
    mixed_positive=mixed_caps(core,[[0]*60 for _ in range(36)])
    reject('allone_mixed_cap',lambda:mixed_caps(core,[[1]*60 for _ in range(36)]))
    bad=[[0]*60 for _ in range(36)]
    for r in range(3):bad[r][0]=bad[r][1]=1
    reject('isolated_column_overlap3',lambda:column_caps(bad))
    canonical=primary[1][:12];bad_factor=[row[:] for _ in range(3) for row in canonical];standard=[[int(b==(a^1)) for b in range(12)] for a in range(12)];identity=[[int(a==b) for b in range(12)] for a in range(12)]
    reject('margins_alone_not_research_Gram',lambda:raw_factor(standard,standard,identity,bad_factor))
    variables,clauses=110904,518160;signed=list(range(1,variables+1));values=common.assignment_values(signed,variables)
    raw=b'c synthetic full-size codec only; not research SAT\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,signed[i:i+100]))+(' 0' if i+100>=variables else '')+'\n').encode() for i in range(0,variables,100))
    parsed,nativeres=native.native_values(io.BytesIO(raw),variables);need(parsed==values,'complete native codec identity')
    cnf=b'p cnf 110904 518160\n'+b''.join((str(i%variables+1)+' 0\n').encode() for i in range(clauses))
    cnfres=common.check_cnf_stream(io.BytesIO(cnf),values,variables,clauses)
    with gzip.open(args.out/'synthetic_fullsize_native.txt.gz','wb') as stream:stream.write(raw)
    with gzip.open(args.out/'synthetic_fullsize.cnf.gz','wb') as stream:stream.write(cnf)
    for name,bad in [('missing_native_status',raw.replace(b's SATISFIABLE\n',b'')),('missing_native_terminator',raw.replace(b'110904 0\n',b'110904\n')),('duplicate_native_variable',raw.replace(b'v 1 2 ',b'v 1 1 ',1)),('missing_native_variable',raw.replace(b'v 1 2 ',b'v 2 ',1))]:reject(name,lambda:native.native_values(io.BytesIO(bad),variables))
    for name,bad in [('old_header',cnf.replace(b'110904 518160',b'61296 256320',1)),('missing_last_clause',cnf[:cnf.rfind(b'\n',0,-1)+1]),('false_literal_sign',cnf.replace(b'1 0\n',b'-1 0\n',1))]:reject(name,lambda:common.check_cnf_stream(io.BytesIO(bad),values,variables,clauses))
    broken=values[:];broken[-1]=0;reject('false_auxiliary',lambda:common.check_cnf_stream(io.BytesIO(cnf),broken,variables,clauses))
    reject('partial_assignment',lambda:common.assignment_values(signed[:-1],variables))
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable artifacts')
    report={**provenance(bindings),'status':'INDEPENDENT_VARIABLE_CORE_FACTOR_OBJECT_CHECKER_CALIBRATION_PASS','variables':variables,'clauses':clauses,'generic_known_valid_raw_object':positive['exact_checks'],'separate_nonempty_column_positive':column_positive,'separate_zero_mixed_positive':mixed_positive,'synthetic_fullsize_codec':dict(native=nativeres,cnf=cnfres,research_SAT_witness=False),'fresh_corruptions_rejected':negative,
      'positive_research_factor':None,'positive_research_factor_null_reason':'No verified complete36row factor satisfying this full research scope is available; the complete generic positive is rook9 with emptyY, and nonempty cap/codec controls are explicitly separate.',
      'encoding_gate_sha256':GATE_SHA,'elapsed_seconds':time.monotonic()-start}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();model,scope,primary,bindings=bind_inputs()
    values=common.assignment_values(read(args.assignment)['assignment'],110904)
    with args.native_output.open('rb') as stream:nativevalues,nativeres=native.native_values(stream,110904)
    need(values==nativevalues,'all raw native and parsed assignment values agree')
    with (D/'instance.cnf').open('rb') as stream:cnfres=common.check_cnf_stream(stream,values,110904,518160)
    raw=decode(values,primary)
    if args.decoded:
        produced=read(args.decoded)
        for field in ['M1','M2','P','core_adjacency','incidence_matrix','prescribed_gram','partial_adjacency_full99']:need(produced[field]==raw[field],'independent decode equals raw producer '+field)
        need(produced['encoding_model_sha256']==digest(D/'model.json') and produced['scope_sha256']==digest(D/'scope.json') and produced['assignment_sha256']==digest(args.assignment),'producer raw object input identities')
        need(produced['full99_graph'] is False and produced['residual_Y_Y_unknown_pairs']==1770,'partial graph boundary')
    save(args.out/'independent_factor_and_partial99.json',{**raw,'encoding_model_sha256':digest(D/'model.json'),'scope_sha256':digest(D/'scope.json'),'full99_graph':False})
    for p in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(p)]=digest(p)
    need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable input artifacts')
    report={**provenance(bindings),'status':'INDEPENDENT_VARIABLE_CORE_FACTOR_SAT_OBJECT_PASS','native_assignment':nativeres,'all_raw_clauses':cnfres,'raw_exact_checks':raw['exact_checks'],'independent_factor_sha256':digest(args.out/'independent_factor_and_partial99.json'),'elapsed_seconds':time.monotonic()-start}
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
