"""Freeze the remaining minimum-ID fibre-orbit representatives, before batch build."""
from pathlib import Path
from collections import Counter,defaultdict
from itertools import permutations
from datetime import datetime,timezone
import argparse,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
GATE=I+'hadamard_fibre_profile_orbits/summary.json';MAPS=B+'hadamard_fibre_profile_orbits/maps.json';SCREEN=B+'hadamard_four_group_local_screen/';LOCAL=B+'hadamard_triplicate_counts/local_triples.json';RAW=B+'hadamard20_support/six_prism.json'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def sig(c):return tuple(c['groups']),tuple(tuple(x)for x in c['profile'])
def select(cases):
    lookup={sig(c):c['case']for c in cases};need(len(lookup)==108,'unique108 cases');records=[];orbits=defaultdict(list)
    for c in cases:
        action=[]
        for tau in permutations(range(3)):
            # Inverse-index pullback represents the same complete S3 action.
            p=tuple(tuple(row[tau.index(f)]for f in range(3))for row in c['profile']);action.append(lookup[(tuple(c['groups']),p)])
        need(len(set(action))==6,'free profile orbit');representative=min(action);orbits[representative].append(c['case']);records.append(dict(case=c['case'],representative=representative,orbit_actions=action))
    need(len(orbits)==18 and all(len(v)==6 for v in orbits.values()),'complete orbit partition')
    need(all(len({cases[k]['gram_caps_ac']['empty']for k in v})==1 for v in orbits.values()),'screen invariant on each orbit')
    rejected=[k for k in sorted(orbits)if cases[k]['gram_caps_ac']['empty']];survivors=[k for k in sorted(orbits)if not cases[k]['gram_caps_ac']['empty']]
    need(len(rejected)==2 and len(survivors)==16 and 0 in survivors,'frozen screen population')
    return records,orbits,rejected,survivors,[k for k in survivors if k!=0]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    try:
        need(sha(ROOT/GATE)=='c45fc396a1e5a345a7f94f1354303376742dd771c8eea64c10654699778da645','exact reviewed action gate');gate=read(GATE)
        for p in[GATE,MAPS,LOCAL,RAW,*[SCREEN+f'case_{k:03d}.json'for k in range(108)]]:
            h=sha(ROOT/p);need(p==GATE or gate['inputs_sha256'][p]==h,'reviewed immutable input '+p);pins[p]=h
        need(gate['status']=='INDEPENDENT_HADAMARD_GLOBAL_FIBRE_PROFILE_NORMALIZATION_PASS','semantic normalization gate')
        cases=[read(SCREEN+f'case_{k:03d}.json')for k in range(108)];need([c['case']for c in cases]==list(range(108)),'indexed cases')
        records,orbits,rejected,survivors,remaining=select(cases);saved=read(MAPS)
        need(records==[{k:r[k]for k in['case','representative','orbit_actions']}for r in saved['case_maps']],'complete saved profile action correspondence')
        local=read(LOCAL);words=local['words'];lookup=defaultdict(list)
        for i,tri in enumerate(local['survivors']):
            counts=tuple(tuple(sum(words[w][p]==f for w in tri)for f in range(3))for p in range(6));lookup[counts].append(i)
        raw=read(RAW);supports=[[a for a in range(12)if raw['L'][a][d]]for d in range(60)];groups=[]
        for s in supports:
            if s not in groups:groups.append(s)
        domains=[]
        for case_id in survivors:
            c=cases[case_id];entries=[]
            for side,g in enumerate(c['groups']):
                wanted=[[1]*3 for _ in groups[g]]
                for coord,delta in zip(c['common_support'],c['profile']):wanted[groups[g].index(coord)]=[1+c['relation'][side]*v for v in delta]
                indices=lookup[tuple(map(tuple,wanted))];need(indices==c['local_survivor_indices'][side]and len(indices)==c['domain_sizes'][side],'full unpruned initial local domain')
                entries.append(dict(group=g,support=groups[g],fixed_counts=wanted,local_survivor_indices=indices,initial_domain_size=len(indices),saved_AC_size=c['gram_caps_ac']['final_domain_sizes'][side]))
            rows=[sum((entry['fixed_counts'][entry['support'].index(a)][f]-1)for entry in entries if a in entry['support'])for a in range(12)for f in range(3)];need(rows==[0]*36,'all36 profile-margin deviations cancel')
            domains.append(dict(case=case_id,case_path=SCREEN+f'case_{case_id:03d}.json',case_sha256=pins[SCREEN+f'case_{case_id:03d}.json'],orbit_members=orbits[case_id],exceptional_groups=c['groups'],common_support=c['common_support'],circuit_relation=c['relation'],deviation_profile=c['profile'],initial_domains=entries,balanced_group_count=16,balanced_options_per_group=150,total_selectors=2400+sum(x['initial_domain_size']for x in entries),case0_already_attempted=case_id==0))
        controls=[]
        def rejected_control(name,f):
            try:f()
            except(ValueError,KeyError,IndexError):controls.append(name);return
            raise ValueError('accepted corruption '+name)
        rejected_control('duplicate_case',lambda:select(cases[:-1]+[cases[0]]))
        rejected_control('include_case0_again',lambda:need(remaining==survivors,'exact removed case0 orbit'))
        rejected_control('drop_representative',lambda:need(remaining[:-1]==remaining,'complete15 representative universe'))
        rejected_control('substitute_AC_domains',lambda:need(all(x['initial_domain_size']==x['saved_AC_size']for d in domains for x in d['initial_domains']),'initial domains cannot be replaced by AC sizes'))
        population=dict(selection_rule='Ascending minimum case ID of each complete global S3 fibre orbit; omit two prior-screen-empty orbits; omit entire case0 orbit already attempted. No other filter.',all_profiles=108,all_orbits=18,screen_empty_orbit_representatives=rejected,screen_survivor_representatives=survivors,case0_orbit=orbits[0],remaining_representatives=remaining,remaining_profile_count=sum(len(orbits[x])for x in remaining),all16_domain_records=domains,initial_domain_size_histogram=dict(Counter(x['initial_domain_size']for d in domains for x in d['initial_domains'])),remaining_selector_counts={str(d['case']):d['total_selectors']for d in domains if d['case']!=0})
        save(out/'expected_universe.json',population);save(out/'controls.json',dict(positive_complete_orbit_cases=108,positive_unpruned_exceptional_domains=64,positive_profile_margins=16*36,rejected_corruptions=controls))
        for p in[Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[p.resolve().relative_to(ROOT).as_posix()]=sha(p)
        result=dict(status='INDEPENDENT_REMAINING_FIFTEEN_PROFILE_UNIVERSE_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},remaining_representatives=remaining,counts=dict(original_profiles=108,original_orbits=18,screen_survivor_profiles=96,screen_survivor_orbits=16,already_attempted_case0_orbit_profiles=6,remaining_profiles=90,remaining_representatives=15),scope='Selection and initial-domain identity only for the checked fixed-support four-exception profiles. Neither feasibility nor new exclusion; fibre permutations relabel solutions, not hypothetical target automorphisms.',solver_calls=0,elapsed_seconds=time.perf_counter()-start,artifact_availability='LOCAL_ONLY');save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),remaining=remaining,domain_histogram=population['initial_domain_size_histogram'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
