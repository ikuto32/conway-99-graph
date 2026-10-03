"""Independent exact six-prism LP primal and integral column-order coverage.

Two separate output modes, no producer/LP imports or solver calls.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
RAW=B+'hadamard20_support/six_prism.json'
SUPPORT=I+'hadamard20_support_v2/summary.json'
MODEL=B+'hadamard_support_remaining_lp/six_prism/exact_model.json'
LP=B+'hadamard_prism_uniform_lp/'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 SUPPORT:'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f'}
LP_PINS={MODEL:'f5ac7adc289d6ca3cc7ce77394565919813138f6322e5ae2dc1856684eef6ae2',
 LP+'certificate.json':'e908ccc22b2706e947f00b7cf00d505d184934d6bf89cae2397d24e510ad83cd',
 LP+'summary.json':'193f9162b69212fccbc0714a8b9491d23ce9d90cf115a23748a8fd958ee392ca'}
def need(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def reject(name,op,records):
    try:op()
    except (ValueError,KeyError,IndexError,TypeError):records.append(dict(name=name,rejected=True))
    else:raise AssertionError('bad control accepted '+name)

def raw_domain(raw):
    m=[a^1 for a in range(12)]
    need(raw['matchings']==[m,m,m],'standard six-prism core only')
    c=[[int((i//12==j//12 and i%12==((j%12)^1))or(i//12!=j//12 and i%12==j%12))for j in range(36)]for i in range(36)]
    need(raw['core_adjacency']==c,'literal core adjacency')
    neighbors=[{j for j,v in enumerate(r)if v}for r in c]
    gram=[[12*int(i==j)+2-c[i][j]-len(neighbors[i]&neighbors[j])-int(i//12==j//12)for j in range(36)]for i in range(36)]
    need(raw['prescribed_Gram36']==gram,'literal prescribed Gram')
    l=raw['L'];need(len(l)==12 and all(len(r)==60 and all(type(v)is int and v in(0,1)for v in r)for r in l),'binary aggregate shape')
    supports=[[a for a in range(12)if l[a][d]]for d in range(60)]
    need(raw['support_columns']==supports and all(len(s)==6 for s in supports),'actual support identity')
    need(all(sum(r)==30 for r in l),'aggregate row margins')
    need(all(sum(l[a][d]*l[b][d]for d in range(60))==15*int(a==b)+15-15*int(m[a]==b)for a in range(12)for b in range(12)),'exact aggregate Gram')
    domains=[]
    for d,coords in enumerate(supports):
        need(len({a//2 for a in coords})==6,'one endpoint per standard matching pair')
        expected={}
        for first in combinations(range(6),2):
            rest=[i for i in range(6)if i not in first]
            for second in combinations(rest,2):
                word=tuple(0 if i in first else 1 if i in second else 2 for i in range(6))
                expected[word]=sorted(12*word[i]+coords[i]for i in range(6))
        need(len(expected)==90,'complete90balanced assignments')
        options=raw['column_colour_options'][d]
        need([tuple(o['fibres_by_sorted_coordinate'])for o in options]==sorted(expected),'exact lex option ordering')
        for option in options:
            rows=expected[tuple(option['fibres_by_sorted_coordinate'])]
            need(option['rows']==rows and int(option['row_mask_hex'],16)==sum(2**r for r in rows),'complete raw option alignment')
            need(all(gram[a][b]>0 for a,b in combinations(rows,2)),'zero-Gram compatible')
        domains.append([set(o['rows'])for o in options])
    return gram,supports,domains

def independent_model(raw,model):
    gram,supports,domains=raw_domain(raw)
    pairs=[(i,j)for i in range(36)for j in range(i,36)]
    index={p:60+r for r,p in enumerate(pairs)};columns=[];selectors=[]
    for d,options in enumerate(domains):
        for j,rows in enumerate(options):
            columns.append([d]+[index[a,b]for a in sorted(rows)for b in sorted(rows)if a<=b]);selectors.append([d,j])
    rhs=[1]*60+[gram[a][b]for a,b in pairs]
    need(model['nonnegative_variables']is True and model['binary_coefficients']is True,'LP domain')
    need(model['columns_nonzero_row_indices']==columns and model['selectors']==selectors,'all sparse columns and selector map')
    need(model['rhs']==rhs and model['Gram_row_pairs']==[list(p)for p in pairs],'all726exact equations')
    need(model['variables']==5400 and model['equations']==726,'fixed LP dimensions')
    return columns,rhs,gram,supports,domains

def rational_primal(columns,rhs,certificate):
    denominator=certificate['denominator'];values=certificate['numerators']
    need(type(denominator)is int and denominator>0 and len(values)==len(columns),'rational dimensions')
    need(all(type(v)is int and v>=0 for v in values),'literal nonnegative integer numerators')
    rows=[0]*len(rhs)
    for value,col in zip(values,columns,strict=True):
        need(len(col)==len(set(col))and all(type(r)is int and 0<=r<len(rhs)for r in col),'binary sparse domain')
        for row in col:rows[row]+=value
    need(rows==[denominator*b for b in rhs],'all exact primal equations')
    need(certificate['row_numerators']==rows,'saved row-numerator receipt')
    return rows

def groups(supports,domains,gram):
    classes={}
    for d,s in enumerate(supports):classes.setdefault(tuple(s),[]).append(d)
    ordered=sorted(classes.items(),key=lambda item:item[1][0]);need(len(ordered)==20 and all(len(v)==3 for _,v in ordered),'twenty identical-support triples')
    records=[];pairs=[];duplicate_obstructions=[]
    for number,(support,cols)in enumerate(ordered):
        need(cols==sorted(cols) and all(domains[d]==domains[cols[0]]for d in cols),'all90option domains align exactly')
        for option,rows in enumerate(domains[cols[0]]):
            fibre0=sorted(r for r in rows if r<12);need(len(fibre0)==2,'option fibre0 quota')
            a,b=fibre0;need(gram[a][b]==1,'duplicate option forbidden by exact within-fibre Gram1')
            duplicate_obstructions.append(dict(group=number,option=option,Gram_pair=[a,b],required=1,duplicate_contribution=2))
        encoded=json.dumps([sorted(r)for r in domains[cols[0]]],separators=(',',':')).encode()
        records.append(dict(group=number,columns=cols,support=list(support),option_count=90,option_row_sets_sha256=sha256(encoded).hexdigest(),
            allowed_rank_order='Strictly increasing saved lexicographic option index along these ascending column labels.'))
        pairs.extend([[cols[0],cols[1]],[cols[1],cols[2]]])
    need(sorted(d for r in records for d in r['columns'])==list(range(60)),'all60columns once')
    return records,pairs,duplicate_obstructions

def order_controls():
    distinct=duplicates=0
    for triple in product(range(90),repeat=3):
        if len(set(triple))<3:duplicates+=1;continue
        old_by_new=sorted(range(3),key=triple.__getitem__)
        arranged=tuple(triple[i]for i in old_by_new)
        need(arranged[0]<arranged[1]<arranged[2]and sorted(old_by_new)==[0,1,2],'complete sorting coverage')
        inverse=[old_by_new.index(i)for i in range(3)]
        need(tuple(arranged[inverse[i]]for i in range(3))==triple,'bijection inverse')
        distinct+=1
    need(distinct==704880 and duplicates==24120,'exact sorting populations')
    # Actual small matrix permutation controls, with a nonempty residual graph.
    f=[[1,0,1],[0,1,1]];d=[[0,1,0],[1,0,1],[0,1,0]]
    original_gram=[[sum(a*b for a,b in zip(r,s))for s in f]for r in f]
    checks=0
    for p in product(range(3),repeat=3):
        if len(set(p))<3:continue
        fp=[[row[j]for j in p]for row in f];dp=[[d[p[i]][p[j]]for j in range(3)]for i in range(3)]
        need([[sum(a*b for a,b in zip(r,s))for s in fp]for r in fp]==original_gram,'column permutation preserves Gram')
        need([[sum(fp[r][k]*dp[k][j]for k in range(3))for j in range(3)]for r in range(2)]==
             [[sum(f[r][k]*d[k][p[j]]for k in range(3))for j in range(3)]for r in range(2)],'mixed product permutation identity')
        need([[sum(dp[i][k]*dp[k][j]for k in range(3))for j in range(3)]for i in range(3)]==
             [[sum(d[p[i]][k]*d[k][p[j]]for k in range(3))for j in range(3)]for i in range(3)],'residual square conjugation identity')
        checks+=1
    return dict(ordered_distinct_option_triples=distinct,duplicate_option_triples=duplicates,all_option_triples=90**3,
                normalized_increasing_triples=117480,small_matrix_permutations=checks,
                positive_scope='Generic permutation controls only; no full research factor asserted.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['lp','order'],required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();need(out.is_relative_to(ROOT),'workspace output');out.mkdir(parents=True,exist_ok=False);now=datetime.now(timezone.utc).isoformat();bindings={};corrupt=[]
    try:
        for p,h in PINS.items():need(digest(ROOT/p)==h,'frozen scope input '+p);bindings[p]=h
        need(read(SUPPORT)['status']=='INDEPENDENT_HADAMARD20_SUPPORT_AND_PROJECTION_PASS','independent support premise')
        raw=read(RAW);gram,supports,domains=raw_domain(raw)
        if args.mode=='lp':
            for p,h in LP_PINS.items():need(digest(ROOT/p)==h,'frozen LP input '+p);bindings[p]=h
            for p,h in {**read(LP+'summary.json')['inputs_sha256'],**read(LP+'summary.json')['outputs_sha256']}.items():need(digest(ROOT/p)==h,'producer bytes '+p);bindings[p]=h
            # Distinct rational positive controls before the research certificate.
            rational_primal([[0],[0]],[1],dict(denominator=2,numerators=[1,1],row_numerators=[2]))
            reject('tiny_negative_weight',lambda:rational_primal([[0],[0]],[1],dict(denominator=2,numerators=[3,-1],row_numerators=[2])),corrupt)
            reject('tiny_wrong_denominator',lambda:rational_primal([[0],[0]],[1],dict(denominator=3,numerators=[1,1],row_numerators=[2])),corrupt)
            model=read(MODEL);columns,rhs,_,_,_=independent_model(raw,model);certificate=read(LP+'certificate.json')
            need(certificate['model_path']==MODEL and certificate['model_sha256']==LP_PINS[MODEL],'exact model certificate pin')
            need(certificate['denominator']==90 and certificate['numerators']==[1]*5400,'literal uniform witness')
            sums=rational_primal(columns,rhs,certificate)
            # A separate ordinary Fraction accumulation, addressed from raw options.
            direct=[Fraction(0)for _ in rhs];pairs=[(i,j)for i in range(36)for j in range(i,36)]
            for d,options in enumerate(domains):
                for selected in options:
                    direct[d]+=Fraction(1,90)
                    for index,(a,b)in enumerate(pairs):
                        if a in selected and b in selected:direct[60+index]+=Fraction(1,90)
            need(direct==rhs,'independent raw-option rational row accumulation')
            probability_checks=[]
            for d,options in enumerate(domains):
                coords=supports[d]
                for a in coords:
                    for g in range(3):need(sum(12*g+a in s for s in options)==30,'coordinate marginal1/3')
                for a,b in combinations(coords,2):
                    for g,h in product(range(3),repeat=2):need(sum(12*g+a in s and 12*h+b in s for s in options)==(6 if g==h else 12),'pair probabilities1/15and2/15')
                probability_checks.append(dict(column=d,options=90,row_numerator=30,same_fibre_pair_numerator=6,different_fibre_pair_numerator=12,denominator=90))
            save(out/'literal_rational_check.json',dict(equations=726,variables=5400,denominator=90,row_numerators=sums,
                direct_raw_Fraction_totals=[[v.numerator,v.denominator]for v in direct],local_probability_checks=probability_checks))
            for name,change in [('alter_weight',lambda c:c['numerators'].__setitem__(0,2)),('negative_weight',lambda c:c['numerators'].__setitem__(0,-1)),
                                ('wrong_denominator',lambda c:c.update(denominator=89)),('false_row_receipt',lambda c:c['row_numerators'].__setitem__(0,0))]:
                bad=deepcopy(certificate);change(bad);reject(name,lambda:rational_primal(columns,rhs,bad),corrupt)
            bad=deepcopy(model);bad['columns_nonzero_row_indices'][0].pop();reject('missing_sparse_entry',lambda:independent_model(raw,bad),corrupt)
            bad=deepcopy(model);bad['rhs'][60]+=1;reject('wrong_rhs',lambda:independent_model(raw,bad),corrupt)
            status='INDEPENDENT_HADAMARD_SIX_PRISM_UNIFORM_RATIONAL_LP_PASS'
            claim=dict(id='C-FIXED-HADAMARD-SIX-PRISM-UNIFORM-RATIONAL-PRIMAL',revision=1,kind='construction',basis=['COMPUTED','DERIVED'],
                statement='The exact fixed six-prism Hadamard support nonnegative selector relaxation has5400variables and726equalities, and assigning every selector the rational value1/90 satisfies every equation exactly with nonnegative weights.',
                scope='Only the saved continuous Gram-selector relaxation; all pairwise Ycaps, integrality, column-order constraints and residualD equations are omitted.',
                dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise')])
            counts=dict(variables=5400,equations=726,denominator=90,raw_rational_checks=726)
        else:
            calibration=order_controls();save(out/'calibration.json',calibration)
            records,pairs,obstructions=groups(supports,domains,gram)
            save(out/'groups.json',dict(schema='FIXED_HADAMARD_SIX_PRISM_IDENTICAL_SUPPORT_ORDER_V1',raw_support_path=RAW,raw_support_sha256=PINS[RAW],
                groups=records,adjacent_order_pairs=pairs,option_index_range=[0,89],strict=True,no_additional_fixed_columns_or_bits=True))
            save(out/'duplicate_option_obstructions.json',dict(records=obstructions,meaning='Two identical selected options would contribute2 to this within-fibre Gram entry whose exact total is1.'))
            need(len(obstructions)==1800 and len(pairs)==40,'all group-option duplicate obstructions and adjacentorders')
            for name,change in [('support_bit',lambda r:r['L'][0].__setitem__(0,1-r['L'][0][0])),
                                ('missing_option',lambda r:r['column_colour_options'][0].pop()),
                                ('changed_option_order',lambda r:r['column_colour_options'][20].reverse()),
                                ('wrong_Gram_entry',lambda r:r['prescribed_Gram36'][0].__setitem__(2,2))]:
                bad=deepcopy(raw);change(bad);reject(name,lambda:raw_domain(bad),corrupt)
            bad=deepcopy(supports);bad[20]=bad[1];reject('broken_identical_support_group',lambda:groups(bad,domains,gram),corrupt)
            status='INDEPENDENT_HADAMARD_SIX_PRISM_IDENTICAL_SUPPORT_ORDER_PASS'
            claim=dict(id='C-FIXED-HADAMARD-SIX-PRISM-IDENTICAL-SUPPORT-ORDER-NORMALIZATION',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],
                statement='Every binary exact prescribed-Gram factor on the fixed six-prism Hadamard aggregate support can be relabelled within each of its20 identical-support size3column groups so that its three saved lexicographic option indices strictly increase; this preserves the full factor Gram, all outside paircaps and existence of any residual target completion.',
                scope='Integral factor solutions in this one exact fixed-support family, modulo outside-vertex relabelling; no graph automorphism, fixed bit or additional chosen column is assumed.',
                dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise')])
            counts=dict(groups=20,columns=60,options_per_column=90,adjacent_order_pairs=40,duplicate_option_obstructions=1800,**calibration)
        save(out/'corruptions.json',dict(controls=corrupt))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_PRISM_RELAXATION_AND_ORDER.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[key(p)]=digest(p)
        need(all(digest(ROOT/p)==h for p,h in bindings.items()),'stable inputs')
        claim.update(recommendation='VERIFIED',review_state='CLEAR',assumptions=['The exact fixed support and its90-option domains are the stated scope.','No nontrivial automorphism of a hypothetical solution is assumed.'],
            limitations=['No integer factor, residualD or target graph is constructed.','Fractional feasibility and integral normalization are separate claims; the uniform witness does not certify the ordered relaxation.'],
            created_at=now,updated_at=datetime.now(timezone.utc).isoformat(),verifier='/root/eight_domain_audit')
        report=dict(status=status,created_at=now,updated_at=datetime.now(timezone.utc).isoformat(),claim=claim,verifier='/root/eight_domain_audit',method='independent_derivation_and_exact_artifact_check',
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=bindings,outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},counts=counts,corruptions=len(corrupt),
            shared_components=['The two modes share this independently authored raw-domain checker.','Only Python standard library; no producer LP, solver, sparse-builder or Hadamard code is imported.'],
            mathematical_review='Written proof is bound in inputs_sha256; group sorting is legitimate relabelling, not an assumed graph automorphism.',
            artifact_availability='LOCAL_ONLY',retrieval='Exact raw sources and saved checking receipts are bound; immutable publication is not yet confirmed.',target_resolution=False,external_review=False,
            overall_search_coverage='UNKNOWN; no validated denominator.')
        save(out/'summary.json',report);print(json.dumps(dict(status=status,summary_sha256=digest(out/'summary.json'))))
    except BaseException as exc:
        save(out/'failure.json',dict(error=repr(exc),source_sha256=digest(Path(__file__)),timestamp=datetime.now(timezone.utc).isoformat()));raise

if __name__=='__main__':main()
