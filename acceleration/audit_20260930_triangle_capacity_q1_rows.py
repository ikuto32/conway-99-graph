"""Independently check one capacity-Q1 raw scope and supplied C2 row artifacts.

No producer imports. The pinned independent integer tree/constraint checker
is shared explicitly; full raw99 scope and raw-row checks are authored here.
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
HELPER='acceleration/audit_20260930_triangle_row29_obstruction.py'
HELPER_SHA='109671d882976ab68b350883340f3f0d7437571caa56b01d56a875f7897c4730'
GATE='acceleration/results/20260930_independent_review/triangle_q1_capacity_sat_object/summary.json'
GATE_SHA='34eec921b8c149c2bd49860e2f0208c4d2fa472e953c55a89dc867a9d8c2605d'
FACTOR='acceleration/results/20260930_triangle_q1_capacity_native_pilot/main/decoded_factor.json'
FACTOR_SHA='94904b766b487e579f656e685643449c23a6aabf07825cac17e9fd8e241427c5'

def h(p):
    with Path(p).open('rb') as f:
        import hashlib
        return hashlib.file_digest(f,'sha256').hexdigest()
def need(ok,msg):
    if not ok:raise ValueError(msg)
need(h(ROOT/HELPER)==HELPER_SHA,'frozen independent helper identity')
from audit_20260930_triangle_row29_obstruction import reconstruct, check_tree, calibration, feasible

def load(p):return json.loads((ROOT/p).read_bytes())
def save(p,obj):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()

def raw_scope(f,q):
    need(len(f)==24 and all(len(r)==60 and all(type(v)is int and v in (0,1)for v in r)for r in f),'literal binary24x60')
    edges=[(i,j)for i,j in combinations(range(12),2)if j!=(i^1)]
    need(len(q)==60 and all(type(v)is int for v in q)and sorted(q)==list(range(60)),'Q1 exact permutation')
    canonical=[[int(i in e)for e in edges]for i in range(12)]
    need(f[:12]==canonical and f[12:]==[[int(i in edges[q[d]])for d in range(60)]for i in range(12)],'canonical incidence and Q1 direction')
    a=[[0]*99 for _ in range(99)]
    def put(i,j,v=1):need(i!=j,'loop');a[i][j]=a[j][i]=v
    for i,j in combinations(range(3),2):put(i,j)
    for cell in range(3):
        for label in range(12):
            v=3+12*cell+label
            put(cell,v);put(v,3+12*cell+(label^1))
    for i in range(12):put(3+i,15+i);put(3+i,27+i);put(15+i,27+(i+6)%12)
    for i in range(36):
        for d in range(60):put(3+i,39+d,f[i][d]if i<24 else -1)
    for i,j in combinations(range(39,99),2):put(i,j,-1)
    c=[r[3:39]for r in a[3:39]]
    k=[[12*int(i==j)-c[i][j]-sum(c[i][t]*c[t][j]for t in range(36))+2-int(i//12==j//12)for j in range(24)]for i in range(24)]
    need([[sum(x*y for x,y in zip(r,s))for s in f]for r in f]==k,'all576 exact prescribed Gram entries')
    need(all(sum(r)==10 for r in f),'all24 row margins')
    need(all(sum(f[12*g+i][d]for i in range(12))==2 for g in range(2)for d in range(60)),'all120 fibre column margins')
    check_partial(a)
    need(sum(a[i][j]==-1 for i,j in combinations(range(99),2))==2490,'exact unknown C2+D population')
    return a,k

def check_partial(a):
    need(len(a)==99 and all(len(r)==99 for r in a),'shape99')
    need(all(type(v)is int and v in (-1,0,1)for r in a for v in r),'ternary')
    need(all(a[i][i]==0 for i in range(99)),'diagonal')
    need(all(a[i][j]==a[j][i]for i,j in combinations(range(99),2)),'symmetry')
    need(all(sum(v==1 for v in r)<=14<=sum(v!=0 for v in r)for r in a),'all99 degree intervals')
    sets=[{j for j,v in enumerate(r)if v==1}for r in a]
    for i,j in combinations(range(99),2):need(len(sets[i]&sets[j])<=2-int(a[i][j]==1),'all4851 known pair caps')
    return dict(degree_intervals=99,known_pair_caps=4851)

def check_witness(a,u,vv,cs,bits):
    need(len(bits)==len(vv)and all(type(v)is int and v in (0,1)for v in bits),'complete strict binary row assignment')
    need(feasible(bits,cs),'every independently reconstructed row constraint')
    b=deepcopy(a)
    for v,bit in zip(vv,bits):b[u][v]=b[v][u]=bit
    need(sum(b[u])==14,'completed chosen row degree14')
    for v in range(3,27):
        need(sum(b[u][w]*b[v][w]for w in range(99))==2-b[u][v],'literal selected exact common counts')
    return check_partial(b),b

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--summary-sha256',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False);start=time.monotonic();inputs={}
    def bind(path,expected=None):
        digest=h(ROOT/path);need(expected is None or digest==expected,'input SHA '+path);inputs[path]=digest
    try:
        for path,digest in [(HELPER,HELPER_SHA),(GATE,GATE_SHA),(FACTOR,FACTOR_SHA)]:bind(path,digest)
        run=ROOT/args.run;summarypath=key(run/'summary.json');bind(summarypath,args.summary_sha256);producer=load(summarypath)
        gate=load(GATE);need(gate['status']=='INDEPENDENT_TRIANGLE_Q1_CAPACITY_SAT_OBJECT_PASS'and gate['inputs_sha256'][FACTOR]==FACTOR_SHA,'exact independent SAT-object binding')
        for path,expected in producer['output_hashes'].items():bind(path,expected)
        manifest=load(key(run/'manifest.json'))
        for path,expected in manifest['inputs_sha256'].items():bind(path,expected)
        factor=load(FACTOR);a,k=raw_scope(factor['incidence_matrix'],factor['Q1'])
        raw=load(key(run/'raw99.json'))
        need(raw['Q1']==factor['Q1']and raw['known_adjacency']==a,'every raw99 fixed/free entry')
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=inputs.copy(),question='Do supplied row artifacts prove precisely their claimed individual C2 row feasibility or impossibility for the one fixed capacity-Q1 factor?',limits=dict(seconds=120),numerical_thresholds=None,numerical_thresholds_null_reason='All checks exact integers, raw sets and finite trees.'))
        controls,_=calibration();save(out/'positive_controls.json',controls)
        paths=sorted(run.glob('row_*.json'));need(len(paths)==12,'all twelve supplied row artifacts')
        rows=[];corruptions=[];seen=set()
        for path in paths:
            need(time.monotonic()-start<120,'120second checker cap')
            record=load(key(path));u=record['vertex'];need(type(u)is int and 27<=u<39 and u not in seen,'unique C2 vertex');seen.add(u)
            vv,cs=reconstruct(a,u,list(range(3,27)))
            need(record['variables']==vv and record['constraints']==cs,'all row variables and constraints reconstructed')
            need(vv==list(range(39,99)),'all60 row variables')
            proof=record['proof'];status=proof['status'];detail=None
            if status=='UNSAT':
                detail=check_tree(60,cs,proof,record=True);need(detail['sat_leaves']==0,'complete row exclusion')
                save(out/f'row_{u:02d}_complete_tree_check.json',detail)
                detail={x:y for x,y in detail.items()if x!='receipts'}
                mutants={}
                spl=next((j for j,n in enumerate(proof['nodes'])if n['status']=='SPLIT'),None)
                if spl is not None:
                    bad=deepcopy(proof);bad['nodes'][spl]['children'].pop();mutants['missing_branch']=bad
                forced=next((j for j,n in enumerate(proof['nodes'])if n['forces']),None)
                if forced is not None:
                    bad=deepcopy(proof);bad['nodes'][forced]['forces'][0]['value']^=1;mutants['wrong_force']=bad
                leaf=next(j for j,n in enumerate(proof['nodes'])if n['status']=='CONFLICT')
                bad=deepcopy(proof);bad['nodes'][leaf]['ones']+=1;mutants['wrong_leaf_counter']=bad
                for label,bad in mutants.items():
                    try:check_tree(60,cs,bad)
                    except ValueError:corruptions.append(f'row{u}_{label}')
                    else:raise ValueError('corrupted tree accepted '+label)
            elif status=='SAT':
                detail,complete=check_witness(a,u,vv,cs,proof['assignment'])
                save(out/f'row_{u:02d}_witness_check.json',dict(vertex=u,assignment=proof['assignment'],partial_adjacency99=complete,checks=detail,complete_search_tree_checked=False,reason='A literal witness proves individual feasibility; the early-stop producer tree is not claimed exhaustive.'))
                bad=proof['assignment'].copy();bad[0]^=1
                try:check_witness(a,u,vv,cs,bad)
                except ValueError:corruptions.append(f'row{u}_flipped_witness_bit')
                else:raise ValueError('flipped witness accepted')
            elif status=='UNKNOWN':
                detail=dict(no_feasibility_or_exclusion_claim=True,reported_nodes=len(proof.get('nodes',[])),reported_reason=proof.get('reason'))
            else:raise ValueError('unknown result status')
            bad=deepcopy(record);bad['constraints'][0]['upper']+=1;need(bad['constraints']!=cs,'constraint corruption');corruptions.append(f'row{u}_changed_degree_constraint')
            rows.append(dict(vertex=u,status=status,row_artifact_sha256=inputs[key(path)],constraint_counts=dict(Counter(c['kind']for c in cs)),details=detail))
        need(seen==set(range(27,39)),'entire declared population of12 C2 vertices')
        need(producer['attempted_rows']==12,'producer attempt count')
        need([(r['vertex'],r['status'])for r in rows]==[(r['vertex'],r['status'])for r in producer['outcomes']],'saved outcome identity and status')
        for r,p in zip(rows,producer['outcomes']):
            need(r['row_artifact_sha256']==p['sha256'],'producer per-row artifact binding')
            if r['status']=='UNSAT':need(r['details']['nodes']==p['nodes'],'producer checked tree count')
        bad=deepcopy(raw);bad['known_adjacency'][27][39]=bad['known_adjacency'][39][27]=0;need(bad['known_adjacency']!=a,'raw free entry corruption');corruptions.append('changed_raw_free_edge')
        bad=deepcopy(factor);bad['incidence_matrix'][12][0]^=1
        try:raw_scope(bad['incidence_matrix'],bad['Q1'])
        except ValueError:corruptions.append('corrupted_factor_bit')
        else:raise ValueError('bad factor accepted')
        save(out/'raw_scope_and_constraints.json',dict(known_adjacency99=a,prescribed_Gram24x24=k,rows=[dict(vertex=r['vertex'],variables=reconstruct(a,r['vertex'],list(range(3,27)))[0],constraints=reconstruct(a,r['vertex'],list(range(3,27)))[1])for r in rows]))
        save(out/'corrupted_controls.json',dict(rejected=corruptions))
        for path,expected in list(inputs.items()):bind(path,expected)
        for path in [key(__file__),'uv.lock','pyproject.toml','docs/AUDIT_20260930_TRIANGLE_CAPACITY_Q1_ROWS.md']:bind(path)
        counts=dict(Counter(r['status']for r in rows))
        save(out/'summary.json',dict(status='INDEPENDENT_TRIANGLE_CAPACITY_Q1_ROW_ARTIFACTS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,verifier='/root/state_literature_audit independent raw99 and individual-row checking path',producer_imports=False,shared_components=['Pinned independent raw row-constraint and complete-tree checker, with original exact controls rerun.','Python standard library.'],rows_attempted=len(rows),row_outcomes=counts,rows=rows,corrupted_controls_rejected=corruptions,raw99_entries_checked=9801,known_pair_caps_checked=4851,partial_factor_Gram_entries_checked=576,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',recommendation='VERIFIED for the exact recorded individual row outcomes only',scope='One explicit fixed39 core, canonical C0 and exact raw Q1 factor. Each individual row is tested with all other C2 rows and D unspecified.',limitations=['No universal fixed-core containment or target automorphism is assumed.','SAT row witnesses need not coexist; no complete36 factor or99graph is established.','UNKNOWN rows give neither feasibility nor exclusion.','No claim of full row-domain enumeration or global search coverage.'],outputs_sha256={key(p):h(p)for p in sorted(out.iterdir())if p.is_file()},elapsed_seconds=time.monotonic()-start))
        print(json.dumps(dict(status='INDEPENDENT_TRIANGLE_CAPACITY_Q1_ROW_ARTIFACTS_PASS',rows=len(rows),outcomes=counts)))
    except BaseException as e:
        save(out/'failure.json',dict(status='CHECK_FAILED',timestamp=datetime.now(timezone.utc).isoformat(),error=repr(e),inputs_sha256=inputs));raise

if __name__=='__main__':main()
