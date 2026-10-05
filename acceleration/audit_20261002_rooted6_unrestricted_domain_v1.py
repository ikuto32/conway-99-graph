"""Independent six-facet/vertex proof of the unrestricted rooted6 count domain.

No discovery module imports. Reuses a pinned prior independent row/rank audit,
but newly parses raw vectors, derives its origin, and proves polytope equality
by six coordinate witnesses and a constructive eight-vertex convex combination.
"""
import argparse, copy, hashlib, itertools as it, json, math, platform, subprocess, sys, time
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
P = 'acceleration/results/'
MODEL = P+'20261002_rooted6_prismfree_rigidity/ordered_nonedge_model.json'
KERNEL = P+'20261002_rooted6_exact_parameter_domain/unrestricted_nonedge_nullspace.json'
PRIMAL = P+'20261002_rooted6_prismfree_rigidity/ordered_nonedge_prismfree_primal.json'
OLD_DOMAIN = P+'20261002_rooted6_exact_parameter_domain/prismfree_nonedge_domain.json'
OLD_AUDIT = P+'20261002_independent_review/rooted6_nonedge_domain01/nonedge_audit.json'
OLD_SUMMARY = P+'20261002_independent_review/rooted6_nonedge_domain01/summary.json'
DOMAIN = P+'20261002_rooted6_unrestricted_domain01/domain.json'
SUMMARY = P+'20261002_rooted6_unrestricted_domain01/summary.json'
PINS = {
 MODEL:'ecf558faa95576b8e76fbc5a62743729a875307eeb99df803c7cb5cdac7b7645',
 KERNEL:'5f3c4b485522156cccc458411d4b2f4517a320905418dc753c9896a5e0dbf384',
 PRIMAL:'1dadc060d77051baefe10ecc8bea5afc26441c3cfea877f37c6a484ded4fa64b',
 OLD_DOMAIN:'54f08f8dc87bebf61bada59067cbc721497f3d3a9683936e850b695f0ec41b12',
 OLD_AUDIT:'a6734101ce1b0509e6172760765045bea5c062f9270cb2338a9268308ffcd7bf',
 OLD_SUMMARY:'65081849ccf721eae5bdf569b16f44c88255e0421f5fab1ec26a7fa7f36e8271',
 DOMAIN:'dcf63f8a34784fe0a125d52a12423239f72559bfeeb370bc8ccda0b5404c3381',
 SUMMARY:'e0be09499b200950f364a42ae668de52d8cebaaab672cb46064dd4875a5bf8d4',
}
AXES = [514,552,566]
FACETS = ((1,0,0,0),(0,1,0,0),(0,0,1,0),(-1,0,0,2),(0,-1,0,20),(1,0,-2,18))
STATEMENT = ('The entire nonnegative integer solution set of the frozen independently reconstructed1445-row567-variable ordered-nonedge rooted-flag necessary system through order6 for srg(99,14,1,2) consists exactly of651 full affine count vectors x=origin+c*kernel0+a*kernel1+b*kernel2, where the actual flagged-count coordinates are c=x514(mask7100),a=x552(mask8024),b=x566(mask15540), c is0,1,or2,0<=a<=20,and0<=b<=floor(9+c/2). Its nonnegative rational parameter domain is exactly c>=0,a>=0,b>=0,c<=2,a<=20,2b<=18+c, with8vertices. These are necessary local count vectors; no graph realization or target exclusion is asserted.')

class AuditError(ValueError):
    def __init__(self, stage): self.stage=stage; super().__init__(stage)
def need(ok, stage):
    if not ok: raise AuditError(stage)
def unique(pairs):
    out={}
    for k,v in pairs:
        need(k not in out,'DUPLICATE_JSON_KEY'); out[k]=v
    return out
def load(path): return json.loads(path.read_bytes(),object_pairs_hook=unique)
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(obj,stream,indent=2,sort_keys=True);stream.write('\n')
def tick(deadline):need(deadline.status()['remaining_seconds']>15,'DEADLINE_RESERVE')
def integer(value):return type(value) is int
def vector(raw,n):
    need(isinstance(raw,list) and len(raw)==n,'VECTOR_SHAPE')
    result=[]
    for cell in raw:
        need(isinstance(cell,list) and len(cell)==2 and all(integer(x) for x in cell) and cell[1]>0,'RATIONAL_SYNTAX')
        q=Fraction(cell[0],cell[1]);need(q.denominator==1,'INTEGRAL_VECTOR');result.append(int(q))
    return result
def parse_rows(raw,n):
    need(isinstance(raw,list) and len(raw)==1445,'ROW_POPULATION')
    rows=[]
    for row in raw:
        need(isinstance(row,dict) and isinstance(row.get('terms'),list) and integer(row.get('rhs')),'ROW_SYNTAX')
        terms=[];seen=set()
        for pair in row['terms']:
            need(isinstance(pair,list) and len(pair)==2 and all(integer(x) for x in pair),'ROW_SYNTAX')
            j,c=pair;need(0<=j<n and c!=0 and j not in seen,'ROW_SYNTAX');seen.add(j);terms.append((j,c))
        rows.append((terms,row['rhs']))
    return rows
def holds(rows,values,homogeneous=False):
    return all(sum(values[j]*coefficient for j,coefficient in terms)==(0 if homogeneous else rhs) for terms,rhs in rows)
def normalize(row):
    d=math.gcd(*row)
    return tuple(x//d for x in row) if d else tuple(row)
def affine(origin,basis,point):return [origin[j]+sum(basis[q][j]*point[q] for q in range(3)) for j in range(len(origin))]
def facet_witnesses(forms):
    result=[]
    for facet in FACETS:
        indices=[j for j,form in enumerate(forms) if normalize(form)==facet]
        need(indices,'FACET_IDENTITIES');result.append(dict(facet=list(facet),raw_coordinate_witnesses=indices))
    return result
def corners(cmax=2,amax=20,low=9,high=10):
    return [(c,a,b) for c in (0,cmax) for a in (0,amax) for b in (0,low if c==0 else high)]
def weights(point,cmax=2,amax=20,low=9,high=10):
    c,a,b=map(Fraction,point);x=c/cmax;y=a/amax;upper=low+(high-low)*x;z=b/upper
    result=[((x if i else 1-x)*(y if j else 1-y)*(z if k else 1-z)) for i,j,k in it.product(range(2),repeat=3)]
    vertices=corners(cmax,amax,low,high)
    need(all(w>=0 for w in result) and sum(result)==1 and all(sum(w*v[q] for w,v in zip(result,vertices))==point[q] for q in range(3)),'CONVEX_COMBINATION')
    return result
def prism_geometry(mask):
    edges={edge for bit,edge in enumerate(it.combinations(range(6),2)) if mask>>bit&1}
    triangles={t for t in it.combinations(range(6),3) if all(e in edges for e in it.combinations(t,2))}
    g=[{v if u==w else u for u,v in edges if w in (u,v)} for w in range(6)]
    partitions=[]
    for t in sorted(triangles):
        other=tuple(sorted(set(range(6))-set(t)))
        if other in triangles and t<other and all(len(g[u]&set(other))==1 for u in t) and all(len(g[u]&set(t))==1 for u in other):partitions.append([list(t),list(other)])
    need(len(partitions)==1 and all(len(s)==3 for s in g),'PRISM_GEOMETRY')
    images=[]
    for free in it.permutations(range(2,6)):
        labels=(0,1,*free);images.append(sum(1<<bit for bit,(u,v) in enumerate(it.combinations(range(6),2)) if tuple(sorted((labels[u],labels[v]))) in edges))
    need(min(images)==mask and (0,1) not in edges,'PRISM_GEOMETRY')
    return dict(mask=mask,neighbors=[sorted(s) for s in g],triangles=[list(t) for t in sorted(triangles)],triangle_matching_partition=partitions[0],canonical_mask=min(images),root_adjacent=False)
def check_vertices(raw,vertices):
    need(isinstance(raw,list) and len(raw)==8,'VERTEX_CENSUS')
    got=[]
    for record in raw:
        need(isinstance(record,list) and len(record)==3,'VERTEX_CENSUS')
        got.append(tuple(Fraction(*v) for v in record))
    need(len(set(got))==8 and set(got)==set(vertices),'VERTEX_CENSUS')
def check_points(raw,expected):
    need(isinstance(raw,list) and all(isinstance(p,list) and len(p)==3 and all(integer(x) for x in p) for p in raw),'INTEGER_CENSUS')
    need(raw==expected,'INTEGER_CENSUS')
def reject(records,name,stage,fn):
    try:fn()
    except AuditError as error:
        need(error.stage==stage,'CONTROL_WRONG_STAGE');records.append(dict(name=name,expected_stage=stage,actual_stage=error.stage,outcome='REJECTED'));return
    raise AuditError('CONTROL_ACCEPTED_'+name)

def run(args):
    started=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Finite complete unrestricted count domain checking;180outer150worker15internal output reserve, prior producer2.265s; no solver/flag enumeration')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};controls=[]
    def pin(path,wanted=None):
        path=path.resolve();actual=sha(path);need(wanted is None or actual==wanted,'FROZEN_INPUT_HASH');pins[path.relative_to(ROOT).as_posix()]=actual;return actual
    try:
        for name,wanted in PINS.items():pin(ROOT/name,wanted)
        for name in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261002_rooted6_unrestricted_domain_v1_spec.md','acceleration/audit_20261002_rooted6_unrestricted_domain_v1_proof.md','acceleration/theory_20261002_rooted6_unrestricted_domain_v1.py','docs/DESIGN_20261002_UNRESTRICTED_ROOTED7_DOMAIN.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']:pin(ROOT/name)
        raw={name:load(ROOT/name) for name in PINS};source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,python=platform.python_version(),scope='Complete necessary integer local count domain, no graph realization/exclusion.',success='Six facet witnesses and all567coordinate evaluations at all8vertices; complete693triple enumeration,651allrow evaluations,42literal rejections; all strict controls.',selection='Every coordinate,vertex,bounding integer triple,row; no sampled checks.',numeric_threshold='Exact integers/Fraction only; every recorded identity must hold exactly.',resource_limits=dict(outer_seconds=180,worker_seconds=args.seconds,worker_reserve_seconds=15),independent_requirement='Verifier/checkpoint_audit differs from producer/structural; no discovery module import. Pinned prior independent geometry/rank reused explicitly.'))
        # Hand known nontrivial wedge with varying b cap:3layers12+12+16=40.
        fixture=[]
        for c,a,b in it.product(range(3),range(4),range(4)):
            if 2*b<=4+c:weights((c,a,b),2,3,2,3);fixture.append([c,a,b])
        need(len(fixture)==40,'POSITIVE_WEDGE_CENSUS')
        controls.append(dict(name='varying_cap40_integer_points8_vertices',outcome='PASS',complete_bounding_population=48,accepted=40))
        for point in [(Fraction(1,3),Fraction(7,2),Fraction(2)),(1,20,Fraction(19,2)),(2,0,10),(0,20,9)]:weights(point)
        controls.append(dict(name='rational_interior_boundary_convex_weights',outcome='PASS',cases=4))
        reject(controls,'duplicate_json','DUPLICATE_JSON_KEY',lambda:json.loads('{"x":1,"x":2}',object_pairs_hook=unique))
        for name,cell in [('zero_denominator',[1,0]),('boolean_numerator',[True,1]),('floating_numerator',[1.0,1]),('fractional_count',[1,2])]:reject(controls,name,'INTEGRAL_VECTOR' if name=='fractional_count' else 'RATIONAL_SYNTAX',lambda cell=cell:vector([cell],1))
        model=raw[MODEL];prior=raw[OLD_AUDIT];old=raw[OLD_SUMMARY];domain=raw[DOMAIN];candidate_summary=raw[SUMMARY];certificate=raw[KERNEL]
        need(model['adjacent_roots'] is False and model['variables']==prior['variables'] and model['equations']==prior['reconstructed_rows'],'PRIOR_INDEPENDENT_OPERATOR_IDENTITY')
        need(old['status']=='INDEPENDENT_ROOTED6_NONEDGE_EXACT_NULLSPACES_AND_CONDITIONAL_DOMAIN_PASS' and old['exact_rational_ranks']==[564,565] and old['exact_nullities']==[3,2] and prior['unrestricted_modular_rank']['rank']==564,'PRIOR_RANK_DEPENDENCY')
        variables=model['variables'];need(len(variables)==567 and [variables[j] for j in AXES]==[[6,7100],[6,8024],[6,15540]],'ACTUAL_COUNT_AXES');rows=parse_rows(model['equations'],567)
        basis=[vector(v,567) for v in certificate['rational_vectors']];need(len(basis)==3 and certificate['rank_lower_bound']['free_coordinates']==AXES,'KERNEL_SHAPE')
        need([[basis[q][j] for j in AXES] for q in range(3)]==[[1,0,0],[0,1,0],[0,0,1]],'IDENTITY_MINOR')
        need(all(holds(rows,v,True) for v in basis),'KERNEL_EQUATIONS')
        primal=raw[PRIMAL]['exact_primal'];need(len(primal)==567 and all(integer(x) and x>=0 for x in primal) and holds(rows,primal),'RAW_PRIMAL')
        origin=[primal[j]-sum(primal[axis]*basis[q][j] for q,axis in enumerate(AXES)) for j in range(567)]
        need(holds(rows,origin) and [origin[j] for j in AXES]==[0,0,0],'ORIGIN_EQUATIONS')
        need(origin==vector(raw[OLD_DOMAIN]['origin'],567),'PRIOR_ORIGIN_IDENTITY')
        need(domain['origin']==origin and domain['basis']==basis and domain['free_coordinates']==AXES and domain['free_variables']==[variables[j] for j in AXES] and domain['coordinate_order']==['c','a','b'],'RAW_AFFINE_IDENTITY')
        # Calibration is run before candidate-domain promotion, against exact parsed operator.
        wrong=origin[:];wrong[0]+=1;reject(controls,'changed_origin','ORIGIN_EQUATIONS',lambda:need(holds(rows,wrong),'ORIGIN_EQUATIONS'))
        wrong=basis[0][:];wrong[0]+=1;reject(controls,'changed_kernel','KERNEL_EQUATIONS',lambda:need(holds(rows,wrong,True),'KERNEL_EQUATIONS'))
        altered=copy.deepcopy(model);altered['equations'][0]['terms'][0][1]+=1
        reject(controls,'changed_raw_row','PRIOR_INDEPENDENT_OPERATOR_IDENTITY',lambda:need(altered['equations']==prior['reconstructed_rows'],'PRIOR_INDEPENDENT_OPERATOR_IDENTITY'))
        changed_basis=[basis[1],basis[0],basis[2]];reject(controls,'permuted_actual_axes','IDENTITY_MINOR',lambda:need([[v[j] for j in AXES] for v in changed_basis]==[[1,0,0],[0,1,0],[0,0,1]],'IDENTITY_MINOR'))
        forms=[tuple(basis[q][j] for q in range(3))+(origin[j],) for j in range(567)]
        witnesses=facet_witnesses(forms)
        removed=[form for form in forms if normalize(form)!=(1,0,-2,18)]
        reject(controls,'missing_slanted_facet','FACET_IDENTITIES',lambda:facet_witnesses(removed))
        vertices=corners();values_at_vertices=[]
        for point in vertices:
            vals=affine(origin,basis,point);need(all(x>=0 for x in vals) and holds(rows,vals),'COORDINATE_VERTEX');values_at_vertices.append(dict(point=list(point),values=vals));weights(point)
        reject(controls,'outside_slanted_boundary','COORDINATE_VERTEX',lambda:need(min(affine(origin,basis,(0,0,10)))>=0,'COORDINATE_VERTEX'))
        check_vertices(domain['vertices'],vertices)
        reject(controls,'omitted_vertex','VERTEX_CENSUS',lambda:check_vertices(domain['vertices'][:-1],vertices))
        changed_vertices=copy.deepcopy(domain['vertices']);changed_vertices[-1][2]=[9,1]
        reject(controls,'changed_vertex','VERTEX_CENSUS',lambda:check_vertices(changed_vertices,vertices))
        # Every affine coordinate holds throughout convex hull of these8vertices.
        # Literal coordinate witnesses prove reverse inclusion in six-facet wedge.
        six=[j for j,v in enumerate(variables) if v[0]==6];total=math.comb(97,4)
        need(sum(origin[j] for j in six)==total and all(sum(v[j] for j in six)==0 for v in basis),'COMPLETE_ORDER6_TOTAL')
        normalized=set(map(normalize,forms));normalized.update({(-1,0,0,total),(0,-1,0,total),(0,0,-1,total)})
        need(set(map(tuple,domain['inequalities_primitive_integer']))==normalized and len(normalized)==131,'ALL_NONNEGATIVE_FORMS')
        need(len(domain['inequality_raw_coordinate_witnesses'])==len(domain['inequalities_primitive_integer']),'COORDINATE_WITNESS_MAP')
        for row,mapped in zip(domain['inequalities_primitive_integer'],domain['inequality_raw_coordinate_witnesses']):
            need(mapped==[j for j,form in enumerate(forms) if normalize(form)==tuple(row)],'COORDINATE_WITNESS_MAP')
        geometry=prism_geometry(7100);need(domain['rooted_prism_geometry'][0]['neighbors']==geometry['neighbors'] and domain['rooted_prism_geometry'][0]['canonical_mask']==7100,'PRISM_GEOMETRY')
        reject(controls,'changed_prism_mask','PRISM_GEOMETRY',lambda:prism_geometry(7100^2))
        points=[];records=[];rejected=[];layer=Counter()
        for c,a,b in it.product(range(3),range(21),range(11)):
            tick(deadline);vals=affine(origin,basis,(c,a,b));accepted=min(vals)>=0
            need(accepted==(2*b<=18+c),'BOUNDING_POINT_EQUIVALENCE')
            if accepted:
                need([vals[j] for j in AXES]==[c,a,b] and holds(rows,vals),'EVERY_INTEGER_PROFILE_ALL_ROWS')
                points.append([c,a,b]);layer[c]+=1;records.append(dict(parameters=[c,a,b],full_count_vector=vals))
            else:rejected.append(dict(parameters=[c,a,b],negative_coordinates=[j for j,x in enumerate(vals) if x<0]))
        check_points(domain['integer_points'],points)
        reject(controls,'omitted_profile','INTEGER_CENSUS',lambda:check_points(domain['integer_points'][:-1],points))
        reject(controls,'duplicate_profile','INTEGER_CENSUS',lambda:check_points([*domain['integer_points'],domain['integer_points'][0]],points))
        outside=copy.deepcopy(domain['integer_points']);outside[-1]=[2,20,11]
        reject(controls,'outside_profile','INTEGER_CENSUS',lambda:check_points(outside,points))
        need(len(points)==651 and len(rejected)==42 and layer=={0:210,1:210,2:231},'INTEGER_POPULATION')
        need([[a,b] for c,a,b in points if c==0]==raw[OLD_DOMAIN]['exact_integer_feasible_points'],'OLD_ZERO_FACE')
        need(domain['complete_integer_domain'] is True and domain['graph_realizability_asserted'] is False and domain['integer_bounding_box']==[[0,2],[0,20],[0,10]] and domain['bounding_integer_population']==693,'CANDIDATE_SCOPE')
        need(candidate_summary['integer_profile_count']==651 and candidate_summary['bounding_integer_population']==693 and candidate_summary['rational_vertices']==8 and candidate_summary['target_resolution'] is False,'SUMMARY_POPULATION')
        reject(controls,'changed_summary_count','SUMMARY_POPULATION',lambda:need(650==candidate_summary['integer_profile_count'],'SUMMARY_POPULATION'))
        for p in [(-1,0,0),(3,0,0),(0,-1,0),(0,21,0),(0,0,-1),(0,0,10),(1,0,10),(2,0,11)]:
            need(min(affine(origin,basis,p))<0,'OUTSIDE_PROFILE_CONTROL')
        controls.append(dict(name='all_six_facets_and_integer_half_cap_boundaries',outcome='REJECTED_BY_NEGATIVE_COORDINATE',cases=8))
        save(out/'controls.json',controls);save(out/'facet_vertex_proof.json',dict(facets=witnesses,vertices=[list(v) for v in vertices],all_coordinate_values_at_vertices=values_at_vertices,constructive_convex_weights='x=c/2,y=a/20,z=b/(9+c/2); at endpoint(i,j,k) use(x if i else1-x)*(y if j else1-y)*(z if k else1-z). Sum1, reconstruct(c,a,b) exactly. Every coordinate affine, so eight checks suffice.',origin=origin,basis=basis,prism_geometry=geometry,prior_rank_reused=True,prior_geometry_reused=True,fresh_rank_computation=False))
        save(out/'complete_integer_profiles.json',records);save(out/'rejected_bounding_triples.json',rejected)
        for path in out.iterdir():
            if path.is_file():pin(path)
        result=dict(status='INDEPENDENT_UNRESTRICTED_ROOTED6_NONEDGE_EXACT_INTEGER_DOMAIN_V1_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),producer='/root/structural',verifier='/root/checkpoint_audit',method='independent_derivation',inputs_sha256=pins,statement=STATEMENT,scope='Entire nonnegative integer solution domain of one complete necessary local operator; no prism-free premise, target automorphism, realizability, exclusion or target resolution.',variables=567,rows=1445,rational_vertices=8,coordinate_forms_at_vertices=567*8,bounding_integer_triples=693,accepted_integer_profiles=651,rejected_integer_triples=42,profile_layers=dict(layer),integer_all_row_checks=651*1445,integer_full_coordinate_checks=651*567,zero_prism_face=210,controls=len(controls),precise_rejection_controls=sum(r['outcome']=='REJECTED' for r in controls),prior_rank_dependency=dict(id='C-UNRESTRICTED-ROOTED6-NONEDGE-NECESSARY-SYSTEM-NULLSPACE',revision=1,rank=564,nullity=3,reused_artifact=OLD_SUMMARY,reused_sha256=PINS[OLD_SUMMARY],fresh_rank_computation=False),shared_components=['Python exact integer/Fraction/stdlib and command_deadline scheduling only.','Pinned prior independent complete rooted6 geometry/row/rank audit reused as mathematical dependency, without a discovery module import.'],limitations=['Count vectors are necessary local profiles; none is certified as realized in any target graph.','Prior finite geometry/rank is reused and compared to raw operator; no fresh geometry/rank or external review claim.','No exclusion or target-wide coverage denominator follows.'],artifact_availability='LOCAL_ONLY',target_resolution='NONE',new_exclusions=0,graph_realizability_asserted=False,elapsed_seconds=time.monotonic()-started,deadline=deadline.status())
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),elapsed_seconds=result['elapsed_seconds'])),flush=True)
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),stage=getattr(error,'stage',None),elapsed_seconds=time.monotonic()-started,outputs_preserved=True,target_resolution='NONE'));raise

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',type=Path,required=True);run(parser.parse_args())
