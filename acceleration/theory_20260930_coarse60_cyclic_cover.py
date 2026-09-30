"""Candidate universal disjoint cover for all raw bits in one coarse template."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
SCOPE=ROOT/'acceleration/results/20260930_prism_coarse60_bitlift/scope.json'
SCOPE_HASH='3237da2a02c60fc3f0c61e562788582b7ce25946afb523a84dc6634912ed98e9'
GATE=ROOT/'acceleration/results/20260930_independent_review/prism_coarse60_bitlift_cnf/summary.json'
GATE_HASH='b82eb3d3c999ae8bdcdbfd246dd28ea9cd6a9dd8d1ce811abc82ee0f3e38d88d'

def need(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def verify(words,orbits):
    need(len(words)==60 and len(set(map(tuple,words)))==60,'60 distinct words')
    need(len(orbits)==20 and sorted(d for triple in orbits for d in triple)==list(range(60)),'20-triple exact cover')
    for triple in orbits:
        need(len(triple)==3 and len(set(triple))==3,'triple shape')
        for offset,d in enumerate(triple):
            need(words[d]==[(v+offset)%3 for v in words[triple[0]]],'cyclic orbit word')
        for a in range(6):need(sorted(words[d][a] for d in triple)==[0,1,2],'all three fibres distinct')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    need(digest(SCOPE)==SCOPE_HASH and digest(GATE)==GATE_HASH,'scope and encoding gate pins')
    gate=json.loads(GATE.read_bytes());need(gate['status']=='INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_CNF_PASS','base gate')
    inputs={key(SCOPE):SCOPE_HASH,key(GATE):GATE_HASH}
    for p in [Path(__file__),Path(__file__).with_name('theory_20260930_coarse60_cyclic_cover_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(p)]=digest(p)
    created=datetime.now(timezone.utc).isoformat()
    save(out/'manifest.json',dict(created_at=created,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),inputs_sha256=inputs,
        versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip()),
        limits=dict(seconds=30,solver_calls=0),scope='One fixed60coarse-word template, all2^360rawbit assignments.'))
    words=json.loads(SCOPE.read_bytes())['columns60'];lookup={tuple(w):d for d,w in enumerate(words)}
    rotation=[lookup[tuple((v+1)%3 for v in w)] for w in words]
    need(sorted(rotation)==list(range(60)),'rotation bijection')
    seen=set();orbits=[]
    for d in range(60):
        if d in seen:continue
        triple=[d,rotation[d],rotation[rotation[d]]]
        need(rotation[triple[-1]]==d and len(set(triple))==3,'length3orbit')
        seen.update(triple);orbits.append(triple)
    verify(words,orbits)
    controls=0
    for fibres in [(0,1,2),(1,2,0),(2,0,1)]:
        for bits in product(range(2),repeat=3):
            vertices=[12*g+b for g,b in zip(fibres,bits)]
            need(len(set(vertices))==3,'arbitrary localbits distinct core rows');controls+=1
    rejected=[]
    for label,change in [('duplicate_column',lambda o:o[0].__setitem__(1,o[0][0])),
                        ('wrong_orbit',lambda o:o[0].__setitem__(1,o[1][1])),
                        ('missing_triangle',lambda o:o.pop()),
                        ('wrong_rotation_order',lambda o:o[0].reverse())]:
        bad=json.loads(json.dumps(orbits));change(bad)
        try:verify(words,bad)
        except ValueError:rejected.append(dict(name=label,rejected=True))
        else:raise AssertionError('bad cyclic cover accepted')
    certificate=dict(schema='COARSE60_ALL_BITS_CYCLIC_COVER_V1',coarse_words=words,rotation_column_images=rotation,
        orbits=orbits,component_fibres=[[[words[d][a] for d in t] for a in range(6)] for t in orbits],
        component_distinct_fibre_checks=120,column_pair_distinct_fibre_checks=60,
        selected_triangles_have_no_conditional_XORs=True,applies_to_all_raw_bit_assignments=True,
        raw_bit_assignment_count_exact=str(1<<360),research_factor=None,
        research_factor_reason='No Gram/margin compatibility is supplied by this universal cover.',residual_D=None,
        residual_D_reason='Only an existential disjoint triangle partition is supplied; no degree8 or mixed equations.')
    save(out/'certificate.json',certificate);save(out/'controls.json',dict(local_truth_cases=controls,corruptions=rejected))
    proof='''For each saved orbit, its three coarse words use different fibres in every component.\nA raw column selects row (fibre,component,bit), so rows from two orbit columns\ncan never coincide: rows from different components differ in component, and\nrows from the same component differ in fibre, for either bit. Thus the three\ncolumns are pairwise disjoint for every assignment of all 360 bits. The twenty\norbits cover all sixty columns exactly once. Every original factor therefore\nhas such a disjoint triangle partition, irrespective of its Gram equations.\nThe proposed triangle-selector extension would admit the twenty orbit selectors\nand exact-one prefix values recomputed from them. All selected triples impose\nzero opposite-bit conditions; unselected triples' implications are vacuous.\nTherefore that extension alone is redundant for this particular coarse template.\nThis argument does not assert these are the triangles of a residual completion,\nor provide residual D, a factor, or a target graph. No target automorphism is assumed.\n'''
    (out/'proof.txt').write_text(proof,encoding='utf-8',newline='\n')
    need(time.monotonic()-start<30 and all(digest(ROOT/p)==h for p,h in inputs.items()),'limits and input stability')
    summary=dict(status='CANDIDATE_COARSE60_UNIVERSAL_CYCLIC_DISJOINT_COVER',created_at=created,completed_at=datetime.now(timezone.utc).isoformat(),
        inputs_sha256=inputs,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},
        exact_scope='For all2^360rawbit assignments of these60coarse words, the saved20cyclic orbits are pairwise-disjoint column triples.',
        candidate_consequence='Adding only existential disjoint-triangle-cover selectors cannot exclude any original rawbit assignment.',
        proposed_strengthening='REDUNDANT_WITHIN_THIS_FIXED_TEMPLATE',independent_approval=False,solver_calls=0,target_resolution='UNKNOWN',wall_seconds=time.monotonic()-start)
    save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=digest(out/'summary.json'),certificate_sha256=digest(out/'certificate.json'))))

if __name__=='__main__':main()
