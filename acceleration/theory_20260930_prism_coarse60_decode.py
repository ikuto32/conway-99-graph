"""Producer-only coarse60 assignment decoder; independent object check required."""
from collections import Counter
from hashlib import file_digest
from itertools import combinations
from pathlib import Path
import argparse
import json

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_prism_coarse60_bitlift'
MODEL_SHA='a437d3f1381e9554bff2376726a991f1d1e0ea23c240f8ebacf005c57e82fcb5'
SCOPE_SHA='3237da2a02c60fc3f0c61e562788582b7ce25946afb523a84dc6634912ed98e9'


def need(ok,why):
    if not ok:raise ValueError(why)


def digest(path):
    with Path(path).open('rb')as stream:return file_digest(stream,'sha256').hexdigest()


def decode(assignment):
    need(digest(D/'model.json')==MODEL_SHA and digest(D/'scope.json')==SCOPE_SHA,'frozen bitlift model/scope')
    model=json.loads((D/'model.json').read_bytes());scope=json.loads((D/'scope.json').read_bytes())
    need(type(assignment)is list and len(assignment)==5238 and all(type(v)is int and 1<=abs(v)<=5238 for v in assignment),'literal complete signed assignment')
    need(len({abs(v)for v in assignment})==5238,'unique complete variable IDs')
    truth={abs(v):int(v>0)for v in assignment};bits=[[truth[2449+6*d+a]for a in range(6)]for d in range(60)]
    selected=[]
    for domain in model['domains']:
        choices=[j for j,v in enumerate(domain['selectors'])if truth[v]];need(len(choices)==1,'exactly one domain selected')
        j=choices[0];selected.append(domain['selectors'][j]);a=domain['component'];mask=domain['local_masks'][j]
        need(all(bits[d][a]==((mask>>i)&1)for i,d in enumerate(domain['column_positions'])),'all selected mask channels')
    factor=[[0]*60 for _ in range(36)]
    for d,word in enumerate(scope['columns60']):
        for a,g in enumerate(word):factor[12*g+2*a+bits[d][a]][d]=1
    gram=[[sum(x*y for x,y in zip(r,s))for s in factor]for r in factor]
    need(gram==scope['target_gram36'],'all1296prescribed Gram entries')
    need(all(sum(row)==10 for row in factor),'row margins')
    need(all(sum(factor[r][d]for r in range(12*g,12*g+12))==2 for d in range(60)for g in range(3)),'all180fibre margins')
    overlaps=[sum(factor[r][d]*factor[r][e]for r in range(36))for d,e in combinations(range(60),2)]
    need(max(overlaps)<=2,'all1770outside column caps')
    pairs=[tuple(r for r in range(12)if factor[r][d])for d in range(60)]
    canonical=list(combinations(range(12),2));canonical=[p for p in canonical if p[0]//2!=p[1]//2]
    need(sorted(pairs)==canonical and len(set(pairs))==60,'C0nonmatching pair bijection')
    order=[pairs.index(p)for p in canonical];canon=[[row[d]for d in order]for row in factor]
    inverse=[order.index(d)for d in range(60)]
    need([[row[d]for d in inverse]for row in canon]==factor,'explicit canonicalization roundtrip')
    return dict(status='CANDIDATE_FIXED_COARSE60_FACTOR_PENDING_INDEPENDENT_REVIEW',factor=factor,bits60x6=bits,
        selected_domain_selector_ids=selected,canonical_factor=canon,canonical_column_order=order,
        canonical_C0_columns=[list(p)for p in canonical],core_adjacency=[row[3:]for row in scope['core_adjacency39'][3:]],
        target_gram=gram,coarse_columns60=scope['columns60'],encoding_model_sha256=MODEL_SHA,encoding_scope_sha256=SCOPE_SHA,
        producer_exact_checks=dict(Gram_entries=1296,domain_masks=18,channel_bits=360,column_caps=1770,
            overlap_histogram={str(k):v for k,v in sorted(Counter(overlaps).items())}),
        target_graph=False,independent_approval=False,residual_D=None,residual_D_null_reason='No residual adjacency encoded or constructed.')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--assignment',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    result=decode(json.loads(args.assignment.read_bytes())['assignment'])
    with args.out.open('x',encoding='utf-8',newline='\n')as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=result['status'],output_sha256=digest(args.out))))
