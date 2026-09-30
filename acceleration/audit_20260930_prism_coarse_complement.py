"""Independent coarse60 geometry and complete local-domain audit; no producer imports."""
from collections import Counter,defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import file_digest
from itertools import combinations,product
from math import comb,factorial
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'acceleration/results/20260930_prism_coarse_complement'
SUMMARY_SHA='1404fbf9a089ae0f1136e10e5d34e1210197a16e2ed30d4a75acc7f038bae170'
BASE_GATE=ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json'
BASE_SHA='07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3'
DOC=ROOT/'docs/AUDIT_20260930_PRISM_COARSE_COMPLEMENT.md'

def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(path):
    with Path(path).open('rb') as f:return file_digest(f,'sha256').hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def stamp():return datetime.now(timezone.utc).isoformat()
def save(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')

def geometry():
    # Construct from vertex labels and adjacency predicates, not producer edge loops.
    labels=[('root',g) for g in range(3)]+[(g,a,b) for g in range(3) for a in range(6) for b in range(2)]
    adjacency=[]
    for i,x in enumerate(labels):
        row=[]
        for j,y in enumerate(labels):
            if i==j:edge=False
            elif i<3 and j<3:edge=True
            elif i<3:edge=x[1]==y[0]
            elif j<3:edge=x[0]==y[1]
            else:edge=x[1]==y[1] and ((x[0]==y[0] and x[2]!=y[2]) or (x[0]!=y[0] and x[2]==y[2]))
            row.append(int(edge))
        adjacency.append(row)
    neighbours=[{j for j,x in enumerate(row) if x} for row in adjacency]
    gram=[[12*int(i==j)+2-adjacency[3+i][3+j]-len(neighbours[3+i]&neighbours[3+j]) for j in range(36)] for i in range(36)]
    return adjacency,gram

def population():
    words=[]
    # Select cell0 and cell1 supports; the complement is cell2. This bijection
    # gives C(6,2)*C(4,2)=90 without iterating producer's 3^6 words.
    for first in combinations(range(6),2):
        remaining=[a for a in range(6) if a not in first]
        for second in combinations(remaining,2):
            words.append(tuple(0 if a in first else 1 if a in second else 2 for a in range(6)))
    words=sorted(words);need(len(words)==len(set(words))==factorial(6)//(factorial(2)**3)==90,'complete balanced population')
    # Finite-field description: the non-infinity edge endpoints sum to2t mod5.
    matching_sets=[frozenset([frozenset((5,t))]+[frozenset((a,b)) for a,b in combinations(range(5),2) if (a+b)%5==(2*t)%5]) for t in range(5)]
    removed=[]
    for word in words:
        matching=frozenset(frozenset(i for i,g in enumerate(word) if g==h) for h in range(3))
        if matching in matching_sets:removed.append(word)
    left=[word for word in words if word not in removed]
    need(len(removed)==30 and len(left)==60 and len(set(left))==60,'90 minus frozen30')
    return words,removed,left,matching_sets

def quotas(words):
    return [dict(components=[a,b],fibres=[g,h],count=sum(word[a]==g and word[b]==h for word in words))
        for a,b in combinations(range(6),2) for g,h in product(range(3),repeat=2)]

def check_template(raw,old):
    universe,removed,left,matchings=population();adjacency,gram=geometry()
    need(raw['universe90']==list(map(list,universe)),'all90 exact lex words')
    need(sorted(map(tuple,raw['removed_round_robin30']))==removed and sorted(tuple(x['cells']) for x in old['patterns'])==removed,'exact prior30 set, no multiplicity inference')
    need(raw['columns60']==list(map(list,left)) and raw['multiplicities']==[int(w in left) for w in universe],'exact60 distinct template and complete multiplicity vector')
    need(raw['component_labels']==list(range(6)) and raw['fibre_labels']==list(range(3)),'literal label sets')
    need([frozenset(map(frozenset,m)) for m in raw['matchings']]==matchings,'five finite-field matching definitions')
    need(raw['complete_raw39_adjacency']==adjacency and raw['prescribed_gram36']==gram,'literal raw39-derived prescribed Gram')
    for field,pop in [('full90_pair_quotas',universe),('removed30_pair_quotas',removed),('all135_pair_quotas',left)]:need(raw[field]==quotas(pop),'complete pair quota table '+field)
    for a,b in combinations(range(6),2):
        for g,h in product(range(3),repeat=2):
            count=sum(w[a]==g and w[b]==h for w in left)
            raw_sum=sum(gram[12*g+2*a+x][12*h+2*b+y] for x,y in product(range(2),repeat=2))
            need(count==raw_sum==(4 if g==h else 8),'coarse raw Gram necessity')
    need(all(sum(w[a]==g for w in left)==20 for a,g in product(range(6),range(3))),'18 exact cell margins')
    need(raw['coordinate_bits_assigned'] is False and raw['complement_pairing_assumed'] is False and raw['target_automorphism_assumed'] is False,'declared narrow domain')
    return left,adjacency,gram

def signatures(width,subsets):
    return [tuple(sum((mask>>j)&1 for j in subset) for subset in subsets) for mask in range(1<<width)]

def meet(n,weight,subsets,targets):
    """Exact disjoint half-mask join; also all first-failure counts by prefix joins."""
    need(0<=weight<=n and len(subsets)==len(targets),'valid finite domain dimensions')
    half=n//2;allsets=[list(range(n)),*subsets];goals=[weight,*targets]
    ls=signatures(half,[[j for j in group if j<half] for group in allsets])
    rs=signatures(n-half,[[j-half for j in group if j>=half] for group in allsets])
    need(len(ls)==1<<half and len(rs)==1<<(n-half),'complete unique half-mask populations')
    prefix_counts=[];survivors=[]
    for length in range(1,len(goals)+1):
        indexed=defaultdict(list)
        for mask,sig in enumerate(ls):indexed[sig[:length]].append(mask)
        count=0
        for right,sig in enumerate(rs):
            target=tuple(goals[i]-sig[i] for i in range(length));matches=indexed.get(target,[]);count+=len(matches)
            if length==len(goals):survivors.extend(left+(right<<half) for left in matches)
        prefix_counts.append(count)
    need(prefix_counts[0]==comb(n,weight),'full balanced population via independent half-mask join')
    need(all(a>=b for a,b in zip(prefix_counts,prefix_counts[1:])),'nested prefix populations')
    failures={str(i):prefix_counts[i]-prefix_counts[i+1] for i in range(len(subsets)) if prefix_counts[i]!=prefix_counts[i+1]}
    return dict(survivors=sorted(survivors),prefix_survivor_counts=prefix_counts,first_failure_histogram=failures,
        full_binary_population=1<<n,balanced_population=prefix_counts[0],half_populations=[len(ls),len(rs)])

def reconstruct_domain(words,gram,a,g):
    positions=[i for i,w in enumerate(words) if w[a]==g];metadata=[];subsets=[];targets=[]
    for b in range(6):
        if b==a:continue
        for h in range(3):
            subset=[j for j,i in enumerate(positions) if words[i][b]==h]
            target=sum(gram[12*g+2*a+1][12*h+2*b+bit] for bit in range(2))
            need(len(subset)==2*target and target==(2 if g==h else 4),'literal bit marginal half-count')
            subsets.append(subset);targets.append(target)
            metadata.append(dict(other_component=b,other_fibre=h,local_positions=subset,required_bit1_count=target))
    return positions,metadata,subsets,targets

def check_domain(raw,a,g,positions,metadata,expected):
    need(raw['component']==a and raw['fibre']==g and raw['column_positions']==positions,'domain exact coordinate identity')
    need(raw['constraints']==metadata,'complete independent marginal metadata')
    masks=raw['survivors'];need(all(type(x)is int and 0<=x<(1<<20) for x in masks),'literal20-bit masks')
    need(len(masks)==len(set(masks)) and sorted(masks)==expected['survivors'],'all and only independently enumerated survivors')
    need(masks==sorted(masks,key=lambda m:tuple(i for i in range(20) if (m>>i)&1)),'declared lex combination order')
    need(raw['attempts']==expected['balanced_population'] and raw['first_failure_histogram']==expected['first_failure_histogram'],'exact denominator and complete first-failure histogram')
    need(all(((1<<20)-1)^m in set(masks) for m in masks),'complement involution from half-count conditions')

def controls():
    positives=0
    # All single-subset quota domains for up to five coordinates, compared to
    # literal Boolean tuple enumeration rather than the half join.
    for n in range(1,6):
        for subsetmask in range(1<<n):
            subset=[i for i in range(n) if subsetmask>>i&1]
            for weight in range(n+1):
                for target in range(len(subset)+2):
                    expected=sorted(sum(bit<<i for i,bit in enumerate(bits)) for bits in product(range(2),repeat=n) if sum(bits)==weight and sum(bits[i] for i in subset)==target)
                    actual=meet(n,weight,[subset],[target]);need(actual['survivors']==expected,'exhaustive small quota positive/impossible control');positives+=1
    need(meet(4,2,[[0,1],[2,3]],[1,1])['survivors']==[5,6,9,10],'two-constraint positive control')
    parity=[]
    for bits in product(range(2),repeat=4):
        counts=[bits.count(0),bits.count(1)];need(sum(counts)==4,'literal binary partition');parity.append(counts)
    return dict(exhaustive_small_quota_cases=positives,two_constraint_positive=True,known_impossible_domains_included=True,
        binary_four_position_controls=16,algorithm='Two independent half-mask enumerations joined by exact integer signatures; expected small controls enumerate Boolean tuples.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();bindings={}
    def bind(path,identity=None):
        value=digest(path);need(identity is None or value==identity,'exact artifact identity '+str(path));bindings[key(path)]=value;return path
    def read(path,identity=None):return json.loads(bind(path,identity).read_bytes())
    try:
        summary=read(DATA/'summary.json',SUMMARY_SHA);manifest=read(DATA/'manifest.json')
        for p,h in summary['inputs_sha256'].items():bind(ROOT/p,h)
        for p,h in summary['outputs_sha256'].items():bind(ROOT/p,h)
        need(summary['status']=='CANDIDATE_COARSE60_SINGLE_ROW_DOMAIN_SCOUT_COMPLETE','frozen completed scout')
        gate=read(BASE_GATE,BASE_SHA);need(gate['status']=='INDEPENDENT_SIX_PRISM_ALL_COLUMNS_CNF_ENCODING_PASS','prior independent geometry gate')
        raw=read(DATA/'coarse_template.json');old=read(ROOT/'acceleration/results/20260930_prism_unpaired_design_pilot/model.json')
        control=controls();words,adj,gram=check_template(raw,old);rejected=[]
        for name in ['missing_column','duplicated_column','invalid_cell','changed_quota','changed_Gram','changed_adjacency','wrong_multiplicity']:
            bad=deepcopy(raw)
            if name=='missing_column':bad['columns60'].pop()
            elif name=='duplicated_column':bad['columns60'][1]=bad['columns60'][0]
            elif name=='invalid_cell':bad['columns60'][0][0]=3
            elif name=='changed_quota':bad['all135_pair_quotas'][0]['count']+=1
            elif name=='changed_Gram':bad['prescribed_gram36'][0][1]+=1
            elif name=='changed_adjacency':bad['complete_raw39_adjacency'][0][1]=0
            else:bad['multiplicities'][0]=2
            try:check_template(bad,old)
            except ValueError:rejected.append(name)
            else:raise ValueError('corrupt template accepted '+name)
        records=[];derived=[]
        for a,g in product(range(6),range(3)):
            positions,metadata,subsets,targets=reconstruct_domain(words,gram,a,g);expected=meet(20,10,subsets,targets)
            domain=read(DATA/f'domain_{a}_{g}.json');check_domain(domain,a,g,positions,metadata,expected)
            if a==g==0:
                for name in ['missing_survivor','duplicated_survivor','invalid_bit','changed_bits','wrong_positions','wrong_target','wrong_histogram','wrong_denominator']:
                    bad=deepcopy(domain)
                    if name=='missing_survivor':bad['survivors'].pop()
                    elif name=='duplicated_survivor':bad['survivors'].append(bad['survivors'][0])
                    elif name=='invalid_bit':bad['survivors'][0]|=1<<20
                    elif name=='changed_bits':bad['survivors'][0]^=1
                    elif name=='wrong_positions':bad['column_positions'][0]+=1
                    elif name=='wrong_target':bad['constraints'][0]['required_bit1_count']+=1
                    elif name=='wrong_histogram':bad['first_failure_histogram']['0']+=1
                    else:bad['attempts']-=1
                    try:check_domain(bad,a,g,positions,metadata,expected)
                    except ValueError:rejected.append(name)
                    else:raise ValueError('corrupt domain accepted '+name)
            need(len(expected['survivors'])==136,'actual verified finite domain count')
            records.append(dict(component=a,fibre=g,balanced_population=expected['balanced_population'],survivors=len(expected['survivors']),complement_pairs=len(expected['survivors'])//2))
            derived.append(dict(component=a,fibre=g,positions=positions,**expected))
            print(json.dumps(records[-1]),flush=True)
        need(summary['completed_domains']==18 and summary['total_local_assignments_attempted']==18*comb(20,10) and summary['sum_domain_survivors']==18*136 and summary['empty_domains']==0,'programmatic producer summary counts')
        for saved,record in zip(summary['domains'],records,strict=True):
            need(saved['component']==record['component'] and saved['fibre']==record['fibre'] and saved['attempts']==record['balanced_population'] and saved['survivors']==record['survivors'],'every summary domain count')
        save(args.out/'independent_domains.json',dict(complete_population='18 distinct component/fibre local domains, each all2^20 bits filtered by weight10 and15 exact marginal equations.',records=derived))
        save(args.out/'raw_geometry.json',dict(raw39_adjacency=adj,prescribed_gram36=gram,columns60=list(map(list,words))))
        control['corrupted_artifacts_rejected']=rejected;save(args.out/'controls.json',control)
        for p in [Path(__file__),DOC,ROOT/'uv.lock',ROOT/'pyproject.toml']:bind(p)
        need(all(digest(ROOT/p)==h for p,h in bindings.items()),'all bound inputs stayed frozen')
        now=stamp();report=dict(status='INDEPENDENT_SIX_PRISM_COARSE60_LOCAL_DOMAINS_PASS',claim_id='C-SIX-PRISM-COMPLEMENT60-SINGLE-ROW-DOMAINS',claim_revision=1,
            statement='The exact60 distinct balanced cell patterns obtained by removing the frozen30 round-robin patterns from all90 have every required coarse pair quota4/8 and all18component/cell margins20; for each of its18local20-bit component/cell assignments, exactly136 of all184756weight10 words satisfy all15 prescribed single-row Gram marginals, with the complete survivor lists and first-failure counts independently reproduced.',
            kind='empirical/engineering result',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
            scope='Exactly one selected fixed-six-prism60-pattern template and all of its18local single-row domains; not a joint bit lift, full factor, residual completion or target graph.',
            dependencies=[dict(id='C-SIX-PRISM-COMPLETE-COLUMN-FACTOR-CNF',revision=1,relation='verification_dependency')],
            assumptions=['Fixed six-prism core and this explicit multiplicity0/1 coarse template.','No target automorphism and no bit-complement column-pair restriction.'],
            verifier='/root/eight_domain_audit independent geometry/count and complete half-mask-join enumeration',method='independent_artifact_check_and_derivation',
            shared_components=['Python standard library, frozen raw prior30 pattern convention and separately verified six-prism geometry premise. No producer imports, combinatorial subset enumerator, or scorer reused.'],
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),
            uv_version=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=bindings,
            records=records,raw_patterns=60,local_domains=18,balanced_words_per_domain=comb(20,10),
            sum_local_balanced_word_populations=18*comb(20,10),sum_local_survivor_populations=18*136,
            empty_local_domains=0,local_complement_pairs=18*68,controls=control,
            coverage='Complete local18×184756word population checked by exact disjoint half-mask joins. This is no global360-bit domain coverage or target-wide measure.',
            limitations=['Nonempty local domains need not admit mutually compatible bits across components.',
                'The prior30-pattern-each-twice exclusion does not apply to this disjoint60-pattern-support family.',
                'No blanket approval of the producer source or future CSP/SAT encoding.',
                'No novelty, full-factor existence, core exclusion, unrestricted coverage, or target resolution.'],
            producer_run_source_commit=manifest['source_commit'],producer_command=manifest['command'],
            outputs_sha256={key(p):digest(p) for p in args.out.iterdir() if p.is_file()},
            created_at=now,updated_at=now,elapsed_seconds=time.monotonic()-start,artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as error:save(args.out/'failure.json',dict(timestamp=stamp(),error=repr(error)));raise

if __name__=='__main__':main()
