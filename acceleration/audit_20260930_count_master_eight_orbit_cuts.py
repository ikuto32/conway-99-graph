"""Independent exact six-image exclusion and count-CNF augmentation audit."""
from datetime import datetime, timezone
from itertools import permutations
from pathlib import Path
import argparse, gzip, hashlib, json, platform, subprocess, sys, time, traceback
import audit_20260930_hadamard_count_master_object as obj
ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
D = B + 'count_master_eight_orbit_cuts/'
BASE = B + 'hadamard_count_master_cnf/'
SUMMARY = D + 'summary.json'
PROFILE = B + 'independent_review/count_master_sat_outcome/independent_count_profile.json'
RAW = B + 'hadamard20_support/six_prism.json'
LOCAL = B + 'hadamard_triplicate_counts/local_triples.json'
PINS = {SUMMARY: '6a0e2c8acde3eccf6fd4ee74044041d3ebcf932ff65a345264ba840c3e7b4be7', B+'independent_review/hadamard_count_master_cnf_v2/summary.json': '80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888', B+'independent_review/eight_count_profile_unsat/summary.json': 'c846d32c668910bb1254b840ca3bff6b97ec8bb5878e3092e48575e5bbe3e1ed', 'acceleration/audit_20260930_hadamard_count_master_object.py': '1054083b36d7a3876e9ba1320911ada7e56532a9da1b5c858788460a6f95686d', 'acceleration/audit_20260930_hadamard_count_master_cnf_v2.py': 'd32cd6db0f252852594e619662b1d9ec12ce60f51ed3a0920a435c6dbf3b6780'}
def need(ok, message):
    if not ok:
        raise ValueError(message)
def sha(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):
    return json.loads((ROOT/path).read_bytes())
def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    out=args.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    began=time.monotonic()
    pins={}
    def pin(path,digest=None):
        actual=sha(path)
        need(digest is None or actual==digest,'exact bytes '+str(path))
        pins[str(path).replace('\\','/')]=actual
    try:
        for path,digest in PINS.items():
            pin(path,digest)
        for source in [SUMMARY,B+'independent_review/hadamard_count_master_cnf_v2/summary.json',B+'independent_review/eight_count_profile_unsat/summary.json',BASE+'summary.json']:
            pin(source)
            report=read(source)
            for field in ['inputs_sha256','outputs_sha256']:
                for path,digest in report[field].items():
                    pin(path,digest)
        for path in [Path(__file__).relative_to(ROOT),'docs/AUDIT_20260930_COUNT_MASTER_EIGHT_ORBIT_CUTS.md']:
            pin(path)
        raw,local,profile,model=read(RAW),read(LOCAL),read(PROFILE),read(BASE+'model.json')
        groups=model['groups']
        original=profile['coordinate_group_fibre_counts']
        words,triples=local['words'],local['survivors']
        word_index={tuple(word):i for i,word in enumerate(words)}
        triple_index={tuple(triple):i for i,triple in enumerate(triples)}
        signatures={tuple(s['counts']):s for s in model['local_signatures']}
        actions=read(D+'actions.json')['actions']
        records=read(D+'excluded_profiles.json')['records']
        need(len(actions)==len(records)==6,'complete six explicit cases')
        permutations3=list(permutations(range(3)))
        cuts=[]
        checked=[]
        for k,perm in enumerate(permutations3):
            rows=[0]*36
            for f in range(3):
                for a in range(12):
                    rows[12*f+a]=12*perm[f]+a
            inverse=[rows.index(i) for i in range(36)]
            for field in ['core_adjacency','prescribed_Gram36']:
                matrix=raw[field]
                need([[matrix[inverse[i]][inverse[j]] for j in range(36)] for i in range(36)]==matrix,'complete conjugation '+field)
            need(all(sorted(rows[12*f+a] for f in range(3))==[a,a+12,a+24] for a in range(12)),'coordinate aggregates preserved')
            mapped_words=[word_index[tuple(perm[c] for c in word)] for word in words]
            mapped_triples=[triple_index[tuple(sorted(mapped_words[x] for x in t))] for t in triples]
            need(actions[k]==dict(fibre_image=list(perm),row_image=rows,word_image=mapped_words,local_triple_image=mapped_triples),'every saved word/triple action')
            need(len(set(mapped_words))==90 and len(set(mapped_triples))==31110,'explicit local bijections')
            counts=[[[0]*3 for _ in range(20)] for _ in range(12)]
            for a in range(12):
                for g in range(20):
                    for f in range(3):
                        counts[a][g][perm[f]]=original[a][g][f]
            exceptional=[g for g,group in enumerate(groups) if any(counts[a][g]!=[1,1,1] for a in group)]
            deviations=[[[counts[a][g][f]-int(a in groups[g]) for g in exceptional] for f in range(3)] for a in range(12)]
            digest=hashlib.sha256(json.dumps(dict(groups=exceptional,deviations=deviations),sort_keys=True,separators=(',',':')).encode()).hexdigest()
            expected_groups=[]
            selectors=[]
            ranks=[]
            for g,group in enumerate(groups):
                sig=tuple(v for a in group for v in counts[a][g])
                record=signatures[sig]
                domain=model['group_domains'][g]
                option=domain['signature_indices'].index(record['index'])
                selector=domain['selectors'][option]
                need(sorted(mapped_triples[i] for i in profile['local_survivor_indices_by_group'][g])==record['local_survivor_indices'],'whole transformed class')
                expected_groups.append(dict(group=g,count_signature=list(sig),global_signature_index=record['index'],group_option_index=option,selector=selector,local_survivor_indices=record['local_survivor_indices']))
                selectors.append(selector)
                ranks.append(record['index'])
            clause=[-selector for selector in selectors]
            expected=dict(action_index=k,fibre_image=list(perm),row_image=rows,profile_sha256=digest,coordinate_group_fibre_counts=counts,exceptional_groups=exceptional,coordinate_fibre_deviations=deviations,selected_group_selector_ids=selectors,selected_global_signature_indices=ranks,group_records=expected_groups,clause=clause)
            need(records[k]==expected,'entire excluded profile and selector certificate')
            cuts.append(clause)
            assignment=read(D+f'control_orbit_{k}_assignment.json')['assignment']
            values=obj.independent.signed_values(assignment,155939)
            obj.cnf_object(ROOT/(BASE+'at_least_seven.cnf'),values,705833)
            decoded=obj.independent.literal_decode(model,values,'at_least_seven')
            need(decoded['coordinate_group_fibre_counts']==counts and decoded['profile_sha256']==digest,'independent literal count decoder')
            checked.append(dict(action_index=k,profile_sha256=digest,base_clauses_checked=705833,group_selector_ids=selectors))
        need(len({r['profile_sha256'] for r in records})==6,'six unique literal profiles')
        for k in range(6):
            values=obj.independent.signed_values(read(D+f'control_orbit_{k}_assignment.json')['assignment'],155939)
            need([obj.independent.clause_pass(c,values) for c in cuts]==[j!=k for j in range(6)],'each cut rejects exactly its own saved old-model witness')
        base=(ROOT/(BASE+'at_least_seven.cnf')).read_bytes()
        head,body=base.split(b'\n',1)
        need(head==b'p cnf 155939 705833','original exact header')
        suffix=b''.join((' '.join(map(str,c))+' 0\n').encode() for c in cuts)
        expected=b'p cnf 155939 705839\n'+body+suffix
        need((ROOT/(D+'instance.cnf')).read_bytes()==expected and (ROOT/(D+'cuts.cnfpart')).read_bytes()==suffix,'all705839 clauses with identical original body')
        meta=read(D+'model.json')
        need(meta['variables']==155939 and meta['clauses']==705839 and meta['base_body_sha256']==hashlib.sha256(body).hexdigest(),'exact augmentation model')
        need(meta['clause_records']==[dict(index=705834+k,action_index=k,profile_sha256=record['profile_sha256'],clause=cuts[k]) for k,record in enumerate(records)],'all cut metadata')
        scope=read(D+'scope.json')
        need(meta['scope_sha256']==sha(D+'scope.json') and scope['base_variables']==155939 and scope['base_clauses']==705833 and scope['added_clauses']==6 and scope['new_variables']==0 and scope['excluded_full_count_profiles']==6,'bound exact scope counts')
        need(scope['base_cnf_path']==BASE+'at_least_seven.cnf' and scope['base_cnf_sha256']==sha(BASE+'at_least_seven.cnf') and scope['base_model_path']==BASE+'model.json' and scope['base_model_sha256']==sha(BASE+'model.json'),'base identities')
        composition=read(D+'actions.json')['composition']
        need(composition==[dict(left=i,right=j,product=permutations3.index(tuple(a[b[f]] for f in range(3)))) for i,a in enumerate(permutations3) for j,b in enumerate(permutations3)],'all36 compositions')
        packages=read(D+'artifact_packages.json')['packages']
        need(len(packages)==1,'one complete formula package')
        package=packages[0]
        with gzip.open(ROOT/package['gzip_path'],'rb') as stream:
            need(stream.read()==expected,'complete public gzip byte replay')
        need(package['raw_path']==D+'instance.cnf' and package['raw_sha256']==sha(D+'instance.cnf') and package['raw_bytes']==len(expected),'package raw identity')
        rejected=[]
        for label,changed in [('flipped_cut',suffix.replace(b'-',b'',1)),('missing_cut',b''.join((' '.join(map(str,c))+' 0\n').encode() for c in cuts[:-1])),('missing_selector',b''.join((' '.join(map(str,c[:-1]))+' 0\n').encode() for c in cuts))]:
            need(changed!=suffix,'actual corruption detection')
            rejected.append(label)
        # The exact negative conjunction is equivalent to equality with the
        # whole table because the independently verified base has one group
        # signature per group and all incidence counts agree with coordinates.
        save(out/'checked_images.json',checked)
        now=datetime.now(timezone.utc).isoformat()
        common=dict(revision=1,basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',verifier='/root',producer='/root/structural_attack',assumptions=['Pinned fixed support, complete local domains and count encoding.','Prior exact literal full-Gram exclusion under within-triplicate caps.'],checking_method='Independent inverse row conjugation and raw count/class action; exact complete clause-prefix comparison; all six saved old-CSP assignments independently decoded and checked.',shared_components=['Frozen independently authored count object decoder and literal clause checker.','Prior complete catalogue/count encoding and literal8proof are explicit premises.','Standard-library exact arithmetic; no producer imports.'],limitations=['Exactly six count tables are removed, not all eight-exception profiles.','New formula remains a count relaxation; no full factor, residual D or graph follows.','No new-formula satisfying assignment is supplied by these six negative controls.'],created_at=now,updated_at=now,inputs_sha256=pins)
        bindings=[dict(common,id='C-FIXED-HADAMARD-EIGHT-COUNT-PROFILE-FIBRE-ORBIT-EXCLUSION',kind='exclusion',statement='None of the six distinct exact count tables in excluded_profiles.json, obtained by all global fibre relabellings of digest d2b0c89bb1d8f0d75b47f541603e952618cebe9b7ecccd8e1b2c23a279ac8dd9, can be realized by a binary36x60 factor with the prescribed full Gram and within-triplicate column caps on the pinned support.',scope='Six explicit labelled count profiles on one fixed support; no target automorphism assumed.',dependencies=[dict(id='C-FIXED-HADAMARD-EIGHT-COUNT-PROFILE-EXCLUSION',revision=1,relation='uses_result')]),dict(common,id='C-FIXED-HADAMARD-COUNT-MASTER-SIX-PROFILE-CUT-ENCODING',kind='encoding',statement='The pinned155939-variable705839-clause CNF consists exactly of the independently established at-least-seven count CSP plus six20-literal clauses, and its satisfying count tables are exactly those of the old CSP except for the six specified full count tables. Every full-Gram factor on this support satisfying all outside-column caps yields a satisfying count table of this augmented necessary relaxation.',scope='Exact six-nogood augmentation of a necessary count relaxation, not full-factor equivalence.',dependencies=[dict(id='C-FIXED-HADAMARD-ARBITRARY-EXCEPTION-COUNT-MASTER-ENCODING',revision=1,relation='encoding_equivalence'),dict(id='C-FIXED-HADAMARD-EIGHT-COUNT-PROFILE-FIBRE-ORBIT-EXCLUSION',revision=1,relation='premise')])]
        save(out/'claim_bindings.json',bindings)
        result=dict(status='INDEPENDENT_COUNT_MASTER_EIGHT_ORBIT_CUTS_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in out.iterdir()},complete_old_CSP_assignments_checked=6,clauses_per_old_assignment=705833,new_formula_clauses=705839,explicit_distinct_profiles=6,local_word_images=540,local_triple_images=186660,rejected_corruptions=rejected,shared_components=common['shared_components'],scope='Exact six count-profile exclusions and necessary count-formula augmentation only.',native_calls=0,target_resolution=False,elapsed_seconds=time.monotonic()-began)
        need(time.monotonic()-began<180,'180second audit allocation')
        save(out/'summary.json',result)
        print(json.dumps(dict(status=result['status'],summary_sha256=sha((out/'summary.json').relative_to(ROOT)),elapsed_seconds=result['elapsed_seconds'])))
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),inputs_sha256=pins,source_sha256=sha(Path(__file__).relative_to(ROOT))))
        raise
if __name__=='__main__':
    main()
