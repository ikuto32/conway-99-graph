"""Independent exact unrestricted edge kernel/rank/rectangle checking.

No discovery imports. New sparse incremental elimination modulo1009, two
exact kernel vectors, four coordinate facet witnesses and all91 full vectors.
"""
import argparse,copy,hashlib,itertools as it,json,math,platform,subprocess,sys,time
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1];P='acceleration/results/'
MODEL=P+'20261002_rooted6_prismfree_rigidity/ordered_edge_model.json'
PRIMAL=P+'20261002_rooted6_prismfree_rigidity/ordered_edge_prismfree_primal.json'
PRIOR=P+'20261002_independent_review/rooted6_prismfree02/ordered_edge_audit.json'
OLD=P+'20261002_independent_review/rooted6_prismfree02/summary.json'
KERNEL=P+'20261002_rooted6_unrestricted_edge_domain01/unrestricted_edge_nullspace.json'
DOMAIN=P+'20261002_rooted6_unrestricted_edge_domain01/domain.json'
SUMMARY=P+'20261002_rooted6_unrestricted_edge_domain01/summary.json'
PINS={MODEL:'06051294a142dfcda956f4ee3748986982f7f8ba5f9785fe4d7680d967538584',PRIMAL:'8c914f27e91f5c003644148738b9a634ac0dfe9683915dd42dc3ae067d2a2010',PRIOR:'55cdf821791a97741c58842c00596b45c541d13b627476a31f28baae3dc5b7ef',OLD:'f7e8f93a671648cd0e73c326a36ee8cc97682a2c568ed88f46044cb04abd4717',KERNEL:'06fd7396f07f6d1eb894a5d0f05dffcee4299921e60176debb2c2a6487c199b0',DOMAIN:'e2cade276f89c87ece74df8544c99704ce116bb55d84a5bd5e364c6264d75c95'}
AXES=[382,393];FACETS=((1,0,0),(0,1,0),(-1,0,12),(0,-1,6))
STATEMENT=('The frozen independently reconstructed1099-row394-variable ordered-edge rooted-flag necessary system through order6 for srg(99,14,1,2) has exact rational rank392 and nullity2 with the two saved integral kernel vectors. Its entire nonnegative integer solution set consists exactly of91 full affine count vectors x=origin+s*kernel0+t*kernel1, where s=x382(mask8025,triangular-prism triangle-edge root) and t=x393(mask15541,triangular-prism matching-edge root) are actual counts,0<=s<=12,and0<=t<=6. The rational nonnegative parameter domain is exactly that four-vertex rectangle. No prism-free premise,graph realization or target exclusion is asserted.')
class AuditError(ValueError):
    def __init__(self,stage):self.stage=stage;super().__init__(stage)
def need(ok,stage):
    if not ok:raise AuditError(stage)
def unique(pairs):
    out={}
    for k,v in pairs:need(k not in out,'DUPLICATE_JSON_KEY');out[k]=v
    return out
def load(p):return json.loads(p.read_bytes(),object_pairs_hook=unique)
def sha(p):
    with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def save(p,obj):
    with p.open('x',encoding='utf8',newline='\n') as s:json.dump(obj,s,indent=2,sort_keys=True);s.write('\n')
def tick(d):need(d.status()['remaining_seconds']>15,'DEADLINE_RESERVE')
def vector(raw):
    need(isinstance(raw,list) and len(raw)==394,'VECTOR_SHAPE');out=[]
    for q in raw:
        need(isinstance(q,list) and len(q)==2 and all(type(x) is int for x in q) and q[1]>0,'RATIONAL_SYNTAX')
        x=Fraction(*q);need(x.denominator==1,'INTEGRAL_VECTOR');out.append(int(x))
    return out
def rows(raw):
    need(len(raw)==1099,'ROW_POPULATION');out=[]
    for r in raw:
        need(type(r.get('rhs')) is int and isinstance(r.get('terms'),list),'ROW_SYNTAX');terms=[];seen=set()
        for q in r['terms']:
            need(isinstance(q,list) and len(q)==2 and all(type(x) is int for x in q),'ROW_SYNTAX');j,c=q
            need(0<=j<394 and c!=0 and j not in seen,'ROW_SYNTAX');seen.add(j);terms.append((j,c))
        out.append((terms,r['rhs']))
    return out
def holds(rs,x,homogeneous=False):return all(sum(c*x[j] for j,c in t)==(0 if homogeneous else rhs) for t,rhs in rs)
def rank_sparse(rs,n,p,deadline):
    need(p>=2 and all(p%d for d in range(2,math.isqrt(p)+1)),'PRIME_MODULUS')
    pivot={};sources=[];eliminations=0
    for at,(terms,rhs) in enumerate(rs):
        tick(deadline);work={j:c%p for j,c in terms if c%p}
        need(all(0<=j<n for j in work),'RANK_COLUMN')
        while work:
            j=min(work);factor=work[j]
            if j not in pivot:
                inverse=pow(factor,-1,p);pivot[j]={col:value*inverse%p for col,value in work.items()};sources.append(at);break
            for col,value in pivot[j].items():
                result=(work.get(col,0)-factor*value)%p
                if result:work[col]=result
                else:work.pop(col,None)
            eliminations+=1
    return dict(prime=p,rank=len(pivot),pivot_columns=sorted(pivot),independent_source_row_indices=sources,nonzero_pivot_echelon_rows=[dict(column=j,terms=sorted(map(list,pivot[j].items()))) for j in sorted(pivot)],row_eliminations=eliminations,method='Sparse incremental row elimination with modular inverse, no NumPy/discovery echelon import.',exact_implication='Nonzero392-column echelon pivots certify a rank392 minor over the prime field; hence rational rank at least392. Two independent exact kernel vectors certify rank at most392.')
def normalize(row):
    d=math.gcd(*row);return tuple(x//d for x in row) if d else tuple(row)
def affine(o,k,p):return [o[j]+p[0]*k[0][j]+p[1]*k[1][j] for j in range(394)]
def facets(forms):
    result=[]
    for form in FACETS:
        indices=[j for j,row in enumerate(forms) if normalize(row)==form];need(indices,'FACET_IDENTITIES');result.append(dict(facet=list(form),raw_coordinates=indices))
    return result
def geometry(mask,root_type):
    edges={pair for bit,pair in enumerate(it.combinations(range(6),2)) if mask>>bit&1};g=[{v if u==w else u for u,v in edges if w in (u,v)} for w in range(6)]
    ts={q for q in it.combinations(range(6),3) if all(e in edges for e in it.combinations(q,2))};part=[]
    for q in sorted(ts):
        other=tuple(sorted(set(range(6))-set(q)))
        if q<other and other in ts and all(len(g[u]&set(other))==1 for u in q) and all(len(g[u]&set(q))==1 for u in other):part.append([q,other])
    need(len(part)==1 and all(len(v)==3 for v in g) and (0,1) in edges,'PRISM_GEOMETRY')
    actual='triangle_edge' if any(0 in q and 1 in q for q in ts) else 'matching_edge'
    need(actual==root_type,'PRISM_ROOT_TYPE')
    images=[]
    for tail in it.permutations(range(2,6)):
        order=(0,1,*tail);images.append(sum(1<<bit for bit,(u,v) in enumerate(it.combinations(range(6),2)) if tuple(sorted((order[u],order[v]))) in edges))
    need(min(images)==mask,'ROOT_FIXED_CANONICAL_CLASS')
    return dict(mask=mask,root_type=actual,neighbors=[sorted(x) for x in g],triangles=[list(q) for q in sorted(ts)],canonical_mask=min(images))
def reject(controls,label,expected,fn):
    try:fn()
    except AuditError as error:need(error.stage==expected,'CONTROL_WRONG_STAGE');controls.append(dict(name=label,stage=error.stage,outcome='REJECTED'));return
    raise AuditError('CONTROL_ACCEPTED_'+label)
def census(raw,wanted,stage):need(raw==wanted,stage)
def run(args):
    started=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent sparse-prime392rank, exact kernels and91-profile rectangle proof;180outer150worker15reserve,no solver/new geometry enumeration')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};controls=[]
    def pin(name,wanted=None):
        actual=sha(ROOT/name);need(wanted is None or actual==wanted,'FROZEN_INPUT_HASH');pins[name]=actual;return actual
    try:
        for name,wanted in PINS.items():pin(name,wanted)
        pin(SUMMARY)
        for name in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261002_rooted6_unrestricted_edge_domain_v1_spec.md','acceleration/audit_20261002_rooted6_unrestricted_edge_domain_v1_proof.md','acceleration/theory_20261002_rooted6_unrestricted_edge_domain_v1.py','docs/DESIGN_20261002_UNRESTRICTED_ROOTED6_EDGE_DOMAIN.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml']:pin(name)
        source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();raw={name:load(ROOT/name) for name in PINS};raw[SUMMARY]=load(ROOT/SUMMARY)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,question='Exact unrestricted edge operator kernel and entire nonnegative integer count domain?',selection='All1099rows394coordinates,fourvertices91profiles; newprime1009 sparse elimination.',success='392prime rank plus2independent exactkernels; identity axes, literal fourfacet/corner proof, every91profile fullrows, strict controls.',numeric_threshold='Exact integer/Fraction arithmetic only.',resources=dict(outer_seconds=180,worker_seconds=args.seconds,reserve_seconds=15),independent_requirement='Prior independent raw row reconstruction reused explicitly, no conditional rank reused, no discovery code imported. No realizedgraphs/exclusions.'))
        # Calibrate new rank path on hand matrices; smaller positive rectangle.
        full=[([(0,1),(1,2),(2,3)],0), ([(1,1),(2,4)],0), ([(2,1)],0), ([(0,3),(1,6),(2,9)],0)]
        deficient=[full[0],full[1],full[3]]
        need(rank_sparse(full,3,1009,deadline)['rank']==3 and rank_sparse(deficient,3,1009,deadline)['rank']==2,'RANK_POSITIVE_CONTROLS');controls.append(dict(name='full_and_deficient_hand_rank',outcome='PASS',ranks=[3,2]))
        reject(controls,'composite_modulus','PRIME_MODULUS',lambda:rank_sparse(full,3,1000,deadline))
        need(len(list(it.product(range(3),range(4))))==12,'RECTANGLE_POSITIVE_CONTROL');controls.append(dict(name='hand_rectangle12_integer_points4corners',outcome='PASS'))
        for label,q,stage in [('zero_denominator',[1,0],'RATIONAL_SYNTAX'),('float',[1.0,1],'RATIONAL_SYNTAX'),('fractional_count',[1,2],'INTEGRAL_VECTOR')]:reject(controls,label,stage,lambda q=q:vector([q]*394))
        model=raw[MODEL];prior=raw[PRIOR];cert=raw[KERNEL];domain=raw[DOMAIN];summary=raw[SUMMARY]
        need(model['adjacent_roots'] is True and model['variables']==prior['variables'] and model['equations']==prior['reconstructed_rows'],'PRIOR_INDEPENDENT_OPERATOR_IDENTITY')
        need(raw[OLD]['status']=='INDEPENDENT_CONDITIONAL_PRISMFREE_ROOTED6_EDGE_RIGIDITY_PASS','PRIOR_GEOMETRY_RECORD')
        variables=model['variables'];need(len(variables)==394 and [variables[j] for j in AXES]==[[6,8025],[6,15541]],'ACTUAL_COUNT_AXES');rs=rows(model['equations'])
        need(cert['format']=='EXACT_ROOTED6_AFFINE_NULLSPACE_V1' and cert['rank_lower_bound']['free_coordinates']==AXES and len(cert['rational_vectors'])==2,'KERNEL_SHAPE');basis=[vector(v) for v in cert['rational_vectors']]
        need([[v[j] for j in AXES] for v in basis]==[[1,0],[0,1]],'IDENTITY_MINOR');need(all(holds(rs,v,True) for v in basis),'KERNEL_EQUATIONS')
        rank=rank_sparse(rs,394,1009,deadline);need(rank['rank']==392,'FRESH_PRIME_RANK')
        need(cert['exact_rational_rank']==392 and cert['exact_nullity']==2 and cert['rank_upper_bound_from_independent_vectors']==392 and domain['exact_rational_rank']==392 and domain['exact_nullity']==2,'EXACT_RANK_BOUNDS')
        primal=raw[PRIMAL]['exact_primal'];need(len(primal)==394 and all(type(x) is int and x>=0 for x in primal) and holds(rs,primal),'RAW_PRIMAL');origin=[primal[j]-sum(primal[axis]*basis[q][j] for q,axis in enumerate(AXES)) for j in range(394)]
        need(holds(rs,origin) and [origin[j] for j in AXES]==[0,0],'ORIGIN_EQUATIONS')
        need(vector(domain['origin'])==origin and [vector(v) for v in domain['basis']]==basis and domain['free_coordinates']==AXES and domain['free_variables']==[variables[j] for j in AXES] and domain['coordinate_order']==['triangle_edge_prism','matching_edge_prism'],'RAW_AFFINE_IDENTITY')
        wrong=origin[:];wrong[0]+=1;reject(controls,'changed_origin','ORIGIN_EQUATIONS',lambda:need(holds(rs,wrong),'ORIGIN_EQUATIONS'))
        wrong=basis[0][:];wrong[0]+=1;reject(controls,'changed_kernel','KERNEL_EQUATIONS',lambda:need(holds(rs,wrong,True),'KERNEL_EQUATIONS'))
        changed=copy.deepcopy(model);changed['equations'][0]['terms'][0][1]+=1;reject(controls,'changed_raw_row','PRIOR_INDEPENDENT_OPERATOR_IDENTITY',lambda:need(changed['equations']==prior['reconstructed_rows'],'PRIOR_INDEPENDENT_OPERATOR_IDENTITY'))
        reject(controls,'axis_swap','IDENTITY_MINOR',lambda:need([[v[j] for j in AXES] for v in basis[::-1]]==[[1,0],[0,1]],'IDENTITY_MINOR'))
        forms=[(basis[0][j],basis[1][j],origin[j]) for j in range(394)];witness=facets(forms)
        reject(controls,'omitted_upperfacet','FACET_IDENTITIES',lambda:facets([f for f in forms if normalize(f)!=(-1,0,12)]))
        corners=list(it.product((0,12),(0,6)));corner_records=[]
        for point in corners:
            vals=affine(origin,basis,point);need(min(vals)>=0 and holds(rs,vals),'CORNER_COORDINATES');corner_records.append(dict(parameters=list(point),full_count_vector=vals))
        need({tuple(Fraction(*x) for x in v) for v in domain['vertices']}==set(corners) and len(domain['vertices'])==4,'VERTEX_CENSUS')
        changed_vertices=domain['vertices'][:-1];reject(controls,'omitted_vertex','VERTEX_CENSUS',lambda:need(len(changed_vertices)==4,'VERTEX_CENSUS'))
        six=[j for j,(h,m) in enumerate(variables) if h==6];total=math.comb(97,4)
        need(len(six)==307 and sum(origin[j] for j in six)==total and all(sum(v[j] for j in six)==0 for v in basis),'ORDER6_TOTAL')
        norms=set(map(normalize,forms));norms.update({(-1,0,total),(0,-1,total)})
        need(set(map(tuple,domain['inequalities_primitive_integer']))==norms,'ALL_NONNEGATIVITY_FORMS')
        need(len(domain['inequalities_primitive_integer'])==len(domain['inequality_raw_coordinate_witnesses']),'FACET_RAW_MAP')
        for form,mapped in zip(domain['inequalities_primitive_integer'],domain['inequality_raw_coordinate_witnesses']):need(mapped==[j for j,f in enumerate(forms) if normalize(f)==tuple(form)],'FACET_RAW_MAP')
        shape=[geometry(8025,'triangle_edge'),geometry(15541,'matching_edge')]
        reject(controls,'changed_prism_shape','PRISM_GEOMETRY',lambda:geometry(8025^2,'triangle_edge'))
        reject(controls,'wrong_prism_root_type','PRISM_ROOT_TYPE',lambda:geometry(8025,'matching_edge'))
        points=[];records=[]
        for s,t in it.product(range(13),range(7)):
            tick(deadline);vals=affine(origin,basis,(s,t));need(all(type(x) is int and x>=0 for x in vals) and [vals[j] for j in AXES]==[s,t] and holds(rs,vals),'EVERY_INTEGER_PROFILE_ALL_ROWS');points.append([s,t]);records.append(dict(parameters=[s,t],full_count_vector=vals))
        census(domain['integer_points'],points,'INTEGER_CENSUS');need(len(points)==91 and domain['integer_bounding_rectangle']==[[0,12],[0,6]] and domain['bounding_integer_population']==91 and domain['complete_integer_domain'] is True and domain['graph_realizability_asserted'] is False,'EXACT_DOMAIN_SCOPE')
        reject(controls,'omitted_profile','INTEGER_CENSUS',lambda:census(points[:-1],points,'INTEGER_CENSUS'));reject(controls,'duplicate_profile','INTEGER_CENSUS',lambda:census(points+[points[0]],points,'INTEGER_CENSUS'))
        changed=copy.deepcopy(points);changed[-1]=[13,6];reject(controls,'outside_profile','INTEGER_CENSUS',lambda:census(changed,points,'INTEGER_CENSUS'))
        outside=[]
        for point in [(-1,0),(0,-1),(13,0),(0,7)]:need(min(affine(origin,basis,point))<0,'OUTSIDE_RECTANGLE');outside.append(list(point))
        controls.append(dict(name='outside_allfourfacets',outcome='REJECTED_BY_NEGATIVE_COORDINATE',points=outside))
        need(summary['exact_rank']==392 and summary['exact_nullity']==2 and summary['integer_profile_count']==91 and summary['target_resolution'] is False,'SUMMARY_SCOPE')
        reject(controls,'false_rank_claim','EXACT_RANK_BOUNDS',lambda:need(rank['rank']==393,'EXACT_RANK_BOUNDS'))
        save(out/'controls.json',controls);save(out/'rank_certificate.json',rank);save(out/'facet_corner_proof.json',dict(facets=witness,corners=corner_records,origin=origin,basis=basis,prism_root_classes=shape,convex_argument='s/12,t/6 in[0,1]; four bilinear nonnegative weights sum1 and reproduce coordinates. Every affine form nonnegative at allfourcorners; literal facets give reverse inclusion.',prior_geometry_reused=True,fresh_prime_rank=True));save(out/'complete_integer_profiles.json',records)
        for file in out.iterdir():
            if file.is_file():pin(file.relative_to(ROOT).as_posix())
        result=dict(status='INDEPENDENT_UNRESTRICTED_ROOTED6_EDGE_EXACT_KERNEL_INTEGER_DOMAIN_V1_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),producer='/root/structural',verifier='/root/checkpoint_audit',method='independent_derivation',inputs_sha256=pins,statement=STATEMENT,scope='Complete exact necessary local operator kernel and nonnegative rational/integer domain,unrestricted target necessary scope,no prism-free premise or graph realization.',rows=1099,columns=394,rational_rank=392,nullity=2,independent_prime=1009,rational_vertices=4,integer_profiles=91,integer_all_row_checks=91*1099,integer_all_coordinate_checks=91*394,coordinate_vertex_checks=394*4,controls=len(controls),strict_rejection_controls=sum(c['outcome']=='REJECTED' for c in controls),shared_components=['Previously independently reconstructed complete raw operator and known-valid control record reused as pinned data only; no old conditional rank conclusion reused.','New purePython sparse incremental modulo1009 elimination,independent of discovery NumPy/65521 lifting.','Python exact integers/Fraction/stdlib and command_deadline scheduling.'],limitations=['No count vector certified as realized in any target graph.','Complete geometry necessity reused from pinned prior independent audit,not newly generated; new exactrank/domain independently checked.','No graph exclusion,existence/nonexistence,novelty,external review or target-wide coverage follows.'],artifact_availability='LOCAL_ONLY',target_resolution='NONE',new_exclusions=0,graph_realizability_asserted=False,elapsed_seconds=time.monotonic()-started,deadline=deadline.status())
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],report_sha256=sha(out/'summary.json'),elapsed_seconds=result['elapsed_seconds'])),flush=True)
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),stage=getattr(error,'stage',None),elapsed_seconds=time.monotonic()-started,outputs_preserved=True,target_resolution='NONE'));raise
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);run(ap.parse_args())
