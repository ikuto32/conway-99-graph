"""Independent quotient-class and all-local-bit proof of coarse-cover redundancy."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
RUN=B+'coarse60_cyclic_cover/'
SCOPE=B+'prism_coarse60_bitlift/scope.json'
ENC=B+'independent_review/prism_coarse60_bitlift_cnf/summary.json'
CENSUS=B+'prism_coarse60_triangle_cover/all_triples.json'
CENSUS_GATE=B+'independent_review/prism_coarse60_triangle_cover/summary.json'
PINS={RUN+'summary.json':'49872a955a8738c5611323ff7e66bae37f0bab67a3cef423a905aae3b44211b0',
 RUN+'certificate.json':'e0c4d47d3933434c56a25073947325b540d692468d2fc1fb87eb7549d6457275',
 SCOPE:'3237da2a02c60fc3f0c61e562788582b7ce25946afb523a84dc6634912ed98e9',
 ENC:'b82eb3d3c999ae8bdcdbfd246dd28ea9cd6a9dd8d1ce811abc82ee0f3e38d88d',
 CENSUS:'fd6c1a24ba39005702ac61742119ed643540285ef5775cdc4555f678e66f8ce3',
 CENSUS_GATE:'50add6b76aea5bade3d74cf56be71941aeed3587974efae2af8ebaf7db36754c'}
def need(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def reject(name,action,rows):
    try:action()
    except (ValueError,KeyError,IndexError,TypeError):rows.append(dict(name=name,rejected=True))
    else:raise AssertionError('corruption accepted: '+name)

def partition(words):
    need(len(words)==60 and all(len(w)==6 and all(type(x)is int and 0<=x<3 for x in w)for w in words),'raw word dimensions')
    need(len({tuple(w)for w in words})==60,'distinct raw words')
    classes={}
    # Quotient by a uniform additive constant, independently of orbit walking.
    for i,w in enumerate(words):
        normalized=tuple((x-w[0])%3 for x in w)
        classes.setdefault(normalized,[]).append(i)
    need(len(classes)==20 and all(len(v)==3 for v in classes.values()),'exact twenty quotient classes')
    groups=sorted(classes.values(),key=min)
    for group in groups:
        need(all({words[d][a]for d in group}=={0,1,2}for a in range(6)),'each component meets every fibre')
    return groups

def verify(words,cert):
    need(cert['coarse_words']==words,'certificate exact raw template')
    groups=partition(words);orbits=cert['orbits']
    need(len(orbits)==20 and [sorted(t)for t in orbits]==groups,'exact class-cover identity')
    need(sorted(d for t in orbits for d in t)==list(range(60)),'each column covered exactly once')
    rotation=cert['rotation_column_images'];need(len(rotation)==60 and sorted(rotation)==list(range(60)),'complete bijection')
    for d,e in enumerate(rotation):need(words[e]==[(g+1)%3 for g in words[d]],'literal coordinate rotation')
    for t in orbits:need(t[1]==rotation[t[0]] and t[2]==rotation[t[1]] and t[0]==rotation[t[2]],'recorded cyclic ordering')
    need(cert['component_fibres']==[[[words[d][a]for d in t]for a in range(6)]for t in orbits],'all120fibre triples')
    need(cert['component_distinct_fibre_checks']==120 and cert['column_pair_distinct_fibre_checks']==60,'scope counts')
    need(cert['raw_bit_assignment_count_exact']==str(2**360),'quantified bit population')
    need(cert['selected_triangles_have_no_conditional_XORs']is True and cert['applies_to_all_raw_bit_assignments']is True,'semantic metadata')
    need(cert['research_factor']is None and cert['residual_D']is None,'no factor or residual witness claim')
    checks=0
    for t in orbits:
        for i in range(3):
            for j in range(i+1,3):
                d,e=t[i],t[j]
                for a,b in product(range(6),repeat=2):
                    for x,y in product(range(2),repeat=2):
                        need(12*words[d][a]+2*a+x != 12*words[e][b]+2*b+y,'any local row pair distinct')
                        checks+=1
    need(checks==8640,'all pairwise literal collision possibilities')
    return groups,checks

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();need(out.is_relative_to(ROOT),'workspace output');out.mkdir(parents=True,exist_ok=False)
    now=datetime.now(timezone.utc).isoformat();bindings={}
    try:
        # Finite local controls calibrate the row-label argument before research.
        controls=[];truth=0
        for g,h in product(range(3),repeat=2):
            for a,b in product(range(6),repeat=2):
                for x,y in product(range(2),repeat=2):
                    same=(12*g+2*a+x==12*h+2*b+y)
                    need(same==((g,a,x)==(h,b,y)),'row label injectivity');truth+=1
        need(truth==1296,'complete row-label control population')
        for p,h in PINS.items():need(digest(ROOT/p)==h,'frozen input '+p);bindings[p]=h
        summary=read(RUN+'summary.json')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():need(digest(ROOT/p)==h,'raw producer binding '+p);bindings[p]=h
        need(read(ENC)['status']=='INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_CNF_PASS','exact template encoding premise')
        need(read(CENSUS_GATE)['status']=='INDEPENDENT_SIX_PRISM_COARSE60_TRIANGLE_COVER_SCOUT_PASS','independent finite census premise')
        words=read(SCOPE)['columns60'];cert=read(RUN+'certificate.json');groups,checks=verify(words,cert)
        census={tuple(r['columns']):r for r in read(CENSUS)['records']};ids=[]
        for group in groups:
            record=census[tuple(group)]
            need(record['all_same_components']==[] and record['required_opposite_bits']==[] and record['local_bit_assignments']==2**18,'selected triples impose no bit equations')
            ids.append(record['admissible_id'])
        for name,change in [
            ('duplicate_column',lambda c:c['orbits'][0].__setitem__(1,c['orbits'][0][0])),
            ('missing_class',lambda c:c['orbits'].pop()),
            ('wrong_class',lambda c:c['orbits'][0].__setitem__(1,c['orbits'][1][1])),
            ('wrong_rotation',lambda c:c['rotation_column_images'].__setitem__(0,0)),
            ('wrong_raw_word',lambda c:c['coarse_words'][0].__setitem__(0,2)),
            ('wrong_fibre_receipt',lambda c:c['component_fibres'][0][0].__setitem__(0,2)),
            ('wrong_population',lambda c:c.update(raw_bit_assignment_count_exact=str(2**359))),
            ('fabricated_factor',lambda c:c.update(research_factor=[])),
        ]:
            bad=deepcopy(cert);change(bad);reject(name,lambda:verify(words,bad),controls)
        save(out/'controls.json',dict(row_label_truth_cases=truth,corruptions=controls))
        save(out/'independent_classes.json',dict(schema='COARSE60_QUOTIENT_CLASS_COVER_V1',classes=groups,
            selected_admissible_ids=ids,all_local_pair_bit_checks=checks,
            proof='For every column pair in a class and every selected component/bit pair, literal row labels differ. Every possible shared row is among these8640checked local possibilities, so no global360-bit assignment can create an overlap.',
            semantic_extension='Set these20triple selectors true and all others false. Each column is covered once; chosen triples have no XOR implications; every unchosen implication is vacuous.'))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_COARSE60_CYCLIC_COVER.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[key(p)]=digest(p)
        need(all(digest(ROOT/p)==h for p,h in bindings.items()),'frozen input stability')
        report=dict(status='INDEPENDENT_COARSE60_ALL_BITS_DISJOINT_COVER_REDUNDANCY_PASS',created_at=now,updated_at=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=bindings,outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},
            claim_id='C-SIX-PRISM-COARSE60-UNIVERSAL-DISJOINT-COVER-REDUNDANCY',claim_revision=1,
            statement='For every assignment of all360 raw coordinate bits of the fixed60coarse columns, the recorded20 classes under uniform fibre rotation partition the columns into pairwise-disjoint incidence triples; consequently adding only existential exact-cover selectors and conditional opposite-bit requirements removes no raw-bit assignment in this template.',
            kind='mathematical result',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
            scope='Universal over all2^360rawbit assignments of one exact labelled60-column template, with no Gram, margin or residual-graph premise.',
            dependencies=[dict(id='C-SIX-PRISM-COARSE60-EXACT-BITLIFT-CNF',revision=1,relation='uses_result'),
                dict(id='C-SIX-PRISM-COARSE60-DISJOINT-TRIPLE-CENSUS-AND-COVER',revision=1,relation='uses_result')],
            assumptions=['The fixed60coarse-word template is explicit.','No hypothetical graph automorphism is assumed.'],
            verifier='/root/eight_domain_audit',method='independent_derivation_and_exact_artifact_check',
            shared_components=['Frozen raw template and separate independently checked encoding/census premises.','Only Python standard-library imports; no producer or earlier checker code.'],
            counts=dict(classes=20,columns=60,component_fibre_checks=120,column_pairs=60,universal_local_collision_checks=checks,
                calibration_truth_cases=truth,corruptions=len(controls),raw_bit_assignments_exact=str(2**360)),
            limitations=['No complete Gram factor, degree8 residual graph or target graph is provided.',
                'This establishes redundancy of the specified semantic existential cover condition; no new CNF implementation was built or audited.',
                'The actual residual mixed/quadratic equations and which triples are residual triangles are not redundant consequences.',
                'No other coarse templates covered; no novelty or target-wide coverage claim.'],
            artifact_availability='LOCAL_ONLY',retrieval='Exact report input/output paths are saved; immutable publication remains unconfirmed.',
            target_resolution=False,external_review=False,overall_search_coverage='UNKNOWN; no validated denominator.')
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=digest(out/'summary.json'))))
    except BaseException as exc:
        save(out/'failure.json',dict(error=repr(exc),source_sha256=digest(Path(__file__)),timestamp=datetime.now(timezone.utc).isoformat()));raise

if __name__=='__main__':main()
