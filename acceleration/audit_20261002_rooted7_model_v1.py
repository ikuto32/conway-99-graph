"""Independent every-isomorphism marked/reroot necessary rooted7 model audit."""
from __future__ import annotations
import argparse,copy,hashlib,json,math,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
from itertools import combinations,permutations
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261002_rooted5_rigidity_v2 as geometry

ROOT=Path(__file__).resolve().parents[1]
MODEL='acceleration/results/20261002_rooted7_extension_model/model.json'
MODEL_SHA='21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595'
CAT='acceleration/results/20261002_rooted7_extension_model/catalogue.json'
CAT_SHA='a01649d78eccfcb93c85ff2a86c84463458c120fd22cebaf34b8e573363084d5'
SIX='acceleration/results/20261002_rooted6_prismfree_rigidity/'
PARAM='acceleration/results/20261002_rooted6_exact_parameter_domain/'
FROZEN={
 MODEL:MODEL_SHA,CAT:CAT_SHA,
 SIX+'ordered_nonedge_model.json':'ecf558faa95576b8e76fbc5a62743729a875307eeb99df803c7cb5cdac7b7645',
 SIX+'ordered_edge_model.json':'06051294a142dfcda956f4ee3748986982f7f8ba5f9785fe4d7680d967538584',
 SIX+'ordered_edge_prismfree_primal.json':'8c914f27e91f5c003644148738b9a634ac0dfe9683915dd42dc3ae067d2a2010',
 PARAM+'prismfree_nonedge_domain.json':'54f08f8dc87bebf61bada59067cbc721497f3d3a9683936e850b695f0ec41b12',
 PARAM+'prismfree_nonedge_nullspace.json':'b8abff4be27e90c5d1274cf94ee8aff262cf02117a2086cfdffec5dc97a13e77',
 'acceleration/results/20261002_independent_review/rooted6_nonedge_domain01/summary.json':'65081849ccf721eae5bdf569b16f44c88255e0421f5fab1ec26a7fa7f36e8271',
 'acceleration/results/20261002_independent_review/rooted6_prismfree02/summary.json':'f7e8f93a671648cd0e73c326a36ee8cc97682a2c568ed88f46044cb04abd4717',
 'acceleration/results/20261002_independent_review/rooted7_catalogue01/summary.json':'3355afb38656eadc83eff6e0db3818eded9621f890c9d46f489fdb0324370758',
 'acceleration/audit_20261002_rooted5_rigidity_v2.py':'b281675c501cbf49116b2c1f6cfd6beb55d0bdf00b0bacc34bf8e9b42660f0ed',
}


def need(value,why):
    if not value:raise ValueError(why)


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')


def orbit_map(order,representatives,tick):
    lookup={}
    for representative in tqdm(representatives,desc='independent labelled orbit map'+str(order),mininterval=5):
        for image in geometry.orbit(order,representative):
            need(image not in lookup or lookup[image]==representative,'distinct coordinate orbits')
            lookup[image]=representative
        tick()
    return lookup


def ordinary(six,seven,lookup,n,k,lam,mu,tick):
    rows=[dict(kind='order7_total',terms=[[i,1] for i in range(len(seven))],known_terms=[],rhs=math.comb(n-2,5))]
    descriptors={};positions={};transports=0
    for mask in six:
        adj=geometry.matrix(6,mask);specs=[('delete',[],n-6)]
        for mark in geometry.mark_orbits(6,mask):
            orbit=[list(value) for value in mark]
            if len(mark[0])==1:kind='degree';left=sum(k-sum(adj[u]) for u, in mark)
            else:kind='pair_common';left=sum((lam if adj[u][v] else mu)-sum(adj[u][w]*adj[v][w] for w in range(6)) for u,v in mark)
            specs.append((kind,orbit,left))
        descriptors[mask]=specs
        for kind,mark,left in specs:
            positions[mask,kind,tuple(map(tuple,mark))]=len(rows)
            rows.append(dict(kind=kind,parent6mask=mask,orbit=mark,terms=[],known_terms=[[mask,-left]] if left else [],rhs=0))
    coeff=[Counter() for _ in rows]
    for j,mask in enumerate(tqdm(seven,desc='all lower isomorphism marked coefficients',mininterval=5)):
        big=geometry.matrix(7,mask)
        for removed in range(2,7):
            free=[v for v in range(2,7) if v!=removed];raw=geometry.bits(big,(0,1,*free));parent=lookup[raw]
            mappings=[(0,1,*tail) for tail in permutations(free) if geometry.bits(big,(0,1,*tail))==parent]
            need(mappings,'explicit lower isomorphism exists')
            for kind,mark,_ in descriptors[parent]:
                values=[1 if kind=='delete' else sum(all(big[removed][mapping[u]] for u in marked) for marked in mark) for mapping in mappings]
                need(len(set(values))==1,'orbit coefficient invariant under every lower isomorphism');transports+=len(values)
                if values[0]:coeff[positions[parent,kind,tuple(map(tuple,mark))]][j]+=values[0]
        tick()
    for i in range(1,len(rows)):rows[i]['terms']=[[col,val] for col,val in sorted(coeff[i].items())]
    return rows,transports


def reroot(six,seven,lookup,cardinalities,edge_counts,origin,bases,aggregates,tick):
    rows=[];positions={}
    for anchor in range(2):
        for partition in range(4):
            adjacent=bool(partition&(1<<anchor));counts=edge_counts if adjacent else origin
            for mask,constant in sorted(counts.items()):
                terms=[]
                if not adjacent and aggregates:
                    terms=[[aggregates[anchor,partition,at],-basis[mask]] for at,basis in enumerate(bases) if basis[mask]]
                positions[anchor,partition,mask]=len(rows)
                rows.append(dict(kind='reroot6',anchor=anchor,partition=partition,relation='edge' if adjacent else 'nonedge',
                                 new_root6mask=mask,terms=terms,known_terms=[],rhs=cardinalities[partition]*constant))
    coefficients=[Counter(dict(row['terms'])) for row in rows];collisions=[Counter() for _ in rows]
    choices=0
    for h,masks in [(6,six),(7,seven)]:
        for j,mask in enumerate(tqdm(masks,desc='independent reroot union/collision'+str(h),mininterval=5)):
            adj=geometry.matrix(h,mask)
            for anchor in range(2):
                for marked in range(2,h):
                    partition=adj[0][marked]+2*adj[1][marked]
                    rest=[v for v in range(h) if v!=anchor and v!=marked and (h==6 or v!=1-anchor)]
                    need(len(rest)==4,'four new-root free vertices')
                    raw=geometry.bits(adj,(anchor,marked,*rest));parent=lookup[raw]
                    at=positions[anchor,partition,parent]
                    if h==6:collisions[at][mask]+=1
                    else:coefficients[at][j]+=1
                    choices+=1
            tick()
    for row,terms,known in zip(rows,coefficients,collisions):
        row['terms']=[[j,v] for j,v in sorted(terms.items()) if v];row['known_terms']=[[mask,v] for mask,v in sorted(known.items()) if v]
    return rows,choices


def verify(raw,variables,rows,equations,origin,bases):
    need(raw['format']=='ROOTED7_CONDITIONAL_EXTENSION_AFFINE_MODEL_V1','exact raw model format')
    need(raw['variables']==variables,'complete labelled flag/aggregate/slack variables')
    descriptors=[{k:v for k,v in row.items() if k!='rhs_reason'} for row in raw['row_derivation_descriptors']]
    need(descriptors==rows,'every marked/reroot/bound descriptor and coefficient reconstructed')
    need(raw['equations']==equations,'every substituted integer affine right-side reconstructed')
    need(raw['root6_profile_basis']=={'origin':{str(k):v for k,v in origin.items()},'basis':[{str(k):v for k,v in basis.items()} for basis in bases]},'exact checked six-profile basis')
    need(raw['parameter_domain']==[[0,20],[0,9]],'actual integer parameter domain')


def count(adj,root,h,lookup):
    counts=Counter()
    for selected in combinations([v for v in range(len(adj)) if v not in root],h-2):
        raw=geometry.bits(adj,(*root,*selected));need(raw in lookup,'actual fixture flag in frozen exact catalogue');counts[lookup[raw]]+=1
    return counts


def holds(rows,unknown,known):
    return all(sum(v*unknown[j] for j,v in row['terms'])+sum(v*known[mask] for mask,v in row['known_terms'])==row['rhs'] for row in rows)


def run(args):
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Every marked lower isomorphism and reroot union/collision coefficient with all actual Petersen roots;30seconds reserve')
    out=args.out.resolve();out.mkdir(exist_ok=False);pins={}
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>30,'not completed within the allocated budget')
    def pin(name,digest=None):
        tick();actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest();need(digest is None or actual==digest,'exact pinned artifact '+name);pins[name]=actual
    def read(name):return json.loads((ROOT/name).read_bytes())
    try:
        for name,digest in FROZEN.items():pin(name,digest)
        for name in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),
                     'acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml']:pin(name)
        catalogue=read(CAT);sixdata=read(SIX+'ordered_nonedge_model.json');edgedata=read(SIX+'ordered_edge_model.json')
        six=[mask for h,mask in sixdata['variables'] if h==6];edge_six=[mask for h,mask in edgedata['variables'] if h==6];seven=catalogue['prismfree_masks']
        need(len(six)==456 and len(edge_six)==307 and len(seven)==2750,'exact independently covered classes')
        map6=orbit_map(6,six+edge_six,tick);map7=orbit_map(7,seven,tick)
        edgevec=read(SIX+'ordered_edge_prismfree_primal.json')['exact_primal'];edgecounts={mask:edgevec[j] for j,(h,mask) in enumerate(edgedata['variables']) if h==6}
        domain=read(PARAM+'prismfree_nonedge_domain.json');null=read(PARAM+'prismfree_nonedge_nullspace.json')
        fullorigin=[Fraction(*value) for value in domain['origin']];fullbases=[[Fraction(*value) for value in vector] for vector in null['rational_vectors']]
        origin={mask:fullorigin[j] for j,(h,mask) in enumerate(sixdata['variables']) if h==6}
        bases=[{mask:vector[j] for j,(h,mask) in enumerate(sixdata['variables']) if h==6} for vector in fullbases]
        need(all(v.denominator==1 for values in [origin,*bases] for v in values.values()),'exact integer profile coefficients')
        origin={k:int(v) for k,v in origin.items()};bases=[{k:int(v) for k,v in values.items()} for values in bases]
        cardinalities={0:99-2-2*(14-2)-2,1:14-2,2:14-2,3:2};need(cardinalities=={0:71,1:12,2:12,3:2},'derived actual external partition sizes')
        variables=[[7,mask] for mask in seven];aggregates={}
        for anchor in range(2):
            for partition in range(4):
                if not partition&(1<<anchor):
                    for coordinate in range(2):aggregates[anchor,partition,coordinate]=len(variables);variables.append(['aggregate',anchor,partition,coordinate])
        ordinary_rows,transports=ordinary(six,seven,map6,99,14,1,2,tick)
        rerooted,reroot_choices=reroot(six,seven,map6,cardinalities,edgecounts,origin,bases,aggregates,tick)
        rows=ordinary_rows+rerooted
        for (anchor,partition,coordinate),at in aggregates.items():
            slack=len(variables);variables.append(['aggregate_slack',anchor,partition,coordinate])
            rows.append(dict(kind='aggregate_rectangle_bound',anchor=anchor,partition=partition,coordinate=coordinate,
                             terms=[[at,1],[slack,1]],known_terms=[],rhs=cardinalities[partition]*(20 if coordinate==0 else 9)))
        equations=[dict(terms=row['terms'],rhs_affine=[row['rhs']-sum(v*origin[mask] for mask,v in row['known_terms']),
                  -sum(v*bases[0][mask] for mask,v in row['known_terms']),-sum(v*bases[1][mask] for mask,v in row['known_terms'])]) for row in rows]
        model=read(MODEL);verify(model,variables,rows,equations,origin,bases)
        need(len(variables)==2766 and len(rows)==11749 and sum(len(r['terms']) for r in equations)==86129,'all exact raw model dimensions')
        # Independently labelled Petersen=KG(5,2): disjoint two-subsets are adjacent.
        vertices=list(combinations(range(5),2));petersen=[[int(set(a).isdisjoint(b)) for b in vertices] for a in vertices]
        need(all(sum(row)==3 and row[i]==0 for i,row in enumerate(petersen)),'known Petersen degree/diagonal')
        need(all(sum(petersen[u][w]*petersen[v][w] for w in range(10))==(0 if petersen[u][v] else 1) for u,v in combinations(range(10),2)),'known exact Petersen SRG identity')
        for selected in combinations(range(10),6):
            lower=geometry.matrix(6,geometry.bits(petersen,selected))
            if all(sum(r)==3 for r in lower):
                need(not any(all(lower[u][v] for u,v in combinations(first,2)) and all(lower[u][v] for u,v in combinations([x for x in range(6) if x not in first],2)) for first in combinations(range(6),3)), 'known fixture prism-free')
        actual6={};actual7={}
        for u in range(10):
            for v in range(10):
                if u!=v:
                    actual6[u,v]=count(petersen,(u,v),6,map6)
                    if not petersen[u][v]:actual7[u,v]=count(petersen,(u,v),7,map7)
        edge_fixture=next(values for (u,v),values in actual6.items() if petersen[u][v]);nonedge_fixture=next(values for (u,v),values in actual6.items() if not petersen[u][v])
        need(all(values==(edge_fixture if petersen[u][v] else nonedge_fixture) for (u,v),values in actual6.items()),'all90 actual root6 profiles directly counted')
        fixture_edge={mask:edge_fixture[mask] for mask in edge_six};fixture_nonedge={mask:nonedge_fixture[mask] for mask in six}
        # Reuse independently reconstructed sparse coefficient left sides, but
        # recalculate each parameter-derived RHS/known coefficient for this fixture.
        fixture_ordinary=copy.deepcopy(ordinary_rows)
        fixture_ordinary[0]['rhs']=math.comb(8,5)
        for row in fixture_ordinary[1:]:
            adj=geometry.matrix(6,row['parent6mask']);mark=row['orbit']
            if row['kind']=='delete':left=10-6
            elif row['kind']=='degree':left=sum(3-sum(adj[u]) for u, in mark)
            else:left=sum((0 if adj[u][v] else 1)-sum(adj[u][w]*adj[v][w] for w in range(6)) for u,v in mark)
            row['known_terms']=[[row['parent6mask'],-left]] if left else []
        fixture_reroot=copy.deepcopy(rerooted);fixture_cards={0:3,1:2,2:2,3:1}
        for row in fixture_reroot:
            row['terms']=[[col,val] for col,val in row['terms'] if col<len(seven)]
            row['rhs']=fixture_cards[row['partition']]*(fixture_edge if row['relation']=='edge' else fixture_nonedge)[row['new_root6mask']]
        for root,known in tqdm(actual6.items(),desc='every actual Petersen nonedge row control',mininterval=5):
            if root not in actual7:continue
            vector=[actual7[root][mask] for mask in seven]
            need(holds(fixture_ordinary,vector,known),'all ordinary fixture relations')
            need(holds(fixture_reroot,vector,known),'all collision/union fixture relations');tick()
        vector=[next(iter(actual7.values()))[mask] for mask in seven];bad=vector[:];bad[0]+=1
        need(not holds(fixture_ordinary,bad,nonedge_fixture),'corrupted actual count rejected')
        rejected=[]
        for label,change in [('coefficient',lambda m:m['equations'][0]['terms'][0].__setitem__(1,2)),
                             ('affine_rhs',lambda m:m['equations'][0]['rhs_affine'].__setitem__(0,m['equations'][0]['rhs_affine'][0]+1)),
                             ('aggregate_bound',lambda m:m['row_derivation_descriptors'][-1].update(rhs=m['row_derivation_descriptors'][-1]['rhs']+1)),
                             ('missing_row',lambda m:m['equations'].pop())]:
            damaged=copy.deepcopy(model);change(damaged)
            try:verify(damaged,variables,rows,equations,origin,bases)
            except ValueError:rejected.append(label)
            else:raise ValueError('corrupted model accepted')
        detail=dict(variables=variables,equations=equations,row_derivation_descriptors=rows,every_lower_isomorphism_coefficient_checks=transports,
                    exact_reroot_choices=reroot_choices,row_kind_counts=dict(Counter(row['kind'] for row in rows)),petersen_root6_direct_profiles=90,petersen_primary_nonedge_roots=60,
                    controls={'corrupted_count_rejected':True,'changed_model_rejections':rejected})
        save(out/'reconstructed_model.json',detail)
        summary=dict(status='INDEPENDENT_ROOTED7_MARKED_REROOT_NECESSARY_MODEL_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',producer='/root/structural',
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
            outputs_sha256={'reconstructed_model.json':hashlib.sha256((out/'reconstructed_model.json').read_bytes()).hexdigest()},variables=2766,rows=11749,nonzeros=86129,
            every_lower_isomorphism_checks=transports,reroot_union_collision_choices=reroot_choices,petersen_actual_ordered_pair_profiles=90,petersen_actual_primary_nonedge_controls=60,
            statement='Every saved integer coefficient, collision/union term, aggregate bound and affine right side of the frozen2766-variable11749-row rooted7 model is independently derived as a necessary count relation for a hypothetical prism-free srg(99,14,1,2), without a target automorphism premise.',
            prismfree_premise_established=False,dependencies=[{'id':cid,'revision':1,'relation':'uses_result'} for cid in ['C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE','C-PRISMFREE-ORDERED-EDGE-ROOTED6-RIGIDITY','C-PRISMFREE-ORDERED-NONEDGE-ROOTED6-INTEGER-DOMAIN']],
            controls=detail['controls'],target_resolution=False,new_exclusions=0,graph_realizability_asserted=False,scope='Exact conditional necessary model encoding only; feasibility and realizability are not equivalent.',
            shared_components=['Earlier independent matrix/bit/orbit/DSU helper; no producer imports.','Python exact integers/Fraction, SHA-256, uv environment, contained deadline/supervisor.'],
            limitations=['Prism absence remains UNKNOWN.','Prior independently checked rooted6 values/catalogue are used as pinned results; no new rank proof repeated here.','No LP certificate, modular screen, integer feasibility, graph construction or target exclusion is checked here.'],elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
        save(out/'summary.json',summary);print(json.dumps({k:summary[k] for k in ['status','variables','rows','every_lower_isomorphism_checks','elapsed_seconds']}))
    except Exception as error:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),error=repr(error),inputs_sha256=pins,elapsed_seconds=time.monotonic()-start,target_resolution=False));raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);run(ap.parse_args())
