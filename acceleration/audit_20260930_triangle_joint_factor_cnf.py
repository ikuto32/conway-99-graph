"""Independent raw-core Gram, column normalization, and complete CNF audit."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import gzip
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_eight_full99_cnf_v1 as gates

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf'
need,digest,key,save=gates.need,gates.digest,gates.key,gates.save
PINS={
 'acceleration/audit_20260930_eight_full99_cnf_v1.py':'c956504752a937ffa6aa1ad84d4aa30d95db8723287970e76cbfd262b74ecf4c',
 'acceleration/theory_20260930_triangle_joint_factor_cnf.py':'218ed1acdfe0878bc169b74c74c8685112f8a66d9344107f4f1fa4a4f1df5fe2',
 'acceleration/theory_20260930_triangle_joint_factor_cnf_spec.md':'bfca60d752c1c801e4091fdd810e128b92746c9df381f78f225b2d23368ab955',
 'acceleration/results/20260930_triangle_joint_factor_cnf/summary.json':'981418a95aec2bbe4e4c83abde20157ae342c2bcb4af43d65da4bd6838cbf03e',
 'acceleration/results/20260930_triangle_joint_factor_cnf/model.json':'d1a52720be73dfdc809a86c7d872ad4d36aaccb3c0b104f9565338ba43a9f1fb',
 'acceleration/results/20260930_triangle_joint_factor_cnf/instance.cnf':'c56b4b5511530efe2ee08934549a1a3f012b8481741f70b58faa440fdaef032c',
 'acceleration/results/20260930_triangle_joint_factor_cnf/scope.json':'51d5f51ba4177d41247239fc2d7a3753b26150e9660960b7452f38e304d731d0',
}

def derive():
    h=[[0]*39 for _ in range(39)]
    def edge(a,b):h[a][b]=h[b][a]=1
    for a,b in combinations(range(3),2):edge(a,b)
    for f in range(3):
        for i in range(12):
            edge(f,3+12*f+i);edge(3+12*f+i,3+12*f+(i^1))
    for i in range(12):
        edge(3+i,15+i);edge(3+i,27+i);edge(15+i,27+(i+6)%12)
    need([sum(row) for row in h]==[14]*3+[4]*36,'literal core degrees')
    g=[[12*int(a==b)-h[3+a][3+b]+2-sum(h[3+a][k]*h[3+b][k] for k in range(39)) for b in range(36)] for a in range(36)]
    need(all(x>=0 for row in g for x in row),'nonnegative forced Gram')
    for f in range(3):
        for a in range(12):
            for b in range(12):need(g[12*f+a][12*f+b]==(10 if a==b else int(b!=(a^1))),'canonical diagonal Gram block')
    columns=[(a,b) for a,b in combinations(range(12),2) if g[a][b]==1]
    need(len(columns)==60,'all distinct nonmatching column pairs')
    c0=[[int(a in edge) for edge in columns] for a in range(12)]
    known=[row[:] for row in c0]+[[-1]*60 for _ in range(24)]
    zeros=[];entries=[]
    for row in range(12,36):
        for col in range(60):
            reasons=[a for a in range(12) if c0[a][col] and g[a][row]==0]
            if reasons:
                known[row][col]=0;zeros.append(dict(row=row,column=col,C0_rows_with_zero_target=reasons))
            else:entries.append(dict(id=len(entries)+1,row=row,column=col))
    need(len(entries)==1200 and len(zeros)==240,'forced-zero and free-entry counts')
    refs=[[bool(x) if x>=0 else None for x in row] for row in known]
    for e in entries:refs[e['row']][e['column']]=e['id']
    return h,g,columns,known,zeros,entries,refs

def scope_check(model,scope):
    h,g,columns,known,zeros,entries,refs=derive()
    need(scope['core']==dict(internal_matchings=[[i^1 for i in range(12)]]*3,F01=list(range(12)),F02=list(range(12)),P12=[(i+6)%12 for i in range(12)]),'exact fixed core')
    need(scope['edge_columns_C0']==list(map(list,columns)),'exact normalized column labels')
    for raw in [model,scope]:
        need(raw['known_incidence_rows']==known and raw['target_gram_rows']==g and raw['entry_variables']==entries,'all raw incidence/Gram/variable values')
        need(all(type(x) is int for row in raw['known_incidence_rows'] for x in row),'literal integer incidence types')
        need(all(type(x) is int for row in raw['target_gram_rows'] for x in row),'literal integer Gram types')
        need(all(type(e[k]) is int for e in raw['entry_variables'] for k in ['id','row','column']),'literal integer primary mappings')
    need(scope['forced_zero_witnesses']==zeros,'all forced-zero proofs')
    need(scope['row_sum']==10 and scope['column_sum_per_fibre']==2,'scope margins')
    need(scope['target_automorphism_assumed'] is False and scope['unrestricted_target_coverage'] is False,'conditional scope without automorphism')
    need(scope['Q1_fixed'] is False and scope['Q2_fixed'] is False and scope['residual_D_included'] is False,'both factors free, no residual graph')
    need(model['full_target_graph_encoded'] is False and model['solver_calls']==0,'factor-only scope')
    need(model['schema']=='FIXED_TRIANGLE_JOINT_BINARY_FACTOR_PREFIX_CNF_V1' and scope['schema']=='FIXED_TRIANGLE_JOINT_BINARY_FACTOR_SCOPE_V1','scope and model schemas')
    need(model['scope_path']==key(D/'scope.json') and model['scope_sha256']==PINS[key(D/'scope.json')],'scope artifact binding')
    return h,g,columns,known,zeros,entries,refs

def factor_check(c,g,known=None):
    n=len(c)
    need(n in [24,36] and len(g)==n,'factor row dimensions')
    need(all(len(row)==60 and all(type(x) is int and x in (0,1) for x in row) for row in c),'binary factor shape/types')
    need(all(len(row)==n and all(type(x) is int for x in row) for row in g),'integer square Gram')
    need(all(sum(row)==10 for row in c),'exact row margins')
    need(all(sum(c[a][d] for a in range(f,f+12))==2 for f in range(0,n,12) for d in range(60)),'exact fibre column margins')
    if known is not None:
        need(len(known)==n and all(len(row)==60 for row in known),'scope dimensions')
        need(all(known[a][d]==-1 or c[a][d]==known[a][d] for a in range(n) for d in range(60)),'every fixed incidence')
    products=0
    for a in range(n):
        for b in range(n):
            need(sum(c[a][d]*c[b][d] for d in range(60))==g[a][b],'literal exact Gram entry '+str((a,b)));products+=1
    return dict(rows=n,columns=60,integer_gram_entries_checked=products,row_margins=n,fibre_column_margins=60*(n//12))

def scope_controls(model,scope):
    small={k:model[k] for k in ['known_incidence_rows','target_gram_rows','entry_variables','full_target_graph_encoded','solver_calls','schema','scope_path','scope_sha256']}
    rejected=[]
    for name in ['fixed_C0','forced_zero','free_entry','duplicate_primary','wrong_gram','missing_zero_reason','wrong_P','Q1_fixed','target_coverage','automorphism']:
        m,s=deepcopy(small),deepcopy(scope)
        if name=='fixed_C0':m['known_incidence_rows'][0][0]^=1
        elif name=='forced_zero':
            z=s['forced_zero_witnesses'][0];m['known_incidence_rows'][z['row']][z['column']]=-1
        elif name=='free_entry':
            e=m['entry_variables'][0];m['known_incidence_rows'][e['row']][e['column']]=0
        elif name=='duplicate_primary':m['entry_variables'][1]['id']=1
        elif name=='wrong_gram':m['target_gram_rows'][12][24]+=1
        elif name=='missing_zero_reason':s['forced_zero_witnesses'][0]['C0_rows_with_zero_target']=[]
        elif name=='wrong_P':s['core']['P12']=list(range(12))
        elif name=='Q1_fixed':s['Q1_fixed']=True
        elif name=='target_coverage':s['unrestricted_target_coverage']=True
        else:s['target_automorphism_assumed']=True
        try:scope_check(m,s)
        except ValueError:rejected.append(name)
        else:raise ValueError('scope corruption accepted '+name)
    return rejected

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(path,expected=None):
        path=Path(path);value=digest(path);need(expected is None or value==expected,'input hash '+str(path));bindings[key(path)]=value;return path
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    try:
        for name,value in PINS.items():bind(ROOT/name,value)
        model=read(D/'model.json');scope=read(D/'scope.json');manifest=read(D/'manifest.json');summary=read(D/'summary.json')
        for name,value in manifest['inputs_sha256'].items():bind(ROOT/name,value)
        h,g,columns,known,zeros,entries,refs=scope_check(model,scope)
        archive=ROOT/'external_conway99_research';pin='85e705cc6c2a14d123120c93a847e30aaab1789e'
        for name in ['wave149-terwilliger-triple','wave151-triangle-root-factor','wave154-triangle-factor-portfolio']:
            p=archive/'attempts'/name/'exact-results.json'
            need(subprocess.check_output(['git','-C',str(archive),'show',pin+':'+p.relative_to(archive).as_posix()])==bind(p).read_bytes(),'immutable historical input')
        archive_g=read(archive/'attempts/wave149-terwilliger-triple/exact-results.json')['minimal_surviving_witness']['gram_rows']
        need(g==archive_g,'raw independently derived Gram equals exact historical core')
        calibration=dict(threshold=gates.controls(),scope_corruptions_rejected=scope_controls(model,scope))
        save(args.out/'controls.json',calibration)
        save(args.out/'independently_derived_core_and_gram.json',dict(core_adjacency=h,target_gram=g,known_incidence=known,columns=columns))
        for path in [Path(__file__),ROOT/'docs/AUDIT_20260930_TRIANGLE_JOINT_FACTOR_ENCODING.md',ROOT/'uv.lock']:bind(path)
        provenance=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings)
        save(args.out/'manifest.json',{**provenance,'scope':'All normalized binary36x60 incidence factors for one raw fixed39core; complete all-clause reconstruction.','wall_seconds_limit':180,'solver_calls':0,'numerical_thresholds':None,'numerical_thresholds_null_reason':'Exact integers and complete Boolean truth relations.'})
        rowi=0;prodi=0
        with (D/'instance.cnf').open('rb') as stream:
            need(stream.readline()==b'p cnf 58860 203748\n','exact CNF header')
            cursor=gates.ClauseCursor(stream,58860);audit=gates.GateAudit(cursor,1200)
            def rowcheck(inputs,bound,annotation):
                nonlocal rowi
                audit.counter(model['counter_rows'][rowi],inputs,bound,True,annotation);rowi+=1
            for fibre in [1,2]:
                for a in range(12):
                    row=12*fibre+a
                    rowcheck([x for x in refs[row] if type(x) is int],10,dict(kind='row_margin',row=row,constant=0,original_bound=10))
                for d in range(60):
                    rowcheck([refs[12*fibre+a][d] for a in range(12) if type(refs[12*fibre+a][d]) is int],2,dict(kind='column_margin',fibre=fibre,column=d,constant=0,original_bound=2))
                for a in range(12):
                    for b in range(12):
                        row=12*fibre+b
                        terms=[refs[row][d] for d in range(60) if known[a][d]==1 and type(refs[row][d]) is int]
                        rowcheck(terms,g[a][row],dict(kind='C0_cross_gram',pair=[a,row],constant=0,original_bound=g[a][row]))
            for a,b in combinations(range(12,36),2):
                terms=[]
                for col in range(60):
                    x,y=refs[a][col],refs[b][col]
                    if type(x) is int and type(y) is int:
                        p=model['product_variables'][prodi];prodi+=1
                        need(p==dict(id=audit.top+1,left=x,right=y,pair=[a,b],column=col,first_clause=cursor.count+1,clause_count=3),'exact raw incidence product metadata')
                        audit.gate(False,x,y,p['id']);terms.append(p['id'])
                rowcheck(terms,g[a][b],dict(kind='unknown_pair_gram',pair=[a,b],constant=0,original_bound=g[a][b]))
            need(stream.read()==b'','no extra CNF clauses')
        need(rowi==len(model['counter_rows'])==708 and prodi==len(model['product_variables'])==11400,'complete equation/product population')
        need(cursor.count==model['clauses']==203748 and audit.top==model['variables']==58860,'complete raw clauses/variables')
        package_checks=[]
        for p in read(D/'artifact_packages.json')['packages']:
            compressed=b''.join(bind(ROOT/part['path'],part['sha256']).read_bytes() for part in p['ordered_parts'])
            need(sha256(compressed).hexdigest()==p['compressed_stream_sha256'],'gzip part concatenation')
            raw=gzip.decompress(compressed)
            need(sha256(raw).hexdigest()==p['raw_sha256']==digest(ROOT/p['raw_path']) and len(raw)==p['raw_bytes'],'recovered exact artifact')
            package_checks.append(dict(path=p['raw_path'],sha256=p['raw_sha256'],bytes=len(raw)))
        need(all(digest(ROOT/p)==v for p,v in bindings.items()),'input stability')
        need(time.monotonic()-start<180,'audit wall cap')
        report={**provenance,'status':'INDEPENDENT_TRIANGLE_JOINT_FACTOR_CNF_ENCODING_PASS','claim_id':'C-FIXED-TRIANGLE-JOINT-BINARY-FACTOR-CNF-ENCODING','claim_revision':1,
          'kind':'encoding','basis':['DERIVED','COMPUTED'],'recommendation':'VERIFIED','review_state':'CLEAR','verifier':'/root/eight_domain_audit independent raw-core and full-clause checker',
          'statement':'The saved 58,860-variable 203,748-clause CNF is satisfiable if and only if a binary36x60 factor of the explicitly fixed triangle-core Gram exists, with row margins10 and per-fibre column margins2, up to the proved harmless C0 column relabelling. Every target containing that exact core supplies such a factor.',
          'scope':'One fixed39vertex core; C1 and C2 entirely free, no residual D or full target graph encoded.','dependencies':[],
          'dependencies_reason':'Direct target-identity premise and raw core derivation are included; no prior fixed-factor exclusion is used.',
          'variables':audit.top,'clauses':cursor.count,'primary_entries':1200,'forced_zeros':240,'AND_products':prodi,'counter_rows':rowi,
          'cnf_sha256':digest(D/'instance.cnf'),'model_sha256':digest(D/'model.json'),'scope_sha256':digest(D/'scope.json'),
          'controls':calibration,'package_checks':package_checks,'derivation_path':'docs/AUDIT_20260930_TRIANGLE_JOINT_FACTOR_ENCODING.md',
          'shared_components':['Frozen independent GateAudit truth-relation/threshold code reused with exact source pin.','New raw39 graph, Gram and incidence-scope reconstruction; no producer imports.','Python standard library and exact integers.'],
          'limitations':['No target-wide core coverage.','SAT supplies only an incidence factor; no residual D is encoded.','UNSAT requires a separately checked complete proof on these exact bytes.'],
          'solver_calls':0,'target_resolution':False,'external_review':False,'artifact_availability':'LOCAL_ONLY','elapsed_seconds':time.monotonic()-start}
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:
        save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e),inputs_sha256=bindings));raise

if __name__=='__main__':main()
