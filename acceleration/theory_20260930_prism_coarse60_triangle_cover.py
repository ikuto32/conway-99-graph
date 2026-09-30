"""Candidate exact coarse triple census and bounded cover witness; no SAT."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, product
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20260930_prism_coarse60_bitlift'
GATE=ROOT/'acceleration/results/20260930_independent_review/identity_p_triangle_partition/summary.json'
GATE_HASH='15a32c8e4fb4928f78a6e931e09054ddcfd90c027717e8c0d0828c6f5406a516'
MODEL_GATE=ROOT/'acceleration/results/20260930_independent_review/prism_coarse60_bitlift_cnf/summary.json'
MODEL_GATE_HASH='b82eb3d3c999ae8bdcdbfd246dd28ea9cd6a9dd8d1ce811abc82ee0f3e38d88d'

def need(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x,compact=False):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=None if compact else 2,separators=(',',':') if compact else None);f.write('\n')

def classify(fibres):
    same=[(i,j) for i,j in combinations(range(3),2) if fibres[i]==fibres[j]]
    return None if len(same)==3 else same

def exact_cover(n, triples, deadline, max_nodes):
    masks=[sum(1<<v for v in t) for t in triples];incident=[[] for _ in range(n)]
    for i,t in enumerate(triples):
        need(len(t)==3 and len(set(t))==3 and all(type(v)is int and 0<=v<n for v in t),'valid 3set')
        for v in t:incident[v].append(i)
    nodes=[]
    def visit(remaining):
        if time.monotonic()>=deadline or len(nodes)>=max_nodes:return 'UNKNOWN',None,None
        index=len(nodes);node=dict(id=index,remaining_mask_hex=format(remaining,'x'),status='PENDING');nodes.append(node)
        if remaining==0:node['status']='SAT';node['cover_triple_ids']=[];return 'SAT',[],index
        best=None;vertex=None
        for v in range(n):
            if not remaining>>v&1:continue
            choices=[i for i in incident[v] if masks[i]&remaining==masks[i]]
            if best is None or len(choices)<len(best):best=choices;vertex=v
            if not choices:break
        node.update(branch_vertex=vertex,available_triple_ids=best,children=[])
        for i in best:
            status,cover,child=visit(remaining^masks[i]);node['children'].append(dict(triple_id=i,child=child,status=status))
            if status=='SAT':node['status']='SAT';node['cover_triple_ids']=[i,*cover];return 'SAT',[i,*cover],index
            if status=='UNKNOWN':node['status']='UNKNOWN';return 'UNKNOWN',None,index
        node['status']='UNSAT';return 'UNSAT',None,index
    status,cover,root=visit((1<<n)-1)
    return dict(status=status,root_node=root,cover_triple_ids=cover,nodes=nodes,
                stopped_by_resource_limit=status=='UNKNOWN',max_nodes=max_nodes)

def check_cover(n,triples,cover):
    need(type(cover)is list and len(cover)*3==n,'cover cardinality')
    counts=Counter()
    for i in cover:
        need(type(i)is int and 0<=i<len(triples),'cover triple index')
        counts.update(triples[i])
    need(counts==Counter(range(n)),'exact disjoint coverage')

def controls():
    cases=0;allowed=0
    for fibres in product(range(3),repeat=3):
        predicted=classify(fibres)
        valid=[]
        for bits in product(range(2),repeat=3):
            disjoint=len(set(zip(fibres,bits)))==3
            expected=predicted is not None and all(bits[i]!=bits[j] for i,j in predicted)
            need(disjoint==expected,'all216component disjointness controls');cases+=1
            if disjoint:valid.append(bits)
        need(len(valid)==(0 if predicted is None else 2**(3-len(predicted))),'component local bit count')
        allowed+=predicted is not None
    fixtures=[dict(name='cover_positive',n=6,triples=[[0,1,2],[3,4,5],[0,3,4]],expected='SAT'),
              dict(name='overlap_only_negative',n=6,triples=[[0,1,2],[0,3,4],[0,4,5]],expected='UNSAT')]
    for f in fixtures:
        result=exact_cover(f['n'],f['triples'],time.monotonic()+5,1000);need(result['status']==f['expected'],'tiny cover outcome')
        brute=[list(c) for c in combinations(range(len(f['triples'])),f['n']//3)
               if sorted(v for i in c for v in f['triples'][i])==list(range(f['n']))]
        need(bool(brute)==(result['status']=='SAT'),'complete tiny cover brute force')
        if result['status']=='SAT':check_cover(f['n'],f['triples'],result['cover_triple_ids'])
        f['complete_bruteforce_covers']=brute;f['result']=result
    rejected=[]
    for wrong in [[0,0],[0],[0,999],[0,2]]:
        try:check_cover(6,fixtures[0]['triples'],wrong)
        except ValueError:rejected.append(dict(witness=wrong,rejected=True))
        else:raise AssertionError('bad cover accepted')
    # Explicit local countercontrols for each of the three fibre types.
    need(classify((0,0,0)) is None,'pigeonhole rejection')
    need(len(set(zip((0,0,1),(0,0,0))))<3,'equal required bits rejected')
    need(len(set(zip((0,0,1),(0,1,0))))==3,'opposite-bit positive')
    return dict(component_truth_cases=cases,admissible_fibre_triples=allowed,cover_fixtures=fixtures,
                corrupted_cover_witnesses=rejected,research_factor_positive=None,
                research_factor_positive_reason='No global research factor or Gram-satisfying cover-bit assignment known.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();deadline=start+120
    pins={}
    for gate,h,status in [(GATE,GATE_HASH,'INDEPENDENT_IDENTITY_P_MIXED_AND_TRIANGLE_PARTITION_PASS'),
                         (MODEL_GATE,MODEL_GATE_HASH,'INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_CNF_PASS')]:
        need(digest(gate)==h and read(gate)['status']==status,'independent premise gate')
        pins.update(read(gate)['inputs_sha256']);pins[key(gate)]=h
    for p in [Path(__file__),Path(__file__).with_name('theory_20260930_prism_coarse60_triangle_cover_spec.md'),
              ROOT/'docs/DERIVATION_20260930_COARSE60_TRIANGLE_COVER.md',BASE/'scope.json',BASE/'model.json',ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=digest(p)
    for p,h in pins.items():need(digest(ROOT/p)==h,'frozen input '+p)
    manifest=dict(created_at=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),inputs_sha256=pins,
        versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip()),
        limits=dict(wall_seconds=120,search_nodes=100000,solver_calls=0),
        scope='Coarse necessary triangle-cover test for one fixed60-column six-prism template; bit/Gram constraints ignored during cover search.')
    save(out/'manifest.json',manifest);save(out/'controls.json',controls())
    scope=read(BASE/'scope.json');model=read(BASE/'model.json');words=scope['columns60']
    variables={(r['column'],r['component']):r['variable'] for r in model['raw_bits']}
    records=[];triples=[];admissible_records=[];reject_hist=Counter();require_hist=Counter()
    for population_id,triple in enumerate(combinations(range(60),3)):
        impossible=[];requirements=[]
        for a in range(6):
            kind=classify(tuple(words[d][a] for d in triple))
            if kind is None:impossible.append(a)
            else:
                for i,j in kind:
                    d,e=triple[i],triple[j];requirements.append(dict(component=a,columns=[d,e],variables=[variables[d,a],variables[e,a]]))
        row=dict(population_id=population_id,columns=list(triple),all_same_components=impossible,
                 required_opposite_bits=requirements if not impossible else None)
        if impossible:reject_hist[len(impossible)]+=1
        else:
            row['admissible_id']=len(triples);row['local_bit_assignments']=2**(18-len(requirements))
            require_hist[len(requirements)]+=1;triples.append(list(triple));admissible_records.append(row)
        records.append(row)
    need(len(records)==34220,'complete triple population')
    save(out/'all_triples.json',dict(schema='FIXED_COARSE60_TRIANGLE_DOMAINS_V1',records=records),compact=True)
    result=exact_cover(60,triples,deadline,100000);save(out/'search_tree.json',result)
    witness=None
    if result['status']=='SAT':
        cover=result['cover_triple_ids'];check_cover(60,triples,cover)
        bits=[[0]*6 for _ in range(60)]
        for i in cover:
            for r in admissible_records[i]['required_opposite_bits']:
                d,e=r['columns'];bits[d][r['component']]=0;bits[e][r['component']]=1
        supports=[sorted(12*words[d][a]+2*a+bits[d][a] for a in range(6)) for d in range(60)]
        pair_checks=0
        for i in cover:
            for d,e in combinations(triples[i],2):
                need(not set(supports[d])&set(supports[e]),'literal disjoint cover columns');pair_checks+=1
        factor=[[int(i in support) for support in supports] for i in range(36)];gram=scope['target_gram36']
        disagreements=[(i,j) for i in range(36) for j in range(36) if sum(factor[i][d]*factor[j][d] for d in range(60))!=gram[i][j]]
        witness=dict(admissible_triple_ids=cover,triangles=[triples[i] for i in cover],bits60x6=bits,
            column_supports36=supports,literal_disjoint_column_pair_checks=pair_checks,
            full_Gram_mismatching_entries=len(disagreements),full_Gram_matches=not disagreements,
            scope='Only20trianglecover plus independently chosen local disjointness bits; not a Gram factor.',
            factor_validation='NOT_ATTEMPTED_AS_RESEARCH_FACTOR',target_graph=False,residual_degree8_graph=None)
        save(out/'coarse_cover_witness.json',witness)
    packages=[]
    for p in [out/'all_triples.json',out/'search_tree.json']:
        compressed=gzip.compress(p.read_bytes(),mtime=0);target=p.with_suffix(p.suffix+'.gz');target.write_bytes(compressed)
        need(gzip.decompress(compressed)==p.read_bytes(),'package identity')
        packages.append(dict(raw_path=key(p),raw_sha256=digest(p),raw_bytes=p.stat().st_size,
                             gzip_path=key(target),gzip_sha256=digest(target),gzip_bytes=target.stat().st_size))
    save(out/'artifact_packages.json',dict(packages=packages,mathematical_verification=False))
    need(time.monotonic()<deadline,'total120second cap');need(all(digest(ROOT/p)==h for p,h in pins.items()),'frozen input stability')
    summary=dict(status='CANDIDATE_COARSE60_TRIANGLE_COVER_'+result['status'],
        created_at=manifest['created_at'],completed_at=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],
        inputs_sha256=pins,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},
        total_column_triples=34220,admissible_triples=len(triples),rejected_triples=34220-len(triples),
        rejection_all_same_component_histogram=dict(sorted(reject_hist.items())),opposite_requirement_histogram=dict(sorted(require_hist.items())),
        cover_status=result['status'],search_nodes=len(result['nodes']),cover_size=len(result['cover_triple_ids']) if result['cover_triple_ids'] is not None else None,
        raw_bit_witness_full_Gram_disagreements=witness['full_Gram_mismatching_entries'] if witness is not None else None,
        solver_calls=0,independent_approval=False,target_resolution='UNKNOWN',wall_seconds=time.monotonic()-start,
        scope=manifest['scope'],limitations=['Coarse cover is not a full factor.','No residual D degree8 or fulltarget identity.',
        'No other coarse templates excluded.','No new triangle-selector CNF constructed.'])
    save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],admissible_triples=len(triples),nodes=len(result['nodes']),
        cover_size=summary['cover_size'],Gram_disagreements=summary['raw_bit_witness_full_Gram_disagreements'],summary_sha256=digest(out/'summary.json'),wall_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
