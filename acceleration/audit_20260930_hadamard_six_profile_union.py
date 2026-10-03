"""Independent exact six-profile coverage composition; no discovery imports."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from itertools import permutations
from pathlib import Path
import argparse, gzip, hashlib, json, platform, subprocess, sys, time, traceback

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
GATES={
 'hadamard_six_exception_census':('4a82b3d74c0015804b844612051596e828439e2ffb73735d3d7689899c6141cd','INDEPENDENT_HADAMARD_SIX_EXCEPTION_KERNEL_CENSUS_PASS'),
 'hadamard_six_rank4_profiles':('0430355de5159a5223c464d3766ec54206a37177b90e18cf92364d276dd483e3','INDEPENDENT_SIX_RANK4_INTEGER_MARGINAL_CENSUS_PASS'),
 'hadamard_six_profile_local_domains':('976e673b02c8742503a33d091e6ddf4650c13289e25fd859cb7854deb0174235','INDEPENDENT_SIX_EXCEPTION_LOCAL_DOMAIN_FILTER_PASS'),
 'hadamard_six_profile_arc_v3':('82be6d4389596959365d5551694f3e1361d0bc855405f2647a682784be1f34ba','INDEPENDENT_SIX_EXCEPTION_PROFILE_ARC_SCREEN_PASS'),
 'hadamard_six_fibre_orbits':('ea4289a741ed19231d88fec5d917428b3ffc2c497a116268c90344448b665109','INDEPENDENT_HADAMARD_SIX_EXCEPTION_FIBRE_NORMALIZATION_PASS'),
 'hadamard_six_profile_cnf':('09997159af6339561bd76aa05e0fed1118f8dfe629413ccbef4c8f05e7947e29','INDEPENDENT_HADAMARD_SIX_PROFILE_ENCODING_PASS'),
 'hadamard_six_profile_unsat':('6d790eea59e2e0924f2c41df36c86ae899a41b03d1d4dddb623431a3f4e7b6b2','INDEPENDENT_FIXED_HADAMARD_SIX_PROFILE0000_UNSAT_PASS'),
 'hadamard_fiftyfour_profile_cnfs':('4fa50584776c9862e4e4c0286567b212b9a436c13a6cf0ebf0cd0b0ad751a6e5','INDEPENDENT_HADAMARD_FIFTYFOUR_PROFILE_ENCODING_PASS'),
 'hadamard_fiftyfour_profile_proofs':('01cfb489e617f16f9c1773e7f10a579de018d87af39738427f52352593d53ee0','INDEPENDENT_FIXED_HADAMARD_FIFTYFOUR_PROFILE_UNSAT_PASS'),
 'hadamard_four_profile_union':('5cc01233ebc8baeff1de6321e0e04f0754a8e8d25790ce17c96e5771fb02ab5c','INDEPENDENT_FIXED_HADAMARD_FOUR_PROFILE_UNION_PASS')}
RAW=B+'hadamard20_support/six_prism.json';RAW_HASH='ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'
UNIVERSE=B+'hadamard_six_profile_local_domains/profiles.jsonl.gz';UNIVERSE_HASH='221d913515ad8e8dedfbca6a9453b2dce1f538462bce1c7cb9f66b202a3bc2a0'

def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def literal_key(groups,delta):return tuple(groups),tuple(tuple(tuple(v)for v in a)for a in delta)
def image(delta,pullback):
    need(sorted(pullback)==[0,1,2],'fibre bijection')
    return [[a[pullback[f]][:]for f in range(3)]for a in delta]
def cover(universe,excluded,orbits,reps):
    need(len(universe)==984 and len(set(universe))==984,'984 distinct literal profiles')
    need(len(excluded)==654 and len(set(excluded))==654,'654 distinct AC exclusions')
    need(len(reps)==55 and len(set(reps))==55 and set(reps)==set(orbits),'55 exact representative identities')
    members=[x for r in reps for x in orbits[r]]
    need(len(members)==330 and len(set(members))==330,'330 disjoint orbit members')
    need(all(len(orbits[r])==6 and r in orbits[r]for r in reps),'six-element identity-containing orbits')
    need(not(set(excluded)&set(members)) and set(excluded)|set(members)==set(universe),'literal disjoint union, no missing profiles')
def replay_binding(replay,cnf_hash,proof_hash):
    need(replay['accepted']is True and replay['actual_exit_code']==0 and replay['expected_acceptance']is True,'accepted independent complete replay')
    need(replay['cnf_sha256']==cnf_hash and replay['proof_sha256']==proof_hash,'exact replay pair')
def scope_binding(scope,profile,raw):
    need(scope['selected_profile_id']==profile['id'] and scope['selected_profile_sha256']==profile['profile_sha256'],'literal profile identity')
    need(scope['exceptional_groups']==profile['group_ids'] and scope['coordinate_fibre_deviations']==profile['coordinate_fibre_deviations'],'literal profile values')
    need(scope['balanced_groups']==[g for g in range(20)if g not in profile['group_ids']],'exact complement of exceptional groups')
    need(scope['core_adjacency36']==raw['core_adjacency'] and scope['prescribed_Gram36']==raw['prescribed_Gram36'] and scope['L12x60']==raw['L'],'literal core/Gram/support')
    need(scope['raw_support_path']==RAW and scope['raw_support_sha256']==RAW_HASH and scope['profile_universe_path']==UNIVERSE and scope['profile_universe_sha256']==UNIVERSE_HASH,'immutable scope inputs')
    need(scope['initial_domain_references']==profile['local_domains'],'complete initial local-domain references')
    need(scope['within_group_column_caps_encoded']is True and scope['cross_group_column_caps_encoded']is False and scope['residual_D_encoded']is False,'weaker necessary full-Gram model')
    need(scope['arc_pruning_used']is False and scope['orbit_coverage_used']is False and scope['balance_WLOG']is False and scope['assumed_target_automorphism']is None,'no hidden reduction in literal formula')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h):
        need(isinstance(h,str)and len(h)==64,'required hash '+p)
        if p not in pins:pins[p]=sha(ROOT/p)
        need(pins[p]==h,'input identity '+p)
    def gate_output(folder,path):
        pin(path,gates[folder]['outputs_sha256'][path]);return read(path)
    try:
        gates={}
        for folder,(h,status)in GATES.items():
            p=I+folder+'/summary.json';pin(p,h);gates[folder]=read(p);need(gates[folder]['status']==status,'approved exact premise '+folder)
        bindings={}
        for folder in GATES:
            p=I+folder+('/claim_bindings.json'if folder=='hadamard_four_profile_union'else'/claim_binding.json')
            q=gate_output(folder,p)
            for c in q if isinstance(q,list)else[q]:
                need(c['revision']==1 and c['status']=='VERIFIED'and c['review_state']=='CLEAR','exact reviewed claim revision');bindings[c['id']]=dict(path=p,sha256=pins[p],revision=1)
        pin(RAW,RAW_HASH);raw=read(RAW);pin(UNIVERSE,UNIVERSE_HASH)
        for folder in ['hadamard_six_profile_local_domains','hadamard_six_profile_arc_v3','hadamard_six_fibre_orbits','hadamard_six_profile_cnf','hadamard_fiftyfour_profile_cnfs']:
            need(gates[folder]['inputs_sha256'][UNIVERSE]==UNIVERSE_HASH and gates[folder]['inputs_sha256'][RAW]==RAW_HASH,'all premises use same literal universe/support')
        with gzip.open(ROOT/UNIVERSE,'rt',encoding='utf-8')as f:profiles=[json.loads(line)for line in f]
        ids=[p['id']for p in profiles];byid={p['id']:p for p in profiles};lookup={literal_key(p['group_ids'],p['coordinate_fibre_deviations']):p['id']for p in profiles};need(len(ids)==len(lookup)==len(byid)==984,'unique literal universe')
        # Bind every old complete marginal path to this local-domain universe.
        mp=I+'hadamard_six_rank4_profiles/all_positive_marginal_profiles.json';marginal=gate_output('hadamard_six_rank4_profiles',mp)['records'];old_paths={(r['case'],tuple(r['groups']),tuple(path))for r in marginal for path in r['ordered_choice_paths']}
        need({(p['rank4_case'],tuple(p['group_ids']),tuple(p['choice_path']))for p in profiles}==old_paths and len(old_paths)==984,'complete upstream marginal population, not sampled paths')
        for p in profiles:
            for d in p['local_domains']:
                pin(d['path'],d['sha256']);need(gates['hadamard_six_profile_local_domains']['inputs_sha256'][d['path']]==d['sha256'],'same complete checked local domain')
        outcomes=gate_output('hadamard_six_profile_arc_v3',I+'hadamard_six_profile_arc_v3/profile_outcomes.json')['records'];need([r['id']for r in outcomes]==ids and [r['index']for r in outcomes]==list(range(984)),'AC population ordering')
        empty={r['id']:r['combined_empty']for r in outcomes};need(all(type(v)is bool for v in empty.values()),'literal AC Boolean classifications')
        excluded=[x for x in ids if empty[x]];orbits={};maps=[];allorbits={};taus=list(permutations(range(3)))
        for p in profiles:
            actions=[]
            for tau in taus:
                destination=lookup[literal_key(p['group_ids'],image(p['coordinate_fibre_deviations'],tau))];actions.append(destination)
                need(image(image(p['coordinate_fibre_deviations'],tau),[tau.index(f)for f in range(3)])==p['coordinate_fibre_deviations'],'inverse literal fibre action')
            members=sorted(actions);rep=min(members);need(len(set(members))==6 and all(empty[x]==empty[p['id']]for x in members),'six distinct images and independently checked AC label covariance')
            allorbits[rep]=members
            if not empty[p['id']]:orbits[rep]=members
            maps.append(dict(profile_id=p['id'],representative=rep,images=actions,AC_excluded=empty[p['id']]))
        need(len(allorbits)==164,'complete164 orbits')
        saved=gate_output('hadamard_six_fibre_orbits',I+'hadamard_six_fibre_orbits/independent_orbits.json')['orbits']
        need({r['representative_id']:sorted(r['member_ids'])for r in saved}==allorbits,'literal actions reproduce authenticated normalization')
        # Exact numerical coefficient invariance is a check of the general row-relabeling argument.
        C=raw['core_adjacency'];G=raw['prescribed_Gram36']
        for tau in taus:
            rows=[12*tau[f]+a for f in range(3)for a in range(12)]
            need(all(C[rows[i]][rows[j]]==C[i][j]and G[rows[i]][rows[j]]==G[i][j]for i in range(36)for j in range(36)),'raw core and Gram invariant under global fibre relabeling')
        proofgate=gates['hadamard_fiftyfour_profile_proofs'];enc=gates['hadamard_fiftyfour_profile_cnfs'];zero=gates['hadamard_six_profile_unsat'];enc0=gates['hadamard_six_profile_cnf'];records=proofgate['profile_records']
        need(proofgate['completed_proof_replays']==len(records)==54 and proofgate['UNKNOWN']==0 and proofgate['SAT_pending_separate_review']==0 and proofgate['unattempted_profiles']==[],'complete54 approved proof records')
        reps=['rank4_00_profile_0000']+[r['profile_id']for r in records];need(proofgate['selected_profiles']==reps[1:],'proof identity order');cover(ids,excluded,orbits,reps)
        proofrecords=[];scope_samples=[];proof_bytes=0
        def receipt(folder,gate,replay,cnf_hash,proof_hash):
            replay_binding(replay,cnf_hash,proof_hash)
            p=I+folder+'/'+replay['name']+'.receipt.json';need(gate_output(folder,p)==replay,'literal replay receipt')
            for suffix in ['stdout','stderr']:
                p=I+folder+'/'+replay['name']+'.'+suffix+'.log';pin(p,gate['outputs_sha256'][p]);need(pins[p]==replay[suffix+'_sha256'],'replay output hash')
                if suffix=='stdout':need('s VERIFIED'in(ROOT/p).read_text(),'checker acceptance output')
        for r in records:
            pid=r['profile_id'];p=byid[pid]
            for field in ['cnf','model','scope']:
                pin(r[field+'_path'],r[field+'_sha256']);need(enc['inputs_sha256'][r[field+'_path']]==r[field+'_sha256'],'encoding binds complete proof input')
            s=read(r['scope_path']);scope_binding(s,p,raw);scope_samples.append(s)
            need(r['literal_profile']=={k:s[k]for k in r['literal_profile']},'proof literal scope record')
            selected=str(Path(r['scope_path']).parent/'selected_profile.json').replace('\\','/');pin(selected,s['selected_profile_artifact_sha256']);need(read(selected)==p,'literal selected profile artifact')
            trace=r['trace'];pin(trace['path'],trace['sha256']);need((ROOT/trace['path']).stat().st_size==trace['bytes'],'complete trace bytes');proof_bytes+=trace['bytes']
            receipt('hadamard_fiftyfour_profile_proofs',proofgate,r['replay'],r['cnf_sha256'],trace['sha256'])
            for field in ['run_summary','native_receipt']:pin(r[field+'_path'],r[field+'_sha256'])
            proofrecords.append(dict(profile_id=pid,scope_sha256=r['scope_sha256'],cnf_sha256=r['cnf_sha256'],proof_sha256=trace['sha256'],proof_bytes=trace['bytes'],orbit_members=orbits[pid]))
        paths0={field:B+'hadamard_six_profile_cnf/profile_0000/'+file for field,file in [('cnf','instance.cnf'),('model','model.json'),('scope','scope.json')]}
        for p in paths0.values():pin(p,enc0['inputs_sha256'][p]);need(zero['inputs_sha256'][p]==pins[p],'prior encoding/proof binding')
        scope0=read(paths0['scope']);scope_binding(scope0,profiles[0],raw)
        t0=zero['proof'];need(t0['complete_independent_replay']is True,'prior proof complete');pin(t0['path'],t0['sha256']);need((ROOT/t0['path']).stat().st_size==t0['bytes'],'prior full trace bytes');proof_bytes+=t0['bytes']
        replay0=next(r for r in zero['replays']if r['name']=='complete_profile0000_proof');receipt('hadamard_six_profile_unsat',zero,replay0,pins[paths0['cnf']],t0['sha256'])
        proofrecords.insert(0,dict(profile_id=reps[0],scope_sha256=pins[paths0['scope']],cnf_sha256=pins[paths0['cnf']],proof_sha256=t0['sha256'],proof_bytes=t0['bytes'],orbit_members=orbits[reps[0]]))
        controls=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,KeyError):controls.append(name);return
            raise ValueError('corruption accepted '+name)
        reject('missing_representative',lambda:cover(ids,excluded,orbits,reps[:-1]));reject('duplicate_representative',lambda:cover(ids,excluded,orbits,reps[:-1]+[reps[0]]))
        bad=deepcopy(orbits);bad[reps[0]][0]=bad[reps[1]][0];reject('overlap_and_gap',lambda:cover(ids,excluded,bad,reps))
        reject('wrong_AC_identity',lambda:cover(ids,[reps[0],*excluded[1:]],orbits,reps));reject('unknown_universe_ID',lambda:cover(ids[:-1]+['not_a_profile'],excluded,orbits,reps))
        reject('nonbijective_fibre_map',lambda:image(profiles[0]['coordinate_fibre_deviations'],[0,0,2]))
        r=deepcopy(records[0]['replay']);r['accepted']=False;reject('unaccepted_replay',lambda:replay_binding(r,records[0]['cnf_sha256'],records[0]['trace']['sha256']))
        reject('wrong_CNF_identity',lambda:replay_binding(records[0]['replay'],'0'*64,records[0]['trace']['sha256']))
        reject('wrong_proof_identity',lambda:replay_binding(records[0]['replay'],records[0]['cnf_sha256'],'0'*64))
        bad=deepcopy(scope_samples[0]);bad['coordinate_fibre_deviations'][0][0][0]+=1;reject('changed_literal_scope',lambda:scope_binding(bad,byid[records[0]['profile_id']],raw))
        bad=deepcopy(scope_samples[0]);bad['arc_pruning_used']=True;reject('unreviewed_scope_restriction',lambda:scope_binding(bad,byid[records[0]['profile_id']],raw))
        # Standalone small known partition, and exact integer-case composition.
        toy=[list(range(i,i+6))for i in range(0,18,6)];need(Counter(x for o in toy for x in o)==Counter(range(18)),'known disjoint partition positive')
        need(set(range(6)).isdisjoint({6})and set(range(6))|{6}==set(range(7)),'disjoint0..5 and6 cases')
        save(out/'controls.json',dict(rejected_corruptions=controls,positive_actual_partition=True,small_partition_positive=toy,integer_exception_partition=[list(range(6)),[6]],full_factor_positive_fixture=None,full_factor_positive_fixture_null_reason='This checks a coverage composition, not a factor validator.'))
        save(out/'coverage.json',dict(profile_population=ids,AC_excluded=excluded,all_orbits=allorbits,proof_representatives=reps,proof_orbits=orbits,profile_maps=maps,covered_once=dict(Counter(excluded+[x for r in reps for x in orbits[r]])),proof_records=proofrecords))
        for p,h in [('docs/DERIVATION_20260930_SIX_PROFILE_UNION_CANDIDATE.md','646aa2e5c3c440c8dccfe0356e7307dfdaf48d42f9a5bbe978b201ce04e0af11')]:pin(p,h)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_SIX_PROFILE_UNION.md','uv.lock','pyproject.toml']:pin(p,sha(ROOT/p))
        ts=datetime.now(timezone.utc).isoformat();base=dict(revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',verifier='/root/eight_domain_audit',checking_method='Independent literal984-profile action/partition and exact55 scope/encoding/proof-identity composition. Separate written implication proof. No new solver or DRAT call.',trusted_components=['Previously independently checked marginal coverage, local-domain coverage, AC soundness, global-fibre normalization, exact encodings and complete DRAT replays at pinned hashes.','Python standard-library exact integers, sets, JSON and SHA256. No producer or earlier checker imports.'],assumptions=['Binary36x60 factor on exactly the pinned six-prism Hadamard support, with its full prescribed integer Gram.','All distinct outside-column overlaps are at most2, including within each identical-support group.'],limitations=['One literal fixed-support family only; no exclusion of all supports, the six-prism core or unrestricted Conway99.','Seven or more exceptional groups remain unresolved by these statements.','No automorphism of a hypothetical target is assumed.','Reuses prior mathematical and proof gates as explicit premises; this run does not repeat their exhaustive searches, encoding reconstruction or DRAT algorithms.'],artifact_availability='LOCAL_ONLY',availability_reason='Awaiting parent publication.',external_review=None,external_review_null_reason='Internal independent composition only.',created_at=ts,updated_at=ts,inputs_sha256=pins,premise_bindings=bindings)
        first=dict(base,id='C-FIXED-HADAMARD-EXACTLY-SIX-UNBALANCED-GROUPS-EXCLUSION',statement='No binary36x60 factor on the pinned six-prism Hadamard support can simultaneously have the prescribed full integer Gram, every outside-column overlap at most2, and exactly six unbalanced identical-support triplicate groups.',scope='All exactly-six-unbalanced factors on this one fixed support; the complete984 necessary profiles are covered exactly once by654 AC exclusions and330 members of55 proof-excluded fibre orbits.',dependencies=[dict(id=x,revision=1,relation=r)for x,r in [('C-FIXED-HADAMARD-SIX-EXCEPTION-KERNEL-CENSUS','coverage'),('C-FIXED-HADAMARD-SIX-EXCEPTION-INTEGER-MARGINAL-CENSUS','coverage'),('C-FIXED-HADAMARD-SIX-EXCEPTION-LOCAL-DOMAIN-FILTER','coverage'),('C-FIXED-HADAMARD-SIX-EXCEPTION-PAIRWISE-PROFILE-SCREEN','uses_result'),('C-FIXED-HADAMARD-SIX-EXCEPTION-FIBRE-NORMALIZATION','normalization'),('C-FIXED-HADAMARD-SIX-EXCEPTION-PROFILE0000-GRAM-ENCODING','encoding_equivalence'),('C-FIXED-HADAMARD-SIX-EXCEPTION-PROFILE0000-EXCLUSION','uses_result'),('C-FIXED-HADAMARD-FIFTYFOUR-SIX-EXCEPTION-GRAM-ENCODINGS','encoding_equivalence'),('C-FIXED-HADAMARD-FIFTYFOUR-SIX-EXCEPTION-PROFILE-EXCLUSIONS','uses_result')]])
        second=dict(base,id='C-FIXED-HADAMARD-AT-MOST-SIX-UNBALANCED-GROUPS-EXCLUSION',statement='Every binary36x60 factor on the pinned six-prism Hadamard support with the prescribed full integer Gram and all outside-column overlaps at most2 has at least seven unbalanced identical-support triplicate groups.',scope='At-most-six-unbalanced subfamily excluded by disjoint integer cases0..5 and6; no assertion of existence for seven or more.',dependencies=[dict(id=x,revision=1,relation='uses_result')for x in ['C-FIXED-HADAMARD-AT-MOST-FIVE-UNBALANCED-GROUPS-EXCLUSION',first['id']]])
        save(out/'claim_bindings.json',[first,second]);result=dict(status='INDEPENDENT_FIXED_HADAMARD_SIX_PROFILE_UNION_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},profile_population=984,AC_exclusions=654,proof_representatives=55,proof_orbit_members=330,all_orbits=164,duplicate_coverage=0,missing_profiles=0,authenticated_complete_proof_bytes=proof_bytes,approved_claim_ids=[first['id'],second['id']],rejected_corruptions=len(controls),new_native_calls=0,new_DRAT_replays=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),elapsed_seconds=result['elapsed_seconds'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
