"""Fresh conditional rooted8 catalogue/extension/universal5-product model.

Build only, no optimizer. Preserve all210 fixed root6 parameter choices while
root7 counts remain free. Finite induced-label permutations never assume a
target automorphism. Producer artifacts require separate semantic/coverage audit.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline
import theory_20261002_rooted7_extension_model as shared

ROOT=shared.ROOT;B=ROOT/'acceleration/results'
OLD=B/'20261002_rooted7_extension_model'
FLAGS=B/'20261002_rooted5_flag_rigidity/ordered_nonedge_forced5flags.json'
PROTOCOL=ROOT/'docs/PROTOCOL_20261002_ROOTED8_UNIVERSAL5_PRODUCTS.md'
OLD_MODEL_SHA='21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595'
OLD_CATALOGUE_SHA='a01649d78eccfcb93c85ff2a86c84463458c120fd22cebaf34b8e573363084d5'


def need(value,reason):
    if not value:raise ValueError(reason)


def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_bytes())


def catalogue(seven,deadline,out,pins,resume):
    seen={};attempts=admissible=accepted=completed=0
    if resume:
        data=read(resume)
        need(data['format']=='ROOTED8_CATALOGUE_CHECKPOINT_V1' and data['inputs_sha256']==pins,'unchanged checkpoint source/input closure')
        completed=data['completed_base_classes'];attempts=data['labelled_attempts']
        admissible=data['locally_admissible_extensions'];accepted=data['prismfree_extensions']
        seen={mask:(parent,neighbors) for mask,parent,neighbors in data['representatives']}
        need(attempts==completed*128 and 0<=completed<=len(seven),'exact completed augmentation prefix')
    for index in tqdm(range(completed,len(seven)),desc='all2750x128 root8 augmentations',mininterval=5):
        parent=seven[index];old=shared.graph(7,parent)
        for neighborhood in range(128):
            attempts+=1;adj=[*old,neighborhood]
            for u in range(7):
                if neighborhood>>u&1:adj[u]|=1<<7
            if not shared.admissible(adj):continue
            admissible+=1
            if not shared.prismfree(adj):continue
            accepted+=1
            mask=shared.canonical(8,shared.encode(adj,range(8)))[0]
            if mask not in seen:seen[mask]=(parent,neighborhood)
        completed=index+1
        if completed%100==0 or completed==len(seven):
            save(out/f'catalogue_checkpoint_{completed:04d}.json',dict(format='ROOTED8_CATALOGUE_CHECKPOINT_V1',
                timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,completed_base_classes=completed,
                labelled_attempts=attempts,locally_admissible_extensions=admissible,prismfree_extensions=accepted,
                representatives=[[mask,*seen[mask]] for mask in sorted(seen)],
                restart='Use this exact source/input closure with --resume this_file and a fresh --out under a newly declared contained invocation; no automatic resume.'))
        need(not deadline.status()['stop_required'],'not completed within the allocated budget')
    return dict(format='COMPLETE_CONDITIONAL_ROOTED8_AUGMENTATION_V1',prismfree_masks=sorted(seen),
        base_prismfree_root7_masks=seven,completed_base_classes=completed,labelled_attempts=attempts,
        locally_admissible_extensions=admissible,prismfree_extensions=accepted,
        first_generating_extensions=[[mask,*seen[mask]] for mask in sorted(seen)],
        coverage='Every globally prismfree rooted8 flag loses a free vertex to the independently covered prismfree rooted7 universe; all128 neighborhoods are enumerated, exact local caps and every6subset tested, only induced free labels canonicalized.')


def marks(n,mask):
    adj=shared.graph(n,mask)
    autom=[order for order,_ in shared.transformations(n) if shared.encode(adj,order)==mask]
    pending={(u,) for u in range(n)}|set(combinations(range(n),2));result=[]
    while pending:
        first=min(pending,key=lambda item:(len(item),item))
        orbit={tuple(sorted(order[u] for u in first)) for order in autom};pending-=orbit
        result.append(('degree' if len(first)==1 else 'pair_common',sorted(orbit)))
    return result


def extension_rows(seven,eight,offset,n,k,lam,mu,deadline):
    index={mask:j for j,mask in enumerate(seven)};descriptors={};positions={}
    rows=[dict(kind='order8_total',terms=[[offset+j,1] for j in range(len(eight))],rhs_affine=[math.comb(n-2,6),0,0])]
    for mask in seven:
        adj=shared.graph(7,mask);specs=[('delete',[],n-7)]
        for kind,orbit in marks(7,mask):
            left=(sum(k-adj[u].bit_count() for u, in orbit) if kind=='degree' else
                  sum((lam if adj[u]>>v&1 else mu)-(adj[u]&adj[v]).bit_count() for u,v in orbit))
            specs.append((kind,orbit,left))
        descriptors[mask]=specs
        for kind,orbit,left in specs:
            positions[mask,kind,tuple(map(tuple,orbit))]=len(rows)
            rows.append(dict(kind=kind,parent7mask=mask,orbit=orbit,terms=[[index[mask],-left]] if left else [],rhs_affine=[0,0,0]))
    coefficients=[Counter(dict(row['terms'])) for row in rows]
    for j,mask in enumerate(tqdm(eight,desc='all rooted7 to8 coefficients',mininterval=5)):
        adj=shared.graph(8,mask)
        for deleted in range(2,8):
            remaining=[u for u in range(8) if u!=deleted]
            parent,order=shared.canonical(7,shared.encode(adj,remaining));mapping=[remaining[u] for u in order]
            need(parent in descriptors,'every free deletion maps to covered prismfree parent')
            for kind,orbit,_ in descriptors[parent]:
                if kind=='delete':value=1
                elif kind=='degree':value=sum(adj[deleted]>>mapping[u]&1 for u, in orbit)
                else:value=sum((adj[deleted]>>mapping[u]&1) and (adj[deleted]>>mapping[v]&1) for u,v in orbit)
                if value:coefficients[positions[parent,kind,tuple(map(tuple,orbit))]][offset+j]+=value
        if not j%128:need(not deadline.status()['stop_required'],'not completed within the allocated budget')
    for i in range(1,len(rows)):rows[i]['terms']=[[j,value] for j,value in sorted(coefficients[i].items()) if value]
    return rows


def product_coefficients(h,mask):
    adj=shared.graph(h,mask);free=list(range(2,h));triples=list(combinations(free,3));full=sum(1<<u for u in free)
    labels=[shared.canonical(5,shared.encode(adj,[0,1,*triple]))[0] for triple in triples]
    bits=[sum(1<<u for u in triple) for triple in triples];counts=Counter()
    for i,first in enumerate(bits):
        for j,second in enumerate(bits):
            if first|second==full:counts[tuple(sorted([labels[i],labels[j]]))]+=1
    need(sum(counts.values())=={5:1,6:12,7:30,8:20}[h],'complete ordered subsetunion coefficient total')
    return counts


def product_rows(seven,eight,offset,six,origin,basis,forced,deadline):
    pairs=list(combinations(sorted(forced),2))+[(mask,mask) for mask in sorted(forced)];pairs=sorted(pairs)
    position={pair:i for i,pair in enumerate(pairs)};terms=[Counter() for _ in pairs];known=[Counter() for _ in pairs]
    for h,masks in [(6,six),(7,seven),(8,eight)]:
        for j,mask in enumerate(tqdm(masks,desc=f'exact5product union{h}',mininterval=5)):
            for pair,value in product_coefficients(h,mask).items():
                if h==6:known[position[pair]][mask]+=value
                else:terms[position[pair]][j if h==7 else offset+j]+=value
            if not j%128:need(not deadline.status()['stop_required'],'not completed within the allocated budget')
    rows=[]
    for pair,coefficients,lower in zip(pairs,terms,known):
        first,second=pair;original=forced[first]*forced[second]*(1 if first==second else 2)
        collision=forced[first] if first==second else 0
        rhs=[original-collision-sum(value*origin[mask] for mask,value in lower.items()),
             -sum(value*basis[0][mask] for mask,value in lower.items()),
             -sum(value*basis[1][mask] for mask,value in lower.items())]
        rows.append(dict(kind='universal5_ordered_product_upper',rooted5_masks=list(pair),
            original_product_rhs=original,known_root5_collision=collision,known_root6_coefficients=[[mask,value] for mask,value in sorted(lower.items())],
            terms=[[j,value] for j,value in sorted(coefficients.items()) if value],rhs_affine=rhs,
            convention='Aggregate both ordered orientations into F<=G: RHS cF^2 diagonal,2cF*cG offdiagonal; overlap included by exact union order.'))
    return rows


def direct_counts(adj,root,h,catalogue_masks):
    free=[u for u in range(len(adj)) if u not in root];values=Counter()
    for subset in combinations(free,h-2):values[shared.canonical(h,shared.encode(adj,[*root,*subset]))[0]]+=1
    need(set(values)<=set(catalogue_masks),'all actual fixture flags covered')
    return values


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--resume',type=Path)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Fresh352000augmentationattempts, exact~100k sparseextension/productrows; checkpoints every100baseclasses; reserve60shutdown.')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();last_stage='initializing'
    try:
        need(sha(OLD/'model.json')==OLD_MODEL_SHA and sha(OLD/'catalogue.json')==OLD_CATALOGUE_SHA,'unchanged frozen root7 inputs')
        paths=[OLD/'model.json',OLD/'catalogue.json',FLAGS,Path(shared.__file__),Path(__file__),PROTOCOL,ROOT/'pyproject.toml',ROOT/'uv.lock',ROOT/'acceleration/command_deadline.py']
        pins={path.relative_to(ROOT).as_posix():sha(path) for path in paths}
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,scope='Conditional prismfree rooted8 necessarymodel preserving all210 root6 profiles and free root7 counts.',
            protocol_path=PROTOCOL.relative_to(ROOT).as_posix(),resume_path=None if not args.resume else args.resume.relative_to(ROOT).as_posix(),
            resume_sha256=None if not args.resume else sha(args.resume),success_criterion='Complete catalogue, exact extension+productcoefficients and positive/corruptfixture controls; nooptimization launched.',
            independent_verification_requirement='Separate newcataloguecoverage, rowderivation/coefficient and eventualrawcertificate audit before promotion.'))
        # Small canonical/product controls before catalogue generation.
        for h in range(5,9):
            coefficients=product_coefficients(h,0)
            need(coefficients=={(0,0):{5:1,6:12,7:30,8:20}[h]},'emptygraph subset-union control')
        old=read(OLD/'model.json');seven=read(OLD/'catalogue.json')['prismfree_masks']
        need(len(seven)==2750 and len(old['variables'])==2766,'frozen root7 population')
        last_stage='catalogue';catalog=catalogue(seven,deadline,out,pins,args.resume);save(out/'catalogue.json',catalog);eight=catalog['prismfree_masks']
        offset=len(old['variables']);variables=[*old['variables'],*[[8,mask] for mask in eight]]
        last_stage='extension_rows';extensions=extension_rows(seven,eight,offset,99,14,1,2,deadline)
        save(out/'extension_rows.json',extensions)
        forced={mask:value[0] for mask,value in read(FLAGS)['flag_counts']}
        need(all(value[1]==1 for _,value in read(FLAGS)['flag_counts']),'integer universalroot5input')
        origin={int(mask):value for mask,value in old['root6_profile_basis']['origin'].items()}
        basis=[{int(mask):value for mask,value in vector.items()} for vector in old['root6_profile_basis']['basis']]
        six=sorted(origin)
        last_stage='product_rows';products=product_rows(seven,eight,offset,six,origin,basis,forced,deadline);save(out/'product_rows.json',products)
        # Generic exact Petersen controls of new coefficients, independent of
        # the99parameter values and without assuming fixture automorphisms.
        last_stage='petersen_controls';adj=[0]*10
        for u in range(5):
            for v in [(u+1)%5,u+5]:adj[u]|=1<<v;adj[v]|=1<<u
            v=(u+2)%5+5;adj[u+5]|=1<<v;adj[v]|=1<<(u+5)
        need(all(row.bit_count()==3 for row in adj) and shared.prismfree(adj) and all((adj[u]&adj[v]).bit_count()==(0 if adj[u]>>v&1 else 1) for u,v in combinations(range(10),2)),'exact knownvalid prismfree Petersen fixture')
        flag5=sorted(forced);reference=None;roots=0
        for u in range(10):
            for v in range(10):
                if u!=v and not adj[u]>>v&1:
                    vector=(direct_counts(adj,[u,v],5,flag5),direct_counts(adj,[u,v],6,six),direct_counts(adj,[u,v],7,seven),direct_counts(adj,[u,v],8,eight))
                    if reference is None:reference=vector
                    need(vector==reference,'all60 directPetersen root5through8 countvectors agree literally')
                    roots+=1
        f5,f6,f7,f8=reference;unknown=Counter({j:f7[mask] for j,mask in enumerate(seven) if f7[mask]})
        unknown.update({offset+j:f8[mask] for j,mask in enumerate(eight) if f8[mask]})
        fixture_extensions=extension_rows(seven,eight,offset,10,3,0,1,deadline)
        need(all(sum(value*unknown[j] for j,value in row['terms'])==row['rhs_affine'][0] for row in fixture_extensions),'every exact Petersen h7to8 extensionrow')
        for row in products:
            first,second=row['rooted5_masks'];target=f5[first]*f5[second]*(1 if first==second else 2)
            lhs=sum(value*unknown[j] for j,value in row['terms'])+sum(value*f6[mask] for mask,value in row['known_root6_coefficients'])+(f5[first] if first==second else 0)
            need(lhs==target,'every exact Petersen orderedproduct identity')
        bad=Counter(unknown);bad[offset]+=1
        need(any(sum(value*bad[j] for j,value in row['terms'])!=row['rhs_affine'][0] for row in fixture_extensions),'corrupted8count control')
        corrupt_row,corrupt_j=next((row,j) for row in products for j,value in row['terms'] if unknown[j])
        corrupt_terms=[[j,value+(j==corrupt_j)] for j,value in corrupt_row['terms']]
        first,second=corrupt_row['rooted5_masks']
        corrupt_lhs=sum(value*unknown[j] for j,value in corrupt_terms)+sum(value*f6[mask] for mask,value in corrupt_row['known_root6_coefficients'])+(f5[first] if first==second else 0)
        target=f5[first]*f5[second]*(1 if first==second else 2)
        need(corrupt_lhs!=target,'changed productcoefficient rejected by actual exact identity')
        save(out/'controls.json',dict(petersen_nonedge_roots_counted=roots,all_root5through8_literal_vectors_equal=True,
            generic_extension_rows_checked=len(fixture_extensions),product_rows_checked=len(products),
            corrupted_count_rejected=True,corrupted_product_coefficient_rejected=True,
            shared_components='The finite canonicalization helper is shared with the producer; these controls are calibration, not independent approval.'))
        equations=[*old['equations'],*[dict(terms=row['terms'],rhs_affine=row['rhs_affine']) for row in extensions],
                   *[dict(terms=row['terms'],rhs_affine=row['rhs_affine']) for row in products]]
        model=dict(format='ROOTED8_CONDITIONAL_EXTENSION_UNIVERSAL5_PRODUCT_MODEL_V1',variables=variables,equations=equations,
            parameter_domain=[[0,20],[0,9]],profile_population=210,
            scope='Necessary localcount model under global inducedtriangularprism absence; no targetautomorphism, no graphrealizability assertion.',
            dependency_claims=[dict(id='C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY',revision=1,relation='uses_result'),
                dict(id='C-PRISMFREE-ORDERED-NONEDGE-ROOTED6-INTEGER-DOMAIN',revision=1,relation='uses_result'),
                dict(id='C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE',revision=1,relation='coverage')],
            inherited_root7_model_sha256=OLD_MODEL_SHA,product_convention='Ordered subset pairs aggregated into unordered F<=G rows, offdiagonal RHS doubled; all intersection sizes included.')
        last_stage='serialization';save(out/'model.json',model)
        summary=dict(status='CANDIDATE_ROOTED8_UNIVERSAL5_PRODUCT_MODEL',timestamp=datetime.now(timezone.utc).isoformat(),
            completed_augmentation_attempts=catalog['labelled_attempts'],conditional_root8_classes=len(eight),
            variables=len(variables),rows=len(equations),nonzero_coefficients=sum(len(row['terms']) for row in equations),
            new_extension_rows=len(extensions),new_product_rows=len(products),profile_population=210,profile_evaluations=0,
            target_resolution='UNKNOWN',independent_review=None,independent_review_reason='Newuniverse/rows/certificates pending separate verification.',
            elapsed_seconds=time.monotonic()-start,outputs_sha256={path.relative_to(ROOT).as_posix():sha(path) for path in out.iterdir() if path.is_file()})
        save(out/'summary.json',summary);print(json.dumps(summary),flush=True)
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),stage=last_stage,elapsed_seconds=time.monotonic()-start,target_resolution='UNKNOWN',
            checkpoints=[path.relative_to(ROOT).as_posix() for path in sorted(out.glob('catalogue_checkpoint_*.json'))],automatic_resume=False));raise


if __name__=='__main__':main()
