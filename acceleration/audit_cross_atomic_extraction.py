"""Independently check exact cross-subset extraction and canonical edge colors."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from math import comb,factorial
from pathlib import Path
import time

from audit_certificate import full_graph
from audit_atomic_trace import atomic_move

ROOT=Path(__file__).resolve().parents[1]


def require(ok,message):
    if not ok:
        raise ValueError(message)


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def resolve(name):
    path=Path(str(name).replace('\\','/'))
    return path if path.is_absolute() else ROOT/path


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load_reference(candidate_path,native_path,family_path):
    family=json.loads(family_path.read_bytes())
    require(family['status']=='INDEPENDENT_COMPLETE_ATOMIC_CYCLE_FAMILY_PASS' and family['cycle_size']=='both', 'Incomplete full-family proof')
    bindings={key(resolve(name)):expected for name,expected in family['inputs_sha256'].items()}
    require(bindings.get(key(candidate_path))==digest(candidate_path),'Unbound proof base')
    require(bindings.get(key(native_path))==digest(native_path),'Unbound original native batch')
    require(all(digest(resolve(name))==expected for name,expected in bindings.items()),'Full-family proof dependency changed')
    candidate=json.loads(candidate_path.read_bytes());native=json.loads(native_path.read_bytes())
    require(native['status']=='COMPLETE_ATOMIC_CYCLE_SUBFAMILY_ENUMERATION' and native['cycle_size']=='both','Wrong native scope')
    require(len(native['moves'])==len(native['overlap_candidates'])==family['legal_cycles'],'Wrong source family length')
    adjacency,_=full_graph(candidate)
    bindings[key(family_path)]=digest(family_path)
    return dict(candidate=candidate,native=native,family=family,adjacency=adjacency,bindings=bindings,
                candidate_path=key(candidate_path),native_path=key(native_path),family_path=key(family_path))


def audit_extraction(reference,adapted):
    require(adapted['status']=='COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION' and adapted['selector']=='cross_3_4'
            and adapted['cycle_sizes']==[3,4],'Wrong cross extraction scope')
    for pathfield,hashfield,refkey in [('candidate_path','candidate_sha256','candidate_path'),
            ('source_native_path','source_native_sha256','native_path'),
            ('source_family_audit_path','source_family_audit_sha256','family_path')]:
        expected_path=reference[refkey]
        require(key(resolve(adapted[pathfield]))==expected_path and adapted[hashfield]==reference['bindings'][expected_path],
                'Extraction provenance mismatch: '+pathfield)
    declared={key(resolve(name)):expected for name,expected in adapted['inputs_sha256'].items()}
    require(all(declared.get(name)==expected for name,expected in reference['bindings'].items()),'Extraction input map differs')
    require(all(digest(resolve(name))==expected for name,expected in declared.items()),'Extraction declared hash changed')
    native=reference['native'];family=reference['family']
    expected_indices=[i for i,move in enumerate(native['moves']) if move['matching_class']=='cross']
    require(adapted['original_native_indices']==expected_indices,'Missing/reordered/extra cross native indices')
    require(len(adapted['moves'])==len(adapted['overlap_candidates'])==len(expected_indices),'Misaligned extraction')
    known=set(map(tuple,reference['candidate']['overlap_edges_outer_zero_based']))
    signatures=set();by_class=Counter();shapes=Counter()
    for i,move,edges in zip(expected_indices,adapted['moves'],adapted['overlap_candidates']):
        original=native['moves'][i]
        require(move['original_native_index']==i and move['source_alternating_cycle']==original['alternating_cycle'], 'Lost original native association')
        for field in ('root_group','matching_class','removed','added','cycle_size'):
            require(move[field]==original[field],'Modified original move field: '+field)
        require(move['matching_class']=='cross' and move['changed_edges']==move['cycle_size'] in (3,4),'Invalid cross size/class')
        cycle=move['alternating_cycle']
        require(move['alternating_cycles']==[cycle] and cycle[0]==min(cycle),'Noncanonical single cycle')
        # The frozen independent atomic checker validates real root signs,
        # removed/added colors, exactly one connected cycle, and net graph.
        final=atomic_move(known,move,reference['adjacency'])
        require(edges==native['overlap_candidates'][i] and edges==[list(e) for e in sorted(final)],'Different selected final graph')
        sig=tuple(sorted(final))
        require(sig not in signatures and final!=known,'Duplicate or unchanged final')
        signatures.add(sig);by_class[(move['root_group'],move['cycle_size'])]+=1;shapes[move['cycle_size']]+=1
    counts=[row for row in family['by_class'] if row['matching_class']=='cross']
    require(adapted['by_class']==counts and len(counts)==14,'Cross class counts differ')
    for row in counts:
        g,k=row['root_group'],row['cycle_size']
        require(row['raw_cycles']==comb(12,k)*factorial(k-1) and row['legal_cycles']==by_class[(g,k)],'Cross raw/legal formula mismatch')
    expected=dict(raw_cycles=7*sum(comb(12,k)*factorial(k-1) for k in (3,4)),unchanged_count=0,
                  legal_count=len(expected_indices),support_rejected_count=sum(row['support_rejected'] for row in counts),
                  cap_rejected_count=sum(row['cap_rejected'] for row in counts))
    require(all(adapted[name]==value for name,value in expected.items()),'Cross total count differs')
    require(expected['raw_cycles']==expected['legal_count']+expected['support_rejected_count']+expected['cap_rejected_count'], 'Cross count partition failed')
    return dict(status='INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS',**expected,
                per_cycle_size_legal=dict(sorted(shapes.items())),by_class=counts,
                all_original_native_indices_and_final_graphs_checked=True,
                all_cycles_min_vertex_removed_first_checked=True,
                full99_legality_source='Byte-identical finals in the independently complete original atomic-both proof',
                original_full_family_legal=family['legal_cycles'],
                original_full_family_pair_checks=family['changed_pair_constraints_checked'],
                frozen_atomic_geometry_checker='audit_atomic_trace.atomic_move',producer_imported=False,
                new_full_family_enumeration_performed=False,
                scope='Exact ordered cross-only subset of the bound complete atomic3/4 family on this baseK. All opposite-sign/root membership and canonical cycle colors checked; final full99 validity reused by exact final-edge identity. No whole-cross, pairAC, global coverage, exclusion or completion claim.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--family-audit',type=Path,required=True)
    parser.add_argument('--adapted',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();require(not args.out.exists(),'Preserve prior extraction audit')
    started=time.perf_counter()
    reference=load_reference(args.candidate,args.native,args.family_audit)
    result=audit_extraction(reference,json.loads(args.adapted.read_bytes()))
    bindings=dict(reference['bindings'])
    for path in (args.adapted,Path(__file__),ROOT/'acceleration/audit_atomic_trace.py',ROOT/'acceleration/audit_certificate.py'):
        bindings[key(path)]=digest(path)
    result.update(inputs_sha256=bindings,elapsed_seconds=time.perf_counter()-started)
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({name:result[name] for name in ('status','raw_cycles','legal_count','support_rejected_count','cap_rejected_count','per_cycle_size_legal','elapsed_seconds')}))


if __name__=='__main__':
    main()
