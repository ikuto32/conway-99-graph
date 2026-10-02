"""Produce an unrestricted rooted8 necessary model; no optimization or selfapproval."""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline
import theory_20261002_rooted7_extension_model as G

ROOT=G.ROOT
B=ROOT/'acceleration/results'
MODEL=B/'20261002_rooted7_unrestricted_extension01/model.json'
AUDIT=B/'20261002_independent_review/rooted7_unrestricted_model01/summary.json'
CATALOGUE=B/'20261002_rooted7_extension_model/catalogue.json'
CATALOGUE_AUDIT=B/'20261002_independent_review/rooted7_catalogue01/summary.json'
FORCED=B/'20261002_rooted5_flag_rigidity/ordered_nonedge_forced5flags.json'
FORCED_AUDIT=B/'20261002_independent_review/rooted5_rigidity02/summary.json'
SPEC=ROOT/'docs/PROTOCOL_20261003_UNRESTRICTED_ROOTED8_V1.md'
DESIGN=ROOT/'docs/DESIGN_20261003_UNRESTRICTED_ROOTED8_V1.md'
EXPECTED={MODEL:'9f636889690071f69ad7a103b02abb2f43a5bbc2d2114c87a779da29c0f647a1',AUDIT:'e7631851f9cc5716c9d8a1bf5b30f9a4644d8e2170f116d1bb30378fbeb16d70',CATALOGUE:'a01649d78eccfcb93c85ff2a86c84463458c120fd22cebaf34b8e573363084d5',CATALOGUE_AUDIT:'3355afb38656eadc83eff6e0db3818eded9621f890c9d46f489fdb0324370758',FORCED:'90697d6bbef39e0636bcb4d60109e4a3c6f0458b478428df5b189607b19e1331',FORCED_AUDIT:'4edccc52f486e6517e1cd00003491c02d2404af09328a1449e5552c4a232f01f',Path(G.__file__):'ac0e8882f5fa72ba3872c8d47fa8e8b1dbcb1c47b9a8016e17f3dacc954e133e'}


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')


def read(path):return json.loads(Path(path).read_bytes())


def pins():
    for path,expected in EXPECTED.items():need(sha(path)==expected,'Frozen prerequisite '+str(path))
    paths=[*EXPECTED,Path(__file__),SPEC,DESIGN,ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py']
    return {path.relative_to(ROOT).as_posix():sha(path)for path in paths}


def marks(n,mask):
    adj=G.graph(n,mask)
    automorphisms=[order for order,_ in G.transformations(n)if G.encode(adj,order)==mask]
    pending={(u,)for u in range(n)}|set(combinations(range(n),2));result=[]
    while pending:
        first=min(pending,key=lambda value:(len(value),value))
        orbit={tuple(sorted(order[u]for u in first))for order in automorphisms}
        need(orbit<=pending,'Complete finite mark orbit partition')
        pending-=orbit;result.append(('degree'if len(first)==1 else'pair_common',sorted(orbit)))
    return result


def parent_factor(adj,kind,orbit,n,k,lam,mu):
    if kind=='delete':return n-7
    if kind=='degree':return sum(k-adj[u].bit_count()for u, in orbit)
    return sum((lam if adj[u]>>v&1 else mu)-(adj[u]&adj[v]).bit_count()for u,v in orbit)


def extension_rows(seven,eight,offset,n,k,lam,mu,deadline):
    parents={mask:j for j,mask in enumerate(seven)};specifications={};positions={}
    rows=[dict(kind='order8_total',terms=[[offset+j,1]for j in range(len(eight))],rhs_affine=[math.comb(n-2,6),0,0,0])]
    for mask in seven:
        adj=G.graph(7,mask);specs=[('delete',[],n-7)]
        specs += [(kind,orbit,parent_factor(adj,kind,orbit,n,k,lam,mu))for kind,orbit in marks(7,mask)]
        specifications[mask]=specs
        for kind,orbit,left in specs:
            positions[mask,kind,tuple(map(tuple,orbit))]=len(rows)
            rows.append(dict(kind=kind,parent7mask=mask,orbit=orbit,parent_factor=left,terms=[[parents[mask],-left]]if left else[],rhs_affine=[0,0,0,0]))
    coefficients=[Counter(dict(row['terms']))for row in rows]
    for j,mask in enumerate(tqdm(eight,desc='Unrestricted rooted7-to8 coefficients',mininterval=5)):
        adj=G.graph(8,mask)
        for deleted in range(2,8):
            remaining=[u for u in range(8)if u!=deleted]
            parent,order=G.canonical(7,G.encode(adj,remaining));mapping=[remaining[u]for u in order]
            need(parent in specifications,'Every free deletion has a complete unrestricted parent')
            for kind,orbit,_ in specifications[parent]:
                if kind=='delete':value=1
                elif kind=='degree':value=sum(adj[deleted]>>mapping[u]&1 for u, in orbit)
                else:value=sum((adj[deleted]>>mapping[u]&1)and(adj[deleted]>>mapping[v]&1)for u,v in orbit)
                if value:coefficients[positions[parent,kind,tuple(map(tuple,orbit))]][offset+j]+=value
        if not j%128:need(not deadline.status()['stop_required'],'not completed within the allocated budget')
    for i in range(1,len(rows)):rows[i]['terms']=[[j,value]for j,value in sorted(coefficients[i].items())if value]
    return rows


def product_coefficients(h,mask):
    adj=G.graph(h,mask);free=list(range(2,h));triples=list(combinations(free,3));full=sum(1<<u for u in free)
    labels=[G.canonical(5,G.encode(adj,[0,1,*triple]))[0]for triple in triples]
    bits=[sum(1<<u for u in triple)for triple in triples];values=Counter()
    for i,first in enumerate(bits):
        for j,second in enumerate(bits):
            if first|second==full:values[tuple(sorted([labels[i],labels[j]]))]+=1
    need(sum(values.values())=={5:1,6:12,7:30,8:20}[h],'Complete ordered triple-union total')
    return values


def product_rows(seven,eight,offset,origin,basis,forced,deadline):
    pairs=sorted([*combinations(sorted(forced),2),*[(f,f)for f in sorted(forced)]])
    positions={pair:i for i,pair in enumerate(pairs)};terms=[Counter()for _ in pairs];known=[Counter()for _ in pairs]
    for h,masks in [(6,sorted(origin)),(7,seven),(8,eight)]:
        for j,mask in enumerate(tqdm(masks,desc=f'Unrestricted five-product union{h}',mininterval=5)):
            for pair,value in product_coefficients(h,mask).items():
                need(pair in positions,'Complete forced rooted-five support')
                if h==6:known[positions[pair]][mask]+=value
                else:terms[positions[pair]][j if h==7 else offset+j]+=value
            if not j%128:need(not deadline.status()['stop_required'],'not completed within the allocated budget')
    rows=[]
    for pair,counts,lower in zip(pairs,terms,known):
        first,second=pair;product=forced[first]*forced[second]*(1 if first==second else 2);collision=forced[first]if first==second else 0
        rhs=[product-collision-sum(value*origin[mask]for mask,value in lower.items())]
        rhs += [-sum(value*coordinate[mask]for mask,value in lower.items())for coordinate in basis]
        need(len(rhs)==4,'Exactly constant,c,a,b RHS components')
        rows.append(dict(kind='unrestricted_universal5_ordered_product_upper',rooted5_masks=list(pair),original_product_rhs=product,known_root5_collision=collision,known_root6_coefficients=[[mask,value]for mask,value in sorted(lower.items())],terms=[[j,value]for j,value in sorted(counts.items())if value],rhs_affine=rhs))
    return rows


def catalogue(seven,deadline,out,source_pins,resume):
    seen={};completed=attempts=local=0
    if resume:
        checkpoint=read(resume)
        need(checkpoint['format']=='UNRESTRICTED_ROOTED8_CATALOGUE_CHECKPOINT_V1'and checkpoint['inputs_sha256']==source_pins,'Exact new unrestricted checkpoint source/input closure')
        completed=checkpoint['completed_parent_classes'];attempts=checkpoint['labelled_attempts'];local=checkpoint['locally_admissible_extensions']
        seen={mask:(parent,neighborhood)for mask,parent,neighborhood in checkpoint['representatives']}
        need(0<=completed<=len(seven)and attempts==128*completed,'Complete fixed augmentation prefix')
    def checkpoint(name):
        save(out/name,dict(format='UNRESTRICTED_ROOTED8_CATALOGUE_CHECKPOINT_V1',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=source_pins,completed_parent_classes=completed,labelled_attempts=attempts,locally_admissible_extensions=local,representatives=[[mask,*seen[mask]]for mask in sorted(seen)],prism_filter_applied=False,restart='Exact frozen source/input closure and --resume this file, fresh --out and separately declared contained invocation; no automatic retry.'))
    for index in tqdm(range(completed,len(seven)),desc='All2770x128 unrestricted augmentations',mininterval=5):
        parent=seven[index];old=G.graph(7,parent)
        for neighborhood in range(128):
            attempts+=1;adj=[*old,neighborhood]
            for u in range(7):
                if neighborhood>>u&1:adj[u]|=1<<7
            if not G.admissible(adj):continue
            local+=1;mask=G.canonical(8,G.encode(adj,range(8)))[0]
            if mask not in seen:seen[mask]=(parent,neighborhood)
        completed=index+1
        if completed%100==0 or completed==len(seven):checkpoint(f'catalogue_checkpoint_{completed:04d}.json')
        if deadline.status()['stop_required']:
            checkpoint(f'catalogue_checkpoint_stop_{completed:04d}.json')
            raise ValueError('not completed within the allocated budget')
    need(attempts==354560 and completed==2770,'All354560 complete neighbourhood attempts')
    return dict(format='COMPLETE_UNRESTRICTED_ROOTED8_AUGMENTATION_V1',complete_locally_admissible_masks=sorted(seen),base_complete_root7_masks=seven,completed_parent_classes=completed,labelled_attempts=attempts,locally_admissible_extensions=local,prism_filter_applied=False,first_generating_extensions=[[mask,*seen[mask]]for mask in sorted(seen)],coverage='Every admissible rooted8 flag has a free deletion into the independently complete2770root7 universe; all128 new-vertex neighbourhoods tested, exact local caps only, free-label canonicalization.')


def fixture_counts(adj,roots,h):
    free=[u for u in range(len(adj))if u not in roots]
    return Counter(G.canonical(h,G.encode(adj,[*roots,*subset]))[0]for subset in combinations(free,h-2))


def fixture_graphs():
    rook=[sum(1<<v for v in range(9)if v!=u and(u//3==v//3 or u%3==v%3))for u in range(9)]
    petersen=[0]*10
    for u in range(5):
        for v in [(u+1)%5,u+5]:petersen[u]|=1<<v;petersen[v]|=1<<u
        v=(u+2)%5+5;petersen[u+5]|=1<<v;petersen[v]|=1<<(u+5)
    return [('rook9',rook,4,1,2,36),('petersen10',petersen,3,0,1,60)]


def controls(deadline,out,model):
    records=[];controls=[];prism_flags=set()
    for h in range(5,9):need(product_coefficients(h,0)=={(0,0):{5:1,6:12,7:30,8:20}[h]},'Empty ordered triple-union control')
    for name,adj,k,lam,mu,expected_roots in fixture_graphs():
        n=len(adj);need(all(row.bit_count()==k for row in adj)and all((adj[u]&adj[v]).bit_count()==(lam if adj[u]>>v&1 else mu)for u,v in combinations(range(n),2)),'Known-valid exact fixture '+name)
        roots=[(u,v)for u in range(n)for v in range(n)if u!=v and not adj[u]>>v&1];need(len(roots)==expected_roots,'Complete fixture ordered-root population')
        for root in roots:
            counts={h:fixture_counts(adj,root,h)for h in range(5,9)};seven=sorted(counts[7]);eight=sorted(counts[8]);offset=len(seven)
            need(all(G.admissible(G.graph(8,mask))for mask in eight),'All actual flags pass exact target local caps')
            extensions=extension_rows(seven,eight,offset,n,k,lam,mu,deadline);vector={**{j:counts[7][mask]for j,mask in enumerate(seven)},**{offset+j:counts[8][mask]for j,mask in enumerate(eight)}}
            need(all(sum(c*vector[j]for j,c in row['terms'])==row['rhs_affine'][0]for row in extensions),'Every observed fixture marked-extension row')
            totals=Counter()
            for h in range(5,9):
                for mask,count in counts[h].items():
                    for pair,coefficient in product_coefficients(h,mask).items():totals[pair]+=count*coefficient
            for first in counts[5]:
                for second in counts[5]:
                    if first<=second:need(totals[first,second]==counts[5][first]*counts[5][second]*(1 if first==second else 2),'Complete actual ordered products including all collisions/overlaps')
            if not records or name!=records[-1]['fixture']:
                bad=dict(vector);bad[offset]+=1;need(sum(c*bad[j]for j,c in extensions[0]['terms'])!=extensions[0]['rhs_affine'][0],'Changed observed count fails total')
                row=next(row for row in extensions[1:]if any(j>=offset and vector[j]for j,c in row['terms']));j=next(j for j,c in row['terms']if j>=offset and vector[j]);changed=[[col,c+(col==j)]for col,c in row['terms']]
                need(sum(c*vector[col]for col,c in changed)!=row['rhs_affine'][0],'Changed genuine positive-support marked coefficient')
                first,second=next(pair for pair in totals if pair[0]!=pair[1]and counts[5][pair[0]]and counts[5][pair[1]])
                need(totals[first,second]!=counts[5][first]*counts[5][second],'Wrong off-diagonal orientation factor')
                diagonal=next((f,f)for f in counts[5]);need(totals[diagonal]-counts[5][diagonal[0]]!=totals[diagonal],'Dropped diagonal collision')
                controls.extend([name+':changed_count',name+':changed_nonzero_marked_coefficient',name+':offdiagonal_factor',name+':diagonal_collision'])
            if name=='rook9':
                for mask in eight:
                    if not G.prismfree(G.graph(8,mask)):prism_flags.add(mask)
                partition=Counter(((adj[root[0]]>>w&1)|((adj[root[1]]>>w&1)<<1))for w in range(n)if w not in root)
                need([partition[p]for p in range(4)]==[1,2,2,2],'Actual rook9 partition1,2,2,2')
            records.append(dict(fixture=name,roots=list(root),counts={str(h):[[mask,count]for mask,count in sorted(counts[h].items())]for h in range(5,9)},marked_rows_checked=len(extensions),ordered_product_rows_checked=len(totals)))
    need(prism_flags,'Positive prism-containing rook flags actually tested')
    origin={int(mask):value for mask,value in model['root6_nonedge_profile_basis']['origin'].items()};basis=[{int(mask):value for mask,value in row.items()}for row in model['root6_nonedge_profile_basis']['basis']]
    need(len(basis)==3 and basis[0][7100]==1,'Actual unrestricted c coordinate retained')
    lower=Counter()
    for mask in origin:
        for pair,coefficient in product_coefficients(6,mask).items():lower[pair]-=coefficient*basis[0][mask]
    need(any(lower.values()),'Some exact product c-RHS component is genuinely nonzero')
    controls.append('Dropped_nonzero_c_RHS_component_changes_exact_lower_formula')
    bad_adj=list(fixture_graphs()[0][1]);bad_adj[0]^=1<<1;need(any((bad_adj[u]>>v&1)!=(bad_adj[v]>>u&1)for u,v in combinations(range(9),2)),'Corrupted fixture asymmetry rejected')
    controls.append('Corrupted_fixture_asymmetry')
    save(out/'fixture_controls.json',records)
    save(out/'controls.json',dict(fixture_ordered_nonedge_roots=dict(rook9=36,petersen10=60),complete_marked_rows_checked=sum(row['marked_rows_checked']for row in records),complete_ordered_product_rows_checked=sum(row['ordered_product_rows_checked']for row in records),positive_prism_containing_order8_masks=sorted(prism_flags),empty_union_totals=dict(order5=1,order6=12,order7=30,order8=20),controls=controls,producer_calibration_only=True,independent_review=None))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--controls-only',action='store_true');ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256');ap.add_argument('--resume',type=Path);args=ap.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='New unrestricted rooted8 exact catalogue/model build,300outer260worker40reserve; controls-only separately short contained allocation')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);stage='pins'
    try:
        source_pins=pins();old=read(MODEL);seven=[mask for h,mask in old['variables']if h==7]
        need(len(old['variables'])==2810 and len(old['equations'])==11769 and len(seven)==2770 and seven==read(CATALOGUE)['complete_locally_admissible_masks'],'Complete unrestricted inherited prefix/catalogue')
        need(all(len(row['rhs_affine'])==4 for row in old['equations']),'Inherited four RHS components')
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python_version=platform.python_version(),inputs_sha256=source_pins,scope='Unrestricted necessary localcount encoding only; no prismabsence, targetautomorphism or uniform secondaryprofile.',selection='All2770parents*128neighborhoods=354560attempts; complete651primaryprofiles, no favorable omissions.',success='Complete newcatalogue, allmarked/product integerrows with fourRHS and frozen2810prefix; nooptimization.',independent_requirement='Separate complete catalogue/orbit/transport/marked/product/fourRHS reconstruction and calibrated corruption controls before claimpromotion.',resource_allocation='300outer260worker40reserve fullbuild; noautomaticretry; controls-only separate supported allowance.',calibration_path=None if not args.calibration else args.calibration.as_posix(),calibration_sha256=args.calibration_sha256,resume_path=None if not args.resume else args.resume.as_posix(),resume_sha256=None if not args.resume else sha(args.resume)))
        if args.controls_only:
            need(not args.resume and not args.calibration,'Controls-only has no scientific resume or selfapproval')
            stage='precontrols';controls(deadline,out,old)
            need(not deadline.status()['stop_required'],'Controls not completed within the allocated budget')
            save(out/'summary.json',dict(status='UNRESTRICTED_ROOTED8_PRODUCER_PRECONTROLS_PASS',producer_calibration_only=True,inputs_sha256=source_pins,outputs_sha256={p.name:sha(p)for p in out.iterdir()if p.is_file()},timestamp=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-started,scientific_build_launched=False));return
        need(args.calibration and args.calibration_sha256 and sha(args.calibration)==args.calibration_sha256,'Exact pre-output producer calibration required')
        calibration=read(args.calibration);need(calibration['status']=='UNRESTRICTED_ROOTED8_PRODUCER_PRECONTROLS_PASS'and calibration['inputs_sha256']==source_pins,'Changed source/input cannot reuse old calibration')
        for name,expected in calibration['outputs_sha256'].items():need(sha(args.calibration.parent/name)==expected,'Calibration raw artifact '+name)
        stage='catalogue';catalog=catalogue(seven,deadline,out,source_pins,args.resume);save(out/'catalogue.json',catalog);eight=catalog['complete_locally_admissible_masks'];offset=2810
        stage='marked_extension';extensions=extension_rows(seven,eight,offset,99,14,1,2,deadline);save(out/'extension_rows.json',extensions)
        origin={int(mask):value for mask,value in old['root6_nonedge_profile_basis']['origin'].items()};basis=[{int(mask):value for mask,value in row.items()}for row in old['root6_nonedge_profile_basis']['basis']]
        flags=read(FORCED)['flag_counts'];need(len(flags)==87 and all(value[1]==1 for mask,value in flags),'Exact universal87 integer rooted-five values');forced={mask:value[0]for mask,value in flags}
        stage='products';products=product_rows(seven,eight,offset,origin,basis,forced,deadline);need(len(products)==3828,'All3828 upper ordered-product pairs');save(out/'product_rows.json',products)
        stage='fixture_catalogue_check';fixtures=read(args.calibration.parent/'fixture_controls.json');allowed=set(eight)
        need(all(set(mask for mask,count in record['counts']['8'])<=allowed for record in fixtures),'All actual prism-containing fixture classes covered')
        variables=[*old['variables'],*[[8,mask]for mask in eight]];equations=[*old['equations'],*[dict(terms=row['terms'],rhs_affine=row['rhs_affine'])for row in extensions],*[dict(terms=row['terms'],rhs_affine=row['rhs_affine'])for row in products]]
        model=dict(format='ROOTED8_UNRESTRICTED_EXTENSION_UNIVERSAL5_PRODUCT_MODEL_V1',variables=variables,equations=equations,affine_RHS_coordinate_order=['constant','c','a','b'],parameter_domain=old['parameter_domain'],inherited_unrestricted_root7_model_sha256=EXPECTED[MODEL],inherited_prefix=dict(variables=2810,rows=11769),scope='Every unrestricted hypothetical target nonedge root gives a nonnegative integer modelsolution; necessity and catalogue coverage require independent review. No graphrealizability, prismabsence, commonsecondaryprofile or targetautomorphism.',dependency_claims=[dict(id='C-UNRESTRICTED-ROOTED7-MARKED-REROOT-MEAN-NECESSARY-ENCODING',revision=1,relation='uses_result'),dict(id='C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY',revision=1,relation='uses_result'),dict(id='C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE',revision=1,relation='coverage')],product_convention='Ordered triple pairs grouped into F<=G; offdiagonal orientations doubled; allunion orders5..8, alloverlaps included.')
        need(len(variables)==2810+len(eight)and all(len(row['rhs_affine'])==4 for row in equations),'Exact full dimensions/fourRHS')
        need(model['variables'][:2810]==old['variables']and model['equations'][:11769]==old['equations'],'Unchanged full inherited prefix')
        stage='serialization';save(out/'model.json',model)
        save(out/'summary.json',dict(status='CANDIDATE_UNRESTRICTED_ROOTED8_NECESSARY_MODEL',timestamp=datetime.now(timezone.utc).isoformat(),completed_augmentation_attempts=catalog['labelled_attempts'],complete_root8_classes=len(eight),locally_admissible_extensions=catalog['locally_admissible_extensions'],prism_filter_applied=False,variables=len(variables),rows=len(equations),terms=sum(len(row['terms'])for row in equations),new_marked_extension_rows=len(extensions),new_product_rows=len(products),primary_integer_profile_population=651,solver_attempts=0,independent_review=None,target_resolution=False,outputs_sha256={p.name:sha(p)for p in out.iterdir()if p.is_file()},elapsed_seconds=time.monotonic()-started,deadline=deadline.status()))
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),stage=stage,elapsed_seconds=time.monotonic()-started,checkpoints=[p.name for p in sorted(out.glob('catalogue_checkpoint*.json'))],automatic_retry=False,all_completed_outputs_preserved=True,target_resolution=False));raise


if __name__=='__main__':main()
