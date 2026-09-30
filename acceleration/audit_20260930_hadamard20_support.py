"""Independent exact aggregate identities, colour domains and projection witnesses."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/';RUN=B+'hadamard20_support/'
PINS={RUN+'summary.json':'94e146c8e4c04acda9468f691cf91e2a2e82dbc6d60019d0bfb2d7e02b568f05',
 I+'connected_identity_cores/summary.json':'efdcacb9130bf29a28ece4c07022bdab11ab953a862f117fc55f44bd5244d2b4',
 I+'identity_p_triangle_partition/summary.json':'15a32c8e4fb4928f78a6e931e09054ddcfd90c027717e8c0d0828c6f5406a516',
 I+'srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debffaa8a44e83b2e3487342104c5d50e',
 B+'srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439'}
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
    else:raise AssertionError('corrupt control accepted '+name)

def matching(m,n):
    need(len(m)==n and all(type(v)is int and 0<=v<n for v in m),'matching domain')
    need(all(m[a]!=a and m[m[a]]==a for a in range(n)),'perfect matching involution')

def core(ms):
    n=len(ms[0]);need(len(ms)==3,'three internal matchings')
    for m in ms:matching(m,n)
    c=[[int((i//n==j//n and ms[i//n][i%n]==j%n)or(i//n!=j//n and i%n==j%n))for j in range(3*n)]for i in range(3*n)]
    neighbors=[{j for j,v in enumerate(row)if v}for row in c]
    gram=[[n*int(i==j)+2-c[i][j]-len(neighbors[i]&neighbors[j])-int(i//n==j//n)for j in range(3*n)]for i in range(3*n)]
    collapsed=[[sum(gram[g*n+a][h*n+b]for g in range(3)for h in range(3))for b in range(n)]for a in range(n)]
    expected=[[(3*n-21)*int(a==b)+15-5*sum(m[a]==b for m in ms)for b in range(n)]for a in range(n)]
    need(collapsed==expected,'literal nine-block aggregate identity')
    return c,gram,expected

def hadamard(h):
    n=len(h);need(n>0 and all(len(r)==n and all(type(x)is int and x in(-1,1)for x in r)for r in h),'square sign matrix')
    need(all(sum(h[i][k]*h[j][k]for k in range(n))==n*int(i==j)for i in range(n)for j in range(n)),'all row orthogonalities')
    need(all(sum(h[k][i]*h[k][j]for k in range(n))==n*int(i==j)for i in range(n)for j in range(n)),'all column orthogonalities')
    need(all(r[0]==1 for r in h) and all(sum(r[j]for r in h)==0 for j in range(1,n)),'normalized and balanced columns')

def positive243(raw):
    ms=raw['internal_matchings'];c,gram,aggregate=core(ms);n=20;f=raw['factor60x180']
    need(c==raw['cubic_core60'] and len(f)==60 and all(len(r)==180 and all(type(v)is int and v in(0,1)for v in r)for r in f),'non-target positive raw factor')
    need(all(sum(r)==18 for r in f)and all(sum(f[i][d]for i in range(20*g,20*(g+1)))==2 for d in range(180)for g in range(3)),'positive margins')
    rowsets=[{d for d,v in enumerate(r)if v}for r in f]
    need(all(len(rowsets[i]&rowsets[j])==gram[i][j]for i in range(60)for j in range(60)),'positive full Gram')
    l=[[sum(f[g*n+a][d]for g in range(3))for d in range(180)]for a in range(n)]
    need(all(v in(0,1)for r in l for v in r)and all(sum(r)==54 for r in l),'positive binary collapse')
    need(all(sum(l[a][d]for a in range(20))==6 for d in range(180)),'positive aggregate column margin')
    need(all(sum(l[a][d]*l[b][d]for d in range(180))==aggregate[a][b]for a in range(n)for b in range(n)),'positive aggregate Gram')
    return dict(non_target_parameters=[243,22,1,2],factor_Gram_entries=3600,aggregate_Gram_entries=400,row_sum=54,column_sum=6)

def support_check(raw,h):
    ms=raw['matchings'];c,gram,aggregate=core(ms);need(len(ms[0])==12,'research n12')
    need(raw['core_adjacency']==c and raw['prescribed_Gram36']==gram,'exact raw core and Gram')
    blocks=[]
    for m in ms:
        edges=sorted({tuple(sorted((a,m[a])))for a in range(12)})
        block=[[None]*20 for _ in range(12)]
        for index,(a,b)in enumerate(edges):
            for d in range(20):block[a][d]=h[d][index+1];block[b][d]=-h[d][index+1]
        blocks.append(block)
    x=[[blocks[g][a][d]for g in range(3)for d in range(20)]for a in range(12)]
    l=[[int(v==1)for v in r]for r in x]
    need(raw['X']==x and raw['L']==l and raw['matching_blocks']==blocks,'exact matching-block construction')
    need(all(sum(r)==0 for r in x)and all(sum(r)==30 for r in l),'balanced row margins')
    need(all(sum(l[a][d]for a in range(12))==6 for d in range(60)),'aggregate column margins')
    for a,b in product(range(12),repeat=2):
        s=sum(m[a]==b for m in ms)
        need(sum(x[a][d]*x[b][d]for d in range(60))==20*(3*int(a==b)-s),'literal X Gram')
        need(sum(l[a][d]*l[b][d]for d in range(60))==aggregate[a][b],'literal L Gram')
    supports=[[a for a in range(12)if l[a][d]]for d in range(60)]
    need(raw['support_columns']==supports,'exact support sets')
    multiplicities=Counter(map(tuple,supports))
    need(raw['support_multiplicities']==[dict(support=list(s),multiplicity=n)for s,n in sorted(multiplicities.items())],'all support multiplicities')
    return ms,gram,supports

def colours(coords,gram):
    """Independent choose-two/choose-two enumeration, not ternary word filtering."""
    valid={};failed=[]
    for first in combinations(range(6),2):
        left=[i for i in range(6)if i not in first]
        for second in combinations(left,2):
            assignment=tuple(0 if i in first else 1 if i in second else 2 for i in range(6))
            rows=sorted(12*assignment[i]+coords[i]for i in range(6))
            zeros=[(i,j)for i,j in combinations(rows,2)if gram[i][j]==0]
            if zeros:failed.append(dict(fibres=list(assignment),rows=rows,forbidden_pair=list(zeros[0])))
            else:valid[assignment]=rows
    need(len(valid)+len(failed)==90,'complete balanced colouring population')
    return valid,failed

def projection_witness(neighbors,result):
    if result['status']=='PERFECT_MATCHING':
        chosen=result['right_by_left'];need(len(chosen)==len(neighbors)and len(set(chosen))==len(chosen),'matching covers columns injectively')
        need(all(type(v)is int and v in neighbors[d]for d,v in enumerate(chosen)),'matching literal allowed edges')
    else:
        need(result['status']=='HALL_DEFICIT','matching result status')
        left=result['left_subset'];need(left==sorted(set(left)) and all(type(d)is int and 0<=d<len(neighbors)for d in left),'Hall left subset')
        right=set().union(*(neighbors[d]for d in left))
        need(result['neighbor_subset']==sorted(right) and len(right)<len(left),'complete literal Hall deficit')

def screens(raw,ms,gram,supports):
    options=raw['column_colour_options'];need(len(options)==60,'all60colour domains')
    rowsets=[];all_failures={};option_hist=Counter();capacity=[[0]*36 for _ in range(36)]
    for d,coords in enumerate(supports):
        expected,failed=colours(coords,gram);all_failures[d]=failed
        saved={};sets=[]
        for option in options[d]:
            word=tuple(option['fibres_by_sorted_coordinate']);need(word not in saved and word in expected,'unique admitted colouring')
            need(option['rows']==expected[word] and int(option['row_mask_hex'],16)==sum(2**r for r in expected[word]),'raw colour rows and mask')
            saved[word]=option['rows'];sets.append(set(option['rows']))
        need(saved==expected,'all and only local colourings retained');rowsets.append(sets);option_hist[len(sets)]+=1
        possible={(i,j)for s in sets for i in s for j in s}
        for i,j in possible:capacity[i][j]+=1
    need(raw['Gram_entry_capacities']==capacity,'all1296independent contribution capacities')
    deficits=[dict(rows=[i,j],required=gram[i][j],available_column_capacity=capacity[i][j])for i in range(36)for j in range(i,36)if capacity[i][j]<gram[i][j]]
    need(raw['Gram_capacity_deficits']==deficits,'complete capacity deficits')
    allpairs={(d,e)for d in range(60)for e in range(d+1,60)};seen=set()
    for witness in raw['pair_cap_witnesses']:
        d,e=witness['columns'];need((d,e)in allpairs and(d,e)not in seen,'unique compatible column pair');seen.add((d,e))
        i,j=witness['option_indices'];need(type(i)is int and type(j)is int and 0<=i<len(rowsets[d])and 0<=j<len(rowsets[e]),'pair option indices')
        overlap=len(rowsets[d][i]&rowsets[e][j]);need(overlap==witness['overlap'] and overlap<=2,'literal paircap witness')
    for pair in raw['incompatible_column_pairs']:
        d,e=pair;need((d,e)in allpairs and(d,e)not in seen,'unique incompatible pair');seen.add((d,e))
        need(all(len(a&b)>2 for a in rowsets[d]for b in rowsets[e]),'complete pair incompatibility')
    need(seen==allpairs,'all1770pair outcomes accounted')
    projections=raw['fibre_pair_matching_projections'];need(len(projections)==3,'all3fibre projections')
    for g,projection in enumerate(projections):
        catalog=[list(p)for p in combinations(range(12),2)if ms[g][p[0]]!=p[1]]
        need(projection['fibre']==g and projection['nonmatching_catalog']==catalog,'canonical60pair catalogue')
        index={tuple(p):i for i,p in enumerate(catalog)}
        neighbors=[{index[tuple(sorted(r%12 for r in s if r//12==g))]for s in opts}for opts in rowsets]
        need(projection['available_pair_indices_by_column']==[sorted(v)for v in neighbors],'entire projected bipartite graph')
        projection_witness(neighbors,projection['result'])
    need(raw['full_factor']is None and raw['target_graph']is False,'no producer factor claim')
    return dict(options_histogram=dict(sorted(option_hist.items())),empty_columns=[d for d,s in enumerate(rowsets)if not s],
                capacity_deficits=deficits,compatible_pairs=len(raw['pair_cap_witnesses']),incompatible_pairs=len(raw['incompatible_column_pairs']),
                projection_statuses=[p['result']['status']for p in projections],total_colour_candidates=5400),all_failures

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve()
    need(out.is_relative_to(ROOT),'workspace output');out.mkdir(parents=True,exist_ok=False);now=datetime.now(timezone.utc).isoformat();start=time.monotonic();bindings={}
    try:
        calibration=[]
        h4=[[(-1)**((i&j).bit_count())for j in range(4)]for i in range(4)];hadamard(h4)
        bad=deepcopy(h4);bad[0][1]*=-1;reject('Sylvester4sign_flip',lambda:hadamard(bad),calibration)
        projection_witness([{0,1},{1,2},{0,2}],dict(status='PERFECT_MATCHING',right_by_left=[0,1,2]))
        projection_witness([{0},{0},{1,2}],dict(status='HALL_DEFICIT',left_subset=[0,1],neighbor_subset=[0]))
        reject('matching_duplicate',lambda:projection_witness([{0,1},{1,2},{0,2}],dict(status='PERFECT_MATCHING',right_by_left=[0,1,0])),calibration)
        reject('false_Hall_neighbor_set',lambda:projection_witness([{0},{0},{1,2}],dict(status='HALL_DEFICIT',left_subset=[0,1],neighbor_subset=[])),calibration)
        for p,h in PINS.items():need(digest(ROOT/p)==h,'pinned input '+p);bindings[p]=h
        positive=read(B+'srg243_residual_fixture/triangle_blocks.json');positive_result=positive243(positive)
        bad=deepcopy(positive);bad['factor60x180'][0][0]^=1;reject('243factor_bit_flip',lambda:positive243(bad),calibration)
        save(out/'preflight_controls.json',dict(positive_Sylvester4=True,positive243=positive_result,projection_positive_and_Hall_negative=True,corruptions=calibration))
        summary=read(RUN+'summary.json')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():need(digest(ROOT/p)==h,'exact producer source/input/output '+p);bindings[p]=h
        raw_h=read(RUN+'Hadamard20.json');h=raw_h['matrix'];need(len(h)==20,'researchH20');hadamard(h)
        need(raw_h['nonconstant_columns_used']==list(range(1,7)) and raw_h['literal_orthogonality_entries']==400,'construction choice metadata')
        need(raw_h['quadratic_residues']==sorted({x*x%19 for x in range(1,19)}),'finite residue metadata')
        checks=[];failure_certificate=None;research_corrupt=[];raw_cases=[]
        expected_names=[f'connected_{i:02}'for i in range(4)]+['six_prism']
        need([c['core']for c in summary['cases']]==expected_names,'frozen5case selection')
        for case in summary['cases']:
            need(digest(ROOT/case['artifact'])==case['sha256'],'exact raw support case');raw=read(case['artifact']);raw_cases.append(raw)
            ms,gram,supports=support_check(raw,h);need(raw['core']==case['core'],'case label')
            if case['core']!='six_prism':
                reference=read(B+'connected_identity_cores/core_'+case['core'][-2:]+'.json')
                need(ms==[reference[f'M{i}']for i in range(3)] and raw['core_adjacency']==reference['core_adjacency'],'authenticated chosen core')
            else:need(ms==[[a^1 for a in range(12)]]*3,'exact standard six-prism control')
            result,failures=screens(raw,ms,gram,supports)
            for field,value in [('column_option_count_histogram',{str(k):v for k,v in result['options_histogram'].items()}),
                ('empty_columns',result['empty_columns']),('Gram_capacity_deficit_count',len(result['capacity_deficits'])),
                ('pair_cap_compatible_pairs',result['compatible_pairs']),('pair_cap_incompatible_pairs',result['incompatible_pairs']),
                ('fibre_matching_statuses',result['projection_statuses'])]:need(case[field]==value,'recorded result '+field)
            multiplicities=Counter(map(tuple,supports));need(case['unique_supports']==len(multiplicities),'unique support count')
            need(case['duplicate_support_multiplicity_histogram']=={str(k):v for k,v in Counter(multiplicities.values()).items()},'duplicate counts')
            checks.append(dict(core=case['core'],raw_sha256=case['sha256'],**result))
            if case['core']=='connected_00':
                coords=supports[41];pairs=sorted({tuple(sorted((a,ms[0][a])))for a in coords})
                need(ms[0]==ms[1] and coords==[2,3,4,5,10,11] and pairs==[(2,3),(4,5),(10,11)],'pigeonhole obstruction premise')
                zero_pairs=[[12*g+a,12*j+b]for a,b in pairs for g,j in product(range(2),repeat=2)]
                need(all(gram[a][b]==0 for a,b in zero_pairs),'all12forbidden same-matching placements in fibres0/1')
                need(len(failures[41])==90,'complete column41failure certificate')
                failure_certificate=dict(core='connected_00',support_column=41,support=coords,matching_pairs=[list(p)for p in pairs],
                    forbidden_Gram_entries=zero_pairs,all90failed_balanced_colours=failures[41],
                    proof='Every one of the three matching pairs needs an endpoint in fibre2, since both endpoints in fibres0/1 hit a zero prescribed-Gram entry. Fibre2 has only two slots. Therefore this one fixed aggregate support has no full factor lift.')
        save(out/'exact_case_checks.json',dict(cases=checks));save(out/'connected00_column41_obstruction.json',failure_certificate)
        bad=deepcopy(h);bad[0][1]*=-1;reject('H20sign_flip',lambda:hadamard(bad),research_corrupt)
        original=raw_cases[1]
        for name,change in [('support_bit_flip',lambda x:x['L'][0].__setitem__(0,1-x['L'][0][0])),
                            ('wrong_matching',lambda x:x['matchings'][0].__setitem__(0,0)),
                            ('wrong_targetGram',lambda x:x['prescribed_Gram36'][0].__setitem__(0,11))]:
            bad=deepcopy(original);change(bad);reject(name,lambda:support_check(bad,h),research_corrupt)
        ms,gram,supports=support_check(original,h)
        for name,change in [('missing_colour',lambda x:x['column_colour_options'][0].pop()),
                            ('false_capacity',lambda x:x['Gram_entry_capacities'][0].__setitem__(0,-1)),
                            ('wrong_pair_overlap',lambda x:x['pair_cap_witnesses'][0].update(overlap=3)),
                            ('missing_pair_case',lambda x:x['pair_cap_witnesses'].pop()),
                            ('false_projection_matching',lambda x:x['fibre_pair_matching_projections'][0]['result']['right_by_left'].__setitem__(0,-1)),
                            ('fabricated_fullfactor',lambda x:x.update(full_factor=[]))]:
            bad=deepcopy(original);change(bad);reject(name,lambda:screens(bad,ms,gram,supports),research_corrupt)
        save(out/'research_corruptions.json',dict(controls=research_corrupt))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD20_SUPPORT.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[key(p)]=digest(p)
        need(all(digest(ROOT/p)==h for p,h in bindings.items()),'input stability')
        common=dict(revision=1,recommendation='VERIFIED',review_state='CLEAR',verifier='/root/eight_domain_audit',
            assumptions=['Identity cross matchings are an explicit premise, not an unrestricted normalization.','No hypothetical target automorphism is assumed.'],
            limitations=['No full incidence factor, residual graph or SRG99 is constructed.','No novelty claim.'])
        claims=[dict(common,id='C-IDENTITY-P-AGGREGATE-INCIDENCE-NECESSITY',kind='mathematical result',basis=['DERIVED'],
            statement='For every binary36x60 prescribed-Gram factor with row sums10 and two entries per fibre per column in an identity-cross core, L[a,d]=sum_gF[12g+a,d] is binary with row sums30,column sums6 and LL^T=15I+15J-5S; X=2L-J satisfies XX^T=20(3I-S), where S=M0+M1+M2.',
            scope='All three internal perfect matchings on12coordinates; necessary aggregate condition for this identity-cross family only.',
            dependencies=[dict(id='C-IDENTITY-P-FACTOR-DISTINCT-COORDINATES-MIXED-CAP-REDUNDANCY',revision=1,relation='premise'),dict(id='C-UNRESTRICTED-TRIANGLE-CORE-FACTOR-NORMALIZATION',revision=1,relation='uses_result')]),
          dict(common,id='C-HADAMARD20-UNIVERSAL-AGGREGATE-SUPPORT-CONSTRUCTION',kind='construction',basis=['DERIVED','COMPUTED'],
            statement='For every triple of perfect matchings on12coordinates, the recorded orthogonal20x20sign matrix supplies a binary12x60 matrix L with row sums30,column sums6 and LL^T=15I+15J-5(M0+M1+M2), by concatenating opposite sign columns at each matching edge and taking (X+J)/2.',
            scope='Universal construction of the aggregate matrix alone; selected firstsix Hadamard columns yield one explicit construction per matching triple.',dependencies=[]),
          dict(common,id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',kind='empirical/engineering result',basis=['COMPUTED'],
            statement='The five exact saved support matrices pass their aggregate identities; complete90-colouring-per-column enumeration and all1770pair projections match the saved records. Connected00 has empty column41,one Gram-capacity deficit and59incompatible columnpairs with three singleton Hall obstructions; connected01,02,03 and six_prism have nonempty columns,no capacity or pair deficits and three independently checked perfect-matching projections each.',
            scope='Exactly these five hash-bound supports,27000 local colouring candidates,8850columnpair cases and15fibre projections; projection choices are not asserted jointly compatible.',
            dependencies=[dict(id='C-FOUR-CONNECTED-IDENTITY-CORE-PORTFOLIO',revision=1,relation='premise'),dict(id='C-HADAMARD20-UNIVERSAL-AGGREGATE-SUPPORT-CONSTRUCTION',revision=1,relation='uses_result')]),
          dict(common,id='C-CONNECTED00-HADAMARD20-COLUMN41-NONLIFT',kind='exclusion',basis=['DERIVED','COMPUTED'],
            statement='No binary prescribed-Gram factor for connected00 with two entries per fibre per column has the exact saved Hadamard aggregate L: its column41 support{2,3,4,5,10,11} contains three M0=M1pairs,each requiring a fibre2endpoint despite onlytwo fibre2slots.',
            scope='Only the exact saved connected00 aggregate support; neither the core nor other Hadamard/support choices are excluded.',
            dependencies=[dict(id='C-FOUR-CONNECTED-IDENTITY-CORE-PORTFOLIO',revision=1,relation='premise'),dict(id='C-IDENTITY-P-AGGREGATE-INCIDENCE-NECESSITY',revision=1,relation='uses_result')])]
        for claim in claims:claim.update(created_at=now,updated_at=datetime.now(timezone.utc).isoformat())
        save(out/'claim_bindings.json',dict(claims=claims,ledger_changed=False))
        report=dict(status='INDEPENDENT_HADAMARD20_SUPPORT_AND_PROJECTION_PASS',created_at=now,updated_at=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=bindings,outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},
            verifier='/root/eight_domain_audit',method='independent_derivation_and_exact_artifact_check',recommendation='VERIFIED',review_state='CLEAR',
            shared_components=['Raw matrix/support artifacts and earlier independently checked core/243premises.','Only Python standard library, no producer or prior checker imports.'],
            case_names=expected_names,counts=dict(H_row_entries=400,H_column_entries=400,aggregate_identities_per_case=288,raw_Gram_entries_per_case=1296,
                colour_candidates=27000,columnpair_cases=8850,fibre_projection_witnesses=15,corruptions=len(calibration)+len(research_corrupt)),
            next_encoding_eligible_supports=expected_names[1:],excluded_fixed_support='connected_00',
            limitations=['Passing these separate necessary projections is not joint colouring feasibility.','No complete factor, residualD or target graph.',
                'The producer keyword search and timing remain bounded historical records, not novelty or performance claims.'],
            artifact_availability='LOCAL_ONLY',retrieval='All exact inputs and checking outputs are saved at bound paths; publication not yet confirmed.',
            target_resolution=False,external_review=False,overall_search_coverage='UNKNOWN; no validated denominator.',wall_seconds=time.monotonic()-start)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=digest(out/'summary.json'),wall_seconds=report['wall_seconds'])))
    except BaseException as exc:
        save(out/'failure.json',dict(error=repr(exc),source_sha256=digest(Path(__file__)),timestamp=datetime.now(timezone.utc).isoformat()));raise

if __name__=='__main__':main()
