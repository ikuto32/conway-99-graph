"""Independent orbit-array and exhaustive augmentation rooted8 catalogue audit."""
from array import array
import argparse,hashlib,json,platform,subprocess,sys,time
from datetime import datetime,timezone
from itertools import combinations,permutations
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
CAT8='acceleration/results/20261002_rooted8_universal5_product_model02/catalogue.json'
CAT8_SHA='8dbec8214e651980a7a4939526c0b92a6e0a26387cb900228bb72cf0cf6d356c'
CAT7='acceleration/results/20261002_rooted7_extension_model/catalogue.json'
CAT7_SHA='a01649d78eccfcb93c85ff2a86c84463458c120fd22cebaf34b8e573363084d5'
REPORT7='acceleration/results/20261002_independent_review/rooted7_catalogue01/summary.json'
REPORT7_SHA='3355afb38656eadc83eff6e0db3818eded9621f890c9d46f489fdb0324370758'
PAIRS8=tuple(combinations(range(8),2));PAIRS7=tuple(combinations(range(7),2))
SIXSETS=tuple(combinations(range(8),6))


def need(value,why):
    if not value:raise ValueError(why)


def rows(mask,n):
    values=[0]*n
    for bit,(u,v) in enumerate(combinations(range(n),2)):
        if mask&(1<<bit):values[u]|=1<<v;values[v]|=1<<u
    return values


def caps(neighbors):
    return all((neighbors[u]&neighbors[v]).bit_count()<=2-int(bool(neighbors[u]&(1<<v))) for u,v in combinations(range(len(neighbors)),2))


def prism(neighbors,selected):
    domain=sum(1<<u for u in selected)
    if any((neighbors[u]&domain).bit_count()!=3 for u in selected):return False
    for tail in combinations(selected[1:],2):
        first=(selected[0],*tail);other=[u for u in selected if u not in first]
        if all(neighbors[u]&(1<<v) for u,v in combinations(first,2)) and all(neighbors[u]&(1<<v) for u,v in combinations(other,2)):return True
    return False


def free(neighbors):return not any(prism(neighbors,selected) for selected in SIXSETS)


def encode(neighbors):
    return sum(1<<bit for bit,(u,v) in enumerate(combinations(range(len(neighbors)),2)) if neighbors[u]&(1<<v))


def maps():
    result=[];position={pair:at for at,pair in enumerate(PAIRS8)}
    for tail in permutations(range(2,8)):
        order=(0,1,*tail);inverse={vertex:at for at,vertex in enumerate(order)}
        result.append(tuple(1<<position[tuple(sorted((inverse[u],inverse[v])))] for u,v in PAIRS8))
    return result


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')


def complete_generation(classes,generated):need(sorted(generated)==classes,'all and only claimed classes generated')


def representative(lookup,mask):
    value=lookup[mask>>1]-1;need(value>=0,'qualifying labelled extension belongs to a claimed orbit');return value


def reject(call,expected):
    try:call()
    except ValueError as error:need(str(error)==expected,'exact expected corrupted catalogue diagnostic');return str(error)
    raise ValueError('corrupted catalogue control accepted')


def run(args):
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Complete20k*720free-label image coverage and352000independent augmentations;60seconds reserve')
    out=args.out.resolve();out.mkdir(exist_ok=False);pins={};progress={'phase':'initializing','completed_classes':0,'completed_parents':0}
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>60,'not completed within the allocated budget')
    def pin(name,wanted=None):
        tick();actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest();need(wanted is None or actual==wanted,'frozen bytes '+name);pins[name]=actual
    def read(name):return json.loads((ROOT/name).read_bytes())
    try:
        for name,digest in [(CAT8,CAT8_SHA),(CAT7,CAT7_SHA),(REPORT7,REPORT7_SHA)]:pin(name,digest)
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py']:pin(p.relative_to(ROOT).as_posix())
        raw=read(CAT8);parents=read(CAT7)['prismfree_masks'];classes=raw['prismfree_masks']
        need(read(REPORT7)['complete_rooted_classes']==2770 and read(REPORT7)['conditional_prismfree_classes']==2750,'pinned independent complete parent catalogue')
        need(raw['format']=='COMPLETE_CONDITIONAL_ROOTED8_AUGMENTATION_V1' and raw['base_prismfree_root7_masks']==parents and len(parents)==2750,'exact covered parent universe')
        need(classes==sorted(set(classes)) and len(classes)==20253 and all(type(mask)is int and 0<=mask<1<<28 and not mask&1 for mask in classes),'exact raw class identity/sizes')
        # Independent explicit prism on the first6 vertices, plus2 isolated.
        edges={(0,1),(0,2),(1,2),(3,4),(3,5),(4,5),(0,3),(1,4),(2,5)}
        mask=sum(1<<bit for bit,pair in enumerate(PAIRS8) if pair in edges);control=rows(mask,8)
        need(caps(control) and not free(control),'known exact locally admissible prism detected')
        damaged=rows(mask^(1<<PAIRS8.index((0,3))),8);need(free(damaged),'missing matching edge does not create prism')
        complete4=sum(1<<bit for bit,(u,v) in enumerate(PAIRS8) if u<4 and v<4)
        need(not caps(rows(complete4,8)) and caps(rows(0,8)) and free(rows(0,8)),'cap violation/empty positive controls')
        mapping=maps();need(len(mapping)==720 and len(set(mapping))==720,'complete free label permutation population')
        # fixed root nonedge removes bit0: exactly2^27 possible coordinates.
        lookup=array('I',[0])*(1<<27);need(lookup.itemsize==4,'exact uint32 lookup');labelled=0;image_checks=0
        progress['phase']='claimed class orbit normalization'
        for at,mask in enumerate(tqdm(classes,desc='all720 free-label images per root8 class',mininterval=5)):
            need(caps(rows(mask,8)) and free(rows(mask,8)),'every claimed representative satisfies conditional predicates')
            active=[bit for bit in range(28) if mask&(1<<bit)];lowest=mask
            for transformation in mapping:
                image=0
                for bit in active:image|=transformation[bit]
                lowest=min(lowest,image);position=image>>1
                previous=lookup[position];need(previous==0 or previous==mask+1,'different claimed class orbits disjoint')
                if previous==0:lookup[position]=mask+1;labelled+=1
                image_checks+=1
            need(lowest==mask,'every raw representative is independently the least orbit member')
            progress['completed_classes']=at+1
            if (at+1)%1000==0:save(out/f'orbit_prefix_{at+1:05d}.json',dict(progress,permutation_images_checked=image_checks,labelled_orbit_members=labelled,elapsed_seconds=time.monotonic()-start))
            tick()
        generated={};attempts=admissible=accepted=0;progress['phase']='complete parent augmentations'
        for at,parent in enumerate(tqdm(parents,desc='all2750x128 conditional rooted8 extensions',mininterval=5)):
            original=rows(parent,7)
            for neighborhood in range(128):
                attempts+=1;neighbor=[*original,neighborhood]
                for vertex in range(7):
                    if neighborhood&(1<<vertex):neighbor[vertex]|=1<<7
                if not caps(neighbor):continue
                admissible+=1
                if not free(neighbor):continue
                accepted+=1;rawmask=encode(neighbor);canonical=representative(lookup,rawmask)
                if canonical not in generated:generated[canonical]=[parent,neighborhood]
            progress['completed_parents']=at+1
            if (at+1)%250==0:save(out/f'augmentation_prefix_{at+1:04d}.json',dict(progress,labelled_attempts=attempts,locally_admissible=admissible,prismfree=accepted,generated_classes=len(generated),elapsed_seconds=time.monotonic()-start))
            tick()
        complete_generation(classes,generated)
        need(raw['completed_base_classes']==2750 and raw['labelled_attempts']==attempts==352000 and raw['locally_admissible_extensions']==admissible and raw['prismfree_extensions']==accepted,'exact raw finite counters')
        need(raw['first_generating_extensions']==[[mask,*generated[mask]] for mask in classes],'all first generating witnesses independently reproduced')
        missing=classes[-1];witness=generated[missing];original=rows(witness[0],7);neighbor=[*original,witness[1]]
        for vertex in range(7):
            if witness[1]&(1<<vertex):neighbor[vertex]|=1<<7
        position=encode(neighbor)>>1;saved=lookup[position];lookup[position]=0
        missing_orbit=reject(lambda:representative(lookup,encode(neighbor)),'qualifying labelled extension belongs to a claimed orbit');lookup[position]=saved
        damaged=dict(generated);del damaged[missing]
        missing_generated=reject(lambda:complete_generation(classes,damaged),'all and only claimed classes generated')
        missing_raw=reject(lambda:complete_generation(classes[:-1],generated),'all and only claimed classes generated')
        summary=dict(status='INDEPENDENT_COMPLETE_CONDITIONAL_ROOTED8_CATALOGUE_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',producer='/root/structural',
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
            parent_classes=2750,labelled_augmentation_attempts=352000,locally_admissible_extensions=admissible,prismfree_extensions=accepted,complete_conditional_rooted_classes=20253,
            free_label_permutations_per_class=720,exact_labelled_image_checks=image_checks,distinct_labelled_orbit_members=labelled,lookup_bytes=len(lookup)*lookup.itemsize,
            controls={'known_prism_detected':True,'missing_prism_edge_rejected':True,'cap_violation_rejected':True,'empty_graph_positive':True,
                      'missing_orbit_and_generated_class_rejected':True,'exact_negative_diagnostics':[missing_orbit,missing_generated,missing_raw]},
            statement='Exact complete prism-free rooted8 nonedge catalogue is the saved20253classes, established from the independently covered2750root7 parents and all128 neighborhoods, with exact free-label orbit normalization/disjointness and every local cap/prism filter checked.',
            scope='Complete finite conditional catalogue only; absence of a target prism remains UNKNOWN.',prismfree_premise_established=False,new_exclusions=0,target_resolution=False,
            dependencies=[{'id':'C-UNRESTRICTED-ROOTED7-NONEDGE-LOCAL-CATALOGUE-COVERAGE','revision':1,'relation':'coverage'}],
            limitations=['Root8 ordinary marked/product model is not checked by this coverage audit.','Free-label coordinate normalization assumes no target automorphism.','No mathematical exclusion, target graph or global search coverage fraction.'],
            elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
        save(out/'summary.json',summary);print(json.dumps({k:summary[k] for k in ['status','complete_conditional_rooted_classes','exact_labelled_image_checks','elapsed_seconds']}))
    except Exception as error:
        save(out/'failure.json',dict(error=repr(error),progress=progress,inputs_sha256=pins,timestamp=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,target_resolution=False));raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);run(ap.parse_args())
