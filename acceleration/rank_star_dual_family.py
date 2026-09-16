"""Rank one audited cross3/4 family using fixed dyadic star duals.

All candidates are scored, and unavailable scores remain in the output. This
wrapper performs no LP solves, candidate pruning, or exclusion certification.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]

def path(p):
    return (ROOT/str(p).replace('\\','/')).resolve()

def key(p):
    return path(p).relative_to(ROOT).as_posix()

def digest(p):
    return sha256(path(p).read_bytes()).hexdigest()

def require(ok,msg):
    if not ok:
        raise ValueError(msg)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--family',required=True)
    p.add_argument('--family-audit',required=True)
    p.add_argument('--weights-manifest',required=True)
    p.add_argument('--native-audit',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--seconds-per-candidate',type=float,default=1.0)
    a = p.parse_args()
    out = path(a.out)
    require(not out.exists(),'Preserve prior output')
    require(math.isfinite(a.seconds_per_candidate) and 0<a.seconds_per_candidate<=3600,'Invalid seconds cap')
    started, bindings = time.perf_counter(), {}
    def bind(p,expected=None):
        name,h=key(p),digest(p)
        require(expected is None or h==expected,'Changed input '+name)
        require(name not in bindings or bindings[name]==h,'Conflicting hash '+name)
        bindings[name]=h
        return h
    def document(p):
        bind(p)
        d=json.loads(path(p).read_bytes())
        for name,h in d.get('inputs_sha256',{}).items():
            bind(name,h)
        return d
    bind(__file__)
    family=document(a.family)
    proof=document(a.family_audit)
    weights=document(a.weights_manifest)
    qa=document(a.native_audit)
    require(family['status']=='COMPLETE_CROSS_ATOMIC_CYCLE_SUBFAMILY_EXTRACTION' and family['selector']=='cross_3_4','Wrong family scope')
    require(proof['status']=='INDEPENDENT_COMPLETE_CROSS_ATOMIC_CYCLE_EXTRACTION_PASS','Missing independent family proof')
    pb={key(p):h for p,h in proof['inputs_sha256'].items()}
    require(pb.get(key(a.family))==digest(a.family),'Family/proof association')
    require(pb.get(key(family['candidate_path']))==family['candidate_sha256'],'Unbound family base')
    require(weights['status']=='AUDITED_STAR_DUAL_DYADIC_RANKING_WEIGHTS_EXPORTED','Wrong weights manifest')
    require(weights['baseline_candidate_sha256']==family['candidate_sha256'] and key(weights['baseline_candidate_path'])==key(family['candidate_path']),'Weights/family baseline mismatch')
    bind(weights['dual_path'],weights['dual_sha256'])
    require(qa['status']=='INDEPENDENT_FULL99_INTEGER_STAR_DUAL_CONTROLS_PASS','Missing native controls')
    native=ROOT/'acceleration/build/star_dual_batch.exe'
    source=ROOT/'acceleration/star_dual_batch.rs'
    qb={key(p):h for p,h in qa['inputs_sha256'].items()}
    for f in (native,source):
        require(qb.get(key(f))==bind(f),'Native QA/source binding')
    candidates=family['overlap_candidates']
    count=len(candidates)
    require(0<count<=100000 and count==family['legal_count']==proof['legal_count']==len(family['moves'])==len(family['original_native_indices']),'Candidate count/association')
    signatures=set()
    for edges in candidates:
        require(type(edges)is list and len(edges)==168 and all(type(e)is list and len(e)==2 and all(type(v)is int for v in e) and 0<=e[0]<e[1]<84 for e in edges),'Malformed candidate')
        require(edges==sorted(edges) and len(set(map(tuple,edges)))==168,'Noncanonical edges')
        signature=tuple(map(tuple,edges))
        require(signature not in signatures,'Repeated family candidate')
        signatures.add(signature)
    out.mkdir(parents=True)
    input_file,output_file=out/'candidates.txt',out/'scores.json'
    with input_file.open('x',encoding='ascii',newline='\n') as f:
        f.write(f'C99OVERLAPS1 {count}\n')
        for edges in candidates:
            f.write(' '.join(str(v) for e in edges for v in e)+'\n')
    bind(input_file)
    command=[str(native),str(input_file),str(path(weights['dual_path'])),str(output_file),str(a.seconds_per_candidate),'2000000','20000']
    manifest=dict(status='FIXED_STAR_DUAL_FAMILY_RANKING_INPUTS_BOUND',inputs_sha256=dict(bindings),
                  family_path=key(a.family),family_sha256=digest(a.family),candidate_count=count,
                  weights_manifest_path=key(a.weights_manifest),weights_manifest_sha256=digest(a.weights_manifest),
                  native_audit_path=key(a.native_audit),native_audit_sha256=digest(a.native_audit),
                  input_path=key(input_file),input_sha256=digest(input_file),command=command,
                  candidate_order='Exactly family.overlap_candidates; indices zero based',
                  seconds_per_candidate=a.seconds_per_candidate,node_cap=2000000,domain_cap=20000,
                  score_scope='Fixed dual ranking only; all native domains newly enumerated for each candidate; no pruning or exclusion')
    manifest_path=out/'manifest.json'
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    tick=time.perf_counter()
    completed=subprocess.run(command,capture_output=True,text=True,timeout=count*a.seconds_per_candidate+120)
    native_wall=time.perf_counter()-tick
    (out/'native.log').write_text(completed.stdout+completed.stderr,encoding='utf-8')
    require(completed.returncode==0,'Native ranking failed; artifacts preserved: '+completed.stderr)
    result=json.loads(output_file.read_bytes())
    require(result['status']=='HEURISTIC_FIXED_STAR_DUAL_BATCH_FINISHED' and result['candidate_count']==count and len(result['results'])==count,'Malformed native results')
    ranked,unavailable=[],[]
    for i,r in enumerate(result['results']):
        if r['status']=='COMPLETE_HEURISTIC_SCORE':
            require(r['complete_domain_enumeration'] and r['local_empty_count']==0 and len(r['domain_counts'])==84 and all(r['domain_counts']),'Invalid complete score status')
            require(type(r['score_numerator'])is int and r['denominator']==1<<40 and r['score_numerator']==sum(r['vertex_minimum_numerators'])-r['weighted_cap_rhs_numerator'],'Invalid exact score arithmetic')
            ranked.append(dict(index=i,original_native_index=family['original_native_indices'][i],score_numerator=r['score_numerator'],denominator=r['denominator'],score=r['score'],root_group=family['moves'][i]['root_group'],cycle_size=family['moves'][i]['cycle_size']))
        else:
            require(r['status'] in ('UNAVAILABLE_INCOMPLETE_DOMAINS','UNAVAILABLE_EMPTY_DOMAIN') and r['score_numerator'] is None and r['score'] is None,'Invalid unavailable score')
            unavailable.append(dict(index=i,status=r['status'],cap_reason=r['cap_reason'],local_empty_count=r['local_empty_count']))
    ranked.sort(key=lambda row:(row['score_numerator'],row['index']))
    for name,h in bindings.items():
        require(digest(name)==h,'Input changed during native run '+name)
    bind(manifest_path);bind(output_file);bind(out/'native.log')
    summary=dict(status='HEURISTIC_FIXED_STAR_DUAL_FAMILY_RANKING_FINISHED',inputs_sha256=bindings,
                 family_path=key(a.family),family_sha256=digest(a.family),candidate_count=count,
                 complete_scores=len(ranked),unavailable_scores=len(unavailable),
                 status_counts=dict(Counter(r['status'] for r in result['results'])),
                 ranking_order='ascending exact integer score numerator, then input index',ranked=ranked,unavailable=unavailable,
                 native_elapsed_seconds=result['elapsed_seconds'],native_process_wall_seconds=native_wall,
                 elapsed_seconds=time.perf_counter()-started,candidates_pruned=0,exclusions_claimed=0,lp_solves=0,
                 scope='Heuristic ordering on this fixed audited family. Negative/zero scores do not prove feasibility; positive scores are not independently audited exclusion certificates. Empty/incomplete scores remain recorded as unavailable.')
    summary_path=out/'summary.json'
    summary_path.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=summary['status'],count=count,complete=len(ranked),unavailable=len(unavailable),native_seconds=result['elapsed_seconds'],best=ranked[:5],summary_sha256=digest(summary_path))))

if __name__=='__main__':
    main()
