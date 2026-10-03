"""Independent extra-triangle equivalence and exact saved-root census.

No construction engine/helper imports; full scalar CN and all vertex triples.
"""
import argparse,copy,hashlib,itertools as it,json,platform,re,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
MATRIX='acceleration/results/20261002_hypergraph_weighted_pilot02/native/best.adj'
STATE='acceleration/results/20261002_hypergraph_weighted_pilot02/native/final.state'
PINS={MATRIX:'5f21ae090fdae2fad1ca27730b6d74e86b820866039317cc89c59ad1d9641066',
 STATE:'f4df0eadf3e7c4199c0715ed6c647ea995e41ffe8f972f91889b3a62a10879ad',
 'acceleration/results/20261002_independent_review/hypergraph_weighted_pilot02/best_object_evidence.json':'94502a1cce1af47bf410d261774cc82c84c08ef309ff73df90915e3e450e2e82',
 'acceleration/results/20261002_independent_review/hypergraph_weighted_pilot02/summary.json':'6e84a14ccd230801ce9efacdddf99bf90876933ff53997898b367e73c91156f0'}

class AuditError(ValueError):
    def __init__(self,stage,detail=''):
        self.stage=stage;super().__init__(stage+(': '+detail if detail else ''))
def need(test,stage,detail=''):
    if not test:raise AuditError(stage,detail)
def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(obj,stream,indent=2,sort_keys=True);stream.write('\n')
def clock(deadline):need(deadline.status()['remaining_seconds']>15,'DEADLINE','save/shutdown reserve')

def read_matrix(raw):
    lines=raw.decode('ascii').splitlines()
    need(lines and re.fullmatch(r'[0-9]+',lines[0]) is not None,'MATRIX_SYNTAX')
    n=int(lines[0]);need(len(lines)==n+1 and all(len(row)==n and set(row)<=set('01') for row in lines[1:]),'MATRIX_SYNTAX')
    return [[int(c) for c in row] for row in lines[1:]]

def best_block(raw):
    lines=raw.decode('ascii').splitlines()
    need(lines[0]=='HYPERGRAPH_WEIGHTED_ANNEAL_STATE_V1' and lines.count('n 99')==1 and lines.count('degree 7')==1,'BEST_BLOCK')
    positions=[i for i,row in enumerate(lines) if row.startswith('best ')]
    need(len(positions)==1 and lines[positions[0]]=='best 231','BEST_BLOCK')
    start=positions[0]+1;records=lines[start:start+231]
    need(len(records)==231 and lines[start+231]=='cn 4851','BEST_BLOCK')
    result=[]
    for row in records:
        tokens=row.split();need(len(tokens)==3 and all(re.fullmatch(r'[0-9]+',x) for x in tokens),'BEST_BLOCK')
        result.append([int(x) for x in tokens])
    return result

def pointgraph(triples,n,degree=None):
    pairs=Counter();counts=Counter();base=set();matrix=[[0]*n for _ in range(n)]
    for raw in triples:
        need(len(raw)==3 and all(type(x) is int and 0<=x<n for x in raw) and len(set(raw))==3,'TRIPLE_DOMAIN')
        t=tuple(sorted(raw));need(t not in base,'TRIPLE_DUPLICATE');base.add(t)
        for u in t:counts[u]+=1
        for u,v in it.combinations(t,2):
            pairs[(u,v)]+=1;need(pairs[(u,v)]==1,'LINEARITY');matrix[u][v]=matrix[v][u]=1
    if degree is not None:need(all(counts[u]==degree for u in range(n)),'POINT_DEGREE')
    return matrix,base

def graph_domain(matrix):
    n=len(matrix);need(n>0 and all(isinstance(row,list) and len(row)==n for row in matrix),'GRAPH_DOMAIN')
    need(all(type(x) is int and x in (0,1) for row in matrix for x in row),'GRAPH_DOMAIN')
    need(all(matrix[u][u]==0 for u in range(n)) and all(matrix[u][v]==matrix[v][u] for u in range(n) for v in range(n)),'GRAPH_DOMAIN')
    return [{v for v,x in enumerate(row) if x} for row in matrix]

def cn_and_triangles(matrix,deadline):
    g=graph_domain(matrix);n=len(g);cn=[]
    for u in range(n):
        clock(deadline)
        row=[]
        for v in range(n):
            # Separate literal full integer matrix multiplication.
            literal=sum(matrix[u][w]*matrix[w][v] for w in range(n))
            need(literal==len(g[u]&g[v]),'CN_PATH_AGREEMENT');row.append(literal)
        cn.append(row)
    literal_triangles={t for t in it.combinations(range(n),3) if all(matrix[u][v] for u,v in it.combinations(t,2))}
    set_triangles={(u,v,w) for u in range(n) for v in g[u] if v>u for w in g[u]&g[v] if w>v}
    need(literal_triangles==set_triangles,'TRIANGLE_PATH_AGREEMENT')
    return g,cn,literal_triangles

def inventory(triangles,base,extra):
    need(all(isinstance(t,(tuple,list)) and len(t)==3 for t in extra),'TRIANGLE_INVENTORY')
    values=[tuple(t) for t in extra]
    need(len(set(values))==len(values),'TRIANGLE_INVENTORY')
    need(set(values)==triangles-base and base<=triangles,'TRIANGLE_INVENTORY')

def root_rows(g,cn,extra,regular_degree=None):
    rows=[];n=len(g)
    for u in range(n):
        neighbors=sorted(g[u]);outside=[v for v in range(n) if v!=u and v not in g[u]]
        ah=Counter(cn[u][v] for v in neighbors);nh=Counter(cn[u][v] for v in outside)
        a=sum((cn[u][v]-1)**2 for v in neighbors);b=sum((cn[u][v]-2)**2 for v in outside)
        tu=sum(u in t for t in extra)
        need(sum(cn[u][v]-1 for v in neighbors)==2*tu,'ROOT_EXTRA_INCIDENCE')
        clean=a==0;matching=sorted(tuple((v,w)) for v in neighbors for w in g[v]&g[u] if v<w)
        if clean:need(len(matching)*2==len(neighbors) and Counter(x for t in matching for x in t)==Counter({v:1 for v in neighbors}),'CLEAN_NEIGHBOR_MATCHING')
        if regular_degree is not None:
            need(sum(cn[u][v] for v in outside)==regular_degree*(regular_degree-2)-2*tu,'ROOT_NONADJACENT_SUM')
        mean=Fraction(sum(cn[u][v] for v in outside),len(outside)) if outside else None
        witness=next((v for v in outside if cn[u][v]!=2),None)
        rows.append({'root':u,'adjacent_histogram':dict(sorted(ah.items())),'nonadjacent_histogram':dict(sorted(nh.items())),
          'adjacent_CN':[[v,cn[u][v]] for v in neighbors],'nonadjacent_CN':[[v,cn[u][v]] for v in outside],
          'extra_triangles_containing_root':tu,'root_E_lambda':a,'root_E_mu':b,
          'clean_root_neighbor_matching':clean,'neighbor_matching_edges_if_clean':matching if clean else None,
          'all_nonneighbors_have_exactly_two_root_neighbors':witness is None,
          'satisfies_both_requested_necessary_scaffold_conditions':clean and witness is None,
          'first_nonadjacent_CN_violation':None if witness is None else {'vertex':witness,'common_neighbors':cn[u][witness]},
          'nonadjacent_CN_sum':sum(cn[u][v] for v in outside),'nonadjacent_CN_mean':None if mean is None else [mean.numerator,mean.denominator],
          'root_neighbor_outside_cross_edge_count':sum(cn[u][v] for v in outside),
          'root_plus_neighbor_induced_edge_count':len(neighbors)+len(matching)})
    return rows

def compare_rows(expected,candidate):need(expected==candidate,'ROOT_TABLE_RECORD')

def analyze(matrix,triples,degree,deadline):
    expected,base=pointgraph(triples,len(matrix),degree)
    g=graph_domain(matrix);need(matrix==expected,'POINTGRAPH_MATRIX')
    k=2*degree if degree is not None else None
    if k is not None:need(all(len(row)==k for row in g),'GRAPH_REGULARITY')
    g,cn,triangles=cn_and_triangles(matrix,deadline);extra=triangles-base;inventory(triangles,base,sorted(extra))
    edgehist=Counter(cn[u][v] for u,v in it.combinations(range(len(g)),2) if v in g[u])
    nonedgehist=Counter(cn[u][v] for u,v in it.combinations(range(len(g)),2) if v not in g[u])
    el=sum(c*(s-1)**2 for s,c in edgehist.items());em=sum(c*(s-2)**2 for s,c in nonedgehist.items())
    need(all(s>=1 for s in edgehist),'BASE_TRIANGLE_ON_EVERY_EDGE')
    need(sum(c*(s-1) for s,c in edgehist.items())==3*len(extra),'GLOBAL_EXTRA_INCIDENCE')
    need((el==0)==(not extra) and el>=3*len(extra),'LAMBDA_ZERO_EQUIVALENCE')
    rows=root_rows(g,cn,extra,k)
    need(sum(r['root_E_lambda'] for r in rows)==2*el and sum(r['root_E_mu'] for r in rows)==2*em,'ROOT_ENERGY_POPULATION')
    union=sorted({u for t in extra for u in t});clean=[r['root'] for r in rows if r['clean_root_neighbor_matching']]
    need(set(clean)==set(range(len(g)))-set(union),'CLEAN_ROOT_UNION_COMPLEMENT')
    both=[r['root'] for r in rows if r['satisfies_both_requested_necessary_scaffold_conditions']]
    return {'vertices':len(g),'point_degree':degree,'pointgraph_regular_degree':k,'base_triples':len(base),
       'graph_triangles':len(triangles),'extra_triangles':len(extra),'extra_triangle_covered_vertices':union,
       'clean_root_ids':clean,'clean_root_count':len(clean),'both_necessary_scaffold_root_ids':both,'both_necessary_scaffold_root_count':len(both),
       'adjacent_CN_histogram':dict(edgehist),'nonadjacent_CN_histogram':dict(nonedgehist),'E_lambda':el,'E_mu':em,
       'all_scalar_matrix_entries_checked':len(g)**2,'all_vertex_triples_attempted':len(list(it.combinations(range(len(g)),3)))},rows,cn,triangles,base,extra

def rejects(controls,label,expected,call):
    try:call()
    except AuditError as e:
        need(e.stage==expected,'CONTROL_EXACT_STAGE',str(e));controls.append({'label':label,'stage':e.stage,'diagnostic':str(e)})
    else:raise AuditError('CONTROL_ACCEPTED',label)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent single graph lambda0 proof/triangle/root histogram audit; finite controls before raw targetobject,15secondreserve')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    for path,want in PINS.items():
        actual=digest(ROOT/path);need(actual==want,'INPUT_PIN',path);pins[path]=actual
    proof='acceleration/audit_20261002_lambda_phase_structure_v1_proof.md'
    for path in (Path(__file__).relative_to(ROOT).as_posix(),proof,'acceleration/audit_20261002_lambda_phase_structure_v1_spec.md',
                 'acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock'):
        pins[path]=digest(ROOT/path)
    controls=[]
    rook=[list(range(3*r,3*r+3)) for r in range(3)]+[[3*r+c for r in range(3)] for c in range(3)]
    rm,_=pointgraph(rook,9,2);rr,rows,cn,triangles,base,extra=analyze(rm,rook,2,deadline)
    need(rr['graph_triangles']==6 and rr['extra_triangles']==rr['E_lambda']==rr['E_mu']==0 and
         rr['both_necessary_scaffold_root_count']==9 and all(r['nonadjacent_CN_mean']==[2,1] for r in rows),'ROOK_POSITIVE')
    # Nonzero direct shape: three distinct lines yield exactly one extra triangle.
    partial=[[0,1,3],[1,2,4],[0,2,5]];pm,_=pointgraph(partial,6)
    pr,prows,pcn,pt,pbase,pextra=analyze(pm,partial,None,deadline)
    need(pextra=={(0,1,2)} and pr['E_lambda']==3 and pr['graph_triangles']==4,'NONZERO_TRIANGLE_POSITIVE')
    rejects(controls,'removed_nonzero_extra_triangle','TRIANGLE_INVENTORY',lambda:inventory(pt,pbase,[]))
    rejects(controls,'duplicate_extra_triangle','TRIANGLE_INVENTORY',lambda:inventory(pt,pbase,[(0,1,2),(0,1,2)]))
    bad=copy.deepcopy(rm);bad[0][0]=1
    rejects(controls,'corrupt_diagonal','GRAPH_DOMAIN',lambda:analyze(bad,rook,2,deadline))
    bad=copy.deepcopy(rm);bad[0][1]=2
    rejects(controls,'corrupt_binary','GRAPH_DOMAIN',lambda:analyze(bad,rook,2,deadline))
    bad=copy.deepcopy(rm);bad[0][1]=1-bad[0][1]
    rejects(controls,'corrupt_symmetry','GRAPH_DOMAIN',lambda:analyze(bad,rook,2,deadline))
    bad=copy.deepcopy(rm);bad[0][1]=bad[1][0]=1-bad[0][1]
    rejects(controls,'symmetric_graph_line_mismatch','POINTGRAPH_MATRIX',lambda:analyze(bad,rook,2,deadline))
    rejects(controls,'wrong_point_degree','POINT_DEGREE',lambda:pointgraph(rook,9,3))
    rejects(controls,'repeated_line_pair','LINEARITY',lambda:pointgraph(partial+[[0,1,5]],6))
    rejects(controls,'invalid_triple_endpoint','TRIPLE_DOMAIN',lambda:pointgraph([[0,1,9]],9))
    corrupt=copy.deepcopy(rows);corrupt[0]['nonadjacent_histogram']={2:3,3:1}
    rejects(controls,'changed_root_histogram','ROOT_TABLE_RECORD',lambda:compare_rows(rows,corrupt))
    raw=(ROOT/STATE).read_bytes();triples=best_block(raw);matrix=read_matrix((ROOT/MATRIX).read_bytes())
    rejects(controls,'wrong_best_block_population','BEST_BLOCK',lambda:best_block(raw.replace(b'best 231',b'best 230',1)))
    result,rows,cn,triangles,base,extra=analyze(matrix,triples,7,deadline)
    need(result['vertices']==99 and result['base_triples']==231 and result['adjacent_CN_histogram']=={1:630,2:63}
         and result['E_lambda']==63 and result['E_mu']==3423,'EXACT_SAVED_OBJECT_SCOPE')
    need(result['extra_triangles']==21 and result['clean_root_count']>=36,'EXACT_TRIANGLE_LOWER_BOUND')
    badroot=next(r for r in rows if not r['all_nonneighbors_have_exactly_two_root_neighbors'])
    corrupt=copy.deepcopy(rows);corrupt[badroot['root']]['all_nonneighbors_have_exactly_two_root_neighbors']=True
    corrupt[badroot['root']]['satisfies_both_requested_necessary_scaffold_conditions']=True
    rejects(controls,'unsupported_warm_scaffold_promotion','ROOT_TABLE_RECORD',lambda:compare_rows(rows,corrupt))
    rejects(controls,'saved_extra_triangle_omission','TRIANGLE_INVENTORY',lambda:inventory(triangles,base,sorted(extra)[1:]))
    save(out/'base_triples.json',sorted(base));save(out/'all_graph_triangles.json',sorted(triangles));save(out/'extra_triangles.json',sorted(extra))
    save(out/'every_root_exact_histograms.json',rows);save(out/'complete_CN_matrix.json',cn)
    save(out/'controls.json',{'rook9':rr,'nonzero_partial_linear_fixture':pr,'strict_corrupt_controls':controls,
                             'partial_fixture_scope':'Irregular6point shape tests extra triangle equivalence only; not regular mean theorem or SRG.'})
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    save(out/'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':source,
        'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python':platform.python_version(),'inputs_sha256':pins,
        'selection':'All99roots,all9801scalarCNentries,all156849vertextriples and complete231line/extra inventories;no favorable selection.',
        'success':'Written general proof plus full exact object/census and precise positive/negative controls.',
        'verification':'Separate literalmatrix and adjacencyset paths; no engine/helperimports; parent proposed theorem independently reviewed.',
        'producer':'/root (mathematical phase proposal); /root/native_driver (saved raw graph)','verifier':'/root/checkpoint_audit',
        'scope':'Necessary phase equivalence/one saved graph local census; no solver,engineapproval,targetresult,coverage or symmetry.'})
    outputs={p.relative_to(ROOT).as_posix():digest(p) for p in out.iterdir() if p.is_file()}
    report={'status':'INDEPENDENT_LAMBDA_PHASE_EQUIVALENCE_AND_SAVED_ROOT_CENSUS_V1_PASS',
        'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':source,'verifier':'/root/checkpoint_audit',
        'producer':'/root','method':'independent_derivation_and_complete_artifact_checking','written_proof':proof,
        'universal_statement':'For a99vertex14regular point graph of231linear3uniform triples with pointdegree7, E_lambda=sum_edges(CN-1)^2 is zero iff all graph triangles are exactly those231triples. For every vertex u, sum_nonadjacent_v CN(u,v)=168-2t_u, where t_u is its number of extra graph triangles; consequently if E_lambda=0 every vertex has nonadjacent CN mean exactly2, without claiming individual CNvalues2.',
        'saved_object':result,'inputs_sha256':pins,'outputs_sha256':outputs,'strict_negative_controls':len(controls),
        'clean_root_lower_bound':36,'warm_scaffold_scope':'The two tested root-local conditions are necessary only, not sufficient for a canonical SRG scaffold or any completion.',
        'no_root_satisfies_both_conditions':result['both_necessary_scaffold_root_count']==0,
        'target_resolution':False,'new_exclusions':0,'solver_calls':0,'changed_engine_approval':False,
        'prospective_weight60_launch_approval':False,'elapsed_seconds':time.monotonic()-start,'deadline':deadline.status(),
        'shared_components':['Python exact integers/Fraction/stdlib','command_deadline scheduling only'],
        'limitations':['One exact saved non-SRG graph; no future phase outcome, target coverage or nonexistence follows.',
          'The regular graph nonadjacent mean2 is an aggregate statement, not the target mu2 pair condition.',
          'A clean root has a14neighbor perfectmatching, but outsider CNdistribution must be separately checked; no canonical scaffold eligibility from the matching alone.',
          'Best triple block only is freshly parsed from checkpoint; RNG/counters/current/caches were checked by the pinned prior full-object audit and are not reapproved here.',
          'No changed weighted source,driver,objective60 controls,performance,ergodicity,scientific launch or external review approval.']}
    save(out/'summary.json',report)
    print(json.dumps({'status':report['status'],'path':str(out/'summary.json'),'sha256':digest(out/'summary.json'),
                      'extra_triangles':result['extra_triangles'],'clean_roots':result['clean_root_count'],
                      'both_local_conditions_roots':result['both_necessary_scaffold_root_count']}))

if __name__=='__main__':main()
