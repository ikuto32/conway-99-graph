"""Independent complete Q1 projection scope and clause reconstruction."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_triangle_joint_factor_cnf as base
import audit_20260930_triangle_factor_components as compaudit

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_q1_capacity_cnf'
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_factor_components/summary.json'
GATE_SHA='03d84677f34e0a209f9331c32efcd0b843dae60b97dbf9e9102b85171a5fef5b'
SUMMARY_SHA='929301b1359c6b06a6955586c0dffd835a677560f58a559a9e4690c5f3e456aa'
need,digest,key,save=base.need,base.digest,base.key,base.save

def derived():
    h,g,cols,known,zeros,entries,refs=base.derive()
    _,components=compaudit.components_from_raw(h)
    return [r[:24] for r in g[:24]],cols,known[:24],[e for e in entries if e['row']<24],refs[:24],components

def scope_check(model,scope):
    g,cols,known,entries,refs,components=derived()
    need(len(entries)==600 and len([x for r in known[12:] for x in r if x==0])==120,'600free+120forced positions')
    for raw in [model,scope]:
        need(raw['known_incidence_rows']==known and raw['target_gram_rows']==g and raw['entry_variables']==entries and raw['components']==components,'complete projection rawscope')
        need(all(type(x) is int for r in raw['known_incidence_rows'] for x in r),'integer incidence entries')
        need(all(type(x) is int for r in raw['target_gram_rows'] for x in r),'integer Gram entries')
    need(scope['edge_columns_C0']==list(map(list,cols)),'canonical C0 labels')
    need(scope['parent_scope']==key(base.D/'scope.json') and scope['parent_scope_sha256']==digest(base.D/'scope.json'),'original fixed-core scope')
    kernel=compaudit.D/'kernel_certificate.json'
    need(scope['kernel_certificate']==key(kernel) and scope['kernel_certificate_sha256']==digest(kernel),'component premise binding')
    need(scope['row_sum']==10 and scope['column_sum_per_fibre']==2 and scope['partial_component_column_upper_bound']==2,'exact margins/capacity')
    need(scope['C1_free'] is True and scope['C2_included'] is False and scope['D_included'] is False,'only C1 free projection')
    need(scope['unrestricted_target_coverage'] is False and scope['target_automorphism_assumed'] is False,'no unrestricted/symmetry assumption')
    need(model['full_target_graph_encoded'] is False and model['complete36row_factor_encoded'] is False and model['C2_included'] is False,'projection, not whole factor')
    need(model['schema']=='TRIANGLE_Q1_COMPONENT_CAPACITY_PREFIX_CNF_V1' and scope['schema']=='FIXED_TRIANGLE_Q1_COMPONENT_CAPACITY_SCOPE_V1','exact schemas')
    need(model['scope_path']==key(D/'scope.json') and model['scope_sha256']==digest(D/'scope.json'),'scope raw identity')
    return g,cols,known,entries,refs,components

def capacity_check(c,components):
    need(len(c)==24 and all(len(row)==60 and all(type(x) is int and x in (0,1) for x in row) for row in c),'binary24x60 capacity input')
    totals=[[sum(c[r][d] for r in group if r<24) for d in range(60)] for group in components]
    need(len(totals)==3 and all(x<=2 for row in totals for x in row),'all180 partial component capacities')
    return totals

def extract_q1(c,columns):
    index={tuple(e):i for i,e in enumerate(columns)};q=[]
    for d in range(60):
        pair=tuple(a for a in range(12) if c[12+a][d])
        need(len(pair)==2 and pair in index,'C1 column is a permitted pair');q.append(index[pair])
    need(sorted(q)==list(range(60)),'Q1 exact permutation of all60pairs')
    need(all(c[12+a][d]==int(a in columns[q[d]]) for a in range(12) for d in range(60)),'Q1 raw column roundtrip')
    return q

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(path,expected=None):
        path=Path(path);v=digest(path);need(expected is None or v==expected,'hash '+str(path));bindings[key(path)]=v;return path
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    try:
        gate=read(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_TRIANGLE_COMPONENT_FACTOR_CNF_ENCODING_PASS','exact independent kernel/scope gate')
        for p,v in gate['inputs_sha256'].items():bind(ROOT/p,v)
        summary=read(D/'summary.json',SUMMARY_SHA);manifest=read(D/'manifest.json')
        for p,v in manifest['inputs_sha256'].items():bind(ROOT/p,v)
        for name,record in summary['outputs'].items():need(bind(D/name,record['sha256']).stat().st_size==record['bytes'],'artifact size')
        model=read(D/'model.json');scope=read(D/'scope.json');g,columns,known,entries,refs,components=scope_check(model,scope)
        rejected=[]
        fields=['known_incidence_rows','target_gram_rows','entry_variables','components','full_target_graph_encoded','complete36row_factor_encoded','C2_included','schema','scope_path','scope_sha256']
        for name in ['fixed_C0','forced_zero','free_bit','Gram','variable','component','C1_fixed','C2_present','cap3','target_scope']:
            m,s=deepcopy({k:model[k] for k in fields}),deepcopy(scope)
            if name=='fixed_C0':m['known_incidence_rows'][0][0]^=1
            elif name=='forced_zero':
                r,d=next((r,d) for r in range(12,24) for d in range(60) if known[r][d]==0);m['known_incidence_rows'][r][d]=-1
            elif name=='free_bit':e=entries[0];m['known_incidence_rows'][e['row']][e['column']]=0
            elif name=='Gram':m['target_gram_rows'][0][12]+=1
            elif name=='variable':m['entry_variables'][0]['id']=2
            elif name=='component':m['components'][0][0]=m['components'][1][0]
            elif name=='C1_fixed':s['C1_free']=False
            elif name=='C2_present':m['C2_included']=True
            elif name=='cap3':s['partial_component_column_upper_bound']=3
            else:s['unrestricted_target_coverage']=True
            try:scope_check(m,s)
            except ValueError:rejected.append(name)
            else:raise ValueError('corrupted scope accepted '+name)
        controls=dict(threshold=base.gates.controls(),scope_corruptions=rejected);save(args.out/'controls.json',controls)
        rowi=0;prodi=0
        with (D/'instance.cnf').open('rb') as stream:
            need(stream.readline()==b'p cnf 19686 68328\n','exact projection header')
            cursor=base.gates.ClauseCursor(stream,19686);audit=base.gates.GateAudit(cursor,600)
            def counter(terms,bound,equality,meta):
                nonlocal rowi
                audit.counter(model['counter_rows'][rowi],terms,bound,equality,meta);rowi+=1
            for r in range(12,24):counter([x for x in refs[r] if type(x) is int],10,True,dict(kind='row_margin',row=r,constant=0,original_bound=10))
            for d in range(60):counter([refs[r][d] for r in range(12,24) if type(refs[r][d]) is int],2,True,dict(kind='column_margin',fibre=1,column=d,constant=0,original_bound=2))
            for a in range(12):
                for b in range(12,24):counter([refs[b][d] for d in range(60) if known[a][d]==1 and type(refs[b][d]) is int],g[a][b],True,dict(kind='C0_cross_gram',pair=[a,b],constant=0,original_bound=g[a][b]))
            for a,b in combinations(range(12,24),2):
                terms=[]
                for d in range(60):
                    x,y=refs[a][d],refs[b][d]
                    if type(x) is int and type(y) is int:
                        record=model['product_variables'][prodi];prodi+=1
                        need(record==dict(id=audit.top+1,left=x,right=y,pair=[a,b],column=d,first_clause=cursor.count+1,clause_count=3),'literal product identity')
                        audit.gate(False,x,y,record['id']);terms.append(record['id'])
                counter(terms,g[a][b],True,dict(kind='unknown_pair_gram',pair=[a,b],constant=0,original_bound=g[a][b]))
            need(rowi==282,'all exact equations')
            for ci,group in enumerate(components):
                support=[r for r in group if r<24]
                for d in range(60):
                    c=sum(refs[r][d] is True for r in support);terms=[refs[r][d] for r in support if type(refs[r][d]) is int]
                    counter(terms,2-c,False,dict(kind='partial_component_capacity',component=ci,column=d,raw_component_rows=group,included_rows=support,constant=c,original_bound=2))
            need(stream.read()==b'','no extra clauses')
        need(rowi==len(model['counter_rows'])==462 and prodi==len(model['product_variables'])==2700,'all projected rows/products')
        need(cursor.count==model['clauses']==68328 and audit.top==model['variables']==19686,'all raw clauses and variables')
        packages=[]
        for p in read(D/'artifact_packages.json')['packages']:
            compressed=b''.join(bind(ROOT/x['path'],x['sha256']).read_bytes() for x in p['ordered_parts'])
            need(sha256(compressed).hexdigest()==p['compressed_stream_sha256'],'gzip stream')
            raw=gzip.decompress(compressed);need(len(raw)==p['raw_bytes'] and sha256(raw).hexdigest()==p['raw_sha256']==digest(ROOT/p['raw_path']),'exact public recovery')
            packages.append(dict(path=p['raw_path'],sha256=p['raw_sha256'],bytes=len(raw)))
        for path in [Path(__file__),ROOT/'docs/AUDIT_20260930_TRIANGLE_Q1_CAPACITY_ENCODING.md']:bind(path)
        need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable inputs')
        report=dict(status='INDEPENDENT_TRIANGLE_Q1_CAPACITY_CNF_ENCODING_PASS',claim_id='C-FIXED-TRIANGLE-Q1-CAPACITY-PROJECTION-CNF',claim_revision=1,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit independent projected polynomial/clause checker',kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
          statement='The exact19686variable68328clause CNF is satisfiable iff a binary24x60factor(C0;C1) has the frozen principal Gram, row10/fibre-column2 margins and all180partial component counts<=2. Every full fixed-core36row factor restricts to such a projection; the converse extension implication is not claimed.',
          dependencies=[dict(id='C-FIXED-TRIANGLE-JOINT-BINARY-FACTOR-CNF-ENCODING',revision=1,relation='uses_result'),dict(id='C-FIXED-TRIANGLE-FACTOR-COMPONENT-BALANCE',revision=1,relation='uses_result')],scope='One fixed39core necessary24row projection; no C2/residual D/target automorphism or unrestricted containment.',variables=19686,clauses=68328,entry_variables=600,forced_zeros=120,AND_products=2700,equalities=282,capacities=180,controls=controls,package_checks=packages,
          shared_components=['Previously frozen independent raw-core Gram/scope and component checking functions.','Frozen independent truth-relation GateAudit reused; every new clause reconstructed.','No producer imports.'],limitations=['SAT need not extend to36rows or a99vertex target.','UNSAT exclusion requires complete independently replayed proof.'],solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e)));raise

if __name__=='__main__':main()
