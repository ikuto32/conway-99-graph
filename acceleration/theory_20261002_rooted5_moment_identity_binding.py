"""Bind new exact rooted5 solutions to the archived flag moment bases.

This is a producer-side identity check, not independent approval.
"""
from datetime import datetime,timezone
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,item):
    with path.open('x',encoding='utf8',newline='\n') as stream:
        json.dump(item,stream,indent=2);stream.write('\n')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--rigidity',type=Path,required=True)
    p.add_argument('--basis',type=Path,required=True)
    p.add_argument('--certificates',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    basis=json.loads(args.basis.read_text());inputs=[args.basis];results=[]
    for name,roots,multiplier in [('ordered_edge',1386,2),('ordered_nonedge',8316,1)]:
        forced_path=args.rigidity/f'{name}_forced5flags.json';certificate_path=args.certificates/f'{name}_certificate.json'
        inputs.extend([forced_path,certificate_path])
        forced=json.loads(forced_path.read_text())['flag_counts'];forced=dict((mask,Fraction(*count)) for mask,count in forced)
        flags=basis['families'][name]['flag_masks'];certificate=json.loads(certificate_path.read_text())
        vector=certificate['terms'][0]['integer_vector']
        assert set(forced)==set(flags)
        counts=[forced[mask] for mask in flags]
        assert all(count.denominator==1 and count>=0 for count in counts)
        assert counts==[multiplier*v for v in vector]
        assert sum(counts)==147440
        integer=[int(x) for x in counts]
        save(args.out/f'{name}_universal_moment.json',dict(flag_masks=flags,forced_per_root_counts=integer,
                                                          ordered_root_count=roots,
                                                          matrix=[[roots*a*b for b in integer] for a in integer],
                                                          status='CANDIDATE_UNIVERSAL_CONDITIONAL_IDENTITY',
                                                          statement='For every srg(99,14,1,2), every ordered root of this relation has this integer5flag vector, hence M=ordered_root_count*c*c^T.',
                                                          assumptions=['Necessary rooted model and exact full-rank/unique solution require independent checking.'],
                                                          independent=False))
        results.append(dict(family=name,flags=len(flags),all_exact_match=True,ordered_roots=roots,sum_per_root=147440,
                            zero_per_root_flags=sum(x==0 for x in integer)))
    save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),
                                      command=[sys.executable,*sys.argv],cwd=str(ROOT),
                                      inputs=[dict(path=str(f),sha256=sha(f)) for f in inputs],
                                      scope='Bind unique rooted5 counts and explicit endpoint moment certificate bases; no new target exclusion.',
                                      verification='Separate reviewer must approve rooted model and mathematical transport.'))
    save(args.out/'summary.json',dict(status='CANDIDATE_BINDING_COMPLETE',results=results,target_resolution='UNKNOWN',exact_new_bound=None))
    print(json.dumps(results),flush=True)


if __name__=='__main__':
    main()
