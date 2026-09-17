"""Necessary neighborhood matching filter for the frozen partial-K pilot.

Producer reuses the earlier matching recurrence, not an independent checker.
Original partial-domain IDs are retained; no source tables are modified.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm
import theory_20260917_triangle_matching as matching

BASE = Path('acceleration/results/20260917_partial_matching')
AUDIT = Path('acceleration/results/20260917_independent_review/partial_matching/summary.json')


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(p, x):
    with p.open('x', encoding='utf-8') as f:
        json.dump(x, f, separators=(',', ':'))
        f.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seconds', type=float, default=180)
    ap.add_argument('--resume', action='store_true')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    audit = json.loads(AUDIT.read_bytes())
    assert audit['status'] == 'INDEPENDENT_PARTIAL_K_DOMAINS_AND_LINEAR_CAPS_PASS'
    inputs = [BASE/'manifest.json', AUDIT, Path(__file__), Path(matching.__file__), Path('uv.lock')]
    inputs += [BASE/f'domain_{u:02d}.json' for u in range(84)]
    hashes = {str(p): digest(p) for p in inputs}
    for p in inputs:
        if p.parent == BASE:
            assert digest(p) in audit['inputs_sha256'].values()
    manifest = dict(timestamp=stamp(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(Path.cwd()), python=platform.python_version(),
        inputs_sha256=hashes, question='Does the necessary neighborhood perfect-matching test remove partial-K local stars?',
        scope='All 54478 original choices from frozen 162-fixed-K, 1740-unknown partial-coordinate family; prescribed other absences retained.',
        selection='Every original domain in ascending center and original ID; no outcome-dependent selection.',
        criterion='Exact matching count zero rejects a local choice; no empty domain implies no family exclusion from this test alone.',
        threshold='Integer zero only', seconds_per_invocation=args.seconds, random_seed=None,
        random_seed_reason='Deterministic enumeration', shared_code='Earlier producer matching recurrence and incremental single-edge cap test; independent check still required.',
        target_resolution=False)
    if args.resume:
        old=json.loads((args.out/'manifest.json').read_bytes())
        assert old['inputs_sha256']==hashes
        save(args.out/('resume_'+str(time.time_ns())+'.json'), manifest)
    else:
        save(args.out/'manifest.json', manifest)
        save(args.out/'controls.json', matching.controls())
    fixed=json.loads((BASE/'manifest.json').read_bytes())
    # Build directly from the frozen partial manifest, with no domain-generation import.
    labels=[(2*a+s,2*b+t) for a in range(7) for b in range(a+1,7) for s in (0,1) for t in (0,1)]
    rows=[0]*99
    for v in range(1,15): matching.add(rows,0,v)
    for v in range(1,15,2): matching.add(rows,v,v+1)
    for u,pair in enumerate(labels,15):
        for s in pair: matching.add(rows,u,s+1)
    for a,b in fixed['remaining_fixed_K_edges_outer']: matching.add(rows,a+15,b+15)
    supports=[{s//2 for s in pair} for pair in labels]
    unknown={(a,b) for a in range(84) for b in range(a+1,84) if not supports[a]&supports[b]}
    unknown.update(tuple(e) for e in fixed['freed_legal_matching_edges_outer'])
    unknown={(a+15,b+15) for a,b in unknown}
    assert len(unknown)==1740 and matching.caps(rows)
    start=time.monotonic(); summaries=[]
    for u in tqdm(range(84),desc='Partial star neighborhood matching',unit='center'):
        dest=args.out/f'vertex_{u:02d}.json'
        if args.resume and dest.exists():
            data=json.loads(dest.read_bytes())
        else:
            table=json.loads((BASE/f'domain_{u:02d}.json').read_bytes())['domain_masks_hex']
            records=[]
            for i,mask in enumerate(table):
                if time.monotonic()-start>args.seconds:
                    save(args.out/('incomplete_'+str(time.time_ns())+'.json'),dict(timestamp=stamp(),reason='TIME_CAP',completed_centers=len(summaries),current_center=u,unsealed_choices=len(records)))
                    return 3
                record=matching.check_star(rows,unknown,u+15,int(mask,16))
                record.update(original_id=i,mask=mask)
                records.append(record)
            data=dict(outer_vertex=u,original_count=len(table),records=records,rejected_ids=[r['original_id'] for r in records if r['matching_count']==0])
            save(dest,data)
        summaries.append(dict(outer_vertex=u,original_count=data['original_count'],rejected=len(data['rejected_ids']),surviving=data['original_count']-len(data['rejected_ids']),path=str(dest),sha256=digest(dest)))
    save(args.out/'summary.json',dict(timestamp=stamp(),status='CANDIDATE_COMPLETE_PARTIAL_K_MATCHING_FILTER',vertices=summaries,
        original_choices=sum(x['original_count'] for x in summaries),rejected_choices=sum(x['rejected'] for x in summaries),
        surviving_choices=sum(x['surviving'] for x in summaries),empty_domains=sum(x['surviving']==0 for x in summaries),
        manifest_sha256=digest(args.out/'manifest.json'),elapsed_seconds=time.monotonic()-start,
        limitations='A surviving matching tests allowed edges individually; combined edges may still fail caps or global extension. Pending independent check.'))
    print(json.dumps({k:v for k,v in json.loads((args.out/'summary.json').read_bytes()).items() if k!='vertices'}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
