"""Extract the complete cross3/4 single-cycle subset of an audited atomic batch."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def require(ok,message):
    if not ok:
        raise ValueError(message)


def path_key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def resolve(name):
    path=Path(str(name).replace('\\','/'))
    return path if path.is_absolute() else ROOT/path


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def canonical_cycle(removed,added):
    red,blue={},{}
    for edges,matching in ((removed,red),(added,blue)):
        for u,v in edges:
            require(u not in matching and v not in matching,'Changed edges are not matchings')
            matching[u]=v;matching[v]=u
    require(set(red)==set(blue),'Changed endpoint sets differ')
    start=min(red);u=start;cycle=[]
    while True:
        v=red[u]
        require(u not in cycle and v not in cycle,'Cycle repeats a vertex')
        cycle.extend((u,v));u=blue[v]
        if u==start:
            break
    require(len(cycle)==len(red),'Replacement has more than one alternating cycle')
    return cycle


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--family-audit',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),'Preserve prior extraction')
    family=json.loads(args.family_audit.read_bytes())
    require(family['status']=='INDEPENDENT_COMPLETE_ATOMIC_CYCLE_FAMILY_PASS' and family['cycle_size']=='both',
            'Need complete audited atomic3/4 family')
    inputs={path_key(resolve(name)):expected for name,expected in family['inputs_sha256'].items()}
    require(inputs.get(path_key(args.candidate))==digest(args.candidate),'Base candidate not bound to family proof')
    require(inputs.get(path_key(args.native))==digest(args.native),'Native batch not bound to family proof')
    require(all(digest(resolve(name))==expected for name,expected in inputs.items()),'Changed full-family dependency')
    inputs.update({path_key(path):digest(path) for path in (args.family_audit,Path(__file__))})
    native=json.loads(args.native.read_bytes())
    require(native['status']=='COMPLETE_ATOMIC_CYCLE_SUBFAMILY_ENUMERATION' and native['cycle_size']=='both', 'Wrong native family')
    require(len(native['moves'])==len(native['overlap_candidates'])==family['legal_cycles'],'Native size differs')
    indices=[i for i,move in enumerate(native['moves']) if move['matching_class']=='cross']
    candidates=[];moves=[]
    for i in indices:
        original=native['moves'][i]
        require(original['cycle_size'] in (3,4),'Unsupported cross cycle')
        cycle=canonical_cycle(original['removed'],original['added'])
        moves.append(dict(root_group=original['root_group'],matching_class='cross',
                          removed=original['removed'],added=original['added'],cycle_size=original['cycle_size'],
                          alternating_cycle=cycle,changed_edges=original['cycle_size'],alternating_cycles=[cycle],
                          original_native_index=i,source_alternating_cycle=original['alternating_cycle']))
        candidates.append(native['overlap_candidates'][i])
    counts=[row for row in family['by_class'] if row['matching_class']=='cross']
    require(len(counts)==14 and sum(row['raw_cycles'] for row in counts)==23870 and
            sum(row['legal_cycles'] for row in counts)==len(indices),'Cross partition counts differ')
    result=dict(status='COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION',selector='cross_3_4',cycle_sizes=[3,4],
                candidate_path=path_key(args.candidate),candidate_sha256=digest(args.candidate),
                source_native_path=path_key(args.native),source_native_sha256=digest(args.native),
                source_family_audit_path=path_key(args.family_audit),source_family_audit_sha256=digest(args.family_audit),
                original_native_indices=indices,overlap_candidates=candidates,moves=moves,
                raw_cycles=23870,unchanged_count=0,legal_count=len(indices),
                support_rejected_count=sum(row['support_rejected'] for row in counts),
                cap_rejected_count=sum(row['cap_rejected'] for row in counts),by_class=counts,inputs_sha256=inputs,
                scope='Complete cross-class single alternating3/4-cycle replacements at this one labeled baseK; seven cross coordinates, one changed at a time, other20 fixed. Full99 final legality and completeness inherited from the bound independent atomic-both proof. No intermediate legality, pairAC, CP/LP evaluation, whole-cross matching enumeration, multi-coordinate coverage, exclusion or completion claim.')
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n')
    print(json.dumps({name:result[name] for name in ('status','raw_cycles','legal_count','support_rejected_count','cap_rejected_count')}))


if __name__=='__main__':
    main()
