"""Corrupt canonical cross extraction metadata without inventing positive graphs."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_cross_atomic_extraction import load_reference,audit_extraction

ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def require(ok,message):
    if not ok:
        raise ValueError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--family-audit',type=Path,required=True)
    parser.add_argument('--adapted',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();require(not args.out.exists(),'Preserve existing controls')
    started=time.perf_counter()
    paths=[args.candidate,args.native,args.family_audit,args.adapted,Path(__file__),
           ROOT/'acceleration/extract_cross_atomic_family.py',ROOT/'acceleration/audit_cross_atomic_extraction.py',
           ROOT/'acceleration/audit_atomic_trace.py',ROOT/'acceleration/audit_certificate.py']
    bindings={key(path):digest(path) for path in paths}
    reference=load_reference(args.candidate,args.native,args.family_audit)
    real=json.loads(args.adapted.read_bytes())
    positive=audit_extraction(reference,real)
    controls=[]

    def negative(name,mutate):
        copied=dict(real)
        copied['moves']=real['moves'].copy();copied['moves'][0]=deepcopy(real['moves'][0])
        copied['overlap_candidates']=real['overlap_candidates'].copy();copied['overlap_candidates'][0]=deepcopy(real['overlap_candidates'][0])
        copied['original_native_indices']=real['original_native_indices'].copy()
        copied['inputs_sha256']=dict(real['inputs_sha256']);copied['by_class']=deepcopy(real['by_class'])
        mutate(copied)
        try:
            audit_extraction(reference,copied)
        except ValueError as exc:
            controls.append(dict(name=name,rejected=True,reason=str(exc)))
        else:
            raise ValueError('Cross corruption accepted: '+name)

    def replace_cycle(data,cycle):
        data['moves'][0]['alternating_cycle']=cycle
        data['moves'][0]['alternating_cycles']=[cycle]

    negative('swap_red_blue_at_same_minimum',lambda d:replace_cycle(d,[d['moves'][0]['alternating_cycle'][0],*reversed(d['moves'][0]['alternating_cycle'][1:])]))
    negative('rotate_valid_colors_away_from_minimum',lambda d:replace_cycle(d,d['moves'][0]['alternating_cycle'][2:]+d['moves'][0]['alternating_cycle'][:2]))
    negative('repeated_cycle_vertex',lambda d:replace_cycle(d,[d['moves'][0]['alternating_cycle'][0],*d['moves'][0]['alternating_cycle'][1:-1],d['moves'][0]['alternating_cycle'][0]]))
    negative('undeclared_second_cycle',lambda d:d['moves'][0]['alternating_cycles'].append(list(d['moves'][0]['alternating_cycle'])))
    negative('wrong_root_group',lambda d:d['moves'][0].update(root_group=(d['moves'][0]['root_group']+1)%7))
    negative('wrong_same_sign_class',lambda d:d['moves'][0].update(matching_class='same_0'))
    negative('changed_edge_size_modified',lambda d:d['moves'][0].update(changed_edges=6))
    negative('original_cycle_metadata_lost',lambda d:d['moves'][0]['source_alternating_cycle'].reverse())
    negative('original_native_index_modified',lambda d:d['moves'][0].update(original_native_index=d['moves'][0]['original_native_index']+1))
    negative('index_order_changed',lambda d:d['original_native_indices'].reverse())

    def drop_final(d):
        d['moves'].pop();d['overlap_candidates'].pop();d['original_native_indices'].pop();d['legal_count']-=1
    negative('omit_cross_member_with_adjusted_count',drop_final)
    negative('wrong_final_edge',lambda d:d['overlap_candidates'][0][0].__setitem__(1,83))
    negative('source_native_hash_changed',lambda d:d.update(source_native_sha256='0'*64))
    negative('base_candidate_hash_changed',lambda d:d.update(candidate_sha256='0'*64))
    negative('declared_family_hash_changed',lambda d:d['inputs_sha256'].__setitem__(key(args.family_audit),'0'*64))
    negative('raw_count_changed',lambda d:d.update(raw_cycles=23871))
    negative('wrong_single_cycle_scope',lambda d:d.update(cycle_sizes=[3]))
    require(all(digest(ROOT/path)==expected for path,expected in bindings.items()),'Bound source/input changed during controls')
    report=dict(status='CROSS_ATOMIC_EXTRACTION_REAL_AND_CORRUPTION_CONTROLS_PASS',inputs_sha256=bindings,
                positive_complete_cross_candidates=positive['legal_count'],negative_controls=len(controls),
                all_negative_controls_rejected=True,controls=controls,
                original_full_family_enumeration_repeated=False,abstract_positive_graphs_used=False,
                elapsed_seconds=time.perf_counter()-started,
                scope='One real independently audited base and its complete cross3/4 subset; negative color/order/hash/index/graph controls. No new numerical optimization or global graph claim.')
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({name:report[name] for name in ('status','positive_complete_cross_candidates','negative_controls','elapsed_seconds')}))


if __name__=='__main__':
    main()
