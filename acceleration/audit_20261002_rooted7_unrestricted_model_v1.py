"""Independent unrestricted rooted7 ordinary/reroot/domain/coupling necessity.

Shares prior independently authored geometry and mean-fixture helpers only.
Discovery builder is not imported. Every literal model row is reconstructed.
"""
import argparse,copy,hashlib,itertools as it,json,math,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
from command_deadline import CommandDeadline
import audit_20261002_rooted7_model_v1 as old
import audit_20261002_rooted6_means_v2 as means
ROOT=Path(__file__).resolve().parents[1];P='acceleration/results/'
MODEL=P+'20261002_rooted7_unrestricted_extension01/model.json'
CAT=P+'20261002_rooted7_extension_model/catalogue.json'
ND=P+'20261002_rooted6_unrestricted_domain01/domain.json'
ED=P+'20261002_rooted6_unrestricted_edge_domain01/domain.json'
NMODEL=P+'20261002_rooted6_prismfree_rigidity/ordered_nonedge_model.json'
EMODEL=P+'20261002_rooted6_prismfree_rigidity/ordered_edge_model.json'
MATRIX=P+'20260930_srg243_residual_fixture/adjacency243.json'
PINS={MODEL:'9f636889690071f69ad7a103b02abb2f43a5bbc2d2114c87a779da29c0f647a1',CAT:'a01649d78eccfcb93c85ff2a86c84463458c120fd22cebaf34b8e573363084d5',ND:'dcf63f8a34784fe0a125d52a12423239f72559bfeeb370bc8ccda0b5404c3381',ED:'e2cade276f89c87ece74df8544c99704ce116bb55d84a5bd5e364c6264d75c95',NMODEL:'ecf558faa95576b8e76fbc5a62743729a875307eeb99df803c7cb5cdac7b7645',EMODEL:'06051294a142dfcda956f4ee3748986982f7f8ba5f9785fe4d7680d967538584',MATRIX:'5c7c8268b7d62997b5c87a56b11fd673f3f80fcb029b83816179ee8127b8e0d3','acceleration/audit_20261002_rooted7_model_v1.py':'e796b8cd30d23750429a66f0a4b9366f5eeff12537c7b0ed0da13526f6a95734','acceleration/audit_20261002_rooted5_rigidity_v2.py':'b281675c501cbf49116b2c1f6cfd6beb55d0bdf00b0bacc34bf8e9b42660f0ed','acceleration/audit_20261002_rooted6_means_v2.py':'d023ed3efeb765be69f58e156a13ab82864a187fe2472d6b83b1277055a25b98','acceleration/theory_20261002_rooted7_unrestricted_extension_v1.py':'79ac64a725b5b09a18a28b4703d9fb7affaaf49dfed3152db098c6d104ccb191','docs/PROTOCOL_20261002_UNRESTRICTED_ROOTED7_EXTENSION_V1.md':'b7f334a6437b53c308825e18b73a001ee15ae8c4b40c4f9615b2e66bcb740546',P+'20261002_independent_review/rooted6_unrestricted_domain01/summary.json':'63addcfc02c13b516d3fe379646d5bc82950c2b9444914d668f66b6713529e00',P+'20261002_independent_review/rooted6_unrestricted_edge_domain01/summary.json':'3199d91f6d2c7f7de601584802412bfa86e2c6a5dfeca6fdddef03c7fe8371fe',P+'20261002_independent_review/rooted6_means02/summary.json':'ffd497c6afacb9173bcb215eceab7603e7530d18d9c4a51dad6ea0e7d8e1d025',P+'20261002_independent_review/rooted7_catalogue01/summary.json':'3355afb38656eadc83eff6e0db3818eded9621f890c9d46f489fdb0324370758'}
class AuditError(ValueError):
    def __init__(self,stage):self.stage=stage;super().__init__(stage)
def need(ok,stage):
    if not ok:raise AuditError(stage)
def sha(p):
    with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as s:json.dump(x,s,indent=2,sort_keys=True);s.write('\n')
def vector(raw):
    out=[]
    for x in raw:
        q=Fraction(*x) if isinstance(x,list) else Fraction(x);need(q.denominator==1,'EXACT_INTEGRAL_PROFILE');out.append(int(q))
    return out
def profiles(model,domain):
    origin=vector(domain['origin']);basis=[vector(v) for v in domain['basis']]
    need(all(sum(origin[j]*c for j,c in row['terms'])==row['rhs'] for row in model['equations']) and all(all(sum(v[j]*c for j,c in row['terms'])==0 for row in model['equations']) for v in basis),'EVERY_LOWER_PROFILE_ROW')
    return {m:origin[j] for j,(h,m) in enumerate(model['variables']) if h==6},[{m:v[j] for j,(h,m) in enumerate(model['variables']) if h==6} for v in basis]
def layout(seven):
    variables=[[7,m] for m in seven];agg={}
    for anchor in range(2):
        for partition in range(4):
            relation='edge' if partition&(1<<anchor) else 'nonedge'
            for q,name in enumerate(['s','t'] if relation=='edge' else ['c','a','b']):agg[anchor,partition,q]=len(variables);variables.append(['aggregate',relation,anchor,partition,name])
    return variables,agg
def reroot(six,seven,lookup,cards,eo,eb,no,nb,agg,tick):
    rows=[];positions={}
    for anchor in range(2):
        for partition in range(4):
            relation='edge' if partition&(1<<anchor) else 'nonedge';o,b=(eo,eb) if relation=='edge' else (no,nb)
            for mask,constant in sorted(o.items()):
                positions[anchor,partition,mask]=len(rows)
                rows.append(dict(kind='reroot6',anchor=anchor,partition=partition,relation=relation,new_root6mask=mask,terms=[[agg[anchor,partition,q],-v[mask]] for q,v in enumerate(b) if v[mask]] if agg else [],known_terms=[],rhs=cards[partition]*constant))
    terms=[Counter(dict(r['terms'])) for r in rows];collisions=[Counter() for r in rows];choices=0
    for h,masks in [(6,six),(7,seven)]:
        for j,mask in enumerate(masks):
            g=old.geometry.matrix(h,mask)
            for anchor in range(2):
                for marked in range(2,h):
                    partition=g[0][marked]+2*g[1][marked];free=[v for v in range(h) if v not in (anchor,marked) and (h==6 or v!=1-anchor)]
                    need(len(free)==4,'UNION_COLLISION_GEOMETRY');flag=lookup[old.geometry.bits(g,(anchor,marked,*free))];at=positions[anchor,partition,flag]
                    if h==6:collisions[at][mask]+=1
                    else:terms[at][j]+=1
                    choices+=1
            tick()
    for row,coeff,known in zip(rows,terms,collisions):row['terms']=[[j,c] for j,c in sorted(coeff.items()) if c];row['known_terms']=[[m,c] for m,c in sorted(known.items()) if c]
    return rows,choices
def bounds(variables,agg,cards):
    rows=[]
    for anchor in range(2):
        for p in range(4):
            relation='edge' if p&(1<<anchor) else 'nonedge';d=cards[p];ids=[agg[anchor,p,q] for q in range(2 if relation=='edge' else 3)]
            descriptors=[('s_upper',[[ids[0],1]],12*d),('t_upper',[[ids[1],1]],6*d)] if relation=='edge' else [('c_upper',[[ids[0],1]],2*d),('a_upper',[[ids[1],1]],20*d),('b_upper',[[ids[2],2],[ids[0],-1]],18*d)]
            for name,terms,rhs in descriptors:
                slack=len(variables);variables.append(['aggregate_slack',relation,anchor,p,name]);rows.append(dict(kind='aggregate_domain_facet',anchor=anchor,partition=p,relation=relation,facet=name,terms=sorted(terms+[[slack,1]]),known_terms=[],rhs=rhs))
    return rows
def couplings(agg,n,k):
    rows=[];need(k*(k-2)==2*(n-k-1),'PARAMETER_RELATION')
    for anchor in range(2):
        ns=[p for p in range(4) if not p&(1<<anchor)];es=[p for p in range(4) if p&(1<<anchor)]
        descriptors=[('almost_triangle_mean',[[agg[anchor,p,q],1] for p in ns for q in (0,1)],[[7100,1],[8024,1]],k*(k-2)),('almost_matching_mean',[[agg[anchor,p,0],1] for p in ns]+[[agg[anchor,p,2],2] for p in ns],[[7100,1],[15540,2]],2*(n-k-1)),('triangle_prism_incidence',[[agg[anchor,p,0],1] for p in es]+[[agg[anchor,p,0],-1] for p in ns],[[7100,-1]],0),('matching_prism_incidence',[[agg[anchor,p,1],2] for p in es]+[[agg[anchor,p,0],-1] for p in ns],[[7100,-1]],0)]
        rows.extend(dict(kind='unrestricted_pervertex_coupling',anchor=anchor,identity=name,terms=sorted(terms),known_terms=known,rhs=rhs) for name,terms,known,rhs in descriptors)
    return rows
def residual(row,unknown,known):return sum(c*unknown[j] for j,c in row['terms'])+sum(c*known.get(mask,0) for mask,c in row['known_terms'])-row['rhs']
def verify(raw,variables,rows,equations,eo,eb,no,nb):
    need(raw['format']=='ROOTED7_UNRESTRICTED_EXTENSION_AFFINE_MODEL_V1','RAW_FORMAT');need(raw['variables']==variables,'VARIABLE_COVERAGE')
    projection=lambda row:{k:v for k,v in row.items() if k not in ('rhs_reason','scope')}
    need(list(map(projection,raw['row_derivation_descriptors']))==list(map(projection,rows)),'EVERY_RAW_ROW_COEFFICIENT');need(raw['equations']==equations,'EVERY_AFFINE_RHS')
    stringify=lambda x:{str(k):v for k,v in x.items()}
    need(raw['root6_nonedge_profile_basis']==dict(origin=stringify(no),basis=list(map(stringify,nb))) and raw['root6_edge_profile_basis']==dict(origin=stringify(eo),basis=list(map(stringify,eb))),'EVERY_LOWER_BASIS')
    need(raw['affine_RHS_coordinate_order']==['constant','c','a','b'] and raw['secondary_aggregate_partition_cardinalities']=={'0':71,'1':12,'2':12,'3':2},'EXACT_PARAMETERS')
def reject(out,name,expected,fn):
    try:fn()
    except AuditError as e:need(e.stage==expected,'CONTROL_WRONG_STAGE');out.append(dict(name=name,stage=e.stage,outcome='REJECTED'));return
    raise AuditError('CONTROL_ACCEPTED_'+name)
def pair_profiles(g,prisms,a,b):
    counts=Counter();tu=Counter();size=len(g)
    for six in prisms:
        tri=[q for q in it.combinations(six,3) if all(v in g[u] for u,v in it.combinations(q,2))];need(len(tri)==2,'INDUCED_PRISM_CLASS')
        for u in six:tu[u]+=1
        for u,v in it.permutations(six,2):
            mask=7100 if v not in g[u] else 8025 if any(u in q and v in q for q in tri) else 15541;counts[u,v,mask]+=1
    for counter,mask in [(a,8024),(b,15540)]:
        for (u,v,six),count in counter.items():need(count==1,'ALMOST_PRISM_OCCURRENCE');counts[u,v,mask]+=1
    for u in range(size):need(sum(counts[u,v,7100] for v in range(size) if v!=u and v not in g[u])==2*tu[u] and sum(counts[u,v,8025] for v in g[u])==2*tu[u] and sum(counts[u,v,15541] for v in g[u])==tu[u],'PRISM_INCIDENCE_FACTORS')
    return counts,tu
def aggregate_counts(g,root,agg,counts):
    value={};cards=Counter();u,v=root
    for w in range(len(g)):
        if w in root:continue
        p=int(w in g[u])+2*int(w in g[v]);cards[p]+=1
        for anchor in range(2):
            masks=[8025,15541] if p&(1<<anchor) else [7100,8024,15540]
            for q,mask in enumerate(masks):index=agg[anchor,p,q];value[index]=value.get(index,0)+counts[root[anchor],w,mask]
    return value,cards
def fixture(matrix,k,label,out,deadline,variables,agg,map6,map7,six,seven,geometry_rows,controls,tick):
    # Prior independently authored scalar/wedge/cycle paths calibrate means;
    # new complete prism rootedpair classification/partition paths are authored here.
    record,vertex,g,a,b,prisms=means.fixture(matrix,k,label,out,deadline);counts,tu=pair_profiles(g,prisms,a,b);coupling=couplings(agg,len(g),k);reports=[];coupling_checks=0;rook_row_checks=0
    if len(g)<=9:
        lower_cache={}
        for u,v in it.permutations(range(len(g)),2):
            direct=old.count(matrix,(u,v),6,map6);lower_cache[u,v]=direct
            for mask in ([8025,15541] if v in g[u] else [7100,8024,15540]):need(direct[mask]==counts[u,v,mask],'ROOK_RAW_PAIR_FLAG_COUNTS')
        ordinary_rows,_=old.ordinary(six,seven,map6,len(g),k,1,2,tick)
    expected_cards={0:len(g)-2-2*(k-2)-2,1:k-2,2:k-2,3:2}
    for u in range(len(g)):
        tick()
        for v in range(len(g)):
            if u==v or v in g[u]:continue
            value,cards=aggregate_counts(g,(u,v),agg,counts);need(dict(cards)==expected_cards,'ACTUAL_PARTITION_CARDINALITIES');known={m:counts[u,v,m] for m in (7100,8024,15540)}
            need(all(residual(r,value,known)==0 for r in coupling),'EVERY_PRIMARY_COUPLING_ROW');coupling_checks+=8
            if len(g)<=9:
                lower=lower_cache[u,v];upper=old.count(matrix,(u,v),7,map7);unknown=[upper[m] for m in seven];need(all(residual(r,unknown,lower)==0 for r in ordinary_rows),'ROOK_EVERY_MARKED_EXTENSION')
                # Geometric reroot sums use actual individually counted lower
                # profiles; target99 affine coefficients never enter fixture.
                for row in geometry_rows:
                    lhs=sum(c*unknown[j] for j,c in row['terms'] if j<len(seven))+sum(c*lower[m] for m,c in row['known_terms'])
                    p=row['partition'];anchor=row['anchor'];rhs=sum(lower_cache[u if anchor==0 else v,w][row['new_root6mask']] for w in range(len(g)) if w not in (u,v) and int(w in g[u])+2*int(w in g[v])==p)
                    need(lhs==rhs,'ROOK_EVERY_REROOT_UNION_COLLISION');rook_row_checks+=1
            reports.append(dict(root=[u,v],primary_cab=[known[7100],known[8024],known[15540]],aggregate_values=[[j,value.get(j,0)] for j in sorted(agg.values())],all8coupling_residuals=[0]*8))
    # Calibration at a positive-prism actual root, with all vectors separately computed.
    sample=reports[0];root=tuple(sample['root']);value=dict(sample['aggregate_values']);known=dict(zip((7100,8024,15540),sample['primary_cab']));need(known[7100]>0,'POSITIVE_PRISM_PRIMARY_CONTROL')
    changed=known.copy();changed[7100]+=1;reject(controls,label+'_changed_primary_c','EVERY_PRIMARY_COUPLING_ROW',lambda:need(all(residual(r,value,changed)==0 for r in coupling),'EVERY_PRIMARY_COUPLING_ROW'))
    for q,row in enumerate(coupling):
        altered=copy.deepcopy(row);j,c=next((j,c) for j,c in row['terms'] if value.get(j,0)!=0);altered['terms'][altered['terms'].index([j,c])][1]+=1
        reject(controls,label+'_changed_nonzero_coupling_coefficient_'+str(q),'EVERY_PRIMARY_COUPLING_ROW',lambda r=altered:need(residual(r,value,known)==0,'EVERY_PRIMARY_COUPLING_ROW'))
    save(out/(label+'_all_primary_coupling_records.json'),reports)
    return dict(label=label,actual_primary_roots=len(reports),coupling_checks=coupling_checks,prisms=len(prisms),complete_prism_vertex_incidence_checks=len(prisms)*6,actual_partition_cardinalities=expected_cards,all_lower_72_rook_pairs_checked=len(g)<=9,rook_reroot_checks=rook_row_checks,mean_fixture_record=record)
def run(args):
    started=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='New unrestricted2810x11769 operator fullindependent reconstruction androok9/243couplings; prior audit4.30s,180outer150worker30reserve,no solver')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};controls=[]
    def tick():need(deadline.status()['remaining_seconds']>30,'DEADLINE_RESERVE')
    def pin(name,wanted=None):actual=sha(ROOT/name);need(wanted is None or actual==wanted,'FROZEN_INPUT_HASH');pins[name]=actual;return actual
    try:
        for name,wanted in PINS.items():pin(name,wanted)
        for name in [Path(__file__).relative_to(ROOT).as_posix(),'acceleration/audit_20261002_rooted7_unrestricted_model_v1_spec.md','acceleration/audit_20261002_rooted7_unrestricted_model_v1_proof.md','docs/DESIGN_20261002_UNRESTRICTED_ROOTED7_EXTENSION_V2.md','acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml']:pin(name)
        source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();raw={name:json.loads((ROOT/name).read_bytes()) for name in PINS if name.endswith('.json')}
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,selection='All2770classes,allmarked transports/allrerootchoices,allliteral rows andRHS,allrook9 and243 primarynonedgecouplings.',success='Exact everyrow equality,independent writtencoupling proof plus positive/corruptcontrols beforepromotion; no commonsecondaryprofile orprismfreeassumption.',numerical_threshold='Exact arithmetic only.',resources=dict(outer_seconds=180,worker_seconds=args.seconds,reserve_seconds=30),shared='Earlier independently authored geometry/ordinary rows andmeans fixture paths, no producer import.'))
        seven=raw[CAT]['complete_locally_admissible_masks'];six=[m for h,m in raw[NMODEL]['variables'] if h==6];edge_six=[m for h,m in raw[EMODEL]['variables'] if h==6];need((len(seven),len(six),len(edge_six))==(2770,456,307),'COMPLETE_FLAG_POPULATIONS')
        map6=old.orbit_map(6,six+edge_six,tick);map7=old.orbit_map(7,seven,tick);no,nb=profiles(raw[NMODEL],raw[ND]);eo,eb=profiles(raw[EMODEL],raw[ED]);need(len(nb)==3 and len(eb)==2,'VARIABLE_LOWER_PROFILES')
        variables,agg=layout(seven);cards={0:71,1:12,2:12,3:2};ordinary,transports=old.ordinary(six,seven,map6,99,14,1,2,tick);rerooted,choices=reroot(six,seven,map6,cards,eo,eb,no,nb,agg,tick);facet_rows=bounds(variables,agg,cards);coupling=couplings(agg,99,14)
        rows=ordinary+rerooted+facet_rows+coupling;equations=[dict(terms=r['terms'],rhs_affine=[r['rhs']-sum(c*no[m] for m,c in r['known_terms'])]+[-sum(c*b[m] for m,c in r['known_terms']) for b in nb]) for r in rows]
        rook=[[int(u!=v and (u//3==v//3 or u%3==v%3)) for v in range(9)] for u in range(9)]
        fixtures=[fixture(rook,4,'rook9',out,deadline,variables,agg,map6,map7,six,seven,rerooted,controls,tick),fixture(raw[MATRIX]['adjacency'],22,'srg243',out,deadline,variables,agg,map6,map7,six,seven,rerooted,controls,tick)]
        # Model literal calibration protects every operator component, beyond
        # the sparse support of highly symmetric positive graph fixtures.
        model=raw[MODEL];verify(model,variables,rows,equations,eo,eb,no,nb)
        for name,stage,mutate in [('omit_variable','VARIABLE_COVERAGE',lambda r:r['variables'].pop()),('marked_coefficient','EVERY_RAW_ROW_COEFFICIENT',lambda r:r['row_derivation_descriptors'][1]['terms'][0].__setitem__(1,r['row_derivation_descriptors'][1]['terms'][0][1]+1)),('affine_rhs','EVERY_AFFINE_RHS',lambda r:r['equations'][0]['rhs_affine'].__setitem__(0,r['equations'][0]['rhs_affine'][0]+1)),('secondary_edge_uniformity','EVERY_LOWER_BASIS',lambda r:r['root6_edge_profile_basis']['basis'].pop()),('omit_coupling','EVERY_RAW_ROW_COEFFICIENT',lambda r:r['row_derivation_descriptors'].pop()),('domain_facet_coefficient','EVERY_RAW_ROW_COEFFICIENT',lambda r:r['row_derivation_descriptors'][-9]['terms'][0].__setitem__(1,7))]:
            damaged=copy.deepcopy(model);mutate(damaged);reject(controls,name,stage,lambda d=damaged:verify(d,variables,rows,equations,eo,eb,no,nb))
        need(len(variables)==2810 and len(rows)==11769 and sum(len(r['terms']) for r in equations)==89350,'COMPLETE_OPERATOR_DIMENSIONS')
        need(model['parameter_domain']['complete_integer_profiles']==raw[ND]['integer_points'] and model['parameter_domain']['rational_vertices']==[[int(Fraction(*x)) for x in p] for p in raw[ND]['vertices']],'PRIMARY_DOMAIN_IDENTITY')
        save(out/'controls.json',controls);save(out/'reconstructed_model.json',dict(variables=variables,equations=equations,row_derivation_descriptors=rows,every_lower_isomorphism_checks=transports,reroot_union_collision_choices=choices,row_type_counts=dict(Counter(r['kind'] for r in rows))));save(out/'fixture_summary.json',fixtures)
        for p in out.iterdir():
            if p.is_file():pin(p.relative_to(ROOT).as_posix())
        report=dict(status='INDEPENDENT_UNRESTRICTED_ROOTED7_NECESSARY_OPERATOR_V1_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),producer='/root/structural',verifier='/root/checkpoint_audit',method='independent_derivation',inputs_sha256=pins,statement='Every integer coefficient,union/collision term,secondary aggregate facet,eight per-anchor prism/mean coupling rows andconstant,c,a,b affine RHS of the frozen2810-variable11769-row89350-term unrestricted ordered-nonedge rooted7 operator is independently reconstructed as a necessary count relation for every actual ordered nonedge of any srg(99,14,1,2),without a prism-free,target automorphism orcommonsecondaryprofile premise. Secondary edge(s,t) andnonedge(c,a,b) coordinates may vary per actual pair; feasibility of these necessary equations does not certify graph realization.',variables=2810,rows=11769,terms=89350,root7_classes=2770,secondary_aggregates=20,integer_slacks=20,every_lower_isomorphism_checks=transports,reroot_union_collision_choices=choices,fixtures=fixtures,strict_negative_controls=len(controls),shared_components=['Pinned prior independently authored root5 geometry androot7 marked-orbit helpers.','Pinned independent mean scalar/wedge/cycle fixture helpers; newprism pairclassification/partition/coupling checking authoredhere.','Python exact integers/Fraction/stdlib,locked uv environment,command_deadline scheduling; no discovery builder imported.'],dependencies=[dict(id=x,revision=1,relation='uses_result') for x in ['C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE','C-UNRESTRICTED-ROOTED6-NONEDGE-INTEGER-DOMAIN','C-UNRESTRICTED-ROOTED6-EDGE-KERNEL-INTEGER-DOMAIN','C-UNRESTRICTED-ROOTED6-PER-VERTEX-GLOBAL-PRISM-MEAN-IDENTITIES']],limitations=['Necessary local count operator only; no realization,integerfeasibility,rank,LPcertificate,profile exclusion,target resolution orcoverage fraction.','Prior finitecatalogue/lowerdomains/means are reused pinned dependencies; no priorconditionalprism-free conclusion is a premise.','For243vertices complete prism/means coupling incidences are checked; full rooted7 geometric enumeration is performed onrook9 only.','Rook9/243a,bcounts arezero; mean coefficients additionally rely on the independently reviewed universal mean proof,not finiteagreement.'],target_resolution='NONE',new_exclusions=0,graph_realizability_asserted=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-started,deadline=deadline.status())
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],report_sha256=sha(out/'summary.json'),elapsed_seconds=report['elapsed_seconds'])),flush=True)
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),stage=getattr(e,'stage',None),elapsed_seconds=time.monotonic()-started,inputs_sha256=pins,outputs_preserved=True,target_resolution='NONE'));raise
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);run(ap.parse_args())
