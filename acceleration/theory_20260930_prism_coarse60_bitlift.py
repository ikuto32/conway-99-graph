"""Candidate exact joint CSP/SAT over audited local coarse60 domains; no solve."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import file_digest
from itertools import combinations, product
from pathlib import Path
import argparse
import gzip
import json
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
D = ROOT/'acceleration/results/20260930_prism_coarse_complement'
GATE = ROOT/'acceleration/results/20260930_independent_review/prism_coarse_complement/summary.json'
GATE_SHA = '7087ce1ff80ffd93e186c2e0d642bb99b1b003262f79bb19862e05015a8c590d'
SPEC = Path(__file__).with_name('theory_20260930_prism_coarse60_bitlift_spec.md')


def need(ok, why):
    if not ok: raise ValueError(why)


def digest(path):
    with Path(path).open('rb') as stream: return file_digest(stream,'sha256').hexdigest()


def key(path): return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, obj):
    with path.open('x',encoding='utf-8',newline='\n') as stream: json.dump(obj,stream,indent=2);stream.write('\n')


def onehot(selectors, next_id):
    clauses=[];prefix=[];previous=selectors[0]
    for selector in selectors[1:]:
        next_id+=1;current=next_id
        clauses.extend([[-previous,current],[-selector,current],[previous,selector,-current],[-previous,-selector]])
        prefix.append(dict(variable=current,previous=previous,selector=selector));previous=current
    clauses.append([previous])
    return clauses,prefix,next_id


def satisfied(clauses, values):
    return all(any(values[abs(v)] == (v>0) for v in clause) for clause in clauses)


def controls():
    cases=0;flips=0
    for n in range(1,8):
        clauses,prefix,top=onehot(list(range(1,n+1)),n)
        for bits in product((0,1),repeat=n):
            values={i+1:bool(b) for i,b in enumerate(bits)}
            for row in prefix:values[row['variable']]=values[row['previous']] or values[row['selector']]
            need(satisfied(clauses,values)==(sum(bits)==1),'complete small exact-one truth table');cases+=1
            if sum(bits)==1:
                for row in prefix:
                    bad=dict(values);bad[row['variable']]=not bad[row['variable']]
                    need(not satisfied(clauses,bad),'flipped prefix auxiliary rejected');flips+=1
    clauses=[]
    for bits in product((0,1),repeat=3):
        clauses.append([(-v if bit else v) for i,bit in enumerate(bits) for v in (2*i+1,2*i+2)])
    for bits in product((0,1),repeat=6):
        values={i+1:bool(b) for i,b in enumerate(bits)}
        need(satisfied(clauses,values)==(sum(bits[2*i]==bits[2*i+1] for i in range(3))<=2),'all64equality triple assignments')
    relation={0:[0,2],1:[1,2]};positive=negative=0
    for a,b in product(range(2),range(3)):
        values={1:a==0,2:a==1,3:b==0,4:b==1,5:b==2}
        rows=[[-(i+1),*(3+j for j in allowed)] for i,allowed in relation.items()]
        result=satisfied(rows,values);need(result==(b in relation[a]),'exact compatibility clause control')
        positive+=result;negative+=not result
    return dict(exact_one_truth_cases=cases,flipped_prefix_rejections=flips,equality_triple_truth_cases=64,
        compatibility_positive_cases=positive,compatibility_negative_cases=negative,full_research_factor_positive=None,
        full_research_factor_positive_null_reason='No full factor of this template known; these are local encoding controls.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();deadline=start+120
    need(digest(GATE)==GATE_SHA,'exact independent local-domain gate')
    gate=json.loads(GATE.read_bytes());need(gate['status']=='INDEPENDENT_SIX_PRISM_COARSE60_LOCAL_DOMAINS_PASS','independent domain status')
    pins=dict(gate['inputs_sha256']);pins[key(GATE)]=GATE_SHA
    for path,h in pins.items():need(digest(ROOT/path)==h,'frozen gate input '+path)
    for p in [Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[key(p)]=digest(p)
    save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
        question='Exact joint Gram and required column caps on one60-distinct coarse template?',scope='Fixed six-prism and fixed coarse multiplicities only.',
        limits=dict(build_seconds=120,solver_calls=0),thresholds=None,thresholds_null_reason='Integer clauses and equalities only.',random_seed=None,
        random_seed_null_reason='Deterministic complete encoding.',independent_approval=False))
    save(args.out/'controls.json',controls())
    raw=json.loads((D/'coarse_template.json').read_bytes());words=raw['columns60'];gram=raw['prescribed_gram36']
    domains=[]
    for a,g in product(range(6),range(3)):
        path=D/f'domain_{a}_{g}.json';data=json.loads(path.read_bytes());need(digest(path)==pins[key(path)],'every independent domain pin')
        positions=data['column_positions'];masks=data['survivors'];need(len(masks)==136 and len(set(masks))==136,'exact domain cardinality')
        need(positions==[d for d,w in enumerate(words) if w[a]==g],'literal domain positions')
        for mask in masks:need(type(mask)is int and 0<=mask<2**20 and mask.bit_count()==10,'literal domain mask')
        selector_ids=[1+(3*a+g)*136+j for j in range(136)]
        global_masks=[sum(((mask>>i)&1)<<d for i,d in enumerate(positions)) for mask in masks]
        domains.append(dict(component=a,fibre=g,source_path=key(path),source_sha256=digest(path),column_positions=positions,
            selectors=selector_ids,local_masks=masks,global_bit1_masks_hex=[format(mask,'015x') for mask in global_masks]))
    bits=[dict(variable=2449+6*d+a,column=d,component=a,fibre=words[d][a]) for d in range(60) for a in range(6)]
    body=args.out/'clauses.body';stream=body.open('x',encoding='ascii',newline='\n');clause_count=0;sections=[]
    def emit(clause):
        nonlocal clause_count
        need(clause and all(type(v)is int and v!=0 for v in clause),'nonempty integer clause')
        stream.write(' '.join(map(str,clause))+' 0\n');clause_count+=1
    top=2808;prefix_rows=[];section_start=clause_count+1
    for i,domain in enumerate(domains):
        clauses,prefix,top=onehot(domain['selectors'],top)
        for clause in clauses:emit(clause)
        prefix_rows.append(dict(domain=i,prefixes=prefix,final_unit=clauses[-1][0]))
    sections.append(dict(kind='exactly_one',first_clause=section_start,last_clause=clause_count,count=clause_count-section_start+1))
    section_start=clause_count+1
    for domain in domains:
        a=domain['component']
        for selector,mask in zip(domain['selectors'],domain['local_masks'],strict=True):
            for i,d in enumerate(domain['column_positions']):
                var=2449+6*d+a;emit([-selector,var if (mask>>i)&1 else -var])
    sections.append(dict(kind='selected_mask_bit_channels',first_clause=section_start,last_clause=clause_count,count=clause_count-section_start+1))
    relations=[];section_start=clause_count+1
    for a,b in combinations(range(6),2):
        for g,h in product(range(3),repeat=2):
            need(time.monotonic()<deadline,'build120second cap')
            left,right=3*a+g,3*b+h;ld,rd=domains[left],domains[right]
            target=gram[12*g+2*a+1][12*h+2*b+1];need(target==(1 if g==h else 2),'exact raw Gram relation target')
            right_masks=[int(s,16) for s in rd['global_bit1_masks_hex']];allowed=[];counts=[];first=clause_count+1
            for selector,mask_hex in zip(ld['selectors'],ld['global_bit1_masks_hex'],strict=True):
                mask=int(mask_hex,16);indices=[j for j,m in enumerate(right_masks) if (mask&m).bit_count()==target]
                emit([-selector,*[rd['selectors'][j] for j in indices]])
                allowed.append(format(sum(1<<j for j in indices),'034x'));counts.append(len(indices))
            relations.append(dict(left_domain=left,right_domain=right,target_bit11=target,allowed_right_masks_hex=allowed,
                row_allowed_counts=counts,allowed_pairs=sum(counts),forbidden_pairs=136**2-sum(counts),first_clause=first,last_clause=clause_count))
    sections.append(dict(kind='all135_Gram_compatibility_relations',first_clause=section_start,last_clause=clause_count,count=clause_count-section_start+1))
    caps=[];hist=Counter();section_start=clause_count+1
    for d,e in combinations(range(60),2):
        common=[a for a in range(6) if words[d][a]==words[e][a]];hist[len(common)]+=1
        need(len(common)<=4,'distinct balanced words agree in at most4positions')
        first=clause_count+1;triple_records=[]
        for triple in combinations(common,3):
            for values in product((0,1),repeat=3):
                clause=[]
                for a,value in zip(triple,values,strict=True):
                    for col in (d,e):
                        variable=2449+6*col+a;clause.append(-variable if value else variable)
                emit(clause)
            triple_records.append(list(triple))
        caps.append(dict(columns=[d,e],same_fibre_components=common,triples=triple_records,first_clause=first if triple_records else None,
            last_clause=clause_count if triple_records else None,clause_count=8*len(triple_records)))
    sections.append(dict(kind='all1770_required_Y_caps',first_clause=section_start,last_clause=clause_count,count=clause_count-section_start+1))
    stream.close();need(top==5238 and [s['count'] for s in sections[:3]]==[9738,48960,18360],'expected predeclared inventory')
    cnf=args.out/'instance.cnf'
    with cnf.open('xb') as dst,body.open('rb') as src:
        dst.write(f'p cnf {top} {clause_count}\n'.encode())
        for block in iter(lambda:src.read(1<<20),b''):dst.write(block)
    scope=dict(schema='FIXED_SIX_PRISM_DISTINCT60_BITLIFT_SCOPE_V1',columns60=words,core_adjacency39=raw['complete_raw39_adjacency'],target_gram36=gram,
        columns_each_once=True,coordinate_bits_free=True,full_Gram_required=True,all_distinct_column_caps_required=True,
        source_template_path=key(D/'coarse_template.json'),source_template_sha256=digest(D/'coarse_template.json'),
        canonical_C0_not_prescribed=True,no_complement_pairing=True,no_target_automorphism_assumed=True,residual_D_encoded=False,
        target_graph_encoded=False,unrestricted_prism_coverage=False)
    save(args.out/'scope.json',scope)
    model=dict(schema='SIX_PRISM_COARSE60_DOMAIN_CSP_CNF_V1',variables=top,clauses=clause_count,domain_selectors=2448,raw_bits=bits,
        domains=domains,exact_one_prefixes=prefix_rows,Gram_relations=relations,column_caps=caps,clause_sections=sections,
        same_fibre_component_histogram={str(k):v for k,v in sorted(hist.items())},scope_sha256=digest(args.out/'scope.json'),
        local_domain_gate=key(GATE),local_domain_gate_sha256=GATE_SHA,complete_target_graph=False,residual_D_encoded=False)
    save(args.out/'model.json',model)
    packages=[]
    for p in [cnf,body,args.out/'model.json']:
        rawbytes=p.read_bytes();compressed=gzip.compress(rawbytes,mtime=0);parts=[]
        from hashlib import sha256
        for offset in range(0,len(compressed),9*1024**2):
            part=args.out/(p.name+f'.gz.part{len(parts):03d}');part.write_bytes(compressed[offset:offset+9*1024**2])
            parts.append(dict(path=key(part),bytes=part.stat().st_size,sha256=digest(part)))
        need(gzip.decompress(compressed)==rawbytes,'lossless package identity')
        packages.append(dict(raw_path=key(p),raw_sha256=digest(p),raw_bytes=len(rawbytes),compressed_stream_sha256=sha256(compressed).hexdigest(),ordered_parts=parts))
    save(args.out/'artifact_packages.json',dict(packages=packages,mathematical_verification=False))
    need(all(digest(ROOT/p)==h for p,h in pins.items()),'stable frozen inputs')
    report=dict(status='CANDIDATE_COARSE60_JOINT_BITLIFT_CNF_BUILT',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        variables=top,clauses=clause_count,clause_sections=sections,domains=18,choices_per_domain=136,relations=len(relations),
        compatibility_allowed_pairs=sum(r['allowed_pairs'] for r in relations),compatibility_forbidden_pairs=sum(r['forbidden_pairs'] for r in relations),
        column_pairs=1770,same_fibre_component_histogram=model['same_fibre_component_histogram'],caps_clause_count=sections[-1]['count'],
        inputs_sha256=pins,outputs_sha256={key(p):digest(p) for p in args.out.iterdir() if p.is_file()},elapsed_seconds=time.monotonic()-start,
        solver_calls=0,independent_approval=False,target_resolution=False,scope='Only the frozen60distinct coarse-pattern six-prism family.',
        limitations=['No solver result or full factor produced.','No general six-prism or target coverage.','No canonicalC0/bitflip/complement normalization introduced.'])
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],variables=top,clauses=clause_count,caps=sections[-1]['count'],sha256=digest(args.out/'summary.json'))))


if __name__=='__main__':main()
