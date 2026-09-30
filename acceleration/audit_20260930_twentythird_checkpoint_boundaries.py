"""Independent wave23 publication-boundary helpers; no execution on import."""
from pathlib import PurePosixPath

PRIVATE='acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log'
WRAPPER_DIRS={
    'acceleration/results/20260930_twentythird_preparation',
    'acceleration/results/20260930_twentythird_artifact_packaging',
}
WRAPPER_NAMES={'catalog.json','stage_inventory.json','reference_checks.json.gz'}
RESEARCH_MAX_BYTES=10*1024**2
WRAPPER_MAX_BYTES=32*1024**2

def require(ok,message):
    if not ok:raise ValueError(message)

def size_ceiling(path):
    p=PurePosixPath(path)
    require(not p.is_absolute() and '..' not in p.parts,'safe repository-relative path')
    return WRAPPER_MAX_BYTES if p.parent.as_posix() in WRAPPER_DIRS and p.name in WRAPPER_NAMES else RESEARCH_MAX_BYTES

def payload_size(path,size):
    require(type(size) is int and size>=0,'literal nonnegative byte count')
    require(size<=size_ceiling(path),'exact-path publication size ceiling')

def privacy(paths):
    require(PRIVATE not in paths,'private historical process snapshot omitted')

def process_receipts(value):
    if isinstance(value,dict):
        command=value.get('command')
        if isinstance(command,list) and any(str(x).rsplit('/',1)[-1]=='ps' for x in command):
            require('-C' in command and command[command.index('-C')+1]=='cadical' and '-e' not in command and '-eo' not in command,'targeted process observation only')
        for v in value.values():process_receipts(v)
    elif isinstance(value,list):
        for v in value:process_receipts(v)

def claim_counts(checkpoint,claims):
    from collections import Counter
    require(len(claims)==checkpoint['claim_population']==229,'229 current claims')
    require(dict(Counter(c['status'] for c in claims))==checkpoint['claim_status_counts']==dict(VERIFIED=226,CANDIDATE=2,REFUTED=1),'exact status population')
    require(dict(Counter(c['review_state'] for c in claims))==checkpoint['claim_review_counts']==dict(CLEAR=229),'exact review population')
    require((checkpoint['verified_clear'],checkpoint['candidate_clear'],checkpoint['refuted_clear'])==(226,2,1),'current clear totals')
    require(checkpoint['target_resolution']=='UNKNOWN' and checkpoint['external_review'] is None and checkpoint['external_review_null_reason'],'no target/external promotion')
    require(checkpoint['coverage']=='Overall search coverage: UNKNOWN; no validated denominator.','unknown target-wide coverage')
    require(len(checkpoint['new_verified_ids'])==len(set(checkpoint['new_verified_ids']))==13,'thirteen distinct additions')
    for field in ['new_full_factors','complete99_graphs','new_whole_support_exclusions','new_core_exclusions','new_unrestricted_exclusions']:
        require(checkpoint[field]==0,'no broader result '+field)

def calibrate_boundaries():
    accepted=[];rejected=[]
    for directory in sorted(WRAPPER_DIRS):
        for name in sorted(WRAPPER_NAMES):
            path=directory+'/'+name;payload_size(path,WRAPPER_MAX_BYTES);accepted.append(path)
    payload_size('acceleration/research_payload.bin',RESEARCH_MAX_BYTES)
    cases=[('large_research',lambda:payload_size('acceleration/research_payload.bin',RESEARCH_MAX_BYTES+1)),
           ('wrong_directory',lambda:payload_size('acceleration/results/20260930_other/catalog.json',RESEARCH_MAX_BYTES+1)),
           ('wrong_basename',lambda:payload_size('acceleration/results/20260930_twentythird_preparation/model.json',RESEARCH_MAX_BYTES+1)),
           ('oversized_wrapper',lambda:payload_size('acceleration/results/20260930_twentythird_preparation/catalog.json',WRAPPER_MAX_BYTES+1)),
           ('path_escape',lambda:payload_size('../catalog.json',1)),
           ('private_staging',lambda:privacy([PRIVATE])),
           ('broad_process',lambda:process_receipts({'command':['ps','-eo','pid,args']}))]
    for label,call in cases:
        try:call()
        except ValueError:rejected.append(label)
        else:raise ValueError('publication boundary corruption accepted: '+label)
    return dict(exact_wrapper_positive_paths=accepted,research_boundary_positive=True,rejected=rejected)
