"""Independent all-clause audit of the target-necessary25row projection."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_one_c2_raw25 as raw

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_one_c2_row_cnf'
GATE=ROOT/'acceleration/results/20260930_independent_review/triangle_factor_components/summary.json'
GATE_SHA='03d84677f34e0a209f9331c32efcd0b843dae60b97dbf9e9102b85171a5fef5b'
SUMMARY_SHA='7a0ad5c55fefaaf288d74f590e0cedfd439a8ca9d64a5d3bd49b3d07d9e1cb16'
need,digest,key,save=raw.need,raw.digest,raw.key,raw.save
gates=raw.prior.base.gates

def scope_check(model,scope):
    g,columns,known,entries,refs,components=raw.derive_scope()
    for obj in [model,scope]:
        need(obj['known_incidence_rows']==known and obj['target_gram_rows']==g and obj['entry_variables']==entries and obj['components']==components,'all1500scope/650primary/625Gram entries')
        need(all(type(x) is int for row in obj['known_incidence_rows'] for x in row),'integer incidence types')
        need(all(type(x) is int for row in obj['target_gram_rows'] for x in row),'integer Gram types')
        need(obj['selected_original_rows']==list(range(25)) and obj['abstract_36_factor_projection_claimed'] is False,'exact selectedrows and limited necessary implication')
    need(scope['edge_columns_C0']==list(map(list,columns)),'canonical C0column labels')
    parent=raw.prior.base.D/'scope.json';kernel=raw.prior.compaudit.D/'kernel_certificate.json'
    need(scope['parent_scope']==key(parent) and scope['parent_scope_sha256']==digest(parent),'parent identity')
    need(scope['kernel_certificate']==key(kernel) and scope['kernel_certificate_sha256']==digest(kernel),'kernel identity')
    need(scope['selected_C2_coordinate']==0 and scope['selected_C2_graph_vertex']==27 and scope['C2_rows_included']==[0],'selected named C2row')
    need(scope['row_sum']==10 and scope['complete_fibres']==[0,1] and scope['column_sum_per_complete_fibre']==2,'exact incomplete-fibre margins')
    need(scope['partial_component_column_upper_bound']==2 and scope['column_pair_overlap_upper_bound']==2,'both target-necessary capacities')
    need(scope['C1_free'] is True and scope['D_included'] is False and scope['unrestricted_target_coverage'] is False and scope['target_automorphism_assumed'] is False,'freeQ1 and exact conditional target scope')
    need(model['full_target_graph_encoded'] is False and model['complete36row_factor_encoded'] is False,'not full target/factor')
    need(model['schema']=='TRIANGLE_ONE_C2_ROW_TARGET_PREFIX_CNF_V1' and scope['schema']=='FIXED_TRIANGLE_ONE_C2_ROW_TARGET_SCOPE_V1','exact25row schemas')
    need(model['scope_path']==key(D/'scope.json') and model['scope_sha256']==digest(D/'scope.json'),'scope binding')
    return g,columns,known,entries,refs,components

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(path,expected=None):
        path=Path(path);value=digest(path);need(expected is None or value==expected,'hash '+str(path));bindings[key(path)]=value;return path
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    try:
        gate=read(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_TRIANGLE_COMPONENT_FACTOR_CNF_ENCODING_PASS','independent scope/kernel premise')
        for path,value in gate['inputs_sha256'].items():bind(ROOT/path,value)
        summary=read(D/'summary.json',SUMMARY_SHA);manifest=read(D/'manifest.json')
        for path,value in manifest['inputs_sha256'].items():bind(ROOT/path,value)
        for name,record in summary['outputs'].items():need(bind(D/name,record['sha256']).stat().st_size==record['bytes'],'exact artifact bytes')
        model=read(D/'model.json');scope=read(D/'scope.json');g,columns,known,entries,refs,components=scope_check(model,scope)
        rejected=[]
        fields=['known_incidence_rows','target_gram_rows','entry_variables','components','selected_original_rows','abstract_36_factor_projection_claimed','full_target_graph_encoded','complete36row_factor_encoded','schema','scope_path','scope_sha256']
        for label in ['fixed_entry','free_C2_entry','Gram','primary_ID','component','selectedrow','wrong_C2_coordinate','complete_C2_fibre','cap3','Q1_fixed','abstract_factor_claim','unrestricted_claim']:
            m,s=deepcopy({k:model[k] for k in fields}),deepcopy(scope)
            if label=='fixed_entry':m['known_incidence_rows'][0][0]^=1
            elif label=='free_C2_entry':e=next(e for e in entries if e['row']==24);m['known_incidence_rows'][24][e['column']]=0
            elif label=='Gram':m['target_gram_rows'][24][0]+=1
            elif label=='primary_ID':m['entry_variables'][-1]['id']=649
            elif label=='component':m['components'][0][0]=m['components'][1][0]
            elif label=='selectedrow':m['selected_original_rows'][-1]=25
            elif label=='wrong_C2_coordinate':s['selected_C2_coordinate']=1
            elif label=='complete_C2_fibre':s['complete_fibres']=[0,1,2]
            elif label=='cap3':s['column_pair_overlap_upper_bound']=3
            elif label=='Q1_fixed':s['C1_free']=False
            elif label=='abstract_factor_claim':m['abstract_36_factor_projection_claimed']=True
            else:s['unrestricted_target_coverage']=True
            try:scope_check(m,s)
            except ValueError:rejected.append(label)
            else:raise ValueError('corrupt scope accepted '+label)
        controls=dict(threshold=gates.controls(),scope_corruptions_rejected=rejected);save(args.out/'controls.json',controls)
        rowi=0;prodi=0;product_counts={}
        with (D/'instance.cnf').open('rb') as stream:
            need(stream.readline()==b'p cnf 74814 256151\n','exact raw25header')
            cursor=gates.ClauseCursor(stream,74814);audit=gates.GateAudit(cursor,650)
            def counter(terms,bound,eq,metadata):
                nonlocal rowi
                audit.counter(model['counter_rows'][rowi],terms,bound,eq,metadata);rowi+=1
            def multiply(x,y,metadata,terms):
                nonlocal prodi
                if x is False or y is False:return 0
                if x is True and y is True:return 1
                if x is True:terms.append(y);return 0
                if y is True:terms.append(x);return 0
                p=model['product_variables'][prodi];prodi+=1
                need(p==dict(id=audit.top+1,left=x,right=y,**metadata,first_clause=cursor.count+1,clause_count=3),'exact independently reconstructed product')
                audit.gate(False,x,y,p['id']);terms.append(p['id']);product_counts[metadata['kind']]=product_counts.get(metadata['kind'],0)+1
                return 0
            for r in range(12,25):counter([x for x in refs[r] if type(x) is int],10,True,dict(kind='row_margin',row=r,constant=0,original_bound=10))
            for d in range(60):counter([refs[r][d] for r in range(12,24) if type(refs[r][d]) is int],2,True,dict(kind='column_margin',fibre=1,column=d,constant=0,original_bound=2))
            for a in range(12):
                for b in range(12,25):counter([refs[b][d] for d in range(60) if known[a][d] and type(refs[b][d]) is int],g[a][b],True,dict(kind='C0_cross_gram',pair=[a,b],constant=0,original_bound=g[a][b]))
            for a,b in combinations(range(12,25),2):
                terms=[];constant=0
                for d in range(60):constant+=multiply(refs[a][d],refs[b][d],dict(kind='row_gram',pair=[a,b],column=d),terms)
                counter(terms,g[a][b]-constant,True,dict(kind='unknown_pair_gram',pair=[a,b],constant=constant,original_bound=g[a][b]))
            need(rowi==307,'all exact Gram/margin equations')
            for ci,group in enumerate(components):
                support=[r for r in group if r<25]
                for d in range(60):
                    constant=sum(refs[r][d] is True for r in support);terms=[refs[r][d] for r in support if type(refs[r][d]) is int]
                    counter(terms,2-constant,False,dict(kind='partial_component_capacity',component=ci,column=d,raw_component_rows=group,included_rows=support,constant=constant,original_bound=2))
            for d,e in combinations(range(60),2):
                terms=[];constant=0
                for r in range(25):constant+=multiply(refs[r][d],refs[r][e],dict(kind='column_overlap',column_pair=[d,e],row=r),terms)
                counter(terms,2-constant,False,dict(kind='column_pair_overlap',column_pair=[d,e],included_rows=list(range(25)),constant=constant,original_bound=2))
            need(stream.read()==b'','no trailing rawCNF')
        need(rowi==len(model['counter_rows'])==2257 and prodi==len(model['product_variables'])==19125,'all rows/products checked')
        need(audit.top==model['variables']==74814 and cursor.count==model['clauses']==256151,'all variables/clauses checked')
        packages=[]
        for p in read(D/'artifact_packages.json')['packages']:
            compressed=b''.join(bind(ROOT/x['path'],x['sha256']).read_bytes() for x in p['ordered_parts'])
            need(sha256(compressed).hexdigest()==p['compressed_stream_sha256'],'gzip stream hash')
            recovered=gzip.decompress(compressed);need(len(recovered)==p['raw_bytes'] and sha256(recovered).hexdigest()==p['raw_sha256']==digest(ROOT/p['raw_path']),'complete exact artifact recovery')
            packages.append(dict(path=p['raw_path'],sha256=p['raw_sha256'],bytes=len(recovered)))
        for path in [Path(__file__),Path(raw.__file__),Path(raw.prior.__file__),ROOT/'docs/AUDIT_20260930_TRIANGLE_ONE_C2_ROW_ENCODING.md']:bind(path)
        need(all(digest(ROOT/p)==v for p,v in bindings.items()),'stable exact inputs')
        report=dict(status='INDEPENDENT_TRIANGLE_ONE_C2_ROW_CNF_ENCODING_PASS',claim_id='C-FIXED-TRIANGLE-ONE-C2-ROW-TARGET-PROJECTION-CNF',claim_revision=1,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit independent raw25 polynomial/completeclause checker',kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
          statement='The exact74814variable256151clause CNF is satisfiable iff the declared binary25x60incidence problem is feasible: frozen principal Gram, row10/complete-fibre-column2 margins, component partial counts<=2 and all1770column overlaps<=2. Every target containing the fixed39core supplies a normalized such model. No extension converse or preservation of every abstract36rowGram factor is claimed.',
          dependencies=[dict(id='C-FIXED-TRIANGLE-JOINT-BINARY-FACTOR-CNF-ENCODING',revision=1,relation='normalization'),dict(id='C-FIXED-TRIANGLE-FACTOR-COMPONENT-BALANCE',revision=1,relation='uses_result')],additional_assumptions=['For the one-way fixed-target implication only: A^2=12I-A+2J, so every pair has at most2common neighbors.'],scope='One labelled fixed39core target projection, selected C2coordinate0; no target automorphism or unrestricted core containment.',variables=74814,clauses=256151,primary_entries=650,forced_zeros=130,AND_products=19125,product_counts=product_counts,counter_rows=2257,equalities=307,component_caps=180,column_pair_caps=1770,controls=controls,package_checks=packages,
          shared_components=['Frozen independently authored rawcore/Gram/component reconstruction reused.','Frozen independent truth-relation GateAudit helper reused, with every new clause reconstructed.','No producer imports.'],limitations=['SAT yields only25rows.','UNSAT conditional exclusion requires a complete independently replayed proof.','Column caps are target-necessary; not proved for arbitrary abstract36row factors.'],target_resolution=False,solver_calls=0,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e)));raise

if __name__=='__main__':main()
