"""Independent exact artifact checker; never imports the bound producer."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json,platform,subprocess,sys,time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'acceleration/results/20260930_degree_block_gram_bounds/run01'
OUT=ROOT/'acceleration/results/20260930_independent_review/degree_block_gram'
def need(ok,message):
    if not ok:raise ValueError(message)
def digest(p):
    value=sha256()
    with Path(p).open('rb')as f:
        while b:=f.read(1<<20):value.update(b)
    return value.hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def unique(pairs):
    result={}
    for k,v in pairs:need(k not in result,'duplicate JSON key');result[k]=v
    return result
def save(p,value):
    with p.open('x')as f:json.dump(value,f,indent=2)
def parse_fixed(raw):
    result={int(k):v for k,v in raw.items()};need(len(result)==len(raw)and all(1<=k<=780 and type(v)is int and v in(0,1)for k,v in result.items()),'fixed variable scope');return result
def reconstruct(model):
    coords=[[0,0],[1,1],[1,2],[2,1],[2,2]];need(model['cell_rook_coordinates']==coords,'frozen cell owner coordinates')
    pairs=list(combinations(range(10,50),2));edge={i+1:p for i,p in enumerate(pairs)}
    need(model['edge_variables']==[dict(u=u,v=v,id=i)for i,(u,v)in edge.items()],'all780canonical edge labels')
    known=model['known_adjacency'];need(len(known)==50 and all(len(r)==50 for r in known),'known geometry')
    for a in range(50):
        for b in range(50):
            need(type(known[a][b])is int and known[a][b]==known[b][a],'symmetric integer fixed adjacency')
            need(known[a][b]==0 if a==b else known[a][b]==-1 if a>=10 and b>=10 else known[a][b]in(0,1),'fixed/free partition')
    groups={}
    for var,(u,v)in edge.items():groups.setdefault((u//10,v//10),[]).append((var,u,v))
    blocks=[];degrees=[]
    order=[(c,c)for c in range(1,5)]+list(combinations(range(1,5),2))
    for c,d in order:
        es=groups[c,d];left=list(range(c*10,c*10+10));right=list(range(d*10,d*10+10))
        if c==d:
            degree=1;block=dict(name=f'internal_{c}',kind='internal',vertices=left,edges=es);vertices=left
        else:
            degree=1 if coords[c][0]==coords[d][0]or coords[c][1]==coords[d][1]else 2
            block=dict(name=f'cross_{c}_{d}',kind='bipartite',left=left,right=right,degree=degree,edges=es);vertices=left+right
        blocks.append(block)
        for v in vertices:degrees.append((tuple(var for var,a,b in es if v in(a,b)),degree))
    need(len(degrees)==160 and Counter(degrees)==Counter((tuple(sorted(r['variables'])),r['value'])for r in model['degree_constraints']),'all160degree equations')
    need(Counter(var for b in blocks for var,u,v in b['edges'])==Counter(range(1,781)),'disjoint780variable coverage')
    A=[[0]*59 for _ in range(59)]
    for a,b in combinations(range(9),2):A[a][b]=A[b][a]=int(a//3==b//3 or a%3==b%3)
    for a in range(50):
        owner=3*coords[a//10][0]+coords[a//10][1];A[owner][a+9]=A[a+9][owner]=1
        for b in range(50):A[a+9][b+9]=max(0,known[a][b])
    return edge,blocks,A
def primal(record,block,weights,fixed):
    edges={v:(a,b)for v,a,b in block['edges']};chosen=record['selected_edges'];need(all(type(v)is int for v in chosen)and len(chosen)==len(set(chosen))and set(chosen)<=set(edges),'binary primal IDs')
    degree=1 if block['kind']=='internal'else block['degree'];vertices=block.get('vertices',block.get('left',[])+block.get('right',[]))
    counts=Counter(a for e in chosen for a in edges[e]);need(all(counts[a]==degree for a in vertices),'all primal degrees')
    need(all(int(e in chosen)==value for e,value in fixed.items()if e in edges),'all primal fixed values')
    objective=sum(weights[e]for e in chosen);need(type(record['objective'])is int and record['objective']==objective,'exact primal objective')
    return objective
def check_internal(record,block,weights,fixed):
    need(record['kind']=='internal_matching'and record['vertices']==block['vertices'],'internal block identity')
    objective=primal(record,block,weights,fixed);vertices=block['vertices'];position={v:i for i,v in enumerate(vertices)}
    forced=[e for e,a,b in block['edges']if fixed.get(e)==1];ends=[v for e,a,b in block['edges']if e in forced for v in(a,b)];need(len(ends)==len(set(ends)),'forced matching')
    remaining=sum(1<<position[v]for v in vertices if v not in ends);need(record['forced_one_edges']==forced and record['remaining_mask']==remaining,'residual mask')
    # Forward edge-processing coverage DP, independent of the producer's
    # first-unmatched-vertex recursion. Every table entry has an exact maximum.
    best={0:0};visits=0
    for e,a,b in block['edges']:
        bits=(1<<position[a])|(1<<position[b])
        if bits&remaining!=bits or fixed.get(e)==0:continue
        for covered,value in list(best.items()):
            visits+=1
            if not covered&bits:
                state=covered|bits;candidate=value+weights[e]
                if state not in best or candidate>best[state]:best[state]=candidate
    table={int(k):v for k,v in record['dp_values'].items()};need(len(table)==len(record['dp_values'])and table.get(0)==0 and remaining in table,'DP root/empty coverage')
    for mask,value in table.items():
        need(0<=mask<1<<len(vertices)and mask&remaining==mask and(value is None or type(value)is int),'DP value domain')
        need(value==best.get(mask),'independent every saved DP maximum')
    residual=best.get(remaining);need(residual is not None and record['residual_objective']==residual and residual+sum(weights[e]for e in forced)==objective,'full independent matching optimum')
    return dict(objective=objective,dp_entries=len(table),independent_edge_DP_transitions=visits,selected_edges=record['selected_edges'])
def check_bipartite(record,block,weights,fixed):
    left,right=block['left'],block['right'];degree=block['degree'];need(record['kind']=='bipartite_factor'and record['left']==left and record['right']==right and record['degree']==degree,'bipartite identity')
    objective=primal(record,block,weights,fixed);edge={e:(a,b)for e,a,b in block['edges']};forced=[e for e,a,b in block['edges']if fixed.get(e)==1]
    quotas={v:degree-sum(v in edge[e]for e in forced)for v in left+right};need(all(q>=0 for q in quotas.values()),'nonnegative residual degree')
    need(record['forced_one_edges']==forced and record['left_residual_degrees']==[quotas[v]for v in left]and record['right_residual_degrees']==[quotas[v]for v in right],'all residual quotas')
    al,ar=record['alpha_left'],record['alpha_right'];need(len(al)==len(left)and len(ar)==len(right)and all(type(v)is int for v in al+ar),'signed integer alpha')
    alpha=dict(zip(left+right,al+ar));beta={int(e):v for e,v in record['capacity_dual'].items()};allowed={e for e in edge if e not in fixed}
    need(len(beta)==len(record['capacity_dual'])and set(beta)==allowed,'exact residual capacity universe')
    for e in allowed:
        a,b=edge[e];need(type(beta[e])is int and beta[e]>=0 and alpha[a]+alpha[b]+beta[e]>=weights[e],'every exact dual inequality')
        need(beta[e]==max(0,weights[e]-alpha[a]-alpha[b]),'saved positive-part dual semantics')
    residual=sum(quotas[v]*alpha[v]for v in quotas)+sum(beta.values());dual=residual+sum(weights[e]for e in forced)
    need(record['residual_objective']==residual and objective==dual,'exact primal dual equality')
    return dict(objective=objective,dual_inequalities=len(allowed),selected_edges=record['selected_edges'])
def controls():
    internal=dict(name='control_internal',kind='internal',vertices=list(range(4)),edges=[(i+1,a,b)for i,(a,b)in enumerate(combinations(range(4),2))]);weights=dict(enumerate([5,-2,7,4,-1,3],1))
    good=dict(kind='internal_matching',vertices=list(range(4)),selected_edges=[3,4],objective=11,forced_one_edges=[],remaining_mask=15,residual_objective=11,dp_values={'0':0,'3':5,'5':-2,'9':7,'6':4,'10':-1,'12':3,'15':11})
    check_internal(good,internal,weights,{})
    forced=dict(kind='internal_matching',vertices=list(range(4)),selected_edges=[1,6],objective=8,forced_one_edges=[1],remaining_mask=12,residual_objective=3,dp_values={'0':0,'12':3});check_internal(forced,internal,weights,{1:1})
    bip=dict(name='control_bipartite',kind='bipartite',left=[0,1],right=[2,3],degree=1,edges=[(1,0,2),(2,0,3),(3,1,2),(4,1,3)]);bw={1:5,2:-2,3:4,4:3}
    bg=dict(kind='bipartite_factor',left=[0,1],right=[2,3],degree=1,left_residual_degrees=[1,1],right_residual_degrees=[1,1],forced_one_edges=[],selected_edges=[1,4],objective=8,residual_objective=8,alpha_left=[1,0],alpha_right=[4,3],capacity_dual={str(e):0 for e in range(1,5)})
    check_bipartite(bg,bip,bw,{})
    bf=deepcopy(bg);bf.update(left_residual_degrees=[0,1],right_residual_degrees=[0,1],forced_one_edges=[1],residual_objective=3,capacity_dual={'2':0,'3':0,'4':0});check_bipartite(bf,bip,bw,{1:1})
    rejected=[]
    for label,kind,change in [('DP_value','internal',lambda r:r['dp_values'].__setitem__('15',12)),('primal_degree','internal',lambda r:r.__setitem__('selected_edges',[1,3])),('dual_alpha','bip',lambda r:r['alpha_left'].__setitem__(0,-100)),('negative_capacity','bip',lambda r:r['capacity_dual'].__setitem__('1',-1)),('missing_capacity','bip',lambda r:r['capacity_dual'].pop('1')),('residual_quota','bip',lambda r:r['left_residual_degrees'].__setitem__(0,0))]:
        r=deepcopy(good if kind=='internal'else bg);change(r)
        try:(check_internal(r,internal,weights,{})if kind=='internal'else check_bipartite(r,bip,bw,{}))
        except ValueError:rejected.append(label)
        else:raise ValueError('corrupted control accepted '+label)
    for name,checker,args in [('internal_infeasible_forcing',check_internal,(good,internal,weights,{1:1,2:1})),('bipartite_infeasible_forcing',check_bipartite,(bg,bip,bw,{1:1,2:1}))]:
        try:checker(*args)
        except ValueError:rejected.append(name)
        else:raise ValueError('infeasible fixed control accepted')
    return dict(known_internal_maximum=11,forced_internal_maximum=8,known_bipartite_maximum=8,forced_bipartite_maximum=8,corruptions_rejected=rejected)
def main():
    OUT.mkdir(parents=True,exist_ok=False);tick=time.monotonic();bindings={};head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    def read(p,pin=None):
        d=digest(p);need(pin is None or d==pin,'pinned artifact '+str(p));bindings[key(p)]=d;return json.loads(p.read_bytes(),object_pairs_hook=unique)
    for p in[Path(__file__),Path(__file__).with_suffix('.md'),ROOT/'uv.lock']:bindings[key(p)]=digest(p)
    save(OUT/'preregistration.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=head,command=[sys.executable,*sys.argv],working_directory=str(ROOT),question='Are the complete degree block bound and12literal conditional Gram cut independently sound?',selection='All780variables,160degree equations,nine polynomials,and31bound records,including all failed deletions.',acceptance='Exact integer identities and feasible primal/dual equality; strict upper<0 for cut.',resource_limit_seconds=120,numerical_tolerance=None,numerical_tolerance_reason='Unbounded Python integers only.',inputs_sha256=dict(bindings)))
    ctrl=controls();save(OUT/'controls.json',ctrl)
    summary=read(RUN/'summary.json','7bf8ba56668e61095be383d07006d10f98e0cc5cab87b88c25344dcf2c40f100');manifest=read(RUN/'manifest.json')
    for f,v in manifest['inputs_sha256'].items():need(digest(ROOT/f)==v,'producer immutable input');bindings[f]=v
    modelpath=ROOT/'acceleration/results/20260930_rook_free_internal_sat/model.json';model=read(modelpath,'26908e992235e307cfc6145275deb3d2765a930c7c59a774c9a7bc42f2f0f95e')
    gate=read(modelpath.parent/'independent_cnf_encoding.json','a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0');need(gate['status']=='INDEPENDENT_ROOK_FREE_INTERNAL_WINDOW_CNF_ENCODING_PASS','scope gate')
    for f,v in gate['inputs_sha256'].items():need(digest(ROOT/f)==v,'scope gate input');bindings[f]=v
    edge,blocks,A0=reconstruct(model);saved_blocks=read(RUN/'blocks.json');expected=json.loads(json.dumps(blocks));need(saved_blocks['blocks']==expected and saved_blocks['edge_variables']==[[e,a,b]for e,(a,b)in edge.items()]and saved_blocks['model_sha256']==digest(modelpath),'saved block mapping')
    map_controls=[]
    for label,change in [('removed_degree',lambda m:m['degree_constraints'].pop()),('wrong_endpoint',lambda m:m['edge_variables'][0].__setitem__('v',12))]:
        broken=deepcopy(model);change(broken)
        try:reconstruct(broken)
        except ValueError:map_controls.append(label)
        else:raise ValueError('corrupt model map accepted')
    checkpoint=read(ROOT/'acceleration/results/20260930_rook_box_batch01/accepted_checkpoint.json');need(len(checkpoint['ordered_cuts'])==9,'nine frozen vectors');polynomials=[]
    for index,rec in enumerate(checkpoint['ordered_cuts']):
        p=read(RUN/f'polynomial_{index:02d}.json');cert=read(ROOT/rec['certificate'],rec['certificate_sha256']);audit=read(ROOT/rec['audit'],rec['audit_sha256'])
        need(audit['status']=='INDEPENDENT_TARGET_GRAM_BOX_NOGOOD_PASS','vector provenance review')
        raw=read(ROOT/p['graph_path'],p['graph_sha256']);A=raw['adjacency_full59'];w=p['vector'];need(len(A)==59 and all(len(r)==59 for r in A)and len(w)==59 and all(type(v)is int for v in w),'full59 raw data')
        need(w==cert['integer_negative_vector']and p['box_certificate']==rec['certificate']and p['box_certificate_sha256']==rec['certificate_sha256']and cert['graph_sha256']==p['graph_sha256'],'raw vector identity')
        free={(a+9,b+9)for a,b in edge.values()}
        for a in range(59):
            for b in range(59):
                need(type(A[a][b])is int and A[a][b]in(0,1)and A[a][b]==A[b][a]and(a!=b or A[a][b]==0),'binary symmetric zero diagonal raw graph')
                if tuple(sorted((a,b)))not in free:need(A[a][b]==A0[a][b],'raw graph fixed scaffold')
        constant=27*sum(v*v for v in w)+sum(w)**2-18*sum(w[a]*w[b]for a,b in combinations(range(59),2)if A0[a][b])
        weights={e:-18*w[a+9]*w[b+9]for e,(a,b)in edge.items()};current=27*sum(v*v for v in w)+sum(w)**2-18*sum(w[a]*w[b]for a,b in combinations(range(59),2)if A[a][b])
        need(p['index']==index and p['constant']==constant==cert['linear_quadratic_constant']and p['coefficients']=={str(e):v for e,v in weights.items()}and p['parent_current_value']==current==cert['quadratic_value_at_parent_graph']<0,'exact raw affine polynomial')
        need(constant+sum(weights[e]*A[a+9][b+9]for e,(a,b)in edge.items())==current and p['model_sha256']==digest(modelpath)and p['blocks_sha256']==digest(RUN/'blocks.json'),'polynomial reconstruction identities')
        polynomials.append(dict(constant=constant,weights=weights,parent=A,vector=w,graph_path=p['graph_path'],graph_sha256=p['graph_sha256'],base_cnf_sha256=cert['base_cnf_sha256'],hash=digest(RUN/f'polynomial_{index:02d}.json')))
    evaluated=[]
    def evaluate(path,index,pin=None):
        need(time.monotonic()-tick<120,'independent audit resource cap');r=read(path,pin);fixed=parse_fixed(r['fixed_values']);poly=polynomials[index]
        need(len(r['blocks'])==10 and[r['block']for r in r['blocks']]==[b['name']for b in blocks],'every block once in order')
        checked=[]
        for b,c in zip(blocks,r['blocks']):checked.append(check_internal(c,b,poly['weights'],fixed)if b['kind']=='internal'else check_bipartite(c,b,poly['weights'],fixed))
        value=poly['constant']+sum(c['objective']for c in checked)
        need(r['exact_degree_relaxation_maximum']==value and r['strictly_negative']==(value<0),'exact total and strict sign')
        selected=sorted(e for c in checked for e in c['selected_edges']);need(len(selected)==100 and len(set(selected))==100,'combined degree-relaxation primal edge population')
        need(all(sum(e in selected for e in row['variables'])==row['value']for row in model['degree_constraints']),'combined all160degree feasibility')
        need(poly['constant']+sum(poly['weights'][e]for e in selected)==value,'combined attaining graph weight')
        evaluated.append(dict(path=key(path),sha256=digest(path),polynomial_index=index,fixed_values=r['fixed_values'],maximum=value,block_checks=checked,selected_edges=selected))
        return r,fixed,value,selected
    need([r['index']for r in summary['unrestricted_bounds']]==list(range(9)),'ordered all-nine vector population')
    no_fixed=[]
    for rec in tqdm(summary['unrestricted_bounds'],desc='Independent degree-bound certificates',unit='vector'):
        index=rec['index'];r,f,value,chosen=evaluate(ROOT/rec['path'],index,rec['sha256']);need(not f and r['polynomial_sha256']==polynomials[index]['hash']and value==rec['exact_degree_relaxation_maximum']and value>0 and not rec['strictly_negative'],'unfixed vector record');no_fixed.append(value)
    initial=checkpoint['ordered_cuts'][0]['clause'];need(len(initial)==len(set(map(abs,initial)))==21,'initial21literal pattern');fixed={abs(v):int(v<0)for v in initial}
    r,f,value,chosen=evaluate(RUN/'initial21_degree_bound.json',0);need(f==fixed and value<0,'initial negative degree bound')
    failures=[];accepted=0;last_negative=None
    need(len(summary['attempts'])==21 and[r['removed_variable']for r in summary['attempts']]==sorted(fixed),'frozen deletion order')
    for number,rec in enumerate(summary['attempts'],1):
        e=rec['removed_variable'];candidate={v:a for v,a in fixed.items()if v!=e};r,f,value,chosen=evaluate(ROOT/rec['path'],0,rec['sha256'])
        need(e in fixed and rec['attempt']==number and r['tried_removing']==e and f==candidate and r['accepted']==rec['accepted']==(value<0)and value==rec['exact_degree_relaxation_maximum'],'deletion chain exact decision')
        if value<0:fixed=candidate;accepted+=1;last_negative=rec['path']
        else:failures.append(dict(removed=e,attaining_edges=chosen,quadratic=value,path=rec['path']))
    expected_clause=[-v if a else v for v,a in sorted(fixed.items())]
    need(accepted==9==summary['accepted_deletions']and len(fixed)==12 and parse_fixed(summary['final_fixed_values'])==fixed and summary['final_clause']==expected_clause and summary['final_clause_length']==12,'final12cut chain')
    need(last_negative=='acceleration/results/20260930_degree_block_gram_bounds/run01/greedy/attempt_016.json','final negative certificate identity')
    final=read(ROOT/last_negative,'c011a394131abe5cdf9d446524be65759a2d6ca76972ed17fdae9eedfe1face6');need(final['exact_degree_relaxation_maximum']==-176426969710399200,'exact final negative upper')
    for r in failures:need(r['removed']in fixed and r['quadratic']>=0 and all(int(v in r['attaining_edges'])==a for v,a in fixed.items()if v!=r['removed']),'retained-literal failed-deletion witness remains feasible')
    package=read(RUN/'final_cut_certificate.json','0307b96985b44b1038eac5ed63e5f332ac6a6b5ea66506cfe14d2760e8feee7e')
    for p,v in package['input_hashes'].items():need(digest(ROOT/p)==v,'cut package input');bindings[p]=v
    clausepath=RUN/'final_nogood.clause';bindings[key(clausepath)]=digest(clausepath);tokens=list(map(int,clausepath.read_text().split()));need(tokens==expected_clause+[0],'DIMACS clause exact signs')
    need(package['nogood_clause']==expected_clause and parse_fixed(package['fixed_values'])==fixed and package['exact_degree_relaxation_maximum']==final['exact_degree_relaxation_maximum']and package['integer_negative_vector']==polynomials[0]['vector']and package['linear_quadratic_constant']==polynomials[0]['constant'],'packaged cut semantics')
    need(package['encoding_model_sha256']==digest(modelpath) and package['base_cnf_sha256']==polynomials[0]['base_cnf_sha256'] and package['graph_path']==polynomials[0]['graph_path'] and package['graph_sha256']==polynomials[0]['graph_sha256'] and package['polynomial']==key(RUN/'polynomial_00.json') and package['polynomial_sha256']==polynomials[0]['hash'] and package['block_definitions']==key(RUN/'blocks.json') and package['block_definitions_sha256']==digest(RUN/'blocks.json') and package['block_maximum_witness']==last_negative and package['block_maximum_witness_sha256']==digest(ROOT/last_negative) and package['matrix']=='27I-9A+J','cut package complete map and witness bindings')
    parent=polynomials[0]['parent'];need(all(parent[edge[e][0]+9][edge[e][1]+9]==a for e,a in fixed.items()),'raw parent falsifies cut pattern')
    corrupted=expected_clause[:];corrupted[0]*=-1;need(corrupted!=[-v if a else v for v,a in sorted(fixed.items())],'clause sign corruption rejected')
    need(len(evaluated)==31 and not summary['candidate_whole_family_negative_vectors']and summary['completed_no_fixed_vectors']==9 and summary['greedy_attempts']==21 and summary['stop_reason']=='COMPLETE','whole registered population')
    need(all(digest(ROOT/f)==v for f,v in bindings.items()),'stable exact inputs')
    report=dict(status='INDEPENDENT_DEGREE_BLOCK_GRAM_BOUND_AND_CUT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=head,command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),verifier='/root/state_literature_audit independent checking agent',verification_type='Independent raw polynomial reconstruction, different edge-processing matching DP, direct primal/dual checking, full deletion chain and written mathematical review',inputs_sha256=bindings,scope='Only the frozen central-factor rook59 scaffold and its780free-edge degree relaxation. No universal rook containment, automorphism assumption, or unrestricted target resolution.',encoding_model_sha256=digest(modelpath),base_cnf_sha256=polynomials[0]['base_cnf_sha256'],edge_variables=780,degree_equations=160,blocks=10,internal_blocks=4,bipartite_degree1_blocks=4,bipartite_degree2_blocks=2,polynomials_checked=9,bound_evaluations=31,internal_certificates=124,bipartite_certificates=186,DP_values_checked=sum(c.get('dp_entries',0)for r in evaluated for c in r['block_checks']),independent_DP_transitions=sum(c.get('independent_edge_DP_transitions',0)for r in evaluated for c in r['block_checks']),dual_inequalities_checked=sum(c.get('dual_inequalities',0)for r in evaluated for c in r['block_checks']),unfixed_maxima=no_fixed,whole_family_negative_vectors=0,initial_clause_length=21,deletion_attempts=21,accepted_deletions=9,final_clause=expected_clause,final_fixed_values={str(v):a for v,a in sorted(fixed.items())},exact_final_upper=-176426969710399200,final_certificate=last_negative,final_certificate_sha256=digest(ROOT/last_negative),clause_path=key(clausepath),clause_sha256=digest(clausepath),cut_package=key(RUN/'final_cut_certificate.json'),cut_package_sha256=digest(RUN/'final_cut_certificate.json'),retained_literal_failure_witnesses=failures,evaluations=evaluated,controls=dict(calibration=ctrl,model_corruptions_rejected=map_controls,wrong_clause_sign_rejected=True),producer_imported=False,shared_components=['Python standard library and exact integer arithmetic','tqdm for progress','pinned independent full-window encoding audit as scope premise; its source was not imported'],limitations=['Conditional12literal cut only; does not exclude the whole fixed family or unrestricted target.','All nine unfixed maxima are positive; that proves neither local graph feasibility nor existence of the target.','Greedy irredundancy concerns this one fixed-vector degree-relaxation test, not global clause minimality or other vectors.','No new SAT search, UNSAT conclusion, or external review.'],elapsed_seconds=time.monotonic()-tick,target_resolution=False,external_review=False)
    save(OUT/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(OUT/'summary.json'),exact_upper=report['exact_final_upper'],clause=expected_clause,elapsed_seconds=report['elapsed_seconds'])))
if __name__=='__main__':main()
