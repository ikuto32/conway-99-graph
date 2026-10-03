"""Independent raw-support census and row-margin cancellation review."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_';I=B+'independent_review/'
RAW=B+'hadamard20_support/six_prism.json'
RAW_SHA='ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'
DOC='docs/AUDIT_20260930_HADAMARD_TWO_GROUP_MARGIN_CANCELLATION.md'

def need(ok,message):
    if not ok:raise ValueError(message)
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')

def geometry(L):
    need(len(L)==12 and all(len(row)==60 and all(type(v)is int and v in[0,1] for v in row) for row in L),'binary12by60 support')
    columns=[[a for a in range(12) if L[a][d]] for d in range(60)]
    supports=[]
    for s in columns:
        if s not in supports:supports.append(s)
    groups=[[d for d,s in enumerate(columns) if s==support] for support in supports]
    need(len(supports)==20 and all(len(s)==6 for s in supports) and all(len(ds)==3 for ds in groups),'twenty distinct triplicate supports')
    need(sorted(d for ds in groups for d in ds)==list(range(60)),'exact column partition')
    counts=[sum(a in s for s in supports) for a in range(12)]
    need(counts==[10]*12,'ten groups per coordinate')
    return supports,groups

def evaluate(F,L,supports,groups,require_margins=True):
    need(len(F)==36 and all(len(row)==60 and all(type(v)is int and v in[0,1] for v in row) for row in F),'literal binary factor shape')
    need(all(sum(F[12*f+a][d] for f in range(3))==L[a][d] for a in range(12) for d in range(60)),'literal coordinate support')
    row_sums=[sum(row) for row in F]
    delta=[[[sum(F[12*f+a][d] for d in ds)-int(a in support) for f in range(3)] for a in range(12)] for support,ds in zip(supports,groups)]
    totals=[[sum(delta[g][a][f] for g in range(20)) for f in range(3)] for a in range(12)]
    need(totals==[[row_sums[12*f+a]-10 for f in range(3)] for a in range(12)],'all36 literal cancellation identities')
    need(all(sum(delta[g][a])==0 for g in range(20) for a in range(12)),'per-coordinate zero sum')
    need(all(delta[g][a]==[0,0,0] for g in range(20) for a in range(12) if a not in supports[g]),'delta vanishes outside support')
    margins=row_sums==[10]*36
    if require_margins:need(margins,'row margins10')
    exceptional=[g for g in range(20) if any(any(row) for row in delta[g])]
    if margins:
        need(all(row==[0,0,0] for row in totals),'embedded group deviations cancel')
        need(len(exceptional)!=1,'one unbalanced group impossible')
        if len(exceptional)==2:
            g,h=exceptional;intersection=set(supports[g])&set(supports[h])
            need(all(delta[g][a][f]+delta[h][a][f]==0 for a in range(12) for f in range(3)),'two opposite embedded deviations')
            need(all(delta[g][a]==delta[h][a]==[0,0,0] for a in range(12) if a not in intersection),'two deviations confined to intersection')
            need(intersection,'disjoint exceptional pair impossible')
    column_quotas=all(sum(F[12*f+a][d] for a in range(12))==2 for f in range(3) for d in range(60))
    if column_quotas:need(all(sum(delta[g][a][f] for a in range(12))==0 for g in range(20) for f in range(3)),'zero per-group fibre sums with column quotas')
    return dict(row_sums=row_sums,row_margin_pass=margins,column_fibre_quotas_pass=column_quotas,exceptional_groups=exceptional,
                group_delta_12_by_3=delta,sum_delta_12_by_3=totals)

def base_factor(supports,groups,overrides=None):
    F=[[0]*60 for _ in range(36)]
    for g,(support,ds) in enumerate(zip(supports,groups)):
        word=[0,0,1,1,2,2] if overrides is None or g not in overrides else overrides[g]
        need(Counter(word)==Counter({0:2,1:2,2:2}),'control balanced word')
        for x,d in enumerate(ds):
            for i,a in enumerate(support):F[a+12*((word[i]+x)%3)][d]=1
    return F

def special_word(support,a,b,ca,cb):
    word=[None]*6;word[support.index(a)]=ca;word[support.index(b)]=cb
    remaining=[color for color in range(3) for _ in range(2-[ca,cb].count(color))]
    for i in range(6):
        if word[i] is None:word[i]=remaining.pop(0)
    return word

def swap_coordinates(F,column,a,b):
    for f in range(3):F[a+12*f][column],F[b+12*f][column]=F[b+12*f][column],F[a+12*f][column]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};rejections=[]
    def pin(path,expected=None):
        digest=sha(ROOT/path);need(expected is None or digest==expected,'input hash '+path);pins[path]=digest
    def reject(name,action):
        try:action()
        except(ValueError,KeyError,TypeError,IndexError):rejections.append(name)
        else:raise ValueError('corruption accepted '+name)
    try:
        pin(RAW,RAW_SHA);pin(DOC);raw=json.loads((ROOT/RAW).read_bytes());L=raw['L'];supports,groups=geometry(L)
        need([raw['prescribed_Gram36'][i][i] for i in range(36)]==[10]*36,'raw full-Gram diagonal supplies row margins for binaryF')
        pairs=[dict(groups=[g,h],intersection=sorted(set(supports[g])&set(supports[h])),size=len(set(supports[g])&set(supports[h]))) for g,h in combinations(range(20),2)]
        histogram=Counter(p['size'] for p in pairs)
        need(dict(histogram)=={0:1,1:16,2:58,3:60,4:47,5:8},'actual complete support-pair census')
        counterexample=next(p for p in pairs if p['size'] not in[0,3]);g,h=counterexample['groups']
        need([g,h]==[0,1] and counterexample['intersection']==[4,6],'first explicit counterexample')
        counterexample=dict(counterexample,supports=[supports[g],supports[h]],refuted_statement='Every pair of distinct raw supports has intersection size0or3.')
        save(out/'raw_support_census.json',dict(supports=supports,group_columns=groups,pairs=pairs,histogram=dict(histogram),pair_population=190))
        save(out/'refuted_intersection_premise.json',counterexample)
        balanced=base_factor(supports,groups);balanced_check=evaluate(balanced,L,supports,groups)
        need(balanced_check['exceptional_groups']==[] and balanced_check['column_fibre_quotas_pass'],'balanced row-margin control only')
        a,b=counterexample['intersection']
        overrides={g:special_word(supports[g],a,b,0,1),h:special_word(supports[h],a,b,1,0)}
        original=base_factor(supports,groups,overrides);positive=deepcopy(original)
        swap_coordinates(positive,groups[g][0],a,b);swap_coordinates(positive,groups[h][0],a,b)
        positive_check=evaluate(positive,L,supports,groups)
        need(positive_check['exceptional_groups']==[g,h] and positive_check['column_fibre_quotas_pass'],'literal two-exception cancellation positive')
        mismatches=[dict(rows=[i,j],actual=sum(positive[i][d]*positive[j][d] for d in range(60)),expected=raw['prescribed_Gram36'][i][j]) for i in range(36) for j in range(36)
                    if sum(positive[i][d]*positive[j][d] for d in range(60))!=raw['prescribed_Gram36'][i][j]]
        need(bool(mismatches),'control explicitly not a full Gram factor')
        save(out/'two_exception_positive.json',dict(factor=positive,checks=positive_check,full_Gram_mismatches=mismatches,
            scope='A genuine support/row-margin/column-quota cancellation fixture only; not a full Gram factor or target graph.'))
        one=deepcopy(original);swap_coordinates(one,groups[g][0],a,b)
        one_check=evaluate(one,L,supports,groups,False)
        need(one_check['exceptional_groups']==[g] and not one_check['row_margin_pass'],'one-exception control violates row margins')
        reject('one_uncancelled_exception',lambda:evaluate(one,L,supports,groups))
        bad=deepcopy(positive);swap_coordinates(bad,groups[h][0],a,b)
        reject('remove_opposite_deviation',lambda:evaluate(bad,L,supports,groups))
        bad=deepcopy(positive);bad[0][0]=2
        reject('nonbinary_factor',lambda:evaluate(bad,L,supports,groups))
        bad=deepcopy(positive);bad[0][0]=bool(bad[0][0])
        reject('Boolean_factor_entry',lambda:evaluate(bad,L,supports,groups))
        bad=deepcopy(positive);bad[0].pop()
        reject('short_factor_row',lambda:evaluate(bad,L,supports,groups))
        badL=deepcopy(L);badL[0][0]^=1
        reject('changed_support',lambda:evaluate(positive,badL,supports,groups))
        reject('claimed_zero_or_three_population',lambda:need(all(p['size'] in[0,3] for p in pairs),'false intersection premise'))
        wrong=deepcopy(positive_check['group_delta_12_by_3']);wrong[g][a][0]+=1
        reject('altered_delta_entry',lambda:need(wrong==evaluate(positive,L,supports,groups)['group_delta_12_by_3'],'literal delta identity'))
        # A newly derived stronger corollary is recorded separately as CANDIDATE.
        singleton_candidates=[list(v) for v in product(range(-1,3),repeat=3) if sum(v)==0]
        nonzero_zero_fibre=[v for v in singleton_candidates if any(v) and all(x==0 for x in v)]
        need(nonzero_zero_fibre==[],'singleton zero-fibre-sum algebra')
        candidate_pairs=[p['groups'] for p in pairs if p['size']<=1]
        need(len(candidate_pairs)==17,'specific17pairs for candidate corollary, not target coverage')
        timestamp=datetime.now(timezone.utc).isoformat()
        binding=dict(id='C-FIXED-HADAMARD-AT-MOST-TWO-GROUP-MARGIN-CANCELLATION',revision=1,
            statement='For every binary36x60 incidence matrix with the exact frozen coordinate-support L and row sums10, embed each group\'s6x3 coordinate/fibre counts minus1 into a12x3 deviation matrix. The twenty deviations sum to zero. Consequently exactly one unbalanced group is impossible; if exactly two groups g,h are unbalanced, their deviations are opposite and vanish outside the intersection of their supports, so disjoint supports are impossible.',
            kind='mathematical result',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
            scope='Necessary row-margin conditions on one fixed support, for any binary factor satisfying the stated support and margins. No general balance normalization or full-factor existence is asserted.',
            assumptions=['Exact pinned12x60 coordinate-support matrix.','BinaryF and36row sums10; every full prescribed-Gram factor satisfies these row sums by its diagonal.'],
            dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise',scope='Only the raw six_prism support component is used.')],
            verifier='/root/eight_domain_audit',discovery_source='/root proposed row-margin cancellation; reviewed here independently from rawF sums.',
            method='Written36-entry summation identity; complete raw190support-pair census; literal balanced and two-unbalanced positive margin fixtures; corrupted controls.',
            limitations=['No fullGram existence is inferred from the positive control; its fullGram mismatches are preserved.','The proposed0or3intersection restriction is refuted and is not a premise.','No all-balanced UNSAT result, residual completion, target automorphism or unrestricted exclusion is used.'],
            created_at=timestamp,updated_at=timestamp,artifact_availability='LOCAL_ONLY',external_review=False)
        save(out/'claim_binding.json',binding)
        save(out/'candidate_singleton_corollary.json',dict(status='CANDIDATE',review_state='NEEDS_RECHECK',discovery_agent='/root/eight_domain_audit',
            statement='With the additional literal column quotas of two entries per fibre, every group deviation also has zero fibre sums. Hence an exceptional pair cannot intersect in only one coordinate; exactly-two exceptional groups require support intersection size at least two.',
            scope='Additional row-margin-only necessary condition; on these raw supports it rules out17specified group-pair choices, not17graphs or a target fraction.',
            group_pairs=candidate_pairs,independent_approval=False,reason='New strengthening derived by this checker author; separate review required before promotion.'))
        save(out/'controls.json',dict(positive_margin_fixtures=2,full_factor_positive_claimed=False,corruptions_rejected=rejections,
            first_raw_intersection_counterexample=counterexample,one_exception_row_sums=one_check['row_sums']))
        pin('acceleration/audit_20260930_hadamard_two_group_margin_cancellation.py')
        for path in ['uv.lock','pyproject.toml']:pin(path)
        save(out/'summary.json',dict(status='INDEPENDENT_HADAMARD_TWO_GROUP_MARGIN_CANCELLATION_PASS',timestamp=timestamp,
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},
            support_groups=20,group_size=6,columns_per_group=3,coordinate_group_counts=[10]*12,group_pairs=190,support_intersection_histogram=dict(histogram),
            zero_or_three_proposal='REFUTED by raw groups0and1 intersecting in coordinates4and6.',
            newly_discovered_singleton_corollary='CANDIDATE; not independently promoted.',corruption_controls=len(rejections),
            verifier='/root/eight_domain_audit',shared_components=['Raw fixed support only; no producer imports, no shared summation implementation.'],
            scope=binding['scope'],target_resolution=False,solver_calls=0,artifact_availability='LOCAL_ONLY'))
        print(json.dumps(dict(status='INDEPENDENT_HADAMARD_TWO_GROUP_MARGIN_CANCELLATION_PASS',sha256=sha(out/'summary.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(__file__)));raise

if __name__=='__main__':main()
