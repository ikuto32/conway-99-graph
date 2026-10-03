"""Independent arbitrary-core factor scope and complete clause reconstruction."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,product
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import audit_20260930_eight_full99_cnf_v1 as gates

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_variable_core_factor_cnf'
COVERAGE=ROOT/'acceleration/results/20260930_independent_review/unrestricted_triangle_factor/summary.json'
COVERAGE_SHA='a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd'
CANDIDATE=ROOT/'acceleration/results/20260930_unrestricted_triangle_factor/summary.json'
CANDIDATE_SHA='fecb50f01e6548c79e486068eeea3ca41dd6922ed4cf74686d9757ae0061b2eb'
GATES_SHA='c956504752a937ffa6aa1ad84d4aa30d95db8723287970e76cbfd262b74ecf4c'
need,digest,key,save=gates.need,gates.digest,gates.key,gates.save

def primary_scope():
    columns=[list(pair) for pair in combinations(range(12),2) if pair[1]!=(pair[0]^1)]
    known=[[int(a in pair) for pair in columns] for a in range(12)]+[[-1]*60 for _ in range(24)]
    entries=[dict(id=60*(r-12)+d+1,row=r,column=d) for r in range(12,36) for d in range(60)]
    f=[[[60*(12*g+a)+d+1 for d in range(60)] for a in range(12)] for g in range(2)]
    top=1440;matching_records=[];ms=[]
    for fibre in [1,2]:
        m=[[False]*12 for _ in range(12)]
        for a,b in combinations(range(12),2):
            top+=1;m[a][b]=m[b][a]=top;matching_records.append(dict(id=top,fibre=fibre,endpoints=[a,b]))
        ms.append(m)
    p=[];permutation_records=[]
    for a in range(12):
        row=[]
        for b in range(12):top+=1;row.append(top);permutation_records.append(dict(id=top,row=a,column=b))
        p.append(row)
    need(top==1716,'entire primary universe')
    return columns,known,entries,f,ms,matching_records,p,permutation_records

def scope_check(model,scope):
    columns,known,entries,f,ms,matches,p,perms=primary_scope()
    expected=dict(schema='ARBITRARY_TRIANGLE_CORE_FACTOR_SCOPE_V1',normalization_candidate_path=key(CANDIDATE),normalization_candidate_sha256=CANDIDATE_SHA,
      normalization_claim_id='C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION',normalization_claim_revision=1,normalization_coverage_gate=key(COVERAGE),normalization_coverage_gate_sha256=COVERAGE_SHA,
      M0=[a^1 for a in range(12)],cross01=list(range(12)),cross02=list(range(12)),
      M1_M2_scope='All symmetric zero-diagonal binary12x12 matrices with every row sum1.',P_scope='All binary12x12 matrices with every row and column sum1; rowsA1,columnsA2.',
      core_extra_restrictions=[],target_automorphism_assumed=False,edge_columns_C0=columns,known_incidence_rows=known,entry_variables=entries,matching_variables=matches,permutation_variables=perms,
      symbolic_C1=f[0],symbolic_C2=f[1],symbolic_M1=ms[0],symbolic_M2=ms[1],symbolic_P=p,row_sum=10,fibre_column_sum=2,mixed_cap_upper_bound=2,distinct_column_cap_upper_bound=2,
      component_restrictions=False,fixed_Q1_Q2=False,zero_incidence_folds=0,residual_D_included=False,full_target_graph_encoded=False,
      target_relation='Every target admits this normalized necessary factor scope by the pinned independent coverage gate; new CNF equivalence still requires independent review.')
    need(scope==expected,'entire unrestricted normalized scope and all primary maps')
    for name,value in [('known_incidence_rows',known),('entry_variables',entries),('matching_variables',matches),('permutation_variables',perms)]:need(model[name]==value,'model raw primary '+name)
    need(model['schema']=='ARBITRARY_TRIANGLE_CORE_FACTOR_CHANNEL_PREFIX_CNF_V1' and model['scope_path']==key(D/'scope.json') and model['scope_sha256']==digest(D/'scope.json'),'raw model scope binding')
    for name,value in [('primary_variables',1716),('selector_channel_variables',2880),('component_restrictions',False),('zero_incidence_folds',0),('residual_D_included',False),('full_target_graph_encoded',False),('solver_calls',0),('normalization_candidate_sha256',CANDIDATE_SHA),('normalization_coverage_gate_sha256',COVERAGE_SHA)]:need(model[name]==value and type(model[name]) is type(value),'scope metadata '+name)
    need(model['independent_coverage_gate_required_before_solver'] is True,'explicit coverage gate requirement')
    return columns,known,entries,f,ms,matches,p,perms

def selector_clauses(selector,inputvar,outputvar):
    refs=[selector,inputvar,outputvar]
    need(len(set(refs))==3 and all(type(x) is int and x>0 for x in refs),'three distinct channel references')
    # Each forbidden truth assignment yields its exact blocking clause.
    return [tuple(sorted(refs[i] if not bit else -refs[i] for i,bit in enumerate(bits))) for bits in product([False,True],repeat=3) if bits[0] and bits[1]!=bits[2]]

def channel_controls():
    checked=0
    for n in range(1,5):
        for selected in range(n):
            for bits in product([False,True],repeat=n):
                for z in [False,True]:
                    values=[False]+[i==selected for i in range(n)]+list(bits)+[z]
                    clauses=[c for i in range(n) for c in selector_clauses(i+1,n+i+1,2*n+1)]
                    observed=all(any(values[abs(lit)]==(lit>0) for lit in c) for c in clauses)
                    need(observed==(z==bits[selected]),'complete one-hot channel relation');checked+=1
    absent=[]
    for z in [False,True]:
        values=[False,False,False,z];clauses=selector_clauses(1,2,3)
        absent.append(all(any(values[abs(lit)]==(lit>0) for lit in c) for c in clauses))
    need(absent==[True,True],'missing selector leaves output unconstrained')
    return dict(one_hot_input_output_cases=checked,zero_selector_both_outputs_allowed=True)

def audit_clauses(model,scope,path):
    columns,known,entries,f,ms,matches,p,perms=scope_check(model,scope)
    rows=model['counter_rows'];products=model['product_variables'];rowi=0;prodi=0
    with Path(path).open('rb') as stream:
        need(stream.readline()==('p cnf %d %d\n'%(model['variables'],model['clauses'])).encode(),'exact full CNF header')
        cursor=gates.ClauseCursor(stream,model['variables']);audit=gates.GateAudit(cursor,1716)
        def counter(terms,bound,equality,annotation):
            nonlocal rowi
            audit.counter(rows[rowi],[x for x in terms if type(x) is int],bound,equality,annotation);rowi+=1
        def conjunction(x,y,annotation):
            nonlocal prodi
            record=products[prodi];prodi+=1
            need(record==dict(id=audit.top+1,left=x,right=y,**annotation,first_clause=cursor.count+1,clause_count=3),'all product mappings')
            audit.gate(False,x,y,record['id']);return record['id']
        for fibre,m in enumerate(ms,1):
            for a in range(12):counter(m[a],1,True,dict(kind='matching_degree',fibre=fibre,row=a))
        for a in range(12):
            counter(p[a],1,True,dict(kind='permutation_degree',axis='row',index=a))
            counter([p[b][a] for b in range(12)],1,True,dict(kind='permutation_degree',axis='column',index=a))
        for fibre in [1,2]:
            block=f[fibre-1]
            for a in range(12):counter(block[a],10,True,dict(kind='incidence_row',row=12*fibre+a))
            for d in range(60):counter([block[a][d] for a in range(12)],2,True,dict(kind='incidence_column',fibre=fibre,column=d))
        for g in range(2):
            for a in range(12):
                for b in range(12):
                    terms=[f[g][b][d] for d in range(60) if known[a][d]]+[ms[g][a][b],p[b][a] if g==0 else p[a][b]]
                    counter(terms,2-int(a==b)-int((a^1)==b),True,dict(kind='C0_cross_Gram',pair=[a,12*(g+1)+b],delta=int(a==b),M0_constant=int((a^1)==b)))
            for a,b in combinations(range(12),2):
                terms=[conjunction(f[g][a][d],f[g][b][d],dict(kind='within_fibre_incidence',pair=[12*(g+1)+a,12*(g+1)+b],column=d)) for d in range(60)]
                counter(terms+[ms[g][a][b]],1,True,dict(kind='within_fibre_Gram',pair=[12*(g+1)+a,12*(g+1)+b]))
        for a in range(12):
            for b in range(12):
                terms=[conjunction(f[0][a][d],f[1][b][d],dict(kind='cross_fibre_incidence',pair=[12+a,24+b],column=d)) for d in range(60)]+[p[a][b]]
                terms.extend(conjunction(ms[0][a][k],p[k][b],dict(kind='M1P',row=a,column=b,middle=k)) for k in range(12) if k!=a)
                terms.extend(conjunction(p[a][k],ms[1][k][b],dict(kind='PM2',row=a,column=b,middle=k)) for k in range(12) if k!=b)
                counter(terms,2-int(a==b),True,dict(kind='C1_C2_Gram',pair=[12+a,24+b],delta=int(a==b)))
        need(model['gram_prefix_end']==dict(variables=audit.top,clauses=cursor.count,counter_rows=rowi),'complete Gram prefix boundary')
        need(rowi==756 and prodi==len(products)==19728,'complete Gram equations and products')
        caprecords=[];compact_clauses=0
        for d,e in combinations(range(60),2):
            common=[r for r in range(12) if known[r][d] and known[r][e]];need(len(common)<=1,'distinct C0 pair intersection')
            if not common:continue
            for a in range(12):
                for b in range(12):
                    caprecords.append([d,e,a,b,cursor.count+1]);clause=tuple(sorted([-f[0][a][d],-f[0][a][e],-f[1][b][d],-f[1][b][e]]))
                    cursor.consume([clause]);compact_clauses+=1
        need(model['column_cap_records']==caprecords and len(caprecords)==77760,'all variable-core compact column clauses')
        need(model['column_cap_record_format']==['column_d','column_e','C1_local_row','C2_local_row','absolute_clause_number'],'compact record schema')
        channels=[('U1',ms[0],f[0]),('U2',ms[1],f[1]),('V1',p,f[1]),('V2',list(map(list,zip(*p))),f[0])];outputs={};channel_clauses=0
        need(len(model['selector_channel_groups'])==4,'exact four channel groups')
        for record,(name,selector,inputs) in zip(model['selector_channel_groups'],channels):
            output=[[audit.top+60*a+d+1 for d in range(60)] for a in range(12)];audit.top+=720;first=cursor.count+1;active=0
            for a in range(12):
                for k in range(12):
                    s=selector[a][k]
                    if s is False:continue
                    active+=1
                    for d in range(60):cursor.consume(selector_clauses(s,inputs[k][d],output[a][d]))
            expected=dict(name=name,selector_matrix=selector,input_matrix=inputs,output_matrix=output,loop_order=['output_row','source_row','column'],false_selectors_omitted=True,active_selector_entries=active,first_clause=first,clause_count=cursor.count-first+1,semantic_relation='For the unique selected source row, output equals that source input bit.',clause_order=['-selector -input output','-selector input -output'])
            need(record==expected,'entire selector channel mapping and clause interval');outputs[name]=output;channel_clauses+=cursor.count-first+1
        for a in range(12):
            for d in range(60):
                constant=known[a][d]+known[a^1][d]
                counter([f[0][a][d],f[1][a][d]],2-constant,False,dict(kind='mixed_column_cap',row=a,column=d,constant=constant,original_bound=2))
                counter([f[0][a][d],outputs['U1'][a][d],outputs['V1'][a][d]],2-known[a][d],False,dict(kind='mixed_column_cap',row=12+a,column=d,constant=known[a][d],original_bound=2))
                counter([f[1][a][d],outputs['U2'][a][d],outputs['V2'][a][d]],2-known[a][d],False,dict(kind='mixed_column_cap',row=24+a,column=d,constant=known[a][d],original_bound=2))
        need(stream.read()==b'','all raw clauses consumed; no hidden restrictions')
    need(rowi==len(rows)==2916 and cursor.count==model['clauses'] and audit.top==model['variables'] and channel_clauses==66240,'complete counts and auxiliary universe')
    return dict(variables=audit.top,clauses=cursor.count,primary_variables=1716,incidence_variables=1440,matching_variables=132,permutation_variables=144,AND_products=prodi,equality_rows=756,mixed_cap_rows=2160,column_cap_clauses=compact_clauses,selector_channel_variables=2880,selector_channel_clauses=channel_clauses)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--summary-sha256',required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(path,expected=None):
        path=Path(path);v=digest(path);need(expected is None or v==expected,'hash '+str(path));bindings[key(path)]=v;return path
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    try:
        coverage=read(COVERAGE,COVERAGE_SHA);need(coverage['status']=='INDEPENDENT_UNRESTRICTED_TRIANGLE_FACTOR_NORMALIZATION_PASS','universal independent coverage gate')
        for p,v in coverage['inputs_sha256'].items():bind(ROOT/p,v)
        bind(Path(gates.__file__),GATES_SHA)
        summary=read(D/'summary.json',args.summary_sha256);manifest=read(D/'manifest.json')
        for p,v in manifest['inputs_sha256'].items():bind(ROOT/p,v)
        for p,r in summary['outputs'].items():need(bind(D/p,r['sha256']).stat().st_size==r['bytes'],'frozen artifact length')
        model=read(D/'model.json');scope=read(D/'scope.json');scope_check(model,scope)
        calibration=dict(threshold=gates.controls(),selector_channels=channel_controls());rejected=[]
        for label in ['extra_fixed_incidence','matching_mapping','transpose_P','core_restriction','component_restriction','scope_bound']:
            bad=deepcopy(scope)
            if label=='extra_fixed_incidence':bad['known_incidence_rows'][12][0]=0
            elif label=='matching_mapping':bad['symbolic_M1'][0][1]=bad['symbolic_M1'][0][2]
            elif label=='transpose_P':bad['symbolic_P']=list(map(list,zip(*bad['symbolic_P'])))
            elif label=='core_restriction':bad['core_extra_restrictions']=['P involution']
            elif label=='component_restriction':bad['component_restrictions']=True
            else:bad['mixed_cap_upper_bound']=3
            try:scope_check(model,bad)
            except ValueError:rejected.append(label)
            else:raise ValueError('corrupt scope accepted '+label)
        calibration['scope_corruptions_rejected']=rejected;save(args.out/'controls.json',calibration)
        counts=audit_clauses(model,scope,D/'instance.cnf')
        for k,v in counts.items():
            name='matching_edge_variables' if k=='matching_variables' else k
            if name in summary:need(summary[name]==v,'producer count agrees '+name)
        packages=[]
        for package in read(D/'artifact_packages.json')['packages']:
            compressed=b''.join(bind(ROOT/part['path'],part['sha256']).read_bytes() for part in package['ordered_parts']);need(sha256(compressed).hexdigest()==package['compressed_stream_sha256'],'gzip stream identity')
            raw=gzip.decompress(compressed);need(len(raw)==package['raw_bytes'] and sha256(raw).hexdigest()==package['raw_sha256']==digest(ROOT/package['raw_path']),'complete artifact reconstruction');packages.append(dict(path=package['raw_path'],sha256=package['raw_sha256'],bytes=len(raw)))
        bind(Path(__file__));bind(ROOT/'docs/AUDIT_20260930_VARIABLE_CORE_FACTOR_CNF.md');need(all(digest(ROOT/p)==v for p,v in bindings.items()),'frozen input stability')
        report=dict(status='INDEPENDENT_VARIABLE_CORE_FACTOR_CNF_ENCODING_PASS',claim_id='C-UNRESTRICTED-TRIANGLE-NECESSARY-FACTOR-CNF-ENCODING',claim_revision=1,
          timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/eight_domain_audit independently reconstructed scope and every clause',recommendation='VERIFIED',review_state='CLEAR',kind='encoding',basis=['DERIVED','COMPUTED'],
          statement='The saved formula is satisfiable exactly for arbitrary normalized M1,M2 perfect matchings, arbitrary P permutation, and binary36x60 incidence F satisfying canonical C0, full variable-core Gram, margins, all mixed caps and all distinct-column caps. Every target graph supplies a primary solution; a primary solution need not extend to residual D.',
          scope='Universally necessary target relaxation covering all target graphs up to the independently proved triangle labels; no fixed core, component, prism or automorphism restriction.',dependencies=[dict(id='C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION',revision=1,relation='coverage')],
          **counts,controls=calibration,package_checks=packages,producer_imports=False,shared_components=['Frozen independent truth-table GateAudit/ClauseCursor reused with exact source pin.','Universal normalization uses separately audited mathematical theorem.','New primary/row/product/channel/compact-clause reconstruction; no producer imports.'],
          limitations=['SAT produces a necessary factor and partial99 specification only; residual D is absent.','No solver run or complete proof is checked by this encoding audit.','Any nonexistence claim still requires an independently replayed complete proof and all recorded premises.'],solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e),inputs_sha256=bindings));raise

if __name__=='__main__':main()
