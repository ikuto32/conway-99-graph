"""Candidate exact coarse60 template and all18 single-row binary domains."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import file_digest
from itertools import combinations, permutations, product
from math import comb
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import time
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
SPEC = Path(__file__).with_name('theory_20260930_prism_coarse_complement_spec.md')


def need(ok, message):
    if not ok: raise ValueError(message)


def digest(path):
    with Path(path).open('rb') as stream: return file_digest(stream, 'sha256').hexdigest()


def save(path, obj):
    with path.open('x', encoding='utf-8', newline='\n') as stream: json.dump(obj, stream, indent=2);stream.write('\n')


def raw_gram():
    adjacency = [[0]*39 for _ in range(39)]
    def edge(a,b): adjacency[a][b] = adjacency[b][a] = 1
    for a,b in combinations(range(3),2): edge(a,b)
    for g in range(3):
        for a in range(12):
            edge(g,3+12*g+a);edge(3+12*g+a,3+12*g+(a^1))
    for a in range(12):
        for g,h in combinations(range(3),2): edge(3+12*g+a,3+12*h+a)
    gram = [[12*int(r==s)+2-adjacency[r+3][s+3]-sum(adjacency[r+3][v]*adjacency[s+3][v] for v in range(39)) for s in range(36)] for r in range(36)]
    return adjacency, gram


def quotas(words):
    return [dict(components=[a,b], fibres=[g,h], count=sum(w[a]==g and w[b]==h for w in words))
        for a,b in combinations(range(6),2) for g,h in product(range(3),repeat=2)]


def enumerate_domain(n, weight, constraints, limit=None):
    survivors = []; failures = Counter(); attempts = 0
    for chosen in combinations(range(n), weight):
        if attempts % 4096 == 0 and limit is not None: need(time.monotonic() < limit, '120second total cap')
        mask = sum(1<<i for i in chosen); attempts += 1
        failed = next((i for i,(bits,required) in enumerate(constraints) if (mask & bits).bit_count() != required), None)
        if failed is None: survivors.append(mask)
        else: failures[failed] += 1
    need(attempts == comb(n,weight) and attempts == len(survivors)+sum(failures.values()), 'complete disjoint enumeration accounting')
    return dict(attempts=attempts, survivors=survivors, first_failure_histogram={str(k):v for k,v in sorted(failures.items())})


def main():
    ap = argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args = ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);start = time.monotonic();deadline=start+120
    inputs = [Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml',
        ROOT/'docs/AUDIT_20260930_PRISM_ALL_COLUMNS.md',ROOT/'docs/AUDIT_20260930_PRISM_UNPAIRED_KERNEL.md',
        ROOT/'acceleration/results/20260930_prism_unpaired_design_pilot/model.json']
    pins={p.relative_to(ROOT).as_posix():digest(p) for p in inputs}
    save(args.out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=pins,
        question='Does the complement60 coarse template satisfy quotas and every necessary single-row bit domain?',
        scope='One fixed six-prism template; no joint feasibility, residual completion or general coverage.',
        seconds_limit=120,thresholds=None,thresholds_null_reason='Exact integer equality only.',random_seed=None,random_seed_null_reason='Deterministic complete enumerations.',independent_approval=False))
    controls = dict(positive=enumerate_domain(4,2,[(3,1),(12,1)]),negative=enumerate_domain(4,2,[(1,2)]))
    need(controls['positive']['survivors'] == [5,9,6,10] and not controls['negative']['survivors'], 'known control exact domains')
    universe = [list(w) for w in product(range(3),repeat=6) if all(w.count(g)==2 for g in range(3))]
    removed=[];matchings=[]
    for t in range(5):
        matching=[[5,t],[(t+1)%5,(t-1)%5],[(t+2)%5,(t-2)%5]];matchings.append(matching)
        for labels in permutations(range(3)):
            word=[None]*6
            for pair,g in zip(matching,labels):
                for a in pair:word[a]=g
            removed.append(word)
    old=json.loads(inputs[-1].read_bytes());need(removed==[p['cells'] for p in old['patterns']], 'same frozen old30 word convention')
    words=[w for w in universe if w not in removed]
    need(len(universe)==90 and len(removed)==len({tuple(w) for w in removed})==30 and len(words)==60,'exact90minus30 populations')
    adjacency,gram=raw_gram(); qfull,qremoved,qleft=map(quotas,[universe,removed,words])
    for a,b,c in zip(qfull,qremoved,qleft,strict=True):
        component_a,component_b=c['components'];g,h=c['fibres']
        target=sum(gram[12*g+2*component_a+bit_a][12*h+2*component_b+bit_b] for bit_a,bit_b in product((0,1),repeat=2))
        need(a['count']==(6 if g==h else 12) and b['count']==(2 if g==h else 4) and c['count']==target==(4 if g==h else 8),'raw Gram aggregates and exact coarse quotas')
    need(all(sum(w[a]==g for w in words)==20 for a in range(6) for g in range(3)),'all18coarse margins')
    raw=dict(schema='SIX_PRISM_DISTINCT60_COARSE_TEMPLATE_V1',component_labels=list(range(6)),fibre_labels=list(range(3)),
        universe90=universe,removed_round_robin30=removed,matchings=matchings,columns60=words,multiplicities=[int(w in words) for w in universe],
        complete_raw39_adjacency=adjacency,prescribed_gram36=gram,all135_pair_quotas=qleft,full90_pair_quotas=qfull,removed30_pair_quotas=qremoved,
        coordinate_bits_assigned=False,complement_pairing_assumed=False,target_automorphism_assumed=False)
    save(args.out/'coarse_template.json',raw)
    controls['corruptions_rejected']=[]
    bad=words[:-1]
    need(quotas(bad)!=qleft,'removed-column corrupt quota');controls['corruptions_rejected'].append('missing_column_changes_quotas')
    bad=[w[:] for w in words];bad[0][0]=3
    need(not all(set(w)<=set(range(3)) and all(w.count(g)==2 for g in range(3)) for w in bad),'nonfibre label control');controls['corruptions_rejected'].append('invalid_fibre')
    save(args.out/'controls.json',controls)
    records=[]
    try:
        for a,g in tqdm(list(product(range(6),range(3))),desc='Exact component/fibre bit domains'):
            positions=[d for d,w in enumerate(words) if w[a]==g];need(len(positions)==20,'every local domain20')
            constraints=[];metadata=[]
            for b in range(6):
                if b==a:continue
                for h in range(3):
                    subset=[i for i,d in enumerate(positions) if words[d][b]==h]
                    required=sum(gram[12*g+2*a+1][12*h+2*b+bit] for bit in range(2))
                    need(len(subset)==2*required and required==(2 if g==h else 4),'raw marginal half target')
                    constraints.append((sum(1<<i for i in subset),required));metadata.append(dict(other_component=b,other_fibre=h,local_positions=subset,required_bit1_count=required))
            result=enumerate_domain(20,10,constraints,deadline)
            for mask in result['survivors']:
                need(mask.bit_count()==10 and all((mask&bits).bit_count()==required for bits,required in constraints),'every saved survivor exact')
            record=dict(component=a,fibre=g,column_positions=positions,constraints=metadata,**result)
            save(args.out/f'domain_{a}_{g}.json',record);records.append(dict(component=a,fibre=g,attempts=result['attempts'],survivors=len(result['survivors']),path=(args.out/f'domain_{a}_{g}.json').resolve().relative_to(ROOT).as_posix()))
    except BaseException as error:
        save(args.out/'failure.json',dict(error=repr(error),completed_domains=len(records),records=records,elapsed_seconds=time.monotonic()-start));raise
    need(len(records)==18,'all18completed')
    report=dict(status='CANDIDATE_COARSE60_SINGLE_ROW_DOMAIN_SCOUT_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs_sha256=pins,
        template=dict(universe_patterns=90,removed_patterns=30,selected_distinct_patterns=60,selected_columns=60,coarse_pair_equations=135),
        domains=records,completed_domains=18,balanced_bit_assignments_per_domain=comb(20,10),
        total_local_assignments_attempted=sum(r['attempts'] for r in records),sum_domain_survivors=sum(r['survivors'] for r in records),
        empty_domains=sum(r['survivors']==0 for r in records),scope='One60-distinct-pattern template, no joint bit-lift or graph supplied.',
        independent_approval=False,target_resolution=False,solver_calls=0,novelty_claim=False,
        limitations=['All18local domains being nonempty does not imply joint bit feasibility.','No prescribed C0 coordinate-bit pairing has been imposed; future normalization relabels columns after a bit lift.',
            'This fixed-core and fixed-template construction does not cover all coarse integer solutions.', 'Prior30x2 exclusion cannot be applied merely because both templates share pair quotas.'],
        outputs_sha256={p.resolve().relative_to(ROOT).as_posix():digest(p) for p in args.out.iterdir() if p.is_file()},elapsed_seconds=time.monotonic()-start)
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],empty_domains=report['empty_domains'],domain_counts=[r['survivors'] for r in records],sha256=digest(args.out/'summary.json'))))


if __name__=='__main__':main()
