"""Independent raw two-star witness/domain audit; no producer imports.

The producer adds edges sequentially. This checker validates whole raw graphs,
and uses a separately derived simultaneous-star delta identity for exhaustive
outside-domain checking. Standard-library integer arithmetic only.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
J='acceleration/results/20260930_joint_two_star_matching/run02/'
D='acceleration/results/20260930_two_star_outside_domains/run01/'
C='acceleration/results/20260930_two_star_coupled_domains/run01/'
S='acceleration/results/20260930_unrestricted_star_matching_redundancy/run01/records.json'
PINS={J+'summary.json':'c71109254d33f9e8e20b95fb4a83bcc426c266a7fb8589c393a3a242e86033da',
      J+'population.json':'36e03d5053644de7e154d838edf6b8152e96701d4eb59ac8f58aac740dfe7f5d'}

def require(ok,message):
    if not ok: raise ValueError(message)

def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_bytes())
def save(p,value):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
def matrix(rows):return [[int(y in r)for y in range(len(rows))]for r in rows]
def rows_from(a):
    n=len(a)
    require(all(len(r)==n for r in a),'square')
    require(all(type(x)is int and x in (0,1)for r in a for x in r),'strict binary')
    require(all(a[i][i]==0 for i in range(n)),'diagonal')
    require(all(a[i][j]==a[j][i] for i in range(n)for j in range(n)),'symmetry')
    return [{j for j,x in enumerate(r)if x}for r in a]
def add(rows,x,y):
    require(x!=y,'loop');rows[x].add(y);rows[y].add(x)
def valid(rows,k=14):
    return all(len(r)<=k for r in rows)and all(len(rows[x]&rows[y])+int(y in rows[x])<=2 for x,y in combinations(range(len(rows)),2))
def prepare_delta(rows):
    masks=[sum(1<<i for i in r)for r in rows]
    caps=[[len(a&b)+int(j in a)for j,b in enumerate(rows)]for a in rows]
    return masks,caps
def delta_ok(rows,z,added,data,k=14):
    """Exact iff all degree/common-plus-adjacency caps hold after z--added.

    Prerequisite: base rows already pass. No edge in added is present.
    For pair(z,x), common count rises by |added intersect old N(x)| and
    adjacency by 1[x in added]. For x,y != z, only the common neighbor z
    changes: increment 1 iff x,y belong to final N(z), not both old N(z).
    """
    added=set(added);masks,caps=data
    require(z not in added and not added&rows[z],'delta domain')
    if len(rows[z])+len(added)>k or any(len(rows[x])+1>k for x in added):return False
    t=sum(1<<x for x in added)
    for x in range(len(rows)):
        if x!=z and caps[z][x]+(t&masks[x]).bit_count()+int(x in added)>2:return False
    for x,y in combinations(rows[z]|added,2):
        if (x in added or y in added)and caps[x][y]+1>2:return False
    return True

def scaffolding():
    # Coordinate-pair then sign order, independently assembled without model imports.
    labels=[(2*i+a,2*j+b)for i,j in combinations(range(7),2)for a in (0,1)for b in (0,1)]
    index={t:15+i for i,t in enumerate(labels)}
    rows=[set()for _ in range(99)]
    for x in range(1,15):add(rows,0,x)
    for x in range(1,15,2):add(rows,x,x+1)
    for label,x in index.items():
        for symbol in label:add(rows,x,1+symbol)
    require(sum(map(len,rows))//2==189 and valid(rows),'root positive')
    return labels,index,rows

def witness(case,raw):
    labels,index,rows=scaffolding()
    u,v=index[(0,2)],index[(4,6)]
    require((u,v)==(15,59),'root coordinate labels')
    require(raw['case_id']==case['id']and raw['status']=='CANDIDATE_LOCAL_MATCHING_WITNESS','case identity')
    stars=[]
    for label,key,center in [((0,2),'u_star',u),((4,6),'v_star',v)]:
        star=[tuple(t)for t in case[key]]
        require(len(star)==len(set(star))==12 and label not in star,'star twelve')
        require(all(t in index for t in star),'allowed root labels')
        for s in range(14):require(sum(s in t for t in star)==2-int(s in label)-int((s^1)in label),'quota')
        for t in star:add(rows,center,index[t])
        stars.append(set(star))
    require(v in rows[u] and u in rows[v],'anchor edge')
    common=rows[u]&rows[v]
    require(len(common)==1,'unique triangle third')
    w=next(iter(common));wl=labels[w-15]
    require(not set(wl)&{0,2,4,6},'triangle root supports disjoint')
    A,B=rows[u]-{v,w},rows[v]-{u,w}
    require(len(A)==len(B)==12 and not A&B,'fibers')
    base=deepcopy(rows);fixed=[];groups=[]
    for name,kind,L,R in [('A','internal',A,A),('B','internal',B,B),('AB','cross',A,B)]:
        edges=[[x,y]for x in sorted(L)for y in sorted(R)if (kind=='cross'or x<y)and y in base[x]]
        require(all(len(base[x]&R)<=1 for x in L)and all(len(base[y]&L)<=1 for y in R),'fixed matchings')
        left=sorted(x for x in L if not base[x]&R);right=sorted(y for y in R if not base[y]&L)
        require(len(left)==len(right)==8,'residual sides')
        groups.append(dict(name=name,kind=kind,left=left,right=right));fixed.append(dict(name=name,edges=edges))
    metadata=dict(u=u,v=v,w=w,A=sorted(A),B=sorted(B),fixed_matching_edges=fixed)
    require(raw['metadata']==case['metadata']==metadata,'metadata reconstruction')
    require(raw['initial_groups']==groups,'initial group reconstruction')
    require(valid(base),'base caps')
    seen=set();chosen_counts=Counter()
    for name,x,y in raw['chosen_edges']:
        require(name in {'A','B','AB'},'chosen group')
        g=next(g for g in groups if g['name']==name)
        require(x in g['left']and y in g['right']and x!=y,'chosen endpoints')
        edge=tuple(sorted((x,y)))
        require(edge not in seen and y not in rows[x],'new edge distinct')
        seen.add(edge);chosen_counts[name]+=1;add(rows,x,y)
    require(chosen_counts=={'A':4,'B':4,'AB':8},'sixteen chosen')
    require(rows_from(raw['partial_known_edge_adjacency'])==rows,'literal graph equals reconstructed graph')
    require(valid(rows),'all99 degree and4851 pair caps')
    for L,R in [(A,A),(B,B),(A,B),(B,A)]:require(all(len(rows[x]&R)==1 for x in L),'three final perfect matchings')
    closed={u,v,w}|A|B;checked=closed|set(range(15))
    require(len(closed)==27 and len(checked)==38,'center scope counts')
    for center in [u,v]:
        require(len(rows[center])==14,'saturated center')
        for x in checked-{center}:require(len(rows[center]&rows[x])+int(x in rows[center])==2,'scoped exact center equation')
    expected=dict(all_pair_caps=4851,degree_caps=99,closed_edge_neighborhood_vertices=27,center_equalities_per_center=37)
    require(raw['checks']==expected,'claim counts')
    require(sum(map(len,rows))//2==228,'known edge count')
    return rows,metadata,dict(case=case['id'],known_edges=228,degree_caps=99,pair_caps=4851,
                            center_equations=74,centers=[u,v],center_comparison_vertices=sorted(checked))

def controls():
    # Exhaustively compare the simultaneous delta identity to literal reconstruction
    # for every cap-valid graph on five vertices, every center and every missing-edge subset.
    pairs=list(combinations(range(5),2));checked=0;bases=0;accepts=0
    for bitset in range(1<<len(pairs)):
        rows=[set()for _ in range(5)]
        for i,(x,y)in enumerate(pairs):
            if bitset>>i&1:add(rows,x,y)
        if not valid(rows,3):continue
        bases+=1;data=prepare_delta(rows)
        for z in range(5):
            missing=sorted(set(range(5))-{z}-rows[z])
            for bits in range(1<<len(missing)):
                added={x for i,x in enumerate(missing)if bits>>i&1}
                changed=deepcopy(rows)
                for x in added:add(changed,z,x)
                actual=valid(changed,3);got=delta_ok(rows,z,added,data,3)
                require(actual==got,'exhaustive delta/literal oracle disagreement')
                checked+=1;accepts+=got
    root=scaffolding()[2];require(valid(root),'root known-positive')
    k4=[set()for _ in range(4)]
    for x,y in combinations(range(4),2):add(k4,x,y)
    require(not valid(k4),'K4 cap corrupt control')
    return dict(exhaustive_five_vertex_base_graphs=bases,exhaustive_delta_cases=checked,
                delta_positive_cases=accepts,delta_negative_cases=checked-accepts,
                root_scaffold_positive=True,K4_negative=True,
                method='Complete small-graph truth table plus literal set-neighborhood reconstruction; no producer checker reused.')

def audit_domain(rows,meta,raw):
    z=raw['z'];u,v,w=(meta[k]for k in ['u','v','w'])
    require(z>=15 and z not in {u,v} and z not in rows[u]|rows[v],'outside z')
    left=sorted(x for x in meta['A']if x>=15);right=sorted(x for x in meta['B']if x>=15)
    require(len(left)==len(right)==10 and not set(left)&set(right),'outside universe sides')
    require(len(rows[z])==2,'outside base scaffold degree')
    p,q=(2-len(rows[x]&rows[z])for x in [u,v])
    require(raw['deficits']==[p,q],'deficit')
    require(raw['universe']['left']==left and raw['universe']['right']==right and raw['universe']['shared_vertex']==w,'raw domain universe')
    data=prepare_delta(rows);survivors=[];total=0;first_bad=None
    for e in [0,1]:
        if p-e<0 or q-e<0:continue
        for L in combinations(left,p-e):
            for Rr in combinations(right,q-e):
                total+=1;pat=[e,list(L),list(Rr)]
                added=set(L)|set(Rr)|({w}if e else set())
                if delta_ok(rows,z,added,data):survivors.append(pat)
                elif first_bad is None:first_bad=pat
    require(total==raw['patterns'],'complete population count')
    require(survivors==raw['surviving_patterns'],'exact full survivor list')
    require(len(survivors)==raw['survivor_count'] and total-len(survivors)==raw['rejection_count'],'partition counts')
    require(bool(survivors)and raw['status']=='NONEMPTY_LOCAL_DOMAIN','nonempty status')
    # Independent literal full99 checks of both a survivor and a rejected pattern
    # calibrate the graph-specific setup, separate from complete delta coverage.
    for pat,want in [(survivors[0],True),(first_bad,False)]:
        if pat is None:continue
        changed=deepcopy(rows)
        for x in set(pat[1])|set(pat[2])|({w}if pat[0]else set()):add(changed,z,x)
        require(valid(changed)==want,'raw99 complete calibration')
        for center in [u,v]:require(len(changed[center]&changed[z])+int(z in changed[center])==2,'pattern exact center equations')
    return dict(case=raw['case'],z=z,patterns=total,survivors=len(survivors),rejections=total-len(survivors),
                survivor_list_sha256=sha256(json.dumps(survivors,separators=(',',':')).encode()).hexdigest())

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False);start=time.monotonic();inputs={}
    def bind(path,expected=None):
        got=h(ROOT/path);require(expected is None or got==expected,'hash '+path);inputs[path]=got
    for path,expected in PINS.items():bind(path,expected)
    for directory in [J,D,C]:
        bind(directory+'summary.json');summary=load(directory+'summary.json')
        for name,expected in summary['artifact_hashes'].items():bind(directory+name,expected)
        manifest=load(directory+'manifest.json')
        for path,expected in manifest['inputs_sha256'].items():bind(path,expected)
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),
         question='Verify all32 saved raw local witnesses and all244 complete individual outside domains, without replaying coupled search.',
         criterion='Exact graph reconstruction, all known caps, scoped center equalities, and exact full surviving pattern lists.',
         inputs_sha256=dict(inputs),numerical_thresholds=None,numerical_thresholds_null_reason='Exact integer computation only.',
         resource_limit_seconds=120,checkpoints='One immutable receipt per checked case and domain; no partial population promotion.'))
    calibrated=controls();save(out/'controls.json',calibrated)
    population=load(J+'population.json');single=load(S)
    require(len(population)==32 and [c['id']for c in population]==list(range(32)),'frozen32 population')
    expected=[r for r in single if r['number']<8]
    require(len(expected)==32,'source selection count')
    for c,r in zip(population,expected):
        require((c['branch'],c['source_number'],c['u_star'])==(r['branch'],r['number'],r['star_labels']),'first8 perbranch source')
    cache={};witness_records=[]
    for case in population:
        raw=load(J+f'case_{case["id"]:02d}.json');rows,meta,record=witness(case,raw)
        record['raw_sha256']=inputs[J+f'case_{case["id"]:02d}.json']
        witness_records.append(record);cache[case['id']]=(rows,meta)
        save(out/f'witness_{case["id"]:02d}.json',record)
    require(all(load(J+'summary.json')[k]==v for k,v in [('frozen_population',32),('attempted',32),('completed',32),('local_witnesses',32),('conditional_exclusions',0),('incomplete',0)]),'joint stage counts')
    # Adversarial mutations of actual raw artifacts, not just abstract controls.
    rejected=[]
    case=population[0];good=load(J+'case_00.json')
    mutations={}
    bad=deepcopy(good);bad['partial_known_edge_adjacency'][0][0]=1;mutations['diagonal']=bad
    bad=deepcopy(good);bad['partial_known_edge_adjacency'][0][1]=2;mutations['nonbinary']=bad
    bad=deepcopy(good);bad['partial_known_edge_adjacency'][0][1]=0;mutations['asymmetric']=bad
    bad=deepcopy(good);_,x,y=bad['chosen_edges'][0];bad['partial_known_edge_adjacency'][x][y]=bad['partial_known_edge_adjacency'][y][x]=0;mutations['missing_chosen_edge']=bad
    bad=deepcopy(good);bad['chosen_edges'][0][1]=0;mutations['wrong_matching_endpoint']=bad
    bad=deepcopy(good);bad['checks']['center_equalities_per_center']=98;mutations['broadened_center_claim']=bad
    bad=deepcopy(good);bad['metadata']['w']=88;mutations['wrong_common_center']=bad
    for name,bad in mutations.items():
        try:witness(case,bad)
        except (ValueError,AssertionError):rejected.append(name)
        else:raise ValueError('accepted corrupted witness '+name)
    save(out/'actual_witness_corruptions.json',dict(rejected=rejected))
    domain_records=[];stage=[];ds=load(D+'summary.json')
    require(ds['selected_local_witnesses']==[0,8,16,24],'frozen domain case selection')
    for case_id in [0,8,16,24]:
        rows,meta=cache[case_id];u,v=meta['u'],meta['v']
        outside=sorted(set(range(15,99))-{u,v}-rows[u]-rows[v]);require(len(outside)==61,'outside61')
        for z in outside:
            require(time.monotonic()-start<120,'audit resource cap before next domain')
            path=D+f'case_{case_id:02d}_z{z:02d}.json';raw=load(path)
            require((raw['case'],raw['z'])==(case_id,z),'domain identity')
            record=audit_domain(rows,meta,raw);record['raw_sha256']=inputs[path]
            domain_records.append(record);save(out/f'domain_{case_id:02d}_{z:02d}.json',record)
        records=[r for r in domain_records if r['case']==case_id]
        item=dict(case=case_id,domains=len(records),patterns=sum(r['patterns']for r in records),survivors=sum(r['survivors']for r in records))
        stage.append(item);save(out/f'checkpoint_stage_{case_id:02d}.json',item);print(json.dumps(item),flush=True)
    require(len(domain_records)==ds['completed_domains']==244,'domain count')
    require(sum(r['patterns']for r in domain_records)==ds['patterns_enumerated']==297024,'pattern count')
    require(sum(r['survivors']for r in domain_records)==ds['surviving_patterns']==64436,'survivor count')
    require(ds['empty_domains']==0,'no empty domains')
    require({(r['case'],r['z'])for r in ds['records']}=={(r['case'],r['z'])for r in domain_records},'records coverage')
    for r,p in zip(domain_records,ds['records']):
        require((r['case'],r['z'],r['patterns'],r['survivors'],r['rejections'])==(p['case'],p['z'],p['patterns'],p['survivor_count'],p['rejection_count']),'summary per-domain')
    rows,meta=cache[0];raw=load(D+'case_00_z16.json');mutations={}
    bad=deepcopy(raw);bad['surviving_patterns'].pop();mutations['missing_survivor']=bad
    bad=deepcopy(raw);bad['surviving_patterns'].append(bad['surviving_patterns'][0]);mutations['duplicated_survivor']=bad
    bad=deepcopy(raw);bad['deficits'][0]+=1;mutations['incorrect_deficit']=bad
    bad=deepcopy(raw);bad['universe']['left'][0]=0;mutations['incorrect_universe']=bad
    bad=deepcopy(raw);bad['patterns']-=1;mutations['missing_population_member']=bad
    rejected=[]
    for name,bad in mutations.items():
        try:audit_domain(rows,meta,bad)
        except (ValueError,AssertionError):rejected.append(name)
        else:raise ValueError('accepted corrupted domain '+name)
    save(out/'actual_domain_corruptions.json',dict(rejected=rejected))
    coupled=load(C+'summary.json')
    require(coupled['status']=='UNKNOWN_RESOURCE_CAP'and coupled['conditional_exclusion_claimed']is False and coupled['checks']is None,'coupled narrow status')
    for path,expected in list(inputs.items()):bind(path,expected)
    for path in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_JOINT_TWO_STAR_DOMAINS.md']:bind(path)
    result=dict(status='INDEPENDENT_JOINT_TWO_STAR_AND_INDIVIDUAL_DOMAINS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),
        python=platform.python_version(),verifier='/root/state_literature_audit independent raw artifact checking agent',inputs_sha256=inputs,
        checking_method='No producer imports; whole99 raw graph reconstruction and cap checking; all outside-pattern subsets checked by exact simultaneous-star delta identity calibrated against literal reconstruction.',
        shared_components=['Python standard library integer, set, JSON and itertools implementations; raw artifacts and root-label convention.'],
        claims=[dict(id='C-UNRESTRICTED-TWO-STAR-32-LOCAL-WITNESSES',revision=1,recommendation='VERIFIED',kind='empirical/engineering result',basis=['COMPUTED'],
                     statement='Each of the32 frozen sampled two-star records has a228-known-edge partial99graph with all99 degrees at most14, all4851 common-plus-adjacency caps at most2, three declared perfect matching blocks, and74 exact centered equations in the declared38-vertex comparison domain.',
                     scope='Exactly32 labelled raw artifacts; zeros outside specified rows are absence from the partial known-edge graph, not forced target nonedges.',
                     dependencies=[dict(id='C-ROOT-SCAFFOLD-NORMALIZATION',revision=1,relation='normalization')]),
                dict(id='C-TWO-STAR-244-INDIVIDUAL-OUTSIDE-DOMAINS',revision=1,recommendation='VERIFIED',kind='empirical/engineering result',basis=['DERIVED','COMPUTED'],
                     statement='For each of61 outside vertices of each of four frozen local witnesses(case0,8,16,24), exhaustive individual pattern enumeration finds the exact saved nonempty domain; the244 disjoint case/vertex populations contain297024 patterns, of which64436 satisfy all known pair caps and degree caps after that single vertex addition.',
                     scope='Individual outside-vertex domains, each over its own frozen base; no simultaneous compatibility assertion.',
                     dependencies=[dict(id='C-UNRESTRICTED-TWO-STAR-32-LOCAL-WITNESSES',revision=1,relation='uses_result')])],
        counts=dict(frozen_joint_candidates=32,independently_checked_local_witnesses=32,joint_exclusions=0,
                    degree_cap_checks=32*99,pair_cap_checks=32*4851,exact_scoped_center_equations=32*74,
                    selected_domain_base_witnesses=4,completed_individual_domains=244,individual_patterns=297024,
                    individual_survivors=64436,individual_rejections=297024-64436,empty_domains=0),
        stages=stage,controls=calibrated,
        coupled_search=dict(path=C+'summary.json',sha256=inputs[C+'summary.json'],recorded_status='UNKNOWN_RESOURCE_CAP',
                            independently_replayed=False,claim_recommendation=None,
                            reason='Only saved status/provenance inspected; search nodes, pruning and completeness not verified. No exclusion follows.'),
        artifact_availability='LOCAL_ONLY',artifact_availability_reason='All raw artifacts and audit receipts are retained locally; parent controls publication.',
        target_resolution=False,external_review=False,elapsed_seconds=time.monotonic()-start,
        limitations=['No completed target graph and no family or unrestricted exclusion.',
                     'The32 sampled witnesses are not an exhaustive population of stars, matchings, or graphs.',
                     'The244 domains concern distinct individual additions to four frozen bases; they do not establish simultaneous feasibility.',
                     'Producer search-node counts, timings and random-sampling attempt counts were not independently reproduced.',
                     'No nontrivial target automorphism is assumed. Overall search coverage: UNKNOWN; no validated denominator.'])
    result['audit_artifact_hashes']={p.relative_to(ROOT).as_posix():h(p)for p in sorted(out.iterdir())if p.is_file()}
    save(out/'summary.json',result)
    print(json.dumps({'status':result['status'],'summary_sha256':h(out/'summary.json'),'counts':result['counts']}))

if __name__=='__main__':main()
