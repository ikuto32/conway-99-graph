"""Candidate identity-P construction; pure raw-neighbor checks, no imports."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
THEOREM = "acceleration/results/20260930_independent_review/triangle_core_paircap_theorem/summary.json"
THEOREM_SHA = "5fa165b4d17673be87097804f0ca64d10f8ed3d4ea199841007e4c7df118cc4f"
CENSUS = "acceleration/results/20260930_independent_review/triangle_matching_pair_census/summary.json"
CENSUS_SHA = "085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79"

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_gate(name, digest):
    assert sha(ROOT/name) == digest
    d = json.loads((ROOT/name).read_text())
    for path, value in d['inputs_sha256'].items():
        assert sha(ROOT/path) == value, path
    return d

def graph(matchings):
    n = len(matchings[0]); assert n > 0 and n % 2 == 0
    assert len(matchings) == 3
    for m in matchings:
        assert len(m) == n and sorted(m) == list(range(n))
        assert all(m[i] != i and m[m[i]] == i for i in range(n))
    a = [set() for _ in range(3+3*n)]
    def edge(x,y):
        assert x != y
        a[x].add(y); a[y].add(x)
    for t in range(3):
        for u in range(t+1,3): edge(t,u)
        for b in range(n):
            edge(t,3+t*n+b)
            edge(3+t*n+b,3+t*n+matchings[t][b])
            for s in range(t+1,3): edge(3+t*n+b,3+s*n+b)
    return a

def caps(a):
    assert all(i not in row for i,row in enumerate(a))
    assert all(i in a[j] for i,row in enumerate(a) for j in row)
    return all(len(a[x]&a[y])+(y in a[x]) <= 2
               for x in range(len(a)) for y in range(x+1,len(a)))

def main():
    p=argparse.ArgumentParser(); p.add_argument('--out',required=True); args=p.parse_args()
    out=ROOT/args.out; out.mkdir(parents=True,exist_ok=False); start=time.monotonic()
    load_gate(THEOREM,THEOREM_SHA); gate=load_gate(CENSUS,CENSUS_SHA)
    controls=[]
    for n in [2,4,6,12]:
        g=graph([[i^1 for i in range(n)]]*3)
        assert caps(g); controls.append({'n':n,'raw_graph_pass':True})
    corrupt=graph([[i^1 for i in range(4)]]*3)
    corrupt[0].add(7); corrupt[7].add(0)
    assert not caps(corrupt)
    malformed=False
    try: graph([list(range(4))]*3)
    except AssertionError: malformed=True
    assert malformed
    records=[]; files=[]
    for stage in sorted((ROOT/'acceleration/results/20260930_triangle_matching_pair_census_v2').glob('stage_*.json')):
        rel=stage.relative_to(ROOT).as_posix()
        assert gate['inputs_sha256'][rel] == sha(stage)
        d=json.loads(stage.read_text()); files.append(rel)
        for i,row in enumerate(d['second_orbits']):
            assert caps(graph([[j^1 for j in range(12)],d['M1'],row['representative']]))
            records.append({'source_stage':stage.name,'second_orbit_index':i,'identity_P_raw39_paircaps':True})
    assert len(records)==3580
    (out/'raw_controls.json').write_text(json.dumps({'controls':controls,'extra_edge_rejected':True,'nonmatching_rejected':True,'records':records},indent=2)+'\n')
    paths=[Path(__file__).relative_to(ROOT).as_posix(),THEOREM,CENSUS,
      'docs/DERIVATION_20260930_TRIANGLE_CORE_IDENTITY_CONSTRUCTION.md','uv.lock','pyproject.toml',*files]
    report={'status':'CANDIDATE_TRIANGLE_CORE_IDENTITY_CONSTRUCTION','claim_id':'C-TRIANGLE-CORE-IDENTITY-P-CONSTRUCTION','claim_revision':1,
      'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'python':platform.python_version(),
      'statement':'For every positive even n and arbitrary three perfect matchings of order n, identity cross-fibre matchings construct a triangle-and-three-fibre graph satisfying every local distinct-pair common-neighbor-plus-adjacency cap <=2.',
      'scope':'Only a local 3+3n positive graph; at n=12 a 39-vertex necessary-condition witness, no target completion.',
      'basis':['DERIVED','COMPUTED'],'mathematical_status':'CANDIDATE','independent_review':None,
      'independent_review_reason':'New corollary authored here; awaiting a different reviewer.',
      'dependencies':[{'id':'C-TRIANGLE-CORE-PERMUTATION-PAIR-CAP-REDUCTION','revision':1,'relation':'uses_result'}],
      'sampled_representative_controls':3580,'controls_sha256':sha(out/'raw_controls.json'),
      'inputs_sha256':{path:sha(ROOT/path) for path in paths},'producer_imports':False,
      'limitations':['No identity normalization for arbitrary target P is asserted.','No hypothetical target automorphism is assumed.','Finite controls do not replace the universal proof.'],
      'elapsed_seconds':time.monotonic()-start}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'sha256':sha(out/'summary.json')}))

if __name__=='__main__': main()
