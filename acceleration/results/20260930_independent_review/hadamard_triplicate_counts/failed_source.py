"""Independent integer-rank and literal counting audit; no producer imports."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from itertools import combinations
from math import gcd
from pathlib import Path
import argparse, copy, hashlib, json, platform, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
def need(ok,message):
    if not ok:raise ValueError(message)
def h(path):
    with(ROOT/path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def rank_integer(matrix):
    a=[list(row)for row in matrix];row=0
    for col in range(len(a[0])):
        pivot=next((i for i in range(row,len(a))if a[i][col]),None)
        if pivot is None:continue
        a[row],a[pivot]=a[pivot],a[row]
        for i in range(row+1,len(a)):
            if a[i][col]:
                a[i]=[a[row][col]*x-a[i][col]*y for x,y in zip(a[i],a[row])]
                divisor=0
                for x in a[i]:divisor=gcd(divisor,abs(x))
                if divisor:a[i]=[x//divisor for x in a[i]]
        row+=1
    return row
def count_vectors(words):return [[sum(w[i]==g for w in words)for g in range(3)]for i in range(6)]
def literal(words):
    need(len(words)==3 and len(set(map(tuple,words)))==3,'distinct triple')
    need(all(len(w)==6 and sorted(w)==[0,0,1,1,2,2]for w in words),'domain words')
    overlaps=[sum(a==b for a,b in zip(left,right))for left,right in combinations(words,2)]
    need(max(overlaps)<=2,'column overlap')
    for i,j in combinations(range(6),2):
        for (g,k),observed in Counter((w[i],w[j])for w in words).items():
            need(observed<= (1 if g==k else 2),'literal Gram upper bound')
    return dict(words=[list(w)for w in words],rows=[sorted(6*g+i for i,g in enumerate(w))for w in words],
                overlaps=overlaps,colour_counts=count_vectors(words))
def kernel(matrix,vector):
    need(len(vector)==len(matrix[0]) and any(vector),'nonzero kernel shape')
    need(all(sum(x*y for x,y in zip(row,vector))==0 for row in matrix),'kernel products')
def compare(actual,expected):need(actual==expected,'exact census comparison')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic();pins={};controls=[]
    def pin(p,expected=None):
        actual=h(p);need(expected is None or actual==expected,'hash '+p);pins[p]=actual;return read(p)
    def reject(label,fn):
        try:fn()
        except (ValueError,AssertionError):controls.append(label)
        else:raise ValueError('accepted corruption '+label)
    try:
        candidate=pin(B+'hadamard_triplicate_counts/candidate_claim_records.json','8a20e3ca8e23fb18b064c51c8234b565c374e261699f5c9af015f46ef2e4ed8b')
        summary=pin(B+'hadamard_triplicate_counts/summary.json','bc347a85af0c4fbff64607a417d6c06a93231139c423f20c98a9bd7c97b0c66f')
        for claim in candidate['claims']:
            for p,sha in claim['evidence_references'].items():need(h(p)==sha,'candidate binding');pins[p]=sha
        for p,sha in summary['inputs_sha256'].items():need(h(p)==sha,'producer input');pins[p]=sha
        raw=read(B+'hadamard20_support/six_prism.json');C=raw['C36']
        G=[[12*(i==j)-C[i][j]-sum(C[i][k]*C[k][j]for k in range(36))+2-(i//12==j//12)for j in range(36)]for i in range(36)]
        need(G==raw['prescribed_Gram36'],'raw core-derived Gram')
        supports=[tuple(i for i in range(12)if raw['L'][i][d])for d in range(60)]
        unique=list(dict.fromkeys(supports));groups=[[d for d,s in enumerate(supports)if s==support]for support in unique]
        need(len(unique)==20 and all(len(g)==3 for g in groups),'triplicate supports')
        for support in unique:
            need(len(support)==6 and len({a//2 for a in support})==6,'independent support geometry')
            for a,b in combinations(support,2):
                for g in range(3):
                    for k in range(3):need(G[12*g+a][12*k+b]==(1 if g==k else 2),'local Gram template')
        # Independent subset-partition generation rather than the producer's 3^6 filter.
        words=[]
        for zero in combinations(range(6),2):
            for one in combinations([i for i in range(6)if i not in zero],2):
                words.append(tuple(0 if i in zero else 1 if i in one else 2 for i in range(6)))
        words.sort();need(len(words)==len(set(words))==90,'complete balanced partitions')
        for domain in raw['column_colour_options']:compare([o['fibres_by_sorted_coordinate']for o in domain],[list(w)for w in words])
        positive=[(0,0,1,1,2,2),(1,1,2,2,0,0),(2,2,0,0,1,1)];literal(positive)
        reject('duplicate_word',lambda:literal([positive[0]]*3))
        reject('invalid_domain',lambda:literal([(0,0,0,1,2,2),*positive[1:]]))
        reject('column_or_Gram_violation',lambda:literal([words[0],words[1],words[2]]))
        need(rank_integer([[1,0],[0,1]])==2 and rank_integer([[1,1],[2,2]])==1,'known rank controls')
        kernel([[1,1],[2,2]],[1,-1]);reject('wrong_kernel',lambda:kernel([[1,1]],[1,1]));reject('zero_kernel',lambda:kernel([[1,1]],[0,0]))
        actual=[];balanced=[];cyclic=[];profiles=Counter()
        for triple in combinations(range(90),3):
            chosen=[words[i]for i in triple]
            try:obj=literal(chosen)
            except ValueError:continue
            actual.append(list(triple));counts=obj['colour_counts']
            profiles[str(tuple(sorted(tuple(sorted(v))for v in counts)))]+=1
            if all(v==[1,1,1]for v in counts):balanced.append(list(triple))
            if set(chosen)=={tuple((c+s)%3 for c in chosen[0])for s in range(3)}:cyclic.append(list(triple))
        saved=read(B+'hadamard_triplicate_counts/local_triples.json')
        for key,value in [('words',[list(w)for w in words]),('examined',117480),('survivors',actual),('balanced',balanced),('cyclic',cyclic),('count_profile_histogram',dict(profiles))]:compare(saved[key],value)
        reject('omitted_survivor',lambda:compare(actual[1:],saved['survivors']))
        reject('extra_survivor',lambda:compare(actual+[[0,0,0]],saved['survivors']))
        for key in ['first_unbalanced','first_balanced_noncyclic']:
            witness=saved[key];obj=literal([words[i]for i in witness['option_indices']])
            for field,value in obj.items():compare(witness[field],value)
        need(any(c!=[1,1,1]for c in saved['first_unbalanced']['colour_counts']),'unbalanced witness')
        need(all(c==[1,1,1]for c in saved['first_balanced_noncyclic']['colour_counts']),'balanced witness')
        need(saved['first_balanced_noncyclic']['option_indices'] not in cyclic,'noncyclic witness')
        records=read(B+'hadamard_triplicate_counts/marginal_certificates.json');need(len(records)==12,'all coordinate cases');ranks=[]
        for a,record in enumerate(records):
            selected=[j for j,s in enumerate(unique)if a in s];others=[b for b in range(12)if b//2!=a//2]
            matrix=[[1]*10]+[[int(b in unique[j])for j in selected]for b in others];rhs=[10]+[5]*10
            compare(record['coordinate'],a);compare(record['groups'],selected);compare(record['other_coordinates'],others);compare(record['matrix'],matrix);compare(record['rhs'],rhs)
            for g in range(3):
                need(G[12*g+a][12*g+a]==10,'row marginal necessity')
                need(all(sum(G[12*g+a][12*k+b]for k in range(3))==5 for b in others),'summed Gram necessity')
            rank=rank_integer(matrix);need(rank==record['elimination']['rank']==6,'integer rank');ranks.append(rank)
            U=[[Fraction(x)for x in row]for row in record['elimination']['left_transform']]
            reduced=[[sum(U[i][k]*matrix[k][j]for k in range(11))for j in range(10)]for i in range(11)]
            compare(reduced,[[Fraction(x)for x in row]for row in record['elimination']['rref']])
            kernel(matrix,record['kernel_witness']);counts=record['colour_counts']
            compare(counts,[[1+v,1-v,1]for v in record['kernel_witness']]);need(all(min(c)>=0 and max(c)<=3 and sum(c)==3 for c in counts),'bounded counts')
            for g in range(3):compare([sum(row[j]*counts[j][g]for j in range(10))for row in matrix],rhs)
            need(len(record['separate_local_realizations'])==10,'all separate local witnesses')
            for pos,witness in enumerate(record['separate_local_realizations']):
                j=selected[pos];coord=unique[j].index(a);compare(witness['group'],j);compare(witness['coordinate_position'],coord)
                obj=literal([words[i]for i in witness['option_indices']]);compare(obj,witness['local_check']);compare(obj['colour_counts'][coord],counts[pos])
        reject('false_rank',lambda:compare(ranks,[7]*12))
        bad=copy.deepcopy(records[0]['colour_counts']);bad[0][0]+=1
        reject('corrupt_marginal_count',lambda:compare([sum(row[j]*bad[j][0]for j in range(10))for row in records[0]['matrix']],records[0]['rhs']))
        now=datetime.now(timezone.utc).isoformat();claims=[]
        for source in candidate['claims']:
            claim={k:copy.deepcopy(source[k])for k in ['id','revision','statement','kind','basis','scope','assumptions','dependencies','limitations']}
            claim.update(recommendation='VERIFIED',review_state='CLEAR',verifier='/root',updated_at=now);claims.append(claim)
        proof='For a full factor, let n[j,a,g] count colour g at coordinate a in the three columns of support group j. Row degree gives sum_j n=10. Summing the exact Gram entry over the three colours at another nonmatched coordinate b counts n exactly in groups containing b and gives 1+2+2=5. These are the saved eleven marginal equations. Integer elimination proves rank six. Every nonzero saved kernel vector and every separate local realization was checked; no joint realization follows. Local six-coordinate triples were completely enumerated by literal pair frequencies and column agreement counts, without importing producer bitset code.'
        save(out/'written_audit.json',dict(proof=proof,claims=claims))
        for p in ['acceleration/audit_20260930_hadamard_triplicate_counts.py','uv.lock','pyproject.toml']:pins[p]=h(p)
        report=dict(status='INDEPENDENT_HADAMARD_TRIPLICATE_PROJECTIONS_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,claims=claims,
            counts=dict(local_universe=117480,local_survivors=len(actual),balanced=len(balanced),cyclic=len(cyclic),marginal_cases=12,ranks=ranks,separate_local_witnesses=120),
            controls=dict(known_ranks=2,nonzero_kernel_positive=True,literal_cyclic_positive=True,corruptions=controls),
            verifier='/root',method='independent_literal_census_integer_elimination_and_marginal_derivation',
            shared_components=['Python standard library; authenticated raw core/support and previously independently reviewed support/order premises. No producer or solver code imports.'],
            limitations=['Only these exact necessary projections and the complete local finite census are verified. No joint factor, target graph, global balance implication, or target exclusion is established.'],
            elapsed_seconds=time.monotonic()-started,target_resolution='UNKNOWN',artifact_availability='LOCAL_ONLY',
            outputs_sha256={str((out/'written_audit.json').relative_to(ROOT)).replace('\\','/'):h(str((out/'written_audit.json').relative_to(ROOT)))})
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],counts=report['counts'],corruptions=len(controls))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error)));raise
if __name__=='__main__':main()
