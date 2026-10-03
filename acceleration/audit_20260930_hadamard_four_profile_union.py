"""Independent exact profile/proof composition; no native solver or DRAT replay."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from itertools import permutations
from pathlib import Path
import argparse,hashlib,json,platform,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
PINS={I+'hadamard_four_group_local_screen/summary.json':'ff30d47b012d1661182f1cba066425dd9d5aaccad3754cad4d526b7477725c67',I+'four_group_ac_calibration/summary.json':'6e53216e9d00ec8990217f80b84c3ed8cc1766d5eaae85c1fc3aead081b4ec6e',I+'hadamard_fibre_profile_orbits/summary.json':'c45fc396a1e5a345a7f94f1354303376742dd771c8eea64c10654699778da645',I+'hadamard_case0_profile_cnf/summary.json':'ea0398fc4ac25ac4746effab578499d21eaa2ae67fc17509e5780e770835c186',I+'hadamard_case0_profile_unsat/summary.json':'355b0b6dbc9707cc86dda748ad5dd0f05bfa6eb7090ab5dd8c30db3df91ebba9',I+'hadamard_fifteen_profile_cnfs/summary.json':'8566b0ab977d4918a51708e3f6390ef276483bc6a7b55722c59c4b2825c4f88b',I+'hadamard_fifteen_profile_unsat_v2/summary.json':'351b66f7b01f5863e932991737b8d35f4b1c043b48ff673c987c653d6ed81768',I+'hadamard_few_exception_marginals/summary.json':'6b9512567a77ef3bad2fbb1b581fadb30c486c9ac4151543001705776e0c5df9',I+'five_unbalanced_groups/summary.json':'d0b20b9c7ff9d6d99c7ed75dce6d935357dd322389870a5a9b53a6ec2d1634df',I+'hadamard_remaining_profile_universe/summary.json':'dffd4d638ee0cfca637a6ae4ba1a5cff5d7cb40d50f0dad2a9dd8f3ac79853ec'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def cover(excluded,orbitlists,reps):
    need(len(excluded)==12 and len(set(excluded))==12,'twelve distinct local exclusions')
    need(len(reps)==16 and len(set(reps))==16 and set(reps)==set(orbitlists),'exact sixteen proof representatives')
    members=[x for r in reps for x in orbitlists[r]];need(len(members)==96 and len(set(members))==96,'disjoint sixteen six-element orbits')
    need(all(len(orbitlists[r])==6 and r in orbitlists[r]for r in reps),'six-member identity-containing orbits')
    need(not(set(excluded)&set(members))and set(excluded)|set(members)==set(range(108)),'exact disjoint108 union')
def proof_binding(r,encoding):
    for field in['cnf','model','scope']:need(encoding[r[field+'_path']]==r[field+'_sha256'],'encoding/proof exact input identity')
    need(r['proof']['complete_independent_replay']is True and r['replay']['accepted']is True and r['replay']['actual_exit_code']==0,'complete accepted independent replay')
    need(r['replay']['cnf_sha256']==r['cnf_sha256']and r['replay']['proof_sha256']==r['proof']['sha256'],'replay binds both exact files')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        actual=sha(ROOT/p);need(h is None or h==actual,'input identity '+p);pins[p]=actual
    try:
        for p,h in PINS.items():pin(p,h)
        gates={p:read(p)for p in PINS};screen=gates[I+'hadamard_four_group_local_screen/summary.json'];orbitgate=gates[I+'hadamard_fibre_profile_orbits/summary.json'];proofs=gates[I+'hadamard_fifteen_profile_unsat_v2/summary.json'];zero=gates[I+'hadamard_case0_profile_unsat/summary.json'];encoding=gates[I+'hadamard_fifteen_profile_cnfs/summary.json'];enc0=gates[I+'hadamard_case0_profile_cnf/summary.json']
        need(proofs['status']=='INDEPENDENT_FIXED_HADAMARD_FIFTEEN_PROFILE_UNSAT_PASS'and proofs['completed_proof_replays']==15 and proofs['SAT']==proofs['UNKNOWN']==0,'fifteen complete approved exclusions');need(zero['status']=='INDEPENDENT_FIXED_HADAMARD_CASE0_PROFILE_UNSAT_PASS','prior case0 exclusion')
        # Authenticate the precise mathematical statements, not mutable ledger labels.
        for folder in['hadamard_four_group_local_screen','hadamard_fibre_profile_orbits','hadamard_case0_profile_unsat','hadamard_fifteen_profile_unsat_v2','five_unbalanced_groups']:
            p=I+folder+'/claim_binding.json';pin(p,gates[I+folder+'/summary.json']['outputs_sha256'][p])
            need(read(p)['revision']==1 and read(p)['status']=='VERIFIED','exact reviewed premise revision')
        p=I+'hadamard_few_exception_marginals/claim_bindings.json';pin(p,gates[I+'hadamard_few_exception_marginals/summary.json']['outputs_sha256'][p]);few=read(p);need(any(r['id']=='C-FIXED-HADAMARD-AT-MOST-THREE-UNBALANCED-GROUPS-EXCLUSION'and r['revision']==1 for r in few),'at-most-three premise')
        cases=[]
        for i in range(108):
            p=B+f'hadamard_four_group_local_screen/case_{i:03d}.json';pin(p,screen['inputs_sha256'][p]);cases.append(read(p))
        lookup={(tuple(c['groups']),tuple(map(tuple,c['profile']))):c['case']for c in cases};need(len(lookup)==108,'unique frozen profile universe')
        excluded=[c['case']for c in cases if c['gram_caps_ac']['empty']];orbits={};mapping=[]
        for c in cases:
            images=[]
            for tau in permutations(range(3)):
                profile=tuple(tuple(row[tau.index(f)]for f in range(3))for row in c['profile']);images.append(lookup[tuple(c['groups']),profile])
            rep=min(images);need(len(set(images))==6 and all(cases[j]['gram_caps_ac']['empty']==c['gram_caps_ac']['empty']for j in images),'literal profile action/labels')
            if not c['gram_caps_ac']['empty']:orbits[rep]=sorted(images)
            mapping.append(dict(case=c['case'],representative=rep,images=images,excluded_by_local_screen=c['gram_caps_ac']['empty']))
        p=B+'hadamard_fibre_profile_orbits/maps.json';pin(p,orbitgate['inputs_sha256'][p]);saved=read(p)
        need(all(r['representative']==mapping[r['case']]['representative']and r['orbit_actions']==mapping[r['case']]['images']for r in saved['case_maps']),'authenticated normalization maps')
        records=proofs['case_records'];reps=[0]+[r['case']for r in records];need(reps==[0]+encoding['selected_cases'],'all exact encoded representatives');cover(excluded,orbits,reps)
        proofrecords=[]
        for r in records:
            proof_binding(r,encoding['inputs_sha256'])
            for field in['cnf','model','scope']:pin(r[field+'_path'],r[field+'_sha256'])
            scope=read(r['scope_path']);c=cases[r['case']]
            need(scope['selected_case']==r['case']and scope['exceptional_groups']==c['groups']and scope['common_support']==c['common_support']and scope['circuit_relation']==c['relation']and scope['deviation_profile']==c['profile'],'literal representative input scope')
            need(scope['within_group_column_caps_encoded']and not scope['cross_group_column_caps_encoded']and not scope['residual_D_encoded'],'weaker full-Gram input covers capped profile')
            pin(r['proof']['path'],r['proof']['sha256']);need((ROOT/r['proof']['path']).stat().st_size==r['proof']['bytes'],'complete proof bytes')
            folder=I+'hadamard_fifteen_profile_unsat_v2/';name=r['replay']['name']
            for suffix in['.receipt.json','.stdout.log','.stderr.log']:
                p=folder+name+suffix;pin(p,proofs['outputs_sha256'][p])
            need(read(folder+name+'.receipt.json')==r['replay'],'literal saved replay receipt');need('s VERIFIED'in(ROOT/(folder+name+'.stdout.log')).read_text(),'accepted checker output')
            proofrecords.append(dict(case=r['case'],cnf_sha256=r['cnf_sha256'],proof_sha256=r['proof']['sha256'],orbit_members=orbits[r['case']]))
        cnf0=B+'hadamard_case0_profile_cnf/instance.cnf';scope0=B+'hadamard_case0_profile_cnf/scope.json';pin(cnf0,enc0['inputs_sha256'][cnf0]);pin(scope0,enc0['inputs_sha256'][scope0]);s0=read(scope0);need(s0['exceptional_groups']==cases[0]['groups']and s0['deviation_profile']==cases[0]['profile'],'literal case0 scope')
        replay0=next(r for r in zero['replays']if r['name']=='complete_case0_proof');need(replay0['accepted']and replay0['actual_exit_code']==0 and replay0['cnf_sha256']==pins[cnf0]and replay0['proof_sha256']==zero['proof']['sha256'],'case0 exact proof premise');pin(zero['proof']['path'],zero['proof']['sha256'])
        controls=[]
        def reject(name,fun):
            try:fun()
            except(ValueError,KeyError):controls.append(name);return
            raise ValueError('corruption accepted '+name)
        reject('missing_representative',lambda:cover(excluded,orbits,reps[:-1]));reject('duplicate_representative',lambda:cover(excluded,orbits,reps[:-1]+[0]));bad=deepcopy(orbits);bad[0][0]=bad[6][0];reject('overlap_and_gap',lambda:cover(excluded,bad,reps));reject('wrong_local_case',lambda:cover([0,*excluded[1:]],orbits,reps));bad=deepcopy(records[0]);bad['cnf_sha256']='0'*64;reject('wrong_proof_input',lambda:proof_binding(bad,encoding['inputs_sha256']));bad=deepcopy(records[0]);bad['replay']['accepted']=False;reject('unaccepted_replay',lambda:proof_binding(bad,encoding['inputs_sha256']))
        need(set(range(4))|{4}|{5}==set(range(6))and not(set(range(4))&{4,5}),'at-most-five disjoint integer cases');save(out/'controls.json',dict(rejected_corruptions=controls,positive_108_partition=True,at_most_five_partition=[[0,1,2,3],[4],[5]]));save(out/'coverage.json',dict(population=list(range(108)),locally_excluded=excluded,representative_orbits=orbits,proof_representatives=reps,case_maps=mapping,covered_once=dict(Counter(excluded+[x for r in reps for x in orbits[r]])),proof_records=proofrecords))
        for p in[Path(__file__),ROOT/'docs/AUDIT_20260930_FOUR_PROFILE_UNION.md',ROOT/'docs/AUDIT_20260930_FOUR_PROFILE_UNION_PREPARATION.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p.resolve().relative_to(ROOT).as_posix())
        ts=datetime.now(timezone.utc).isoformat();base=dict(revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',verifier='/root/eight_domain_audit',method='Separate exact108-profile set union and proof/encoding binding audit; independent written composition of previously reviewed premises. No new native or DRAT call.',assumptions=['Binary36x60 factor with the fixed six-prism Hadamard coordinate support and prescribed full integer Gram.','Every two distinct outside columns overlap at most2.'],trusted_components=['Previously independently checked normalization, local exclusions, encodings and complete DRAT replays at exact hashes.','Python exact integer/set arithmetic; no producer imports.'],limitations=['One fixed-support construction family only.','No exclusion of the whole support, its core, or unrestricted Conway99.','No target automorphism assumed.'],artifact_availability='LOCAL_ONLY',availability_reason='Pending parent publication.',external_review=None,external_review_reason='Internal independent composition only.',created_at=ts,updated_at=ts,inputs_sha256=pins)
        first=dict(base,id='C-FIXED-HADAMARD-EXACTLY-FOUR-UNBALANCED-GROUPS-EXCLUSION',statement='No binary36x60 factor on the pinned six-prism Hadamard support can simultaneously have the prescribed full integer Gram, all outside-column overlaps at most2, and exactly four unbalanced identical-support triples.',scope='Exactly-four-unbalanced subfamily on this literal fixed support;108 labelled necessary profiles are partitioned into12 local-screen exclusions and96 members of16 separately proof-excluded representative orbits.',dependencies=[dict(id=i,revision=1,relation=r)for i,r in [('C-FIXED-HADAMARD-FOUR-EXCEPTION-LOCAL-PROFILE-SCREEN','coverage'),('C-FIXED-HADAMARD-FOUR-EXCEPTION-GLOBAL-FIBRE-NORMALIZATION','normalization'),('C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-EXCLUSION','uses_result'),('C-FIXED-HADAMARD-FIFTEEN-FOUR-EXCEPTION-EXCLUSIONS','uses_result'),('C-FIXED-HADAMARD-FOUR-EXCEPTION-CASE0-GRAM-ENCODING','encoding_equivalence'),('C-FIXED-HADAMARD-FIFTEEN-FOUR-EXCEPTION-GRAM-ENCODINGS','encoding_equivalence')]])
        second=dict(base,id='C-FIXED-HADAMARD-AT-MOST-FIVE-UNBALANCED-GROUPS-EXCLUSION',statement='Every binary36x60 factor on the pinned six-prism Hadamard support with the prescribed full integer Gram and all outside-column overlaps at most2 has at least six unbalanced identical-support triples.',scope='At-most-five-unbalanced subfamily excluded; six or more unbalanced groups remain unresolved by this statement.',dependencies=[dict(id=i,revision=1,relation='uses_result')for i in['C-FIXED-HADAMARD-AT-MOST-THREE-UNBALANCED-GROUPS-EXCLUSION',first['id'],'C-FIXED-HADAMARD-EXACTLY-FIVE-UNBALANCED-GROUPS-EXCLUSION']]);save(out/'claim_bindings.json',[first,second])
        result=dict(status='INDEPENDENT_FIXED_HADAMARD_FOUR_PROFILE_UNION_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},profile_population=108,local_exclusions=12,proof_representatives=16,proof_orbit_members=96,duplicate_coverage=0,missing_profiles=0,approved_claim_ids=[first['id'],second['id']],new_native_calls=0,new_DRAT_replays=0,target_resolution=False);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
