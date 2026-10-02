"""Independent historical Wave147 coefficient audit using adjacency sets.

No discovery/checker modules are imported. Ordered root pairs and unordered
free triples are counted directly. Approval of any new endpoint claim is left
to its separate reviewer; this checks only the archived coefficient layer.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from itertools import combinations, permutations, product
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'external_conway99_research'
COEFFICIENT=ARCHIVE/'attempts/wave147-alternative-lane/coefficients.json.gz'
BASIS=ARCHIVE/'attempts/wave147-alternative-lane/exact-results.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,item):
    with path.open('x',encoding='utf8',newline='\n') as stream:
        json.dump(item,stream,indent=2);stream.write('\n')


def graph(n,mask):
    adjacency=[set() for _ in range(n)]
    for i,(u,v) in enumerate(combinations(range(n),2)):
        if (mask>>i)&1:
            adjacency[u].add(v);adjacency[v].add(u)
    return adjacency


def induced_mask(adjacency,vertices):
    return sum(1<<i for i,(u,v) in enumerate(combinations(vertices,2)) if v in adjacency[u])


@lru_cache(None)
def rooted_mask(mask):
    adjacency=graph(5,mask)
    return min(induced_mask(adjacency,(0,1,*p)) for p in permutations((2,3,4)))


def matrix(adjacency,adjacent,flags):
    lookup={m:i for i,m in enumerate(flags)}
    size=len(flags);result=[[0]*size for _ in range(size)]
    n=len(adjacency);overlap=8-n
    for first in range(n):
        for second in range(n):
            if first==second or ((second in adjacency[first])!=adjacent):
                continue
            remaining=set(range(n))-{first,second}
            flag_for={}
            for free in combinations(sorted(remaining),3):
                mask=rooted_mask(induced_mask(adjacency,(first,second,*free)))
                flag_for[frozenset(free)]=lookup[mask]
            for free,left in flag_for.items():
                complement=remaining-set(free)
                for selected in combinations(sorted(free),overlap):
                    other=frozenset(complement|set(selected))
                    assert len(other)==3
                    right=flag_for[other]
                    result[left][right]+=1
    assert result==[list(x) for x in zip(*result)]
    return result


def upper(full):
    return [[i,j,full[i][j]] for i in range(len(full)) for j in range(i,len(full)) if full[i][j]]


def compare(actual,expected):
    if actual!=expected:
        raise AssertionError('A coefficient matrix differs from its complete direct root/triple reconstruction')


def canonical_mask(adjacency):
    cells=defaultdict(list)
    for u,neighbors in enumerate(adjacency):
        cells[len(neighbors)].append(u)
    ordered_cells=[cells[d] for d in sorted(cells)]
    return min(induced_mask(adjacency,tuple(u for cell in ordering for u in cell))
               for ordering in product(*(permutations(cell) for cell in ordered_cells)))


def direct_rook_moment(adjacency,adjacent,flags):
    lookup={m:i for i,m in enumerate(flags)};size=len(flags)
    result=[[0]*size for _ in range(size)];vectors=[]
    for first in range(9):
        for second in range(9):
            if first==second or ((second in adjacency[first])!=adjacent):
                continue
            counts=[0]*size
            for free in combinations(sorted(set(range(9))-{first,second}),3):
                counts[lookup[rooted_mask(induced_mask(adjacency,(first,second,*free)))]]+=1
            vectors.append(counts)
            for i,x in enumerate(counts):
                for j,y in enumerate(counts):
                    result[i][j]+=x*y
    assert len(vectors)==36
    assert all(sum(v)==35 for v in vectors)
    return result,vectors


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    packed=COEFFICIENT.read_bytes();payload=gzip.decompress(packed)
    data=json.loads(payload);basis=json.loads(BASIS.read_text())
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),
                  claim_scope='All2414 stored class coefficient matrices under exact ordered roots/unordered free triples union convention; inherited class-stream completeness is not re-enumerated.',
                  source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  checker=dict(path=str(Path(__file__).relative_to(ROOT)),sha256=digest(Path(__file__))),
                  command=[sys.executable,*sys.argv],cwd=str(ROOT),
                  archive_repository='https://github.com/YesterdaysLemon/conway-99-research',
                  archive_commit=subprocess.check_output(['git','rev-parse','HEAD:external_conway99_research'],cwd=ROOT,text=True).strip(),
                  original_claim_id='C-WAVE147-PAIR-ROOT-001',
                  inputs=[dict(path=str(f.relative_to(ROOT)),sha256=digest(f)) for f in [COEFFICIENT,BASIS]],
                  payload_sha256=hashlib.sha256(payload).hexdigest(),
                  trusted_components=['Raw archived masks/bases','Python integer arithmetic','Gzip/zlib and SHA256','tqdm displays'],
                  shared_source_code=None,shared_source_code_reason='No producer/checker code import or execution.',
                  versions=dict(python=platform.python_version()),numerical_settings=None,
                  numerical_settings_reason='All counts/matrices computed with exact Python integers.')
    write(args.out/'manifest.json',manifest)
    families=data['families'];control_results={}
    for family,adjacent in [('ordered_edge',True),('ordered_nonedge',False)]:
        flags=basis['families'][family]['flag_masks']
        assert len(flags)==families[family]['matrix_size']
        empty=matrix([set() for _ in range(5)],adjacent,flags)
        if adjacent:
            assert not any(any(row) for row in empty)
        else:
            assert empty[flags.index(0)][flags.index(0)]==20 and sum(map(sum,empty))==20
        corrupted=[row[:] for row in empty];corrupted[0][0]+=1
        try:
            compare(empty,corrupted)
        except AssertionError:
            rejected=True
        else:
            rejected=False
        assert rejected
        control_results[family]=dict(empty_order5_expected_coefficients='PASS',mutated_coefficient_rejected=True)
    write(args.out/'controls_before_full_audit.json',control_results)
    totals=[];independent_matrices={}
    for family,adjacent in [('ordered_edge',True),('ordered_nonedge',False)]:
        flags=basis['families'][family]['flag_masks']
        record_results=[];matrices={}
        for record in tqdm(families[family]['class_coefficients'],desc=family):
            n=record['order'];mask=record['canonical_mask'];adjacency=graph(n,mask)
            rebuilt=matrix(adjacency,adjacent,flags)
            entries=upper(rebuilt)
            compare(entries,record['upper_entries'])
            root_count=sum(1 for u in range(n) for v in range(n) if u!=v and ((v in adjacency[u])==adjacent))
            assert sum(map(sum,rebuilt))==root_count*math.comb(n-2,3)*math.comb(3,8-n)
            key=(n,canonical_mask(adjacency));assert key not in matrices
            matrices[key]=rebuilt
            record_results.append(dict(order=n,raw_mask=mask,degree_canonical_mask=key[1],nonzero_upper_entries=len(entries)))
        independent_matrices[family]=matrices
        write(args.out/f'{family}_record_checks.json',record_results)
        totals.append(dict(family=family,complete_records=len(record_results),nonzero_upper_entries=sum(r['nonzero_upper_entries'] for r in record_results),result='ALL_EXACT_MATCH'))
    # Non-vacuous expansion control on a known strongly regular graph.
    labels=list(product(range(3),repeat=2))
    rook=[{j for j,v in enumerate(labels) if u!=v and (u[0]==v[0] or u[1]==v[1])} for u in labels]
    assert all(len(neighbors)==4 for neighbors in rook)
    assert all(len(rook[u]&rook[v])==(1 if v in rook[u] else 2) for u,v in combinations(range(9),2))
    counts=Counter()
    for n in range(5,9):
        for subset in combinations(range(9),n):
            subgraph=[{j for j,w in enumerate(subset) if w in rook[v]} for v in subset]
            counts[n,canonical_mask(subgraph)]+=1
    rook_controls={}
    for family,adjacent in [('ordered_edge',True),('ordered_nonedge',False)]:
        flags=basis['families'][family]['flag_masks'];size=len(flags)
        direct,vectors=direct_rook_moment(rook,adjacent,flags)
        expansion=[[0]*size for _ in range(size)]
        for key,count in counts.items():
            coeff=independent_matrices[family][key]
            for i in range(size):
                for j in range(size):
                    expansion[i][j]+=count*coeff[i][j]
        compare(direct,expansion)
        assert sum(map(sum,direct))==44100
        altered=[row[:] for row in expansion];altered[-1][-1]+=1
        try:
            compare(direct,altered)
        except AssertionError:
            pass
        else:
            raise AssertionError('Corrupted expanded moment accepted')
        rook_controls[family]=dict(ordered_roots=36,free_triples_per_root=35,
                                  exact_direct_vs_class_expansion='ALL_ENTRIES_MATCH',
                                  sum_all_entries=44100,corrupt_expansion_rejected=True)
    write(args.out/'rook_controls.json',rook_controls)
    write(args.out/'summary.json',dict(status='PASS_COMPLETE_STORED_COEFFICIENTS',
                                       mathematical_scope=manifest['claim_scope'],
                                       all_records=sum(t['complete_records'] for t in totals),
                                       all_nonzero_upper_entries=sum(t['nonzero_upper_entries'] for t in totals),
                                       family_results=totals,controls=rook_controls,
                                       limitations=['Complete locally admissible class-stream enumeration is inherited, not rerun.',
                                                    'No new endpoint or target graph claim is approved by this historical dependency checker.'],
                                       elapsed_seconds=time.monotonic()-start,
                                       outputs=[dict(path=f.name,sha256=digest(f)) for f in sorted(args.out.iterdir()) if f.is_file()]))
    print(json.dumps(totals),flush=True)


if __name__=='__main__':
    main()
