"""Independent unrestricted full99 scope, coverage and complete CNF audit.

Reuses the prior independently authored truth-table gate checker; imports no
producer. The new unrestricted scaffold is separately reconstructed here.
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
import audit_20260930_eight_full99_cnf_v1 as independent

ROOT=Path(__file__).resolve().parents[1]
need=independent.need
digest=independent.digest
key=independent.key
save=independent.save
HELPER_SHA='c956504752a937ffa6aa1ad84d4aa30d95db8723287970e76cbfd262b74ecf4c'
NORMALIZATION=ROOT/'acceleration/results/20260917_independent_review/root_scaffold.json'
NORMALIZATION_SHA='e96941c2bc050aad65b67a4f22a8968d588ae4dbe3cd7b7f22bfe84972a963a8'
DERIVATION=ROOT/'docs/AUDIT_20260930_UNRESTRICTED_FULL99_ENCODING_DERIVATION.md'


def expected_scope():
    labels=sorted([(a,b) for a in range(14) for b in range(a+1,14) if a//2!=b//2],
                  key=lambda pair:(pair[0]//2,pair[1]//2,pair[0]%2,pair[1]%2))
    known=[[0]*99 for _ in range(99)]
    for u,v in combinations(range(99),2):
        if u==0: value=int(v<=14)
        elif v<=14: value=int((u-1)//2==(v-1)//2)
        elif u<=14: value=int(u-1 in labels[v-15])
        else: value=-1
        known[u][v]=known[v][u]=value
    edges=[dict(u=u,v=v,id=i) for i,(u,v) in enumerate(combinations(range(15,99),2),1)]
    return known,labels,edges


def check_scope(model):
    known,labels,edges=expected_scope()
    observed=model['known_adjacency_full99']
    need(len(observed)==99 and all(len(row)==99 for row in observed),'raw99 shape')
    need(all(type(value) is int and value in (-1,0,1) for row in observed for value in row),'raw99 exact integer alphabet')
    need(observed==known,'complete unrestricted known/free scope')
    need(model['outer_labels']==list(map(list,labels)),'exact label order')
    need(model['edge_variables']==edges and all(type(row[name]) is int for row in model['edge_variables'] for name in ('u','v','id')),'complete3486 primary-edge bijection')
    need(model['fixed_K_edges']==[] and model['fixed_outer_nonedges']==[] and model['branch_units']==[], 'no outer restrictions or branches')
    need(model['target_automorphism_assumed'] is False,'no automorphism assumption')
    need(model['unknown_edges_outer']==[list(pair) for pair in combinations(range(84),2)],'all outer pairs free')
    need(model['fixed_scaffold_edges']==189 and model['schema']=='UNRESTRICTED_FULL99_EXACT_PREFIX_CNF_V1','scaffold/schema')
    need(model['normalization_dependency']==dict(id='C-ROOT-SCAFFOLD-NORMALIZATION',revision=1),'normalization revision')
    expressions=[[bool(x) if x>=0 else None for x in row] for row in known]
    for row in edges:expressions[row['u']][row['v']]=expressions[row['v']][row['u']]=row['id']
    need(sum(known[u][v]==1 for u,v in combinations(range(99),2))==189,'positive scaffold count')
    need(sum(known[u][v]==0 for u,v in combinations(range(99),2))==1176,'prescribed root/inner nonedges')
    need(all(sum(value==1 for value in known[u])==14 for u in range(15)),'root/inner degrees saturated')
    return expressions,edges


def normalization_controls():
    rook=[[int(u!=v and (u//3==v//3 or u%3==v%3)) for v in range(9)] for u in range(9)]
    def check_graph(graph):
        need(all(sum(row)==4 for row in graph),'rook degree')
        for u in range(9):
            need(graph[u][u]==0,'rook zero diagonal')
            for v in range(9):
                need(type(graph[u][v]) is int and graph[u][v] in (0,1) and graph[u][v]==graph[v][u],'rook binary symmetry')
                if u!=v:need(sum(graph[u][w]*graph[v][w] for w in range(9))==2-graph[u][v],'rook exact common neighbors')
        maps=0
        for root in range(9):
            neighbors=[v for v in range(9) if graph[root][v]]
            inner_edges=[pair for pair in combinations(neighbors,2) if graph[pair[0]][pair[1]]]
            need(len(inner_edges)==2 and all(sum(graph[u][v] for v in neighbors)==1 for u in neighbors),'rook local matching')
            labels={pair for pair in combinations(neighbors,2) if not graph[pair[0]][pair[1]]}
            actual=[]
            for outside in range(9):
                if outside==root or outside in neighbors:continue
                pair=tuple(v for v in neighbors if graph[v][outside])
                need(len(pair)==2 and pair in labels,'rook outside cross pair')
                actual.append(pair)
            need(len(actual)==len(set(actual))==4 and set(actual)==labels,'rook outside-pair bijection')
            maps+=1
        return maps
    roots=check_graph(rook);rejected=[]
    for u,v in combinations(range(9),2):
        bad=deepcopy(rook);bad[u][v]^=1;bad[v][u]^=1
        try:check_graph(bad)
        except ValueError:rejected.append([u,v])
        else:raise ValueError('rook edge corruption accepted')
    return dict(known_rook9_valid=True,root_pair_bijections_checked=roots,corrupted_unordered_edge_toggles_rejected=rejected,
                scope='Calibrates normalization bookkeeping, not the universal theorem')


def scope_controls(model):
    # Copy only scope fields, never the large counter/product arrays.
    fields=('known_adjacency_full99','outer_labels','edge_variables','fixed_K_edges','fixed_outer_nonedges','branch_units',
            'target_automorphism_assumed','unknown_edges_outer','fixed_scaffold_edges','schema','normalization_dependency')
    base={name:model[name] for name in fields};check_scope(base);rejected=[]
    for label in ('fixed_outer_edge','fixed_outer_absence','wrong_root_edge','missing_variable','duplicate_variable',
                  'wrong_label','added_branch','claimed_automorphism'):
        bad=deepcopy(base)
        if label in ('fixed_outer_edge','fixed_outer_absence'):
            bad['known_adjacency_full99'][15][16]=bad['known_adjacency_full99'][16][15]=int(label=='fixed_outer_edge')
        elif label=='wrong_root_edge':bad['known_adjacency_full99'][0][1]=bad['known_adjacency_full99'][1][0]=0
        elif label=='missing_variable':bad['edge_variables'].pop()
        elif label=='duplicate_variable':bad['edge_variables'][1]=bad['edge_variables'][0]
        elif label=='wrong_label':bad['outer_labels'][0]=[0,1]
        elif label=='added_branch':bad['branch_units']=[1]
        else:bad['target_automorphism_assumed']=True
        try:check_scope(bad)
        except ValueError:rejected.append(label)
        else:raise ValueError('corrupt scope accepted: '+label)
    return dict(positive_unrestricted_scope_passed=True,corrupted_scope_artifacts_rejected=rejected)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--model-sha256',required=True);parser.add_argument('--cnf-sha256',required=True)
    parser.add_argument('--producer-sha256',required=True);parser.add_argument('--seconds',type=float,default=900)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();bindings={}
    def bind(path,expected=None):
        observed=digest(path);need(expected is None or observed==expected,'hash mismatch: '+str(path));bindings[key(path)]=observed
        return Path(path)
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    bind(independent.__file__,HELPER_SHA)
    normalization=read(NORMALIZATION,NORMALIZATION_SHA)
    need(normalization['status']=='INDEPENDENT_ROOT_SCAFFOLD_DERIVATION_AND_CALIBRATION_PASS' and normalization['claim_revision']==1,'root normalization gate')
    for name,value in normalization['inputs_sha256'].items():bind(ROOT/name,value)
    model_path,cnf_path=args.run/'model.json',args.run/'instance.cnf'
    model=read(model_path,args.model_sha256);bind(cnf_path,args.cnf_sha256)
    manifest=read(args.run/'manifest.json');summary=read(args.run/'summary.json')
    for name,value in manifest['input_hashes'].items():bind(ROOT/name,value)
    producer_path=ROOT/'acceleration/theory_20260930_unrestricted_full99_cnf.py';bind(producer_path,args.producer_sha256)
    need(model['normalization_audit']==key(NORMALIZATION) and model['normalization_audit_sha256']==NORMALIZATION_SHA,'model normalization identity')
    scope=read(ROOT/model['scope_path'],model['scope_sha256'])
    expressions,edges=check_scope(model)
    need(scope['known_adjacency_full99']==model['known_adjacency_full99'] and scope['edge_variables']==edges,'preflight scope agrees')
    calibration=dict(threshold=independent.controls(),normalization=normalization_controls(),scope=scope_controls(model))
    save(args.out/'controls.json',calibration)
    need(model['degree_rows']==99 and model['pair_cap_rows']==4851 and len(model['counter_rows'])==4950,'all row populations')
    for path in (__file__,DERIVATION,ROOT/'uv.lock',ROOT/'pyproject.toml'):bind(path)
    source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source_commit,
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
        question='Does the complete unrestricted raw CNF encode exactly the target after a universally available root normalization?',
        scope='All3486outerpairs free; all4950degree/cap rows and everyraw clause; no solver',limits=dict(wall_seconds=args.seconds),
        numerical_threshold=None,numerical_threshold_null_reason='Exact Boolean truth tables and Python integers'))
    counter_index=0;product_index=0
    with cnf_path.open('rb') as stream:
        need(stream.readline().split()==[b'p',b'cnf',str(model['variables']).encode(),str(model['clauses']).encode()],'DIMACS header')
        cursor=independent.ClauseCursor(stream,model['variables']);audit=independent.GateAudit(cursor,len(edges))
        for u in range(99):
            inputs=[x for x in expressions[u] if type(x) is int];constant=sum(x is True for x in expressions[u])
            audit.counter(model['counter_rows'][counter_index],inputs,14-constant,True,dict(kind='degree',vertex=u,original_bound=14,constant=constant));counter_index+=1
        for u,v in tqdm(list(combinations(range(99),2)),desc='Independent unrestricted full99 clauses'):
            inputs=[];constant=0
            for w in range(99):
                if w in (u,v):continue
                left,right=expressions[u][w],expressions[v][w]
                if left is False or right is False:continue
                if left is True and right is True:constant+=1
                elif left is True:inputs.append(right)
                elif right is True:inputs.append(left)
                else:
                    need(product_index<len(model['product_variables']),'missing product')
                    row=model['product_variables'][product_index];product_index+=1
                    need(row['left']==left and row['right']==right and row['pair']==[u,v] and row['center']==w,'exact direct product mapping')
                    need(row['first_clause']==cursor.count+1 and row['clause_count']==3,'product clause range')
                    audit.gate(False,left,right,row['id']);inputs.append(row['id'])
            adjacent=expressions[u][v]
            if adjacent is True:constant+=1
            elif type(adjacent) is int:inputs.append(adjacent)
            residual=2-constant;need(residual>=0,'impossible fixed cap')
            audit.counter(model['counter_rows'][counter_index],inputs,min(residual,len(inputs)),False,
                dict(kind='pair_cap',pair=[u,v],original_bound=2,constant=constant,residual_before_trivial_cap_fold=residual));counter_index+=1
            if counter_index%250==0:need(time.monotonic()-started<args.seconds,'independent audit wall cap')
        need(stream.read()==b'','extra raw clause bytes')
    need(counter_index==4950 and product_index==len(model['product_variables'])==3486*82,'complete polynomial/row coverage')
    need(cursor.count==model['clauses'] and audit.top==model['variables'],'complete clause/variable coverage')
    need(summary['complete'] is True and summary['clauses']==cursor.count and summary['variables']==audit.top and summary['products']==product_index,'producer summary counts')
    packages=read(args.run/'artifact_packages.json');package_checks=[];raw_paths=[]
    for package in packages['packages']:
        compressed=b''
        for part in package['ordered_parts']:
            path=bind(ROOT/part['path'],part['sha256']);need(path.stat().st_size==part['bytes']<10*1024*1024,'part size')
            compressed+=path.read_bytes()
        need(sha256(compressed).hexdigest()==package['compressed_stream_sha256'],'compressed stream identity')
        h=sha256();size=0
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as zipped:
            for block in iter(lambda:zipped.read(1<<20),b''):h.update(block);size+=len(block)
        need(h.hexdigest()==package['raw_sha256']==digest(ROOT/package['raw_path']) and size==package['raw_bytes'],'complete independent decompression')
        raw_paths.append(package['raw_path'])
        package_checks.append(dict(raw_path=package['raw_path'],raw_sha256=h.hexdigest(),raw_bytes=size,independent_decompression='PASS'))
    need(set(raw_paths)=={key(model_path),key(cnf_path)} and len(raw_paths)==2,'both public raw packages')
    need(all(digest(ROOT/name)==value for name,value in bindings.items()),'input stability')
    report=dict(status='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS',claim_id='C-UNRESTRICTED-FULL99-PREFIX-CNF-ENCODING',claim_revision=1,
        recommendation='VERIFIED',kind='encoding',basis=['DERIVED','COMPUTED'],timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=source_commit,command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent unrestricted scope/coverage derivation plus complete raw polynomial and truth-relation clause comparison',
        statement='The exact recorded CNF is satisfiable if and only if there exists a99x99 symmetric binary zero-diagonal adjacency A satisfying A^2=12I-A+2J. Every satisfying assignment decodes to such a normalized target, and every target admits the recorded scaffold labeling and an auxiliary extension.',
        scope='Unrestricted target equivalence via universally available root normalization; all3486outerpairs are free and no nontrivial automorphism is assumed.',
        assumptions=['Only the target definition: order99, symmetry, binary adjacency, zero diagonal, and exact A^2=12I-A+2J.',
                     'Exact recorded raw CNF/model bytes and audited Boolean semantics.'],
        dependencies=[dict(id='C-ROOT-SCAFFOLD-NORMALIZATION',revision=1,relation='normalization')],
        inputs_sha256=bindings,controls=calibration,written_derivation=key(DERIVATION),
        model_sha256=digest(model_path),cnf_sha256=digest(cnf_path),producer_sha256=digest(producer_path),
        fixed_positive_scaffold_edges=189,prescribed_root_or_inner_nonedges=1176,fixed_outer_edges=0,fixed_outer_nonedges=0,
        unknown_outer_edges=3486,variables=audit.top,edge_variables=3486,product_variables=product_index,prefix_variables=audit.top-3486-product_index,
        clauses=cursor.count,degree_rows=99,pair_cap_rows=4851,gate_clause_populations=dict(audit.gates),folded_alias_states=audit.aliases,
        independent_package_checks=package_checks,degree_cap_sum=dict(degree=14,edges=693,common_neighbor_sum=9009,cap_lhs_sum=9702,cap_upper_sum=9702),
        producer_imported=False,solver_launched=False,unrestricted_encoding_coverage=True,
        shared_components=['The prior independently authored and hash-pinned audit_20260930_eight_full99_cnf_v1 truth-table gate/threshold checker is reused; this is not a second independent gate implementation.',
            'Python standard library exact integers, JSON and gzip; tqdm progress output.',
            'Historical root normalization audit is authenticated; coverage is independently rederived in the linked written proof.'],
        limitations=['An encoding equivalence is not a target graph or nonexistence proof.',
                     'A SAT assignment requires a separately calibrated full decoded99graph validator and complete raw clause checking.',
                     'An UNSAT result requires a complete saved proof and independently authenticated checker replay against these exact bytes.',
                     'No solver performance, novelty, or external review claim.'],
        target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-started)
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],clauses=cursor.count,variables=audit.top,sha256=digest(args.out/'summary.json'))))


if __name__=='__main__':main()
