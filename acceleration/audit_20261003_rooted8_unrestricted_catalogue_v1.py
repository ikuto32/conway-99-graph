"""Independent complete unrestricted rooted8 orbit and augmentation coverage."""
from array import array
import argparse,copy,hashlib,json,platform,subprocess,sys,time
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261002_rooted8_catalogue_v1 as independent_core

ROOT=Path(__file__).resolve().parents[1]
PARENT='acceleration/results/20261002_rooted7_extension_model/catalogue.json'
PARENT_SHA='a01649d78eccfcb93c85ff2a86c84463458c120fd22cebaf34b8e573363084d5'
REPORT7='acceleration/results/20261002_independent_review/rooted7_catalogue01/summary.json'
REPORT7_SHA='3355afb38656eadc83eff6e0db3818eded9621f890c9d46f489fdb0324370758'
ENGINE='acceleration/theory_20261003_rooted8_unrestricted_extension_v2.py'
ENGINE_SHA='8fbc97fa13296ba4e78a839882419e0b1b1cbfe7c6415486cb444bc749e29796'
CORE='acceleration/audit_20261002_rooted8_catalogue_v1.py'
CORE_SHA='5826d45d18bf3b803c6df120f4cb3acfe17bb4c2ce010cec16dab456acc29d34'

class AuditError(ValueError):
    def __init__(self,stage,detail=''):self.stage=stage;super().__init__(stage+(': '+detail if detail else ''))
def need(ok,stage,detail=''):
    if not ok:raise AuditError(stage,detail)
def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,data):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(data,stream,indent=2);stream.write('\n')
def reject(records,label,stage,call):
    try:call()
    except AuditError as error:
        need(error.stage==stage,'CONTROL_EXACT_STAGE',str(error));records.append({'label':label,'stage':stage,'diagnostic':str(error)})
    else:raise AuditError('CONTROL_ACCEPTED',label)
def representative(lookup,mask):
    need(not mask&1,'ROOT_NONEDGE')
    value=lookup[mask>>1]-1;need(value>=0,'COMPLETE_ORBIT_MEMBERSHIP');return value
def equality(classes,generated):need(classes==sorted(generated),'COMPLETE_GENERATED_UNIVERSE')

def calibration(mapping):
    controls=[];pair_order=tuple(combinations(range(8),2))
    # Prism has root0/root1 nonadjacent, and two isolated free vertices.
    edges={(0,2),(0,3),(2,3),(1,4),(1,5),(4,5),(0,4),(1,2),(3,5)}
    prism=sum(1<<at for at,pair in enumerate(pair_order) if pair in edges)
    need(not prism&1 and independent_core.caps(independent_core.rows(prism,8)) and not independent_core.free(independent_core.rows(prism,8)),'EXACT_NONEDGE_PRISM_POSITIVE')
    need(len(mapping)==len(set(mapping))==720,'COMPLETE_FREE_LABEL_PERMUTATIONS')
    def orbit(mask):
        active=[at for at in range(28) if mask>>at&1]
        return {sum(transformation[at] for at in active) for transformation in mapping}
    def canonical_test(mask):need(min(orbit(mask))==mask,'CANONICAL_MINIMUM')
    positive=min(orbit(prism));canonical_test(positive)
    lookup={image>>1:positive+1 for image in orbit(positive)}
    need(all(representative(lookup,image)==positive for image in orbit(prism)),'POSITIVE_COMPLETE_PRISM_ORBIT')
    missing=next(iter(lookup));damaged=dict(lookup);damaged[missing]=0
    reject(controls,'omitted_real_prism_orbit_image','COMPLETE_ORBIT_MEMBERSHIP',lambda:representative(damaged,missing<<1))
    reject(controls,'prism_filter_would_omit_valid_class','COMPLETE_GENERATED_UNIVERSE',lambda:equality([0,positive],{0:None}))
    changed=max(orbit(positive));need(changed!=positive,'NONCANONICAL_CONTROL_DISTINCT')
    reject(controls,'noncanonical_prism_representative','CANONICAL_MINIMUM',lambda:canonical_test(changed))
    reject(controls,'root_relation_mutation','ROOT_NONEDGE',lambda:representative(lookup,positive|1))
    complete4=sum(1<<at for at,(u,v) in enumerate(pair_order) if u<4 and v<4)
    need(not independent_core.caps(independent_core.rows(complete4,8)) and independent_core.caps(independent_core.rows(0,8)),'CAP_NEGATIVE_AND_EMPTY_POSITIVE')
    fixture=[14333546,14334680,15404506,15428952]
    for mask in fixture:
        canonical_test(mask);need(independent_core.caps(independent_core.rows(mask,8)) and not independent_core.free(independent_core.rows(mask,8)),'ROOK_PRISM_POSITIVE_SUPPORT')
    return {'complete_free_label_permutations':720,'nonedge_prism_positive_mask':positive,'positive_prism_orbit_size':len(lookup),'rook_prism_support':fixture,'strict_controls':controls,'full_catalogue_checked':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('calibration','full'));ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--artifact-dir',type=Path);ap.add_argument('--producer-summary-sha256');ap.add_argument('--calibration',type=Path);ap.add_argument('--calibration-sha256');args=ap.parse_args()
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='New complete unrestrictedroot8 catalogue calibration/full354560augmentation coverage;512MiB lookup,40second full shutdown reserve')
    reserve=20 if args.mode=='calibration' else 40;out=args.out.resolve();need(out.is_relative_to(ROOT),'BOUNDED_OUTPUT');out.mkdir(parents=True,exist_ok=False);pins={};progress={'phase':'pins','completed_classes':0,'completed_parents':0}
    def tick():need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>reserve,'DEADLINE','not completed within the allocated budget')
    def pin(name,expected=None):
        tick();name=Path(name).as_posix();actual=digest(ROOT/name);need(expected is None or actual==expected,'INPUT_PIN',name);pins[name]=actual
    def read(name):return json.loads((ROOT/name).read_bytes())
    try:
        for name,identity in [(PARENT,PARENT_SHA),(REPORT7,REPORT7_SHA),(ENGINE,ENGINE_SHA),(CORE,CORE_SHA)]:pin(name,identity)
        for name in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),'acceleration/command_deadline.py','acceleration/run_compute_command.py','uv.lock','pyproject.toml']:pin(name)
        parents=read(PARENT)['complete_locally_admissible_masks'];need(len(parents)==2770 and read(REPORT7)['complete_rooted_classes']==2770,'COMPLETE_INDEPENDENT_PARENT_UNIVERSE')
        mapping=independent_core.maps();controls=calibration(mapping)
        report={'timestamp':datetime.now(timezone.utc).isoformat(),'verifier':'/root/checkpoint_audit','producer':'/root/structural','command':[sys.executable,*sys.argv],'cwd':str(ROOT),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'python':platform.python_version(),'inputs_sha256':pins,'controls':controls,'target_resolution':False,'new_exclusions':0,'shared_components':['Pinned earlier independent bit-neighborhood/cap/orbit-array methods, newly scoped without prism filtering; no producer import or gate transfer.','Python exact integers/array uint32, SHA256, uv environment and supported deadline/Job supervisor.'],'limitations':['Finite flag-catalogue coverage only; target graph realization and necessary row operator are separately checked.','Root labels are fixed individually; free-label canonicalization assumes no target automorphism.']}
        if args.mode=='calibration':report['status']='INDEPENDENT_UNRESTRICTED_ROOTED8_CATALOGUE_V1_PREOUTPUT_CALIBRATION_PASS'
        else:
            need(all((args.artifact_dir,args.producer_summary_sha256,args.calibration,args.calibration_sha256)),'FULL_EXACT_ARGUMENTS')
            pin(args.calibration,args.calibration_sha256);cal=read(args.calibration)
            need(cal['status']=='INDEPENDENT_UNRESTRICTED_ROOTED8_CATALOGUE_V1_PREOUTPUT_CALIBRATION_PASS' and cal['inputs_sha256'][Path(__file__).relative_to(ROOT).as_posix()]==pins[Path(__file__).relative_to(ROOT).as_posix()],'APPLICABLE_PREOUTPUT_CALIBRATION')
            directory=args.artifact_dir.as_posix().rstrip('/')+'/';pin(directory+'summary.json',args.producer_summary_sha256);summary=read(directory+'summary.json')
            pin(directory+'catalogue.json',summary['outputs_sha256']['catalogue.json']);raw=read(directory+'catalogue.json');classes=raw['complete_locally_admissible_masks']
            need(raw['format']=='COMPLETE_UNRESTRICTED_ROOTED8_AUGMENTATION_V1' and raw['base_complete_root7_masks']==parents and raw['prism_filter_applied'] is False,'FULL_UNRESTRICTED_CATALOGUE_SCOPE')
            need(classes==sorted(set(classes)) and all(type(mask)is int and 0<=mask<1<<28 and not mask&1 for mask in classes),'EXACT_CLASS_UNIVERSE')
            lookup=array('I',[0])*(1<<27);need(lookup.itemsize==4,'UINT32_LOOKUP');labelled=images=0;progress['phase']='allclass orbits'
            for index,mask in enumerate(tqdm(classes,desc='every720 unrestricted root8 image',mininterval=5)):
                need(independent_core.caps(independent_core.rows(mask,8)),'EVERY_CLASS_LOCAL_CAPS');active=[at for at in range(28) if mask>>at&1];lowest=mask
                for transformation in mapping:
                    image=sum(transformation[at] for at in active);lowest=min(lowest,image);at=image>>1
                    need(lookup[at] in (0,mask+1),'DISJOINT_CLASS_ORBITS')
                    if not lookup[at]:lookup[at]=mask+1;labelled+=1
                    images+=1
                need(lowest==mask,'CANONICAL_MINIMUM');progress['completed_classes']=index+1
                if not (index+1)%2000:save(out/f'orbit_prefix_{index+1:05d}.json',dict(progress,permutation_images_checked=images,labelled_orbit_members=labelled,elapsed_seconds=time.monotonic()-start))
                tick()
            generated={};attempts=admissible=prism_extensions=0;progress['phase']='all2770x128 unrestricted augmentations'
            for index,parent in enumerate(tqdm(parents,desc='all354560 independent root8 augmentations',mininterval=5)):
                old=independent_core.rows(parent,7)
                for neighborhood in range(128):
                    attempts+=1;adj=[*old,neighborhood]
                    for vertex in range(7):
                        if neighborhood>>vertex&1:adj[vertex]|=1<<7
                    if not independent_core.caps(adj):continue
                    admissible+=1;mask=independent_core.encode(adj);canonical=representative(lookup,mask)
                    if canonical not in generated:generated[canonical]=[parent,neighborhood]
                    if not independent_core.free(adj):prism_extensions+=1
                progress['completed_parents']=index+1
                if not (index+1)%250:save(out/f'augmentation_prefix_{index+1:04d}.json',dict(progress,labelled_attempts=attempts,locally_admissible=admissible,generated_classes=len(generated),elapsed_seconds=time.monotonic()-start))
                tick()
            equality(classes,generated)
            need(raw['completed_parent_classes']==2770 and raw['labelled_attempts']==attempts==354560 and raw['locally_admissible_extensions']==admissible,'ACTUAL_FROZEN_GENERATION_COUNTS')
            need(raw['first_generating_extensions']==[[mask,*generated[mask]] for mask in classes],'EVERY_FIRST_GENERATING_WITNESS')
            need(set(controls['rook_prism_support'])<=set(classes) and prism_extensions>0,'REAL_PRISM_SUPPORT_RETAINED')
            missing=next(mask for mask in controls['rook_prism_support'] if mask in generated);damaged=dict(generated);del damaged[missing];negative=[]
            reject(negative,'actual_omitted_prism_class','COMPLETE_GENERATED_UNIVERSE',lambda:equality(classes,damaged))
            parent,neighbors=generated[missing];adj=[*independent_core.rows(parent,7),neighbors]
            for vertex in range(7):
                if neighbors>>vertex&1:adj[vertex]|=1<<7
            position=independent_core.encode(adj)>>1;saved=lookup[position];lookup[position]=0
            reject(negative,'actual_missing_qualifying_prism_orbit','COMPLETE_ORBIT_MEMBERSHIP',lambda:representative(lookup,position<<1));lookup[position]=saved
            report.update(status='INDEPENDENT_COMPLETE_UNRESTRICTED_ROOTED8_CATALOGUE_PASS',parent_classes=2770,labelled_augmentation_attempts=attempts,locally_admissible_extensions=admissible,prism_containing_extensions_retained=prism_extensions,complete_unrestricted_rooted_classes=len(classes),free_label_permutations_per_class=720,exact_labelled_image_checks=images,distinct_labelled_orbit_members=labelled,lookup_bytes=len(lookup)*lookup.itemsize,prism_filter_applied=False,actual_omission_controls=negative,statement='The complete unrestricted locally admissible ordered-nonedge rooted8 catalogue is exactly the frozen class list, independently generated from all2770 complete rooted7 parents and all128 neighborhoods, with exact local caps, canonical minima, disjoint720-image free-label orbits and first witnesses checked; no prism filter or target automorphism assumption.')
        report.update(elapsed_seconds=time.monotonic()-start,deadline=deadline.status());save(out/'summary.json',report)
        print(json.dumps({'status':report['status'],'sha256':digest(out/'summary.json'),'elapsed_seconds':report['elapsed_seconds']}))
    except BaseException as error:
        save(out/'failure.json',{'error':repr(error),'progress':progress,'inputs_sha256':pins,'timestamp':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'target_resolution':False});raise

if __name__=='__main__':main()
