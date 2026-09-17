"""Necessary neighborhood matching filter on new complete four-coordinate stars.

Reuses the prior producer recurrence, never calls it independent verification.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm
import theory_20260917_triangle_matching as matching

BASE=Path('acceleration/results/20260917_partial_four_matchings')
PROTOCOL=Path('docs/NEXT_20260917_FOUR_COORDINATE_MATCHING_FILTER.md')


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def stamp():return datetime.now(timezone.utc).isoformat()
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,separators=(',',':'));f.write('\n')


def build(manifest):
    labels=[(2*a+s,2*b+t) for a,b in combinations(range(7),2) for s in(0,1) for t in(0,1)]
    rows=[0]*99
    for v in range(1,15):matching.add(rows,0,v)
    for v in range(1,15,2):matching.add(rows,v,v+1)
    for u,pair in enumerate(labels,15):
        for s in pair:matching.add(rows,u,s+1)
    fixed=manifest['remaining_fixed_K_edges_outer']
    assert len(fixed)==144
    for a,b in fixed:matching.add(rows,a+15,b+15)
    supports=[{s//2 for s in pair} for pair in labels]
    unknown={(a,b) for a,b in combinations(range(84),2) if not supports[a]&supports[b]}
    unknown.update(map(tuple,manifest['freed_legal_matching_edges_outer']))
    assert sorted(unknown)==list(map(tuple,manifest['unknown_edges_outer'])) and len(unknown)==1920
    assert Counter(14-rows[u+15].bit_count() for u in range(84))=={10:4,9:40,8:40}
    assert matching.caps(rows)
    return rows,{(a+15,b+15) for a,b in unknown}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--domain-audit',type=Path,required=True)
    ap.add_argument('--domain-audit-sha256',required=True)
    ap.add_argument('--resume-checkpoint',type=Path)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    assert not any(args.out.iterdir()),'Use a fresh directory for every invocation'
    assert digest(args.domain_audit)==args.domain_audit_sha256
    audit=read(args.domain_audit)
    assert audit['status']=='INDEPENDENT_FOUR_COORDINATE_DOMAINS_PASS'
    assert audit['domain_choices']==290460 and len(audit['records'])==84
    paths=[BASE/'manifest.json',args.domain_audit,Path(__file__),Path(matching.__file__),PROTOCOL,Path('uv.lock')]
    paths+=[BASE/f'domain_{u:02d}.json' for u in range(84)]
    for p in paths:
        if p.parent==BASE:assert digest(p) in audit['inputs_sha256'].values(),f'Unbound domain {p}'
    hashes={str(p):digest(p) for p in paths}
    source=read(BASE/'manifest.json');rows,unknown=build(source)
    manifest=dict(timestamp=stamp(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),inputs_sha256=hashes,
        question='Does necessary N(center)=7K2 matching consistency remove four-coordinate localstar choices?',
        scope=source['scope'],population='All290460 originalmasks across84 complete four-coordinate domains',
        selection='Ascending center0..83, ascending originalID with no outcome selection',
        criterion='Exact residual matching count zero removes a localchoice; positive existence is only a necessary survival condition',
        seconds_per_invocation=180,random_seed=None,random_seed_reason='Deterministic enumeration',
        shared_components=['Prior producer full99 incremental single-edge cap checker','Prior producer exact subset matching recurrence','Python standard library','tqdm progress'],
        resume_checkpoint=str(args.resume_checkpoint) if args.resume_checkpoint else None,
        resume_checkpoint_sha256=digest(args.resume_checkpoint) if args.resume_checkpoint else None,
        mathematical_status='CANDIDATE_PENDING_INDEPENDENT_REVIEW',LP_ran=False,target_resolution=False)
    save(args.out/'manifest.json',manifest);save(args.out/'controls.json',matching.controls())
    completed=[];partial=None
    if args.resume_checkpoint:
        previous=read(args.resume_checkpoint)
        assert previous['inputs_sha256']==hashes and previous['status']=='INCOMPLETE_TIME_CAP'
        completed=previous['completed_centers'];partial=previous['partial_center']
        for item in completed:assert digest(item['path'])==item['sha256']
        if partial:assert digest(partial['path'])==partial['sha256']
        assert [x['outer_vertex'] for x in completed]==list(range(len(completed)))
    started=time.monotonic();fresh_evaluations=0
    for u in tqdm(range(len(completed),84),desc='Four-coordinate neighborhood matching',unit='center'):
        table=read(BASE/f'domain_{u:02d}.json')['domain_masks_hex']
        records=[]
        if partial:
            assert partial['outer_vertex']==u
            data=read(partial['path']);records=data['records'];partial=None
            assert [x['original_id'] for x in records]==list(range(len(records)))
            assert all(x['mask']==table[i] for i,x in enumerate(records))
        for i in range(len(records),len(table)):
            if time.monotonic()-started>=180:
                part_path=args.out/f'partial_vertex_{u:02d}.json'
                save(part_path,dict(outer_vertex=u,original_count=len(table),records=records,complete=False))
                checkpoint=dict(timestamp=stamp(),status='INCOMPLETE_TIME_CAP',inputs_sha256=hashes,
                    completed_centers=completed,partial_center=dict(outer_vertex=u,path=str(part_path),sha256=digest(part_path)),
                    fresh_evaluations=fresh_evaluations,total_completed_evaluations=sum(x['original_count'] for x in completed)+len(records),
                    elapsed_seconds=time.monotonic()-started,target_resolution=False)
                save(args.out/'checkpoint.json',checkpoint)
                print(json.dumps({k:v for k,v in checkpoint.items() if k not in('inputs_sha256','completed_centers')}))
                return 3
            mask=int(table[i],16)
            assert mask.bit_count()+rows[u+15].bit_count()==14
            record=matching.check_star(rows,unknown,u+15,mask)
            record.update(original_id=i,mask=table[i]);records.append(record);fresh_evaluations+=1
        dest=args.out/f'vertex_{u:02d}.json'
        rejected=[x['original_id'] for x in records if x['matching_count']==0]
        rejected_set=set(rejected)
        surviving=[i for i in range(len(table)) if i not in rejected_set]
        save(dest,dict(outer_vertex=u,original_count=len(table),records=records,rejected_ids=rejected,surviving_ids=surviving,complete=True))
        completed.append(dict(outer_vertex=u,original_count=len(table),rejected=len(rejected),surviving=len(surviving),path=str(dest),sha256=digest(dest)))
    summary=dict(timestamp=stamp(),status='CANDIDATE_COMPLETE_FOUR_COORDINATE_MATCHING_FILTER',vertices=completed,
        inputs_sha256=hashes,original_choices=sum(x['original_count'] for x in completed),
        rejected_choices=sum(x['rejected'] for x in completed),surviving_choices=sum(x['surviving'] for x in completed),
        empty_domains=sum(x['surviving']==0 for x in completed),fresh_evaluations=fresh_evaluations,
        elapsed_seconds=time.monotonic()-started,manifest_sha256=digest(args.out/'manifest.json'),
        limitations='Allowed edges checked separately; even surviving perfectmatching may fail jointcaps or globalextension. Independent fullgraph/DP review required.',
        LP_ran=False,target_resolution=False)
    assert summary['original_choices']==290460
    save(args.out/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in('vertices','inputs_sha256')}))
    return 0


if __name__=='__main__':raise SystemExit(main())
