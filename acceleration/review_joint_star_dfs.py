"""Synthetic branching, real AC-only parity, and bounded refusal controls."""
import argparse
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import subprocess
import sys

from audit_joint_star_dfs import audit,require,path,key

ROOT=Path(__file__).resolve().parents[1]
EXE=ROOT/'acceleration/build/joint_star_dfs.exe'
CONTROL=ROOT/'acceleration/results/20260916_cp_round8_auto/search/local/index_52112'
CANDIDATE=CONTROL.parent.parent/'adopted_index_52112/best_candidate.json'


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();require(not args.out.exists(),'Fresh control directory required');args.out.mkdir(parents=True)
    started_sources=[EXE,ROOT/'acceleration/joint_star_dfs.rs',ROOT/'acceleration/run_joint_star_dfs.py',
                     ROOT/'acceleration/audit_joint_star_dfs.py',Path(__file__)]
    hashes={key(p):digest(p) for p in started_sources}
    process=subprocess.run([str(EXE),'--self-test'],capture_output=True,text=True,check=True)
    synthetic=json.loads(process.stdout)
    counts={c:sum(all(x[u]!=x[v] for u,v in combinations(range(3),2)) for x in product(range(c),repeat=3)) for c in (2,3)}
    require(counts=={2:0,3:6},'Independent synthetic oracle failed')
    require(synthetic['status']=='JOINT_STAR_SYNTHETIC_BRANCH_CONTROLS_PASS' and
            synthetic['controls'][0]['status']=='EXHAUSTED_SYNTHETIC_CSP' and synthetic['controls'][0]['branches']==2 and
            synthetic['controls'][1]['status']=='FOUND_SYNTHETIC_ASSIGNMENT' and synthetic['controls'][1]['branches']>0 and
            synthetic['node_cap_rejected'] and synthetic['time_cap_rejected'],'Synthetic branch controls failed')
    runs=[]
    for name,extra,expected in [('compact_ac',[],'AC_NONEMPTY_NO_SEARCH'),('pair_cap',['--pair-cap','1'],'UNKNOWN'),
                               ('memory_cap',['--memory-mib','1'],'UNKNOWN'),('time_cap',['--seconds','0.000000000001'],'UNKNOWN')]:
        out=args.out/name
        command=[sys.executable,'-B',str(ROOT/'acceleration/run_joint_star_dfs.py'),'--candidate',str(CANDIDATE),
                 '--domains',str(CONTROL/'stars.json'),'--pair-certificate',str(CONTROL/'pairs.json'),
                 '--pair-audit',str(CONTROL/'independent_pair_audit.json'),'--out',str(out),'--mode','ac',*extra]
        child=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=45)
        require(child.returncode==0,child.stderr)
        checked=audit(out)
        with (out/'audit.json').open('x',encoding='utf-8') as f:f.write(json.dumps(checked,indent=2)+'\n')
        native=json.loads((out/'native.json').read_bytes())
        require(native['status']==expected and native['branches']==native['nodes']==0,'Real control branched or wrong cap')
        runs.append(dict(name=name,status=native['status'],cap_reason=native['cap_reason'],nodes=0,branches=0,
                         relation_bytes=native['relation_bytes'],domain_pairs=native['domain_pairs_evaluated'],
                         audit_path=key(out/'audit.json'),audit_sha256=digest(out/'audit.json')))
    negatives=[]
    def refusal(name,inp,dom,options):
        out=args.out/(name+'_must_not_exist.json')
        run=subprocess.run([str(EXE),str(inp),str(dom),str(out),*options],capture_output=True,text=True)
        require(run.returncode!=0 and not out.exists(),'Invalid native input accepted: '+name)
        negatives.append(dict(name=name,rejected=True,error=run.stderr.strip()))
    inp,dom=CONTROL/'candidate.txt',CONTROL/'domains.txt'
    for name,options in [('nan_seconds',['NaN']),('zero_nodes',['10','0']),('zero_memory',['10','100','1000','0']),
                         ('invalid_mode',['10','100','1000','1','bad'])]: refusal(name,inp,dom,options)
    bad=args.out/'duplicate_candidate.txt'
    tokens=inp.read_text().split();tokens[4:6]=tokens[2:4];bad.write_text(' '.join(tokens),encoding='ascii')
    refusal('duplicate_K',bad,dom,[])
    stars=json.loads((CONTROL/'stars.json').read_bytes())
    rows=[[int(m,16) for m in r['domain_masks_hex']] for r in stars['domains']]
    bad_domain=args.out/'bad_mask.txt'
    bad_domain.write_text('C99DOMAINS1 84\n'+''.join('1 '+hex(1 if u==0 else row[0])+'\n' for u,row in enumerate(rows)),encoding='ascii')
    refusal('wrong_star_degree',inp,bad_domain,[])
    # Eight disjoint neighbors but deliberately wrong root-label quotas.
    labels=[(2*a+s,2*b+t) for a,b in combinations(range(7),2) for s in range(2) for t in range(2)]
    allowed=[v for v in range(84) if not({x//2 for x in labels[0]}&{x//2 for x in labels[v]})]
    bad_domain2=args.out/'wrong_quota_mask.txt'
    wrong=sum(1<<v for v in allowed[:8])
    bad_domain2.write_text('C99DOMAINS1 84\n'+''.join('1 '+hex(wrong if u==0 else row[0])+'\n' for u,row in enumerate(rows)),encoding='ascii')
    refusal('wrong_star_quota',inp,bad_domain2,[])
    oldout=args.out/'existing.json';oldout.write_text('preserve\n',encoding='ascii');oldhash=digest(oldout)
    refused=subprocess.run([str(EXE),str(inp),str(dom),str(oldout)],capture_output=True,text=True)
    require(refused.returncode!=0 and digest(oldout)==oldhash,'Native replaced prior output')
    negatives.append(dict(name='existing_output_preserved',rejected=True))
    require(all(digest(path(n))==h for n,h in hashes.items()),'Sources changed during controls')
    report=dict(status='JOINT_STAR_DFS_SYNTHETIC_AND_REAL_AC_CONTROLS_PASS',inputs_sha256=hashes,
        independent_synthetic_solution_counts=counts,synthetic_native=synthetic,real_controls=runs,
        negative_controls=negatives,all_negative_controls_rejected=True,
        research_branch_searches=0,conway_witness_created=False,independent_conway_exclusion_proved=False,
        scope='Tiny synthetic CSP branches verified by exhaustive Python coloring oracle; real fixed-K runs only reproduce audited AC or return caps. No real branching search performed.')
    with (args.out/'report.json').open('x',encoding='utf-8') as f:f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],real_ac_runs=len(runs),native_negative_controls=len(negatives),research_branch_searches=0)))


if __name__=='__main__':main()
