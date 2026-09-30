"""Independent balanced-triple domain reconstruction for one parity branch.

Enumerates six S3 coordinate permutations, rather than importing the producer's
saved triple list or classification. No SAT or factor-existence assertion.
"""
from itertools import permutations, product
from pathlib import Path
import json
import audit_20260930_hadamard_prism_ordered_cnf as support

ROOT=support.ROOT
RAW=support.RAW
RAW_SHA=support.RAW_SHA
GATE=ROOT/'acceleration/results/20260930_independent_review/hadamard_balanced_parity_sat_v2/summary.json'
GATE_SHA='d2536119ac3fa0d45c190a6562de2ccc67c3f9c9765fbfc03257e37b15097f9c'
PROJECTION=GATE.parent/'independent_projection.json'
PROJECTION_SHA='08e2a5a4d3eca4777a71bf0d39ff557cc896041c74720fb8326fee92d748db3b'
need=support.need

def parity(p):
    return sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))%2

def validate_triple(words):
    need(len(words)==3 and all(len(w)==6 and all(type(v)is int and 0<=v<3 for v in w) for w in words),'three literal six-color words')
    need(list(map(tuple,words))==sorted(set(map(tuple,words))),'distinct lexicographically ordered words')
    need(all(all(w.count(g)==2 for g in range(3)) for w in words),'two of each fibre in each word')
    need(all(sorted(w[a] for w in words)==[0,1,2] for a in range(6)),'each coordinate visits each fibre once')
    ps=[parity(tuple(w[a] for w in words)) for a in range(6)]
    return [p^ps[0] for p in ps]

def local_triples():
    # All six independently chosen coordinate bijections exhaust precisely
    # the ordered three-column arrays having coordinatewise balance.
    ps=list(permutations(range(3)))
    found=set()
    examined=0
    for coordinate_maps in product(ps,repeat=6):
        examined+=1
        words=tuple(sorted(tuple(p[r] for p in coordinate_maps) for r in range(3)))
        if all(all(w.count(g)==2 for g in range(3)) for w in words):
            found.add(words)
    need(examined==46656 and len(found)==150,'complete balanced local universe')
    return sorted(found)

def reconstruct(raw, projection):
    core,gram,L,supports,columns,groups=support.reconstruct(raw)
    patterns=projection['selected_group_parity_patterns']
    need(len(patterns)==20 and all(len(p)==6 and all(type(v)is int and v in(0,1) for v in p) and p[0]==0 for p in patterns),'literal chosen branch parity')
    triples=local_triples()
    words=sorted(tuple(x['fibres_by_sorted_coordinate'])for x in columns[0]['choices'])
    word_id={word:i for i,word in enumerate(words)}
    need(len(word_id)==90,'complete distinct single-column coloring domain')
    domains=[];sid=0;counts=[]
    for j,cols in enumerate(groups):
        coords=supports[cols[0]];options=[]
        for index,triple in enumerate(triples):
            signature=validate_triple([list(w)for w in triple])
            if signature!=patterns[j]:continue
            rows=[sorted(12*g+a for a,g in zip(coords,word,strict=True))for word in triple]
            need(all(not(set(rows[r])&set(rows[t])) for r in range(3)for t in range(r+1,3)),'within-group raw columns are disjoint')
            sid+=1
            options.append(dict(selector=sid,local_triple_index=index,word_indices=[word_id[w]for w in triple],words=[list(w)for w in triple],column_rows=rows,column_masks_hex=[format(sum(1<<v for v in row),'09x')for row in rows]))
        need(len(options)==(30 if not any(patterns[j]) else 12),'complete branch local domain size')
        domains.append(dict(group=j,columns=cols,coordinates=coords,parity=patterns[j],choices=options));counts.append(len(options))
    need(sid==312 and counts.count(30)==4 and counts.count(12)==16,'specific chosen branch has312 selectors')
    return dict(core=core,gram=gram,L=L,supports=supports,domains=domains,triples=triples,words=words,primary_selectors=sid)

def controls(data):
    from copy import deepcopy
    rejected=[]
    def reject(label,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,TypeError):rejected.append(label)
        else:raise ValueError('bad domain control accepted '+label)
    first=[list(w)for w in data['triples'][0]]
    need(len(validate_triple(first))==6,'positive literal balanced triple')
    for name in ['nonbinary_color','boolean_color','duplicate_word','wrong_quota','wrong_coordinate_balance','unsorted']:
        bad=deepcopy(first)
        if name=='nonbinary_color':bad[0][0]=3
        elif name=='boolean_color':bad[0][0]=bool(bad[0][0])
        elif name=='duplicate_word':bad[1]=bad[0][:]
        elif name=='wrong_quota':bad[0][0]=(bad[0][0]+1)%3
        elif name=='wrong_coordinate_balance':
            # Preserve each word quota while deliberately breaking balance.
            a,b=next((a,b)for a in range(6)for b in range(a+1,6)if bad[0][a]!=bad[0][b])
            bad[0][a],bad[0][b]=bad[0][b],bad[0][a];bad.sort()
        else:bad.reverse()
        reject(name,lambda bad=bad:validate_triple(bad))
    profiles={}
    for triple in data['triples']:
        p=tuple(validate_triple([list(w)for w in triple]));profiles[p]=profiles.get(p,0)+1
    need(len(profiles)==11 and profiles[(0,)*6]==30 and sorted(profiles.values())==[12]*10+[30],'independent150 local parity profile counts')
    return dict(coordinate_permutation_arrays_examined=46656,distinct_balanced_unordered_triples=150,local_parity_profiles=[dict(pattern=list(p),count=n)for p,n in sorted(profiles.items())],group_domain_counts=[len(d['choices'])for d in data['domains']],primary_selectors=data['primary_selectors'],corruptions_rejected=rejected,positive_scope='Literal local domain only; no complete research factor or SAT witness asserted.')

def authenticated_reconstruct():
    for p,h in [(RAW,RAW_SHA),(GATE,GATE_SHA),(PROJECTION,PROJECTION_SHA)]:need(support.digest(p)==h,'immutable input '+str(p))
    gate=support.read(GATE);need(gate['status']=='INDEPENDENT_HADAMARD_BALANCED_PARITY_SAT_OBJECT_PASS','actual parity object gate')
    need(gate['outputs_sha256'][support.key(PROJECTION)]==PROJECTION_SHA,'raw independently checked projection identity')
    return reconstruct(support.read(RAW),support.read(PROJECTION))
