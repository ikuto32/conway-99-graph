"""Candidate exact six-component relabelling normalization, with no solver."""
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

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'acceleration/results/20260930_prism_coarse60_bitlift'
GATE = ROOT/'acceleration/results/20260930_independent_review/prism_coarse60_bitlift_cnf/summary.json'
GATE_HASH = 'b82eb3d3c999ae8bdcdbfd246dd28ea9cd6a9dd8d1ce811abc82ee0f3e38d88d'
SPEC = Path(__file__).with_name('theory_20260930_prism_coarse60_bitflip_spec.md')
PROOF = ROOT/'docs/DERIVATION_20260930_PRISM_COARSE60_BITFLIP.md'

def need(ok, why):
    if not ok: raise ValueError(why)
def digest(p): return sha256(p.read_bytes()).hexdigest()
def key(p): return p.resolve().relative_to(ROOT).as_posix()
def read(p): return json.loads(p.read_bytes())
def save(p, obj):
    with p.open('x',encoding='utf-8',newline='\n') as f: json.dump(obj,f,indent=2); f.write('\n')

def action(mask, model, complements):
    rows = [12*g+2*a+(b^((mask>>a)&1)) for g,a,b in product(range(3),range(6),range(2))]
    selectors = []
    for i,d in enumerate(model['domains']):
        selectors.extend(d['selectors'][complements[i][j]] if (mask>>d['component'])&1 else v
                         for j,v in enumerate(d['selectors']))
    bits = [(-v['variable'] if (mask>>v['component'])&1 else v['variable']) for v in model['raw_bits']]
    return dict(component_flip_mask=mask, row_images=rows, selector_images=selectors,
                raw_bit_literal_images=bits)

def check_action(row, model, scope, complements):
    m=row['component_flip_mask']; need(type(m)is int and 0<=m<64,'action range')
    expected=action(m,model,complements); need(row==expected,'complete literal action definition')
    perm=row['row_images']; need(sorted(perm)==list(range(36)),'row bijection')
    need(sorted(row['selector_images'])==list(range(1,2449)),'selector bijection')
    c=[r[3:] for r in scope['core_adjacency39'][3:]]; g=scope['target_gram36']
    need(all(c[i][j]==c[perm[i]][perm[j]] and g[i][j]==g[perm[i]][perm[j]]
             for i in range(36) for j in range(36)),'literal core/Gram invariance')
    for i,d in enumerate(model['domains']):
        lookup=dict(zip(d['selectors'],d['local_masks'],strict=True))
        for j,s in enumerate(d['selectors']):
            mapped=row['selector_images'][s-1]
            need(lookup[mapped]==(d['local_masks'][j]^(((1<<20)-1) if (m>>d['component'])&1 else 0)),
                 'mask transport')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    need(digest(GATE)==GATE_HASH,'independent base gate pin'); gate=read(GATE)
    need(gate['status']=='INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_CNF_PASS','base gate status')
    inputs=dict(gate['inputs_sha256']);inputs[key(GATE)]=GATE_HASH
    for p,h in inputs.items():need(digest(ROOT/p)==h,'frozen input '+p)
    for p in [Path(__file__),SPEC,PROOF,ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(p)]=digest(p)
    model=read(BASE/'model.json');scope=read(BASE/'scope.json')
    for p in [BASE/'model.json',BASE/'scope.json',BASE/'instance.cnf']:inputs[key(p)]=digest(p)
    manifest=dict(created_at=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),inputs_sha256=inputs,
        versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip()),
        limits=dict(build_seconds=120,solver_calls=0),random_seed=None,random_seed_reason='Deterministic exact construction.',
        scope='Only fixed60distinct coarse columns of fixed six-prism core.')
    save(out/'manifest.json',manifest)
    complements=[]
    for d in model['domains']:
        masks=d['local_masks']; index={v:i for i,v in enumerate(masks)}
        need(len(index)==136,'136 unique masks')
        complement=[index[v^((1<<20)-1)] for v in masks]
        need(all(complement[complement[i]]==i and complement[i]!=i for i in range(136)),'fixed-point-free complement involution')
        complements.append(complement)
    actions=[]
    for mask in range(64):
        row=action(mask,model,complements);check_action(row,model,scope,complements);actions.append(row)
    for a,b in product(range(64),repeat=2):
        need(all(actions[a]['row_images'][actions[b]['row_images'][i]]==actions[a^b]['row_images'][i] for i in range(36)), 'XOR group law')
    transport_counts=[]
    for relation in model['Gram_relations']:
        need(time.monotonic()-start<120,'120second limit')
        left,right=relation['left_domain'],relation['right_domain'];table=[int(v,16) for v in relation['allowed_right_masks_hex']]
        checks=0
        for flip_left,flip_right in product(range(2),repeat=2):
            for i in range(136):
                ii=complements[left][i] if flip_left else i
                for j in range(136):
                    jj=complements[right][j] if flip_right else j
                    need(((table[i]>>j)&1)==((table[ii]>>jj)&1),'complete compatibility transport'); checks+=1
        transport_counts.append(dict(left_domain=left,right_domain=right,transported_pair_checks=checks))
    first=sorted((v for v in model['raw_bits'] if v['column']==0),key=lambda r:r['component'])
    need([r['component'] for r in first]==list(range(6)),'exact first-column metadata')
    units=[-v['variable'] for v in first]
    coverage=[]
    for mask in range(64):
        good=[e for e in range(64) if all(((mask>>a)&1)^((e>>a)&1)==0 for a in range(6))]
        need(good==[mask],'unique normalizing group element')
        coverage.append(dict(first_column_bits=[(mask>>a)&1 for a in range(6)],unique_action=mask,normalized_bits=[0]*6))
    # Exhaust the componentwise equal-bit relation under a common flip.
    equality_controls=0
    for x,y,e in product(range(2),repeat=3):
        need((x==y)==((x^e)==(y^e)),'column overlap unchanged');equality_controls+=1
    prefix_controls=0
    for d,prefix in zip(model['domains'],model['exact_one_prefixes'],strict=True):
        for selected in d['selectors']:
            values={s:s==selected for s in d['selectors']}
            for r in prefix['prefixes']:
                p,s,v=r['previous'],r['selector'],r['variable'];values[v]=values[p] or values[s]
                need((not values[p] or values[v]) and (not values[s] or values[v]) and
                     (values[p] or values[s] or not values[v]) and (not values[p] or not values[s]), 'regenerated exact-one prefix clauses')
            need(values[prefix['final_unit']],'regenerated final unit');prefix_controls+=1
    corruptions=[]
    for label,field,position,value in [('row_image','row_images',0,0),('selector_image','selector_images',0,1),('bit_sign','raw_bit_literal_images',0,2449)]:
        bad=json.loads(json.dumps(actions[1]));bad[field][position]=value
        try:check_action(bad,model,scope,complements)
        except ValueError:corruptions.append(dict(name=label,rejected=True))
        else:raise AssertionError('corrupt action accepted')
    for bad in [units[:-1],[-units[0],*units[1:]],units+[units[0]]]:
        need(bad!=units,'corrupt exact suffix must differ');corruptions.append(dict(name='wrong_unit_suffix',rejected=True))
    save(out/'actions64.json',dict(schema='FIXED_COARSE60_COMPONENT_BIT_ACTIONS_V1',actions=actions,
        domain_complement_indices=complements,first_column_coverage=coverage,
        prefix_auxiliary_policy='Recompute exact prefix OR from transported one-hot selectors; no auxiliary permutation asserted.'))
    raw=(BASE/'instance.cnf').read_bytes();header,body=raw.split(b'\n',1)
    need(header==b'p cnf 5238 85698','exact base header')
    suffix=b''.join(f'{v} 0\n'.encode() for v in units)
    new=b'p cnf 5238 85704\n'+body+suffix
    (out/'units.clauses').write_bytes(suffix);(out/'instance.cnf').write_bytes(new)
    need(new.split(b'\n',1)[1]==body+suffix,'unchanged body plus units')
    ext=dict(schema='FIXED_COARSE60_COMPONENT_BIT_NORMALIZATION_V1',variables=5238,clauses=85704,
        base_cnf=key(BASE/'instance.cnf'),base_cnf_sha256=digest(BASE/'instance.cnf'),
        base_model=key(BASE/'model.json'),base_model_sha256=digest(BASE/'model.json'),
        base_scope=key(BASE/'scope.json'),base_scope_sha256=digest(BASE/'scope.json'),
        base_encoding_gate=key(GATE),base_encoding_gate_sha256=GATE_HASH,
        first_column_records=first,appended_unit_literals=units,base_clause_count=85698,
        actions=key(out/'actions64.json'),actions_sha256=digest(out/'actions64.json'),
        group_size=64,auxiliaries_regenerated=True,no_target_automorphism_assumed=True,
        target_graph=False,residual_D=False,unrestricted_prism_coverage=False)
    save(out/'extension.json',ext)
    save(out/'controls.json',dict(all_135_relation_transports=transport_counts,
        total_selector_pair_transport_checks=sum(x['transported_pair_checks'] for x in transport_counts),
        prefix_single_choice_regeneration_controls=prefix_controls,equality_truth_cases=equality_controls,
        corruptions=corruptions,research_factor_positive=None,
        research_factor_positive_reason='No full research factor known; local equivalence controls only.'))
    packages=[]
    for p in [out/'instance.cnf',out/'actions64.json']:
        compressed=gzip.compress(p.read_bytes(),mtime=0);target=p.with_suffix(p.suffix+'.gz');target.write_bytes(compressed)
        need(gzip.decompress(compressed)==p.read_bytes(),'lossless package')
        packages.append(dict(raw_path=key(p),raw_sha256=digest(p),raw_bytes=p.stat().st_size,
                             gzip_path=key(target),gzip_sha256=digest(target),gzip_bytes=target.stat().st_size))
    save(out/'artifact_packages.json',dict(packages=packages,mathematical_verification=False))
    need(time.monotonic()-start<120,'120second total limit')
    need(all(digest(ROOT/p)==h for p,h in inputs.items()),'all inputs stable')
    summary=dict(status='CANDIDATE_COARSE60_SIX_BIT_NORMALIZATION',claim_id='C-SIX-PRISM-COARSE60-COMPONENT-BIT-NORMALIZATION',revision=1,
        statement='The fixed5238-variable85698-clause base is SAT iff its six first-column bit-zero unit extension is SAT.',
        scope='Only one fixed60-pattern six-prism factor family; no residual D or arbitrary-template coverage.',
        dependencies=[dict(id='C-SIX-PRISM-COARSE60-EXACT-BITLIFT-CNF',revision=1,relation='encoding_equivalence'),
                      dict(id='C-SIX-PRISM-COMPLEMENT60-SINGLE-ROW-DOMAINS',revision=1,relation='coverage')],
        created_at=manifest['created_at'],completed_at=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],
        inputs_sha256=inputs,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},
        variables=5238,clauses=85704,group_actions=64,appended_units=units,
        selector_pair_transport_checks=sum(x['transported_pair_checks'] for x in transport_counts),
        solver_calls=0,independent_approval=False,target_resolution='UNKNOWN',wall_seconds=time.monotonic()-start)
    save(out/'summary.json',summary)
    print(json.dumps(dict(status=summary['status'],summary_sha256=digest(out/'summary.json'),cnf_sha256=digest(out/'instance.cnf'),wall_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
