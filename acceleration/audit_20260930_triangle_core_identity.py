"""Separate universal identity construction review and literal bit-matrix controls."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'acceleration/results/20260930_triangle_core_identity/run01'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def need(x,m):
    if not x:raise ValueError(m)

def matrix(ms):
    n=len(ms[0]);need(n>0 and n%2==0 and len(ms)==3,'positive even matching order')
    need(all(len(m)==n and sorted(m)==list(range(n))and all(m[i]!=i and m[m[i]]==i for i in range(n))for m in ms),'perfect matchings')
    rows=[]
    for u in range(3+3*n):
        mask=0
        for v in range(3+3*n):
            adjacent=False
            if u!=v:
                if u<3 and v<3:adjacent=True
                elif u<3:adjacent=(v-3)//n==u
                elif v<3:adjacent=(u-3)//n==v
                else:
                    i,a=divmod(u-3,n);j,b=divmod(v-3,n)
                    adjacent=(ms[i][a]==b)if i==j else a==b
            if adjacent:mask|=1<<v
        rows.append(mask)
    return rows

def caps(rows):
    for i,row in enumerate(rows):
        need(not(row>>i&1),'zero diagonal')
        for j in range(i):
            need((row>>j&1)==(rows[j]>>i&1),'symmetric')
            if (row&rows[j]).bit_count()+(row>>j&1)>2:return False
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False)
    need(digest(RUN/'summary.json')=='ec5a16696cb2933ad1213ff7c24ce92a14ff04c2fbc06309e12aeec0fe6b029d','candidate hash')
    candidate=read(RUN/'summary.json');inputs=candidate['inputs_sha256'].copy()
    for name,h in inputs.items():need(digest(ROOT/name)==h,'pinned candidate input '+name)
    controls=read(RUN/'raw_controls.json');need(digest(RUN/'raw_controls.json')==candidate['controls_sha256'],'raw controls identity')
    gate=read(ROOT/'acceleration/results/20260930_independent_review/triangle_core_paircap_theorem/summary.json')
    need(gate['recommendation']=='VERIFIED'and gate['claim_revision']==1,'reduction premise')
    checked=[]
    for stage in sorted((ROOT/'acceleration/results/20260930_triangle_matching_pair_census_v2').glob('stage_*.json')):
        data=read(stage)
        for i,row in enumerate(data['second_orbits']):
            need(caps(matrix([[j^1 for j in range(12)],data['M1'],row['representative']])),'literal representative cap')
            checked.append({'source_stage':stage.name,'second_orbit_index':i,'identity_P_raw39_paircaps':True})
    need(checked==controls['records']and len(checked)==3580,'all stated raw representative controls')
    small=[]
    for n in [2,4,6,12]:
        rows=matrix([[i^1 for i in range(n)]]*3);need(caps(rows),'positive control')
        small.append(dict(n=n,vertices=len(rows),caps=True))
    # n=2 is a complete SRG(9,4,1,2), furnishing a calibrated positive fixture.
    rows=matrix([[1,0]]*3)
    need(all(r.bit_count()==4 for r in rows),'rook9 degree')
    need(all((rows[i]&rows[j]).bit_count()==2-(rows[i]>>j&1)for i in range(9)for j in range(i)),'rook9 exact pair identity')
    bad=matrix([[i^1 for i in range(4)]]*3);bad[0]|=1<<7;bad[7]|=1
    need(not caps(bad),'extra-edge negative')
    rejected=False
    try:matrix([list(range(4))]*3)
    except ValueError:rejected=True
    need(rejected,'loop-matching negative')
    inputs.update({(RUN/'summary.json').relative_to(ROOT).as_posix():digest(RUN/'summary.json'),
        (RUN/'raw_controls.json').relative_to(ROOT).as_posix():digest(RUN/'raw_controls.json'),
        Path(__file__).relative_to(ROOT).as_posix():digest(Path(__file__))})
    report=dict(status='INDEPENDENT_TRIANGLE_CORE_IDENTITY_CONSTRUCTION_PASS',claim_id=candidate['claim_id'],claim_revision=1,
        recommendation='VERIFIED',kind='construction',basis=['DERIVED','COMPUTED'],statement=candidate['statement'],scope=candidate['scope'],
        dependencies=candidate['dependencies'],timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],
        working_directory=str(ROOT),python=platform.python_version(),verifier='/root independent direct derivation and bit-matrix checker',
        inputs_sha256=inputs,exact_derivation=[
            'With P=I, a forbidden unary equality P(i)=M0(i) is impossible because each matching has no fixed point. The forbidden two-entry conjunction contains P(M1(b))=b, which is already impossible since M1(b)!=b. The independently reviewed necessary-and-sufficient reduction proves all pair caps.',
            'Direct verification for arbitrary positive even n: a pair of triangle vertices has one common neighbor and an edge. A triangle vertex and a vertex in its own fiber have one common neighbor and an edge; in another fiber they have exactly two common neighbors and no edge.',
            'Two distinct vertices in one fiber have only its triangle vertex as common neighbor, so common-plus-adjacency is1 or2. The cap block across distinct fibers i,j is2I+Mi+Mj: diagonal2, every off-diagonal at most2. These cases exhaust all distinct vertex pairs and prove the universal statement independently of fixture counts.',
        ],checks=dict(representatives_checked=3580,representative_pair_caps=3580*741,small_controls=small,
            complete_srg9_control=True,corruptions_rejected=['extra_edge','nonmatching_fixed_points']),
        shared_components=['Frozen representative data and Python integer runtime; no producer code imports.'],
        limitations=['This is a local positive graph construction, not a 99-vertex SRG construction.',
            'P=I is not asserted without loss of generality for a target; it supplies one local witness for each matching triple.',
            'No target automorphism, target-wide coverage percentage, novelty or external review is asserted.'])
    path=out/'summary.json';path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':report['status'],'sha256':digest(path)}))

if __name__=='__main__':main()
