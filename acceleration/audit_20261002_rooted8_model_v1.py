"""Independent complete marked/union-partition rooted8 necessary model audit."""
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
BASE='acceleration/results/20261002_rooted8_universal5_product_model02/'
OLD='acceleration/results/20261002_rooted7_extension_model/'
REVIEW='acceleration/results/20261002_independent_review/'
FORCED='acceleration/results/20261002_rooted5_flag_rigidity/ordered_nonedge_forced5flags.json'
FROZEN={
 BASE+'catalogue.json':'8dbec8214e651980a7a4939526c0b92a6e0a26387cb900228bb72cf0cf6d356c',
 BASE+'model.json':'a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b',
 BASE+'extension_rows.json':'012b02939a96f1ccf24778118c9957760652f42a2a3dd52dce65e43c421ab44d',
 BASE+'product_rows.json':'ca205a283ef8ea39db79807444b06544e76fa4cf7b1032ba07d27e95bb3fcb9a',
 OLD+'model.json':'21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595',
 OLD+'catalogue.json':'a01649d78eccfcb93c85ff2a86c84463458c120fd22cebaf34b8e573363084d5',
 FORCED:'90697d6bbef39e0636bcb4d60109e4a3c6f0458b478428df5b189607b19e1331',
 REVIEW+'rooted5_rigidity02/summary.json':'4edccc52f486e6517e1cd00003491c02d2404af09328a1449e5552c4a232f01f',
 REVIEW+'rooted6_nonedge_domain01/summary.json':'65081849ccf721eae5bdf569b16f44c88255e0421f5fab1ec26a7fa7f36e8271',
 REVIEW+'rooted7_model01/summary.json':'df0a614a76d4cc6365468993c9cb7b2ad836484946e00da059977642b37db76f',
 REVIEW+'rooted8_catalogue01/summary.json':'c763a3929b0c857167e7ec618078ed207aedd213a6bf74939cc856f1e5ed4a59',
 'acceleration/audit_20261002_rooted5_rigidity_v2.py':'b281675c501cbf49116b2c1f6cfd6beb55d0bdf00b0bacc34bf8e9b42660f0ed',
}


def need(ok,why):
    if not ok:raise ValueError(why)


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def orbit_map(order,representatives,tick):
    result={}
    for mask in tqdm(representatives,desc='independent lower orbit map'+str(order),mininterval=5):
        for image in geometry.orbit(order,mask):
            need(image not in result or result[image]==mask,'CANONICAL_ORBIT_DISJOINTNESS');result[image]=mask
        tick()
    return result


def extensions(seven,eight,lookup,offset,tick,checkpoint):
    rows=[dict(kind='order8_total',terms=[[offset+j,1] for j in range(len(eight))],rhs_affine=[math.comb(97,6),0,0])]
    descriptors={};positions={}
    for j,mask in enumerate(seven):
        adj=geometry.matrix(7,mask);specs=[('delete',[],99-7)]
        for mark in geometry.mark_orbits(7,mask):
            mark=[list(value) for value in mark]
            if len(mark[0])==1:kind='degree';left=sum(14-sum(adj[u]) for u, in mark)
            else:kind='pair_common';left=sum((1 if adj[u][v] else 2)-sum(adj[u][w]*adj[v][w] for w in range(7)) for u,v in mark)
            specs.append((kind,mark,left))
        descriptors[mask]=specs
        for kind,mark,left in specs:
            positions[mask,kind,tuple(map(tuple,mark))]=len(rows)
            rows.append(dict(kind=kind,parent7mask=mask,orbit=mark,terms=[[j,-left]] if left else [],rhs_affine=[0,0,0]))
        tick()
    coefficients=[Counter(dict(row['terms'])) for row in rows];transports=deletions=0
    for j,mask in enumerate(tqdm(eight,desc='every lower isomorphism in rooted8',mininterval=5)):
        adj=geometry.matrix(8,mask)
        for removed in range(2,8):
            free=[v for v in range(2,8) if v!=removed];raw=geometry.bits(adj,(0,1,*free));parent=lookup[raw]
            mappings=[(0,1,*tail) for tail in permutations(free) if geometry.bits(adj,(0,1,*tail))==parent]
            need(mappings,'LOWER_ISOMORPHISM_EXISTS');deletions+=1
            for kind,mark,_ in descriptors[parent]:
                values=[1 if kind=='delete' else sum(all(adj[removed][mapping[u]] for u in marked) for marked in mark) for mapping in mappings]
                need(len(set(values))==1,'ALL_LOWER_TRANSPORTS_AGREE');transports+=len(values)
                if values[0]:coefficients[positions[parent,kind,tuple(map(tuple,mark))]][offset+j]+=values[0]
        if (j+1)%2000==0:checkpoint('extensions',dict(completed_child_classes=j+1,lower_free_deletions=deletions,every_isomorphism_checks=transports))
        tick()
    for i in range(1,len(rows)):rows[i]['terms']=[[col,value] for col,value in sorted(coefficients[i].items()) if value]
    return rows,transports,deletions


def union_coefficients(h,mask,five_lookup):
    """Select overlap, then private first set; second is its complement.

    This differs from the producer's all-triple-pairs union filter. Each ordered
    pair with complete union has a unique overlap and first private set.
    """
    adj=geometry.matrix(h,mask);free=tuple(range(2,h));counts=Counter();population=0
    for overlap in combinations(free,8-h):
        remaining=tuple(v for v in free if v not in overlap)
        for private_first in combinations(remaining,h-5):
            private_second=tuple(v for v in remaining if v not in private_first)
            first=tuple(sorted((*overlap,*private_first)));second=tuple(sorted((*overlap,*private_second)))
            need(len(first)==len(second)==3 and set(first)|set(second)==set(free),'UNION_PARTITION_COVERS')
            first_type=five_lookup[geometry.bits(adj,(0,1,*first))];second_type=five_lookup[geometry.bits(adj,(0,1,*second))]
            counts[tuple(sorted((first_type,second_type)))]+=1;population+=1
    need(population=={5:1,6:12,7:30,8:20}[h],'EXACT_ORDERED_UNION_POPULATION')
    return counts,population


def products(five,six,seven,eight,offset,lookup,forced,origin,bases,tick,checkpoint):
    pairs=[(a,b) for i,a in enumerate(five) for b in five[i:]];position={pair:j for j,pair in enumerate(pairs)}
    terms=[Counter() for _ in pairs];known=[Counter() for _ in pairs];populations={}
    # Order5 is independently checked rather than silently collapsed to collision.
    for mask in five:need(union_coefficients(5,mask,lookup)==(Counter({(mask,mask):1}),1),'EXACT_ROOT5_COLLISION')
    for h,masks in [(6,six),(7,seven),(8,eight)]:
        populations[h]=0
        for j,mask in enumerate(tqdm(masks,desc='overlap/private-set products order'+str(h),mininterval=5)):
            counts,population=union_coefficients(h,mask,lookup);populations[h]+=population
            for pair,value in counts.items():
                if h==6:known[position[pair]][mask]+=value
                else:terms[position[pair]][j if h==7 else offset+j]+=value
            if (j+1)%2000==0:checkpoint('products'+str(h),dict(completed_classes=j+1,exact_ordered_pairs=populations[h]))
            tick()
    rows=[]
    for pair,coeff,lower in zip(pairs,terms,known):
        a,b=pair;original=forced[a]*forced[b]*(1 if a==b else 2);collision=forced[a] if a==b else 0
        rhs=[original-collision-sum(value*origin[mask] for mask,value in lower.items()),
             -sum(value*bases[0][mask] for mask,value in lower.items()),-sum(value*bases[1][mask] for mask,value in lower.items())]
        rows.append(dict(kind='universal5_ordered_product_upper',rooted5_masks=list(pair),original_product_rhs=original,
             known_root5_collision=collision,known_root6_coefficients=[[mask,value] for mask,value in sorted(lower.items())],
             terms=[[col,value] for col,value in sorted(coeff.items()) if value],rhs_affine=rhs))
    return rows,populations


def verify(raw,old,eight,extensions_,products_,raw_extension,raw_products):
    need(raw['format']=='ROOTED8_CONDITIONAL_EXTENSION_UNIVERSAL5_PRODUCT_MODEL_V1','MODEL_FORMAT')
    need(raw['variables']==old['variables']+[[8,mask] for mask in eight],'MODEL_VARIABLES')
    need(raw_extension==extensions_,'EXTENSION_COEFFICIENTS')
    stripped=[{key:value for key,value in row.items() if key!='convention'} for row in raw_products]
    need(stripped==products_,'PRODUCT_COEFFICIENTS_OR_RHS')
    expected=old['equations']+[dict(terms=row['terms'],rhs_affine=row['rhs_affine']) for row in extensions_+products_]
    need(raw['equations']==expected,'MODEL_COMPLETE_OPERATOR')
    need(raw['inherited_root7_model_sha256']==FROZEN[OLD+'model.json'],'INHERITED_OPERATOR_PIN')
    need(raw['parameter_domain']==[[0,20],[0,9]] and raw['profile_population']==210,'MODEL_PARAMETER_UNIVERSE')
    need(len(raw['variables'])==23019 and len(raw['equations'])==85874 and sum(len(r['terms']) for r in raw['equations'])==968172,'MODEL_DIMENSIONS')


def exact_rejection(function,message):
    try:function()
    except ValueError as error:need(str(error)==message,'UNEXPECTED_CONTROL_DIAGNOSTIC:'+str(error))
    else:raise ValueError('CORRUPTED_CONTROL_ACCEPTED:'+message)


def fixture_extensions(rows,seven):
    result=copy.deepcopy(rows);result[0]['rhs_affine']=[math.comb(8,6),0,0]
    position={mask:j for j,mask in enumerate(seven)}
    for row in result[1:]:
        adj=geometry.matrix(7,row['parent7mask']);mark=row['orbit']
        if row['kind']=='delete':left=10-7
        elif row['kind']=='degree':left=sum(3-sum(adj[u]) for u, in mark)
        else:left=sum((0 if adj[u][v] else 1)-sum(adj[u][w]*adj[v][w] for w in range(7)) for u,v in mark)
        parent=position[row['parent7mask']]
        row['terms']=[[col,value] for col,value in row['terms'] if col!=parent]
        if left:row['terms'].insert(0,[parent,-left])
    return result


def fixture_checks(extensions_,products_,five_lookup,six_lookup,seven_lookup,seven,eight,offset,tick):
    vertices=list(combinations(range(5),2));adj=[[int(set(u).isdisjoint(v)) for v in vertices] for u in vertices]
    need(all(sum(row)==3 and row[i]==0 for i,row in enumerate(adj)),'PETERSEN_DEGREE')
    need(all(sum(adj[u][w]*adj[v][w] for w in range(10))==(0 if adj[u][v] else 1) for u,v in combinations(range(10),2)),'PETERSEN_EXACT_SRG')
    fixture_rows=fixture_extensions(extensions_,seven);eight_set=set(eight);eight_cache={};root_records=[];reference=None
    def count(root,h,lookup):
        counts=Counter()
        for selected in combinations([v for v in range(10) if v not in root],h-2):
            raw=geometry.bits(adj,(*root,*selected))
            if h==8:
                if raw not in eight_cache:eight_cache[raw]=min(geometry.orbit(8,raw))
                canon=eight_cache[raw];need(canon in eight_set,'PETERSEN_ROOT8_CATALOGUE')
            else:need(raw in lookup,'PETERSEN_LOWER_CATALOGUE');canon=lookup[raw]
            counts[canon]+=1
        return counts
    def hold_extensions(vector):
        need(all(sum(value*vector[col] for col,value in row['terms'])==row['rhs_affine'][0] for row in fixture_rows),'PETERSEN_EXTENSION_IDENTITY')
    def hold_products(vector,f5,f6,rows=products_):
        for row in rows:
            a,b=row['rooted5_masks'];lhs=sum(value*vector[col] for col,value in row['terms'])+sum(value*f6[mask] for mask,value in row['known_root6_coefficients'])+(f5[a] if a==b else 0)
            need(lhs==f5[a]*f5[b]*(1 if a==b else 2),'PETERSEN_PRODUCT_IDENTITY')
    for u in range(10):
        for v in range(10):
            if u==v or adj[u][v]:continue
            f5=count((u,v),5,five_lookup);f6=count((u,v),6,six_lookup);f7=count((u,v),7,seven_lookup);f8=count((u,v),8,None)
            vector=Counter({j:f7[mask] for j,mask in enumerate(seven) if f7[mask]});vector.update({offset+j:f8[mask] for j,mask in enumerate(eight) if f8[mask]})
            hold_extensions(vector);hold_products(vector,f5,f6)
            root_records.append(dict(root=[u,v],root5=[[k,value] for k,value in sorted(f5.items())],root6=[[k,value] for k,value in sorted(f6.items())],root7=[[k,value] for k,value in sorted(f7.items())],root8=[[k,value] for k,value in sorted(f8.items())]))
            if reference is None:reference=(vector,f5,f6)
            tick()
    need(len(root_records)==60,'ALL_ACTUAL_PETERSEN_ROOTS')
    vector,f5,f6=reference;damaged=Counter(vector);damaged[offset]+=1
    exact_rejection(lambda:hold_extensions(damaged),'PETERSEN_EXTENSION_IDENTITY')
    row_index,col=next((i,col) for i,row in enumerate(products_) for col,value in row['terms'] if vector[col])
    row=copy.deepcopy(products_[row_index]);row['terms']= [[j,value+(j==col)] for j,value in row['terms']]
    exact_rejection(lambda:hold_products(vector,f5,f6,[row]),'PETERSEN_PRODUCT_IDENTITY')
    return dict(actual_nonedge_roots=60,extension_rows_per_root=len(fixture_rows),product_rows_per_root=len(products_),actual_profiles=root_records,
         corrupted_root8_count_rejected=True,corrupted_nonzero_product_coefficient_rejected=True,
         method='KG(5,2) direct unordered-subset counts at each actual ordered nonedge; every sparse row calculated, no fixture automorphism assumption.')


def run(args):
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Full70297marked/3828product rows, every lowerisomorphism and independent unionpartitions, all60Petersen roots;60seconds orderly reserve.')
    out=args.out.resolve();out.mkdir(exist_ok=False);pins={};stage='pins'
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>60,'not completed within the allocated budget')
    def read(name):return json.loads((ROOT/name).read_bytes())
    def pin(name,digest=None):
        tick()
        with (ROOT/name).open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
        need(digest is None or actual==digest,'INPUT_HASH:'+name);pins[name]=actual
    def checkpoint(part,value):save(out/(part+'_'+str(value.get('completed_child_classes',value.get('completed_classes')))+'.json'),dict(timestamp=datetime.now(timezone.utc).isoformat(),stage=part,progress=value,deadline=deadline.status(),target_resolution=False))
    try:
        for name,digest in FROZEN.items():pin(name,digest)
        for name in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),
                     'acceleration/command_deadline.py','acceleration/run_compute_command.py','pyproject.toml','uv.lock']:pin(name)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,
            allocation_seconds=args.seconds,reserve_seconds=60,estimated_memory='Under2GiB Python decoded operator/coefficients; root8 full orbit table deliberately not retained.',
            selection='Complete frozen operator; all70297extension and3828product rows, all20253root8classes and every parent transport.',
            success='Exact equality of every raw row, variable and affine RHS; all inherited rows pinned; all60 known fixture roots pass, specified corrupted inputs fail at exact diagnostics.',
            independent_requirement='Independent derivation and full artifact checking; producer imports prohibited; no solver/certificate promotion.'))
        old=read(OLD+'model.json');catalog=read(BASE+'catalogue.json');seven=read(OLD+'catalogue.json')['prismfree_masks'];eight=catalog['prismfree_masks'];offset=len(old['variables'])
        need(offset==2766 and len(seven)==2750 and len(eight)==20253,'BOUND_CLASS_COUNTS')
        forced={mask:Fraction(*value) for mask,value in read(FORCED)['flag_counts']};need(len(forced)==87 and all(v.denominator==1 for v in forced.values()),'BOUND_ROOT5_INTEGER_VECTOR');forced={mask:int(v) for mask,v in forced.items()}
        five=sorted(forced);origin={int(mask):value for mask,value in old['root6_profile_basis']['origin'].items()};bases=[{int(mask):value for mask,value in vector.items()} for vector in old['root6_profile_basis']['basis']];six=sorted(origin)
        need(len(six)==456,'BOUND_ROOT6_UNIVERSE')
        stage='lower_orbit_maps';map5=orbit_map(5,five,tick);map6=orbit_map(6,six,tick);map7=orbit_map(7,seven,tick)
        # Cheap positive exact union controls precede the substantial derivation.
        for h,population in [(5,1),(6,12),(7,30),(8,20)]:need(union_coefficients(h,0,map5)==(Counter({(0,0):population}),population),'EMPTY_GRAPH_UNION_CONTROL')
        stage='every_marked_transport';extensions_,transports,deletions=extensions(seven,eight,map7,offset,tick,checkpoint)
        stage='union_partition_products';products_,populations=products(five,six,seven,eight,offset,map5,forced,origin,bases,tick,checkpoint)
        need(len(extensions_)==70297 and len(products_)==3828,'FULL_NEW_ROW_POPULATION')
        raw=read(BASE+'model.json');raw_extension=read(BASE+'extension_rows.json');raw_products=read(BASE+'product_rows.json')
        stage='complete_raw_comparison';verify(raw,old,eight,extensions_,products_,raw_extension,raw_products)
        # Bind old code's independently checked exact row scope rather than
        # treating the discovery code or a floating-point guide as its checker.
        old_review=read(REVIEW+'rooted7_model01/summary.json');need(old_review['status']=='INDEPENDENT_ROOTED7_MARKED_REROOT_NECESSARY_MODEL_PASS','INDEPENDENT_INHERITED_OPERATOR_SCOPE')
        rejected=[]
        def bad_model(label,mutator,message):
            damaged=copy.deepcopy(raw);mutator(damaged);exact_rejection(lambda:verify(damaged,old,eight,extensions_,products_,raw_extension,raw_products),message);rejected.append(label)
        # Cheap copied new-row lists avoid replicating the entire operator where
        # the intended failure is descriptive rather than flattened equations.
        for label,mutate in [('coefficient',lambda rows:rows[0]['terms'][0].__setitem__(1,2)),('affine_rhs',lambda rows:rows[0]['rhs_affine'].__setitem__(0,rows[0]['rhs_affine'][0]+1)),('omitted_row',lambda rows:rows.pop())]:
            damaged=copy.deepcopy(raw_extension);mutate(damaged)
            exact_rejection(lambda:verify(raw,old,eight,extensions_,products_,damaged,raw_products),'EXTENSION_COEFFICIENTS');rejected.append('extension_'+label)
        for label,mutate in [('coefficient',lambda rows:rows[0]['terms'][0].__setitem__(1,rows[0]['terms'][0][1]+1)),('affine_rhs',lambda rows:rows[0]['rhs_affine'].__setitem__(0,rows[0]['rhs_affine'][0]+1)),('offdiagonal_factor',lambda rows:next(row for row in rows if row['rooted5_masks'][0]!=row['rooted5_masks'][1] and row['original_product_rhs']>0).__setitem__('original_product_rhs',1)),('omitted_row',lambda rows:rows.pop())]:
            damaged=copy.deepcopy(raw_products);mutate(damaged)
            exact_rejection(lambda:verify(raw,old,eight,extensions_,products_,raw_extension,damaged),'PRODUCT_COEFFICIENTS_OR_RHS');rejected.append('product_'+label)
        bad_model('inherited_equation',lambda obj:obj['equations'][0]['rhs_affine'].__setitem__(0,obj['equations'][0]['rhs_affine'][0]+1),'MODEL_COMPLETE_OPERATOR')
        bad_model('variable',lambda obj:obj['variables'][-1].__setitem__(1,obj['variables'][-1][1]+2),'MODEL_VARIABLES')
        stage='all_actual_fixture_roots';controls=fixture_checks(extensions_,products_,map5,map6,map7,seven,eight,offset,tick);controls['raw_model_rejections']=rejected
        # Mathematical output intentionally contains no discovery explanatory
        # prose, only the independently reconstructed integer rows/variables.
        detail=dict(variables=raw['variables'],inherited_root7_sha256=FROZEN[OLD+'model.json'],extensions=extensions_,products=products_,every_lower_isomorphism_checks=transports,
            free_deletions_checked=deletions,ordered_union_pair_populations={str(h):value for h,value in populations.items()},controls=controls)
        save(out/'reconstructed_rows.json',detail)
        summary=dict(status='INDEPENDENT_ROOTED8_MARKED_UNIVERSAL5_PRODUCT_MODEL_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',producer='/root/structural',
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
            outputs_sha256={'reconstructed_rows.json':hashlib.sha256((out/'reconstructed_rows.json').read_bytes()).hexdigest()},variables=23019,rows=85874,nonzeros=968172,
            inherited_rows=len(old['equations']),marked_extension_rows=70297,upper_pair_product_rows=3828,free_deletions_checked=deletions,every_lower_isomorphism_checks=transports,
            ordered_union_pair_populations={str(h):value for h,value in populations.items()},actual_petersen_nonedge_roots=60,fixture_extension_row_calculations=60*70297,fixture_product_row_calculations=60*3828,
            statement='Every saved integer coefficient and affine right side of the frozen23019-variable85874-row rooted8 operator is independently established as a necessary local count equation at each actual ordered nonedge of a hypothetical prism-free srg(99,14,1,2), preserving free rooted7 counts and all210 conditional rooted6 parameter profiles, without a target automorphism premise.',
            scope='Complete conditional necessary count encoding only; no graph realizability, profile exclusion, optimizer outcome or target resolution.',
            dependencies=[dict(id=cid,revision=1,relation=relation) for cid,relation in [
              ('C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY','uses_result'),('C-PRISMFREE-ORDERED-NONEDGE-ROOTED6-INTEGER-DOMAIN','uses_result'),
              ('C-PRISMFREE-ROOTED7-MARKED-REROOT-NECESSARY-ENCODING','uses_result'),('C-PRISMFREE-ROOTED8-NONEDGE-LOCAL-CATALOGUE-COVERAGE','coverage')]],
            controls={key:value for key,value in controls.items() if key!='actual_profiles'},prismfree_premise_established=False,target_resolution=False,new_exclusions=0,graph_realizability_asserted=False,
            shared_components=['Earlier independently calibrated exact bit/matrix/free-label orbit and finite mark-DSU geometry helper, pinned; no producer imports.','Python exact integers/Fraction, SHA-256, uv locked environment, supported deadline and contained supervisor.'],
            limitations=['Global prism absence remains UNKNOWN.','Previously independently checked rooted5/rooted6 and rooted7 necessity results are pinned, not re-proved here.','No numerical LP or modular guide, primal/Farkas/UNSAT certificate or actual99-graph is checked.','Positive Petersen controls use their actual parameters and counts; they test finite semantics, not target existence.'],elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
        save(out/'summary.json',summary);print(json.dumps({key:summary[key] for key in ['status','variables','rows','every_lower_isomorphism_checks','elapsed_seconds']}))
    except Exception as error:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),stage=stage,error=repr(error),inputs_sha256=pins,elapsed_seconds=time.monotonic()-start,target_resolution=False));raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);run(ap.parse_args())
