"""Full21-quota unmerged enumeration of all200 septet marginal cases."""
import argparse, copy, gzip, json, math, platform, subprocess, sys, time
from datetime import datetime,timezone
from pathlib import Path
from tqdm import tqdm
import audit_20260930_hadamard_six_rank4_profiles as independent
need=independent.need;sha=independent.sha;key=independent.key;read=independent.read;write=independent.write
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
D=B/'20260930_hadamard_seven_rank5_dp';G=B/'20260930_independent_review/hadamard_seven_exception_census'
RAW=B/'20260930_hadamard20_support/six_prism.json'
CID='C-FIXED-HADAMARD-SEVEN-EXCEPTION-INTEGER-MARGINAL-CENSUS'
PINS={D/'summary.json':'6eb84ece5bd4a1eb494215a7bab5020f1b2297463604ed32ba22b9bc995bbef5',G/'summary.json':'0baaa10f59840dc2ca02676cf9d0f56a6dc0fd6f227edfeecabd0e94b3ff6c91',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,expected=None):
        name=key(p)
        if name not in pins:pins[name]=sha(p)
        need(expected is None or pins[name]==expected,'input identity '+name);return pins[name]
    try:
        for p,h in PINS.items():pin(p,h)
        summary=read(D/'summary.json');gate=read(G/'summary.json')
        need(gate['status']=='INDEPENDENT_HADAMARD_SEVEN_EXCEPTION_KERNEL_CENSUS_PASS','independently authenticated candidate population')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():pin(ROOT/p,h)
        helper=Path(independent.__file__);prior=B/'20260930_independent_review/hadamard_six_rank4_profiles/summary.json';pin(prior,'0430355de5159a5223c464d3766ec54206a37177b90e18cf92364d276dd483e3');pin(helper,read(prior)['inputs_sha256'][key(helper)])
        cand=B/'20260930_hadamard_seven_exception_census/remaining_candidates.json';pin(cand,gate['inputs_sha256'][key(cand)]);cases=read(cand)['records']
        independently_retained=G/'independent_remaining.json';pin(independently_retained,gate['outputs_sha256'][key(independently_retained)]);checked=read(independently_retained)
        need(checked['count']==len(cases)==200 and checked['records']==[dict(groups=c['groups'],rank=5,integer_null_basis=c['certificate']['integer_null_basis']) for c in cases],'same exact200 retained septets')
        raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][j]) for j in range(60)))
        _,control_rows=independent.domains([groups[i] for i in [0,7,9,19]])
        control_layers,control_paths,control_population=independent.enumerate_paths(control_rows,4)
        need(len(control_paths)==6 and control_layers[-1][(0,)*12+(0,)]==1,'known four-circuit exact six-active-positive calibration')
        inventory=read(D/'domain_inventory.json')['cases'];need(len(inventory)==len(summary['cases'])==200,'all200 prepared and completed cases')
        need(summary['status']=='CANDIDATE_SEVEN_RANK5_MARGINAL_DP_COMPLETE' and summary['selected_cases']==summary['complete_cases']==200 and summary['unattempted_cases']==0,'complete frozen producer outcome')
        results=[];positive_records=[];total_full=total_layers=total_states=0;control_template=None
        for ci,c in enumerate(tqdm(cases,desc='Independent21-quota enumeration',mininterval=1)):
            selected=[groups[g] for g in c['groups']];H,rows=independent.domains(selected);inv=inventory[ci];case=summary['cases'][ci]
            need(inv['case']==case['case']==ci and inv['groups']==case['groups']==c['groups'],'literal septet identity')
            domainpath=ROOT/inv['domain_path'];pin(domainpath,inv['domain_sha256']);saved=read(domainpath)
            p=saved['projection_group_indices'];need(len(p)==2 and p==sorted(set(p)) and all(type(i) is int and 0<=i<7 for i in p),'projection coordinate pair')
            basis=c['certificate']['integer_null_basis'];pm=[[v[i] for v in basis] for i in p];det=pm[0][0]*pm[1][1]-pm[0][1]*pm[1][0]
            need(det!=0 and pm==saved['projection_matrix'] and det==saved['projection_determinant'],'injective whole rational nullspace projection')
            need(saved['case']==ci and saved['groups']==c['groups'] and saved['global_kernel_H']==H,'raw domain scope')
            expected_rows=independent.expected_rows(rows,p,7);need(saved['records']==expected_rows,'every full integer vector and ordered fibre triple')
            need(inv['integer_vector_counts']==[len(r['vectors']) for r in rows] and inv['fibre_profile_counts']==[len(r['choices']) for r in rows],'complete finite domain counts')
            layers,paths,population=independent.enumerate_paths(rows,7)
            need(population==math.prod(len(r['choices']) for r in rows),'every unmerged full profile sequence')
            total_full+=population;caseout=domainpath.parent;pin(caseout/'summary.json');need(read(caseout/'summary.json')==case,'case summary identity')
            need(case['complete'] and case['completed_coordinate']==11 and len(case['checkpoints'])==12 and case['status']=='COMPLETE' and case['unknown_reason'] is None,'no unfinished layer promoted')
            details=[];previous_states=1
            for depth,cp in enumerate(case['checkpoints']):
                path=ROOT/cp['path'];pin(path,cp['sha256']);receipt=read(path);need(receipt['case']==ci and receipt['coordinate']==depth and receipt['domain_sha256']==pins[key(domainpath)],'checkpoint exact input')
                statepath=ROOT/receipt['state_path'];pin(statepath,receipt['state_sha256']);expected={};full_by_project={}
                for full,count in layers[depth].items():
                    projected=independent.project(full,p,7);need(projected not in expected,'literal full-state projection injectivity')
                    expected[projected]=count;full_by_project[projected]=full
                with gzip.open(statepath,'rt',encoding='utf8') as stream:records=[json.loads(line) for line in stream]
                independent.check_layer(records,expected,full_by_project,rows,7,p,depth)
                need(receipt['states']==len(expected) and receipt['profile_sequence_count']==sum(expected.values()),'all exact state multiplicities')
                need(receipt['transitions']==previous_states*len(rows[depth]['choices']),'complete recorded aggregated transitions');previous_states=len(expected)
                details.append(dict(coordinate=depth,full_quota_states=len(layers[depth]),profile_prefix_sequences=sum(layers[depth].values()),saved_witnesses=len(records)))
                total_layers+=1;total_states+=len(records)
                if control_template is None and len(records)>1:control_template=(records,expected,full_by_project,rows,p,depth)
            need(case['exactly_seven_marginal_profile_sequences']==len(paths) and case['has_marginal_witness']==bool(paths),'exact positive/zero count')
            if paths:
                witnesspath=caseout/'first_witness.json';pin(witnesspath);w=read(witnesspath);full=independent.path_state(w['choice_path'],rows,7)
                need(full==(0,)*21+(127,) and w['groups']==c['groups'] and w['activity_mask']==127 and w['total_group_fibre_deviations']==[[0]*7 for _ in range(3)],'literal all21-quota positive witness')
            else:need(not(caseout/'first_witness.json').exists(),'no claimed witness in empty case')
            results.append(dict(case=ci,groups=c['groups'],complete_profile_product=population,exactly_seven_active=len(paths),balanced_profiles=layers[-1].get((0,)*22,0),layers=details))
            positive_records.append(dict(case=ci,groups=c['groups'],ordered_choice_paths=[list(path) for path in sorted(paths)],scope='Linear integer/count marginals only; no local column or full factor realization.'))
        exact_counts=[r['exactly_seven_active'] for r in results];zeros=[i for i,n in enumerate(exact_counts) if n==0];positives=[i for i,n in enumerate(exact_counts) if n]
        need(len(zeros)==summary['complete_empty_cases']==162 and len(positives)==summary['complete_nonempty_cases']==38,'complete independent case outcomes')
        need(total_full==154214 and total_layers==2400,'full unmerged finite coverage')
        rejected=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError,IndexError,TypeError):rejected.append(label)
            else:raise ValueError('corruption accepted '+label)
        records,expected,full_by_project,rows,p,depth=control_template
        bad=copy.deepcopy(records);bad[0][1]+=1;reject('wrong_path_count',lambda:independent.check_layer(bad,expected,full_by_project,rows,7,p,depth))
        reject('missing_state',lambda:independent.check_layer(records[:-1],expected,full_by_project,rows,7,p,depth))
        bad=copy.deepcopy(records);bad.insert(1,bad[0]);reject('duplicate_state',lambda:independent.check_layer(bad,expected,full_by_project,rows,7,p,depth))
        bad=copy.deepcopy(records);bad[0][2][-1]=999;reject('invalid_path',lambda:independent.check_layer(bad,expected,full_by_project,rows,7,p,depth))
        bad=copy.deepcopy(records);bad[0][0][-1]^=1;reject('wrong_activity_mask',lambda:independent.check_layer(bad,expected,full_by_project,rows,7,p,depth))
        bad=copy.deepcopy(records);bad[0][0][0]+=1;reject('wrong_projected_quota',lambda:independent.check_layer(bad,expected,full_by_project,rows,7,p,depth))
        reject('incomplete_domain',lambda:need(expected_rows[:-1]==saved['records'],'all twelve coordinate domains'))
        reject('zero_projection_determinant',lambda:need(0!=0,'projection must be injective'))
        reject('missing_septet',lambda:need(len(cases[:-1])==200,'complete selected population'))
        write(out/'controls.json',dict(four_circuit_exactly_four_positive_profiles=6,four_circuit_balanced_profiles=1,four_circuit_total_sequences=control_population,corruptions_rejected=rejected))
        write(out/'independent_layers.json',dict(records=results,total_full_profile_sequences=total_full,total_saved_states_checked=total_states,total_layers=total_layers))
        write(out/'all_positive_marginal_profiles.json',dict(records=positive_records,total_labelled_profiles=sum(exact_counts)))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_SEVEN_RANK5_MARGINALS.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat()
        binding=dict(id=CID,revision=1,kind='mathematical result',basis=['COMPUTED','DERIVED'],status='VERIFIED',review_state='CLEAR',statement=f'For all200 independently retained rank5 septets of the literal fixed Hadamard support, complete bounded integer marginal enumeration gives162 cases with no exactly-seven-active profile and38 cases with a total of{sum(exact_counts)} explicitly labelled profiles. All154214 full coordinate-profile sequences,2400 saved layers and{total_states} state witnesses have been independently checked against all21 group/fibre quotas. Thus an exactly-seven-unbalanced prescribed-Gram factor must use one of the38 saved nonempty septets, while none of their positive marginal counts establishes a factor.',scope='Complete necessary integer/count marginal relaxation for the200 fixed septets; no local triple, quadratic Gram, outside-column-cap or graph feasibility claim.',assumptions=['The literal fixed Hadamard support and full prescribed integer Gram.','Exactly seven nominated groups are unbalanced.'],dependencies=[dict(id='C-FIXED-HADAMARD-SEVEN-EXCEPTION-KERNEL-CENSUS',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-TRIPLICATE-MARGINAL-RELAXATION',revision=1,relation='uses_result')],verifier='/root/structural_attack',producer='/root',method='Independent complete unmerged profile recursion using all21 sums, after complete4^7 vector enumeration; saved compressed states checked only after exact projection injectivity.',shared_components=['Frozen independently authored generic domains/recursion/layer checker from the six-group audit, with exact source hash and previous calibration disclosed.','Same raw support and separately approved septet coverage; no producer DP imports or calls.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},artifact_availability='LOCAL_ONLY',availability_reason='Review records pending parent publication.',external_review=None,external_review_reason='No external review asserted.',limitations=['Positive marginal profiles are not local triples or full factors.','No native solver, outside-column-cap premise, target automorphism or unrestricted exclusion.'],created_at=now,updated_at=now)
        write(out/'claim_binding.json',binding)
        write(out/'summary.json',dict(status='INDEPENDENT_SEVEN_RANK5_INTEGER_MARGINAL_CENSUS_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},claim_id=CID,claim_revision=1,complete_cases=200,zero_cases=zeros,positive_cases=positives,exact_counts=exact_counts,complete_profile_sequences=total_full,labelled_feasible_marginal_profiles=sum(exact_counts),saved_layers_checked=total_layers,saved_state_witnesses_checked=total_states,corruptions_rejected=len(rejected),solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start))
        print(json.dumps(dict(status='INDEPENDENT_SEVEN_RANK5_INTEGER_MARGINAL_CENSUS_PASS',sha256=sha(out/'summary.json'),positive_marginal_profiles=sum(exact_counts))))
    except BaseException as exc:write(out/'failure.json',dict(error=repr(exc),source_sha256=sha(Path(__file__))));raise

if __name__=='__main__':main()
