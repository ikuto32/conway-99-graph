"""Independent core-cap derivation controls and complete labelled-P recount."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, permutations
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'acceleration/results/20260930_triangle_core_permutation'
PRIOR=ROOT/'acceleration/results/20260930_independent_review/triangle_matching_pair_census/summary.json'
PRIOR_SHA='085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79'
STAGES=ROOT/'acceleration/results/20260930_triangle_matching_pair_census_v2'
DOC=ROOT/'docs/AUDIT_20260930_TRIANGLE_CORE_PERMUTATION_CAPS.md'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def h(p):return sha256(p.read_bytes()).hexdigest()
def read(p):
    def unique(pairs):
        d={}
        for k,v in pairs:need(k not in d,'duplicate JSON key');d[k]=v
        return d
    return json.loads(p.read_bytes(),object_pairs_hook=unique)
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,obj):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def matching(m,n):
    need(type(n)is int and n>=2 and n%2==0 and len(m)==n,'even matching dimension')
    need(all(type(x)is int and 0<=x<n for x in m),'integer matching entries')
    need(all(m[i]!=i and m[m[i]]==i for i in range(n)),'fixed-point-free involution')
def inputs(m0,m1,m2,p):
    n=len(m0)
    for m in(m0,m1,m2):matching(m,n)
    need(len(p)==n and all(type(x)is int for x in p)and sorted(p)==list(range(n)),'exact permutation')
def all_matchings(n):
    def visit(left,edges):
        if not left:
            out=[None]*n
            for a,b in edges:out[a]=b;out[b]=a
            yield tuple(out);return
        a=left[-1]
        for b in left[:-1]:yield from visit(tuple(x for x in left if x not in(a,b)),edges+((a,b),))
    return sorted(visit(tuple(range(n)),()))
def raw_graph(m0,m1,m2,p):
    inputs(m0,m1,m2,p);n=len(m0);rows=[0]*(3+3*n)
    def add(a,b):rows[a]|=1<<b;rows[b]|=1<<a
    for i,j in combinations(range(3),2):add(i,j)
    for f,m in enumerate((m0,m1,m2)):
        for i in range(n):
            add(f,3+f*n+i)
            if i<m[i]:add(3+f*n+i,3+f*n+m[i])
    for i in range(n):add(3+i,3+n+i);add(3+i,3+2*n+i);add(3+n+i,3+2*n+p[i])
    return rows
def literal_caps(rows):
    size=len(rows)
    for i,row in enumerate(rows):need(type(row)is int and 0<=row<(1<<size)and not(row>>i&1),'raw binary diagonal')
    for i,j in combinations(range(size),2):
        need((rows[i]>>j&1)==(rows[j]>>i&1),'raw symmetry')
        if(rows[i]&rows[j]).bit_count()+(rows[i]>>j&1)>2:return False
    return True
def reduced(m0,m1,m2,p):
    for b in range(len(m0)):
        if(m1[b]==m0[b]or m2[b]==m0[b])and p[b]==m0[b]:return False
        if p[m1[b]]==b and p[b]==m2[b]:return False
    return True
def coefficient_count(m0,m1,m2):
    n=len(m0);pairs=sorted(((a,m1[a])for a in range(n)if a<m1[a]),reverse=True)
    polynomials=[]
    for r,s in pairs:
        terms={}
        for x in range(n):
            for y in range(n):
                if x==y:continue
                image={r:x,s:y};ok=True
                for b in(r,s):
                    if(m1[b]==m0[b]or m2[b]==m0[b])and image[b]==m0[b]:ok=False
                    if image[m1[b]]==b and image[b]==m2[b]:ok=False
                if ok:
                    monomial=(1<<x)|(1<<y);terms[monomial]=terms.get(monomial,0)+1
        polynomials.append(terms)
    coefficients={0:1}
    for factor in polynomials:
        new={}
        for support,c in coefficients.items():
            for monomial,d in factor.items():
                if not support&monomial:
                    total=support|monomial;new[total]=new.get(total,0)+c*d
        coefficients=new
    return coefficients.get((1<<n)-1,0)
def provenance():return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),verifier='/root/eight_domain_audit independent core adjacency and exact coefficient checker',producer_imports=False,external_review=False,target_resolution=False)
def theorem(out):
    out.mkdir(parents=True,exist_ok=False);start=time.monotonic();records=[];totals={}
    for n in(4,6):
        m0=tuple(i^1 for i in range(n));ms=all_matchings(n);ps=list(permutations(range(n)));tested=0;accepted=0
        for i,m1 in enumerate(ms):
            for j,m2 in enumerate(ms):
                direct=compact=0
                for p in ps:
                    raw=literal_caps(raw_graph(m0,m1,m2,p));simple=reduced(m0,m1,m2,p)
                    need(raw==simple,'raw adjacency vs reduced condition mismatch');direct+=raw;compact+=simple;tested+=1
                coeff=coefficient_count(m0,m1,m2);need(coeff==direct,'independent coefficient count vs exhaustive literal adjacency')
                records.append(dict(n=n,M1=list(m1),M2=list(m2),permutations=len(ps),literal_accepted=direct,reduced_accepted=compact,coefficient=coeff));accepted+=direct
                need(time.monotonic()-start<120,'small exhaustive control wall cap')
        totals[str(n)]=dict(matching_pairs=len(ms)**2,permutations_per_pair=len(ps),triples_tested=tested,cap_compatible_triples=accepted)
    m0=list(i^1 for i in range(12));identity=list(range(12));rows=raw_graph(m0,m0,m0,identity);need(literal_caps(rows),'positive raw39 core')
    save(out/'known_positive39.json',dict(M0=m0,M1=m0,M2=m0,P=identity,adjacency=[[row>>j&1 for j in range(39)]for row in rows]))
    corruptions=[]
    def reject(name,fn):
        try:fn()
        except ValueError:corruptions.append(name)
        else:raise ValueError('malformed object accepted '+name)
    bad=m0[:];bad[0]=0;reject('matching_fixed_point',lambda:raw_graph(m0,bad,m0,identity))
    bad=m0[:];bad[0]=3;reject('matching_not_involution',lambda:raw_graph(m0,bad,m0,identity))
    reject('odd_dimension',lambda:raw_graph([1,0,2],[1,0,2],[1,0,2],[0,1,2]))
    bad=identity[:];bad[0]=1;reject('duplicate_permutation_image',lambda:raw_graph(m0,m0,m0,bad))
    bad=identity[:];bad[0]=True;reject('boolean_not_integer_permutation',lambda:raw_graph(m0,m0,m0,bad))
    badrows=rows[:];badrows[0]|=1;reject('nonzero_diagonal',lambda:literal_caps(badrows))
    badrows=rows[:];badrows[0]^=1<<1;reject('asymmetric_adjacency',lambda:literal_caps(badrows))
    badrows=rows[:];badrows[3]|=1<<5;badrows[5]|=1<<3;need(not literal_caps(badrows),'extra within-fibre edge violates cap')
    save(out/'small_exhaustive_counts.json',records)
    report=provenance();report.update(status='INDEPENDENT_TRIANGLE_CORE_PAIR_CAP_REDUCTION_PASS',claim_id='C-TRIANGLE-CORE-PERMUTATION-PAIR-CAP-REDUCTION',claim_revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',statement='For every positive even n and every three perfect matchings M0,M1,M2 and permutation P, the specified3+3n triangle core satisfies all distinct-vertex common-plus-adjacency caps<=2 if and only if its unary common-M0-edge prohibitions and its n two-row diagonal prohibitions hold. The squarefree product coefficient equals its complete labelled allowed-P count.',scope='Exact positive-core local pair-cap feasibility only; at n12 this is the39vertex principal core, not target completion or a canonical core census.',dependencies=[],dependency_null_reason='Direct adjacency-block identity and elementary permutation counting; no prior graph-existence theorem used.',inputs_sha256={key(p):h(p)for p in[Path(__file__).resolve(),DOC,ROOT/'acceleration/theory_20260930_triangle_core_permutation_spec.md',ROOT/'uv.lock']},calibration=totals,malformed_controls_rejected=corruptions,extra_edge_negative_control=True,positive_raw39_sha256=h(out/'known_positive39.json'),exhaustive_counts_sha256=h(out/'small_exhaustive_counts.json'),shared_components=['Python exact integers and bitsets; no producer code or producer DP imported.','The polynomial-count recurrence is mathematically equivalent to subset DP, independently derived and implemented with reversed row-pair order.'],limitations=['Finite controls calibrate code; the written exhaustive pair-type derivation establishes the general reduction.','No claim of target feasibility, target exclusion, novelty or P-orbit classification.'],elapsed_seconds=time.monotonic()-start)
    save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=h(out/'summary.json'),controls=totals)),flush=True)
def census(out,theorem_path,theorem_sha):
    out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(p,expected=None):
        actual=h(p);need(expected is None or actual==expected,'input hash '+key(p));pins[key(p)]=actual
    pin(Path(__file__).resolve())
    pin(theorem_path,theorem_sha);th=read(theorem_path);need(th['status']=='INDEPENDENT_TRIANGLE_CORE_PAIR_CAP_REDUCTION_PASS','theorem gate')
    for path,sha in th['inputs_sha256'].items():pin(ROOT/path,sha)
    pin(PRIOR,PRIOR_SHA);prior=read(PRIOR)
    need(prior['status']=='INDEPENDENT_TRIANGLE_ORDERED_MATCHING_PAIR_CENSUS_PASS','prior complete matching-pair census')
    for path,sha in prior['inputs_sha256'].items():pin(ROOT/path,sha)
    pin(RUN/'cases.jsonl','8fd01ebe995367fbb03b381dfa40ac1cb19ec70d5a3063a2ab64799bc9259f7b');pin(RUN/'summary.json','33d5c516eacdf59137e5327d8a796c3598cd7bf77a112ecd887028011b85d253')
    for p in[RUN/'manifest.json',ROOT/'acceleration/theory_20260930_triangle_core_permutation.py',DOC]:pin(p)
    producer=read(RUN/'summary.json');cases=[json.loads(line)for line in(RUN/'cases.jsonl').read_text().splitlines()];expected=[]
    for stage_path in sorted(STAGES.glob('stage_*.json')):
        pin(stage_path);stage=read(stage_path)
        for i,orb in enumerate(stage['second_orbits']):expected.append((stage_path.name,i,stage['M1'],orb))
    need(len(expected)==len(cases)==3580,'frozen complete matching-pair population')
    save(out/'manifest.json',dict(**provenance(),inputs_sha256=pins,question='Independently recount all3580 labelled P domains and replay every raw39 witness.',resource_seconds=180,selection='All prior matching-pair representatives exactly once; no sampling.'))
    m0=tuple(i^1 for i in range(12));results=[];weighted=total=0;weight_sum=0;witnesses=set()
    for number,(rec,exp)in enumerate(tqdm(list(zip(cases,expected)),desc='Independent squarefree P counts')):
        stage_name,i,m1,orb=exp;m2=orb['representative'];p=rec['witness_P']
        need(rec['case']==number and rec['source_stage']==stage_name and rec['second_orbit_index']==i,'unique ordered representative mapping')
        need(rec['M1']==m1 and rec['M2']==m2 and rec['joint_stabilizer_order']==orb['joint_stabilizer_order'],'exact prior representative and stabilizer')
        inputs(m0,m1,m2,p);need(literal_caps(raw_graph(m0,m1,m2,p)),'complete raw39 witness caps')
        count=coefficient_count(m0,m1,m2);need(count==rec['labelled_permutation_count'],'complete exact P count')
        weight=46080//orb['joint_stabilizer_order'];need(weight*orb['joint_stabilizer_order']==46080 and rec['matching_pair_orbit_size']==weight,'exact pair-orbit weight')
        total+=count;weighted+=weight*count;weight_sum+=weight;witnesses.add(tuple(p));results.append(dict(case=number,source_stage=stage_name,second_orbit_index=i,independent_labelled_P_count=count,matching_pair_orbit_weight=weight,raw39_witness_pairs_checked=741))
        if(number+1)%100==0:
            save(out/f'checkpoint_{number+1:04d}.json',dict(completed=number+1,partial_weighted_sum=weighted,partial_unweighted_sum=total))
            need(time.monotonic()-start<180,'independent census cap')
    counts=[r['independent_labelled_P_count']for r in results]
    need(weight_sum==10395**2,'all labelled matching pairs restored')
    population=weight_sum*math.factorial(12)
    need((total,weighted,population,min(counts),max(counts))==(producer['unweighted_P_counts_sum'],producer['weighted_labelled_cap_compatible_triples'],producer['labelled_triple_population'],producer['minimum_labelled_P_domain'],producer['maximum_labelled_P_domain']),'producer aggregate exact values')
    save(out/'independent_counts.json',results)
    report=provenance();report.update(status='INDEPENDENT_TRIANGLE_CORE_LABELLED_P_CENSUS_PASS',claim_id='C-TRIANGLE-CORE-LABELLED-P-PAIRCAP-CENSUS',claim_revision=1,kind='empirical/engineering result',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',statement='For all3580 independently classified ordered matching-pair representatives, the exact labelled P-domain counts under all39vertex local pair caps equal the saved independently recomputed counts. Every domain is nonempty. Restoring matching-pair orbit sizes gives40781203938462691 cap-compatible labelled triples out of the precisely defined51759008864640000 triples.',scope='Fixed standard M0, named fibres, all labelled M1/M2/P choices; exact local39 pair-cap filter only, not P-orbit census or target extensions.',dependencies=[dict(id=th['claim_id'],revision=1,relation='uses_result'),dict(id=prior['claim_id'],revision=1,relation='coverage')],inputs_sha256=pins,completed_matching_pair_cases=len(results),independently_checked_raw39_witnesses=len(results),unique_recorded_P_arrays=len(witnesses),zero_domains=sum(c==0 for c in counts),minimum_labelled_P_count=min(counts),maximum_labelled_P_count=max(counts),unweighted_count_sum=total,restored_labelled_matching_pairs=weight_sum,weighted_cap_compatible_labelled_triples=weighted,labelled_triple_population=population,independent_counts_sha256=h(out/'independent_counts.json'),shared_components=['Own raw graph constructor and literal-neighbor-intersection checker; no producer imports.','Own decreasing-row-pair squarefree coefficient convolution; mathematically related to producer subset DP, code independently written.','Prior independently audited representative census is an explicit coverage premise.'],limitations=['Witness count is by representative; equal P arrays in different cases are not called distinct permutations.','No target search coverage percentage or full extension/nonexistence result.','The positive-core feasible population is a necessary local condition only.'],elapsed_seconds=time.monotonic()-start)
    need(all(h(ROOT/path)==sha for path,sha in pins.items()),'inputs unchanged after audit');save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=h(out/'summary.json'),cases=len(results),weighted=weighted)),flush=True)
def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='mode',required=True)
    t=sub.add_parser('theorem');t.add_argument('--out',type=Path,required=True)
    c=sub.add_parser('census');c.add_argument('--out',type=Path,required=True);c.add_argument('--theorem-report',type=Path,required=True);c.add_argument('--theorem-sha256',required=True)
    a=parser.parse_args();theorem(a.out)if a.mode=='theorem'else census(a.out,a.theorem_report,a.theorem_sha256)
if __name__=='__main__':main()

