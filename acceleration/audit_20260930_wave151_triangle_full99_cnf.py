"""Independent complete equality-CNF audit for one fixed triangle Q1 scope.

Imports only a frozen independently authored truth-relation checker, not the
producer. Original fixed-factor assembly/propagation is a separate audit gate.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
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
from tqdm import tqdm
import audit_20260930_eight_full99_cnf_v1 as gates

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_wave151_full99_cnf'
PARTIAL=ROOT/'acceleration/results/20260930_triangle_partial99/wave151.json'
PINS={
 'acceleration/audit_20260930_triangle_full99_cnf.py':'e6ffa96c25dc02daa367dbc3ea75f3aaed2af5d3ef99f2fd10bf79cfcc3c5a38',
 'acceleration/results/20260930_triangle_wave151_full99_cnf/summary.json':'a0ab23019ca60bd74450bb17272c7e066147d41be751a0d9555c1a4327f43afd',
 'acceleration/audit_20260930_eight_full99_cnf_v1.py':'c956504752a937ffa6aa1ad84d4aa30d95db8723287970e76cbfd262b74ecf4c',
 'acceleration/results/20260930_triangle_partial99/wave151.json':'688b0255760a57a4cdd39e1ea471a784e3771a13c6fd3a6eb8b3615a7c43f063',
 'acceleration/results/20260930_triangle_wave151_full99_cnf/model.json':'e688c04d330cb1470af19dd1590960c9ddc0c9b7f71c718de2db5358ae1668f7',
 'acceleration/results/20260930_triangle_wave151_full99_cnf/instance.cnf':'24d6b14e08fcd10f390edf462f75a6bc160c91c863448adf72d076f2297fc27e',
 'acceleration/results/20260930_triangle_wave151_full99_cnf/scope.json':'f593054838b96460b2b62b187966696696173d3bc915c7e6e33779c56b05f508',
}
need,digest,key,save=gates.need,gates.digest,gates.key,gates.save
def scope_check(model,scope,partial):
    known=model['known_adjacency_full99']
    need(len(known)==99 and all(len(r)==99 for r in known),'exact99shape')
    need(all(type(known[u][v]) is int and known[u][v] in (-1,0,1) and known[u][v]==known[v][u] for u in range(99) for v in range(99)),'exact ternary symmetric scope')
    need(all(known[u][u]==0 for u in range(99)),'zero diagonal')
    need(known==partial['final_adjacency']==scope['known_adjacency_full99'],'complete separately audited rawscope')
    need(scope['initial_adjacency_full99']==partial['initial_adjacency'],'original fixed factor scope')
    pairs=[(u,v) for u,v in combinations(range(99),2) if known[u][v]==-1]
    edges=[dict(id=i,u=u,v=v) for i,(u,v) in enumerate(pairs,1)]
    need(len(edges)==1928 and model['edge_variables']==scope['edge_variables']==edges,'all freeedges bijective')
    need(all(type(row[x]) is int for row in model['edge_variables'] for x in ('id','u','v')),'integer edge mapping')
    need(model['schema']=='CONDITIONAL_TRIANGLE_FULL99_EXACT_PREFIX_CNF_V1' and scope['schema']=='FIXED_TRIANGLE_Q1_FULL99_SCOPE_V1','declared encoding schema')
    need(model['target_automorphism_assumed'] is False and scope['target_automorphism_assumed'] is False,'no automorphism premise')
    need(model['unrestricted_coverage_claim'] is False and scope['unrestricted_coverage_claim'] is False and model['branch_units']==[],'conditional scope only, no extra branches')
    need(model['propagation_artifact']==scope['propagation_artifact']==key(PARTIAL) and model['propagation_sha256']==scope['propagation_sha256']==digest(PARTIAL),'propagation identity')
    need(scope['archive_Q1_key']=='exact_partial_factor.Q1' and scope['archive_commit']=='85e705cc6c2a14d123120c93a847e30aaab1789e','fixed archive identity')
    need(scope['archive_Q1_path']=='attempts/wave151-triangle-root-factor/exact-results.json','exact Wave151 archive path')
    need(scope['forced_steps_count']==len(partial['steps'])==562,'exact separately audited Wave151 propagation length')
    need(scope['vertex_labels']==dict(triangle=[0,1,2],A_groups=[list(range(3+12*i,15+12*i))for i in range(3)],B=list(range(39,99))),'exact triangle and fibre vertex labels')
    refs=[[None if x<0 else bool(x) for x in row] for row in known]
    for e in edges:refs[e['u']][e['v']]=refs[e['v']][e['u']]=e['id']
    return refs,edges
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--propagation-gate',type=Path,required=True);parser.add_argument('--propagation-gate-sha256',required=True)
    parser.add_argument('--propagation-gate-status',required=True);args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(path,expected=None):
        path=Path(path);value=digest(path);need(expected is None or value==expected,'input hash '+str(path));bindings[key(path)]=value;return path
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    for name,value in PINS.items():bind(ROOT/name,value)
    propagation=read(args.propagation_gate,args.propagation_gate_sha256)
    need(args.propagation_gate_sha256=='bad7ddc51101377b8eaa284c650db8adcee5c261a0717073b90fc9e2347d7594','frozen independent propagation report')
    need(args.propagation_gate_status=='INDEPENDENT_TRIANGLE_Q1_PARTIAL99_PROPAGATION_PASS','specific propagation gate status')
    need(propagation['status']==args.propagation_gate_status and args.propagation_gate_status.startswith('INDEPENDENT_') and args.propagation_gate_status.endswith('_PASS'),'independent propagation approval')
    need(propagation['inputs_sha256'].get(key(PARTIAL))==digest(PARTIAL),'gate binds exact wave151 rawartifact')
    for name,value in propagation['inputs_sha256'].items():bind(ROOT/name,value)
    wave151=next(r for r in propagation['results'] if r['case']=='wave151')
    need(wave151['propagation_sha256']==digest(PARTIAL) and wave151['forced_entries']==562 and wave151['archive_Q1_key']=='exact_partial_factor.Q1','Wave151 subclaim within independent propagation report')
    model=read(D/'model.json');scope=read(D/'scope.json');partial=read(PARTIAL)
    manifest=read(D/'manifest.json');summary=read(D/'summary.json')
    for name,value in manifest['inputs_sha256'].items():bind(ROOT/name,value)
    refs,edges=scope_check(model,scope,partial)
    need(model['scope_path']==key(D/'scope.json') and model['scope_sha256']==digest(D/'scope.json'),'scope pathhash')
    need(len(model['counter_rows'])==4950 and model['degree_rows']==99 and model['pair_equality_rows']==4851,'row population')
    rejected=[]
    fields=('known_adjacency_full99','edge_variables','schema','target_automorphism_assumed','unrestricted_coverage_claim','branch_units','propagation_artifact','propagation_sha256')
    small={name:model[name] for name in fields}
    for label in ('fixed_entry','free_entry','missing_edge','duplicate_id','diagonal','symmetry','coverage','automorphism','extra_units'):
        bad=deepcopy(small)
        if label=='fixed_entry':bad['known_adjacency_full99'][0][1]=bad['known_adjacency_full99'][1][0]=0
        elif label=='free_entry':
            e=edges[0];bad['known_adjacency_full99'][e['u']][e['v']]=bad['known_adjacency_full99'][e['v']][e['u']]=0
        elif label=='missing_edge':bad['edge_variables'].pop()
        elif label=='duplicate_id':bad['edge_variables'][1]['id']=1
        elif label=='diagonal':bad['known_adjacency_full99'][0][0]=1
        elif label=='symmetry':bad['known_adjacency_full99'][0][1]=0
        elif label=='coverage':bad['unrestricted_coverage_claim']=True
        elif label=='automorphism':bad['target_automorphism_assumed']=True
        else:bad['branch_units']=[1]
        try:scope_check(bad,scope,partial)
        except ValueError:rejected.append(label)
        else:raise ValueError('corrupt scope accepted '+label)
    calibration=dict(threshold=gates.controls(),scope_corruptions_rejected=rejected)
    save(args.out/'controls.json',calibration)
    bind(__file__);bind(ROOT/'uv.lock');bind(ROOT/'docs/AUDIT_20260930_WAVE151_TRIANGLE_FULL99_ENCODING.md')
    save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,scope='Every rawclause of fixedwave151 full99 equalityCNF; no unrestricted containment assertion.',wall_seconds_limit=180,numerical_thresholds=None,numerical_thresholds_null_reason='Exact integers and Boolean truth relations.'))
    index=0;products=0
    with (D/'instance.cnf').open('rb') as stream:
        need(stream.readline()==b'p cnf 429779 1487778\n','exact DIMACS header')
        cursor=gates.ClauseCursor(stream,429779);audit=gates.GateAudit(cursor,len(edges))
        for u in range(99):
            terms=[x for x in refs[u] if type(x) is int];constant=sum(x is True for x in refs[u])
            audit.counter(model['counter_rows'][index],terms,14-constant,True,dict(kind='degree',vertex=u,original_bound=14,constant=constant));index+=1
        for u,v in tqdm(list(combinations(range(99),2)),desc='Independent fixed-triangle full99 equalities'):
            terms=[];constant=0
            for w in range(99):
                if w==u or w==v:continue
                x,y=refs[u][w],refs[v][w]
                if x is False or y is False:continue
                if x is True and y is True:constant+=1
                elif x is True:terms.append(y)
                elif y is True:terms.append(x)
                else:
                    row=model['product_variables'][products];products+=1
                    need(row['left']==x and row['right']==y and row['pair']==[u,v] and row['center']==w,'exact polynomial product mapping')
                    need(row['first_clause']==cursor.count+1 and row['clause_count']==3,'product clause range')
                    audit.gate(False,x,y,row['id']);terms.append(row['id'])
            entry=refs[u][v]
            if entry is True:constant+=1
            elif type(entry) is int:terms.append(entry)
            audit.counter(model['counter_rows'][index],terms,2-constant,True,dict(kind='pair_equality',pair=[u,v],original_bound=2,constant=constant));index+=1
            if index%250==0:need(time.monotonic()-start<180,'audit resource cap')
        need(stream.read()==b'','no trailing clauses')
    need(index==4950 and products==len(model['product_variables'])==104098,'complete row and product coverage')
    need(cursor.count==model['clauses']==summary['clauses']==1487778 and audit.top==model['variables']==summary['variables']==429779,'complete variable and clause coverage')
    package_checks=[]
    for package in read(D/'artifact_packages.json')['packages']:
        compressed=b''.join(bind(ROOT/p['path'],p['sha256']).read_bytes() for p in package['ordered_parts'])
        need(sha256(compressed).hexdigest()==package['compressed_stream_sha256'],'gzip stream hash')
        h=sha256();size=0
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as zipped:
            for chunk in iter(lambda:zipped.read(1<<20),b''):h.update(chunk);size+=len(chunk)
        need(h.hexdigest()==package['raw_sha256']==digest(ROOT/package['raw_path']) and size==package['raw_bytes'],'full recovered raw bytes')
        package_checks.append(dict(path=package['raw_path'],sha256=h.hexdigest(),bytes=size))
    need({x['path'] for x in package_checks}=={key(D/'model.json'),key(D/'instance.cnf')},'both rawpackages')
    need(all(digest(ROOT/p)==value for p,value in bindings.items()),'stable inputs')
    report=dict(status='INDEPENDENT_CONDITIONAL_WAVE151_TRIANGLE_FULL99_CNF_ENCODING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),verifier='/root/eight_domain_audit separate Wave151 conditional encoding checking path',claim_id='C-FIXED-WAVE151-TRIANGLE-FULL99-CNF-ENCODING',claim_revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',statement='The exact saved429779variable1487778clause CNF is satisfiable if and only if the specified labelled Wave151 triangle-root/Q1 partial99graph has a completion satisfying A^2=12I-A+2J. The independently checked562forced assignments preserve precisely that fixed-family completion problem.',scope='One immutable fixed labelled Q1 incidence factor; no claim that every target contains this factor, no target automorphism assumption, no solver result.',inputs_sha256=bindings,variables=audit.top,clauses=cursor.count,edge_variables=1928,product_variables=products,degree_rows=99,pair_equality_rows=4851,model_sha256=digest(D/'model.json'),cnf_sha256=digest(D/'instance.cnf'),scope_sha256=digest(D/'scope.json'),propagation_gate_sha256=digest(args.propagation_gate),gate_populations=dict(audit.gates),controls=calibration,package_checks=package_checks,derivation='Each bidirectional AND equals the indicated direct adjacency product. Every counter state equals its exact input-prefix threshold. All99degree counters impose14 and all4851unordered pair counters impose Aij+sum_w AiwAvw=2. Symmetry and zero diagonal then give every entry of the target identity. Conversely each fixed-scope target uniquely supplies the gate and counter values. The separate propagation gate shows the frozen forced assignments preserve the original fixedQ1 scope.',shared_components=['Frozen independent truth-relation and threshold checker reused with explicit source pin; no producer imported.','Separate independent fixed-factor assembly and ordered propagation gate is an explicit scope premise.','Python exact integers, JSON and gzip; tqdm progress.'],limitations=['Conditional fixed-family equivalence only; no unrestricted coverage.','SAT needs independent complete assignment and graph checking. UNSAT needs complete proof replay on this exact instance.','No solver performance claim or external review.'],target_resolution=False,solver_calls=0,external_review=False,elapsed_seconds=time.monotonic()-start)
    report['dependencies']=[dict(id='C-TRIANGLE-FIXED-Q1-PARTIAL99-PROPAGATION',revision=1,relation='uses_result')]
    report['adapted_from_independent_checker']=dict(path='acceleration/audit_20260930_triangle_full99_cnf.py',sha256=PINS['acceleration/audit_20260930_triangle_full99_cnf.py'],scope_change='Wave154 to exact Wave151 fixed factor; all raw clauses and scope controls rerun on changed inputs.')
    report['review_state']='CLEAR'
    report['artifact_availability']='LOCAL_ONLY'
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'),clauses=cursor.count,variables=audit.top)))
if __name__=='__main__':main()

