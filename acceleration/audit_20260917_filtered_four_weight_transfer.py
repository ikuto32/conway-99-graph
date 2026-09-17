"""Independent exact raw-neighborhood review of ten fixed transferred weights."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm
import audit_20260917_moment_positive600 as direct

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('acceleration/results')
SUB=BASE/'20260917_filtered_four_weight_transfer'
FOUR=BASE/'20260917_partial_four_matchings'
FILTER=BASE/'20260917_four_coordinate_matching_filter/run01'
OUT=BASE/'20260917_independent_review/filtered_four_weight_transfer'
PINS={SUB/'summary.json':'293fcaa5f5eb1d6a771f515568be88fc3edf806aacc69fa8d8567fcd57394352',
      BASE/'20260917_independent_review/four_coordinate_matching_filter/summary.json':'6ee0eea6854f8e82e4067f60225f6c897908d5824f5d71c7d4564e21e86738b3',
      BASE/'20260917_independent_review/four_matching_filtered_moments.json':'472b7f332a99560fd961d7b6a411edd5db619504c21dd6285470f579e0ba2c51'}


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def require(c,m):
    if not c:raise ValueError(m)
def save(p,d):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2);f.write('\n')
def members(value):
    out=set()
    while value:
        bit=value&-value;out.add(bit.bit_length()-1);value-=bit
    return out


def compare(case,source,expected_q,calc):
    require(case['denominator']==source['denominator'] and case['denominator']>0,'denominator')
    require(case['moment_weight_numerators']==source['moment_weight_numerators'],'moment weights unchanged')
    require(case['reciprocity_weight_numerators']==expected_q,'reciprocity edge mapping/zeroextension')
    require(case['rhs_dot_numerator']==calc['dot'],'raw rhs product')
    require(case['center_maxima_numerators']==calc['maxima'],'all84 maxima')
    require(case['first_argmax_original_ids']==calc['argmax'],'first original argmax IDs')
    num=calc['dot']-sum(calc['maxima'])
    require(case['numerator']==num and case['strictly_positive']==(num>0),'exact bound sign/value')
    require(case['checked_columns']==230879,'full retained column count')


def main():
    OUT.mkdir(parents=True,exist_ok=False);bindings={};started=time.monotonic()
    def read(p):
        bindings[str(p).replace('\\','/')]=digest(p)
        return json.loads(Path(p).read_bytes())
    require(all(digest(p)==h for p,h in PINS.items()),'pinned inputs')
    summary=read(SUB/'summary.json');manifest=read(SUB/'manifest.json')
    fa=read(BASE/'20260917_independent_review/four_coordinate_matching_filter/summary.json')
    ma=read(BASE/'20260917_independent_review/four_matching_filtered_moments.json')
    require(fa['status']=='INDEPENDENT_FOUR_COORDINATE_NEIGHBORHOOD_MATCHING_FILTER_PASS','filter premise')
    require(ma['status']=='INDEPENDENT_FOUR_COORDINATE_FILTERED_FULL_MOMENT_MODEL_PASS','model premise')
    primary=read(FOUR/'manifest.json');old=read(BASE/'20260917_partial_two_matchings/manifest.json')
    require(digest(FOUR/'manifest.json')==fa['inputs_sha256'][(FOUR/'manifest.json').as_posix()],'same rawscope')
    require(summary['attempted']==summary['completed']==summary['selected']==10,'ten frozen attempts')
    require('added after' in manifest['timing_deviation'],'preregistration deviation disclosed')
    labels=[{2*a+s,2*b+t} for a,b in combinations(range(7),2) for s in(0,1) for t in(0,1)]
    known=[set() for _ in range(84)]
    for a,b in primary['remaining_fixed_K_edges_outer']:known[a].add(b);known[b].add(a)
    pairs=list(combinations(range(84),2));unknown=list(map(tuple,primary['unknown_edges_outer']))
    old_unknown=list(map(tuple,old['unknown_edges_outer']))
    require(len(unknown)==1920 and len(old_unknown)==1800 and set(old_unknown)<=set(unknown),'unknown scope containment')
    rhs={e:2-len(labels[e[0]]&labels[e[1]])-int(e[1] in known[e[0]]) for e in pairs}
    sources=[BASE/'20260917_two_matching_moments/exact_support_bound.json']+[BASE/f'20260917_two_coordinate_small_certificate/denominator_{d:03d}.json' for d in(1,2,4,8,16,32,64,128,256)]
    cases=[];originals=[];ys=[];qs=[];mapped=[];calculations=[]
    for i,path in enumerate(sources):
        source=read(path);source=source.get('bound',source);casepath=SUB/f'case_{i:02d}.json';case=read(casepath)
        require(digest(casepath)==summary['records'][i]['sha256'],'case record hash')
        require(Path(case['source_certificate'])==path and case['source_sha256']==digest(path),'source weights binding')
        q_old=dict(zip(old_unknown,source['reciprocity_weight_numerators']))
        q=[q_old[e] if e in q_old else 0 for e in unknown];y=source['moment_weight_numerators']
        require(len(y)==3486 and len(q)==1920 and all(type(v)is int for v in q+y),'integer dimensions')
        require(max(map(abs,y))<=source['denominator'],'moment norm')
        cases.append(case);originals.append(source);mapped.append(q)
        ys.append(dict(zip(pairs,y)));qs.append(dict(zip(unknown,q)))
        calculations.append(dict(dot=sum(w*rhs[e] for e,w in zip(pairs,y)),maxima=[],argmax=[]))
    direct.controls();count=0;maxL1=0
    for u in tqdm(range(84),desc='Independent ten raw-neighborhood weight checks',unit='center'):
        if time.monotonic()-started>240:
            save(OUT/'incomplete.json',dict(status='INCOMPLETE_AUDIT_TIME_CAP',completed_centers=u,checked_retained_choices=count,calculations=calculations,inputs_sha256=bindings));return 3
        dp=FOUR/f'domain_{u:02d}.json';fp=FILTER/f'vertex_{u:02d}.json'
        require(digest(dp)==fa['inputs_sha256'][dp.as_posix()] and digest(fp)==fa['inputs_sha256'][fp.as_posix()],'domain/filter raw hashes')
        table=read(dp)['domain_masks_hex'];filtered=read(fp);retained=filtered['surviving_ids']
        require(retained==sorted(set(retained)) and set(retained)==set(range(len(table)))-set(filtered['rejected_ids']),'retained original-ID partition')
        maxima=[None]*10;argmax=[None]*10
        for original_id in retained:
            chosen=members(int(table[original_id],16));require(not known[u]&chosen and len(known[u]|chosen)==12,'completed outerneighborhood')
            maxL1=max(maxL1,1+len(chosen)+66+sum(u<v for v in chosen))
            for k in range(10):
                value=direct.score(u,chosen,known[u],ys[k],qs[k])
                if maxima[k] is None or value>maxima[k]:maxima[k]=value;argmax[k]=original_id
        count+=len(retained)
        for k,calc in enumerate(calculations):calc['maxima'].append(maxima[k]);calc['argmax'].append(argmax[k])
        save(OUT/f'vertex_{u:02d}.json',dict(outer_vertex=u,retained_choices=len(retained),case_maxima=maxima,case_first_argmax_original_ids=argmax))
    require(count==230879,'all retained choices checked')
    for c,s,q,calc in zip(cases,originals,mapped,calculations):
        compare(c,s,q,calc)
        require(c['max_column_l1']==maxL1 and c['integer_dot_absolute_bound']==maxL1*max(map(abs,q+s['moment_weight_numerators'])),'integer arithmetic guard')
    controls=[]
    for name,edit in [('numerator',lambda c:c.update(numerator=c['numerator']+1)),
                      ('maximum',lambda c:c['center_maxima_numerators'].__setitem__(0,c['center_maxima_numerators'][0]+1)),
                      ('original_id',lambda c:c['first_argmax_original_ids'].__setitem__(0,-1)),
                      ('moment_weight',lambda c:c['moment_weight_numerators'].__setitem__(0,c['moment_weight_numerators'][0]+1)),
                      ('mapped_q',lambda c:c['reciprocity_weight_numerators'].__setitem__(0,c['reciprocity_weight_numerators'][0]+1)),
                      ('denominator',lambda c:c.update(denominator=0))]:
        bad=deepcopy(cases[0]);edit(bad)
        try:compare(bad,originals[0],mapped[0],calculations[0])
        except ValueError:controls.append(dict(name=name,outcome='REJECT'))
        else:raise ValueError('Corrupt result accepted')
    records=[dict(case=i,source_certificate=str(sources[i]),numerator=c['numerator'],denominator=c['denominator'],
                  rhs_dot=calc['dot'],sum_maxima=sum(calc['maxima']),positive=c['numerator']>0,
                  every_retained_column_checked=True,all84_maxima_and_original_argmax_verified=True,
                  raw_case_sha256=digest(SUB/f'case_{i:02d}.json')) for i,(c,calc) in enumerate(zip(cases,calculations))]
    require(all(not r['positive'] for r in records) and summary['positive']==0,'reported nonpositive fixed weight outcomes')
    for p in(Path(__file__),Path(direct.__file__),Path(direct.h.__file__),Path('uv.lock')):bindings[str(p).replace('\\','/')]=digest(p)
    require(all(digest(p)==h for p,h in bindings.items()),'inputs unchanged')
    report=dict(status='INDEPENDENT_FILTERED_FOUR_TEN_WEIGHT_TRANSFER_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
        python=platform.python_version(),inputs_sha256=bindings,records=records,weight_sets_checked=10,retained_choices_per_set=230879,
        distinct_retained_choices=230879,positive_bounds=0,nonpositive_bounds=10,controls=controls,positive_rook_controls=True,
        scope=manifest['scope'],timing_deviation=manifest['timing_deviation'],
        method='Python unbounded integer sums over every rawfullouterneighborhood and unknownedge; mapping oldq by edge and zeroextension; allmaxima/argmax IDs independent of serializedCSR.',
        producer_imported=False,serialized_matrix_loaded=False,
        shared_components=['Earlier independent raw-neighborhood scorer and rookcontrols','Python standard library','tqdm display','Hash-bound prior complete-domain/filter/model audits'],
        disclosure='This reviewer produced the matchingfilter but does not approve it here; partition validity is a premise from the distinct matchingfilter independent audit.',
        mathematical_conclusion='These ten specific fixed transferred weight sets fail to provide a strictly positive support lowerbound on this declared filteredfamily.',
        feasibility_established=False,exclusion_established=False,unrestricted_target_result=False,ledger_edited=False,elapsed_seconds=time.monotonic()-started)
    save(OUT/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(OUT/'summary.json'),elapsed_seconds=report['elapsed_seconds'])))
    return 0


if __name__=='__main__':raise SystemExit(main())
