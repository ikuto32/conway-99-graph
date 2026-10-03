"""Direct full-group image audit of the frozen ordered-matching-pair census.

No producer imports. Producer traverses generators on matching indices; this
checker explicitly evaluates every element of each full centralizer/stabilizer
on each proposed representative, using unordered edge sets rather than mate
array conjugation. It also checks supplied generator closures independently.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import permutations, combinations
import json
from math import factorial, prod
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20260930_triangle_matching_pair_census_v2/'
SUMMARY_SHA='b9b474b011ce93ad1d9e4dcd197d86a5e7a0d483bcfefb3b7dfe951d03032339'
DEADLINE=float('inf')
def need(ok,reason):
    if not ok:raise ValueError(reason)
def budget():need(time.monotonic()<DEADLINE,'audit120second resource limit')
def h(path):return sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def save(path,data):
    with path.open('x',encoding='utf-8',newline='\n')as f:json.dump(data,f,indent=2);f.write('\n')
def is_perm(p,n):return len(p)==n and all(type(x)is int for x in p)and sorted(p)==list(range(n))
def edges(m,n):
    need(is_perm(m,n),'matching mate permutation')
    need(all(m[i]!=i and m[m[i]]==i for i in range(n)),'matching involution without fixed points')
    return frozenset((i,m[i])for i in range(n)if i<m[i])
def image(e,p):
    return frozenset((min(p[x],p[y]),max(p[x],p[y]))for x,y in e)
def full_group(n):
    # An arbitrary permutation preserving the standard matching chooses an
    # ordered list of destination pairs, then one of two orientations per pair.
    group=[]
    for destinations in permutations(range(n//2)):
        for mask in range(1<<(n//2)):
            mapped=[]
            for i,j in enumerate(destinations):
                a=2*j+((mask>>i)&1);mapped.extend((a,a^1))
            group.append(tuple(mapped))
    standard=frozenset((i,i+1)for i in range(0,n,2))
    need(len(group)==len(set(group))==(1<<(n//2))*factorial(n//2),'full centralizer cardinality')
    need(all(is_perm(p,n)and image(standard,p)==standard for p in group),'full centralizer preservation')
    return group
def generated_group(generators,n,target):
    need(all(is_perm(g,n)for g in generators),'valid generators')
    target=set(target);identity=tuple(range(n));seen={identity};pending=[identity]
    need(all(tuple(g)in target for g in generators),'generator preserves named matching data')
    while pending:
        p=pending.pop()
        for g in generators:
            q=tuple(p[g[i]]for i in range(n))
            need(q in target,'generator closure within expected full stabilizer')
            if q not in seen:seen.add(q);pending.append(q)
        if len(seen)%1024==0:budget()
    need(seen==target,'generators span full actual stabilizer')
    return len(seen)
def partition_type(a,b,n):
    adjacency=[set()for _ in range(n)]
    for x,y in a|b:adjacency[x].add(y);adjacency[y].add(x)
    unseen=set(range(n));types=[]
    while unseen:
        component={min(unseen)}
        while True:
            more=component|set().union(*(adjacency[x]for x in component))
            if more==component:break
            component=more
        unseen-=component;types.append(len(component)//2)
    return sorted(types)
def member_set(raw,N):
    need(isinstance(raw,list)and all(type(x)is int and 0<=x<N for x in raw),'valid member IDs')
    need(len(raw)==len(set(raw))and raw==sorted(raw),'unique sorted member IDs')
    return set(raw)

def audit(data,stages,items,out=None):
    n=data['n'];N=prod(range(1,n,2));need(n%2==0,'even n')
    need(len(items)==N,'all matching count (n-1)!!')
    edge_items=[edges(m,n)for m in items]
    need(len(set(edge_items))==N,'matching uniqueness gives complete universe')
    need(items==sorted(items),'canonical indexed ordering')
    lookup={m:i for i,m in enumerate(edge_items)}
    m0=edges(data['M0'],n);need(m0==frozenset((i,i+1)for i in range(0,n,2)),'standard M0')
    full=full_group(n);need(data['group_order']==len(full),'recorded group order')
    generated_group(data['generators'],n,full)
    first_used=set();hist=Counter();records=[];image_evaluations=0;second_members=0
    for stage_id,s in enumerate(stages):
        budget();rep=s['first_representative_index'];need(type(rep)is int and 0<=rep<N,'M1 representative index')
        need(s['M1']==items[rep],'M1 raw representative')
        M1=edge_items[rep];declared=member_set(s['first_members'],N)
        need(rep==min(declared),'first canonical representative')
        actual={lookup[image(M1,p)]for p in full};image_evaluations+=len(full)
        need(actual==declared,'first orbit full direct images')
        need(not first_used&actual,'first orbit disjointness');first_used|=actual
        need(s['first_orbit_size']==len(actual),'first orbit size')
        stabilizer=[p for p in full if image(M1,p)==M1]
        need(s['stabilizer_order']==len(stabilizer),'actual M0,M1 stabilizer')
        need(len(actual)*len(stabilizer)==len(full),'first orbit stabilizer identity')
        need(partition_type(m0,M1,n)==s['M0_M1_alternating_partition'],'alternating component type')
        generated_group(s['stabilizer_generators'],n,stabilizer)
        used=set();counts=Counter();orbit_records=[]
        for r in s['second_orbits']:
            idx=r['representative_index'];need(type(idx)is int and 0<=idx<N,'M2 representative index')
            need(r['representative']==items[idx],'M2 raw representative')
            M2=edge_items[idx];declared=member_set(r['members'],N)
            need(idx==min(declared),'second canonical representative')
            actual=set();joint=0
            for p in stabilizer:
                transformed=image(M2,p);actual.add(lookup[transformed]);joint+=transformed==M2
            image_evaluations+=len(stabilizer)
            need(actual==declared,'second orbit full direct images')
            need(not used&actual,'second orbit disjointness');used|=actual
            need(r['orbit_size']==len(actual),'second orbit size')
            need(r['joint_stabilizer_order']==joint,'explicit joint stabilizer cardinality')
            need(joint*len(actual)==len(stabilizer),'second orbit stabilizer identity')
            counts[str(joint)]+=1
            orbit_records.append(dict(representative_index=idx,orbit_size=len(actual),joint_stabilizer_order=joint))
        need(used==set(range(N)),'second complete partition')
        need(s['second_covered_matchings']==len(used),'second covered count')
        need(s['second_orbit_count']==len(orbit_records),'second orbit count')
        second_members+=len(used);hist.update(counts)
        record=dict(stage=stage_id,first_orbit_size=len(s['first_members']),
                    first_representative_index=rep,stabilizer_order=len(stabilizer),
                    alternating_partition=partition_type(m0,M1,n),second_orbits=len(orbit_records),
                    second_population=len(used),joint_stabilizer_histogram=dict(counts),orbits=orbit_records)
        records.append(record)
        if out is not None:
            save(out/f'checked_stage_{stage_id:02d}.json',record)
            print(json.dumps({k:v for k,v in record.items()if k not in ['orbits','joint_stabilizer_histogram']}),flush=True)
    need(first_used==set(range(N)),'first complete partition')
    orbit_count=sum(len(s['second_orbits'])for s in stages)
    weighted=sum(s['first_orbit_size']*N for s in stages)
    need(data['first_orbit_count']==len(stages),'first total')
    need(data['ordered_pair_orbit_count']==orbit_count,'ordered pair total')
    need(data['labelled_ordered_pairs']==weighted==N*N,'weighted disjoint pair coverage')
    need(data['unclassified_labelled_triples']==weighted*factorial(n),'unclassified P product count')
    need(data['joint_stabilizer_order_histogram']==dict(hist),'complete joint stabilizer histogram')
    return dict(n=n,matchings=N,centralizer_order=len(full),first_orbits=len(stages),ordered_pair_orbits=orbit_count,
                labelled_ordered_pairs=weighted,unclassified_labelled_triples=weighted*factorial(n),
                explicit_group_image_evaluations=image_evaluations,second_stage_matching_members=second_members,
                trivial_joint_stabilizer_orbits=hist['1'],joint_stabilizer_order_histogram=dict(hist))

def controls(raw):
    results=[]
    for case in raw['positive']:
        results.append(audit(case,case['stages'],case['matchings']))
    tiny=raw['positive'][0];need(tiny['n']==4,'n4 control')
    need(results[0]['ordered_pair_orbits']==5,'independently known n4 five ordered pair orbits')
    # Literal matrix relabeling validates image direction, independently of edge-set action.
    actions=0
    for m in tiny['matchings']:
        e=edges(m,4);a=[[int((min(x,y),max(x,y))in e)if x!=y else 0 for y in range(4)]for x in range(4)]
        for p in full_group(4):
            b=[[0]*4 for _ in range(4)]
            for x in range(4):
                for y in range(4):b[p[x]][p[y]]=a[x][y]
            need(frozenset((x,y)for x,y in combinations(range(4),2)if b[x][y])==image(e,p),'literal matrix action')
            actions+=1
    variants={}
    bad=deepcopy(tiny);bad['matchings'].pop();variants['missing_matching']=bad
    bad=deepcopy(tiny);bad['matchings'][1]=bad['matchings'][0];variants['duplicate_matching']=bad
    bad=deepcopy(tiny);bad['matchings'][0]=[0,1,2,3];variants['fixed_point_not_matching']=bad
    bad=deepcopy(tiny);bad['generators'][0][0]=bad['generators'][0][1];variants['duplicate_generator_image']=bad
    bad=deepcopy(tiny);bad['generators']=[];variants['generators_not_spanning']=bad
    bad=deepcopy(tiny);bad['stages'][0]['first_members'].append(bad['stages'][1]['first_members'][0]);variants['mixed_first_orbits']=bad
    bad=deepcopy(tiny);bad['stages'][0]['second_orbits'][1]['members'].pop();variants['missing_second_member']=bad
    bad=deepcopy(tiny);bad['stages'][0]['second_orbits'][0]['joint_stabilizer_order']+=1;variants['wrong_joint_stabilizer']=bad
    bad=deepcopy(tiny);bad['stages'][1]['stabilizer_generators']=bad['generators'];variants['wrong_full_group_on_second_stage']=bad
    bad=deepcopy(tiny);bad['stages'][0]['M0_M1_alternating_partition']=[2];variants['wrong_alternating_type']=bad
    bad=deepcopy(tiny);bad['labelled_ordered_pairs']-=1;variants['wrong_pair_total']=bad
    rejected=[]
    for name,bad in variants.items():
        try:audit(bad,bad['stages'],bad['matchings'])
        except (ValueError,IndexError):rejected.append(name)
        else:raise ValueError('corruption accepted '+name)
    return dict(status='DIRECT_IMAGE_CENSUS_CONTROLS_PASS',positive=results,literal_matrix_action_cases=actions,
                corruptions_rejected=rejected,shared_with_producer='Only serialized controls and standard-library mathematics; no producer imports.')

def main():
    global DEADLINE
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False);start=time.monotonic();DEADLINE=start+120
    inputs={}
    def bind(path,expected=None):
        actual=h(ROOT/path);need(expected is None or actual==expected,'input hash '+path);inputs[path]=actual
    bind(BASE+'summary.json',SUMMARY_SHA);data=read(BASE+'summary.json')
    for path,expected in data['output_hashes'].items():bind(path,expected)
    manifest=read(BASE+'manifest.json')
    for path,expected in manifest['input_hashes'].items():bind(path,expected)
    stages=[read(BASE+f'stage_{i:02d}.json')for i in range(11)];items=read(BASE+'matchings.json')
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=dict(inputs),
         question='Does each emitted partition equal the full direct group-image orbit, with complete disjoint coverage and exact stabilizers?',
         success='All finite image sets, subgroup closures, representatives, sizes and weighted population identities agree exactly.',
         limits=dict(seconds=120,partial_result_promotion=False),numerical_thresholds=None,numerical_thresholds_null_reason='Exact finite sets and integers.'))
    calibrated=controls(read(BASE+'controls.json'));save(out/'controls.json',calibrated)
    counts=audit(data,stages,items,out)
    need((counts['first_orbits'],counts['ordered_pair_orbits'],counts['trivial_joint_stabilizer_orbits'])==(11,3580,1701),'frozen material counts')
    for path,expected in list(inputs.items()):bind(path,expected)
    for path in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_TRIANGLE_MATCHING_PAIR_CENSUS.md']:bind(path)
    result=dict(status='INDEPENDENT_TRIANGLE_ORDERED_MATCHING_PAIR_CENSUS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),
        python=platform.python_version(),verifier='/root/state_literature_audit independent direct-image checking agent',
        claim_id='C-TRIANGLE-ORDERED-MATCHING-PAIR-CENSUS',claim_revision=1,recommendation='VERIFIED',kind='mathematical result',basis=['DERIVED','COMPUTED'],
        statement='Fix M0=(01)(23)(45)(67)(89)(10 11) on twelve labelled points. The centralizer H of M0 in S12 has exactly3580 simultaneous-conjugation orbits on ordered pairs(M1,M2) of arbitrary perfect matchings. The saved eleven first-stage and3580 second-stage orbit partitions cover all108056025 labelled ordered pairs; exactly1701 pair orbits have trivial joint stabilizer in H.',
        scope='Finite ordered-pair action on twelve labelled points only. No fibre interchange, no constraint on or classification of the additional A1--A2 bijection P, no target graph or family exclusion.',
        dependencies=[],dependencies_reason='Self-contained finite matching/permutation theorem, without using target normalization or target existence as a premise.',
        checking_method='Every perfect matching is validated; count and uniqueness establish complete matching universe. Every full centralizer element is explicitly generated and checked. Every proposed orbit is compared to all direct group images, every joint stabilizer counted directly, every supplied generator closure checked.',
        independence='No producer imports. Producer uses generator-BFS on mate arrays; audit uses full direct images of unordered edge sets plus a separate matrix-action calibration.',
        inputs_sha256=inputs,counts=counts,controls=calibrated,
        artifact_availability='LOCAL_ONLY',artifact_availability_reason='All finite partitions, checker and receipts are local; parent controls publication.',
        target_resolution=False,external_review=False,elapsed_seconds=time.monotonic()-start,
        limitations=['No nontrivial target automorphism is assumed; H relabels hypothetical objects rather than acting as a presumed automorphism of one graph.',
                     'The remaining bijection P is wholly unclassified, so3580 is not a count of triangle cores or target graphs.',
                     'No common-neighbor, Gram, incidence-factor, residual-graph or extension pruning has been verified by this census.',
                     'Trivial joint stabilizer of three finite matchings does not establish asymmetry of a hypothetical full target.',
                     'Overall search coverage: UNKNOWN; no validated target-wide denominator.'])
    result['audit_artifact_hashes']={p.relative_to(ROOT).as_posix():h(p)for p in sorted(out.iterdir())if p.is_file()}
    save(out/'summary.json',result);print(json.dumps({'status':result['status'],'summary_sha256':h(out/'summary.json'),'counts':counts}))

if __name__=='__main__':main()
