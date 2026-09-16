"""One bounded joint-star run from independently audited full pair domains.

Default input is the audited surviving subdomain; discarded values are not
forgotten, because the complete-domain/deletion audit is bound explicitly.
Native UNSAT is always an unverified claim. This wrapper never submits a graph.
"""
import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'acceleration/build/joint_star_dfs.exe'
SOURCE=ROOT/'acceleration/joint_star_dfs.rs'


def require(ok,message):
    if not ok: raise ValueError(message)


def path(name):
    p=Path(str(name).replace('\\','/'))
    return p.resolve() if p.is_absolute() else (ROOT/p).resolve()


def key(name):
    p=path(name)
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()


def digest(name): return sha256(path(name).read_bytes()).hexdigest()


def save(name,data):
    with name.open('x',encoding='utf-8') as f: f.write(json.dumps(data,indent=2,allow_nan=False)+'\n')


def prepare(args):
    require(not args.out.exists(),'Fresh output required; no resume/retry')
    require(isfinite(args.seconds) and args.seconds>0 and args.node_cap>0 and args.pair_cap>0 and 0<args.memory_mib<=65536,'Invalid limits')
    candidate,stars,pairs,audit=[json.loads(path(p).read_bytes()) for p in (args.candidate,args.domains,args.pair_certificate,args.pair_audit)]
    require(audit['status']=='INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and audit['complete_used_domains_verified'] is True and
            audit['propagation_status']=='ARC_CONSISTENT_NONEMPTY' and
            sorted(r['outer_vertex'] for r in audit['independently_reenumerated_domains'])==list(range(84)),'Complete independent nonempty pair audit required')
    bindings={key(n):v for n,v in audit['inputs_sha256'].items()}
    require(len(bindings)==len(audit['inputs_sha256']),'Duplicate normalized proof inputs')
    require(all(digest(n)==v for n,v in bindings.items()),'Changed pair audit dependency')
    require(bindings.get(key(args.domains))==digest(args.domains) and bindings.get(key(args.pair_certificate))==digest(args.pair_certificate),'Pair audit is not bound to supplied domains/certificate')
    old_candidates=[n for n in bindings if 'candidate' in Path(n).name]
    require(len(old_candidates)==1,'Ambiguous audited candidate')
    old=json.loads(path(old_candidates[0]).read_bytes())
    signature=lambda data:tuple(sorted(map(tuple,data['overlap_edges_outer_zero_based'])))
    require(signature(candidate)==signature(old),'Candidate graph differs from audited pair input')
    require(stars['complete_domain_enumeration'] is True and len(stars['domains'])==84 and
            [r['outer_vertex'] for r in stars['domains']]==list(range(84)),'Incomplete domain inventory')
    require(pairs['propagation_status']=='ARC_CONSISTENT_NONEMPTY' and len(pairs['surviving_domain_ids'])==84,'Wrong prior closure')
    masks=[[int(m,16) for m in row['domain_masks_hex']] for row in stars['domains']]
    survivors=pairs['surviving_domain_ids']
    require(all(type(ids) is list and ids and all(type(i) is int and 0<=i<len(masks[u]) for i in ids)
                and ids==sorted(set(ids)) for u,ids in enumerate(survivors)),'Invalid audited surviving IDs')
    ids=[list(range(len(row))) for row in masks] if args.domain_source=='all' else survivors
    selected=[[row[i] for i in ids[u]] for u,row in enumerate(masks)]
    require(all(row and row==sorted(set(row)) for row in selected),'Unsorted/repeated selected masks')
    files=[args.candidate,args.domains,args.pair_certificate,args.pair_audit,NATIVE,SOURCE,Path(__file__)]
    bindings.update({key(p):digest(p) for p in files})
    return candidate,selected,ids,bindings,old_candidates[0]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('candidate','domains','pair-certificate','pair-audit','out'): p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--mode',choices=('ac','search'),required=True)
    p.add_argument('--domain-source',choices=('all','survivors'),default='survivors')
    p.add_argument('--seconds',type=float,default=30)
    p.add_argument('--node-cap',type=int,default=100000)
    p.add_argument('--pair-cap',type=int,default=500000000)
    p.add_argument('--memory-mib',type=int,default=256)
    p.add_argument('--validate-only',action='store_true')
    args=p.parse_args()
    candidate,masks,ids,bindings,old_candidate=prepare(args)
    if args.validate_only:
        print(json.dumps(dict(status='JOINT_STAR_DFS_READ_ONLY_PREFLIGHT_PASS',mode=args.mode,
                              total_domains=sum(map(len,masks)),native_runs=0,output_created=False)));return
    args.out.mkdir(parents=True,exist_ok=False)
    inp,dom,native=args.out/'candidate.txt',args.out/'domains.txt',args.out/'native.json'
    with inp.open('x',encoding='ascii',newline='\n') as f:
        f.write('C99OVERLAPS1 1\n'+' '.join(str(v) for e in sorted(candidate['overlap_edges_outer_zero_based']) for v in e)+'\n')
    with dom.open('x',encoding='ascii',newline='\n') as f:
        f.write('C99DOMAINS1 84\n'+''.join(str(len(row))+' '+' '.join(hex(m) for m in row)+'\n' for row in masks))
    bindings.update({key(inp):digest(inp),key(dom):digest(dom)})
    manifest=dict(status='JOINT_STAR_DFS_RUN_MANIFEST',inputs_sha256=bindings,
        candidate_path=key(args.candidate),domains_path=key(args.domains),pair_certificate_path=key(args.pair_certificate),
        pair_audit_path=key(args.pair_audit),audited_candidate_path=old_candidate,
        native_input_path=key(inp),native_domains_path=key(dom),native_output_path=key(native),
        mode=args.mode,domain_source=args.domain_source,original_domain_ids=ids,
        caps=dict(seconds=args.seconds,nodes=args.node_cap,domain_pairs=args.pair_cap,relation_memory_mib=args.memory_mib),
        known_graph_identity_method='EXACT_LABELED_168_EDGE_SET',unsat_is_independent_proof=False,
        scope='One fixed K and independently complete domains after optional audited AC deletions. One bounded native invocation only.')
    save(args.out/'manifest.json',manifest)
    command=[str(NATIVE),str(inp),str(dom),str(native),str(args.seconds),str(args.node_cap),str(args.pair_cap),str(args.memory_mib),args.mode]
    with (args.out/'native.log').open('x',encoding='utf-8') as log:
        result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=args.seconds+30)
    require(result.returncode==0,'Native run failed; artifacts preserved')
    require(all(digest(n)==v for n,v in bindings.items()),'Bound input/source changed during run')
    outcome=json.loads(native.read_bytes())
    require(outcome['status'] in ('SAT_NATIVE_VERIFIED_WITNESS','UNSAT_CLAIM_UNVERIFIED','UNKNOWN','AC_NONEMPTY_NO_SEARCH'),'Unknown native status')
    report=dict(status='JOINT_STAR_DFS_RUN_FINISHED',native_status=outcome['status'],mode=args.mode,
        manifest_path=key(args.out/'manifest.json'),manifest_sha256=digest(args.out/'manifest.json'),
        native_path=key(native),native_sha256=digest(native),log_path=key(args.out/'native.log'),log_sha256=digest(args.out/'native.log'),
        inputs_sha256=bindings,nodes=outcome['nodes'],branches=outcome['branches'],elapsed_seconds=outcome['elapsed_seconds'],
        independent_exclusion_proved=False,independent_graph_witness_verified=False,goal_marked_complete=False)
    save(args.out/'result.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='inputs_sha256'}))


if __name__=='__main__': main()
