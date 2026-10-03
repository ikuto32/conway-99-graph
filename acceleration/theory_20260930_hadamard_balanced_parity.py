"""Candidate exact S3 reduction and tiny parity CNF; no solver calls."""
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations,permutations,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
RAW=B+'hadamard20_support/six_prism.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 B+'hadamard_triplicate_counts/local_triples.json':'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',
 B+'independent_review/hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88'}
def need(ok,why):
    if not ok:raise ValueError(why)
def h(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,obj):
    with path.open('x',encoding='utf-8',newline='\n')as stream:json.dump(obj,stream,indent=2);stream.write('\n')
def compositions(total,length):
    if length==1:yield(total,);return
    for first in range(total+1):
        for rest in compositions(total-first,length-1):yield(first,*rest)
def parity(p):return sum(p[i]>p[j]for i in range(3)for j in range(i+1,3))%2
def matrix_sum(counts,perms):return [[sum(counts[i]*(p[t]==g)for i,p in enumerate(perms))for g in range(3)]for t in range(3)]
def check_patterns(patterns):
    need(len(patterns)==11 and len(set(map(tuple,patterns)))==11,'complete distinct parity patterns')
    need(patterns==[(0,)*6]+sorted(p for p in product(range(2),repeat=6)if p[0]==0 and sum(p)==3),'literal gauge universe')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();pins={};controls=[]
    def reject(name,fn):
        try:fn()
        except ValueError:controls.append(name)
        else:raise ValueError('corruption accepted '+name)
    try:
        for p,digest in PINS.items():need(h(ROOT/p)==digest,'input '+p);pins[p]=digest
        for name in ['acceleration/theory_20260930_hadamard_balanced_parity.py','acceleration/theory_20260930_hadamard_balanced_parity_spec.md','uv.lock','pyproject.toml']:pins[name]=h(ROOT/name)
        perms=list(permutations(range(3)));signs=[parity(p)for p in perms]
        need(signs.count(0)==signs.count(1)==3 and parity((0,1,2))==0 and parity((1,0,2))==1,'known permutation parities')
        six=[];five=[];all_six=list(compositions(6,6));all_five=list(compositions(5,6))
        for counts in all_six:
            if matrix_sum(counts,perms)==[[2]*3 for _ in range(3)]:six.append(list(counts))
        for counts in all_five:
            if matrix_sum(counts,perms)==[[2-(i==j)for j in range(3)]for i in range(3)]:five.append(list(counts))
        need(len(all_six)==462 and len(six)==3 and len(all_five)==252 and len(five)==2,'complete multiset classification sizes')
        need(all(len({c[i]for i in range(6)if signs[i]==0})==len({c[i]for i in range(6)if signs[i]==1})==1 for c in six),'equal multiplicities by sign')
        need(sorted(sum(c[i]*signs[i]for i in range(6))for c in five)==[0,3],'relative odd count')
        patterns=[(0,)*6]+sorted(p for p in product(range(2),repeat=6)if p[0]==0 and sum(p)==3);check_patterns(patterns)
        reject('missing_pattern',lambda:check_patterns(patterns[:-1]))
        reject('bad_weight',lambda:check_patterns([patterns[0],(0,1,0,0,0,0),*patterns[2:]]))
        local=json.loads((ROOT/(B+'hadamard_triplicate_counts/local_triples.json')).read_bytes());profiles=Counter();records=[]
        for triple in local['balanced']:
            words=[local['words'][i]for i in triple];ps=[tuple(w[pos]for w in words)for pos in range(6)]
            need(all(p in perms for p in ps),'each coordinate permutation')
            counts=[ps.count(p)for p in perms];need(counts in six,'column quotas classify local triple')
            parities=[parity(p)for p in ps];gauge=tuple(v^parities[0]for v in parities);need(gauge in patterns,'parity gauge')
            kind='cyclic'if triple in local['cyclic']else'mixed';need((gauge==patterns[0])==(kind=='cyclic'),'cyclic iff equal parity inside balanced domain')
            profiles[patterns.index(gauge)]+=1;records.append(dict(triple=triple,coordinate_permutations=[list(p)for p in ps],permutation_multiplicities=counts,parity_pattern=list(gauge),kind=kind))
        need(profiles==Counter({0:30,**{i:12 for i in range(1,11)}}),'all150local profile counts')
        raw=json.loads((ROOT/RAW).read_bytes());supports=[tuple(i for i in range(12)if raw['L'][i][d])for d in range(60)]
        unique=list(dict.fromkeys(supports));need(len(unique)==20 and all(supports.count(s)==3 for s in unique),'twenty triplicate supports')
        clauses=[];groups=[]
        for j,support in enumerate(unique):
            selectors=[11*j+i+1 for i in range(11)];clauses.append(selectors)
            clauses.extend([[-a,-b]for a,b in combinations(selectors,2)])
            groups.append(dict(group=j,support=list(support),selectors=selectors,parity_patterns=[list(p)for p in patterns]))
        sections=[dict(kind='onehot',clauses=len(clauses))];nextvar=220;pairrows=[]
        for a,b in combinations(range(12),2):
            if a//2==b//2:continue
            incidence=[j for j,s in enumerate(unique)if a in s and b in s];need(len(incidence)==5,'five cooccurring groups')
            terms=[]
            for j in incidence:
                apos=unique[j].index(a);bpos=unique[j].index(b);literals=[11*j+i+1 for i,p in enumerate(patterns)if p[apos]!=p[bpos]]
                need(len(literals)==6,'six disagreeing patterns');nextvar+=1;y=nextvar
                clauses.extend([[-s,y]for s in literals]);clauses.append([-y,*literals]);terms.append(dict(group=j,difference_variable=y,disagree_selectors=literals))
            ys=[term['difference_variable']for term in terms]
            for bits in product(range(2),repeat=5):
                if sum(bits)not in(0,3):clauses.append([-v if b else v for v,b in zip(ys,bits)])
            pairrows.append(dict(coordinates=[a,b],terms=terms,allowed_disagreement_counts=[0,3]))
        clauses.append([11*j+i+1 for j in range(20)for i in range(1,11)])
        need(nextvar==520 and len(clauses)==4481 and len(pairrows)==60,'exact parity formula dimensions')
        model=dict(schema='BALANCED_TRIPLET_PARITY_NECESSARY_CNF_V1',variables=nextvar,clauses=len(clauses),groups=groups,pair_rows=pairrows,
            requires_noncyclic_group=True,primary_selectors=220,additional_balance_assumption=True,target_graph=False,residual_D=False,
            scope='Necessary parity projection for balanced triples on one fixed support, with at least one noncyclic group; not a complete factor encoding.')
        save(out/'model.json',model);save(out/'classification.json',dict(permutations=[list(p)for p in perms],parities=signs,six_multisets_examined=462,
            six_matrix_profiles=six,five_multisets_examined=252,five_matrix_profiles=five,balanced_local_triples=records,parity_pattern_counts=dict(profiles)))
        with(out/'instance.cnf').open('x',encoding='ascii',newline='\n')as stream:
            stream.write(f'p cnf {nextvar} {len(clauses)}\n');stream.writelines(' '.join(map(str,row))+' 0\n'for row in clauses)
        # Exhaustive Boolean truth controls for the only non-onehot relations.
        for bits in product(range(2),repeat=7):
            domain=bits[:6];y=bits[6];relation=all(not s or y for s in domain)and(not y or any(domain))
            need(relation==(bool(y)==any(domain)),'OR equivalence truth control')
        for bits in product(range(2),repeat=5):
            accepted=all(any(x!=y for x,y in zip(bits,forbidden))for forbidden in product(range(2),repeat=5)if sum(forbidden)not in(0,3))
            need(accepted==(sum(bits)in(0,3)),'allowed count truth control')
        need(time.monotonic()-start<60,'build time cap')
        save(out/'controls.json',dict(OR_cases=128,count_cases=32,corruptions=controls))
        save(out/'summary.json',dict(status='CANDIDATE_BALANCED_TRIPLET_PARITY_MODEL',timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():h(p)for p in out.iterdir()if p.is_file()},
            variables=520,clauses=4481,groups=20,parity_patterns=11,coordinate_pairs=60,solver_calls=0,independent_approval=False,
            full_factor_balance_necessity='UNKNOWN',target_resolution='UNKNOWN',elapsed_seconds=time.monotonic()-start))
        print(json.dumps(dict(status='CANDIDATE_BALANCED_TRIPLET_PARITY_MODEL',variables=520,clauses=4481,solver_calls=0)))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=h(__file__)));raise
if __name__=='__main__':main()
