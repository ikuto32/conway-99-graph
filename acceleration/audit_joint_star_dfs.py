"""Independent provenance, root-AC identity, and optional full99 witness audit.

Never treats native exhaustive DFS as a proof: no branch tree is replayed.
An AC comparison reuses the exact already-audited deletion closure by hash.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def require(ok,message):
    if not ok: raise ValueError(message)


def path(name):
    p=Path(str(name).replace('\\','/'))
    return p.resolve() if p.is_absolute() else (ROOT/p).resolve()


def key(name):
    p=path(name)
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()


def digest(name): return sha256(path(name).read_bytes()).hexdigest()


def audit(directory):
    mp,rp=directory/'manifest.json',directory/'result.json'
    manifest,result=(json.loads(p.read_bytes()) for p in (mp,rp))
    require(manifest['status']=='JOINT_STAR_DFS_RUN_MANIFEST' and result['status']=='JOINT_STAR_DFS_RUN_FINISHED','Incomplete run')
    require(key(result['manifest_path'])==key(mp) and result['manifest_sha256']==digest(mp),'Different run manifest')
    require(key(result['native_path'])==key(manifest['native_output_path']) and result['native_sha256']==digest(result['native_path']),'Different native result')
    bindings={key(n):v for n,v in manifest['inputs_sha256'].items()}
    require(all(digest(n)==v for n,v in bindings.items()),'Changed run input/source')
    require(result['inputs_sha256']==manifest['inputs_sha256'],'Run report inputs differ')
    candidate,stars,pairs,proof=[json.loads(path(manifest[k]).read_bytes()) for k in ('candidate_path','domains_path','pair_certificate_path','pair_audit_path')]
    require(proof['status']=='INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and proof['complete_used_domains_verified'] is True and
            proof['propagation_status']=='ARC_CONSISTENT_NONEMPTY' and sorted(r['outer_vertex'] for r in proof['independently_reenumerated_domains'])==list(range(84)),
            'Prior complete pair audit not available')
    prior={key(n):v for n,v in proof['inputs_sha256'].items()}
    for field in ('domains_path','pair_certificate_path','audited_candidate_path'):
        require(prior.get(key(manifest[field]))==digest(manifest[field]),'Prior audit not bound to supplied data')
    require(all(digest(n)==v for n,v in prior.items()),'Changed prior evidence')
    original=json.loads(path(manifest['audited_candidate_path']).read_bytes())
    sig=lambda data:sorted(map(tuple,data['overlap_edges_outer_zero_based']))
    require(sig(candidate)==sig(original),'Changed fixed labeled K')
    all_masks=[[int(m,16) for m in row['domain_masks_hex']] for row in stars['domains']]
    require(len(all_masks)==84 and [r['outer_vertex'] for r in stars['domains']]==list(range(84)),'Wrong source domain order')
    orig_ids=manifest['original_domain_ids']
    expected=[list(range(len(row))) for row in all_masks] if manifest['domain_source']=='all' else pairs['surviving_domain_ids']
    require(manifest['domain_source'] in ('all','survivors') and orig_ids==expected,'Unjustified domain restriction')
    masks=[[all_masks[u][i] for i in ids] for u,ids in enumerate(orig_ids)]
    input_tokens=path(manifest['native_input_path']).read_text(encoding='ascii').split()
    require(input_tokens[:2]==['C99OVERLAPS1','1'] and list(map(int,input_tokens[2:]))==[v for e in sig(candidate) for v in e],'Native candidate input differs')
    domain_tokens=iter(path(manifest['native_domains_path']).read_text(encoding='ascii').split())
    require(next(domain_tokens)== 'C99DOMAINS1' and next(domain_tokens)=='84','Native domain header differs')
    for row in masks:
        count=int(next(domain_tokens));require(count==len(row),'Native domain count differs')
        require([int(next(domain_tokens),16) for _ in range(count)]==row,'Native domain mask differs')
    require(next(domain_tokens,None) is None,'Native domain trailing data')
    native=json.loads(path(result['native_path']).read_bytes())
    require(native['status']==result['native_status'] and native['mode']==manifest['mode']==result['mode'],'Native/result scope differs')
    status=native['status']; require(status in ('SAT_NATIVE_VERIFIED_WITNESS','UNSAT_CLAIM_UNVERIFIED','UNKNOWN','AC_NONEMPTY_NO_SEARCH'),'Unexpected native status')
    root=native['root_ac'];root_reused=False
    if root['propagation_status']=='ARC_CONSISTENT_NONEMPTY':
        lifted=[[orig_ids[u][i] for i in ids] for u,ids in enumerate(root['surviving_domain_ids'])]
        require(lifted==pairs['surviving_domain_ids'],'Root AC differs from independently audited closure')
        root_reused=True
    else:
        require(root['propagation_status']=='INCOMPLETE' and status=='UNKNOWN','Prior nonempty closure cannot become empty for identical domains')
    if manifest['mode']=='ac':require(native['nodes']==native['branches']==0 and status in ('AC_NONEMPTY_NO_SEARCH','UNKNOWN'),'AC mode branched')
    witness=False
    if status=='SAT_NATIVE_VERIFIED_WITNESS':
        selected=native['selected_domain_ids'];require(type(selected) is list and len(selected)==84,'Wrong assignment length')
        labels=[(a,b) for a,b in combinations(range(14),2) if a//2!=b//2]
        labels.sort(key=lambda p:(p[0]//2,p[1]//2,p))
        edges={(0,s) for s in range(1,15)}|{(s,s+1) for s in range(1,15,2)}
        edges|={(s+1,u+15) for u,lab in enumerate(labels) for s in lab}
        edges|={(u+15,v+15) for u,v in sig(candidate)}
        directed=[]
        for u,identifier in enumerate(selected):
            require(type(identifier) is int and identifier in root['surviving_domain_ids'][u],'Selected ID outside root domain')
            mask=masks[u][identifier];require(mask.bit_count()==8 and mask>>84==0,'Invalid selected star')
            directed.append({v for v in range(84) if mask>>v&1})
        for u,row in enumerate(directed):
            for v in row:
                require(u in directed[v] and not ({s//2 for s in labels[u]}&{s//2 for s in labels[v]}),'Asymmetric/non-disjoint selected edge')
                edges.add(tuple(sorted((u+15,v+15))))
        adj=[set() for _ in range(99)]
        for u,v in edges:require(0<=u<v<99,'Invalid witness edge');adj[u].add(v);adj[v].add(u)
        require(len(edges)==693 and all(len(row)==14 for row in adj),'Full witness size/degrees fail')
        require(all(len(adj[u]&adj[v])==(1 if v in adj[u] else 2) for u,v in combinations(range(99),2)),'Full witness common-neighbor condition fails')
        require(native['edges_one_based']==[list((u+1,v+1)) for u,v in sorted(edges)],'Native edge witness differs')
        witness=True
    else:require(native['selected_domain_ids'] is None and native['edges_one_based'] is None,'Nonsatisfiable status carries witness')
    if status=='UNKNOWN':require(native['cap_reason'] in ('TIME_CAP','NODE_CAP','DOMAIN_PAIR_CAP','RELATION_MEMORY_CAP'),'Unknown lacks valid cap')
    else:require(native['cap_reason'] is None,'Uncapped status has cap')
    require(native['independent_exclusion_proved'] is False and result['independent_exclusion_proved'] is False,'Native UNSAT promoted to proof')
    bindings.update(prior)
    bindings.update({key(p):digest(p) for p in (mp,rp,result['native_path'],Path(__file__))})
    return dict(status='INDEPENDENT_JOINT_STAR_RESULT_SCOPE_AUDIT_PASS',native_status=status,
        inputs_sha256=bindings,independently_audited_root_closure_reused=root_reused,
        independent_full99_witness_verified=witness,witness_pairs_checked=4851 if witness else 0,
        branch_tree_replayed=False,independent_exclusion_proved=False,goal_marked_complete=False,
        scope='Provenance and exact audited root closure identity, plus direct full99 witness verification if SAT. Exhaustive native failure is not an independently verified exclusion.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();require(not args.out.exists(),'Fresh audit path required')
    result=audit(args.directory)
    with args.out.open('x',encoding='utf-8') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='inputs_sha256'}))


if __name__=='__main__':main()
